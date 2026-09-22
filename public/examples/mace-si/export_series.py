import csv
import numpy as np
from ase.io import read

for directory, trajectory in [("si-relax", "relax.traj"), ("si-vc-relax", "vc-relax.traj")]:
    frames = read(f"{directory}/{trajectory}", index=":")
    with open(f"{directory}/optimization.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["step", "energy_eV", "fmax_eV_A", "volume_A3"])
        for step, atoms in enumerate(frames):
            writer.writerow([step, atoms.get_potential_energy(),
                             np.linalg.norm(atoms.get_forces(), axis=1).max(), atoms.get_volume()])
    print(directory, "frames", len(frames), "last_energy_eV", frames[-1].get_potential_energy())
