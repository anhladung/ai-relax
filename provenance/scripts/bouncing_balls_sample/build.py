import bpy, math, os, sys, json, wave
import numpy as np
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
os.makedirs(ROOT+'/frames',exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'
s.render.resolution_x=720; s.render.resolution_y=1280; s.render.resolution_percentage=100
s.render.fps=30; s.render.fps_base=1; s.frame_start=1; s.frame_end=300
s.render.image_settings.file_format='PNG'
s.world=bpy.data.worlds.new('Dark studio'); s.world.use_nodes=True
s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.006,.009,.015,1)
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.3
s.view_settings.view_transform='AgX'
col=bpy.data.collections.new('COL_Bouncing_Balls'); s.collection.children.link(col)
def mat(name,color,metal=0,rough=.35):
 m=bpy.data.materials.new(name); m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 return m
balls=mat('MAT_Gold_to_Crimson',(.8,.2,.01),.25,.25)
n=balls.node_tree.nodes; l=balls.node_tree.links; p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
geo=n.new('ShaderNodeNewGeometry'); sep=n.new('ShaderNodeSeparateXYZ'); l.new(geo.outputs['Position'],sep.inputs[0])
sq=[]
for axis in ['X','Y']:
 a=n.new('ShaderNodeMath'); a.operation='MULTIPLY'; l.new(sep.outputs[axis],a.inputs[0]); l.new(sep.outputs[axis],a.inputs[1]); sq.append(a)
a=n.new('ShaderNodeMath'); a.operation='ADD'; l.new(sq[0].outputs[0],a.inputs[0]); l.new(sq[1].outputs[0],a.inputs[1])
b=n.new('ShaderNodeMath'); b.operation='SQRT'; l.new(a.outputs[0],b.inputs[0])
c=n.new('ShaderNodeMath'); c.operation='DIVIDE'; c.inputs[1].default_value=3; l.new(b.outputs[0],c.inputs[0])
r=n.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(1,.72,.008,1); r.color_ramp.elements[1].color=(.65,.006,.015,1)
r.color_ramp.elements.new(.55).color=(1,.15,.005,1); l.new(c.outputs[0],r.inputs[0]); l.new(r.outputs[0],p.inputs['Base Color'])
xy=[]
for j in range(-32,33):
 for i in range(-32,33):
  x=(i+.5*(j%2))*.112; y=j*.112*math.sqrt(3)/2
  if x*x+y*y<=2.98**2: xy.append((x,y))
xy=np.array(xy); rr=np.linalg.norm(xy,axis=1)/3
mesh=bpy.data.meshes.new('Point lattice'); mesh.from_pydata([(x,y,2.65) for x,y in xy],[],[])
ob=bpy.data.objects.new('Spheres hex packed disc',mesh); col.objects.link(ob)
ng=bpy.data.node_groups.new('GN_Instanced_Spheres','GeometryNodeTree')
ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
inp=ng.nodes.new('NodeGroupInput'); out=ng.nodes.new('NodeGroupOutput')
ico=ng.nodes.new('GeometryNodeMeshIcoSphere'); ico.inputs['Radius'].default_value=.047; ico.inputs['Subdivisions'].default_value=2
sm=ng.nodes.new('GeometryNodeSetShadeSmooth'); ng.links.new(ico.outputs['Mesh'],sm.inputs['Geometry'])
ma=ng.nodes.new('GeometryNodeSetMaterial'); ma.inputs['Material'].default_value=balls; ng.links.new(sm.outputs['Geometry'],ma.inputs['Geometry'])
inst=ng.nodes.new('GeometryNodeInstanceOnPoints'); ng.links.new(inp.outputs[0],inst.inputs['Points']); ng.links.new(ma.outputs[0],inst.inputs['Instance']); ng.links.new(inst.outputs[0],out.inputs[0])
mod=ob.modifiers.new('Lightweight sphere instances','NODES'); mod.node_group=ng
white=mat('MAT_Porcelain',(.65,.69,.74),.12,.26)
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=3.22,depth=.17,location=(0,0,.035)); stage=bpy.context.object; stage.name='Round porcelain dais'; stage.data.materials.append(white)
bev=stage.modifiers.new('Soft rim','BEVEL'); bev.width=.055; bev.segments=3
for poly in stage.data.polygons: poly.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.06)); bpy.context.object.data.materials.append(mat('MAT_Charcoal',(.008,.011,.017),.2,.25))
def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-13,11)); cam=bpy.context.object; cam.name='CAM_Studio'; aim(cam,(0,0,1.35)); cam.data.type='ORTHO'; cam.data.ortho_scale=12.8; s.camera=cam
for name,loc,power,size in [('Key',(-4,-5,9),1700,7),('Fill',(5,-1,6),1200,6),('Rim',(0,5,7),1900,5)]:
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; o=bpy.data.objects.new(name,d); s.collection.objects.link(o); o.location=loc; aim(o,(0,0,1))
g=8.; h=2.5; base=.17; first=math.sqrt(2*h/g); v=math.sqrt(2*g*h)
elastic=.975-.075*rr**1.3
def heights(t):
 if t<first: return np.full(len(xy),base+h-.5*g*t*t)
 remaining=np.full(len(xy),t-first); speed=v*elastic; z=np.full(len(xy),base)
 for bounce in range(100):
  flight=2*speed/g; active=(remaining>=0)&(remaining<flight)
  z[active]=base+speed[active]*remaining[active]-.5*g*remaining[active]**2
  remaining=np.where(remaining>=flight,remaining-flight,-1); speed*=elastic
  if np.all(remaining<0): break
 return z
def update(scene):
 t=(scene.frame_current-1)/30
 coords=np.column_stack((xy,heights(t))).astype(np.float32)
 mesh.vertices.foreach_set('co',coords.ravel()); mesh.update()
bpy.app.handlers.frame_change_pre.append(update)
# Persist motion as point-mesh shape keys so the .blend opens without handlers.
ob.shape_key_add(name='Basis')
for f in range(1,301):
 k=ob.shape_key_add(name='Frame_%03d'%f); coords=np.column_stack((xy,heights((f-1)/30))).astype(np.float32); k.data.foreach_set('co',coords.ravel())
 k.value=0; k.keyframe_insert('value',frame=f-1); k.value=1; k.keyframe_insert('value',frame=f); k.value=0; k.keyframe_insert('value',frame=f+1)
bpy.app.handlers.frame_change_pre.remove(update)
if mesh.shape_keys.animation_data and mesh.shape_keys.animation_data.action:
 try:
  for fc in mesh.shape_keys.animation_data.action.fcurves:
   for kp in fc.keyframe_points: kp.interpolation='LINEAR'
 except AttributeError: pass
# Synthetic marimba-like notes from contact times; aggregate dense impacts to <=30 onsets/s.
sr=48000; sound=np.zeros((sr*10,2),dtype=np.float64); events={}
for ri,e in zip(rr,elastic):
 t=first; vel=v*e; b=0
 while t<10:
  slot=int(t*30); events.setdefault(slot,[]).append(float(ri)); t+=2*vel/g; vel*=e; b+=1
  if b>100: break
notes=[130.8128,146.8324,164.8138,195.9977,220.0,261.6256]
for slot,radii in events.items():
 start=int(slot/30*sr); count=min(int(.7*sr),len(sound)-start); tt=np.arange(count)/sr; radius=float(np.mean(radii)); freq=notes[min(5,int(radius*6))]
 tone=(np.sin(2*math.pi*freq*tt)*np.exp(-tt*7)+.32*np.sin(2*math.pi*freq*2.76*tt)*np.exp(-tt*20)+.12*np.sin(2*math.pi*freq*5.4*tt)*np.exp(-tt*35))
 tone*=np.minimum(tt/.003,1)*min(.16,.022*math.sqrt(len(radii)))
 sound[start:start+count,0]+=tone*(.8-.3*radius); sound[start:start+count,1]+=tone*(.5+.3*radius)
for delay,amp in [(.083,.12),(.151,.07),(.229,.04)]:
 shift=int(sr*delay); sound[shift:]+=sound[:-shift].copy()*amp
sound=np.tanh(sound*1.3); sound*=.8/max(.8,np.max(np.abs(sound)))
with wave.open(ROOT+'/marimba.wav','wb') as w:
 w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((sound*32767).astype('<i2').tobytes())
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/bouncing_balls_v01.blend')
json.dump({'balls':len(xy),'fps':30,'frames':300,'seconds':10,'gravity':g,'restitution_center':.975,'restitution_edge':.9,'audio':'synthesized marimba-like'},open(ROOT+'/settings.json','w'),indent=2)
if '--preview' in sys.argv:
 for f in [1,90,180,270]:
  s.frame_set(f); s.render.filepath=ROOT+'/preview_%03d.png'%f; bpy.ops.render.render(write_still=True)
else:
 s.render.filepath=ROOT+'/frames/'; bpy.ops.render.render(animation=True)
