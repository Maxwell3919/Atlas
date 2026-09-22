from pathlib import Path
import re,csv,json,sys
import numpy as np
r=Path(__file__).resolve().parent
BOHR=0.529177210903;RYEV=13.605693122994;RYTIME_FS=0.04837768653
scenarios=[('nvt-dt20-cg',20.,100),('nve-dt20-nosym',20.,50),('nve-dt10-nosym',10.,100)]
if '--nve-only' in sys.argv: scenarios=scenarios[1:]
all_summary={};all_rows={};all_xyz={}
for name,dt,nstep in scenarios:
    d=r/name;txt=(d/'al.md.out').read_text();inp=(d/'al.md.in').read_text()
    assert 'JOB DONE.' in txt and 'The maximum number of steps has been reached.' in txt
    assert (d/'al.md.err').stat().st_size==0
    assert not re.search(r'convergence NOT achieved|Error in routine',txt)
    starts=list(re.finditer(r'Entering Dynamics:\s+iteration\s*=\s*(\d+)',txt));assert len(starts)==nstep
    cellblock=inp.split('CELL_PARAMETERS angstrom')[1].split('K_POINTS')[0]
    cell=np.array([list(map(float,l.split())) for l in cellblock.strip().splitlines()])
    init=np.array([list(map(float,l.split()[1:4])) for l in inp.split('ATOMIC_POSITIONS crystal')[1].split('CELL_PARAMETERS')[0].strip().splitlines()])
    assert init.shape==(8,3) and cell.shape==(3,3)
    nconv=len(re.findall(r'convergence has been achieved in\s+(\d+) iterations',txt));assert nconv==nstep
    rows=[];positions=[init@cell]
    for i,m in enumerate(starts):
        step=int(m.group(1));assert step==i+1
        pre=txt[(starts[i-1].end() if i else 0):m.start()]
        end=starts[i+1].start() if i+1<len(starts) else len(txt)
        b=txt[m.start():end]
        potential=float(re.findall(r'!\s+total energy\s*=\s*([-\d.]+)\s+Ry',pre)[-1])
        kinetic=float(re.search(r'kinetic energy \(Ekin\)\s*=\s*([-\d.]+)',b).group(1))
        total=float(re.search(r'Ekin \+ Etot \(const\)\s*=\s*([-\d.]+)',b).group(1))
        temperature=float(re.search(r'temperature\s*=\s*([-\d.]+)\s*K',b).group(1))
        assert abs(total-(potential+kinetic))<2e-8
        assert 'eigenvalues not converged' not in re.split(r'iteration\s+#\s*\d+',pre)[-1]
        early_warnings=pre.count('eigenvalues not converged')
        conv=int(re.findall(r'convergence has been achieved in\s+(\d+) iterations',pre)[-1])
        residual=float(re.findall(r'estimated scf accuracy\s*<\s*([.\dEe+\-]+)\s*Ry',pre)[-1])
        assert residual<=1.0e-10
        posblock=b.split('ATOMIC_POSITIONS (crystal)')[1].strip().splitlines()[:8]
        frac=np.array([list(map(float,l.split()[1:4])) for l in posblock]);assert frac.shape==(8,3)
        positions.append(frac@cell)
        # Position-Verlet in QE 7.5 advances coordinates before output_tau.
        # Etot and the centred finite-difference velocity belong to the preceding position.
        rows.append(dict(step=step,energy_sample_time_fs=(step-1)*dt*RYTIME_FS,position_time_fs=step*dt*RYTIME_FS,temperature_K=temperature,potential_Ry=potential,kinetic_Ry=kinetic,total_Ry=total,scf_iterations=conv,early_diagonalization_warning_count=early_warnings,scf_estimated_accuracy_Ry=residual))
    t=np.array([v['energy_sample_time_fs'] for v in rows]);en=np.array([v['total_Ry'] for v in rows]);temps=np.array([v['temperature_K'] for v in rows]);de=(en-en[0])*RYEV*1000/8
    for v,x in zip(rows,de):v['total_change_meV_atom']=float(x)
    with (d/'thermo.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    xyz=np.array(positions);np.savez_compressed(d/'trajectory.npz',positions_A=xyz,cell_A=cell,time_fs=np.arange(nstep+1)*dt*RYTIME_FS)
    lattice=' '.join(f'{v:.12f}' for v in cell.ravel())
    with (d/'trajectory.xyz').open('w') as f:
        for j,pos in enumerate(xyz):
            f.write('8\nLattice="'+lattice+'" Properties=species:S:1:pos:R:3 pbc="T T T" time_fs='+str(j*dt*RYTIME_FS)+'\n')
            f.writelines('Al '+' '.join(f'{x:.10f}' for x in p)+'\n' for p in pos)
    wall=re.findall(r'PWSCF\s*:\s*(.*?)\s+CPU\s+(.*?)\s+WALL',txt)[-1][1]
    summary=dict(nsteps=nstep,natoms=8,dt_Ry_au=dt,dt_fs=dt*RYTIME_FS,coordinate_end_time_fs=nstep*dt*RYTIME_FS,energy_end_time_fs=float(t[-1]),all_scf_converged=True,final_scf_iteration_diagonalization_warnings=0,early_scf_diagonalization_warnings=sum(v['early_diagonalization_warning_count'] for v in rows),scf_cycles=nconv,scf_iterations_min=min(x['scf_iterations'] for x in rows),scf_iterations_max=max(x['scf_iterations'] for x in rows),temperature_first_K=float(temps[0]),temperature_mean_K=float(np.mean(temps)),temperature_min_K=float(np.min(temps)),temperature_max_K=float(np.max(temps)),temperature_last_K=float(temps[-1]),energy_change_final_meV_atom=float(de[-1]),energy_peak_to_peak_meV_atom=float(np.ptp(de)),energy_linear_slope_meV_atom_ps=float(np.polyfit(t,de,1)[0]*1000),rms_displacement_final_A=float(np.sqrt(np.mean(np.sum((xyz[-1]-xyz[0])**2,axis=1)))),max_atom_displacement_A=float(np.max(np.linalg.norm(xyz[-1]-xyz[0],axis=1))),wall_time=wall,interpretation='short fixed-volume small-cell trajectory; not thermal-stability or equilibrium-property evidence')
    (d/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');all_summary[name]=summary;all_rows[name]=rows;all_xyz[name]=xyz
coarse=np.array([v['total_change_meV_atom'] for v in all_rows['nve-dt20-nosym']]);fine=np.array([v['total_change_meV_atom'] for v in all_rows['nve-dt10-nosym'][::2]])
assert coarse.shape==fine.shape
matched=dict(matched_energy_times=50,energy_time_end_fs=all_rows['nve-dt20-nosym'][-1]['energy_sample_time_fs'],max_energy_change_difference_meV_atom=float(np.max(np.abs(coarse-fine))),final_position_same_time_fs=all_summary['nve-dt20-nosym']['coordinate_end_time_fs'],rms_position_difference_at_same_end_A=float(np.sqrt(np.mean(np.sum((all_xyz['nve-dt20-nosym'][-1]-all_xyz['nve-dt10-nosym'][-1])**2,axis=1)))))
all_summary['nve_matched_time_comparison']=matched
all_summary['time_axis_note']='QE7.5 position Verlet prints advanced coordinates at n*dt; Etot and centred velocity in that block refer to preceding geometry at (n-1)*dt. CSV keeps both clocks.'
(r/'summary.json').write_text(json.dumps(all_summary,indent=2)+'\n')
print('case                steps  dt_fs    coord_end_fs  energy_range_meV_atom  mean_T_K')
for name,s in all_summary.items():
    if not isinstance(s,dict) or 'nsteps' not in s:continue
    print(f"{name:20s} {s['nsteps']:3d}  {s['dt_fs']:.6f}  {s['coordinate_end_time_fs']:9.6f}  {s['energy_peak_to_peak_meV_atom']:13.6f}       {s['temperature_mean_K']:.3f}")
print(f"All {sum(n for _,_,n in scenarios)} SCF cycles converged; no final-iteration diagonalization warning; {len(scenarios)} native JOB DONE endings.")
print('Early SCF diagonalization warnings:', {n: all_summary[n]['early_scf_diagonalization_warnings'] for n,_,_ in scenarios})
print('NVE position difference at the common final time:',matched['rms_position_difference_at_same_end_A'],'angstrom RMS')
print('NVE total-energy conservation tested only over ~48 fs; no thermodynamic convergence claim.')
