#!/bin/bash
#SBATCH --job-name=atlas-epw-nscf
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=scheduler.%j.out
#SBATCH --error=scheduler.%j.err
ulimit -s unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
date -Is > start.txt
mpirun -np 8 <PRIVATE_PATH> -nk 8 -in al.nscf.in > al.nscf.out 2> al.nscf.err
status=$?
printf '%s\n' "$status" > exit.status
date -Is > finish.txt
exit "$status"
