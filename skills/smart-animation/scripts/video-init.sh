#!/bin/bash
# video-init.sh - scaffold a HyperFrames project wired for the video loop.
#
# Usage: video-init.sh <dir>
#   Runs `npx hyperframes init <dir>` (non-interactive), then adds the starter scenes
#   (two springs-only scenes with data-cues), scenes.json, PLAN.md, assets/SOURCES.md and critique/.
#   Next: fill PLAN.md with the user, write the scenes, then run video-loop.sh <dir> until it exits 0.
#
# Set HYPERFRAMES_SKIP_SKILLS=1 to stop `hyperframes init` refreshing its agent skills.
# Exit: 0 scaffolded, 1 usage error, existing dir, or init failure. bash 3.2-safe.

set -u

if [ $# -ne 1 ]; then
  echo "usage: video-init.sh <dir>" >&2
  exit 1
fi
dir=$1
here=$(cd "$(dirname "$0")" && pwd)
tpl="$here/templates/video"

if [ -e "$dir" ]; then
  echo "video-init.sh: $dir already exists; pick a new directory" >&2
  exit 1
fi
command -v npx >/dev/null 2>&1 || { echo "video-init.sh: npx not found (Node 22+ required)" >&2; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "video-init.sh: ffmpeg not found (brew install ffmpeg)" >&2; exit 1; }

npx -y hyperframes init "$dir" --non-interactive >/dev/null || { echo "video-init.sh: hyperframes init failed" >&2; exit 1; }

cp "$tpl/index.html" "$dir/index.html"
mkdir -p "$dir/compositions" "$dir/assets" "$dir/audio" "$dir/critique/pairs"
cp "$tpl/compositions/"*.html "$dir/compositions/"
cp "$tpl/scenes.json" "$dir/scenes.json"
cp "$tpl/PLAN.md" "$dir/PLAN.md"
# GSAP vendored into the project: renders never depend on a CDN being up or unchanged
mkdir -p "$dir/assets/vendor"
curl -fsSL "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js" -o "$dir/assets/vendor/gsap.min.js" \
  || { echo "video-init.sh: could not download gsap 3.14.2" >&2; exit 1; }
cat > "$dir/assets/SOURCES.md" <<'EOF'
# Asset sources

One line per file in assets/: `<filename> - <where it came from> - <license or owner>`.
The loop fails a scene that uses an asset not listed here, or a placeholder image host.

gsap.min.js - GSAP 3.14.2 from jsDelivr (vendor/) - GreenSock standard license
EOF
cat >> "$dir/.gitignore" <<'EOF'
renders/
.loop/
critique/**/frames/
EOF

echo "scaffolded $dir"
echo "next: fill $dir/PLAN.md with the user (one question at a time), write the scenes, then: bash $here/video-loop.sh $dir"
