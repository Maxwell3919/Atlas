"""Pair two complete QE lambda.x branches and find straight-segment crossings.

Example, after both independent calculations have completed:
    python3 compare_tc.py --a k32 --b k48 --out comparison

Only Python's standard library is required. Keep rebuild_tc.py beside this
script. Curves reconstructed from lambda.x's actual elph inputs retain the
digits lost by its final 0.001 K printing. Printed Tc and a cross-check from
the printed moments are reported separately, without editing native files.
"""

from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
from rebuild_tc import reconstruct

NUMBER = r"[-+0-9.eEdD]+"
MOMENT = re.compile(
    rf"lambda\s*=\s*({NUMBER})\s*\(\s*({NUMBER})\s*\)\s*"
    rf"<log w>\s*=\s*({NUMBER})\s*K\s*N\(Ef\)\s*=\s*({NUMBER})"
    rf"\s*at degauss=\s*({NUMBER})"
)


def number(value):
    result = float(value.replace("D", "E").replace("d", "e"))
    if not math.isfinite(result):
        raise ValueError("Non-finite native value")
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_branch(path):
    text = (path / "lambda.out").read_text()
    rows = []
    for m in MOMENT.finditer(text):
        lam, spectral_lam, omega, nef, sigma = map(number, m.groups())
        rows.append(
            dict(
                sigma_Ry=sigma,
                lambda_qsum=lam,
                lambda_spectrum=spectral_lam,
                omega_log_K=omega,
                N_Ef_native=nef,
            )
        )
    sections = re.split(r"lambda\s+omega_log\s+T_c", text)
    if len(sections) != 2 or not rows:
        raise ValueError(f"{path}: expected one native Tc table")
    table = []
    for line in sections[1].splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 3 or not all(re.fullmatch(NUMBER, x) for x in fields):
            raise ValueError(f"{path}: unexpected native Tc row: {line}")
        table.append(list(map(number, fields)))
    if len(table) != len(rows):
        raise ValueError(f"{path}: incomplete moment/Tc pairing")
    sigmas = [r["sigma_Ry"] for r in rows]
    if len(set(sigmas)) != len(sigmas) or sigmas != sorted(sigmas):
        raise ValueError(f"{path}: duplicated or unordered sigma points")
    input_lines = [
        x.split("!")[0].strip() for x in (path / "lambda.in").read_text().splitlines()
    ]
    input_lines = [x for x in input_lines if x]
    mu = number(input_lines[-1])
    for row, (lam, omega, tc) in zip(rows, table):
        # These bounds follow the native five/three-place output formats.
        if abs(row["lambda_qsum"] - lam) > 0.0000051 or row["omega_log_K"] != omega:
            raise ValueError(f"{path}: lambda/Tc table rows do not correspond")
        denominator = row["lambda_qsum"] - mu * (1 + 0.62 * row["lambda_qsum"])
        if denominator <= 0 or omega <= 0 or tc < 0:
            raise ValueError(f"{path}: formula outside the supported positive regime")
        recomputed = (
            omega / 1.2 * math.exp(-1.04 * (1 + row["lambda_qsum"]) / denominator)
        )
        if abs(recomputed - tc) > 0.00055:
            raise ValueError(
                f"{path}: printed moments do not reproduce native Tc rounding"
            )
        row.update(mu_star=mu, Tc_printed_K=tc, Tc_printed_moments_K=recomputed)
    dat = []
    for line in (path / "lambda.dat").read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            dat.append(list(map(number, line.split())))
    if len(dat) != len(rows):
        raise ValueError(f"{path}: lambda.dat count mismatch")
    for row, fields in zip(rows, dat):
        expected = [
            row[k]
            for k in (
                "sigma_Ry",
                "lambda_qsum",
                "lambda_spectrum",
                "omega_log_K",
                "N_Ef_native",
            )
        ]
        if fields != expected:
            raise ValueError(f"{path}: lambda.dat differs from stdout")
    return rows, {
        n: digest(path / n) for n in ("lambda.in", "lambda.out", "lambda.dat")
    }


def crossings(x, a, b):
    """Return all isolated sampled zeros, sign changes and overlap intervals."""
    difference = [y - z for y, z in zip(a, b)]
    overlaps = []
    overlap_indices = set()
    for i in range(len(x) - 1):
        if difference[i] == 0 and difference[i + 1] == 0:
            if overlaps and overlaps[-1]["right_index"] == i:
                overlaps[-1].update(sigma_hi_Ry=x[i + 1], right_index=i + 1)
            else:
                overlaps.append(
                    dict(
                        kind="overlap",
                        sigma_lo_Ry=x[i],
                        sigma_hi_Ry=x[i + 1],
                        left_index=i,
                        right_index=i + 1,
                    )
                )
            overlap_indices.update((i, i + 1))
    points = []
    for i, d in enumerate(difference):
        if d == 0 and i not in overlap_indices:
            points.append(
                dict(
                    kind="sampled_equality",
                    sigma_Ry=x[i],
                    Tc_K=a[i],
                    sigma_lo_Ry=x[i],
                    sigma_hi_Ry=x[i],
                    delta_lo_K=0.0,
                    delta_hi_K=0.0,
                )
            )
    for i, (d1, d2) in enumerate(zip(difference, difference[1:])):
        if d1 * d2 < 0:
            t = -d1 / (d2 - d1)
            xc = x[i] + t * (x[i + 1] - x[i])
            ya = a[i] + t * (a[i + 1] - a[i])
            yb = b[i] + t * (b[i + 1] - b[i])
            if not x[i] < xc < x[i + 1] or abs(ya - yb) > 1e-12:
                raise ValueError("Crossing interpolation arithmetic failed")
            points.append(
                dict(
                    kind="segment_crossing",
                    sigma_Ry=xc,
                    Tc_K=ya,
                    sigma_lo_Ry=x[i],
                    sigma_hi_Ry=x[i + 1],
                    delta_lo_K=d1,
                    delta_hi_K=d2,
                )
            )
    points.sort(key=lambda r: r["sigma_Ry"])
    for i, p in enumerate(points, 1):
        p["id"] = f"C{i}"
    return dict(points=points, overlap_intervals=overlaps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", type=Path, default=Path("k32"))
    parser.add_argument("--b", type=Path, default=Path("k48"))
    parser.add_argument("--out", type=Path, default=Path("comparison"))
    args = parser.parse_args()
    a, ha = load_branch(args.a)
    b, hb = load_branch(args.b)
    xa = [r["sigma_Ry"] for r in a]
    xb = [r["sigma_Ry"] for r in b]
    if xa != xb or {r["mu_star"] for r in a + b} != {a[0]["mu_star"]}:
        raise ValueError("Branches must have identical native sigma values and mu_star")
    # This reconstruction follows the actual QE 7.5 simple-Gaussian inputs.
    # Its own checks compare each result with native output-format precision.
    precise_a, checks_a = reconstruct(args.a)
    precise_b, checks_b = reconstruct(args.b)
    for native, precise in ((a, precise_a), (b, precise_b)):
        if len(native) != len(precise):
            raise ValueError("Incomplete raw-input reconstruction")
        for record, exact in zip(native, precise):
            if (record["sigma_Ry"], record["mu_star"]) != (
                exact["sigma_Ry"],
                exact["mu_star"],
            ):
                raise ValueError(
                    "Raw-input reconstruction is not paired with the native table"
                )
            record.update(
                Tc_rebuilt_K=exact["Tc_K"],
                lambda_qsum_rebuilt=exact["lambda_qsum"],
                lambda_spectrum_rebuilt=exact["lambda_spectrum"],
                omega_log_rebuilt_K=exact["omega_log_K"],
            )
    paired = []
    for ra, rb in zip(a, b):
        row = {"sigma_Ry": ra["sigma_Ry"], "mu_star": ra["mu_star"]}
        for tag, record in [("A", ra), ("B", rb)]:
            row.update({k + "_" + tag: v for k, v in record.items() if k not in row})
        row["delta_Tc_printed_K"] = ra["Tc_printed_K"] - rb["Tc_printed_K"]
        row["delta_Tc_printed_moments_K"] = (
            ra["Tc_printed_moments_K"] - rb["Tc_printed_moments_K"]
        )
        row["delta_Tc_rebuilt_K"] = ra["Tc_rebuilt_K"] - rb["Tc_rebuilt_K"]
        paired.append(row)
    printed = crossings(
        xa, [r["Tc_printed_K"] for r in a], [r["Tc_printed_K"] for r in b]
    )
    reconstructed = crossings(
        xa,
        [r["Tc_printed_moments_K"] for r in a],
        [r["Tc_printed_moments_K"] for r in b],
    )
    raw = crossings(xa, [r["Tc_rebuilt_K"] for r in a], [r["Tc_rebuilt_K"] for r in b])
    report = {
        "branch_A": args.a.name,
        "branch_B": args.b.name,
        "points_per_branch": len(a),
        "mu_star": a[0]["mu_star"],
        "branch_A_hashes": ha,
        "branch_B_hashes": hb,
        "branch_A_rebuild_checks": checks_a,
        "branch_B_rebuild_checks": checks_b,
        "raw_input_reconstruction": raw,
        "native_printed_curves": printed,
        "printed_moment_crosscheck": reconstructed,
        "native_output_files_identical": ha["lambda.out"] == hb["lambda.out"],
        "scope": "All in-range straight-segment intersections; no fit or extrapolation. The plotted curves are reconstructed from exact elph inputs to lambda.x, whose final Tc print precision is 0.001 K. Reconstruction does not recover unprinted DFPT precision. Source files alone do not establish matched protocols: inspect the accompanying independent run review.",
        "scientific_convergence": "not assessed by this postprocessor",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "paired-tc.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    (args.out / "crossings.json").write_text(json.dumps(report, indent=2) + "\n")
    with (args.out / "crossings.csv").open("w", newline="") as f:
        fields = [
            "id",
            "kind",
            "sigma_Ry",
            "Tc_K",
            "sigma_lo_Ry",
            "sigma_hi_Ry",
            "delta_lo_K",
            "delta_hi_K",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(raw["points"])
    print(
        f'Paired branches: {args.a.name} / {args.b.name}; {len(a)} common sigma points; mu*={a[0]["mu_star"]:.2f}'
    )
    print("sigma_Ry  Tc_A_native_K  Tc_B_native_K  Delta_Tc_rebuilt_K")
    for row in paired:
        print(
            f'{row["sigma_Ry"]:8.3f}  {row["Tc_printed_K_A"]:13.3f}  {row["Tc_printed_K_B"]:13.3f}  {row["delta_Tc_rebuilt_K"]:+18.9f}'
        )
    print("All in-range intersections, reconstructed from native elph inputs:")
    for p in raw["points"]:
        print(
            f'{p["id"]}: sigma={p["sigma_Ry"]:.9f} Ry; Tc={p["Tc_K"]:.9f} K; bracket=[{p["sigma_lo_Ry"]:.3f}, {p["sigma_hi_Ry"]:.3f}] Ry'
        )
    if not raw["points"]:
        print("No isolated crossing in the sampled range.")
    if raw["overlap_intervals"]:
        print("Overlap intervals:", json.dumps(raw["overlap_intervals"]))
    print(
        f'Native 0.001 K print check: {len(printed["points"])} isolated points, {len(printed["overlap_intervals"])} overlap intervals.'
    )
    print("Saved paired-tc.csv, crossings.csv, crossings.json.")


if __name__ == "__main__":
    main()
