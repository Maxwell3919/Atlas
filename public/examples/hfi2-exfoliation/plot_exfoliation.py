import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = np.genfromtxt("exfoliation.csv", delimiter=",", names=True)
x = data["displacement_A"]
y = data["delta_energy_meV_cell"]
assert len(x) == 21 and np.all(np.isfinite(y))
plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none"})
fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), layout="constrained")
axes[0].plot(x, y, "o-", color="#2450ae", markersize=4)
axes[0].set(ylim=(0, None), xlabel="Top-layer displacement (angstrom)",
            ylabel="E(displacement) - E(0) (meV/cell)", title="All 21 recorded points")
tail = x >= 14
axes[1].plot(x[tail], y[tail], "o-", color="#b6682b", markersize=5)
axes[1].set(xlabel="Top-layer displacement (angstrom)",
            ylabel="E(displacement) - E(0) (meV/cell)", title="Final points on an expanded scale")
for ax in axes:
    ax.grid(axis="y", alpha=0.2)
fig.suptitle("HfI2: one-layer separation at fixed geometry", fontsize=14)
fig.savefig("exfoliation-repro.svg")
fig.savefig("exfoliation-repro.png", dpi=180)
print("exfoliation-repro.svg")
print("exfoliation-repro.png")
