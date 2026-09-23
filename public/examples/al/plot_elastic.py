
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
p=np.genfromtxt(r/"elastic/kmesh-comparison.csv",delimiter=",",names=True)
(r/"figures").mkdir(exist_ok=True)
for file,cols in [("elastic-kmesh",["C11_GPa","C12_GPa","C44_GPa","B_GPa"]),("elastic-moduli",["B_GPa","GH_GPa","E_GPa"])]:
    fig,ax=plt.subplots(figsize=(6.8,4.4),layout="constrained")
    for name in cols:ax.plot(p["kmesh"],p[name],"o-",lw=1.6,label=name.replace("_GPa",""))
    ax.set(xlabel="n in the n × n × n electronic mesh",ylabel="Elastic response (GPa)")
    ax.set_xticks(p["kmesh"]);ax.legend(frameon=False);ax.grid(alpha=.2)
    fig.savefig(r/f"figures/{file}.png",dpi=220);fig.savefig(r/f"figures/{file}.pdf")
