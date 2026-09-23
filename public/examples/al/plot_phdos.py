
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(6.8,4.3),layout="constrained")
for n,file in [(24,"al.phdos.dat"),(32,"al.phdos32.dat")]:
    d=np.loadtxt(root/"dfpt"/file)
    print(f"mesh={n} integral={np.trapezoid(d[:,1],d[:,0]):.8f}")
    ax.plot(d[:,0],d[:,1],label=f"{n}³ integration mesh",lw=1.8)
ax.set(xlabel="Frequency (cm⁻¹)",ylabel="Phonon DOS (states / cm⁻¹)",xlim=(0,None))
ax.legend(frameon=False);ax.grid(alpha=.18)
(root/"figures").mkdir(exist_ok=True)
fig.savefig(root/"figures/phdos.png",dpi=220)
fig.savefig(root/"figures/phdos.pdf")
