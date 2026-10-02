#!/usr/bin/env python3
"""Resolve original Al J(q) into band pairs without phonon matrix elements."""
from pathlib import Path
import argparse, csv, json
import numpy as np

def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--al-root", type=Path, required=True,
                    help="Extracted al directory containing fermi/k24-cg and k32-cg")
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    if args.output_dir.exists():
        raise FileExistsError("Use a new output directory: " + str(args.output_dir))
    pairs, summaries, checks = [], [], []
    for n in [24, 32]:
        folder = args.al_root / "fermi" / f"k{n}-cg"
        with np.load(folder / "fermi-grid.npz", allow_pickle=False) as saved:
            energies = saved["energy_eV"].copy()
            grid = int(saved["grid"])
            ef = float(saved["fermi_eV"])
        info = json.loads((folder / "grid-info.json").read_text())
        if grid != n or energies.shape != (n, n, n, 6):
            raise ValueError("Expected the archived six-band complete Al grid")
        if not np.all(np.isfinite(energies)) or not np.isfinite(ef):
            raise ValueError("Non-finite energies or Fermi reference")
        if info["nks"] != n**3 or abs(info["fermi_eV"] - ef) > 1e-10:
            raise ValueError("Grid metadata differs")
        for sigma in [0.10, 0.20]:
            band_weight = np.exp(-0.5 * (energies / sigma)**2) / (
                sigma * np.sqrt(2 * np.pi))
            total_weight = band_weight.sum(axis=3)
            transform = np.fft.fftn(total_weight)
            joint = np.fft.ifftn(transform.conj() * transform).real / n**3
            zero = float(joint[0, 0, 0])
            tolerance = 1e-10 * max(1.0, zero)
            if zero <= 0 or np.min(joint) < -tolerance:
                raise ValueError("Invalid joint weight")
            if np.max(joint) > zero + tolerance:
                raise ValueError("Periodic autocorrelation exceeds J(0)")
            if abs(zero - float(np.mean(total_weight**2))) > tolerance:
                raise ValueError("q=0 direct sum differs")
            cut = np.loadtxt(folder / f"nesting-GX-s{sigma:.2f}.csv",
                             delimiter=",", skiprows=1)
            indices = np.arange(n//2 + 1)
            computed = joint[indices, 0, indices]
            if cut.shape != (n//2 + 1, 3):
                raise ValueError("Unexpected stored cut shape")
            if not np.allclose(cut[:, 0], indices/n, rtol=0, atol=1e-12):
                raise ValueError("Stored q coordinates differ")
            if not np.allclose(cut[:, 1], computed, rtol=1e-10, atol=1e-12):
                raise ValueError("Stored absolute J differs from FFT")
            if not np.allclose(cut[:, 2], computed/zero, rtol=1e-10, atol=1e-12):
                raise ValueError("Stored normalized J differs")
            for name, i in [("Gamma", 0), ("quarter", n//4), ("X", n//2)]:
                shift = (i, 0, i)
                shifted = np.roll(band_weight, tuple(-v for v in shift),
                                  axis=(0, 1, 2))
                matrix = (band_weight.reshape(-1, 6).T @
                          shifted.reshape(-1, 6)) / n**3
                direct = float(np.mean(total_weight *
                                       np.roll(total_weight, tuple(-v for v in shift),
                                               axis=(0, 1, 2))))
                total = float(matrix.sum())
                if abs(total - direct) > tolerance or abs(total - joint[shift]) > tolerance:
                    raise ValueError("Band-pair, direct and FFT sums differ")
                diagonal = float(np.trace(matrix))
                offdiagonal = float(matrix[~np.eye(6, dtype=bool)].sum())
                for band_n in range(6):
                    for band_m in range(6):
                        pairs.append({"kmesh": n, "sigma_eV": sigma,
                                      "q_name": name, "q_fraction_b1_plus_b3": i/n,
                                      "initial_band": band_n+1, "final_band": band_m+1,
                                      "J_pair_eV_minus2": float(matrix[band_n, band_m])})
                summaries.append({"kmesh": n, "sigma_eV": sigma,
                                  "q_name": name, "q_fraction_b1_plus_b3": i/n,
                                  "J_eV_minus2": total, "same_band_eV_minus2": diagonal,
                                  "different_band_eV_minus2": offdiagonal,
                                  "J_over_J0": total/zero})
                if name == "X":
                    print(f'{n}^3 sigma={sigma:.2f} eV: J(X)={total:.8f}; '
                          f'same-band={diagonal:.8f}; different-band={offdiagonal:.8f} eV^-2')
            checks.append({"kmesh": n, "sigma_eV": sigma,
                           "fermi_eV": ef, "all_six_bands_used": True,
                           "complete_grid_points": n**3, "stored_cut_reproduced": True,
                           "nonnegative_and_J_not_above_J0": True,
                           "band_pair_direct_FFT_agree": True})
    report = {"source_root": str(args.al_root), "numpy_version": np.__version__,
              "definition": "J_nm(q)=mean_k delta_sigma(E_n(k)-EF) delta_sigma(E_m(k+q)-EF)",
              "units": "eV^-2; all six bands; no added spin factor",
              "scope": "Geometric band-pair weights, not orbital/layer-resolved EPC or static susceptibility",
              "checks": checks, "summaries": summaries}
    args.output_dir.mkdir(parents=True)
    write_csv(args.output_dir / "band-pairs.csv", pairs)
    write_csv(args.output_dir / "band-pair-summary.csv", summaries)
    (args.output_dir / "band-pair-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f'{len(summaries)} q-point summaries; {len(pairs)} band-pair records; '
          'pair/direct/FFT sums, stored cuts and J(q)<=J(0) checked.')
    print("No matrix elements, mode assignment, occupation denominator or DFT calculation added.")

if __name__ == "__main__":
    main()
