把两个 H 放到 Al 表面，程序会给出一个新的总能。但吸附态比洁净表面多了两个原子，两个 OUT 的总能直接相减还没有说明 H 从哪里来。这里选气相 H₂ 作为来源：一分子 H₂ 提供两个 H，分别放到薄膜上下表面的 Al 顶位。要计算的反应是 `洁净 Al 薄膜 + H₂ → 两面各吸附一个 H 的 Al 薄膜`。

这次使用三个明确的结构：三层 Al(111) 洁净薄膜、同一薄膜上增加两个 H 的吸附态，以及独立盒子中的 H₂。每个表面原胞含一个 Al，表面每胞再放一个 H，所以**每一面都是 1 ML 覆盖度**。这是一个三层、指定 atop 位点的例子；三个目录始终一起核对。

[QE：pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE：结构优化](https://www.quantum-espresso.org/Doc/pw_user_guide/node11.html) · [ASE：表面与吸附体建模](https://wiki.fysik.dtu.dk/ase/ase/build/surface.html)

本页的[完整计算文件包](/Atlas/examples/h-al111-adsorption-files.tar.gz)包含 13 项实际计算的输入、OUT、XML、逐项核对记录和绘图脚本。解压后保留目录层级；运行脚本里的 `<qe_bin>` 需改为本机 QE 的程序目录。包内没有保存波函数或电荷密度，图表可直接从 OUT、XML 和 CSV 重建，重新做电子计算则从所附输入开始。

## 准备洁净表面、吸附态与 H₂

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

## 写入结构与优化条件

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

## 提交优化并读出最终结构

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

最终吸附态和分子参考的关键几何量列于下表；原子坐标可从 [structures.json](/Atlas/examples/h-al111-adsorption/structures.json)复核。

| 对象 | 模型与最终几何 |
| --- | --- |
| 吸附模型 | 3 个 Al 的周期 Al(111) 薄膜；上下两面各放置 1 个 H，组成对称的两 H 顶位构型 |
| 分子参考 | 独立 H₂，初始分子盒边长 10 Å；最终 H–H 键长 0.75034816 Å |
| 顶位几何 | 上表面 H 到其正下方 Al 的垂直距离为 1.60637699 Å |

坐标数据见 [structures.json](/Atlas/examples/h-al111-adsorption/structures.json)；各协议的输入、输出摘要和哈希见 [energy-table.csv](/Atlas/examples/h-al111-adsorption/energy-table.csv)。

## 用三能差计算每个 H 的吸附能

取能量时三者都使用 QE 的 `! total energy`。它包含当前冷展宽下的 `F=E−TS` 数值约定；不能从某份输出改取 `internal energy`，再与另两份的 `F` 相减。本次 H₂ 的占据已接近整数，但仍使用同一项读取。按“每一个吸附 H”归一化：

```text
Eads (eV/H) = [E(Al3H2) − E(Al3) − E(H2)] × 13.605693122994 / 2
```

因晶胞内吸附了两个 H，能量差按两个 H 归一化，得到每个 H 的值；气相参考取一整个 H₂ 分子的总能。将三份最终值代入：

```text
[(-17.3494214515) − (-15.0701501110) − (-2.3332211394)] Ry
× 13.605693122994 eV/Ry ÷ 2 = 0.36701220 eV/H
```

这个定义下负值表示相对“洁净薄膜 + 气相 H₂”降低了电子能量，正值表示提高。本次 6×6×1 协议给出正值：在这组指定模型和参考态下，这个解离吸附构型并不放热。它没有给出 H₂ 解离势垒，也没有证明 atop 是最低吸附位点；高对称点的力小，同样不能代替横向位移或振动稳定性检查。

## 成对检查网格、真空和分子盒

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

从原始输出运行 `analyse_adsorption.py` 和后面的 `analyse_refinement.py` 需要 Python 3 与 NumPy；后面的独立表格复核器 `review_al111_adsorption.py` 读取已提取的 CSV，只用 Python 标准库。

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

[独立表格复核脚本](/Atlas/examples/thermo-postprocessing/adsorption/review_al111_adsorption.py) 读取 [energy-table.csv](/Atlas/examples/thermo-postprocessing/adsorption/energy-table.csv)、[adsorption-energy.csv](/Atlas/examples/thermo-postprocessing/adsorption/adsorption-energy.csv)、[refined-energy-table.csv](/Atlas/examples/thermo-postprocessing/adsorption/refined-energy-table.csv)、[refined-adsorption-energy.csv](/Atlas/examples/thermo-postprocessing/adsorption/refined-adsorption-energy.csv) 与 [refined-force-check.csv](/Atlas/examples/thermo-postprocessing/adsorption/refined-force-check.csv)，按每组洁净表面、吸附态和 H₂ 的配对关系重算三能差，并单独检查力阈值。将上述五份 CSV 与脚本放在同一目录，按下方完整源码后的命令运行；脚本只使用 Python 标准库。

输出包括 [协议对照 CSV](/Atlas/examples/thermo-postprocessing/adsorption/review/al111-h-adsorption-review.csv)、[力对照 CSV](/Atlas/examples/thermo-postprocessing/adsorption/review/al111-h-refined-force-review.csv) 和 [文字报告](/Atlas/examples/thermo-postprocessing/adsorption/review/al111-h-adsorption-review.md)。下表列出前三项参数对照：

| 参数变化 | Eads (eV/H) | 相对 k6 (meV/H) | 本例 10 meV/H 比较线 |
| --- | ---: | ---: | --- |
| 6×6×1 → 8×8×1 | 0.38008429 | +13.072091 | 超出 |
| 晶胞高度 c 增加 5 Å | 0.36701288 | +0.000675 | 线内 |
| H₂ 盒长 10 → 12 Å | 0.36701462 | +0.002419 | 线内 |

## 在更密网格优化后，分别检查能量与力

进一步将洁净与吸附表面同时改到 12×12×1，重新做内部优化。起点使用各自 6 网格优化的最终坐标，晶胞、赝势、截断、展宽和中层约束全部保留。实际输入差别可以直接用 diff 核对：

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

两份结构都达到了本次 BFGS 条件。把各自的新坐标写进 16×16×1 静态输入，并保持晶胞、原子顺序和坐标与对应的 12 网格父结构相同，就能在固定几何下比较 12→16 的能量与力。输入为 [clean-k16/scf.in](/Atlas/examples/h-al111-adsorption/clean-k16/scf.in) 与 [ads-k16/scf.in](/Atlas/examples/h-al111-adsorption/ads-k16/scf.in)。下面读取 16 网格静态计算的力，判断这些坐标在更密网格下是否仍满足力阈值：

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

| 比较 | Eads k12 (eV/H) | Eads k16 (eV/H) | Δ (meV/H) | 洁净表面 Fmax k16 (Ry/Bohr) | 吸附表面 Fmax k16 (Ry/Bohr) | 2×10⁻⁴ 力线 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| k12-relaxed → k16-fixed | 0.36515144 | 0.37050785 | +5.356413 | 0.00252060 | 0.00166686 | 两者均超出 |

这轮能量与力的联合检查未通过：能量差位于本例 10 meV/H 比较线内，洁净与吸附表面的 16 网格最大力分别约为所设力阈值的 12.6 倍和 8.3 倍。

原始数值和 SHA 在 [refined-energy-table.csv](/Atlas/examples/h-al111-adsorption/refined-energy-table.csv)，配对三能差在 [refined-adsorption-energy.csv](/Atlas/examples/h-al111-adsorption/refined-adsorption-energy.csv)，力对照在 [refined-force-check.csv](/Atlas/examples/h-al111-adsorption/refined-force-check.csv)。表格复核结果另见[汇总报告](/Atlas/examples/thermo-postprocessing/adsorption/review/al111-h-adsorption-review.md)与[逐结构力对照](/Atlas/examples/thermo-postprocessing/adsorption/review/al111-h-refined-force-review.csv)；原始提取脚本为 [analyse_refinement.py](/Atlas/examples/h-al111-adsorption/analyse_refinement.py)。

<details>
<summary>analyse_refinement.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from pathlib import Path
import json,numpy as np
from analyse_adsorption import read_run,save_csv,RY_EV
ROOT=Path(__file__).resolve().parent
def main():
    names={'clean-k12-relax':'relax','ads-k12-relax':'relax','clean-k16':'scf','ads-k16':'scf','h2-10A':'relax'}
    runs={n:read_run(n,stem) for n,stem in names.items()}
    for clean,ads in [('clean-k12-relax','ads-k12-relax'),('clean-k16','ads-k16')]:
        assert np.allclose(runs[clean][1]['cell_A'],runs[ads][1]['cell_A'],atol=1e-10,rtol=0)
    forces=[]
    for child,parent in [('clean-k16','clean-k12-relax'),('ads-k16','ads-k12-relax')]:
        cg=runs[child][1];pg=runs[parent][1]
        assert cg['symbols']==pg['symbols']
        assert np.allclose(cg['cell_A'],pg['cell_A'],atol=1e-10,rtol=0)
        assert np.allclose(cg['positions_A'],pg['positions_A'],atol=1e-10,rtol=0)
        delta=float(np.abs(np.array(cg['forces_Ry_Bohr'])-np.array(pg['forces_Ry_Bohr'])).max())
        force16=runs[child][0]['max_force_component_Ry_Bohr']
        forces.append(dict(case=child,parent=parent,max_force_k12_Ry_Bohr=runs[parent][0]['max_force_component_Ry_Bohr'],max_force_k16_Ry_Bohr=force16,max_force_change_Ry_Bohr=delta,k16_within_2e4=force16<=2e-4,change_within_2e4=delta<=2e-4))
    gas=runs['h2-10A'][0]['total_energy_Ry'];energies=[]
    for label,clean,ads in [('k12-relaxed','clean-k12-relax','ads-k12-relax'),('k16-fixed','clean-k16','ads-k16')]:
        rc=runs[clean][0];ra=runs[ads][0]
        assert (rc['nAl'],rc['nH'],ra['nAl'],ra['nH'])==(3,0,3,2)
        e=(ra['total_energy_Ry']-rc['total_energy_Ry']-gas)*RY_EV/2
        energies.append(dict(protocol=label,clean_case=clean,adsorbed_case=ads,gas_case='h2-10A',clean_energy_Ry=rc['total_energy_Ry'],adsorbed_energy_Ry=ra['total_energy_Ry'],h2_energy_Ry=gas,adsorption_eV_H=e))
    delta=(energies[1]['adsorption_eV_H']-energies[0]['adsorption_eV_H'])*1000
    save_csv('refined-energy-table.csv',[r[0] for r in runs.values()])
    save_csv('refined-adsorption-energy.csv',energies);save_csv('refined-force-check.csv',forces)
    (ROOT/'refined-structures.json').write_text(json.dumps({k:v[1] for k,v in runs.items()},indent=2)+'\n')
    result={'scientific_acceptance':'not_assessed','scope':'Two meshes on the k12-relaxed, nonmagnetic three-layer one-ML atop model; does not establish a complete converged series or all physical/model dimensions','energy_change_meV_H':delta,'energy_comparison_within_10meV_H':abs(delta)<=10,'force_checks':forces,'both_energy_and_force_comparisons_pass':abs(delta)<=10 and all(f['k16_within_2e4'] and f['change_within_2e4'] for f in forces),'energies':energies,'runs':[v[0] for v in runs.values()]}
    (ROOT/'evidence/refined-analysis-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in energies:print(f"{r['protocol']:<13} Eads = {r['adsorption_eV_H']:.8f} eV/H")
    print(f'k12 -> k16 fixed-geometry energy change: {delta:+.6f} meV/H')
    for f in forces:print(f"{f['case']:<10} max|F|={f['max_force_k16_Ry_Bohr']:.8f} Ry/Bohr; max force change={f['max_force_change_Ry_Bohr']:.8f} Ry/Bohr")
    print('Named energy comparison:',result['energy_comparison_within_10meV_H'])
    print('Named energy and force comparisons:',result['both_energy_and_force_comparisons_pass'])
if __name__=='__main__':main()
```

</details>

## 编写三能差与力检查脚本

从原始输出提取能量后，表格后处理要保持每组洁净表面、吸附态和 H₂ 的配对关系。先按两颗 H 归一化，再比较不同协议的能量差；力检查另列两种表面的最大力。这能避免把能量差在线内误读为更密网格下的几何也已通过检查。

~~~text
编写 review_al111_adsorption.py，仅使用 Python 标准库。读取 energy-table.csv、adsorption-energy.csv、refined-energy-table.csv、refined-adsorption-energy.csv、refined-force-check.csv，保留输入。按协议对应的 clean、ads、H2 case 读取 total_energy_Ry，使用 [Eadsorbed-Eclean-EH2]*13.605693122994/2 计算 eV/H，并核对原表。输出 k6、k8、vacuum20、H2-box12 相对 k6 的 meV/H 差，以及 k12-relaxed 到 k16-fixed 的变化。缺少配对项、重复 case、非有限数或重算不一致时停止，报告行与字段。
单独核对 clean-k16 与 ads-k16 的最大力和 refined-force-check.csv，沿用 2e-4 Ry/Bohr 力阈值与 10 meV/H 能量比较线；k16 是 k12 优化几何上的静态计算。支持 --outdir，写出 al111-h-adsorption-review.csv、al111-h-refined-force-review.csv、al111-h-adsorption-review.md。报告 k6→k8 的 13.072091 meV/H、k12→k16 的 5.356413 meV/H 和两结构的力判断。不要绘图；正值解释为相对洁净薄膜+气相 H2 的电子能量升高。
~~~

完整源码如下，与上面的下载文件相同。保存为 `review_al111_adsorption.py`，与前面列出的五份 CSV 放在同一目录；运行命令见源码后。

<details>
<summary>review_al111_adsorption.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Recompute the finite Al(111)-H adsorption checks as audit tables."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

RY_TO_EV = 13.605693122994
FORCE_LIMIT_RY_BOHR = 2e-4
ENERGY_LIMIT_EV_H = 0.010
ROOT = Path(__file__).resolve().parent


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing CSV header")
        return list(reader)


def unique_by(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "")
        if not value or value in out:
            raise ValueError(f"{label}: empty or duplicate {key} {value!r}")
        out[value] = row
    return out


def close(a: float, b: float, label: str, atol: float = 1e-10) -> None:
    if not math.isfinite(a) or not math.isclose(a, b, rel_tol=0, abs_tol=atol):
        raise ValueError(f"{label}: values disagree ({a:.12g} vs {b:.12g})")


def adsorption_eV_H(
    raw: dict[str, dict[str, str]], clean_case: str, ads_case: str, gas_case: str, label: str
) -> tuple[float, dict[str, dict[str, str]]]:
    try:
        clean, ads, gas = raw[clean_case], raw[ads_case], raw[gas_case]
    except KeyError as exc:
        raise ValueError(f"{label}: missing raw case {exc.args[0]!r}") from exc
    if (int(clean["nAl"]), int(clean["nH"])) != (3, 0):
        raise ValueError(f"{label}: clean reference is not the three-Al slab")
    if (int(ads["nAl"]), int(ads["nH"])) != (3, 2):
        raise ValueError(f"{label}: adsorbed reference is not Al3H2")
    if (int(gas["nAl"]), int(gas["nH"])) != (0, 2):
        raise ValueError(f"{label}: gas reference is not H2")
    value = (
        float(ads["total_energy_Ry"])
        - float(clean["total_energy_Ry"])
        - float(gas["total_energy_Ry"])
    ) * RY_TO_EV / 2
    return value, {"clean": clean, "ads": ads, "gas": gas}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "review")
    args = parser.parse_args()
    outdir = args.outdir if args.outdir.is_absolute() else ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    base_raw = unique_by(read_rows(ROOT / "energy-table.csv"), "case", "baseline raw table")
    refined_raw = unique_by(read_rows(ROOT / "refined-energy-table.csv"), "case", "refined raw table")
    summary = read_rows(ROOT / "adsorption-energy.csv")
    summary_by_protocol = unique_by(summary, "protocol", "baseline summary")
    required_protocols = {"baseline-k6", "k8", "vacuum20", "H2-box12"}
    if set(summary_by_protocol) != required_protocols:
        raise ValueError(f"baseline summary protocols differ: {sorted(summary_by_protocol)}")

    baseline_values: dict[str, float] = {}
    baseline_table: list[dict[str, str]] = []
    for protocol in ("baseline-k6", "k8", "vacuum20", "H2-box12"):
        row = summary_by_protocol[protocol]
        value, matched = adsorption_eV_H(
            base_raw, row["clean_case"], row["adsorbed_case"], row["gas_case"], protocol
        )
        close(value, float(row["adsorption_eV_H"]), f"{protocol} summary Eads")
        baseline_values[protocol] = value
        close((value - baseline_values["baseline-k6"]) * 1000, float(row["change_from_baseline_meV_H"]), f"{protocol} summary delta")
        baseline_table.append({
            "protocol": protocol,
            "clean_case": row["clean_case"],
            "adsorbed_case": row["adsorbed_case"],
            "gas_case": row["gas_case"],
            "clean_stage": matched["clean"]["stage"],
            "adsorbed_stage": matched["ads"]["stage"],
            "gas_stage": matched["gas"]["stage"],
            "adsorption_eV_H": f"{value:.12f}",
            "delta_from_baseline_meV_H": f"{(value - baseline_values['baseline-k6']) * 1000:.9f}",
        })

    refined_summary = read_rows(ROOT / "refined-adsorption-energy.csv")
    refined_by_protocol = unique_by(refined_summary, "protocol", "refined summary")
    expected_refined = {"k12-relaxed", "k16-fixed"}
    if set(refined_by_protocol) != expected_refined:
        raise ValueError(f"refined protocols differ: {sorted(refined_by_protocol)}")
    refined_values: dict[str, float] = {}
    for protocol in ("k12-relaxed", "k16-fixed"):
        row = refined_by_protocol[protocol]
        value, matched = adsorption_eV_H(
            refined_raw, row["clean_case"], row["adsorbed_case"], row["gas_case"], protocol
        )
        close(value, float(row["adsorption_eV_H"]), f"{protocol} summary Eads")
        for name, raw_value in (
            ("clean_energy_Ry", matched["clean"]["total_energy_Ry"]),
            ("adsorbed_energy_Ry", matched["ads"]["total_energy_Ry"]),
            ("h2_energy_Ry", matched["gas"]["total_energy_Ry"]),
        ):
            close(float(row[name]), float(raw_value), f"{protocol} {name}")
        refined_values[protocol] = value

    delta_refined_meV = (refined_values["k16-fixed"] - refined_values["k12-relaxed"]) * 1000
    energy_status = (
        "within selected 10 meV/H line"
        if abs(delta_refined_meV) <= ENERGY_LIMIT_EV_H * 1000
        else "outside selected 10 meV/H line"
    )

    force_rows = unique_by(read_rows(ROOT / "refined-force-check.csv"), "case", "force summary")
    refined_table: list[dict[str, str]] = []
    for case, parent_case in (("clean-k16", "clean-k12-relax"), ("ads-k16", "ads-k12-relax")):
        expected = force_rows.get(case)
        if not expected:
            raise ValueError(f"force summary missing {case}")
        current, prior = refined_raw[case], refined_raw[parent_case]
        close(float(expected["max_force_k16_Ry_Bohr"]), float(current["max_force_component_Ry_Bohr"]), f"{case} force")
        close(float(expected["max_force_k12_Ry_Bohr"]), float(prior["max_force_component_Ry_Bohr"]), f"{case} parent force")
        force_k12 = float(prior["max_force_component_Ry_Bohr"])
        force_k16 = float(current["max_force_component_Ry_Bohr"])
        force_change = float(expected["max_force_change_Ry_Bohr"])
        if not math.isfinite(force_change) or force_change < 0:
            raise ValueError(f"{case}: invalid stored component-wise force change")
        k16_flag = expected["k16_within_2e4"].strip().lower() == "true"
        change_flag = expected["change_within_2e4"].strip().lower() == "true"
        if k16_flag != (force_k16 <= FORCE_LIMIT_RY_BOHR):
            raise ValueError(f"{case}: stored k16 force criterion disagrees with recomputed value")
        if change_flag != (force_change <= FORCE_LIMIT_RY_BOHR):
            raise ValueError(f"{case}: stored force-change criterion disagrees with recomputed value")
        refined_table.append({
            "case": case,
            "parent_case": parent_case,
            "k12_Eads_eV_H": f"{refined_values['k12-relaxed']:.12f}",
            "k16_fixed_Eads_eV_H": f"{refined_values['k16-fixed']:.12f}",
            "k12_to_k16_delta_meV_H": f"{delta_refined_meV:.9f}",
            "max_force_k12_Ry_Bohr": f"{force_k12:.12g}",
            "max_force_k16_Ry_Bohr": f"{force_k16:.12g}",
            "max_force_change_k12_to_k16_Ry_Bohr": f"{force_change:.12g}",
            "force_change_within_limit": str(force_change <= FORCE_LIMIT_RY_BOHR),
            "selected_force_limit_Ry_Bohr": f"{FORCE_LIMIT_RY_BOHR:.1e}",
            "k16_force_factor_over_limit": f"{force_k16 / FORCE_LIMIT_RY_BOHR:.6f}",
            "energy_delta_within_10_meV_H": str(abs(delta_refined_meV) <= ENERGY_LIMIT_EV_H * 1000),
            "k16_force_within_limit": str(force_k16 <= FORCE_LIMIT_RY_BOHR),
        })

    write_csv(outdir / "al111-h-adsorption-review.csv", list(baseline_table[0]), baseline_table)
    write_csv(outdir / "al111-h-refined-force-review.csv", list(refined_table[0]), refined_table)

    report = [
        "# Al(111)-H adsorption energy review",
        "",
        "- The stated observable is Eads = (E(Al3H2) - E(Al3) - E(H2)) × 13.605693122994 / 2 in eV per H.",
        "- Energies are read from the supplied Quantum ESPRESSO total_energy_Ry fields; the two adsorbed H atoms account for the divisor 2.",
        "- The 10 meV/H energy comparison and 2×10⁻⁴ Ry/Bohr force limit are the selected teaching thresholds for this case.",
        "- The 6→8 k-grid adsorption-energy change exceeds 10 meV/H; vacuum and H2-box changes are below it.",
        f"- The 12-relaxed→16-fixed energy difference is {delta_refined_meV:+.6f} meV/H ({energy_status}).",
        "- The 16-grid clean-slab and adsorbed-slab forces are checked separately; both exceed the selected force limit, so the combined energy-and-force acceptance is false.",
        "- Component-wise force changes come from the supplied refined-force-check.csv, generated from matched k12 and k16 force arrays; this script checks their reported threshold flags against the selected limit.",
        "- Scope is the supplied symmetric two-H atop model and its stated finite checks; this review makes no claim about other adsorption sites, coverage, slab thickness, barriers, or vibrational and thermal terms.",
        "",
        "## Finite protocol comparisons",
        "",
        "| protocol | clean / adsorbed / gas cases | Eads (eV/H) | change from k6 (meV/H) |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in baseline_table:
        report.append(
            f"| {row['protocol']} | {row['clean_case']} / {row['adsorbed_case']} / {row['gas_case']} | {float(row['adsorption_eV_H']):.8f} | {float(row['delta_from_baseline_meV_H']):+.6f} |"
        )
    report.extend([
        "",
        "## 12-grid relaxation to 16-grid fixed-geometry check",
        "",
        "| pair | Eads k12 (eV/H) | Eads k16 (eV/H) | Δ (meV/H) | Fmax clean k16 (Ry/Bohr) | Fmax ads k16 (Ry/Bohr) | force limit (Ry/Bohr) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| k12-relaxed → k16-fixed | {refined_values['k12-relaxed']:.8f} | {refined_values['k16-fixed']:.8f} | {delta_refined_meV:+.6f} | {float(refined_table[0]['max_force_k16_Ry_Bohr']):.8f} | {float(refined_table[1]['max_force_k16_Ry_Bohr']):.8f} | {FORCE_LIMIT_RY_BOHR:.1e} |",
        "",
        "The energy difference is within the selected 10 meV/H comparison line. The maximum forces are 12.60× and 8.33× the selected force limit, respectively; energy-only agreement therefore does not pass the combined check.",
    ])
    (outdir / "al111-h-adsorption-review.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"baseline_protocols={','.join(sorted(required_protocols))}")
    print(f"baseline_k6={baseline_values['baseline-k6']:.12f} eV/H")
    print(f"k8_change={(baseline_values['k8']-baseline_values['baseline-k6'])*1000:+.6f} meV/H")
    print(f"k12_to_k16_change={delta_refined_meV:+.6f} meV/H ({energy_status})")
    print(f"force_limit={FORCE_LIMIT_RY_BOHR:.1e} Ry/Bohr clean={float(refined_table[0]['max_force_k16_Ry_Bohr']):.8f} ads={float(refined_table[1]['max_force_k16_Ry_Bohr']):.8f}")
    print(f"wrote {outdir / 'al111-h-adsorption-review.csv'}")
    print(f"wrote {outdir / 'al111-h-refined-force-review.csv'}")
    print(f"wrote {outdir / 'al111-h-adsorption-review.md'}")


if __name__ == "__main__":
    main()
```

</details>

将本节前面链接的五份 CSV 和脚本放在同一目录后运行：

```bash
python3 review_al111_adsorption.py --outdir review
```

终端的关键结果为：

```text
baseline_k6=0.367012203736 eV/H
k8_change=+13.072091 meV/H
k12_to_k16_change=+5.356413 meV/H (within selected 10 meV/H line)
force_limit=2.0e-04 Ry/Bohr clean=0.00252060 ads=0.00166686
```

k6→k8 的能量变化超出比较线；k12→k16 的能量变化在线内，但两结构的最大力均超出力阈值。下一步应在 16×16×1 网格下继续弛豫洁净与吸附结构，再以匹配设置成对重算吸附能并检查可移动原子的力。

## 文献方法与吸附能参考态

Kocabas 等人研究 electrene 材料上的 Li 储存，在 2×2×1 超胞中采用 25% Li 覆盖度比较吸附位点，并用 NEB 计算候选迁移路径。文中的吸附能定义基于吸附体系、洁净薄层和 Li 原子能量；Fig. 5 展示不同路径的势垒对比。该方法把位点筛选与扩散势垒作为需要分别计算的量。[Kocabas 等，J. Phys. Chem. Lett. 9, 4262 (2018)](https://doi.org/10.1021/acs.jpclett.8b01468)。

本页采用解离 H₂ 参考：洁净 Al(111) 薄膜、对称放置的两个吸附 H，以及独立 H₂。参考能与 Kocabas 等人的原子吸附定义不同；本例当前也只覆盖一个指定顶位构型。两者的吸附能数值不作横向比较，本例没有计算位点排序或 NEB 势垒。

继续计算时，可先在更密表面采样下优化洁净与吸附几何，再用匹配设置复核能量差和可移动原子的力；随后比较薄膜层数、覆盖度与其他吸附位点。若目标是 H₂ 到达吸附态的路径，应另建初态、终态与中间构型并计算 NEB 势垒。当前结果是非磁性 PBE 电子能量差；零点能和温度项需要独立计算。

```text
同一表面晶胞 → 洁净基底优化 ─┐
               吸附态优化 ──┼→ 核对力与能量定义 → 三能差 / 2
独立分子盒 → H2 优化 ──────┘                         ↓
                                          成对 k 网格 / 真空 / 分子盒检查
                                                     ↓
                                           当前数值边界与下一项证据
```
