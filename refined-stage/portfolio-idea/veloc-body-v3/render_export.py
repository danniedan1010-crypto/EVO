import bpy,os,runpy,json
OUT=os.path.dirname(os.path.abspath(__file__))
runpy.run_path(OUT+'/build_car.py',run_name='__main__')
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=8;s.cycles.samples=128;s.cycles.use_denoising=True;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.filepath=OUT+'/veloc-body-render.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/veloc-body-v3.blend')
bpy.ops.render.render(write_still=True)
# Convert curves on export only, preserving editable curves in saved Blender file.
bpy.ops.object.select_all(action='DESELECT')
for c in bpy.data.collections:
 if c.name[:2] in ['01','02','03','04']:
  for o in c.objects:
   if o.type in {'MESH','CURVE'}:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.selected_objects if o.type=='MESH')
bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=OUT+'/veloc-body-v3.glb',export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
bpy.ops.export_scene.fbx(filepath=OUT+'/veloc-body-v3.fbx',use_selection=True,object_types={'MESH'},bake_anim=False)
print('EXPORTED',len(bpy.context.selected_objects),'objects',sum(len(o.data.polygons) for o in bpy.context.selected_objects if o.type=='MESH'),'faces')
