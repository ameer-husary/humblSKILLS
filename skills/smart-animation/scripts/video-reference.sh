#!/bin/bash
# video-reference.sh - measure a reference video so a plan can borrow its style, not its content.
#
# Usage: video-reference.sh <reference.mp4> <out_dir>
#   Writes <out_dir>/STYLE.md (measured facts + a style sheet for the agent to fill) and evidence:
#   shots.tsv (hard cuts), palette.txt (dominant colors), motion-NN.jpg (6 fps strips of 2 s windows),
#   contact.jpg, and listen.txt (earshot sections, BPM, voice, sync) when EARSHOT_PYTHON imports earshot.
#   Spoken words: run the smart-watch skill on the same file for a timestamped transcript.
#
# The reference is evidence only: never copy its logos, footage, copy or brand colors into the new video.
# Exit: 0 written, 1 usage or ffmpeg error. bash 3.2-safe.

set -u

if [ $# -ne 2 ] || [ ! -f "$1" ]; then
  echo "usage: video-reference.sh <reference.mp4> <out_dir>" >&2
  exit 1
fi
ref=$1
out=$2
mkdir -p "$out" || exit 1
epy=${EARSHOT_PYTHON:-python3}

meta=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration \
  -of default=nw=1 "$ref") || { echo "video-reference.sh: ffprobe failed" >&2; exit 1; }
dur=$(printf '%s\n' "$meta" | sed -n 's/^duration=//p')

# hard cuts: a scene score over 0.25 on a 640 px proxy (soft morphs and pushes stay under it)
ffmpeg -hide_banner -nostats -i "$ref" -an -vf "scale=640:-1,select='gt(scene,0.25)',showinfo" -f null - 2>&1 \
  | sed -n 's/.*pts_time:\([0-9.]*\).*/\1/p' > "$out/shots.tsv"

# dominant colors over 1 frame per second
ffmpeg -v error -y -i "$ref" -vf "fps=1,scale=320:-1,palettegen=max_colors=32:reserve_transparent=0" \
  -frames:v 1 "$out/.palette.png" || exit 1
ffmpeg -v error -y -i "$out/.palette.png" -f rawvideo -pix_fmt rgb24 "$out/.palette.rgb" || exit 1
ffmpeg -v error -y -i "$ref" -vf "fps=1/2,scale=160:-1" -f rawvideo -pix_fmt rgb24 "$out/.frames.rgb" || exit 1
python3 - "$out" <<'EOF'
import sys
d = sys.argv[1]
raw = open(f'{d}/.palette.rgb', 'rb').read()
import colorsys
cols = sorted({tuple(raw[i:i + 3]) for i in range(0, len(raw) - 2, 3)})
sat = lambda c: colorsys.rgb_to_hsv(*(v / 255 for v in c))[1]
lum = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
neutrals = sorted((c for c in cols if sat(c) < 0.25), key=lum)
# accents cover small areas that a palette quantizer averages away: bucket saturated pixels by hue
fr = open(f'{d}/.frames.rgb', 'rb').read()
buckets = {}
for i in range(0, len(fr) - 2, 3):
    c = tuple(fr[i:i + 3])
    h, sv, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
    if sv > 0.35 and v > 0.25:
        b = buckets.setdefault(int(h * 12), [0, 0, 0, 0])
        b[0] += 1; b[1] += c[0]; b[2] += c[1]; b[3] += c[2]
total = len(fr) // 3
accents = [(b[1] // b[0], b[2] // b[0], b[3] // b[0]) for b in sorted(buckets.values(), reverse=True)
           if b[0] / total > 0.0001][:3]  # the reference accent covered 0.05% of pixels
hexs = lambda cs: ' '.join('#%02x%02x%02x' % c for c in cs)
step = max(1, len(neutrals) // 6)
open(f'{d}/palette.txt', 'w').write(f'neutrals: {hexs(neutrals[::step])}\naccents: {hexs(accents) or "none"}\n')
EOF
rm -f "$out/.palette.png" "$out/.palette.rgb" "$out/.frames.rgb"

# motion strips: six 2 s windows spread over the film, 6 frames per second, gray padding
for i in 1 2 3 4 5 6; do
  at=$(python3 -c "print(round($dur * $i / 7, 2))")
  ffmpeg -v error -y -ss "$at" -t 2 -i "$ref" -vf "fps=6,scale=480:-1,tile=6x2:color=0x808080" \
    -frames:v 1 "$out/motion-0$i.jpg" || exit 1
done
ffmpeg -v error -y -i "$ref" -vf "fps=1/$(python3 -c "print(max(1, round($dur / 24)))"),scale=480:-1,tile=6x4:color=0x808080" \
  -frames:v 1 "$out/contact.jpg" || exit 1

loud=$(ffmpeg -hide_banner -nostats -i "$ref" -vn -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p' \
  | grep -E '^ *(I|LRA|Peak):' | sed 's/^ *//; s/  */ /g' | tr '\n' ';')

if "$epy" -c 'import earshot' 2>/dev/null; then
  "$epy" -c "
from earshot import api
tl = api.timeline('$ref', video='$ref')
print(tl.get('summary', ''))
" > "$out/listen.txt" 2>/dev/null || echo "earshot timeline failed" > "$out/listen.txt"
else
  echo "earshot not available (set EARSHOT_PYTHON): no sound sections, BPM or voice detection" > "$out/listen.txt"
fi

python3 - "$out" "$dur" "$loud" "$meta" <<'EOF'
import statistics, sys
d, dur, loud, meta = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
cuts = [float(x) for x in open(f'{d}/shots.tsv').read().split()]
edges = [0.0] + cuts + [dur]
shots = [b - a for a, b in zip(edges, edges[1:]) if b > a]
pal = open(f'{d}/palette.txt').read().strip().replace('\n', '; ')
listen = open(f'{d}/listen.txt').read().strip()
m = dict(l.split('=', 1) for l in meta.splitlines() if '=' in l)
md = f"""# Style evidence

Measured by video-reference.sh. The reference is evidence only: take its grammar (pacing, motion
vocabulary, sound layers), never its logos, footage, words or brand colors.

## Measured
- format: {m.get('width')}x{m.get('height')} at {m.get('r_frame_rate')} fps, {dur:.1f} s
- hard cuts: {len(cuts)} ({len(cuts) / dur * 60:.1f} per minute); shots median {statistics.median(shots):.1f} s, \
longest {max(shots):.1f} s. Few cuts means motion carries the transitions (morphs, pushes, in-place rebuilds).
- palette (1 fps sample, dark to light; accents = most saturated): {pal}
- loudness: {loud}
- sound (earshot): {listen[:1500]}
- evidence: contact.jpg (whole film), motion-01..06.jpg (2 s at 6 fps: read how things move), shots.tsv

## Style sheet (fill in from the evidence, in your own words; this feeds PLAN.md)
- ground / ink / accent roles (not their hex if it is a brand color): TODO
- type: families by role (headline, body, data), weights, the headline treatment: TODO
- motion vocabulary (how text enters, how UI assembles, what moves the eye between moments): TODO
- transition grammar (cut, morph, push, rebuild in place) and how often: TODO
- pacing: words per minute of narration if any, seconds per idea, where it breathes: TODO
- sound layers (voice, music bed and its BPM / mood, effects density) and the loudness to aim for: TODO
- what NOT to copy from this reference: TODO
"""
open(f'{d}/STYLE.md', 'w').write(md)
EOF
echo "wrote $out/STYLE.md (+ contact.jpg, motion-0[1-6].jpg, shots.tsv, palette.txt, listen.txt)"
