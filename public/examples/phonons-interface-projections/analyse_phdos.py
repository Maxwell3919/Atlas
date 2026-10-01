#!/usr/bin/env python3
"""Group existing QE 7.2 atomic PHDOS; do not recompute force constants."""
from pathlib import Path
import argparse, csv, json, re
import numpy as np

CM_PER_THZ = 33.3564095198152
CASES = {
    "zrcl2-sc2c": {
        "dos": "zrclscc.phdos", "input": "pwx.in",
        "symbols": ["Zr", "C", "Cl", "Cl", "Sc", "Sc"],
        "layers": {"ZrCl2": [0, 2, 3], "Sc2C": [1, 4, 5]},
    },
    "snse2-sr2n": {
        "dos": "srnsnse.phdos", "input": "pwxall.in",
        "symbols": ["Sr", "Sr", "Sn", "Se", "Se", "N"],
        "layers": {"Sr2N": [0, 1, 5], "SnSe2": [2, 3, 4]},
    },
}

def analyse(public_root, output):
    output.mkdir(parents=True, exist_ok=True)
    report = {"numpy_version": np.__version__,
              "projection": "QE 7.2 matdyn dynq: squared dynamical-matrix eigenvector",
              "density_unit": "states/THz", "frequency_unit": "THz", "cases": {}}
    for name, case in CASES.items():
        directory = public_root / "examples" / name / "ph64"
        text = (directory / case["input"]).read_text()
        tail = re.split(r"ATOMIC_POSITIONS[^\n]*\n", text, flags=re.I)[1]
        symbols = [line.split()[0] for line in tail.splitlines()[:6]]
        assert symbols == case["symbols"], (name, symbols)
        data = np.loadtxt(directory / case["dos"])
        assert data.shape[1] == len(symbols) + 2
        assert np.all(np.isfinite(data)) and np.all(np.diff(data[:, 0]) > 0)
        frequency = data[:, 0] / CM_PER_THZ
        total = data[:, 1] * CM_PER_THZ
        atoms = data[:, 2:] * CM_PER_THZ
        elements = {s: np.flatnonzero(np.array(symbols) == s).tolist()
                    for s in dict.fromkeys(symbols)}
        groups = {**elements, **case["layers"]}
        grouped = {g: atoms[:, ids].sum(axis=1) for g, ids in groups.items()}
        with (output / (name + "-grouped.csv")).open("w") as handle:
            writer = csv.writer(handle)
            writer.writerow(["frequency_THz", "total_states_per_THz", *groups])
            writer.writerows(zip(frequency, total, *grouped.values()))
        integral = lambda y: float(np.trapezoid(y, frequency))
        peak = float(np.max(np.abs(total)))
        result = {"sources": ["examples/" + name + "/ph64/" + case[k]
                              for k in ["dos", "input"]],
                  "atom_order": symbols, "layer_site_indices_1based": {
                      g: [i + 1 for i in ids] for g, ids in case["layers"].items()},
                  "rows": len(data), "frequency_range_THz": [float(frequency[0]), float(frequency[-1])],
                  "total_integral": integral(total), "expected_modes": 3 * len(symbols),
                  "atom_integrals": [integral(atoms[:, i]) for i in range(len(symbols))],
                  "group_integrals": {g: integral(y) for g, y in grouped.items()},
                  "max_projection_sum_error_relative_to_peak":
                      float(np.max(np.abs(atoms.sum(axis=1) - total)) / peak)}
        report["cases"][name] = result
        print(f"{name}: rows={len(data)} modes={result['total_integral']:.8f} / 18 "
              f"sum_error/peak={result['max_projection_sum_error_relative_to_peak']:.3e}")
        print("  atom order:", ", ".join(f"{i+1}:{s}" for i, s in enumerate(symbols)))
        print("  layer integrals:", ", ".join(f"{g}={result['group_integrals'][g]:.8f}"
                                               for g in case["layers"]))
    (output / "projection-checks.json").write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("projection-results"))
    arguments = parser.parse_args()
    analyse(arguments.public_root, arguments.output)
