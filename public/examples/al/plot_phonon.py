from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=np.loadtxt(r/"dfpt/al.freq.gp")
assert d.shape==(161,4), d.shape
fig,ax=plt.subplots(figsize=(7,4.3),layout="constrained")
for i in range(1,4):ax.plot(d[:,0],d[:,i],lw=1.6,color="#236990")
ticks=d[[0,40,80,120,160],0]
ax.set_xticks(ticks,["Γ","X","W","L","Γ"])
for x in ticks:ax.axvline(x,color="0.8",lw=.7)
ax.axhline(0,color="0.4",lw=.7)
ax.set(xlim=(ticks[0],ticks[-1]),ylabel="Frequency (cm⁻¹)")
(r/"figures").mkdir(exist_ok=True)
fig.savefig(r/"figures/phonon-dfpt.png",dpi=220);fig.savefig(r/"figures/phonon-dfpt.pdf")
