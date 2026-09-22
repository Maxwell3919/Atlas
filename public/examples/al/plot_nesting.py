from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
fig,axes=plt.subplots(1,2,figsize=(10.5,4.2),layout="constrained")
for n in [24,32]:
    for sigma in [.10,.20]:
        x=np.loadtxt(r/f"fermi/k{n}-cg/nesting-GX-s{sigma:.2f}.csv",delimiter=",",skiprows=1)
        label=f"{n}³, σ={sigma:.2f} eV"
        for ax,col in zip(axes,[1,2]):ax.plot(x[:,0],x[:,col],"o-",ms=3,lw=1.3,label=label)
for ax in axes:ax.set(xlabel="q = t(b₁+b₃), Γ → X",xlim=(0,.5));ax.grid(alpha=.2)
axes[0].set_ylabel("J(q) (eV⁻²)");axes[1].set_ylabel("J(q) / J(0)");axes[1].legend(frameon=False,fontsize=8)
(r/"figures").mkdir(exist_ok=True)
fig.savefig(r/"figures/fermi-nesting.png",dpi=220);fig.savefig(r/"figures/fermi-nesting.pdf")
