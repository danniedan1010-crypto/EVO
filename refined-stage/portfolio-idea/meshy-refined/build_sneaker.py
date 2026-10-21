"""Refine the supplied Meshy shoe without changing its mesh or UV layout."""
import bpy,glob,os,json,math
import numpy as np
from mathutils import Vector, Matrix
ROOT=os.path.dirname(os.path.abspath(__file__))
SOURCE=glob.glob('/workspace/attachments/*/meshy_blue_pulse_sneaker.glb')[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SOURCE)
s=bpy.context.scene
modelcol=bpy.data.collections.new('01 | Sneaker');s.collection.children.link(modelcol)
objs=[o for o in s.objects if o.type=='MESH']
for o in objs:
 for c in list(o.users_collection):c.objects.unlink(o)
 modelcol.objects.link(o);o.name='Blue Pulse | Meshy original geometry'
 o.data.transform(o.matrix_world.copy());o.parent=None;o.matrix_world=Matrix.Identity(4)
# Normalize to a 30cm product; preserve source vertex positions and UVs.
points=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));factor=.30/(hi.x-lo.x)
for o in objs:
 o.scale*=factor;o.location.z-=lo.z*factor
m=objs[0].data.materials[0];m.name='Blue Pulse | Textile, cobalt overlays and rubber PBR atlas'
source_images={}
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE':
  a=np.array(n.image.pixels[:],dtype=np.float32).reshape(n.image.size[1],n.image.size[0],4);source_images[n.image.name]=(n.image,a.copy())
pbr=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
base_node=next(l.from_node for l in pbr.inputs['Base Color'].links)
colorim=base_node.image;color=np.array(colorim.pixels[:],dtype=np.float32).reshape(2048,2048,4)
# Image.pixels are linear RGB for the imported sRGB base-color texture.
blue=np.clip((color[:,:,2]-color[:,:,0]*1.65-.015)/.055,0,1)
scene_collections={}
for name in ['02 | Studio floor','03 | Lighting','04 | Cameras']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);scene_collections[name]=c
def move(o,name):
 for c in list(o.users_collection):c.objects.unlink(o)
 scene_collections[name].objects.link(o)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
mat=bpy.data.materials.new('Studio | dark reflective floor');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.015,.019,.027,1);p.inputs['Roughness'].default_value=.30;p.inputs['Metallic'].default_value=.18
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='Studio | charcoal floor';floor.data.materials.append(mat);move(floor,'02 | Studio floor')
for name,loc,power,size,c in [
 ('Key softbox',(-.15,-.2,.65),22,.55,(1,.95,.9)),
 ('Cool rim',(.28,.3,.4),18,.38,(.65,.78,1)),
 ('Front fill',(-.45,-.2,.25),5,.30,(1,1,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='Light | '+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=c;aim(o,(0,0,.055));move(o,'03 | Lighting')
bpy.ops.object.camera_add(location=(-.39,-.59,.31));cam=bpy.context.object;cam.name='Camera | product three quarter';cam.data.lens=62;aim(cam,(0,0,.063));s.camera=cam;move(cam,'04 | Cameras')
s.world=bpy.data.worlds.new('Studio | dark world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.015,.022,.04,1);s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.22
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=75;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
s.render.filepath=ROOT+'/sneaker-before.png';bpy.ops.render.render(write_still=True)
# Tune maps while retaining all source texture detail.
newcol=color.copy();blue_gain=np.array([.72,1.12,1.85]);ivory_gain=np.array([1.025,1.016,.99]);newcol[:,:,:3]=np.clip(color[:,:,:3]*(ivory_gain[None,None,:]*(1-blue[:,:,None])+blue_gain[None,None,:]*blue[:,:,None]),0,1)
colorim.pixels.foreach_set(newcol.ravel());colorim.pack()
# Locate the ORM image through the imported material's non-color texture nodes.
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE' and n.image!=colorim:
  outgoing=[l.to_node.type for l in n.outputs['Color'].links]
  if 'NORMAL_MAP' in outgoing:continue
  arr=np.array(n.image.pixels[:],dtype=np.float32).reshape(2048,2048,4)
  # Preserve the roughness map's existing detail and suppress spurious metallic texels.
  target=np.clip(arr[:,:,1]+.14, .58,.86)*(1-blue)+np.clip(arr[:,:,1]*.72,.34,.58)*blue
  arr[:,:,1]=target;arr[:,:,2]=0;n.image.pixels.foreach_set(arr.ravel());n.image.pack()
for n in m.node_tree.nodes:
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.65
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.gltf(filepath=ROOT+'/blue-pulse-refined.glb',export_format='GLB',use_selection=True,export_image_format='WEBP',export_image_quality=95)
s.render.resolution_percentage=100;s.cycles.samples=64;s.render.filepath=ROOT+'/sneaker-after.png'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blue-pulse-studio.blend');bpy.ops.render.render(write_still=True)
info={'geometry_changed':False,'source_mesh_preserved':True,'source_uv_preserved':True,'normalized_length_m':.30,'changes':['Cobalt blue color tuning','Warmer ivory color tuning','Map-based roughness separation','Nonmetallic shoe materials','Normal strength reduced to 0.65'],'limitations':['Original silhouette, shoe design, laces and source texture artifacts remain','Lime heel accent and precise panel layout of image reference are not reconstructed','No exact-reference-match claim'],'source_vertices':sum(len(o.data.vertices) for o in objs),'source_triangles':sum(len(o.data.loop_triangles) for o in objs)}
open(ROOT+'/refinement.json','w').write(json.dumps(info,indent=2))
