from __future__ import print_function
import os, re, math, json, hashlib, csv, gzip, io
BOHR = 0.529177210903

def det(cell):
    a,b,c=cell
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def finite(values):
    return all(not (math.isnan(x) or math.isinf(x)) for x in values)

def open_text(filename):
    if os.path.isfile(filename):
        return io.open(filename, 'r', encoding='ascii')
    if os.path.isfile(filename+'.gz'):
        return io.TextIOWrapper(gzip.open(filename+'.gz', 'rb'), encoding='ascii')
    raise IOError('Missing '+filename+' or '+filename+'.gz')

def digest(filename):
    if os.path.isfile(filename):
        handle=open(filename,'rb')
    elif os.path.isfile(filename+'.gz'):
        handle=gzip.open(filename+'.gz','rb')
    elif filename.endswith('/POTCAR') and os.path.isfile(filename+'.sha256'):
        value=open(filename+'.sha256').read().split()[0]
        if not re.match(r'^[0-9a-f]{64}$',value):
            raise ValueError('Invalid pseudopotential fingerprint')
        return value
    else:
        raise IOError('Missing source '+filename)
    sha=hashlib.sha256()
    while True:
        chunk=handle.read(1024*1024)
        if not chunk:break
        sha.update(chunk)
    handle.close()
    return sha.hexdigest()

def read_charge(filename):
    f=open_text(filename)
    head=[f.readline(),f.readline()]
    scale=float(head[1].split()[0])
    if scale<=0:raise ValueError('This example requires a positive scalar scale')
    lines=[f.readline() for _ in range(3)];head+=lines
    cell=[[float(x)*scale for x in line.split()[:3]] for line in lines]
    species=f.readline();counts_line=f.readline();head += [species,counts_line]
    counts=list(map(int,counts_line.split()));nat=sum(counts)
    mode=f.readline();head.append(mode)
    if mode.lower().startswith('s'):mode=f.readline();head.append(mode)
    coords_lines=[f.readline() for _ in range(nat)];head+=coords_lines
    coords=[[float(x) for x in line.split()[:3]] for line in coords_lines]
    if mode.lower().startswith('d'):
        positions=[[sum(v[k]*cell[k][a] for k in range(3)) for a in range(3)] for v in coords]
    elif mode.lower().startswith(('c','k')):
        positions=[[x*scale for x in v] for v in coords]
    else:raise ValueError('Unknown coordinate mode')
    line=f.readline()
    while line and not line.strip():line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0:raise ValueError('Invalid charge grid')
    n=grid[0]*grid[1]*grid[2]
    def block():
        values=[]
        while len(values)<n:
            line=f.readline()
            if not line:raise ValueError('Truncated scalar block')
            values.extend(float(x.replace('D','E')) for x in line.split())
        if len(values)!=n or not finite(values):raise ValueError('Invalid scalar block length/values')
        return values
    total=block()
    magnetic=None
    while True:
        line=f.readline()
        if not line:break
        words=line.split()
        if len(words)==3 and all(re.match(r'^\d+$',x) for x in words):
            candidate=list(map(int,words))
            if candidate==grid:
                magnetic=block();break
    f.close()
    if magnetic is None:raise ValueError('Expected second spin-density block')
    return dict(header=head,cell=cell,species=species.split(),counts=counts,
                positions=positions,grid=grid,total=total,magnetic=magnetic)

def incar(path):
    result={}
    for line in open(path):
        line=line.split('#',1)[0].split('!',1)[0]
        if '=' in line:
            key,value=line.split('=',1)
            if key.strip().upper() not in ('SYSTEM','MAGMOM'):
                result[key.strip().upper()]=value.strip()
    return result

cases={}
protocol=None
for name,expected_nelect,expected_mag in [('AB',2.,0.),('A',1.,1.),('B',1.,-1.)]:
    out=open(name+'/OUTCAR').read()
    if out.count('aborting loop because EDIFF is reached')!=1 or out.count('General timing and accounting')!=1:
        raise ValueError(name+': missing converged SCF / normal end')
    if re.search(r'VERY BAD NEWS|BRMIX:|Error EDD|ZHEGV failed',out,re.I):
        raise ValueError(name+': solver error')
    if 'Your FFT grids' in out:
        raise ValueError(name+': VASP reports an insufficient FFT grid')
    nelect=float(re.findall(r'NELECT\s*=\s*([-\d.]+)',out)[-1])
    mag=float(re.findall(r'mag=\s*([-\d.Ee+]+)',open(name+'/OSZICAR').read())[-1])
    data=read_charge(name+'/CHGCAR');n=len(data['total'])
    total=math.fsum(data['total'])/n
    spin=math.fsum(data['magnetic'])/n
    if abs(total-nelect)>1e-5 or abs(nelect-expected_nelect)>1e-8:
        raise ValueError(name+': electron count mismatch')
    if abs(mag-expected_mag)>2e-4 or abs(spin-mag)>2e-4:
        raise ValueError(name+': unexpected spin state')
    tags=incar(name+'/INCAR')
    if protocol is None:protocol=tags
    elif tags!=protocol:raise ValueError('Different electronic protocols')
    data.update(nelect=nelect,integral_e=total,mag_OSZICAR_muB=mag,mag_grid_muB=spin)
    cases[name]=data

ab,a,b=[cases[name] for name in ('AB','A','B')]
if not (ab['grid']==a['grid']==b['grid']):raise ValueError('FFT grids differ')
if not (ab['cell']==a['cell']==b['cell']):raise ValueError('Cells differ')
if not (ab['species']==a['species']==b['species']==['H']):raise ValueError('Expected the H model')
if ab['counts']!=[2] or a['counts']!=[1] or b['counts']!=[1]:raise ValueError('Wrong atom counts')
for point,target in [(a['positions'][0],ab['positions'][0]),(b['positions'][0],ab['positions'][1])]:
    if max(abs(x-y) for x,y in zip(point,target))>1e-6:raise ValueError('A fragment moved')
hashes={}
pot_hash=[]
for name in ('AB','A','B'):
    for filename in ('POSCAR','INCAR','KPOINTS','OUTCAR','OSZICAR','CHGCAR','POTCAR'):
        value=digest(name+'/'+filename)
        if filename=='POTCAR':pot_hash.append(value)
        else:hashes[name+'/'+filename]=value
if len(set(pot_hash))!=1:raise ValueError('Different pseudopotentials')
if len(set(open(name+'/KPOINTS').read() for name in ('AB','A','B')))!=1:
    raise ValueError('Different k sampling')
vol=abs(det(ab['cell']));nx,ny,nz=ab['grid'];n=nx*ny*nz
if max(abs(ab['cell'][i][j]-(10. if i==j else 0.)) for i in range(3) for j in range(3))>1e-8:
    raise ValueError('Plot extraction is specific to the 10 Angstrom cubic cell')
delta=[x-y-z for x,y,z in zip(ab['total'],a['total'],b['total'])]
integral=math.fsum(delta)/n
if abs(integral)>1e-5:raise ValueError('Charge difference does not integrate to zero')
positive=math.fsum(x for x in delta if x>0)/n
negative=math.fsum(x for x in delta if x<0)/n
nxy=nx*ny
plane=[math.fsum(delta[k*nxy:(k+1)*nxy])/nxy/vol for k in range(nz)]
linear=[100.*x for x in plane]
dz=10./nz
cumulative=[0.]
for k in range(1,nz+1):
    cumulative.append(cumulative[-1]+.5*(linear[k-1]+linear[k%nz])*dz)
with open('delta-planar.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['z_A','delta_n_e_A3','delta_N_e_A','cumulative_e'])
    for k in range(nz+1):
        writer.writerow(['%.10f'%(k*dz),'%.12e'%plane[k%nz],
                         '%.12e'%linear[k%nz],'%.12e'%cumulative[k]])
j=ny//2
with open('delta-y5.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['x_A','z_A','delta_n_e_A3'])
    for k in range(nz):
        for i in range(nx):
            writer.writerow(['%.10f'%(10.*i/nx),'%.10f'%(10.*k/nz),
                             '%.12e'%(delta[(k*ny+j)*nx+i]/vol)])
with open('CHGDIFF.vasp','w') as handle:
    handle.writelines(ab['header']);handle.write('\n%d %d %d\n'%(nx,ny,nz))
    for k in range(0,n,5):handle.write(' '.join('%.11E'%x for x in delta[k:k+5])+'\n')
# A Gaussian cube uses bohr and electrons/bohr^3; its z index runs fastest.
with open('delta-charge.cube','w') as handle:
    handle.write('H2 minus frozen spin-polarized H fragments\n')
    handle.write('Signed electron-number density in electrons/bohr^3\n')
    handle.write('%5d %13.8f %13.8f %13.8f\n'%(2,0.,0.,0.))
    for count,vector in zip((nx,ny,nz),ab['cell']):
        handle.write('%5d %13.8f %13.8f %13.8f\n'%tuple([count]+[v/count/BOHR for v in vector]))
    for position in ab['positions']:
        handle.write('%5d %13.8f %13.8f %13.8f %13.8f\n'%tuple([1,1.]+[v/BOHR for v in position]))
    line=[]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                line.append('%.10E'%(delta[(k*ny+j)*nx+i]/vol*BOHR**3))
                if len(line)==6:handle.write(' '.join(line)+'\n');line=[]
    if line:handle.write(' '.join(line)+'\n')
summary={'grid':ab['grid'],'volume_A3':vol,'positions_A':ab['positions'],
         'delta_integral_e':integral,'positive_integral_e':positive,'negative_integral_e':negative,
         'minimum_delta_n_e_A3':min(delta)/vol,'maximum_delta_n_e_A3':max(delta)/vol,
         'cumulative_endpoint_e':cumulative[-1],'potcar_sha256':pot_hash[0],
         'definition':'total-charge first block: AB - A - B; density = stored_value / cell_volume',
         'sha256':hashes,'cases':{}}
for name in ('AB','A','B'):
    summary['cases'][name]={key:cases[name][key] for key in
        ('nelect','integral_e','mag_OSZICAR_muB','mag_grid_muB')}
with open('charge-difference-summary.json','w') as handle:json.dump(summary,handle,indent=2,sort_keys=True)
for name in ('AB','A','B'):
    row=summary['cases'][name]
    print('%s NELECT=%.1f integral=%.10f e mag(OSZICAR)=%.4f mag(grid)=%.10f'%
          (name,row['nelect'],row['integral_e'],row['mag_OSZICAR_muB'],row['mag_grid_muB']))
print('grid = %d %d %d; points = %d; volume = %.6f A^3'%(nx,ny,nz,n,vol))
print('integral_delta = %.12e e; accumulated = %.10f e; depleted = %.10f e'%(integral,positive,negative))
print('delta_n range = %.10f to %.10f e/A^3'%(min(delta)/vol,max(delta)/vol))
print('cumulative endpoint = %.12e e'%cumulative[-1])
print('Wrote CHGDIFF.vasp, delta-charge.cube, delta-planar.csv, delta-y5.csv, charge-difference-summary.json')
