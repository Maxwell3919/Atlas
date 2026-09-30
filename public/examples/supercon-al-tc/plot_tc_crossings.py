"""Plot the paired lambda.x reconstructions written by compare_tc.py.

Run with NumPy and Matplotlib installed:
    python3 plot_tc_crossings.py --data comparison --out figures
Keep atlas_plot_style.py beside this script. No smoothing or data filtering
is used; the second Tc panel is explicitly a magnified view.
"""

from pathlib import Path
import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import atlas_plot_style


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("comparison"))
    parser.add_argument("--out", type=Path, default=Path("figures"))
    parser.add_argument("--prefix", default="al-two-dense-grids")
    args = parser.parse_args()
    with (args.data / "paired-tc.csv").open() as f:
        rows = list(csv.DictReader(f))
    report = json.loads((args.data / "crossings.json").read_text())
    if len(rows) != report["points_per_branch"] or len(rows) < 3:
        raise ValueError("Incomplete paired native table")

    def col(name):
        return np.array([float(r[name]) for r in rows])

    sigma = col("sigma_Ry")
    a = col("Tc_rebuilt_K_A")
    b = col("Tc_rebuilt_K_B")
    candidates = report["raw_input_reconstruction"]["points"]
    overlaps = report["raw_input_reconstruction"]["overlap_intervals"]
    atlas_plot_style.install()
    mesh_a = int(report.get('branch_A','k32').removeprefix('k'))
    mesh_b = int(report.get('branch_B','k48').removeprefix('k'))
    styles = {
        32:dict(color='#0072b2',ls='-',marker='o',mfc='white'),
        48:dict(color='#d55e00',ls='--',marker='s',mfc='#d55e00'),
        64:dict(color='#009e73',ls='-.',marker='^',mfc='white'),
    }

    def pair(ax, ya, yb):
        ax.plot(
            sigma,
            ya,
            **styles[mesh_a],
            lw=1.1,
            ms=4,
            mew=0.9,
            label=rf"$k_{{\rm dense}}={mesh_a}^3$",
        )
        ax.plot(
            sigma,
            yb,
            **styles[mesh_b],
            lw=1.1,
            ms=3.5,
            mew=0.8,
            label=rf"$k_{{\rm dense}}={mesh_b}^3$",
        )
        ax.set_xlabel(r"EPC electronic smearing $\sigma$ (Ry)")
        ax.set_xlim(sigma[0] - 0.001, sigma[-1] + 0.001)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.22, top=0.72, wspace=0.31)
    fig.suptitle(
        "Al: two independently calculated $T_c$ curves", x=0.085, y=0.98, ha="left"
    )
    crossing_note = ('Diamonds: all straight-segment intersections.' if candidates else 'No intersection in the sampled range.')
    if overlaps:
        crossing_note += ' Gray bands: overlaps.'
    fig.text(
        0.085,
        0.88,
        r"Response $k=16^3$  |  $q=4^3$  |  $\mu^*=0.10$  |  identical remaining inputs",
    )
    for ax, title in zip(
        axes, ["Full sampled range", "Magnified temperature range"]
    ):
        pair(ax, a, b)
        ax.set_ylabel(r"$T_c$ (K)")
        ax.set_title(title, pad=10)
        for interval in overlaps:
            ax.axvspan(
                interval["sigma_lo_Ry"],
                interval["sigma_hi_Ry"],
                facecolor="#dddddd",
                alpha=0.5,
                zorder=0,
            )
        for c in candidates:
            ax.plot(
                c["sigma_Ry"],
                c["Tc_K"],
                marker="D",
                ms=5,
                mec="#222222",
                mfc="white",
                mew=1,
                zorder=5,
            )
    axes[0].legend(loc="upper right")
    zoom = np.r_[a[1:], b[1:], [c["Tc_K"] for c in candidates]]
    span = max(float(np.ptp(zoom)), 0.01)
    axes[1].set_ylim(float(zoom.min()) - 0.20 * span, float(zoom.max()) + 0.32 * span)
    for i, c in enumerate(candidates):
        dy = 18 if i % 2 == 0 else -27
        axes[1].annotate(
            c["id"],
            xy=(c["sigma_Ry"], c["Tc_K"]),
            xytext=(7, dy),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            arrowprops=dict(arrowstyle="-", lw=0.65, color="#555555"),
        )
    fig.text(
        0.085,
        0.035,
        "Reconstructed from native elph inputs. " + crossing_note,
        fontsize=9,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out / (args.prefix + "-tc.png"))
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.22, top=0.72, wspace=0.31)
    fig.suptitle(
        "Al: moments from the same two EPC calculations", x=0.085, y=0.98, ha="left"
    )
    fig.text(
        0.085,
        0.88,
        r"Response $k=16^3$  |  $q=4^3$  |  same electronic-smearing points",
    )
    pair(axes[0], col("lambda_qsum_rebuilt_A"), col("lambda_qsum_rebuilt_B"))
    pair(axes[1], col("omega_log_rebuilt_K_A"), col("omega_log_rebuilt_K_B"))
    axes[0].set_ylabel(r"$\lambda$ (weighted mode sum)")
    axes[1].set_ylabel(r"$\omega_{\log}$ (K)")
    axes[0].set_title("Coupling constant", pad=10)
    axes[1].set_title("Logarithmic frequency", pad=10)
    axes[0].legend(loc="upper right")
    fig.text(
        0.085,
        0.035,
        "Moments are reconstructed using the same lambda.x algorithm as the $T_c$ curves.",
        fontsize=9,
    )
    fig.savefig(args.out / (args.prefix + "-moments.png"))
    plt.close(fig)
    summary = {
        "rows_per_curve": len(rows),
        "crossing_markers": len(candidates),
        "overlap_intervals": len(overlaps),
        "x_range_Ry": [float(sigma.min()), float(sigma.max())],
        "reconstructed_Tc_range_K": [
            float(min(a.min(), b.min())),
            float(max(a.max(), b.max())),
        ],
        "figures": [args.prefix + "-tc", args.prefix + "-moments"],
        "numerical_treatment": "lambda.x reconstruction from unmodified elph inputs, straight segments, full range plus explicitly magnified Tc view",
    }
    (args.out / (args.prefix + "-plot-checks.json")).write_text(json.dumps(summary, indent=2) + "\n")
    print(f'{len(rows)} points per curve; {len(candidates)} isolated intersections; {len(overlaps)} overlap intervals.')
    for name in summary['figures']:
        print(f'Saved {args.out / name}.png, .svg, .pdf')


if __name__ == "__main__":
    main()
