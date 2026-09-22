#!/bin/bash
#SBATCH --job-name=atlas-si-w6
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
mpirun -np 8 <qe_bin>/pw.x -in si.scf.in > si.scf.out 2> si.scf.err
cp tmp/si.save/data-file-schema.xml scf.data-file-schema.xml
cp -r tmp/si.save validation/tmp/
mpirun -np 8 <qe_bin>/pw.x -in si.nscf.in > si.nscf.out 2> si.nscf.err
cp tmp/si.save/data-file-schema.xml nscf.data-file-schema.xml
<qe_bin>/wannier90.x -pp silicon > wannier-pp.out 2> wannier-pp.err
mpirun -np 8 <qe_bin>/pw2wannier90.x -in silicon.pw2wan > pw2wan.out 2> pw2wan.err
<qe_bin>/wannier90.x silicon > wannier.out 2> wannier.err
