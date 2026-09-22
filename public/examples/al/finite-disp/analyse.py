from pathlib import Path
import json,hashlib
import numpy as np
import phonopy
from ase.io import read
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections
root=Path(__file__).resolve().parent
summary=[]
for label in ['n2-d0.01','n2-d0.02','n2-d0.01-k9','n3-d0.01']:
 d=root/label
 files=[d/'disp-001/al.scf.out',d/'disp-002/al.scf.out']
 if not all(f.exists() and 'JOB DONE.' in f.read_text() for f in files):
  print(label, 'still running');continue
 forces=[];provenance=[]
 for file in files:
  out=file.read_text();err=file.with_suffix('.err').read_text()
  assert out.count('JOB DONE.')==1 and 'convergence has been achieved' in out and not err
  assert 'convergence NOT achieved' not in out
  f=read(file,format='espresso-out').get_forces()
  forces.append(f)
  provenance.append({'file':str(file.relative_to(root)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'net_force_eV_A':f.sum(axis=0).tolist()})
 ph=phonopy.load(d/'phonopy_disp.yaml',produce_fc=False,symmetrize_fc=False,primitive_matrix='P')
 ph.forces = forces
 ph.produce_force_constants(fc_calculator='traditional')
 raw_fc=ph.force_constants.copy();drift=float(np.max(np.abs(raw_fc.sum(axis=1))))
 ph.run_qpoints([[0,0,0],[.5,0,.5],[.5,.25,.75],[.5,.5,.5]],with_eigenvectors=True)
 raw_freq=ph.qpoints.frequencies.copy()
 ph.symmetrize_force_constants()
 ph.run_qpoints([[0,0,0],[.5,0,.5],[.5,.25,.75],[.5,.5,.5]],with_eigenvectors=True)
 freq=ph.qpoints.frequencies.copy()
 # Angstrom cells, ASE forces eV/Angstrom, phonopy's default THz conversion.
 ph.save(d/'phonopy_params.yaml',settings={'force_constants':True})
 path=[[[0,0,0],[.5,0,.5],[.5,.25,.75],[.5,.5,.5],[0,0,0]]]
 q,connections=get_band_qpoints_and_path_connections(path,npoints=41)
 ph.run_band_structure(q,path_connections=connections,labels=['Γ','X','W','L','Γ'])
 b={k:getattr(ph.band_structure,k) for k in ['distances','qpoints','frequencies']};lines=[]
 for segment,(dist,qs,fs) in enumerate(zip(b['distances'],b['qpoints'],b['frequencies'])):
  lines.extend([[segment,float(x),*qpt.tolist(),*(f*33.3564095198152).tolist()] for x,qpt,f in zip(dist,qs,fs)])
 np.savetxt(d/'bands.csv',np.array(lines),delimiter=',',header='segment,distance_A_minus1,q1,q2,q3,f1_cm_minus1,f2_cm_minus1,f3_cm_minus1',comments='')
 data={'label':label,'phonopy_version':phonopy.__version__,'unit_length':'angstrom','force_unit':'eV/angstrom','frequency_unit':'THz','raw_fc_drift_eV_A2':drift,'raw_gamma_X_W_L_THz':raw_freq.tolist(),'symmetrized_gamma_X_W_L_THz':freq.tolist(),'displacements':[{k:(v.tolist() if hasattr(v,'tolist') else v) for k,v in p.items()} for p in ph.dataset['first_atoms'] if 'forces' not in p],'provenance':provenance}
 # Keep compact displacement identity without bulk force arrays in metadata.
 data['displacements']=[{'number':int(p['number']),'displacement_A':np.asarray(p['displacement']).tolist()} for p in ph.dataset['first_atoms']]
 (d/'summary.json').write_text(json.dumps(data,indent=2));summary.append(data)
 print(label, 'raw FC drift=',drift,'; Gamma THz=',freq[0],'; X THz=',freq[1])
(root/'summary.json').write_text(json.dumps(summary,indent=2))
