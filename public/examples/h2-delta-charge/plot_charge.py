
from pathlib import Path
import csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from atlas_plot_style import install
install()
from matplotlib.colors import LinearSegmentedColormap
plt.rcParams.update({
 "font.family":"sans-serif","font.sans-serif":["Arial","DejaVu Sans"],"font.size":8,
 "axes.labelsize":8,"axes.titlesize":8,"xtick.labelsize":7,"ytick.labelsize":7,
 "text.color":"black","axes.labelcolor":"black","axes.edgecolor":"black",
 "xtick.color":"black","ytick.color":"black","axes.linewidth":.7,
 "xtick.direction":"out","ytick.direction":"out","axes.grid":False,
 "axes.spines.top":False,"axes.spines.right":False,"figure.facecolor":"white",
 "axes.facecolor":"white","savefig.facecolor":"white",
 "pdf.fonttype":42,"ps.fonttype":42,"svg.fonttype":"none"})
R=Path(__file__).resolve().parent
s=json.loads((R/"charge-difference-summary.json").read_text())
xy=np.genfromtxt(R/"delta-y5.csv",delimiter=",",names=True)
p=np.genfromtxt(R/"delta-planar.csv",delimiter=",",names=True)
nx,ny,nz=s["grid"]
if len(xy)!=nx*nz or len(p)!=nz+1:raise ValueError("Grid dimensions do not match")
x=xy["x_A"].reshape(nz,nx);z=xy["z_A"].reshape(nz,nx)
dn=xy["delta_n_e_A3"].reshape(nz,nx)
if not np.isfinite(dn).all():raise ValueError("Non-finite density")
cmap=LinearSegmentedColormap.from_list("depletion-white-accumulation",["#0072B2","white","#D55E00"])
lim=max(abs(s["minimum_delta_n_e_A3"]),abs(s["maximum_delta_n_e_A3"]))
fig,ax=plt.subplots(1,3,figsize=(7.2,2.7),layout="constrained")
im=ax[0].pcolormesh(x,z,dn,cmap=cmap,vmin=-lim,vmax=lim,shading="nearest",rasterized=True)
ax[0].contour(x,z,dn,levels=[-.05,-.02,-.005],colors="#0072B2",linewidths=.55,linestyles="dashed")
ax[0].contour(x,z,dn,levels=[.005,.02,.05],colors="#D55E00",linewidths=.55)
pos=np.asarray(s["positions_A"])
ax[0].scatter(pos[:,0],pos[:,2],s=18,facecolors="white",edgecolors="black",linewidths=.7,zorder=4)
ax[0].set(xlabel=r"$x$ ($\mathrm{\AA}$)",ylabel=r"$z$ ($\mathrm{\AA}$)",
          xlim=(3,7),ylim=(3,7),aspect="equal")
fig.colorbar(im,ax=ax[0],label=r"$\Delta n$ (e $\mathrm{\AA}^{-3}$)",fraction=.05,pad=.03)
ax[1].plot(p["z_A"],p["delta_N_e_A"],color="#0072B2",lw=1)
ax[1].axhline(0,color="black",lw=.5)
ax[1].set(xlabel=r"$z$ ($\mathrm{\AA}$)",ylabel=r"$A\langle\Delta n\rangle_{xy}$ (e $\mathrm{\AA}^{-1}$)",xlim=(0,10))
ax[2].plot(p["z_A"],p["cumulative_e"],color="#D55E00",lw=1)
ax[2].axhline(0,color="black",lw=.5)
ax[2].set(xlabel=r"$z$ ($\mathrm{\AA}$)",ylabel=r"$\int_0^z A\langle\Delta n\rangle_{xy}\,dz'$ (e)",xlim=(0,10))
for a in ax[1:]:
 for zz in pos[:,2]:a.axvline(zz,color="0.5",lw=.5,ls=":")
for label,a in zip("abc",ax):
 a.text(-.17,1.04,label,transform=a.transAxes,fontweight="bold",va="bottom")
for ext in ["png","pdf","svg"]:fig.savefig(R/("h2-charge-difference."+ext),dpi=300)
checks={"linear_colour_range_e_A3":[-lim,lim],"slice_y_A":5.,
 "grid":s["grid"],"cumulative_endpoint_e":float(p["cumulative_e"][-1]),
 "minimum_linear_density_e_A":float(p["delta_N_e_A"].min()),
 "maximum_linear_density_e_A":float(p["delta_N_e_A"].max()),
 "minimum_cumulative_e":float(p["cumulative_e"].min()),
 "maximum_cumulative_e":float(p["cumulative_e"].max())}
(R/"plot-checks.json").write_text(json.dumps(checks,indent=2)+"\n")
print("h2-charge-difference.png/pdf/svg; plot-checks.json")
