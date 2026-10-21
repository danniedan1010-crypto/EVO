import bpy,glob,math,os,json,bmesh
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
def mat(name,c,metal=0,rough=.4):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
for kind in ['car','sneaker']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=glob.glob('/workspace/attachments/*/hyper3d_'+kind+'*.glb')[0])
 obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');obj.name=kind.title()+' | Original Hyper3D geometry'
 # Bake source transform, retain original mesh shape and UVs.
 bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # Preserve original topology and imported surface normals.
 vs=obj.data.vertices
 lo=Vector(tuple(min(v.co[i] for v in vs) for i in range(3)));hi=Vector(tuple(max(v.co[i] for v in vs) for i in range(3)))
 center=(hi+lo)/2;size=hi-lo
 obj.data.materials.clear()
 if kind=='car':
  mats=[mat('Silver automotive paint',(.48,.51,.55),.87,.23),mat('Dark smoked glazing',(.012,.019,.026),.32,.16),mat('Tire rubber',(.012,.014,.017),0,.67),mat('Machined graphite rims',(.105,.12,.14),.88,.25),mat('Carbon lower trim',(.018,.022,.027),.35,.34)]
 else:
  mats=[mat('Ivory technical textile',(.72,.69,.60),0,.76),mat('Cobalt outsole and heel',(.012,.055,.43),0,.43),mat('Cream sculpted midsole',(.83,.79,.68),0,.54)]
 if kind=='sneaker':
  n=mats[0].node_tree.nodes;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=260;t.inputs['Detail'].default_value=2;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.003;mats[0].node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);mats[0].node_tree.links.new(b.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
 for m in mats:obj.data.materials.append(m)
 counts={m.name:0 for m in mats}
 for f in obj.data.polygons:
  c=sum((vs[i].co for i in f.vertices),Vector())/len(f.vertices);x,y,z=((c[i]-center[i])/size[i] for i in range(3));idx=0
  if kind=='car':
   # Distinguish outer wheels from body by axle proximity and cross-car extent.
   r=min(math.hypot((y-.31)*size.y,(z+.22)*size.z),math.hypot((y+.31)*size.y,(z+.22)*size.z))
   if abs(x)>.37 and r<size.z*.30:
    idx=3 if abs(x)>.40 and r<size.z*.205 else 2
   elif z>.22 and abs(y)<.265:idx=1
   elif z<-.34 and abs(x)<.37:idx=4
  else:
   if z<-.31:idx=1
   elif z<-.14:idx=2
   elif y>.23 and z>.19:idx=1
   elif abs(x)>.22 and y>.03 and -.06<z<(.17+.08*math.sin(y*12)):idx=1
  f.material_index=idx;f.use_smooth=True;counts[mats[idx].name]+=1
 # Rasterize spatial material masks into the existing UV atlas, so color boundaries
 # cross faces cleanly instead of following triangle edges. Geometry stays intact.
 import numpy as np
 N=2048
 filled=np.zeros((N,N),dtype=bool)
 color=np.zeros((N,N,4),dtype=np.float32);color[:,:,:3]=mats[0].diffuse_color[:3];color[:,:,3]=1
 orm=np.ones((N,N,4),dtype=np.float32)
 orm[:,:,1]=.5;orm[:,:,2]=0
 obj.data.calc_loop_triangles();uv=obj.data.uv_layers.active.data
 def classify(q):
  x,y,z=q.T;idx=np.zeros(len(q),dtype=np.int32)
  if kind=='car':
   rr=np.minimum(np.hypot((y-.31)*size.y,(z+.22)*size.z),np.hypot((y+.31)*size.y,(z+.22)*size.z))
   wheel=(np.abs(x)>.37)&(rr<size.z*.30)
   idx[(z>.22)&(np.abs(y)<.265)]=1
   idx[(z<-.34)&(np.abs(x)<.37)]=4
   idx[wheel]=2;idx[wheel&(np.abs(x)>.40)&(rr<size.z*.205)]=3
  else:
   idx[z<-.14]=2;idx[z<-.31]=1
   idx[(y>.23)&(z>.19)]=1
   idx[(np.abs(x)>.22)&(y>.03)&(z>-.06)&(z<(.17+.08*np.sin(y*12)))]=1
  return idx
 palette=np.array([m.diffuse_color[:] for m in mats]);rough=np.array([m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value for m in mats]);metal=np.array([m.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value for m in mats])
 # Blender image pixels use linear RGB. Material base colors are linear as well.
 for tri in obj.data.loop_triangles:
  uvv=np.array([uv[l].uv[:] for l in tri.loops])*(N-1)
  mn=np.maximum(np.floor(uvv.min(0)).astype(int),0);mx=np.minimum(np.ceil(uvv.max(0)).astype(int),N-1)
  if np.any(mx<mn):continue
  xx,yy=np.meshgrid(np.arange(mn[0],mx[0]+1),np.arange(mn[1],mx[1]+1));xx=xx.ravel();yy=yy.ravel()
  a,b,c=uvv;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-8:continue
  w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
  valid=(w0>=-.006)&(w1>=-.006)&(w2>=-.006)
  if not valid.any():continue
  xx=xx[valid];yy=yy[valid];weights=np.stack([w0[valid],w1[valid],w2[valid]],axis=1)
  pts=np.array([vs[i].co[:] for i in tri.vertices]);q=(weights@pts-np.array(center))/np.array(size)
  filled[yy,xx]=True
  idx=classify(q);color[yy,xx]=palette[idx];orm[yy,xx,1]=rough[idx];orm[yy,xx,2]=metal[idx]
 # A tiny UV gutter fills unpainted border texels without changing mesh topology.
 for gutter in range(8):
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
   neighbor=np.roll(filled,(dy,dx),(0,1));take=(~filled)&neighbor
   color[take]=np.roll(color,(dy,dx),(0,1))[take];orm[take]=np.roll(orm,(dy,dx),(0,1))[take];filled[take]=True
 for label,pixels in [('basecolor',color),('orm',orm)]:
  im=bpy.data.images.new(kind+' | '+label,width=N,height=N,alpha=True)
  im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(pixels.ravel());im.pack()
  if label=='basecolor':baseim=im
  else:ormim=im
 for m in mats:
  tree=m.node_tree;p=tree.nodes.get('Principled BSDF');tex=tree.nodes.new('ShaderNodeTexImage');tex.image=baseim;tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  tex=tree.nodes.new('ShaderNodeTexImage');tex.image=ormim;sep=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(tex.outputs['Color'],sep.inputs['Color']);tree.links.new(sep.outputs['Green'],p.inputs['Roughness']);tree.links.new(sep.outputs['Blue'],p.inputs['Metallic'])

 scale=(4.75 if kind=='car' else 2.4)/size.y
 obj.scale=(scale,)*3;obj.location.z=-lo.z*scale+.015
 bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,kind+'-refined.glb'),use_selection=True,export_format='GLB')
 floor=mat('Studio charcoal',(.024,.027,.032),.25,.28)
 # Fine surface relief creates broad, subtle floor reflections.
 nodes=floor.node_tree.nodes;noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=95;noise.inputs['Detail'].default_value=2
 bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.025;floor.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);floor.node_tree.links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
 bpy.ops.mesh.primitive_plane_add(size=2000);bpy.context.object.name='Studio | reflective floor';bpy.context.object.data.materials.append(floor)
 def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
 def light(name,loc,power,size,color):
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;aim(o,(0,0,.5))
 light('Studio | overhead softbox',(1,-1,6),800,5,(1,.96,.9));light('Studio | cool rim',(-4,2,3),650,4,(.64,.78,1));light('Studio | front strip',(4,-4,2.5),500,3,(1,1,1))
 bpy.ops.object.camera_add(location=(6.3,-8.2,1.9) if kind=='car' else (3.8,-5,2.6));cam=bpy.context.object;cam.name='Camera | product review';aim(cam,(0,0,.62 if kind=='car' else .65));cam.data.lens=62;bpy.context.scene.camera=cam
 s=bpy.context.scene;s.world=bpy.data.worlds.new('Studio world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.008,.009,.012,1);s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.25;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(ROOT,kind+'-studio.png')
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,kind+'-studio.blend'));bpy.ops.render.render(write_still=True)
 with open(os.path.join(ROOT,kind+'-inspection.json'),'w') as f:json.dump({'output_vertices':len(vs),'output_faces':len(obj.data.polygons),'material_faces':counts,'geometry_modified':False,'material_regions':'Approximate spatial masks; source provides no authored component separation.'},f,indent=2)
