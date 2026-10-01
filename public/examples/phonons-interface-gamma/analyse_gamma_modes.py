#!/usr/bin/env python3
"""Read accepted real-Gamma QE 7.2 matrices; export mode weights and AXSF frames.

crystal ASR acts on real Cartesian force constants before mass weighting.
Only these real Hermitian Gamma data are supported. No DFT or job submission.
"""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np
from scipy.linalg import null_space

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "gamma16": "c692eab1e220ed8f43a9d8714755f5462d227e6ccaa4d1a331ebb8b40e13b5e6",
    "gamma32": "833f0fbe22d8bb679acfe785b92add032223f6d48fb539ba15eafb2013e154e7",
}
H_PLANCK = 6.62607015e-34
HARTREE = 4.3597447222071e-18
C_LIGHT = 2.99792458e8
AU_PS = H_PLANCK / (2 * np.pi * HARTREE) * 1e12
RY_CM = 1e10 / (AU_PS * 4 * np.pi * C_LIGHT)
BOHR_A = 0.529177210903
LAYERS = {"ZrCl2": [0, 2, 3], "Sc2C": [1, 4, 5]}


def load(path):
    lines = path.read_text().splitlines()
    ntype, nat = map(int, lines[2].split()[:2])
    alat = float(lines[2].split()[3])
    i = lines.index("Basis vectors")
    cell = np.array([list(map(float, l.split())) for l in lines[i+1:i+4]]) * alat * BOHR_A
    species = {}
    for line in lines[i+4:i+4+ntype]:
        match = re.fullmatch(r"\s*(\d+)\s+'([^']+)'\s+(\S+)\s*", line)
        species[int(match[1])] = (match[2].strip(), float(match[3]))
    atomlines = [l.split() for l in lines[i+4+ntype:i+4+ntype+nat]]
    symbols = [species[int(l[1])][0] for l in atomlines]
    mass = np.array([species[int(l[1])][1] for l in atomlines])
    positions = np.array([list(map(float, l[2:5])) for l in atomlines]) * alat * BOHR_A
    qline = next(j for j, l in enumerate(lines) if re.match(r"\s*q\s*=", l))
    q = np.fromstring(re.search(r"\(([^)]+)\)", lines[qline])[1], sep=" ")
    assert np.allclose(q, 0) and symbols == ["Zr", "C", "Cl", "Cl", "Sc", "Sc"]
    force = np.zeros((3*nat, 3*nat), complex)
    j = qline + 1
    for _ in range(nat*nat):
        while not lines[j].strip(): j += 1
        a, b = map(int, lines[j].split())
        for alpha in range(3):
            row = np.array(list(map(float, lines[j+1+alpha].split())))
            force[3*(a-1)+alpha, 3*(b-1):3*b] = row[::2] + 1j*row[1::2]
        j += 4
    printed = np.array([float(m[1]) for l in lines
                        for m in [re.search(r"freq.*=\s*([-+\d.]+)\s*\[cm-1\]", l)] if m])
    assert printed.size == 3*nat
    assert np.max(np.abs(force.imag)) < 1e-12
    assert np.linalg.norm(force-force.conj().T) < 1e-12
    return force.real, mass, symbols, cell, positions, printed


def frequency(v):
    return np.sign(v) * np.sqrt(np.abs(v)) * RY_CM


def save_axsf(path, symbols, cell, positions, normalized_u):
    # Common scale for the entire mode; max atomic excursion = 0.10 Angstrom.
    # 36 equally spaced phases cover one period. This is a visualization scale,
    # not a thermal displacement or a finite-distortion energy calculation.
    amplitude = 0.10 / np.max(np.linalg.norm(normalized_u, axis=1))
    frames = ["ANIMSTEPS 36", "CRYSTAL", "PRIMVEC"]
    frames += [" ".join(f"{x:.12f}" for x in row) for row in cell]
    for step, phase in enumerate(np.linspace(0, 2*np.pi, 36, endpoint=False), 1):
        frames += [f"PRIMCOORD {step}", f"{len(symbols)} 1"]
        displaced = positions + amplitude * np.cos(phase) * normalized_u
        frames += [s + " " + " ".join(f"{x:.12f}" for x in row)
                   for s, row in zip(symbols, displaced)]
    path.write_text("\n".join(frames) + "\n")
    return amplitude


def main():
    report = {"q_fractional": [0, 0, 0], "structure": "ZrCl2/Sc2C +1.5%",
              "ASR": "real force-constant crystal projection; three translations",
              "frequency_unit": "cm-1", "mass_unit": "QE native amu_ry",
              "vector_definitions": {"e": "orthonormal mass-weighted eigenvector",
                  "u": "e/sqrt(M), then normalized over all atoms and directions"},
              "animation": "36 phases; shared mode scale, maximum excursion 0.10 Angstrom",
              "grids": {}}
    for label, expected in EXPECTED.items():
        source = ROOT / (label + ".dyn")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == expected, (label, digest)
        force, mass, symbols, cell, positions, printed = load(source)
        repeated = np.repeat(mass, 3)
        massscale = np.sqrt(repeated[:, None]*repeated[None, :])
        raw, _ = np.linalg.eigh(force/massscale)
        reproduction = float(np.max(np.abs(frequency(raw)-printed)))
        assert reproduction < 1e-4
        translation = np.kron(np.sqrt(mass[:, None]/mass.sum()), np.eye(3))
        uniform = np.kron(np.ones((len(mass), 1))/np.sqrt(len(mass)), np.eye(3))
        projector = np.eye(len(repeated)) - uniform @ uniform.T
        corrected = projector @ force @ projector
        optical = null_space(translation.T)
        value, basis = np.linalg.eigh(optical.T @ (corrected/massscale) @ optical)
        eigenvectors = optical @ basis
        displacements = eigenvectors/np.sqrt(repeated[:, None])
        displacements /= np.linalg.norm(displacements, axis=0)
        is_a = np.array([True, False, True, True, False, False])
        ma, mb = mass[is_a].sum(), mass[~is_a].sum()
        relative_atom = np.where(is_a, np.sqrt(mass)*np.sqrt(mb/(ma*(ma+mb))),
                                -np.sqrt(mass)*np.sqrt(ma/(mb*(ma+mb))))
        relative = np.kron(relative_atom[:, None], np.eye(3))
        relative_weight = np.abs(relative.T @ eigenvectors)**2
        modes = []
        with (ROOT / (label + "-vectors.csv")).open("w") as handle:
            writer = csv.writer(handle)
            writer.writerow(["optical_mode", "frequency_cm1", "atom", "symbol",
                             "ex", "ey", "ez", "ux", "uy", "uz", "atom_e_weight"])
            for k, w in enumerate(frequency(value)):
                e = eigenvectors[:, k].reshape(-1, 3)
                u = displacements[:, k].reshape(-1, 3)
                weights = np.sum(e**2, axis=1)
                for atom, symbol in enumerate(symbols):
                    writer.writerow([k+1, w, atom+1, symbol, *e[atom], *u[atom], weights[atom]])
                mode = {"optical_mode": k+1, "full_mode_after_three_translations": k+4,
                        "frequency_cm1": float(w), "e": e.tolist(), "u": u.tolist(),
                        "atom_e_weights": weights.tolist(),
                        "layer_e_weights": {g: float(weights[ids].sum()) for g, ids in LAYERS.items()},
                        "relative_inplane_template_weight": float(relative_weight[:2, k].sum()),
                        "relative_outofplane_template_weight": float(relative_weight[2, k])}
                if k < 3:
                    mode["axsf_common_scale_A"] = save_axsf(
                        ROOT / f"{label}-optical-{k+1}.axsf", symbols, cell, positions, u)
                modes.append(mode)
        report["grids"][label] = {"source": source.name, "sha256": digest,
                                 "raw_reproduction_max_error_cm1": reproduction,
                                 "symbols": symbols, "positions_A": positions.tolist(),
                                 "cell_A": cell.tolist(), "modes": modes}
        print(label, "lowest optical cm-1:", " ".join(f"{m['frequency_cm1']:.8f}" for m in modes[:3]))
        print("  lowest E pair relative-inplane weight:",
              " ".join(f"{m['relative_inplane_template_weight']:.8f}" for m in modes[:2]))
        print(f"  raw matrix reproduction max error: {reproduction:.3e} cm-1")
    (ROOT / "gamma-mode-products.json").write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__": main()
