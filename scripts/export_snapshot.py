"""Maintainer helper: sanitize the approved local checkpoint before distributing it."""
import argparse
import json
from pathlib import Path
import sys
import bpy
p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--dest',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); dest=Path(a.dest).resolve(); dest.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()))
for o in list(bpy.data.objects):
    if o.hide_render: bpy.data.objects.remove(o,do_unlink=True)
for t in list(bpy.data.texts): bpy.data.texts.remove(t)
if bpy.data.libraries: raise RuntimeError('Snapshot has linked libraries; make them local first')
if any(i.filepath for i in bpy.data.images if i.type not in ['RENDER_RESULT','COMPOSITING']): raise RuntimeError('Snapshot has external image references; review before shipping')
s=bpy.context.scene; s.render.filepath='//outputs/frames/'; s.frame_set(135)
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
audit={'blender':bpy.app.version_string,'objects':len(s.objects),'external_libraries':len(bpy.data.libraries),'external_textures':0,'frame':s.frame_current,'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'camera_scale':s.camera.data.ortho_scale,'lights':{o.name:{'energy':o.data.energy,'location':list(o.location),'size':o.data.size,'size_y':o.data.size_y} for o in s.objects if o.type=='LIGHT'}}
(dest.with_suffix('.json')).write_text(json.dumps(audit,indent=2),encoding='utf-8')
