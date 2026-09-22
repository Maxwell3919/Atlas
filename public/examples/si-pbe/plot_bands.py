from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
data=np.loadtxt(r/'bands-cg/si.bands.dat.gnu')
assert data.shape==(8*121,2)
bands=data.reshape(8,121,2)
assert np.allclose(bands[:,:,0],bands[0,:,0])
vbm=bands[3,:,1].max()
ticks=bands[0,[0,24,36,48,72,96,120],0]
fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
for band in bands:ax.plot(band[:,0],band[:,1]-vbm,color='#2463a5',lw=1.1)
for tick in ticks:ax.axvline(tick,color='0.85',lw=.7)
ax.axhline(0,color='0.4',ls='--',lw=.8)
ax.set(xticks=ticks,xticklabels=['Γ','X','W','K','Γ','L','X'],
       xlim=(ticks[0],ticks[-1]),ylim=(-13,7),ylabel='Energy − path VBM (eV)',
       title='Si, PBE, fixed example cell; no SOC')
(r/'plots').mkdir(exist_ok=True)
fig.savefig(r/'plots/bands-direct.png',dpi=240)
fig.savefig(r/'plots/bands-direct.svg')
print('8 bands, 121 k points; path VBM =',vbm,'eV')
