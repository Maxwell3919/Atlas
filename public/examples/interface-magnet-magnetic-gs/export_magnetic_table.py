#!/usr/bin/env python3
"""Export the three-state Fe comparison as a compact CSV table."""
import csv, json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = json.loads((root / "magnetic-energies.json").read_text(encoding="utf-8"))
with (root / "magnetic-state-energy-table.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["state", "E0_eV_cell", "F_eV_cell", "delta_E0_meV_atom_from_FM", "cell_moment_muB"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "state": row["state"],
            "E0_eV_cell": f'{row["E0_eV_cell"]:.8f}',
            "F_eV_cell": f'{row["F_eV_cell"]:.8f}',
            "delta_E0_meV_atom_from_FM": f'{row["dE0_meV_atom"]:.6f}',
            "cell_moment_muB": f'{row["mag_cell_muB"]:.6f}',
        })
print(f"Wrote {len(rows)} rows to magnetic-state-energy-table.csv")

