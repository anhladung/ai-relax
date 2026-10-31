import bpy, os, sys, math, json
from mathutils import Vector
r=os.path.dirname(os.path.abspath(__file__)); os.makedirs(r+'/frames',exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.dirname(r)+'/v03/bouncing_balls_v03_final.blend')
s=bpy.context.scene; s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=32
s.eevee.use_raytracing=True
print('RAY OPTIONS',[(p.identifier) for p in s.eevee.ray_tracing_options.bl_rna.properties])
try: s.eevee.ray_tracing_options.resolution_scale='1'
except (TypeError,ValueError): pass
def principled(name,color,metal=0,rough=.3,trans=0):
 m=bpy.data.materials.new(name); m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 p.inputs['Transmission Weight'].default_value=trans; p.inputs['IOR'].default_value=1.46
 return m,p
# Remove the artistic mirrored duplicate: planar reflection now comes from the scene.
for o in s.objects:
 if 'Faint vertically mirrored' in o.name: o.hide_render=True
balls=bpy.data.materials['MAT_Gold_to_Crimson']; p=next(n for n in balls.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Metallic'].default_value=.88; p.inputs['Roughness'].default_value=.20
p.inputs['Coat Weight'].default_value=.32; p.inputs['Coat Roughness'].default_value=.13; p.inputs['Emission Strength'].default_value=0
# A polished glass top with a mildly frosted underside gives a readable glass disc.
glass,gp=principled('MAT_Polished_Clear_Glass',(.94,.985,1),0,.055,1)
gp.inputs['Coat Weight'].default_value=.25
frost,fp=principled('MAT_Frosted_Glass_Underside',(.80,.88,.94),0,.28,.65)
stage=bpy.data.objects['Round porcelain dais']; stage.name='Polished glass dais'
stage.scale.x*=3.6/3.22; stage.scale.y*=3.6/3.22
stage.data.materials.clear(); stage.data.materials.append(glass); stage.data.materials.append(frost)
for poly in stage.data.polygons: poly.material_index=1 if poly.normal.z<-.5 else 0
for lamp in list(bpy.data.objects):
 if lamp.type=='LIGHT': bpy.data.objects.remove(lamp,do_unlink=True)
def aim(o,pt): o.rotation_euler=(Vector(pt)-o.location).to_track_quat('-Z','Y').to_euler()
sun_data=bpy.data.lights.new('LGT_Physical_Soft_Shadow','SUN'); sun_data.energy=2.2; sun_data.angle=.04; sun_data.use_shadow=True
sun=bpy.data.objects.new('LGT_Physical_Soft_Shadow',sun_data); s.collection.objects.link(sun); sun.rotation_euler=(.1,0,0)
for name,loc,power,size in [('Key_softbox',(-4,-4,8),1050,4),('Fill_softbox',(4,-2,7),700,5),('Rim_strip',(0,5,6),1400,3)]:
 d=bpy.data.lights.new('LGT_'+name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.use_shadow=True
 o=bpy.data.objects.new('LGT_'+name,d); s.collection.objects.link(o); o.location=loc; aim(o,(0,0,1))
# Neutral blue-grey floor/backdrop, no texture or busy scenery.
floor=next((o for o in s.objects if o.type=='MESH' and o.name=='Plane'),None)
if floor is None:
 bpy.ops.mesh.primitive_plane_add(size=200); floor=bpy.context.object
floor.name='Quiet blue grey studio floor'; floor.hide_render=False; floor.location.z=-.17
fm,fmp=principled('MAT_Quiet_Blue_Grey',(.12,.155,.20),0,.6)
floor.data.materials.clear(); floor.data.materials.append(fm)
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs[0].default_value=(.22,.27,.34,1); bg.inputs[1].default_value=.6
# True planar reflection capture, positioned directly above the glass surface.
probe_data=bpy.data.lightprobes.new('Glass planar reflection','PLANE')
probe=bpy.data.objects.new('Glass planar reflection',probe_data); s.collection.objects.link(probe); probe.location=(0,0,.125); probe.scale=(3.65,3.65,3.65)
print('PROBE',[(p.identifier) for p in probe_data.bl_rna.properties])
if hasattr(probe_data,'influence_distance'): probe_data.influence_distance=5
if hasattr(probe_data,'clip_start'): probe_data.clip_start=.01
s.camera.data.ortho_scale=14.2
s.view_settings.view_transform='AgX'; s.view_settings.exposure=.1
s.render.filepath=r+'/frames/'
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_v04.blend')
json.dump({'glass':'IOR 1.46, roughness 0.055, transmission 1; frosted underside','beads':'metallic .88, roughness .20, coat .32','background':'blue-grey matte','fake_reflection_hidden':True,'shadow_sun_tilt':.1,'shadow_sun_angle':.04,'disc_radius':3.6},open(r+'/settings.json','w'),indent=2)
if '--preview' in sys.argv:
 for f in [1,34,135,250]:
  s.frame_set(f); s.render.filepath=r+'/preview_%03d.png'%f; bpy.ops.render.render(write_still=True)
else: bpy.ops.render.render(animation=True)
