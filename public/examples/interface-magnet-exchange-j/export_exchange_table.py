#!/usr/bin/env python3
"""Export model-fit states and the rejected stripe trial without implying Tc."""
import csv, json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / "exchange-summary.json").read_text(encoding="utf-8"))
roles = {"fm2": "fit", "afm2": "fit", "fm4": "folding check", "neel4": "folding check"}
rows = []
for row in summary["rows"]:
    rows.append({
        "state": row["state"], "role": roles[row["state"]], "atoms": row["n_atoms"],
        "correlation_sum": row["correlation_sum"], "E0_eV_cell": f'{row["E0_eV_cell"]:.8f}',
        "model_E0_eV_cell": f'{row["predicted_E0_eV_cell"]:.8f}',
        "residual_meV_atom": f'{row["residual_meV_atom"]:.8f}',
        "local_moments_muB": ";".join(f"{m:.3f}" for m in row["local_moment_muB"]),
        "interpretation": "two-state fit" if row["state"] in ("fm2", "afm2") else "supercell folding check",
    })
trial = summary["rejected_trial"]
rows.append({
    "state": trial["state"], "role": "rejected target",
    "atoms": trial["n_atoms"], "correlation_sum": "",
    "E0_eV_cell": f'{trial["E0_eV_cell"]:.8f}', "model_E0_eV_cell": "",
    "residual_meV_atom": "", "local_moments_muB": ";".join(f"{m:.3f}" for m in trial["local_moment_muB"]),
    "interpretation": "moment collapsed; not an independent validation state",
})
with (root / "exchange-state-model-checks.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["state", "role", "atoms", "correlation_sum", "E0_eV_cell", "model_E0_eV_cell", "residual_meV_atom", "local_moments_muB", "interpretation"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
with (root / "exchange-fit-summary.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["J_eff_meV_per_unique_NN_bond", "Eref_eV_atom", "fit_states", "independent_third_state_validation", "scope"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerow({
        "J_eff_meV_per_unique_NN_bond": f'{summary["J_effective_meV_per_bond"]:.8f}',
        "Eref_eV_atom": f'{summary["Eref_eV_atom"]:.10f}',
        "fit_states": ";".join(summary["fit_states"]),
        "independent_third_state_validation": summary["independent_third_state_validation"],
        "scope": summary["scope"],
    })
print("Wrote 5 model-state rows and one fit-summary row; no finite-temperature result is inferred")

