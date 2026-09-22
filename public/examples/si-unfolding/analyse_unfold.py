"""Audit scalar norm-conserving QE7.5 unfolding without changing weights.
Binary layout follows QE Modules/io_base.f90: write_wfc.
For diagonal2x1x1 cell, even/odd Miller h are complementary projectors.
Unsupported spinors, Gamma-only, non-unit scale and US/PAW are rejected.
"""
from pathlib import Path
import csv,json,re,struct,hashlib,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent
HARTREE_EV=27.211386245988
meta=json.loads((R/'metadata.json').read_text())
upf=ET.parse(R/'pseudo/Si.pz-vbc.UPF').getroot().find('PP_HEADER')
assert upf.attrib['pseudo_type']=='NC'
assert upf.attrib['is_ultrasoft'].lower() in ['f','false','.false.']
assert upf.attrib['is_paw'].lower() in ['f','false','.false.']

def record(f):
 raw=f.read(4)
 if len(raw)!=4:raise ValueError('Truncated Fortran record')
 n=struct.unpack('<i',raw)[0]
 if not 0<n<1000000000:raise ValueError('Unsupported record marker/endian')
 a=f.read(n);tail=f.read(4)
 assert len(a)==n and len(tail)==4 and struct.unpack('<i',tail)[0]==n
 return a

def wfc(path):
 with path.open('rb') as f:
  hdr=record(f)
  assert len(hdr)==44,len(hdr)
  ik=struct.unpack('<i',hdr[:4])[0];k=np.frombuffer(hdr[4:28],'<f8').copy()
  spin,gamma=struct.unpack('<ii',hdr[28:36]);scale=struct.unpack('<d',hdr[36:44])[0]
  ngw,igwx,npol,nbnd=np.frombuffer(record(f),'<i4')
  assert npol==1 and gamma==0 and spin==1 and abs(scale-1)<1e-12
  reciprocal=np.frombuffer(record(f),'<f8').reshape(3,3).copy()
  mill=np.frombuffer(record(f),'<i4').reshape(igwx,3).copy()
  c=np.array([np.frombuffer(record(f),'<c16').copy() for j in range(nbnd)])
  assert c.shape==(nbnd,igwx) and not f.read(1)
 return ik,k,mill,c,reciprocal

def native(path):
 lines=path.read_text().splitlines(); nband,nk=map(int,re.findall(r'\d+',lines[0]))
 a=np.array([float(x) for line in lines[1:] for x in line.split()]).reshape(nk,3+nband)
 return a[:,:3],a[:,3:]

def xml(path):
 root=ET.parse(path).getroot();bs=root.find('output/band_structure')
 ks=bs.findall('ks_energies')
 return np.array([np.fromstring(x.find('k_point').text,sep=' ') for x in ks]), np.array([np.fromstring(x.find('eigenvalues').text,sep=' ') for x in ks])*HARTREE_EV,root

kpath=np.genfromtxt(R/'kpath.csv',delimiter=',',names=True)
a=np.array(meta['lattice_pc_A'])
expected=np.column_stack([kpath[x] for x in ['k1_pc','k2_pc','k3_pc']])@np.linalg.inv(a).T*(10.2*.529177210903)
summary={'scope':meta['claimed_scope'],'pseudo_sha256':hashlib.sha256((R/'pseudo/Si.pz-vbc.UPF').read_bytes()).hexdigest(),'pseudo_type':'NC','method':'Native bands_unfold.x and independent even/odd plane-wave projectors','native_weights_modified':False,'k_header_note':'Native file prints Cartesian xk(i)/dimi. This is not a primitive fractional k coordinate for an anisotropic non-orthogonal supercell. Plots use validated input kpath.csv distances.'}
rows=[]; energies={}; norms={}; weights={}
for tag in ['primitive','supercell']:
 d=R/tag
 for outfile in ['si.scf.out','si.bands.out','unfold.out']:
  text=(d/outfile).read_text();assert 'JOB DONE.' in text,outfile
  assert 'not converged' not in text and 'Error in routine' not in text,outfile
 assert 'convergence has been achieved' in (d/'si.scf.out').read_text()
 k,e,root=xml(d/'bands.data-file-schema.xml');energies[tag]=e
 assert e.shape==(40,24 if tag=='supercell' else 8)
 assert np.max(abs(k-expected))<1e-8
 kn,en=native(d/'bands01.dat');kw,wn=native(d/'spectral_weights01.dat')
 assert en.shape==wn.shape==e.shape
 assert np.max(abs(e-en))<2e-5,np.max(abs(e-en))
 wn0=[];ww1=[];nn=[]
 for ik in range(1,len(k)+1):
  idx,wk,m,c,b=wfc(d/f'tmp/si.save/wfc{ik}.dat')
  assert idx==ik and np.max(abs(wk-k[ik-1]*(2*np.pi/10.2)))<1e-9
  norm=np.sum(abs(c)**2,axis=1)
  even=np.sum(abs(c[:,m[:,0]%2==0])**2,axis=1) if tag=='supercell' else norm
  odd=np.sum(abs(c[:,m[:,0]%2!=0])**2,axis=1) if tag=='supercell' else np.zeros_like(norm)
  nn.append(norm);wn0.append(even);ww1.append(odd)
  for j in range(len(norm)):
   rows.append([tag,ik,j+1,e[ik-1,j],wn[ik-1,j],even[j],odd[j],norm[j],wn[ik-1,j]-even[j]])
 norms[tag]=np.array(nn);weights[tag]=np.array(wn0)
 err=np.max(abs(norms[tag]-1));assert err<1e-7,err
 summary[tag]={'nk':len(k),'nbnd':e.shape[1],'max_norm_error':float(err),'max_coset_sum_error':float(np.max(abs(np.array(wn0)+np.array(ww1)-1))),'native_vs_pw_max_abs':float(np.max(abs(wn-weights[tag]))),'native_range':[float(wn.min()),float(wn.max())],'max_xml_native_energy_difference_eV':float(np.max(abs(e-en))),'max_xml_input_kdifference_tpiba':float(np.max(abs(k-expected)))}
 with (d/'bands.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['ik','band','distance_inv_A','energy_eV','native_weight','pw_weight'])
  for i in range(len(k)):
   for j in range(e.shape[1]):w.writerow([i+1,j+1,kpath['distance_inv_A'][i],e[i,j],wn[i,j],weights[tag][i,j]])

with (R/'wavefunction-audit.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['cell','ik','band','energy_eV','native_weight','even_weight','odd_weight','norm','native_minus_even']);w.writerows(rows)
# Match each primitive state to the energy-nearby supercell eigenspace.
# Sum weights over that eigenspace to handle arbitrary degenerate rotations.
# The primitive bands are checked as groups, not by a fragile same-index mapping.
comparisons=[]
for i,(pe,se,sw) in enumerate(zip(energies['primitive'],energies['supercell'],weights['supercell'])):
 used=set()
 for j,p in enumerate(pe):
  if j in used:continue
  pgroup=np.where(abs(pe-p)<1e-4)[0];used.update(pgroup.tolist())
  # tolerance0.002eV only for association, measured error retained separately
  sg=np.where(abs(se-p)<.002)[0]
  if not len(sg):raise ValueError(f'No matched SC eigenspace k{i+1} primitive band{j+1}: {p}')
  weight=float(sw[sg].sum());centroid=float(np.dot(sw[sg],se[sg])/weight)
  err=centroid-float(pe[pgroup].mean())
  comparisons.append([i+1,';'.join(str(x+1) for x in pgroup),';'.join(str(x+1) for x in sg),len(pgroup),weight,float(pe[pgroup].mean()),centroid,err,weight-len(pgroup)])
with (R/'primitive-comparison.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['ik','primitive_bands','supercell_bands','expected_weight','measured_weight','primitive_mean_eV','supercell_weighted_mean_eV','delta_eV','weight_error']);w.writerows(comparisons)
summary['comparison']={'primitive_eigenvalues_compared':int(energies['primitive'].size),'degenerate_groups':len(comparisons),'energy_association_window_eV':.002,'primitive_group_tolerance_eV':1e-4,'max_abs_centroid_difference_eV':max(abs(x[7]) for x in comparisons),'RMS_centroid_difference_eV':float(np.sqrt(np.mean([x[7]**2 for x in comparisons]))),'max_group_weight_error':max(abs(x[8]) for x in comparisons),'energy_zero_eV':float(energies['primitive'][0,3])}
(R/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Si perfect2x1x1 supercell:40 path points,320 primitive eigenvalues checked')
print('cell       nbnd   max|norm-1|   max|even+odd-1|   max|native-even|')
for tag in ['primitive','supercell']:
 s=summary[tag];print(f"{tag:10s} {s['nbnd']:4d}   {s['max_norm_error']:.3e}       {s['max_coset_sum_error']:.3e}       {s['native_vs_pw_max_abs']:.3e}")
s=summary['comparison'];print('Degenerate-eigenspace centroid max/RMS difference(eV):',f"{s['max_abs_centroid_difference_eV']:.9f}",f"{s['RMS_centroid_difference_eV']:.9f}")
print('Degenerate-eigenspace weight maximum error:',f"{s['max_group_weight_error']:.3e}")
print('Reference energy: primitiveGammaVBM(eV)=',f"{s['energy_zero_eV']:.9f}")
print('Native Cartesian headers are not used as primitive fractional coordinates; input kpath was checked against XML and binary wfc headers.')
