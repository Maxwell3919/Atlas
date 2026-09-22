from pathlib import Path
import ast
import hashlib
import json
import numpy as np
from ase.io import read
import phonopy

summary=json.loads(Path('fit-summary.json').read_text())
environment=json.loads(Path('environment.json').read_text())
source_hash=hashlib.sha256(Path('../si-md/nve-1fs.traj').read_bytes()).hexdigest()
assert source_hash==environment['source_trajectory_sha256']
assert hashlib.sha256(Path('../models/mace-mp-0-small.model').read_bytes()).hexdigest()==environment['model_sha256']
order=np.load('phonopy-to-ase-order.npy')
assert sorted(order.tolist())==list(range(64))
mapped=np.load('mapped-dataset.npz')
frames=read('mapped-configurations.traj',':')
assert len(frames)==101
saved_forces=np.array([a.calc.results['forces'][order] for a in frames])
force_difference=float(np.max(np.abs(saved_forces-mapped['forces'])))
assert force_difference<1e-12

new=read('independent-initial.traj');old=read('../si-md/initial.traj')
assert not np.array_equal(new.get_momenta(),old.get_momenta())
ind=np.load('independent-dataset.npz')
assert len(read('independent-nve.traj',':'))==51
fc=np.load('effective-60-fc.npy')
matrix=fc.transpose(0,2,1,3).reshape(192,192)
prediction=-(ind['displacements'].reshape(-1,192)@matrix.T).reshape(-1,64,3)
saved=np.load('effective-60-independent-prediction.npy')
prediction_difference=float(np.max(np.abs(prediction-saved)))
assert prediction_difference<1e-12
rmse=float(np.sqrt(np.mean((prediction-ind['forces'])**2))*1000)
assert abs(rmse-summary['fits'][-1]['independent']['rmse_meV_A'])<1e-10
for fit in summary['fits']:
    assert set(fit['training_source_indices']).isdisjoint(fit['heldout_source_indices'])
for name in ['harmonic-0.01','harmonic-0.005','effective-20','effective-40','effective-60']:
    table=np.genfromtxt(name+'-bands.csv',delimiter=',',skip_header=1)
    assert table.shape==(255,11) and np.isfinite(table).all()
ph=phonopy.load('effective-60.yaml', is_compact_fc=False, symmetrize_fc=False)
yaml_fc_difference=float(np.max(np.abs(ph.force_constants-fc)))
assert yaml_fc_difference<1e-10
ph.run_qpoints([[0,0,0]])
gamma_difference=float(np.max(np.abs(ph.qpoints.frequencies[0]-np.array(summary['fits'][-1]['bands']['gamma_THz']))))
assert gamma_difference<1e-5
for name in ['prepare.py','fit.py','plot.py','verify.py']:
    ast.parse(Path(name).read_text())
result=dict(source_trajectory_unchanged=True,independent_initial_velocities=True,mapped_frames=101,independent_frames=51,
            saved_force_max_difference_eV_A=force_difference,independent_prediction_max_difference_eV_A=prediction_difference,
            independently_recomputed_RMSE_meV_A=rmse,yaml_force_constant_max_difference_eV_A2=yaml_fc_difference,
            gamma_reload_max_difference_THz=gamma_difference,all_dispersion_rows_finite=True)
Path('verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
print('DATA_AND_EXPORT_CHECKS_FINISHED')


