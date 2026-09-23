#!/bin/bash
#SBATCH --job-name=atlas-c-basis-koga
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
#SBATCH --output=_lobster.%j.log
#SBATCH --error=_lobstererr.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -l unlimited
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
<lobster_bin>/lobster-6.0.0 > lobster.stdout 2> lobster.stderr
