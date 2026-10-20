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
silver=mat('Satin silver metallic',(.34,.36,.39),.95,.18)
silver.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.25
silver.node_tree.nodes.get('Principled BSDF').inputs['Coat Roughness'].default_value=.14
wing_silver=mat('Satin bumper silver',(.34,.36,.39),.82,.30)
black=mat('Gloss black trim',(.009,.012,.017),.6,.22)
glass=mat('Smoked black glazing',(.18,.23,.27),0,.06)
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.45
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
rubber=mat('Tire rubber',(.006,.007,.008),0,.72)
alloy=mat('Machined graphite alloy',(.035,.041,.05),.9,.28)
brake=mat('Brake rotor steel',(.025,.03,.035),.7,.48)
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
center=lambda x:interp(x,[(-2.35,.74),(-1.8,.91),(-1,.94),(.5,.97),(1.2,.89),(1.8,.75),(2.4,.62)])
shoulder=lambda x:interp(x,[(-2.35,.79),(-1.45,1.00),(-.5,.985),(.5,1.005),(1.267,.955),(1.8,.78),(2.4,.63)])
def top(x,t):
 z=center(x)+(shoulder(x)-center(x))*abs(t)**6
 if .55<x<2.25:
  line=.48+.10*(2.25-x)/1.7;z+=.010*sin(pi*(x-.55)/1.7)*exp(-((abs(t)-line)/.025)**2)
 return (x,width(x)*t,z)
hood=grid('Continuous sculpted hood and haunches',160,50,lambda u,v:top(-2.35+(4.75-.38*abs(2*v-1)**4)*u,2*v-1),silver)
# Open the cabin aperture so transmission reveals the interior, not a silver slab.
import bmesh
bm=bmesh.new();bm.from_mesh(hood.data)
remove=[f for f in bm.faces if -1.35<f.calc_center_median().x<.60 and abs(f.calc_center_median().y)<.77]
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(hood.data);bm.free()
def side_y(x,z):
 v=max(0,min(1,(shoulder(x)-z)/(shoulder(x)-.20)))
 return width(x)+interp(v,[(0,0),(.13,.01),(.24,-.015),(.62,-.065),(.68,-.035),(.72,-.012),(.78,-.03),(1,-.065)])
# Curved side skins with open wheel arches.
def bottom(x):
 z=.20
 for w in WX:
  dx=abs(x-w)
  if dx<.425:z=max(z,.5+sqrt(.425**2-dx**2))
 return z
for s in [-1,1]:
 def side(u,v,s=s):
  x=-2.35+4.37*u;z0=bottom(x);zt=shoulder(x);z=zt*(1-v)+z0*v
  y=side_y(x,z)
  return (x,s*y,z)
 o=grid(('Left' if s==1 else 'Right')+' body with wheel apertures',220,16,side,silver)
 if s==-1:o.data.flip_normals()
 for wx in WX:
  pts=[(wx+.431*cos(a),s*(side_y(wx+.431*cos(a),.5+.431*sin(a))+.003),.5+.431*sin(a)) for a in [i*pi/100 for i in range(101)]]
  tube('Rolled wheel arch lip',pts,.005,silver,'01')
 # sculpted lower sill, seam and blade
 skirt_points=[(1,.20),(.93,.25),(-.93,.43),(-1,.20)]
 mesh('Angular rocker recess',[(x,s*(side_y(x,z)+.005),z) for x,z in skirt_points],[(0,1,2,3)],black)
 # door shutline
 tube('Door rear shutline',[(x,s*(side_y(x,z)+.002),z) for x,z in [(-.82,.94),(-.84,.80),(-.88,.62),(-.85,.40)]],.002,black,'04')
 cube('Flush door handle',(-.6,s*.953,.86),(.14,.012,.022),alloy,'04',.008)
 mesh('Side vent',[(.77,s*.96,.91),(.50,s*.948,.90),(.49,s*.943,.73),(.63,s*.96,.78)],[(0,1,2,3)],black,'04',False)
# Unified cabin profiles: the windshield corners follow the image landmarks.
roof_sections=[(-1.45,.78,1.01),(-1.05,.63,1.21),(-.60,.54,1.31),(-.10,.53,1.35),(0,.5315,1.339),(.6463,.9051,1.028)]
def canopy(u,v):
 x=-1.45+2.0963*u;t=2*v-1
 return (x,interp(x,[(a,b) for a,b,c in roof_sections])*t,interp(x,[(a,c) for a,b,c in roof_sections])-.015*t*t)
glass_roof=grid('Windshield panoramic roof rear glazing',100,32,canopy,glass,'02')
glass_roof.modifiers.new('Glass thickness','SOLIDIFY').thickness=.004
for sg in [-1,1]:
 def win(u,v,sg=sg):
  x=-1.40+2.0463*u;yt=interp(x,[(a,b) for a,b,c in roof_sections]);zt=interp(x,[(a,c-.015) for a,b,c in roof_sections]);yb=interp(x,[(-1.4,.78),(-.8,.87),(.3,.88),(.6463,.9051)])
  return(x,sg*(yt*(1-v)+yb*v),zt*(1-v)+.98*v)
 o=grid('Quarter and door glazing',90,16,win,glass,'02')
 if sg==-1:o.data.flip_normals()
 o.modifiers.new('Glass thickness','SOLIDIFY').thickness=.004
 tube('Silver roof rail',[(x,sg*(interp(x,[(a,b) for a,b,c in roof_sections])+.005),interp(x,[(a,c-.010) for a,b,c in roof_sections])) for x in [-1.45+i*1.45/100 for i in range(101)]],.013,silver,'01')
 tube('Window sill',[(x,sg*interp(x,[(-1.4,.78),(-.8,.87),(.3,.88),(.6463,.9051)]),.98) for x in [-1.4+i*2.0463/90 for i in range(91)]],.010,silver,'01')
 corners=[Vector((-1.45,sg*.78,.99)),Vector((-1.05,sg*.63,1.195)),Vector((-.83,sg*.57,1.245)),Vector((-1.18,sg*.82,.99))]
 def quarter(u,v,corners=corners,sg=sg):
  p=corners[0].lerp(corners[1],u).lerp(corners[3].lerp(corners[2],u),v);p.y+=sg*.025*sin(pi*u)*sin(pi*v);return tuple(p)
 o=grid('Curved rear C pillar',24,12,quarter,silver)
 if sg==-1:o.data.flip_normals()
 tube('B pillar',[(-.50,sg*.54,1.31),(-.65,sg*.866,.98)],.022,black,'02')
 tube('A pillar',[(0,sg*.5315,1.324),(.6463,sg*.9051,1.013)],.016,black,'02')
 tube('Mirror support',[(.48,sg*.89,1.0),(.48,sg*1.04,1.01)],.018,black)
 mirror_local=[(.15,-.035,.015),(.15,.035,.015),(-.14,.075,.03),(-.14,-.075,.03),(.14,-.03,-.02),(.14,.03,-.02),(-.13,.065,-.02),(-.13,-.065,-.02)]
 o=mesh('Tapered silver mirror housing',[(.48+x,sg*(1.08+y),1.04+z) for x,y,z in mirror_local],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],silver,'04',False)
 be=o.modifiers.new('Mirror edge radius','BEVEL');be.width=.007;be.segments=3;o.modifiers.new('Mirror normals','WEIGHTED_NORMAL')
 mesh('Mirror inset',[(.335,sg*(1.08+y),1.04+z) for y,z in [(-.06,.023),(.06,.023),(.055,-.012),(-.055,-.012)]],[(0,1,2,3)],alloy,'04',False)
grid('Windshield cowl',12,40,lambda u,v:(.6463+.1937*u,(2*v-1)*.89,1.013*(1-u)+top(.84,(2*v-1)*.89/width(.84))[2]*u),black,'02')
# Dark editable cockpit visible through the glass.
interior=mat('Charcoal leather interior',(.009,.011,.014),0,.72)
cube('Cabin floor',(-.4,0,.62),(1.9,1.52,.06),interior,'02')
cube('Dashboard',(.42,0,.92),(.36,1.53,.14),interior,'02',.06)
for sg in [-1,1]:
 seat=cube('Seat back',(-.55,sg*.36,1.03),(.14,.38,.45),interior,'02',.065);seat.rotation_euler.y=-.17
 cube('Headrest',(-.60,sg*.36,1.22),(.13,.24,.15),interior,'02',.04)
 cube('Seat cushion',(-.32,sg*.36,.76),(.43,.39,.10),interior,'02',.04)
 cube('Door interior panel',(-.38,sg*.77,.83),(1.55,.06,.3),interior,'02',.03)
tube('Steering wheel',[(.21,.36+.14*cos(a),1.0+.14*sin(a)) for a in [i*2*pi/64 for i in range(65)]],.016,interior,'02')
# Swept front edge and inset fascia, matched to the hood edge.
def lip(t):
 x=2.4-.38*abs(t)**4
 return (x,width(x)*t,top(x,t)[2])
o=grid('Swept upper bumper',70,8,lambda u,v:(lip(u*2-1)[0]+.035*sin(v*pi/2),lip(u*2-1)[1],lip(u*2-1)[2]-.145*v),black);o.data.flip_normals()
mesh('Deep central intake',[(1.95,-.66,.465),(1.95,.66,.465),(1.95,.77,.20),(1.95,-.77,.20)],[(0,1,2,3)],black,smooth=False)
for s in [-1,1]:
 # Ribbon and cheek corners fitted to visible reference landmarks.
 A=Vector((2.42319,s*.45,.49610));B=Vector((2.16385,s*.91,.51655));C=Vector((1.98884,s*.98,.34611));D=Vector((2.31338,s*.90,.30617));E=Vector((1.75349,s*1.0,.26889));H=Vector((1.98067,s*.98,.70817));J=Vector((1.76469,s*1.02,.76714));K=Vector((2.38,s*.45,.61))
 mesh('Recess above bumper ribbon',[tuple(K),tuple(H),tuple(B),tuple(A)],[(0,1,2,3)],black,smooth=False)
 mesh('Outer duct recess',[tuple(H),tuple(C),tuple(B)],[(0,1,2)],black,smooth=False)
 def wing(u,v,A=A,B=B,D=D,E=E,s=s):
  p=A.lerp(B,u).lerp(D.lerp(E,u),v)
  p.x+=.11*sin(pi*v)*u**3;p.y+=s*.025*sin(pi*v)*(1-u)
  p.z+=.016*sin(pi*u)*sin(pi*v)
  return tuple(p)
 o=grid('Swept four-sided bumper ribbon',48,28,wing,wing_silver)
 if s==1:o.data.flip_normals()
 o.modifiers.new('Panel thickness','SOLIDIFY').thickness=.010
 def cheek(u,v,H=H,J=J,C=C,E=E,s=s):
  p=H.lerp(J,u).lerp(C.lerp(E,u),v);p.y+=s*.015*sin(pi*u)*sin(pi*v);return tuple(p)
 o=grid('Outer fender front cheek',24,32,cheek,silver)
 if s==-1:o.data.flip_normals()
 # Unequal LED blade lengths and separate slopes, fitted to the reference.
 LI=Vector((2.39585,s*.52,.61123));LO=Vector((2.04867,s*.98,.64460));UI=Vector((2.29208,s*.70,.67462));UO=Vector((2.00720,s*.99,.70678))
 upperleft=UI+(UI-UO)*.40
 housing=[tuple(LI+Vector((-.008,0,-.022))),tuple(LO+Vector((-.008,0,-.022))),tuple(UO+Vector((-.008,0,.024))),tuple(upperleft+Vector((-.008,0,.024)))]
 mesh('Tapered headlamp housing',housing,[(0,1,2,3)],black,'04',False)
 for start,end in [(LI,LO),(UI,UO)]:tube('White LED blade',[tuple(start.lerp(end,i/30)) for i in range(31)],.009,white)
 o=grid('Hood extraction vent',30,8,lambda u,v,s=s:(1.18+.40*u,s*width(1.18+.40*u)*(.62+.08*v+.03*u),top(1.18+.40*u,.62+.08*v+.03*u)[2]+.002),black,'04')
 if s==-1:o.data.flip_normals()
 tube('Rear tail light',[(-2.365,s*(.12+i*.70/40),.80) for i in range(41)],.008,red)
 tube('Rear wraparound red blade',[(x,s*width(x)*.96,top(x,.96)[2]+.015) for x in [-1.85-i*.45/40 for i in range(41)]],.008,red)
# Swept thin lower splitter
mesh('Front carbon splitter',[(2.49,-.77,.17),(2.49,.77,.17),(2.34,.96,.17),(1.95,1.04,.17),(1.95,-1.04,.17),(2.34,-.96,.17)],[(0,1,2,3,4,5)],black,smooth=False)
cube('Inset front plate',(2.36,0,.325),(.018,.56,.16),black,bevel=.012)
# A fine actual grille lattice, recessed behind the opening.
for j in range(3):
 for i in range(17):
  y=-.48+i*.06+(j%2)*.03;z=.25+j*.065
  tube('Hexagonal grille cell',[(2.10,y+.034*cos(k*pi/3),z+.034*sin(k*pi/3)) for k in range(7)],.0015,black)
mesh('Rear bumper',[(-2.35,-.78,.74),(-2.35,.78,.74),(-2.36,.88,.24),(-2.36,-.88,.24)],[(0,1,2,3)],silver)
# Wheels with modeled tire crown, sidewall rings, spokes, rotors, drilled holes.
def cyl(name,loc,r,depth,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=80,radius=r,depth=depth,location=loc,rotation=(pi/2,0,0));o=bpy.context.object;o.name=name;place(o,'03');o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
for wx in WX:
 for s in [-1,1]:
  wy=s*.89;wz=.50
  profile=[(.36,-.12),(.395,-.145),(.438,-.125),(.45,-.095),(.45,.095),(.438,.125),(.395,.145),(.36,.12)]
  def tire(u,v):
   a=u*2*pi;q=(v%1)*len(profile);i=int(q);t=q-i
   p0=Vector(profile[(i-1)%len(profile)]);p1=Vector(profile[i]);p2=Vector(profile[(i+1)%len(profile)]);p3=Vector(profile[(i+2)%len(profile)])
   q=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
   rr,yy=q;return(wx+rr*cos(a),wy+yy,wz+rr*sin(a))
  o=grid('Low profile performance tire',128,48,tire,rubber,'03');o.data.flip_normals()
  yf=wy+s*.139
  for rr in [.365,.383]:
   tube('Polished rim lip',[(wx+rr*cos(a),yf,wz+rr*sin(a)) for a in [i*2*pi/100 for i in range(101)]],.009,alloy,'03')
  cyl('Vented brake rotor',(wx,wy+s*.08,wz),.31,.025,brake)
  cyl('Wheel center hub',(wx,yf,wz),.073,.04,alloy)
  def blade(name,polar,widths):
   verts=[]
   pts=[Vector((wx+r*cos(ang),yf+s*(.018-.04*r/.37),wz+r*sin(ang))) for r,ang in polar]
   for j,p in enumerate(pts):
    tang=pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)];n=Vector((-tang.z,0,tang.x)).normalized()*widths[j]
    verts.extend([tuple(p+n),tuple(p-n)])
   faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(len(pts)-1)]
   ob=mesh(name,verts,faces,alloy,'03',False);ob.modifiers.new('Forging depth','SOLIDIFY').thickness=.018
   be=ob.modifiers.new('Machined edge','BEVEL');be.width=.0025;be.segments=2
  for k in range(10):
   a=k*2*pi/10
   blade('Forged Y spoke stem',[(.055,a),(.19,a+.025)],[.017,.013])
   for sign in [-1,1]:blade('Forged Y spoke branch',[(.18,a+.025),(.27,a+sign*.10),(.37,a+sign*.18)],[.012,.010,.006])
  for k in range(5):
   a=k*2*pi/5;cyl('Lug nut',(wx+.045*cos(a),yf+s*.027,wz+.045*sin(a)),.009,.012,silver)
  for k in range(40):
   a=k*2*pi/40
   for rr in [.25,.28]:cyl('Rotor perforation',(wx+rr*cos(a),wy+s*.095,wz+rr*sin(a)),.007,.002,black)
  cube('Brake caliper',(wx-.23,wy+s*.07,wz+.04),(.09,.08,.20),black,'03')
  # grooves on tread
  for k in range(72):
   a=k*2*pi/72
   pts=[(wx+(.4502-.003*abs(t))*cos(a+.035*t),wy+.10*t,wz+(.4502-.003*abs(t))*sin(a+.035*t)) for t in [-1,-.5,0,.5,1]]
   tube('Tire tread groove',pts,.0025,black,'03')
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
floor=mat('Studio charcoal floor',(.003,.004,.005),.35,.22)
nt=floor.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=35;tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Object'],n.inputs['Vector']);n.inputs['Detail'].default_value=3;b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.018;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
coarse=nt.nodes.new('ShaderNodeTexNoise');coarse.inputs['Scale'].default_value=7;coarse.inputs['Detail'].default_value=3;nt.links.new(tc.outputs['Object'],coarse.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=.10;ramp.inputs['To Max'].default_value=.27;nt.links.new(coarse.outputs['Fac'],ramp.inputs['Value']);nt.links.new(ramp.outputs['Result'],nt.nodes.get('Principled BSDF').inputs['Roughness'])
cube('Studio floor',(0,0,.070),(2000,2000,.05),floor,'05',0)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.012,.014,.018,1);world.node_tree.nodes['Background'].inputs[1].default_value=.05

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size,scale in [('Front broad reflection',(5,5,2.5),350,4,(1,.5,1)),('Long overhead softbox',(0,-4,5),950,4,(1,.12,1)),('Front key',(4,-3,4),650,3,(1,.13,1)),('Rear rim',(-3,1,4),850,3,(1,.25,1)),('Side reflection',(-1,5,1.8),450,4,(1,.35,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;place(o,'05');o.data.energy=power;o.data.shape='RECTANGLE';o.data.size=size;o.data.size_y=size*scale[1];aim(o,(0,0,.5))
bpy.ops.object.camera_add(location=(10.29121306970669,7.441836705672749,1.08318));cam=bpy.context.object;cam.name='Reference camera';place(cam,'05');aim(cam,(0,0,.77905));cam.data.lens=96.941;cam.data.shift_x=-.057227;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.resolution_x=1200;sc.render.resolution_y=675;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=OUT+'/preview.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/veloc-body-v3.blend')
