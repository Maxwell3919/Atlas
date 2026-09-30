"""Check native QE unfolding energy/weight tables against saved XML and CSV.
No binary wavefunctions required. Original wavefunction checks are separate.
"""
from pathlib import Path
import csv,json,re,xml.etree.ElementTree as ET
import numpy as np
root=Path(__file__).resolve().parent
def native(path):
 lines=path.read_text().splitlines()
 nb,nk=map(int,re.findall(r'\d+',lines[0]))
 a=np.array([float(x) for line in lines[1:] for x in line.split()])
 if a.size!=nk*(3+nb):raise ValueError(f'{path}: incomplete native blocks')
 a=a.reshape(nk,3+nb)
 return a[:,:3],a[:,3:]
path=np.genfromtxt(root/'kpath.csv',delimiter=',',names=True)
meta=json.loads((root/'metadata.json').read_text())
expected=np.column_stack([path[x] for x in ['k1_pc','k2_pc','k3_pc']])@np.linalg.inv(np.array(meta['lattice_pc_A'])).T*(10.2*.529177210903)
rows=[];receipt=[]
for tag,nb in [('primitive',8),('supercell',24)]:
 d=root/tag
 ke,e=native(d/'bands01.dat');kw,w=native(d/'spectral_weights01.dat')
 assert e.shape==w.shape==(40,nb) and np.max(abs(ke-kw))<1e-12
 assert np.isfinite(e).all() and np.isfinite(w).all() and w.min()>=-1e-8 and w.max()<=1+1e-5
 states=ET.parse(d/'bands.data-file-schema.xml').getroot().findall('output/band_structure/ks_energies')
 xe=np.array([np.fromstring(x.findtext('eigenvalues'),sep=' ') for x in states])*27.211386245988
 xk=np.array([np.fromstring(x.findtext('k_point'),sep=' ') for x in states])
 assert xe.shape==e.shape and np.max(abs(xk-expected))<1e-8
 err=float(np.max(abs(xe-e)));assert err<2e-5
 saved=np.genfromtxt(d/'bands.csv',delimiter=',',names=True)
 assert len(saved)==40*nb
 assert np.max(abs(saved['energy_eV'].reshape(40,nb)-xe))<1e-10
 assert np.max(abs(saved['native_weight'].reshape(40,nb)-w))<1e-12
 receipt.append(dict(cell=tag,nk=40,nbnd=nb,max_native_xml_energy_difference_eV=err,max_xml_kpath_difference_tpiba=float(np.max(abs(xk-expected))),native_weight_range=[float(w.min()),float(w.max())]))
 for i in range(40):
  for j in range(nb):
   rows.append(dict(cell=tag,ik=i+1,band=j+1,distance_inv_A=float(path['distance_inv_A'][i]),energy_xml_eV=float(xe[i,j]),energy_native_eV=float(e[i,j]),native_weight=float(w[i,j])))
with (root/'native-result-check.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(root/'native-result-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
for x in receipt:print(x)
print('NATIVE_UNFOLDING_TABLE_CHECKS_PASSED')
