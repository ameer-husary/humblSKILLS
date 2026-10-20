# Gold reference: a narrated B2B product launch film (measured 2026-10-20)

Source: a private launch film the user supplied as the target style for code-built videos. Not
redistributable: no frames, names, copy or brand colors are kept here, only measurements and the
grammar, so the skill learns the kind of video, not the video.
Measured with the smart-watch skill (frames + on-device transcript), FFmpeg (cuts, loudness, palette)
and earshot (sound sections, BPM, sync), plus video-reference.sh.

## Format and structure
- 168 s, 3840x2160 at 24 fps, AAC stereo. 29 narration segments.
- Story: the viewer's problem in one line -> the product name and what it does (by beat 2) ->
  "four things to build", each a chapter with a header -> the system running live -> an incident
  (a metric drops) -> diagnosis -> the fix in the data, the agent and the interface -> resolved ->
  tagline lockup. One fictional customer scenario carries the whole film.

## Picture grammar
- Hard cuts: 6 in 168 s (2.1 per minute); median shot 7.7 s, longest 80 s. Transitions are in-place
  rebuilds, ground brightness wipes and pushes, not cuts.
- Ground: charcoal for the open, warm off-white for the body; near-black ink; grays for secondary
  text. One saturated accent covering about 0.05% of pixels (a small square "cursor" / particle
  cluster) that leads the eye between focal points and across transitions. A palette quantizer
  averages it away; a saturated-pixel histogram finds it.
- Type: one neo-grotesk sans, regular weight, tight tracking; monospace for numbers and data.
  Headlines are two-tone (key words in ink, the rest gray) and resolve word by word with blur.
- UI is built as flat wireframe cards (1 px borders, no shadows): grids of cards with run counts,
  checklists whose rows tick in, node graphs that grow, KPI tiles counting up, bar charts growing,
  tables, a map. Chapter headers repeat a small brand lockup top-left.
- The light-gray secondary text measures about 2.55:1 on the off-white ground: under WCAG AA.
  HyperFrames `check` fails it, so a new video keeps the two-tone idea with darker grays.

## Sound grammar (earshot)
- Voice-over narration on top, about 115-125 words per minute, one idea per line.
- A continuous house bed ("confident and cool"), about 103 BPM, five sections that follow the story,
  ducked under the voice; UI ticks on arrivals; strongest accents at chapter turns.
- Cuts do NOT follow the beat: 10% of cuts land on the beat grid (chance 17%); the voice sets timing.
- Loudness -12.3 LUFS integrated, true peak +0.1 dBTP, 83 clipped runs, LRA 6.3 LU; 6.8 s quiet tail.
  Hotter than this skill's -14 LUFS / -1 dBTP gate; the gate stays stricter than the reference.
