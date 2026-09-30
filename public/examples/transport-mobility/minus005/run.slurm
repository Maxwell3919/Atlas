#!/bin/bash
#SBATCH --job-name=atlas-mob-minus005
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
mpirun -np 8 <qe_bin>/pw.x -in mos2.relax.in > mos2.relax.out 2> mos2.relax.err
python3 ../finish_mobility_relax.py > preparation.out
mpirun -np 8 <qe_bin>/pw.x -in mos2.scf.in > mos2.scf.out 2> mos2.scf.err
cp tmp/mos2.save/data-file-schema.xml scf.data-file-schema.xml
mpirun -np 8 <qe_bin>/pp.x -in potential.in > potential.out 2> potential.err
<qe_bin>/average.x < average.in > average.out 2> average.err
mpirun -np 8 <qe_bin>/pw.x -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml
