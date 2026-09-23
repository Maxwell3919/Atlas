
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
z,v=np.loadtxt('PLANAR_AVERAGE.dat',unpack=True)
r=json.load(open('workfunction-summary.json'))
fig,axes=plt.subplots(2,1,figsize=(8,6.4),gridspec_kw={'height_ratios':[2,1]},layout='constrained')
a,b=axes
a.plot(z,v,color='#25313c',lw=1.3,label='Planar electrostatic potential')
a.axhline(r['fermi_eV'],color='#d55e00',ls='--',lw=1,label='E_F = %.4f eV'%r['fermi_eV'])
colors=['#009e73','#d55e00']
for i,w in enumerate(r['windows']):
    c=colors[i%len(colors)]
    for ax in axes: ax.axvspan(w['lo_A'],w['hi_A'],color=c,alpha=.13)
    a.hlines(w['mean_eV'],w['lo_A'],w['hi_A'],color=c,lw=2)
    b.plot(z,v-w['mean_eV'],color=c,lw=1.1,label='Relative to window %d mean'%(i+1))
a.set(ylabel='Potential (eV)',title='SnSe2: self-consistent 33 x 33 x 1 mesh, LVHAR')
a.legend(frameon=False,fontsize=9)
b.set(xlabel='Distance normal to the layer (Angstrom)',ylabel='Vacuum offset (eV)',ylim=(-.002,.002))
b.legend(frameon=False,fontsize=8)
for ax in axes: ax.grid(alpha=.18); ax.set_xlim(z[0],z[-1])
fig.savefig('workfunction-z.png',dpi=220)
fig.savefig('workfunction-z.pdf')
