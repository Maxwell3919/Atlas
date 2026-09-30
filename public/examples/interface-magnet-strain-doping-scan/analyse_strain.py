from pathlib import Path
import csv, re, json, hashlib, math
r=Path(__file__).resolve().parent
rows=[]; hashes={}
def cell(text):
    rows=re.findall(r'CELL_PARAMETERS\s+angstrom\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)',text)
    if len(rows)!=1:raise ValueError('Expected one angstrom cell')
    return [[float(v) for v in line.split()] for line in rows[0]]
reference=cell((r/'elastic/al.reference.in').read_text())

for case in json.loads((r/'elastic/cases.json').read_text()):
    if case['mode']!='xx':continue
    p=r/'elastic'/case['label'];s=(p/'al.scf.out').read_text();err=(p/'al.scf.err').read_text()
    if s.count('JOB DONE.')!=1 or 'convergence has been achieved' not in s or err.strip() or 'convergence NOT achieved' in s or 'Error in routine' in s:
        raise ValueError('Incomplete SCF: '+case['label'])
    inp=(p/'al.scf.in').read_text(); current=cell(inp)
    strain=float(case['engineering_strain'])
    for i in range(3):
        for j in range(3):
            expected=reference[i][j]*(1+strain if j==0 else 1)
            if abs(current[i][j]-expected)>1e-10:raise ValueError('Cell/strain mismatch: '+case['label'])
    energy=float(re.findall(r'!\s+total energy\s+=\s+([-0-9.]+)',s)[-1])
    block=re.findall(r'total\s+stress[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)',s)[-1]
    stress=[[-14710.5076*float(x) for x in line.split()[:3]] for line in block]
    if not math.isfinite(energy) or not all(math.isfinite(v) for row in stress for v in row):raise ValueError('Non-finite result')
    rows.append({**case,'energy_Ry':energy,'sigma_xx_GPa':stress[0][0],'sigma_yy_GPa':stress[1][1],'sigma_zz_GPa':stress[2][2],'sigma_xy_GPa':stress[0][1]})
    for n in ['al.scf.in','al.scf.out','al.scf.err']:
        hashes[str((p/n).relative_to(r))]=hashlib.sha256((p/n).read_bytes()).hexdigest()
rows.sort(key=lambda x:x['engineering_strain'])
if len(rows)!=6:raise ValueError('Expected six xx samples')
with (r/'elastic/strain-stress.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(r/'strain-summary.json').write_text(json.dumps({'rows':rows,'source_sha256':hashes,'energy':'QE printed F in Ry/one-atom cell','stress':'Tensile-positive; minus QE Ry/bohr^3 * 14710.5076 GPa','scope':'Six xx fixed-cell SCFs, 16^3 k mesh; no doping/DOS/EPC.'},indent=2)+'\n')
print('Six xx SCFs: electronic convergence, one JOB DONE, empty stderr.')
for x in rows:print(f"{x['engineering_strain']:+.3f} F={x['energy_Ry']:.8f} Ry sigma_xx={x['sigma_xx_GPa']:+.6f} sigma_yy={x['sigma_yy_GPa']:+.6f} GPa")
