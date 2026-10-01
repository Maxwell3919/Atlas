#!/usr/bin/env python3
"""Build a VESTA-readable VASP volumetric file for Δρ = ρ(AB) − ρ(A) − ρ(B).

Inputs are CHGCAR files (plain text or gzip-compressed).  The script reads only
VASP's first total-charge grid block; magnetization and PAW augmentation blocks
are not part of the plotted scalar field.  The output keeps VASP's stored
volume-scaled values, so divide a grid value by cell volume (Å³) to get e/Å³.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import Iterable, TextIO

import numpy as np

_INTEGER = re.compile(r"^[+-]?\d+$")


def _open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="ascii", errors="strict")
    return path.open("rt", encoding="ascii", errors="strict")


def _line(stream: TextIO, label: str) -> str:
    value = stream.readline()
    if not value:
        raise ValueError(f"Unexpected end of file while reading {label}")
    return value


def _ints(tokens: list[str]) -> bool:
    return bool(tokens) and all(_INTEGER.fullmatch(token) for token in tokens)


def _float(token: str) -> float:
    return float(token.replace("D", "E").replace("d", "e"))


def _float_values(stream: TextIO) -> Iterable[float]:
    for line in stream:
        for token in line.split():
            yield _float(token)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_uncompressed(path: Path) -> str:
    opener = gzip.open if path.suffix.lower() == ".gz" else open
    digest = hashlib.sha256()
    with opener(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_chgcar(path: Path) -> dict:
    """Parse cell/atoms, one 3-D total-charge block, and its exact VASP header."""
    header: list[str] = []
    with _open_text(path) as stream:
        title = _line(stream, "title")
        header.append(title)
        scale_tokens = _line(stream, "scale factor").split()
        header.append(" ".join(scale_tokens) + "\n")
        if not scale_tokens:
            raise ValueError(f"{path}: missing scale factor")
        scale = _float(scale_tokens[0])

        raw_cell = []
        for axis in "abc":
            row = _line(stream, f"lattice vector {axis}")
            header.append(row)
            values = [_float(token) for token in row.split()[:3]]
            if len(values) != 3:
                raise ValueError(f"{path}: invalid lattice vector {axis}")
            raw_cell.append(values)
        raw_cell = np.asarray(raw_cell, dtype=np.float64)
        raw_volume = abs(float(np.linalg.det(raw_cell)))
        if raw_volume <= 0 or scale == 0:
            raise ValueError(f"{path}: invalid cell volume or scale factor")
        factor = scale if scale > 0 else (abs(scale) / raw_volume) ** (1.0 / 3.0)
        cell = raw_cell * factor

        species_or_counts = _line(stream, "species/count line")
        header.append(species_or_counts)
        fields = species_or_counts.split()
        if _ints(fields):
            counts = [int(token) for token in fields]
            species = [f"X{i + 1}" for i in range(len(counts))]
        else:
            species = fields
            count_line = _line(stream, "atom counts")
            header.append(count_line)
            count_fields = count_line.split()
            if not _ints(count_fields):
                raise ValueError(f"{path}: atom-count line is not integer-valued")
            counts = [int(token) for token in count_fields]
        if len(species) != len(counts) or any(count <= 0 for count in counts):
            raise ValueError(f"{path}: invalid species/count list")
        atom_species = [symbol for symbol, count in zip(species, counts) for _ in range(count)]

        coordinate_line = _line(stream, "coordinate mode or selective-dynamics line")
        header.append(coordinate_line)
        if coordinate_line.strip().lower().startswith("s"):
            coordinate_line = _line(stream, "coordinate mode")
            header.append(coordinate_line)
        mode = coordinate_line.strip().lower()
        if not mode or mode[0] not in {"d", "c", "k"}:
            raise ValueError(f"{path}: unknown coordinate mode {coordinate_line!r}")

        fractional_or_cartesian = []
        for atom_index in range(len(atom_species)):
            atom_line = _line(stream, f"atom coordinate {atom_index + 1}")
            header.append(atom_line)
            xyz = [_float(token) for token in atom_line.split()[:3]]
            if len(xyz) != 3:
                raise ValueError(f"{path}: invalid coordinate for atom {atom_index + 1}")
            fractional_or_cartesian.append(xyz)
        coordinates = np.asarray(fractional_or_cartesian, dtype=np.float64)
        cartesian = coordinates @ cell if mode[0] == "d" else coordinates * factor

        dimensions = None
        for _ in range(40):
            candidate = _line(stream, "grid dimensions")
            header.append(candidate)
            fields = candidate.split()
            if _ints(fields) and len(fields) == 3 and all(int(value) > 0 for value in fields):
                dimensions = tuple(int(value) for value in fields)
                break
        if dimensions is None:
            raise ValueError(f"{path}: no 3-D grid dimensions after the structure header")

        npoints = math.prod(dimensions)
        values = np.fromiter(itertools.islice(_float_values(stream), npoints),
                             dtype=np.float64, count=npoints)
        if values.size != npoints:
            raise ValueError(f"{path}: expected {npoints} charge values, read {values.size}")

    return {
        "path": path,
        "header": header,
        "cell": cell,
        "volume_A3": abs(float(np.linalg.det(cell))),
        "species": atom_species,
        "cartesian_A": cartesian,
        "dimensions": dimensions,
        "values": values,
        "sha256_gz_or_file": _sha256_file(path),
        "sha256_uncompressed": _sha256_uncompressed(path),
    }


def check_same_cell_and_grid(data: dict[str, dict]) -> None:
    reference = data["AB"]
    for label in ("A", "B"):
        item = data[label]
        if item["dimensions"] != reference["dimensions"]:
            raise ValueError(f"{label} grid {item['dimensions']} != AB grid {reference['dimensions']}")
        if not np.allclose(item["cell"], reference["cell"], rtol=0.0, atol=1e-8):
            raise ValueError(f"{label} cell vectors differ from AB")
    if len(reference["species"]) != len(data["A"]["species"]) + len(data["B"]["species"]):
        raise ValueError("AB atom count must equal A plus B")

    # Verify that A and B retain the corresponding AB atomic coordinates.
    remaining = list(range(len(reference["species"])))
    for label in ("A", "B"):
        item = data[label]
        for symbol, xyz in zip(item["species"], item["cartesian_A"]):
            matches = [i for i in remaining
                       if reference["species"][i] == symbol
                       and np.allclose(reference["cartesian_A"][i], xyz, rtol=0.0, atol=1e-6)]
            if not matches:
                raise ValueError(f"{label} atom {symbol} at {xyz} Å is not an AB atom at that position")
            remaining.remove(matches[0])
    if remaining:
        raise ValueError(f"A/B references did not account for AB atom indices {remaining}")


def write_grid(path: Path, header: list[str], values: np.ndarray) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}; choose another output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    out_header = list(header)
    out_header[0] = "H2 delta density rho_AB-rho_A-rho_B; VASP volume-scaled grid values\n"
    with path.open("wt", encoding="ascii", newline="\n") as stream:
        stream.writelines(out_header)
        for start in range(0, values.size, 5):
            chunk = values[start:start + 5]
            stream.write(" ".join(f"{value: .11E}" for value in chunk) + "\n")


def build(ab: Path, a: Path, b: Path, output: Path, summary: Path) -> dict:
    for path in (output, summary):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}; choose a new output path")
    if output.resolve() == summary.resolve():
        raise ValueError("Output and summary must have different paths")
    data = {"AB": read_chgcar(ab), "A": read_chgcar(a), "B": read_chgcar(b)}
    check_same_cell_and_grid(data)
    npoints = math.prod(data["AB"]["dimensions"])
    volume = data["AB"]["volume_A3"]
    delta_stored = data["AB"]["values"] - data["A"]["values"] - data["B"]["values"]
    delta_rho = delta_stored / volume

    total_e = float(np.sum(delta_stored, dtype=np.float64) / npoints)
    positive_e = float(np.sum(np.maximum(delta_stored, 0.0), dtype=np.float64) / npoints)
    negative_e = float(np.sum(np.minimum(delta_stored, 0.0), dtype=np.float64) / npoints)
    if abs(total_e) > 1e-6:
        raise ValueError(f"Difference density does not conserve charge: integral={total_e:.9g} e")

    if not all(np.isfinite(item["values"]).all() for item in data.values()):
        raise ValueError("Input grid contains non-finite values")
    write_grid(output, data["AB"]["header"], delta_stored)
    record = {
        "source": {label: {"path": str(item["path"]),
                           "sha256_file": item["sha256_gz_or_file"],
                           "sha256_uncompressed": item["sha256_uncompressed"]}
                   for label, item in data.items()},
        "output": str(output),
        "formula": "rho_AB(r) - rho_A(r) - rho_B(r)",
        "grid": list(data["AB"]["dimensions"]),
        "volume_A3": volume,
        "points": npoints,
        "grid_value_convention": "VASP CHGCAR values are rho(r) * cell_volume; divide this output's grid values by volume_A3 to obtain e/Angstrom^3.",
        "minimum_delta_rho_e_A3": float(np.min(delta_rho)),
        "maximum_delta_rho_e_A3": float(np.max(delta_rho)),
        "delta_integral_e": total_e,
        "negative_integral_e": negative_e,
        "positive_integral_e": positive_e,
        "vesta_symmetric_threshold_grid_value": 30.0,
        "equivalent_threshold_e_A3": 30.0 / volume,
        "input_grid_integrals_e": {
            label: float(np.sum(item["values"], dtype=np.float64) / npoints)
            for label, item in data.items()
        },
        "output_sha256": _sha256_file(output),
    }
    summary.parent.mkdir(parents=True, exist_ok=True)
    if summary.exists():
        raise FileExistsError(f"Refusing to overwrite {summary}; choose another summary path")
    summary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ab", type=Path, required=True, help="AB CHGCAR or CHGCAR.gz")
    parser.add_argument("--a", type=Path, required=True, help="A CHGCAR or CHGCAR.gz")
    parser.add_argument("--b", type=Path, required=True, help="B CHGCAR or CHGCAR.gz")
    parser.add_argument("--output", type=Path, required=True, help="New VESTA-readable VASP volumetric file")
    parser.add_argument("--summary", type=Path, required=True, help="New JSON validation summary")
    args = parser.parse_args()
    result = build(args.ab, args.a, args.b, args.output, args.summary)
    print(f"grid: {result['grid'][0]} {result['grid'][1]} {result['grid'][2]}")
    print(f"volume: {result['volume_A3']:.6f} Å^3")
    print(f"integrals A/B/AB: {result['input_grid_integrals_e']['A']:.9f} / "
          f"{result['input_grid_integrals_e']['B']:.9f} / {result['input_grid_integrals_e']['AB']:.9f} e")
    print(f"delta integral: {result['delta_integral_e']:.3e} e")
    print(f"delta rho min/max: {result['minimum_delta_rho_e_A3']:.6f} / "
          f"{result['maximum_delta_rho_e_A3']:.6f} e/Å^3")
    print(f"±{result['equivalent_threshold_e_A3']:.3f} e/Å^3 maps to ±{result['vesta_symmetric_threshold_grid_value']:.1f} stored VASP grid values (VESTA display units must be checked)")
    print(f"wrote: {result['output']}")
    print(f"summary: {args.summary}")


if __name__ == "__main__":
    main()
