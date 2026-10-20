# hyperframes-motion-reel-skill (Sunwood-ai-labs) - distilled notes

Source: https://github.com/Sunwood-ai-labs/hyperframes-motion-reel-skill README. Read 2026-10-20.
MIT, 147 stars. HyperFrames port of a Remotion reel skill, built for no-license commercial use.

- Beat-locked timing: every cut and impact is written as b(n) on a 120 BPM / 60 FPS grid
  (1 beat = 0.5 s = 30 frames); the same beat table drives picture and generated sound.
- Two-layer animation: one paused GSAP timeline for choreography + a pure render(t) function for
  generative Canvas/SVG layers, so both are seek-safe. Seeded PRNG, no Date.now()/Math.random().
- Morphing transitions: shapes carry over between scenes (type -> line -> graph -> grid -> logo)
  instead of cross-fades. Plain fade-in chains are banned.
- Verification: lint -> check (0 findings) -> snapshot review of every scene peak -> render
  --quality delivery -> ffprobe / ffmpeg spot checks.
