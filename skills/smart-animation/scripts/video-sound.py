#!/usr/bin/env python3
"""Sound for a video-loop project, built on earshot (https://github.com/Leonxlnx/earshot).

Run with a Python that can `import earshot` (set EARSHOT_PYTHON for video-loop.sh).

    video-sound.py build  <project> <cues.json> <duration_s>   # kit takes on cues -> audio/soundtrack.wav
    video-sound.py listen <project> <cues.json> <video.mp4> [out=critique/audio] [scenes]
        # earshot timeline + sheet + critique -> <out>/; scenes = "id:t0:t1,..." adds critique/<id>/sound.png

build is pure DSP (no models). listen loads earshot's models once (~1.1 GB download on first use).
cues.json: {"fps": 30, "events": [{"t": 0.3, "kind": "key", "scene": "s01-hook", "pitch": "C5"?, "gain_db": 0?}]}
A cue's kind is a kit role (see `earshot kit init`); a role set to null in audio/kit.json is skipped.
Kind "vo" is a narration line: {"t": 0.4, "kind": "vo", "text": "..."} (or "file": "assets/vo/x.wav").
scenes.json "voice": {"engine": "say" | "hyperframes" | "files", "name": "Samantha", "rate": 180} renders
each line once (cached by text) to audio/vo/; leading silence is trimmed so the line starts on its cue.
scenes.json "bed": {"file": "assets/bed.wav", "db": -6, "duck_db": -5} mixes a music bed under
everything, ducked while a line plays, faded out over the last 1.5 s. Line timings -> .loop/voice.json.
"""
import hashlib
import json
import os
import subprocess
import sys

TARGET_LUFS, CEILING_DBTP = -14.0, -1.0


def render_line(project, ev, voice, sr):
    """one narration line -> float32 mono at sr, leading silence trimmed (cached under audio/vo/)."""
    import numpy as np
    import soundfile as sf
    engine = voice.get('engine', 'say')
    if engine == 'files' or ev.get('file'):
        src = os.path.join(project, ev['file'])
    else:
        key = hashlib.sha1(json.dumps([engine, voice, ev['text']], sort_keys=True).encode()).hexdigest()[:12]
        src = os.path.join(project, 'audio', 'vo', key + '.wav')
        if not os.path.exists(src):
            os.makedirs(os.path.dirname(src), exist_ok=True)
            if engine == 'say':  # macOS, offline; the fallback when local TTS is unavailable
                tmp = src[:-4] + '.aiff'
                subprocess.run(['say', '-v', voice.get('name', 'Samantha'), '-r', str(voice.get('rate', 180)),
                                '-o', tmp, ev['text']], check=True)
            elif engine == 'hyperframes':  # local Kokoro via `npx hyperframes tts`
                tmp = src[:-4] + '.tts.wav'
                subprocess.run(['npx', '-y', 'hyperframes', 'tts', ev['text'], '-v', voice.get('name', 'am_michael'),
                                '-s', str(voice.get('speed', 1.0)), '-o', tmp], check=True)
            else:
                raise SystemExit(f'video-sound: unknown voice engine {engine!r}')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ac', '1', '-ar', str(sr), src], check=True)
            os.remove(tmp)
    y, ysr = sf.read(src, dtype='float32', always_2d=True)
    assert ysr == sr, f'{src} is {ysr} Hz, mix is {sr} Hz'
    y = y.mean(axis=1)
    loud = np.flatnonzero(np.abs(y) > 10 ** (-45 / 20) * max(np.abs(y).max(), 1e-9))
    return y[max(0, loud[0] - int(0.005 * sr)):loud[-1] + int(0.05 * sr)] if len(loud) else y


def build(project, cues_path, duration):
    import numpy as np
    import soundfile as sf
    from earshot import api
    from earshot.features import true_peak_dbtp
    from earshot.forge import fx
    import pyloudnorm

    kit_json = os.path.join(project, 'audio', 'kit.json')
    if not os.path.exists(kit_json):
        api.kit_init('calm', kit_json)  # effects-only default; edit roles per film
    lock = api.kit_render(kit_json, os.path.join(project, 'audio', 'kit'))
    roles = lock['roles']
    sr = lock['sr']
    events = json.load(open(cues_path))['events']

    cfg = json.load(open(os.path.join(project, 'scenes.json')))
    mix = np.zeros((int(round(duration * sr)), 2), np.float32)
    used, skipped, lines = {}, [], []
    for ev in events:
        if ev['kind'] == 'vo':
            y = render_line(project, ev, cfg.get('voice', {}), sr) * 10 ** (ev.get('gain_db', 0.0) / 20)
            start = int(round(ev['t'] * sr))
            b = min(start + len(y), len(mix))
            if b > start:
                mix[start:b] += y[:b - start, None]
            lines.append({'id': ev.get('id'), 't': ev['t'], 'end': round(ev['t'] + len(y) / sr, 3), 'text': ev.get('text', ev.get('file'))})
            continue
        role = roles.get(ev['kind'])
        if not role:
            skipped.append(ev['kind'])
            continue
        takes = role['takes']
        if ev.get('pitch'):
            takes = [k for k in takes if k.get('pitch') == ev['pitch']] or takes
        n = used.get(ev['kind'], 0)
        used[ev['kind']] = n + 1
        take = takes[n % len(takes)]  # cycle takes so repeats (typing) never sound identical
        y, tsr = sf.read(os.path.join(project, 'audio', 'kit', take['file']), dtype='float32', always_2d=True)
        assert tsr == sr, f"take {take['file']} is {tsr} Hz, kit is {sr} Hz"
        if y.shape[1] == 1:
            y = np.repeat(y, 2, axis=1)
        sync = {'onset': take['onset_s'], 'peak': take['peak_s'], 'end': take['end_s']}[role['align']]
        y = y * 10 ** ((role.get('level_db') or 0.0) / 20 + ev.get('gain_db', 0.0) / 20)
        start = int(round((ev['t'] - sync) * sr))
        a, b = max(start, 0), min(start + len(y), len(mix))
        if b > a:
            mix[a:b] += y[a - start:b - start]

    bed = cfg.get('bed')
    if bed:  # a music bed under everything, ducked under narration (a simple sidechain, 150 ms ramps)
        y, bsr = sf.read(os.path.join(project, bed['file']), dtype='float32', always_2d=True)
        assert bsr == sr, f"bed {bed['file']} is {bsr} Hz, mix is {sr} Hz"
        y = np.resize(y if y.shape[1] == 2 else np.repeat(y, 2, axis=1), mix.shape)  # loops a short bed
        env = np.zeros(len(mix), np.float32)
        for ln in lines:
            env[int(ln['t'] * sr):int(ln['end'] * sr)] = 1.0
        k = int(0.15 * sr)
        env = np.convolve(env, np.ones(k) / k, mode='same')
        gain = 10 ** ((bed.get('db', -6) + bed.get('duck_db', -5) * env) / 20)  # measured: ~10-12 LU under the voice
        fade = np.clip((len(mix) - np.arange(len(mix))) / (1.5 * sr), 0, 1)
        mix += y * (gain * fade)[:, None]
    os.makedirs(os.path.join(project, '.loop'), exist_ok=True)
    json.dump(lines, open(os.path.join(project, '.loop', 'voice.json'), 'w'), indent=1)

    meter = pyloudnorm.Meter(sr)
    lufs = meter.integrated_loudness(mix) if np.any(mix) else float('-inf')
    if np.isfinite(lufs):
        dry, gain_db = mix, TARGET_LUFS - lufs
        for _ in range(4):  # the limiter pulls loudness down; re-aim the gain until it lands
            mix = fx.limit(dry * 10 ** (gain_db / 20), ceiling_db=CEILING_DBTP - 0.3)
            lufs = meter.integrated_loudness(mix)
            if abs(lufs - TARGET_LUFS) < 0.2:
                break
            gain_db += TARGET_LUFS - lufs
    out = os.path.join(project, 'audio', 'soundtrack.wav')
    sf.write(out, mix, sr, subtype='PCM_24')
    report = {'soundtrack': out, 'events': len(events), 'placed': sum(used.values()), 'vo_lines': len(lines),
              'skipped_roles': sorted(set(skipped)),
              'integrated_lufs': round(lufs, 1) if np.isfinite(lufs) else None,
              'true_peak_dbtp': round(true_peak_dbtp(mix), 1) if np.any(mix) else None}
    print(json.dumps(report))


def listen(project, cues_path, video, out='critique/audio', scenes=''):
    from earshot import api
    out = os.path.join(project, out)
    os.makedirs(out, exist_ok=True)
    tl = api.timeline(video, video=video, cues=cues_path)
    api.sheet(video, os.path.join(out, 'sheet.png'), video=video, cues=cues_path, tl=tl)
    for spec in filter(None, scenes.split(',')):  # one sheet per scene, so each sound line is judged on its own
        sid, t0, t1 = spec.rsplit(':', 2)
        os.makedirs(os.path.join(project, 'critique', sid), exist_ok=True)
        api.sheet(video, os.path.join(project, 'critique', sid, 'sound.png'), video=video, cues=cues_path,
                  start=float(t0), end=float(t1))
    crit = api.critique(video, video=video)
    json.dump(tl, open(os.path.join(out, 'listen.json'), 'w'), indent=1, default=str)
    json.dump(crit, open(os.path.join(out, 'critique.json'), 'w'), indent=1, default=str)
    lo = tl.get('loudness', {})
    items = tl.get('sync', {}).get('cues', {}).get('items', [])
    print(json.dumps({'integrated_lufs': lo.get('integrated_lufs'), 'true_peak_dbtp': lo.get('true_peak_dbtp'),
                      'cues': [{k: i.get(k) for k in ('t', 'kind', 'offset_ms', 'status')} for i in items]}))


if __name__ == '__main__':
    if len(sys.argv) < 5 or sys.argv[1] not in ('build', 'listen'):
        sys.exit(__doc__)
    if sys.argv[1] == 'build':
        build(sys.argv[2], sys.argv[3], float(sys.argv[4]))
    else:
        listen(*sys.argv[2:7])
