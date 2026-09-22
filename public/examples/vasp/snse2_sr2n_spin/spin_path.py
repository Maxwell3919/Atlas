from __future__ import print_function
import re, math, json

def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
p=open('POSCAR').readlines(); scale=float(p[1]); cell=[[float(x)*scale for x in t.split()] for t in p[2:5]]
vol=dot(cell[0],cross(cell[1],cell[2])); rec=[[2*math.pi*x/vol for x in cross(cell[(i+1)%3],cell[(i+2)%3])] for i in range(3)]
ef=float(re.findall(r'E-fermi\s*:\s*([-0-9.]+)',open('SCF_OUTCAR').read())[-1])
rows=[]; dist=0.; prev=None; k=None; b=None; sums=[]
for line in open('PROCAR'):
    m=re.match(r'\s*k-point\s+(\d+)\s*:\s*([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)',line)
    if m:
        k=list(map(float,m.group(2,3,4))); ik=int(m.group(1))
        cart=[sum(k[i]*rec[i][j] for i in range(3)) for j in range(3)]
        if prev is not None: dist+=math.sqrt(sum((x-y)**2 for x,y in zip(cart,prev)))
        prev=cart
    m=re.match(r'\s*band\s+(\d+)\s+# energy\s+([-0-9.]+)\s+# occ.\s+([-0-9.]+)',line)
    if m:
        if b is not None and len(sums)!=4: raise ValueError('Need exactly four tot rows per band')
        b=int(m.group(1)); energy=float(m.group(2)); occ=float(m.group(3)); sums=[]
    if line.strip().startswith('tot '):
        sums.append(float(line.split()[-1]))
        if len(sums)==4:
            rows.append([ik,b,dist]+k+[energy,energy-ef,occ]+sums)
if len(sums)!=4: raise ValueError('Truncated last band')
if len(rows)!=150*72: raise ValueError('Unexpected k/band block count')
with open('spin-path.dat','w') as f:
    f.write('# ik band kdist_A-1 k1 k2 k3 energy_eV E-Ef_eV occupation charge mx my mz\n')
    for a in rows: f.write('%d %d '%(a[0],a[1])+' '.join('%.9f'%v for v in a[2:])+'\n')
summary={'nk':150,'nb':72,'nrows':len(rows),'fermi_scf_eV':ef,'axis':'default SAXIS=(0,0,1), Cartesian','quantity':'native PROCAR projected magnetization; no normalization','path_ticks_A-1':[rows[i*72][2] for i in [0,49,99,149]],'max_abs_mz':max(abs(a[-1]) for a in rows)}
json.dump(summary,open('spin-summary.json','w'),indent=2)
print('Parsed %d k-points x %d bands = %d four-block records'%(150,72,len(rows)))
print('SCF E-fermi = %.4f eV'%ef)
print('path ticks / A^-1 = '+str(summary['path_ticks_A-1']))
print('columns charge,mx,my,mz; output spin-path.dat')
