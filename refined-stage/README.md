# Refined static stage

Target: the latest 1672 × 941 reference supplied in the conversation. Surrounding headline, navigation and footer text are deliberately omitted per the latest instruction. Screen artwork is retained from the supplied GLB.

## Deliverables
- `beyond_the_screen_refined.glb`: self-contained GLB with editable stage meshes, screen assemblies, camera, embedded textures and six punctual lights; no animation.
- `refined_stage.blend`: editable Blender 5.2 master, organized into Screens, Stage, Backdrop and Camera/Lights collections.
- `renders/final.png`: 1672 × 941, 128-sample denoised Cycles render of the **exported GLB after fresh import**.
- `comparison.png`: original upload versus refined result, plus an overlay of manually traced reference screen/pedestal landmarks.
- `inspection/refined_geometry.json`: projected display-corner coordinates, object counts.
- `inspection/glb_validation.json`: container, embedded assets, camera/light and animation checks.

## What changed
The supplied Blender file was verified to correspond to the supplied GLB. The GLB was used as the refinement base so its embedded screen artwork and portable materials could be retained. All three screen assemblies were fitted to reference image coordinates, including foreshortening and slight perspective skew. The pedestal's actual mesh was reshaped to the reference footprint and visible top/front/left edges. The floor now has finer wet-surface normal and roughness maps; the pedestal has new finer black-marble maps. Blue and warm punctual lighting, frame materials, useful assembly pivots and collection organization were added/refined.

The screens and pedestal are actual meshes with thickness. Each screen display, bezel, parent assembly and underglow remains separately editable. The ground and stage are not replaced with a raster of the reference.

## Verification and remaining differences
The image-coordinate fitting error against the **manually selected** display corners is below 0.001 pixel. This measures the fitted landmarks only; it is **not** a claim of pixel-identical reconstruction. Hidden screen edges are inferred, and the perspective fit can produce slight affine skew in the rectangular assemblies. Absolute real-world dimensions, rear construction and exact original camera/lighting cannot be established from one image.

The comparison overlay uses manually traced contours because the reference image is supplied inline in the conversation rather than as a local image file. It is not an automated reference-image difference metric.

The supplied interior screen artwork differs from the reference and was retained in accordance with the earlier instruction to ignore screen content. Fine marble veins, floor microstructure, reflection shapes and overhead illumination remain approximations. The original GLB's textured backdrop is retained for its atmospheric blue rays; those rays are a baked background effect, not volumetric geometry. The actual stage remains three-dimensional.

GLB does not define a world environment, renderer or screen-space/ray-traced reflection system. The embedded PBR maps, camera and punctual lights travel with the file, but reflections and tone mapping depend on the viewer. The final render uses Cycles, Standard view transform, a very dim blue-gray environment and the included camera. Use that camera and enable suitable reflections in a web viewer to reproduce the intended presentation.

## Reproducibility
Blender 5.2.2 LTS is available through the official `bpy` wheel in `/workspace/tools/blender52`. Original uploads are untouched. Scripts and intermediate renders are retained beside the deliverables. Run the Python scripts with `/workspace/tools/blender52/bin/python` for Blender operations; texture-generation scripts use the workspace Python with NumPy, SciPy and Pillow. This is a static scene only.
