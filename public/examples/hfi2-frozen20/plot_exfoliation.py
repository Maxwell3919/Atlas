from pathlib import Path
import csv, json
import numpy as np
import matplotlib.pyplot as plt
from atlas_plot_style import install
install()
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "text.color": "black", "axes.labelcolor": "black", "axes.edgecolor": "black",
    "xtick.color": "black", "ytick.color": "black", "axes.linewidth": .7,
    "xtick.major.width": .7, "ytick.major.width": .7,
    "xtick.direction": "out", "ytick.direction": "out", "axes.grid": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"
})

here=Path(__file__).resolve().parent
with (here/'exfoliation.csv').open() as f: rows=list(csv.DictReader(f))
d=np.array([float(r['d_A']) for r in rows])
w=np.array([float(r['W_meV_A2']) for r in rows])
e=np.array([float(r['delta_E_meV']) for r in rows])
if len(rows)!=20 or not np.isfinite(np.r_[d,w,e]).all():raise ValueError('Invalid data')
fig,ax=plt.subplots(1,2,figsize=(6.8,2.8),layout='constrained')
ax[0].plot(d,w,'o-',color='#0072B2',ms=3,lw=1)
ax[0].set(xlabel=r'Layer displacement, $d$ ($\mathrm{\AA}$)',
          ylabel=r'$\left[E(d)-E(0)\right]/A$ (meV $\mathrm{\AA}^{-2}$)',
          xlim=(-.4,20.4),ylim=(-.5,25))
take=d>=12
ax[1].plot(d[take],e[take],'s--',color='#D55E00',ms=3,lw=1)
ax[1].set(xlabel=r'Layer displacement, $d$ ($\mathrm{\AA}$)',
          ylabel=r'$E(d)-E(0)$ (meV)',xlim=(11.6,20.4))
for label,a in zip('ab',ax):a.text(-.18,1.03,label,transform=a.transAxes,fontweight='bold',va='bottom')
for ext in ('svg','pdf','png'):fig.savefig(here/('hfi2-exfoliation.'+ext),dpi=300)
plt.close(fig)
