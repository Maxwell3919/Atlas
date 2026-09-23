#!/usr/bin/env python3
"""Render verified Al EPC data; run on the visualization machine.
Requires NumPy and Matplotlib. This script never runs QE.
Default: web PNG plus publication PDF, with separate font scales.
"""
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLUE,ORANGE,BLACK='#0072B2','#D55E00','#222222'

def read_rows(path):
    with path.open() as f:return list(csv.DictReader(f))

def number(rows,key):return np.array([float(r[key]) for r in rows])

def style(publication):
    fs=7 if publication else 12
    plt.rcParams.update({'font.family':'sans-serif',
        'font.sans-serif':['Arial','Helvetica','DejaVu Sans'],
        'font.size':fs,'axes.labelsize':fs,'xtick.labelsize':fs,'ytick.labelsize':fs,
        'legend.fontsize':fs,'axes.linewidth':.65,'lines.linewidth':1 if publication else 1.5,
        'xtick.major.width':.65,'ytick.major.width':.65,'xtick.major.size':2.5,'ytick.major.size':2.5,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
        'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
    return fs

def panel(ax,label,publication):
    ax.text(-.15,1.035,label,transform=ax.transAxes,fontweight='bold',
            fontsize=8 if publication else 14,color='black',va='bottom')
    ax.tick_params(direction='out')

def save(fig,out,name,publication):
    fig.savefig(out/(name+('.pdf' if publication else '.png')),
                dpi=240,bbox_inches=None if publication else 'tight',pad_inches=.12)
    plt.close(fig)

def draw(data,out,publication):
    style(publication)
    width,height=(183/25.4,3.35) if publication else (9,4.3)
    spec=read_rows(data/'spectra-and-integrals.csv')
    scan=read_rows(data/'tc-formula-scan.csv');mu=read_rows(data/'mu-star-scan.csv')
    report=json.loads((data/'tc-chain-checks.json').read_text())
    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    for route,color,line,label in [('lambda.x',BLUE,'-','Direct q sum + Gaussian'),
                                  ('matdyn.x',ORANGE,'--','q2r / matdyn interpolation')]:
        rows=[r for r in spec if r['route']==route and abs(float(r['sigma_Ry'])-.02)<1e-9]
        x=number(rows,'frequency_THz')
        ax[0].plot(x,number(rows,'a2F'),color=color,linestyle=line,label=label)
        ax[1].plot(x,number(rows,'cumulative_lambda'),color=color,linestyle=line,label=label)
    ax[0].set(xlabel='Frequency (THz)',ylabel=r'$\alpha^2F$')
    ax[1].set(xlabel='Frequency (THz)',ylabel=r'Cumulative $\lambda$')
    for i,a in enumerate(ax):a.set_xlim(0,14);panel(a,chr(97+i),publication)
    ax[1].legend(frameon=False,loc='lower right')
    save(fig,out,'a2f-route-check',publication)

    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    x=number(scan,'sigma_Ry')
    ax[0].plot(x,number(scan,'Tc_QE_replay_K'),'o-',color=BLACK,markersize=3,label='QE simplified')
    ax[0].plot(x,number(scan,'Tc_spectrum_simple_K'),'--',color=BLUE,label='Spectrum simplified')
    ax[0].plot(x,number(scan,'Tc_spectrum_full_AD_K'),'s:',color=ORANGE,markersize=3,label=r'Spectrum with $f_1f_2$')
    ax[0].set(xlabel='Electronic broadening (Ry)',ylabel=r'Formula $T_c$ (K)')
    x=number(mu,'mu_star')
    ax[1].plot(x,number(mu,'Tc_QE_rounded_input_K'),'o-',color=BLACK,markersize=3,label='QE rounded inputs')
    ax[1].plot(x,number(mu,'Tc_spectrum_simple_K'),'--',color=BLUE,label='Spectrum simplified')
    ax[1].plot(x,number(mu,'Tc_spectrum_full_AD_K'),'s:',color=ORANGE,markersize=3,label=r'Spectrum with $f_1f_2$')
    ax[1].set(xlabel=r'Assumed $\mu^*$',ylabel=r'Formula $T_c$ (K)')
    for i,a in enumerate(ax):a.set_ylim(bottom=0);panel(a,chr(97+i),publication)
    ax[0].legend(frameon=False)
    save(fig,out,'tc-formulas',publication)

    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    for sigma,color,line in [(.005,ORANGE,'--'),(.020,BLUE,'-')]:
        rows=[r for r in spec if r['route']=='matdyn.x' and abs(float(r['sigma_Ry'])-sigma)<1e-9]
        x=number(rows,'frequency_THz');y=number(rows,'a2F')
        ax[0].plot(x,y,color=color,linestyle=line,label=f'{sigma:.3f} Ry')
        # Same raw values; only the viewing limits change for the right panel.
        ax[1].plot(x,y,color=color,linestyle=line)
    ax[0].axhline(0,color=BLACK,linewidth=.6);ax[1].axhline(0,color=BLACK,linewidth=.6)
    ax[0].set(xlabel='Frequency (THz)',ylabel=r'Raw interpolated $\alpha^2F$')
    ax[1].set(xlabel='Frequency (THz)',ylabel=r'Raw $\alpha^2F$ near zero',ylim=(-.007,.015))
    for i,a in enumerate(ax):panel(a,chr(97+i),publication)
    ax[0].legend(frameon=False)
    save(fig,out,'a2f-negative-values',publication)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('data'))
    p.add_argument('--output',type=Path,default=Path('figures'))
    p.add_argument('--mode',choices=['both','web','publication'],default='both')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    for pub in ([False,True] if a.mode=='both' else [a.mode=='publication']):
        draw(a.data,a.output,pub)
    print('Raw values retained; no clipping, absolute-value repair, or extra spin factor.')
    print('Publication PDF: 7 pt text, 8 pt bold black panel labels, embedded type-42 fonts.')
    print('Scientific status: formula demonstration; material Tc convergence not established.')

if __name__=='__main__':main()
