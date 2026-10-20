#!/bin/bash
# video-loop.sh - one pass of the render -> evidence -> gate loop for a video-init project.
#
# Usage: video-loop.sh [dir=.]
#   1. timeline + scene data-cues -> cues.json      (hyperframes timeline is the only timing source)
#   2. sound: earshot kit takes on cues -> audio/soundtrack.wav   (scenes.json "audio" != "none")
#   3. hyperframes check (lint included)            -> stop on errors
#   4. draft render, only when an input changed     -> renders/draft-<n>.mp4
#   5. evidence: dead frames, earshot listening, fresh frames for changed scenes and cuts
#   6. gate: critique stubs, scores, mechanical rules
# Then the agent scores the stubs in critique/ and runs this again.
#
# Exit: 0 pass (ask the user to preview, then render --quality delivery)
#       1 tool error (check failed, render failed, earshot missing)
#       2 waiting for scores   3 failing   4 iteration cap reached while failing
#
# Env: EARSHOT_PYTHON  a python that can `import earshot` (default python3)
# bash 3.2-safe; JSON work is delegated to video-gate.py (stdlib python3).

set -u

here=$(cd "$(dirname "$0")" && pwd)
dir=${1:-.}
cd "$dir" || exit 1
[ -f scenes.json ] || { echo "video-loop.sh: no scenes.json in $dir (scaffold with video-init.sh)" >&2; exit 1; }

hfv=$(sed -n 's/.*hyperframes@\([0-9][0-9.]*\).*/\1/p' package.json 2>/dev/null | head -1)
hf() { npx -y "hyperframes@${hfv:-latest}" "$@"; }
gate() { python3 "$here/video-gate.py" "$@"; }
cfg() { python3 -c "import json,sys; print(json.load(open('scenes.json')).get(sys.argv[1], sys.argv[2]))" "$1" "$2"; }
die() { echo "video-loop.sh: $*" >&2; exit 1; }
epy=${EARSHOT_PYTHON:-python3}
audio=$(cfg audio sfx)
fps=$(cfg fps 30)
mkdir -p .loop renders critique/pairs

# 1. timing
hf timeline --json > .loop/timeline.json 2> .loop/timeline.err || die "hyperframes timeline failed (.loop/timeline.err)"
cues=$(gate cues .) || exit 1
set -- $cues
dur=$1
echo "timeline: ${dur} s, $2 cues"

# 2. sound
if [ "$audio" != "none" ]; then
  "$epy" -c 'import earshot' 2>/dev/null || die "earshot not importable by $epy. Install (tested pin): uv venv -p 3.12 ~/.venvs/earshot && VIRTUAL_ENV=~/.venvs/earshot uv pip install --extra-index-url https://download.pytorch.org/whl/cpu 'earshot @ git+https://github.com/Leonxlnx/earshot@925ebe5', then EARSHOT_PYTHON=~/.venvs/earshot/bin/python, or set \"audio\": \"none\""
  "$epy" "$here/video-sound.py" build . cues.json "$dur" > .loop/sound.json 2> .loop/sound.err || die "sound build failed (.loop/sound.err)"
  echo "sound: $(cat .loop/sound.json)"
  if [ "$audio" = "music" ]; then
    hf beats --json > .loop/beats.json 2> .loop/beats.err || die "hyperframes beats failed (.loop/beats.err); a music <audio> needs data-timeline-role=\"music\""
  fi
fi

# 3. check
hf check --json > .loop/check.json 2> .loop/check.err
python3 - <<'EOF' || die "hyperframes check failed; fix the errors above, then rerun"
import json, sys
d = json.load(open('.loop/check.json'))
for sec in ('lint', 'runtime', 'layout', 'motion', 'contrast'):
    for f in (d.get(sec) or {}).get('findings', []):
        if f.get('severity') == 'error':
            print(f"check {sec}: {f.get('code')} {f.get('sourceFile', '')} {f.get('selector', '')} {f.get('message', '')}")
sys.exit(0 if d.get('ok') else 1)
EOF

# 4. render (draft), skipped when no input changed since the last render
inputs=$(find index.html compositions assets audio/soundtrack.wav scenes.json -type f 2>/dev/null | LC_ALL=C sort | xargs shasum 2>/dev/null | shasum | cut -c1-12)
set -- $(python3 -c "
import json, os
s = json.load(open('.loop/state.json')) if os.path.exists('.loop/state.json') else {}
same = s.get('inputs') == '$inputs' and os.path.exists(s.get('mp4', ''))
n = s.get('iteration', 0) if same else s.get('iteration', 0) + 1
print(n, 'reuse' if same else 'render')")
iter=$1
mp4="renders/draft-${iter}.mp4"
if [ "$2" = "render" ]; then
  echo "render: iteration $iter (draft)"
  hf render --quality draft --fps "$fps" --output "$mp4" > .loop/render.log 2>&1 || die "render failed (.loop/render.log)"
  python3 -c "import json; json.dump({'iteration': $iter, 'inputs': '$inputs', 'mp4': '$mp4'}, open('.loop/state.json', 'w'))"
  rm -f critique/audio/listen.json
else
  echo "render: inputs unchanged, reusing $mp4"
fi
got=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$mp4")
python3 -c "import sys; sys.exit(abs($got - $dur) > 1.0 / $fps)" || die "$mp4 is ${got} s, timeline says ${dur} s"

# 5. evidence
bash "$here/dead-frames.sh" "$mp4" "$(cfg freeze_s 0.5)" > .loop/dead.tsv || die "dead-frames.sh failed"
if [ "$audio" != "none" ] && [ ! -f critique/audio/listen.json ]; then
  echo "listen: earshot timeline + sheet + critique (models load once, ~1.1 GB on first use)"
  "$epy" "$here/video-sound.py" listen . cues.json "$mp4" > .loop/listen.json 2> .loop/listen.err || die "earshot listening failed (.loop/listen.err)"
fi
gate stale . > .loop/stale.txt || exit 1
while read -r kind a b c d e; do
  if [ "$kind" = "scene" ]; then out=$d; args="--composition $a --frames 8"; label=$a
  else out=$e; args="--range $c:$d --frames 6"; label="$a | $b"; fi
  rm -rf "$out"
  # shellcheck disable=SC2086
  hf snapshot $args --output "$out" > /dev/null 2>&1 || die "snapshot failed for $label"
  echo "frames: $label -> $out"
done < .loop/stale.txt

# 6. gate
gate report . "$mp4"
