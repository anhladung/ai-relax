"""Install only the self-contained AI Relax skill; keep repository location machine-local."""
import argparse
import json
import os
from pathlib import Path
import shutil
p=argparse.ArgumentParser(); p.add_argument('--codex-home',type=Path); p.add_argument('--replace',action='store_true'); a=p.parse_args()
repo=Path(__file__).resolve().parents[1]
home=(a.codex_home or Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))).expanduser().resolve()
target=home/'skills/ai-relax'
if target.exists() and not a.replace: raise SystemExit('Skill already exists. Use --replace to update its files.')
shutil.copytree(repo/'skills/ai-relax',target,dirs_exist_ok=a.replace)
(target/'references').mkdir(exist_ok=True)
(target/'references/repository.json').write_text(json.dumps({'repository':str(repo)},indent=2),encoding='utf-8')
print('Installed:',target,'\nRepository:',repo)
