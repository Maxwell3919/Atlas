#!/usr/bin/env python3
"""Validate HfI2 separation-energy bookkeeping and emit a focused review table."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

EV_A2_TO_J_M2 = 16.02176634
EXPECTED_AREA_A2 = 10.848221494425957
TAIL_DISTANCES = {16.0, 17.0, 18.0, 19.0, 20.0}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing CSV header")
        return reader.fieldnames, list(reader)


def poscar_area(path: Path) -> float:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 5:
        raise ValueError(f"{path}: incomplete POSCAR lattice")
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError(f"{path}: expected positive POSCAR scale factor")
    a = [float(value) * scale for value in lines[2].split()[:3]]
    b = [float(value) * scale for value in lines[3].split()[:3]]
    if len(a) != 3 or len(b) != 3:
        raise ValueError(f"{path}: malformed first two lattice vectors")
    cross = (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )
    area = math.sqrt(sum(value * value for value in cross))
    if not math.isfinite(area) or area <= 0:
        raise ValueError(f"{path}: non-positive/non-finite in-plane area")
    return area


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted", type=Path, default=Path("exfoliation.csv"))
    parser.add_argument("--excluded", type=Path, default=Path("excluded.csv"))
    parser.add_argument("--poscar", type=Path, default=Path("POSCAR"))
    parser.add_argument("--outdir", type=Path, default=Path("review"))
    args = parser.parse_args()

    accepted_header, accepted_rows = read_csv(args.accepted)
    excluded_header, excluded_rows = read_csv(args.excluded)
    area = poscar_area(args.poscar)
    if not math.isclose(area, EXPECTED_AREA_A2, rel_tol=0, abs_tol=2e-9):
        raise ValueError(
            f"{args.poscar}: area {area:.12f} A^2 differs from reviewed cell "
            f"{EXPECTED_AREA_A2:.12f} A^2"
        )
    required = {
        "directory", "d_A", "energy_without_entropy_eV", "energy_sigma0_eV",
        "delta_E_meV", "W_meV_A2", "W_J_m2", "outer_periodic_gap_A",
    }
    missing = required - set(accepted_header)
    if missing:
        raise ValueError(f"{args.accepted}: missing columns {sorted(missing)}")
    for required_name in ("directory", "reason", "energy_lines", "ediff", "normal_end"):
        if required_name not in excluded_header:
            raise ValueError(f"{args.excluded}: missing column {required_name}")

    by_distance: dict[float, dict[str, str]] = {}
    for row in accepted_rows:
        d = float(row["d_A"])
        if d in by_distance:
            raise ValueError(f"{args.accepted}: duplicate accepted d={d:g} A")
        for column in required - {"directory"}:
            value = float(row[column])
            if not math.isfinite(value):
                raise ValueError(f"{args.accepted}: non-finite {column} at d={d:g} A")
        by_distance[d] = row
    expected_distances = {0.0} | set(float(d) for d in range(2, 21))
    if set(by_distance) != expected_distances:
        missing_d = sorted(expected_distances - set(by_distance))
        unexpected_d = sorted(set(by_distance) - expected_distances)
        raise ValueError(
            f"accepted d set differs: missing={missing_d}, unexpected={unexpected_d}"
        )
    if by_distance[0.0]["directory"] != "scf_eq":
        raise ValueError("the sole d=0 reference must be scf_eq")

    e0 = float(by_distance[0.0]["energy_without_entropy_eV"])
    recalculated: dict[float, tuple[float, float, float]] = {}
    for d, row in by_distance.items():
        energy = float(row["energy_without_entropy_eV"])
        delta_e = energy - e0
        delta_mev = delta_e * 1000.0
        work_mev_a2 = delta_mev / area
        work_j_m2 = delta_e / area * EV_A2_TO_J_M2
        checks = (
            ("delta_E_meV", delta_mev, 2e-5),
            ("W_meV_A2", work_mev_a2, 2e-7),
            ("W_J_m2", work_j_m2, 2e-8),
        )
        for column, calculated, tolerance in checks:
            stored = float(row[column])
            if not math.isclose(calculated, stored, rel_tol=0, abs_tol=tolerance):
                raise ValueError(
                    f"d={d:g} A: recomputed {column}={calculated:.12g}, "
                    f"stored={stored:.12g}"
                )
        recalculated[d] = (delta_mev, work_mev_a2, work_j_m2)

    if len(accepted_rows) != 20 or len(excluded_rows) != 7:
        raise ValueError(
            f"reviewed dataset requires 20 accepted and 7 excluded; "
            f"found {len(accepted_rows)} and {len(excluded_rows)}"
        )
    excluded_by_name = {row["directory"]: row for row in excluded_rows}
    if len(excluded_by_name) != len(excluded_rows):
        raise ValueError(f"{args.excluded}: duplicate excluded directory")
    expected_d1 = {"scf_d1", "scf_d1.00"}
    if expected_d1 - set(excluded_by_name):
        raise ValueError(f"nominal d=1 A exclusions are missing: {sorted(expected_d1 - set(excluded_by_name))}")
    if excluded_by_name["scf_d1"]["reason"] != "OUTCAR absent":
        raise ValueError("scf_d1 exclusion reason no longer matches the reviewed record")
    if excluded_by_name["scf_d1.00"]["reason"] != "Incomplete static SCF":
        raise ValueError("scf_d1.00 exclusion reason no longer matches the reviewed record")

    selected = [0.0, 2.0, 16.0, 17.0, 18.0, 19.0, 20.0]
    selected_rows: list[dict[str, str]] = []
    for d in selected:
        row = by_distance[d]
        delta_mev, work_mev_a2, work_j_m2 = recalculated[d]
        selected_rows.append({
            "directory": row["directory"],
            "d_A": f"{d:.1f}",
            "energy_without_entropy_eV": row["energy_without_entropy_eV"],
            "delta_E_meV": f"{delta_mev:.8f}",
            "W_meV_A2": f"{work_mev_a2:.8f}",
            "W_J_m2": f"{work_j_m2:.10f}",
            "outer_periodic_gap_A": row["outer_periodic_gap_A"],
        })

    args.outdir.mkdir(parents=True, exist_ok=True)
    table_path = args.outdir / "hfi2-selected-separation-review.csv"
    exclusion_path = args.outdir / "hfi2-exclusion-review.csv"
    report_path = args.outdir / "hfi2-separation-review.md"
    write_csv(table_path, [
        "directory", "d_A", "energy_without_entropy_eV", "delta_E_meV",
        "W_meV_A2", "W_J_m2", "outer_periodic_gap_A",
    ], selected_rows)
    write_csv(exclusion_path, excluded_header, excluded_rows)

    tail_energies = [float(by_distance[d]["energy_without_entropy_eV"]) for d in sorted(TAIL_DISTANCES)]
    tail_spread_mev = (max(tail_energies) - min(tail_energies)) * 1000.0
    step_19_20_mev = (
        float(by_distance[20.0]["energy_without_entropy_eV"])
        - float(by_distance[19.0]["energy_without_entropy_eV"])
    ) * 1000.0
    w20 = recalculated[20.0][2]
    report_path.write_text(
        "# HfI2 frozen-slab separation review\n\n"
        f"- POSCAR area: {area:.12f} Å².\n"
        f"- Accepted scan points: {len(accepted_rows)}; excluded directories: {len(excluded_rows)}.\n"
        "- Accepted distances: d=0 and d=2…20 Å. The nominal d=1 Å attempts are not accepted: "
        "scf_d1 has no OUTCAR and scf_d1.00 is an incomplete static SCF.\n"
        "- Energy field used throughout: OUTCAR energy without entropy, eV/cell.\n"
        f"- At d=20 Å, ΔE={recalculated[20.0][0]:.8f} meV/cell and W={w20:.10f} J/m².\n"
        f"- The d=16…20 Å five-point energy spread is {tail_spread_mev:.5f} meV/cell; "
        f"the d=19→20 Å change is {step_19_20_mev:.5f} meV/cell.\n\n"
        "Interpretation: these values describe the frozen six-layer, prototype-derived slab under "
        "one specified layer-separation operation. The d=0 reference is itself a six-layer slab, "
        "not a bulk calculation. The finite-distance energy and non-monotone high-distance spread "
        "do not establish a bulk-referenced exfoliation energy or a converged asymptote.\n",
        encoding="utf-8",
    )
    print(f"accepted={len(accepted_rows)} excluded={len(excluded_rows)} area={area:.12f} A^2")
    print(f"d20: delta_E={recalculated[20.0][0]:.8f} meV/cell W={w20:.10f} J/m^2")
    print(f"d16-20 energy spread={tail_spread_mev:.5f} meV/cell; d19->20={step_19_20_mev:.5f} meV/cell")
    print(table_path)
    print(exclusion_path)
    print(report_path)


if __name__ == "__main__":
    main()

