from __future__ import print_function
import json,math
from plane_average import read_grid,cross,dot
summary={}
for name in ['snse2','sr2n']:
 cell,grid,v=read_grid(name+'/CHGCAR')
 volume=abs(dot(cell[0],cross(cell[1],cell[2])))
 nxy=grid[0]*grid[1];height=abs(dot(cell[2],cross(cell[0],cell[1])))/math.sqrt(dot(cross(cell[0],cell[1]),cross(cell[0],cell[1])))
 z=[height*i/grid[2] for i in range(grid[2])]
 density=[sum(v[i*nxy:(i+1)*nxy])/nxy/volume for i in range(grid[2])]
 electrons=sum(v)/len(v)
 expected={'snse2':26,'sr2n':25}[name]
 if abs(electrons-expected)>1e-4: raise ValueError('CHGCAR integral does not match NELECT')
 row={'electrons':electrons,'volume_A3':volume,'grid':grid,'windows':[]}
 print('%s: integrated valence electrons=%.9f; volume=%.9f A^3'%(name,electrons,volume))
 for lo,hi in [(6.,10.),(29.,33.)]:
  a=[n for zz,n in zip(z,density) if lo<=zz<=hi]
  r={'lo_A':lo,'hi_A':hi,'mean_e_per_A3':sum(a)/len(a),'max_abs_e_per_A3':max(abs(x) for x in a)}
  row['windows'].append(r)
  print('  z=%.1f:%.1f A: mean density=%.6g; max abs density=%.6g e/A^3'%(lo,hi,r['mean_e_per_A3'],r['max_abs_e_per_A3']))
 summary[name]=row
json.dump(summary,open('vacuum-density.json','w'),indent=2,sort_keys=True)
