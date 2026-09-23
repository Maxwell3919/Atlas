#!/usr/bin/env python3
"""Materialize a new stage without overwriting any previous run directory."""
from pathlib import Path
import argparse,shutil,json,hashlib
B=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stage',choices=['parent','nscf','wannier','coarse','fine','bandcheck','phononcheck']);a=p.parse_args()
name={'parent':'00-phonon','nscf':'01-nscf','wannier':'02-wannier','coarse':'03-coarse','fine':'04-fine','bandcheck':'05-bandcheck','phononcheck':'06-phononcheck'}[a.stage]
d=B/name;d.mkdir(exist_ok=False)
def cp(src,dst):
 assert src.exists(),str(src)
 dst.parent.mkdir(exist_ok=True,parents=True)
 if src.is_dir():shutil.copytree(src,dst)
 else:shutil.copy2(src,dst)
def density(src):
 for f in ['data-file-schema.xml','charge-density.dat','Al.pz-vbc.UPF']:cp(src/f,d/'tmp/al.save'/f)
if a.stage in ['parent','nscf','wannier','coarse','bandcheck']:cp(B/'pseudo',d/'pseudo')
if a.stage=='parent':
 for f in ['al.dense.in','al.scf.in','al.elph.in','q2r.in']:cp(B/'inputs/parent'/f,d/f)
elif a.stage=='nscf':
 density(B/'00-phonon/tmp/al.save');cp(B/'inputs/al.nscf-k12.in',d/'al.nscf.in')
elif a.stage=='wannier':
 cp(B/'01-nscf/tmp',d/'tmp');cp(B/'inputs/epw1-k12.in',d/'epw1.in')
elif a.stage=='coarse':
 cp(B/'01-nscf/tmp',d/'tmp')
 for f in ['al.ukk','al.win','al.bvec','al.mmn']:cp(B/'02-wannier'/f,d/f)
 cp(B/'inputs/epw-coarse.in',d/'epw-coarse.in')
elif a.stage in ['fine','phononcheck']:
 for f in ['crystal.fmt','epwdata.fmt','dmedata.fmt','vmedata.fmt','wigner.fmt','al.ukk']:cp(B/'03-coarse'/f,d/f)
 cp(B/'03-coarse/tmp/al.epmatwp',d/'tmp/al.epmatwp')
 if a.stage=='fine':cp(B/'inputs/epw2-k12-fine24.in',d/'epw2.in')
 else:
  for f in ['epw-phcheck.in','qmesh12.dat']:cp(B/'inputs'/f,d/f)
elif a.stage=='bandcheck':
 density(B/'00-phonon/tmp/al.save')
 s=(B/'inputs/al.nscf-k12.in').read_text().replace("calculation = 'nscf'","calculation = 'bands'")
 s=s[:s.index('K_POINTS crystal')]+'K_POINTS crystal\n'+(B/'02-wannier/al_band.kpt').read_text()
 (d/'al.bands.in').write_text(s)
rows=[]
for f in sorted(d.rglob('*')):
 if f.is_file():rows.append({'file':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(d/'stage-materialization.json').write_text(json.dumps({'stage':a.stage,'files':rows},indent=2)+'\n')
print(d)
