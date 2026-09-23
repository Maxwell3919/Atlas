from __future__ import print_function
import os, re, math, csv, json, hashlib

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read_poscar(path):
    lines=open(path).read().splitlines()
    scale=float(lines[1])
    if scale<=0:raise ValueError('Positive scalar POSCAR scale required')
    cell=[[float(x)*scale for x in line.split()[:3]] for line in lines[2:5]]
    species=lines[5].split();counts=list(map(int,lines[6].split()));nat=sum(counts)
    at=7
    if lines[at].lower().startswith('s'):at+=1
    mode=lines[at].lower();at+=1
    raw=[[float(x) for x in line.split()[:3]] for line in lines[at:at+nat]]
    if mode.startswith('d'):
        pos=[[sum(v[k]*cell[k][j] for k in range(3)) for j in range(3)] for v in raw]
    elif mode.startswith(('c','k')):
        pos=[[x*scale for x in v] for v in raw]
    else:raise ValueError('Unsupported coordinates')
    return cell,species,counts,pos

def area(cell):
    a,b=cell[:2]
    cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    return math.sqrt(sum(x*x for x in cross))

base='raw'
rows=[];excluded=[];fingerprints={}
reference=read_poscar(os.path.join(base,'scf_eq','POSCAR'))
protocol=[digest(os.path.join(base,'scf_eq',f)) for f in ('INCAR','KPOINTS')]
expected_titles=None
for name in sorted(os.listdir(base)):
    folder=os.path.join(base,name)
    if not os.path.isdir(folder) or not name.startswith('scf_'):continue
    outpath=os.path.join(folder,'OUTCAR')
    if not os.path.isfile(outpath):
        excluded.append(dict(directory=name,reason='OUTCAR absent',energy_lines=0,ediff=0,normal_end=0))
        continue
    out=open(outpath).read()
    energies=re.findall(r'energy\s+without entropy=\s*([-\d.]+)\s+energy\(sigma->0\)\s*=\s*([-\d.]+)',out)
    ediff=out.count('aborting loop because EDIFF is reached')
    normal=out.count('General timing and accounting')
    if len(energies)!=1 or ediff!=1 or normal!=1:
        excluded.append(dict(directory=name,reason='Incomplete static SCF',energy_lines=len(energies),ediff=ediff,normal_end=normal))
        continue
    if re.search(r'VERY BAD NEWS|BRMIX:|Error EDD|ZHEGV failed',out,re.I):
        raise ValueError(name+': electronic solver error')
    current=read_poscar(os.path.join(folder,'POSCAR'))
    if current[:3]!=reference[:3]:raise ValueError(name+': cell/species/counts changed')
    if [digest(os.path.join(folder,f)) for f in ('INCAR','KPOINTS')]!=protocol:
        raise ValueError(name+': input protocol differs')
    titles=re.findall(r'TITEL\s*=\s*(.*)',out)
    if expected_titles is None:expected_titles=titles
    if titles!=expected_titles:raise ValueError(name+': output pseudopotentials differ')
    if float(re.findall(r'NELECT\s*=\s*([-\d.]+)',out)[-1])!=156.:
        raise ValueError(name+': unexpected electron count')
    shifts=[[v-w for v,w in zip(p,q)] for p,q in zip(current[3],reference[3])]
    d=0. if name=='scf_eq' else float(name.split('scf_d')[1])
    for index,vec in enumerate(shifts):
        expected=d if index in (10,11,17) else 0.
        if max(abs(vec[0]),abs(vec[1]),abs(vec[2]-expected))>1e-7:
            raise ValueError(name+': incorrect frozen-layer displacement')
    energy=float(energies[0][0]);sigma=float(energies[0][1])
    ez=[v[2] for v in current[3]]
    outer_gap=current[0][2][2]-(max(ez)-min(ez))
    fingerprints[name]={f:digest(os.path.join(folder,f)) for f in
                       ('INCAR','KPOINTS','POSCAR','OUTCAR','OSZICAR','script_std')
                       if os.path.isfile(os.path.join(folder,f))}
    rows.append(dict(directory=name,d_A=d,energy_without_entropy_eV=energy,
                     energy_sigma0_eV=sigma,outer_periodic_gap_A=outer_gap))
rows.sort(key=lambda row:row['d_A'])
if len(rows)!=20 or [row['d_A'] for row in rows]!=[0.]+list(map(float,range(2,21))):
    raise ValueError('Expected exactly the verified 20-point set')
area_A2=area(reference[0]);e0=rows[0]['energy_without_entropy_eV']
for row in rows:
    row['delta_E_meV']=1000*(row['energy_without_entropy_eV']-e0)
    row['W_meV_A2']=row['delta_E_meV']/area_A2
    row['W_J_m2']=row['W_meV_A2']*.01602176634
keys=['directory','d_A','energy_without_entropy_eV','energy_sigma0_eV','delta_E_meV','W_meV_A2','W_J_m2','outer_periodic_gap_A']
with open('exfoliation.csv','w') as f:
    w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
with open('excluded.csv','w') as f:
    w=csv.DictWriter(f,['directory','reason','energy_lines','ediff','normal_end'],lineterminator='\n')
    w.writeheader();w.writerows(excluded)
summary=dict(natoms=18,species=reference[1],counts=reference[2],area_A2=area_A2,
             c_A=reference[0][2][2],moved_atom_indices_1based=[11,12,18],
             accepted_points=len(rows),excluded_points=len(excluded),
             energy_reference_eV=e0,energy_definition='energy without entropy',
             geometry_scope='Frozen prototype-derived HfI2 structure; no accepted HfI2 relaxation in this dataset',
             final_point=rows[-1],tail_16_to_20_range_meV=max(r['delta_E_meV'] for r in rows[-5:])-min(r['delta_E_meV'] for r in rows[-5:]),
             output_potential_titles=expected_titles,sha256=fingerprints)
with open('summary.json','w') as f:json.dump(summary,f,indent=2,sort_keys=True)
print('accepted=%d excluded=%d atoms=18 moved=11,12,18'%(len(rows),len(excluded)))
print('area=%.12f A^2 c=%.12f A'%(area_A2,reference[0][2][2]))
for row in rows:
    print('d=%4.1f A E=%14.8f eV dE=%10.5f meV W=%10.6f meV/A^2 outer_gap=%9.5f A'%
          (row['d_A'],row['energy_without_entropy_eV'],row['delta_E_meV'],row['W_meV_A2'],row['outer_periodic_gap_A']))
print('16--20 A energy range=%.5f meV'%summary['tail_16_to_20_range_meV'])
for row in excluded:
    print('excluded %s: %s energy=%d EDIFF=%d end=%d'%(row['directory'],row['reason'],row['energy_lines'],row['ediff'],row['normal_end']))
