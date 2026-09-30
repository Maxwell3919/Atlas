#!/usr/bin/env python3
"""Export vacuum-referenced band-edge and facing-surface tables from analysis JSON.

Standard library only. Run from this directory after analyze_alignment.py.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "alignment-summary.json"


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    summary = json.loads(SOURCE.read_text(encoding="utf-8"))
    layer_rows: list[dict[str, object]] = []
    for material, layer in summary["layers"].items():
        extrema = {
            "vbm_minus_vacuum_eV": "",
            "cbm_minus_vacuum_eV": "",
        }
        for window in layer["windows"]:
            layer_rows.append({
                "material": material,
                "surface": window["side"],
                "vacuum_window_A": f'{window["lo_A"]:.1f}:{window["hi_A"]:.1f}',
                "vacuum_mean_eV": f'{window["mean_eV"]:.9f}',
                "vacuum_range_eV": f'{window["range_eV"]:.9g}',
                "fermi_minus_vacuum_eV": f'{window["fermi_minus_vacuum_eV"]:.9f}',
                "vbm_minus_vacuum_eV": f'{window.get("vbm_minus_vacuum_eV", ""):.9f}' if "vbm_minus_vacuum_eV" in window else "",
                "cbm_minus_vacuum_eV": f'{window.get("cbm_minus_vacuum_eV", ""):.9f}' if "cbm_minus_vacuum_eV" in window else "",
                "sampled_gap_eV": f'{layer["gap_eV"]:.9f}' if "gap_eV" in layer else "",
                "classification": layer["classification"],
            })
    write_csv(ROOT / "band-edges-vacuum-referenced.csv", [
        "material", "surface", "vacuum_window_A", "vacuum_mean_eV",
        "vacuum_range_eV", "fermi_minus_vacuum_eV",
        "vbm_minus_vacuum_eV", "cbm_minus_vacuum_eV",
        "sampled_gap_eV", "classification",
    ], layer_rows)

    facing = summary["interface_facing_isolated_reference"]
    offsets = [
        {
            "quantity": "CBM(SnSe2, lower-z) - EF(Sr2N, upper-z)",
            "value_eV": f'{facing["cbm_minus_metal_fermi_eV"]:.9f}',
            "meaning": "vacuum-referenced isolated-layer edge offset",
            "scope": facing["scope"],
        },
        {
            "quantity": "EF(Sr2N, upper-z) - VBM(SnSe2, lower-z)",
            "value_eV": f'{facing["metal_fermi_minus_vbm_eV"]:.9f}',
            "meaning": "vacuum-referenced isolated-layer edge offset",
            "scope": facing["scope"],
        },
    ]
    write_csv(ROOT / "facing-surface-offsets.csv", [
        "quantity", "value_eV", "meaning", "scope",
    ], offsets)

    print(f"Wrote {len(layer_rows)} surface rows to band-edges-vacuum-referenced.csv")
    print(f"Wrote {len(offsets)} facing offsets to facing-surface-offsets.csv")


if __name__ == "__main__":
    main()
