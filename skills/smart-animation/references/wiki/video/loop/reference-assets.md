---
title: "Reference and Assets: Real Files, Closed-Form Springs, No Default Motion"
context: video
category: loop
concept: reference-assets
description: "Stage 2 of the video loop: every asset is real and listed in assets/SOURCES.md, motion uses closed-form damped springs (seek-safe by construction), and legal-but-generic motion (default easing, CSS transitions, stock fade-ups) is flagged."
tags: video, assets, spring, easing, closed-form, gsap, banned-motion, choreography
sources:
  - "references/raw/video-loop-brief.md"
  - "references/raw/claude-remotion-skill.md"
  - "references/raw/hyperframes-motion-reel-skill.md"
  - "references/raw/hyperframes.md"
last_ingested: 2026-10-20
command: scripts/video-gate.py
---

## Reference and Assets: Real Files, Closed-Form Springs, No Default Motion

Generic AI video looks generic for three reasons: placeholder assets, default easing, and everything
entering at once. Stage 2 removes all three before the first render.

### Real assets only
Logos, UI captures, fonts and footage live in `assets/`, one line each in `assets/SOURCES.md`
(`<file> - <origin> - <license or owner>`). The gate fails a scene that references (`src=`, `href=`,
`url()`) a missing or unlisted asset, or a placeholder host (placehold, picsum, dummyimage...).
Licensed brand files stay in the video's own repo, never in a public skill.

### Closed-form springs
A damped spring has an exact solution, so position is a pure function of time and any frame can be
seeked without simulating the frames before it:

```js
// zeta < 1 overshoots then settles; omega sets speed. 0 -> 1.
function spring(t, zeta, omega) {
  if (t <= 0) return 0;
  var wd = omega * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * omega * t) * (Math.cos(wd * t) + (zeta * omega / wd) * Math.sin(wd * t));
}
function springEase(dur, zeta, omega) { return function (p) { return p >= 1 ? 1 : spring(p * dur, zeta, omega); }; }
tl.fromTo(el, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5, ease: springEase(0.5, 0.55, 22) }, t);
```

Presets: snappy (zeta 0.75, omega 22), settle (0.9, 14), playful (0.5, 18). Keep `dur` long enough
for the spring to settle (about 4 / (zeta * omega) seconds) or the last frame snaps. Paste the helper
inside each scene's `<template>`: sub-composition heads are discarded.

**Incorrect (legal in HyperFrames, generic on screen):**

```js
tl.from('.card', { opacity: 0, y: 20, duration: 0.3, ease: 'power1.out' }, 0);  // stock fade-up
tl.from('.item', { opacity: 0, stagger: 0.1, ease: 'none' });                   // uniform, linear
```

**Correct (springs, 3-property entrance, hierarchy in the stagger):**

```js
tl.fromTo('.hero', { opacity: 0, y: 60, scale: 0.96 },
  { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: springEase(0.7, 0.75, 22) }, cue.t);
// supporting items follow the hero by 3-6 frames each, smaller travel, softer spring
```

### Shipped helpers: `assets/vendor/motion.js`
`video-init.sh` copies it and `index.html` loads it after GSAP, so every scene can call
`window.motion`: `springEase`, `glide`, `drift` (constant velocity, for pushes that cross cuts),
`words` (left-to-right resolve: blur and opacity glide, only the rise springs, because a spring's
overshoot on blur made later words look sharper than earlier ones), `count`, `push`, `morph`
(transform-only box-to-box) and `lead` (move the cursor to a target). Each encodes a lesson from the
test films; extend it rather than pasting new copies into scenes.

### The banned list is a taste layer, not a determinism check
HyperFrames `check` already rejects seek-unsafe motion. `video-gate.py` adds warnings (file:line) for
default GSAP eases (`none`, `linear`, `power1*`, `sine*`), CSS `transition:` and default CSS timing
functions. A grep cannot prove taste: the rubric's motion line is where the agent judges the rest.

### Transitions are designed, not cross-faded
Carry a shape, direction or velocity across the cut (type becomes a line, a card becomes the next
scene's frame). The pair critique in `video/loop/self-critique.md` judges exactly this.

The most common failure, measured on a six-scene narrated test film: four of five cuts faded to an
empty ground for 0.4-0.7 s before the next scene drew itself (pair scores 4-7). What fixed them:
- **End a scene in the next scene's first state.** The last frame of scene A and the first frame of
  scene B are the same picture: the dashboard stays, the accent bar stays put, the cursor is where
  the next element appears. Scene B never fades in what is already on screen.
- **Morph one element into the next scene's anchor:** a card becomes row 1 of a list, three rows
  close into a frame that grows into a dashboard, a card folds into the accent square of the logo.
- **Morph with transforms, not layout:** animate `x/y/scaleX/scaleY` from `transform-origin: 0 0`
  between the two boxes. Tweening `left/top/width/height` fails HyperFrames `check --strict`
  (`gsap_non_transform_motion`) and breaks this skill's compositor-only rule.
- **Start the next scene moving at 0.0 s.** A scene whose first element arrives at 0.5 s leaves a
  dead half-second the freeze rule catches.
- **A slow push must be continuous across cuts.** Scene A pushing 1 -> 1.035 and scene B restarting
  at 1 reads as a visible scale snap at every cut (earshot's cut detector even marked two). Alternate:
  A 1 -> 1.02, B 1.02 -> 1, so each scene starts at the scale the last one ended on, and push at
  constant velocity (`motion.drift`): an eased push stops at both ends, which read as a frozen
  dashboard across a cut.
- **Grow a text card with a clip-path reveal, not a scale.** Scaling a chip up into a card
  squashed its text to ~8 px mid-morph; `clipPath: inset(0 0 100% 0) -> inset(0)` reveals it whole.
- **One accent means one.** Accent-filled checkboxes and card dots next to an accent cursor broke the
  style's one-accent rule; fill checks in ink and keep the accent for the eye's target.
- **Numbers agree across scenes.** A grid header of 41K over cards summing to 24.4K was flagged;
  derive every on-screen total from the same data.
- **The cursor always has a target** (the word just resolved, the row being checked, the bar that
  moved) and never parks on top of text: critics marked idle or colliding cursors in 4 of 6 scenes.

## Sources

- `references/raw/video-loop-brief.md` - real assets, closed-form springs, the CSS motion ban
- `references/raw/claude-remotion-skill.md` - 3-property entrances, 3-6 frame staggers, no linear motion
- `references/raw/hyperframes-motion-reel-skill.md` - morphing transitions instead of cross-fades
- `references/raw/hyperframes.md` - template-only sub-composition scripts, determinism rules
