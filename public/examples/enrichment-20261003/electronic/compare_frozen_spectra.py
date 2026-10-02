#!/usr/bin/env python3
"""Compare existing frozen Sc2C spectral readouts; no DFT or source writes."""
from pathlib import Path
import argparse
import csv
import math

D = "sc2c_pdos_at_EF_states_per_eV_cell"
W = "sc2c_pdos_window_weight_states_per_cell"
PAIRS = [
    ("Contact at 0%", "Isolated Sc2C 0%", "Heterostructure 0%"),
    ("Contact at +1.5%", "Isolated Sc2C +1.5%", "Heterostructure +1.5%"),
    ("Heterostructure strain 0% to +1.5%", "Heterostructure 0%", "Heterostructure +1.5%"),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.source.resolve():
        raise ValueError("Output must differ from the source")
    with args.source.open(newline="") as handle:
        items = list(csv.DictReader(handle))
    rows = {item["state"]: item for item in items}
    if len(items) != 4 or len(rows) != 4:
        raise ValueError("Expected four unique frozen states")
    results = []
    for label, ref, target in PAIRS:
        record = dict(comparison=label, reference=ref, target=target)
        for key, name in [(D, "D_EF"), (W, "window_weight")]:
            x, y = float(rows[ref][key]), float(rows[target][key])
            if not all(math.isfinite(v) for v in [x, y]) or x <= 0 or y < 0:
                raise ValueError("Invalid recorded spectral quantity")
            record[name + "_reference"] = x
            record[name + "_target"] = y
            record[name + "_difference"] = y - x
            record[name + "_change_percent"] = 100 * (y / x - 1)
        results.append(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    for row in results:
        print("{}: D(EF) change={:+.4f}% ; window change={:+.4f}%".format(
            row["comparison"], row["D_EF_change_percent"],
            row["window_weight_change_percent"]))
    print("These are changes of broadened projected spectra, not transferred electrons.")

if __name__ == "__main__":
    main()
