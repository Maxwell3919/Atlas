from pathlib import Path
import numpy as np,xml.etree.ElementTree as E,json,hashlib,re
HARTREE_EV=27.211386245988
root=Path(__file__).resolve().parent
summary=[]
for n in [24,32]:
 d=root/f'k{n}-cg';out=(d/'al.nscf.out').read_text();err=(d/'al.nscf.err').read_text()
 assert out.count('JOB DONE.')==1 and not err and 'Error in routine' not in out
 assert 'not converged' not in out.lower()
 xml=d/'tmp/al.save/data-file-schema.xml';doc=E.parse(xml).getroot();o=doc.find('output');band=o.find('band_structure');nk=int(band.findtext('nks'));nb=int(band.findtext('nbnd'))
 assert nk==n**3
 b=np.array([np.fromstring(o.findtext('basis_set/reciprocal_lattice/'+tag),sep=' ') for tag in ['b1','b2','b3']])
 cell=np.array([np.fromstring(o.findtext('atomic_structure/cell/'+tag),sep=' ') for tag in ['a1','a2','a3']])*0.529177210903
 ef=float(band.findtext('fermi_energy'))*HARTREE_EV
 energies=np.empty((n,n,n,nb));seen=np.zeros((n,n,n),dtype=int)
 for point in band.findall('ks_energies'):
  cart=np.fromstring(point.findtext('k_point'),sep=' ');frac=cart@np.linalg.inv(b)
  scaled=frac*n;assert np.max(np.abs(scaled-np.rint(scaled)))<1e-7
  i=tuple(np.rint(scaled).astype(int)%n);seen[i]+=1
  energies[i]=np.fromstring(point.findtext('eigenvalues'),sep=' ')*HARTREE_EV-ef
 assert np.all(seen==1)
 np.savez_compressed(d/'fermi-grid.npz',energy_eV=energies,fermi_eV=ef,cell_angstrom=cell,grid=n)
 ranges=[{'band':j+1,'min_eV':float(energies[:,:,:,j].min()),'max_eV':float(energies[:,:,:,j].max())} for j in range(nb)]
 crossing=[r['band'] for r in ranges if r['min_eV']<0<r['max_eV']]
 record={'kmesh':n,'nks':nk,'fermi_eV':ef,'crossing_bands':crossing,'band_ranges':ranges,'source_xml_sha256':hashlib.sha256(xml.read_bytes()).hexdigest(),'nscf_out_sha256':hashlib.sha256((d/'al.nscf.out').read_bytes()).hexdigest(),'definition':'Energy grid includes all k, no interpolation, E-EF in eV.'}
 (d/'grid-info.json').write_text(json.dumps(record,indent=2));summary.append(record)
 print(f'k={n}^3 nks={nk} EF={ef:.8f} eV crossing bands={crossing}; all grid cells assigned once')
 for sigma in [.10,.20]:
  weight=np.exp(-0.5*(energies/sigma)**2).sum(axis=3)/(sigma*np.sqrt(2*np.pi))
  spectrum=np.fft.fftn(weight);J=np.fft.ifftn(spectrum.conj()*spectrum).real/nk
  assert np.min(J)>-1e-10
  assert abs(J[0,0,0]-np.mean(weight*weight))<1e-8
  # one nontrivial point cross-check against direct Brillouin-zone sum
  idx=(n//4,0,n//4);direct=np.mean(weight*np.roll(weight,tuple(-x for x in idx),axis=(0,1,2)))
  assert abs(J[idx]-direct)<1e-8
  np.savez_compressed(d/f'nesting-s{sigma:.2f}.npz',nesting_eV_minus2=J,sigma_eV=sigma,grid=n)
  cut=np.array([[i/n,J[i,0,i],J[i,0,i]/J[0,0,0]] for i in range(n//2+1)])
  np.savetxt(d/f'nesting-GX-s{sigma:.2f}.csv',cut,delimiter=',',header='q_fraction_along_b1_plus_b3,J_eV_minus2,J_over_J0',comments='')
  print(f' sigma={sigma:.2f} eV J(0)={J[0,0,0]:.8f} J(X)={J[n//2,0,n//2]:.8f} eV^-2; direct-sum check passed')
(root/'summary.json').write_text(json.dumps(summary,indent=2))
