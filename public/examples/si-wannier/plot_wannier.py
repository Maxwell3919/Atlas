
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;out=r/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
cols={4:'#ad623e',6:'#277f8e'}
def load(p):return np.loadtxt(r/p,delimiter=',',skiprows=1)
b4=load('k4/bands.csv');b6=load('k6/bands.csv');direct=load('direct-bands.csv');e=list(csv.DictReader((r/'validation-errors.csv').open()))
labels=[x.split() for x in (r/'k4/silicon_band.labelinfo.dat').read_text().splitlines()];ticks=[float(x[2]) for x in labels];names=['Γ' if x[0]=='G' else x[0] for x in labels]
fig,ax=plt.subplots(2,1,figsize=(7.5,7),sharex=True,gridspec_kw={'height_ratios':[3,1.3]})
for mesh,b,ls in [(4,b4,'--'),(6,b6,'-')]:
 for ib in range(4):ax[0].plot(b[:,0],b[:,5+ib],color=cols[mesh],ls=ls,lw=1.2,label=f'{mesh}³ Wannier' if ib==0 else None)
for ib in range(4):ax[0].plot(direct[:,4],direct[:,9+ib],'o',mfc='white',mec='#24242a',ms=4,label='Direct DFT checks' if ib==0 else None)
ax[0].set(ylabel='Energy relative to direct Γ valence maximum (eV)',title='Si | four valence bands only');ax[0].legend(frameon=False,ncol=3,fontsize=9)
for mesh in [4,6]:
 rows=[v for v in e if int(v['training_mesh'])==mesh];ix=sorted(set(int(v['path_index']) for v in rows));x=[];y=[]
 for j in ix:
  values=[v for v in rows if int(v['path_index'])==j];x.append(float(values[0]['distance_Ainv']));y.append(max(abs(float(v['error_eV'])) for v in values)*1000)
 ax[1].plot(x,y,'o-',color=cols[mesh],label=f'{mesh}³ mesh')
ax[1].set(ylabel='Maximum band error (meV)',xticks=ticks,xticklabels=names,xlim=(ticks[0],ticks[-1]))
for a in ax:
 for x in ticks:a.axvline(x,color='#bfbfc4',lw=.6,zorder=0)
fig.tight_layout();fig.savefig(out/'wannier-bands.png',bbox_inches='tight');fig.savefig(out/'wannier-bands.pdf',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(9,3.8))
for mesh in [4,6]:
 x=load(f'k{mesh}/spread-history.csv');ax[0].plot(x[:,0],x[:,3],'o-',color=cols[mesh],label=f'{mesh}³')
 ax[1].semilogy(x[:,0],np.maximum(abs(x[:,1]),1e-16),'o-',color=cols[mesh],label=f'{mesh}³')
ax[0].set(xlabel='Wannier iteration',ylabel='Total spread (bohr²)');ax[0].legend(frameon=False)
ax[1].axhline(1e-10,color='#777',ls='--',lw=1,label='Tolerance');ax[1].set(xlabel='Wannier iteration',ylabel='Absolute spread change (bohr²)');ax[1].legend(frameon=False)
fig.suptitle('Spread convergence within a mesh does not establish interpolation accuracy',fontsize=11)
fig.tight_layout();fig.savefig(out/'wannier-spread.png',bbox_inches='tight');fig.savefig(out/'wannier-spread.pdf',bbox_inches='tight');plt.close(fig)
print('Wrote wannier-bands and wannier-spread as PNG/PDF')
