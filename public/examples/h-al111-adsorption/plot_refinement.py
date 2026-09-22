#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
def main():
    energies=list(csv.DictReader((ROOT/'refined-adsorption-energy.csv').open()))
    forces=list(csv.DictReader((ROOT/'refined-force-check.csv').open()))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,axs=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    e=np.array([float(r['adsorption_eV_H']) for r in energies])
    axs[0].bar([0,1],e,width=.55,color=['#2463a7','#d17b3d'])
    axs[0].set_xticks([0,1],['12×12×1\nrelaxed','16×16×1\nfixed k12 geometry'])
    axs[0].set_ylabel('Adsorption energy (eV/H)');axs[0].axhline(0,color='#657081',lw=.7)
    axs[0].set_title('Matched clean / adsorbed slabs; same H₂ reference')
    for i,v in enumerate(e):axs[0].annotate(f'{v:.6f}',(i,v),xytext=(0,6 if v>=0 else -14),textcoords='offset points',ha='center')
    axs[0].text(.04,.96,f'Change: {(e[1]-e[0])*1000:+.3f} meV/H\nEnergy comparison line: 10 meV/H',transform=axs[0].transAxes,va='top',fontsize=9)
    if np.all(e>0):axs[0].set_ylim(0,max(e)*1.4)
    f12=np.array([float(r['max_force_k12_Ry_Bohr']) for r in forces]);f16=np.array([float(r['max_force_k16_Ry_Bohr']) for r in forces])
    x=np.arange(len(forces));w=.32
    axs[1].bar(x-w/2,f12,w,label='12×12×1 relaxed',color='#2463a7')
    axs[1].bar(x+w/2,f16,w,label='16×16×1 fixed geometry',color='#d17b3d')
    axs[1].axhline(2e-4,color='#8e2e2e',ls='--',lw=1,label='2×10⁻⁴ Ry/Bohr force condition')
    axs[1].set_xticks(x,['Clean slab','Adsorbed slab']);axs[1].set_ylabel('Largest absolute force component (Ry/Bohr)')
    axs[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    axs[1].set_ylim(0,max(2e-4,float(f12.max()),float(f16.max()))*1.5)
    axs[1].set_title('Energy agreement is checked together with forces')
    axs[1].legend(fontsize=8,loc='upper left');axs[1].grid(axis='y',alpha=.12)
    (ROOT/'plots').mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(ROOT/'plots'/f'k12-k16-refinement.{ext}',bbox_inches='tight')
    plt.close(fig);print('plots/k12-k16-refinement.png and plots/k12-k16-refinement.svg')
if __name__=='__main__':main()
