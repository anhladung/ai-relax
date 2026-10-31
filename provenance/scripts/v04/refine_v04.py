import bpy, os, sys
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bouncing_balls_v04_cycles.blend')
s=bpy.context.scene
mat=bpy.data.materials['MAT_Gold_to_Crimson']; p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Coat Weight'].default_value=0; p.inputs['Metallic'].default_value=.92; p.inputs['Roughness'].default_value=.23
ramp=next(n for n in mat.node_tree.nodes if n.type=='VALTORGB')
ramp.color_ramp.elements[0].color=(1,.60,.018,1); ramp.color_ramp.elements[1].color=(.9,.16,.012,1); ramp.color_ramp.elements[2].color=(.62,.008,.015,1)
# Keep one more concentrated key to resolve individual soft shadows; fills stay broad.
key=bpy.data.objects['LGT_Key']; key.data.size=1.2; key.data.size_y=3
s.render.engine='BLENDER_EEVEE'; s.eevee.taa_render_samples=24; s.eevee.use_raytracing=True
try: s.eevee.ray_tracing_options.resolution_scale='2'
except (TypeError,ValueError): pass
s.render.resolution_x=720; s.render.resolution_y=1280
s.render.filepath=r+'/frames_final/'
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_v04_final.blend')
if '--preview' in sys.argv:
 for f in [1,34,135,250]:
  s.frame_set(f); s.render.filepath=r+'/final_preview_%03d.png'%f; bpy.ops.render.render(write_still=True)
else: bpy.ops.render.render(animation=True)
