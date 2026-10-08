from pathlib import Path
import csv,os,resource
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent;(p/'figures').mkdir(exist_ok=True)
rows=list(csv.DictReader((p/'scf-ledger.csv').open()));x=[int(r['iteration']) for r in rows];e=[float(r['energy_Ha']) for r in rows]
with (p/'figures/scf-convergence.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['iteration','energy_Ha','energy_minus_final_Ha','absolute_derived_energy_change_Ha']);w.writeheader()
 for i,r in enumerate(rows):w.writerow({'iteration':r['iteration'],'energy_Ha':r['energy_Ha'],'energy_minus_final_Ha':e[i]-e[-1],'absolute_derived_energy_change_Ha':abs(float(r['derived_deltaE_Ha'])) if r['derived_deltaE_Ha'] else ''})
fig,axs=plt.subplots(1,2,figsize=(9,3.8),layout='constrained');axs[0].plot(x,[v-e[-1] for v in e],'-o');axs[0].set_ylabel('Energy - final energy (Ha)');axs[1].semilogy(x[1:],[abs(float(r['derived_deltaE_Ha'])) for r in rows[1:]],'-o');axs[1].axhline(1e-6,color='black',ls='--',label='toldfe = 1e-6 Ha');axs[1].set_ylabel('Absolute consecutive energy change (Ha)');axs[1].legend(fontsize=8)
for ax in axs:ax.set_xlabel('Actual SCF iteration');ax.set_xticks(x);ax.grid(alpha=.2)
fig.suptitle('ABINIT 9.10.4: fixed H₂ / NC-LDA / 10 Ha / periodic 10 Bohr box\nTeaching SCF check; basis, box and force accuracy not established',fontsize=10);fig.savefig(p/'figures/scf-convergence.png',dpi=180);fig.savefig(p/'figures/scf-convergence.svg');plt.close(fig)
