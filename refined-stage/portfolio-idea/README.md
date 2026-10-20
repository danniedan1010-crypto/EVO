# VELOC assets and reconstruction reviews

Latest geometry work: [version 3 — files and visual comparison](veloc-body-v3/README.md). This remains an approximate reconstruction. [Version 2](veloc-body-v2/README.md) is preserved.

## Original material-only mesh review

This folder contains a material-refined export of the uploaded VELOC GLB, a Blender preview render, and a side-by-side comparison against the silver-car reference.

The mesh is a single connected vehicle body plus 36 disconnected part islands. The refined export preserves the supplied geometry and adds silver body paint, smoked glazing, rubber tires, dark alloy wheels, rear lamp color, and a dark front intake. It imports as one mesh with six materials and 9,650 faces.

## Files

- `veloc-model-refined.glb` — web-ready refined asset
- `veloc-model-refined.fbx` — editable interchange export
- `veloc-model-preview.png` — Blender render of the refined mesh
- `veloc-comparison.png` — reference and mesh render side by side

## Remaining differences

The uploaded geometry is not an exact reconstruction. Its roof and body are rounder and more generic than the sharper wedge-shaped reference, its wheels have five broad spokes rather than fine multi-spoke rims, and the glazing and front/rear details are less precise. This pass changes materials only; a closer match requires remodeling the car geometry and wheel details.
