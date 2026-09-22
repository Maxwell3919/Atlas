"""Block jackknife of helicity modulus; preserve finite-sampling limitations."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;O=R/'results';O.mkdir(exist_ok=True)

def write(name,rows):
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

def helicity(mean,n,temp):
    # mean refers to the columns in series.csv, including sweep at index 0.
    return .5*(mean[3]+mean[4]-(mean[7]-mean[5]**2+mean[8]-mean[6]**2)/temp)/(n*n)

def jackknife(data,n,temp,blocks=16):
    length=len(data)//blocks
    assert length>=10
    a=data[:length*blocks].reshape(blocks,length,-1).mean(axis=1)
    mean=a.mean(axis=0)
    raw=helicity(mean,n,temp)
    leave=np.array([helicity((blocks*mean-b)/(blocks-1),n,temp) for b in a])
    corrected=blocks*raw-(blocks-1)*leave.mean()
    error=np.sqrt((blocks-1)/blocks*np.sum((leave-leave.mean())**2))
    return float(corrected),float(error),float(raw),length

def tau_positive_window(values):
    a=values-values.mean();n=len(a)
    if np.dot(a,a)==0:return .5
    size=1<<(2*n-1).bit_length()
    f=np.fft.rfft(a,n=size)
    cov=np.fft.irfft(f*np.conj(f),n=size)[:n]/np.arange(n,0,-1)
    ac=cov/cov[0];tau=.5
    for k in range(1,n//4):
        if ac[k]<=0:break
        tau+=ac[k]
        if k>=6*tau:break
    return float(tau)

cases=[]
for family in ['base','extended']:
    for d in sorted((R/family).glob('L*')):
        if not (d/'run.json').exists():continue
        run=json.loads((d/'run.json').read_text());n=run['L'];temp=run['temperature_J']
        data=np.loadtxt(d/'series.csv',delimiter=',',skiprows=1)
        assert len(data)==run['measurements'] and np.isfinite(data).all()
        assert np.array_equal(data[:,0],np.arange(1,len(data)+1)*5)
        assert np.all((-2<=data[:,1])&(data[:,1]<=2)) and np.all((0<=data[:,2])&(data[:,2]<=1+1e-12))
        assert np.allclose(data[:,1],-(data[:,3]+data[:,4])/(n*n),rtol=0,atol=1e-12)
        assert np.allclose(data[:,7],data[:,5]**2,atol=1e-10) and np.allclose(data[:,8],data[:,6]**2,atol=1e-10)
        y,error,raw,blocklength=jackknife(data,n,temp)
        y8,e8,_,_=jackknife(data,n,temp,8);y32,e32,_,_=jackknife(data,n,temp,32)
        tauE=tau_positive_window(data[:,1]);tauI=tau_positive_window(data[:,7]+data[:,8]);tau=max(tauE,tauI)
        half=len(data)//2;first=jackknife(data[:half],n,temp,8);last=jackknife(data[half:],n,temp,8)
        case=dict(family=family,case=d.name,L=n,temperature_J=temp,seed=run['seed'],initialization=run['initialization'],production_sweeps=run['production_sweeps'],measurements=len(data),energy_per_spin=float(data[:,1].mean()),M2=float(data[:,2].mean()),vortex_abs_density=float(data[:,9].mean()),Y_J=y,Y_block_stderr_J=error,Y_raw_J=raw,Y_error_8_blocks_J=e8,Y_error_32_blocks_J=e32,block_sweeps=blocklength*5,tau_energy_sweeps=tauE*5,tau_current_squared_sweeps=tauI*5,block_over_max_tau=blocklength/tau,effective_samples_diagnostic=len(data)/(2*tau),first_half_Y_J=first[0],second_half_Y_J=last[0],half_shift_J=last[0]-first[0],half_shift_over_combined_block_error=abs(last[0]-first[0])/max(np.hypot(first[1],last[1]),1e-15),acceptance=run['production_acceptance'])
        cases.append(case)
write('cases.csv',cases)
groups=[]
for n in [8,16,24]:
    for temp in [.70,.80,.88,.92,1.00,1.10]:
        family='extended' if n in [16,24] and temp in [.88,.92] else 'base'
        rows=[c for c in cases if c['L']==n and c['temperature_J']==temp and c['family']==family]
        assert len(rows)==2
        y=np.array([c['Y_J'] for c in rows]);e=np.array([c['Y_block_stderr_J'] for c in rows])
        within=float(np.linalg.norm(e)/2);between=float(abs(y[0]-y[1])/2)
        groups.append(dict(L=n,temperature_J=temp,family=family,independent_seeds=2,Y_J=float(y.mean()),within_chain_stderr_J=within,between_seed_stderr_J=between,display_error_J=max(within,between),seed_difference_J=float(abs(y[0]-y[1])),seed_difference_over_combined_block_error=float(abs(y[0]-y[1])/max(np.linalg.norm(e),1e-15)),reference_2T_over_pi=float(2*temp/np.pi),min_block_over_tau=min(c['block_over_max_tau'] for c in rows),max_half_shift_over_combined_error=max(c['half_shift_over_combined_block_error'] for c in rows),vortex_abs_density=float(np.mean([c['vortex_abs_density'] for c in rows]))))
write('helicity.csv',groups)
extensions=[]
for c in cases:
    if c['family']!='extended':continue
    b=next(x for x in cases if x['family']=='base' and x['case']==c['case'])
    extensions.append(dict(L=c['L'],temperature_J=c['temperature_J'],seed=c['seed'],initialization=c['initialization'],base_sweeps=b['production_sweeps'],extended_sweeps=c['production_sweeps'],Y_base_J=b['Y_J'],base_error_J=b['Y_block_stderr_J'],Y_extended_J=c['Y_J'],extended_error_J=c['Y_block_stderr_J'],shift_J=c['Y_J']-b['Y_J'],note='nested same-chain extension, not an independent second estimate'))
write('extension-comparison.csv',extensions)
brackets=[]
for n in [8,16,24]:
    rows=sorted([g for g in groups if g['L']==n],key=lambda g:g['temperature_J'])
    for a,b in zip(rows,rows[1:]):
        if (a['Y_J']-a['reference_2T_over_pi'])*(b['Y_J']-b['reference_2T_over_pi'])<0:
            brackets.append(dict(L=n,lower_sampled_T=a['temperature_J'],upper_sampled_T=b['temperature_J'],meaning='finite-size mean-curve crossing bracket only; no extrapolation to thermodynamic limit'))
flags=[{'case':c['family']+'/'+c['case'],'block_over_tau':c['block_over_max_tau'],'half_shift_over_error':c['half_shift_over_combined_block_error']} for c in cases if c['block_over_max_tau']<10 or c['half_shift_over_combined_block_error']>3]
seed_flags=[g for g in groups if g['seed_difference_over_combined_block_error']>3]
summary=dict(model='periodic nearest-neighbour square-lattice classical XY; J=kB=1',helicity_definition='Y=(<Cx+Cy>-[Var(Ix)+Var(Iy)]/T)/(2 L^2)',uncertainty='16-block delete-one jackknife per chain; plotted error=max(within-chain combined error, half the two-seed difference); diagnostic error, not a calibrated confidence interval',autocorrelation='positive autocorrelation window capped at six tau; diagnostic only',case_count=len(cases),base_cases=sum(c['family']=='base' for c in cases),extended_cases=sum(c['family']=='extended' for c in cases),crossing_brackets=brackets,sampling_flags=flags,seed_disagreement_flags=seed_flags,conclusion='finite-size Monte Carlo workflow completed; thermodynamic-limit TBKT and material temperatures not estimated')
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('L  T/J    Y/J      display_error   seed_delta/error  minimum_block/tau')
for g in groups:print(f"{g['L']:2d} {g['temperature_J']:.2f}  {g['Y_J']:+.6f}   {g['display_error_J']:.6f}          {g['seed_difference_over_combined_block_error']:.2f}             {g['min_block_over_tau']:.1f}")
print('Mean-curve crossing brackets:',brackets)
print('Sampling flags:',len(flags),'seed disagreement flags:',len(seed_flags))
print('No thermodynamic-limit TBKT, no material J, no material superconducting temperature.')
