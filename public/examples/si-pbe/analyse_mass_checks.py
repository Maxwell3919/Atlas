from pathlib import Path
import json,csv,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent
BOHR_ANG=0.529177210903
HA_EV=27.211386245988
C=3.80998211615486

def read(d):
    x=ET.parse(R/d/'data-file-schema.xml').getroot().find('output');a=float(x.find('atomic_structure').attrib['alat'])*BOHR_ANG
    states=x.find('band_structure').findall('ks_energies')
    k=np.array([[float(v) for v in s.find('k_point').text.split()] for s in states])*2*np.pi/a
    e=np.array([[float(v)*HA_EV for v in s.find('eigenvalues').text.split()] for s in states])
    return k,e

rows=[]
for d,direction,part,col in [('mass','longitudinal',slice(None),0),('mass-k14','longitudinal-k14',slice(None),0),('mass-transverse','transverse-y',slice(0,33),1),('mass-transverse','transverse-z',slice(33,66),2)]:
    k,e=read(d);q=k[part,col];ec=e[part,4];q0=q[ec.argmin()]
    for window in [.01,.02,.03]:
        mask=np.abs(q-q0)<=window+1e-12
        a,b,c=np.polyfit(q[mask]-q0,ec[mask],2)
        residual=np.polyval([a,b,c],q[mask]-q0)-ec[mask]
        rows.append({'directory':d,'direction':direction,'window_inv_A':window,'points':int(mask.sum()),'mass_over_me':float(C/a),'curvature_eVA2':float(2*a),'minimum_k_inv_A':float(q0-b/(2*a)),'rms_residual_meV':float(np.sqrt(np.mean(residual**2))*1000)})
(R/'mass/mass-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
with (R/'mass/mass-checks.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for row in rows:
    print(f"{row['direction']:18s} window={row['window_inv_A']:.2f}  n={row['points']:2d}  m/me={row['mass_over_me']:.8f}  RMS={row['rms_residual_meV']:.6f} meV")
