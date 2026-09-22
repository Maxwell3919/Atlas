from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
from ase.build import bulk
from ase.io import write
from ase.optimize import BFGS
from mace.calculators import MACECalculator

torch.set_num_threads(2)
model = Path("../models/mace-mp-0-small.model")
print("MACE", metadata.version("mace-torch"), "ASE", metadata.version("ase"))
print("model_sha256", hashlib.sha256(model.read_bytes()).hexdigest())
calc = MACECalculator(model_paths=str(model), device="cpu", default_dtype="float64")

# Diamond Si, conventional cubic cell: 8 atoms, a = 5.43 angstrom.
# Move one atom to give the optimizer a finite restoring force.
atoms = bulk("Si", "diamond", a=5.43, cubic=True)
atoms.positions[0] += [0.10, -0.06, 0.04]
write("initial.extxyz", atoms)
cell_before = atoms.cell.array.copy()
atoms.calc = calc
e0 = atoms.get_potential_energy()
f0 = np.linalg.norm(atoms.get_forces(), axis=1).max()
print(f"INITIAL atoms={len(atoms)} energy_eV={e0:.10f} fmax_eV_A={f0:.8f}")

start = time.perf_counter()
opt = BFGS(atoms, trajectory="relax.traj", logfile="relax.log")
converged = opt.run(fmax=0.001, steps=100)
energy = atoms.get_potential_energy()
fmax = np.linalg.norm(atoms.get_forces(), axis=1).max()
unchanged = bool(np.array_equal(cell_before, atoms.cell.array))
write("relaxed.extxyz", atoms)
write("relaxed.cif", atoms)
result = dict(converged=bool(converged), steps=opt.nsteps,
              energy_eV=float(energy), initial_energy_eV=float(e0),
              fmax_eV_A=float(fmax), cell_unchanged=unchanged,
              volume_A3=atoms.get_volume(), wall_seconds=time.perf_counter()-start)
Path("result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert converged and fmax < 0.001 and unchanged
print("RELAX_ACCEPTED")

