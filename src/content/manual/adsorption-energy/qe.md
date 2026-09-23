[QE：pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE：结构优化](https://www.quantum-espresso.org/Doc/pw_user_guide/node11.html) · [ASE：表面与吸附体建模](https://wiki.fysik.dtu.dk/ase/ase/build/surface.html)

把两个 H 放到 Al 表面，程序会给出一个新的总能。但吸附态比洁净表面多了两个原子，两个 OUT 的总能直接相减还没有说明 H 从哪里来。这里选气相 H₂ 作为来源：一分子 H₂ 提供两个 H，分别放到薄膜上下表面的 Al 顶位。要计算的反应是 `洁净 Al 薄膜 + H₂ → 两面各吸附一个 H 的 Al 薄膜`。

这次使用三个明确的结构：三层 Al(111) 洁净薄膜、同一薄膜上增加两个 H 的吸附态，以及独立盒子中的 H₂。每个表面原胞含一个 Al，表面每胞再放一个 H，所以**每一面都是 1 ML 覆盖度**。这是一个三层、指定 atop 位点的例子；三个目录始终一起核对。

本页的[完整计算文件包](/Atlas/examples/h-al111-adsorption-files.tar.gz)包含 13 项实际计算的输入、OUT、XML、逐项核对记录和绘图脚本。解压后保留目录层级；运行脚本里的 `<qe_bin>` 需改为本机 QE 的程序目录。包内没有保存波函数或电荷密度，图表可直接从 OUT、XML 和 CSV 重建，重新做电子计算则从所附输入开始。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ ls -lh clean-slab/relax.* adsorbed/relax.* h2-10A/relax.*
-rw-rw-r-- 1 preston preston   0 Sep 22 23:54 adsorbed/relax.err
-rw-rw-r-- 1 preston preston 942 Sep 22 23:53 adsorbed/relax.in
-rw-rw-r-- 1 preston preston 85K Sep 22 23:58 adsorbed/relax.out
-rw-rw-r-- 1 preston preston   0 Sep 22 23:54 clean-slab/relax.err
-rw-rw-r-- 1 preston preston 800 Sep 22 23:53 clean-slab/relax.in
-rw-rw-r-- 1 preston preston 67K Sep 22 23:57 clean-slab/relax.out
-rw-rw-r-- 1 preston preston   0 Sep 22 23:54 h2-10A/relax.err
-rw-rw-r-- 1 preston preston 716 Sep 22 23:53 h2-10A/relax.in
-rw-rw-r-- 1 preston preston 23K Sep 22 23:55 h2-10A/relax.out
[preston@preston-System-Product-Name h-al111-adsorption]$
```

`clean-slab` 有 3 个 Al，`adsorbed` 有 3 个 Al 和 2 个 H，`h2-10A` 只有 2 个 H。`relax.in` 是输入，`relax.out` 是主输出，`relax.err` 是单独保存的错误流。本次三份错误流实际均为 0 B；换到其它会话或机器时仍要重新检查。普通 [SCF](/Atlas/m/scf/qe/) 和 [固定晶胞结构优化](/Atlas/m/relax/qe/) 的基本流程从链接进入，下面集中看吸附计算增加的结构与参考态约束。

Al 的面内晶格来自 [形成能例子](/Atlas/m/formation-energy/qe/) 中同一套 PBE USPP 的 fcc Al 优化，常规立方晶格常数为 `4.04281076 Å`。由它构造 (111) 面，面内最近邻周期为 `a/√2=2.85869891 Å`，初始层间距为 `a/√3=2.33411788 Å`。三个 Al 组成 ABC 堆垛，中层固定，外层和 H 可以移动。

上下两个 H 互为反演对应，初始都在表面 Al 的正上方 `1.6 Å` 处。两面相同的构造避免引入单面吸附模型的净垂直偶极；仍需要真空与薄膜厚度检查。晶胞高度为 `22.86823576 Å`，初始跨周期相邻 H 层之间留出 `15 Å`。洁净薄膜使用完全相同的三根晶胞矢量。构造说明与实际坐标保存在 [sources/construction.json](/Atlas/examples/h-al111-adsorption/sources/construction.json)。

Al 与 H 的赝势分别来自 QE 官方托管的 pslibrary 1.0.0：[Al](https://pseudopotentials.quantum-espresso.org/upf_files/Al.pbe-n-rrkjus_psl.1.0.0.UPF)、[H](https://pseudopotentials.quantum-espresso.org/upf_files/H.pbe-rrkjus_psl.1.0.0.UPF)。两者都是标量相对论 PBE USPP，文件独立核对了来源和 SHA。这个例子使用非自旋极化模型，没有加入 SOC、U 或色散修正。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ sha256sum pseudo/*.UPF
cc4f5dc6afe09c8f482dc7645e6e7cca546a55f8d907c71c825c62bf85a38d3e  pseudo/Al.pbe-n-rrkjus_psl.1.0.0.UPF
e03cd098d78e3eeb37cc9f790690f5827234cbc019fb621913391689a9ddacf7  pseudo/H.pbe-rrkjus_psl.1.0.0.UPF
[preston@preston-System-Product-Name h-al111-adsorption]$
```

先用 5 原子的初始吸附态做一次短 SCF，确认输入和预计耗时。实际用了 `26.31 s`，电子部分 10 轮收敛，但 H 的初始力分量约为 `0.00331637 Ry/Bohr`，还不能把这个结构直接拿来作为优化后的吸附态。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ grep -n -E 'convergence has been achieved|Total force|PWSCF|JOB DONE' pilot/scf.out
2:     Program PWSCF v.7.5 starts on 22Sep2026 at 23:52:22 
20:     Current dimensions of program PWSCF are:
313:     convergence has been achieved in  10 iterations
325:     Total force =     0.004704     Total SCF correction =     0.000039
383:     PWSCF        :     23.65s CPU     26.31s WALL
389:   JOB DONE.
[preston@preston-System-Product-Name h-al111-adsorption]$
```

这里 `JOB DONE.` 与电子收敛已经出现，`Total force=0.004704` 仍然很大。吸附计算还要让原子位置继续调整。接着复制这份输入，在 vi 中把任务改为 `relax`，加入 BFGS 离子段并使用独立前缀：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ cp pilot/scf.in adsorbed/relax.in
[preston@preston-System-Product-Name h-al111-adsorption]$
```

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ vi adsorbed/relax.in
```

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ cat adsorbed/relax.in
&CONTROL
 calculation='relax'
 prefix='adsorbed'
 outdir='./tmp'
 pseudo_dir='../pseudo'
 tstress=.true.
 tprnfor=.true.
 nstep=35
 etot_conv_thr=1.0d-5
 forc_conv_thr=2.0d-4
/
&SYSTEM
 ibrav=0
 nat=5
 ntyp=2
 nbnd=12
 ecutwfc=60
 ecutrho=640
 occupations='smearing'
 smearing='mv'
 degauss=0.01
/
&ELECTRONS
 conv_thr=1.0d-9
/
&IONS
 ion_dynamics='bfgs'
/
ATOMIC_SPECIES
Al 26.9815385 Al.pbe-n-rrkjus_psl.1.0.0.UPF
H 1.00794 H.pbe-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
2.858698905630 0.000000000000 0.000000000000
1.429349452815 2.475705874046 0.000000000000
0.000000000000 0.000000000000 22.868235764697
ATOMIC_POSITIONS angstrom
Al 2.858698905630 1.650470582697 9.100000000000 1 1 1
Al 0.000000000000 0.000000000000 11.434117882349 0 0 0
Al 1.429349452815 0.825235291349 13.768235764697 1 1 1
H 2.858698905630 1.650470582697 7.500000000000 1 1 1
H 1.429349452815 0.825235291349 15.368235764697 1 1 1
K_POINTS automatic
6 6 1 0 0 0
[preston@preston-System-Product-Name h-al111-adsorption]$
```

`CELL_PARAMETERS angstrom` 给出真实长度；`ATOMIC_POSITIONS angstrom` 后的数值也是 Å。中层 Al 行末的 `0 0 0` 固定三个方向，其余原子的 `1 1 1` 允许移动。晶胞本身保持不变，所以使用 `relax`。面内应变、薄膜厚度和覆盖度都属于此处已选定的模型。

`ecutwfc=60 Ry`、`ecutrho=640 Ry`、PBE 赝势和 `mv` 展宽在三份能量里保持一致。表面使用 `6 6 1` 网格，垂直方向只有一个点。电子阈值为 `1e-9 Ry`；BFGS 同时要求能量变化小于 `1e-5 Ry`，每个可动的力分量小于 `2e-4 Ry/Bohr`，后者约为 `0.00514 eV/Å`。这些是这一次优化的停止条件，参数误差还要用后面的对照计算检查。

洁净基底的完整输入是 [clean-slab/relax.in](/Atlas/examples/h-al111-adsorption/clean-slab/relax.in)：保留同一晶胞和三层 Al，去掉 H，重新独立优化外层 Al。它与吸附态分别松弛，因此后面的能量差包含基底因吸附而发生的结构调整。

H₂ 的参考文件也要看清楚。表面原胞横向只有约 `2.86 Å`，直接把 H₂ 塞进这个窄胞，会得到横向重复很密的分子阵列。这里把 H₂ 放入 `10 Å` 的立方盒，初始键长 `0.74 Å`，在同一盒中先优化键长：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ cat h2-10A/relax.in
&CONTROL
 calculation='relax'
 prefix='h2-10A'
 outdir='./tmp'
 pseudo_dir='../pseudo'
 tstress=.true.
 tprnfor=.true.
 nstep=35
 etot_conv_thr=1.0d-5
 forc_conv_thr=2.0d-4
/
&SYSTEM
 ibrav=0
 nat=2
 ntyp=1
 nbnd=4
 ecutwfc=60
 ecutrho=640
 occupations='smearing'
 smearing='mv'
 degauss=0.01
/
&ELECTRONS
 conv_thr=1.0d-9
/
&IONS
 ion_dynamics='bfgs'
/
ATOMIC_SPECIES
H 1.00794 H.pbe-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
10.000000000000 0.000000000000 0.000000000000
0.000000000000 10.000000000000 0.000000000000
0.000000000000 0.000000000000 10.000000000000
ATOMIC_POSITIONS angstrom
H 5.000000000000 5.000000000000 4.630000000000 1 1 1
H 5.000000000000 5.000000000000 5.370000000000 1 1 1
K_POINTS gamma
[preston@preston-System-Product-Name h-al111-adsorption]$
```

两电子 H₂ 按闭壳层非磁性模型处理。它与表面使用相同的 H 赝势、PBE、截断和展宽；它的三维周期盒使用 Γ 点，并在后面用更大的盒子检查镜像影响。表面与分子的 k 网格不同来自两个模型的周期性，不是从不相干的研究目录各取一个能量。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ cat adsorbed/run.sh
#!/bin/bash
#SBATCH --job-name=a-adsorbed
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in relax.in > relax.out 2> relax.err
[preston@preston-System-Product-Name h-al111-adsorption]$
```

这份脚本对应 Preston 上的 GCC/OpenMPI QE 7.5，每项使用 4 个 MPI 进程，线程数固定为 1。主输出和错误流分开写；Slurm 的 `_out.%j.log`、`_err.%j.log` 另行保留。三份任务分别提交：

```console
[preston@preston-System-Product-Name clean-slab]$ sbatch run.sh
Submitted batch job 853
[preston@preston-System-Product-Name clean-slab]$
```

```console
[preston@preston-System-Product-Name adsorbed]$ sbatch run.sh
Submitted batch job 854
[preston@preston-System-Product-Name adsorbed]$
```

```console
[preston@preston-System-Product-Name h2-10A]$ sbatch run.sh
Submitted batch job 855
[preston@preston-System-Product-Name h2-10A]$
```

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ squeue -u preston -o "%i %j %T %C %M"
JOBID NAME STATE CPUS TIME
855 a-h2-10A RUNNING 4 0:05
854 a-adsorbed RUNNING 4 0:08
853 a-clean-slab RUNNING 4 0:11
[preston@preston-System-Product-Name h-al111-adsorption]$
```

队列里的 `RUNNING` 说明资源已经分配。再看 `relax.out` 中电子迭代与离子步是否持续推进；可使用 `tail -f adsorbed/relax.out` 跟踪新行，或 `watch -n 2 "tail -n 12 adsorbed/relax.out"` 重看尾部，按 Ctrl-C 退出监视。电子迭代结束后还可能开始下一轮原子移动，所以尾部出现一次电子收敛并不等于整个优化已经结束。

打开吸附态 OUT 的开头，可以先确认程序、资源和模型是否真的是刚才提交的那份输入：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ head -n 110 adsorbed/relax.out

     Program PWSCF v.7.5 starts on 22Sep2026 at 23:54:42 

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
     2664 MiB available memory on the printing compute node when the environment starts

     Reading input from relax.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4
     Message from routine setup:
     using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead

     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


     Parallelization info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Min         321     123     37                74689    17124    2889
     Max         322     129     38                74718    17125    2906
     Sum        1285     499    151               298799    68499   11607

     Using Slab Decomposition



     bravais-lattice index     =            0
     lattice parameter (alat)  =       5.4022  a.u.
     unit-cell volume          =    1092.1863 (a.u.)^3
     number of atoms/cell      =            5
     number of atomic types    =            2
     number of electrons       =        11.00
     number of Kohn-Sham states=           12
     kinetic-energy cutoff     =      60.0000  Ry
     charge density cutoff     =     640.0000  Ry
     scf convergence threshold =      1.0E-09
     mixing beta               =       0.7000
     number of iterations used =            8  plain     mixing
     energy convergence thresh.=      1.0E-05
     force convergence thresh. =      2.0E-04
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     nstep                     =           35


     celldm(1)=   5.402158  celldm(2)=   0.000000  celldm(3)=   0.000000
     celldm(4)=   0.000000  celldm(5)=   0.000000  celldm(6)=   0.000000

     crystal axes: (cart. coord. in units of alat)
               a(1) = (   1.000000   0.000000   0.000000 )  
               a(2) = (   0.500000   0.866025   0.000000 )  
               a(3) = (   0.000000   0.000000   7.999526 )  

     reciprocal axes: (cart. coord. in units 2 pi/alat)
               b(1) = (  1.000000 -0.577350  0.000000 )  
               b(2) = (  0.000000  1.154701  0.000000 )  
               b(3) = (  0.000000  0.000000  0.125007 )  


     PseudoPot. # 1 for Al read from file:
     ../pseudo/Al.pbe-n-rrkjus_psl.1.0.0.UPF
     MD5 check sum: bbe9f3f15d9b3b5ab9a58e4859ebdbfe
     Pseudo is Ultrasoft + core correction, Zval =  3.0
     Generated using &quot;atomic&quot; code by A. Dal Corso  v.6.3
     Using radial grid of 1135 points,  6 beta functions with: 
                l(1) =   0
                l(2) =   0
                l(3) =   1
                l(4) =   1
                l(5) =   2
                l(6) =   2
     Q(r) pseudized with 0 coefficients 


     PseudoPot. # 2 for H  read from file:
     ../pseudo/H.pbe-rrkjus_psl.1.0.0.UPF
     MD5 check sum: 3f4114867bd07edc7f1424d066fc1888
     Pseudo is Ultrasoft, Zval =  1.0
     Generated using &quot;atomic&quot; code by A. Dal Corso  v.6.3MaX
     Using radial grid of  929 points,  2 beta functions with: 
                l(1) =   0
                l(2) =   0
     Q(r) pseudized with 0 coefficients 


     atomic species   valence    mass     pseudopotential
     Al                3.00    26.98154     Al( 1.00)
     H                 1.00     1.00794     H ( 1.00)

     12 Sym. Ops., with inversion, found



   Cartesian axes
[preston@preston-System-Product-Name h-al111-adsorption]$
```

这里依次能找到版本、4 个进程、5 个原子、2 种元素、11 个价电子、截断、电子与离子阈值，再往下是实空间/倒空间晶格、两份赝势及其价电子数，最后列出含反演的对称操作。Al 的 3 个价电子乘 3，再加两个 H 的各 1 个价电子，正好得到 11。`ibrav=0` 的提示也保留在输出中；本例显式给出表面与真空的晶胞，核对的是实际三根矢量及坐标。

优化过程会重复“电子自洽 → 力和应力 → BFGS 原子移动”。本次洁净薄膜经历 9 个 BFGS 步，吸附态 10 个，H₂ 3 个。洁净薄膜最初一轮有一条 `c_bands` 本征值提示，原文件保留；最终电子迭代已收敛，三者的末轮没有该提示。下面保留吸附态最后一段，从力开始一直看到最终坐标、保存文件、计时与程序结束：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ tail -n 105 adsorbed/relax.out
     hartree contribution      =      81.01062593 Ry
     xc contribution           =      -9.03973814 Ry
     ewald contribution        =      68.96869711 Ry

     convergence has been achieved in   6 iterations

     negative rho (up, down):  3.035E-06 0.000E+00

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000   -0.00000000    0.00000307
     atom    2 type  1   force =     0.00000000    0.00000000    0.00000000
     atom    3 type  1   force =    -0.00000000    0.00000000   -0.00000307
     atom    4 type  2   force =     0.00000000    0.00000000    0.00004639
     atom    5 type  2   force =     0.00000000    0.00000000   -0.00004639

     Total force =     0.000066     Total SCF correction =     0.000004


     Computing stress (Cartesian axis) and pressure


     negative rho (up, down):  3.035E-06 0.000E+00
          total   stress  (Ry/bohr**3)                   (kbar)     P=        0.96
   0.00001020   0.00000000  -0.00000000            1.50        0.00       -0.00
   0.00000000   0.00001020   0.00000000            0.00        1.50        0.00
  -0.00000000   0.00000000  -0.00000079           -0.00        0.00       -0.12

     Energy error            =      8.2E-07 Ry
     Gradient error          =      4.6E-05 Ry/Bohr

     bfgs converged in  11 scf cycles and  10 bfgs steps
     (criteria: energy <  1.0E-05 Ry, force <  2.0E-04 Ry/Bohr)

     End of BFGS Geometry Optimization

     Final energy             =     -17.3494214515 Ry

     File ./tmp/adsorbed.bfgs deleted, as requested
Begin final coordinates

ATOMIC_POSITIONS (angstrom)
Al               2.8586989056        1.6504705827        9.0674092364
Al               0.0000000000        0.0000000000       11.4341178823    0   0   0
Al               1.4293494528        0.8252352913       13.8008265283
H                2.8586989056        1.6504705827        7.4610322504
H                1.4293494528        0.8252352913       15.4072035143
End final coordinates



     Writing all to output data dir ./tmp/adsorbed.save/ :
     XML data file, charge density, pseudopotentials, collected wavefunctions

     init_run     :      1.47s CPU      1.63s WALL (       1 calls)
     electrons    :    141.84s CPU    159.60s WALL (      11 calls)
     update_pot   :      1.47s CPU      1.60s WALL (      10 calls)
     forces       :     10.30s CPU     11.46s WALL (      11 calls)
     stress       :     41.59s CPU     44.70s WALL (      11 calls)

     Called by init_run:
     wfcinit      :      0.31s CPU      0.32s WALL (       1 calls)
     potinit      :      0.28s CPU      0.32s WALL (       1 calls)
     hinit0       :      0.45s CPU      0.46s WALL (       1 calls)

     Called by electrons:
     c_bands      :     57.35s CPU     58.65s WALL (      84 calls)
     sum_band     :     45.33s CPU     54.30s WALL (      84 calls)
     v_of_rho     :     10.43s CPU     10.91s WALL (      89 calls)
     newd         :     31.70s CPU     39.51s WALL (      89 calls)
     mix_rho      :      1.11s CPU      1.17s WALL (      84 calls)

     Called by c_bands:
     init_us_2    :      1.56s CPU      1.59s WALL (    1337 calls)
     cegterg      :     53.94s CPU     55.23s WALL (     588 calls)

     Called by *egterg:
     cdiaghg      :      0.38s CPU      0.38s WALL (    1901 calls)
     h_psi        :     38.59s CPU     39.81s WALL (    2020 calls)
     s_psi        :      6.02s CPU      6.04s WALL (    2020 calls)
     g_psi        :      0.11s CPU      0.11s WALL (    1425 calls)

     Called by h_psi:
     h_psi:calbec :      6.08s CPU      6.15s WALL (    2020 calls)
     vloc_psi     :     26.53s CPU     27.67s WALL (    2020 calls)
                                        0.00s GPU  (    2020 calls)
     add_vuspsi   :      5.85s CPU      5.86s WALL (    2020 calls)

     General routines
     calbec       :     14.02s CPU     14.15s WALL (    3917 calls)
     fft          :     11.00s CPU     11.69s WALL (    1426 calls)
     ffts         :      0.34s CPU      0.35s WALL (     173 calls)
     fftw         :     28.79s CPU     29.99s WALL (   40240 calls)
     interpolate  :      0.85s CPU      0.90s WALL (      89 calls)

     Parallel routines

     PWSCF        :   3m20.67s CPU   3m43.90s WALL


   This run was terminated on:  23:58:26  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name h-al111-adsorption]$
```

吸附态打印 `Gradient error=4.6e-5 Ry/Bohr`，小于 `2e-4`；`Energy error=8.2e-7 Ry`，也小于 `1e-5`。两个条件与 `bfgs converged` 同时出现，才支持这一次几何优化已经达到设定停止条件。中层的 `0 0 0` 在最终坐标中仍然可见。XML 中的最终最大力分量和 OUT 相符：

| 结构 | 最终最大 \|Fᵢ\| / Ry·Bohr⁻¹ | 原生运行时间 / s |
| --- | --- | --- |
| clean-slab | 0.00000523 | 188.19 |
| adsorbed | 0.00004639 | 223.90 |
| h2-10A | 0.00000424 | 30.55 |

输出还保留了约 `3×10⁻⁶` 量级的 `negative rho` 行。本次没有额外扫描电荷密度截断，不能用 BFGS 停止条件代替这项数值检查。应力表中的压力则包含任意选定的真空体积；这是固定晶胞的表面优化，不以这一三维压力等于零作为吸附结构的验收条件。

最终 H₂ 键长为 `0.75034816 Å`，吸附态顶面 H 到其正下方 Al 的垂直距离为 `1.60637699 Å`。下面的图直接读取最终 XML 坐标，显示沿 y 方向的投影；各面板分别使用自己的真实晶胞高度，球的大小只用来区分元素。

![优化后的三个结构](/Atlas/examples/h-al111-adsorption/plots/structures.svg)

取能量时三者都使用 QE 的 `! total energy`。它包含当前冷展宽下的 `F=E−TS` 数值约定；不能从某份输出改取 `internal energy`，再与另两份的 `F` 相减。本次 H₂ 的占据已接近整数，但仍使用同一项读取。按“每一个吸附 H”归一化：

```text
Eads (eV/H) = [E(Al3H2) − E(Al3) − E(H2)] × 13.605693122994 / 2
```

除以 2 是因为整个晶胞里吸附了两个 H，分居上下两面。这里不是再额外按两个表面除一次，也不是把 H₂ 总能当成一个 H 的参考能。把三份最终值代入：

```text
[(-17.3494214515) − (-15.0701501110) − (-2.3332211394)] Ry
× 13.605693122994 eV/Ry ÷ 2 = 0.36701220 eV/H
```

这个定义下负值表示相对“洁净薄膜 + 气相 H₂”降低了电子能量，正值表示提高。本次 6×6×1 协议给出正值：在这组指定模型和参考态下，这个解离吸附构型并不放热。它没有给出 H₂ 解离势垒，也没有证明 atop 是最低吸附位点；高对称点的力小，同样不能代替横向位移或振动稳定性检查。

三能差还可能对数值设置敏感，因此只改一项并成对重算。k 网格检查同时把洁净与吸附表面改到 8×8×1；真空检查同时增加两者晶胞高度 5 Å，并把原子整体平移到新胞中心。两种检查都固定刚才已优化的内部几何。H₂ 的检查只把盒长由 10 Å 改为 12 Å，保持键长不变。

| 目录组 | 只改变什么 | 继续使用的参考 |
| --- | --- | --- |
| clean-k8 / ads-k8 | 6×6×1 → 8×8×1 | h2-10A |
| clean-vac20 / ads-vac20 | c 增加 5 Å，原子 z 整体增加 2.5 Å | h2-10A |
| h2-12A | 10 Å → 12 Å 分子盒 | clean-slab 与 adsorbed |

例如吸附态的网格检查先复制优化输入，再在 vi 中写入最终原子坐标、改为静态 SCF 和新的 k 网格；完整实际文件是 [ads-k8/scf.in](/Atlas/examples/h-al111-adsorption/ads-k8/scf.in)，匹配的洁净表面文件是 [clean-k8/scf.in](/Atlas/examples/h-al111-adsorption/clean-k8/scf.in)。不能只提高吸附态的网格，却继续减去旧网格的洁净能量。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ cp adsorbed/relax.in ads-k8/scf.in
[preston@preston-System-Product-Name h-al111-adsorption]$
```

实际解析命令会同时核对元素个数、两个表面的同胞关系、PBE/自旋/截断/展宽、最终力、OUT 与 XML 的总能一致性，以及各组检查中内部几何是否保持不变：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ python3 analyse_adsorption.py
case           energy (Ry/cell)    max |F_i| (Ry/Bohr)
clean-slab         -15.0701501110           0.00000523
adsorbed           -17.3494214515           0.00004639
h2-10A              -2.3332211394           0.00000424
protocol       Eads (eV/H)    change (meV/H)
baseline-k6       0.36701220         0.000000
k8                0.38008429        13.072091
vacuum20          0.36701288         0.000675
H2-box12          0.36701462         0.002419
H2 bond length: 0.75034816 Angstrom
Top atop H height: 1.60637699 Angstrom
Comparison completed for the named finite model; untested model dimensions remain explicit.
[preston@preston-System-Product-Name h-al111-adsorption]$
```

| 协议 | Eads / eV·H⁻¹ | 相对基线变化 / meV·H⁻¹ |
| --- | --- | --- |
| baseline-k6 | 0.36701220 | +0.000000 |
| k8 | 0.38008429 | +13.072091 |
| vacuum20 | 0.36701288 | +0.000675 |
| H2-box12 | 0.36701462 | +0.002419 |

这次采用 `10 meV/H` 作为已测参数差值的教学比较线。这两个有限尺寸对照是在 6 网格几何和协议下得到的；真空和 H₂ 盒长变化很小，但 **6→8 的 k 网格变化为 13.072 meV/H，仍高于比较线**。因此，这组结果可以把完整三能差路线走通，不能称为吸附能已经达到 10 meV/H 数值收敛。8×8×1 的点又是固定旧几何的静态检查，也不能直接冒称其自身网格下重新优化后的最低能量。

力也必须一起看：把 6 网格优化坐标原样放进 8 网格后，洁净基底和吸附态的力都明显回升。下面的数值直接来自相应静态 OUT 和 XML：

| 结构 | 6 网格优化末次最大 \|Fᵢ\| | 8 网格固定坐标最大 \|Fᵢ\|（Ry/Bohr） |
| --- | --- | --- |
| 洁净基底 | 0.00000523 | 0.01342680 |
| 吸附态 | 0.00004639 | 0.00196471 |

因此，几何停止条件通过这一结论只适用于 6 网格协议。到这一步，还没有得到经 k 网格与力一致性检验的吸附能。后面继续在更密的表面采样下重新优化洁净与吸附结构，再用新的配对静态结果检查；8 网格的静态能量本身不代表已经完成了新优化。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ python3 plot_adsorption.py
plots/structures.png and plots/structures.svg
plots/adsorption-checks.png and plots/adsorption-checks.svg
[preston@preston-System-Product-Name h-al111-adsorption]$
```

![吸附能与三项参数对照](/Atlas/examples/h-al111-adsorption/plots/adsorption-checks.svg)

左图保持统一的气相参考定义，右图单独显示各项相对基线的变化。横轴上的真空数值指初始设置；原子优化后实际的跨周期 H 层间空隙略有改变。原始每项能量、最大力和输入输出 SHA 在 [energy-table.csv](/Atlas/examples/h-al111-adsorption/energy-table.csv)，三能差与参数变化在 [adsorption-energy.csv](/Atlas/examples/h-al111-adsorption/adsorption-energy.csv)。

要在本机重画，把 [plot_adsorption.py](/Atlas/examples/h-al111-adsorption/plot_adsorption.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/h-al111-adsorption/atlas_plot_style.py)）、[structures.json](/Atlas/examples/h-al111-adsorption/structures.json) 和 [adsorption-energy.csv](/Atlas/examples/h-al111-adsorption/adsorption-energy.csv) 放到同一目录，运行 `python3 plot_adsorption.py`。需要 Python、NumPy 和 Matplotlib；程序同时生成两幅 PNG 与 SVG。重新从原始输入输出提取，则使用 [analyse_adsorption.py](/Atlas/examples/h-al111-adsorption/analyse_adsorption.py)，并保留对应目录里的 XML 与审计文件。

能量差和力一起回看后，接下来把洁净与吸附表面同时改到 12×12×1，重新做内部优化。起点使用各自 6 网格优化的最终坐标，晶胞、赝势、截断、展宽和中层约束全部保留。实际输入差别可以直接用 diff 核对：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ diff -u adsorbed/relax.in ads-k12-relax/relax.in
--- adsorbed/relax.in   2026-09-22 23:53:26.685280406 +0800
+++ ads-k12-relax/relax.in      2026-09-23 00:12:58.446358201 +0800
@@ -1,6 +1,6 @@
 &CONTROL
  calculation='relax'
- prefix='adsorbed'
+ prefix='ads-k12-relax'
  outdir='./tmp'
  pseudo_dir='../pseudo'
  tstress=.true.
@@ -34,10 +34,10 @@
 1.429349452815 2.475705874046 0.000000000000
 0.000000000000 0.000000000000 22.868235764697
 ATOMIC_POSITIONS angstrom
-Al 2.858698905630 1.650470582697 9.100000000000 1 1 1
+Al 2.858698905630 1.650470582697 9.067409236443 1 1 1
 Al 0.000000000000 0.000000000000 11.434117882349 0 0 0
-Al 1.429349452815 0.825235291349 13.768235764697 1 1 1
-H 2.858698905630 1.650470582697 7.500000000000 1 1 1
-H 1.429349452815 0.825235291349 15.368235764697 1 1 1
+Al 1.429349452815 0.825235291349 13.800826528254 1 1 1
+H 2.858698905630 1.650470582697 7.461032250364 1 1 1
+H 1.429349452815 0.825235291349 15.407203514333 1 1 1
 K_POINTS automatic
-6 6 1 0 0 0
+12 12 1 0 0 0
[preston@preston-System-Product-Name h-al111-adsorption]$
```

两份优化每项改用 8 个 MPI 进程，任务和文件仍分别保存。完整的 [clean-k12-relax/relax.in](/Atlas/examples/h-al111-adsorption/clean-k12-relax/relax.in)、[ads-k12-relax/relax.in](/Atlas/examples/h-al111-adsorption/ads-k12-relax/relax.in) 与 [ads-k12-relax/run.sh](/Atlas/examples/h-al111-adsorption/ads-k12-relax/run.sh) 可下载；实际提交后的结束证据为：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ grep -n -E 'bfgs converged|Final energy|Total force|PWSCF|JOB DONE' clean-k12-relax/relax.out
2:     Program PWSCF v.7.5 starts on 23Sep2026 at  0:12:53 
20:     Current dimensions of program PWSCF are:
368:     Total force =     0.012415     Total SCF correction =     0.000013
607:     Total force =     0.011977     Total SCF correction =     0.000003
849:     Total force =     0.011506     Total SCF correction =     0.000006
1089:     Total force =     0.010809     Total SCF correction =     0.000009
1329:     Total force =     0.009763     Total SCF correction =     0.000009
1569:     Total force =     0.008107     Total SCF correction =     0.000007
1820:     Total force =     0.005151     Total SCF correction =     0.000015
2083:     Total force =     0.001113     Total SCF correction =     0.000001
2334:     Total force =     0.000193     Total SCF correction =     0.000001
2349:     bfgs converged in   9 scf cycles and   8 bfgs steps
2354:     Final energy             =     -15.0668099856 Ry
2413:     PWSCF        :   2m17.71s CPU   2m30.90s WALL
2419:   JOB DONE.
[preston@preston-System-Product-Name h-al111-adsorption]$
```

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ grep -n -E 'bfgs converged|Final energy|Total force|PWSCF|JOB DONE' ads-k12-relax/relax.out
2:     Program PWSCF v.7.5 starts on 23Sep2026 at  0:13: 9 
20:     Current dimensions of program PWSCF are:
402:     Total force =     0.005613     Total SCF correction =     0.000011
640:     Total force =     0.004087     Total SCF correction =     0.000014
890:     Total force =     0.003322     Total SCF correction =     0.000002
1134:     Total force =     0.003489     Total SCF correction =     0.000001
1378:     Total force =     0.004719     Total SCF correction =     0.000005
1633:     Total force =     0.006398     Total SCF correction =     0.000002
1888:     Total force =     0.007705     Total SCF correction =     0.000001
2132:     Total force =     0.006757     Total SCF correction =     0.000004
2376:     Total force =     0.003147     Total SCF correction =     0.000001
2615:     Total force =     0.000327     Total SCF correction =     0.000005
2865:     Total force =     0.000013     Total SCF correction =     0.000003
2881:     bfgs converged in  11 scf cycles and  10 bfgs steps
2886:     Final energy             =     -17.3463548537 Ry
2947:     PWSCF        :   2m59.42s CPU   3m15.38s WALL
2953:   JOB DONE.
[preston@preston-System-Product-Name h-al111-adsorption]$
```

| 12 网格优化 | 最终最大 \|Fᵢ\| / Ry·Bohr⁻¹ | 原生运行时间 / s |
| --- | --- | --- |
| clean-k12-relax | 0.00013632 | 150.90 |
| ads-k12-relax | 0.00000845 | 195.38 |

两份结构都达到了本次 BFGS 条件。然后把这组新坐标分别写进 16×16×1 的静态输入；它们与各自 12 网格父结构的晶胞、原子顺序和坐标逐项相同。这一轮才是在同一组更密网格优化几何上检验 12→16。输入为 [clean-k16/scf.in](/Atlas/examples/h-al111-adsorption/clean-k16/scf.in) 与 [ads-k16/scf.in](/Atlas/examples/h-al111-adsorption/ads-k16/scf.in)。原始力行没有因电子收敛而变成零：

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ grep -n 'force =' clean-k16/scf.out
427:     atom    1 type  1   force =     0.00000000    0.00000000   -0.00252060
428:     atom    2 type  1   force =     0.00000000    0.00000000    0.00000000
429:     atom    3 type  1   force =     0.00000000   -0.00000000    0.00252060
431:     Total force =     0.003565     Total SCF correction =     0.000002
[preston@preston-System-Product-Name h-al111-adsorption]$
```

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ grep -n 'force =' ads-k16/scf.out
460:     atom    1 type  1   force =    -0.00000000    0.00000000   -0.00166686
461:     atom    2 type  1   force =    -0.00000000   -0.00000000    0.00000000
462:     atom    3 type  1   force =     0.00000000    0.00000000    0.00166686
463:     atom    4 type  2   force =     0.00000000    0.00000000    0.00035340
464:     atom    5 type  2   force =     0.00000000    0.00000000   -0.00035340
466:     Total force =     0.002410     Total SCF correction =     0.000001
[preston@preston-System-Product-Name h-al111-adsorption]$
```

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ python3 analyse_refinement.py
k12-relaxed   Eads = 0.36515144 eV/H
k16-fixed     Eads = 0.37050785 eV/H
k12 -> k16 fixed-geometry energy change: +5.356413 meV/H
clean-k16  max|F|=0.00252060 Ry/Bohr; max force change=0.00265692 Ry/Bohr
ads-k16    max|F|=0.00166686 Ry/Bohr; max force change=0.00166271 Ry/Bohr
Named energy comparison: True
Named energy and force comparisons: False
[preston@preston-System-Product-Name h-al111-adsorption]$
```

这次 12 网格优化后的吸附能为 `+0.36515144 eV/H`，16 网格同几何静态值为 `+0.37050785 eV/H`，变化 `5.356413 meV/H`，已经低于所设的 10 meV/H 能量差线。可是洁净与吸附表面的 16 网格最大力仍分别为 `0.00252060`、`0.00166686 Ry/Bohr`，约为力停止阈值的 12.6 倍和 8.3 倍。相减得到的能量看似稳定，并没有让每个结构的受力也稳定。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ python3 plot_refinement.py
plots/k12-k16-refinement.png and plots/k12-k16-refinement.svg
[preston@preston-System-Product-Name h-al111-adsorption]$
```

![12到16网格的能量和力检查](/Atlas/examples/h-al111-adsorption/plots/k12-k16-refinement.svg)

所以这一轮的结论是：**已测能量差比较通过，力一致性未通过，吸附能不能获得整体数值验收。** 这不是程序崩溃或输入对应错误；末轮电子收敛和同源几何都已核验，失败发生在把采样加密之后对同一结构的力检查上。当前两个正值可用于复算这条路线，不能作为已完成数值收敛的材料吸附能。

新增原始数值和 SHA 在 [refined-energy-table.csv](/Atlas/examples/h-al111-adsorption/refined-energy-table.csv)，配对三能差在 [refined-adsorption-energy.csv](/Atlas/examples/h-al111-adsorption/refined-adsorption-energy.csv)，力对照在 [refined-force-check.csv](/Atlas/examples/h-al111-adsorption/refined-force-check.csv)。重做这一段解析用 [analyse_refinement.py](/Atlas/examples/h-al111-adsorption/analyse_refinement.py)；重画图只需 [plot_refinement.py](/Atlas/examples/h-al111-adsorption/plot_refinement.py) 与后两份 CSV，并运行 `python3 plot_refinement.py`。它会同时写出 PNG 与 SVG。

继续计算的条件也因此明确：先在更密表面采样下获得力稳定的洁净与吸附几何，再用更严格的匹配采样同时复核能量差与自由原子力；不能只选一项数值较好看的结果作为通过。完成采样检查后，还需要比较薄膜层数、覆盖度和其它吸附位点；本例没有把这几项压缩成一个“可靠吸附能”的标签。参数对照可接 [收敛测试](/Atlas/m/convergence/qe/)；若要研究 H₂ 如何到达吸附态，需另外建立初态、终态和中间构型，进行 NEB 势垒计算。在加入振动零点能与温度项前，这里讨论的仍是上述非磁性 PBE 模型的电子能量差。

```text
同一表面晶胞 → 洁净基底优化 ─┐
               吸附态优化 ──┼→ 核对力与能量定义 → 三能差 / 2
独立分子盒 → H2 优化 ──────┘                         ↓
                                          成对 k 网格 / 真空 / 分子盒检查
                                                     ↓
                                           当前数值边界与下一项证据
```
