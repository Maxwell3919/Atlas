from pathlib import Path
import json,csv,re
from decimal import Decimal
import numpy as np
from ase.io import read
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
results={s:json.loads((p/'outputs'/s/'result.json').read_text()) for s in ['smoke','relax','forcecheck']}
assert all(r['accepted_local'] for r in results.values())
def table(name,rows):
 with (p/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for i,a in enumerate(read(p/'outputs/relax/trajectory.traj',index=':')):
 rows.append({'optimizer_step':i,'bond_A':float(a.get_distance(0,1)),'energy_eV':float(a.get_potential_energy()),'max_force_eV_A':float(np.linalg.norm(a.get_forces(),axis=1).max())})
assert len(rows)>=1 and abs(rows[-1]['energy_eV']-results['relax']['energy_final_eV'])<1e-10
table('figures/h2-relax.csv',rows)
fig,axs=plt.subplots(1,2,figsize=(9,3.8),layout='constrained');x=[r['optimizer_step'] for r in rows]
axs[0].plot(x,[r['energy_eV']-rows[-1]['energy_eV'] for r in rows],'-o');axs[0].set_ylabel('Energy - final energy (eV)')
axs[1].semilogy(x,[r['max_force_eV_A'] for r in rows],'-o',label='Accepted optimizer frames');axs[1].axhline(.05,ls='--',color='black',label='0.05 eV/Å threshold');axs[1].set_ylabel('Maximum force (eV/Å)');axs[1].legend(fontsize=8)
for ax in axs:ax.set_xlabel('Optimizer step');ax.set_xticks(x);ax.grid(alpha=.2)
fig.suptitle('GPAW H₂: symmetry off / PBE / PW 340 eV / periodic 6 Å box\nLocal teaching check; cutoff and box convergence not tested',fontsize=10)
fig.savefig(p/'figures/h2-relax.png',dpi=180);fig.savefig(p/'figures/h2-relax.svg');plt.close(fig)
# Arithmetic independent of the input's stored finite-difference result.
fd=json.loads((p/'outputs/forcecheck/result.json').read_text(),parse_float=Decimal)
f_calc=-(fd['energy_plus_eV']-fd['energy_minus_eV'])/(2*fd['delta_A']);f_analytic=fd['forces_initial_eV_A'][1][2];err=abs(f_calc-f_analytic)
assert err<=Decimal('0.02') and abs(f_calc-fd['force_fd_eV_A'])<Decimal('1e-13')
force_log=(p/'outputs/forcecheck/gpaw.txt').read_text();iterations=list(map(int,re.findall(r'Converged in (\d+) steps',force_log)));assert len(iterations)==3
positions=[float(x) for x in re.findall(r'\| 1 \|\s+H \|\s+[0-9.]+ \|\s+[0-9.]+ \|\s+([0-9.]+) \|',force_log)];assert positions==[3.37,3.375,3.365],positions
energies=[fd['energy_initial_eV'],fd['energy_plus_eV'],fd['energy_minus_eV']]
printed=re.findall(r'Extrapolated:\s+(-?[0-9.]+)',force_log);assert len(printed)==3
for exact,q in zip(energies,printed):assert abs(exact-Decimal(q))<=Decimal('0.00000051')
force_rows=[{'geometry':label,'atom1_z_A':str(z),'displacement_from_reference_A':str(delta),'energy_eV':str(e),'SCF_iterations':n} for label,z,delta,e,n in zip(['reference','plus','minus'],positions,[Decimal('0'),fd['delta_A'],-fd['delta_A']],energies,iterations)]
table('force-energies.csv',force_rows)
arithmetic={'method':'Decimal arithmetic independently from saved precise energies, not copied finite-difference result','E0_eV':str(fd['energy_initial_eV']),'Eplus_eV':str(fd['energy_plus_eV']),'Eminus_eV':str(fd['energy_minus_eV']),'delta_A':str(fd['delta_A']),'denominator_A':'0.010','F1z_eV_A':str(f_analytic),'Ffd_independent_eV_A':str(f_calc),'absolute_error_independent_eV_A':str(err),'threshold_eV_A':'0.02','threshold_pass':True,'three_logged_SCF_iterations':iterations,'logged_atom1_z_A':positions,'printed_energy_rounding_matches_saved_values':True,'basis_box_delta_convergence_claim':False}
(p/'force-check-independent.json').write_text(json.dumps(arithmetic,indent=2)+'\n')
table('force-check-comparison.csv',[{'F1z_eV_A':str(f_analytic),'Ffd_eV_A':str(f_calc),'abs_error_eV_A':str(err),'threshold_eV_A':'0.02','pass':True}])
scf=[];summary=[];warnings=[]
for stage,d in results.items():
 log=(p/'outputs'/stage/'gpaw.txt').read_text();iters=list(map(int,re.findall(r'Converged in (\d+) steps',log)));assert len(iters)==({'smoke':1,'relax':5,'forcecheck':3}[stage])
 assert "symmetry=Symmetry(point_group=False, time_reversal=False)" in log
 for n in ['1e-06 eV / valence electron','1e-06 electrons / valence electron','1e-08 eV^2 / valence electron']:assert log.count(n)==len(iters)
 for i,n in enumerate(iters):scf.append({'stage':stage,'SCF_block_index':i,'iterations':n,'converged_under_original_thresholds':True})
 for source in [p/'outputs'/stage/'gpaw.txt',p/'logs'/f'{stage}.log']:
  for i,line in enumerate(source.read_text().splitlines(),1):
   if re.search(r'\b(warning|error|deprecated)\b',line,re.I):warnings.append({'file':str(source.relative_to(p)),'line':i,'text':line})
 summary.append({'stage':stage,'status':'PASS_LOCAL_TEACHING','energy_initial_eV':d['energy_initial_eV'],'energy_final_eV':d.get('energy_final_eV',''),'bond_initial_A':d['bond_initial_A'],'bond_final_A':d.get('bond_final_A',''),'max_force_final_eV_A':d.get('max_force_final_eV_A',''),'force_error_eV_A':d.get('force_error_eV_A','')})
sm=results['smoke'];net=float(np.linalg.norm(np.asarray(sm['forces_initial_eV_A']).sum(axis=0)));assert net<=1e-5
rel=results['relax'];assert rel['max_force_final_eV_A']<=.05 and rel['optimizer_steps']<=12 and rel['energy_final_eV']<=rel['energy_initial_eV']+1e-4 and .5<rel['bond_final_A']<1.2
(p/'local-output-checks.json').write_text(json.dumps({'status':'EXECUTOR_POSTPROCESS_CHECKS_PASS_NOT_INDEPENDENT_FINAL_REVIEW','smoke_net_force_norm_eV_A':net,'all_original_geometry_criteria_pass':True,'SCF_blocks':scf,'warning_error_deprecated_matches':warnings,'warning_check_scope':'literal word scan of full native GPAW and stage stdout; not proof of all possible warning semantics'},indent=2))
table('scf-ledger.csv',scf);table('stage-summary.csv',summary)
steps=[]
for f in sorted((p/'logs').glob('*-exit.txt')):
 label=f.name[:-9];text=(p/'logs'/f'{label}-time.txt').read_text();wall=next(s.split(': ',1)[1] for s in text.splitlines() if 'Elapsed (wall clock)' in s);v=wall.split(':');sec=float(v[-1])+60*int(v[-2]);sec+=3600*int(v[-3]) if len(v)==3 else 0;rss=int(next(s.rsplit(': ',1)[1] for s in text.splitlines() if 'Maximum resident set size' in s));steps.append({'step':label,'exit_code':int(f.read_text()),'elapsed_seconds':sec,'max_RSS_KiB':rss,'log':f'logs/{label}.log'})
(p/'step-ledger.json').write_text(json.dumps(steps,indent=2));table('step-ledger.csv',steps)
print('PASS: nine actual SCF blocks, independent force arithmetic, actual atom positions and energy rounding, three optimizer frames; warning matches:',len(warnings))
