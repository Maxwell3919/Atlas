from pathlib import Path
import csv
import hashlib
import json
import time
import numpy as np
from ase.io import read
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms

start=time.perf_counter()
uc=read('reference-unitcell.extxyz')
ref=read('reference-supercell.extxyz')
order=np.load('phonopy-to-ase-order.npy')
data=np.load('mapped-dataset.npz')
u=data['displacements']; f=data['forces']
assert u.shape==f.shape==(101,64,3)
assert np.isfinite(u).all() and np.isfinite(f).all()
assert np.max(np.abs(u.mean(axis=1)))<1e-12
assert Path('independent.json').exists(), 'Wait for independent MD to finish.'
frames=read('independent-nve.traj',':')
ui=[];fi=[];temps=[]
for frame in frames:
    d=frame.get_scaled_positions(wrap=False)-ref.get_scaled_positions(wrap=False)
    d-=np.rint(d)
    cart=d@ref.cell.array
    cart-=cart.mean(axis=0)
    ui.append(cart[order]);fi.append(frame.calc.results['forces'][order]);temps.append(frame.get_temperature())
ui=np.array(ui);fi=np.array(fi)
assert ui.shape==fi.shape==(51,64,3)
assert np.isfinite(ui).all() and np.isfinite(fi).all()
np.savez_compressed('independent-dataset.npz',displacements=ui,forces=fi,temperature_K=temps,time_ps=np.arange(len(frames))*.01)

vertices=np.array([[0,0,0],[.5,0,.5],[.5,.25,.75],[.375,.375,.75],[0,0,0],[.5,.5,.5]])
labels=['Gamma','X','W','K','Gamma','L']
paths=[np.linspace(a,b,51) for a,b in zip(vertices[:-1],vertices[1:])]

def new_phonon():
    cell=PhonopyAtoms(symbols=uc.get_chemical_symbols(),cell=uc.cell.array,scaled_positions=uc.get_scaled_positions())
    return Phonopy(cell,supercell_matrix=[2,2,2],primitive_matrix='F',symprec=1e-5)

def dispersion(ph,label):
    ph.run_band_structure(paths)
    bs=ph.band_structure
    with open(label+'-bands.csv','w',newline='') as h:
        w=csv.writer(h);w.writerow(['segment','distance_inv_A','q1','q2','q3']+[f'frequency_{i+1}_THz' for i in range(6)])
        for seg,(q,d,freq) in enumerate(zip(bs.qpoints,bs.distances,bs.frequencies)):
            for qi,di,fi in zip(q,d,freq):w.writerow([seg,di,*qi,*fi])
    ph.run_qpoints([[0,0,0]])
    gamma=ph.qpoints.frequencies[0].tolist()
    allfreq=np.concatenate(bs.frequencies)
    assert np.isfinite(allfreq).all()
    return dict(min_path_THz=float(allfreq.min()),max_path_THz=float(allfreq.max()),gamma_THz=gamma,
                boundaries_inv_A=[float(bs.distances[0][0])]+[float(d[-1]) for d in bs.distances]),allfreq

def errors(fc,positions,forces):
    prediction=-np.einsum('ijab,sjb->sia',fc,positions,optimize=True)
    residual=prediction-forces
    rmse=float(np.sqrt(np.mean(residual**2)))
    force_rms=float(np.sqrt(np.mean(forces**2)))
    return dict(snapshots=len(positions),rmse_meV_A=1000*rmse,force_rms_meV_A=1000*force_rms,
                relative_rmse=rmse/force_rms,max_abs_error_meV_A=1000*float(np.abs(residual).max()),
                r2=1-float(np.sum(residual**2)/np.sum((forces-forces.mean())**2))),prediction

baseline={}; allfreq={}
for label in ['harmonic-0.01','harmonic-0.005']:
    ph=new_phonon();ph.force_constants=np.load(label+'-fc.npy')
    stats,freq=dispersion(ph,label);allfreq[label]=freq
    ev,_=errors(ph.force_constants,ui,fi)
    stats['independent_force_error']=ev
    baseline[label]=stats
    print('BASELINE',label,json.dumps(stats),flush=True)
baseline_difference=float(np.max(np.abs(allfreq['harmonic-0.01']-allfreq['harmonic-0.005'])))
print('AMPLITUDE_COMPARISON max_abs_frequency_difference_THz',baseline_difference,flush=True)

results=[]
for ntrain in [20,40,60]:
    train=np.arange(1,ntrain+1)
    held=np.arange(80,101)
    ph=new_phonon()
    ph.dataset={'displacements':np.array(u[train],order='C'),'forces':np.array(f[train],order='C')}
    print('FIT_START ntrain',ntrain,'training_time_ps',[float(data['source_time_ps'][train[0]]),float(data['source_time_ps'][train[-1]])],flush=True)
    t0=time.perf_counter()
    ph.produce_force_constants(fc_calculator='symfc',calculate_full_force_constants=True,fc_calculator_log_level=1)
    fc=ph.force_constants
    assert fc.shape==(64,64,3,3) and np.isfinite(fc).all()
    label=f'effective-{ntrain}'
    np.save(label+'-fc.npy',fc)
    ph.save(label+'.yaml',settings={'force_constants':True})
    fit_seconds=time.perf_counter()-t0
    train_error,_=errors(fc,u[train],f[train])
    block_error,_=errors(fc,u[held],f[held])
    independent_error,pred=errors(fc,ui,fi)
    bands,freq=dispersion(ph,label)
    out=dict(training_snapshots=ntrain,training_source_indices=train.tolist(),heldout_source_indices=held.tolist(),
             source_training_temperature_K=float(data['source_temperature_K'][train].mean()),
             source_heldout_temperature_K=float(data['source_temperature_K'][held].mean()),
             independent_temperature_K=float(np.mean(temps)),fit_wall_s=fit_seconds,
             train=train_error,heldout_block=block_error,independent=independent_error,bands=bands,
             translational_drift_eV_A2=float(np.abs(fc.sum(axis=1)).max()),
             permutation_difference_eV_A2=float(np.max(np.abs(fc-fc.transpose(1,0,3,2)))))
    results.append(out);allfreq[label]=freq
    np.save(label+'-independent-prediction.npy',pred)
    print('FIT_RESULT',json.dumps(out,indent=2),flush=True)

summary=dict(reference=json.loads(Path('reference.json').read_text()),
             baseline=baseline,baseline_amplitude_max_frequency_difference_THz=baseline_difference,
             fits=results,band_labels=labels,band_vertices_fractional=vertices.tolist(),
             independent=json.loads(Path('independent.json').read_text()),
             effective_40_vs_60_max_path_difference_THz=float(np.max(np.abs(allfreq['effective-40']-allfreq['effective-60']))),
             total_fit_script_wall_s=time.perf_counter()-start,
             interpretation='Finite-temperature effective second-order force-constant fitting demonstration; not a temperature-converged phonon renormalization or SSCHA calculation.')
Path('fit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with open('learning-curve.csv','w',newline='') as h:
    w=csv.writer(h);w.writerow(['training_snapshots','train_RMSE_meV_A','heldout_block_RMSE_meV_A','independent_RMSE_meV_A'])
    for r in results:w.writerow([r['training_snapshots'],r['train']['rmse_meV_A'],r['heldout_block']['rmse_meV_A'],r['independent']['rmse_meV_A']])
print('EFFECTIVE_40_VS_60_MAX_PATH_DIFFERENCE_THz',summary['effective_40_vs_60_max_path_difference_THz'],flush=True)
print('FIT_PIPELINE_FINISHED wall_s',time.perf_counter()-start,flush=True)

