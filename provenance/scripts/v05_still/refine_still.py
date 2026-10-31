import bpy, os
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bright_metal_glass_v05.blend')
s=bpy.context.scene
s.view_settings.view_transform='Standard'; s.view_settings.exposure=-.65
p=next(n for n in bpy.data.materials['MAT_Gold_to_Crimson'].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Roughness'].default_value=.27
s.render.filepath=r+'/bright_metal_glass_v05_final.png'
bpy.ops.wm.save_as_mainfile(filepath=r+'/bright_metal_glass_v05_final.blend')
bpy.ops.render.render(write_still=True)
