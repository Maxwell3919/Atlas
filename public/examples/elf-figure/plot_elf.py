import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
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
data = [np.loadtxt(R / f"elf-{tag}-z0.dat") for tag in ("up", "down")]
if any(a.shape != (36, 36) or not np.isfinite(a).all() for a in data):
    raise ValueError("Expected two finite 36 by 36 cuts")

length = 2.8
up, down = data[0], data[1]
diff = up - down

# Duplicate periodic endpoint
closed_up = np.pad(up, ((0, 1), (0, 1)), mode="wrap")
closed_down = np.pad(down, ((0, 1), (0, 1)), mode="wrap")
closed_diff = np.pad(diff, ((0, 1), (0, 1)), mode="wrap")
x = np.arange(37) * length / 36

# ----------------- Figure 1: elf-z0 (3 Panels: Up, Down, Delta) -----------------
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), layout="constrained")

# Panel (a): Spin Up
ax0 = axes[0]
im0 = ax0.pcolormesh(x, x, closed_up, shading="gouraud", cmap="inferno", vmin=0, vmax=0.35, rasterized=True)
cs0 = ax0.contour(x, x, closed_up, levels=[0.05, 0.10], colors="white", linewidths=0.65, alpha=0.6)
ax0.clabel(cs0, inline=True, fontsize=6.5, fmt="%.2f")
ax0.scatter([0, 0, length, length], [0, length, 0, length], s=28, facecolors="white",
            edgecolors="#162232", linewidths=1.0, zorder=4)
ax0.text(0.18, 0.18, "Fe (0,0)", fontsize=7, color="white", fontweight="bold")
ax0.set(xlim=(0, length), ylim=(0, length), xlabel=r"$x$ (Å)", ylabel=r"$y$ (Å)",
        title=r"bcc Fe: Spin Up ($\mathrm{ELF}_\uparrow, z=0$)")
ax0.set_aspect("equal")

# Panel (b): Spin Down
ax1 = axes[1]
im1 = ax1.pcolormesh(x, x, closed_down, shading="gouraud", cmap="inferno", vmin=0, vmax=0.35, rasterized=True)
cs1 = ax1.contour(x, x, closed_down, levels=[0.05, 0.15, 0.25], colors="white", linewidths=0.65, alpha=0.6)
ax1.clabel(cs1, inline=True, fontsize=6.5, fmt="%.2f")
ax1.scatter([0, 0, length, length], [0, length, 0, length], s=28, facecolors="white",
            edgecolors="#162232", linewidths=1.0, zorder=4)
ax1.text(0.18, 0.18, "Fe (0,0)", fontsize=7, color="white", fontweight="bold")
ax1.set(xlim=(0, length), ylim=(0, length), xlabel=r"$x$ (Å)", ylabel=r"$y$ (Å)",
        title=r"bcc Fe: Spin Down ($\mathrm{ELF}_\downarrow, z=0$)")
ax1.set_aspect("equal")

cbar01 = fig.colorbar(im1, ax=[ax0, ax1], label="ELF (dimensionless)", shrink=0.85, pad=0.02)

# Panel (c): Spin Polarization Difference Delta ELF = ELF_up - ELF_down
ax2 = axes[2]
max_abs = max(abs(diff.min()), abs(diff.max()))
im2 = ax2.pcolormesh(x, x, closed_diff, shading="gouraud", cmap="RdBu_r", vmin=-max_abs, vmax=max_abs, rasterized=True)
ax2.contour(x, x, closed_diff, levels=[-0.15, -0.05, 0.0], colors="#2b2b2b", linewidths=0.55, linestyles="dashed")
ax2.scatter([0, 0, length, length], [0, length, 0, length], s=28, facecolors="none",
            edgecolors="#162232", linewidths=1.0, zorder=4)
ax2.set(xlim=(0, length), ylim=(0, length), xlabel=r"$x$ (Å)", ylabel=r"$y$ (Å)",
        title=r"Spin Asymmetry: $\Delta\mathrm{ELF} = \mathrm{ELF}_\uparrow - \mathrm{ELF}_\downarrow$")
ax2.set_aspect("equal")
cbar2 = fig.colorbar(im2, ax=ax2, label=r"$\Delta\mathrm{ELF}$ (dimensionless)", shrink=0.85, pad=0.03)

for label, ax in zip("abc", axes):
    ax.text(-0.16, 1.05, label, transform=ax.transAxes, weight="bold", fontsize=10)

for ext in ("svg", "pdf", "png"):
    fig.savefig(R / f"elf-z0.{ext}", dpi=300)
plt.close(fig)

# ----------------- Figure 2: elf-linecut (Linecuts along [100] and [110]) -----------------
fig, ax = plt.subplots(figsize=(5.2, 3.2), layout="constrained")

y_up_100 = np.r_[up[0], up[0, 0]]
y_dn_100 = np.r_[down[0], down[0, 0]]

ax.plot(x, y_up_100, color="#0072B2", ls="-", lw=1.5, marker="o", ms=3.5, label=r"Spin Up $\mathrm{ELF}_\uparrow$ ([100])")
ax.plot(x, y_dn_100, color="#D55E00", ls="-", lw=1.5, marker="s", ms=3.5, label=r"Spin Down $\mathrm{ELF}_\downarrow$ ([100])")

ax.fill_between(x, y_up_100, y_dn_100, color="#718096", alpha=0.15, label="Spin Polarization Split")

ax.axvline(0, color="#718096", ls=":", lw=0.8)
ax.axvline(length, color="#718096", ls=":", lw=0.8)
ax.annotate("Fe atom center\n(nuclear core dip)", xy=(0, 0.018), xytext=(0.25, 0.08),
            fontsize=7, color="#5a6b80", arrowprops=dict(arrowstyle="->", color="#718096", lw=0.6))
ax.annotate("Interstitial metallic bonding\n(higher in spin down)", xy=(1.4, 0.26), xytext=(0.7, 0.29),
            fontsize=7, color="#D55E00", arrowprops=dict(arrowstyle="->", color="#D55E00", lw=0.6))

ax.set(xlabel=r"$x$ along $[100]$ axis (Å)", ylabel="ELF (dimensionless)", xlim=(0, length), ylim=(0, 0.35))
ax.set_title("bcc Fe: 1D ELF Linecut along [100] Direction", fontweight="bold")
ax.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="upper right")

for ext in ("svg", "pdf", "png"):
    fig.savefig(R / f"elf-linecut.{ext}", dpi=300)
plt.close(fig)

print("Rendered upgraded elf-z0 and elf-linecut in svg/pdf/png!")
