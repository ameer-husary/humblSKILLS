---
title: "Self-Critique: Per-Scene Scores, Adjacent Pairs, Mechanical Rules"
context: video
category: loop
concept: self-critique
description: "Stage 3 of the video loop: the script gathers evidence and writes stubs, a critic scores each scene and each adjacent pair (>= 8/10) with a reason per rubric line, mechanical rules (dead frames, capped holds, sync, loudness, beats, assets) override any score, edits to a scene or a shared file clear stale scores, and a 5-iteration cap escalates to the user."
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

**Correct (open critique/<scene>/frames/*.png at full size and sound.png, give every rubric line a
number and a reason, then a score equal to their sum):**

```markdown
---
scene: s02-lockup
source_sha: 1c9e0a4f7b2d       # written by the script; an edit to the scene clears the score
mechanical: clean               # dead frames, sync, beats, assets: written by the script
score: 8
---
- Intent lands in one viewing: 2 - mark reads as the brand at frame 02 (0.4 s)
- Motion quality (springs, hierarchy, no banned defaults): 2 - underdamped spring lands on the hit frame
- Composition and type (hierarchy, spacing, legibility at 1x): 1 - lone mark, no wordmark beside it
- Brand fidelity (real assets, correct colors and fonts): 2 - logo.svg from SOURCES.md, brand blue
- Rhythm and sound (gesture-to-sound sync, restraint, level; quote earshot numbers): 1 - hit 0 ms (OK), rest feels long
## Fix notes for next iteration
- shorten the hold to 1.0 s; move the scale overshoot onto the hit frame
```

### Units and rubric
A score counts only when all five lines read `- <label>: <0-2> - <reason of 10+ characters>` and sum to
the `score:`; otherwise the gate prints `score <unit>: not counted, ...` and treats the unit as unscored.
The reason should cite a frame, a timestamp or a number, so the next iteration knows what to keep.
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
| Holds too long | declared holds cover more than `max_hold_share` (default 40%) of the scene | scenes.json |

Declare intentional rests per scene in `scenes.json`: `"holds": [{"from": 1.1, "to": "end", "reason":
"logo lockup"}]` (scene-local seconds). Without them every logo lockup reads as a dead frame. Holds are
printed in each stub and capped at 40% of the scene: never add a hold, raise a threshold or lower
`pass_score` to get through. Those are the user's calls. (The starter's lockup first held 56% of its
scene; the cap caught it, and the scene was shortened to 1.8 s.) FFmpeg's
common n=0.003 missed real motion of a 100 px word on 1080p; 0.0003 matched the frames.
There is no separate "blank frame" rule. A blank-but-not-black frame (an empty light background)
only shows up when it lasts long enough to read as a freeze, so the agent still opens the first and
last frames itself. The starter's first draft held an empty canvas for 0.5 s after the word swept
out, and the freeze rule caught it.

### Staleness and termination
- Each stub stores `source_sha`: the scene file, its scenes.json entry, the assets it references,
  kit.json, and the **shared files**: `index.html` (the host) plus every glob in scenes.json `"shared"`
  (fonts, shared CSS). Pairs hash both scenes. A changed hash clears the score and refreshes that unit's
  frames; a shared edit clears every unit. Editing a scene's entry (holds, intent) clears it too, even
  if you later revert the edit: rescore after the next run.
- Exit codes: 0 pass, 1 plan not ready or tool error, 2 waiting for scores, 3 failing, 4 cap reached
  while failing.
- `max_iterations` (default 5) counts renders. At exit 4, stop and show the user the failing units,
  their scores and fix notes; never loosen a threshold to get through.
### Critic subagent (recommended for every scoring pass)
The author of a scene grades it generously. Hand each stale unit to a subagent that sees the evidence,
not the source:

```text
You are the critic for one unit of a code-built video. Do not open compositions/ or any source.
Read: PLAN.md (the message and this unit's row), <unit>.md (rubric, mechanical findings),
every PNG in <unit>/frames/ at full size, and <unit>/sound.png for a scene.
For each of the five rubric lines write "<0-2> - <reason citing a frame, time or number>".
Set score to their sum. Under "Fix notes for next iteration", list the changes that would raise the
lowest lines, most valuable first. Change nothing else in the file. Reply with the score only.
```

Units are independent, so critics can run in parallel; the author then applies the fix notes.

## Sources

- `references/raw/video-loop-brief.md` - >= 8/10 per scene, dead-frame hunt, groups of two = adjacent pairs
- `references/raw/hyperframes.md` - snapshot outputs, managed-storage retention, freezedetect threshold finding
- `references/raw/earshot.md` - sync statuses, onset timing of peak-aligned sounds, loudness fields
- `references/raw/claude-remotion-skill.md` - inspect extracted frames before delivering

## Command

```bash
EARSHOT_PYTHON=/path/to/venv/bin/python bash scripts/video-loop.sh my-video; echo $?
bash scripts/dead-frames.sh my-video/renders/draft-1.mp4      # standalone: freeze/black TSV
python3 scripts/tests/test_video_gate.py                       # hermetic gate test, no tools needed
```
