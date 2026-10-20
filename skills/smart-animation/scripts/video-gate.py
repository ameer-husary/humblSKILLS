#!/usr/bin/env python3
"""The mechanical half of the video loop: cues, stale detection, critique stubs and the gate.

Called by video-loop.sh; stdlib only. All paths are relative to the project directory.

    video-gate.py cues   <project>          # data-cues of every scene + timeline -> cues.json; prints duration
    video-gate.py stale  <project>          # what needs fresh frames: "scene <id> <start> <end>" / "pair <a> <b> <start> <end>"
    video-gate.py report <project> <mp4>    # write stubs, apply the gate, print a summary, exit with the gate's code

Gate exit codes: 0 pass, 2 waiting for scores, 3 failing, 4 iteration cap reached while failing.
Scores live in critique/<scene>.md and critique/pairs/<a>__<b>.md (`score: N` in the frontmatter).
A score counts only while the stub's source_sha matches the current sources; any edit clears it.
"""
import glob
import hashlib
import json
import os
import re
import sys
from html.parser import HTMLParser

PLACEHOLDER_HOSTS = ('placehold', 'picsum.photos', 'dummyimage', 'lorempixel', 'via.placeholder', 'unsplash.it')
ASSET_RX = r'''(?:src|href)\s*=\s*["'](assets/[^"']+)|url\(\s*["']?(assets/[^"')]+)'''  # referenced, not mentioned
BANNED = [  # legal but generic motion; warnings, the rubric scores the rest
    (re.compile(r'''ease\s*:\s*["'](none|linear|power1[^"']*|sine[^"']*)["']'''), 'default GSAP ease'),
    (re.compile(r'\btransition\s*:'), 'CSS transition (not timeline-driven)'),
    (re.compile(r'(animation-timing-function|transition-timing-function)\s*:\s*(ease|linear|ease-in-out)\b'),
     'default CSS easing'),
]
RUBRIC = ['Intent lands in one viewing', 'Motion quality (springs, hierarchy, no banned defaults)',
          'Composition and type (hierarchy, spacing, legibility at 1x)',
          'Brand fidelity (real assets, correct colors and fonts)',
          'Rhythm and sound (gesture-to-sound sync, restraint, level; quote earshot numbers)']
PAIR_RUBRIC = ['The cut reads as one motion, not two', 'Direction and velocity carry across the cut',
               'Sound bridges or punctuates the cut (no double hit, no gap)', 'Color and layout continuity',
               'The second scene answers the first (story)']
PAD = 0.5  # seconds either side of a cut in a pair's evidence


def load(project, name, default=None):
    p = os.path.join(project, name)
    if not os.path.exists(p):
        return default
    return json.load(open(p))


def config(project):
    cfg = load(project, 'scenes.json')
    if not cfg or not cfg.get('scenes'):
        sys.exit('video-gate: scenes.json missing or has no scenes')
    return cfg


def scene_times(project, cfg):
    """{id: (absStart, absEnd)} from `hyperframes timeline --json` (the only timing source)."""
    tl = load(project, '.loop/timeline.json')
    if not tl:
        sys.exit('video-gate: .loop/timeline.json missing (run hyperframes timeline --json first)')
    rows = {}

    def walk(rs):
        for r in rs:
            rows[r['id']] = (float(r['absStart']), float(r['absEnd']), r.get('sourceFile') or r.get('src'))
            walk(r.get('children') or [])
    for tr in tl['timeline']['tracks']:
        walk(tr['rows'])
    out = {}
    for s in cfg['scenes']:
        if s['id'] not in rows:
            sys.exit(f"video-gate: scene {s['id']} is in scenes.json but not on the timeline")
        out[s['id']] = rows[s['id']]
    return out, float(tl['timeline']['duration'])


class _Cues(HTMLParser):
    def __init__(self, cid):
        super().__init__()
        self.cid, self.cues = cid, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.cues is None and a.get('data-composition-id') == self.cid and 'data-cues' in a:
            self.cues = json.loads(a['data-cues'])


def scene_cues(project, sid, src):
    p = _Cues(sid)
    p.feed(open(os.path.join(project, src)).read())
    return p.cues or []


def cmd_cues(project):
    cfg = config(project)
    times, duration = scene_times(project, cfg)
    events = []
    for s in cfg['scenes']:
        t0, t1, src = times[s['id']]
        for c in scene_cues(project, s['id'], src):
            if not 0 <= c['t'] <= t1 - t0:
                sys.exit(f"video-gate: {s['id']} cue at {c['t']} s is outside the scene (0-{t1 - t0:.3f} s)")
            events.append(dict(c, t=round(t0 + c['t'], 4), id=s['id'], scene_t=c['t']))
    events.sort(key=lambda e: e['t'])
    json.dump({'fps': cfg.get('fps', 30), 'events': events}, open(os.path.join(project, 'cues.json'), 'w'), indent=1)
    print(f'{duration} {len(events)}')


def assets_in(text):
    return sorted({a or b for a, b in re.findall(ASSET_RX, text)})


def sha(project, sid, src, entry):
    """Everything a scene's look depends on: its file, its scenes.json entry, the assets it names, the kit."""
    h = hashlib.sha1()
    text = open(os.path.join(project, src), 'rb').read()
    h.update(text)
    h.update(json.dumps(entry, sort_keys=True).encode())
    for a in assets_in(text.decode()):
        p = os.path.join(project, a)
        h.update(a.encode() + (open(p, 'rb').read() if os.path.exists(p) else b'MISSING'))
    kit = os.path.join(project, 'audio', 'kit.json')
    if os.path.exists(kit):
        h.update(open(kit, 'rb').read())
    return h.hexdigest()[:12]


def front(path):
    """frontmatter of a stub as a dict of strings ({} when missing)."""
    if not os.path.exists(path):
        return {}
    m = re.match(r'---\n(.*?)\n---', open(path).read(), re.S)
    return dict(re.findall(r'^(\w+):[ \t]*(.*?)[ \t]*$', m.group(1), re.M)) if m else {}


def units(project, cfg, times):
    """scenes then adjacent pairs: (kind, key, sha, stub path, start, end)."""
    out = []
    for s in cfg['scenes']:
        t0, t1, src = times[s['id']]
        out.append(('scene', s['id'], sha(project, s['id'], src, s),
                    os.path.join(project, 'critique', s['id'] + '.md'), t0, t1))
    for a, b in zip(out[:], out[1:]):
        key = f'{a[1]}__{b[1]}'
        out.append(('pair', key, hashlib.sha1((a[2] + b[2]).encode()).hexdigest()[:12],
                    os.path.join(project, 'critique', 'pairs', key + '.md'),
                    max(a[4], a[5] - PAD), min(b[5], b[4] + PAD)))
    return out


def frames_dir(stub):
    return stub[:-3] + '/frames'


def cmd_stale(project):
    cfg = config(project)
    times, _ = scene_times(project, cfg)
    for kind, key, h, stub, t0, t1 in units(project, cfg, times):
        if front(stub).get('source_sha') != h or not glob.glob(frames_dir(stub) + '/*.png'):
            print(kind, key.replace('__', ' ') if kind == 'pair' else key, f'{t0:.3f}', f'{t1:.3f}',
                  os.path.relpath(frames_dir(stub), project))


def subtract(a, b, holds):
    """parts of [a, b] not covered by any hold interval."""
    parts = [(a, b)]
    for h0, h1 in holds:
        parts = [q for p0, p1 in parts for q in ((p0, min(p1, h0)), (max(p0, h1), p1)) if q[1] - q[0] > 1e-3]
    return parts


def dead_findings(project, cfg, times, freeze_s):
    p = os.path.join(project, '.loop', 'dead.tsv')
    rows = [ln.split('\t') for ln in open(p).read().splitlines() if ln.strip()] if os.path.exists(p) else []
    found = {}
    for s in cfg['scenes']:
        t0, t1, _ = times[s['id']]
        holds = [(t0 + float(h['from']), t1 if h.get('to', 'end') == 'end' else t0 + float(h['to']))
                 for h in s.get('holds', [])]
        for kind, a, b in rows:
            a, b = max(float(a), t0), min(float(b), t1)
            if b <= a:
                continue
            for p0, p1 in subtract(a, b, holds):
                if kind == 'black' or p1 - p0 >= freeze_s:
                    found.setdefault(s['id'], []).append(f'{kind} {p0 - t0:.2f}-{p1 - t0:.2f} s (unplanned)')
    return found


def beat_times(project):
    """beat seconds from `hyperframes beats` (beats/*.json), or None without a music bed."""
    files = glob.glob(os.path.join(project, 'beats', '**', '*.json'), recursive=True)
    if not files:
        return None
    d = json.load(open(files[0]))
    seq = d.get('beats', d) if isinstance(d, dict) else d
    return sorted(float(b['time'] if isinstance(b, dict) and 'time' in b else b.get('t') if isinstance(b, dict) else b)
                  for b in seq)


def sound_findings(project, cfg, fps):
    """per-scene sync failures and film-level loudness from earshot (critique/audio/listen.json)."""
    tl = load(project, 'critique/audio/listen.json')
    if tl is None:
        return {}, ['no listening report: earshot did not run (set EARSHOT_PYTHON)']
    lock = load(project, 'audio/kit/kit.lock.json', {}).get('roles', {})
    per, film = {}, []
    for it in (tl.get('sync', {}).get('cues') or {}).get('items', []):
        off = it.get('offset_ms')
        # earshot times an event at its onset, so a whoosh placed by its apex (align peak / end)
        # reads early by design: those roles pass on any answer within 100 ms, onset roles need 1 frame
        align = (lock.get(it.get('kind')) or {}).get('align', 'onset')
        ok = ('OK',) if align == 'onset' else ('OK', 'near', 'swell', 'peak')
        if it.get('status') not in ok:
            per.setdefault(it.get('id'), []).append(
                f"{it.get('kind')} at {it['t']:.2f} s: {it.get('status')}" + (f' ({off:+.0f} ms)' if off is not None else ''))
    # a take still flagged after earshot's re-rolls (clicks, clipping, cut tail, rising glide...)
    used = {e['kind'] for e in load(project, 'cues.json', {}).get('events', [])}
    for role in sorted(used):
        for tk in (lock.get(role) or {}).get('takes', []):
            if tk.get('checks'):
                film.append(f"dirty take {tk['file']} ({', '.join(tk['checks'])}): pick another sound for {role}")
    # the lockup is one clean element: no second effect within 3 frames of a hit
    evs = load(project, 'cues.json', {}).get('events', [])
    for h in (e for e in evs if e['kind'] == 'hit'):
        for e in evs:
            if e is not h and abs(e['t'] - h['t']) <= 3.0 / fps:
                per.setdefault(h.get('id'), []).append(f"stacked lockup: {e['kind']} {e['t'] - h['t']:+.3f} s from the hit")
    lo = tl.get('loudness', {})
    lufs, tp = lo.get('integrated_lufs'), lo.get('true_peak_dbtp')
    target = cfg.get('lufs', -14.0)
    if lufs is None or abs(lufs - target) > 1.0:
        film.append(f'integrated loudness {lufs} LUFS, target {target} +-1')
    if tp is not None and tp > -1.0:
        film.append(f'true peak {tp} dBTP, ceiling -1.0')
    return per, film


def asset_findings(project, cfg, times):
    sources = open(os.path.join(project, 'assets', 'SOURCES.md')).read() \
        if os.path.exists(os.path.join(project, 'assets', 'SOURCES.md')) else ''
    found = {}
    for s in cfg['scenes']:
        text = open(os.path.join(project, times[s['id']][2])).read()
        for host in PLACEHOLDER_HOSTS:
            if host in text:
                found.setdefault(s['id'], []).append(f'placeholder asset host: {host}')
        for a in assets_in(text):
            if not os.path.exists(os.path.join(project, a)):
                found.setdefault(s['id'], []).append(f'missing asset: {a}')
            elif os.path.basename(a) not in sources:
                found.setdefault(s['id'], []).append(f'asset not listed in assets/SOURCES.md: {a}')
    return found


def banned_warnings(project, times):
    out = []
    for sid, (_, _, src) in times.items():
        for n, line in enumerate(open(os.path.join(project, src)).read().splitlines(), 1):
            for rx, why in BANNED:
                if rx.search(line):
                    out.append(f'{src}:{n}: {why}')
    return out


def write_stub(stub, kind, key, h, iteration, auto):
    old = front(stub)
    keep = old.get('source_sha') == h  # unchanged sources keep the agent's score and notes
    os.makedirs(os.path.dirname(stub), exist_ok=True)
    body = open(stub).read().split('\n---\n', 1)[1] if keep and os.path.exists(stub) else None
    lines = ['---', f'{kind}: {key}', f'source_sha: {h}', f'iteration: {iteration}']
    lines += [f'{k}: {v}' for k, v in auto.items()]
    lines += [f"score: {old.get('score', '') if keep else ''}", '---']
    if body is None:
        rub = RUBRIC if kind == 'scene' else PAIR_RUBRIC
        body = '## Rubric (2 points each)\n' + ''.join(f'- {r}:\n' for r in rub) + \
            '\n## Evidence\n- frames/ next to this file (open at full size; the contact sheet only locates)\n' + \
            '\n## Fix notes for next iteration\n'
    open(stub, 'w').write('\n'.join(lines) + '\n' + body)
    return front(stub).get('score', '')


def cmd_report(project, mp4):
    cfg = config(project)
    times, duration = scene_times(project, cfg)
    state = load(project, '.loop/state.json', {})
    iteration, cap = state.get('iteration', 1), cfg.get('max_iterations', 5)
    fps, need = cfg.get('fps', 30), cfg.get('pass_score', 8)
    dead = dead_findings(project, cfg, times, cfg.get('freeze_s', 0.5))
    assets = asset_findings(project, cfg, times)
    audio = cfg.get('audio', 'sfx')
    sync, film = sound_findings(project, cfg, fps) if audio != 'none' else ({}, [])
    beats = beat_times(project) if audio == 'music' else None
    if audio == 'music' and beats is None:
        film.append('audio is "music" but no beats/*.json (run hyperframes beats with a music <audio>)')

    unscored, failing = [], []
    for kind, key, h, stub, t0, t1 in units(project, cfg, times):
        auto = {}
        if kind == 'scene':
            probs = dead.get(key, []) + assets.get(key, []) + sync.get(key, [])
            if beats and t0 > 0:
                off = min(abs(t0 - b) for b in beats) * fps
                auto['beat_offset_frames'] = f'{off:.1f}'
                if off > 1:
                    probs.append(f'cut {off:.1f} frames off the beat')
            auto['mechanical'] = '; '.join(probs) or 'clean'
        score = write_stub(stub, kind, key, h, iteration, auto)
        if kind == 'scene' and auto['mechanical'] != 'clean':
            failing.append(f"{key}: {auto['mechanical']}")
        if not re.fullmatch(r'\d+(\.\d+)?', score):
            unscored.append(key)
        elif float(score) < need:
            failing.append(f'{key}: {score}/10')

    warn = banned_warnings(project, times)
    for w in warn:
        print('warn  ' + w)
    for f in film:
        print('film  ' + f)
    for f in failing:
        print('fail  ' + f)
    failing += film
    if unscored and not failing:
        print('waiting for scores: ' + ', '.join(unscored))
        return 2
    if failing:
        if unscored:
            print('also unscored: ' + ', '.join(unscored))
        if iteration >= cap:
            print(f'iteration cap reached ({iteration}/{cap}): stop and show the user the failing units')
            return 4
        return 3
    print(f'pass: {len(times)} scenes and {len(times) - 1} pairs at >= {need}/10, picture and sound clean '
          f'({mp4}). Ask the user to preview before the delivery render.')
    return 0


if __name__ == '__main__':
    cmds = {'cues': cmd_cues, 'stale': cmd_stale, 'report': cmd_report}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    sys.exit(cmds[sys.argv[1]](*sys.argv[2:]) or 0)
