#!/usr/bin/env python3
"""Quantify Al k32/k48 Eliashberg spectral and moment differences; no plotting."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read_a2f(path: Path):
    lines = path.read_text().splitlines()
    header = next((line.split() for line in lines if line.strip()), None)
    if not header or len(header) < 3:
        raise ValueError(f"{path}: missing frequency/sigma header")
    sigmas = [float(x) for x in header[2:]]
    groups = {sigma: [] for sigma in sigmas}
    for line in lines[1:]:
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        values = [float(x) for x in parts]
        if len(values) != len(sigmas) + 1 or any(not math.isfinite(x) for x in values):
            raise ValueError(f"{path}: malformed/non-finite alpha2F row")
        for sigma, a2f in zip(sigmas, values[1:]):
            groups[sigma].append((values[0], a2f))
    for sigma, rows in groups.items():
        xs = [r[0] for r in rows]
        if len(rows) < 2 or any(b <= a for a, b in zip(xs, xs[1:])):
            raise ValueError(f"{path}: invalid frequency axis at sigma={sigma}")
    return groups

def trapezoid(xs, ys):
    return sum((xs[i] - xs[i - 1]) * (ys[i] + ys[i - 1]) / 2 for i in range(1, len(xs)))

def read_pairs(path: Path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return {float(r["sigma_Ry"]): r for r in rows}

def signed_summary(values):
    return {"min": min(values), "max": max(values), "max_abs": max(abs(v) for v in values)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True, help="supercon-al-tc package root")
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args()
    root, outdir = a.root, a.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    path32, path48 = root / "k32/alpha2F.dat", root / "k48/alpha2F.dat"
    s32, s48 = read_a2f(path32), read_a2f(path48)
    paired_path = root / "comparison-k32-k48/paired-tc.csv"
    paired = read_pairs(paired_path)
    sigmas = sorted(set(s32) & set(s48) & set(paired))
    if len(sigmas) != 10 or set(sigmas) != set(s32) or set(sigmas) != set(s48) or set(sigmas) != set(paired):
        raise ValueError("Expected exactly ten common sigma samples in both alpha2F files and paired Tc table")
    result_rows = []
    max_rounded_spectrum_lambda_mismatch = 0.0
    for sigma in sigmas:
        left, right = s32[sigma], s48[sigma]
        if [x[0] for x in left] != [x[0] for x in right]:
            raise ValueError(f"Frequency grids differ at sigma={sigma}")
        row = paired[sigma]
        xs = [r[0] for r in left]
        diff_integrand = [0.0 if x == 0.0 else 2.0 * abs(l[1] - r[1]) / x for x, l, r in zip(xs, left, right)]
        l1 = trapezoid(xs, diff_integrand)
        max_idx = max(range(len(xs)), key=lambda i: abs(left[i][1] - right[i][1]))
        # The native alpha2F.dat prints five decimals; this integral diagnoses spectral-shape
        # differences from that saved output and is not substituted for lambda.x's full-precision moments.
        lam_a2f_32 = trapezoid(xs, [0.0 if x == 0.0 else 2.0 * r[1] / x for x, r in zip(xs, left)])
        lam_a2f_48 = trapezoid(xs, [0.0 if x == 0.0 else 2.0 * r[1] / x for x, r in zip(xs, right)])
        max_rounded_spectrum_lambda_mismatch = max(
            max_rounded_spectrum_lambda_mismatch,
            abs(lam_a2f_32 - float(row["lambda_spectrum_rebuilt_A"])),
            abs(lam_a2f_48 - float(row["lambda_spectrum_rebuilt_B"])),
        )
        record = {
            "sigma_Ry": sigma,
            "lambda_qsum_32": float(row["lambda_qsum_rebuilt_A"]),
            "lambda_qsum_48": float(row["lambda_qsum_rebuilt_B"]),
            "delta_lambda_qsum_32_minus_48": float(row["lambda_qsum_rebuilt_A"]) - float(row["lambda_qsum_rebuilt_B"]),
            "lambda_spectrum_32": float(row["lambda_spectrum_rebuilt_A"]),
            "lambda_spectrum_48": float(row["lambda_spectrum_rebuilt_B"]),
            "delta_lambda_spectrum_32_minus_48": float(row["lambda_spectrum_rebuilt_A"]) - float(row["lambda_spectrum_rebuilt_B"]),
            "weighted_L1_spectral_difference_lambda_from_saved_a2F": l1,
            "weighted_L1_relative_to_mean_lambda_percent": 100.0 * l1 / ((float(row["lambda_spectrum_rebuilt_A"]) + float(row["lambda_spectrum_rebuilt_B"])) / 2.0),
            "max_abs_delta_a2F_from_saved_files": abs(left[max_idx][1] - right[max_idx][1]),
            "frequency_at_max_abs_delta_a2F_THz": xs[max_idx],
            "omega_log_32_K": float(row["omega_log_rebuilt_K_A"]),
            "omega_log_48_K": float(row["omega_log_rebuilt_K_B"]),
            "delta_omega_log_32_minus_48_K": float(row["omega_log_rebuilt_K_A"]) - float(row["omega_log_rebuilt_K_B"]),
            "Tc_32_K": float(row["Tc_rebuilt_K_A"]),
            "Tc_48_K": float(row["Tc_rebuilt_K_B"]),
            "delta_Tc_32_minus_48_K": float(row["Tc_rebuilt_K_A"]) - float(row["Tc_rebuilt_K_B"]),
        }
        result_rows.append(record)
    fields = list(result_rows[0])
    with (outdir / "spectral-grid-differences.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result_rows)
    summary = {
        "method": "For each native sigma, compare the paired saved alpha2F.dat arrays pointwise on their common 0-14 THz grid. Weighted L1 spectral difference is integral 2*abs(alpha2F_32-alpha2F_48)/nu dnu. The source alpha2F.dat values are printed to five decimals; lambda, omega_log and Tc are reconstructed independently from the exact printed elph.inp_lambda records.",
        "source_files": {
            "k32_alpha2F_sha256": sha256(path32),
            "k48_alpha2F_sha256": sha256(path48),
            "paired_tc_sha256": sha256(paired_path),
        },
        "sigma_count": len(result_rows),
        "frequency_bins_per_sigma": len(s32[sigmas[0]]),
        "frequency_range_THz": [s32[sigmas[0]][0][0], s32[sigmas[0]][-1][0]],
        "max_abs_lambda_integral_difference_from_five_decimal_alpha2F_vs_rebuilt_source": max_rounded_spectrum_lambda_mismatch,
        "delta_lambda_qsum_32_minus_48": signed_summary([r["delta_lambda_qsum_32_minus_48"] for r in result_rows]),
        "delta_lambda_spectrum_32_minus_48": signed_summary([r["delta_lambda_spectrum_32_minus_48"] for r in result_rows]),
        "weighted_L1_relative_to_mean_lambda_percent": {
            "min": min(r["weighted_L1_relative_to_mean_lambda_percent"] for r in result_rows),
            "max": max(r["weighted_L1_relative_to_mean_lambda_percent"] for r in result_rows),
            "max_at_sigma_Ry": max(result_rows, key=lambda r: r["weighted_L1_relative_to_mean_lambda_percent"])["sigma_Ry"],
        },
        "delta_omega_log_32_minus_48_K": signed_summary([r["delta_omega_log_32_minus_48_K"] for r in result_rows]),
        "delta_Tc_32_minus_48_K": signed_summary([r["delta_Tc_32_minus_48_K"] for r in result_rows]),
        "tc_curve_crossings": 0 if all(r["delta_Tc_32_minus_48_K"] > 0.0 for r in result_rows) else "review required",
        "interpretation": "This is a dense-k comparison at fixed 16^3 response k, 4^3 q, and common smearing values. It supplies spectral and moment evidence for those two branches, but the smearing scan is not by itself a k/q convergence proof.",
    }
    (outdir / "spectral-grid-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("sigma lambda_q32 lambda_q48 delta_lambda_q L1_spectrum_pct d_omega_log_K delta_Tc_K")
    for r in result_rows:
        print(f"{r['sigma_Ry']:.3f} {r['lambda_qsum_32']:.9f} {r['lambda_qsum_48']:.9f} "
              f"{r['delta_lambda_qsum_32_minus_48']:+.9f} "
              f"{r['weighted_L1_relative_to_mean_lambda_percent']:.5f} "
              f"{r['delta_omega_log_32_minus_48_K']:+.3f} {r['delta_Tc_32_minus_48_K']:+.9f}")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
