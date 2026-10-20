# claude-remotion-skill (haidrrrry) - distilled notes

Source: https://github.com/haidrrrry/claude-remotion-skill README. Read 2026-10-20. MIT, 551 stars.
Remotion-based (not usable here commercially at 4+ employees without a company license); read for
its craft rules and verification loop only.

- Premise: "Remotion is never the bottleneck - motion-design craft is." Generic AI video = linear
  interpolation, lonely opacity fades, everything entering at once, flat backgrounds, static images,
  unverified renders.
- Hard rules: never linear interpolation (springs / bezier + clamp); 3-property entrances (fade +
  rise + scale); staggered choreography at 3-6 frame offsets; gradient mesh + grade + grain +
  vignette instead of flat fills; Ken Burns on every still.
- Mandatory render -> extract frames with ffmpeg -> inspect -> fix -> re-render loop; a render shipped
  without frame checks means the skill was not loaded.
