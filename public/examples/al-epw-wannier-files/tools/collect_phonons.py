#!/usr/bin/env python3
"""Copy the completed Al q4 DFPT artifacts without changing the source tree."""
from pathlib import Path
import argparse,shutil,hashlib,json
p=argparse.ArgumentParser();p.add_argument('parent',type=Path);p.add_argument('destination',type=Path);a=p.parse_args()
s=a.parent;d=a.destination;d.mkdir(exist_ok=False,parents=True)
assert [int(x)for x in(s/'al.dyn0').read_text().splitlines()[0].split()]==[4,4,4]
assert int((s/'al.dyn0').read_text().splitlines()[1])==8
rows=[]
def copy(src,dst):
 assert src.is_file()and src.stat().st_size>0
 dst.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(src,dst)
 h=hashlib.sha256(src.read_bytes()).hexdigest();assert h==hashlib.sha256(dst.read_bytes()).hexdigest()
 rows.append({'source_relative_to_parent':str(src.relative_to(s)),'copy_relative_to_destination':str(dst.relative_to(d)),'bytes':src.stat().st_size,'sha256':h})
for i in range(1,9):
 copy(s/f'al.dyn{i}',d/f'al.dyn_q{i}')
 copy(s/'tmp/_ph0'/('al.aldv1'if i==1 else f'al.q_{i}/al.aldv1'),d/f'al.dvscf_q{i}')
for f in(s/'tmp/_ph0/al.phsave').iterdir():
 if f.is_file():copy(f,d/'al.phsave'/f.name)
copy(s/'al.fc',d/'ifc.q2r')
(d/'copy-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Copied and hash-checked',len(rows),'files; source left intact.')
