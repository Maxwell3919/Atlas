"""Compare two dynmat runs of one unchanged Si Gamma matrix.

Run next to si-no.modes and si-crystal.modes. Needs NumPy and Matplotlib.
Numbers are read from files; negative frequencies are never clipped.
"""
from pathlib import Path
import csv
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def frequencies(filename):
    text = Path(filename).read_text()
    values = re.findall(r"freq\s*\(\s*\d+\)\s*=.*?=\s*([-+\d.Ee]+)\s*\[cm-1\]", text)
    result = np.array([float(value) for value in values])
    if len(result) != 6 or not np.isfinite(result).all():
        raise ValueError(f"Expected six finite Gamma frequencies in {filename}")
    return result

raw = frequencies("si-no.modes")
asr = frequencies("si-crystal.modes")
with open("asr-comparison.csv", "w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["mode", "no_asr_cm-1", "crystal_asr_cm-1", "change_cm-1"])
    writer.writerows((i + 1, x, y, y - x) for i, (x, y) in enumerate(zip(raw, asr)))

plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none"})
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.7))
for ax, indices, title in [(axes[0], np.arange(3), "Acoustic modes (zoom)"),
                            (axes[1], np.arange(3, 6), "Optical modes")]:
    x = indices + 1
    ax.scatter(x - .08, raw[indices], s=70, facecolors="none",
               edgecolors="#2450ae", linewidths=1.6, label="ASR = no", zorder=3)
    ax.scatter(x + .08, asr[indices], s=50, marker="x", color="#b6682b",
               linewidths=1.8, label="ASR = crystal", zorder=3)
    ax.set(xticks=x, xlabel="Mode index", title=title, ylabel="Frequency (cm$^{-1}$)")
    ax.grid(axis="y", alpha=.18)
axes[0].axhline(0, color="#404040", lw=.8)
axes[0].set_ylim(-6.4, 1.0)
axes[0].text(2, -5.0, "-5.586079 → about 0", ha="center", fontsize=10)
axes[1].set_ylim(520, 528)
axes[1].text(5, 525, "523.722542 in both runs", ha="center", fontsize=10)
axes[0].legend(frameon=False, loc="center right")
fig.suptitle("Si at Γ: diagonalize the same matrix twice", x=.09, ha="left", fontsize=15)
fig.text(.09, .895, "QE 7.5 · fixed input structure · two separate vertical scales", fontsize=10, color="#555555")
fig.tight_layout(rect=(0, 0, 1, .87))
for ext in ("svg", "png", "pdf"):
    fig.savefig(f"si-gamma-asr.{ext}", dpi=180, facecolor="white")
print("asr-comparison.csv; si-gamma-asr.svg/png/pdf")
