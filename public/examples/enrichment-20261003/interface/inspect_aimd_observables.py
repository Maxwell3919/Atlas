"""Inspect existing Al trajectory frames and match their native energy clock."""
from pathlib import Path
import csv, itertools, json, sys
import numpy as np

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("structure-observations")
out.mkdir(parents=True, exist_ok=True)
cases = ("nve-dt20-nosym", "nve-dt10-nosym")
summary = {}
end_frames = {}
for case in cases:
    folder = root / "aimd" / case
    thermo = list(csv.DictReader((folder / "thermo.csv").open()))
    with np.load(folder / "trajectory.npz") as trajectory:
        positions = trajectory["positions_A"]
        cell = trajectory["cell_A"]
        time = trajectory["time_fs"]
    assert positions.shape == (len(thermo) + 1, 8, 3)
    assert cell.shape == (3, 3) and np.isfinite(positions).all()
    assert all(abs(float(row["energy_sample_time_fs"]) - time[j]) < 1e-8 for j, row in enumerate(thermo))
    # Use explicit periodic images; component-wise rounding is unsuitable for this oblique cell.
    candidates = []
    for i, j, shift in itertools.product(range(8), range(8), itertools.product((-1, 0, 1), repeat=3)):
        if i == j and shift == (0, 0, 0):
            continue
        vector = positions[0, j] - positions[0, i] + np.array(shift) @ cell
        candidates.append((float(np.linalg.norm(vector)), i, j, shift))
    nearest = min(item[0] for item in candidates)
    bonds = []
    for distance, i, j, shift in candidates:
        reverse = (j, i, tuple(-n for n in shift))
        if abs(distance - nearest) < 1e-7 and (i, j, shift) < reverse:
            bonds.append((i, j, np.array(shift) @ cell))
    assert len(bonds) == 48
    displacement = positions - positions[0]
    rms = np.sqrt(np.mean(np.sum(displacement**2, axis=2), axis=1))
    lengths = np.array([[np.linalg.norm(frame[j] - frame[i] + translation)
                         for i, j, translation in bonds] for frame in positions])
    rows = []
    for frame, t in enumerate(time):
        rows.append(dict(time_fs=float(t),rms_A=float(rms[frame]),
                         bond_min_A=float(lengths[frame].min()),bond_max_A=float(lengths[frame].max()),
                         bond_mean_A=float(lengths[frame].mean()),
                         temperature_K=float(thermo[frame]["temperature_K"]) if frame < len(thermo) else ""))
    with (out / (case + "-structure.csv")).open("w") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    cold = min(range(len(thermo)), key=lambda j: float(thermo[j]["temperature_K"]))
    e0 = thermo[0]
    row = thermo[cold]
    factor = 13.605693122994 * 1000 / 8
    summary[case] = dict(nframes=len(time),initial_neighbor_pairs=48,initial_neighbor_A=nearest,
                         rms_end_A=float(rms[-1]),rms_peak_A=float(rms.max()),
                         rms_peak_time_fs=float(time[rms.argmax()]),
                         end_bond_min_A=float(lengths[-1].min()),end_bond_max_A=float(lengths[-1].max()),
                         end_bond_mean_A=float(lengths[-1].mean()),
                         cold_energy_time_fs=float(row["energy_sample_time_fs"]),
                         cold_temperature_K=float(row["temperature_K"]),cold_coordinate_frame=cold,
                         cold_rms_A=float(rms[cold]),cold_bond_min_A=float(lengths[cold].min()),
                         cold_bond_max_A=float(lengths[cold].max()),
                         cold_potential_change_meV_atom=(float(row["potential_Ry"])-float(e0["potential_Ry"]))*factor,
                         cold_kinetic_change_meV_atom=(float(row["kinetic_Ry"])-float(e0["kinetic_Ry"]))*factor,
                         cold_total_change_meV_atom=(float(row["total_Ry"])-float(e0["total_Ry"]))*factor)
    end_frames[case] = positions[-1]
    print(f"{case}: frames={len(time)} initial_pairs=48 initial_nn={nearest:.8f} A")
    print(f"  RMS_end={rms[-1]:.8f} A RMS_peak={rms.max():.8f} A at {time[rms.argmax()]:.8f} fs")
    print(f"  end_initial_neighbor_range={lengths[-1].min():.8f}..{lengths[-1].max():.8f} A")
difference = end_frames[cases[0]] - end_frames[cases[1]]
summary["matched_end_rms_difference_A"] = float(np.sqrt(np.mean(np.sum(difference**2, axis=1))))
summary["definition"] = "48 unique periodic-image pairs in the initial first neighbor shell, tracked without changing pair identity; range is not a confidence interval or a coordination-number test."
summary["time_axis"] = "Coordinate frame j at j*dt matches thermo energy row j at j*dt; the final coordinate frame has no matching printed energy/temperature sample."
(out / "structure-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(f"matched_end_RMS_difference={summary['matched_end_rms_difference_A']:.10e} A")
