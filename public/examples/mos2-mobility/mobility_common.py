from pathlib import Path
import numpy as np,xml.etree.ElementTree as ET
BOHR=.529177210903
ROOT=Path(__file__).resolve().parent

def geometry(xml):
 r=ET.parse(xml).getroot();st=r.find('output/atomic_structure')
 cell=np.array([np.fromstring(x.text,sep=' ') for x in st.find('cell')])*BOHR
 atoms=list(st.find('atomic_positions'));species=[x.attrib['name'] for x in atoms]
 pos=np.array([np.fromstring(x.text,sep=' ') for x in atoms])*BOHR
 return cell,pos,species

def input_pw(cell,pos,species,calc='scf',mesh=12,kpoints=None):
 ions="&IONS\n ion_dynamics = 'bfgs'\n/\n" if calc=='relax' else ''
 flags=" nosym = .true.\n noinv = .true.\n" if calc=='bands' else ''
 frac=pos@np.linalg.inv(cell)
 cards='CELL_PARAMETERS angstrom\n'+''.join(' '.join(f'{x:.14f}' for x in v)+'\n' for v in cell)+'ATOMIC_POSITIONS crystal\n'+''.join(s+' '+' '.join(f'{x:.14f}' for x in v)+'\n' for s,v in zip(species,frac))
 if kpoints is None:cards+=f'K_POINTS automatic\n{mesh} {mesh} 1 0 0 0\n'
 else:cards+='K_POINTS crystal\n'+str(len(kpoints))+'\n'+''.join(' '.join(f'{x:.14f}' for x in k)+' 1.0\n' for k in kpoints)
 return f"""&CONTROL
 calculation = '{calc}'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 40
 etot_conv_thr = 1.0d-8
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 0
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
{flags}/
&ELECTRONS
 conv_thr = 1.0d-12
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
{ions}ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
{cards}"""

def kset(cell):
 b=2*np.pi*np.linalg.inv(cell).T;rows=[];ks=[]
 K=np.array([1/3,1/3,0.]);Kcart=K@b
 for dx in [-.03,-.02,-.01,0,.01,.02,.03]:
  for dy in [-.03,-.02,-.01,0,.01,.02,.03]:
   k=(Kcart+[dx,dy,0])@np.linalg.inv(b);ks.append(k);rows.append(['K-local',dx,dy,*k])
 for label,k in [('Gamma',np.zeros(3)),('M',np.array([.5,0,0])),('K-prime',-K)]:
  ks.append(k);rows.append([label,0,0,*k])
 for direction,Kend in enumerate([K,np.array([-2/3,1/3,0.]),np.array([1/3,-2/3,0.])]):
  for t in np.linspace(.25,.95,15):
   k=t*Kend;ks.append(k);rows.append([f'Gamma-K{direction+1}',t,0,*k])
 return np.array(ks),rows

def slurm(name,body):return f'''#!/bin/bash
#SBATCH --job-name={name}
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
{body}'''

QE='<qe_bin>/'
BODY=f'''mpirun -np 8 {QE}pw.x -in mos2.scf.in > mos2.scf.out 2> mos2.scf.err
cp tmp/mos2.save/data-file-schema.xml scf.data-file-schema.xml
mpirun -np 8 {QE}pp.x -in potential.in > potential.out 2> potential.err
{QE}average.x < average.in > average.out 2> average.err
mpirun -np 8 {QE}pw.x -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml
'''
def post_inputs(d):
 (d/'potential.in').write_text("&INPUTPP\n prefix = 'mos2'\n outdir = './tmp'\n filplot = 'electrostatic-potential.dat'\n plot_num = 11\n/\n")
 (d/'average.in').write_text('1\nelectrostatic-potential.dat\n1.0\n0\n3\n1.0\n')
