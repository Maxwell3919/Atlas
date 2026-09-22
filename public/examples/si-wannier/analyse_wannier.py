from pathlib import Path
import numpy as np,xml.etree.ElementTree as ET,re,json,csv,hashlib
r=Path(__file__).resolve().parent;HAEV=27.211386245988
sel=np.loadtxt(r/'validation-kpoints.csv',delimiter=',',skiprows=1);inds=sel[:,0].astype(int);nsel=len(sel)
valid=r/'k4/validation'
out=(valid/'si.bands.out').read_text();assert 'JOB DONE.' in out and 'eigenvalues not converged' not in out and (valid/'si.bands.err').stat().st_size==0
xml=ET.parse(valid/'bands.data-file-schema.xml').getroot();ks=xml.findall('./output/band_structure/ks_energies');assert len(ks)==nsel
rec=xml.find('./output/basis_set/reciprocal_lattice');B=np.array([list(map(float,rec.find(t).text.split())) for t in ['b1','b2','b3']])
kfrac=np.array([list(map(float,x.find('k_point').text.split())) for x in ks])@np.linalg.inv(B)
assert np.max(np.abs(kfrac-sel[:,1:4]))<2e-10
energy=np.array([list(map(float,x.find('eigenvalues').text.split())) for x in ks])*HAEV;assert energy.shape==(nsel,4)
reference=float(max(energy[0]));summary={'qe_version':'7.5','wannier90_version':'3.1.0','validation_unique_kpoints':len(np.unique(np.round(sel[:,1:4],12),axis=0)),'validation_points':nsel,'validation_eigenvalues':nsel*4,'energy_reference':'highest occupied direct DFT Gamma eigenvalue','energy_reference_eV':reference,'direct_DFT_source':'k4/validation/si.bands.in and bands.data-file-schema.xml','scope':'4 isolated valence bands only; no conduction bands, gap or transport claim','kmesh_results':{}}
records=[]
for mesh in [4,6]:
 d=r/f'k{mesh}'
 for prog in ['si.scf','si.nscf','pw2wan']:
  txt=(d/f'{prog}.out').read_text();assert 'JOB DONE.' in txt and not re.search('eigenvalues not converged|convergence NOT achieved|Error in routine',txt);assert (d/f'{prog}.err').stat().st_size==0
 for name in ['wannier.err','wannier-pp.err']:assert (d/name).stat().st_size==0
 wo=(d/'silicon.wout').read_text();assert 'Wannierisation convergence criteria satisfied' in wo and 'All done: wannier90 exiting' in wo
 eig=np.loadtxt(d/'silicon.eig');assert eig.shape==(mesh**3*4,3)
 nxml=ET.parse(d/'nscf.data-file-schema.xml').getroot();nks=nxml.findall('./output/band_structure/ks_energies');assert len(nks)==mesh**3
 nbasis=nxml.find('./output/basis_set/reciprocal_lattice');nB=np.array([list(map(float,nbasis.find(t).text.split())) for t in ['b1','b2','b3']])
 xmlk=np.array([list(map(float,x.find('k_point').text.split())) for x in nks])@np.linalg.inv(nB)
 wink=np.array([list(map(float,l.split())) for l in (d/'silicon.win').read_text().split('begin kpoints')[1].split('end kpoints')[0].strip().splitlines()])
 assert wink.shape==xmlk.shape and np.max(np.abs((xmlk-wink+.5)%1-.5))<2e-10
 assert list(map(int,(d/'silicon.mmn').read_text().splitlines()[1].split()))==[4,mesh**3,8]
 assert list(map(int,(d/'silicon.amn').read_text().splitlines()[1].split()))==[4,mesh**3,4]
 xmlE=np.array([list(map(float,x.find('eigenvalues').text.split())) for x in nks])*HAEV
 assert np.max(np.abs(eig[:,2].reshape(-1,4)-xmlE))<1e-7
 x=np.loadtxt(d/'silicon_band.dat');assert x.shape==(247*4,2)
 band=x[:,1].reshape(4,247).T;distance=x[:247,0]
 assert np.max(np.abs(distance[inds]-sel[:,-1]))<1e-7
 err=band[inds]-energy
 spread=float(re.search(r'Final Spread \(Bohr\^2\)\s+Omega Total\s*=\s*([.\d]+)',wo).group(1))
 convrows=re.findall(r'^\s*(\d+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+).*?<-- CONV',wo,re.M)
 conv=np.array([[int(v[0]),float(v[1]),float(v[2]),float(v[3])] for v in convrows]);assert conv.ndim==2
 np.savetxt(d/'spread-history.csv',conv,delimiter=',',header='iteration,delta_spread_bohr2,rms_gradient,total_spread_bohr2',comments='')
 np.savetxt(d/'bands.csv',np.column_stack([distance,band,band-reference]),delimiter=',',header='distance_Ainv,E1_eV,E2_eV,E3_eV,E4_eV,E1_minus_VBM_eV,E2_minus_VBM_eV,E3_minus_VBM_eV,E4_minus_VBM_eV',comments='')
 maxerr=float(np.max(np.abs(err)));rms=float(np.sqrt(np.mean(err**2)))
 summary['kmesh_results'][str(mesh)]={'num_kpoints':mesh**3,'num_bands':4,'num_wann':4,'spread_bohr2':spread,'spread_angstrom2':spread*.529177210903**2,'wannier_iterations':int(conv[-1,0]),'validation_max_abs_error_eV':maxerr,'validation_RMSE_eV':rms,'native_complete':True,'scientific_protocol_convergence':'not established'}
 for i,idx in enumerate(inds):
  for ib in range(4):
   records.append(dict(training_mesh=mesh,path_index=int(idx),k1=sel[i,1],k2=sel[i,2],k3=sel[i,3],distance_Ainv=sel[i,4],band=ib+1,E_DFT_eV=energy[i,ib],E_Wannier_eV=band[idx,ib],error_eV=err[i,ib]))
with (r/'validation-errors.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
np.savetxt(r/'direct-bands.csv',np.column_stack([sel,energy,energy-reference]),delimiter=',',header='path_index,k1,k2,k3,distance_Ainv,E1_eV,E2_eV,E3_eV,E4_eV,E1_minus_VBM_eV,E2_minus_VBM_eV,E3_minus_VBM_eV,E4_minus_VBM_eV',comments='')
summary['pseudopotential']={'filename':'Si.pbe-n-van.UPF','source':'https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-van.UPF','sha256':hashlib.sha256((r/'pseudo/Si.pbe-n-van.UPF').read_bytes()).hexdigest(),'type':'USPP','functional':'PBE','relativistic':'nonrelativistic','valence_electrons':4}
(r/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Direct DFT validation: 13 path points, 4 valence eigenvalues at each point')
print(f'Common energy reference: direct Gamma valence maximum = {reference:.9f} eV')
print('mesh   n_k   spread_bohr2   MLWF_iterations   max_error_eV   RMSE_eV')
for n,v in summary['kmesh_results'].items(): print(f"{n}^3    {v['num_kpoints']:3d}    {v['spread_bohr2']:.9f}      {v['wannier_iterations']:3d}           {v['validation_max_abs_error_eV']:.9f}   {v['validation_RMSE_eV']:.9f}")
print('Interpolation comparison is limited to these 13 points; no full-grid convergence or conduction-band claim.')
