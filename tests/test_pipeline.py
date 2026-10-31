import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from model import Motion,validate
from sound import synthesize

class PipelineTests(unittest.TestCase):
    def setUp(self): self.c=json.loads((ROOT/'presets/bright-metal-v06.json').read_text()); self.m=Motion(self.c)
    def test_ballistic_fall_and_contact(self):
        pos=self.m.positions(self.m.first*.5)
        np.testing.assert_allclose(pos[:,2],self.m.base+self.m.h*.75,atol=1e-6)
        for group in self.m.contacts().values():
            for i,t,_ in group[::max(1,len(group)//5)]:
                self.assertAlmostEqual(float(self.m.positions(t)[i,2]),self.m.base,places=5)
    def test_containing_footprint_and_center_height(self):
        self.assertLess(np.max(np.linalg.norm(self.m.xy,axis=1))+self.c['balls']['radius'],self.c['dais']['radius'])
        frames=[self.m.positions(f/30) for f in range(300)]
        self.assertGreaterEqual(min(float(x[:,2].min()) for x in frames),self.m.base-1e-6)
        self.assertEqual(len({hashlib.sha256(x.tobytes()).hexdigest() for x in frames}),300)
    def test_bad_preset_rejected(self):
        bad=copy.deepcopy(self.c); bad['dais']['radius']=4
        with self.assertRaises(ValueError): validate(bad)
        bad=copy.deepcopy(self.c); bad['fps']=15
        with self.assertRaises(ValueError): validate(bad)
    def test_repeatable_audio_and_format(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a.wav'; b=Path(td)/'b.wav'; stats=synthesize(self.c,self.m,a); synthesize(self.c,self.m,b)
            self.assertEqual(hashlib.sha256(a.read_bytes()).digest(),hashlib.sha256(b.read_bytes()).digest())
            self.assertLess(stats['peak'],1); self.assertGreater(stats['rms'],.01)
            with wave.open(str(a)) as w:
                self.assertEqual((w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes()),(48000,2,2,480000))
if __name__=='__main__': unittest.main()
