"""Run from the downloaded Al bundle root: python plot_epc.py.
Inputs stay in epc-q4/. Figures are written to figures/.
"""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=r/'epc-q4';out=r/'figures';out.mkdir(exist_ok=True)
a=np.loadtxt(d/'alpha2F.dat')
s=np.genfromtxt(d/'tc-scan.csv',delimiter=',',names=True)
colors=['#009e73','#d55e00','#cc79a7']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
def save(fig,name):
    fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(7.2,6),sharex=True)
for j,c in zip([0,3,9],colors):
    ax[0].plot(a[:,0],a[:,j+1],color=c,label=f"Electronic width {s['sigma_Ry'][j]:.3f} Ry")
    integ=np.zeros(len(a));f=np.zeros(len(a));f[1:]=2*a[1:,j+1]/a[1:,0]
    integ[1:]=np.cumsum(.5*(f[1:]+f[:-1])*np.diff(a[:,0]))
    ax[1].plot(a[:,0],integ,color=c)
ax[0].set(ylabel=r'$\alpha^2 F$');ax[0].legend(frameon=False)
ax[1].set(xlabel='Phonon frequency (THz)',ylabel=r'Cumulative $\lambda(\nu)$',xlim=(0,14))
fig.suptitle('fcc Al | 32³ electron grid, 4³ phonon grid\nUnconverged teaching calculation; Gaussian frequency width 0.12 THz',fontsize=11)
fig.tight_layout();save(fig,'eliashberg-a2f')
fig,ax=plt.subplots(1,2,figsize=(9,3.9))
ax[0].plot(s['sigma_Ry'],s['lambda_qsum'],'o-',color=colors[0],label='q-point sum')
ax[0].plot(s['sigma_Ry'],s['lambda_printed_spectrum_integral'],'x--',color=colors[1],label='Spectrum integral')
ax[0].plot(s['sigma_Ry'],s['lambda_matdyn'],'s:',color=colors[2],label='matdyn real-space interpolation')
ax[0].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'$\lambda$');ax[0].legend(frameon=False,fontsize=8)
ax[1].plot(s['sigma_Ry'],s['omega_log_K'],'o-',color=colors[0]);ax[1].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'$\omega_{\log}$ (K)')
fig.suptitle('Changing electronic width does not establish k/q convergence',fontsize=11);fig.tight_layout();save(fig,'epc-smearing')
mu=np.genfromtxt(d/'mu-sensitivity.csv',delimiter=',',names=True)
fig,ax=plt.subplots(1,2,figsize=(9,3.8))
ax[0].plot(s['sigma_Ry'],s['Tc_formula_K'],'o-',color=colors[0]);ax[0].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'Formula $T_c$ (K)',title=r'Assumed $\mu^*=0.10$')
ax[1].plot(mu['mu_star'],mu['Tc_K'],'o-',color=colors[1]);ax[1].set(xlabel=r'Assumed $\mu^*$',ylabel=r'Formula $T_c$ (K)',title='Electronic width 0.020 Ry')
fig.suptitle('Simplified Allen–Dynes expression (f₁=f₂=1); not a converged Al prediction',fontsize=11);fig.tight_layout();save(fig,'allen-dynes')
rows=list(csv.DictReader((d/'linewidth.csv').open()))
fig,ax=plt.subplots(2,1,figsize=(7.5,6),sharex=True)
for m,c in zip([1,2,3],colors):
    sel=[x for x in rows if int(x['mode'])==m and abs(float(x['sigma_Ry'])-.020)<1e-8]
    q=np.array([int(x['q_index']) for x in sel]);x=q+(m-2)*.22
    ax[0].bar(x,[float(v['gamma_GHz']) for v in sel],.20,color=c,label=f'Mode {m}')
    ax[1].bar(x,[float(v['lambda_mode']) for v in sel],.20,color=c)
ax[0].set(ylabel=r'QE linewidth $\gamma$ (GHz)');ax[0].legend(frameon=False,ncol=3)
ax[1].set(ylabel=r'Mode $\lambda_{q\nu}$',xlabel='Irreducible q-point index (file order; not a band path)',xticks=range(1,9))
fig.suptitle('fcc Al | electronic width 0.020 Ry\nRaw ph.x values; Γ acoustic residual is not an optical mode',fontsize=11)
fig.tight_layout();save(fig,'phonon-linewidth')
print('Wrote eliashberg-a2f, epc-smearing, allen-dynes, phonon-linewidth as PNG and PDF')
