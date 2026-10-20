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
