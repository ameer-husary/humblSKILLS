# Chatterbox TTS (resemble-ai/chatterbox) - distilled notes

Source: https://github.com/resemble-ai/chatterbox README, read 2026-10-20; installed and run locally.
MIT, 27.1k stars, pushed 2026-07-21. Suggested by the user: the macOS `say` voice is flat and dated,
and Chatterbox is an expressive ("emotional") open TTS.

## Models
- Chatterbox (English, 500M): the default; `exaggeration` (emotion intensity, default 0.5) and
  `cfg_weight` (default 0.5) controls; no reference clip needed. `audio_prompt_path=` clones a voice
  from a ~10 s clip.
- Chatterbox-Turbo (350M, English): paralinguistic tags (`[laugh]`, `[chuckle]`), needs a reference clip.
- Chatterbox-Nano (110M): CPU-friendly, same tags. Multilingual V3 (500M, 23+ languages, `language_id=`).
- README tips: expressive/dramatic -> exaggeration ~0.7, cfg_weight ~0.3; fast reference speaker ->
  lower cfg_weight to ~0.3 for pacing.

## Install (measured on macOS, Apple M-series)
- `uv venv -p 3.11 ~/.venvs/chatterbox && VIRTUAL_ENV=~/.venvs/chatterbox uv pip install chatterbox-tts "setuptools<81"`.
  Without `setuptools<81` the bundled watermarker (`resemble-perth`) imports `pkg_resources`, fails
  silently, and model construction dies with `TypeError: 'NoneType' object is not callable`.
- Keep it in its own venv: its pinned torch differs from earshot's.
- First run downloads the weights (~6.5 min here). Device: `mps` on Apple Silicon.
- Cost: one process loading the model and rendering 6 lines took 44 s; a single line with load, 44 s.
- Output 24 kHz mono, watermarked (Perth implicit watermark).

## Measured against macOS `say` (earshot 0.3.0, voice descriptions are unvalidated in earshot)
- `say` (Reed, rate 178): realness "uncertain"; match to "a warm expressive human narrator voice-over"
  weak (z +2.2, rank 11 of 322).
- Chatterbox (exaggeration 0.6, cfg 0.45): realness "real or pro-produced"; match strong (z +3.3, rank 1).
- Pace: the same six lines ran 2.0-3.2 s with Chatterbox against 3.0-3.7 s with `say`; lowering
  cfg_weight from 0.45 to 0.3 did not slow them measurably. Measure line lengths per engine.
