#!/usr/bin/env python3
"""Recompute Al-Si formation energies and finite binary hulls as tables."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

RY_TO_EV = 13.605693122994
EXPECTED = {"al-fcc", "al3si-l12", "alsi-b2", "alsi3-l12", "si-diamond"}
COMPOUNDS = ("al3si-l12", "alsi-b2", "alsi3-l12")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing header")
        return reader.fieldnames, list(reader)


def unique_by_case(rows: list[dict[str, str]], protocol: str) -> dict[str, dict[str, str]]:
    selected = [row for row in rows if row.get("protocol") == protocol]
    out: dict[str, dict[str, str]] = {}
    for row in selected:
        case = row.get("case", "")
        if not case or case in out:
            raise ValueError(f"{protocol}: empty or duplicate case {case!r}")
        out[case] = row
    if set(out) != EXPECTED:
        raise ValueError(
            f"{protocol}: expected cases {sorted(EXPECTED)}, found {sorted(out)}"
        )
    return out


def validated_values(rows: dict[str, dict[str, str]], protocol: str) -> dict[str, tuple[float, float]]:
    values: dict[str, tuple[float, float]] = {}
    for case, row in rows.items():
        n_al = int(row["nAl"])
        n_si = int(row["nSi"])
        n_atoms = int(row["natoms"])
        if n_atoms <= 0 or n_al + n_si != n_atoms:
            raise ValueError(f"{protocol}/{case}: nAl+nSi does not equal natoms")
        x = float(row["xSi"])
        expected_x = n_si / n_atoms
        if not math.isclose(x, expected_x, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"{protocol}/{case}: xSi disagrees with stoichiometry")
        total = float(row["total_energy_Ry"])
        reference = float(row["reference_energy_Ry"])
        computed = (total - reference) * RY_TO_EV / n_atoms
        stored = float(row["formation_eV_atom"])
        if not math.isfinite(computed) or not math.isclose(computed, stored, rel_tol=0, abs_tol=1e-9):
            raise ValueError(f"{protocol}/{case}: formation_eV_atom disagrees with raw energies")
        values[case] = (x, computed)
    return values


def lower_hull(values: dict[str, tuple[float, float]]) -> list[tuple[str, float, float]]:
    lowest: dict[float, tuple[str, float]] = {}
    for case, (x, energy) in values.items():
        if x not in lowest or energy < lowest[x][1]:
            lowest[x] = (case, energy)
    points = [(case, x, energy) for x, (case, energy) in sorted(lowest.items())]
    hull: list[tuple[str, float, float]] = []
    for point in points:
        while len(hull) >= 2:
            _, x0, e0 = hull[-2]
            _, x1, e1 = hull[-1]
            _, x2, e2 = point
            if (e1 - e0) / (x1 - x0) >= (e2 - e1) / (x2 - x1) - 1e-12:
                hull.pop()
            else:
                break
        hull.append(point)
    if len(hull) < 2 or not math.isclose(hull[0][1], 0, abs_tol=1e-12) or not math.isclose(hull[-1][1], 1, abs_tol=1e-12):
        raise ValueError("binary lower hull does not include xSi=0 and xSi=1")
    return hull


def hull_energy(x: float, hull: list[tuple[str, float, float]]) -> float:
    for _, xv, energy in hull:
        if math.isclose(x, xv, abs_tol=1e-12):
            return energy
    for left, right in zip(hull, hull[1:]):
        _, x0, e0 = left
        _, x1, e1 = right
        if x0 < x < x1:
            weight = (x - x0) / (x1 - x0)
            return e0 + weight * (e1 - e0)
    raise ValueError(f"xSi={x:g} is outside hull range")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k24", type=Path, default=Path("formation-energy.csv"))
    parser.add_argument("--k32", type=Path, default=Path("formation-k32.csv"))
    parser.add_argument("--comparison", type=Path, default=Path("comparison-k24-k32.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("review"))
    args = parser.parse_args()

    _, raw24 = read_rows(args.k24)
    _, raw32 = read_rows(args.k32)
    _, raw_comparison = read_rows(args.comparison)
    rows24 = unique_by_case(raw24, "k24")
    rows32 = unique_by_case(raw32, "k32")
    comparison: dict[str, dict[str, str]] = {}
    for row in raw_comparison:
        case = row["case"]
        if case in comparison:
            raise ValueError(f"comparison table: duplicate case {case}")
        comparison[case] = row
    if set(comparison) != EXPECTED:
        raise ValueError("comparison table must contain exactly the five reviewed cases")

    values24 = validated_values(rows24, "k24")
    values32 = validated_values(rows32, "k32")
    hull24 = lower_hull(values24)
    hull32 = lower_hull(values32)

    results: list[dict[str, str]] = []
    max_change = 0.0
    max_case = ""
    for case in sorted(EXPECTED, key=lambda item: values24[item][0]):
        x24, e24 = values24[case]
        x32, e32 = values32[case]
        if not math.isclose(x24, x32, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"{case}: composition changed between meshes")
        above24 = e24 - hull_energy(x24, hull24)
        above32 = e32 - hull_energy(x32, hull32)
        if not math.isclose(above24, float(rows24[case]["above_hull_eV_atom"]), rel_tol=0, abs_tol=2e-8):
            raise ValueError(f"k24/{case}: reconstructed hull distance disagrees")
        if not math.isclose(above32 * 1000.0, float(rows32[case]["above_hull_meV_atom"]), rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"k32/{case}: reconstructed hull distance disagrees")
        delta = (e32 - e24) * 1000.0
        row = comparison[case]
        candidate = float(row["candidate_energy_change_meV_atom"])
        reference = float(row["reference_energy_change_meV_atom"])
        stored_delta = float(row["formation_change_meV_atom"])
        if not math.isclose(delta, stored_delta, rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"{case}: stored mesh change disagrees with recomputed energies")
        if not math.isclose(candidate - reference, delta, rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"{case}: candidate/reference decomposition does not close")
        results.append({
            "case": case,
            "xSi": f"{x24:.8f}",
            "formation_k24_eV_atom": f"{e24:.9f}",
            "above_hull_k24_eV_atom": f"{above24:.9f}",
            "formation_k32_eV_atom": f"{e32:.9f}",
            "above_hull_k32_meV_atom": f"{above32*1000:.6f}",
            "formation_change_meV_atom": f"{delta:.6f}",
            "candidate_energy_change_meV_atom": f"{candidate:.6f}",
            "reference_energy_change_meV_atom": f"{reference:.6f}",
        })
        if case in COMPOUNDS and abs(delta) > max_change:
            max_change, max_case = abs(delta), case

    if max_case != "al3si-l12" or not math.isclose(max_change, 1.79822269267, rel_tol=0, abs_tol=2e-6):
        raise ValueError(f"unexpected maximum intermediate formation-energy change: {max_case} {max_change}")
    if {item[0] for item in hull24} != {"al-fcc", "si-diamond"}:
        raise ValueError("k24 finite hull vertices changed from the reviewed endpoints")
    if {item[0] for item in hull32} != {"al-fcc", "si-diamond"}:
        raise ValueError("k32 finite hull vertices changed from the reviewed endpoints")

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / "alsi-thermo-review.csv"
    md_path = args.outdir / "alsi-thermo-review.md"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    md_lines = [
        "# Al-Si formation-energy and finite-hull review",
        "",
        "- Scope: the five supplied cubic prototypes only; no omitted compositions are inferred.",
        "- Both k24 and k32 finite hulls contain only fcc Al and diamond Si endpoints.",
        "- At 32³, Al3Si L12, B2 AlSi, and AlSi3 L12 remain above the endpoint tie-line.",
        f"- Largest intermediate 24³-to-32³ formation-energy change: {max_change:.6f} meV/atom ({max_case}).",
        "- The 1 meV/atom line is a selected numerical comparison, not a universal criterion.",
        "- Component relation: formation-energy change = candidate energy change − reference energy change.",
        "",
        "| case | xSi | ΔEform k24 (eV/atom) | above hull k24 (eV/atom) | ΔEform k32 (eV/atom) | above hull k32 (meV/atom) | Δ mesh (meV/atom) | candidate Δ (meV/atom) | reference Δ (meV/atom) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        md_lines.append(
            f"| {row['case']} | {row['xSi']} | {row['formation_k24_eV_atom']} | "
            f"{row['above_hull_k24_eV_atom']} | {row['formation_k32_eV_atom']} | "
            f"{row['above_hull_k32_meV_atom']} | {row['formation_change_meV_atom']} | "
            f"{row['candidate_energy_change_meV_atom']} | {row['reference_energy_change_meV_atom']} |"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"rows={len(results)} k24_hull=Al-fcc,Si-diamond k32_hull=Al-fcc,Si-diamond")
    print(f"max_intermediate_change={max_change:.6f} meV/atom case={max_case}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()

