from __future__ import print_function
import math,json
f=open('ELFCAR')
header=[f.readline() for _ in range(8)]
if not header[-1].strip().lower().startswith('d'): raise ValueError('Expected Direct coordinate mode')
counts=list(map(int,header[6].split())); coords=[f.readline() for _ in range(sum(counts))]
blocks=[]; grids=[]
while True:
    line=f.readline()
    while line and not line.strip(): line=f.readline()
    if not line: break
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0: raise ValueError('Invalid ELF grid')
    n=grid[0]*grid[1]*grid[2];values=[]
    while len(values)<n:
        line=f.readline()
        if not line: raise ValueError('Truncated ELF block')
        values.extend(float(t) for t in line.split())
    if len(values)!=n: raise ValueError('Extra values in ELF block')
    if any(math.isnan(v) or math.isinf(v) for v in values): raise ValueError('Nonfinite ELF values')
    if min(values)<-1e-6 or max(values)>1+1e-6: raise ValueError('ELF outside expected 0..1 range')
    blocks.append(values);grids.append(grid)
if len(blocks)!=2 or grids[0]!=grids[1]: raise ValueError('Expected two equal spin ELF grids')
summary={'grid':grids[0],'blocks':[],'slice_fractional_z':0.0}
for tag,values in zip(['up','down'],blocks):
    nx,ny,nz=grids[0]
    with open('elf-'+tag+'-z0.dat','w') as out:
        for j in range(ny): out.write(' '.join('%.8f'%x for x in values[j*nx:(j+1)*nx])+'\n')
    row={'spin':tag,'points':len(values),'minimum':min(values),'maximum':max(values)}; summary['blocks'].append(row)
    print('%s grid=%s values=%d min=%.9g max=%.9g'%(tag,grids[0],len(values),min(values),max(values)))
json.dump(summary,open('elf-grid-check.json','w'),indent=2)
print('Wrote elf-up-z0.dat and elf-down-z0.dat; z=0 slice')
