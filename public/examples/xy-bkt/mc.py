"""Nearest-neighbour classical XY Monte Carlo on even periodic square lattices.

J=k_B=1. Checkerboard Metropolis, fixed symmetric angle proposal.
One sweep attempts every spin once. NumPy only; no DFT/material parameters.
"""
from pathlib import Path
import argparse
import csv
import json
import time
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

ROOT=Path(__file__).resolve().parent

def energy(theta):
    return -float(np.sum(np.cos(np.roll(theta,-1,axis=0)-theta)+np.cos(np.roll(theta,-1,axis=1)-theta)))

def sweep(theta,rng,temperature,masks):
    accepted=0
    for mask in masks:
        c=np.cos(theta);s=np.sin(theta)
        hc=np.roll(c,1,0)+np.roll(c,-1,0)+np.roll(c,1,1)+np.roll(c,-1,1)
        hs=np.roll(s,1,0)+np.roll(s,-1,0)+np.roll(s,1,1)+np.roll(s,-1,1)
        proposal=theta+rng.uniform(-np.pi/2,np.pi/2,theta.shape)
        delta=-(np.cos(proposal)-c)*hc-(np.sin(proposal)-s)*hs
        take=mask&(rng.random(theta.shape)<np.exp(-np.maximum(delta,0)/temperature))
        theta[take]=(proposal[take]+np.pi)%(2*np.pi)-np.pi
        accepted+=int(np.count_nonzero(take))
    return accepted/theta.size

def observe(theta):
    dx=np.roll(theta,-1,axis=0)-theta
    dy=np.roll(theta,-1,axis=1)-theta
    cx=float(np.cos(dx).sum());cy=float(np.cos(dy).sum())
    ix=float(np.sin(dx).sum());iy=float(np.sin(dy).sum())
    magnetization=abs(np.exp(1j*theta).mean())**2
    wrap=lambda x:(x+np.pi)%(2*np.pi)-np.pi
    vortex=np.rint((wrap(dx)+np.roll(wrap(dy),-1,axis=0)-np.roll(wrap(dx),-1,axis=1)-wrap(dy))/(2*np.pi)).astype(int)
    assert int(vortex.sum())==0
    return [-(cx+cy)/theta.size,float(magnetization),cx,cy,ix,iy,ix*ix,iy*iy,float(np.abs(vortex).mean())],vortex

def self_check():
    n=8;theta=np.zeros((n,n));assert energy(theta)==-2*n*n
    rng=np.random.default_rng(9135701);theta=rng.uniform(-np.pi,np.pi,(n,n))
    errors=[]
    for _ in range(25):
        i,j=map(int,rng.integers(0,n,size=2));old=theta[i,j];new=rng.uniform(-np.pi,np.pi)
        neighbours=[theta[(i+1)%n,j],theta[(i-1)%n,j],theta[i,(j+1)%n],theta[i,(j-1)%n]]
        local=-sum(np.cos(new-v)-np.cos(old-v) for v in neighbours)
        before=energy(theta);theta[i,j]=new;actual=energy(theta)-before
        errors.append(abs(local-actual))
    assert max(errors)<1e-12
    values,vort=observe(theta)
    assert abs(values[0]*n*n-energy(theta))<1e-12
    result={'ordered_energy_per_spin':-2.0,'random_local_delta_energy_max_error':max(errors),'periodic_net_vorticity':int(vort.sum()),'numpy':np.__version__}
    print('SELF_CHECK',json.dumps(result),flush=True)
    return result

def run_case(spec):
    length,temperature,seed,initial,extend=spec
    name=f'L{length}-T{temperature:.2f}-s{seed}'
    base=ROOT/'base'/name;target=(ROOT/'extended'/name) if extend else base
    target.mkdir(parents=True,exist_ok=False)
    rng=np.random.default_rng(seed)
    parity=np.indices((length,length)).sum(axis=0)%2
    masks=[parity==0,parity==1]
    started=time.perf_counter()
    if extend:
        theta=np.load(base/'final-angles.npy')
        rng.bit_generator.state=json.loads((base/'rng-state.json').read_text())
        previous=np.loadtxt(base/'series.csv',delimiter=',',skiprows=1)
        warmup=0
    else:
        theta=np.zeros((length,length)) if initial=='ordered' else rng.uniform(-np.pi,np.pi,(length,length))
        previous=None;warmup=5000
    initial_energy=energy(theta)/theta.size
    initial_angles=theta.copy()
    warm_records=[]
    warm_accept=0
    for step in range(1,warmup+1):
        warm_accept+=sweep(theta,rng,temperature,masks)
        if step%50==0:
            obs,_=observe(theta);warm_records.append([step,*obs])
    rows=[];acceptance=0
    for step in range(1,20001):
        acceptance+=sweep(theta,rng,temperature,masks)
        if step%5==0:
            obs,_=observe(theta);rows.append([step+(20000 if extend else 0),*obs])
    data=np.array(rows)
    if previous is not None:data=np.vstack([previous,data])
    header='sweep,energy_per_spin,M2,cos_x,cos_y,current_x,current_y,current_x2,current_y2,vortex_abs_density'
    np.savetxt(target/'series.csv',data,delimiter=',',header=header,comments='')
    if warm_records:np.savetxt(target/'warmup.csv',np.array(warm_records),delimiter=',',header=header,comments='')
    obs,vort=observe(theta)
    np.save(target/'initial-angles.npy',initial_angles);np.save(target/'final-angles.npy',theta)
    np.savetxt(target/'final-angles.csv',theta,delimiter=',')
    np.savetxt(target/'final-vortices.csv',vort,delimiter=',',fmt='%d')
    (target/'rng-state.json').write_text(json.dumps(rng.bit_generator.state,indent=2)+'\n')
    receipt=dict(L=length,temperature_J=temperature,J=1,kB=1,seed=seed,initialization=initial,extension_from_base=extend,initial_energy_per_spin=initial_energy,warmup_sweeps=warmup,production_sweeps=40000 if extend else 20000,additional_production_sweeps=20000,measurement_every_sweeps=5,measurements=len(data),proposal_half_width_rad=float(np.pi/2),sweep_definition='two checkerboard sublattice updates, each spin attempted once',warmup_acceptance=warm_accept/warmup if warmup else None,production_acceptance=acceptance/20000,periodic_net_vorticity=int(vort.sum()),wall_seconds=time.perf_counter()-started,numpy_version=np.__version__)
    (target/'run.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('FINISHED',str(target.relative_to(ROOT)),f"samples={len(data)} acceptance={receipt['production_acceptance']:.4f} wall={receipt['wall_seconds']:.2f}s",flush=True)
    return receipt

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--benchmark',action='store_true');parser.add_argument('--base',action='store_true');parser.add_argument('--extended',action='store_true');args=parser.parse_args()
    check=self_check()
    if args.benchmark:
        theta=np.zeros((24,24));rng=np.random.default_rng(20260922);parity=np.indices(theta.shape).sum(0)%2;masks=[parity==0,parity==1]
        start=time.perf_counter()
        for i in range(1000):sweep(theta,rng,.92,masks)
        duration=time.perf_counter()-start
        print(f'BENCHMARK L24 1000 sweeps = {duration:.6f} s; 36 base + 8 extension cases at 2 workers estimated < {duration*1060/2:.1f} s plus I/O',flush=True)
        return
    temps=[.70,.80,.88,.92,1.00,1.10]
    specifications=[]
    for length in [8,16,24]:
        for ti,temp in enumerate(temps):
            for replica,initial in [(0,'ordered'),(1,'random')]:
                if args.extended and not(length in [16,24] and temp in [.88,.92]):continue
                seed=2026092200+length*100+ti*2+replica
                specifications.append((length,temp,seed,initial,args.extended))
    assert args.base or args.extended
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        result=[f.result() for f in as_completed([pool.submit(run_case,s) for s in specifications])]
    record=dict(hamiltonian='H/J=-sum_nearest_neighbour_once cos(theta_i-theta_j)',boundary='periodic square',software='Python/NumPy, two workers, one thread each',cases=result,total_wall_seconds=time.perf_counter()-start,self_check=check,interpretation='finite size and finite sampling model demonstration; no material J or thermodynamic-limit transition estimate')
    (ROOT/('extended-summary.json' if args.extended else 'base-summary.json')).write_text(json.dumps(record,indent=2)+'\n')
    print('MONTE_CARLO_FINISHED',len(result),'cases',f"wall={record['total_wall_seconds']:.2f}s",flush=True)

if __name__=='__main__':main()
