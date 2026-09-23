
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = np.genfromtxt("optimization.csv", delimiter=",", names=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(3, 1, figsize=(7, 8), sharex=True, layout="constrained")
axes[0].plot(data["step"], 1000 * (data["energy_eV"] - data["energy_eV"][0]) / 8, "o-", color="#0072b2")
axes[0].set_ylabel("Energy change (meV/atom)")
axes[0].set_title("Diamond Si: variable-cell MACE relaxation")
axes[1].plot(data["step"], data["volume_A3"], "o-", color="#cc79a7")
axes[1].set_ylabel("Cell volume (angstrom^3)")
axes[2].semilogy(data["step"], data["fmax_eV_A"], "o-", color="#B45309")
axes[2].axhline(0.001, color="#555555", linestyle="--", label="atomic-force threshold")
axes[2].set(ylabel="Largest force (eV/angstrom)", xlabel="BFGS step")
axes[2].legend(frameon=False)
for ax in axes:
    ax.grid(alpha=0.18)
fig.savefig("cell-relaxation.svg")
fig.savefig("cell-relaxation.png", dpi=180)
print("cell-relaxation.svg", "cell-relaxation.png")
