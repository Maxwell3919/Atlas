#!/usr/bin/env python3
"""Plot the actual tables produced by analyse_alsi.py; no QE installation needed."""
from pathlib import Path
import argparse,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
BLUE='#2463a7';ORANGE='#d56925';GRAY='#657081'
LABELS={'al-fcc':'Al (fcc)','al3si-l12':'Al₃Si (L1₂)','alsi-b2':'AlSi (B2)','alsi3-l12':'AlSi₃ (L1₂)','si-diamond':'Si (diamond)'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def save(fig,name):
    (ROOT/'plots').mkdir(exist_ok=True)
    for suffix in ['png','svg']:fig.savefig(ROOT/'plots'/f'{name}.{suffix}',bbox_inches='tight')
    plt.close(fig)
    print(f'plots/{name}.png and plots/{name}.svg')
def formation():
    rows=[r for r in read('formation-energy.csv') if r['case'] not in ['al-fcc','si-diamond']]
    checks=read('numerical-checks.csv')
    fig,axes=plt.subplots(1,2,figsize=(12,4.2),layout='constrained',gridspec_kw={'width_ratios':[1,1.8]})
    x=np.arange(len(rows));y=np.array([float(r['formation_eV_atom']) for r in rows])
    axes[0].bar(x,y,color=BLUE,width=.64)
    for xx,yy in zip(x,y):axes[0].text(xx,yy+max(y)*.025,f'{yy:.3f}',ha='center')
    axes[0].set_xticks(x,[LABELS[r['case']].replace(' ','\n',1) for r in rows]);axes[0].set_ylim(0,max(y)*1.2)
    axes[0].set_ylabel('Formation energy (eV/atom)');axes[0].set_title('Same reference energies and protocol')
    transitions=[('k12','k16','k:12→16'),('k16','k20','k:16→20'),('k20','sigma005','σ:0.01→0.005'),('sigma005','cutoff80','cutoff:60→80'),('cutoff80','k24','k:20→24')]
    colors=[BLUE,ORANGE,'#328d77']
    for case,col in zip([r['case'] for r in rows],colors):
        yy=[float(next(c for c in checks if c['case']==case and c['from_protocol']==a and c['to_protocol']==b)['formation_change_meV_atom']) for a,b,_ in transitions]
        axes[1].plot(np.arange(len(transitions)),yy,'o-',label=LABELS[case],color=col,ms=5)
    axes[1].axhspan(-1,1,color='#dde8f0',alpha=.7,label='±1 meV/atom comparison line')
    axes[1].axhline(0,color=GRAY,lw=.7);axes[1].set_xticks(np.arange(len(transitions)),[x[2] for x in transitions],rotation=25,ha='right')
    axes[1].set_ylabel('Change in formation energy (meV/atom)');axes[1].set_title('Controlled numerical checks at fixed geometry')
    axes[1].legend(fontsize=8,loc='best');axes[1].grid(axis='y',alpha=.15)
    save(fig,'formation-energy')
def hull():
    rows=sorted(read('formation-energy.csv'),key=lambda r:float(r['xSi']))
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    x=np.array([float(r['xSi']) for r in rows]);y=np.array([float(r['formation_eV_atom']) for r in rows]);h=np.array([float(r['hull_eV_atom']) for r in rows])
    nodes=[r for r in rows if abs(float(r['above_hull_eV_atom']))<1e-10]
    ax.plot([float(r['xSi']) for r in nodes],[float(r['formation_eV_atom']) for r in nodes],color=BLUE,lw=2,label='Lower hull of these five candidates')
    for r,xx,yy,hh in zip(rows,x,y,h):
        if yy-hh>1e-10:
            ax.vlines(xx,hh,yy,color=ORANGE,ls='--',lw=1)
            ax.scatter([xx],[yy],s=55,marker='s',color=ORANGE,zorder=3)
            ax.annotate(LABELS[r['case']],(xx,yy),xytext=(0,10),textcoords='offset points',ha='center')
            ax.text(xx+.018,(yy+hh)/2,f'{1000*(yy-hh):.1f}\nmeV/atom',rotation=0,va='center',fontsize=8,color=GRAY)
        else:
            ax.scatter([xx],[yy],s=58,color=BLUE,zorder=3)
            ax.annotate(LABELS[r['case']],(xx,yy),xytext=(4,10) if xx==0 else (-4,10),textcoords='offset points',ha='left' if xx==0 else 'right')
    ax.set_xlim(-.04,1.04);ax.set_ylim(-.025,max(y)*1.23);ax.set_xticks([0,.25,.5,.75,1]);ax.set_xlabel('Si atomic fraction x = N(Si) / [N(Al) + N(Si)]')
    ax.set_ylabel('Formation energy (eV/atom)');ax.set_title('Al–Si: a finite set of constrained cubic prototypes')
    ax.legend(fontsize=9,loc='upper right');ax.grid(axis='y',alpha=.12)
    save(fig,'convex-hull')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('figure',choices=['formation','hull','all']);a=p.parse_args()
    if a.figure in ['formation','all']:formation()
    if a.figure in ['hull','all']:hull()
