# HyperFrames planning doctrine - distilled notes

Source: HyperFrames agent skills installed by `hyperframes init` at 0.8.181 (2026-10-20):
`hyperframes/references/intent-interview.md`, `hyperframes-studio/SKILL.md` (sections 0 and 5),
`hyperframes-creative/references/story-spine.md` and `storyboard-recipe.md`.
https://github.com/heygen-com/hyperframes (Apache-2.0).

## Talk before you build (hyperframes-studio section 0)
- A new film is planned before any composition file changes. Ask only questions whose answer changes
  the film, each with a recommended answer and its trade-off ("30 seconds fits a feed; 60 leaves room").
- Keep the plan in the project, not only the chat: the next session may not see this one.
- A wrong answer costs one message; a wrong build costs a long run and a round of notes.

## The intent interview (hyperframes intent-interview.md)
- Memory first (remembered defaults, recipes), then triage: is the request formed (message, material,
  occasion readable) or unformed (a subject with no take)? Unformed requests get a pitch round:
  five genuinely different concepts, at least two from the tail, then a recommendation.
- Must-haves one question per field, recommended option first with its receipt; never ask what the
  request already answered (inference is not an answer).
- Integration check: read the combined answers for a consequence no single answer showed
  (vertical at 90 s with chart-dense concept = charts a phone can't read) and propose the fix now.
- Present the locked brief with stated and inferred answers as two separate groups.
  Revision is not confirmation: re-present after a correction; never build an unconfirmed brief.
- BRIEF.md frontmatter: workflow, flow, storyboard, message (the ONE thing), destination, aspect,
  language, audience, length, angle.

## Story spine (hyperframes-creative story-spine.md)
- The hook speaks the viewer's language: outcome, not internal vocabulary or feature lists.
- Reverse iceberg: the value claim (the message) lands by the second beat; the rest is evidence.
  Self-check: delete the evidence beats, the value must still stand; delete the value beats, the video
  should stop working.
- Present the storyboard as a proposal: "This video tells [audience] that [message]." then a table
  Frame | Beat | On screen | Why; a frame whose why cannot be traced to the message is cut.
- Visuals point back to the source: real filenames, the product's own numbers, the article's own
  metaphor. If a prop could appear unchanged in another product's video, swap it.
- A frame change in the plan costs 30 seconds; after the build it costs minutes.

## Storyboard recipe
- Optional stills board (`boards/storyboard.html`) posed in the real composition at each key moment,
  snapshot with `hyperframes snapshot --at <times>`; stop and wait for the person's go; notes change
  only the named frames.
