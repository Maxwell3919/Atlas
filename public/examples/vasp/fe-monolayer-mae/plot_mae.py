
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=json.load(open('mae-summary.json'))
k=[p['mesh'] for p in r['pairs']]
e0=[p['delta_E0_x_minus_z_meV_per_Fe'] for p in r['pairs']]
f=[p['delta_F_x_minus_z_meV_per_Fe'] for p in r['pairs']]
fig,axes=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
a,b=axes
a.axhline(0,color='#888888',lw=.8)
a.plot(k,e0,'o-',color='#0072b2',label='E(sigma -> 0)')
a.plot(k,f,'s--',color='#d55e00',label='Free energy F')
a.set(xlabel='In-plane mesh divisions',ylabel='E_x - E_z (meV / Fe)',title='Direction-energy difference')
a.set_xticks(k)
a.legend(frameon=False)
for vals,color,shift in [(e0,'#0072b2',.08),(f,'#d55e00',-.09)]:
    for x,y in zip(k,vals):a.text(x+.3 if x==min(k) else x-.3,y+shift,'%+.4f'%y,ha='left' if x==min(k) else 'right',color=color,fontsize=8)
a.margins(y=.20)
for axis,color in [('x','#d55e00'),('z','#0072b2')]:
    rows=[c for c in r['cases'] if c['name'].endswith('_'+axis)]
    mags=[np.linalg.norm(c['mag_cartesian_muB']) for c in rows]
    b.plot(k,mags,'o-',color=color,label='m along '+axis)
b.set(xlabel='In-plane mesh divisions',ylabel='Total magnetic moment (mu_B / Fe)',title='Magnetization also changes with mesh')
b.set_xticks(k);b.legend(frameon=False)
for ax in axes:ax.grid(alpha=.18)
fig.suptitle('Fe monolayer: fixed structure, sigma = 0.1 eV')
fig.savefig('mae-mesh-check.png',dpi=220)
fig.savefig('mae-mesh-check.pdf')
