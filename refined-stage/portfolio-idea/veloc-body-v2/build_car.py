import bpy, math, os
from mathutils import Vector
from math import sin,cos,pi,sqrt,exp
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection': bpy.data.collections.remove(c)
COL={}
for name in ['01 Body panels','02 Glass and trim','03 Wheels and brakes','04 Lights and details','05 Studio']:
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);COL[name[:2]]=c

def place(obj,col):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 COL[col].objects.link(obj)
 return obj

def mat(name,color,metal=0,rough=.3,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
silver=mat('Satin silver metallic',(.42,.44,.47),.93,.23)
black=mat('Gloss black trim',(.009,.012,.017),.6,.22)
glass=mat('Smoked black glazing',(.003,.004,.006),0,.16)
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.15
rubber=mat('Tire rubber',(.014,.016,.019),0,.58)
alloy=mat('Machined graphite alloy',(.035,.041,.05),.9,.28)
brake=mat('Brake rotor steel',(.24,.26,.28),.8,.36)
white=mat('White LED',(.8,.93,1),.15,.2,5)
red=mat('Rear red LED',(1,.008,.003),.1,.2,4)

def mesh(name,v,f,m,col='01',smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);COL[col].objects.link(o);o.data.materials.append(m)
 for p in me.polygons:p.use_smooth=smooth
 return o

def grid(name,nu,nv,fn,m,col='01'):
 v=[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)];f=[]
 for i in range(nu):
  for j in range(nv):
   a=i*(nv+1)+j;f.append((a,a+nv+1,a+nv+2,a+1))
 return mesh(name,v,f,m,col)

def tube(name,pts,r,m,col='04'):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);COL[col].objects.link(ob);ob.data.materials.append(m);return ob

def cube(name,loc,scale,m,col='04',bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);place(o,col);o.data.materials.append(m)
 if bevel:mod=o.modifiers.new('Edge radius','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def interp(x,pts):
 if x<=pts[0][0]:return pts[0][1]
 if x>=pts[-1][0]:return pts[-1][1]
 for i in range(len(pts)-1):
  a,b=pts[i];c,d=pts[i+1]
  if x<=c:
   t=(x-a)/(c-a)
   m0=(d-pts[max(0,i-1)][1])/(c-pts[max(0,i-1)][0])
   m1=(pts[min(len(pts)-1,i+2)][1]-b)/(pts[min(len(pts)-1,i+2)][0]-a)
   return (2*t**3-3*t*t+1)*b+(t**3-2*t*t+t)*(c-a)*m0+(-2*t**3+3*t*t)*d+(t**3-t*t)*(c-a)*m1
# Long axis X; nose positive. Wheelbase 2.85m, width 2.04m.
WX=[-1.45,1.267];R=.48
width=lambda x:interp(x,[(-2.35,.78),(-2.1,.97),(-1.45,1.02),(-.5,.94),(.5,.94),(1.4,1.02),(1.9,.98),(2.4,.78)])
center=lambda x:interp(x,[(-2.35,.74),(-1.8,.91),(-1,.94),(.5,.96),(1.2,.98),(1.8,.75),(2.4,.61)])
shoulder=lambda x:center(x)+.03+.05*exp(-((x-1.267)/.48)**2)+.10*exp(-((x+1.45)/.53)**2)
def top(x,t):
 z=center(x)+(shoulder(x)-center(x))*sin(abs(t)*pi/2)**4
 return (x,width(x)*t,z)
grid('Continuous sculpted hood and haunches',160,50,lambda u,v:top(-2.35+(4.75-.38*abs(2*v-1)**4)*u,2*v-1),silver)
# Curved side skins with open wheel arches.
def bottom(x):
 z=.20
 for w in WX:
  dx=abs(x-w)
  if dx<.465:z=max(z,.5+sqrt(.465**2-dx**2))
 return z
for s in [-1,1]:
 def side(u,v,s=s):
  x=-2.35+4.37*u;z0=bottom(x);zt=shoulder(x);z=zt*(1-v)+z0*v
  y=width(x)-.105*sin(pi*v)**2-.045*v+.025*exp(-((v-.23)/.12)**2)
  return (x,s*y,z)
 grid(('Left' if s==1 else 'Right')+' body with wheel apertures',220,16,side,silver)
 for wx in WX:
  pts=[(wx+.471*cos(a),s*(width(wx+.471*cos(a))+.004),.5+.471*sin(a)) for a in [i*pi/100 for i in range(101)]]
  tube('Rolled wheel arch lip',pts,.012,silver,'01')
 # sculpted lower sill, seam and blade
 mesh('Angular rocker blade',[(1,s*.96,.19),(.93,s*.96,.28),(-.93,s*.96,.31),(-1,s*.98,.2),(1,s*1.01,.17),(-1,s*1.01,.17)],[(0,1,2,3),(0,3,5,4)],black)
 tube('Door lower crease',[(x,s*(width(x)-.025),.32+.02*cos(x*2)) for x in [1-i*1.95/50 for i in range(51)]],.008,silver,'01')
 # door shutline
 tube('Door rear shutline',[(-.82,s*.949,.94),(-.78,s*.884,.68),(-.80,s*.917,.37)],.002,black,'04')
 cube('Flush door handle',(-.6,s*.953,.86),(.14,.012,.022),alloy,'04',.008)
 mesh('Side vent',[(.77,s*.96,.91),(.48,s*.948,.9),(.43,s*.943,.58),(.58,s*.96,.65)],[(0,1,2,3)],black,'04',False)
# Roof canopy from front windshield to rear glass. Clean deliberately bounded glazing.
roof_sections=[(-1.63,.52,1.05),(-1.15,.60,1.20),(-.76,.49,1.43),(-.18,.50,1.46),(.15,.51,1.40),(.82,.86,1.08)]
def canopy(u,v):
 x=-1.63+2.45*u;t=v*2-1;w=interp(x,[(a,b) for a,b,c in roof_sections]);z=interp(x,[(a,c) for a,b,c in roof_sections]);return(x,w*t,z-.10-.015*t*t)
grid('Panoramic windshield roof and rear glass',90,32,canopy,glass,'02')
for s in [-1,1]:
 # side windows: bottom edge runs shoulder, upper edge follows roof
 def window(u,v,s=s):
  x=-1.55+2.30*u;w=interp(x,[(a,b) for a,b,c in roof_sections]);zt=interp(x,[(a,c-.10) for a,b,c in roof_sections]);yb=interp(x,[(-1.55,.78),(-.8,.87),(.3,.88),(.75,.86)]);zb=.965
  return (x,s*(w*(1-v)+yb*v),zt*(1-v)+zb*v)
 grid('Side glazing',70,12,window,glass,'02')
 # silver sweeping upper rail
 tube('Silver roof rail',[(x,s*interp(x,[(a,b+.012) for a,b,c in roof_sections]),interp(x,[(a,c-.115) for a,b,c in roof_sections])) for x in [-1.63+i*2.45/100 for i in range(101)]],.018,silver,'01')
 tube('Window sill',[(x,s*interp(x,[(-1.55,.78),(-.8,.87),(.3,.88),(.75,.86)]),.963) for x in [-1.55+i*2.3/80 for i in range(81)]],.018,silver,'01')
 # rear pillar and front pillar
 mesh('Rear silver C pillar',[(-1.60,s*.78,.95),(-1.05,s*.49,1.17),(-.87,s*.50,1.29),(-1.30,s*.83,.95)],[(0,1,2,3)],silver)
 tube('B pillar',[(-.55,s*.50,1.35),(-.65,s*.862,.965)],.027,black,'02')
 tube('A pillar',[(.15,s*.515,1.30),(.80,s*.86,.96)],.021,black,'02')
 tube('Mirror support',[(.51,s*.86,1.0),(.50,s*1.04,1.01)],.023,black)
 o=cube('Silver side mirror',(.48,s*1.08,1.04),(.26,.15,.075),silver,bevel=.035)
# Swept front edge and inset fascia, matched to the hood edge.
def lip(t):
 x=2.4-.38*abs(t)**4
 return (x,width(x)*t,top(x,t)[2])
grid('Swept upper bumper',70,8,lambda u,v:(lip(u*2-1)[0]+.035*sin(v*pi/2),lip(u*2-1)[1],lip(u*2-1)[2]-.145*v),black)
mesh('Deep central intake',[(2.30,-.66,.465),(2.30,.66,.465),(2.36,.77,.20),(2.36,-.77,.20)],[(0,1,2,3)],black,smooth=False)
for s in [-1,1]:
 mesh('Angular intake sidewall',[(2.36,s*.65,.49),(2.03,s*.97,.62),(2.03,s*.98,.25),(2.33,s*.91,.19),(2.43,s*.76,.20),(2.37,s*.70,.45),(2.13,s*.92,.48),(2.14,s*.92,.28),(2.42,s*.78,.23)],[(0,1,6,5),(1,2,7,6),(4,0,5,8)],silver,smooth=True)
 mesh('Side recessed intake',[(2.38,s*.70,.45),(2.14,s*.92,.48),(2.15,s*.92,.28),(2.43,s*.78,.23)],[(0,1,2,3)],black,smooth=False)
 grid('Sculpted lower bumper wing',24,8,lambda u,v,s=s:(2.44-.38*u-.45*v*sin(pi*u),s*(.65+.34*u),.46*(1-u)+.21*u+.045*sin(pi*u)+.06*v),silver)
 # LEDs on the exposed front lip, no intersection with the hood
 pts=[lip(s*(.49+.51*i/40)) for i in range(41)]
 tube('Headlight black surround',[(x+.035,y,z-.027) for x,y,z in pts],.037,black)
 for dz in [-.012,.012]:tube('Twin LED blade',[(x+.068,y,z-.027+dz) for x,y,z in pts],.006,white)
 grid('Hood extraction vent',30,8,lambda u,v,s=s:(1.18+.40*u,s*width(1.18+.40*u)*(.62+.08*v+.03*u),top(1.18+.40*u,.62+.08*v+.03*u)[2]+.002),black,'04')
 tube('Rear tail light',[(-2.365,s*(.12+i*.70/40),.77) for i in range(41)],.010,red)
# Swept thin lower splitter
mesh('Front carbon splitter',[(2.49,-.77,.17),(2.49,.77,.17),(2.34,.96,.17),(1.95,1.04,.17),(1.95,-1.04,.17),(2.34,-.96,.17)],[(0,1,2,3,4,5)],black,smooth=False)
cube('Inset front plate',(2.36,0,.325),(.018,.56,.16),black,bevel=.012)
# A fine actual grille lattice, recessed behind the opening.
for j in range(3):
 for i in range(17):
  y=-.48+i*.06+(j%2)*.03;z=.25+j*.065
  tube('Hexagonal grille cell',[(2.32,y+.034*cos(k*pi/3),z+.034*sin(k*pi/3)) for k in range(7)],.0015,black)
mesh('Rear bumper',[(-2.35,-.78,.74),(-2.35,.78,.74),(-2.36,.88,.24),(-2.36,-.88,.24)],[(0,1,2,3)],silver)
# Wheels with modeled tire crown, sidewall rings, spokes, rotors, drilled holes.
def cyl(name,loc,r,depth,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=80,radius=r,depth=depth,location=loc,rotation=(pi/2,0,0));o=bpy.context.object;o.name=name;place(o,'03');o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
for wx in WX:
 for s in [-1,1]:
  wy=s*.89;wz=.50
  def tire(u,v):
   a=u*2*pi;b=v*2*pi;rr=.415+.065*cos(b);return(wx+rr*cos(a),wy+.145*sin(b),wz+rr*sin(a))
  grid('Performance tire',128,32,tire,rubber,'03')
  # visible tire sidewalls
  for edge in [-1,1]:
   grid('Tire sidewall',100,5,lambda u,v,edge=edge:(wx+(.37+.075*v)*cos(u*2*pi),wy+edge*(.125+.012*sin(v*pi)),wz+(.37+.075*v)*sin(u*2*pi)),rubber,'03')
  yf=wy+s*.139
  for rr in [.365,.383]:
   tube('Polished rim lip',[(wx+rr*cos(a),yf,wz+rr*sin(a)) for a in [i*2*pi/100 for i in range(101)]],.009,alloy,'03')
  cyl('Vented brake rotor',(wx,wy+s*.08,wz),.31,.025,brake)
  cyl('Wheel center hub',(wx,yf,wz),.073,.04,alloy)
  for k in range(10):
   a=k*2*pi/10
   for d in [-1,1]:
    pts=[]
    for r,ang in [(.065,a),(.19,a+d*.10),(.37,a+d*.17)]:pts.append((wx+r*cos(ang),yf+s*(.015-.04*r/.37),wz+r*sin(ang)))
    tube('Split forged spoke',pts,.012,alloy,'03')
  for k in range(5):
   a=k*2*pi/5;cyl('Lug nut',(wx+.045*cos(a),yf+s*.027,wz+.045*sin(a)),.009,.012,silver)
  for k in range(40):
   a=k*2*pi/40
   for rr in [.25,.28]:cyl('Rotor perforation',(wx+rr*cos(a),wy+s*.095,wz+rr*sin(a)),.007,.002,black)
  cube('Brake caliper',(wx-.23,wy+s*.07,wz+.04),(.09,.08,.20),black,'03')
  # grooves on tread
  for k in range(72):
   a=k*2*pi/72
   pts=[(wx+(.480-.009*abs(t))*cos(a+.035*t),wy+.10*t,wz+(.480-.009*abs(t))*sin(a+.035*t)) for t in [-1,-.5,0,.5,1]]
   tube('Tire tread groove',pts,.0025,black,'03')
# Lower the cabin crown to the reference's squat coupe proportions.
for o in list(COL['02'].objects)+[o for o in COL['01'].objects if any(k in o.name for k in ['roof rail','C pillar'])]:
 if o.type=='MESH':
  for v in o.data.vertices:
   if v.co.z>1.0:v.co.z=1.0+(v.co.z-1.0)*1.034
   v.co.x=interp(v.co.x,[(-1.7,-1.47),(-.76,-.502),(.15,.02),(.82,.70)])
 elif o.type=='CURVE':
  for sp in o.data.splines:
   for p in sp.points:
    if p.co.z>1.0:p.co.z=1.0+(p.co.z-1.0)*1.034
    p.co.x=interp(p.co.x,[(-1.7,-1.47),(-.76,-.502),(.15,.02),(.82,.70)])
from mathutils import Matrix
bpy.context.view_layer.update()
for o in COL['03'].objects:
 center_world=o.matrix_world @ (sum((Vector(v) for v in o.bound_box),Vector())/8)
 wx=min(WX,key=lambda x:abs(x-center_world.x));sgn=1 if center_world.y>0 else -1
 pivot=Vector((wx,sgn*.89,.5))
 o.matrix_world=Matrix.Translation(pivot) @ Matrix.Scale(.90,4) @ Matrix.Translation(-pivot) @ o.matrix_world
for col in ['01','02','03','04']:
 for o in COL[col].objects:
  o.location.y*=.90;o.scale.y*=.90
# studio
floor=mat('Studio charcoal floor',(.009,.011,.014),.25,.29)
nt=floor.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=35;tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Object'],n.inputs['Vector']);n.inputs['Detail'].default_value=3;b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.018;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
cube('Studio floor',(0,0,.043),(2000,2000,.05),floor,'05',0)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.012,.014,.018,1);world.node_tree.nodes['Background'].inputs[1].default_value=.05

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size,scale in [('Long overhead softbox',(0,-4,5),700,4,(1,.3,1)),('Front key',(4,-3,4),950,3,(1,.3,1)),('Rear rim',(-3,1,4),850,3,(1,.25,1)),('Side reflection',(-1,4,4.5),900,4,(1,.15,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;place(o,'05');o.data.energy=power;o.data.shape='RECTANGLE';o.data.size=size;o.data.size_y=size*scale[1];aim(o,(0,0,.5))
bpy.ops.object.camera_add(location=(10.29121306970669,7.441836705672749,1.08318));cam=bpy.context.object;cam.name='Reference camera';place(cam,'05');aim(cam,(0,0,.77905));cam.data.lens=96.941;cam.data.shift_x=-.057227;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.resolution_x=1200;sc.render.resolution_y=675;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=OUT+'/preview.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/veloc-body-v2.blend')
