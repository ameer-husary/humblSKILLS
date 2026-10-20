---
title: "Sound: earshot Kits on Picture Cues, Effects-Only by Default"
context: video
category: loop
concept: sound
description: "Code-made sound for the video loop: scene data-cues become cues.json; narration lines (say or local TTS) and earshot kit takes land on their cues; an optional music bed is ducked under the voice; the mix is limited to -14 LUFS / -1 dBTP; earshot measures sync on the rendered MP4."
tags: video, sound, sfx, earshot, cues, sync, loudness, lufs, beats, music
sources:
  - "references/raw/earshot.md"
  - "references/raw/hyperframes.md"
  - "references/raw/video-loop-brief.md"
  - "references/raw/hyperframes-motion-reel-skill.md"
last_ingested: 2026-10-20
command: scripts/video-sound.py
---

## Sound: earshot Kits on Picture Cues, Effects-Only by Default

The agent cannot hear, so sound is built and checked the same way as picture: from code, against
measurements. earshot supplies both halves: a bank of 201 code-made effects rendered by role, and
listening tools that time every sound against its cue on the rendered video.

### Modes (`scenes.json` "audio")
- `sfx` (default): every gesture gets an effect; deliberate silences; no music, no beat grid.
  Suits short and muted-by-default videos.
- `voice`: narration-led. Lines are cues `{"t": 0.4, "kind": "vo", "text": "..."}` in each scene's
  `data-cues`; effects and an optional ducked bed sit under them. The voice times the film
  (`cut_on: "free"`): a measured narrated launch film put only 10% of its cuts on the beat.
  - `"voice": {"engine": "say", "name": "Reed (English (US))", "rate": 178}` renders each line with
    macOS `say` (offline). `"engine": "hyperframes"` uses `npx hyperframes tts` (local Kokoro; it
    needs `kokoro-onnx` in `HYPERFRAMES_PYTHON`, and on 0.8.181 it failed here on an espeak-ng data
    path baked into the loader). `"engine": "files"` with `"file"` per cue uses recorded lines.
  - Lines are cached by text in `audio/vo/`, leading silence trimmed so a line starts on its cue;
    `.loop/voice.json` records each line's start and end. Measure line lengths before timing scenes
    (`say -o` and ffprobe, or one loop pass): a scene is its line plus 0.5-1 s of breath.
  - `"bed": {"file": "assets/bed.wav", "db": -6, "duck_db": -5}` loops a bed under everything,
    ducks it while a line plays (150 ms ramps) and fades it over the last 1.5 s. earshot makes no
    music: supply a licensed bed, source one via HyperFrames `/media-use`, or synthesize one in code.
    Level it about 10-12 LU under the voice. At db -17 / duck -8 the critic heard music in only 33%
    of 5 s windows (the bed sat ~20 dB under); at -6 / -5 gaps measure -16.6 LUFS against a -14 mix
    and earshot hears a clear 103 BPM pulse under "voice-over narration".
- `music`: effects plus a music bed you supply as `<audio data-timeline-role="music">` (earshot makes
  no music; HyperFrames `/media-use` can source one). `hyperframes beats` writes the beat grid and
  every scene cut must land within 1 frame of a beat. Give the tracker a full-length track: a 4.2 s
  bed returned no beats, a 16 s one 32 beats at 120.1 BPM. The -14 LUFS target applies to the final
  MP4: the soundtrack is normalised alone, so a bed added on top moves the total (a test bed at
  `data-volume="0.5"` measured -15.8). Tune the bed's `data-volume` until the gate's loudness line clears.
- `none`: no sound; delete the template's `<audio id="soundtrack">`.

### One timing source for picture and sound
Each scene root carries its sound events in scene-local seconds, and its timeline is built from them:

```html
<div id="root" data-composition-id="s02-lockup" data-cues='[{"t":0.20,"kind":"hit"}]'>
<script>
  var hit = JSON.parse(document.querySelector('#root').dataset.cues)[0];
  tl.to('#mark', { scale: 1, duration: 0.9, ease: springEase(0.9, 0.45, 16) }, hit.t);
</script>
```

**Incorrect (a hand-kept cue list next to the animation):** the two drift after the first retime
and the hit lands 80 ms after the picture.

`video-gate.py cues` adds each scene's `absStart` from `hyperframes timeline --json` and writes
`cues.json` (`{fps, events: [{t, kind, id}]}`); `kind` is a kit role (key, hit, whoosh.short, click...).

### Build (`video-sound.py build`, no models)
1. `audio/kit.json`: created from earshot's `calm` preset when missing; edit roles per video (tune
   the hit to the root note, set unused roles to `null`).
2. `kit render` (cached, deterministic, audit re-rolls bad takes) -> `audio/kit/*.wav` + `kit.lock.json`.
3. One take per cue, cycling takes so typing never repeats a sample, placed by the role's `align`:
   onset for keys/clicks/hits, the loudest 5 ms for a whoosh (`peak`), the end for a riser.
4. Gain to -14 LUFS integrated through earshot's true-peak limiter at -1.3 dBTP, re-aimed until it
   lands (one pass landed at -15.7; iterating reached -14.1 / -1.3 dBTP).
5. `audio/soundtrack.wav` is mounted in `index.html` as `<audio id="soundtrack">`; HyperFrames muxes it.

### Listen (`video-sound.py listen`, models load once)
`api.timeline(mp4, video=mp4, cues=cues.json)`, `api.sheet(...)` -> `critique/audio/sheet.png`,
`api.critique(mp4)` -> `critique/audio/critique.json`, and one `api.sheet(..., start, end)` per scene
-> `critique/<scene>/sound.png`, so each scene's sound line is judged on its own window. The per-scene
sheet of the starter showed an uncued "laptop key click" at 0.90 s (a take's release), which the
film-wide sheet hid among the other keys: uncued events are for the critic, not the gate. Measured: keys and the hit landed 0-2 ms from
their cues. A whoosh placed by its apex read -37 ms `near`, because earshot times an event at its
onset: peak/end-aligned roles pass within 100 ms, onset roles need 1 frame.

### Sound rules the gate enforces
- Narration lines keep 0.1 s between them and end before the video does.
- Sync tolerance: 1 frame for onset effects in the clear; 100 ms for apex/end-aligned sounds, for
  voice lines (speech starts softly: measured +35 to +55 ms after the trimmed start) and for any cue
  under a voice line (earshot matched a syllable: a click read -40 ms).
- A take whose earshot audit still flags it after re-rolls (`checks` in `kit.lock.json`) fails the film:
  pick another bank sound for that role.
- Stacked lockup: no other cue within 3 frames of a `hit` (one clean element carries the lockup).

### Version drift
`video-sound.py` calls earshot internals (`earshot.features.true_peak_dbtp`, `earshot.forge.fx.limit`).
`video-loop.sh` warns when `earshot.__version__` differs from the tested 0.3.0 (commit `925ebe5`):
re-run `scripts/tests/test_video_gate.py` and one real loop before trusting sound results.

### What never gates
Silence (it is not a dead frame), earshot's `critique` verdict and its `realness` score. earshot's own
docs warn both can be pleased without the sound improving; quote them in the rubric instead.

## Sources

- `references/raw/earshot.md` - bank, kits, locks, align, limiter, timeline sync fields, measured offsets, cost
- `references/raw/hyperframes.md` - `<audio>` rules and the `beats` output format
- `references/raw/video-loop-brief.md` - effects-only default, music supported, cuts on the beat only with music
- `references/raw/hyperframes-motion-reel-skill.md` - one beat table driving picture and sound

## Command

```bash
"$EARSHOT_PYTHON" scripts/video-sound.py build  <project> <project>/cues.json <duration_s>
"$EARSHOT_PYTHON" scripts/video-sound.py listen <project> <project>/cues.json <video.mp4>
```
