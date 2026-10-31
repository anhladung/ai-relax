"""Original seeded wooden-mallet synthesis used in v03/v04; no downloaded samples."""
import math
import wave
import numpy as np

def synthesize(c,m,path):
    sr=c['audio']['sample_rate']; rng=np.random.default_rng(c['seed']); dry=np.zeros((round(sr*c['duration']),2),dtype=np.float64)
    midi=[48,50,52,55,57,60,62,64,67,69,72,74,76,79,81]; cache={}
    def mallet(note):
        if note in cache: return cache[note]
        f=440*2**((note-69)/12); tt=np.arange(int(sr*1.15))/sr; y=np.zeros_like(tt)
        for ratio,amp,tau in [(1,1,.31),(3.99,.35,.095),(9.98,.11,.035),(14.37,.035,.018)]:
            y+=amp*np.cos(2*math.pi*f*ratio*tt)*np.exp(-tt/(tau*(261.63/f)**.25))
        y*=1-np.exp(-tt/.0012)
        noise=np.convolve(rng.standard_normal(len(tt)),np.ones(9)/9,mode='same')
        y+=noise*.12*np.exp(-tt/.008)*(1-np.exp(-tt/.0004)); y/=max(1,np.max(np.abs(y))); cache[note]=y
        return y
    groups=m.contacts()
    for impacts in groups.values():
        group=sorted(impacts,key=lambda x:m.rad[x[0]])
        picks=[group[len(group)//2]] if len(group)<200 else [group[int((len(group)-1)*q)] for q in [.08,.3,.55,.78,.96]]
        for j,(i,t,velocity) in enumerate(picks):
            note=midi[int(np.clip(round(3+m.rad[i]*10),0,14))]; sample=mallet(note)
            start=int((t+(j*.009 if len(picks)>1 else 0))*sr); count=min(len(sample),len(dry)-start)
            if count<=0: continue
            amp=(.12+.07*min(1,math.log1p(len(group))/5))*velocity**1.3
            pan=float(np.clip(m.xy[i,0]/3*.65,-.8,.8)); angle=(pan+1)*math.pi/4
            dry[start:start+count,0]+=sample[:count]*amp*math.cos(angle); dry[start:start+count,1]+=sample[:count]*amp*math.sin(angle)
        if len(group)>160:
            start=int(min(x[1] for x in group)*sr); count=min(int(.38*sr),len(dry)-start); tt=np.arange(count)/sr
            body=np.sin(2*math.pi*(65.406*tt+10*.022*(1-np.exp(-tt/.022))))*np.exp(-tt/.12)*(1-np.exp(-tt/.003))*.13
            dry[start:start+count]+=body[:,None]
    wet=np.zeros_like(dry)
    for k in range(28):
        delay=.024+k*.0093+float(rng.uniform(0,.004)); shift=int(delay*sr); gain=.075*math.exp(-delay/.115)
        if shift<len(dry): wet[shift:]+=(dry[:-shift,::-1] if k%2 else dry[:-shift])*gain
    mix=np.tanh((dry+wet)*1.15); mix*=.87/max(.87,np.max(np.abs(mix)))
    fade=min(int(sr*.035),len(mix)); mix[-fade:]*=np.linspace(1,0,fade)[:,None]
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes())
    return {'groups':len(groups),'peak':float(np.max(np.abs(mix))),'rms':float(np.sqrt(np.mean(mix**2)))}
