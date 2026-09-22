from pathlib import Path
import numpy as np,json
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
r=Path(__file__).resolve().parent;d=r/'aimd';d.mkdir()
cell=np.array(json.loads((r/'structure.json').read_text())['cell_angstrom'])
p=Phonopy(PhonopyAtoms(symbols=['Al'],cell=cell,scaled_positions=[[0,0,0]],masses=[26.9815385]),np.eye(3,dtype=int)*2,primitive_matrix='P')
sc=p.supercell;N=len(sc);rng=np.random.default_rng(20260922)
v=rng.normal(size=(N,3));v-=v.mean(axis=0)
kb=1.380649e-23;mass=26.9815385*1.66053906660e-27;dof=3*N-3
v*=np.sqrt(dof*kb*300/(mass*np.sum(v*v)))
va=v/(0.529177210903e-10/4.837768653e-17)
base=(r/'finite-disp/n2-d0.01/disp-001/al.scf.in').read_text()
base=base[:base.index('ATOMIC_POSITIONS crystal')]+'ATOMIC_POSITIONS crystal\n'+''.join('Al '+' '.join(f'{x:.14f}' for x in row)+'\n' for row in sc.scaled_positions)+'CELL_PARAMETERS angstrom\n'+''.join(' '.join(f'{x:.14f}' for x in row)+'\n' for row in sc.cell)+'K_POINTS automatic\n4 4 4 0 0 0\nATOMIC_VELOCITIES\n'+''.join('Al '+' '.join(f'{x:.14e}' for x in row)+'\n' for row in va)
for name,dt,nstep,thermostat in [('nvt-dt20',20,100,'svr'),('nve-dt20',20,50,'not_controlled'),('nve-dt10',10,100,'not_controlled')]:
 sub=d/name;sub.mkdir();(sub/'tmp').mkdir()
 inp=base.replace(" calculation = 'scf'",f" calculation = 'md'\n nstep = {nstep}\n dt = {dt}\n iprint = 1").replace(" verbosity = 'high'"," verbosity = 'low'").replace(' conv_thr = 1.0d-12',' conv_thr = 1.0d-10')
 ions=f"&IONS\n ion_dynamics = 'verlet'\n ion_velocities = 'from_input'\n ion_temperature = '{thermostat}'\n tempw = 300\n nraise = 20\n/\n"
 inp=inp.replace('ATOMIC_SPECIES',ions+'ATOMIC_SPECIES');(sub/'al.md.in').write_text(inp)
 head=(r/'dfpt/run.slurm').read_text().split('set -e\n')[0].replace('atlas-al-ph4',f'atlas-al-{name}')
 (sub/'run.slurm').write_text(head+'set -e\nmpirun -np 8 <qe_bin>/pw.x -in al.md.in > al.md.out 2> al.md.err\n')
(d/'initial-velocities.json').write_text(json.dumps({'seed':20260922,'temperature_K_from_21_dof':mass*np.sum(v*v)/(dof*kb),'center_of_mass_velocity_m_s':v.mean(axis=0).tolist(),'velocity_unit':'bohr/Rydberg atomic time','velocities':va.tolist(),'physical_time_fs':{'nvt-dt20':96.75537306,'nve-dt20':48.37768653,'nve-dt10':48.37768653},'scope':'short integration and thermostat demonstration; 8-atom box and 4^3 mesh are not a production thermal-stability protocol'},indent=2))
print('Prepared 8-atom Al: SVR 100xdt20, matched-duration NVE 50xdt20 and 100xdt10; explicit identical initial velocities, 300K/21 DOF.')
