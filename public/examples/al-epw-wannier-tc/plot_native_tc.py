"""Plot the native EPW Wannier spectrum and its independent Tc scan."""
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import atlas_plot_style

ap=argparse.ArgumentParser()
ap.add_argument('--data',type=Path,default=Path('.'))
ap.add_argument('--out',type=Path,default=Path('figures'))
args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
atlas_plot_style.install()
spec=list(csv.DictReader((args.data/'source-spectrum.csv').open()))
linear=list(csv.DictReader((args.data/'linear.csv').open()))
w=np.array([float(r['omega_meV']) for r in spec])
a=np.array([float(r['alpha2F']) for r in spec])
lam=np.array([float(r['lambda_cumulative_native']) for r in spec])
assert len(w)==500 and (np.diff(w)>0).all() and w[0]>0 and (a>=0).all()
points={}
for r in linear:
    if r['complete']!='True' or r['solver']!='power':continue
    assert float(r['muc'])==.1 and float(r['requested_wscut_eV'])==.1
    t,y=float(r['T_K']),float(r['max_eigenvalue'])
    if t in points:assert abs(y-points[t])<1e-7
    points[t]=y
p=np.array(sorted(points.items()))
brackets=[(x1,x2) for (x1,y1),(x2,y2) in zip(p,p[1:]) if y1>1 and y2<1]
assert len(brackets)==1,brackets
lo,hi=brackets[0]
fig,ax=plt.subplots(1,2,figsize=(10,4.3))
fig.subplots_adjust(left=.09,right=.97,bottom=.20,top=.78,wspace=.33)
fig.suptitle('Native EPW spectrum and its linearized transition',x=.09,ha='left',y=.98,fontsize=12)
fig.text(.09,.88,r'Al: coarse $k=12^3$, $q=4^3$; fine $k=24^3$, $q=12^3$  |  $\mu^*=0.10$, $w_{\rm scut}=0.10$ eV',fontsize=10)
blue,orange='#0072b2','#d55e00'
ax[0].plot(w,a,color=blue,lw=1.1,label=r'$\alpha^2F(\omega)$')
ax[0].plot(w,lam,color=orange,lw=1.1,ls='--',label=r'Cumulative $\lambda(\omega)$')
ax[0].set(xlabel='Phonon energy (meV)',ylabel=r'$\alpha^2F(\omega)$, $\lambda(\omega)$',xlim=(0,w[-1]),ylim=(0,max(max(a),max(lam))*1.25))
ax[0].legend(frameon=False,loc='upper left',fontsize=9)
ax[0].text(.98,.93,fr'$\lambda_{{spectrum}}={lam[-1]:.6f}$',transform=ax[0].transAxes,ha='right',va='top',fontsize=9)
ax[1].plot(p[:,0],p[:,1],color=blue,lw=1.1,marker='o',mfc='white',ms=4,mew=.85)
ax[1].axhline(1,color='#333333',ls='--',lw=.8)
ax[1].axvspan(lo,hi,color='#cccccc',alpha=.65,lw=0)
ax[1].set(xlabel='Temperature (K)',ylabel=r'Leading kernel eigenvalue $\eta$')
ax[1].margins(x=.08,y=.2)
ax[1].text(.96,.94,f'$T_c$: {lo:.2f}–{hi:.2f} K',transform=ax[1].transAxes,ha='right',va='top')
fig.text(.09,.025,'One finite-grid teaching calculation; interpolation, smearing and cutoff convergence remain separate checks.',fontsize=9)
fig.savefig(args.out/'al-native-spectrum-tc.png');plt.close(fig)
result={'spectrum_points':len(w),'spectrum_lambda_native_cumulative':float(lam[-1]),
        'linear_points':len(p),'Tc_bracket_K':[float(lo),float(hi)],'muc':.1,'requested_wscut_eV':.1}
(args.out/'native-plot-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
