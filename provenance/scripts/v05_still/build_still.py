import bpy, os
r=os.path.dirname(os.path.abspath(__file__)); os.makedirs(r,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.dirname(r)+'/v04/bouncing_balls_v04_glass.blend')
s=bpy.context.scene
s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=32; s.cycles.use_denoising=True
s.cycles.max_bounces=8; s.cycles.transmission_bounces=6; s.cycles.glossy_bounces=3
s.render.threads_mode='FIXED'; s.render.threads=8
s.render.resolution_x=720; s.render.resolution_y=1280; s.render.resolution_percentage=100
if hasattr(s.render,'use_motion_blur'): s.render.use_motion_blur=False
# Bright neutral environment fills the colored metal bodies, not only their highlights.
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs[0].default_value=(.8,.86,1,1); bg.inputs[1].default_value=.9
for lamp in bpy.data.lights: lamp.energy*=1.55
mat=bpy.data.materials['MAT_Gold_to_Crimson']; p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Metallic'].default_value=.78; p.inputs['Roughness'].default_value=.23; p.inputs['Coat Weight'].default_value=.06
ramp=next(n for n in mat.node_tree.nodes if n.type=='VALTORGB')
ramp.color_ramp.elements[0].color=(1,.88,.008,1)
ramp.color_ramp.elements[1].color=(1,.27,.006,1)
ramp.color_ramp.elements[2].color=(.88,.015,.009,1)
# Cool white glass disc is deliberately distinct from the muted lavender backdrop.
stage=bpy.data.objects['Polished glass dais']
p=next(n for n in stage.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.88,.96,1,1); p.inputs['Transmission Weight'].default_value=.35
p.inputs['Roughness'].default_value=.23; p.inputs['Coat Weight'].default_value=1; p.inputs['Coat Roughness'].default_value=.055
q=next(n for n in stage.data.materials[1].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
q.inputs['Base Color'].default_value=(.75,.86,.94,1)
fm=bpy.data.materials['MAT_Quiet_Blue_Grey']; fp=next(n for n in fm.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
fp.inputs['Base Color'].default_value=(.17,.115,.235,1); fp.inputs['Roughness'].default_value=.85
s.view_settings.view_transform='AgX'; s.view_settings.exposure=.5
s.frame_set(135)
s.render.image_settings.file_format='PNG'; s.render.filepath=r+'/bright_metal_glass_v05.png'
bpy.ops.wm.save_as_mainfile(filepath=r+'/bright_metal_glass_v05.blend')
bpy.ops.render.render(write_still=True)
