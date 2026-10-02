#!/usr/bin/env python3
"""Integrate a fixed own-EF PDOS window from the published frozen controls."""
from pathlib import Path
import argparse, bisect, csv, json, math

STATES = {
    "Heterostructure 0%": 0.0,
    "Isolated Sc2C 0%": 0.0,
    "Heterostructure +1.5%": 1.5,
    "Isolated Sc2C +1.5%": 1.5,
}
COLUMNS = ["sc2c_pdos", "zrcl2_pdos", "total_projected_pdos"]

def integrate(x, y, lo, hi):
    if not x[0] < lo < hi < x[-1]:
        raise ValueError("Window must lie inside the saved energy grid")
    def at(t):
        i = bisect.bisect_right(x, t) - 1
        return y[i] + (y[i+1] - y[i]) * (t - x[i]) / (x[i+1] - x[i])
    points = [(lo, at(lo))]
    points.extend((a, b) for a, b in zip(x, y) if lo < a < hi)
    points.append((hi, at(hi)))
    return math.fsum((b[0] - a[0]) * (a[1] + b[1]) / 2
                     for a, b in zip(points, points[1:]))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--half-width", type=float, default=0.1)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    if not math.isfinite(args.half_width) or args.half_width <= 0:
        raise ValueError("half-width must be a positive finite eV value")
    if args.output_dir.exists():
        raise FileExistsError("Use a new output directory: " + str(args.output_dir))
    groups = {state: [] for state in STATES}
    fields = ["strain_percent", "fermi_eV", "energy_minus_fermi_eV",
              *COLUMNS, "projected_sum_error"]
    with args.input.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"state", *fields}.issubset(reader.fieldnames or []):
            raise ValueError("Missing PDOS fields")
        for item in reader:
            state = item["state"]
            if state not in groups:
                raise ValueError("Unknown state: " + state)
            row = {name: float(item[name]) for name in fields}
            if not all(math.isfinite(v) for v in row.values()):
                raise ValueError("Non-finite data: " + state)
            mismatch = row["sc2c_pdos"] + row["zrcl2_pdos"] - row["total_projected_pdos"]
            if abs(mismatch - row["projected_sum_error"]) > 1e-10:
                raise ValueError("Projection discrepancy column does not match")
            groups[state].append(row)
    rows, checks = [], []
    width = 2 * args.half_width
    for state, strain in STATES.items():
        data = groups[state]
        if not data or {v["strain_percent"] for v in data} != {strain}:
            raise ValueError("Empty or mixed-strain state: " + state)
        if len({v["fermi_eV"] for v in data}) != 1:
            raise ValueError("Mixed Fermi energies: " + state)
        x = [v["energy_minus_fermi_eV"] for v in data]
        steps = [b-a for a, b in zip(x, x[1:])]
        if not steps or any(abs(v - 0.005) > 1e-8 for v in steps):
            raise ValueError("Expected a strictly increasing 0.005 eV grid")
        weights = {col: integrate(x, [v[col] for v in data],
                                  -args.half_width, args.half_width)
                   for col in COLUMNS}
        absolute_mismatch = integrate(x, [abs(v["projected_sum_error"]) for v in data],
                                      -args.half_width, args.half_width)
        if weights["total_projected_pdos"] <= 0:
            raise ValueError("Nonpositive integrated total projection")
        row = {"state": state, "strain_percent": strain,
               "half_width_eV": args.half_width, "fermi_eV": data[0]["fermi_eV"]}
        for col in COLUMNS:
            row[col + "_weight_states_cell"] = weights[col]
            row[col + "_mean_states_eV_cell"] = weights[col] / width
        rows.append(row)
        checks.append({"state": state, "source_rows": len(data),
                       "L1_closure_percent": 100 * absolute_mismatch /
                       weights["total_projected_pdos"]})
        print(f'{state}: Sc2C={weights["sc2c_pdos"]:.6f}; '
              f'ZrCl2={weights["zrcl2_pdos"]:.6f}; '
              f'total projection={weights["total_projected_pdos"]:.6f} states/cell')
    changes = {}
    for tag, first, last in [("heterostructure", rows[0], rows[2]),
                              ("isolated_Sc2C", rows[1], rows[3])]:
        key = "sc2c_pdos_weight_states_cell"
        changes[tag] = 100 * (last[key] / first[key] - 1)
    print(f'Sc2C window-weight change: heterostructure={changes["heterostructure"]:+.4f}%; '
          f'isolated={changes["isolated_Sc2C"]:+.4f}%')
    report = {"source": str(args.input), "half_width_eV": args.half_width,
              "method": "Piecewise-linear spectrum; exact window endpoints; trapezoidal integral",
              "reference": "Each state uses its own saved Fermi energy; no absolute band alignment",
              "units": "Integrated projected spectral weight: states/cell; mean PDOS: states/(eV cell)",
              "scope": "Frozen geometry; no occupation integral, transferred charge, or EPC",
              "rows": rows, "checks": checks, "sc2c_weight_change_percent": changes}
    args.output_dir.mkdir(parents=True)
    with (args.output_dir / "window-pdos.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "window-pdos.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f'Window [-{args.half_width:g}, +{args.half_width:g}] eV; '
          'linear endpoints only; no DFT or charge-transfer inference.')

if __name__ == "__main__":
    main()
