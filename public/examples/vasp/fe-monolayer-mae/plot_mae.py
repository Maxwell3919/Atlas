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
a.plot(k,e0,'o-',color='#195f8a',label='E(sigma -> 0)')
a.plot(k,f,'s--',color='#b76729',label='Free energy F')
a.set(xlabel='In-plane mesh divisions',ylabel='E_x - E_z (meV / Fe)',title='Direction-energy difference')
a.set_xticks(k)
a.legend(frameon=False)
for vals,color,shift in [(e0,'#195f8a',.025),(f,'#b76729',-.055)]:
    for x,y in zip(k,vals):a.text(x,y+shift,'%+.4f'%y,ha='center',color=color,fontsize=8)
for axis,color in [('x','#b76729'),('z','#195f8a')]:
    rows=[c for c in r['cases'] if c['name'].endswith('_'+axis)]
    mags=[np.linalg.norm(c['mag_cartesian_muB']) for c in rows]
    b.plot(k,mags,'o-',color=color,label='m along '+axis)
b.set(xlabel='In-plane mesh divisions',ylabel='Total magnetic moment (mu_B / Fe)',title='Magnetization also changes with mesh')
b.set_xticks(k);b.legend(frameon=False)
for ax in axes:ax.grid(alpha=.18)
fig.suptitle('Fe monolayer: fixed structure, sigma = 0.1 eV')
fig.savefig('mae-mesh-check.png',dpi=220)
fig.savefig('mae-mesh-check.pdf')
