import bpy, os, sys
from mathutils import Vector
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bouncing_balls_v04.blend')
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=24; s.cycles.use_denoising=True
s.cycles.max_bounces=8; s.cycles.transmission_bounces=6; s.cycles.glossy_bounces=3
s.cycles.use_light_tree=True
s.render.threads_mode='FIXED'; s.render.threads=8; s.render.use_persistent_data=True
s.render.resolution_x=540; s.render.resolution_y=960
for o in list(s.objects):
 if o.type=='LIGHT': bpy.data.objects.remove(o,do_unlink=True)
# Narrow strip softboxes give a coherent highlight rather than large white dots.
for name,loc,power,size,sizey in [('Key',(-4,-5,8),600,2,6),('Fill',(5,-3,5),220,3,5),('Rim',(1,5,7),750,1,5)]:
 d=bpy.data.lights.new('LGT_'+name,'AREA'); d.energy=power; d.shape='RECTANGLE'; d.size=size; d.size_y=sizey
 o=bpy.data.objects.new('LGT_'+name,d); s.collection.objects.link(o); o.location=loc; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
p=next(n for n in bpy.data.materials['MAT_Gold_to_Crimson'].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Metallic'].default_value=.82; p.inputs['Roughness'].default_value=.24; p.inputs['Coat Weight'].default_value=.035
stage=bpy.data.objects['Polished glass dais']
# A clear polished top with a satin underside, physically shaded by Cycles.
gp=next(n for n in stage.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
gp.inputs['Roughness'].default_value=.075; gp.inputs['Coat Weight'].default_value=0
fp=next(n for n in stage.data.materials[1].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
fp.inputs['Roughness'].default_value=.24; fp.inputs['Transmission Weight'].default_value=.6
s.view_settings.exposure=0
s.render.filepath=r+'/frames_cycles/'
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_v04_cycles.blend')
for f in [1,34,135,250]:
 s.frame_set(f); s.render.filepath=r+'/cycles_%03d.png'%f; bpy.ops.render.render(write_still=True)
