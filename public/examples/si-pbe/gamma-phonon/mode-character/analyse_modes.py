"""Read the two saved QE 7.5 Si Gamma displacement files; no DFT rerun.

Run in this directory: python3 analyse_modes.py
Requires NumPy. This intentionally validates only the supplied equal-mass,
two-atom Si Gamma example. It is not a general phonon file converter.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parent
BOHR_ANGSTROM = 0.529177210903
NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[EeDd][-+]?\d+)?"

def number(text):
    return float(text.replace("D", "E").replace("d", "e"))

def modes(filename):
    text = (ROOT / filename).read_text()
    q = re.search(r"q\s*=\s*("+NUMBER+r")\s+("+NUMBER+r")\s+("+NUMBER+r")", text)
    if q is None or not np.allclose([number(x) for x in q.groups()], 0, atol=1e-12, rtol=0):
        raise ValueError("This diagnostic requires Gamma: " + filename)
    pattern = re.compile(r"freq\s*\(\s*(\d+)\)\s*=.*?=\s*("+NUMBER+r")\s*\[cm-1\]")
    hits = list(pattern.finditer(text))
    if [int(m[1]) for m in hits] != list(range(1, 7)):
        raise ValueError("Expected six consecutive modes: " + filename)
    frequencies, vectors = [], []
    for i, hit in enumerate(hits):
        end = hits[i+1].start() if i+1 < len(hits) else len(text)
        rows = re.findall(r"^\s*\(\s*([^\n]+?)\s*\)\s*$", text[hit.end():end], re.M)
        if len(rows) != 2:
            raise ValueError("Expected two atomic vectors per mode: " + filename)
        values = np.array([[number(s) for s in row.split()] for row in rows])
        if values.shape != (2, 6) or not np.isfinite(values).all():
            raise ValueError("Expected six finite real/imaginary columns per atom")
        frequencies.append(number(hit[2]))
        vectors.append(values[:, 0::2] + 1j*values[:, 1::2])
    return np.array(frequencies), np.array(vectors)

def geometry():
    lines = (ROOT / "si.dynG").read_text().splitlines()
    header = lines[2].split()
    if [int(x) for x in header[:3]] != [1, 2, 2] or "'Si" not in lines[3]:
        raise ValueError("Expected this two-atom, one-species fcc Si matrix")
    alat = number(header[3]) * BOHR_ANGSTROM
    rows = [line.split() for line in lines[4:6]]
    if [(int(x[0]), int(x[1])) for x in rows] != [(1, 1), (2, 1)]:
        raise ValueError("Unexpected atom/species order")
    return alat, np.array([[number(x) for x in row[2:5]] for row in rows])*alat

def projector(vectors):
    matrix = vectors.reshape(3, 6).T
    if np.linalg.matrix_rank(matrix, tol=1e-7) != 3:
        raise ValueError("A three-mode group lost rank")
    q, _ = np.linalg.qr(matrix)
    return q @ q.conj().T

def write_csv(name, header, rows):
    with (ROOT / name).open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)

alat, positions = geometry()
sets = {name: modes(filename) for name, filename in
        [("no", "si-no.modes"), ("crystal", "si-crystal.modes")]}
translation_basis = np.vstack([np.eye(3), np.eye(3)]) / np.sqrt(2)
p_translation = translation_basis @ translation_basis.T
records, arrows = [], []
summary = {"case": "Si, two equal-mass atoms, Gamma, fixed example geometry",
           "numpy_version": np.__version__, "alat_angstrom": alat,
           "scope": "Diagnostics of rounded filout displacements; no new phonon calculation",
           "maximum_imaginary_component": 0.0, "sets": {}, "subspace_comparison": {}}
for name, (frequencies, u) in sets.items():
    if not np.isfinite(frequencies).all():
        raise ValueError("Nonfinite frequency")
    norm = np.linalg.norm(u.reshape(6, 6), axis=1)
    if not np.allclose(norm, 1, atol=3e-6, rtol=0):
        raise ValueError("Displacements not normalized to printed precision")
    imaginary = float(np.max(np.abs(u.imag)))
    if imaginary > 1e-12:
        raise ValueError("The static real-arrow view is specific to these real Gamma modes")
    summary["maximum_imaginary_component"] = max(summary["maximum_imaginary_component"], imaginary)
    same = np.linalg.norm(u[:, 0]-u[:, 1], axis=1)/norm
    opposite = np.linalg.norm(u[:, 0]+u[:, 1], axis=1)/norm
    fraction = np.sum(np.abs(u[:, 0]+u[:, 1])**2, axis=1)/(2*norm**2)
    if np.any(fraction < -1e-12) or np.any(fraction > 1+1e-12):
        raise ValueError("Invalid projection fraction")
    acoustic = projector(u[:3])
    optical = projector(u[3:])
    gram = (u.reshape(6, 6)/norm[:, None]) @ (u.reshape(6, 6)/norm[:, None]).conj().T
    summary["sets"][name] = {
        "max_norm_deviation": float(np.max(np.abs(norm-1))),
        "max_gram_deviation": float(np.max(np.abs(gram-np.eye(6)))),
        "acoustic_translation_projector_frobenius": float(np.linalg.norm(acoustic-p_translation)),
        "optical_translation_projector_frobenius": float(np.linalg.norm(optical-(np.eye(6)-p_translation))),
        "acoustic_frequency_range_cm-1": [float(x) for x in (frequencies[:3].min(), frequencies[:3].max())],
        "optical_frequency_range_cm-1": [float(x) for x in (frequencies[3:].min(), frequencies[3:].max())]}
    for i in range(6):
        records.append([name, i+1, frequencies[i], norm[i], same[i], opposite[i], fraction[i]])
        for atom in range(2):
            arrows.append([name, i+1, atom+1, *positions[atom], *u[i, atom].real, *u[i, atom].imag])
    print(f"ASR={name}: modes=6, atoms=2, max |norm-1|={np.max(np.abs(norm-1)):.3e}")
    print("  translation fraction: " + " ".join(f"{x:.6f}" for x in fraction))
for label, group in [("acoustic", slice(0, 3)), ("optical", slice(3, 6))]:
    delta = float(np.linalg.norm(projector(sets["no"][1][group])-projector(sets["crystal"][1][group])))
    summary["subspace_comparison"][label+"_projector_frobenius"] = delta
    print(f"{label} projector difference: {delta:.3e}")
summary["sha256"] = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
                     for f in ["si-no.modes", "si-crystal.modes", "si.dynG"]}
write_csv("mode-diagnostics.csv", ["asr", "mode", "frequency_cm-1", "displacement_norm",
          "same_displacement_residual", "opposite_displacement_residual", "translation_fraction"], records)
write_csv("mode-vectors.csv", ["asr", "mode", "atom", "x_angstrom", "y_angstrom", "z_angstrom",
          "ux_real", "uy_real", "uz_real", "ux_imag", "uy_imag", "uz_imag"], arrows)
(ROOT/"mode-checks.json").write_text(json.dumps(summary, indent=2)+"\n")
print("Wrote mode-diagnostics.csv, mode-vectors.csv, mode-checks.json")
