"""Deterministic trajectories shared by scene, sound and verification. Requires NumPy (bundled with Blender)."""
import math
import numpy as np

def validate(c):
    if c.get('schema_version') != 1: raise ValueError('Unsupported preset schema')
    if c['fps'] != 30: raise ValueError('This production preset requires true 30 fps')
    if c['duration'] <= 0 or c['duration']*c['fps'] != int(c['duration']*c['fps']): raise ValueError('Duration must map to whole frames')
    if not 1 <= c['balls']['count'] <= 50000: raise ValueError('Invalid ball count')
    if c['physics']['gravity'] <= 0 or c['physics']['drop_height'] <= 0: raise ValueError('Gravity and release height must be positive')
    if not 0 < c['physics']['speed_retention'] <= 1: raise ValueError('Invalid speed retention')
    if not 0 < c['physics']['restitution_center'] <= 1 or not 0 < c['physics']['restitution_edge'] <= 1: raise ValueError('Invalid restitution')
    if not c['balls']['disc_radius']+c['balls']['radius'] < c['dais']['radius'] <= 1.1*(c['balls']['disc_radius']+c['balls']['radius']): raise ValueError('Dais must have a narrow containing rim')
    if len(c['resolution']) != 2 or any(int(v) != v or v < 16 or v%2 for v in c['resolution']): raise ValueError('Resolution must contain two even positive dimensions')
    return c

class Motion:
    def __init__(self,c):
        validate(c); self.c=c; self.n=c['balls']['count']; i=np.arange(self.n,dtype=np.float64)
        self.rad=np.sqrt((i+.5)/self.n); theta=i*math.pi*(3-math.sqrt(5))
        self.xy=c['balls']['disc_radius']*np.column_stack((self.rad*np.cos(theta),self.rad*np.sin(theta)))
        p=c['physics']; self.g=p['gravity']; self.h=p['drop_height']; self.base=p['surface_z']+p['trajectory_radius']
        self.first=math.sqrt(2*self.h/self.g); self.v=math.sqrt(2*self.g*self.h)
        self.e=p['restitution_center']+(p['restitution_edge']-p['restitution_center'])*self.rad; self.decay=p['speed_retention']
    def positions(self,t):
        if t<0: t=0
        if t<self.first: z=np.full(self.n,self.base+self.h-.5*self.g*t*t)
        else:
            remain=np.full(self.n,t-self.first); speed=self.v*self.e; z=np.full(self.n,self.base)
            for _ in range(10000):
                flight=2*speed/self.g; active=(remain>=0)&(remain<flight)
                z[active]=self.base+speed[active]*remain[active]-.5*self.g*remain[active]**2
                remain=np.where(remain>=flight,remain-flight,-1); speed*=self.decay
                if np.all(remain<0): break
                if np.max(speed)<1e-5: break
            else: raise RuntimeError('Trajectory iteration limit reached')
        return np.column_stack((self.xy,z)).astype(np.float32)
    def contacts(self):
        rate=self.c['audio']['impact_groups_per_second']; groups={}
        for i,e in enumerate(self.e):
            t=self.first; speed=self.v*e
            for _ in range(10000):
                if t>=self.c['duration'] or speed<1e-5: break
                groups.setdefault(int(t*rate),[]).append((i,t,speed/self.v)); t+=2*speed/self.g; speed*=self.decay
            else: raise RuntimeError('Contact iteration limit reached')
        return groups
