import bpy, os
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bouncing_balls_render_v01.blend')
s=bpy.context.scene; s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=8
os.makedirs(r+'/frames_eevee',exist_ok=True)
s.render.filepath=r+'/frames_eevee/'
bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_final_v01.blend')
bpy.ops.render.render(animation=True)
