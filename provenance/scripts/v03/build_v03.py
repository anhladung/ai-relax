import bpy, os, sys, math, wave, json
import numpy as np
r=os.path.dirname(os.path.abspath(__file__)); os.makedirs(r+'/frames',exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.dirname(r)+'/v02/bouncing_balls_v02_final.blend')
s=bpy.context.scene
# A near-overhead directional source casts readable individual bead shadows.
for light in bpy.data.lights: light.energy*=.38
light=bpy.data.lights.new('LGT_Bead_Shadow_Key','SUN'); light.energy=3.8; light.angle=.012; light.use_shadow=True
if hasattr(light,'specular_factor'): light.specular_factor=.15
sun=bpy.data.objects.new('LGT_Bead_Shadow_Key',light); s.collection.objects.link(sun); sun.rotation_euler=(0,0,0)
stage=bpy.data.objects['Round porcelain dais']
p=next(n for n in stage.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.20,.22,.25,1)
s.eevee.taa_render_samples=32
s.render.filepath=r+'/frames/'
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=r+'/bouncing_balls_v03.blend')
# Sample-accurate impact timing, modal wooden mallets, velocity, stereo position,
# warm low body and a short diffuse room rather than repeated pure sine tones.
sr=48000; length=10; rng=np.random.default_rng(20261031)
N=2566; idx=np.arange(N); rad=np.sqrt((idx+.5)/N); theta=idx*(math.pi*(3-math.sqrt(5)))
xy=np.column_stack((3*rad*np.cos(theta),3*rad*np.sin(theta)))
g=6.5; h=3.6; v=math.sqrt(2*g*h); first=math.sqrt(2*h/g)
events={}
for i,rr in enumerate(rad):
 t=first; speed=v*(.8+.18*rr)
 while t<10:
  slot=int(t*120); events.setdefault(slot,[]).append((i,t,speed/v)); t+=2*speed/g; speed*=.993
# 15 pitches from C major pentatonic, C3 through B5 region.
midi=np.array([48,50,52,55,57,60,62,64,67,69,72,74,76,79,81])
cache={}
def mallet(note):
 if note in cache: return cache[note]
 f=440*2**((note-69)/12); tt=np.arange(int(sr*1.15))/sr
 # Wooden-bar modes; upper resonances decay quickly, leaving a rounded body.
 y=np.zeros_like(tt)
 for ratio,amp,tau in [(1,1,.31),(3.99,.35,.095),(9.98,.11,.035),(14.37,.035,.018)]:
  y+=amp*np.cos(2*math.pi*f*ratio*tt)*np.exp(-tt/(tau*(261.63/f)**.25))
 y*=1-np.exp(-tt/.0012)
 noise=rng.standard_normal(len(tt)); noise=np.convolve(noise,np.ones(9)/9,mode='same')
 y+=noise*.12*np.exp(-tt/.008)*(1-np.exp(-tt/.0004))
 y/=max(1,np.max(np.abs(y))); cache[note]=y
 return y
dry=np.zeros((sr*length,2),dtype=np.float64)
for slot,impacts in events.items():
 # One clear note per 8.3ms group; simultaneous first impact is a gentle arpeggiated chord.
 group=sorted(impacts,key=lambda x:rad[x[0]])
 picks=[group[len(group)//2]] if len(group)<200 else [group[int((len(group)-1)*q)] for q in [.08,.3,.55,.78,.96]]
 for j,(i,t,velocity) in enumerate(picks):
  ri=rad[i]; pitch=int(np.clip(round(3+ri*10),0,14)); note=int(midi[pitch])
  sample=mallet(note); onset=t+(j*.009 if len(picks)>1 else 0)
  start=int(onset*sr); count=min(len(sample),len(dry)-start)
  if count<=0: continue
  # Soften dense runs; stronger impacts have a fuller body.
  amp=(.12+.07*min(1,math.log1p(len(group))/5))*velocity**1.3
  pan=float(np.clip(xy[i,0]/3*.65,-.8,.8)); angle=(pan+1)*math.pi/4
  dry[start:start+count,0]+=sample[:count]*amp*math.cos(angle)
  dry[start:start+count,1]+=sample[:count]*amp*math.sin(angle)
 # Low resonant body under collective landings, not every tiny strike.
 if len(group)>160:
  t0=min(x[1] for x in group); st=int(t0*sr); count=min(int(.38*sr),len(dry)-st); tt=np.arange(count)/sr
  body=np.sin(2*math.pi*(65.406*tt+10*.022*(1-np.exp(-tt/.022))))*np.exp(-tt/.12)*(1-np.exp(-tt/.003))*.13
  dry[st:st+count]+=body[:,None]
# Small stereo room, multiple low-level taps without a prominent repeated echo.
wet=np.zeros_like(dry)
for k in range(28):
 delay=.024+k*.0093+float(rng.uniform(0,.004)); shift=int(delay*sr)
 gain=.075*math.exp(-delay/.115)
 signal=dry[:-shift,::-1] if k%2 else dry[:-shift]
 wet[shift:]+=signal*gain
mix=dry+wet
# Soft saturation and very slow DC removal; preserve impact transients.
mix=np.tanh(mix*1.15)
mix*=.87/max(.87,np.max(np.abs(mix)))
mix[-int(sr*.035):]*=np.linspace(1,0,int(sr*.035))[:,None]
with wave.open(r+'/wooden_mallets_v03.wav','wb') as w:
 w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes())
json.dump({'sample_rate':sr,'impact_groups':len(events),'peak':float(np.max(np.abs(mix))),'rms':float(np.sqrt(np.mean(mix**2))),'shadow_sun_angle':.012,'shadow_energy':3.8},open(r+'/settings.json','w'),indent=2)
if '--preview' in sys.argv:
 for frame in [34,135,250]:
  s.frame_set(frame); s.render.filepath=r+'/preview_%03d.png'%frame; bpy.ops.render.render(write_still=True)
else: bpy.ops.render.render(animation=True)
