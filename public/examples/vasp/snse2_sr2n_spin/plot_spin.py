import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
x=np.loadtxt('spin-path.dat'); s=json.load(open('spin-summary.json'))
a=x[(x[:,7]>=-2)&(x[:,7]<=2)]
fig,axes=plt.subplots(1,3,figsize=(12,4.5),sharex=True,sharey=True,layout='constrained')
for ax,col,label in zip(axes,[10,11,12],['m_x','m_y','m_z']):
    sc=ax.scatter(a[:,2],a[:,7],c=a[:,col],s=5,cmap='coolwarm',norm=Normalize(-1,1),rasterized=True)
    ax.axhline(0,color='0.35',ls='--',lw=.7)
    for p in s['path_ticks_A-1']: ax.axvline(p,color='0.8',lw=.6,zorder=0)
    ax.set_xticks(s['path_ticks_A-1'],['Γ','M','K','Γ'])
    ax.set_title(label+' (native PROCAR projection)')
    ax.set_xlabel('High-symmetry path')
axes[0].set_ylabel('Energy relative to SCF Fermi level (eV)')
fig.colorbar(sc,ax=axes,label='Projected magnetization',shrink=.75)
fig.suptitle('SnSe2/Sr2N: spin projections along Gamma-M-K-Gamma')
fig.savefig('spin-path.png',dpi=220)
fig.savefig('spin-path.pdf')
