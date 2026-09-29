#!/bin/bash

#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

#unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 32 ph.x<phx1.in>phx1.out
#rm -r _*.log
