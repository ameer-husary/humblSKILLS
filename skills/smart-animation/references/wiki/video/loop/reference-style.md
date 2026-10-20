---
title: "Reference Style: Measure a Film, Borrow Its Grammar, Not Its Content"
context: video
category: loop
concept: reference-style
description: "How to turn a reference video into a style sheet: video-reference.sh measures cuts, palette (including small accents), loudness and sound layers; smart-watch adds the transcript; the agent writes the grammar (type, motion vocabulary, transitions, pacing, sound) in its own words into STYLE.md and PLAN.md, adapts it to the contrast floor, and copies nothing brand-specific."
tags: video, reference, style, palette, pacing, narration, product-film, launch
sources:
  - "references/raw/reference-product-film-2026-10-20.md"
  - "references/raw/hyperframes-planning.md"
  - "references/raw/earshot.md"
last_ingested: 2026-10-20
command: scripts/video-reference.sh
---

## Reference Style: Measure a Film, Borrow Its Grammar, Not Its Content

"Make it look like this one" is the most common brief and the easiest to get wrong in two directions:
eyeballing a reference and missing what makes it work (pacing, how few cuts it has, where sound
sits), or copying it so closely that the new film carries someone else's brand. Measure first, then
write the grammar down in your own words.

**Incorrect (copy the look):**

```markdown
Style: same as the reference - their accent color, their headline copy, their card layouts.
```

**Correct (measured, generalized, adapted):**

```markdown
- transitions: 2 hard cuts per minute; moments rebuild in place; ground brightness as the wipe
- accent: one saturated color on ~0.05% of pixels, a cursor that leads the eye (ours: our own hue, not theirs)
- type: two-tone headline resolving word by word; grays darkened to pass 3:1 / 4.5:1 contrast
- sound: narration ~120 wpm on top, house bed ~103 BPM ducked, sparse UI ticks, cuts follow the voice
```

### The procedure
1. `bash scripts/video-reference.sh <ref.mp4> <project>/reference` writes `STYLE.md` plus evidence:
   hard cuts and shot lengths (`shots.tsv`), neutrals and accents (`palette.txt`; accents come from
   a saturated-pixel histogram because a palette quantizer averages small accents away), loudness,
   earshot's sound summary (sections, BPM, voice, cuts on the beat), `contact.jpg` and six
   `motion-NN.jpg` strips (2 s at 6 fps: how things move, not just how they look).
2. Run the smart-watch skill on the same file for the timestamped transcript: words per minute,
   one-idea-per-line pacing, and the story spine.
3. Look at the strips at full size, then fill the style sheet in STYLE.md: ground / ink / accent
   roles, type roles and the headline treatment, motion vocabulary, transition grammar, pacing,
   sound layers, and an explicit "what NOT to copy".
4. Carry it into PLAN.md (research section and beat sheet). Measured numbers become targets: cut
   rate, seconds per idea, loudness, bed BPM. The voice, not the beat, times a narrated film
   (`cut_on: "free"`).
5. Adapt before you build: grays that fail contrast get darker (HyperFrames `check` gates WCAG AA:
   3:1 for text >= 24 px, 4.5:1 below); a reference that clips (+0.1 dBTP) does not lower the gate.

### Grammar of a narrated product film (one well-measured case)
- Story: the viewer's problem -> the product and its value by beat 2 -> the build, as chapters ->
  the system running -> an incident -> the fix -> resolved -> tagline lockup.
- Picture: a few long "sets" that rebuild in place; flat wireframe UI built in code that assembles
  piece by piece (checklist rows tick in, numbers count up in mono, bars grow, cards stack); two-tone
  headlines resolving word by word; a small accent cursor that carries the eye across every cut.
- Show before you say: the evidence (the bar refills, the number counts back) lands before the
  claim ("back on track"); a claim on screen before its proof cost the fix scene its pass.
- Sound: narration on top; a continuous bed ducked under it; one UI tick per arrival; a clean hit on
  the lockup. Readable rests while the voice talks must still move (a slow push, a counter, the
  next word arriving), or the freeze rule fails them: animate the words with the voice.

## Sources

- `references/raw/reference-product-film-2026-10-20.md` - the measured gold reference (anonymized)
- `references/raw/hyperframes-planning.md` - "visuals point back to the source", story spine
- `references/raw/earshot.md` - sound sections, BPM and cut-on-beat measurement

## Command

```bash
EARSHOT_PYTHON=/path/to/venv/bin/python bash scripts/video-reference.sh ref.mp4 my-video/reference
```
