#!/usr/bin/env python3
"""Repack frozen SnSe2 CSVs for gnuplot; no smoothing or recalculation."""
import argparse
import csv
import math
from pathlib import Path


def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_new(path, rows):
    with path.open("x") as f:
        for row in rows:
            f.write(" ".join(format(x, ".12g") for x in row) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tables", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    path = read(args.tables / "path.csv")
    bands = read(args.tables / "bands.csv")
    dos = read(args.tables / "dos.csv")
    if len(path) != 150 or len(bands) != 3000 or len(dos) != 301:
        raise ValueError("This frozen example requires 150 k points, 20 bands, 301 DOS points")
    states = {}
    for row in bands:
        key = (int(row["k_index"]), int(row["band"]))
        if key in states:
            raise ValueError("Duplicate (k, band)")
        states[key] = row
    matrix = []
    zeros = []
    for i, p in enumerate(path, 1):
        if int(p["k_index"]) != i:
            raise ValueError("Path order changed")
        distance = float(p["distance_Ainv"])
        values = [distance]
        for band in range(1, 21):
            row = states[(i, band)]
            if abs(float(row["distance_Ainv"]) - distance) > 1e-10:
                raise ValueError("Path/band distance mismatch")
            relative = float(row["energy_minus_scf_EF_eV"])
            zeros.append(float(row["energy_eV"]) - relative)
            values.append(relative)
        matrix.append(values)
    if max(zeros) - min(zeros) > 1e-9 or abs(zeros[0] + 2.39071823) > 1e-9:
        raise ValueError("Energy zero differs from frozen SCF reference")
    spectra = [[float(row[k]) for k in
                ("total_DOS_states_per_eV_cell", "Sn_s", "Se_p", "energy_minus_scf_EF_eV")]
               for row in dos]
    if any(not math.isfinite(x) for row in matrix + spectra for x in row):
        raise ValueError("Non-finite input")
    if any(spectra[i][3] <= spectra[i - 1][3] for i in range(1, len(spectra))):
        raise ValueError("DOS energies are not increasing")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    destinations = [args.output_dir / n for n in ("snse2-bands.dat", "snse2-pdos.dat")]
    if any(p.exists() for p in destinations):
        raise FileExistsError("Use a new output directory; original results are retained")
    write_new(destinations[0], matrix)
    write_new(destinations[1], spectra)
    print("Bands: 150 rows x 21 columns; all 20 bands and duplicated segment endpoints retained")
    print("DOS: 301 rows x 4 columns; TDOS, Sn-s, summed Se-p, E-SCF_EF; no smoothing")
    print("Energy zero: SCF EF = -2.39071823 eV")


if __name__ == "__main__":
    main()
