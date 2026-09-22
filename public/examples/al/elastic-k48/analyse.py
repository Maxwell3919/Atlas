from pathlib import Path
import json,re,hashlib,csv
import numpy as np
RY_BOHR3_GPA=14710.5076
rows=[]
for case in json.loads(Path('cases.json').read_text()):
 p=Path(case['label']);s=(p/'al.scf.out').read_text();err=(p/'al.scf.err').read_text()
 assert s.count('JOB DONE.')==1 and 'convergence has been achieved' in s and not err
 assert 'convergence NOT achieved' not in s and 'Error in routine' not in s
 energy=float(re.findall(r'!\s+total energy\s+=\s+([-0-9.]+)',s)[-1])
 block=re.findall(r'total\s+stress[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)',s)[-1]
 stress=-RY_BOHR3_GPA*np.array([[float(x) for x in line.split()[:3]] for line in block])
 row={**case,'energy_Ry':energy,'sigma_xx_GPa':stress[0,0],'sigma_yy_GPa':stress[1,1],'sigma_zz_GPa':stress[2,2],'sigma_xy_GPa':stress[0,1]}
 rows.append(row)
with open('strain-stress.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
results=[]
for mag in [.005]:
 def pair(mode):
  a=[r for r in rows if r['mode']==mode and r['engineering_strain']==mag][0]
  b=[r for r in rows if r['mode']==mode and r['engineering_strain']==-mag][0]
  return a,b
 a,b=pair('xx');c11=(a['sigma_xx_GPa']-b['sigma_xx_GPa'])/(2*mag)
 c12=sum(a[f'sigma_{i}_GPa']-b[f'sigma_{i}_GPa'] for i in ['yy','zz'])/(4*mag)
 a,b=pair('xy');c44=(a['sigma_xy_GPa']-b['sigma_xy_GPa'])/(2*mag)
 B=(c11+2*c12)/3;Gv=(c11-c12+3*c44)/5;Gr=5*(c11-c12)*c44/(4*c44+3*(c11-c12));G=(Gv+Gr)/2
 r={'strain':mag,'C11_GPa':c11,'C12_GPa':c12,'C44_GPa':c44,'C11-C12_GPa':c11-c12,'C11+2C12_GPa':c11+2*c12,'B_GPa':B,'Gv_GPa':Gv,'Gr_GPa':Gr,'GH_GPa':G,'E_GPa':9*B*G/(3*B+G),'nu':(3*B-2*G)/(2*(3*B+G)),'anisotropy':2*c44/(c11-c12)}
 results.append(r)
with open('elastic-results.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
print('All 4 SCFs: one JOB DONE., electronic convergence, empty stderr.')
print('strain     C11       C12       C44       B         GH        E        nu')
for r in results:print(f"{r['strain']:.3f} {r['C11_GPa']:10.4f} {r['C12_GPa']:9.4f} {r['C44_GPa']:9.4f} {r['B_GPa']:9.4f} {r['GH_GPa']:9.4f} {r['E_GPa']:9.4f} {r['nu']:8.4f}")
