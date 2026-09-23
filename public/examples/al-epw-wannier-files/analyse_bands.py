#!/usr/bin/env python3
"""Compare native Wannier90 bands with direct QE at the same 166 k points.
Pair ascending eigenvalue ranks independently at each k. This compares spectra,
not orbital character through crossings. All cases share the parent potential
and reference EF; no fit, rigid energy shift, smoothing, or point deletion.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import csv,json,math
BASE=Path(__file__).resolve().parent
HARTREE_EV=27.211386245988
EF=8.4122
r=ET.parse(BASE/'runs/bandcheck-001/tmp/al.save/data-file-schema.xml')
ks=r.findall('.//output/band_structure/ks_energies')
dft=[[float(x)*HARTREE_EV for x in k.find('eigenvalues').text.split()] for k in ks]
kpath=BASE/'runs/wannier-002/al_band.kpt'
pathrows=[[float(x)for x in line.split()]for line in kpath.read_text().splitlines()[1:]]
assert len(pathrows)==len(dft)
n=len(dft)
def stats(records):
    vals=[x['error_eV']for x in records]
    return {'count':len(vals),'rms_eV':math.sqrt(sum(x*x for x in vals)/len(vals)),'max_abs_eV':max(abs(x)for x in vals)}
allsummary={}
for label,folder in [('k4_frozen10','wannier-002'),('k8_frozen10','wannier-003'),('k8_frozen13p5','wannier-004'),('k12_frozen13p5','wannier-005')]:
    w=BASE/'runs'/folder
    if not(w/'al_band.dat').exists():continue
    assert(w/'al_band.kpt').read_text()==kpath.read_text()
    wan=[[float(x)for x in line.split()]for line in(w/'al_band.dat').read_text().splitlines()if line.strip()]
    assert len(wan)==4*n
    rows=[]
    for k in range(n):
        energies=sorted(wan[i*n+k][1]for i in range(4))
        for i in range(4):
            rows.append({'k_index':k+1,'kx_crystal':pathrows[k][0],'ky_crystal':pathrows[k][1],'kz_crystal':pathrows[k][2],'distance_inv_angstrom':wan[k][0],'band_rank':i+1,'QE_eV':dft[k][i],'Wannier_eV':energies[i],'QE_minus_EF_eV':dft[k][i]-EF,'Wannier_minus_EF_eV':energies[i]-EF,'error_eV':energies[i]-dft[k][i]})
    with(BASE/f'derived/band-{label}.csv').open('w')as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
    wt=(w/'al.wout').read_text()
    summary={'case':label,'kpath_points':n,'shared_parent_EF_eV':EF,'all_four_bands':stats(rows),'QE_energy_below10eV':stats([x for x in rows if x['QE_eV']<=10]),'QE_energy_within1eV_of_EF':stats([x for x in rows if abs(x['QE_minus_EF_eV'])<=1]),'QE_energy_within0p2eV_of_EF':stats([x for x in rows if abs(x['QE_minus_EF_eV'])<=.2]),'disentanglement_local_criterion':'Disentanglement convergence criteria satisfied' in wt,'wannierisation_local_criterion':'Wannierisation convergence criteria satisfied' in wt,'pairing':'ascending eigenvalue rank at each identical k; spectral comparison, not orbital-character tracking','scope':'same 166-point line path; not a whole-Brillouin-zone error bound','scientific_acceptance':'not_assessed'}
    allsummary[label]=summary
(BASE/'derived/band-comparison-summary.json').write_text(json.dumps(allsummary,indent=2)+'\n')
print(json.dumps(allsummary,indent=2))
