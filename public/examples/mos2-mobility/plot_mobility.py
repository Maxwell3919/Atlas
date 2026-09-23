
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
summary=json.loads((R/'summary.json').read_text())
def rows(p):return list(csv.DictReader((R/p).open()))
cs=rows('cases.csv');by={x['case']:x for x in cs};mass=rows('mass-windows.csv');valley=rows('valley-bands.csv');pot=rows('potential-profiles.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
 for ext in ['png','svg']:fig.savefig(R/f'{name}.{ext}',dpi=220)
 plt.close(fig)
base=['minus010','minus005','zero','plus005','plus010'];eps=np.array([float(by[n]['epsilon']) for n in base]);Et=np.array([float(by[n]['etot_eV']) for n in base]);Ec=np.array([float(by[n]['K_CBM_vac_eV']) for n in base]);Ezero=float(by['zero']['etot_eV']);Czero=float(by['zero']['K_CBM_vac_eV'])
fig,ax=plt.subplots(1,2,figsize=(10,4.5),layout='constrained');xx=np.linspace(-.01,.01,200)
ax[0].plot(eps*100,(Et-Ezero)*1000,'o',color='#009e73',label='12 × 12 × 1; relaxed ions')
ax[0].plot(xx*100,np.polyval(np.polyfit(eps,Et-Ezero,2),xx)*1000,'-',color='#009e73')
ax[1].plot(eps*100,(Ec-Czero)*1000,'o',color='#009e73',label='Vacuum-aligned K-valley minimum')
ax[1].plot(xx*100,np.polyval(np.polyfit(eps,Ec-Czero,1),xx)*1000,'-',color='#009e73')
for fam,color,marker in [('k16','#d55e00','s'),('vacuum28','#6c54a3','^')]:
 names=[f'{fam}-{n}' for n in ['minus005','zero','plus005']]
 ee=np.array([float(by[n]['epsilon']) for n in names]);en=np.array([float(by[n]['etot_eV']) for n in names]);cb=np.array([float(by[n]['K_CBM_vac_eV']) for n in names])
 ax[0].plot(ee*100,(en-en[1])*1000,marker+'--',color=color,label=fam)
 ax[1].plot(ee*100,(cb-cb[1])*1000,marker+'--',color=color,label=fam)
for a in ax:a.set_xlabel('Longitudinal strain εxx (%)');a.grid(alpha=.2);a.legend(frameon=False,fontsize=8)
ax[0].set_ylabel('E(ε) − E(0) (meV / 3-atom cell)');ax[1].set_ylabel('Aligned conduction edge shift (meV)')
fig.suptitle('MoS₂ acoustic-DP inputs | fixed transverse lattice, relaxed internal coordinates')
save(fig,'deformation-fits')
fig,ax=plt.subplots(1,3,figsize=(13,4.2),layout='constrained')
for name,color in [('minus005','#009e73'),('zero','#3b3b3b'),('plus005','#d55e00')]:
 rr=[r for r in pot if r['case']==name];z=np.array([float(x['z_A']) for x in rr]);vv=np.array([float(x['potential_eV']) for x in rr]);offset=float(by[name]['vacuum_eV']);height=float(by[name]['height_A'])
 ax[0].plot(z,vv-offset,lw=.8,color=color,label=name)
 outer=(z<.25*height)|(z>.75*height)
 ax[1].plot(z[outer],(vv[outer]-offset)*1000,'.',ms=2,color=color,label=name)
ax[0].set_xlabel('z (Å)');ax[0].set_ylabel('Potential − vacuum (eV)');ax[0].legend(frameon=False,fontsize=8)
ax[1].set_xlabel('z (Å), vacuum regions');ax[1].set_ylabel('Vacuum plateau residual (meV)');ax[1].set_ylim(-.25,.10)
height0=float(by['zero']['height_A'])
for lo,hi in [(.10,.20),(.80,.90)]:ax[1].axvspan(lo*height0,hi*height0,color='#a9bdac',alpha=.18)
ax[1].text(.5,.97,'Shaded: vacuum reference windows',transform=ax[1].transAxes,ha='center',va='top',fontsize=8)
for key,label,color in [('Q1_minus_K_eV','Q direction 1','#009e73'),('Q2_minus_K_eV','Q direction 2','#d55e00'),('Q3_minus_K_eV','Q direction 3','#6c54a3'),('Gamma_minus_K_eV','Γ','#888')]:
 ax[2].plot(eps*100,[float(by[n][key]) for n in base],'o-',ms=3,label=label,color=color)
ax[2].axhline(0,color='#333',ls='--',lw=.6);ax[2].set_xlabel('εxx (%)');ax[2].set_ylabel('Valley energy − E(K) (eV)');ax[2].legend(frameon=False,fontsize=8)
fig.suptitle('Vacuum reference and sampled valley competition')
save(fig,'vacuum-and-valleys')
fig,ax=plt.subplots(1,3,figsize=(12,4),layout='constrained')
rr=[r for r in valley if r['case']=='zero' and r['kind']=='K-local'];center=min(rr,key=lambda r:abs(float(r['offsetx_invA']))+abs(float(r['offsety_invA'])));E0=float(center['conduction_eV'])
for a,axis,other in [(ax[0],'offsetx_invA','offsety_invA'),(ax[1],'offsety_invA','offsetx_invA')]:
 subset=sorted([r for r in rr if abs(float(r[other]))<1e-9],key=lambda r:float(r[axis]));k=np.array([float(r[axis]) for r in subset]);en=np.array([float(r['conduction_eV'])-E0 for r in subset]);a.plot(k,en*1000,'o',color='#009e73');kk=np.linspace(k.min(),k.max(),200);a.plot(kk,np.polyval(np.polyfit(k,en,2),kk)*1000,'-',color='#d55e00');a.set_xlabel('Δkx (Å⁻¹)' if axis.startswith('offsetx') else 'Δky (Å⁻¹)');a.set_ylabel('Conduction energy − E(K) (meV)');a.grid(alpha=.2)
mm=[r for r in mass if r['case']=='zero']
for key,label in [('mx_me','mx'),('my_me','my'),('md_me','DOS mass')]:ax[2].plot([float(r['window_invA']) for r in mm],[float(r[key]) for r in mm],'o-',label=label)
ax[2].set_xlabel('Quadratic-fit half width (Å⁻¹)');ax[2].set_ylabel('Effective mass / electron mass');ax[2].legend(frameon=False);ax[2].grid(alpha=.2)
fig.suptitle('K-valley curvature at the optimized zero-strain structure')
save(fig,'effective-mass-windows')
print('Wrote deformation-fits, vacuum-and-valleys, effective-mass-windows PNG/SVG')
print('Mobility publication status:',summary.get('mobility_status','alldeclaredmodelchecksmet'))
