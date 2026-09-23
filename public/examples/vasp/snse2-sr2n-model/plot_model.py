
from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def read(name):
    rows=list(csv.DictReader(open(name)))
    return rows,np.array([[float(r[k]) for k in ['x_A','y_A','z_A']] for r in rows])
r=json.load(open('model-check.json'));cell=np.array(r['reference']['cell'])
old,po=read('reference-atoms.csv');new,pn=read('gap3p0-atoms.csv')
colors={'Sn':'#cc79a7','Se':'#e69f00','Sr':'#0072b2','N':'#009e73'}
markers={'Sn':'o','Se':'o','Sr':'s','N':'D'}
fig,axes=plt.subplots(1,3,figsize=(11.5,6),layout='constrained',gridspec_kw={'width_ratios':[1.3,1,1]})
ax=axes[0]
for i in range(-1,2):
    for j in range(-1,2):
        points=po+i*cell[0]+j*cell[1]
        for row,p in zip(old,points):
            ax.scatter(p[0],p[1],s=100 if row['layer']=='SnSe2' else 45,c=colors[row['element']],marker=markers[row['element']],alpha=.65,edgecolors='white',linewidths=.5)
poly=np.array([[0,0],cell[0,:2],cell[0,:2]+cell[1,:2],cell[1,:2]])
ax.add_patch(Polygon(poly,closed=True,fill=False,ec='#30383c',lw=1.5))
ax.set(xlabel='x (Angstrom)',ylabel='y (Angstrom)',title='Unchanged lateral registry');ax.set_aspect('equal')
for ax,rows,points,key,title in [(axes[1],old,po,'reference','Reference geometry'),(axes[2],new,pn,'gap3p0','Rigid-layer model')]:
    for el in ['Sn','Se','N','Sr']:
        q=np.array([points[i] for i,row in enumerate(rows) if row['element']==el])
        ax.scatter(q[:,0],q[:,2],s=110,c=colors[el],marker=markers[el],edgecolors='white',linewidths=.5,label=el)
    upper=min(points[i,2] for i,row in enumerate(rows) if row['layer']=='SnSe2')
    lower=max(points[i,2] for i,row in enumerate(rows) if row['layer']=='Sr2N')
    xpos=3.15
    ax.annotate('',xy=(xpos,upper),xytext=(xpos,lower),arrowprops={'arrowstyle':'<->','color':'#45525a','lw':1})
    ax.text(xpos+.15,(upper+lower)/2,'%.3f A'%r[key]['normal_gap_A'],va='center',fontsize=9)
    ax.axhline(cell[2,2]/2,color='#999999',ls=':',lw=.8)
    ax.set(xlabel='x (Angstrom)',ylabel='z (Angstrom)',title=title,ylim=(0,cell[2,2]),xlim=(-1,5.4))
    ax.text(.04,.97,'Empty interval\n%.3f A'%r[key]['empty_interval_A'],transform=ax.transAxes,va='top',fontsize=9)
    ax.grid(axis='y',alpha=.15)
axes[2].legend(frameon=False,loc='lower right',fontsize=9)
fig.savefig('heterostructure-model.png',dpi=220)
fig.savefig('heterostructure-model.pdf')
