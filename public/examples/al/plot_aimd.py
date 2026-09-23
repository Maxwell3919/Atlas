"""Plot the verified QE Al AIMD records from the Al bundle root."""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=r/'aimd';out=r/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
colors=['#009e73','#d55e00','#cc79a7']
def data(name):return np.genfromtxt(d/name/'thermo.csv',delimiter=',',names=True)
def save(fig,name):
    fig.tight_layout();fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
nvt=data('nvt-dt20-cg');nve20=data('nve-dt20-nosym');nve10=data('nve-dt10-nosym')
fig,ax=plt.subplots(2,1,figsize=(7.4,6),sharex=True)
ax[0].plot(nvt['energy_sample_time_fs'],nvt['temperature_K'],color=colors[0],label='SVR target 300 K; dt = 0.968 fs')
ax[0].axhline(300,color='#777',ls='--',lw=1,label='Target')
ax[0].set(ylabel='Instantaneous temperature (K)');ax[0].legend(frameon=False,fontsize=9)
for arr,c,label in [(nve20,colors[1],'NVE dt = 0.968 fs'),(nve10,colors[2],'NVE dt = 0.484 fs')]:
    ax[1].plot(arr['energy_sample_time_fs'],arr['temperature_K'],color=c,label=label)
ax[1].set(xlabel='Time of the sampled energy/velocity (fs)',ylabel='Instantaneous temperature (K)');ax[1].legend(frameon=False,fontsize=9)
fig.suptitle('8-atom periodic Al | short trajectories, not a thermal-stability test',fontsize=11);save(fig,'aimd-temperature')
fig,ax=plt.subplots(1,2,figsize=(10,4))
for arr,c,label in [(nve20,colors[1],'dt = 0.968 fs'),(nve10,colors[2],'dt = 0.484 fs')]:
    ax[0].plot(arr['energy_sample_time_fs'],arr['total_change_meV_atom'],color=c,label=label)
ax[0].set(xlabel='Time (fs)',ylabel='Change of total energy (meV/atom)');ax[0].legend(frameon=False)
conv=13.605693122994*1000/8
for field,c,label in [('kinetic_Ry',colors[1],'Kinetic'),('potential_Ry',colors[0],'Potential')]:
    ax[1].plot(nve10['energy_sample_time_fs'],(nve10[field]-nve10[field][0])*conv,color=c,label=label)
ax[1].set(xlabel='Time (fs)',ylabel='Energy change (meV/atom)');ax[1].legend(frameon=False)
fig.suptitle('NVE step-size check over ~48 fs | identical initial positions and velocities',fontsize=11);save(fig,'aimd-energy')
fig,ax=plt.subplots(figsize=(7.2,3.7))
for name,c,label in [('nvt-dt20-cg',colors[0],'SVR'),('nve-dt20-nosym',colors[1],'NVE dt = 0.968 fs'),('nve-dt10-nosym',colors[2],'NVE dt = 0.484 fs')]:
    a=np.load(d/name/'trajectory.npz');p=a['positions_A'];rms=np.sqrt(np.mean(np.sum((p-p[0])**2,axis=2),axis=1))
    ax.plot(a['time_fs'],rms,color=c,label=label)
ax.set(xlabel='Coordinate time (fs)',ylabel='RMS displacement from initial positions (Å)',title='Short-time displacement; no diffusion or long-term stability inference')
ax.legend(frameon=False);save(fig,'aimd-displacement')
print('Wrote aimd-temperature, aimd-energy, aimd-displacement as PNG and PDF')
