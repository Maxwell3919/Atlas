#!/usr/bin/env python3
"""Plot only the paired tables; use the common parent-SCF energy reference."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
summary = json.loads((ROOT / "summary.json").read_text())
bands = np.genfromtxt(ROOT / "tables/bands.csv", delimiter=",", names=True)
dos = np.genfromtxt(ROOT / "tables/dos.csv", delimiter=",", names=True)
fat = np.genfromtxt(ROOT / "tables/fatband.csv", delimiter=",", names=True)
nk, nb = summary["path_kpoints"], summary["bands"]
x = bands["distance_Ainv"].reshape(nk,nb)[:,0]
energy = bands["energy_minus_scf_EF_eV"].reshape(nk,nb)
ticks = [item["distance_Ainv"] for item in summary["path_ticks"]]
labels = [r"$\Gamma$", "M", "K", r"$\Gamma$"]
plt.rcParams.update({"font.family":"DejaVu Serif","font.size":10,
                     "axes.linewidth":0.8,"xtick.direction":"in","ytick.direction":"in",
                     "xtick.top":True,"ytick.right":True,"svg.fonttype":"none",
                     "pdf.fonttype":42,"savefig.bbox":"tight"})
def path_axis(ax):
    ax.set_xlim(x[0],x[-1])
    ax.set_ylim(-7,4)
    ax.set_xticks(ticks,labels)
    ax.axhline(0,color="0.45",lw=0.7,ls="--")
    for tick in ticks[1:-1]:
        ax.axvline(tick,color="0.8",lw=0.6)
def export(fig,stem):
    for suffix in ("png","svg","pdf"):
        fig.savefig(FIG / f"{stem}.{suffix}",dpi=240)
    plt.close(fig)
    print(f"Exported figures/{stem}.png, .svg and .pdf")
fig,(ax,dx) = plt.subplots(1,2,figsize=(6.5,4.1),sharey=True,
                           gridspec_kw={"width_ratios":[2.1,1],"wspace":0.08})
ax.plot(x,energy,color="0.16",lw=0.65)
path_axis(ax)
ax.set_ylabel(r"$E-E_F^{\mathrm{SCF}}$ (eV)")
ax.set_title("(a) SnSe$_2$ bands",loc="left",fontsize=10)
dy = dos["energy_minus_scf_EF_eV"]
dx.plot(dos["total_DOS_states_per_eV_cell"],dy,color="0.12",lw=1,label="Total")
dx.plot(dos["Sn_s"],dy,color="#2B6CB0",lw=0.9,label="Sn s")
dx.plot(dos["Se_p"],dy,color="#B45309",lw=0.9,label="Se p")
visible = (dy >= -7) & (dy <= 4)
dx.set_xlim(0,1.08*np.max(dos["total_DOS_states_per_eV_cell"][visible]))
dx.axhline(0,color="0.45",lw=0.7,ls="--")
dx.set_xlabel("DOS (states/eV/cell)")
dx.set_title("(b) 18x18x1 SCF DOS",loc="left",fontsize=10)
dx.legend(frameon=False,fontsize=8,loc="lower right")
export(fig,"bands-dos")
fig,axes = plt.subplots(1,2,figsize=(6.5,4.1),sharey=True,
                        gridspec_kw={"wspace":0.08})
for ax,channel,color,title in zip(axes,["Sn_s","Se_p"],["#2B6CB0","#B45309"],
                                 ["(a) Sn s projection","(b) Se p projection"]):
    ax.plot(x,energy,color="0.7",lw=0.45,zorder=1)
    weights = fat[channel].reshape(nk,nb)
    ax.scatter(np.repeat(x,nb),energy.ravel(),s=20*weights.ravel(),
               c=color,linewidths=0,alpha=0.75,zorder=2)
    path_axis(ax)
    ax.set_title(title,loc="left",fontsize=10)
axes[0].set_ylabel(r"$E-E_F^{\mathrm{SCF}}$ (eV)")
export(fig,"fatband")
