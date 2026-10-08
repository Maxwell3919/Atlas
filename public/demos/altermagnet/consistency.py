#!/usr/bin/env python3
"""Independent stdlib oracle. python3 consistency.py [--output-dir DIR]; <=3min."""
import math,csv,json,time,os,argparse,resource,signal
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output-dir',default='.');a=p.parse_args();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
if hasattr(os,'sched_setaffinity'):os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]))
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3));signal.alarm(180)
start=time.monotonic();N=64;tol=2e-13;theta=.05
# Independent cos-sum/difference reference; no JavaScript import.
def values(x,y,j):
 e=-2*(math.cos(x)+math.cos(y));d=j*(math.cos(x)-math.cos(y));return e,d,e+d,e-d
def f(e,mu):return .5*(1-math.tanh((e-mu)/(2*theta)))
errs=dict(inversion=0.,C4_spin_swap=0.,J0_degeneracy=0.,nodal=0.,mean_Delta=0.,occupation_compensation=0.,parameter_sign_spin_swap=0.)
for j in [-1.,-.6,0.,.6,1.]:
 rows=[]
 for iy in range(N):
  for ix in range(N):
   x=-math.pi+2*math.pi*(ix+.5)/N;y=-math.pi+2*math.pi*(iy+.5)/N;e,d,up,dn=values(x,y,j)
   inv=values(-x,-y,j);rot=values(-y,x,j);zero=values(x,y,0);sign=values(x,y,-j)
   errs['inversion']=max(errs['inversion'],abs(up-inv[2]),abs(dn-inv[3]));errs['C4_spin_swap']=max(errs['C4_spin_swap'],abs(up-rot[3]),abs(dn-rot[2]));errs['J0_degeneracy']=max(errs['J0_degeneracy'],abs(zero[2]-zero[3]));errs['nodal']=max(errs['nodal'],abs(values(x,x,j)[1]),abs(values(x,-x,j)[1]));errs['parameter_sign_spin_swap']=max(errs['parameter_sign_spin_swap'],abs(up-sign[3]));rows.append((ix,iy,x,y,e,d,up,dn))
 errs['mean_Delta']=max(errs['mean_Delta'],abs(math.fsum(r[5] for r in rows)/N**2))
 for mu in [-4.,-.7,0.,.5,1.2,4.]:errs['occupation_compensation']=max(errs['occupation_compensation'],abs(math.fsum(f(r[6],mu)-f(r[7],mu) for r in rows)/N**2))
 assert all(((N-1-iy,ix) in {(i,k) for k in range(N) for i in range(N)}) for iy,ix in [(0,0),(32,32),(63,63)])
 assert time.monotonic()-start<180
# Full C4 midpoint grid index mapping: (ix,iy)->(N-1-iy,ix).
maperr=0.
for iy in range(N):
 for ix in range(N):
  k=lambda i:-math.pi+2*math.pi*(i+.5)/N
  maperr=max(maperr,abs(k(N-1-iy)+k(iy)),abs(k(ix)-k(ix)))
errs['C4_grid_map']=maperr
with (out/'default-grid.csv').open('w') as h:
 h.write('# TOY MODEL; no DFT/SOC/transport; no physical space-group validation\n# E_sigma=-2*(cos(kx)+cos(ky))+sigma*J*(cos(kx)-cos(ky))\n# J_E0=.6;mu_E0=.5;t_E0=1;theta_E0=.05;N=64;midpoint[-pi,pi);units=k_dimensionless,energy_E0\n');w=csv.writer(h);w.writerow(['ix','iy','kx','ky','epsilon_E0','Delta_E0','E_up_E0','E_down_E0','f_up','f_down'])
 for iy in range(N):
  for ix in range(N):
   x=-math.pi+2*math.pi*(ix+.5)/N;y=-math.pi+2*math.pi*(iy+.5)/N;v=values(x,y,.6);w.writerow([ix,iy,*[format(z,'.17g') for z in (x,y,*v,f(v[2],.5),f(v[3],.5))]])
# Analytic point oracle at (0,pi): epsilon=0, Delta=2J, E+=(2J), E-=(-2J).
assert values(0,math.pi,.6)==(0.,1.2,1.2,-1.2)
passed=all(v<=tol for v in errs.values());r={'status':'PASS' if passed else 'FAIL','tolerance_absolute':tol,'max_errors':errs,'grid':N,'J_cases':[-1,-.6,0,.6,1],'mu_cases':[-4,-.7,0,.5,1.2,4],'oracle_point':[0,'pi',.6,0,1.2,1.2,-1.2],'elapsed_seconds':time.monotonic()-start,'scientific_acceptance':False};(out/'analytic-results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert passed
