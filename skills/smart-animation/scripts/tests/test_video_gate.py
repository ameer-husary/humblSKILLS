#!/usr/bin/env python3
"""Hermetic test for video-gate.py: fixture files only, no HyperFrames, earshot, ffmpeg or network.

    python3 scripts/tests/test_video_gate.py      # prints "ok: N checks", exits 1 on the first failure
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('gate', os.path.join(HERE, '..', 'video-gate.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SCENE = '''<template><div id="root" data-composition-id="{id}" data-cues='{cues}'></div>
<script>tl.to('#x', {{ x: 1, ease: springEase(0.5, 0.7, 20) }}, 0);</script></template>'''
GOOD = '''- Intent lands in one viewing: 2 - the word reads at frame 02, before the sweep
- Motion quality (springs, hierarchy, no banned defaults): 2 - spring overshoot visible at frame 03
- Composition and type (hierarchy, spacing, legibility at 1x): 1 - word is small for 1080p at 96 px
- Brand fidelity (real assets, correct colors and fonts): 2 - only the listed mark, palette per PLAN
- Rhythm and sound (gesture-to-sound sync, restraint, level; quote earshot numbers): 1 - keys 0-2 ms, one whoosh
'''
checks = 0


def run(cmd, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = getattr(gate, 'cmd_' + cmd)(*args) or 0
    return code, out.getvalue()


def expect(cond, what, out=''):
    global checks
    checks += 1
    if not cond:
        raise SystemExit(f'FAIL: {what}\n{out}')


def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(text if isinstance(text, str) else json.dumps(text))


def score_all(d, body=GOOD, score='8'):
    for stub in [os.path.join(d, 'critique', f) for f in ('a.md', 'b.md')] + [os.path.join(d, 'critique', 'pairs', 'a__b.md')]:
        text = open(stub).read()
        head, rest = text.split('\n---\n', 1)
        head = '\n'.join(ln if not ln.startswith('score:') else f'score: {score}' for ln in head.splitlines())
        rest = rest.split('## Rubric', 1)[0] + '## Rubric\n' + body + '\n## Fix notes for next iteration\n'
        open(stub, 'w').write(head + '\n---\n' + rest)


def project():
    d = tempfile.mkdtemp(prefix='vgate-')
    write(f'{d}/scenes.json', {'fps': 30, 'pass_score': 8, 'max_iterations': 5, 'audio': 'sfx', 'shared': ['fonts/*'],
                               'scenes': [{'id': 'a', 'intent': 'x', 'holds': []},
                                          {'id': 'b', 'intent': 'y', 'holds': [{'from': 1.5, 'to': 'end', 'reason': 'lockup'}]}]})
    write(f'{d}/index.html', '<div data-composition-id="main"></div>')
    write(f'{d}/fonts/brand.woff2', 'font-v1')
    write(f'{d}/compositions/a.html', SCENE.format(id='a', cues=json.dumps([{'t': 0.3, 'kind': 'key'}, {'t': 1.5, 'kind': 'whoosh.short'}])))
    write(f'{d}/compositions/b.html', SCENE.format(id='b', cues=json.dumps([{'t': 0.2, 'kind': 'hit'}])))
    rows = [{'id': 'a', 'absStart': 0, 'absEnd': 2, 'sourceFile': 'compositions/a.html'},
            {'id': 'b', 'absStart': 2, 'absEnd': 4.5, 'sourceFile': 'compositions/b.html'}]
    write(f'{d}/.loop/timeline.json', {'timeline': {'duration': 4.5, 'tracks': [{'rows': rows}]}})
    write(f'{d}/.loop/dead.tsv', 'freeze\t3.600\t4.500\n')  # inside b's hold (3.5-4.5): planned
    write(f'{d}/audio/kit/kit.lock.json', {'roles': {
        'key': {'align': 'onset', 'takes': [{'file': 'key_1.wav', 'checks': []}]},
        'whoosh.short': {'align': 'peak', 'takes': [{'file': 'whoosh-short_1.wav', 'checks': []}]},
        'hit': {'align': 'onset', 'takes': [{'file': 'hit_1.wav', 'checks': []}]}}})
    write(f'{d}/critique/audio/listen.json', {'loudness': {'integrated_lufs': -14.1, 'true_peak_dbtp': -1.3}, 'sync': {'cues': {'items': [
        {'t': 0.3, 'kind': 'key', 'id': 'a', 'offset_ms': 2.0, 'status': 'OK'},
        {'t': 1.5, 'kind': 'whoosh.short', 'id': 'a', 'offset_ms': -37.0, 'status': 'near'},
        {'t': 2.2, 'kind': 'hit', 'id': 'b', 'offset_ms': 0.0, 'status': 'OK'}]}}})
    write(f'{d}/PLAN.md', '# plan\nmessage: TODO\n| a | hook |\n| b | lockup |\napproved:\n')
    return d


def main():
    d = project()
    try:
        code, out = run('plan', d)
        expect(code == 1 and 'TODO' in out and 'approved' in out, 'plan with TODO and no approval is refused', out)
        write(f'{d}/PLAN.md', '# plan\nmessage: ship it\n| a | hook |\n| b | lockup |\napproved: 2026-10-20, user\n')
        expect(run('plan', d)[0] == 0, 'filled, approved plan passes')

        code, out = run('cues', d)
        cues = json.load(open(f'{d}/cues.json'))['events']
        expect([round(c['t'], 2) for c in cues] == [0.3, 1.5, 2.2] and cues[2]['id'] == 'b', 'cues become absolute', out)

        code, out = run('report', d, 'x.mp4')
        expect(code == 2, 'fresh stubs wait for scores', out)

        score_all(d, body='- Intent lands in one viewing: 2\n', score='8')
        code, out = run('report', d, 'x.mp4')
        expect(code == 2 and 'not counted' in out, 'a bare score without reasons is not counted', out)

        score_all(d, score='9')
        code, out = run('report', d, 'x.mp4')
        expect(code == 2 and 'sum to 8' in out, 'rubric lines must sum to the score', out)

        score_all(d)
        code, out = run('report', d, 'x.mp4')
        expect(code == 0, 'reasoned scores, clean evidence, planned freeze -> pass', out)

        write(f'{d}/fonts/brand.woff2', 'font-v2')
        code, out = run('report', d, 'x.mp4')
        expect(code == 2, 'editing a shared file clears every score', out)
        score_all(d)
        write(f'{d}/index.html', '<div data-composition-id="main" style="background:#000"></div>')
        expect(run('report', d, 'x.mp4')[0] == 2, 'editing the host (index.html) clears every score')
        score_all(d)
        expect(run('report', d, 'x.mp4')[0] == 0, 'rescored after shared edits -> pass')

        write(f'{d}/.loop/dead.tsv', 'freeze\t0.900\t1.600\n')
        code, out = run('report', d, 'x.mp4')
        expect(code == 3 and 'freeze 0.90-1.60' in out, 'unplanned freeze fails the scene', out)
        write(f'{d}/.loop/dead.tsv', '')

        cfg = json.load(open(f'{d}/scenes.json'))
        cfg['scenes'][1]['holds'] = [{'from': 0.5, 'to': 'end', 'reason': 'long rest'}]
        write(f'{d}/scenes.json', cfg)
        code, out = run('report', d, 'x.mp4')
        expect(code == 3 and 'holds cover 80%' in out, 'a hold over 40% of the scene fails', out)
        cfg['scenes'][1]['holds'] = [{'from': 1.5, 'to': 'end', 'reason': 'lockup'}]
        write(f'{d}/scenes.json', cfg)
        run('report', d, 'x.mp4')  # stubs take the restored sources' hash, then get rescored
        score_all(d)
        expect(run('report', d, 'x.mp4')[0] == 0, 'restored hold, rescored -> pass')

        lock = json.load(open(f'{d}/audio/kit/kit.lock.json'))
        lock['roles']['key']['takes'][0]['checks'] = ['clicks']
        write(f'{d}/audio/kit/kit.lock.json', lock)
        code, out = run('report', d, 'x.mp4')
        expect(code == 3 and 'dirty take key_1.wav' in out, 'a dirty take fails the film', out)
        lock['roles']['key']['takes'][0]['checks'] = []
        write(f'{d}/audio/kit/kit.lock.json', lock)

        ev = json.load(open(f'{d}/cues.json'))
        ev['events'].append({'t': 2.25, 'kind': 'pop', 'id': 'b'})
        write(f'{d}/cues.json', ev)
        code, out = run('report', d, 'x.mp4')
        expect(code == 3 and 'stacked lockup' in out, 'a second cue within 3 frames of the hit fails', out)
        run('cues', d)

        listen = json.load(open(f'{d}/critique/audio/listen.json'))
        listen['sync']['cues']['items'][0]['status'] = 'near'
        write(f'{d}/critique/audio/listen.json', listen)
        code, out = run('report', d, 'x.mp4')
        expect(code == 3 and 'key at 0.30' in out and 'whoosh' not in out.split('fail')[-1],
               'onset roles need 1 frame; peak-aligned whoosh passes at 37 ms', out)
        listen['sync']['cues']['items'][0]['status'] = 'OK'
        listen['loudness']['integrated_lufs'] = -17.0
        write(f'{d}/critique/audio/listen.json', listen)
        code, out = run('report', d, 'x.mp4')
        expect(code == 3 and 'integrated loudness -17.0' in out, 'loudness off target fails the film', out)

        write(f'{d}/.loop/state.json', {'iteration': 5})
        expect(run('report', d, 'x.mp4')[0] == 4, 'failing at the iteration cap exits 4')
        write(f'{d}/.loop/state.json', {'iteration': 1})
        listen['loudness']['integrated_lufs'] = -14.1
        write(f'{d}/critique/audio/listen.json', listen)
        code, out = run('report', d, 'x.mp4')
        expect(code == 0, 'back to clean -> pass', out)

        write(f'{d}/critique/final/listen.json', listen)
        write(f'{d}/.loop/dead-final.tsv', 'black\t0.000\t0.200\n')
        code, out = run('final', d, 'final.mp4')
        expect(code == 3 and 'black 0.00-0.20' in out, 'the delivery render is checked again', out)
        write(f'{d}/.loop/dead-final.tsv', '')
        code, out = run('final', d, 'final.mp4')
        expect(code == 0 and 'ask the user' in out, 'clean final asks the user to watch', out)
    finally:
        shutil.rmtree(d)
    print(f'ok: {checks} checks')


if __name__ == '__main__':
    main()
