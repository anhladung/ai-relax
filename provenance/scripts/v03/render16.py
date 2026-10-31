import bpy, os, sys
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bouncing_balls_v03.blend')
s=bpy.context.scene; s.eevee.taa_render_samples=16
sun=bpy.data.objects['LGT_Bead_Shadow_Key']; sun.rotation_euler=(0,0,0); sun.data.angle=.02
s.render.filepath=r+'/frames_centered/'
if '--preview' in sys.argv:
 s.frame_set(250); s.render.filepath=r+'/preview16_250.png'; bpy.ops.render.render(write_still=True)
else:
 s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_v03_final.blend'); bpy.ops.render.render(animation=True)
