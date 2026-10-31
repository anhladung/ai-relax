"""Run inside Blender; independent of saved scenes, add-ons, local paths or external assets."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import Motion,validate
from sound import synthesize

def material(name,color,metal=0,rough=.3,trans=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=color; p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough; p.inputs['Transmission Weight'].default_value=trans; p.inputs['IOR'].default_value=1.46
    return m,p

def configure(s,c,a):
    s.render.engine='CYCLES' if a.engine=='cycles' else 'BLENDER_EEVEE'
    if a.engine=='cycles':
        s.cycles.device='CPU'; s.cycles.samples=a.samples or c['samples']; s.cycles.use_denoising=True
        s.cycles.max_bounces=8; s.cycles.transmission_bounces=6; s.cycles.glossy_bounces=3; s.cycles.seed=c['seed']
    else:
        s.eevee.taa_render_samples=a.samples or c['samples']; s.eevee.use_raytracing=True
    s.render.threads_mode='FIXED'; s.render.threads=a.threads; s.render.use_persistent_data=True
    s.render.resolution_x=max(16,int(c['resolution'][0]*a.scale/100)//2*2); s.render.resolution_y=max(16,int(c['resolution'][1]*a.scale/100)//2*2); s.render.resolution_percentage=100
    s.render.fps=c['fps']; s.render.fps_base=1; s.frame_start=1; s.frame_end=round(c['duration']*c['fps']); s.frame_step=1
    s.render.image_settings.file_format='PNG'
    if hasattr(s.render,'use_motion_blur'): s.render.use_motion_blur=a.mode in ['video','smoke']
    if hasattr(s.render,'motion_blur_shutter'): s.render.motion_blur_shutter=.32

def build(c):
    bpy.ops.wm.read_factory_settings(use_empty=True); s=bpy.context.scene; m=Motion(c)
    collection=bpy.data.collections.new('COL_Bouncing_Balls'); s.collection.children.link(collection)
    mesh=bpy.data.meshes.new('Sunflower spiral point positions'); mesh.from_pydata(m.positions(0),[],[])
    ob=bpy.data.objects.new('Phyllotaxis sunflower spheres',mesh); collection.objects.link(ob)
    ob.shape_key_add(name='Initial disc')
    frames=round(c['duration']*c['fps'])
    for frame in range(2,frames+2):
        key=ob.shape_key_add(name='Sample_%03d'%frame); key.data.foreach_set('co',m.positions((frame-1)/c['fps']).ravel())
    keys=mesh.shape_keys; keys.use_relative=False
    for key in keys.key_blocks: key.interpolation='KEY_LINEAR'
    keys.driver_add('eval_time').driver.expression='max(0,(frame-1)*10)'
    look=c['look']; balls,p=material('MAT_Gold_to_Crimson',look['colors'][0],look['metallic'],look['roughness'])
    p.inputs['Coat Weight'].default_value=look['coat']; p.inputs['Coat Roughness'].default_value=.13
    p.inputs['Specular IOR Level'].default_value=.3
    nodes=balls.node_tree.nodes; links=balls.node_tree.links
    geo=nodes.new('ShaderNodeNewGeometry'); sep=nodes.new('ShaderNodeSeparateXYZ'); links.new(geo.outputs['Position'],sep.inputs[0])
    sq=[]
    for axis in ['X','Y']:
        n=nodes.new('ShaderNodeMath'); n.operation='MULTIPLY'; links.new(sep.outputs[axis],n.inputs[0]); links.new(sep.outputs[axis],n.inputs[1]); sq.append(n)
    add=nodes.new('ShaderNodeMath'); add.operation='ADD'; links.new(sq[0].outputs[0],add.inputs[0]); links.new(sq[1].outputs[0],add.inputs[1])
    root=nodes.new('ShaderNodeMath'); root.operation='SQRT'; links.new(add.outputs[0],root.inputs[0])
    div=nodes.new('ShaderNodeMath'); div.operation='DIVIDE'; div.inputs[1].default_value=c['balls']['disc_radius']; links.new(root.outputs[0],div.inputs[0])
    ramp=nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=look['colors'][0]; ramp.color_ramp.elements[1].color=look['colors'][2]
    ramp.color_ramp.elements.new(.55).color=look['colors'][1]; links.new(div.outputs[0],ramp.inputs[0]); links.new(ramp.outputs[0],p.inputs['Base Color'])
    ng=bpy.data.node_groups.new('GN_Instanced_Spheres','GeometryNodeTree')
    ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    inp=ng.nodes.new('NodeGroupInput'); out=ng.nodes.new('NodeGroupOutput')
    ico=ng.nodes.new('GeometryNodeMeshIcoSphere'); ico.inputs['Radius'].default_value=c['balls']['radius']; ico.inputs['Subdivisions'].default_value=2
    smooth=ng.nodes.new('GeometryNodeSetShadeSmooth'); ng.links.new(ico.outputs['Mesh'],smooth.inputs['Geometry'])
    setmat=ng.nodes.new('GeometryNodeSetMaterial'); setmat.inputs['Material'].default_value=balls; ng.links.new(smooth.outputs['Geometry'],setmat.inputs['Geometry'])
    instance=ng.nodes.new('GeometryNodeInstanceOnPoints'); ng.links.new(inp.outputs[0],instance.inputs['Points']); ng.links.new(setmat.outputs[0],instance.inputs['Instance']); ng.links.new(instance.outputs[0],out.inputs[0])
    ob.modifiers.new('Lightweight sphere instances','NODES').node_group=ng
    glass,gp=material('MAT_Polished_Clear_Glass',(.88,.96,1,1),0,.23,.35)
    gp.inputs['Coat Weight'].default_value=1; gp.inputs['Coat Roughness'].default_value=.055; gp.inputs['Coat IOR'].default_value=1.46
    frost,fp=material('MAT_Frosted_Glass_Underside',(.75,.86,.94,1),0,.35,.3)
    d=c['dais']; bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=d['radius'],depth=d['depth'],location=(0,0,d['center_z']))
    stage=bpy.context.object; stage.name='Polished glass dais'; stage.data.materials.append(glass); stage.data.materials.append(frost)
    for poly in stage.data.polygons: poly.use_smooth=True; poly.material_index=1 if poly.normal.z<-.5 else 0
    bevel=stage.modifiers.new('Soft glass rim','BEVEL'); bevel.width=.055*(d['radius']/3.22); bevel.segments=3
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.17)); floor=bpy.context.object; floor.name='Quiet lavender studio floor'
    floor_mat,_=material('MAT_Quiet_Lavender',look['background_color'],0,.85); floor.data.materials.append(floor_mat)
    s.world=bpy.data.worlds.new('Bright neutral studio'); s.world.use_nodes=True
    bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs[0].default_value=look['world_color']; bg.inputs[1].default_value=look['world_strength']
    def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    for light in c['lights']:
        data=bpy.data.lights.new('LGT_'+light['name'],'AREA'); data.energy=light['power']; data.shape='RECTANGLE'; data.size=light['size']; data.size_y=light['size_y']; data.use_shadow=True
        o=bpy.data.objects.new(data.name,data); s.collection.objects.link(o); o.location=light['location']; aim(o,(0,0,1))
    bpy.ops.object.camera_add(location=c['camera']['location']); s.camera=bpy.context.object; s.camera.name='CAM_Studio'; aim(s.camera,c['camera']['target'])
    s.camera.data.type='ORTHO'; s.camera.data.ortho_scale=c['camera']['ortho_scale']
    # Captures reflections for optional Eevee; Cycles computes its own transport.
    data=bpy.data.lightprobes.new('Glass planar reflection','PLANE'); probe=bpy.data.objects.new(data.name,data); s.collection.objects.link(probe); probe.location=(0,0,.125); probe.scale=(3.65,)*3; data.influence_distance=5; data.clip_start=.01
    s.view_settings.view_transform=look['view_transform']; s.view_settings.exposure=look['exposure']
    return s,m,ob

def main():
    p=argparse.ArgumentParser(); p.add_argument('--preset',required=True); p.add_argument('--output',required=True)
    p.add_argument('--mode',choices=['build','still','video','smoke','reference'],default='still'); p.add_argument('--engine',choices=['cycles','eevee'],default='cycles')
    p.add_argument('--samples',type=int); p.add_argument('--threads',type=int,default=8); p.add_argument('--scale',type=int,default=100); p.add_argument('--frame',type=int); p.add_argument('--resume',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); c=validate(json.loads(Path(a.preset).read_text(encoding='utf-8')))
    out=Path(a.output).resolve(); out.mkdir(parents=True,exist_ok=True)
    if a.mode=='reference':
        bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).resolve().parents[1]/'assets/approved-v06.blend')); s=bpy.context.scene; m=Motion(c); ob=bpy.data.objects['Phyllotaxis sunflower spheres']
    else: s,m,ob=build(c)
    configure(s,c,a)
    if bpy.app.version[:2]!=(5,2): print('WARNING: tested on Blender 5.2.3; this version may differ',flush=True)
    source_digest=hashlib.sha256(Path(a.preset).read_bytes()).hexdigest()
    checkpoints={str(f):hashlib.sha256(m.positions((f-1)/c['fps']).tobytes()).hexdigest() for f in sorted(set([1,32,min(135,s.frame_end),s.frame_end]))}
    manifest={'blender':bpy.app.version_string,'engine':s.render.engine,'preset_sha256':source_digest,'fps':c['fps'],'duration':c['duration'],'frame_count':s.frame_end,'resolution':[s.render.resolution_x,s.render.resolution_y],'motion_hashes':checkpoints,'balls':m.n,'source':a.mode,'audio':synthesize(c,m,out/'sound.wav')}
    # Check baked source positions; instances need not be expanded into dense meshes.
    checks=[]
    for f in [1,min(135,s.frame_end),s.frame_end]:
        s.frame_set(f)
        # Geometry-node instances are not expanded here; validate the baked source keys.
        block=ob.data.shape_keys.key_blocks[f-1]; actual=list(block.data[0].co); expected=m.positions((f-1)/c['fps'])[0].tolist()
        error=max(abs(x-y) for x,y in zip(actual,expected)); checks.append(error)
    if max(checks)>1e-5: raise RuntimeError('Baked motion differs from preset')
    manifest['baked_position_error']=max(checks)
    subframe=min(135,s.frame_end)
    s.frame_set(subframe,subframe=.5)
    error=abs(ob.data.shape_keys.eval_time-((subframe-.5)*10))
    if error>1e-3: raise RuntimeError('Subframe motion driver did not evaluate')
    manifest['subframe_driver_error']=error
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    s.frame_set(a.frame or min(c['preview_frame'],s.frame_end)); s.render.filepath='//frames/'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
    if a.mode=='build': return
    if a.mode in ['still','reference']:
        s.render.filepath=str(out/'preview.png'); bpy.ops.render.render(write_still=True)
    else:
        frame_dir=out/'frames'; frame_dir.mkdir(exist_ok=True)
        end=s.frame_end if a.mode=='video' else min(s.frame_end,135)
        start=1 if a.mode=='video' else max(1,end-5)
        for f in range(start,end+1):
            path=frame_dir/('%04d.png'%f)
            if a.resume and path.exists(): continue
            s.frame_set(f); s.render.filepath=str(path); bpy.ops.render.render(write_still=True)
        manifest['render_start']=start; manifest['render_end']=end
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
if __name__=='__main__': main()
