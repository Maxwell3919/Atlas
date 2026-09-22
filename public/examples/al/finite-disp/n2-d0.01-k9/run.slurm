#!/bin/bash
#SBATCH --job-name=atlas-al-fd2k9
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
cd "<工作目录>/finite-disp/n2-d0.01-k9/disp-001"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/finite-disp/n2-d0.01-k9/disp-002"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
