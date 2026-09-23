"""Read actual Monte Carlo CSVs and render figures; no generated fit data."""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'figures';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
rows=list(csv.DictReader((R/'results/helicity.csv').open()))
fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
for n,color in [(8,'#326ca8'),(16,'#bf6635'),(24,'#39816d')]:
    selected=[r for r in rows if int(r['L'])==n]
    temp=np.array([float(r['temperature_J']) for r in selected])
    axs[0].errorbar(temp,[float(r['Y_J']) for r in selected],yerr=[float(r['display_error_J']) for r in selected],fmt='o-',capsize=3,color=color,label=f'L={n}, two seeds')
    axs[1].plot(temp,[float(r['vortex_abs_density']) for r in selected],'o-',color=color,label=f'L={n}')
t=np.linspace(.68,1.12,100);axs[0].plot(t,2*t/np.pi,'--',color='.25',label='2T / pi reference')
axs[0].set(xlabel='T / J  (kB=1)',ylabel='Helicity modulus Y / J',title='Finite square lattices; no TBKT extrapolation')
axs[1].set(xlabel='T / J',ylabel='Mean absolute plaquette vorticity',title='Defect density, not an unbinding test')
for ax in axs:ax.legend(fontsize=8)
fig.savefig(O/'xy-helicity.png',dpi=200);fig.savefig(O/'xy-helicity.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,5),layout='constrained')
for ax,temp in zip(axs,[.70,1.10]):
    run=sorted((R/'base').glob(f'L24-T{temp:.2f}-s*'))[0]
    angle=np.loadtxt(run/'final-angles.csv',delimiter=',');vort=np.loadtxt(run/'final-vortices.csv',delimiter=',')
    n=angle.shape[0];x,y=np.indices(angle.shape)
    ax.quiver(x,y,np.cos(angle),np.sin(angle),angle,cmap='twilight',clim=(-np.pi,np.pi),pivot='mid',scale=32,width=.0025)
    for charge,color,marker in [(1,'#d02525','o'),(-1,'#18449e','s')]:
        px,py=np.where(vort==charge)
        ax.scatter((px+.5)%n,(py+.5)%n,s=45,facecolors='none',edgecolors=color,marker=marker,label=f'vorticity {charge:+d}')
    meta=json.loads((run/'run.json').read_text())
    ax.set(xlim=(-.7,n+.2),ylim=(-.7,n+.2),aspect='equal',xlabel='lattice x',ylabel='lattice y',title=f'L=24, T/J={temp:.2f}, seed={meta["seed"]}')
    ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2)
fig.suptitle('Actual final Monte Carlo configurations; periodic square lattice',fontsize=12)
fig.savefig(O/'xy-configurations.png',dpi=200);fig.savefig(O/'xy-configurations.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
cases=[r for r in csv.DictReader((R/'results/extension-comparison.csv').open()) if int(r['L'])==24]
for i,r in enumerate(cases):
    label=f'T={r["temperature_J"]}, {r["initialization"]}'
    axs[0].errorbar([20000,40000],[float(r['Y_base_J']),float(r['Y_extended_J'])],yerr=[float(r['base_error_J']),float(r['extended_error_J'])],fmt='o-',capsize=3,label=label)
for d in sorted((R/'extended').glob('L24-T0.92-*')):
    a=np.loadtxt(d/'series.csv',delimiter=',',skiprows=1);meta=json.loads((d/'run.json').read_text())
    means=a.reshape(80,100,10).mean(axis=1)
    axs[1].plot(means[:,0],means[:,1],label=meta['initialization'])
axs[0].set(xlabel='Production sweeps',ylabel='Helicity modulus Y / J',title='Nested continuation of the same chains')
axs[1].set(xlabel='Production sweep',ylabel='Block-mean energy / (N J)',title='L=24, T/J=0.92; blocks of 500 sweeps')
axs[0].set_xticks([20000,40000])
axs[1].set_xticks([0,10000,20000,30000,40000])
for ax in axs:ax.legend(fontsize=7)
fig.savefig(O/'xy-sampling.png',dpi=200);fig.savefig(O/'xy-sampling.pdf');plt.close(fig)
print('Saved xy-helicity, xy-configurations, xy-sampling as PNG and PDF')
