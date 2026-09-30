#!/usr/bin/env python3
"""Plot the actual full-cell planar LVHAR profile used to inspect the vacuum plateau."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from atlas_plot_style import install

install()


def poscar_atomic_extent(path: Path, normal_height: float, normal: np.ndarray) -> tuple[float, float]:
    """Return the z extent of atomic coordinates projected along the cell normal."""
    lines = path.read_text().splitlines()
    scale = float(lines[1].split()[0])
    cell = np.asarray([[float(x) for x in lines[i].split()[:3]] for i in (2, 3, 4)]) * scale
    i = 5
    fields = lines[i].split()
    i += 1
    if all(word.lstrip("+").isdigit() for word in fields):
        counts = [int(word) for word in fields]
    else:
        counts = [int(word) for word in lines[i].split()]
        i += 1
    if lines[i].strip().lower().startswith("s"):
        i += 1
    mode = lines[i].strip().lower()
    i += 1
    coordinates = np.asarray([
        [float(x) for x in lines[i + j].split()[:3]]
        for j in range(sum(counts))
    ])
    if mode.startswith("d"):
        cartesian = coordinates @ cell
    elif mode.startswith(("c", "k")):
        cartesian = coordinates * scale
    else:
        raise ValueError(f"Unsupported POSCAR coordinate mode: {mode!r}")
    z = np.mod(cartesian @ normal, normal_height)
    return float(z.min()), float(z.max())


profile_path = Path("PLANAR_AVERAGE.dat")
summary_path = Path("workfunction-summary.json")
if not profile_path.is_file() or not summary_path.is_file():
    raise FileNotFoundError("Run analyze_workfunction.py first")

profile = np.loadtxt(profile_path, comments="#")
summary = json.loads(summary_path.read_text())
windows = sorted(summary["windows"], key=lambda item: item["lo_A"])
if profile.ndim != 2 or profile.shape[1] != 2:
    raise ValueError("Expected z_A and planar_potential_eV columns")
if len(windows) != 2:
    raise ValueError("This example expects its two measured surface vacuum windows")
z, potential = profile[:, 0], profile[:, 1]
height = float(summary["normal_height_A"])
if not np.all(np.isfinite(profile)) or z.max() >= height:
    raise ValueError("Profile contains invalid values or an out-of-cell z coordinate")

cell = np.asarray([[float(x) for x in line.split()[:3]]
                   for line in Path("POSCAR").read_text().splitlines()[2:5]], dtype=float)
scale = float(Path("POSCAR").read_text().splitlines()[1].split()[0])
cell *= scale
normal = np.cross(cell[0], cell[1])
normal /= np.linalg.norm(normal)
if np.dot(cell[2], normal) < 0:
    normal *= -1.0
atom_lo, atom_hi = poscar_atomic_extent(Path("POSCAR"), height, normal)

vacuum_reference = float(windows[0]["mean_eV"])
relative_potential = potential - vacuum_reference
fermi_relative = float(summary["fermi_eV"]) - vacuum_reference
work_function = vacuum_reference - float(summary["fermi_eV"])
colors = ("#0072b2", "#d55e00")

fig, ax = plt.subplots(figsize=(8.1, 4.8), layout="constrained")
ax.plot(z, relative_potential, color="#222222", lw=1.25,
        label=r"Planar-averaged $V_{\mathrm{LVHAR}}(z)$")
ax.axhline(0.0, color=colors[0], ls="--", lw=1.0,
           label="Lower-z vacuum reference")
ax.axhline(fermi_relative, color=colors[1], ls="-.", lw=1.0,
           label=r"$E_F$ from the same SCF")
ax.axvspan(atom_lo, atom_hi, color="#777777", alpha=0.12, zorder=0)
for window in windows:
    ax.axvspan(window["lo_A"], window["hi_A"], color=colors[0], alpha=0.08, zorder=0)

handles = [
    Line2D([0], [0], color="#222222", lw=1.25,
           label=r"Planar-averaged $V_{\mathrm{LVHAR}}(z)$"),
    Line2D([0], [0], color=colors[0], ls="--", lw=1.0,
           label="Lower-z vacuum reference"),
    Line2D([0], [0], color=colors[1], ls="-.", lw=1.0,
           label=r"$E_F$ from the same SCF"),
    Patch(facecolor="#777777", alpha=0.12, label="Atomic z extent from POSCAR"),
    Patch(facecolor=colors[0], alpha=0.08, label="Vacuum windows used in the table"),
]
ax.legend(handles=handles, frameon=False, ncols=2, loc="lower left")
arrow_x = 2.55
ax.annotate(
    "", xy=(arrow_x, fermi_relative), xytext=(arrow_x, 0.0),
    arrowprops={"arrowstyle": "<->", "color": colors[1], "lw": 1.1},
)
ax.text(arrow_x + 0.22, 0.5 * fermi_relative,
        rf"$\Phi={work_function:.4f}\ \mathrm{{eV}}$",
        color=colors[1], ha="left", va="center")

span = float(relative_potential.max() - relative_potential.min())
ax.set_xlim(0.0, height)
ax.set_ylim(relative_potential.min() - 0.04 * span,
            relative_potential.max() + 0.04 * span)
ax.set_xlabel("Distance along the surface normal (Å)")
ax.set_ylabel(r"$\bar{V}(z)-V_{\mathrm{vac,lower}}$ (eV)")
ax.set_title(r"SnSe$_2$ monolayer: planar-averaged LVHAR and work-function reference")
ax.grid(False)

output = "interface-magnet-workfunction-profile.png"
fig.savefig(output)
plt.close(fig)

upper_minus_lower = float(windows[1]["mean_eV"] - windows[0]["mean_eV"])
print(f"Wrote interface-magnet-workfunction-profile.png, .svg, and .pdf")
print(f"Lower-z Vvac = {vacuum_reference:.9f} eV; E_F = {summary['fermi_eV']:.6f} eV")
print(f"Phi at the printed E_F = {work_function:.9f} eV")
print(f"Upper-minus-lower vacuum mean = {upper_minus_lower * 1000.0:+.5f} meV")
print("That last difference is reported numerically only; it is not resolved as a material effect.")

