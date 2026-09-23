#!/bin/bash
#SBATCH --job-name=atlas-native-linear-coarse
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
mpirun -np 1 <qe_bin>/epw.x -in epw.in > epw.out 2> epw.err
