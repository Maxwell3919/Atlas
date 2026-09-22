from pathlib import Path
import shutil,json,hashlib
r=Path(__file__).resolve().parent
source=Path('<Wannier90源码目录>/examples/example11')
for name in ['silicon.scf','silicon.nscf','silicon.pw2wan','silicon.win']:
 shutil.copy2(source/name,r/'evidence'/('official-'+name))
common=f'''&CONTROL
 calculation = '{{calculation}}'
 prefix = 'si'
 pseudo_dir = '{r}/pseudo'
 outdir = './tmp'
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 2
 celldm(1) = 10.2
 nat = 2
 ntyp = 1
 ecutwfc = 40
 ecutrho = 320
 nbnd = 4
 occupations = 'fixed'
{{sym}}/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Si 28.0855 Si.pbe-n-van.UPF
ATOMIC_POSITIONS crystal
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
'''
for n in [4,6]:
 d=r/f'k{n}';(d/'tmp').mkdir(parents=True,exist_ok=True);(d/'validation/tmp').mkdir(parents=True,exist_ok=True)
 kpts=[(i/n,j/n,k/n) for i in range(n) for j in range(n) for k in range(n)]
 (d/'si.scf.in').write_text(common.format(calculation='scf',sym='')+'K_POINTS automatic\n10 10 10 0 0 0\n')
 (d/'si.nscf.in').write_text(common.format(calculation='nscf',sym=' nosym = .true.\n noinv = .true.\n')+f'K_POINTS crystal\n{n**3}\n'+''.join(' '.join(f'{v:.12f}' for v in p)+f' {1/n**3:.12f}\n' for p in kpts))
 win=f'''num_bands = 4
num_wann = 4
num_iter = 200
conv_tol = 1.0d-10
conv_window = 5
iprint = 2
length_unit = bohr
write_hr = true
write_xyz = true
bands_plot = true
bands_num_points = 80
begin projections
f=-0.125,-0.125,0.375:s
f=0.375,-0.125,-0.125:s
f=-0.125,0.375,-0.125:s
f=-0.125,-0.125,-0.125:s
end projections
begin unit_cell_cart
bohr
-5.10 0.00 5.10
0.00 5.10 5.10
-5.10 5.10 0.00
end unit_cell_cart
begin atoms_frac
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
end atoms_frac
begin kpoint_path
G 0.00 0.00 0.00 X 0.50 0.00 0.50
X 0.50 0.00 0.50 W 0.50 0.25 0.75
W 0.50 0.25 0.75 L 0.50 0.50 0.50
L 0.50 0.50 0.50 G 0.00 0.00 0.00
end kpoint_path
mp_grid = {n} {n} {n}
begin kpoints
'''+''.join(' '.join(f'{v:.12f}' for v in p)+'\n' for p in kpts)+'end kpoints\n'
 (d/'silicon.win').write_text(win)
 (d/'silicon.pw2wan').write_text("&INPUTPP\n outdir='./tmp'\n prefix='si'\n seedname='silicon'\n write_amn=.true.\n write_mmn=.true.\n write_unk=.false.\n/\n")
 script=f'''#!/bin/bash
#SBATCH --job-name=atlas-si-w{n}
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in si.scf.in > si.scf.out 2> si.scf.err
cp tmp/si.save/data-file-schema.xml scf.data-file-schema.xml
cp -r tmp/si.save validation/tmp/
mpirun -np 8 <qe_bin>/pw.x -in si.nscf.in > si.nscf.out 2> si.nscf.err
cp tmp/si.save/data-file-schema.xml nscf.data-file-schema.xml
<qe_bin>/wannier90.x -pp silicon > wannier-pp.out 2> wannier-pp.err
mpirun -np 8 <qe_bin>/pw2wannier90.x -in silicon.pw2wan > pw2wan.out 2> pw2wan.err
<qe_bin>/wannier90.x silicon > wannier.out 2> wannier.err
'''
 # Keep a plain numeric job label.
 script=script.replace(f'{{n}}',str(n))
 (d/'run.slurm').write_text(script)
(r/'structure-source.json').write_text(json.dumps({'source':'Wannier90 3.1.0 official example11 shipped with QE7.5','structure':'diamond Si, 2 atoms, ibrav=2, celldm(1)=10.2 bohr','not_relaxed_here':True,'modifications':['40/320 Ry cutoffs','explicit fixed occupations and 4 valence bands','full k grid with nosym/noinv','four bond-centred s projections; isolated valence subspace; no disentanglement','4^3 and 6^3 uniform meshes'],'protocol_convergence':'not established'},indent=2)+'\n')
print('Prepared independent k4 and k6 SCF -> NSCF -> interface -> Wannier chains')
