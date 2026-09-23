
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'plots';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130,'savefig.dpi':300,'axes.titleweight':'bold'})
BLUE='#0072b2';ORANGE='#e69f00';GRAY='#667080'

def read(name):return np.genfromtxt(ROOT/name,delimiter=',',names=True,encoding='utf-8')
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig);print(OUT/(name+'.png'))
def clean(ax):ax.grid(alpha=.18);ax.set_axisbelow(True)
def convergence():
    rows=list(csv.DictReader((ROOT/'convergence.csv').open()))
    fig,axes=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    for ax,param,label in zip(axes,['ecutwfc','ecutrho','kmesh'],['Wavefunction cutoff (Ry)','Charge-density cutoff (Ry)','Uniform mesh n × n × n']):
        r=[x for x in rows if x['parameter']==param];x=[float(v['setting']) for v in r];y=[float(v['delta_meV_per_atom_vs_last']) for v in r]
        ax.plot(x,y,'o-',color=BLUE);ax.set_xlabel(label);ax.set_ylabel('ΔE vs last point (meV/atom)');clean(ax)
        if param=='kmesh':ax.set_yscale('symlog',linthresh=.1);ax.axhline(1,color=ORANGE,ls='--',label='Example comparison: 1 meV/atom');ax.legend(fontsize=8)
        ax.set_title({'ecutwfc':'Fixed 640 Ry, 8³ mesh','ecutrho':'Fixed 60 Ry, 8³ mesh','kmesh':'Fixed 60 / 640 Ry'}[param],fontsize=11)
    save(fig,'convergence')
def relax():
    r=read('relax/relaxation.csv');fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    axes[0].plot(r['scf_cycle'],(r['energy_Ry']-r['energy_Ry'][-1])*13605.693122994,'o-',color=BLUE)
    axes[0].set_ylabel('Energy above final structure (meV/cell)')
    axes[1].plot(r['scf_cycle'],r['total_force_Ry_per_Bohr'],'o-',color=ORANGE)
    axes[1].set_ylabel('QE total force (Ry/Bohr)');axes[1].annotate('Printed as 0.000000',xy=(r['scf_cycle'][-1],r['total_force_Ry_per_Bohr'][-1]),xytext=(-95,25),textcoords='offset points',fontsize=9,arrowprops={'arrowstyle':'->','color':GRAY})
    for ax in axes:ax.set_xlabel('SCF cycle along BFGS relaxation');ax.set_xticks(r['scf_cycle']);clean(ax)
    save(fig,'relax')
def gap():
    r=json.loads((ROOT/'gap-results.json').read_text());base=[x for x in r if x['directory'] in ['gap12','gap18-cg','gap24-cg']]
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    axes[0].plot([12,18,24],[x['gap_eV'] for x in base],'o-',color=BLUE);axes[0].set_xticks([12,18,24]);axes[0].set_xlabel('Uniform NSCF mesh n × n × n');axes[0].set_ylabel('Sampled indirect gap (eV)');axes[0].set_title('The sampled minimum need not vary monotonically',fontsize=10)
    for n,x in zip([12,18,24],base):axes[0].annotate(f"{max(x['cbm_k_tpiba']):.4f} × 2π/a",(n,x['gap_eV']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
    m=read('mass/longitudinal.csv');fit=json.loads((ROOT/'mass/mass-fits.json').read_text())[1]
    dense=next(x for x in r if x['directory']=='gap24-k12-cg');axes[1].plot(m['kx_tpiba'],m['band5_eV']-dense['vbm_eV'],color=BLUE)
    axes[1].scatter([fit['minimum_k_tpiba']],[fit['minimum_energy_eV']-dense['vbm_eV']],color=ORANGE,zorder=4)
    axes[0].margins(y=.20)
    axes[1].set_xlabel('kx (2π/a), ky = kz = 0');axes[1].set_ylabel('Conduction energy − VBM (eV)');axes[1].set_title('Local Γ–X valley refinement; 12³ parent density',fontsize=10)
    for ax in axes:clean(ax)
    save(fig,'band-gap')
def mass():
    r=read('mass/longitudinal.csv');fits=json.loads((ROOT/'mass/mass-fits.json').read_text());fit=fits[1]
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    dk=r['kx_inv_A']-fit['minimum_k_inv_A'];take=np.abs(dk)<.04
    axes[0].scatter(dk[take],(r['band5_eV'][take]-fit['minimum_energy_eV'])*1000,s=24,color=BLUE,label='Actual QE eigenvalues')
    q=np.linspace(-.035,.035,101);axes[0].plot(q,fit['quadratic_A_eVA2']*q*q*1000,color=ORANGE,label='Quadratic fit, ±0.02 Å⁻¹')
    axes[0].set_xlabel('kx − valley minimum (Å⁻¹)');axes[0].set_ylabel('Energy above minimum (meV)');axes[0].legend(fontsize=8)
    axes[1].plot([f['half_window_inv_A'] for f in fits],[f['mass_over_me'] for f in fits],'o-',color=BLUE)
    axes[1].set_xlabel('Fit half-window (Å⁻¹)');axes[1].set_ylabel('Longitudinal electron mass / me');axes[1].set_xticks([.01,.02,.03]);axes[1].ticklabel_format(useOffset=False,axis='y')
    for ax in axes:clean(ax)
    save(fig,'effective-mass')
def band3d():
    r=read('band3d/cube.csv');emin=r['band5_eV'].min();fig=plt.figure(figsize=(11,4.4),layout='constrained')
    for i,(key,value,xkey,ykey,title) in enumerate([('kz_tpiba',0.,'kx_tpiba','ky_tpiba','kz = 0 plane'),('kx_tpiba',.85,'ky_tpiba','kz_tpiba','kx = 0.85 × 2π/a plane')]):
        d=r[np.isclose(r[key],value)];xs=np.unique(d[xkey]);ys=np.unique(d[ykey]);X,Y=np.meshgrid(xs,ys,indexing='ij');Z=np.empty_like(X)
        for u,x in enumerate(xs):
            for v,y in enumerate(ys):Z[u,v]=(d['band5_eV'][np.isclose(d[xkey],x)&np.isclose(d[ykey],y)][0]-emin)*1000
        ax=fig.add_subplot(1,2,i+1,projection='3d');ax.plot_surface(X,Y,Z,cmap='viridis',linewidth=.2,edgecolor=(0,0,0,.15),antialiased=True)
        ax.set_xlabel(xkey.replace('_tpiba','')+' (2π/a)');ax.set_ylabel(ykey.replace('_tpiba','')+' (2π/a)');ax.set_zlabel('');ax.text2D(0.02, 0.91, 'E − sampled minimum (meV)', transform=ax.transAxes, fontsize=9);ax.set_title(title);ax.view_init(elev=25,azim=-125);ax.xaxis.set_major_locator(plt.MaxNLocator(4));ax.yaxis.set_major_locator(plt.MaxNLocator(4));ax.zaxis.set_major_locator(plt.MaxNLocator(4))
    fig.suptitle('Two cuts through an actual 11 × 9 × 9 local k-point cube',fontsize=12)
    save(fig,'band-3d')
def population():
    r=read('population-cg/lowdin.csv');fig,ax=plt.subplots(figsize=(6,4),layout='constrained');x=np.arange(len(r))
    ax.bar(x,r['s_electrons'],color=BLUE,label='s');ax.bar(x,r['p_electrons'],bottom=r['s_electrons'],color=ORANGE,label='p')
    for i,q in enumerate(r['total_electrons']):ax.text(i,q+.03,f'{q:.4f}',ha='center')
    ax.axhline(4,color=GRAY,ls='--',lw=1,label='4 valence electrons / Si');ax.set_xticks(x,['Si 1','Si 2']);ax.set_ylabel('Projected electrons');ax.set_ylim(0,4.5);ax.legend(ncol=3,fontsize=9,loc='lower center',bbox_to_anchor=(.5,1.));ax.set_title('Equivalent atoms; spilling = 0.0092',pad=38);save(fig,'population-analysis')
def fatband():
    r=read('bands-cg/fatband.csv');vbm=r['energy_eV'][r['iband']==4].max();fig,axes=plt.subplots(1,2,figsize=(12,4.6),sharey=True,layout='constrained')
    idx=[1,25,37,49,73,97,121];ticks=[r['path_distance_tpiba'][r['ik']==i][0] for i in idx];labels=['Γ','X','W','K','Γ','L','X']
    for ax,weight,color,title in zip(axes,['Si_s_weight','Si_p_weight'],[BLUE,ORANGE],['Si s projection','Si p projection']):
        for ib in range(1,9):
            q=r[r['iband']==ib];ax.plot(q['path_distance_tpiba'],q['energy_eV']-vbm,color='#b6bdc7',lw=.65,zorder=1);ax.scatter(q['path_distance_tpiba'],q['energy_eV']-vbm,s=34*q[weight],color=color,alpha=.75,edgecolors='none',zorder=2)
        for tick in ticks:ax.axvline(tick,color='#e0e3e8',lw=.65,zorder=0)
        ax.axhline(0,color=GRAY,ls='--',lw=.7);ax.set_xticks(ticks,labels);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,7);ax.set_title(title);ax.set_ylabel('Energy − VBM (eV)')
        handles=[ax.scatter([],[],s=34*w,color='#555555',edgecolors='none',label=f'{w:g}') for w in (.25,.5,1.)]
        ax.legend(handles=handles,title='Projection weight (point area)',ncol=3,
                  loc='lower left',bbox_to_anchor=(0,1.015),frameon=False,fontsize=8)
        ax.set_title('',loc='center')
        ax.set_title(title,loc='left',pad=55)
    save(fig,'fatband')
def bands():
    r=read('bands-cg/fatband.csv');vbm=r['energy_eV'][r['iband']==4].max();fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained');idx=[1,25,37,49,73,97,121];ticks=[r['path_distance_tpiba'][r['ik']==i][0] for i in idx]
    for ib in range(1,9):
        q=r[r['iband']==ib];ax.plot(q['path_distance_tpiba'],q['energy_eV']-vbm,color=BLUE,lw=1)
    for tick in ticks:ax.axvline(tick,color='#dce1e8',lw=.7)
    ax.axhline(0,color=GRAY,ls='--',lw=.7);ax.set_xticks(ticks,['Γ','X','W','K','Γ','L','X']);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,7);ax.set_ylabel('Energy − VBM (eV)');ax.set_title('Si, PBE, fixed example cell; no SOC');save(fig,'bands')
def dos():
    r=np.loadtxt(ROOT/'dos-cg/si.dos.dat');g=json.loads((ROOT/'gap-results.json').read_text());vbm=next(x['vbm_eV'] for x in g if x['directory']=='gap24-cg')
    fig,ax=plt.subplots(figsize=(7.5,3.7),layout='constrained');ax.plot(r[:,0]-vbm,r[:,1],color=BLUE);ax.fill_between(r[:,0]-vbm,r[:,1],alpha=.15,color=BLUE);ax.axvline(0,color=GRAY,ls='--');ax.set_xlim(-13,8);ax.set_xlabel('Energy − VBM (eV)');ax.set_ylabel('DOS (states/eV/cell)');ax.set_title('24³ NSCF mesh; Gaussian broadening 0.01 Ry');clean(ax);save(fig,'dos')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('figure',choices=['convergence','relax','gap','mass','band3d','population','fatband','bands','dos','all']);args=parser.parse_args()
    funcs={'convergence':convergence,'relax':relax,'gap':gap,'mass':mass,'band3d':band3d,'population':population,'fatband':fatband,'bands':bands,'dos':dos}
    for name,fun in funcs.items():
        if args.figure in [name,'all']:fun()
