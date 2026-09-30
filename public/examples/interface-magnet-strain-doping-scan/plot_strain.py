
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
rows=sorted((x for x in csv.DictReader((r/'elastic/strain-stress.csv').open()) if x['mode']=='xx'),key=lambda x:float(x['engineering_strain']))
e=np.array([float(x['engineering_strain']) for x in rows])*100
energy=np.array([float(x['energy_Ry']) for x in rows])
sxx=[float(x['sigma_xx_GPa']) for x in rows]
syy=[float(x['sigma_yy_GPa']) for x in rows]
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
axes[0].plot(e,(energy-energy.min())*13.605693122994*1000,'o-',color='#0072b2')
axes[0].set(xlabel='Applied x strain (%)',ylabel='F - lowest sampled F (meV/atom)')
axes[1].plot(e,sxx,'o-',label='Tensile-positive stress xx',color='#0072b2')
axes[1].plot(e,syy,'s-',label='Tensile-positive stress yy',color='#d55e00')
axes[1].set(xlabel='Applied x strain (%)',ylabel='Stress (GPa)')
axes[1].legend(frameon=False,fontsize=8)
for ax in axes:
    ax.axvline(0,color='.6',lw=.7);ax.grid(alpha=.18)
fig.suptitle('fcc Al | fixed electron number, 16³ k mesh, MV width 0.02 Ry',fontsize=11)
(r/'figures').mkdir(exist_ok=True)
fig.savefig(r/'figures/strain-scan.png',dpi=220)
fig.savefig(r/'figures/strain-scan.svg')
