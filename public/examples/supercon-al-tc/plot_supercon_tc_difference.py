#!/usr/bin/env python3
"""Plot the paired Al k32/k48 Tc curves and their signed difference."""
from __future__ import annotations
import argparse
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"no rows in {path}")
    sigma = [float(r["sigma_Ry"]) for r in rows]
    tc32 = [float(r["Tc_rebuilt_K_A"]) for r in rows]
    tc48 = [float(r["Tc_rebuilt_K_B"]) for r in rows]
    delta_saved = [float(r["delta_Tc_rebuilt_K"]) for r in rows]
    mu = [float(r["mu_star"]) for r in rows]
    if any(not math.isfinite(x) for seq in (sigma, tc32, tc48, delta_saved, mu) for x in seq):
        raise ValueError("non-finite input value")
    if sigma != sorted(sigma) or len(set(sigma)) != len(sigma):
        raise ValueError("sigma values must be strictly increasing")
    if max(mu) - min(mu) > 1e-12:
        raise ValueError("mu* differs between paired rows")
    delta = [a - b for a, b in zip(tc32, tc48)]
    if any(abs(x - y) > 2e-9 for x, y in zip(delta, delta_saved)):
        raise ValueError("stored Delta Tc does not equal Tc32 - Tc48")
    return sigma, tc32, tc48, delta, mu[0]


def intersections(sigma, delta):
    points = []
    intervals = []
    i = 0
    while i < len(delta):
        if delta[i] != 0:
            i += 1
            continue
        j = i
        while j + 1 < len(delta) and delta[j + 1] == 0:
            j += 1
        if j > i:
            intervals.append((sigma[i], sigma[j]))
        else:
            points.append((sigma[i], 0.0))
        i = j + 1
    for i in range(len(delta) - 1):
        if delta[i] * delta[i + 1] < 0:
            x = sigma[i] - delta[i] * (sigma[i + 1] - sigma[i]) / (delta[i + 1] - delta[i])
            points.append((x, 0.0))
    return points, intervals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("comparison-k32-k48/paired-tc.csv"))
    ap.add_argument("--out", type=Path, default=Path("figures"))
    ap.add_argument("--prefix", default="supercon-al-k32-k48-tc-delta")
    args = ap.parse_args()
    sigma, tc32, tc48, delta, mu = read_rows(args.data)
    points, intervals = intersections(sigma, delta)
    args.out.mkdir(parents=True, exist_ok=True)

    blue, vermillion = "#0072B2", "#D55E00"
    fig, (ax_tc, ax_delta) = plt.subplots(
        2, 1, figsize=(7.4, 6.1), sharex=True,
        gridspec_kw={"height_ratios": [1.55, 1.0], "hspace": 0.08},
        layout="constrained",
    )
    ax_tc.plot(sigma, tc32, color=blue, marker="o", ms=5, lw=1.8,
               label=r"$32^3$ dense $k$ mesh")
    ax_tc.plot(sigma, tc48, color=vermillion, marker="s", ms=5, lw=1.8,
               ls="--", label=r"$48^3$ dense $k$ mesh")
    ax_tc.set_ylabel(r"$T_c$ (K)")
    ax_tc.set_ylim(0, max(tc32 + tc48) * 1.12)
    ax_tc.legend(frameon=False, ncol=2, loc="upper right")
    ax_tc.text(0.02, 0.94, rf"$\mu^*= {mu:.2f}$; {len(sigma)} calculated widths",
               transform=ax_tc.transAxes, va="top", fontsize=9)

    ax_delta.axhline(0, color="#333333", lw=1.15, ls=(0, (4, 2)), zorder=4)
    ax_delta.plot(sigma, delta, color="#6A3D9A", marker="D", ms=4.5, lw=1.7)
    ax_delta.fill_between(sigma, 0, delta, where=[d >= 0 for d in delta],
                          color="#6A3D9A", alpha=0.10, interpolate=True)
    for x, y in points:
        ax_tc.scatter([x], [y], s=50, facecolor="white", edgecolor="#111111", zorder=5)
        ax_delta.scatter([x], [y], s=45, facecolor="white", edgecolor="#111111", zorder=5)
    ax_delta.set_ylabel(r"$\Delta T_c=T_c(32^3)-T_c(48^3)$ (K)")
    ax_delta.set_xlabel(r"Electronic smearing $\sigma$ (Ry)")
    ax_delta.set_xlim(min(sigma) - 0.002, max(sigma) + 0.002)
    ax_delta.xaxis.set_major_locator(MultipleLocator(0.005))
    span = max(delta) - min(delta)
    lo = min(0.0, min(delta)) - 0.24 * span
    hi = max(0.0, max(delta)) + 0.16 * span
    ax_delta.set_ylim(lo, hi)
    if points or intervals:
        summary = f"{len(points)} isolated crossing(s), {len(intervals)} overlap interval(s)"
    else:
        min_i = min(range(len(delta)), key=delta.__getitem__)
        summary = ("No crossing in sampled range; "
                   rf"min $\Delta T_c={delta[min_i]:.6f}$ K at $\sigma={sigma[min_i]:.3f}$ Ry")
    ax_delta.text(0.02, 0.94, summary, transform=ax_delta.transAxes,
                  va="top", fontsize=8.7)
    for ax in (ax_tc, ax_delta):
        ax.grid(axis="both", color="#B7B7B7", alpha=0.28, lw=0.65)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(direction="out", length=3.5, width=0.8)
    fig.suptitle("Al: paired dense-mesh Allen–Dynes results", fontsize=12, y=1.015)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(args.out / f"{args.prefix}.{ext}", dpi=320 if ext == "png" else None,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"rows={len(sigma)}; mu*={mu:.2f}; isolated crossings={len(points)}; overlap intervals={len(intervals)}")
    print(f"delta_min_K={min(delta):.9f}; delta_max_K={max(delta):.9f}")
    print(f"saved {args.out / (args.prefix + '.png')}, .svg, .pdf")


if __name__ == "__main__":
    main()
