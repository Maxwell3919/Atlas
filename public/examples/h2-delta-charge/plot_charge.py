from pathlib import Path
import csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from atlas_plot_style import install
install()

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7,
    "text.color": "#162232", "axes.labelcolor": "#162232", "axes.edgecolor": "#718096",
    "xtick.color": "#162232", "ytick.color": "#162232", "axes.linewidth": .75,
    "xtick.major.width": .75, "ytick.major.width": .75,
    "xtick.direction": "out", "ytick.direction": "out", "axes.grid": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"
})

R = Path(__file__).resolve().parent
s = json.loads((R / "charge-difference-summary.json").read_text())
xy = np.genfromtxt(R / "delta-y5.csv", delimiter=",", names=True)
p = np.genfromtxt(R / "delta-planar.csv", delimiter=",", names=True)

nx, ny, nz = s["grid"]
if len(xy) != nx * nz or len(p) != nz + 1:
    raise ValueError("Grid dimensions do not match")

x = xy["x_A"].reshape(nz, nx)
z = xy["z_A"].reshape(nz, nx)
dn = xy["delta_n_e_A3"].reshape(nz, nx)
if not np.isfinite(dn).all():
    raise ValueError("Non-finite density")

# Custom diverging colormap: Deep blue (depletion) -> White -> Amber gold (accumulation)
cmap = LinearSegmentedColormap.from_list("cdd_isomorphism", ["#0072B2", "#E8F0F8", "#FFFFFF", "#FFF3E0", "#D55E00"])
lim = max(abs(s["minimum_delta_n_e_A3"]), abs(s["maximum_delta_n_e_A3"]))

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), layout="constrained")

# ----------------- Panel (a): 2D Delta n Slice -----------------
ax0 = axes[0]
im0 = ax0.pcolormesh(x, z, dn, cmap=cmap, vmin=-lim, vmax=lim, shading="gouraud", rasterized=True)
cs_neg = ax0.contour(x, z, dn, levels=[-0.05, -0.02, -0.005], colors="#0072B2", linewidths=0.6, linestyles="dashed")
cs_pos = ax0.contour(x, z, dn, levels=[0.005, 0.02, 0.05], colors="#D55E00", linewidths=0.6)

pos = np.asarray(s["positions_A"])
ax0.scatter(pos[:, 0], pos[:, 2], s=40, facecolors="white", edgecolors="#162232", linewidths=1.2, zorder=5)
ax0.plot([pos[0, 0], pos[1, 0]], [pos[0, 2], pos[1, 2]], color="#162232", lw=1.0, ls=":", zorder=4)

ax0.text(pos[0, 0] + 0.18, pos[0, 2] - 0.22, "H #1", fontsize=7.5, fontweight="bold", color="#162232")
ax0.text(pos[1, 0] + 0.18, pos[1, 2] + 0.12, "H #2", fontsize=7.5, fontweight="bold", color="#162232")
ax0.text(5.0, 5.0, "Bond Center\nAccumulation", fontsize=6.8, ha="center", va="center", color="#8c3b00", fontweight="bold")

ax0.set(xlabel=r"$x$ (Å)", ylabel=r"$z$ (Å)", xlim=(3.2, 6.8), ylim=(3.2, 6.8))
ax0.set_aspect("equal")
ax0.set_title(r"2D Slice: $\Delta\rho(x, z)$ ($y = 5.0$ Å)", fontweight="bold")
cbar = fig.colorbar(im0, ax=ax0, label=r"$\Delta n$ ($e\cdot$Å$^{-3}$)", fraction=0.046, pad=0.04)

# ----------------- Panel (b): 1D Planar Average -----------------
ax1 = axes[1]
z_arr = p["z_A"]
d_arr = p["delta_N_e_A"]

ax1.plot(z_arr, d_arr, color="#162232", lw=1.2, zorder=3)
ax1.axhline(0, color="#718096", lw=0.6, ls="-", zorder=2)

# Dual-color shading matching 2D map
ax1.fill_between(z_arr, 0, d_arr, where=(d_arr >= 0), color="#D55E00", alpha=0.35, label="Accumulation (>0)", zorder=1)
ax1.fill_between(z_arr, 0, d_arr, where=(d_arr < 0), color="#0072B2", alpha=0.35, label="Depletion (<0)", zorder=1)

for i, zz in enumerate(pos[:, 2]):
    ax1.axvline(zz, color="#5a6b80", lw=0.7, ls=":", zorder=2)
    ax1.text(zz, -0.09, f"H #{i+1}\n({zz:.2f} Å)", fontsize=6.5, ha="center", color="#5a6b80")

ax1.annotate("Covalent Bond\nPeak: +0.07 e/Å", xy=(5.0, 0.071), xytext=(5.6, 0.055),
             fontsize=7, color="#8c3b00", arrowprops=dict(arrowstyle="->", color="#D55E00", lw=0.6))

ax1.set(xlabel=r"$z$ along box normal (Å)", ylabel=r"$A\langle\Delta n\rangle_{xy}$ ($e\cdot$Å$^{-1}$)", xlim=(2.0, 8.0), ylim=(-0.11, 0.095))
ax1.set_title(r"Planar Average: $A\langle\Delta n(z)\rangle_{xy}$", fontweight="bold")
ax1.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="upper right")

# ----------------- Panel (c): Cumulative Charge Integral -----------------
ax2 = axes[2]
cum_arr = p["cumulative_e"]

ax2.plot(z_arr, cum_arr, color="#009E73", lw=1.3, label=r"$\int_0^z A\langle\Delta n\rangle dz'$", zorder=3)
ax2.axhline(0, color="#718096", lw=0.6, ls="-", zorder=2)
ax2.fill_between(z_arr, 0, cum_arr, color="#009E73", alpha=0.15, zorder=1)

for zz in pos[:, 2]:
    ax2.axvline(zz, color="#5a6b80", lw=0.7, ls=":", zorder=2)

ax2.annotate(f"Final Endpoint:\n{cum_arr[-1]:+.2e} e\n(Charge Conserved)", xy=(8.0, cum_arr[-1]), xytext=(5.6, -0.015),
             fontsize=7, color="#007050", arrowprops=dict(arrowstyle="->", color="#009E73", lw=0.6))

ax2.set(xlabel=r"$z$ along box normal (Å)", ylabel=r"Cumulative Charge $\Delta Q(z)$ ($e$)", xlim=(2.0, 8.0), ylim=(-0.035, 0.025))
ax2.set_title("Charge Conservation Integral", fontweight="bold")
ax2.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="lower right")

for label, a in zip("abc", axes):
    a.text(-0.14, 1.05, label, transform=a.transAxes, fontweight="bold", fontsize=10)

for ext in ["png", "pdf", "svg"]:
    fig.savefig(R / f"h2-charge-difference.{ext}", dpi=300)
plt.close(fig)

checks = {
    "linear_colour_range_e_A3": [-lim, lim],
    "slice_y_A": 5.0,
    "grid": s["grid"],
    "cumulative_endpoint_e": float(p["cumulative_e"][-1]),
    "minimum_linear_density_e_A": float(p["delta_N_e_A"].min()),
    "maximum_linear_density_e_A": float(p["delta_N_e_A"].max()),
    "minimum_cumulative_e": float(p["cumulative_e"].min()),
    "maximum_cumulative_e": float(p["cumulative_e"].max())
}
(R / "plot-checks.json").write_text(json.dumps(checks, indent=2) + "\n")
print(f"Rendered upgraded h2-charge-difference in {R}!")
