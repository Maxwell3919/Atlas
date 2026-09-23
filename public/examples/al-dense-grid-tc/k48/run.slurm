#!/bin/bash
#SBATCH --job-name=atlas-al-k48
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
mpirun -np 8 ${QE_BIN}/pw.x -in al.dense.in > al.dense.out 2> al.dense.err
grep -q 'JOB DONE.' al.dense.out
grep -q 'convergence has been achieved' al.dense.out
cp tmp/al.a2Fsave al.a2Fsave.k48
cp tmp/al.save/data-file-schema.xml dense.data-file-schema.xml
mpirun -np 8 ${QE_BIN}/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
grep -q 'JOB DONE.' al.scf.out
grep -q 'convergence has been achieved' al.scf.out
cp tmp/al.save/data-file-schema.xml response.data-file-schema.xml
cmp tmp/al.a2Fsave al.a2Fsave.k48
sha256sum tmp/al.a2Fsave al.a2Fsave.k48 > a2Fsave-after-response.sha256
mpirun -np 8 ${QE_BIN}/ph.x -in al.elph.in > al.elph.out 2> al.elph.err
grep -q 'JOB DONE.' al.elph.out
${QE_BIN}/q2r.x -in q2r.in > q2r.out 2> q2r.err
grep -q 'JOB DONE.' q2r.out
${QE_BIN}/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
grep -q 'JOB DONE.' matdyn-dos.out
${QE_BIN}/lambda.x < lambda.in > lambda.out 2> lambda.err
date -u > finished.txt

