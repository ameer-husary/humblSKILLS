---
title: "Plan: Interview, Context, Research, Beat Sheet Before Any Scene"
context: video
category: loop
concept: plan
description: "Stage 0 of the video loop: interview the user one question at a time, gather real context and 2-3 references, write a beat sheet whose every row traces to the message and names its sound cues, then get an explicit approval line; video-loop.sh refuses to run until PLAN.md is complete."
tags: video, plan, brief, storyboard, beat-sheet, interview, story, loop
sources:
  - "references/raw/hyperframes-planning.md"
  - "references/raw/video-loop-brief.md"
  - "references/raw/earshot.md"
last_ingested: 2026-10-20
command: scripts/video-gate.py
---

## Plan: Interview, Context, Research, Beat Sheet Before Any Scene

Most loop iterations are spent fixing what a plan would have caught: a message that never lands,
a scene with no reason to exist, sound that fights a muted autoplay. A frame change in the plan costs
seconds; after a render it costs a full loop. So `video-init.sh` writes `PLAN.md`, and `video-loop.sh`
exits 1 while it has a `TODO`, misses a `scenes.json` id, or has no `approved:` line.

**Incorrect (build from the one-line request):**

```markdown
User: "make a launch video for the CLI"
Agent: writes four scenes, renders, scores them 8 - and the user's first note is "who is this for?"
```

**Correct (one question at a time, recommended answer first, the user's words recorded):**

```markdown
Q: Where does it play, and is it muted? Recommended: landing-page hero, muted autoplay loop,
   because that is where launch videos are watched; the trade-off is that no idea may depend on sound.
A (user): "README and the launch tweet, muted."   -> recorded under 1. Brief
```

### The five parts of PLAN.md
1. **Brief (asked):** message (the ONE thing), audience, where and how it plays (muted? autoplay?
   loop?), length and aspect, sound mode (sfx / music / none), must show / must not show. Ask only what
   the request did not answer; never fill a field by inference without saying so.
2. **Context (gathered):** the facts the video states, each with its source; brand files (logo, colors,
   fonts) placed in `assets/` and listed in `SOURCES.md`; who supplies real captures. Read the product,
   repo or page itself: visuals should come from the subject, not from stock ideas.
3. **Research:** 2-3 reference videos and the one technique to take from each. When the user hands
   over a target video, run `scripts/video-reference.sh` on it first and fill its STYLE.md
   (`video/loop/reference-style.md`); its measured numbers become the plan's targets (for sound, the earshot
   launch film: one effect per gesture, deliberate silences, one clean hit on the lockup).
4. **Beat sheet:** open with "This video tells [audience] that [message]." One row per scene: id (must
   match `scenes.json`), beat, seconds, on screen, sound cues (kind @ s), and **why**, traced to the
   message. The message lands by the second beat. A row whose why does not trace is cut. Then one line
   per cut: how the shape, direction or sound hands over (the pair critique will judge exactly this).
5. **Integration check, then approval:** name one consequence no single answer showed (a sound-led
   joke in a muted autoplay; a 3 s scene carrying a 12-word line) and its fix. Present the plan with
   what the user said and what you inferred as two separate lists. A correction is not an approval:
   re-present. Only then write `approved: <date>, <who>`.

### Keeping it honest
- The plan lives in the project, so a new session or another agent starts from it, not from chat.
- When a scene is added, cut or retimed later, update its row first; the gate checks ids, the critic
  checks intent against the row.
- Unformed requests ("a video about X") get 3-5 genuinely different directions before the interview,
  with one recommended. Pick, mix or redirect are all answers.

## Sources

- `references/raw/hyperframes-planning.md` - talk before build, one question with a recommendation,
  integration check, stated vs inferred, story spine and the traced "why" column
- `references/raw/video-loop-brief.md` - the loop this plan feeds; first-pass reliability as the goal
- `references/raw/earshot.md` - the launch film as a sound reference

## Command

```bash
python3 scripts/video-gate.py plan my-video   # 0 = ready; 1 lists every TODO / missing scene / no approval
```
