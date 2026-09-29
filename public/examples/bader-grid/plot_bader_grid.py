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
data = np.genfromtxt(R / "bader-grid.csv", delimiter=",", names=True)
if len(data) != 4:
    raise ValueError("Expected two atoms at two grids")

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), layout="constrained")

# Panel (a): Fe grid convergence
ax0 = axes[0]
for atom, color, marker, label in [(1, "#0072B2", "o", "Fe #1 (0,0,0)"), (2, "#D55E00", "s", "Fe #2 (½,½,½)")]:
    r = data[data["atom"] == atom]
    ax0.plot(r["grid"], 1000 * r["delta_e"], marker=marker, color=color,
             ms=5, lw=1.2, label=label, zorder=3)

ax0.axhspan(-0.1, 0.1, color="#2ca02c", alpha=0.12, label=r"$\pm 10^{-4}$ e precision band", zorder=1)
ax0.axhline(0, color="#718096", lw=.65, ls="--", zorder=2)
ax0.set_xticks([96, 192])
ax0.set_xticklabels([r"$96^3$ mesh", r"$192^3$ mesh"])
ax0.set_xlim(75, 213)
ax0.set_ylabel(r"Basin deviation $N_{\rm Bader} - Z_{\rm val}$ ($10^{-3}$ e)")
ax0.set_title("bcc Fe: FFT Mesh Charge Error", fontweight="bold")
ax0.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="upper right")

# Panel (b): AECCAR0 Core Electron Integral Convergence
ax1 = axes[1]
r1 = data[data["atom"] == 1]
ax1.plot(r1["grid"], r1["core_integral_e"], "o-", color="#0072B2", ms=5, lw=1.2, label="AECCAR0 Integral", zorder=3)
ax1.axhline(36, color="#D55E00", ls="--", lw=1.0, label="Exact 36 Core Electrons", zorder=2)
ax1.fill_between([75, 213], 35.8, 36.2, color="#D55E00", alpha=0.10, zorder=1)
ax1.set_xticks([96, 192])
ax1.set_xticklabels([r"$96^3$ mesh", r"$192^3$ mesh"])
ax1.set_xlim(75, 213)
ax1.set_ylim(35.5, 40.5)
ax1.set_ylabel("Core charge integral (electrons)")
ax1.set_title("bcc Fe: AECCAR0 Core Convergence", fontweight="bold")
ax1.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="upper right")
ax1.annotate("96³: 39.52 e\n(residual +3.52 e)", xy=(96, 39.52), xytext=(15, -5),
             textcoords="offset points", fontsize=6.8, color="#5a6b80",
             arrowprops=dict(arrowstyle="->", color="#718096", lw=0.6))
ax1.annotate("192³: 36.29 e\n(residual +0.29 e)", xy=(192, 36.29), xytext=(-65, 12),
             textcoords="offset points", fontsize=6.8, color="#5a6b80",
             arrowprops=dict(arrowstyle="->", color="#718096", lw=0.6))

# Panel (c): Real 2D Monolayer Sc2C Bader Charge Partitioning
ax2 = axes[2]
species = ["Sc #1\n(z=0.470)", "Sc #2\n(z=0.530)", "C #3\n(z=0.500)"]
zval = np.array([11.0, 11.0, 4.0])
nbader = np.array([9.7893, 9.7893, 6.4214])
net_q = zval - nbader

x = np.arange(len(species))
width = 0.35

rects1 = ax2.bar(x - width/2, nbader, width, label="Bader Basin Charge", color="#0072B2", alpha=0.88, edgecolor="#004c75")
rects2 = ax2.bar(x + width/2, zval, width, label="Valence Nominal $Z_{\\rm val}$", color="#CBD5E1", alpha=0.9, edgecolor="#94A3B8")

# Add net charge labels on top of the bars
for i in range(len(species)):
    sign = "+" if net_q[i] > 0 else ""
    ax2.text(x[i], max(zval[i], nbader[i]) + 0.45, f"$Q = {sign}{net_q[i]:.2f}$ e",
             ha="center", va="bottom", fontsize=7.2, fontweight="bold",
             color="#D55E00" if net_q[i] > 0 else "#0072B2")

ax2.set_xticks(x)
ax2.set_xticklabels(species)
ax2.set_ylim(0, 13.5)
ax2.set_ylabel("Electrons / atom")
ax2.set_title(r"2D Monolayer Sc$_2$C: Bader Partitioning", fontweight="bold")
ax2.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="upper left")

# Panel labels
for label, ax in zip("abc", axes):
    ax.text(-0.14, 1.05, label, transform=ax.transAxes, weight="bold", fontsize=10)

for ext in ("svg", "pdf", "png"):
    fig.savefig(R / f"bader-grid.{ext}", dpi=300)

print(f"Rendered upgraded bader-grid.svg/pdf/png (3 panels) at {R}")
