---
name: ai-relax
description: Build, preview and render the AI Relax sunflower bouncing-ball scene with bright metallic beads, glossy glass, contact sound and true 30fps using the bundled Blender pipeline.
---

Use the repository containing this skill and `run.py`; resolve its path from the skill location, not a previous machine's drive letter. If installed into Codex, first read `references/repository.json` for the machine-local clone location, then verify `run.py` exists there. If it moved, ask for its current location or rerun the repository's installer. Read `docs/PRODUCTION_STANDARDS.md` for the user's current look and `docs/PORTABILITY.md` when installing on another machine.

The maintained preset is `presets/bright-metal-v06.json`. It reproduces 2,566 equal sunflower-packed beads, bright gold/orange/red metal, a narrow white glass dais and a quiet lavender background. A sanitized checkpoint and original preview are in `assets/`; `reference` opens that exact scene, while `still` rebuilds independently.

Start with `python run.py doctor`. Set `BLENDER_BIN` if Blender is not found. Default is Cycles CPU for portability; Eevee is optional and driver-dependent. No MCP, online generation, external textures, API keys or paid service is required. Blender includes NumPy.

- Scene only: `python run.py build`.
- A still for scoring: `python run.py still` (default frame 135).
- Exact checkpoint still: `python run.py reference`.
- Short pipeline test: `python run.py smoke --samples 4 --scale 25` renders six consecutive frames and verifies video/audio.
- When the user asks for a video: `python run.py video` renders all 300 unique frames. Do not substitute duplicated 15fps images.
- Recover an interrupted video: rerun with the same preset/engine/samples/scale, the same `--out`, and `--resume`. Changed input signatures are rejected.

The current production workflow is still-first: when the user requests an image or scoring, render a still only. A packaging test may use the short smoke command; it is not permission to render or publish a complete new video.

Change JSON parameters instead of adding dependent scripts that reopen prior iterations. Keep physical trajectories and contact sound linked through `scripts/model.py`. The model is independent vertical ballistics, not a full ball-to-ball rigid-body solver. Initial beads overlap slightly to suppress black gaps, so do not claim collision accuracy.

Inspect brightness, background/dais separation, narrow rim, and shadows in near-contact and high phases. A fixed overhead sun over fixed XY positions previously produced a stationary footprint; use finite angled area lights and native shadows. Keep the satin glass body with a glossy coat readable. Keep existing outputs; use a new output directory for changed presets.

After video rendering, require successful `verification.json`: expected duration, 30/1 fps, expected resolution, complete decoding and unique image hashes. Do not describe identical pixels on all GPUs/Blender versions as guaranteed. Full-resolution reference still and six-frame integration tests are described in `docs/VALIDATION.md`.
