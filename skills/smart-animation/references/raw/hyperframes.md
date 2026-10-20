# HyperFrames (heygen-com/hyperframes) - distilled notes

Source: https://github.com/heygen-com/hyperframes (README, skills/hyperframes-cli,
skills/hyperframes-keyframes, skills/hyperframes-core references, hyperframes-cli/references/beats.md
and lint-validate-inspect.md). Read 2026-10-20 at CLI v0.8.181. Apache-2.0, Node >= 22, FFmpeg.
68.3k stars, pushed 2026-10-20. All CLI behaviour below was run locally on 0.8.181 unless marked.

## What it is
HTML + CSS + seekable animation (GSAP default) -> deterministic MP4. Headless Chrome seeks each frame;
FFmpeg encodes. Built for agents; ships 21 agent skills (router `/hyperframes`, domain skills
`hyperframes-core`, `-animation`, `-keyframes`, `-creative`, `-cli`, `-audio`, `-registry`, `media-use`).
`npx hyperframes skills update` installs the core set. NOTE: `hyperframes init` also refreshes the
core skills into ~/.claude/skills and ~/.agents/skills; `HYPERFRAMES_SKIP_SKILLS=1` opts out.

## Composition contract (hyperframes-core)
- Root `<div data-composition-id="main" data-start data-duration data-width data-height>`; one paused
  GSAP timeline per composition registered on `window.__timelines[id]`.
- Scenes as sub-compositions: host `<div data-composition-id="X" data-composition-src="compositions/x.html"
  data-start data-duration data-track-index data-width data-height>`; the file wraps EVERYTHING (style,
  markup, script) in `<template>` - the runtime clones only template contents. Host id == inner id ==
  timeline key, or the render waits 45 s per scene and captures static frames.
- Style the sub-composition root by `#root`, never a class (lint error).
- Only deterministic logic: no Date.now(), Math.random(), network fetches.
- Media: `<audio>` needs an `id` (else the render is silent); never `crossorigin`; `data-volume`;
  scene-local `data-start` inside sub-compositions; HyperFrames owns playback (no .play()).
- Root `data-fps` sets fps; `render --fps` overrides.

## CLI (verified)
- `init <dir> --non-interactive` -> index.html (GSAP from jsDelivr), hyperframes.json, meta.json,
  package.json with scripts pinned to `hyperframes@<version>`, AGENTS.md/CLAUDE.md.
- `lint` (fast), `check` (lint + runtime + layout + motion + contrast in one browser pass; required gate).
  `check --json` -> `{ok, strict, browserSkipped, lint, runtime, layout, motion, contrast, hdr, snapshots}`,
  each section `{ok, errorCount, warningCount, infoCount, findings[]}`; findings carry code, severity,
  time, selector, sourceFile, bbox, fixHint. Text sweeping off-canvas is info `canvas_overflow`
  (mark intentional with `data-layout-allow-overflow`). `sweep_static` fails a 3 s+ composition with
  no visible change. `*.motion.json` sidecars assert motion intent (appearsBy, stagger, maxStaticSec).
- `timeline --json` -> `{timeline: {duration, tracks: [{kind, rows: [{id, start, duration, end,
  absStart, absEnd, sourceFile, src, children, ...}]}]}}`. Absolute times for every sub-composition.
- `snapshot --composition <id> --frames N --output DIR` / `--range A:B --frames N` / `--at t1,t2`:
  PNGs named `frame-NN-at-<t>s.png` plus `contact-sheet.jpg`. Managed storage (no --output) keeps only
  the newest 10 runs, so copy evidence out.
- `render --quality draft|looks|delivery --fps N --output PATH`. 4.2-5 s 1080p draft: ~8.5 s render
  (setup 4 s, capture 4 s) on Apple M5 Pro, drawelement capture, hardware GPU.
- `beats [dir] --json` decodes the `<audio data-timeline-role="music">` (or id containing music/bgm/
  soundtrack) and writes `beats/<audio-path>.json` = `{version: 1, audio, beats: [{time, strength}]}`.
  A 4.2 s drum bed returned "No beats detected"; a 16 s 120 BPM bed returned 32 beats at 120.1 BPM,
  first at 0.505 s. Give the tracker a full-length track.
- The HyperFrames skills say "render only after approval"; drafts for self-critique are working renders.

## Determinism and freeze detection gotcha
FFmpeg `freezedetect` at the common n=0.003 reads a 100 px word moving on a 1080p canvas as frozen;
n=0.0003 (about -70 dB) matched what the frames showed.
