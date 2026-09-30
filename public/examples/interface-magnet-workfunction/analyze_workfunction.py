#!/usr/bin/env python3
"""Rebuild planar potential and vacuum-referenced levels from VASP outputs.

Required files in the current directory: LOCPOT, OUTCAR, EIGENVAL.
The reader is intentionally restricted to a non-spin-polarized, gapped,
single-scalar LOCPOT case. It rejects unsupported inputs instead of guessing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np

A = np.asarray


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_locpot(path: Path):
    lines = path.read_text(errors="strict").splitlines()
    if len(lines) < 10:
        raise ValueError("LOCPOT is too short to contain a POSCAR header and grid")
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError("This example reader requires a positive POSCAR scale")
    cell = A([[float(x) * scale for x in lines[i].split()[:3]]
              for i in (2, 3, 4)], dtype=float)
    index = 5
    species_or_counts = lines[index].split()
    index += 1
    if all(re.fullmatch(r"\d+", word) for word in species_or_counts):
        counts = [int(word) for word in species_or_counts]
    else:
        counts = [int(word) for word in lines[index].split()]
        index += 1
    mode = lines[index].strip().lower()
    index += 1
    if mode.startswith("s"):
        mode = lines[index].strip().lower()
        index += 1
    if not (mode.startswith("d") or mode.startswith("c") or mode.startswith("k")):
        raise ValueError(f"Unrecognized coordinate mode in LOCPOT header: {mode!r}")
    natoms = sum(counts)
    if natoms <= 0:
        raise ValueError("Invalid atom counts in LOCPOT header")
    index += natoms
    while index < len(lines) and not lines[index].strip():
        index += 1
    grid = tuple(map(int, lines[index].split()))
    index += 1
    if len(grid) != 3 or min(grid) <= 0:
        raise ValueError(f"Invalid LOCPOT grid dimensions: {grid}")
    nx, ny, nz = grid
    expected = nx * ny * nz
    fields = []
    for line in lines[index:]:
        fields.extend(float(token.replace("D", "E").replace("d", "e"))
                      for token in line.split())
    if len(fields) != expected:
        raise ValueError(
            f"Expected one scalar potential block ({expected} values), found {len(fields)}"
        )
    values = np.asarray(fields, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("LOCPOT contains non-finite potential values")
    normal = np.cross(cell[0], cell[1])
    area = np.linalg.norm(normal)
    if area == 0:
        raise ValueError("The first two lattice vectors do not span a surface")
    normal_height = abs(float(np.dot(cell[2], normal))) / area
    if normal_height <= 0:
        raise ValueError("Invalid cell height along the surface normal")
    # VASP writes x fastest, then y, with z as the slowest index.
    field = values.reshape((nz, ny, nx))
    planar = field.mean(axis=(1, 2))
    z = np.arange(nz, dtype=float) * normal_height / nz
    return grid, normal_height, z, planar


def outcar_values(path: Path):
    text = path.read_text(errors="strict")
    if "aborting loop because EDIFF is reached" not in text:
        raise ValueError("OUTCAR has no EDIFF convergence marker")
    if "General timing and accounting" not in text:
        raise ValueError("OUTCAR has no final timing/accounting section")
    if "LVHAR" not in text or not re.search(r"LVHAR\s*=\s*T\b", text):
        raise ValueError("OUTCAR does not confirm LVHAR=T")
    if re.search(r"LVTOT\s*=\s*T\b", text):
        raise ValueError("OUTCAR also has LVTOT=T; this route expects LVHAR only")
    ispin = re.findall(r"^\s*ISPIN\s*=\s*(\d+)", text, flags=re.M)
    nelect = re.findall(r"^\s*NELECT\s*=\s*([-+0-9.]+)", text, flags=re.M)
    efermi = re.findall(r"E-fermi\s*:\s*([-+0-9.]+)", text)
    if not ispin or int(ispin[-1]) != 1:
        raise ValueError("This band-edge reader requires a non-spin-polarized ISPIN=1 run")
    if not nelect or not efermi:
        raise ValueError("OUTCAR is missing NELECT or E-fermi")
    return int(round(float(nelect[-1]))), float(efermi[-1])


def read_eigenval(path: Path, expected_electrons: int):
    with path.open() as stream:
        for _ in range(5):
            if not stream.readline():
                raise ValueError("EIGENVAL ended before its electron/k-point/band header")
        try:
            electrons, nkpoints, nbands = map(int, stream.readline().split())
        except Exception as exc:
            raise ValueError("Invalid EIGENVAL electron/k-point/band header") from exc
        if electrons != expected_electrons:
            raise ValueError(
                f"EIGENVAL has {electrons} electrons but OUTCAR has {expected_electrons}"
            )
        if electrons % 2:
            raise ValueError("An even electron count is required for this ISPIN=1 example")
        nocc = electrons // 2
        if not (0 < nocc < nbands):
            raise ValueError("EIGENVAL does not contain both occupied and empty bands")
        k_weights, energies, occupations = [], [], []
        for _ in range(nkpoints):
            line = stream.readline()
            while line and not line.strip():
                line = stream.readline()
            if not line:
                raise ValueError("EIGENVAL ended before all k-point blocks were read")
            point = list(map(float, line.split()))
            if len(point) != 4:
                raise ValueError("Expected kx ky kz weight on each EIGENVAL k-point line")
            k_weights.append(point[3])
            e_k, occ_k = [], []
            for _ in range(nbands):
                row = stream.readline().split()
                if len(row) != 3:
                    raise ValueError("Expected band index, energy, and occupation (ISPIN=1)")
                band_index, energy, occupation = map(float, row)
                e_k.append(energy)
                occ_k.append(occupation)
            energies.append(e_k)
            occupations.append(occ_k)
    weights = np.asarray(k_weights, dtype=float)
    eigenvalues = np.asarray(energies, dtype=float)
    occ = np.asarray(occupations, dtype=float)
    if abs(float(weights.sum()) - 1.0) > 1e-5:
        raise ValueError(f"EIGENVAL k-point weights sum to {weights.sum():.8g}, not 1")
    weighted_electrons = 2.0 * float(np.sum(weights[:, None] * occ))
    if abs(weighted_electrons - expected_electrons) > 1e-3:
        raise ValueError(
            f"Weighted EIGENVAL occupations give {weighted_electrons:.8f} electrons, "
            f"not {expected_electrons}"
        )
    if float(occ[:, nocc - 1].min()) < 0.5 or float(occ[:, nocc].max()) > 0.5:
        raise ValueError(
            "The NELECT/2 band boundary is partially occupied; this is not a gapped "
            "non-spin-polarized case"
        )
    vbm = float(eigenvalues[:, nocc - 1].max())
    cbm = float(eigenvalues[:, nocc].min())
    if cbm <= vbm:
        raise ValueError("Sampled EIGENVAL band edges do not form a positive gap")
    return {
        "electrons": electrons,
        "nkpoints": nkpoints,
        "bands": nbands,
        "weighted_electrons": weighted_electrons,
        "vbm_eV": vbm,
        "cbm_eV": cbm,
        "indirect_gap_eV": cbm - vbm,
    }


def parse_window(spec: str):
    try:
        low, high = map(float, spec.split(":"))
    except Exception as exc:
        raise argparse.ArgumentTypeError("Use a window such as 1:3 (angstrom)") from exc
    if not (math.isfinite(low) and math.isfinite(high) and low < high):
        raise argparse.ArgumentTypeError("Window endpoints must be finite with low < high")
    return low, high


def main():
    parser = argparse.ArgumentParser(
        description="Average LVHAR from LOCPOT and align the gapped band edges to vacuum."
    )
    parser.add_argument(
        "--windows", nargs="+", type=parse_window, default=[(1.0, 3.0), (15.0, 17.0)],
        metavar="LOW:HIGH", help="vacuum windows in angstrom (default: 1:3 15:17)"
    )
    args = parser.parse_args()
    if not args.windows:
        raise ValueError("At least one vacuum window is required")
    loct = Path("LOCPOT")
    outcar = Path("OUTCAR")
    eigenval = Path("EIGENVAL")
    if not all(path.is_file() for path in (loct, outcar, eigenval)):
        raise FileNotFoundError("Run in a directory containing LOCPOT, OUTCAR, EIGENVAL")

    grid, height, z, potential = read_locpot(loct)
    nelect, ef = outcar_values(outcar)
    bands = read_eigenval(eigenval, nelect)
    windows = []
    for low, high in args.windows:
        if low < 0 or high > height:
            raise ValueError(
                f"Window {low:g}:{high:g} A lies outside 0:{height:.8f} A"
            )
        chosen = (z >= low) & (z <= high)
        values = potential[chosen]
        if values.size == 0:
            raise ValueError(f"Window {low:g}:{high:g} A contains no LOCPOT planes")
        mean = float(values.mean())
        row = {
            "lo_A": low, "hi_A": high, "n": int(values.size),
            "mean_eV": mean,
            "std_eV": float(values.std(ddof=0)),
            "range_eV": float(values.max() - values.min()),
            "vacuum_minus_fermi_eV": mean - ef,
            "vacuum_minus_vbm_eV": mean - bands["vbm_eV"],
            "vacuum_minus_cbm_eV": mean - bands["cbm_eV"],
        }
        windows.append(row)

    order = sorted(windows, key=lambda item: item["lo_A"])
    for left, right in zip(order, order[1:]):
        if left["hi_A"] > right["lo_A"]:
            raise ValueError("Vacuum windows overlap")

    np.savetxt(
        "PLANAR_AVERAGE.dat", np.column_stack((z, potential)),
        fmt=("%.10f", "%.12f"),
        header="z_A  planar_potential_eV",
        comments="# ",
    )
    result = {
        "code": "VASP",
        "potential_component": "LVHAR (ionic + Hartree; LVTOT is false)",
        "surface_normal": "normal to lattice vectors a and b",
        "normal_height_A": height,
        "grid": list(grid),
        "scalar_values": int(np.prod(grid)),
        "ispin": 1,
        "electrons": nelect,
        "nkpoints": bands["nkpoints"],
        "bands": bands["bands"],
        "weighted_electrons": bands["weighted_electrons"],
        "fermi_eV": ef,
        "vbm_eV": bands["vbm_eV"],
        "cbm_eV": bands["cbm_eV"],
        "indirect_gap_eV": bands["indirect_gap_eV"],
        "formula": {
            "work_function_eV": "V_vacuum - E_F",
            "ionization_potential_eV": "V_vacuum - VBM",
            "electron_affinity_eV": "V_vacuum - CBM",
            "potential_spread_eV": "max(Vbar) - min(Vbar) within each selected window",
        },
        "windows": windows,
        "input_sha256": {
            path.name: sha256(path) for path in (loct, outcar, eigenval)
        },
        "limits": [
            "EIGENVAL band edges are extrema on the sampled SCF k mesh, not a continuous-Brillouin-zone search.",
            "E_F in a semiconductor is the chemical potential printed for this occupation setup; it can move within the gap.",
            "Window spread is a local flatness diagnostic, not an uncertainty or convergence estimate.",
        ],
    }
    Path("workfunction-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(
        f"grid={grid}; scalar values={int(np.prod(grid))}; normal height={height:.10f} A"
    )
    print(
        f"NELECT={nelect}; NKPTS={bands['nkpoints']}; weighted electrons="
        f"{bands['weighted_electrons']:.8f}; E_F={ef:.6f} eV"
    )
    print(
        f"sampled VBM={bands['vbm_eV']:.6f} eV; CBM={bands['cbm_eV']:.6f} eV; "
        f"gap={bands['indirect_gap_eV']:.6f} eV"
    )
    for item in windows:
        print(
            f"z={item['lo_A']:.2f}:{item['hi_A']:.2f} A N={item['n']} "
            f"V_vac={item['mean_eV']:.9f} eV std={item['std_eV']:.6g} eV "
            f"range={item['range_eV']:.6g} eV Phi={item['vacuum_minus_fermi_eV']:.9f} eV"
        )


if __name__ == "__main__":
    main()
