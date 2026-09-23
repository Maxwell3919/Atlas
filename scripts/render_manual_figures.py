"""Rebuild static teaching figures from public/data/teaching-extracts.json.

Requires numpy and matplotlib. No DFT calculation is performed.
Charts show archived outputs and their limitations, not accepted predictions.
"""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'public/data/teaching-extracts.json').read_text())
OUT=ROOT/'public/figures'; OUT.mkdir(exist_ok=True)
BLUE='#0072b2'; ORANGE='#d55e00'; INK='#292b30'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','axes.prop_cycle':plt.cycler(color=[BLUE,ORANGE])})
def finish(fig,name,title,subtitle):
 fig.suptitle(title,x=.10,y=.98,ha='left',fontsize=15,fontweight='bold')
 fig.text(.10,.92,subtitle,ha='left',fontsize=10,color='#575b62')
 fig.tight_layout(rect=(0,0,1,.87))
 for ax in fig.axes: ax.grid(axis='y',alpha=.16)
 for ext in ['svg','png']: fig.savefig(OUT/f'{name}.{ext}',dpi=160,facecolor='white')
 plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.6));f=np.array(D['relax_force'])
ax.semilogy(np.arange(1,len(f)+1),f,'o-',markersize=3)
ax.set(xlabel='Force report index (not an accepted-step counter)',ylabel='Total force (Ry/Bohr)')
finish(fig,'relax-force','HfCl2/PbO2: force history','Original vc-relax output; BFGS reported non-convergence.')

fig,ax=plt.subplots(figsize=(8,4.6));a=D['scf_accuracy'];ax.semilogy(range(1,len(a)+1),a,'o-',markersize=3)
ax.axhline(1e-12,color=INK,ls='--',label='Input conv_thr = 1e-12 Ry');ax.legend(frameon=False)
ax.set(xlabel='SCF accuracy report index',ylabel='Estimated SCF accuracy (Ry)')
finish(fig,'scf-accuracy','ZrCl2/Sc2C: electronic SCF iterations','Dense k = 64 x 64 x 1; archived QE 7.1 output.')

fig,ax=plt.subplots(figsize=(8,5));a=np.array(D['bands'])
cuts=np.r_[0,np.where(np.diff(a[:,0])<0)[0]+1,len(a)]
for i,j in zip(cuts[:-1],cuts[1:]):ax.plot(a[i:j,0],a[i:j,1]-.0483,color=BLUE,lw=.8)
ticks=[0,.5774,.9107,1.5774]
for x in ticks:ax.axvline(x,color='#999999',lw=.6)
ax.axhline(0,color=INK,ls='--',lw=.9);ax.set(xticks=ticks,xticklabels=['Γ','M','K','Γ'],xlim=(0,1.5774),ylim=(-4,4),ylabel='E - E_F (eV)')
finish(fig,'bands','HfCl2/PbO2: bands without SOC','Candidate geometry; SCF E_F = 0.0483 eV. Input .gnu energies are already eV.')

fig,ax=plt.subplots(figsize=(8,4.8));a=np.array(D['dos']);b=np.array(D['pdos_total'])
ax.plot(a[:,0]-.05,a[:,1],label='dos.x total DOS');ax.plot(b[:,0]-.05,b[:,2],ls='--',label='projwfc.x summed PDOS')
ax.axvline(0,color=INK,ls=':',lw=1);ax.set(xlim=(-3,3),ylim=(0,None),xlabel='E - E_F (eV)',ylabel='DOS (states/eV/cell)');ax.legend(frameon=False)
finish(fig,'dos','HfCl2/PbO2: DOS and projected DOS','Without SOC; E_F = 0.050 eV. One grid and broadening, no convergence claim.')

fig,ax=plt.subplots(figsize=(8,4.8));a=np.array(D['potential']);ax.plot(a[:,0],a[:,1]);ax.axhline(-2.4741,color=ORANGE,ls='--',label='E_F = -2.4741 eV');ax.legend(frameon=False)
ax.set(xlabel='z (Å)',ylabel='Planar-averaged potential (eV)',xlim=(0,a[-1,0]))
finish(fig,'potential','SnSe2: saved planar-average profile','Legacy LVTOT calculation; vacuum-window and potential-choice checks remain open.')

fig,ax=plt.subplots(figsize=(8,4.8));a=np.array(D['phonon']);ax.plot(a[:,0],a[:,1:],color=BLUE,lw=.7);ax.axhline(0,color=INK,lw=.7)
ticks=[a[0,0],a[50,0],a[100,0],a[-1,0]]
for x in ticks:ax.axvline(x,color='#999999',lw=.6)
ax.set(xticks=ticks,xticklabels=['Γ','M','K','Γ'],xlim=(ticks[0],ticks[-1]),ylabel='Frequency (cm$^{-1}$)')
finish(fig,'phonon','ZrCl2/Sc2C: interpolated phonon path','q mesh 8 x 8 x 1; ASR applied in post-processing. A path is not the whole BZ.')

fig,(ax,bx)=plt.subplots(2,1,figsize=(8,7),sharex=True)
for grid,style,color in [(64,'-',BLUE),(96,'--',ORANGE)]:
 a=np.array(D[f'lambda{grid}']);t=np.array(D[f'tc{grid}']);ax.plot(a[:,0],a[:,1],style,color=color,label=f'Dense k = {grid} x {grid} x 1');bx.plot(a[:,0],t[:,2],style,color=color)
ax.set_ylabel('Electron-phonon coupling λ');ax.legend(frameon=False);bx.set(xlabel='Electronic broadening (Ry)',ylabel='Formula estimate T_c (K)')
finish(fig,'epc-broadening','ZrCl2/Sc2C: broadening dependence','Both q meshes are 8 x 8 x 1; μ* = 0.1. These are not converged T_c predictions.')
