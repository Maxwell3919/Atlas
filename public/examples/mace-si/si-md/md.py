from pathlib import Path
import csv
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
from ase import units
from ase.constraints import FixCom
from ase.io import read, write
from ase.md.bussi import Bussi
from ase.md.verlet import VelocityVerlet
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from mace.calculators import MACECalculator

torch.set_num_threads(2)
model = Path("../models/mace-mp-0-small.model")
print("MACE", metadata.version("mace-torch"), "ASE", metadata.version("ase"))
print("model_sha256", hashlib.sha256(model.read_bytes()).hexdigest())
calc = MACECalculator(model_paths=str(model), device="cpu", default_dtype="float64")

# Use the accepted variable-cell minimum and make a 64-atom supercell.
assert json.loads(Path("../si-vc-relax/result.json").read_text())["converged"]
atoms = read("../si-vc-relax/relaxed.extxyz").repeat((2, 2, 2))
atoms.set_constraint(FixCom())
atoms.calc = calc
MaxwellBoltzmannDistribution(atoms, temperature_K=300.0, force_temp=True,
                            rng=np.random.default_rng(20260922))
Stationary(atoms, preserve_temperature=True)
write("initial.traj", atoms)
print(f"INITIAL atoms={len(atoms)} DOF={atoms.get_number_of_degrees_of_freedom()} "
      f"temperature_K={atoms.get_temperature():.8f}")

# Bring kinetic and potential energy into contact with a 300 K bath.
warmup = Bussi(atoms, timestep=1.0 * units.fs, temperature_K=300.0,
               taut=100.0 * units.fs, rng=np.random.default_rng(923),
               trajectory="warmup.traj", logfile="warmup.log", loginterval=10)
t0 = time.perf_counter()
warmup.run(1000)
write("equilibrated.traj", atoms)
write("equilibrated.extxyz", atoms)
print(f"WARMUP_DONE steps={warmup.nsteps} time_ps=1.000 "
      f"temperature_K={atoms.get_temperature():.8f} wall_s={time.perf_counter()-t0:.3f}")

results = {}
for label, dt_fs, steps in [("nve-1fs", 1.0, 500), ("nve-0p5fs", 0.5, 1000)]:
    # Read exactly the same positions, velocities, cell and constraints twice.
    atoms = read("equilibrated.traj")
    atoms.calc = calc
    state_hash = hashlib.sha256(atoms.positions.tobytes() + atoms.get_momenta().tobytes()).hexdigest()
    dyn = VelocityVerlet(atoms, timestep=dt_fs * units.fs,
                         trajectory=label + ".traj", logfile=label + ".log",
                         loginterval=round(5.0 / dt_fs))
    series = []
    with open(label + ".csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_ps", "potential_eV_atom", "kinetic_eV_atom",
                         "total_eV_atom", "temperature_K"])
        def record():
            epot = atoms.get_potential_energy() / len(atoms)
            ekin = atoms.get_kinetic_energy() / len(atoms)
            row = [dyn.get_time() / (1000 * units.fs), epot, ekin,
                   epot + ekin, atoms.get_temperature()]
            series.append(row)
            writer.writerow([f"{value:.12f}" for value in row])
            handle.flush()
        dyn.attach(record, interval=round(5.0 / dt_fs))
        print(f"START {label} steps={steps} timestep_fs={dt_fs} initial_state_sha256={state_hash}")
        t0 = time.perf_counter()
        dyn.run(steps)
    data = np.asarray(series)
    delta = 1000 * (data[:, 3] - data[0, 3])
    fit = np.polyfit(data[:, 0], delta, 1)
    results[label] = dict(steps=dyn.nsteps, timestep_fs=dt_fs, duration_ps=float(data[-1, 0]),
                         initial_state_sha256=state_hash,
                         max_abs_delta_meV_atom=float(np.abs(delta).max()),
                         final_delta_meV_atom=float(delta[-1]),
                         linear_drift_meV_atom_ps=float(fit[0]),
                         mean_temperature_K=float(data[:, 4].mean()),
                         wall_seconds=time.perf_counter()-t0)
    write(label + "-final.extxyz", atoms)
    print(json.dumps(results[label], indent=2))

same_start = results["nve-1fs"]["initial_state_sha256"] == results["nve-0p5fs"]["initial_state_sha256"]
results["same_initial_state"] = same_start
Path("result.json").write_text(json.dumps(results, indent=2) + "\n")
assert same_start
assert results["nve-1fs"]["max_abs_delta_meV_atom"] < 0.1
assert results["nve-0p5fs"]["max_abs_delta_meV_atom"] < results["nve-1fs"]["max_abs_delta_meV_atom"]
print("MD_INTEGRATION_ACCEPTED")

