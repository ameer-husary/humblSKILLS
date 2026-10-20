---
name: smart-animation
description: >
  Performance-first frontend animation and transition guidance, routed by
  codebase (HTML, CSS, JavaScript, TypeScript, React) and by ready-made
  libraries (thinking-orbs, border-beam, metal-fx, liquid-gooey,
  transitions.dev, Canvas UI, Motion/Framer Motion, React Bits, Beautiful UI), plus a
  code-built video loop (HyperFrames render, earshot sound, self-critique).
  Use when adding animations, transitions, page or route transitions, scroll
  reveals, hover micro-interactions, loading/thinking indicators, or agent UI
  states (streaming text, tool calls, approval gates); when the user says
  "animate this", "add motion", "make it feel premium", "page transition",
  "reveal on scroll", or asks which animation library to use; or for
  "make a video", "intro video", "launch video", "render to MP4" or
  sound effects on a video. Enforces compositor-only performance and a
  reduced-motion floor. For whole-interface
  design direction use smart-frontend-design. Do NOT use for non-frontend
  work or static visual design with no motion.
license: MIT
compatibility: Requires bash, POSIX utilities (awk, sed, find, grep), python3, writable filesystem at the skill target path. The video loop also needs Node 22+ (npx hyperframes), ffmpeg/ffprobe, Chrome, and for sound a Python with earshot installed (CPU torch, ~1.1 GB models on first listen).
metadata:
  author: jjfantini
  version: "0.6.0"
  previous_names: ["use-smart-animation"]
  category: design
  tags: [animation, transitions, frontend, motion, css, react, webgl, performance, accessibility, agent-ui, video, hyperframes, earshot, humblskill]
  platforms: [claude-code, cursor, codex]
  preserve:
    - references/raw/
    - references/wiki/
    - references/decisions.md
    - references/log.md
    - references/patterns.md
---

# Smart Animation

Give any frontend the right motion for its stack: read the shared principles,
then load only the file for the language you're in and the library you're
reaching for. Motion is deliberate here — one orchestrated moment beats
scattered effects, everything animates on compositor-only properties, and every
snippet honors `prefers-reduced-motion`.

## Brain Protocol (read BEFORE animating anything)

1. `references/_index.md`    - what this skill knows (map)
2. `references/patterns.md`  - what worked, with numbers
3. `references/decisions.md` - past reasoning, don't repeat mistakes
4. `references/log.md`       - last 5 session entries
5. The relevant `references/wiki/<context>/<category>/` concepts (see routing below)

After completing work, UPDATE the brain:
- New user-provided material -> `references/raw/` (never renamed or edited)
- Distilled insights -> new/updated `references/wiki/<ctx>/<cat>/<concept>.md`,
  citing every raw file used in `sources:`
- Quantified results (fps, bundle size, LCP) -> `patterns.md`
- Non-obvious decisions -> `decisions.md`
- Session summary (always) -> append to `log.md`
- Run `scripts/lint.sh` to regenerate `_index.md` and verify structure

_Full spec: `references/_brain.md`._

## CCCCC Architecture

| Layer        | Role                                | Location                                       |
|--------------|-------------------------------------|------------------------------------------------|
| **Core**     | Root structure of the skill         | `SKILL.md`, `references/`, `scripts/`          |
| **Context**  | Top-level grouping                   | 1st segment under `references/wiki/` (`motion`, `lang`, `lib`) |
| **Category** | Specific topic within a context      | 2nd segment (`principles`; `css`/`react`/…; `orbs`/`beams`/…) |
| **Concept**  | One atomic idea per file             | Filename stem + required frontmatter field     |
| **Command**  | Deterministic executable script      | `scripts/lint.sh`, `scripts/video-*.{sh,py}`, `scripts/dead-frames.sh` |

## When to Use

- Adding or reviewing animations/transitions in a web frontend
- Choosing a motion approach for a specific language (HTML/CSS/JS/TS/React)
- Wiring one of the nine bundled libraries (orbs, border-beam, metal-fx, liquid-gooey, transitions.dev, Canvas UI, Motion, React Bits, Beautiful UI)
- Building the UI around an agent: thinking states, streaming answers, tool calls, human-in-the-loop approval
- Page/route transitions, scroll reveals, hover micro-interactions, loading states
- Fixing janky animation (dropped frames) or missing reduced-motion handling
- Making a short animation video in code (intro, launch film, explainer, logo sting) and rendering it to MP4

## How to Use

**Always read first — the shared principles apply to every task:**
Read `references/wiki/motion/principles/design.md` (where/if to animate),
`references/wiki/motion/principles/performance.md` (compositor-only, 60fps),
and `references/wiki/motion/principles/accessibility.md` (reduced-motion floor + tokens).

**Then route by the codebase language:**

- **CSS-only / static site:** Read `references/wiki/lang/css/animation.md`
- **Plain HTML:** Read `references/wiki/lang/html/animation.md`
- **Vanilla JavaScript:** Read `references/wiki/lang/js/animation.md`
- **TypeScript (non-React):** Read `references/wiki/lang/ts/animation.md`
- **React / Next.js:** Read `references/wiki/lang/react/animation.md`

**And route by the effect / library you need:**

- **Thinking / loading indicator for an AI or agent UI:** Read `references/wiki/lib/orbs/usage.md` (thinking-orbs)
- **Animated glow around a card, button, or input border:** Read `references/wiki/lib/beams/usage.md` (border-beam)
- **Metallic / liquid-metal accent on one premium element:** Read `references/wiki/lib/metal/usage.md` (metal-fx)
- **Elements that merge like drops of liquid (expanding FAB cluster, morphing card, slider thumb with a rubbery trail):** Read `references/wiki/lib/gooey/usage.md` (liquid-gooey)
- **Standard UI transitions (modals, toasts, tabs) in any stack:** Read `references/wiki/lib/transitions/usage.md` (transitions.dev)
- **Creative canvas/WebGL effects over content (particle reveal, liquid, glass, shatter) for a hero or signature moment:** Read `references/wiki/lib/canvas-ui/usage.md` (Canvas UI)
- **Exit animations, layout/FLIP animation, spring physics, or interruptible orchestration in React:** Read `references/wiki/lib/motion-react/usage.md` (Motion, formerly Framer Motion) — the four things CSS cannot do
- **A specific finished effect (split-text reveal, aurora background, magnet button) from a large catalog:** Read `references/wiki/lib/react-bits/usage.md` (React Bits) — check the per-component dependency cost first
- **AI / agent interface states — thinking traces, streaming text, tool chips, approval gates, confidence, context cards, diffs:** Read `references/wiki/lib/beautiful-ui/usage.md` (Beautiful UI)

**And route video work (a rendered MP4, not live UI motion):**

- **Make / fix an animation video (render loop, scoring, sound):** Read all four
  `references/wiki/video/loop/` concepts in order: `render-engine.md` (HyperFrames, one command,
  approval point), `reference-assets.md` (real assets, closed-form springs, banned defaults),
  `sound.md` (earshot kits on picture cues, effects-only default, music mode) and `self-critique.md`
  (rubric, adjacent pairs, mechanical rules, exit codes). Install HyperFrames' own skills
  (`npx hyperframes skills update`) for the composition contract.

**Live enumeration of everything this skill knows:**
Read `references/_index.md` (auto-regenerated by `scripts/lint.sh`).

**Brain protocol, naming, linking contract, lint checks, `patterns.md` shape:**
Read `references/_brain.md`. **Wiki concept file shape:** Read `references/_template.md`.

### Scripts

- `scripts/lint.sh` — brain health check: regenerates `_index.md`, validates
  every wiki file's path/frontmatter triple and that each cites a real
  `references/raw/` source. Run after editing any wiki concept.
- `scripts/video-init.sh <dir>` — `hyperframes init` plus two starter scenes (springs, `data-cues`),
  `scenes.json`, `assets/SOURCES.md`, `critique/`.
- `scripts/video-loop.sh [dir]` — one loop pass: timeline -> cues -> sound -> check -> draft render ->
  dead frames, earshot listening, frames for changed scenes and cuts -> gate. Exit 0 pass, 1 tool
  error, 2 waiting for scores, 3 failing, 4 iteration cap. Set `EARSHOT_PYTHON`.
- `scripts/dead-frames.sh <mp4>` — freeze/black stretches from the encoded pixels (TSV).
- `scripts/video-sound.py`, `scripts/video-gate.py` — the sound build/listen and the gate, called by
  `video-loop.sh`.

## Examples

### Example 1: "Add a page-load animation to my React landing page"

1. Read the three `motion/principles/*` concepts (deliberate, performant, accessible).
2. Read `lang/react/animation.md` — decision rule says use CSS for the entrance,
   or Motion only if you need staggered orchestration/exit.
3. Implement ONE orchestrated entrance (staggered children), compositor-only
   (`transform`/`opacity`), with a `prefers-reduced-motion` fallback.
4. If they want a premium accent on the CTA, read `lib/metal/usage.md` and gate
   the shader with `paused` under reduced motion.
5. Append a `log.md` entry; if you measured LCP/fps, add a `patterns.md` entry.

### Example 2: "Make my modals and toasts feel polished in a plain HTML/CSS site"

1. Read the `motion/principles/*` concepts.
2. Read `lib/transitions/usage.md` — copy the `t-*` pattern (open + closing
   states, motion tokens) or install the upstream transitions.dev skill.
3. Read `lang/html/animation.md` — prefer `<dialog>`/Popover so the motion hangs
   on accessible native elements.
4. Verify each transition keeps its `@media (prefers-reduced-motion: reduce)` block.

### Example 3: "Make a 15-second launch video for my CLI, with sound"

1. Read the four `video/loop/*` concepts; `bash scripts/video-init.sh launch`.
2. Put real assets in `launch/assets/` and list them in `SOURCES.md`; write one scene per beat of
   the story as a sub-composition, its sound events in `data-cues`, motion on `springEase`.
3. `EARSHOT_PYTHON=... bash scripts/video-loop.sh launch` until it exits 2, open every frame under
   `critique/`, score scenes and pairs, fix, rerun. Exit 3 means fix notes to apply.
4. At exit 0, start `npx hyperframes preview --background` and ask the user to approve; then render
   `--quality delivery`. At exit 4, stop and show the user what still fails.

## Troubleshooting

**`video-loop.sh` exits 1 "earshot not importable":** install earshot into a venv (CPU torch) and
point `EARSHOT_PYTHON` at its python, or set `"audio": "none"` in `scenes.json`.

**A scene fails "freeze ... (unplanned)" on an intentional rest:** declare it in that scene's
`holds` in `scenes.json` (scene-local seconds, `"to": "end"` allowed). Do not raise the threshold.

**Render shows static frames after a long wait:** a host `data-composition-id` does not match the
sub-composition's inner id and timeline key. They must be identical.

**Animation is janky / drops frames:** you're likely animating a layout
property. Read `motion/principles/performance.md` — move to `transform`/`opacity`
or FLIP.

**`scripts/lint.sh` exits 1 with "path/frontmatter mismatch":** a wiki file's
`context/category/concept` doesn't match its path. Rename the file or fix the
frontmatter, then re-run.

**`scripts/lint.sh` exits 1 with "broken source path":** a wiki concept's
`sources:` points at a missing `references/raw/` file. Fix the path or the raw file.

**Skill never triggers:** the `description:` lacks the phrases a user would type.
Ask "When would you use smart-animation?" and adjust until it matches.

## Success Signals

- `scripts/lint.sh` exits 0 after every wiki change (all triples valid, all sources resolve).
- Every animation uses `transform`/`opacity` (no layout-property tweens).
- Every motion-producing snippet has a `prefers-reduced-motion` fallback.
- Motion is concentrated on one signature moment, not scattered across the view.
- The right file loads for the stack: React work reads `lang/react`, a modal reads `lib/transitions`, etc.
- A video ships only after `video-loop.sh` exits 0 and the user approved the preview.
