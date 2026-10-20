# Patterns

Performance memory. Each entry records a concrete attempt, its numeric
outcome, and the lesson. Read before every session; append after every
session where quantified results appear.

Entry shape:

```
### <YYYY-MM-DD> | <short title>
- Context: <what was attempted, in one line>
- Approach: <the method used>
- Result: <metrics, numbers, outcomes>
- Worked: <what helped>
- Didn't: <what hurt>
- Lesson: <the rule to apply next time>
```

---

### 2026-10-20 | Video loop on the starter project (2 scenes, 4.2 s, 7 cues)
- Context: end-to-end run of video-init.sh + video-loop.sh, HyperFrames 0.8.181, earshot 0.3.0, Apple M5 Pro.
- Approach: calm kit, placed by lock sync points, limiter re-aimed to -14 LUFS, draft render, earshot listen.
- Result: first pass 64 s (render ~8.5 s, earshot listen dominates); reruns with unchanged inputs
  skip render and listen. Mix -14.1 LUFS / -1.3 dBTP (single limiter pass gave -15.7).
  Sync: 5 keys and the hit 0-2 ms (OK); a peak-aligned whoosh -37 ms (`near`).
  freezedetect n=0.003 missed a moving 100 px word; n=0.0003 matched the frames.
  hyperframes beats: 4.2 s bed -> no beats; 16 s 120 BPM bed -> 32 beats, 120.1 BPM.
- Worked: one timing source (data-cues + timeline --json); per-unit hashes so a one-scene edit
  re-snapshots one scene and one pair.
- Didn't: the starter's first timing held an empty canvas 0.5 s after the word left; the gate
  caught it as an unplanned freeze (fixed by shortening the scene to 1.7 s).
- Lesson: judge peak-aligned sounds with a 100 ms window; keep freezedetect at n=0.0003; declare holds.

### 2026-10-20 | Delivery pass and per-scene sound on the starter (3.5 s)
- Context: `video-loop.sh --deliver` after a passing draft gate, HyperFrames 0.8.181, earshot 0.3.0.
- Approach: delivery render + dead frames + earshot listen on the final, poster, 2 fps frames.
- Result: whole --deliver run 26 s. Per-scene earshot sheet exposed an uncued key-release click at
  0.90 s that the film-wide sheet hid. A fixed 6x6 contact sheet padded a 3.5 s video with black
  tiles that read as black frames; grid sized to the frame count with gray padding instead.
- Lesson: judge sound per scene; never pad evidence images with black.

### 2026-10-20 | Narrated product film from a reference (26.8 s, 6 scenes, voice + bed + ticks)
- Context: test of reference -> STYLE.md -> PLAN -> scenes -> loop, macOS `say` voice, synthesized 103 BPM bed.
- Result: video-reference.sh on a 168 s 4K film took 20 s; the accent covered 0.05% of pixels and
  needed a saturated-pixel histogram (threshold 0.01% of pixels). Draft 1 failed the contrast gate
  on copied grays (2.55:1); draft 2 failed on frozen openings (a 16 px cursor on an empty ground) and
  speech sync (+35/+55 ms); draft 3 was mechanically clean after a moving glow on the open, cards
  assembling from 0.1 s, and the tagline resolving word by word with the voice.
- Lesson: in narrated films, animate words with the voice and never open on an almost-empty frame;
  measure line lengths before timing scenes.

### 2026-10-20 | Narrated test film through three critic rounds (6 scenes, 11 units, cap 5)
- Context: 28 s film in a reference's grammar; independent critic subagents per round (scenes, cuts).
- Result: scenes passing 1/6 -> 3/6 -> 5/6; cuts 1/5 -> 2/5 -> 3/5; the loop hit the 5-render cap
  (two renders went to mechanical fixes: contrast, frozen openings) and exited 4 with three units at 7.
  Critics were specific and mostly consistent; one contradiction (accent vs hatch for the problem
  bar) came from a vague PLAN row and was settled by rewriting the row.
- Worked: fix notes from the critics, applied all at once per render; carrying an element across cuts.
- Didn't: fading to empty ground (4/5 cuts in round 1); a per-scene push restarting at every cut.
- Lesson: a 5+ scene film needs more than 5 renders to clear every unit; ask the user to raise
  max_iterations up front for long films instead of discovering the cap at the end.

### 2026-10-20 | Narrated test film to the raised cap (8 renders, Chatterbox voice)
- Context: the same 28 s film, cap raised 5 -> 8 with the user's approval; voice switched to Chatterbox.
- Result: rounds 4-6 took scenes to 5/6 (9, 9, 9, 8, 7, 10) and cuts to 4/5 (9, 8, 9, 10, 7). Exit 4 at
  8/8 with the fix scene and its outgoing cut at 7. Mix -14.7 LUFS / -1.8 dBTP, 103 BPM bed with a
  clear pulse, "voice-over narration" detected. Units passing per round: 2, 4, 8, 8, 8, 9 of 11.
- Worked: carrying one element across each cut (s04 -> s05 reached 10/10: the dashboard never leaves,
  the cursor rides the refilling bar, one note on the cut); headline type for the key beat; motion.js.
- Didn't: following a critic note that contradicted the plan's beat order; quiet planned ticks.
- Lesson: about 8 renders get a six-scene narrated film to ~9 of 11 units; the last units need the
  plan row to fix the beat order before the critics see it.
