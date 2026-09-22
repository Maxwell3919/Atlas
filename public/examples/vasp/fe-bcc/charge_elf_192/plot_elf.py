import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(8.4,3.8),layout='constrained')
for ax,tag in zip(axes,['up','down']):
    a=np.loadtxt('elf-'+tag+'-z0.dat'); nx=a.shape[1];ny=a.shape[0]
    im=ax.pcolormesh(np.linspace(0,2.8,nx+1),np.linspace(0,2.8,ny+1),a,shading='flat',cmap='viridis',vmin=0,vmax=1)
    ax.set(xlabel='x (Angstrom)',ylabel='y (Angstrom)',title='Spin '+tag+', z=0')
    ax.set_aspect('equal')
fig.colorbar(im,ax=axes,label='Electron localization function',shrink=.8)
fig.savefig('elf-z0.png',dpi=220);fig.savefig('elf-z0.pdf')
