#!/usr/bin/env python3
from pathlib import Path
import csv,json,re,hashlib
b=Path(__file__).resolve().parent
linear=[]; nonlinear=[]; status=[]
pattern=re.compile(r'^\s*(\d+\.\d+)\s+(-?\d+\.\d{7})\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s*$',re.M)
for d in sorted(d for d in b.iterdir() if d.is_dir() and (d.name.startswith('linear-') or d.name.startswith('nonlinear-'))):
 if not d.is_dir() or not (d/'epw.out').exists():continue
 inp=(d/'epw.in').read_text();out=(d/'epw.out').read_text();err=(d/'epw.err').read_text() if (d/'epw.err').exists() else ''
 get=lambda k:re.search(r'\b'+k+r'\s*=\s*([^\n!,/]+)',inp,re.I).group(1).strip()
 w=float(get('wscut'));mu=float(get('muc'));ns=int(get('nsiter'))
 islinear=get('tc_linear').lower()=='.true.'
 finish=('Finish: Solving (isotropic) linearized Eliashberg equation' in out) if islinear else ('Finish: Free energy' in out or ('EPW          :' in out and 'Error in routine' not in out))
 status.append({'run':d.name,'native_finish':finish,'stderr_bytes':len(err.encode()),'fatal':'Error in routine' in out or bool(err),'iteration_limit':'Convergence was not reached' in out,'requested_wscut_eV':w,'muc':mu})
 if islinear:
  for T,eta,n,wa,it in pattern.findall(out):
   linear.append({'run':d.name,'T_K':float(T),'max_eigenvalue':float(eta),'nsiw':int(n),'actual_wscut_eV':float(wa),'iterations':int(it),'requested_wscut_eV':w,'muc':mu,'solver':get('tc_linear_solver').strip("'"),'complete':finish and not err,'nsiter':ns})
 else:
  its=[int(x) for x in re.findall(r'Convergence was reached in nsiter =\s*(\d+)',out)]
  temperatures=[float(x) for x in re.findall(r'Temp \(itemp =\s*\d+\) =\s*([\d.]+)',out)]
  for f in sorted(d.glob('al.imag_iso_*')):
   T=float(f.name.split('_')[-1]);row=f.read_text().splitlines()[1].split();vals=[float(x.replace('D','E')) for x in row]
   if T not in temperatures:continue
   idx=temperatures.index(T)
   nonlinear.append({'run':d.name,'T_K':T,'omega0_eV':vals[0],'Z_omega0':vals[1],'Delta_omega0_meV':vals[2]*1000,'converged':idx<len(its),'iterations':its[idx] if idx<len(its) else None,'requested_wscut_eV':w,'muc':mu,'whole_run_complete':finish and not err})
for name,rows in [('linear.csv',linear),('gap.csv',nonlinear)]:
 with (b/name).open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['empty']);wr.writeheader();wr.writerows(rows)
(b/'solver-status.json').write_text(json.dumps(status,indent=2)+'\n')
manifest={str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.rglob('*') if p.is_file() and p.suffix not in ('.gz',) and p.name not in ('terminal.log','SHA256.json') and p.stat().st_size<5000000}
(b/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'linear_rows':len(linear),'converged_gap_rows':len(nonlinear),'status':status},indent=2))

brackets=[]
for requested, run in [(.1,'linear-refine')]:
 rows=sorted([r for r in linear if r['run']==run and r['complete']],key=lambda r:r['T_K'])
 for a,z in zip(rows,rows[1:]):
  if a['max_eigenvalue']>=1 and z['max_eigenvalue']<=1:
   frac=(a['max_eigenvalue']-1)/(a['max_eigenvalue']-z['max_eigenvalue'])
   brackets.append({'run':run,'requested_wscut_eV':requested,'muc':.1,'T_low_K':a['T_K'],'T_high_K':z['T_K'],'eta_low':a['max_eigenvalue'],'eta_high':z['max_eigenvalue'],'linear_interpolation_K':a['T_K']+frac*(z['T_K']-a['T_K']),'claim':'conditional model crossing bracket; interpolation is a plotting estimate, not material accuracy'})
(b/'tc-brackets.json').write_text(json.dumps(brackets,indent=2)+'\n')

# Native EPW a2F has 500 positive-frequency rows, followed by a human-readable footer.
spectrum=[]
for line in (b/'source/al.a2f').read_text().splitlines()[1:]:
 try: values=[float(v) for v in line.split()]
 except ValueError: break
 if len(values)!=3: raise ValueError('Expected three native spectrum columns')
 spectrum.append(values)
assert len(spectrum)==500
step=spectrum[-1][0]/len(spectrum); cumulative=0.0
with (b/'source-spectrum.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['omega_meV','alpha2F','lambda_cumulative_native','lambda_cumulative_rectangle'])
 for omega,a2f,integ in spectrum:
  cumulative+=2*step*a2f/omega;writer.writerow([omega,a2f,integ,cumulative])
