
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=json.load(open('exchange-summary.json'))
base=r['rows'][0]['E0_eV_cell']/r['rows'][0]['n_atoms']
rows=r['rows'][2:]
x=np.arange(len(rows))
dft=[1000*(a['E0_eV_cell']/a['n_atoms']-base) for a in rows]
model=[1000*(a['predicted_E0_eV_cell']/a['n_atoms']-base) for a in rows]
fig,axes=plt.subplots(1,2,figsize=(10,4.3),layout='constrained')
a,b=axes
a.bar(x-.16,dft,.32,color='#0072b2',label='DFT')
a.bar(x+.16,model,.32,color='#d0a354',label='Two-state model')
a.set_xticks(x,[a['state'] for a in rows]);a.set(ylabel='Energy relative to FM (meV / Fe)',title='Cell-folding controls')
for i,row in enumerate(rows):a.text(i,max(dft[i],model[i])+10,'residual\n%+.4f meV/Fe'%row['residual_meV_atom'],ha='center',fontsize=8)
a.set_ylim(-30,500);a.legend(frameon=False)
labels=['FM reference','AFM reference','Stripe trial']
mag=[np.mean(np.abs(r['rows'][i]['local_moment_muB'])) for i in [0,1]]+[np.mean(np.abs(r['rejected_trial']['local_moment_muB']))]
b.bar(np.arange(3),mag,color=['#0072b2','#d0a354','#9a4856'])
b.set_xticks(np.arange(3),labels,rotation=12);b.set(ylabel='Mean absolute PAW local moment (mu_B)',title='Third initialization loses its moment')
for i,v in enumerate(mag):b.text(i,v+.045,'%.3f'%v,ha='center',fontsize=10)
b.set_ylim(0,2.6);b.text(2,.4,'Excluded from\nmodel validation',ha='center',color='#9a4856',fontsize=9)
for ax in axes:ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.savefig('exchange-model-check.png',dpi=220)
fig.savefig('exchange-model-check.pdf')
