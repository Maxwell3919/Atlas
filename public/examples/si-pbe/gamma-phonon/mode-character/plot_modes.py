"""Draw existing Si Gamma displacements and their translational content.

Run analyse_modes.py first, then python3 plot_modes.py. Needs NumPy/Matplotlib.
This figure uses the supplied equal-mass Si files. Arrows are static glyphs,
not an MD trajectory, thermal amplitude, or oscillation of an imaginary mode.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from atlas_plot_style import install
install()

ROOT = Path(__file__).resolve().parent
with (ROOT/"mode-vectors.csv").open() as handle:
    vectors = list(csv.DictReader(handle))
with (ROOT/"mode-diagnostics.csv").open() as handle:
    diagnostic = list(csv.DictReader(handle))
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9, "legend.fontsize": 8,
    "text.color": "black", "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black",
    "axes.edgecolor": "black", "axes.linewidth": .7, "axes.grid": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.direction": "out", "ytick.direction": "out", "svg.fonttype": "none",
    "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.facecolor": "white",
})
blue, orange = "#0072B2", "#D55E00"
fig, axes = plt.subplots(1, 3, figsize=(7.3, 2.85), gridspec_kw={"width_ratios": [1, 1, 1.1]})
scale_angstrom = 0.60  # common visual glyph scale, not a calculated amplitude
for ax, mode, color in zip(axes[:2], [1, 4], [blue, orange]):
    selected = sorted([row for row in vectors if row["asr"] == "no" and int(row["mode"]) == mode],
                      key=lambda row: int(row["atom"]))
    if len(selected) != 2:
        raise ValueError("Expected two Si vectors per selected mode")
    for row in selected:
        x, y = float(row["x_angstrom"]), float(row["y_angstrom"])
        dx, dy = scale_angstrom*float(row["ux_real"]), scale_angstrom*float(row["uy_real"])
        ax.annotate("", xy=(x+dx, y+dy), xytext=(x, y),
                    arrowprops={"arrowstyle": "-|>", "lw": 1.6, "color": color, "mutation_scale": 10})
        ax.scatter(x, y, s=35, facecolor="white", edgecolor="black", linewidth=.8, zorder=3)
        ax.annotate("Si "+row["atom"], (x, y), xytext=(6, 3), textcoords="offset points", color="black")
    frequency = next(float(row["frequency_cm-1"]) for row in diagnostic if row["asr"] == "no" and int(row["mode"]) == mode)
    ax.set(xlim=(-.55, 2.1), ylim=(-.70, 1.95), xticks=[0, 1, 2], yticks=[0, 1],
           xlabel=r"$x$ (Å)", ylabel=r"$y$ (Å)", title=f"ASR off: mode {mode}\n{frequency:.6f} cm"+r"$^{-1}$")
    ax.set_aspect("equal", adjustable="box")
ax = axes[2]
for setting, offset, marker, color, label in [("no", -.07, "o", blue, "ASR off"),
                                               ("crystal", .07, "x", orange, "ASR crystal")]:
    rows = sorted([row for row in diagnostic if row["asr"] == setting], key=lambda row: int(row["mode"]))
    mode = np.array([int(row["mode"]) for row in rows])
    fraction = np.array([float(row["translation_fraction"]) for row in rows])
    kwargs = {"facecolors": "none", "edgecolors": color} if marker == "o" else {"color": color}
    ax.scatter(mode+offset, fraction, s=30, marker=marker, linewidth=1.1, label=label, **kwargs)
ax.set(xlim=(.55, 6.45), ylim=(-.10, 1.10), xticks=range(1, 7), yticks=[0, .5, 1],
       xlabel="Mode index", ylabel="Translation fraction (1)", title="Equal-mass Si subspace")
ax.legend(frameon=False, loc="center", handletextpad=.4)
for letter, ax in zip("abc", axes):
    ax.text(-.17, 1.18, letter, transform=ax.transAxes, fontsize=10, fontweight="bold", va="top", color="black")
fig.subplots_adjust(left=.07, right=.99, bottom=.25, top=.78, wspace=.62)
fig.text(.07, .06, r"a, b: $xy$ projection; arrows = normalized displacement × 0.60 Å (visual scale only).", fontsize=8, color="black")
for suffix in ["svg", "pdf", "png"]:
    fig.savefig(ROOT/("si-gamma-mode-character."+suffix), dpi=300)
print("si-gamma-mode-character.svg, si-gamma-mode-character.pdf, si-gamma-mode-character.png")
