# Hyper3D material study

Original uploaded car and sneaker geometry is preserved. These are material studies, not exact reproductions of the reference photographs.

- `car-refined.glb`, `sneaker-refined.glb`: web assets with approximate material regions.
- `car-studio.blend`, `sneaker-studio.blend`: editable model, material nodes, lights, floor and camera.
- `car-studio.png`, `sneaker-studio.png`: rendered previews.
- `refine.py`: reproducible build, using the original uploaded GLBs in `/workspace/attachments`.

The source GLBs each contain a single mesh, one material and a 2×2 pixel embedded image. They do not contain detailed photographic textures or authored component/material boundaries. Silver, dark glazing, wheel, ivory, cobalt and sole regions have therefore been assigned using approximate spatial masks. These have been rasterized into 2048px UV color and roughness/metallic atlases so boundaries can cross triangles. The placement is approximate and still requires manual texture painting for production quality. The new atlases contain assigned colors rather than recovered photographic detail. Shoe overlays, laces and lining have not been individually reconstructed; the source mesh is preserved.

The previews demonstrate material direction and lighting. They do not establish an exact match to the original images. Neither model contains animation.
