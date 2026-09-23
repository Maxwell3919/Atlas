import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from atlas_plot_style import install
install()
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "text.color": "black", "axes.labelcolor": "black", "axes.edgecolor": "black",
    "xtick.color": "black", "ytick.color": "black", "axes.linewidth": .7,
    "xtick.major.width": .7, "ytick.major.width": .7,
    "xtick.direction": "out", "ytick.direction": "out", "axes.grid": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"
})

data=np.genfromtxt("bader-grid.csv",delimiter=",",names=True)
if len(data)!=4:raise ValueError("Expected two atoms at two grids")
fig,axes=plt.subplots(1,2,figsize=(6.8,2.65),layout="constrained")
for atom,color,marker in [(1,"#0072B2","o"),(2,"#D55E00","s")]:
    r=data[data["atom"]==atom]
    axes[0].plot(r["grid"],1000*r["delta_e"],marker=marker,color=color,
                 ms=4,lw=1,label="Fe "+str(atom))
axes[0].axhline(0,color="black",lw=.65,ls=":")
axes[0].set(xlabel="Fine FFT grid",ylabel=r"$N_{\rm Bader}-Z_{\rm val}$ ($10^{-3}$ electrons)")
axes[0].legend(frameon=False)
r=data[data["atom"]==1]
axes[1].plot(r["grid"],r["core_integral_e"],"o-",color="#0072B2",ms=4,lw=1)
axes[1].axhline(36,color="black",ls="--",lw=.8,label="36 core electrons")
axes[1].set(xlabel="Fine FFT grid",ylabel="AECCAR0 integral (electrons)")
axes[1].legend(frameon=False,loc="upper right")
for label,ax in zip("ab",axes):
    ax.set_xticks([96,192],labels=[r"$96^3$",r"$192^3$"])
    ax.set_xlim(78,210);ax.text(-.16,1.03,label,transform=ax.transAxes,weight="bold",fontsize=9)
for ext in ("svg","pdf","png"):fig.savefig("bader-grid."+ext,dpi=300)
print("bader-grid.svg/pdf/png")
