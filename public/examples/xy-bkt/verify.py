"""Verify saved Monte Carlo snapshots and continuations without a new campaign."""
from pathlib import Path
import csv,json,math
import numpy as np
R=Path(__file__).resolve().parent
errors=[];vortex_errors=[];extensions=0;current_z=[]
for family in ['base','extended']:
    for d in sorted((R/family).glob('L*')):
        a=np.loadtxt(d/'final-angles.csv',delimiter=',');q=np.loadtxt(d/'final-vortices.csv',delimiter=',',dtype=int)
        n=len(a);energy=0;charge=np.zeros((n,n),int)
        wrap=lambda x:(x+math.pi)%(2*math.pi)-math.pi
        for i in range(n):
            for j in range(n):
                energy-=math.cos(a[(i+1)%n,j]-a[i,j])+math.cos(a[i,(j+1)%n]-a[i,j])
                edges=[a[(i+1)%n,j]-a[i,j],a[(i+1)%n,(j+1)%n]-a[(i+1)%n,j],a[i,(j+1)%n]-a[(i+1)%n,(j+1)%n],a[i,j]-a[i,(j+1)%n]]
                charge[i,j]=round(sum(wrap(x) for x in edges)/(2*math.pi))
        data=np.loadtxt(d/'series.csv',delimiter=',',skiprows=1)
        errors.append(abs(energy/(n*n)-data[-1,1]));vortex_errors.append(int(np.max(np.abs(charge-q))))
        assert charge.sum()==0
        blocks=data.reshape(16,len(data)//16,10).mean(axis=1)
        for k in [5,6]:
            se=np.std(blocks[:,k],ddof=1)/4
            current_z.append(abs(blocks[:,k].mean())/max(se,1e-15))
        if family=='extended':
            base=R/'base'/d.name;b=np.loadtxt(base/'series.csv',delimiter=',',skiprows=1)
            assert np.array_equal(data[:len(b)],b)
            assert np.array_equal(np.load(d/'initial-angles.npy'),np.load(base/'final-angles.npy'))
            extensions+=1
assert max(errors)<1e-12 and max(vortex_errors)==0 and extensions==8
# Seed reproducibility check of the saved first 100 warmup sweeps.
from mc import sweep,observe
d=R/'base/L8-T0.70-s2026093001'
meta=json.loads((d/'run.json').read_text());n=meta['L'];rng=np.random.default_rng(meta['seed'])
theta=rng.uniform(-np.pi,np.pi,(n,n));parity=np.indices((n,n)).sum(0)%2;masks=[parity==0,parity==1]
saved=np.loadtxt(d/'warmup.csv',delimiter=',',skiprows=1);prefix=[]
for step in range(1,101):
    sweep(theta,rng,meta['temperature_J'],masks)
    if step%50==0:obs,_=observe(theta);prefix.append([step,*obs])
replay_error=float(np.max(np.abs(np.array(prefix)-saved[:2])))
# Short replay only: permit floating-point reductions across BLAS/libm/CPU variants.
# Stored base/extension sample equality above remains exact.
assert np.allclose(np.array(prefix),saved[:2],rtol=1e-13,atol=1e-13), f'Short seed replay differs by {replay_error}'
receipt=dict(checked_snapshots=len(errors),max_snapshot_energy_error_per_spin=max(errors),max_snapshot_vorticity_error=max(vortex_errors),continuations_with_identical_original_samples=extensions,seed_warmup_replay_max_error=replay_error,max_current_mean_over_block_error=max(current_z),current_mean_note='zero-current symmetry check is a finite-sampling diagnostic, not a proof of winding-sector ergodicity')
(R/'results/independent-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
print('SAVED_DATA_CHECKS_PASSED; sampling and thermodynamic-limit convergence remain separate.')
