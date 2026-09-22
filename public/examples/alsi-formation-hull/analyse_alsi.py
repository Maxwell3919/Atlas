#!/usr/bin/env python3
"""Read actual QE 7.5 outputs; compare matched Al--Si candidate sets."""
from pathlib import Path
import csv, hashlib, json, re, shutil, xml.etree.ElementTree as ET
import numpy as np

ROOT=Path(__file__).resolve().parent
RY_EV=13.605693122994
BOHR_A=0.529177210903
CASES={'al-fcc':(1,0),'al3si-l12':(3,1),'alsi-b2':(1,1),'alsi3-l12':(1,3),'si-diamond':(0,2)}
PROTOCOLS=['k12','k16','k20','sigma005','cutoff80','k24']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def numbers(node):return np.array([float(v) for v in node.text.split()])
def save_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def qexml(path):
    r=ET.parse(path).getroot()
    assert r.get('Units')=='Hartree atomic units'
    assert r.find('general_info/creator').get('VERSION')=='7.5'
    return r
def read_run(case,label):
    folder=ROOT/case/label
    txt=(folder/'scf.out').read_text()
    if txt.count('JOB DONE.')!=1 or 'convergence has been achieved' not in txt:
        raise ValueError(f'Incomplete native SCF: {case}/{label}')
    last_iteration=re.split(r'\n\s+iteration #\s*\d+',txt)[-1]
    if re.search(r'Error in routine|convergence NOT',txt,re.I) or 'not converged' in last_iteration:
        raise ValueError(f'Adverse native SCF: {case}/{label}')
    p=folder/'data-file-schema.xml'
    if not p.exists():shutil.copy2(folder/'tmp'/f'{case}.save'/'data-file-schema.xml',p)
    r=qexml(p);out=r.find('output')
    conv=out.find('convergence_info/scf_conv/convergence_achieved')
    assert conv is not None and conv.text.strip()=='true'
    e_ry=float(out.find('total_energy/etot').text)*2
    printed=float(re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry',txt)[-1])
    assert abs(e_ry-printed)<1e-7
    st=out.find('atomic_structure')
    cell=np.array([numbers(st.find('cell/'+a)) for a in ['a1','a2','a3']])
    atoms=st.findall('atomic_positions/atom')
    symbols=[a.get('name') for a in atoms]
    nAl,nSi=CASES[case];nat=nAl+nSi
    assert symbols.count('Al')==nAl and symbols.count('Si')==nSi
    shape={'cell':np.round(cell,9).tolist(),'symbols':symbols,'positions':[np.round(numbers(a),9).tolist() for a in atoms]}
    geometry_hash=hashlib.sha256(json.dumps(shape,sort_keys=True).encode()).hexdigest()
    inp=r.find('input')
    assert inp.find('dft/functional').text.strip()=='PBE'
    assert inp.find('spin/lsda').text.strip()=='false'
    assert inp.find('spin/noncolin').text.strip()=='false'
    assert inp.find('spin/spinorbit').text.strip()=='false'
    assert inp.find('bands/occupations').text.strip()=='smearing'
    smear=inp.find('bands/smearing');assert smear.text.strip()=='mv'
    mesh=inp.find('k_points_IBZ/monkhorst_pack')
    if mesh is None:raise ValueError('Missing echoed automatic mesh')
    k=[int(mesh.get(v)) for v in ['nk1','nk2','nk3']]
    assert len(set(k))==1
    assert [int(mesh.get(v)) for v in ['k1','k2','k3']]==[0,0,0]
    force=out.find('forces')
    fmax=float(np.linalg.norm(numbers(force).reshape(nat,3)*2,axis=1).max())
    row=dict(case=case,protocol=label,nAl=nAl,nSi=nSi,natoms=nat,xSi=nSi/nat,
             k_mesh=k[0],ecutwfc_Ry=float(inp.find('basis/ecutwfc').text)*2,
             ecutrho_Ry=float(inp.find('basis/ecutrho').text)*2,
             degauss_Ry=float(smear.get('degauss'))*2,total_energy_Ry=e_ry,
             energy_per_atom_eV=e_ry*RY_EV/nat,
             final_pressure_kbar=float(re.findall(r'P=\s*([-\d.]+)',txt)[-1]),
             initial_eigensolver_warnings=txt.count('not converged'),final_iteration_eigensolver_warnings=last_iteration.count('not converged'),
             max_force_Ry_per_bohr=fmax,volume_A3=abs(float(np.linalg.det(cell)))*BOHR_A**3,
             input_sha256=sha(folder/'scf.in'),output_sha256=sha(folder/'scf.out'),
             xml_sha256=sha(p),geometry_sha256=geometry_hash)
    return row
def lower_hull(rows):
    points=sorted(rows,key=lambda p:p['xSi'])
    hull=[]
    for p in points:
        while len(hull)>=2:
            a,b=hull[-2:]
            cross=(b['xSi']-a['xSi'])*(p['formation_eV_atom']-a['formation_eV_atom'])-(b['formation_eV_atom']-a['formation_eV_atom'])*(p['xSi']-a['xSi'])
            if cross>1e-12:break
            hull.pop()
        hull.append(p)
    return hull
def main():
    (ROOT/'plots').mkdir(exist_ok=True)
    rows=[read_run(c,p) for p in PROTOCOLS for c in CASES]
    for case in CASES:
        assert len({r['geometry_sha256'] for r in rows if r['case']==case})==1,'Geometry differs across numerical checks'
    for label in PROTOCOLS:
        rr=[r for r in rows if r['protocol']==label]
        for key in ['k_mesh','ecutwfc_Ry','ecutrho_Ry','degauss_Ry']:
            assert len({r[key] for r in rr})==1,f'Mixed {key} in {label}'
        al=next(r for r in rr if r['case']=='al-fcc')['total_energy_Ry']
        si=next(r for r in rr if r['case']=='si-diamond')['total_energy_Ry']/2
        for r in rr:
            r['reference_energy_Ry']=r['nAl']*al+r['nSi']*si
            r['formation_eV_formula']=(r['total_energy_Ry']-r['reference_energy_Ry'])*RY_EV
            r['formation_eV_atom']=r['formation_eV_formula']/r['natoms']
        hull=lower_hull(rr)
        for r in rr:
            for left,right in zip(hull,hull[1:]):
                if left['xSi']-1e-12<=r['xSi']<=right['xSi']+1e-12:
                    wr=(r['xSi']-left['xSi'])/(right['xSi']-left['xSi']);wl=1-wr
                    r.update(hull_eV_atom=wl*left['formation_eV_atom']+wr*right['formation_eV_atom'],
                             hull_left=left['case'],hull_right=right['case'],left_atom_fraction=wl,right_atom_fraction=wr)
                    break
            r['above_hull_eV_atom']=r['formation_eV_atom']-r['hull_eV_atom']
            assert r['above_hull_eV_atom']>=-1e-10
    save_csv(ROOT/'energy-table.csv',rows)
    final=[r for r in rows if r['protocol']=='k24']
    save_csv(ROOT/'formation-energy.csv',final)
    save_csv(ROOT/'formation-summary.csv',[{k:r[k] for k in ['case','natoms','xSi','total_energy_Ry','formation_eV_atom','above_hull_eV_atom']} for r in final])
    checks=[]
    for case in CASES:
        if case in ['al-fcc','si-diamond']:continue
        d={r['protocol']:r for r in rows if r['case']==case}
        for a,b,axis in [('k12','k16','k mesh at sigma .01'),('k16','k20','k mesh at sigma .01'),('k20','sigma005','smearing at k20'),('sigma005','cutoff80','wavefunction cutoff at k20'),('cutoff80','k24','k mesh at sigma .005')]:
            delta=(d[b]['formation_eV_atom']-d[a]['formation_eV_atom'])*1000
            checks.append(dict(case=case,axis=axis,from_protocol=a,to_protocol=b,formation_change_meV_atom=delta,within_1meV_atom=abs(delta)<=1.0))
    save_csv(ROOT/'numerical-checks.csv',checks)
    receipt={'schema':'alsi-evidence-v1','qe_version':'7.5','energy_definition':'QE ! total energy, finite cold-smearing F=E-TS, identical setting for all five candidates within each protocol',
             'scientific_acceptance':'not_assessed','candidate_scope':'Five constrained cubic prototypes only; no global structure search, phonon/free-energy or experimental claim',
             'geometry_optimization':'Native BFGS with cell_dofree=ibrav; initial Davidson warnings preserved. Final independent CG static inputs/outputs are checked separately.',
             'numerical_line_meV_atom':1.0,'reference_per_atom_Ry':{r['case']:r['total_energy_Ry']/r['natoms'] for r in final if r['case'] in ['al-fcc','si-diamond']},
             'hull_vertices':[r['case'] for r in lower_hull(final)],'files':{str(p.relative_to(ROOT)):sha(p) for r in rows for p in [ROOT/r['case']/r['protocol']/name for name in ['scf.in','scf.out','scf.err','data-file-schema.xml']]},
             'checks':checks}
    (ROOT/'evidence/analysis-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('case           xSi   total_energy(Ry/cell) formation(eV/atom) above_hull(eV/atom)')
    for r in final:
        print(f"{r['case']:<15} {r['xSi']:4.2f} {r['total_energy_Ry']:20.10f} {r['formation_eV_atom']:18.8f} {r['above_hull_eV_atom']:19.8f}")
    print('Finite-set hull vertices:',', '.join(receipt['hull_vertices']))
    print('Numerical differences: numerical-checks.csv (1 meV/atom teaching comparison line)')
if __name__=='__main__':main()
