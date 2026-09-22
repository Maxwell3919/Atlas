from pathlib import Path
import csv
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
import ase, scipy, phonopy, symfc
from ase import units
from ase.build import bulk
from ase.calculators.singlepoint import SinglePointCalculator
from ase.constraints import FixCom
from ase.filters import FrechetCellFilter
from ase.io import read, write
from ase.md.bussi import Bussi
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from ase.md.verlet import VelocityVerlet
from ase.optimize import BFGS
from mace.calculators import MACECalculator
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from scipy.optimize import linear_sum_assignment

torch.set_num_threads(2)
start = time.perf_counter()
model = Path('../models/mace-mp-0-small.model')
versions = {name: metadata.version(name) for name in ['mace-torch','ase','phonopy','symfc','spglib','scipy','numpy','torch']}
paths = {mod.__name__: mod.__file__ for mod in [ase, scipy, phonopy, symfc]}
provenance = dict(versions=versions, module_paths=paths,
                  model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                  cpu_threads=2, source_trajectory_sha256=hashlib.sha256(Path('../si-md/nve-1fs.traj').read_bytes()).hexdigest())
print('ENVIRONMENT', json.dumps(provenance, indent=2), flush=True)
Path('environment.json').write_text(json.dumps(provenance, indent=2)+'\n')
calc = MACECalculator(model_paths=str(model), device='cpu', default_dtype='float64')

# Define the cubic reference explicitly. No old trajectory file is modified.
old_uc = read('../si-vc-relax/relaxed.extxyz')
old_ref = old_uc.repeat((2,2,2))
a0 = old_uc.get_volume()**(1/3)
uc = bulk('Si','diamond',a=a0,cubic=True)
uc.calc = calc
opt = BFGS(FrechetCellFilter(uc, hydrostatic_strain=True), logfile='reference-relax.log', trajectory='reference-relax.traj')
accepted = opt.run(fmax=1e-5, steps=100)
assert accepted
assert np.ptp(uc.cell.lengths()) < 1e-10
assert np.max(np.abs(uc.cell.angles()-90)) < 1e-10
write('reference-unitcell.extxyz', uc)
ase_ref = uc.repeat((2,2,2))
write('reference-supercell.extxyz', ase_ref)
ref_info = dict(a_initial_A=a0, a_final_A=float(uc.cell.lengths()[0]), steps=opt.nsteps,
                volume_A3=uc.get_volume(), fmax_eV_A=float(np.linalg.norm(uc.get_forces(),axis=1).max()),
                stress_eV_A3=uc.get_stress().tolist())
print('CUBIC_REFERENCE',json.dumps(ref_info),flush=True)
Path('reference.json').write_text(json.dumps(ref_info,indent=2)+'\n')

def new_phonon():
    cell=PhonopyAtoms(symbols=uc.get_chemical_symbols(), cell=uc.cell.array, scaled_positions=uc.get_scaled_positions())
    return Phonopy(cell, supercell_matrix=[2,2,2], primitive_matrix='F', symprec=1e-5)

ph = new_phonon()
ph_ref = ph.supercell
# Explicit atom-order mapping: phonopy's supercell order differs from ASE.repeat.
frac = ph_ref.scaled_positions[:,None,:]-ase_ref.get_scaled_positions()[None,:,:]
frac -= np.rint(frac)
cost = np.linalg.norm(frac@ase_ref.cell.array,axis=2)
rows, order = linear_sum_assignment(cost)
assert np.array_equal(rows,np.arange(64))
assert cost[rows,order].max()<1e-8
np.save('phonopy-to-ase-order.npy',order)
ph.save('reference-phonopy.yaml')
print('ATOM_ORDER max_mapping_error_A',cost[rows,order].max(),'primitive_atoms',len(ph.primitive),flush=True)

baseline={}
for amplitude in [0.01,0.005]:
    label=f'harmonic-{amplitude:g}'
    ph=new_phonon()
    ph.generate_displacements(distance=amplitude,is_plusminus=True)
    forces=[]
    displaced=[]
    for index, sc in enumerate(ph.supercells_with_displacements):
        from ase import Atoms
        atoms=Atoms(symbols=sc.symbols,cell=sc.cell,scaled_positions=sc.scaled_positions,pbc=True)
        atoms.calc=calc
        force=atoms.get_forces()
        forces.append(force)
        displaced.append(atoms.copy())
        displaced[-1].calc=SinglePointCalculator(displaced[-1],energy=atoms.get_potential_energy(),forces=force)
        print('FINITE_DISPLACEMENT',label,index+1,'fmax',float(np.linalg.norm(force,axis=1).max()),flush=True)
    ph.forces=np.array(forces)
    ph.produce_force_constants(fc_calculator='traditional')
    raw_drift=float(np.abs(ph.force_constants.sum(axis=1)).max())
    ph.symmetrize_force_constants()
    np.save(label+'-fc.npy',ph.force_constants)
    ph.save(label+'.yaml',settings={'force_constants':True})
    write(label+'-forces.traj',displaced)
    baseline[label]=dict(amplitude_A=amplitude, force_evaluations=len(forces),raw_fc_translational_drift_eV_A2=raw_drift,
                         corrected_fc_translational_drift_eV_A2=float(np.abs(ph.force_constants.sum(axis=1)).max()))
print('HARMONIC_BASELINES',json.dumps(baseline),flush=True)
Path('baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')

# Transfer only displacements from the old cell. Every mapped configuration gets new forces.
source=read('../si-md/nve-1fs.traj',':')
us=[]; fs=[]; mapped=[]; temperatures=[]
for i,frame in enumerate(source):
    delta=frame.get_scaled_positions(wrap=False)-old_ref.get_scaled_positions(wrap=False)
    delta-=np.rint(delta)
    u=delta@ase_ref.cell.array
    u-=u.mean(axis=0)
    atoms=ase_ref.copy()
    atoms.positions+=u
    atoms.calc=calc
    force=atoms.get_forces()
    us.append(u[order]); fs.append(force[order]); temperatures.append(frame.get_temperature())
    copy=atoms.copy()
    copy.calc=SinglePointCalculator(copy,energy=atoms.get_potential_energy(),forces=force)
    mapped.append(copy)
    if i%20==0: print('MAPPED_FORCE',i,'of',len(source),'max_u_A',float(np.linalg.norm(u,axis=1).max()),flush=True)
np.savez_compressed('mapped-dataset.npz',displacements=np.array(us),forces=np.array(fs),source_temperature_K=temperatures,
                    source_time_ps=np.arange(len(source))*0.005,order=order)
write('mapped-configurations.traj',mapped)
print('MAPPING_DONE snapshots',len(source),'all_forces_recomputed',True,flush=True)

# An independent velocity seed probes transfer beyond the original short trajectory.
atoms=ase_ref.copy(); atoms.set_constraint(FixCom()); atoms.calc=calc
MaxwellBoltzmannDistribution(atoms,temperature_K=300,force_temp=True,rng=np.random.default_rng(2026092202))
Stationary(atoms,preserve_temperature=True)
seed_hash=hashlib.sha256(atoms.get_momenta().tobytes()).hexdigest()
write('independent-initial.traj',atoms)
print('INDEPENDENT_START seed=2026092202 momentum_sha256',seed_hash,flush=True)
warm=Bussi(atoms,1*units.fs,temperature_K=300,taut=100*units.fs,rng=np.random.default_rng(924),
           trajectory='independent-warmup.traj',logfile='independent-warmup.log',loginterval=10)
t0=time.perf_counter(); warm.run(1000)
print('INDEPENDENT_WARMUP_DONE steps',warm.nsteps,'temperature_K',atoms.get_temperature(),'wall_s',time.perf_counter()-t0,flush=True)
write('independent-after-warmup.traj',atoms)
dyn=VelocityVerlet(atoms,1*units.fs,trajectory='independent-nve.traj',logfile='independent-nve.log',loginterval=10)
rows=[]
with open('independent-nve.csv','w',newline='') as h:
    writer=csv.writer(h); writer.writerow(['time_ps','temperature_K','potential_eV_atom','total_eV_atom'])
    def record():
        ep=atoms.get_potential_energy()/64
        row=[dyn.get_time()/(1000*units.fs),atoms.get_temperature(),ep,ep+atoms.get_kinetic_energy()/64]
        writer.writerow(row);h.flush();rows.append(row)
    dyn.attach(record,interval=10)
    t0=time.perf_counter();dyn.run(500)
series=np.array(rows)
info=dict(warmup_steps=1000,production_steps=500,timestep_fs=1,snapshots=len(rows),
          velocity_seed=2026092202,momentum_sha256=seed_hash,mean_temperature_K=float(series[:,1].mean()),
          temperature_std_K=float(series[:,1].std()),
          max_abs_delta_total_meV_atom=float(np.max(np.abs(series[:,3]-series[0,3]))*1000),
          production_wall_s=time.perf_counter()-t0,total_prepare_wall_s=time.perf_counter()-start)
Path('independent.json').write_text(json.dumps(info,indent=2)+'\n')
print('INDEPENDENT_MD_DONE',json.dumps(info,indent=2),flush=True)
print('DATA_PREPARATION_FINISHED',flush=True)

