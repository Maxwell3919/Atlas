#!/usr/bin/env python3
"""Check the archived H2 CSV and save exact slider reference values.

This is numerical post-processing only; it does not run DFT or produce a plot.
Supply archived planar.csv and summary.json; choose a new output directory.
"""

import argparse
import bisect
import csv
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--planar', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    DATA = args.output_dir
    require(not DATA.exists(), 'Choose a new output directory')
    with args.planar.open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(
            reader.fieldnames
            == ["z_A", "delta_n_e_A3", "linear_e_A", "cumulative_e"],
            "Unexpected CSV columns",
        )
        rows = [{key: float(value) for key, value in row.items()} for row in reader]
    summary = json.loads(args.summary.read_text())
    require(all(math.isfinite(v) for r in rows for v in r.values()), "Non-finite data")
    z = [r["z_A"] for r in rows]
    line = [r["linear_e_A"] for r in rows]
    stored = [r["cumulative_e"] for r in rows]
    require(len(rows) == summary["grid"][2] + 1, "Missing periodic endpoint")
    require(all(a < b for a, b in zip(z, z[1:])), "Coordinate order")
    require(abs(z[0]) < 1e-12, "Nonzero integral origin")
    require(abs(z[-1] - summary["height_A"]) < 1e-12, "Cell height mismatch")
    require(abs(line[-1] - line[0]) < 1e-12, "Periodic endpoint mismatch")
    area_error = max(
        abs(r["linear_e_A"] - summary["area_A2"] * r["delta_n_e_A3"])
        for r in rows
    )
    require(area_error < 1e-12, "Area factor or units mismatch")

    increments = [
        0.5 * (a + b) * (zb - za)
        for za, zb, a, b in zip(z, z[1:], line, line[1:])
    ]
    cumulative = [0.0]
    for increment in increments:
        cumulative.append(cumulative[-1] + increment)
    cumulative_error = max(abs(a - b) for a, b in zip(cumulative, stored))
    require(cumulative_error < 1e-12, "Stored cumulative values mismatch")
    total = cumulative[-1]
    require(abs(total - summary["full_cell_residual_e"]) < 1e-12, "Total mismatch")

    def integral_at(boundary):
        require(z[0] - 1e-12 <= boundary <= z[-1] + 1e-12, "Boundary outside cell")
        if abs(boundary - z[0]) < 1e-12:
            return 0.0
        if abs(boundary - z[-1]) < 1e-12:
            return total
        boundary = min(max(boundary, z[0]), z[-1])
        if boundary == z[-1]:
            return total
        k = max(0, bisect.bisect_right(z, boundary) - 1)
        h = boundary - z[k]
        width = z[k + 1] - z[k]
        # The line density is piecewise linear, so its partial integral is quadratic.
        return (
            cumulative[k]
            + line[k] * h
            + 0.5 * (line[k + 1] - line[k]) * h * h / width
        )

    for region in summary["regions"]:
        obtained = integral_at(region["hi_A"]) - integral_at(region["lo_A"])
        require(abs(obtained - region["delta_e"]) < 1e-12, "Archived region mismatch")

    positive_parts = []
    for width, a, b in zip((b - a for a, b in zip(z, z[1:])), line, line[1:]):
        if a >= 0 and b >= 0:
            positive_parts.append(0.5 * (a + b) * width)
        elif a <= 0 and b <= 0:
            positive_parts.append(0.0)
        else:
            zero_fraction = -a / (b - a)
            positive_width = width * (zero_fraction if a > 0 else 1 - zero_fraction)
            positive_parts.append(0.5 * max(a, b) * positive_width)
    positive_1d = math.fsum(positive_parts)
    negative_1d = total - positive_1d
    require(positive_1d <= summary["positive_3d_e"] + 1e-12, "Invalid 1D/3D ordering")

    cuts = [0.0, 4.0, 4.63, 4.9, 4.95, 5.0, 5.05, 5.1, 5.37, 6.0, 10.0]
    fixtures = []
    for cut in cuts:
        left = integral_at(cut)
        right = total - left
        require(abs(left + right - total) < 1e-12, "Complement mismatch")
        fixtures.append(
            {"boundary_A": cut, "left_delta_e": left, "right_delta_e": right}
        )
    DATA.mkdir(parents=True)
    with (DATA / "boundary-reference.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fixtures[0]))
        writer.writeheader()
        writer.writerows(fixtures)

    peak = max(rows, key=lambda r: r["linear_e_A"])
    trough = min(rows, key=lambda r: r["linear_e_A"])
    result = {
        "status": "pass",
        "method": "exact integration of each piecewise-linear line-density segment",
        "samples_including_periodic_endpoint": len(rows),
        "area_factor_max_error_e_A": area_error,
        "cumulative_max_error_e": cumulative_error,
        "full_cell_delta_e": total,
        "positive_area_of_1d_profile_e": positive_1d,
        "negative_area_of_1d_profile_e": negative_1d,
        "positive_voxel_integral_3d_e": summary["positive_3d_e"],
        "negative_voxel_integral_3d_e": summary["negative_3d_e"],
        "profile_peak": {"z_A": peak["z_A"], "linear_e_A": peak["linear_e_A"]},
        "profile_trough": {"z_A": trough["z_A"], "linear_e_A": trough["linear_e_A"]},
        "boundary_fixtures": fixtures,
        "input_files": [str(args.planar), str(args.summary)],
        "plot_created": False,
        "raw_chgcar_reprocessed": False,
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (DATA / "boundary-reference.json").write_text(encoded)
    print(f"samples={len(rows)}; full-cell residual={total:.12e} e")
    print(f"positive 1D={positive_1d:.10f} e; positive 3D={summary['positive_3d_e']:.10f} e")
    for fixture in fixtures:
        if fixture['boundary_A'] in (4.9, 5.0, 5.1):
            print(f"boundary={fixture['boundary_A']:.2f} A: left={fixture['left_delta_e']:+.12e} e; right={fixture['right_delta_e']:+.12e} e")
    print(f"checks=pass; wrote {DATA}/boundary-reference.csv and boundary-reference.json")


if __name__ == "__main__":
    main()
