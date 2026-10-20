# VELOC body reconstruction — review version 2

This is a geometry rebuild, replacing the earlier material-only treatment of the uploaded car. It is **not a 100% match to the reference** and should not be treated as an approved final asset.

## Deliverables

- `veloc-body-v2.blend`: editable scene, reference camera, studio, materials, and separately named body, glazing, wheel, brake, lighting, and trim objects. Saved with Blender 5.2.2 LTS.
- `veloc-body-v2.glb`: car geometry and materials for interchange; excludes the studio and camera.
- `veloc-body-v2.fbx`: alternate geometry export.
- `veloc-body-render.png`: 1672 × 941 Cycles render, 128 samples with denoising.
- `comparison.jpg`: original reference and current render at the same image dimensions.
- `build_car.py` and `render_export.py`: reproducible construction and export scripts. Run `render_export.py` with Blender 5.2's Python/bpy or Blender's `--python` option.

## Geometry changes

Rebuilt the hood, fenders with wheel openings, side panels, panoramic canopy, front fascia, intakes, splitter, lower bumper wings, mirrors, roof trim, headlights and rear light strips. Replaced the wheels with modeled split spokes, tire profiles and tread, rotors, calipers and hubs. Adjusted the perspective camera against visible reference landmarks. All geometry is static; no reference image plane, animation, or website interaction is used.

## Remaining differences

The reference's exact sculpted bumper, hood creases, fender transitions, roof/window outlines, and door surfacing are not fully reproduced. The wheels, vents, lamps, and trim are approximations rather than exact replicas. Studio reflections and surface finish also differ. Some panels are separate surface meshes, not a single watertight production body, and the dense component structure is not yet optimized for real-time web use.

The reference is one view: the unseen side, rear, underbody, interior, physical dimensions, original camera, and lighting are not established by it. Those areas use inferred geometry. The visible differences above are also genuine modeling limitations of this review version, not just missing reference information.

The previous exports remain in the parent folder for comparison. This version does not overwrite them.
