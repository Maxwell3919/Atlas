#!/bin/bash
#SBATCH --job-name=atlas-al-ph4
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
mpirun -np 8 <qe_bin>/ph.x -in al.ph.in > al.ph.out 2> al.ph.err
<qe_bin>/dynmat.x -in dynmat-no.in > dynmat-no.out 2> dynmat-no.err
<qe_bin>/dynmat.x -in dynmat-simple.in > dynmat-simple.out 2> dynmat-simple.err
<qe_bin>/dynmat.x -in dynmat-crystal.in > dynmat-crystal.out 2> dynmat-crystal.err
<qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err
<qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
<qe_bin>/matdyn.x -in matdyn-band.in > matdyn-band.out 2> matdyn-band.err

