#!/bin/bash
#SBATCH --job-name=atlas-si-super
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
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
mpirun -np 8 <qe_bin>/pw.x -in si.bands.in > si.bands.out 2> si.bands.err
cp tmp/si.save/data-file-schema.xml bands.data-file-schema.xml
mpirun -np 8 <qe_bin>/bands_unfold.x -in unfold.in > unfold.out 2> unfold.err
