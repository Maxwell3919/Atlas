#!/bin/bash
#SBATCH --job-name=atlas-vacuum28-zero-bands
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
mkdir -p tmp/mos2.save
cp ../tmp/mos2.save/charge-density.dat tmp/mos2.save/
cp ../scf.data-file-schema.xml tmp/mos2.save/data-file-schema.xml
cp ../../pseudo/*.UPF tmp/mos2.save/
mpirun -np 8 <qe_bin>/pw.x -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml

