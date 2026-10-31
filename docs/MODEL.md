# Scene, motion and sound

`scripts/model.py` is the single motion/contact source. For bead i, radius is `3*sqrt((i+0.5)/2566)` and angle is `i*pi*(3-sqrt(5))`. These golden-angle positions create the initial sunflower arms. Sphere radius is 0.061 and dais radius 3.16, leaving a narrow margin. Intentional initial sphere overlap suppresses dark interstices.

Release height 3.6, gravity 6.5 scene-units/s². All beads first fall from the same height. Initial rebound velocity is 80–98% of release-impact velocity, increasing radially. Subsequent rebound speed retains 99.3%; resulting flight durations drift, generating funnels and central domes. These are scene units, not a validated Jupiter gravity experiment. Each XY stays fixed. There is no rigid-body solver, lateral collision, mass interaction or friction.

Historical motion uses collision-center base `0.12 + 0.051`. The visible sphere was later enlarged to 0.061 for tight packing, so the visible surface overlaps the dais by approximately 0.010 scene units at contact. This small artistic overlap is preserved for reference reproducibility; it is not claimed to be collision-exact. For nonpenetrating geometric contact, change `trajectory_radius` to 0.061 in a new preset, accepting that it differs from the original checkpoint.

Absolute shape keys store each 30fps sample and one extra endpoint, with linear subframe interpolation. The saved scene does not depend on a Python frame-change handler. A simple `eval_time` driver maps frames to the keys. This is a deterministic precomputed trajectory, not a simulated mesh membrane.

Three finite rectangular area lights create height-dependent shadow projection and penumbra. Cycles computes the glass/metal light transport; optional Eevee uses its own approximations and a planar probe. The approved scene uses a polished dielectric coat over satin partially transmitting glass. It is not clear window glass, and it is not a fixed mirror-image duplicate. Brighter white dais and lavender backdrop remain separate.

`scripts/sound.py` generates sample-timed wooden-bar modes with seeded noise, pentatonic pitch mapping, velocity, stereo placement, a restrained collective low body, and short room reflections. Contacts are grouped into 8.3ms windows to avoid rendering thousands of simultaneous audio voices. The first mass landing becomes a 36ms chord. This is original synthesized mallet audio, not an acoustic marimba recording.

Full video is 300 unique source frames/10 seconds/30 fps. `smoke` uses frames 130–135 and trims sound from the corresponding instant. `verification.json` checks the encoded result rather than trusting container labels only.
