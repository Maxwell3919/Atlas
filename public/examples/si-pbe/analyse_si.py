from pathlib import Path
import csv, json, re, hashlib, xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parent
RY_EV=13.605693122994
HA_EV=2*RY_EV
BOHR_ANG=0.529177210903
HBAR2_OVER_2ME=3.80998211615486 # eV Angstrom^2

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def table(path,header,rows):
    with path.open('w') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
def read_xml(directory):
    x=ET.parse(ROOT/directory/'data-file-schema.xml').getroot()
    output=x.find('output')
    states=output.find('band_structure').findall('ks_energies')
    k=np.array([[float(v) for v in s.find('k_point').text.split()] for s in states])
    e=np.array([[float(v)*HA_EV for v in s.find('eigenvalues').text.split()] for s in states])
    alat=float(output.find('atomic_structure').attrib['alat'])*BOHR_ANG
    return k,e,alat

# Raw total energies plus separate basis and Brillouin-zone sampling series.
conv=[]
for group,names in [('ecutwfc',[f'cutoff{i}' for i in [40,50,60,70,80]]),('ecutrho',['rho320','rho480','scf']),('kmesh',[f'k{i}' for i in [4,6,8,10,12,14]])]:
    vals=[]
    for name in names:
        d=ROOT/name
        out=(d/'scf.out').read_text()
        assert out.count('JOB DONE.')==1 and 'convergence has been achieved' in out
        val=float(re.findall(r'!\s+total energy\s+=\s+([-\d.]+)',out)[-1])
        setting=int(re.search(r'(\d+)$',name).group(1)) if name!='scf' else 640
        vals.append((name,setting,val))
    reference=vals[-1][2]
    for name,setting,e in vals:
        conv.append([group,name,setting,e,(e-reference)*RY_EV*1000/2])
table(ROOT/'convergence.csv',['parameter','directory','setting','energy_Ry_per_cell','delta_meV_per_atom_vs_last'],conv)

# Relaxation history: each total-energy/force pair belongs to one electronic cycle.
rt=(ROOT/'relax/relax.out').read_text()
energies=[float(v) for v in re.findall(r'!\s+total energy\s+=\s+([-\d.]+)',rt)]
forces=[float(v) for v in re.findall(r'Total force\s+=\s+([-\d.]+)',rt)]
assert len(energies)==len(forces)
table(ROOT/'relax/relaxation.csv',['scf_cycle','energy_Ry','total_force_Ry_per_Bohr'],[[i+1,e,f] for i,(e,f) in enumerate(zip(energies,forces))])

# Gap on uniform meshes; a local line refinement is a separate piece of evidence.
gaps=[]
for name in ['gap12','gap18-cg','gap24-cg','gap24-k12-cg']:
    if not (ROOT/name/'data-file-schema.xml').exists():continue
    k,e,a=read_xml(name)
    v=e[:,3]; c=e[:,4];iv=int(v.argmax());ic=int(c.argmin())
    row={'directory':name,'nks':len(k),'vbm_eV':float(v[iv]),'cbm_eV':float(c[ic]),'gap_eV':float(c[ic]-v[iv]),'minimum_direct_gap_eV':float((c-v).min()),'vbm_k_tpiba':k[iv].tolist(),'cbm_k_tpiba':k[ic].tolist()}
    gaps.append(row)
    table(ROOT/name/'edges.csv',['kx_tpiba','ky_tpiba','kz_tpiba','vbm_band4_eV','cbm_band5_eV'],np.c_[k,v,c])
(ROOT/'gap-results.json').write_text(json.dumps(gaps,indent=2)+'\n')

# Fits use physical k in inverse Angstrom, not a path-point index.
k,e,a=read_xml('mass'); kcart=k*2*np.pi/a
imin=int(e[:,4].argmin());center=kcart[imin,0]
fits=[]
for window in [.010,.020,.030]:
    take=np.abs(kcart[:,0]-center)<=window+1e-12
    coeff=np.polyfit(kcart[take,0]-center,e[take,4],2)
    fit=np.polyval(coeff,kcart[take,0]-center)
    x0=center-coeff[1]/(2*coeff[0]);e0=coeff[2]-coeff[1]**2/(4*coeff[0])
    fits.append({'half_window_inv_A':window,'npoints':int(take.sum()),'quadratic_A_eVA2':float(coeff[0]),'minimum_k_inv_A':float(x0),'minimum_k_tpiba':float(x0*a/(2*np.pi)),'minimum_energy_eV':float(e0),'mass_over_me':float(HBAR2_OVER_2ME/coeff[0]),'rms_residual_meV':float(np.sqrt(np.mean((fit-e[take,4])**2))*1000)})
(ROOT/'mass/mass-fits.json').write_text(json.dumps(fits,indent=2)+'\n')
table(ROOT/'mass/longitudinal.csv',['kx_tpiba','kx_inv_A','band5_eV'],np.c_[k[:,0],kcart[:,0],e[:,4]])

# Actual 3D local cube: retain every point, not only a plotted 2D slice.
if (ROOT/'band3d/data-file-schema.xml').exists():
    k,e,a=read_xml('band3d')
    assert len(k)==891
    table(ROOT/'band3d/cube.csv',['kx_tpiba','ky_tpiba','kz_tpiba','kx_inv_A','ky_inv_A','kz_inv_A','band5_eV'],np.c_[k,k*2*np.pi/a,e[:,4]])

# Fatband weights are squared complex projection amplitudes. Take energies
# from PW QEXSD (Hartree); the independent atomic_proj E values use Ry.
k,e,a=read_xml('bands-cg')
pr=ET.parse(ROOT/'bands-cg/atomic_proj.xml').getroot().find('EIGENSTATES')
projs=pr.findall('PROJS'); pk=pr.findall('K-POINT');pe=pr.findall('E')
assert len(projs)==len(k)
rows=[];distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(k,axis=0),axis=1))]
for ik,proj in enumerate(projs):
    kp=np.array([float(v) for v in pk[ik].text.split()])
    ep=np.array([float(v)*RY_EV for v in pe[ik].text.split()])
    assert np.max(np.abs(kp-k[ik]))<1e-9 and np.max(np.abs(ep-e[ik]))<1e-6
    weights=[]
    for orbital in proj.findall('ATOMIC_WFC'):
        z=np.array([float(v) for v in orbital.text.split()]).reshape(-1,2)
        weights.append((z*z).sum(axis=1))
    weights=np.array(weights)
    assert weights.shape==(8,8)
    for ib in range(8):
        sw=weights[[0,4],ib].sum();pw=weights[[1,2,3,5,6,7],ib].sum()
        rows.append([ik+1,ib+1,distance[ik],*k[ik],e[ik,ib],sw,pw,sw+pw])
table(ROOT/'bands-cg/fatband.csv',['ik','iband','path_distance_tpiba','kx_tpiba','ky_tpiba','kz_tpiba','energy_eV','Si_s_weight','Si_p_weight','projection_norm'],rows)

pop=(ROOT/'population-cg/projwfc.out').read_text()
charges=[]
for m in re.finditer(r'Atom #\s+(\d+): total charge =\s+([\d.]+), p =\s+([\d.]+), pz=\s+([\d.]+), px=\s+([\d.]+), py=\s+([\d.]+)',pop):
    atom,q,p,pz,px,py=m.groups();s=float(q)-float(p)
    charges.append([int(atom),float(q),s,float(p),float(pz),float(px),float(py)])
table(ROOT/'population-cg/lowdin.csv',['atom','total_electrons','s_electrons','p_electrons','pz_electrons','px_electrons','py_electrons'],charges)
print('convergence rows:',len(conv))
for row in gaps:print(row)
for row in fits:print(row)
print('fatband rows:',len(rows),'projection normalization maximum:',max(r[-1] for r in rows))
print('Lowdin atoms:',charges)
