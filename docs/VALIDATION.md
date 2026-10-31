# Validation performed before initial publication

Environment: Windows, Blender 5.2.3 LTS (`e13b728c6880`), bundled Python 3.13, NumPy 2.3.4, FFmpeg/FFprobe 9.0.2. Rendering uses Cycles CPU by default. Cross-platform code/CI does not constitute proof of rendering on an untested GPU or OS.

- Fresh independent build: passed; no earlier iteration file loaded. Saved scene contains 2,566 animated bead points, instancing geometry, lights, glass and camera.
- Full-resolution rebuilt still: passed at frame 135, 720×1280, 32 samples; visually compared to the latest small-dais reference. `assets/rebuilt-preview.png` retains the result. Preset data and optical setup match the reference; floating-point and sample seed differences can change exact pixels.
- Sanitized checkpoint: passed; no linked libraries or external textures. `assets/approved-v06.json` records audit. `reference` command loaded/rendered it at reduced resolution and verified motion checkpoints.
- Six-frame smoke integration: passed. Scene → PNGs → seeded audio → H.264/AAC MP4 → full decode. 6/6 distinct decoded image hashes, 30/1 fps, 180×320, 0.200 seconds. See `smoke-verification.json`.
- Motion/audio unit tests: contact positions, ballistic fall, containing footprint, 300 distinct motion states, invalid preset rejection, nonclipping deterministic 48kHz/stereo/16-bit sound. Passed locally.
- Asset checksums and skill frontmatter validation are part of the publication check.

No complete new 300-frame video was rendered for packaging: the user had requested still-only look review before this task. The smoke test checks integration with six real consecutive frames; historical full videos used the same frame/audio pipeline but older looks. Run `video` on the target machine when a complete new video is wanted.

On another machine, run doctor, reference, still and smoke before starting a long render. The GitHub workflow tests deterministic model and audio on three OSes; it does not render Blender there.
