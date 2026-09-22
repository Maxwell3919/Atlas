from pathlib import Path
import json,csv
from mobility_common import geometry,input_pw,kset
r=Path.cwd();text=(r/'mos2.relax.out').read_text()
assert 'JOB DONE.' in text and 'bfgs converged' in text.lower(), 'Ionic relaxation not accepted'
assert 'Error in routine' not in text
cell,pos,species=geometry(r/'tmp/mos2.save/data-file-schema.xml')
(r/'relax.data-file-schema.xml').write_bytes((r/'tmp/mos2.save/data-file-schema.xml').read_bytes())
conf=json.loads((r/'config.json').read_text())
ks,rows=kset(cell)
scf=input_pw(cell,pos,species,'scf',conf['mesh']).replace('&ELECTRONS\n', '&ELECTRONS\n startingpot = \'file\'\n startingwfc = \'file\'\n')
(r/'mos2.scf.in').write_text(scf)
(r/'mos2.bands.in').write_text(input_pw(cell,pos,species,'bands',conf['mesh'],ks))
with (r/'kpoints.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['kind','offsetx_invA','offsety_invA','k1','k2','k3']);w.writerows(rows)
print('Acceptedionicconvergence;wrotefinalSCF and97explicitvalleykpoints')
