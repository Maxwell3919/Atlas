#!/usr/bin/env python3
"""Split the two spin-resolved scalar ELF grids in one VASP ELFCAR.

VASP ISPIN=2 writes ELF_up first and ELF_down second. This script copies the
same POSCAR-style geometry header to two VESTA-readable files, each followed
by exactly one scalar grid. It does not add, average, or otherwise combine
the spin channels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

_GRID = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s*$")


def grid_dims(line: str) -> tuple[int, int, int] | None:
    match = _GRID.fullmatch(line)
    return tuple(map(int, match.groups())) if match else None


def read_grid(lines: list[str], start: int, npoints: int, label: str) -> tuple[list[float], int]:
    values: list[float] = []
    cursor = start
    while len(values) < npoints:
        if cursor >= len(lines):
            raise ValueError(f"{label}: ended after {len(values)} of {npoints} values")
        tokens = lines[cursor].split()
        if not tokens:
            raise ValueError(f"{label}: unexpected blank line at grid value {len(values)}")
        row = [float(token.replace("D", "E").replace("d", "e")) for token in tokens]
        if len(values) + len(row) > npoints:
            raise ValueError(f"{label}: extra values on the final grid line")
        values.extend(row)
        cursor += 1
    if not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values):
        raise ValueError(f"{label}: ELF grid contains non-finite or out-of-range values")
    return values, cursor


def write_grid(path: Path, header: list[str], dims: tuple[int, int, int],
               values: list[float], channel: str) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    out_header = list(header)
    out_header[0] = f"Fe bcc FM ELF {channel}; one VASP spin-resolved scalar grid\n"
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.writelines(out_header)
        stream.write("  " + "  ".join(map(str, dims)) + "\n")
        for start in range(0, len(values), 5):
            stream.write(" ".join(f"{value: .8E}" for value in values[start:start + 5]) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="VASP ELFCAR from an ISPIN=2 run")
    parser.add_argument("--output-dir", required=True, type=Path, help="new directory for one-grid VESTA files")
    args = parser.parse_args()

    lines = args.input.read_text(encoding="ascii").splitlines(keepends=True)
    matches = [(index, grid_dims(line)) for index, line in enumerate(lines) if grid_dims(line)]
    matches = [(index, dims) for index, dims in matches if dims is not None]
    if len(matches) != 2:
        raise ValueError(f"Expected exactly two spin-grid headers, found {len(matches)}")
    first_index, dims = matches[0]
    second_index, second_dims = matches[1]
    if second_dims != dims:
        raise ValueError(f"Spin grid mismatch: {dims} vs {second_dims}")
    npoints = math.prod(dims)

    up, after_up = read_grid(lines, first_index + 1, npoints, "ELF_up")
    while after_up < len(lines) and not lines[after_up].strip():
        after_up += 1
    if after_up != second_index:
        raise ValueError(f"Unexpected data between spin channels at line {after_up + 1}")
    down, after_down = read_grid(lines, second_index + 1, npoints, "ELF_down")
    if any(line.strip() for line in lines[after_down:]):
        raise ValueError("Unexpected trailing content after the second ELF grid")

    header = lines[:first_index]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    up_path = args.output_dir / "ELFCAR_up.vasp"
    down_path = args.output_dir / "ELFCAR_down.vasp"
    summary = args.output_dir / "elf-spin-channels.summary.json"
    for path in (up_path, down_path, summary):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}")
    write_grid(up_path, header, dims, up, "spin-up")
    write_grid(down_path, header, dims, down, "spin-down")
    record = {
        "source": str(args.input),
        "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "source_spin_order": ["ELF_up", "ELF_down"],
        "grid": list(dims),
        "points_per_channel": npoints,
        "units": "dimensionless ELF values",
        "channels": {
            "up": {"file": up_path.name, "minimum": min(up), "maximum": max(up), "mean": sum(up) / npoints},
            "down": {"file": down_path.name, "minimum": min(down), "maximum": max(down), "mean": sum(down) / npoints},
        },
        "operation": "split only; no spin summation or averaging",
    }
    summary = args.output_dir / "elf-spin-channels.summary.json"
    if summary.exists():
        raise FileExistsError(f"Refusing to overwrite {summary}")
    summary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"source sha256: {record['source_sha256']}")
    print(f"grid: {dims[0]} {dims[1]} {dims[2]} ({npoints} points per spin channel)")
    for name, values in (("ELF_up", up), ("ELF_down", down)):
        print(f"{name}: min={min(values):.8f} max={max(values):.8f} mean={sum(values)/npoints:.8f}")
    print(f"wrote: {up_path}")
    print(f"wrote: {down_path}")
    print(f"summary: {summary}")


if __name__ == "__main__":
    main()

