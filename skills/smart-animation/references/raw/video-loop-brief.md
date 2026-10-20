# Code-built video loop: the brief (2026-10-20)

Source: the user's description of a three-stage loop from an Instagram reel
(https://www.instagram.com/reel/DeZRVmkvhiR/, not watched; described by the user), recorded
in a session handoff, plus the user's answers to the design questions on 2026-10-20.

## The loop as described
1. **Render engine**: Node, FFmpeg, headless Chrome, a frontier model as the author. HTML frames are
   seeked one at a time and encoded to MP4.
2. **Reference and assets**: real assets (logos, real UI captures, real fonts), never placeholders.
   "Close-form strings" = closed-form spring easing (confirmed by the user): physics springs computed
   per frame, so any frame seeks deterministically. Basic CSS motion is banned (default ease / linear
   fades and slides). Audio is synthesized; cuts land on the beat.
3. **Self-critique**: the agent watches its own rendered frames, scores each scene, hunts dead
   frames (no change, blank, unplanned frozen holds), goes back to stage 2 and renders again. Each
   scene must score >= 8/10. Then scenes are checked "in groups of two"; stop only when every
   scene passes.

## Decisions taken with the user (2026-10-20)
- "Groups of two" = **adjacent scene pairs**, each judged on the cut between them (the user left it
  to the best-performing option; pairs are the only reading that judges transitions).
- Easing: closed-form springs, yes.
- Sound: **effects only is the default**; effects plus a music bed is supported. "Cuts on the beat"
  applies only when there is music.
- The skill stays a **general framework** for code-built animation videos. Product-specific videos
  (the motivating case was an in-app intro) live in their own repos, not in this skill.
- Render engine: HyperFrames (Apache-2.0) over Remotion, whose company license is paid at 4+ employees.
- Sound: earshot (MIT) for code-made effects and for listening.
