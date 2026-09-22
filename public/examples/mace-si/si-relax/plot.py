from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = np.genfromtxt("optimization.csv", delimiter=",", names=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True, layout="constrained")
axes[0].plot(data["step"], 1000 * (data["energy_eV"] - data["energy_eV"][0]) / 8, "o-", color="#176B87")
axes[0].set_ylabel("Energy change (meV/atom)")
axes[0].set_title("Diamond Si: fixed-cell MACE relaxation")
axes[1].semilogy(data["step"], data["fmax_eV_A"], "o-", color="#B45309")
axes[1].axhline(0.001, color="#555555", linestyle="--", label="force threshold")
axes[1].set(ylabel="Largest force (eV/angstrom)", xlabel="BFGS step")
axes[1].legend(frameon=False)
for ax in axes:
    ax.grid(alpha=0.18)
fig.savefig("relaxation.svg")
fig.savefig("relaxation.png", dpi=180)
print("relaxation.svg", "relaxation.png")
