import hashlib
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
expected=json.loads((r/'assets/checksums.json').read_text())
for name,want in expected.items():
    path=r/name
    if not path.is_file(): raise SystemExit('Asset missing: '+name)
    payload=path.read_text(encoding='utf-8').encode('utf-8') if path.suffix=='.json' else path.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=want: raise SystemExit('Asset checksum mismatch: '+name)
print('Packaged asset checksums: OK')
