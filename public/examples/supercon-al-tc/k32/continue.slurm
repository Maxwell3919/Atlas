#!/bin/bash
#SBATCH --job-name=atlas-al-epc4
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
cp tmp/al.a2Fsave al.a2Fsave.k32
cp tmp/al.save/data-file-schema.xml dense.data-file-schema.xml
mpirun -np 8 ${QE_BIN}/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cmp tmp/al.a2Fsave al.a2Fsave.k32
mpirun -np 8 ${QE_BIN}/ph.x -in al.elph.in > al.elph.out 2> al.elph.err
${QE_BIN}/q2r.x -in q2r.in > q2r.out 2> q2r.err
${QE_BIN}/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err

