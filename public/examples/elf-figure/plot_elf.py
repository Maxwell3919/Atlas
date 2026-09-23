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

data=[np.loadtxt("elf-"+tag+"-z0.dat") for tag in ("up","down")]
if any(a.shape!=(36,36) or not np.isfinite(a).all() for a in data):
    raise ValueError("Expected two finite 36 by 36 cuts")
if any(a.min()<0 or a.max()>1 for a in data):raise ValueError("ELF outside 0..1")
length=2.8
fig,axes=plt.subplots(1,2,figsize=(6.3,2.75),layout="constrained")
for label,ax,a,spin in zip("ab",axes,data,("up","down")):
    # Duplicate only the periodic endpoint; node positions remain i*L/N.
    closed=np.pad(a,((0,1),(0,1)),mode="wrap")
    x=np.arange(37)*length/36
    im=ax.pcolormesh(x,x,closed,shading="nearest",cmap="viridis",vmin=0,vmax=1,rasterized=True)
    ax.scatter([0,0,length,length],[0,length,0,length],s=20,facecolors="none",
               edgecolors="black",linewidths=.8,zorder=3)
    ax.set(xlim=(0,length),ylim=(0,length),xlabel=r"$x$ (Å)",ylabel=r"$y$ (Å)",
           title="Spin "+spin)
    ax.set_aspect("equal")
    ax.text(-.18,1.05,label,transform=ax.transAxes,weight="bold",fontsize=9)
fig.colorbar(im,ax=axes,label="ELF (dimensionless)",shrink=.9,ticks=[0,.25,.5,.75,1])
for ext in ("svg","pdf","png"):fig.savefig("elf-z0."+ext,dpi=300)
fig,ax=plt.subplots(figsize=(3.45,2.6),layout="constrained")
x=np.arange(37)*length/36
for a,tag,color,ls in zip(data,("Spin up","Spin down"),("#0072B2","#D55E00"),("-","--")):
    y=np.r_[a[0],a[0,0]]
    ax.plot(x,y,color=color,ls=ls,lw=1,marker="o",ms=2,label=tag)
ax.set(xlabel=r"$x$ (Å)",ylabel="ELF (dimensionless)",xlim=(0,length),ylim=(0,.28))
ax.legend(frameon=False)
for ext in ("svg","pdf","png"):fig.savefig("elf-linecut."+ext,dpi=300)
print("elf-z0.svg/pdf/png; elf-linecut.svg/pdf/png")
