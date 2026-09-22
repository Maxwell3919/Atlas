#!/usr/bin/env python3
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
def save(fig,name):
    (ROOT/'plots').mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(ROOT/'plots'/f'{name}.{ext}',bbox_inches='tight')
    plt.close(fig);print(f'plots/{name}.png and plots/{name}.svg')
def main():
    data=json.loads((ROOT/'structures.json').read_text())
    fig,axs=plt.subplots(1,3,figsize=(10,5.3),layout='constrained')
    for ax,name,title in zip(axs,['clean-slab','adsorbed','h2-10A'],['Clean Al slab','H on both surfaces','Gas H₂ reference']):
        d=data[name];p=np.array(d['positions_A']);cell=np.array(d['cell_A'])
        for i,(sym,pos) in enumerate(zip(d['symbols'],p)):
            col='#3275ac' if sym=='Al' else '#e3994c'
            ax.scatter(pos[0],pos[2],s=260 if sym=='Al' else 105,c=col,edgecolors='white',linewidths=1.2,zorder=3)
            ax.annotate(sym,(pos[0],pos[2]),xytext=(8,0),textcoords='offset points',va='center',fontsize=9)
        if name=='h2-10A':ax.plot(p[:,0],p[:,2],color='#9a774e',lw=3,zorder=1)
        if name=='adsorbed':
            for a,b in [(0,3),(2,4)]:ax.plot(p[[a,b],0],p[[a,b],2],color='#9a774e',lw=2,zorder=1)
        if name!='h2-10A':
            ax.axhline(p[1,2],color='#657081',ls=':',lw=.8)
            ax.text(.04,.06,'Middle Al fixed\n1 × 1 surface cell',transform=ax.transAxes,fontsize=9)
            ax.set_xlim(-.7,cell[0,0]+1)
        else:ax.set_xlim(3.5,6.5)
        ax.set_ylim(0,cell[2,2]);ax.set_xlabel('x (Å), projection along y');ax.set_ylabel('z (Å)')
        ax.set_title(title);ax.grid(axis='y',alpha=.12)
    fig.suptitle('Actual relaxed coordinates; each panel shows its own periodic cell')
    save(fig,'structures')
    rows=list(csv.DictReader((ROOT/'adsorption-energy.csv').open()))
    fig,axs=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
    labels=['6×6×1\n15 Å initial gap','8×8×1\nfixed geometry','20 Å initial gap\nfixed geometry','12 Å H₂ box\nfixed bond']
    values=[float(r['adsorption_eV_H']) for r in rows]
    axs[0].bar(range(4),values,color=['#2463a7','#5195ba','#5195ba','#5195ba'],width=.6)
    axs[0].axhline(0,color='#657081',lw=.8);axs[0].set_xticks(range(4),labels,fontsize=8)
    axs[0].set_ylabel('Adsorption energy (eV/H)');axs[0].set_title('Gas H₂ reference; two adsorbed H per cell')
    for i,v in enumerate(values):axs[0].annotate(f'{v:.4f}',(i,v),xytext=(0,5 if v>=0 else -13),textcoords='offset points',ha='center',fontsize=8)
    delta=[float(r['change_from_baseline_meV_H']) for r in rows[1:]]
    axs[1].axhspan(-10,10,color='#dde8f0',alpha=.8,label='±10 meV/H comparison line')
    axs[1].plot(range(3),delta,'o',ms=7,color='#cc7033');axs[1].axhline(0,color='#657081',lw=.8)
    axs[1].set_xticks(range(3),['k: 6→8','vacuum: +5 Å','H₂ box: 10→12 Å'])
    axs[1].set_ylabel('Change from baseline (meV/H)');axs[1].set_title('One numerical change at a time')
    axs[1].legend(fontsize=8);axs[1].grid(axis='y',alpha=.15)
    save(fig,'adsorption-checks')
if __name__=='__main__':main()
