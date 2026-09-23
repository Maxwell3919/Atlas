#!/bin/bash
#SBATCH --job-name=atlas-epw-gaps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source <软件环境>/env.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
for calc_dir in nonlinear-w010-T*; do
  (cd "$calc_dir" && mpirun -np 1 <qe_bin>/epw.x -in epw.in > epw.out 2> epw.err)
 done
