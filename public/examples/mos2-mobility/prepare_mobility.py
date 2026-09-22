from pathlib import Path
import json,numpy as np
from ase.build import mx2
R=Path('<工作目录>/mos2-mobility')
a=mx2('MoS2',kind='2H',a=3.18,thickness=3.19,vacuum=10)
meta={'structure_source':'https://wiki.fysik.dtu.dk/ase/_modules/ase/build/surface.html#mx2','builder':"ase.build.mx2('MoS2',kind='2H',a=3.18,thickness=3.19,vacuum=10)",'ASE_version':'3.29.0','initial_cell_A':a.cell.array.tolist(),'initial_scaled_positions':a.get_scaled_positions().tolist(),'pseudo_urls':['https://pseudopotentials.quantum-espresso.org/upf_files/Mo.pbe-spn-rrkjus_psl.1.0.0.UPF','https://pseudopotentials.quantum-espresso.org/upf_files/S.pbe-n-rrkjus_psl.1.0.0.UPF'],'model':'Scalar-relativistic PBE; K-valley electron, longitudinal acoustic deformation-potential approximation,300K; no material prediction.','strain_boundary':'UniaxialCartesianxx strain; transversey fixed;cellz fixed;internalcoordinatesrelaxed at eachstrain.','start_utc':'2026-09-22T15:43:14Z','checkpoint_utc':'2026-09-22T16:03:14Z','target_utc':'2026-09-22T16:13:14Z'}
(R/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
base=f"""&CONTROL
 calculation = 'vc-relax'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 60
 etot_conv_thr = 1.0d-7
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 4
 A = 3.18
 C = 23.19
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
/
&ELECTRONS
 conv_thr = 1.0d-11
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-9
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
&IONS
 ion_dynamics = 'bfgs'
/
&CELL
 cell_dynamics = 'bfgs'
 cell_dofree = 'ibrav+2Dxy'
 press_conv_thr = 0.1
/
ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
Mo 0.000000000000 0.000000000000 0.500000000000
S 0.666666666667 0.333333333333 0.568779646399
S 0.666666666667 0.333333333333 0.431220353601
K_POINTS automatic
12 12 1 0 0 0
"""
(R/'base/mos2.vc-relax.prepared').write_text(base)
(R/'base/run.prepared').write_text('''#!/bin/bash
#SBATCH --job-name=atlas-mos2-vc
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in mos2.vc-relax.in > mos2.vc-relax.out 2> mos2.vc-relax.err
''')
print('Prepared3-atompublicMoS2 baseline60/480Ry12x12x1,8MPI')
