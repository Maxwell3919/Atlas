from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

# Run beside the CSV/JSON/NPZ outputs. No MACE, ASE or phonopy import is needed.
root=Path(__file__).resolve().parent
summary=json.loads((root/'fit-summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'svg.fonttype':'none','savefig.dpi':200})
colors={'harmonic':'#5d626a','effective':'#2469a8','small':'#ca802c','validation':'#3a8660'}
def bands(name): return np.genfromtxt(root/(name+'-bands.csv'),delimiter=',',skip_header=1)
def decorate(ax):
    ticks=summary['fits'][-1]['bands']['boundaries_inv_A']
    for x in ticks:ax.axvline(x,color='#dddddd',lw=.6,zorder=0)
    ax.axhline(0,color='#bbbbbb',lw=.7,zorder=0)
    ax.set_xticks(ticks,['Γ','X','W','K','Γ','L'])
    ax.set_xlim(ticks[0],ticks[-1])
    ax.set_xlabel('Wave-vector path')
base=bands('harmonic-0.005'); other=bands('harmonic-0.01'); fit=bands('effective-60')
fig,axes=plt.subplots(1,2,figsize=(10.4,4),layout='constrained')
for seg in range(5):
    rows=base[:,0]==seg
    for branch in range(5,11):
        axes[0].plot(base[rows,1],1000*(other[rows,branch]-base[rows,branch]),color=colors['harmonic'],lw=1)
        axes[1].plot(base[rows,1],base[rows,branch],color=colors['harmonic'],lw=1.1,ls='--')
        axes[1].plot(fit[rows,1],fit[rows,branch],color=colors['effective'],lw=1.15)
for ax in axes:decorate(ax)
axes[0].set_title('Small-displacement amplitude check')
axes[0].set_ylabel('Frequency(0.01 Å) − frequency(0.005 Å) [GHz]')
axes[1].set_title('One finite-temperature fitting demonstration')
axes[1].set_ylabel('Frequency [THz]')
axes[1].plot([],[],color=colors['harmonic'],ls='--',label='Small displacement: 0.005 Å')
axes[1].plot([],[],color=colors['effective'],label='Effective FCs: 60 training frames')
axes[1].legend(frameon=False,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.18))
fig.savefig(root/'effective-phonons.svg');fig.savefig(root/'effective-phonons.png');plt.close(fig)

fig,axes=plt.subplots(2,2,figsize=(10.4,7.2),layout='constrained')
learning=np.genfromtxt(root/'learning-curve.csv',delimiter=',',names=True)
for field,label,color in [('train_RMSE_meV_A','Training block',colors['harmonic']),
                         ('heldout_block_RMSE_meV_A','Held-out later block',colors['small']),
                         ('independent_RMSE_meV_A','Independent velocity seed',colors['validation'])]:
    axes[0,0].plot(learning['training_snapshots'],learning[field],'-o',label=label,color=color,ms=4)
axes[0,0].set(xlabel='Training snapshots',ylabel='Force RMSE [meV/Å]',title='Sample-count comparison')
axes[0,0].set_xticks([20,40,60]);axes[0,0].legend(frameon=False,fontsize=8)
ind=np.load(root/'independent-dataset.npz')
pred=np.load(root/'effective-60-independent-prediction.npy')
true=ind['forces'].reshape(-1);estimate=pred.reshape(-1)
lo=min(true.min(),estimate.min());hi=max(true.max(),estimate.max())
axes[0,1].scatter(true,estimate,s=3,alpha=.22,color=colors['effective'],rasterized=True)
axes[0,1].plot([lo,hi],[lo,hi],color='#333333',lw=.8)
axes[0,1].set(xlabel='MACE force component [eV/Å]',ylabel='Effective-model force [eV/Å]',title='Independent trajectory, 60-frame fit')
axes[0,1].text(.04,.94,f"RMSE = {summary['fits'][-1]['independent']['rmse_meV_A']:.2f} meV/Å",transform=axes[0,1].transAxes,va='top')
source=np.load(root/'mapped-dataset.npz')
axes[1,0].plot(source['source_time_ps'],source['source_temperature_K'],color=colors['harmonic'],lw=1,label='Source trajectory')
axes[1,0].plot(ind['time_ps'],ind['temperature_K'],color=colors['validation'],lw=1,label='Independent trajectory')
axes[1,0].axvspan(.005,.300,color=colors['effective'],alpha=.09,label='60-frame training interval')
axes[1,0].axvspan(.400,.500,color=colors['small'],alpha=.12,label='Held-out source interval')
axes[1,0].set(xlabel='Production time [ps]',ylabel='Instantaneous temperature [K]',title='Actual short-trajectory temperatures')
axes[1,0].legend(frameon=False,fontsize=7,loc='best')
short=bands('effective-40')
for seg in range(5):
    rows=fit[:,0]==seg
    for branch in range(5,11):axes[1,1].plot(fit[rows,1],1000*(fit[rows,branch]-short[rows,branch]),color=colors['effective'],lw=1)
decorate(axes[1,1]);axes[1,1].set_title('Sensitivity to 40 versus 60 training frames')
axes[1,1].set_ylabel('Frequency(60) − frequency(40) [GHz]')
fig.savefig(root/'fit-validation.svg');fig.savefig(root/'fit-validation.png');plt.close(fig)
print('Created effective-phonons.svg/png and fit-validation.svg/png')

