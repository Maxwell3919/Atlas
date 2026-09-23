
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
x,y=np.loadtxt('PLANAR_AVERAGE.dat',unpack=True)
s=json.load(open('potential-summary.json'))
fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
ax.plot(x,y,color='#25313c',lw=1.4)
for n,w in enumerate(s['windows']):
    ax.axvspan(w['lo_A'],w['hi_A'],color=['#009e73','#d55e00'][n%2],alpha=.14)
    ax.hlines(w['mean_eV'],w['lo_A'],w['hi_A'],color=['#009e73','#d55e00'][n%2],lw=2,label='Window %d: %.4f eV'%(n+1,w['mean_eV']))
ax.set(xlabel='Distance normal to the layer (Angstrom)',ylabel='Planar-averaged potential (eV)')
ax.legend(frameon=False)
ax.grid(alpha=.18)
fig.savefig('potential-z.png',dpi=220)
fig.savefig('potential-z.pdf')
