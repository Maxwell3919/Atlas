- [Quantum ESPRESSO 7.5：pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [LOBSTER 官方页面、下载与配套手册](https://www.cohp.de/)
- [QE 官方 C PAW 赝势](https://pseudopotentials.quantum-espresso.org/upf_files/C.pbe-n-kjpaw_psl.0.1.UPF)

金刚石中，每个 C 原子有四个最近邻。本次从两原子原胞出发，计算这四条 C–C 键的 pCOHP，并检查把 k 网格和波函数截断提高后，每条键的积分值变了多少。先看实际生成了哪些键，再看它们在哪些能量范围呈现成键、反键贡献。

通用操作见 [SCF](/Atlas/m/scf/qe/)。这里每组重新进行静态 SCF → LOBSTER，没有使用其它 Si 或 Al 教案的密度，也没有独立 NSCF 步骤。LOBSTER 6.0.0 要读取 `.scf.in`、对应 PAW UPF 和 `.save` 中的波函数；只有 `scf.out` 不能完成投影。

[本次输入、输出和绘图脚本](/Atlas/examples/diamond-cohp-files.tar.gz)解压为 `diamond-cohp`。包内包括四组正式比较和两份同波函数的基组诊断，没有程序、手册、UPF 和大体积波函数。已有结果可直接重画；重算时需要自己的 LOBSTER、下面的赝势，以及重新运行产生的 `.save`。

结构采用 LOBSTER 6.0.0 配套 QE diamond 示例的两原子金刚石原胞，常规立方晶格常数固定为 `6.746 bohr`，约 `3.56981 Å`。本轮没有重新优化，不把它称为这套赝势的零压平衡结构。相较配套示例，本次明确改用非自旋 `nspin=1`、8 条带、固定占据，并重新做网格和截断对照。

## 从固定原胞准备波函数

先准备目录和赝势。
```console
[preston@preston-System-Product-Name cohp]$ mkdir -p pseudo diamond-k6
[preston@preston-System-Product-Name cohp]$ curl -fL --connect-timeout 15 --max-time 45 https://pseudopotentials.quantum-espresso.org/upf_files/C.pbe-n-kjpaw_psl.0.1.UPF -o pseudo/C.pbe-n-kjpaw_psl.0.1.UPF
[preston@preston-System-Product-Name cohp]$ sha256sum pseudo/C.pbe-n-kjpaw_psl.0.1.UPF
f147c19f79e4539c4490226dc2b68560f335e4a2008b1c7b2fdda94f2456ad32  pseudo/C.pbe-n-kjpaw_psl.0.1.UPF
```
这份文件为 858987 字节，文件头记录 `6Sep2018`、`atomic v.6.3`，是标量相对论 PBE PAW，每个 C 有 4 个价电子。随 LOBSTER 示例附带的同名文件是另一份 2012 年生成的数据，本次没有使用它。同名文件不能代替内容校验，后面全部固定上述 SHA-256。

写完输入后，进入 k6 目录，用 `cat` 核对完整文件。
```console
[preston@preston-System-Product-Name cohp]$ vi diamond-k6/diamond.scf.in
[preston@preston-System-Product-Name cohp]$ cd diamond-k6
[preston@preston-System-Product-Name diamond-k6]$ cat diamond.scf.in run.sh
&CONTROL
 calculation = 'scf'
 prefix = 'diamond'
 outdir = './tmp'
 pseudo_dir = '../pseudo'
 wf_collect = .true.
 tprnfor = .true.
 tstress = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 2
 celldm(1) = 6.746
 nat = 2
 ntyp = 1
 nbnd = 8
 ecutwfc = 60
 ecutrho = 640
 occupations = 'fixed'
 nspin = 1
 nosym = .true.
 noinv = .false.
/
&ELECTRONS
 conv_thr = 1.0d-10
 diagonalization = 'cg'
 diago_cg_maxiter = 200
 diago_thr_init = 1.0d-8
 diago_full_acc = .true.
/
ATOMIC_SPECIES
 C 12.011 C.pbe-n-kjpaw_psl.0.1.UPF
ATOMIC_POSITIONS alat
 C 0.00 0.00 0.00
 C 0.25 0.25 0.25
K_POINTS automatic
 6 6 6 0 0 0

#!/bin/bash
#SBATCH --job-name=atlas-c-cohp-k6
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -l unlimited
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in diamond.scf.in > scf.out 2> scf.err
```
`ibrav=2` 指定面心立方原胞。`ATOMIC_POSITIONS alat` 中 `0.25 0.25 0.25` 是沿笛卡尔方向、以 `alat` 为单位的坐标，不能直接当成原胞分数坐标。两个 C 共 8 个价电子，非自旋计算中有 4 条占据带。

`nbnd=8` 对应后面每个 C 选用的 2s、2p：s 有 1 个分量，p 有 3 个，两原子共 `2 × (1 + 3) = 8` 个局域轨道。只计算通常占据的 4 条带，不足以重建这个 8 维局域基组的 COHP。`diago_full_acc=.true.` 让空带也按完整精度求解，不能只关注占据带总能量。

`conv_thr=1e-10 Ry` 约束整胞电子自洽误差，不是每键 ICOHP 的 0.02 eV 比较容差。`diago_thr_init=1e-8` 给初始本征求解阈值，`diago_cg_maxiter=200` 限制每条带的 CG 内循环次数；是否求解充分，仍要看实际末轮残差及本征值警告。

`ecutwfc=60`、`ecutrho=640` 都以 Ry 为单位，分别控制波函数平面波基组和密度、势的网格。末尾保持 640 Ry 不变，把波函数截断提到 80 Ry，检查目标量 ICOHP。这不等于密度截断也已经单独收敛。

`nosym=.true.` 关闭空间群约化。`noinv=.false.` 保留时间反演约化，LOBSTER 6.0.0 支持这种输入，所以 6³ 不意味着一定写出 216 个独立 k 点。这里用自动网格，不能换成 `K_POINTS gamma` 的专用实数格式。

`wf_collect=.true.` 保留了 LOBSTER 配套输入的写法，但 QE 7.5 已将它标记为 obsolete，不再执行其旧功能。是否保存成功，要看实际波函数文件，不能凭这个开关判断。

脚本用这台机器的 GCC/OpenMPI 版 QE 7.5，4 个 MPI 进程、每进程 1 个线程。文中 `<qe_bin>` 和 `<lobster_bin>` 需替换成自己的安装路径。`unset DISPLAY XAUTHORITY` 清掉批处理不需要的图形会话变量，与电子参数无关；两条 `ulimit` 在运行前设置。标准输出与错误输出分别保存。
```console
[preston@preston-System-Product-Name diamond-k6]$ sbatch run.sh
Submitted batch job 865
```
```console
[preston@preston-System-Product-Name diamond-k6]$ squeue -u preston -o "%.18i %.16j %.8T %.6C %.10M"
             JOBID             NAME    STATE   CPUS       TIME
               865  atlas-c-cohp-k6  RUNNING      4       0:00
```
队列中的 RUNNING 说明已经分配资源。实际读入什么、电子迭代走到哪里，要看 `scf.out`。开头依次列出程序与并行设置、晶胞与电子数、截断、赝势信息。
```console
[preston@preston-System-Product-Name diamond-k6]$ head -n 80 scf.out

     Program PWSCF v.7.5 starts on 23Sep2026 at 10:29:43 

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org", 
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     4 processors

     MPI processes distributed on     1 nodes
     4290 MiB available memory on the printing compute node when the environment starts

     Reading input from diamond.scf.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4
     file C.pbe-n-kjpaw_psl.0.1.UPF: wavefunction(s)  2P renormalized

     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


     Parallelization info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Min         250      94     30                 5217     1227     234
     Max         251      95     31                 5220     1228     238
     Sum        1003     379    121                20875     4909     941

     Using Slab Decomposition



     bravais-lattice index     =            2
     lattice parameter (alat)  =       6.7460  a.u.
     unit-cell volume          =      76.7501 (a.u.)^3
     number of atoms/cell      =            2
     number of atomic types    =            1
     number of electrons       =         8.00
     number of Kohn-Sham states=            8
     kinetic-energy cutoff     =      60.0000  Ry
     charge density cutoff     =     640.0000  Ry
     scf convergence threshold =      1.0E-10
     mixing beta               =       0.7000
     number of iterations used =            8  plain     mixing
     Exchange-correlation= SLA  PW   PBX  PBC
                           (   1   4   3   4   0   0   0)

     celldm(1)=   6.746000  celldm(2)=   0.000000  celldm(3)=   0.000000
     celldm(4)=   0.000000  celldm(5)=   0.000000  celldm(6)=   0.000000

     crystal axes: (cart. coord. in units of alat)
               a(1) = (  -0.500000   0.000000   0.500000 )  
               a(2) = (   0.000000   0.500000   0.500000 )  
               a(3) = (  -0.500000   0.500000   0.000000 )  

     reciprocal axes: (cart. coord. in units 2 pi/alat)
               b(1) = ( -1.000000 -1.000000  1.000000 )  
               b(2) = (  1.000000  1.000000  1.000000 )  
               b(3) = ( -1.000000  1.000000 -1.000000 )  


     PseudoPot. # 1 for C  read from file:
     ../pseudo/C.pbe-n-kjpaw_psl.0.1.UPF
     MD5 check sum: de42a9c63963d1dbc0cd3c66b74ae98e
     Pseudo is Projector augmented-wave + core cor, Zval =  4.0
     Generated using &quot;atomic&quot; code by A. Dal Corso  v.6.3
     Shape of augmentation charge: BESSEL
     Using radial grid of 1073 points,  4 beta functions with: 
                l(1) =   0
                l(2) =   0
                l(3) =   1
```
这里是 8 个电子、8 条 Kohn–Sham 带、60/640 Ry；读入的 PAW 由 `atomic v.6.3` 生成，价电子数 4。`SLA PW PBX PBC` 是这份 PBE UPF 中记录的泛函分量标识。

再看第一轮电子迭代。每轮不只有总能量，还包括本征求解器信息和密度残差。
```console
[preston@preston-System-Product-Name diamond-k6]$ head -n 440 scf.out | tail -n 45

     Estimated total dynamical RAM >      39.63 MB

     Initial potential from superposition of free atoms

     starting charge       7.9999, renormalised to       8.0000
     Starting wfcs are    8 randomized atomic wfcs
     Checking if some PAW data can be deallocated... 

     total cpu time spent up to now is        0.6 secs

     per-process dynamical memory:    11.5 Mb

     Self-consistent Calculation

     iteration #  1     ecut=    60.00 Ry     beta= 0.70
     CG style diagonalization

---- Real-time Memory Report at c_bands before calling an iterative solver
            34 MiB given to the printing process from OS
            11 MiB allocation reported by mallinfo(arena+hblkhd)
          4238 MiB available memory on the node where the printing process lives
------------------
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  2 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     ethr =  1.00E-08,  avg # of iterations = 44.1

     total cpu time spent up to now is        9.1 secs

     total energy              =     -36.85981362 Ry
     estimated scf accuracy    <       0.11729238 Ry

     iteration #  2     ecut=    60.00 Ry     beta= 0.70
     CG style diagonalization
```
第一轮真实出现了 `eigenvalues not converged`。它从随机化原子波函数开始，不能把这几行删掉，也不能只凭它们就断定最终状态。这次继续迭代后，后续电子步和最终求解中都没有该警告，最终残差降到 `1.6E-11 Ry`。若警告延续至最后一轮，或 SCF 残差未通过，应先处理波函数精度再投影。

输出末尾先列逐 k 本征值和占据数，再给最终能量、能量分项、收敛结论和力。
```console
[preston@preston-System-Product-Name diamond-k6]$ tail -n 230 scf.out | head -n 75
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k = 1.1667 0.5000 0.1667 (   608 PWs)   bands (ev):

    -0.5962   1.6167   5.5037   7.3993  22.0964  23.3287  27.0264  27.2778

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k = 1.0000 0.6667-0.0000 (   608 PWs)   bands (ev):

     1.1054   1.1054   5.5203   5.5203  21.5216  21.5216  27.7879  27.7879

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k = 0.0000 0.0000-1.0000 (   620 PWs)   bands (ev):

     0.5640   0.5640   7.0270   7.0270  18.0669  18.0669  30.0776  30.0776

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k =-0.1667 0.1667-1.1667 (   603 PWs)   bands (ev):

    -1.5416   3.1034   5.6773   7.6861  18.5731  21.6564  28.1068  28.4825

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k =-0.3333 0.3333-1.3333 (   606 PWs)   bands (ev):

    -2.3912   1.3202   8.3318   9.3536  20.4028  24.0165  24.5069  27.5724

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k = 0.5000-0.5000-0.5000 (   610 PWs)   bands (ev):

    -2.3710  -0.0354  10.5160  10.5160  21.7627  21.7627  22.1263  28.9860

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

     highest occupied, lowest unoccupied level (ev):    13.3079   17.4618

!    total energy              =     -36.86860268 Ry
     total all-electron energy =      -152.396805 Ry
     estimated scf accuracy    <          1.6E-11 Ry

     The total energy is the sum of the following terms:
     one-electron contribution =       8.43290098 Ry
     hartree contribution      =       1.93838719 Ry
     xc contribution           =      -8.38857107 Ry
     ewald contribution        =     -25.55255521 Ry
     one-center paw contrib.   =     -13.29876457 Ry
      -> PAW hartree energy AE =      10.42443149 Ry
      -> PAW hartree energy PS =     -10.41057198 Ry
      -> PAW xc energy AE      =     -10.82373741 Ry
      -> PAW xc energy PS      =       4.16049558 Ry
      -> total E_H with PAW    =       1.95224670 Ry
      -> total E_XC with PAW   =     -15.05181290 Ry

     convergence has been achieved in  26 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000022   -0.00000006    0.00000002
     atom    2 type  1   force =     0.00000022    0.00000006   -0.00000002
     The non-local contrib.  to forces
     atom    1 type  1   force =     0.00000009    0.00000009   -0.00000012
     atom    2 type  1   force =    -0.00000009   -0.00000014    0.00000014
     The ionic contribution  to forces
     atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
     atom    2 type  1   force =    -0.00000000    0.00000000   -0.00000000
```
`convergence has been achieved in 26 iterations` 和残差共同说明 SCF 通过。占据数前四条为 1、后四条为 0；这个非自旋格式已把自旋简并计入总共 8 个电子，不能把它误读成只有 4 个电子。

最高占据能级为 13.3079 eV，最低未占据能级为 17.4618 eV，是此固定结构和网格下的计算能级。XML 记录的能量参考与最高占据能级一致；稍后 LOBSTER 的 0 eV 也在价带顶，没有自动放到带隙中点。
```console
[preston@preston-System-Product-Name diamond-k6]$ tail -n 15 scf.out
     interpolate  :      0.10s CPU      0.10s WALL (      27 calls)

     Parallel routines

     PAW routines
     PAW_pot      :      0.73s CPU      0.75s WALL (      27 calls)

     PWSCF        :     29.92s CPU     32.56s WALL


   This run was terminated on:  10:30:16  23Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
这组 SCF 实际用时 32.56 秒。`JOB DONE.` 说明程序正常结束；电子收敛与后面的投影质量仍需分别核对。接着看 LOBSTER 真正要读取的保存目录。
```console
[preston@preston-System-Product-Name diamond-k6]$ ls tmp/diamond.save | head -n 12
C.pbe-n-kjpaw_psl.0.1.UPF
charge-density.dat
data-file-schema.xml
paw.txt
wfc1.dat
wfc10.dat
wfc100.dat
wfc101.dat
wfc102.dat
wfc103.dat
wfc104.dat
wfc105.dat
```
```console
[preston@preston-System-Product-Name diamond-k6]$ ls tmp/diamond.save/wfc*.dat | wc -l
112
```
XML 保存设置、结构、k 点、本征值和占据；`charge-density.dat` 是密度，`wfc*.dat` 是波函数，`paw.txt` 和对应 UPF 提供 PAW 数据。112 份波函数与 XML 和原生输出中的 112 个独立 k 点吻合。这些文件来自同一次 SCF，才构成后处理的输入。

同目录写入 `lobsterin`。C 显式选用 2s、2p，保留默认正交化；距离筛选包括最近邻而排除更远的壳层。
```console
[preston@preston-System-Product-Name diamond-k6]$ cat > lobsterin <<'EOF'
COHPStartEnergy -25
COHPEndEnergy 15
COHPSteps 2001
basisSet Bunge
basisFunctions C 2s 2p
gaussianSmearingWidth 0.2
printTotalSpilling
cohpGenerator from 1.4 to 1.7
EOF

```
`cohpGenerator` 距离单位为 Å，本模型最近邻约 1.546 Å。实际找到几条键仍要看输出。能量窗口 −25 到 15 eV 相对 LOBSTER 的能量零点，覆盖占据价带并显示部分空态。`COHPSteps` 控制能量网格细分，实际行数受端点、零点处理影响，后面直接读文件头。

`gaussianSmearingWidth=0.2` 的单位为 eV，控制后处理谱的展宽；它不是 QE 里以 Ry 为单位的 `degauss`，也没有改变 SCF 的固定占据。

LOBSTER 用 OpenMP，下面只启动一个程序实例并给它 4 个线程，不用 MPI 启动多份程序。
```console
[preston@preston-System-Product-Name diamond-k6]$ cat lobsterin run-lobster.sh
COHPStartEnergy -25
COHPEndEnergy 15
COHPSteps 2001
basisSet Bunge
basisFunctions C 2s 2p
gaussianSmearingWidth 0.2
printTotalSpilling
cohpGenerator from 1.4 to 1.7
#!/bin/bash
#SBATCH --job-name=atlas-c-lob-k6
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
```
```console
[preston@preston-System-Product-Name diamond-k6]$ sbatch run-lobster.sh
Submitted batch job 866
```
结束后读 `lobsterout`。它把程序识别、推荐与实际基组、键数、投影诊断、积分方法、输出文件保存在一起。
```console
[preston@preston-System-Product-Name diamond-k6]$ cat lobsterout
LOBSTER v6.0.0 (g++ 9.3.0)
Copyright (C) 2026 by Chair of Solid-State and Quantum Chemistry, RWTH Aachen.
All rights reserved. Contributions by S. Maintz, V. L. Deringer, M. Esser, R. Nelson, C. Ertural, P. C. Mueller, L. S. Reitz, M. Pauls, L. Sann, D. Schnieders, A. L. Tchougreeff, and R. Dronskowski
starting on host preston-System-Product-Name on 2026-09-23 at 10:31:41 CST using 4 threads
detecting used PAW program... Quantum Espresso
initializing PW system...
initializing Augmentations...
recommended basis functions:
C 2p 2s 
initializing LCAO system...
setting up local basis functions...
 C (bunge) 2s 2p_y 2p_z 2p_x 
setting up CO interactions... found 4 interactions.
projecting...
WARNING: Cannot use the tetrahedron method for k-space integration and must fall
WARNING: back to Gaussian smearing which can take significantly longer. Make
WARNING: sure to use the tetrahedron method whenever applicable.

calculating overlaps...
post-processing projection...
abs. total  spilling:   9.23%
abs. charge spilling:   1.12%

NOTE: The spilling is a measure for the relocation, *not* the absence of electrons.
number of electrons recovered by projection: 8.0000 of 8

calculating pDOS... using Gaussian smearing integration (sigma=0.2eV)
writing DOSCAR.lobster...
writing COOPCAR.lobster...
Writing ICOOPLIST.lobster
calculating pCOHPs... using Gaussian smearing integration (sigma=0.2eV)
writing CHARGE.lobster...
Writing GROSSPOP.lobster...
writing polarization to POLARIZATION.lobster...
calculating Madelung energies...
writing SitePotentials.lobster and MadelungEnergies.lobster...
writing Valences.lobster...
writing OxidationScores.lobster...
writing COHPCAR.lobster...
Writing ICOHPLIST.lobster
writing COBICAR.lobster...
Writing ICOBILIST.lobster
finished in 0 h  0 min  1 s 704 ms of wall time
            0 h  0 min  6 s 360 ms of user time
            0 h  0 min  0 s  80 ms of sys  time
```
程序识别到 Quantum ESPRESSO；推荐 C 2p、2s，与实际 `C (bunge) 2s 2p_y 2p_z 2p_x` 相符，找到 4 条相互作用。

这里明确提示不能使用四面体积分，实际用了 `sigma=0.2 eV` 的 Gaussian 方法。后面所有比较保持相同展宽；改变它会改变峰宽和零点附近的累计曲线。

`abs. charge spilling=1.12%` 主要检查占据电子子空间；`abs. total spilling=9.23%` 还包括参与投影的空带。后者较大，显示这个最小 C 2s/2p 空间对整组能带的表示有限，尤其限制高能空态谱的定量解释。这里不把某个 spilling 值当作通用合格线。`8.0000 of 8` 也不表示投影无误：电子数在正交化后可以恢复，局域表示误差仍需看 spilling 和重叠诊断。

六份后处理中都没有 `bandOverlaps.lobster` 或相应警告。按配套手册，这个文件在重叠偏离触发条件时才写出；未生成是本次诊断的一部分，不是所有物理量都已收敛的证明。

另用同一份 k6 波函数选 Koga 和 pbeVaspFit2015，仍只使用 C 2s/2p。原生输出分别回显库名，charge/total spilling 仍为 1.12%/9.23%，ICOHP 与 Bunge 最多差 0.00001 eV。两套替代库的投影矩阵在输出精度内相同，不能将三个库名当成三个独立基组空间的收敛证明。本次没有明确理由换库，正式的网格、截断对照全部固定 Bunge。

现在读每条键的积分值。
```console
[preston@preston-System-Product-Name diamond-k6]$ cat ICOHPLIST.lobster
  COHP#    atomMU    atomNU   distance   translation   ICOHP (at) eF 
                                                          for spin 1 
      1        C1        C2    1.54578     0  -1   0        -9.60866 
      2        C1        C2    1.54578     1  -1   0        -9.60866 
      3        C1        C2    1.54578     0   0   0        -9.60867 
      4        C1        C2    1.54578     0  -1   1        -9.60866
```
每行是键编号、起点原子、终点原子、距离、终点晶胞的三个整数平移，最后是 ICOHP。起点都是原胞 C1，终点是不同晶胞中的 C2。`(0,0,0)` 是同胞的一条，其余三条跨越边界，并非同一条键重复抄写。

本例非自旋输出只有 `for spin 1` 这一组数据，不能再把每个数乘 2。金刚石的四个最近邻应等价，这里差约 0.00001 eV，属于数值精度与文本舍入。比较设置时按原子编号和晶胞平移匹配同一条键，同时检查平均变化和最大单键变化。

本轮实际结构文件名带有 `.vasp` 后缀。
```console
[preston@preston-System-Product-Name cohp]$ cat diamond-k6/POSCAR.lobster.vasp
C2
1.0
-1.78491        0  1.78491
       0  1.78491  1.78491
-1.78491  1.78491        0
 C
 2
Direct
0 0 0
-0.25  0.75 -0.25
```
这个文件是 Å 晶格与原胞分数坐标。C2 的 `(-0.25,0.75,-0.25)` 与输入中的笛卡尔 `alat` 坐标表示同一位置；分数坐标可超出 0–1，周期平移后仍等价。图用精度更高的 QE XML 晶格和位置，结合 ICOHPLIST 平移，重建四个邻居并核对距离。

![由真实晶格和 ICOHPLIST 平移重建的四条最近邻 C–C 键](/Atlas/figures/cohp-diamond/cohp-bonds.png)

原胞含两原子，各自四配位，每条键连接两个原子，唯一近邻键数为 `2 × 4 / 2 = 4`。本页给每条键或四键平均；如果需要这组近邻的每原胞总贡献，才把四个唯一键相加，不能再重复乘配位数。

再看能量分辨的文件。
```console
[preston@preston-System-Product-Name diamond-k6]$ head -n 14 COHPCAR.lobster
ESCALE ; pCOHP file generated by LOBSTER. Energy is shifted such that the Fermi level lies at 0 eV.
         5          1       2002  -1.16921e+01   2.83279e+01   1.33079e+01 
Average
No.1:C1->C2(1.5457814950700495)
No.2:C1->C2(1.5457814950700495)
No.3:C1->C2(1.5457814950700495)
No.4:C1->C2(1.5457814950700495)
-25.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
-24.98000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
-24.96000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
-24.94000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
-24.92000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
-24.90000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
-24.88000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
```
第一行已说明能量平移到 `EF=0`。第二行的 5 表示一个平均通道加四条键，1 表示一组自旋数据，2002 是实际能量点数。输入 `COHPSteps=2001`，输出仍应按真实头部和行数读取。本次从 −25.00 eV 开始，步长约 0.02 eV，末端实际为 15.02 eV。头部保存的绝对边界和 13.3079 eV 参考值不是第一列的能量轴，不能再次平移。

| 列 | 本例含义 |
| --- | --- |
| 1 | 已平移的 `E−EF`，eV |
| 2、3 | 四键平均的 pCOHP、累计 pCOHP |
| 4、5 | 第 1 条键的 pCOHP、累计值 |
| 6、7 | 第 2 条键的 pCOHP、累计值 |
| 8、9 | 第 3 条键的 pCOHP、累计值 |
| 10、11 | 第 4 条键的 pCOHP、累计值 |

原始 pCOHP 的负值表示成键贡献，正值表示反键贡献。图画 `−pCOHP`，因此正侧表示成键；右图同样画 `−ICOHP(E)`，单位为 eV/bond；正文数表则保留 ICOHPLIST 的原始负号。两幅图共享纵轴 `E−EF`，横轴分别是谱与累计能量贡献，不能把两者数值直接比较。

通常把积分写作 `ICOHP = ∫ COHP(E) dE`，上限取相应占据参考。本例还需区分实际文件：ICOHPLIST 给原生占据态积分，COHPCAR 是 Gaussian 展宽的谱及累计曲线。k6 的原生四键平均为 −9.6086625 eV，COHPCAR 在 0 eV 行的累计平均为 −9.60613 eV；对离散谱用梯形法积分到 0 得到约 −9.605996 eV，不能强行写成完全相等。

这里零点在价带顶，Gaussian 展宽将部分边缘谱重带到 0 eV 之上。原生占据求和与截到这个端点的展宽曲线不完全相同；到带隙中约 1.5 eV 的平台，累计值约为 −9.60866 eV。网格和截断比较始终用同定义的 ICOHPLIST，把约 0.00253 eV 的端点差单独保留。

![固定基组的金刚石最近邻 −pCOHP 与累计曲线](/Atlas/figures/cohp-diamond/cohp-spectrum.png)

谱图显示最终 `diamond-k10-80`，零点沿用 QE/LOBSTER 的参考，与价带顶重合。占据能区给出负的原生 ICOHP，支持此固定结构中近邻的净成键贡献。它是局域轨道下的带能贡献，不是拉断 C–C 键的解离能。只有 8 条带与 C 2s/2p，未做空态谱收敛，高能空态图形用于查看文件与符号，不能当作精确的完整空态谱。

## 改变网格和截断后，逐键比较

接着检查结果对采样有多敏感。新目录只复制输入和脚本，每组重新 SCF，不复制正在使用的波函数目录。以 k8 为例，实际操作是：

```console
[preston@preston-System-Product-Name cohp]$ mkdir diamond-k8
[preston@preston-System-Product-Name cohp]$ cp diamond-k6/diamond.scf.in diamond-k6/run.sh diamond-k8/
[preston@preston-System-Product-Name cohp]$ vi diamond-k8/diamond.scf.in
```

把输入末尾改为 `8 8 8 0 0 0`，脚本作业名也改为 k8，随后实际 `cat` 回读完整文件，确认 60/640 Ry、结构、占据、带数和其它电子设置保持一致。

```console
[preston@preston-System-Product-Name cohp]$ cd diamond-k8
[preston@preston-System-Product-Name diamond-k8]$ sbatch run.sh
Submitted batch job 867
```

计算中读输出末尾，看当前电子迭代是否还在推进。这是本次尚未结束时的真实状态：

```console
[preston@preston-System-Product-Name cohp]$ tail -n 8 diamond-k8/scf.out
     iteration # 15     ecut=    60.00 Ry     beta= 0.70
     CG style diagonalization

---- Real-time Memory Report at c_bands before calling an iterative solver
            42 MiB given to the printing process from OS
            20 MiB allocation reported by mallinfo(arena+hblkhd)
          3880 MiB available memory on the node where the printing process lives
------------------
```

这段只有第 15 轮求解信息，还没有最终结论。等 SCF 正常结束并检查最终电子步后，再使用完全相同的 LOBSTER 输入：

```console
[preston@preston-System-Product-Name cohp]$ cp diamond-k6/lobsterin diamond-k6/run-lobster.sh diamond-k8/
[preston@preston-System-Product-Name cohp]$ cd diamond-k8
[preston@preston-System-Product-Name diamond-k8]$ sbatch run-lobster.sh
Submitted batch job 872
```

k10 同样建立独立目录，改成 `10 10 10 0 0 0`；最后一组仍用 k10，只把 `ecutwfc=60` 改成 `80`，密度截断仍为 640 Ry。所有组固定几何、同一 SHA 的 PAW、8 条带、非自旋固定占据、Bunge C 2s/2p、Gaussian 0.2 eV 和能量窗口。

四组 SCF 分别在 26、23、28、31 轮收敛。第一轮分别出现 12、10、28、27 行本征值警告，之后各轮及最后一轮均未再出现；下载包保留完整输出。四次 LOBSTER 均正常结束，四个原子对和平移匹配。

| 目录 | k 网格 | 独立 k 点 | 波函数/密度截断（Ry） | SCF 墙时 | 四键平均 ICOHP（eV/bond） | charge / total spilling |
| --- | --- | ---: | --- | --- | ---: | --- |
| diamond-k6 | 6³ | 112 | 60 / 640 | 32.56 s | −9.6086625 | 1.12% / 9.23% |
| diamond-k8 | 8³ | 260 | 60 / 640 | 1 min 11.25 s | −9.6049900 | 1.11% / 9.24% |
| diamond-k10 | 10³ | 504 | 60 / 640 | 2 min 35.27 s | −9.6040500 | 1.11% / 9.26% |
| diamond-k10-80 | 10³ | 504 | 80 / 640 | 5 min 4.58 s | −9.6039400 | 1.11% / 9.26% |

平均数来自原生文本中的四个积分。多列出的小数位用于明确算术平均，没有增加原始输出的物理精度。

计算前选定 **0.02 eV/bond** 作为本次教学比较线，分别检查平均变化和最大单键变化。它是本例目标量的数值标准，不是 LOBSTER 官方通用阈值，也不是 PBE 模型误差或实验精度。

| 对照 | 平均值的绝对变化（eV/bond） | 最大单键变化（eV/bond） |
| --- | ---: | ---: |
| k6 → k8，60/640 Ry | 0.0036725 | 0.00368 |
| k8 → k10，60/640 Ry | 0.0009400 | 0.00094 |
| k10，60 → 80 Ry，密度截断仍为 640 Ry | 0.0001100 | 0.00011 |

![相同几何、PAW、基组与积分设置下的 ICOHP 对照](/Atlas/figures/cohp-diamond/cohp-comparison.png)

三个变化都小于本次比较线，支持“在已测试的 k 网格与 60→80 Ry 波函数截断范围内，最近邻 ICOHP 对这些设置不敏感”。这个结论只覆盖已测试范围：密度截断未单独收敛，展宽固定，几何未重新优化，空态总 spilling 仍约 9.26%。这些限制不会因一个比较表通过而消失。

## 从原始文件重画并导出论文用图

最后在本机重画。公开包解压后进入 `diamond-cohp`，在 **NumPy ≥ 2.0、Matplotlib** 的 Python 环境执行：

```bash
python3 plot_cohp.py
```

本次在 Mac 的 NumPy 2.3.4、Matplotlib 3.10.7 环境重画并核对了三张图。脚本直接读取各目录的 COHPCAR、ICOHPLIST、lobsterout、输入和 QE XML，不调用 LOBSTER，也不需要波函数。它检查真实列数和能量点数、四条键、已经平移的能量轴、XML 几何与距离，同时独立检查 0 eV 谱积分与原生 ICOHP 的差。输出在 `figures/`：三张网页用 PNG、对应矢量 PDF，以及 `plot-checks.json`。PDF 按 183 mm 宽单独排版，正文标注 5–7 pt、面板字母 8 pt；PNG 使用较大的阅读字号。字体使用本机 Arial，PDF 已检查为嵌入的 TrueType；有数学符号的部分同时嵌入 DejaVu Sans。其他机器若没有 Arial 或 Helvetica，脚本明确回退到 DejaVu Sans。

图中只保留零能量线、正负号分界和数值比较线。参数对照的右图使用对数纵轴，便于同时读出 0.00368、0.00094 和 0.00011 eV/bond 三个变化；它没有改变原始积分。邻近键图由 XML 坐标和周期平移计算，球的大小仅帮助辨认原子，不表示原子半径。

完整脚本可单独下载：[plot_cohp.py](/Atlas/examples/diamond-cohp/plot_cohp.py)。一般的轴标、图例、配色与矢量导出操作见[科研图的后处理与导出](/Atlas/plotting/)。

读图时先定位 0 eV 与正负号，再核对画的是单键、四键平均还是总和。引用数字时回到相应目录的原生 ICOHPLIST 和参数对照，便能把成键图连回具体波函数、局域基组和周期原子对。

下一步：[投影能带](/Atlas/m/fatband/qe/)看沿 k 路径的轨道成分；[电子布居分析](/Atlas/m/population-analysis/qe/)看投影电子数。这些量可以与成对 Hamiltonian 分解结合阅读。

```text
固定金刚石两原子结构 + 同一份 PBE PAW
  → 每个网格各自进行静态 SCF
  → 检查电子收敛、8 条带、完整 .save
  → LOBSTER：固定 C 2s/2p，核对四条周期键与投影质量
  → ICOHPLIST 同定义对照 + COHPCAR 绘图
  → 在已测试数值范围内解释最近邻净成键贡献
```
