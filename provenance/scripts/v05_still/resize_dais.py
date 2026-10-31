import bpy, os
r=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=r+'/bright_metal_glass_v05_final.blend')
s=bpy.context.scene
stage=bpy.data.objects['Polished glass dais']
factor=3.16/3.6
stage.scale.x*=factor; stage.scale.y*=factor
s.render.filepath=r+'/bright_metal_glass_v06_small_dais.png'
bpy.ops.wm.save_as_mainfile(filepath=r+'/bright_metal_glass_v06_small_dais.blend')
bpy.ops.render.render(write_still=True)
