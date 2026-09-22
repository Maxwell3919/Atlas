"""Run in the downloaded berry directory; needs NumPy and Matplotlib."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
out=root/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,3,figsize=(12,3.7),layout='constrained')
phase_grids=[]
for n in [4,6]:
    rows=list(csv.DictReader((root/f'results/k{n}-plaquettes.csv').open()))
    array=np.empty((n,n))
    for r in rows:
        if int(r['k3_index'])==0:array[int(r['k2_index']),int(r['k1_index'])]=float(r['phase_rad'])*1e6
    phase_grids.append(array)
limit=max(np.max(np.abs(a)) for a in phase_grids)
for ax,n,a in zip(axs[:2],[4,6],phase_grids):
    im=ax.imshow(a,origin='lower',extent=(0,1,0,1),cmap='RdBu_r',vmin=-limit,vmax=limit,interpolation='nearest')
    ax.set(xlabel='Fractional k1',ylabel='Fractional k2',title=f'{n} x {n} x {n}, k3 = 0')
fig.colorbar(im,ax=list(axs[:2]),label='Plaquette phase (microradian)',shrink=.85)
rows=list(csv.DictReader((root/'results/slices.csv').open()))
for n,marker in [(4,'o'),(6,'s')]:
    selected=[r for r in rows if int(r['grid'])==n]
    axs[2].plot([float(r['k3_fraction']) for r in selected],[float(r['chern_raw']) for r in selected],marker=marker,label=f'{n} x {n} x {n}')
axs[2].axhline(0,color='.6',lw=.8)
axs[2].set(xlabel='Fixed fractional k3',ylabel='Raw slice Chern sum',title='All periodic slices')
axs[2].ticklabel_format(axis='y',style='sci',scilimits=(0,0));axs[2].legend()
fig.suptitle('Si occupied-subspace overlap calculation; no SOC; one equivalent spin channel',fontsize=12)
fig.savefig(out/'berry-slices.png',dpi=190);fig.savefig(out/'berry-slices.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(9,3.6),layout='constrained')
for n,color in [(4,'#326ca8'),(6,'#cc6b2c')]:
    rows=list(csv.DictReader((root/f'results/k{n}-links.csv').open()))
    axs[0].hist([float(r['min_singular']) for r in rows],bins=18,histtype='step',lw=1.8,color=color,label=f'{n} x {n} x {n}')
    gauges=list(csv.DictReader((root/f'results/k{n}-gauge-check.csv').open()))
    axs[1].plot([int(r['trial'])+1 for r in gauges],[float(r['max_flux_difference_rad']) for r in gauges],'o-',ms=4,color=color,label=f'{n} x {n} x {n}')
axs[0].set(xlabel='Smallest singular value of each occupied overlap',ylabel='Directed links',title='No singular selected links')
axs[1].set(xlabel='Independent random U(4) gauge',ylabel='Maximum phase difference (rad)',title='Gauge invariance check')
axs[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
for ax in axs:ax.legend()
fig.savefig(out/'berry-checks.png',dpi=190);fig.savefig(out/'berry-checks.pdf');plt.close(fig)
print('Saved figures/berry-slices.png,.pdf and berry-checks.png,.pdf')
