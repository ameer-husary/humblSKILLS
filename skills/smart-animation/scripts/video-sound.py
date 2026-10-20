#!/usr/bin/env python3
"""Sound for a video-loop project, built on earshot (https://github.com/Leonxlnx/earshot).

Run with a Python that can `import earshot` (set EARSHOT_PYTHON for video-loop.sh).

    video-sound.py build  <project> <cues.json> <duration_s>   # kit takes on cues -> audio/soundtrack.wav
    video-sound.py listen <project> <cues.json> <video.mp4> [out=critique/audio] [scenes]
        # earshot timeline + sheet + critique -> <out>/; scenes = "id:t0:t1,..." adds critique/<id>/sound.png

build is pure DSP (no models). listen loads earshot's models once (~1.1 GB download on first use).
cues.json: {"fps": 30, "events": [{"t": 0.3, "kind": "key", "scene": "s01-hook", "pitch": "C5"?, "gain_db": 0?}]}
A cue's kind is a kit role (see `earshot kit init`); a role set to null in audio/kit.json is skipped.
"""
import json
import os
import sys

TARGET_LUFS, CEILING_DBTP = -14.0, -1.0


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

    mix = np.zeros((int(round(duration * sr)), 2), np.float32)
    used, skipped = {}, []
    for ev in events:
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
    report = {'soundtrack': out, 'events': len(events), 'placed': sum(used.values()),
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
