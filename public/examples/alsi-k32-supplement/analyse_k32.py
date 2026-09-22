#!/usr/bin/env python3
"""Recompute the matched k24/k32 Al--Si comparison from the bundled native files."""
from pathlib import Path
import csv,hashlib,json,math,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
RY_EV=13.605693122994
CASES={'al-fcc':(1,0),'al3si-l12':(3,1),'alsi-b2':(1,1),'alsi3-l12':(1,3),'si-diamond':(0,2)}
JOBS={'al-fcc/k24':839,'si-diamond/k24':840,'alsi-b2/k24':841,'al3si-l12/k24':842,'alsi3-l12/k24':843,'al-fcc/k32':844,'si-diamond/k32':845,'alsi-b2/k32':846,'al3si-l12/k32':847,'alsi3-l12/k32':848,'al3si-l12/k32-davidson':851}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def floats(node):return [float(v) for v in node.text.split()]
def read_run(case,label):
    d=ROOT/case/label;txt=(d/'scf.out').read_text();r=ET.parse(d/'data-file-schema.xml').getroot()
    assert txt.count('JOB DONE.')==1 and 'convergence has been achieved' in txt
    err=(d/'scf.err').read_text()
    assert all(line.strip()=='Authorization required, but no authorization protocol specified' for line in err.splitlines() if line.strip())
    assert not re.search(r'Error in routine|convergence NOT',txt,re.I)
    final=re.split(r'\n\s+iteration #\s*\d+',txt)[-1]
    assert 'not converged' not in final
    assert r.attrib['Units']=='Hartree atomic units'
    assert r.find('general_info/creator').get('VERSION')=='7.5'
    inp,out=r.find('input'),r.find('output')
    assert inp.find('control_variables/calculation').text.strip()=='scf'
    assert out.find('convergence_info/scf_conv/convergence_achieved').text.strip()=='true'
    error_Ry=float(out.find('convergence_info/scf_conv/scf_error').text)*2
    conv_Ry=float(inp.find('electron_control/conv_thr').text)*2
    assert error_Ry<conv_Ry and abs(conv_Ry-1e-10)<1e-20
    assert inp.find('dft/functional').text.strip()=='PBE'
    assert len(inp.find('dft'))==1  # No Hubbard, exact-exchange or dispersion additions.
    for key in ['lsda','noncolin','spinorbit']:assert inp.find('spin/'+key).text.strip()=='false'
    assert inp.find('bands/occupations').text.strip()=='smearing'
    smear=inp.find('bands/smearing');assert smear.text.strip()=='mv'
    assert abs(float(smear.get('degauss'))*2-.005)<1e-12
    assert abs(float(inp.find('bands/tot_charge').text))<1e-12
    assert float(inp.find('basis/ecutwfc').text)*2==80
    assert float(inp.find('basis/ecutrho').text)*2==640
    mesh=inp.find('k_points_IBZ/monkhorst_pack')
    nk=24 if label=='k24' else 32
    assert [int(mesh.get(k)) for k in ['nk1','nk2','nk3']]==[nk]*3
    assert [int(mesh.get(k)) for k in ['k1','k2','k3']]==[0]*3
    st=out.find('atomic_structure');at=st.findall('atomic_positions/atom')
    nAl,nSi=CASES[case];nat=nAl+nSi
    assert [a.get('name') for a in at].count('Al')==nAl
    assert [a.get('name') for a in at].count('Si')==nSi
    geom={'cell':[[round(v,9) for v in floats(st.find('cell/'+a))] for a in ['a1','a2','a3']],
          'atoms':[(a.get('name'),[round(v,9) for v in floats(a)]) for a in at]}
    species={sp.get('name'):sp.find('pseudo_file').text.strip() for sp in inp.find('atomic_species')}
    for el,file in species.items():assert file==el+'.pbe-n-rrkjus_psl.1.0.0.UPF'
    eRy=float(out.find('total_energy/etot').text)*2
    printed=float(re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry',txt)[-1]);assert abs(eRy-printed)<1e-7
    f=floats(out.find('forces'));fmax=max(math.sqrt(sum((2*v)**2 for v in f[i:i+3])) for i in range(0,len(f),3))
    native_time=re.findall(r'PWSCF\s+:.*?([0-9.mhs ]+) WALL',txt)[-1]
    terms=re.findall(r'(\d+(?:\.\d+)?)\s*([hms])',native_time)
    wall=sum(float(v)*{'h':3600,'m':60,'s':1}[unit] for v,unit in terms)
    return {'case':case,'protocol':label,'job_id':JOBS[case+'/'+label],'nAl':nAl,'nSi':nSi,'natoms':nat,'xSi':nSi/nat,
            'k_mesh':nk,'ecutwfc_Ry':80,'ecutrho_Ry':640,'degauss_Ry':.005,'total_energy_Ry':eRy,
            'final_pressure_kbar':float(re.findall(r'P=\s*([-\d.]+)',txt)[-1]),'max_force_Ry_per_bohr':fmax,
            'scf_error_Ry':error_Ry,'scf_iterations':int(out.find('convergence_info/scf_conv/n_scf_steps').text),
            'initial_eigensolver_warnings':txt.count('not converged'),'final_iteration_eigensolver_warnings':final.count('not converged'),
            'stderr_bytes':(d/'scf.err').stat().st_size,'wall_time_s':wall,
            'geometry_sha256':hashlib.sha256(json.dumps(geom,sort_keys=True).encode()).hexdigest(),
            'input_sha256':sha(d/'scf.in'),'output_sha256':sha(d/'scf.out'),'xml_sha256':sha(d/'data-file-schema.xml')}
def formation(rows):
    al=next(r for r in rows if r['case']=='al-fcc')['total_energy_Ry']
    si=next(r for r in rows if r['case']=='si-diamond')['total_energy_Ry']/2
    for row in rows:
        ref=row['nAl']*al+row['nSi']*si
        row['reference_energy_Ry']=ref
        row['formation_eV_atom']=(row['total_energy_Ry']-ref)*RY_EV/row['natoms']
    hull=[]
    for p in sorted(rows,key=lambda r:r['xSi']):
        while len(hull)>=2:
            a,b=hull[-2:]
            cross=(b['xSi']-a['xSi'])*(p['formation_eV_atom']-a['formation_eV_atom'])-(b['formation_eV_atom']-a['formation_eV_atom'])*(p['xSi']-a['xSi'])
            if cross>1e-12:break
            hull.pop()
        hull.append(p)
    for row in rows:
        for a,b in zip(hull,hull[1:]):
            if a['xSi']-1e-12<=row['xSi']<=b['xSi']+1e-12:
                wb=(row['xSi']-a['xSi'])/(b['xSi']-a['xSi']);wa=1-wb
                row.update(hull_eV_atom=wa*a['formation_eV_atom']+wb*b['formation_eV_atom'],hull_left=a['case'],hull_right=b['case'],left_atom_fraction=wa,right_atom_fraction=wb)
                row['above_hull_meV_atom']=(row['formation_eV_atom']-row['hull_eV_atom'])*1000
                assert row['above_hull_meV_atom']>=-1e-7
                break
    return [r['case'] for r in hull]
def main():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    for item in manifest['files']:assert sha(ROOT/item['file'])==item['public_sha256'],item['file']
    rows=[read_run(c,p) for p in ['k24','k32'] for c in CASES]
    checks=[]
    for c in CASES:
        a,b=[next(r for r in rows if r['case']==c and r['protocol']==p) for p in ['k24','k32']]
        assert a['geometry_sha256']==b['geometry_sha256'],c
        old=(ROOT/c/'k24/scf.in').read_text();new=(ROOT/c/'k32/scf.in').read_text()
        assert old.replace('24 24 24 0 0 0','32 32 32 0 0 0')==new,c
        assert a['initial_eigensolver_warnings']==b['initial_eigensolver_warnings']==0
    vertices={p:formation([r for r in rows if r['protocol']==p]) for p in ['k24','k32']}
    for c in CASES:
        a,b=[next(r for r in rows if r['case']==c and r['protocol']==p) for p in ['k24','k32']]
        delta=(b['formation_eV_atom']-a['formation_eV_atom'])*1000
        checks.append({'case':c,'k24_formation_eV_atom':a['formation_eV_atom'],'k32_formation_eV_atom':b['formation_eV_atom'],
                       'formation_change_meV_atom':delta,'within_1meV_atom':abs(delta)<=1,
                       'candidate_energy_change_meV_atom':(b['total_energy_Ry']-a['total_energy_Ry'])*RY_EV*1000/a['natoms'],
                       'reference_energy_change_meV_atom':(b['reference_energy_Ry']-a['reference_energy_Ry'])*RY_EV*1000/a['natoms']})
    final=[r for r in rows if r['protocol']=='k32'];david=read_run('al3si-l12','k32-davidson')
    cg=next(r for r in final if r['case']=='al3si-l12')
    assert cg['geometry_sha256']==david['geometry_sha256']
    solver_delta=(david['total_energy_Ry']-cg['total_energy_Ry'])*RY_EV*1000/4
    write_csv('energy-k24-k32.csv',rows);write_csv('formation-k32.csv',final);write_csv('comparison-k24-k32.csv',checks)
    receipt={'schema':'alsi-k32-supplement-v1','native_completion':'pass','matched_protocol':'pass','inputs_differ_only_in_kmesh':True,
             'native_numerics_unchanged':True,'k28_computed':False,'geometry':'Same constrained k12-optimized geometry as k24; no further ionic relaxation',
             'energy_definition':'QE ! total energy F=E-TS, matched mv sigma 0.005 Ry; not a physical-temperature free energy',
             'hull_vertices':vertices,'comparison_line_meV_atom':1.0,'max_change_meV_atom':max(abs(r['formation_change_meV_atom']) for r in checks),
             'within_1meV_atom':all(r['within_1meV_atom'] for r in checks),'scientific_acceptance':'not_assessed',
             'solver_comparison':{'cg_job':847,'davidson_job':851,'delta_meV_atom':solver_delta,'cg_initial_warnings':cg['initial_eigensolver_warnings'],'davidson_initial_warnings':david['initial_eigensolver_warnings'],'final_iteration_warnings':[cg['final_iteration_eigensolver_warnings'],david['final_iteration_eigensolver_warnings']]},
             'original_guard_status':'blocked: unsupported input assignments in the automated core; unmodified original audit retained. Native completion checked here independently.',
             'stderr':'All k32 files retain repeated X authorization messages; stderr is not empty.',
             'limitations':['No phonon or lower-symmetry stability claim.','No full phase diagram.','No k28 calculation.','Charge-density cutoff and zero-smearing limit are not checked here.']}
    (ROOT/'evidence/k32-analysis-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('case           job    E32 (Ry/cell)       formation (eV/atom)  delta24->32 (meV/atom)')
    for r in final:
        ck=next(t for t in checks if t['case']==r['case'])
        print(f"{r['case']:<15} {r['job_id']:3d} {r['total_energy_Ry']:18.10f} {r['formation_eV_atom']:20.8f} {ck['formation_change_meV_atom']:+21.6f}")
    print('Inputs differ only in k mesh: True')
    print('Finite-set hull vertices:',', '.join(vertices['k32']))
    print(f"Maximum formation-energy change: {receipt['max_change_meV_atom']:.6f} meV/atom")
    print('All changes within 1 meV/atom:',receipt['within_1meV_atom'])
    print(f'Davidson-CG Al3Si difference: {solver_delta:.9g} meV/atom')
if __name__=='__main__':main()
