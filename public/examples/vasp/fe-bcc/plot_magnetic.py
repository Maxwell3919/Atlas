import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=json.load(open('magnetic-energies.json'))
fig,ax=plt.subplots(figsize=(6,4),layout='constrained')
x=[v['state'].upper() for v in r];y=[v['dE0_meV_atom'] for v in r]
ax.bar(x,y,color=['#297b70','#cc7652','#7d8798'],width=.55)
for i,v in enumerate(y): ax.text(i,v+12,'%.2f'%v,ha='center')
ax.set_ylim(0,max(y)*1.16)
ax.set_ylabel('Energy above FM (meV/atom)')
ax.set_title('bcc Fe, fixed a = 2.8 Angstrom; E(sigma->0)')
fig.savefig('magnetic-energies.png',dpi=220);fig.savefig('magnetic-energies.pdf')
