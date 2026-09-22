from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout="constrained",sharey=True)
series=[[("n2-d0.01","0.01 Å", "#256b8e"),("n2-d0.02","0.02 Å", "#d97742")],[("n2-d0.01-k9","2³ supercell, 9³ k", "#256b8e"),("n3-d0.01","3³ supercell, 6³ k", "#d97742")]]
for ax,cases,title in zip(axes,series,["Displacement amplitude","Supercell range"]):
    for name,label,color in cases:
        x=np.genfromtxt(r/"finite-disp"/name/"bands.csv",delimiter=",",skip_header=1)
        for branch in [5,6,7]:ax.plot(x[:,1],x[:,branch],color=color,lw=1.3,label=label if branch==5 else None,alpha=.85)
    ticks=x[[0,40,81,122,163],1]
    ax.set_xticks(ticks,["Γ","X","W","L","Γ"])
    for p in ticks:ax.axvline(p,color="0.8",lw=.6)
    ax.axhline(0,color="0.3",lw=.7);ax.set(xlim=(ticks[0],ticks[-1]),title=title)
    ax.legend(frameon=False,fontsize=9)
axes[1].legend(frameon=False, fontsize=9, loc="lower center", bbox_to_anchor=(0.5, 0.07))
axes[0].set_ylabel("Frequency (cm⁻¹)")
(r/"figures").mkdir(exist_ok=True)
fig.savefig(r/"figures/finite-displacement.png",dpi=220);fig.savefig(r/"figures/finite-displacement.pdf")
