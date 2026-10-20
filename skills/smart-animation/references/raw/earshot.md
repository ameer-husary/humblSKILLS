# earshot (Leonxlnx/earshot) - distilled notes

Source: https://github.com/Leonxlnx/earshot v0.3.0 (README, docs/SFX.md, docs/INTEGRATION.md,
skills/earshot/SKILL.md, earshot/api.py, earshot/timeline.py), plus the 22 s launch film
`earshot_launch.mp4` the user shared. Read 2026-10-20. MIT, Python >= 3.10, CPU only.
1.9k stars, pushed 2026-10-18.

## What it is
"Ears for coding agents": turns sound into evidence (describe, match, find, compare, realness,
timeline, sheet, critique, measure) and makes sound in code (forge, fit, a bank of 201 code-made
effects, kits). CLI, Python API (`from earshot import api`) and an MCP server.

## Install and cost (measured locally)
- Tested pin: commit `925ebe5` (pyproject 0.3.0; newest tag is v0.2.0, so pin the commit).
  `video-sound.py` imports `earshot.features.true_peak_dbtp` and `earshot.forge.fx.limit`, which are
  internal: re-test after moving the pin.
- `uv venv -p 3.12 && uv pip install --extra-index-url https://download.pytorch.org/whl/cpu -e <clone>`
  installs torch 2.14 CPU, transformers, librosa, pyloudnorm. `earshot doctor` checks it.
- Models (CLAP larger_clap_general + AST audioset, ~1.1 GB, pinned revisions) download on first model
  call or `earshot doctor --fetch`; cached under `<clone>/.cache/hf` for an editable install.
- Every CLI call reloads models (20-40 s); use one Python process or the MCP server.
- `kit`, `sfx` and `measure` load no models. A whole preset kit renders in 9-34 s cold, 3-5 s cached.

## Sound bank, kits and locks (no models)
- `earshot kit init --preset calm|crisp|minimal -o audio/kit.json`; calm = text-led default.
  Roles: tick, tick.crisp, tock, hit, land, land.light, pop, whoosh.short, whoosh.long, suck, riser,
  drop, key, key.space, key.return, click, click.confirm, snap, swell, bell, text. `null` = not sounded.
- `kit render kit.json --out audio/kit` -> 24-bit takes + `kit.lock.json`: per role `{sound, align,
  level_db, takes: [{file, seed, pitch, onset_s, peak_s, end_s, dur_s, peak_db, checks}]}`.
  Deterministic and cached; a take that fails the audit is re-rolled on a new seed.
- `align`: onset (clicks, hits, keys), peak (whoosh apex), end (riser lands on the hit).
- `sfx render ID --dur --apex --pitch`: apex lands within 2.5 ms; dur exact; pitch via the recipe.
- `sfx check` audit (model-free): clicks, clipping, dc, ring, truncated, silent, rising_glide
  (the "synth whip"), stacked / pre_swell on hits.
- `earshot.forge.fx.limit(x, ceiling_db, true_peak=True)`: look-ahead true-peak limiter.
- No music and no ambience in the bank.

## Listening (models)
- `api.timeline(path, video=, cues=)`: events (time, label), sections, loudness (integrated LUFS, LRA,
  true peak), beat grid, and `sync.cues.items[]` = `{t, kind, id, offset_ms, status, event_t, event}`;
  status `OK` = an onset within 1 frame (frame from cues fps), `near` = within 100 ms, also `swell`,
  `peak`, `no sound`. Cue file: `{fps, events: [{t | f, kind, id}]}`.
- Measured on a placed kit: keys and hit landed 0-2 ms from their cues (OK); a whoosh placed by its
  apex read `near` at -37 ms because the event is timed at its onset. Peak/end-aligned roles need the
  100 ms tolerance.
- `api.sheet(path, png, video=, cues=, tl=)`: one PNG with frames, labelled events, spectrogram,
  waveform, loudness and sync markers. `api.critique(path, video=)`: scorecard against 7 pro launch
  films with timestamped fixes.
- Limits stated by earshot itself: the search optimizes its own models (Goodhart); realness is easy
  to fool; judge by model-free measurements, spectrograms and a human. `llm` uploads audio to Gemini.

## Cinetic integration pattern (docs/INTEGRATION.md)
Picture code exports cues; a kit supplies one voice per role; a conductor places one take per event
by the role's sync point; a stack guard warns on a second effect within 3 frames of the lockup;
master to -14 LUFS for launch films.

## The launch film (earshot_launch.mp4, measured with FFmpeg, not listened to)
22.0 s, 1920x1080 at 60 fps, AAC stereo 48 kHz. Integrated -14.0 LUFS, true peak -2.2 dBTP, LRA 12.3 LU.
Eight silences under -40 dB, longest 17.9-20.0 s before the end card. Structure: typed question
("can AI hear?"), demonstrations (notes, waveform, key / toggle / bubbles / sweep), logo resolve,
claim, end card. Light ground, one blue accent. Spectrogram: one transient per typed key, a tonal
pluck per note, clicks and pops on UI controls, broadband whooshes on sweeps, one low hit under the
logo. No music bed.
