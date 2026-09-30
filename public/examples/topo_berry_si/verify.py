"""Independent polar-matrix loop check, plus a nonzero synthetic link test."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
root=Path(__file__).resolve().parent
hashes=json.loads((root/'results/source-sha256.json').read_text())
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
receipts=[]
for n in [4,6]:
    raw=(root/f'source/k{n}/silicon.mmn').read_text().splitlines()
    nb,nk,nn=map(int,raw[1].split())
    matrices={}
    for at in range(2,len(raw),nb*nb+1):
        header=tuple(map(int,raw[at].split()))
        z=np.array([complex(*map(float,line.split())) for line in raw[at+1:at+1+nb*nb]]).reshape(nb,nb,order='F')
        u,sv,vh=np.linalg.svd(z)
        matrices[header]=u@vh
    rows=list(csv.DictReader((root/f'results/k{n}-links.csv').open()))
    links={(int(x['k_index'])-1,int(x['axis'])-1):(int(x['neighbor_index'])-1,matrices[(int(x['k_index']),int(x['neighbor_index']),int(x['G1']),int(x['G2']),int(x['G3']))]) for x in rows}
    phases={}
    for k in range(nk):
        k1,m1=links[k,0];k2,m2=links[k,1]
        k12,m12=links[k1,1];k21,m21=links[k2,0]
        assert k12==k21
        phases[k]=float(np.angle(np.linalg.det(m1@m12@m21.conj().T@m2.conj().T)))
    saved=list(csv.DictReader((root/f'results/k{n}-plaquettes.csv').open()))
    error=max(abs(np.angle(np.exp(1j*(phases[int(x['k_index'])-1]-float(x['phase_rad']))))) for x in saved)
    assert error<1e-12
    receipts.append(dict(grid=n,independent_polar_loop_max_phase_error_rad=error,raw_mmn_sha256=hashlib.sha256((root/f'source/k{n}/silicon.mmn').read_bytes()).hexdigest()))
    print(f'k{n}: independent SVD polar-matrix loop phase difference = {error:.3e} rad')
# Periodic link field with a known +1 total flux; not a material calculation.
n=7
u1=np.array([[np.exp(-2j*np.pi*j/(n*n)) for j in range(n)] for i in range(n)])
u2=np.ones((n,n),complex)
for i in range(n):u2[i,-1]=np.exp(2j*np.pi*i/n)
phase=np.empty((n,n))
for i in range(n):
    for j in range(n):phase[i,j]=np.angle(u1[i,j]*u2[(i+1)%n,j]*np.conj(u1[i,(j+1)%n])*np.conj(u2[i,j]))
synthetic=float(phase.sum()/(2*np.pi))
assert abs(synthetic-1)<1e-12
print(f'Synthetic periodic link field: C = {synthetic:.12f} (expected +1; algebra check only)')
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
receipt=dict(source_files_unchanged=len(hashes),polar_loop_checks=receipts,synthetic_link_chern=synthetic,synthetic_scope='Algorithm orientation and periodic-boundary check, not a Si/QE result')
(root/'results/independent-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('INDEPENDENT_CHECKS_PASSED')
