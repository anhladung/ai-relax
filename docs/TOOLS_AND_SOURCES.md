# Tools, skills and provenance

## Runtime included

The maintained Python scripts, JSON preset, original synthesized sound generator, checked reference scene and preview assets are in this repo. No imported asset store model, texture, font, API secret, downloaded Instagram clip, user Downloads file or external linked library is needed.

Original Instagram videos were visual references supplied by the user. They are not redistributed; the provided assets here are our generated scene/previews. Huge frame directories, crash logs and superseded .blend backups are omitted because they are generated intermediates.

## Used during development

| Tool/skill | Role | Required to run this package? |
|---|---|---|
| Blender 5.2.3 LTS | bpy scene authoring, Geometry Nodes instancing, Cycles/Eevee rendering | Yes, separate installation |
| Blender-bundled NumPy 2.3.4 | Bead positions, trajectories, PCM synthesis | Included with tested Blender |
| Python 3.13 | Launcher and verification | Python 3.11+ host install |
| FFmpeg/FFprobe 9.0.2 | Encode/decode, frame counting, hashes, preview sheets | For video/smoke |
| Blender MCP | Initial scene inspection and process launching in the original development session | No; headless CLI replaces it |
| PowerShell, Git, GitHub CLI | Local orchestration and publishing | Git for clone; others optional |
| Codex `skill-creator` | Packaging guidance | No; supplied by Codex, not redistributed as third-party code |
| `blender-director`, `rendering`, `lighting`, `materials` | Scene planning, look development, visual checks | No; archived under vendor |

The four Blender skill texts used locally are preserved in `vendor/blender-skills/` under their MIT license. Upstream source: [arjun988/blender-skills](https://github.com/arjun988/blender-skills), checked source commit `8f778d2405a214b508d4c7d80742be8e43acdd52`. The local versions had additional project preferences; the maintained production preferences for this scene are consolidated in `docs/PRODUCTION_STANDARDS.md`. Vendor skill texts may refer to a larger upstream skill set or MCP; use the self-contained `skills/ai-relax` entrypoint for this package.

Blender MCP development helper was the `mcp-for-blender` add-on/server (reported add-on 1.8, protocol 15); [project setup](https://mcp-for-blender.com/). No paid generator was used. Do not install it merely to run `run.py`.

`provenance/scripts/` contains historical script files still present on the development machine. They refer to previous iteration scenes and are **not portable entrypoints**. Some earlier v02 source was no longer on disk when packaging; its trajectory, packing and instancing behavior is reconstructed in `scripts/model.py` and `scripts/build_scene.py` and validated against the retained final checkpoint. The runtime does not depend on these historical files. No claim is made that every deleted experiment can be recovered.

External tools keep their own licenses and are not bundled here. The vendor MIT notice applies to the vendor files. No additional license grant for the project's original files is selected by this packaging task; the repository owner can choose one later.
