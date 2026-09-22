#!/usr/bin/env python3
"""Plot the k24/k32 comparison and the finite candidate hull from CSV only."""
from pathlib import Path
import argparse,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
LABELS={'al-fcc':'Al (fcc)','al3si-l12':'Al3Si (L12)','alsi-b2':'AlSi (B2)','alsi3-l12':'AlSi3 (L12)','si-diamond':'Si (diamond)'}
BLUE='#2563a6';ORANGE='#cf6d24';GRAY='#667085'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def save(fig,name):
    (ROOT/'plots').mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(ROOT/'plots'/f'{name}.{ext}',bbox_inches='tight')
    plt.close(fig);print(f'plots/{name}.png and plots/{name}.svg')
def comparison():
    rows=[r for r in read('comparison-k24-k32.csv') if r['case'] not in ['al-fcc','si-diamond']]
    fig,ax=plt.subplots(1,2,figsize=(11.5,4.2),layout='constrained')
    x=np.arange(len(rows));old=np.array([float(r['k24_formation_eV_atom']) for r in rows]);new=np.array([float(r['k32_formation_eV_atom']) for r in rows])
    ax[0].plot(x,old,'o',mfc='white',mec=GRAY,ms=9,label='24 x 24 x 24')
    ax[0].plot(x,new,'s',color=BLUE,ms=5,label='32 x 32 x 32')
    for xx,yy in zip(x,new):ax[0].annotate(f'{yy:.6f}',(xx,yy),xytext=(0,10),textcoords='offset points',ha='center')
    ax[0].set_xticks(x,[LABELS[r['case']] for r in rows]);ax[0].set_xlim(-.4,2.4);ax[0].set_ylim(0,.43)
    ax[0].set_ylabel('Formation energy (eV/atom)');ax[0].set_title('Matched elemental references at each mesh');ax[0].legend(loc='upper left',fontsize=9)
    delta=np.array([float(r['formation_change_meV_atom']) for r in rows])
    ax[1].axhspan(-1,1,color='#dbe9f3',alpha=.8,label='1 meV/atom comparison line')
    ax[1].bar(x,delta,color=[ORANGE if abs(v)>1 else BLUE for v in delta],width=.55)
    for xx,yy in zip(x,delta):ax[1].text(xx,yy+.065,f'{yy:+.6f}',ha='center',fontsize=9)
    ax[1].axhline(0,color=GRAY,lw=.7);ax[1].set_xticks(x,[LABELS[r['case']] for r in rows]);ax[1].set_ylim(-1.2,2.25)
    ax[1].set_ylabel('Formation-energy change (meV/atom)');ax[1].set_title('24 to 32: the comparison is still not passed');ax[1].legend(loc='lower left',fontsize=9)
    fig.suptitle('Fixed geometry, PBE, 80/640 Ry, cold smearing 0.005 Ry',fontsize=11)
    save(fig,'k32-comparison')
def hull():
    rows=sorted(read('formation-k32.csv'),key=lambda r:float(r['xSi']))
    fig,ax=plt.subplots(figsize=(8,4.7),layout='constrained')
    nodes=[r for r in rows if abs(float(r['above_hull_meV_atom']))<1e-7]
    ax.plot([float(r['xSi']) for r in nodes],[float(r['formation_eV_atom']) for r in nodes],color=BLUE,lw=2,label='Lower hull of these five candidates')
    for r in rows:
        x,y,h=float(r['xSi']),float(r['formation_eV_atom']),float(r['hull_eV_atom'])
        if y-h>1e-10:
            ax.vlines(x,h,y,color=ORANGE,lw=1,ls='--');ax.scatter([x],[y],marker='s',s=50,color=ORANGE,zorder=3)
            ax.annotate(LABELS[r['case']],(x,y),xytext=(0,10),textcoords='offset points',ha='center')
            ax.text(x+.02,y/2,f'{float(r["above_hull_meV_atom"]):.3f}\nmeV/atom',fontsize=8,va='center',color=GRAY)
        else:
            ax.scatter([x],[y],s=50,color=BLUE,zorder=3)
            ax.annotate(LABELS[r['case']],(x,y),xytext=(4 if x==0 else -4,10),textcoords='offset points',ha='left' if x==0 else 'right')
    ax.set_xlim(-.04,1.04);ax.set_ylim(-.025,.46);ax.set_xticks([0,.25,.5,.75,1])
    ax.set_xlabel('Si atomic fraction');ax.set_ylabel('Formation energy (eV/atom)')
    ax.set_title('32 x 32 x 32: same finite candidate set, same two hull vertices')
    ax.legend(fontsize=9,loc='upper left');ax.grid(axis='y',alpha=.15);save(fig,'hull-k32')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('figure',choices=['comparison','hull','all']);a=p.parse_args()
    if a.figure in ['comparison','all']:comparison()
    if a.figure in ['hull','all']:hull()
