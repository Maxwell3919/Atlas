from pathlib import Path
import json,numpy as np
from mobility_common import geometry,input_pw,kset,slurm,post_inputs,BODY,QE
R=Path(__file__).resolve().parent
base=R/'base';t=(base/'mos2.vc-relax.out').read_text()
assert 'JOB DONE.' in t and 'bfgs converged' in t.lower(), 'Baselinegeometrynotaccepted'
cell,pos,sp=geometry(base/'tmp/mos2.save/data-file-schema.xml')
assert abs(cell[2,2]-23.19)<1e-6
print('AcceptedbasecellA',cell.tolist())
print('AreaA2',np.linalg.norm(np.cross(cell[0],cell[1])))
(base/'final-geometry.json').write_text(json.dumps({'cell_A':cell.tolist(),'positions_A':pos.tolist(),'species':sp},indent=2)+'\n')
for eps,name in [(-.01,'minus010'),(-.005,'minus005'),(0.,'zero'),(.005,'plus005'),(.01,'plus010')]:
 d=R/name;d.mkdir(exist_ok=True)
 F=np.diag([1+eps,1,1]);c=cell@F;p=pos@F
 (d/'config.json').write_text(json.dumps({'epsilon_xx':eps,'mesh':12,'vacuum_add_A':0,'reference':'base','transverse':'fixed','ions':'relaxed'},indent=2)+'\n')
 (d/'mos2.relax.prepared').write_text(input_pw(c,p,sp,'relax',12))
 (d/'mos2.relax.in').write_text(input_pw(c,p,sp,'relax',12))
 post_inputs(d)
 body=f'mpirun -np 8 {QE}pw.x -in mos2.relax.in > mos2.relax.out 2> mos2.relax.err\npython3 ../finish_mobility_relax.py > preparation.out\n'+BODY
 (d/'run.slurm').write_text(slurm('atlas-mob-'+name,body))
 print(name,'ready')
