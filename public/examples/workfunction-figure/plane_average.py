from __future__ import print_function
import sys, math, json, hashlib

def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def read_grid(name):
    f=open(name)
    title=f.readline().strip()
    scale=float(f.readline().split()[0])
    cell=[[float(x)*scale for x in f.readline().split()[:3]] for i in range(3)]
    if scale <= 0: raise ValueError('This reader requires a positive POSCAR scale')
    words=f.readline().split()
    if all(x.isdigit() for x in words):
        counts=list(map(int,words))
    else:
        counts=list(map(int,f.readline().split()))
    mode=f.readline().strip()
    if mode.lower().startswith('s'): mode=f.readline().strip()
    coords=[f.readline().split()[:3] for i in range(sum(counts))]
    line=f.readline()
    while line and not line.strip(): line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0: raise ValueError('Invalid FFT grid')
    n=grid[0]*grid[1]*grid[2]
    vals=[]
    while len(vals)<n:
        line=f.readline()
        if not line: raise ValueError('Truncated potential: %d/%d'%(len(vals),n))
        vals.extend(float(x.replace('D','E')) for x in line.split())
    if len(vals)!=n: raise ValueError('Unexpected extra values in scalar block')
    f.close()
    if any(math.isnan(x) or math.isinf(x) for x in vals):
        raise ValueError("Non-finite potential value")
    return cell,grid,vals

if __name__=='__main__':
    name=sys.argv[1] if len(sys.argv)>1 else 'LOCPOT'
    cell,grid,v=read_grid(name)
    area=math.sqrt(dot(cross(cell[0],cell[1]),cross(cell[0],cell[1])))
    height=abs(dot(cell[2],cross(cell[0],cell[1])))/area
    nxy=grid[0]*grid[1]
    avg=[sum(v[i*nxy:(i+1)*nxy])/nxy for i in range(grid[2])]
    zz=[height*i/grid[2] for i in range(grid[2])]
    with open('PLANAR_AVERAGE.dat','w') as f:
        f.write('# z_A  planar_potential_eV\n')
        for z,p in zip(zz,avg): f.write('%.10f %.12f\n'%(z,p))
    summary={'grid':grid,'points':len(v),'normal_height_A':height,'source_sha256':hashlib.sha256(open(name,'rb').read()).hexdigest(),'windows':[]}
    print('grid = %d %d %d; scalar values = %d'%tuple(grid+[len(v)]))
    print('normal height = %.10f A; output = PLANAR_AVERAGE.dat'%height)
    for spec in sys.argv[2:]:
        lo,hi=map(float,spec.split(':'))
        a=[p for z,p in zip(zz,avg) if lo<=z<=hi]
        if not a: raise ValueError('Empty averaging window')
        mean=sum(a)/len(a); std=math.sqrt(sum((x-mean)**2 for x in a)/len(a)); span=max(a)-min(a)
        row={'lo_A':lo,'hi_A':hi,'n':len(a),'mean_eV':mean,'std_eV':std,'range_eV':span}
        summary['windows'].append(row)
        print('window %.2f:%.2f A  N=%d  mean=%.9f eV  std=%.6g eV  range=%.6g eV'%(lo,hi,len(a),mean,std,span))
    with open('potential-summary.json','w') as f: json.dump(summary,f,indent=2,sort_keys=True)
