#!/bin/bash
# dead-frames.sh - list frozen and black stretches in a rendered video, read from the encoded pixels.
#
# Usage: dead-frames.sh <video.mp4> [freeze_s=0.5] [black_s=0.1]
# Output (stdout, TSV, absolute seconds): <freeze|black>\t<start>\t<end>
# Exit: 0 always when ffmpeg ran (a clean video prints nothing), 1 on usage or ffmpeg error.
#
# n=0.0003 (about -70 dB) is deliberate: at 0.003 a 100 px word moving on a 1080p frame reads as frozen.
# Picture only: silence in the audio is never a dead frame. Splitting by scene and
# subtracting planned holds happens in video-gate.py, so this stays usable on any MP4.
# bash 3.2-safe (macOS /bin/bash).

set -u

if [ $# -lt 1 ] || [ ! -f "$1" ]; then
  echo "usage: dead-frames.sh <video.mp4> [freeze_s=0.5] [black_s=0.1]" >&2
  exit 1
fi
video=$1
freeze_s=${2:-0.5}
black_s=${3:-0.1}

dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$video") || exit 1

log=$(ffmpeg -hide_banner -nostats -i "$video" -an \
  -vf "freezedetect=n=0.0003:d=${freeze_s},blackdetect=d=${black_s}:pix_th=0.10" \
  -f null - 2>&1) || { echo "dead-frames.sh: ffmpeg failed on $video" >&2; exit 1; }

printf '%s\n' "$log" | awk -v dur="$dur" '
  /freezedetect\.freeze_start/ { split($0, a, ": "); fs = a[2]; open = 1 }
  /freezedetect\.freeze_end/   { split($0, a, ": "); printf "freeze\t%.3f\t%.3f\n", fs, a[2]; open = 0 }
  /black_start:/ {
    s = $0; sub(/.*black_start:/, "", s); split(s, b, " ")
    e = $0; sub(/.*black_end:/, "", e); split(e, c, " ")
    printf "black\t%.3f\t%.3f\n", b[1], c[1]
  }
  END { if (open) printf "freeze\t%.3f\t%.3f\n", fs, dur }   # a freeze that runs to the last frame
'
