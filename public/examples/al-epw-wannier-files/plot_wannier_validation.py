"""Compare the same QE and Wannier eigenvalues; no Fermi-level refitting."""
from pathlib import Path
import argparse, csv, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import atlas_plot_style

parser=argparse.ArgumentParser()
parser.add_argument('--data',type=Path,default=Path('derived'))
parser.add_argument('--out',type=Path,default=Path('figures'))
args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
atlas_plot_style.install()
cases=['k4_frozen10','k8_frozen10','k8_frozen13p5','k12_frozen13p5']
tables={k:list(csv.DictReader((args.data/('band-'+k+'.csv')).open())) for k in cases}
assert all(len(t)==664 for t in tables.values())
q12=tables[cases[-1]]
shared=[(r['k_index'],r['band_rank'],r['QE_eV']) for r in q12]
statistics=[]
for case in cases:
    r=tables[case]
    assert shared==[(x['k_index'],x['band_rank'],x['QE_eV']) for x in r]
    errors=np.array([float(x['error_eV']) for x in r if abs(float(x['QE_minus_EF_eV']))<=1])
    assert len(errors)==47
    for x in r:
        assert abs(float(x['Wannier_eV'])-float(x['QE_eV'])-float(x['error_eV']))<1e-10
        assert abs(float(x['QE_eV'])-float(x['QE_minus_EF_eV'])-8.4122)<1e-10
    statistics.append({'case':case,'selected_states':len(errors),
                       'rms_meV':float(np.sqrt(np.mean(errors**2))*1000),
                       'max_abs_meV':float(np.max(abs(errors))*1000)})

fig,ax=plt.subplots(1,2,figsize=(10,4.7),gridspec_kw={'width_ratios':[1.25,1]})
fig.subplots_adjust(left=.09,right=.97,bottom=.24,top=.78,wspace=.31)
fig.suptitle('Wannier interpolation checked against direct QE bands',x=.09,ha='left',y=.98,fontsize=12)
fig.text(.09,.89,r'Same 166 path points; fixed parent $E_F=8.4122$ eV; eigenvalues paired by energy rank',fontsize=10)
blue,orange='#0072b2','#d55e00'
for n in range(1,5):
    r=[x for x in q12 if int(x['band_rank'])==n]
    x=np.array([float(t['distance_inv_angstrom']) for t in r])
    qe=[float(t['QE_minus_EF_eV']) for t in r]
    wan=[float(t['Wannier_minus_EF_eV']) for t in r]
    ax[0].plot(x,qe,color='#222222',lw=1.3,label='Direct QE' if n==1 else None)
    ax[0].plot(x,wan,color=blue,lw=.9,ls='--',label='Wannier, coarse $12^3$' if n==1 else None)
first=[x for x in q12 if x['band_rank']=='1']
labels=[];positions=[]
special=[('Γ',(0,0,0)),('X',(.5,0,.5)),('W',(.5,.25,.75)),('L',(.5,.5,.5)),('K',(.375,.375,.75))]
for r in first:
    k=tuple(float(r[c]) for c in ('kx_crystal','ky_crystal','kz_crystal'))
    name=next((name for name,v in special if max(abs(a-b) for a,b in zip(k,v))<1e-7),None)
    if name is not None: labels.append(name);positions.append(float(r['distance_inv_angstrom']))
assert labels==['Γ','X','W','L','Γ','K'],labels
for x in positions[1:-1]:ax[0].axvline(x,color='#cccccc',lw=.65,zorder=0)
ax[0].axhline(0,color='#666666',ls=':',lw=.7)
ax[0].set(xticks=positions,xticklabels=labels,xlim=(positions[0],positions[-1]),
          ylim=(-2,2),ylabel=r'$E-E_F$ (eV)',xlabel='Path through the Brillouin zone')
ax[0].legend(frameon=False,loc='lower left',bbox_to_anchor=(0,1.005),ncol=2,fontsize=9,handlelength=1.8,columnspacing=1)
xs=np.arange(4)
ax[1].scatter(xs,[r['rms_meV'] for r in statistics],s=28,color=blue,label='RMS error',zorder=3)
ax[1].scatter(xs,[r['max_abs_meV'] for r in statistics],s=32,facecolors='none',edgecolors=orange,
              marker='s',linewidths=1,label='Maximum absolute error',zorder=3)
ax[1].set_yscale('log')
ax[1].set(xticks=xs,xticklabels=['$4^3$\n10 eV','$8^3$\n10 eV','$8^3$\n13.5 eV','$12^3$\n13.5 eV'],
          ylabel='Band-energy error (meV)',xlabel='Coarse k mesh / frozen-window upper bound',
          xlim=(-.35,3.55),ylim=(15,5500))
ax[1].legend(frameon=False,loc='upper right',fontsize=9)
for key,color,dy in [('rms_meV',blue,-.05),('max_abs_meV',orange,.07)]:
    value=statistics[-1][key]
    ax[1].annotate(f'{value:.1f}',(3,value),xytext=(7,0),textcoords='offset points',va='center',fontsize=9)
fig.text(.09,.025,r'Left: a $\pm 2$ eV view. Right: 47 states within $\pm 1$ eV of the same $E_F$; this path is not a full-zone error bound.',fontsize=9)
fig.savefig(args.out/'al-wannier-validation.png')
plt.close(fig)
(args.out/'wannier-plot-checks.json').write_text(json.dumps({'states_per_case':664,'path_points':166,
    'shared_parent_EF_eV':8.4122,'selected_states':47,'statistics':statistics,
    'special_point_labels':labels,'special_point_positions_inv_angstrom':positions},indent=2)+'\n')
print(json.dumps(statistics,indent=2))
