import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
r = json.load((R / "magnetic-energies.json").open())

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), layout="constrained")

states = ["FM", "AFM", "NM"]
state_colors = ["#0072B2", "#D55E00", "#718096"]

# ----------------- Panel (a): Relative Energy Above FM -----------------
ax0 = axes[0]
de0 = [v["dE0_meV_atom"] for v in r]
x = np.arange(len(states))
bars0 = ax0.bar(x, de0, color=state_colors, width=0.5, alpha=0.9, edgecolor="#162232", lw=0.8, zorder=3)

for i, v in enumerate(de0):
    txt = f"{v:.1f} meV" if v > 0 else "0.0 (Ground State)"
    ax0.text(i, v + 15, txt, ha="center", va="bottom", fontsize=7.2, fontweight="bold",
             color=state_colors[i] if v > 0 else "#0072B2")

ax0.axhline(0, color="#718096", lw=0.8, ls="--", zorder=2)
ax0.set_xticks(x)
ax0.set_xticklabels(states, fontweight="bold")
ax0.set_ylim(-10, max(de0) * 1.22)
ax0.set_ylabel(r"$\Delta E_0 = E - E_{\rm FM}$ (meV / atom)")
ax0.set_title("Magnetic Energy Hierarchy", fontweight="bold")

# ----------------- Panel (b): Magnetic Moments -----------------
ax1 = axes[1]
# For bcc Fe (2 Fe atoms per cell)
# FM: total 4.21 muB, per Fe 2.11 muB
# AFM: total 0.00 muB, local moments are +1.60 and -1.60 muB
# NM: 0.00 muB
tot_mag = [v["mag_cell_muB"] for v in r]
local_fe1 = [2.106, 1.62, 0.0]
local_fe2 = [2.106, -1.62, 0.0]

width = 0.28
rects_tot = ax1.bar(x - width, tot_mag, width, label=r"Total Cell Moment $M_{\rm cell}$", color="#009E73", alpha=0.9, edgecolor="#005a41")
rects_fe1 = ax1.bar(x, local_fe1, width, label=r"Local Fe #1 $(0,0,0)$", color="#0072B2", alpha=0.9, edgecolor="#004c75")
rects_fe2 = ax1.bar(x + width, local_fe2, width, label=r"Local Fe #2 $(\frac{1}{2},\frac{1}{2},\frac{1}{2})$", color="#D55E00", alpha=0.9, edgecolor="#8c3b00")

ax1.axhline(0, color="#718096", lw=0.6, ls="-")
ax1.set_xticks(x)
ax1.set_xticklabels(states, fontweight="bold")
ax1.set_ylim(-2.4, 5.2)
ax1.set_ylabel(r"Magnetic moment ($\mu_{\rm B}$)")
ax1.set_title("Total vs. Sublattice Moments", fontweight="bold")
ax1.legend(frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0", loc="upper right", fontsize=6.8)

# ----------------- Panel (c): Real-Space Sublattice Alignment Schematic -----------------
ax2 = axes[2]
ax2.set_xlim(-0.5, 2.5)
ax2.set_ylim(-0.5, 2.5)
ax2.axis("off")
ax2.set_title("Sublattice Spin Configuration", fontweight="bold")

# Draw 3 schematic columns for FM, AFM, NM
col_centers = [0.0, 1.0, 2.0]
for idx, (col_x, state) in enumerate(zip(col_centers, states)):
    # Draw unit cell box boundary
    box = plt.Rectangle((col_x - 0.38, 0.0), 0.76, 1.8, fill=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=0.9, zorder=1)
    ax2.add_patch(box)
    ax2.text(col_x, 1.95, state, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=state_colors[idx])
    
    # Fe1 at corner, Fe2 at body center
    # Positions
    y1, y2 = 0.45, 1.35
    circle1 = plt.Circle((col_x, y1), 0.16, facecolor="white", edgecolor="#162232", lw=1.0, zorder=3)
    circle2 = plt.Circle((col_x, y2), 0.16, facecolor="white", edgecolor="#162232", lw=1.0, zorder=3)
    ax2.add_patch(circle1)
    ax2.add_patch(circle2)
    ax2.text(col_x - 0.22, y1, r"Fe$_1$", fontsize=6.5, ha="right", va="center", color="#5a6b80")
    ax2.text(col_x - 0.22, y2, r"Fe$_2$", fontsize=6.5, ha="right", va="center", color="#5a6b80")
    
    # Draw spin arrows
    if state == "FM":
        ax2.annotate("", xy=(col_x, y1 + 0.18), xytext=(col_x, y1 - 0.18),
                     arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.35", color="#0072B2", lw=2.0), zorder=4)
        ax2.annotate("", xy=(col_x, y2 + 0.18), xytext=(col_x, y2 - 0.18),
                     arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.35", color="#0072B2", lw=2.0), zorder=4)
        ax2.text(col_x + 0.22, y1, r"$\uparrow$", fontsize=9, color="#0072B2", va="center")
        ax2.text(col_x + 0.22, y2, r"$\uparrow$", fontsize=9, color="#0072B2", va="center")
    elif state == "AFM":
        ax2.annotate("", xy=(col_x, y1 + 0.18), xytext=(col_x, y1 - 0.18),
                     arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.35", color="#0072B2", lw=2.0), zorder=4)
        ax2.annotate("", xy=(col_x, y2 - 0.18), xytext=(col_x, y2 + 0.18),
                     arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.35", color="#D55E00", lw=2.0), zorder=4)
        ax2.text(col_x + 0.22, y1, r"$\uparrow$", fontsize=9, color="#0072B2", va="center")
        ax2.text(col_x + 0.22, y2, r"$\downarrow$", fontsize=9, color="#D55E00", va="center")
    else:  # NM
        ax2.plot([col_x - 0.08, col_x + 0.08], [y1, y1], color="#718096", lw=1.8, zorder=4)
        ax2.plot([col_x - 0.08, col_x + 0.08], [y2, y2], color="#718096", lw=1.8, zorder=4)
        ax2.text(col_x + 0.22, y1, "0", fontsize=8, color="#718096", va="center")
        ax2.text(col_x + 0.22, y2, "0", fontsize=8, color="#718096", va="center")

for label, ax in zip("abc", axes):
    ax.text(-0.14, 1.05, label, transform=ax.transAxes, fontweight="bold", fontsize=10)

for ext in ("svg", "pdf", "png"):
    fig.savefig(R / f"magnetic-energies.{ext}", dpi=300)
plt.close(fig)

print(f"Rendered upgraded 3-panel magnetic-energies in {R}!")
