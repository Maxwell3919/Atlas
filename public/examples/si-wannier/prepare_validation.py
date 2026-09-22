from pathlib import Path
import numpy as np,json
r=Path(__file__).resolve().parent;d=r/'k4'
raw=[x.split() for x in (d/'silicon_band.labelinfo.dat').read_text().splitlines()]
labels=[(x[0],int(x[1])-1,float(x[2]),np.array(list(map(float,x[3:6])))) for x in raw]
n=labels[-1][1]+1
k=np.zeros((n,3));distance=np.zeros(n)
for left,right in zip(labels[:-1],labels[1:]):
 for i in range(left[1],right[1]+1):
  frac=(i-left[1])/(right[1]-left[1]);k[i]=left[3]*(1-frac)+right[3]*frac;distance[i]=left[2]*(1-frac)+right[2]*frac
assert np.max(np.abs(k-np.loadtxt(d/'silicon_band.kpt',skiprows=1)[:,:3]))<6e-7
indices=np.array([0,13,31,57,80,95,120,139,160,177,196,219,246])
base=(d/'si.scf.in').read_text().split('K_POINTS automatic')[0].replace("calculation = 'scf'","calculation = 'bands'").replace(' nat = 2',' nosym = .true.\n noinv = .true.\n nat = 2')
(d/'validation/si.bands.in').write_text(base+'K_POINTS crystal\n'+str(len(indices))+'\n'+''.join(' '.join(f'{v:.14f}' for v in k[i])+' 1.0\n' for i in indices))
np.savetxt(r/'validation-kpoints.csv',np.column_stack([indices,k[indices],distance[indices]]),delimiter=',',header='band_path_index_zero_based,k1,k2,k3,distance_Ainv',comments='')
(d/'validation/run.slurm').write_text('''#!/bin/bash
#SBATCH --job-name=atlas-si-check
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in si.bands.in > si.bands.out 2> si.bands.err
cp tmp/si.save/data-file-schema.xml bands.data-file-schema.xml
''')
print('Prepared 13 direct-DFT validation points, including points outside both training meshes.')
