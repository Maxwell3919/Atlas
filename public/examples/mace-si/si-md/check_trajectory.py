import json
from pathlib import Path
import numpy as np
from ase.io import read

report = {}
starts = []
for label in ["nve-1fs", "nve-0p5fs"]:
    frames = read(label + ".traj", index=":")
    series = np.genfromtxt(label + ".csv", delimiter=",", names=True)
    starts.append(frames[0])
    energies = np.array([a.get_total_energy() / len(a) for a in frames])
    volumes = np.array([a.get_volume() for a in frames])
    momenta = np.array([np.linalg.norm(a.get_momenta().sum(axis=0)) for a in frames])
    minimum_distances = []
    for atoms in frames:
        distances = atoms.get_all_distances(mic=True)
        np.fill_diagonal(distances, np.inf)
        minimum_distances.append(distances.min())
    report[label] = {
        "frames": len(frames), "csv_rows": len(series), "atoms_per_frame": len(frames[0]),
        "all_frames_finite": bool(all(np.isfinite(a.positions).all() for a in frames)),
        "max_energy_csv_mismatch_eV_atom": float(np.max(np.abs(energies - series["total_eV_atom"]))),
        "volume_range_A3": float(np.ptp(volumes)),
        "max_total_momentum_ase_units": float(momenta.max()),
        "minimum_pair_distance_A": float(np.min(minimum_distances)),
        "final_rms_displacement_A": float(np.sqrt(np.mean(np.sum((frames[-1].positions - frames[0].positions)**2, axis=1))))
    }
    assert len(frames) == len(series) == 101
    assert all(len(a) == 64 for a in frames)
    assert report[label]["all_frames_finite"]
    assert report[label]["max_energy_csv_mismatch_eV_atom"] < 1e-10
    assert report[label]["volume_range_A3"] < 1e-10
report["initial_positions_identical"] = bool(np.array_equal(starts[0].positions, starts[1].positions))
report["initial_momenta_identical"] = bool(np.array_equal(starts[0].get_momenta(), starts[1].get_momenta()))
assert report["initial_positions_identical"] and report["initial_momenta_identical"]
Path("trajectory-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
print("TRAJECTORY_CHECK_ACCEPTED")
