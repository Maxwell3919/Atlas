"""Replay saved printed residuals only; no GPAW/ASE import or solver call."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
root=Path(__file__).resolve().parent
rows=list(csv.DictReader((root/'scf-iterations.csv').open(newline='')))
assert len(rows)==80
plt.rcParams.update({'font.size':16,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(10,10.8),layout='constrained')
grid=fig.add_gridspec(3,1,height_ratios=[1,1,.30])
axes=[fig.add_subplot(grid[0]),fig.add_subplot(grid[1])]
axes[1].sharex(axes[0])
axes[0].tick_params(labelbottom=False)
for ax,key,threshold,title,unit,color in [
 (axes[0],'eigenstates_log10',-8,'All-band squared KS residual','eV² / valence electron','#2450ae'),
 (axes[1],'density_log10',-6,'Density change','electrons / valence electron','#a4441b')]:
 valid=[r for r in rows if r[key]!='']
 ax.plot([int(r['iteration']) for r in valid],[float(r[key]) for r in valid],'.-',color=color,markersize=5,linewidth=1.2,label='Printed log10 (2 decimals)')
 ax.axhline(threshold,color='#333',linestyle='--',linewidth=1.4,label=f'Threshold: {threshold}')
 ax.set_title(title,loc='left');ax.set_ylabel('log10(value in\n'+unit+')');ax.grid(alpha=.25);ax.legend(loc='upper right',fontsize=12)
 ax.set_ylim(min(threshold,min(float(r[key]) for r in valid))-1,max(float(r[key]) for r in valid)+1)
axes[1].set_xlabel('SCF iteration');axes[1].set_xlim(1,80);axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))
fig.suptitle('H / PBE / PW 340 eV / Γ · GPAW 26.7.0\n80 printed steps; native SCF did not converge',fontsize=18)
footer=fig.add_subplot(grid[2])
footer.set_axis_off()
warning=footer.text(0,.85,
    'Native exit 1 after 80 steps: KohnShamConvergenceError.\n'
    'Fractional-spin reference not run. No paired energy.\n'
    'No final measured energy, occupations, density or moment.',
    transform=footer.transAxes,fontsize=14,va='top',ha='left',linespacing=1.5)
# Reserve a separate footer row; fail instead of exporting cropped/overlapping text.
fig.canvas.draw()
renderer=fig.canvas.get_renderer()
box=warning.get_window_extent(renderer)
footer_box=footer.get_window_extent(renderer)
assert footer_box.contains(box.x0,box.y0) and footer_box.contains(box.x1,box.y1)
assert box.y1 < axes[1].get_window_extent(renderer).y0
fig.savefig(root/'residual.svg',metadata={'Date':None,'Creator':'Matplotlib; saved printed SCF tokens only'})
plt.close(fig)
