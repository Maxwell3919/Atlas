
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import plotly.graph_objects as go
r=Path(__file__).resolve().parent;(r/"figures").mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(6.3,5.4),layout="constrained")
for n,style in [(24,"--"),(32,"-")]:
    e=np.load(r/f"fermi/k{n}-cg/fermi-grid.npz")["energy_eV"]
    x=np.arange(-n//2,n//2)/n
    for band,color in [(1,"#0072b2"),(2,"#d55e00")]:
        plane=np.fft.fftshift(e[:,:,0,band])
        ax.contour(x,x,plane.T,levels=[0],colors=[color],linestyles=[style],linewidths=1.5)
ax.set(xlabel="k₁ (reciprocal fractional coordinate)",ylabel="k₂ (reciprocal fractional coordinate)",title="Al Fermi-surface section at k₃=0",aspect="equal")
ax.legend(handles=[Line2D([0],[0],color="#0072b2",label="band 2"),Line2D([0],[0],color="#d55e00",label="band 3"),Line2D([0],[0],color="0.3",ls="--",label="24³ mesh"),Line2D([0],[0],color="0.3",label="32³ mesh")],frameon=False,fontsize=9)
fig.savefig(r/"figures/fermi-slices.png",dpi=220);fig.savefig(r/"figures/fermi-slices.pdf")
e=np.load(r/"fermi/k32-cg/fermi-grid.npz")["energy_eV"];n=e.shape[0]
x=np.arange(-n//2,n//2)/n;X,Y,Z=np.meshgrid(x,x,x,indexing="ij")
p=go.Figure()
for band,color in [(1,"#0072b2"),(2,"#d55e00")]:
    v=np.fft.fftshift(e[:,:,:,band])
    p.add_trace(go.Isosurface(x=X.ravel(),y=Y.ravel(),z=Z.ravel(),value=v.ravel(),isomin=-1e-7,isomax=1e-7,surface_count=1,opacity=.65,colorscale=[[0,color],[1,color]],showscale=False,caps=dict(x_show=False,y_show=False,z_show=False),name=f"band {band+1}",showlegend=True))
p.update_layout(title="Al: Eₙ(k) − E_F = 0, 32³ QE grid",scene=dict(xaxis_title="k₁",yaxis_title="k₂",zaxis_title="k₃",aspectmode="cube"),annotations=[dict(text="Reciprocal fractional cell; not a Wigner–Seitz BZ crop",xref="paper",yref="paper",x=.5,y=-.06,showarrow=False)],margin=dict(l=0,r=0,b=60,t=55))
p.write_html(r/"figures/fermi-surface.html",include_plotlyjs=True if "--standalone" in sys.argv else "cdn",full_html=True)
