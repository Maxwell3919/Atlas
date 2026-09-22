"""Audit this scalar MoS2 acoustic-DP model. Missing/unstable evidence blocks mobility.
All potentials and energy offsets remain in raw files; no invented reference values.
"""
from pathlib import Path
import numpy as np,xml.etree.ElementTree as ET,csv,json,re
from mobility_common import geometry,BOHR
R=Path(__file__).resolve().parent
HA=27.211386245988;RY=HA/2;HBAR2_ME=7.619964231
records=[];massrows=[];bandrows=[];potentialrows=[];fail=[]

def xml_eig(p):
 r=ET.parse(p).getroot();ks=r.findall('output/band_structure/ks_energies')
 e=np.array([np.fromstring(k.find('eigenvalues').text,sep=' ') for k in ks])*HA
 return e,r

def fit_local(x,y,E,window):
 sel=(abs(x)<=window+1e-9)&(abs(y)<=window+1e-9);xx=x[sel];yy=y[sel];ee=E[sel]
 X=np.column_stack([np.ones(len(xx)),xx,yy,.5*xx*xx,xx*yy,.5*yy*yy])
 c=np.linalg.lstsq(X,ee,rcond=None)[0];H=np.array([[c[3],c[4]],[c[4],c[5]]]);ev=np.linalg.eigvalsh(H)
 if ev.min()<=0:raise ValueError('Nonpositivecurvature')
 shift=-np.linalg.solve(H,c[1:3]);emin=c[0]+.5*np.dot(c[1:3],shift)
 return {'window':window,'H':H,'mx':HBAR2_ME/H[0,0],'my':HBAR2_ME/H[1,1],'md':HBAR2_ME/np.sqrt(np.linalg.det(H)),'shift':shift,'emin':emin,'rms':np.sqrt(np.mean((X@c-ee)**2)),'residual_max':np.max(abs(X@c-ee))}

all_dirs=sorted([p for p in R.iterdir() if p.is_dir() and (p/'config.json').exists()])
for d in all_dirs:
 conf=json.loads((d/'config.json').read_text())
 bd=d/conf.get('bands_subdir','.')
 required=['mos2.scf.out','potential.out','average.out','mos2.bands.out']
 if not all(((bd if x=='mos2.bands.out' else d)/x).exists() for x in required):fail.append(d.name+':unfinished');continue
 for out in required:
  text=((bd if out=='mos2.bands.out' else d)/out).read_text()
  if out!='average.out' and 'JOB DONE.' not in text:fail.append(d.name+':'+out+':noJOBDONE')
  if 'Error in routine' in text:fail.append(d.name+':'+out+':nativeerror')
  if out=='mos2.scf.out':
   if 'not converged' in text.rsplit('iteration #',1)[-1] or 'convergence has been achieved' not in text:fail.append(d.name+':finalSCFnotaccepted')
  elif 'not converged' in text:fail.append(d.name+':'+out+':unconvergedeigenvalues')
 if not (bd/'bands.data-file-schema.xml').exists():continue
 e,r=xml_eig(bd/'bands.data-file-schema.xml');scfe,sr=xml_eig(d/'scf.data-file-schema.xml')
 ne=float(sr.find('output/band_structure/nelec').text);assert ne==26
 val=12;cb=13
 cell,pos,sp=geometry(d/'scf.data-file-schema.xml');area=np.linalg.norm(np.cross(cell[0],cell[1]));height=cell[2,2]
 etot=float(sr.find('output/total_energy/etot').text)*HA
 forces=np.array([float(v) for v in sr.find('output/forces').text.split()]).reshape(-1,3)*HA/BOHR
 avg=np.loadtxt(d/'avg.dat');z=avg[:,0]*BOHR;V=avg[:,1]*RY
 left=(z>.10*height)&(z<.20*height);right=(z>.80*height)&(z<.90*height)
 assert left.sum()>3 and right.sum()>3
 vl=V[left].mean();vr=V[right].mean();vv=(vl+vr)/2
 flat=max(np.ptp(V[left]),np.ptp(V[right]),abs(vl-vr))
 krows=list(csv.DictReader((d/'kpoints.csv').open()));assert len(krows)==len(e)==97
 b=2*np.pi*np.linalg.inv(cell).T
 expected_k=np.array([[float(k[x]) for x in ['k1','k2','k3']] for k in krows])@b
 alat=float(r.find('output/atomic_structure').attrib['alat'])*BOHR
 actual_k=np.array([np.fromstring(kk.find('k_point').text,sep=' ') for kk in r.findall('output/band_structure/ks_energies')])*2*np.pi/alat
 kerr=float(np.max(abs(expected_k-actual_k)))
 if kerr>1e-8:fail.append(d.name+':nativekpointorderormappingmismatch')
 bcell,bpos,bsp=geometry(bd/'bands.data-file-schema.xml')
 if np.max(abs(cell-bcell))>1e-8 or np.max(abs(pos-bpos))>1e-8 or sp!=bsp:fail.append(d.name+':SCFbandsgeometrymismatch')
 ids=np.array([x['kind']=='K-local' for x in krows]);x=np.array([float(k['offsetx_invA']) for k in krows])[ids];y=np.array([float(k['offsety_invA']) for k in krows])[ids]
 fits=[fit_local(x,y,e[ids,cb],w) for w in [.01,.02,.03]];fit=fits[1]
 kp=float(e[[k['kind']=='K-prime' for k in krows],cb][0])
 gamma=float(e[[k['kind']=='Gamma' for k in krows],cb][0]);M=float(e[[k['kind']=='M' for k in krows],cb][0])
 q=[]
 for j in range(1,4):
  ind=np.array([k['kind']==f'Gamma-K{j}' and .40-1e-9<=float(k['offsetx_invA'])<=.80+1e-9 for k in krows]);q.append(float(e[ind,cb].min()))
 gap=float(e[:,cb].min()-e[:,val].max())
 coarse_min=float(scfe[:,cb].min())
 row={'case':d.name,'epsilon':conf['epsilon_xx'],'mesh':conf['mesh'],'vacuum_add_A':conf['vacuum_add_A'],'etot_eV':etot,'area_A2':area,'height_A':height,'vacuum_eV':vv,'plateau_left_eV':vl,'plateau_right_eV':vr,'plateau_spread_eV':flat,'CB14_CB15_local_min_separation_eV':float(np.min(e[ids,14]-e[ids,13])),'bands_source':str(bd.relative_to(R)),'kpoint_mapping_max_invA':kerr,'K_CBM_eV':float(fit['emin']),'K_CBM_vac_eV':float(fit['emin']-vv),'K_shift_x_invA':float(fit['shift'][0]),'K_shift_y_invA':float(fit['shift'][1]),'Kprime_minus_K_eV':kp-float(fit['emin']),'Gamma_minus_K_eV':gamma-float(fit['emin']),'M_minus_K_eV':M-float(fit['emin']),'Q1_minus_K_eV':q[0]-float(fit['emin']),'Q2_minus_K_eV':q[1]-float(fit['emin']),'Q3_minus_K_eV':q[2]-float(fit['emin']),'coarse_scf_CBM_minus_K_eV':coarse_min-float(fit['emin']),'sampled_gap_eV':gap,'force_max_eVA':float(np.linalg.norm(forces,axis=1).max()),'mx_me':float(fit['mx']),'my_me':float(fit['my']),'md_me':float(fit['md']),'fit_residual_eV':float(fit['residual_max']),'SCF_intermediate_eigenwarning_count':(d/'mos2.scf.out').read_text().count('not converged'),'SCF_final_eigenwarning_count':(d/'mos2.scf.out').read_text().rsplit('iteration #',1)[-1].count('not converged')}
 records.append(row)
 for f in fits:massrows.append({'case':d.name,'window_invA':f['window'],'mx_me':f['mx'],'my_me':f['my'],'md_me':f['md'],'shift_x_invA':f['shift'][0],'shift_y_invA':f['shift'][1],'CBM_eV':f['emin'],'fit_RMS_eV':f['rms'],'fit_max_residual_eV':f['residual_max'],'Hxy_eVA2':f['H'][0,1]})
 for i,k in enumerate(krows):bandrows.append({'case':d.name,'point':i+1,**k,'valence_eV':e[i,val],'conduction_eV':e[i,cb],'conduction_vac_eV':e[i,cb]-vv})
 for zi,vi in zip(z,V):potentialrows.append({'case':d.name,'z_A':zi,'potential_eV':vi})
 if conf['vacuum_add_A']==0 and conf['mesh']==12:
  if 'bfgs converged' not in (d/'mos2.relax.out').read_text().lower():fail.append(d.name+':ionicrelaxnotaccepted')
  if np.max(abs(forces))>1e-5*RY/BOHR:fail.append(d.name+':finalSCFforceexceedsionicthreshold')
 if flat>.001:fail.append(d.name+':vacuumplateaunotflat')
 if gap<=0 or min(q+[gamma,M,kp])<fit['emin']-1e-5 or coarse_min<fit['emin']-.001:fail.append(d.name+':Knotlowestcheckedsemiconductingvalley')
 if np.min(e[ids,14]-e[ids,13])<.01:fail.append(d.name+':CB14notisolatedfromCB15')
 if max(abs(fit['shift']))>.025:fail.append(d.name+':Kminimumoutsidecentralfitwindow')

def write(name,rows):
 if not rows:return
 with (R/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('cases.csv',records);write('mass-windows.csv',massrows);write('valley-bands.csv',bandrows);write('potential-profiles.csv',potentialrows)
by={r['case']:r for r in records};summary={'completed_cases':len(records),'expected_cases':11,'failures':fail,'model':'300Kscalar-PBEK-valleylongitudinalacousticDPonly','mobility_cm2_Vs':None}
if len(records)==11:
 A0=by['zero']['area_A2']
 def params(names):
  rr=sorted([by[n] for n in names],key=lambda x:x['epsilon']);eps=np.array([x['epsilon'] for x in rr]);Et=np.array([x['etot_eV'] for x in rr]);Ec=np.array([x['K_CBM_vac_eV'] for x in rr]);En=Et-Et[len(Et)//2]
  energy=np.polyfit(eps,En,2);coef,cov=np.polyfit(eps,Ec,1,cov=True)
  return {'C2D_N_m':float(2*energy[0]/A0*16.02176634),'E1_eV':float(coef[0]),'E1_standard_error_eV':float(np.sqrt(cov[0,0])),'energy_fit_max_residual_eV':float(np.max(abs(np.polyval(energy,eps)-En))),'edge_fit_max_residual_eV':float(np.max(abs(np.polyval(coef,eps)-Ec)))}
 sets={'five_strains':['minus010','minus005','zero','plus005','plus010'],'three_strains':['minus005','zero','plus005'],'k16':['k16-minus005','k16-zero','k16-plus005'],'vacuum28':['vacuum28-minus005','vacuum28-zero','vacuum28-plus005']}
 ps={k:params(v) for k,v in sets.items()};summary['fits']=ps
 base=ps['three_strains'];full=ps['five_strains']
 for name,limit in [('five_strains',.05),('k16',.05),('vacuum28',.02)]:
  for key in ['C2D_N_m','E1_eV']:
   change=abs(ps[name][key]-base[key])/abs(base[key]);ps[name][key+'_relative_vs_three']=float(change)
   if change>limit:fail.append(name+':'+key+':differenceexceedsgate')
 if full['C2D_N_m']<=0:fail.append('nonpositiveelasticconstant')
 if abs(full['E1_eV'])<.1 or full['E1_standard_error_eV']/abs(full['E1_eV'])>.1:fail.append('E1nearzeroorunstable')
 mm=[x for x in massrows if x['case']=='zero']
 for key in ['mx_me','my_me','md_me']:
  spread=np.ptp([x[key] for x in mm])/mm[1][key]
  if spread>.05:fail.append('masswindowunstable:'+key)
 summary['baseline_masses']={k:by['zero'][k] for k in ['mx_me','my_me','md_me']}
 # State the sign ofE1 separately; scattering uses its square.
 if not fail:
  ee=1.602176634e-19;hbar=1.054571817e-34;kb=1.380649e-23;me=9.1093837015e-31
  mu=ee*hbar**3*full['C2D_N_m']/(kb*300*(by['zero']['mx_me']*me)*(by['zero']['md_me']*me)*(full['E1_eV']*ee)**2)*1e4
  summary['mobility_cm2_Vs']=float(mu)
 else:summary['mobility_status']='Notreported:finite-difference/modelgatesnotallmet'
else:summary['mobility_status']='Notreported:requiredcasesincomplete'
(R/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('case            strain     Etot(eV)        EC-Vvac(eV)  maxplateau(eV)  Qmin-K(eV)')
for r in records:print(f"{r['case']:19s} {r['epsilon']:+.4f} {r['etot_eV']:15.8f} {r['K_CBM_vac_eV']:12.8f} {r['plateau_spread_eV']:12.3e} {min(r['Q1_minus_K_eV'],r['Q2_minus_K_eV'],r['Q3_minus_K_eV']):10.6f}")
print(json.dumps(summary,indent=2))
