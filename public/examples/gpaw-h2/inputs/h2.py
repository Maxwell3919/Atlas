#!/usr/bin/env python3
"""GPAW 26.7.0 public H2 proposal; NOT runtime-validated in this task.
Adapted from version-matched official atomize.py/relax.py, GPL-3.0-or-later.
No H-atom calculation or atomization-energy claim.
"""
import argparse
import hashlib
import importlib.metadata as md
import json
from pathlib import Path
import numpy as np
import gpaw
from gpaw import GPAW, PW
from ase import Atoms
from ase.optimize import BFGSLineSearch

p = argparse.ArgumentParser()
p.add_argument('--stage', choices=['smoke', 'relax', 'forcecheck'], required=True)
p.add_argument('--setup-dir', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
assert md.version('gpaw') == '26.7.0', 'Unfrozen GPAW version'
assert md.version('ase') == '3.29.0', 'Unfrozen ASE version'
# Disable fallback datasets; the exact PBE H dataset must exist here.
setup_dir = a.setup_dir.resolve()
files = [f for f in (setup_dir / 'H.PBE', setup_dir / 'H.PBE.gz') if f.is_file()]
assert len(files) == 1, 'Supply exactly one H.PBE or H.PBE.gz in isolated setup-dir'
gpaw.setup_paths[:] = [str(setup_dir)]
a.out.mkdir(parents=True, exist_ok=False)
versions = {n: md.version(n) for n in ['gpaw', 'ase', 'numpy', 'scipy']}
identity = {'versions': versions, 'setup': str(files[0]),
            'setup_sha256': hashlib.sha256(files[0].read_bytes()).hexdigest(),
            'input_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(a.out / 'identity.json').write_text(json.dumps(identity, indent=2))
# Explicit periodic finite-box model, not an isolated-molecule convergence claim.
calc = GPAW(mode=PW(340), xc='PBE', nbands=2, kpts=(1, 1, 1),
            spinpol=False, charge=0, hund=False,
            occupations={'name': 'fermi-dirac', 'width': 0.0},
            symmetry='off',  # proposed: displaced geometry may break initial symmetry
            convergence={'energy': 1e-6, 'density': 1e-6, 'eigenstates': 1e-8},
            maxiter=60, txt=str(a.out / 'gpaw.txt'))
d = 0.90 if a.stage == 'relax' else 0.74
atoms = Atoms('H2', positions=[(0, 0, -d/2), (0, 0, d/2)],
              cell=(6., 6., 6.), pbc=True)
atoms.center()
atoms.calc = calc
energy0 = float(atoms.get_potential_energy())
forces0 = atoms.get_forces().copy()
result = {'stage': a.stage, 'energy_initial_eV': energy0,
          'forces_initial_eV_A': forces0.tolist(), 'bond_initial_A': d,
          'physics_converged': False, 'basis_box_converged': False}
if a.stage == 'relax':
    opt = BFGSLineSearch(atoms, logfile=str(a.out / 'optimizer.log'),
                        trajectory=str(a.out / 'trajectory.traj'))
    converged = bool(opt.run(fmax=0.05, steps=12))
    result.update(geometry_threshold_met=converged,
                  optimizer_steps=opt.nsteps,
                  energy_final_eV=float(atoms.get_potential_energy()),
                  bond_final_A=float(atoms.get_distance(0, 1)),
                  max_force_final_eV_A=float(np.linalg.norm(atoms.get_forces(), axis=1).max()))
    result['accepted_local'] = (converged and result['energy_final_eV'] <= energy0 + 1e-4
                                and 0.5 < result['bond_final_A'] < 1.2)
elif a.stage == 'forcecheck':
    delta = 0.005
    # Analytic Cartesian force of atom 1, z component versus central difference.
    z = float(atoms.positions[1, 2])
    atoms.positions[1, 2] = z + delta
    ep = float(atoms.get_potential_energy())
    atoms.positions[1, 2] = z - delta
    em = float(atoms.get_potential_energy())
    atoms.positions[1, 2] = z
    fd = -(ep-em)/(2*delta)
    err = abs(fd-float(forces0[1, 2]))
    result.update(delta_A=delta, energy_plus_eV=ep, energy_minus_eV=em,
                  force_fd_eV_A=fd, force_error_eV_A=err, accepted_local=err <= 0.02)
else:
    result['accepted_local'] = bool(np.isfinite(energy0) and np.isfinite(forces0).all()
                                   and np.linalg.norm(forces0.sum(axis=0)) <= 1e-5)
# Successful energy/force calls imply GPAW's specified SCF criteria were met;
# the full gpaw.txt must still be inspected for warnings and actual criteria.
result['scf_calls_completed'] = True
result['accepted_local'] = bool(result['accepted_local'] and np.isfinite(energy0))
(a.out / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False))
if not result['accepted_local']:
    raise SystemExit('Local teaching acceptance failed; retain output and stop')
