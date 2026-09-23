import json
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

z,v=np.loadtxt("PLANAR_AVERAGE.dat",unpack=True)
r=json.load(open("workfunction-summary.json"))
if len(z)!=280 or not np.isfinite(v).all():raise ValueError("Expected the 280-plane SnSe2 profile")
reference=r["windows"][0]["mean_eV"]
fig=plt.figure(figsize=(6.8,4.15),layout="constrained")
gs=fig.add_gridspec(2,2,height_ratios=[1.3,1])
main=fig.add_subplot(gs[0,:]);lo=fig.add_subplot(gs[1,0]);hi=fig.add_subplot(gs[1,1])
main.plot(z,v-reference,color="black",lw=.9,label="Planar electrostatic potential")
ef=r["fermi_eV"]-reference
main.axhline(ef,color="#0072B2",ls="--",lw=.9,label=r"$E_{\rm F}$")
main.axhline(0,color="black",ls=":",lw=.65)
for w in r["windows"]:
    main.axvspan(w["lo_A"],w["hi_A"],color="#999999",alpha=.12,lw=0)
main.annotate("",xy=(2.1,0),xytext=(2.1,ef),
              arrowprops=dict(arrowstyle="<->",color="black",lw=.7))
main.text(2.45,.5*ef,r"$\Phi=%.5f$ eV"%(-ef),va="center",fontsize=7)
main.set(xlabel=r"$z$ (Å)",ylabel=r"$\bar V(z)-V_{\rm vac,L}$ (eV)",xlim=(z[0],18.357298))
main.legend(frameon=False,loc="lower right")
for ax,w,color,marker in zip((lo,hi),r["windows"],("#0072B2","#D55E00"),("o","s")):
    mask=(z>=w["lo_A"])&(z<=w["hi_A"])
    ax.plot(z[mask],1000*(v[mask]-reference),color=color,marker=marker,ms=2.5,lw=.8)
    ax.axhline(1000*(w["mean_eV"]-reference),color="black",ls="--",lw=.65)
    ax.axhline(0,color="black",ls=":",lw=.5)
    ax.set(xlabel=r"$z$ (Å)",ylabel=r"$\bar V(z)-V_{\rm vac,L}$ (meV)",
           xlim=(w["lo_A"],w["hi_A"]),ylim=(-.15,.15))
    ax.set_xticks([w["lo_A"],(w["lo_A"]+w["hi_A"])/2,w["hi_A"]])
for label,ax in zip("abc",(main,lo,hi)):
    ax.text(-.11,1.04,label,transform=ax.transAxes,weight="bold",fontsize=9)
for ext in ("svg","pdf","png"):fig.savefig("workfunction-z."+ext,dpi=300)
print("workfunction-z.svg/pdf/png")
