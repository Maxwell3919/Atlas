#!/usr/bin/env python3
"""Export k-mesh dependence and orientation-resolved MAE totals as CSV."""
import csv, json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / "mae-summary.json").read_text(encoding="utf-8"))
with (root / "mae-kmesh-comparison.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["mesh", "nkpoints_per_calculation", "delta_E0_x_minus_z_meV_per_Fe", "delta_F_x_minus_z_meV_per_Fe", "sign_changed_vs_previous_mesh"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    previous = None
    for pair in summary["pairs"]:
        delta = pair["delta_E0_x_minus_z_meV_per_Fe"]
        writer.writerow({
            "mesh": pair["mesh"],
            "nkpoints_per_calculation": pair["mesh"] ** 2,
            "delta_E0_x_minus_z_meV_per_Fe": f'{delta:.8f}',
            "delta_F_x_minus_z_meV_per_Fe": f'{pair["delta_F_x_minus_z_meV_per_Fe"]:.8f}',
            "sign_changed_vs_previous_mesh": "" if previous is None else str((delta > 0) != (previous > 0)).lower(),
        })
        previous = delta
with (root / "mae-orientation-energies.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["case", "nkpoints", "E0_eV", "F_eV", "moment_magnitude_muB", "magnetization_angle_error_deg"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for case in summary["cases"]:
        m = case["mag_cartesian_muB"]
        magnitude = sum(x*x for x in m) ** 0.5
        writer.writerow({
            "case": case["name"], "nkpoints": case["nkpoints"],
            "E0_eV": f'{case["E0_eV"]:.8f}', "F_eV": f'{case["F_eV"]:.8f}',
            "moment_magnitude_muB": f'{magnitude:.6f}',
            "magnetization_angle_error_deg": f'{case["mag_angle_from_target_deg"]:.6f}',
        })
print("Wrote 2 mesh rows and 4 orientation rows")

