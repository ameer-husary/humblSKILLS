---
title: "Self-Critique: Per-Scene Scores, Adjacent Pairs, Mechanical Rules"
context: video
category: loop
concept: self-critique
description: "Stage 3 of the video loop: the script gathers evidence and writes stubs, the agent scores each scene and each adjacent pair (>= 8/10) from full-size frames, mechanical rules (dead frames, sync, loudness, beats, assets) override any score, edits clear stale scores, and a 5-iteration cap escalates to the user."
tags: video, critique, rubric, dead-frames, freezedetect, gate, pairs, loop
sources:
  - "references/raw/video-loop-brief.md"
  - "references/raw/hyperframes.md"
  - "references/raw/earshot.md"
  - "references/raw/claude-remotion-skill.md"
last_ingested: 2026-10-20
command: scripts/video-loop.sh
---

## Self-Critique: Per-Scene Scores, Adjacent Pairs, Mechanical Rules

A script cannot judge a frame, and an agent should not judge its own frames from memory. So the
loop splits: `video-loop.sh` produces evidence and enforces what it can measure; the agent writes
a score into a file; the next run of the same command is the gate.

**Incorrect (score from the source code, or from the contact sheet):**

```markdown
score: 9   <!-- written after editing the HTML, before looking at the new frames -->
```

**Correct (open critique/<scene>/frames/*.png at full size, fill every rubric line, then score):**

```markdown
---
scene: s02-lockup
source_sha: 1c9e0a4f7b2d       # written by the script; an edit to the scene clears the score
mechanical: clean               # dead frames, sync, beats, assets: written by the script
score: 8
---
- Intent lands in one viewing: 2 - mark reads as the brand at 0.4 s
- Rhythm and sound: 1 - hit lands 0 ms on the cue (earshot OK), but the 1.6 s rest feels long
## Fix notes for next iteration
- shorten the hold to 1.0 s; move the scale overshoot onto the hit frame
```

### Units and rubric
- **Scenes**: 5 lines x 2 points - intent, motion quality, composition and type, brand fidelity
  (real assets), rhythm and sound. Pass at `pass_score` (default 8).
- **Adjacent pairs** ("groups of two"): every cut gets its own stub `critique/pairs/<a>__<b>.md` with
  frames from 0.5 s before to 0.5 s after the cut, scored on continuity: one motion across the cut,
  direction and velocity carried, sound bridging or punctuating, color and layout continuity, story.
  Per-scene scoring never sees a cut, so pairs are what catch cross-fade sludge and double hits.

### Mechanical rules (override any score)
| Rule | Threshold | Source |
|---|---|---|
| Frozen picture | freeze >= 0.5 s outside the scene's declared `holds` | FFmpeg freezedetect n=0.0003 on the MP4 |
| Black picture | any blackdetect stretch (0.1 s) outside holds | FFmpeg blackdetect |
| Sound off its cue | onset roles > 1 frame; peak/end roles > 100 ms | earshot timeline |
| Loudness | integrated outside -14 +-1 LUFS, or true peak > -1 dBTP | earshot timeline |
| Cut off the beat (music mode) | > 1 frame from the nearest beat | hyperframes beats |
| Dirty take | an earshot audit warning left after re-rolls | kit.lock.json |
| Stacked lockup | another cue within 3 frames of a `hit` | cues.json |
| Asset | missing, unlisted in SOURCES.md, or a placeholder host | scene source |

Declare intentional rests per scene in `scenes.json`: `"holds": [{"from": 1.1, "to": "end", "reason":
"logo lockup"}]` (scene-local seconds). Without them every logo lockup reads as a dead frame. FFmpeg's
common n=0.003 missed real motion of a 100 px word on 1080p; 0.0003 matched the frames.
There is no separate "blank frame" rule. A blank-but-not-black frame (an empty light background)
only shows up when it lasts long enough to read as a freeze, so the agent still opens the first and
last frames itself. The starter's first draft held an empty canvas for 0.5 s after the word swept
out, and the freeze rule caught it.

### Staleness and termination
- Each stub stores `source_sha` (scene file + its scenes.json entry + referenced assets + kit.json;
  pairs hash both scenes). A changed hash clears the score and refreshes that unit's frames only.
- Exit codes: 0 pass, 1 tool error, 2 waiting for scores, 3 failing, 4 cap reached while failing.
- `max_iterations` (default 5) counts renders. At exit 4, stop and show the user the failing units,
  their scores and fix notes; never loosen a threshold to get through.
- A critic subagent that did not author the scene scores more honestly than the author.

## Sources

- `references/raw/video-loop-brief.md` - >= 8/10 per scene, dead-frame hunt, groups of two = adjacent pairs
- `references/raw/hyperframes.md` - snapshot outputs, managed-storage retention, freezedetect threshold finding
- `references/raw/earshot.md` - sync statuses, onset timing of peak-aligned sounds, loudness fields
- `references/raw/claude-remotion-skill.md` - inspect extracted frames before delivering

## Command

```bash
EARSHOT_PYTHON=/path/to/venv/bin/python bash scripts/video-loop.sh my-video; echo $?
bash scripts/dead-frames.sh my-video/renders/draft-1.mp4      # standalone: freeze/black TSV
```
