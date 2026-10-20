---
title: "Render Engine: HyperFrames Drafts, One Command, Human Approval"
context: video
category: loop
concept: render-engine
description: "Stage 1 of the video loop: HyperFrames seeks HTML frame by frame and encodes MP4; video-loop.sh drives timeline, check, draft render and evidence in one command, and only the user's approval unlocks the delivery render."
tags: video, hyperframes, render, mp4, headless-chrome, gsap, determinism, loop
sources:
  - "references/raw/hyperframes.md"
  - "references/raw/video-loop-brief.md"
last_ingested: 2026-10-20
command: scripts/video-loop.sh
---

## Render Engine: HyperFrames Drafts, One Command, Human Approval

A code-built video is HTML whose motion is a pure function of time. HyperFrames seeks that page one
frame at a time in headless Chrome and encodes the frames with FFmpeg, so the same source renders the
same MP4 every time. The skill never renders on its own; it orchestrates HyperFrames and adds the gate.

**Incorrect (a custom renderer, or a page that plays in real time):**

```js
// Hand-rolled Puppeteer loop + setTimeout-driven animation: frames depend on machine speed,
// a slow frame drops a beat, and nothing reproduces.
await page.goto(url); for (let f = 0; f < 300; f++) { await page.screenshot({ path: `f${f}.png` }); }
```

**Correct (one paused timeline per scene, HyperFrames seeks it):**

```html
<div id="s01-hook" data-composition-id="s01-hook" data-composition-src="compositions/s01-hook.html"
     data-start="0" data-duration="1.7" data-track-index="0" data-width="1920" data-height="1080"></div>
<!-- inside compositions/s01-hook.html, everything in <template>:
     window.__timelines["s01-hook"] = gsap.timeline({ paused: true }); -->
```

### Contract that matters for the loop
- **One sub-composition per scene.** Host id = the file's inner `data-composition-id` = timeline key =
  the scene id in `scenes.json`. A mismatch renders static frames after a 45 s wait per scene.
- **Timing has one source:** `hyperframes timeline --json` (`absStart`/`absEnd` per scene).
  `scenes.json` never stores seconds; scene-local cue offsets live on the scene root (`data-cues`).
- **Drafts are working renders.** Every iteration renders `--quality draft` (about 8.5 s for 5 s of
  1080p on an M-series Mac). The render is skipped when no input changed.
- **Approval point:** after `video-loop.sh` exits 0, open `npx hyperframes preview --background`,
  hand the user the URL, and only after they approve run
  `npx hyperframes render --quality delivery --fps <fps> --output renders/final.mp4`, then
  `bash scripts/dead-frames.sh renders/final.mp4` once more.
- Projects pin `hyperframes@<version>` in `package.json`; the loop uses that pin.

## Sources

- `references/raw/hyperframes.md` - composition contract, CLI behaviour and timings (verified on 0.8.181)
- `references/raw/video-loop-brief.md` - the three-stage loop and the decision to use HyperFrames

## Command

```bash
bash scripts/video-init.sh my-video          # scaffold (hyperframes init + starter scenes)
EARSHOT_PYTHON=/path/to/venv/bin/python bash scripts/video-loop.sh my-video
```
