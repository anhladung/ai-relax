#!/usr/bin/env python3
"""Portable launcher. Standard-library Python only; NumPy comes from Blender."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
def find_binary(value,env,name):
    raw=value or os.environ.get(env) or shutil.which(name)
    if not raw and name=='blender':
        candidates=[]
        if sys.platform=='win32': candidates=sorted(Path(os.environ.get('PROGRAMFILES','C:/Program Files')).glob('Blender Foundation/Blender*/blender.exe'),reverse=True)
        elif sys.platform=='darwin': candidates=[Path('/Applications/Blender.app/Contents/MacOS/Blender')]
        raw=next((str(x) for x in candidates if x.is_file()),None)
    if not raw: raise RuntimeError(f'Missing {name}. Install it and set {env} to the executable path.')
    located=shutil.which(str(raw)) or str(Path(raw).expanduser().resolve())
    if not Path(located).is_file(): raise RuntimeError(f'Executable not found: {located}')
    return located

def call(args,**kw):
    print('+ '+' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True,**kw)

def fingerprint(preset,engine,samples,scale):
    h=hashlib.sha256()
    for p in [preset,ROOT/'scripts/model.py',ROOT/'scripts/sound.py',ROOT/'scripts/build_scene.py']:
        h.update(p.read_bytes())
    h.update(json.dumps([engine,samples,scale]).encode()); return h.hexdigest()

def verify(out,ffprobe,ffmpeg,expect_frames=None):
    path=out/'video.mp4'; m=json.loads((out/'manifest.json').read_text())
    data=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-of','json',str(path)],text=True))
    v=next(s for s in data['streams'] if s['codec_type']=='video'); a=next(s for s in data['streams'] if s['codec_type']=='audio')
    frames=expect_frames or m.get('render_end',m['frame_count'])-m.get('render_start',1)+1
    assert int(v['nb_read_frames'])==frames,(v['nb_read_frames'],frames)
    assert v['r_frame_rate']=='30/1',v['r_frame_rate']
    assert [v['width'],v['height']]==m['resolution']
    assert abs(float(v['duration'])-frames/30)<.04
    assert abs(float(a['duration'])-frames/30)<.06
    call([ffmpeg,'-v','error','-i',path,'-f','null','-'])
    hashes=subprocess.check_output([ffmpeg,'-v','error','-i',str(path),'-an','-f','framemd5','-'],text=True)
    lines=[x for x in hashes.splitlines() if x and not x.startswith('#')]; unique=len(set(x.rsplit(',',1)[-1].strip() for x in lines))
    assert len(lines)==frames and unique==frames, f'Expected unique motion frames, got {unique}/{frames}'
    report={'passed':True,'frames':frames,'unique_frames':unique,'fps':v['r_frame_rate'],'resolution':m['resolution'],'duration':v['duration'],'decoded':True}
    (out/'verification.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['doctor','build','still','reference','video','smoke','verify'])
    p.add_argument('--blender'); p.add_argument('--ffmpeg'); p.add_argument('--ffprobe')
    p.add_argument('--preset',type=Path,default=ROOT/'presets/bright-metal-v06.json'); p.add_argument('--out',type=Path)
    p.add_argument('--engine',choices=['cycles','eevee'],default='cycles'); p.add_argument('--gpu-backend',choices=['opengl','vulkan','metal'])
    p.add_argument('--samples',type=int); p.add_argument('--scale',type=int,default=100); p.add_argument('--threads',type=int,default=min(8,os.cpu_count() or 4)); p.add_argument('--frame',type=int)
    p.add_argument('--resume',action='store_true'); a=p.parse_args()
    if a.samples is not None and a.samples<1: p.error('samples must be positive')
    if not 1<=a.scale<=100 or a.threads<1: p.error('scale must be 1..100 and threads positive')
    if a.mode=='verify':
        if not a.out: p.error('verify requires --out')
        verify(a.out.resolve(),find_binary(a.ffprobe,'FFPROBE_BIN','ffprobe'),find_binary(a.ffmpeg,'FFMPEG_BIN','ffmpeg')); return
    blender=find_binary(a.blender,'BLENDER_BIN','blender')
    if a.mode=='doctor':
        call([blender,'--version'])
        for val,env,name in [(a.ffmpeg,'FFMPEG_BIN','ffmpeg'),(a.ffprobe,'FFPROBE_BIN','ffprobe')]:
            try: call([find_binary(val,env,name),'-version'],stdout=subprocess.DEVNULL); print(name+': OK')
            except RuntimeError as e: print(str(e)+' (needed for video/smoke only)')
        print('Python:',sys.version.split()[0], '\nPreset:',a.preset.resolve()); return
    preset=a.preset.resolve(); c=json.loads(preset.read_text(encoding='utf-8'))
    if a.mode=='reference' and preset!=(ROOT/'presets/bright-metal-v06.json').resolve(): p.error('reference is tied to the shipped v06 preset; use still for custom presets')
    if a.frame and not 1<=a.frame<=round(c['duration']*c['fps']): p.error('frame outside preset duration')
    ffmpeg=ffprobe=None
    if a.mode in ['video','smoke']:
        ffmpeg=find_binary(a.ffmpeg,'FFMPEG_BIN','ffmpeg'); ffprobe=find_binary(a.ffprobe,'FFPROBE_BIN','ffprobe')
    out=(a.out or ROOT/'outputs'/(a.mode+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))).resolve()
    signature=fingerprint(preset,a.engine,a.samples,a.scale)
    if out.exists() and any(out.iterdir()):
        prior=out/'run.json'
        if not(a.resume and a.mode in ['video','smoke'] and prior.is_file() and json.loads(prior.read_text())['signature']==signature):
            raise RuntimeError('Output folder is nonempty. Choose a new folder; --resume only accepts matching video/smoke inputs.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'run.json').write_text(json.dumps({'signature':signature,'mode':a.mode,'preset':preset.name},indent=2))
    cmd=[blender,'--background','--python-exit-code','1','--threads',str(a.threads)]
    if a.gpu_backend: cmd+=['--gpu-backend',a.gpu_backend]
    cmd+=['--python',str(ROOT/'scripts/build_scene.py'),'--','--mode',a.mode,'--preset',str(preset),'--output',str(out),'--engine',a.engine,'--threads',str(a.threads),'--scale',str(a.scale)]
    if a.samples: cmd+=['--samples',str(a.samples)]
    if a.frame: cmd+=['--frame',str(a.frame)]
    if a.resume: cmd+=['--resume']
    print('Blender log:',out/'blender.log',flush=True)
    with (out/'blender.log').open('a',encoding='utf-8') as log: call(cmd,stdout=log,stderr=subprocess.STDOUT)
    if a.mode in ['video','smoke']:
        manifest=json.loads((out/'manifest.json').read_text()); first=manifest['render_start']; count=manifest['render_end']-first+1
        images=[out/'frames'/('%04d.png'%f) for f in range(first,first+count)]
        if any(not x.is_file() or x.stat().st_size<100 for x in images): raise RuntimeError('Incomplete PNG sequence')
        call([ffmpeg,'-y','-v','error','-framerate','30','-start_number',str(first),'-i',out/'frames/%04d.png','-ss',str((first-1)/30),'-i',out/'sound.wav','-frames:v',str(count),'-t',str(count/30),'-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',out/'video.mp4'])
        verify(out,ffprobe,ffmpeg,count)
    print('Complete:',out,flush=True)
if __name__=='__main__':
    try: main()
    except (RuntimeError,ValueError,AssertionError,subprocess.CalledProcessError,FileNotFoundError,KeyError) as e:
        print('ERROR:',e,file=sys.stderr); sys.exit(1)
