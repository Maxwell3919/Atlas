"""Run beside summary.json after analyse_unfold.py; matplotlib/numpy only.
Display raw native spectral weights; no weight rescaling or invented broadening.
"""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
m=json.loads((R/'metadata.json').read_text());s=json.loads((R/'summary.json').read_text())
zero=s['comparison']['energy_zero_eV']
pc=np.genfromtxt(R/'primitive/bands.csv',delimiter=',',names=True)
sc=np.genfromtxt(R/'supercell/bands.csv',delimiter=',',names=True)
ticks=m['path_vertex_distance_inv_A'];labels=['Γ','X','W','L','Γ']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(11,5.4),sharex=True,sharey=True,layout='constrained')
axs[0].scatter(sc['distance_inv_A'],sc['energy_eV']-zero,s=8,color='#969ba3',alpha=.8,label='24 supercell states per k')
for ax in axs:
 for band in range(1,9):
  b=pc[pc['band']==band]
  ax.plot(b['distance_inv_A'],b['energy_eV']-zero,color='#202734',lw=.8,alpha=.75,label='Primitive-cell DFT' if band==1 else None)
 ax.set_xticks(ticks,labels);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,12)
 ax.set_xlabel('Primitive reciprocal-space path');ax.axhline(0,color='#555',lw=.5,ls='--')
 for x in ticks[1:-1]:ax.axvline(x,color='#bbb',lw=.6)
show=sc['native_weight']>=1e-5
points=axs[1].scatter(sc['distance_inv_A'][show],sc['energy_eV'][show]-zero,s=45*sc['native_weight'][show],c=sc['native_weight'][show],cmap='viridis',vmin=0,vmax=1,zorder=3,alpha=.85)
fig.colorbar(points,ax=axs[1],label='Native unfolding weight',shrink=.8)
axs[0].set_ylabel('Energy − primitive Γ valence maximum (eV)')
axs[0].set_title('Same perfect Si crystal, more supercell states')
axs[1].set_title('Wavefunction weights recover primitive bands')
axs[0].legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.15),ncol=2,fontsize=8)
fig.suptitle('Si: perfect 2 × 1 × 1 supercell | QE 7.5 | NC/PZ | 40 path points',fontsize=13)
for ext in ['png','svg']:fig.savefig(R/f'unfolded-bands.{ext}',dpi=220)
plt.close(fig)
# Validation panels use independent wavefunction audit, not plot marker appearance.
audit=np.genfromtxt(R/'wavefunction-audit.csv',delimiter=',',names=True,dtype=None,encoding='utf-8')
audit=audit[audit['cell']=='supercell']
indices=np.arange(1,41)
errnorm=np.array([max(abs(audit['norm'][audit['ik']==i]-1)) for i in indices])
errnative=np.array([max(abs(audit['native_minus_even'][audit['ik']==i])) for i in indices])
comp=list(csv.DictReader((R/'primitive-comparison.csv').open()))
errenergy=np.array([max(abs(float(x['delta_eV'])) for x in comp if int(x['ik'])==i) for i in indices])
fig,axs=plt.subplots(1,3,figsize=(12,3.7),layout='constrained')
for ax,y,title,label in zip(axs,[errnorm,errnative,errenergy*1e6],['Wavefunction normalization','Native versus independent projector','Unfolded versus primitive DFT'],['max |norm − 1|','max |weight difference|','max |energy difference| (μeV)']):
 ax.plot(indices,y,'o-',ms=3,lw=.8,color='#246a73');ax.set_title(title,fontsize=10);ax.set_xlabel('Path-point index');ax.set_ylabel(label)
 if ax!=axs[2]:ax.set_yscale('log')
 ax.grid(alpha=.2)
for ext in ['png','svg']:fig.savefig(R/f'unfolding-audit.{ext}',dpi=220)
plt.close(fig)
print('Wrote unfolded-bands.png/.svg and unfolding-audit.png/.svg')
print('Weights below1e-5 are hidden in the spectral scatter only; source values are unchanged.')
