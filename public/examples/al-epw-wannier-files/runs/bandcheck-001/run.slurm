#!/bin/bash
#SBATCH --job-name=atlas-epw-band
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=scheduler.%j.out
#SBATCH --error=scheduler.%j.err
ulimit -s unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
date -Is > start.txt
mpirun -np 4 <PRIVATE_PATH> -nk 4 -in al.bands.in > al.bands.out 2> al.bands.err
status=$?
printf '%s\n' "$status" > exit.status
date -Is > finish.txt
exit "$status"
