#!/usr/bin/env python3
"""Rebuild the QE7.5 lambda.x result from its native elph input files. No QE executable is run."""

import argparse, csv, hashlib, json, math, re
from pathlib import Path

NUMBER = r"[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?"
num = lambda x: float(x.replace("D", "E").replace("d", "e"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def reconstruct(root):
    root = Path(root)
    lines = [
        l.split("!")[0].strip()
        for l in (root / "lambda.in").read_text().splitlines()
        if l.split("!")[0].strip()
    ]
    emax, width, order = map(float, lines[0].split())
    assert order == 0, "This script supports the actual simple-Gaussian spectrum only"
    nq = int(lines[1])
    qs = [list(map(float, l.split())) for l in lines[2 : 2 + nq]]
    names = lines[2 + nq : 2 + 2 * nq]
    mu = float(lines[2 + 2 * nq])
    totalweight = sum(q[3] for q in qs)
    native = (root / "lambda.out").read_text()
    details = re.findall(
        r"lambda\s*=\s*("
        + NUMBER
        + r")\s*\(\s*("
        + NUMBER
        + r")\s*\)\s*<log w>=\s*("
        + NUMBER
        + r")\s*K\s*N\(Ef\)=\s*("
        + NUMBER
        + r")\s*at degauss=\s*("
        + NUMBER
        + r")",
        native,
    )
    printed = [
        list(map(num, line.split()))
        for line in native.split("T_c")[-1].strip().splitlines()
        if len(line.split()) == 3
    ]
    assert len(details) == len(printed) == 10
    n = 2000
    step = emax / (n - 1)
    freq = [i * step for i in range(n)]
    lq = [0.0] * 10
    a2f = [[0.0] * n for _ in range(10)]
    sigma0 = None
    dos0 = None
    ef0 = None
    hashes = {p: sha(root / p) for p in ["lambda.in", "lambda.out"]}
    qcheck = []
    for iq, (qinfo, name) in enumerate(zip(qs, names), 1):
        p = root / name
        hashes[name] = sha(p)
        records = p.read_text().splitlines()
        head = records[0].split()
        qread = list(map(num, head[:3]))
        ns, nm = map(int, head[3:])
        w2 = list(map(num, records[1].split()))
        assert ns == 10 and nm == 3 and len(w2) == 3 and min(w2) >= 0
        coordinate_error = max(abs(x - y) for x, y in zip(qinfo[:3], qread))
        assert (
            coordinate_error <= 5.005e-7
        ), "q differs beyond its six-decimal output rounding"
        weight = qinfo[3] / totalweight
        sig = []
        doses = []
        efs = []
        for j in range(ns):
            k = 2 + j * (nm + 2)
            sm = re.search(
                r"Gaussian Broadening:\s*(" + NUMBER + r") Ry, ngauss=\s*(-?\d+)",
                records[k],
            )
            sigma = num(sm.group(1))
            assert int(sm.group(2)) == 0
            d = re.search(
                r"DOS =\s*(" + NUMBER + r").*at Ef=\s*(" + NUMBER + r")", records[k + 1]
            )
            dos, ef = map(num, d.groups())
            sig.append(sigma)
            doses.append(dos)
            efs.append(ef)
            for im in range(nm):
                m = re.search(
                    r"lambda\(\s*(\d+)\)=\s*("
                    + NUMBER
                    + r")\s*gamma=\s*("
                    + NUMBER
                    + r")",
                    records[k + im + 2],
                )
                assert int(m.group(1)) == im + 1
                lam = num(m.group(2))
                om = math.sqrt(w2[im]) * 3289.828
                lq[j] += weight * lam
                coefficient = weight * lam * om * 0.5 / math.sqrt(math.pi) / width
                for i, e in enumerate(freq):
                    a2f[j][i] += coefficient * math.exp(
                        -min(200.0, ((e - om) / width) ** 2)
                    )
        if sigma0 is None:
            sigma0, dos0, ef0 = sig, doses, efs
        else:
            assert (
                sig == sigma0 and doses == dos0 and efs == ef0
            ), "Sigma/DOS/EF metadata mismatch between q files"
        qcheck.append(
            {
                "q_index": iq,
                "q_lambda_in": qinfo[:3],
                "q_elph": qread,
                "weight": qinfo[3],
                "coordinate_error": coordinate_error,
            }
        )
    rows = []
    for j, detail in enumerate(details):
        lp, l2p, wp, dosp, sigmap = map(num, detail)
        assert sigmap == sigma0[j]
        l2 = 2 * step * sum(a2f[j][i] / freq[i] for i in range(1, n))
        wlog = (
            math.exp(
                2
                * step
                * sum(a2f[j][i] * math.log(freq[i]) / freq[i] for i in range(1, n))
                / l2
            )
            * 47.9924
        )
        value = (
            wlog
            / 1.2
            * math.exp(-1.04 * (1 + lq[j]) / (lq[j] - mu * (1 + 0.62 * lq[j])))
        )
        assert (
            abs(lp - lq[j]) <= 0.500001e-6
            and abs(l2p - l2) <= 0.500001e-6
            and abs(wp - wlog) <= 0.500001e-3
        )
        assert (
            abs(printed[j][2] - value) <= 0.500001e-3
        ), "Reconstruction does not round to native Tc"
        rows.append(
            {
                "sigma_Ry": sigmap,
                "mu_star": mu,
                "lambda_qsum": lq[j],
                "lambda_spectrum": l2,
                "omega_log_K": wlog,
                "N_EF": dosp,
                "N_EF_unit": "states/spin/Ry/cell",
                "Tc_K": value,
                "native_printed_Tc_K": printed[j][2],
                "native_lambda_6dp": lp,
                "native_lambda_spectrum_6dp": l2p,
                "native_omega_log_K_3dp": wp,
                "EF_eV": ef0[j],
            }
        )
    metadata = {
        "source_sha256": hashes,
        "q_pairing": qcheck,
        "q_weight_sum": totalweight,
        "nq": nq,
        "spectrum_points": n,
        "spectrum_max_THz": emax,
        "spectrum_gaussian_width_THz": width,
        "mu_star": mu,
        "formula": "Tc=omega_log/1.2*exp(-1.04*(1+lambda_qsum)/(lambda_qsum-mu_star*(1+0.62*lambda_qsum)))",
        "frequency_constants": "3289.828THz/Ry;47.9924K/THz, matching QE7.5lambda.f90",
        "precision_scope": "Reconstruction of lambda.x from the exact printed elph records, not recovery of unprinted DFT precision. Mode lambda is stored to4decimals; final native Tc is printed to3decimals.",
        "source": "https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90",
        "no_QE_executable_run": True,
    }
    return rows, metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "branches",
        nargs="+",
        type=Path,
        help="Directories containing lambda.in/lambda.out/elph_dir",
    )
    p.add_argument("--outdir", type=Path, default=Path("."))
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    for branch in args.branches:
        rows, meta = reconstruct(branch)
        name = branch.name
        with (args.outdir / (name + "-rebuilt.csv")).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        (args.outdir / (name + "-rebuild-checks.json")).write_text(
            json.dumps(meta, indent=2) + "\n"
        )
        print(
            name
            + ":10sigma rows reconstructed; native lambda/omega/Tc match their printed precision"
        )


if __name__ == "__main__":
    main()
