#!/usr/bin/env python3
"""Inspect accepted frozen-control PDOS tables; no DFT or plotting."""
from pathlib import Path
import csv, json, math, sys
root = Path(__file__).resolve().parent
source = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "frozen_pdos_long.csv"
expected = ["Heterostructure 0%", "Isolated Sc2C 0%",
            "Heterostructure +1.5%", "Isolated Sc2C +1.5%"]
groups = {name: [] for name in expected}
with source.open(newline="") as handle:
    reader = csv.DictReader(handle)
    names = ["strain_percent", "fermi_eV", "energy_minus_fermi_eV",
             "sc2c_pdos", "zrcl2_pdos", "total_projected_pdos",
             "projected_sum_error"]
    if not set(["state"] + names).issubset(reader.fieldnames or []):
        raise ValueError("Missing PDOS fields")
    for item in reader:
        state = item["state"]
        if state not in groups:
            raise ValueError("Unknown state: " + state)
        values = {k: float(item[k]) for k in names}
        if not all(math.isfinite(v) for v in values.values()):
            raise ValueError("Non-finite PDOS row")
        discrepancy = values["sc2c_pdos"] + values["zrcl2_pdos"] - values["total_projected_pdos"]
        if abs(discrepancy - values["projected_sum_error"]) > 1e-10:
            raise ValueError("Saved projection mismatch differs")
        groups[state].append(values)
rows, checks = [], []
for state in expected:
    data = groups[state]
    if not data:
        raise ValueError("Empty state: " + state)
    if len({x["strain_percent"] for x in data}) != 1 or len({x["fermi_eV"] for x in data}) != 1:
        raise ValueError("Mixed strain or Fermi reference")
    energy = [x["energy_minus_fermi_eV"] for x in data]
    steps = [b-a for a,b in zip(energy[:-1],energy[1:])]
    if not steps or min(steps) <= 0 or max(abs(x-0.005) for x in steps) > 1e-8:
        raise ValueError("Unexpected energy grid")
    if not min(energy) < 0 < max(energy):
        raise ValueError("Grid does not bracket EF")
    near = min(data, key=lambda x: abs(x["energy_minus_fermi_eV"]))
    if abs(near["energy_minus_fermi_eV"]) > 0.0025 + 1e-8:
        raise ValueError("No near-Fermi grid point")
    window = [x for x in data if abs(x["energy_minus_fermi_eV"]) <= 0.1]
    denominator = sum(abs(x["total_projected_pdos"]) for x in window)
    if not window or denominator <= 0:
        raise ValueError("Invalid closure window")
    closure = 100 * sum(abs(x["projected_sum_error"]) for x in window) / denominator
    row = {"state": state, "strain_percent": near["strain_percent"],
           "nearest_E_minus_EF_eV": near["energy_minus_fermi_eV"],
           "sc2c_pdos": near["sc2c_pdos"], "zrcl2_pdos": near["zrcl2_pdos"],
           "total_projected_pdos": near["total_projected_pdos"]}
    rows.append(row)
    checks.append({"state":state, "rows":len(data), "grid_step_eV":steps[0],
                   "L1_projection_error_percent_EF_pm_0p1":closure})
    print(f'{state}: E-EF={row["nearest_E_minus_EF_eV"]:+.4f} eV; '
          f'Sc2C={row["sc2c_pdos"]:.6f}; ZrCl2={row["zrcl2_pdos"]:.6f}; '
          f'total={row["total_projected_pdos"]:.2f} states/(eV cell)')
with (root/"nearest-fermi-pdos.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
result = {"source":source.name, "method":"Nearest grid point; no interpolation at EF",
          "units":"PDOS: states/(eV cell); E-EF: eV",
          "reference":"Each state has its own Fermi energy",
          "scope":"Frozen geometry; projected DOS is not transferred charge",
          "rows":rows, "checks":checks}
(root/"nearest-fermi-pdos.json").write_text(json.dumps(result,indent=2)+"\n")
print("Four frozen-control PDOS states checked; no DFT invoked.")
