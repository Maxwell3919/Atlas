from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
from ase import units
from ase.build import bulk
from ase.filters import FrechetCellFilter
from ase.io import write
from ase.optimize import BFGS
from mace.calculators import MACECalculator

torch.set_num_threads(2)
model = Path("../models/mace-mp-0-small.model")
print("MACE", metadata.version("mace-torch"), "ASE", metadata.version("ase"))
print("model_sha256", hashlib.sha256(model.read_bytes()).hexdigest())
calc = MACECalculator(model_paths=str(model), device="cpu", default_dtype="float64")

# Start diamond Si from a larger cubic cell and perturb one atom.
atoms = bulk("Si", "diamond", a=5.60, cubic=True)
atoms.positions[0] += [0.05, -0.03, 0.02]
write("initial.extxyz", atoms)
atoms.calc = calc
e0 = atoms.get_potential_energy()
v0 = atoms.get_volume()
print(f"INITIAL atoms={len(atoms)} energy_eV={e0:.10f} volume_A3={v0:.8f}")

start = time.perf_counter()
cell_filter = FrechetCellFilter(atoms, scalar_pressure=0.0)
opt = BFGS(cell_filter, trajectory="vc-relax.traj", logfile="vc-relax.log")
converged = opt.run(fmax=0.0005, steps=150)
energy = atoms.get_potential_energy()
forces = atoms.get_forces()
stress = atoms.get_stress()
fmax = float(np.linalg.norm(forces, axis=1).max())
smax = float(np.abs(stress).max())
write("relaxed.extxyz", atoms)
write("relaxed.cif", atoms)
result = dict(converged=bool(converged), steps=opt.nsteps,
              initial_energy_eV=float(e0), energy_eV=float(energy),
              initial_volume_A3=v0, volume_A3=atoms.get_volume(),
              cell_lengths_A=atoms.cell.lengths().tolist(),
              cell_angles_deg=atoms.cell.angles().tolist(),
              fmax_eV_A=fmax, stress_eV_A3=stress.tolist(),
              max_abs_stress_GPa=smax / units.GPa,
              wall_seconds=time.perf_counter()-start)
Path("result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert converged and fmax < 0.001 and smax < 0.0001
print("VC_RELAX_ACCEPTED")

