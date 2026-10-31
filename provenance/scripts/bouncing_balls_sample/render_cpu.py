import bpy, os, sys
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bouncing_balls_v01.blend')
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=8; s.cycles.use_denoising=True
for lamp in bpy.data.lights: lamp.energy*=.4
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.12
s.view_settings.view_transform='Standard'
s.view_settings.exposure=-.4
s.cycles.max_bounces=4; s.render.threads_mode='FIXED'; s.render.threads=8
s.render.resolution_x=540; s.render.resolution_y=960
s.render.use_persistent_data=True
if '--preview' in sys.argv:
 s.frame_set(90); s.render.filepath=r+'/preview_cpu.png'; bpy.ops.render.render(write_still=True)
else:
 bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_render_v01.blend')
 s.render.filepath=r+'/frames/'; bpy.ops.render.render(animation=True)
