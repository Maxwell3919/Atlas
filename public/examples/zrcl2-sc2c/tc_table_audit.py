#!/usr/bin/env python3
"""Audit stored Tc tables and calculate piecewise-linear intersections."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Sequence


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_series(base: Path, tag: str, suffix: str) -> dict:
    table_path = base / tag / f"lambda{suffix}.dat"
    output_path = base / tag / f"lambdax{suffix}.out"
    rows = []
    for line in table_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rows.append([float(value) for value in line.split()])
    lines = output_path.read_text().splitlines()
    header = next(i for i, line in enumerate(lines) if "omega_log" in line and "T_c" in line)
    tc = [float(line.split()[2]) for line in lines[header + 1:header + 1 + len(rows)]]
    if len(rows) != len(tc):
        raise ValueError(f"{tag}{suffix}: {len(rows)} table rows but {len(tc)} Tc rows")
    return {
        "rows": rows,
        "sigma": [row[0] for row in rows],
        "lambda": [row[1] for row in rows],
        "omega_log": [row[3] for row in rows],
        "tc": tc,
        "table_path": table_path,
        "output_path": output_path,
    }


def _interp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def piecewise_linear_crossings(
    sigma: Sequence[float], tc64: Sequence[float], tc96: Sequence[float]
) -> list[dict]:
    if not (len(sigma) == len(tc64) == len(tc96)):
        raise ValueError("The two Tc series must have the same sample count")
    delta = [a - b for a, b in zip(tc64, tc96)]
    roots = []
    for i, (d0, d1) in enumerate(zip(delta, delta[1:])):
        if d0 == 0.0:
            if i == 0 or delta[i - 1] != 0.0:
                roots.append({
                    "sigma_ry": sigma[i],
                    "tc_k": (tc64[i] + tc96[i]) / 2.0,
                    "tc64_k": tc64[i],
                    "tc96_k": tc96[i],
                    "sigma_bracket_ry": [sigma[i], sigma[i]],
                    "delta_bracket_k": [d0, d0],
                })
        elif d0 * d1 < 0.0:
            x0, x1 = sigma[i], sigma[i + 1]
            x = x0 - d0 * (x1 - x0) / (d1 - d0)
            y64 = _interp(x, x0, x1, tc64[i], tc64[i + 1])
            y96 = _interp(x, x0, x1, tc96[i], tc96[i + 1])
            roots.append({
                "sigma_ry": x,
                "tc_k": (y64 + y96) / 2.0,
                "tc64_k": y64,
                "tc96_k": y96,
                "sigma_bracket_ry": [x0, x1],
                "delta_bracket_k": [d0, d1],
            })
    if delta and delta[-1] == 0.0 and (len(delta) == 1 or delta[-2] != 0.0):
        roots.append({
            "sigma_ry": sigma[-1],
            "tc_k": (tc64[-1] + tc96[-1]) / 2.0,
            "tc64_k": tc64[-1],
            "tc96_k": tc96[-1],
            "sigma_bracket_ry": [sigma[-1], sigma[-1]],
            "delta_bracket_k": [0.0, 0.0],
        })
    return roots


def _source(path: Path, root: Path, first_line: bool = False) -> dict:
    record = {"path": str(path.relative_to(root)), "sha256": sha256(path)}
    if first_line:
        record["first_line"] = path.read_text().splitlines()[0]
    return record


def build_report(base: Path) -> dict:
    root = base.parent.parent.parent
    series = {}
    for label, suffix in (("emax10", ""), ("emax18", ".emax18")):
        p64 = load_series(base, "ph64", suffix)
        p96 = load_series(base, "ph96", suffix)
        if p64["sigma"] != p96["sigma"]:
            raise ValueError(f"{label}: ph64/ph96 sigma grids differ")
        roots = piecewise_linear_crossings(p64["sigma"], p64["tc"], p96["tc"])
        if label == "emax10":
            inputs = [
                _source(base / "ph64" / "lambdax.in", root, True),
                _source(base / "ph96" / "lambdax.in", root, True),
            ]
            protocol_status = "matched input records present"
        else:
            candidates = [
                _source(base / "ph64.1" / "lambdax.in", root, True),
                _source(base / "ph96.1" / "lambdax.in", root, True),
            ]
            inputs = {
                "output_input_record": None,
                "prepared_candidates_not_linked_to_outputs": candidates,
            }
            protocol_status = "unverified: saved output files are not linked to an executed input or command"
        series[label] = {
            "protocol_status": protocol_status,
            "inputs": inputs,
            "tables": [
                _source(p64["table_path"], root),
                _source(p96["table_path"], root),
                _source(p64["output_path"], root),
                _source(p96["output_path"], root),
            ],
            "intersection_count": len(roots),
            "intersections": roots,
        }
    return {
        "schema_version": 1,
        "purpose": "Arithmetic audit of stored Tc tables; not a material convergence result.",
        "method": "Piecewise-linear interpolation between adjacent Tc samples where Tc64-Tc96 changes sign.",
        "stored_tc_resolution_k": 0.001,
        "interpretation": "Interpolated digits reflect arithmetic on Tc values printed to 0.001 K, not physical precision.",
        "series": series,
        "limitations": [
            "The emax18 stored outputs do not have a linked executed input, QE executable identity, or run command.",
            "The ph64.1/ph96.1 input files are prepared candidates and have no complete matching Tc output pair.",
            "The emax18 table roots cannot be attributed to changing only the frequency cutoff until provenance is closed.",
            "A crossing between two sampled electron meshes does not establish physical k/q convergence.",
        ],
    }


def write_report(base: Path) -> Path:
    report = build_report(base)
    output = base / "tc-intersections.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return output
