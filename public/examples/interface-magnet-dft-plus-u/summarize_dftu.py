from pathlib import Path
import re, json, csv, hashlib, math
r=Path(__file__).resolve().parent
out=(r/'OUTCAR').read_text(); osz=(r/'OSZICAR').read_text()
if 'aborting loop because EDIFF is reached' not in out or 'General timing' not in out:
    raise ValueError('Missing electronic convergence or timing record')
def last(pattern):
    v=re.findall(pattern,out)
    if not v: raise ValueError('Missing field: '+pattern)
    return v[-1]
species=(r/'POSCAR').read_text().splitlines()[5].split()
if species!=['V','Ge','P']:raise ValueError('Expected V Ge P species order')
F=float(last(r'free  energy\s+TOTEN\s*=\s*([-0-9.]+)'))
E0=float(last(r'energy\(sigma->0\)\s*=\s*([-0-9.]+)'))
EF=float(last(r'E-fermi\s*:\s*([-0-9.]+)'))
M=float(re.findall(r'mag=\s*([-0-9.]+)',osz)[-1])
steps=[int(x) for x in re.findall(r'DAV:\s*(\d+)',osz)]
u=[float(x) for x in last(r'U \(eV\)\s+for each species LDAUU\s*=([^\n]+)').split()]
j=[float(x) for x in last(r'J \(eV\)\s+for each species LDAUJ\s*=([^\n]+)').split()]
l=[int(x) for x in last(r'angular momentum for each species LDAUL\s*=([^\n]+)').split()]
if l!=[2,-1,-1] or len(u)!=3 or len(j)!=3:raise ValueError('Unexpected DFT+U orbital/species arrays')
if not all(math.isfinite(x) for x in [F,E0,EF,M,*u,*j]):raise ValueError('Non-finite output')
row={'elements':' '.join(species),'LDAUTYPE':int(last(r'LDAUTYPE\s*=\s*(\d+)')),'LDAUL':' '.join(map(str,l)),'Ueff_V_d_eV':u[0]-j[0],'LMAXMIX':int(last(r'LMAXMIX\s*=\s*(\d+)')),'LORBIT':int(last(r'LORBIT\s*=\s*(\d+)')),'electron_steps':steps[-1],'F_eV_cell':F,'E0_eV_cell':E0,'EF_eV_run_reference':EF,'M_muB_cell':M}
summary={'result':row,'source_sha256':{n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ['INCAR','POSCAR','KPOINTS','OUTCAR','OSZICAR','EIGENVAL']},'scope':'Single U=3 eV SCF; no U=0 comparison or U-dependence conclusion.'}
(r/'dftu-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (r/'dftu-result-table.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=row);w.writeheader();w.writerow(row)
for k,v in row.items(): print(k,'=',v)
