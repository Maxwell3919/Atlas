from __future__ import print_function
import sys,math,json

def read_scalar(name):
    f=open(name); header=[]
    title=f.readline(); header.append(title)
    scale_line=f.readline(); header.append(scale_line); scale=float(scale_line.split()[0])
    raw=[f.readline() for _ in range(3)];header+=raw; cell=[[float(x)*scale for x in t.split()[:3]] for t in raw]
    species=f.readline();header.append(species)
    if all(x.isdigit() for x in species.split()): counts=list(map(int,species.split())); species=''
    else:
        countline=f.readline();header.append(countline);counts=list(map(int,countline.split()))
    mode=f.readline();header.append(mode)
    if mode.strip().lower().startswith('s'): mode=f.readline();header.append(mode)
    raw=[f.readline() for _ in range(sum(counts))];header+=raw; coords=[[float(x) for x in t.split()[:3]] for t in raw]
    line=f.readline()
    while line and not line.strip(): line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0: raise ValueError('Invalid grid: '+name)
    n=grid[0]*grid[1]*grid[2]; values=[]
    while len(values)<n:
        line=f.readline()
        if not line: raise ValueError('Truncated scalar grid: '+name)
        values.extend(float(x.replace('D','E')) for x in line.split())
    if len(values)!=n: raise ValueError('Extra scalar values in last line: '+name)
    if not all(math.isfinite(x) if hasattr(math,'isfinite') else not(math.isnan(x) or math.isinf(x)) for x in values): raise ValueError('Nonfinite scalar')
    f.close()
    structure=[species.strip(),counts,mode.strip().lower(),cell,coords]
    return header,structure,grid,values

if __name__=='__main__':
    a=read_scalar('AECCAR0'); b=read_scalar('AECCAR2'); c=read_scalar('CHGCAR')
    if not(a[1]==b[1]==c[1]): raise ValueError('Cell, species, counts or coordinates differ')
    if not(a[2]==b[2]==c[2]): raise ValueError('FFT grids differ')
    if not(len(a[3])==len(b[3])==len(c[3])): raise ValueError('Scalar lengths differ')
    v=[x+y for x,y in zip(a[3],b[3])]; n=len(v)
    with open('CHGCAR_sum','w') as f:
        f.writelines(a[0]);f.write('\n%d %d %d\n'%tuple(a[2]))
        for i in range(0,n,5): f.write(' '.join('%18.11E'%x for x in v[i:i+5])+'\n')
    verify=read_scalar('CHGCAR_sum')
    if verify[2]!=a[2] or len(verify[3])!=n: raise ValueError('Read-back failed')
    report={'grid':a[2],'points':n,'AECCAR0_integral':sum(a[3])/n,'AECCAR2_integral':sum(b[3])/n,'CHGCAR_integral':sum(c[3])/n,'reference_integral':sum(v)/n,'scope':'first total-charge block only; no spin-density or augmentation blocks copied'}
    json.dump(report,open('charge-grid-check.json','w'),indent=2)
    for k in sorted(report): print('%s = %s'%(k,report[k]))
