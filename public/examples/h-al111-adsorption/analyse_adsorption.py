#!/usr/bin/env python3
"""Read a matched, finite H/Al(111) teaching calculation; no fitted energies."""
from pathlib import Path
import csv,hashlib,json,re,shutil,xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parent
BOHR_A=0.529177210903;RY_EV=13.605693122994
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(n):return np.array([float(v) for v in n.text.split()])
def save_csv(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def read_run(name,stem):
    d=ROOT/name;txt=(d/(stem+'.out')).read_text();audit=json.loads((d/'output-audit.json').read_text())
    assert audit['decision']=='pass',(name,audit['findings'])
    assert txt.count('JOB DONE.')==1 and 'convergence has been achieved' in txt
    assert not re.search(r'Error in routine|convergence NOT achieved after',txt,re.I)
    last_iteration=txt.rsplit('iteration #',1)[-1]
    assert 'not converged' not in last_iteration
    if stem=='relax':assert 'bfgs converged' in txt and 'End final coordinates' in txt
    q=d/'data-file-schema.xml'
    if not q.exists():
        xs=list((d/'tmp').glob('*.save/data-file-schema.xml'));assert len(xs)==1
        shutil.copy2(xs[0],q)
    for role,p in [('input',d/(stem+'.in')),('output',d/(stem+'.out')),('stderr',d/(stem+'.err'))]:
        assert audit['evidence'][role]['sha256']==sha(p),(name,role,'content changed after audit')
    r=ET.parse(q).getroot();assert r.get('Units')=='Hartree atomic units'
    assert r.find('general_info/creator').get('VERSION')=='7.5'
    inp=r.find('input');out=r.find('output');st=out.find('atomic_structure')
    assert out.find('convergence_info/scf_conv/convergence_achieved').text.strip()=='true'
    assert inp.find('dft/functional').text.strip()=='PBE'
    for key in ['lsda','noncolin','spinorbit']:assert inp.find('spin/'+key).text.strip()=='false'
    assert inp.find('bands/occupations').text.strip()=='smearing'
    smear=inp.find('bands/smearing');assert smear.text.strip()=='mv'
    assert abs(float(smear.get('degauss'))*2-.01)<1e-12
    assert abs(float(inp.find('basis/ecutwfc').text)*2-60)<1e-10
    assert abs(float(inp.find('basis/ecutrho').text)*2-640)<1e-10
    cell=np.array([arr(st.find('cell/'+a)) for a in ['a1','a2','a3']])*BOHR_A
    atoms=st.findall('atomic_positions/atom');pos=np.array([arr(a) for a in atoms])*BOHR_A
    symbols=[a.get('name') for a in atoms]
    forces=arr(out.find('forces')).reshape(len(atoms),3)*2
    fmax=float(np.abs(forces).max())
    if stem=='relax':assert fmax<=2e-4,(name,fmax)
    e=float(out.find('total_energy/etot').text)*2
    assert abs(e-float(re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry',txt)[-1]))<1e-7
    time=re.findall(r'PWSCF\s*:\s*[^\n]*CPU\s+([^\n]+?)\s+WALL',txt)[-1]
    wall=sum(float(n)*{'h':3600,'m':60,'s':1}[u] for n,u in re.findall(r'(\d+(?:\.\d+)?)\s*([hms])',time))
    row=dict(case=name,stage=stem,nAl=symbols.count('Al'),nH=symbols.count('H'),total_energy_Ry=e,
             max_force_component_Ry_Bohr=fmax,initial_eigen_warnings=txt.count('not converged'),final_iteration_eigen_warnings=last_iteration.count('not converged'),native_wall_s=wall,stderr_bytes=(d/(stem+'.err')).stat().st_size,
             input_sha256=sha(d/(stem+'.in')),output_sha256=sha(d/(stem+'.out')),xml_sha256=sha(q),audit_sha256=sha(d/'output-audit.json'))
    geom=dict(symbols=symbols,cell_A=cell.tolist(),positions_A=pos.tolist(),forces_Ry_Bohr=forces.tolist())
    return row,geom
def main():
    names={'clean-slab':'relax','adsorbed':'relax','h2-10A':'relax','clean-k8':'scf','ads-k8':'scf','clean-vac20':'scf','ads-vac20':'scf','h2-12A':'scf'}
    allruns={k:read_run(k,v) for k,v in names.items()};rows=[r[0] for r in allruns.values()]
    for a,b in [('clean-slab','adsorbed'),('clean-k8','ads-k8'),('clean-vac20','ads-vac20')]:
        assert np.allclose(allruns[a][1]['cell_A'],allruns[b][1]['cell_A'],atol=1e-10,rtol=0)
    for child,parent in [('clean-k8','clean-slab'),('ads-k8','adsorbed'),('clean-vac20','clean-slab'),('ads-vac20','adsorbed'),('h2-12A','h2-10A')]:
        cg=allruns[child][1];pg=allruns[parent][1]
        assert cg['symbols']==pg['symbols']
        c=np.array(cg['positions_A']);p=np.array(pg['positions_A'])
        assert np.allclose(c-c.mean(axis=0),p-p.mean(axis=0),atol=1e-9,rtol=0),'Changed internal geometry in '+child
    baseline=None;comparisons=[]
    for label,clean,ads,gas in [('baseline-k6','clean-slab','adsorbed','h2-10A'),('k8','clean-k8','ads-k8','h2-10A'),('vacuum20','clean-vac20','ads-vac20','h2-10A'),('H2-box12','clean-slab','adsorbed','h2-12A')]:
        rc,ra,rh=[allruns[x][0] for x in [clean,ads,gas]]
        assert (rc['nAl'],rc['nH'],ra['nAl'],ra['nH'],rh['nAl'],rh['nH'])==(3,0,3,2,0,2)
        energy=(ra['total_energy_Ry']-rc['total_energy_Ry']-rh['total_energy_Ry'])*RY_EV/2
        if baseline is None:baseline=energy
        comparisons.append(dict(protocol=label,clean_case=clean,adsorbed_case=ads,gas_case=gas,adsorption_eV_H=energy,change_from_baseline_meV_H=(energy-baseline)*1000))
    save_csv('energy-table.csv',rows);save_csv('adsorption-energy.csv',comparisons)
    geoms={k:v[1] for k,v in allruns.items()}
    (ROOT/'structures.json').write_text(json.dumps(geoms,indent=2)+'\n')
    receipt={'qe_version':'7.5','scientific_acceptance':'not_assessed','definition':'[E(slab+2H)-E(clean slab)-E(gas H2)]/2; QE ! total energy for all terms','model':'Symmetric nonmagnetic PBE three-layer 1x1 Al111; one atop H per surface per cell; fixed middle layer and in-plane lattice','comparison_line_meV_H':10,'unassessed':['Slab thickness','Dilute coverage','Global adsorption site','Spin-state alternatives','Zero-point and finite-temperature contributions','Basis cutoff convergence'],'baseline':comparisons[0],'runs':rows,'comparisons':comparisons}
    (ROOT/'evidence/analysis-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('case           energy (Ry/cell)    max |F_i| (Ry/Bohr)')
    for row in rows[:3]:print(f"{row['case']:<14} {row['total_energy_Ry']:18.10f} {row['max_force_component_Ry_Bohr']:20.8f}")
    print('protocol       Eads (eV/H)    change (meV/H)')
    for row in comparisons:print(f"{row['protocol']:<15} {row['adsorption_eV_H']:12.8f} {row['change_from_baseline_meV_H']:16.6f}")
    h2=np.array(geoms['h2-10A']['positions_A']);ads=np.array(geoms['adsorbed']['positions_A'])
    print(f'H2 bond length: {np.linalg.norm(h2[1]-h2[0]):.8f} Angstrom')
    print(f'Top atop H height: {ads[4,2]-ads[2,2]:.8f} Angstrom')
    print('Comparison completed for the named finite model; untested model dimensions remain explicit.')
if __name__=='__main__':main()
