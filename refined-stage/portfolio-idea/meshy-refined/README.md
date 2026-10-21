# Meshy Blue Pulse sneaker refinement

Material refinement of the uploaded `meshy_blue_pulse_sneaker.glb` with its original surface shape and UVs preserved. Imported quantization transforms are baked without changing the surface, and the model is normalized to 30 cm length with the sole on the ground.

## Files

- `blue-pulse-refined.glb`: refined, textured model for web use; studio is excluded. Three 2048px WebP maps are embedded (95 quality); the viewer must support `EXT_texture_webp` and `KHR_texture_transform`, as the supplied source does.
- `blue-pulse-studio.blend`: editable product, PBR texture images, studio lights, floor and camera, organized into collections.
- `sneaker-before.png` and `sneaker-after.png`: source and refined material previews under the same lighting and camera. The source preview has a lower render resolution/sample count; differences in fine sampling should not be interpreted as material changes.
- `comparison.jpg`: reference image, source material render and refined material render.
- `build_sneaker.py`: reproducible build using the original upload in `/workspace/attachments`.
- `refinement.json` and `verification.json`: changes, limitations and verification results.

## Changes and limits

Source color, roughness/metallic and normal maps are retained. Blue is shifted toward cobalt, ivory is warmed slightly, textile roughness is increased, blue overlays have lower roughness, unintended metallic values are removed, and normal-map strength is reduced to 0.65.

This is a material refinement, not an exact reconstruction. The supplied mesh's panel design, sole shape, laces and texture artifacts remain. In particular, the generated reference shoe has different panels, a lime heel accent, and more defined textile detail. Materials cannot correct those geometric differences. The single source mesh and texture atlas remain a single asset; parts are not independently reconstructed. There is no animation.

## Car remains blocked

The uploaded Meshy car is 57,886,784 bytes, exceeding the upload-download tool's 32 MiB transfer limit. The manifest source domain is blocked by the environment network policy. No car file is included here and no car refinement is claimed. A ZIP below 32 MiB or a file committed to the authorized EVO repository would provide an accessible source.
