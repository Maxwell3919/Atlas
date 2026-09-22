import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warmup = np.loadtxt("warmup.log", skiprows=1)
one = np.genfromtxt("nve-1fs.csv", delimiter=",", names=True)
half = np.genfromtxt("nve-0p5fs.csv", delimiter=",", names=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(3, 1, figsize=(8, 9), layout="constrained")
axes[0].plot(warmup[:, 0], warmup[:, 4], color="#6D28D9")
axes[0].axhline(300, color="#666666", linestyle="--", linewidth=1)
axes[0].set(title="64-atom Si with MACE-MP-0 small", ylabel="Temperature (K)",
            xlabel="Bussi warmup time (ps)")
for data, label, color in [(one, "1.0 fs", "#176B87"), (half, "0.5 fs", "#B45309")]:
    delta = 1000 * (data["total_eV_atom"] - data["total_eV_atom"][0])
    axes[1].plot(data["time_ps"], delta, label=label, color=color)
    axes[2].plot(data["time_ps"], data["temperature_K"], label=label, color=color)
axes[1].set(ylabel="Energy change (meV/atom)", xlabel="NVE time (ps)")
axes[2].set(ylabel="Temperature (K)", xlabel="NVE time (ps)")
for ax in axes:
    ax.grid(alpha=0.18)
for ax in axes[1:]:
    ax.legend(frameon=False, title="Time step")
fig.savefig("md-check.svg")
fig.savefig("md-check.png", dpi=180)
print("md-check.svg", "md-check.png")
