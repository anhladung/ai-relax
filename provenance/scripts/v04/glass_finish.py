import bpy, os, sys
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bouncing_balls_v04_final.blend')
s=bpy.context.scene
stage=bpy.data.objects['Polished glass dais']
p=next(n for n in stage.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
# Glossy clear surface over a light-scattering satin glass body.
p.inputs['Base Color'].default_value=(.40,.46,.53,1)
p.inputs['Transmission Weight'].default_value=.32; p.inputs['Roughness'].default_value=.30
p.inputs['Coat Weight'].default_value=1; p.inputs['Coat Roughness'].default_value=.055; p.inputs['Coat IOR'].default_value=1.46
q=next(n for n in stage.data.materials[1].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
q.inputs['Transmission Weight'].default_value=.3; q.inputs['Roughness'].default_value=.35
s.eevee.taa_render_samples=16
s.render.filepath=r+'/frames_glass/'
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_v04_glass.blend')
if '--preview' in sys.argv:
 for f in [1,34,135,250]:
  s.frame_set(f); s.render.filepath=r+'/glass_preview_%03d.png'%f; bpy.ops.render.render(write_still=True)
else: bpy.ops.render.render(animation=True)
