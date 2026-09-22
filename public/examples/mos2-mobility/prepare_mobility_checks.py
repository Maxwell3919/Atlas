from pathlib import Path
import json,csv,numpy as np
from mobility_common import geometry,input_pw,kset,slurm,post_inputs,BODY
R=Path(__file__).resolve().parent
for family,mesh,dz in [('k16',16,0),('vacuum28',12,5)]:
 for parent in ['zero','minus005','plus005']:
  d0=R/parent
  if not (d0/'scf.data-file-schema.xml').exists():continue
  t=(d0/'mos2.scf.out').read_text()
  if 'JOB DONE.' not in t or 'convergence has been achieved' not in t:continue
  if (R/f'{family}-{parent}'/'run.slurm').exists():continue
  cell,pos,sp=geometry(d0/'scf.data-file-schema.xml');cell=cell.copy();pos=pos.copy()
  cell[2,2]+=dz;pos[:,2]+=dz/2
  d=R/f'{family}-{parent}';d.mkdir(exist_ok=True)
  conf=json.loads((d0/'config.json').read_text());conf.update({'mesh':mesh,'vacuum_add_A':dz,'geometry_reference':parent,'ions':'fixedtoaccepted12x12relaxedpositions'})
  (d/'config.json').write_text(json.dumps(conf,indent=2)+'\n')
  ks,rows=kset(cell)
  scf=input_pw(cell,pos,sp,'scf',mesh)
  if family=='k16':scf=scf.replace('&ELECTRONS\n', "&ELECTRONS\n startingpot = 'file'\n")
  (d/'mos2.scf.in').write_text(scf)
  (d/'mos2.bands.in').write_text(input_pw(cell,pos,sp,'bands',mesh,ks))
  with (d/'kpoints.csv').open('w') as f:
   w=csv.writer(f);w.writerow(['kind','offsetx_invA','offsety_invA','k1','k2','k3']);w.writerows(rows)
  post_inputs(d)
  body=BODY.replace('pw.x -in','pw.x -nk 4 -in')
  if family=='k16':body='mkdir -p tmp/mos2.save\ncp ../'+parent+'/tmp/mos2.save/charge-density.dat tmp/mos2.save/\n'+body
  (d/'run.slurm').write_text(slurm('atlas-'+family+'-'+parent,body));print(d.name,'ready')
