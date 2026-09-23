[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [QE 7.5 的 Si 官方例子](https://github.com/QEF/q-e/blob/qe-7.5/PW/examples/example01/run_example) · [本例 Si 赝势来源](https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，各测试目录按本页的 SCF 输入独立生成电子密度。

先在一个算得快、结果容易核对的结构上看参数到底改了什么。这里用两个 Si 原子的金刚石原胞，晶格取自 QE 官方例子的 `celldm(1)=10.20 bohr`，换算为 `A=5.397607551 Å`。赝势改用公开库的 PBE 超软赝势 `Si.pbe-n-rrkjus_psl.1.0.0.UPF`。因此这是一个固定晶胞的 PBE 参数对照，不是在重现原例的 LDA 能量，也还没有优化 PBE 的平衡晶格。

`scf` 保存一份起点，`cutoff40` 等目录改变波函数截断能，`rho320`、`rho480` 改变电荷密度截断能，`k4` 到 `k14` 改变均匀 k 网格。每个目录各有自己的 `tmp/si.save`，不会轮流覆盖同一份密度。

```text
[preston@preston-System-Product-Name si-pbe]$ ls -d cutoff* rho* k[0-9]*
cutoff40  cutoff50  cutoff60  cutoff70  cutoff80  k10  k12  k14  k4  k6  k8  rho320  rho480
[preston@preston-System-Product-Name si-pbe]$
```


先打开输入。整份文件只有两个原子，读完它比从一份复杂材料的输入中删参数更容易看清固定项。

```text
[preston@preston-System-Product-Name si-pbe]$ cat scf/scf.in
&CONTROL
  calculation = 'scf'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  conv_thr = 1.0d-10
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS automatic
8 8 8 0 0 0
[preston@preston-System-Product-Name si-pbe]$
```


`ecutwfc=60` 和 `ecutrho=640` 都以 Ry 为单位：前者限制波函数的平面波基组，后者控制电荷密度与势的表示，超软赝势的增广电荷也在其中。增大它们通常会增加平面波或 FFT 网格及计算开销，所以先分开比较，才知道计算量花在哪一项上。`conv_thr=1.0d-10` 控制本次电子自洽的估计能量误差；即使一次 SCF 已满足这个阈值，改用更密的 k 网格仍然可能改变总能量。`occupations='fixed'` 对应本例的非磁性半导体设置。最后三个零表示这份均匀网格没有半格位移；后面比较网格时也保持这一约定。

做一个截断能对照时，实际操作是复制输入，再用 `vi` 改那一个数。例如 `cutoff40/scf.in` 把 `ecutwfc` 改成 40，保留 `ecutrho=640` 和 `8 8 8 0 0 0`。这样横轴才只有一个变量。这里没有把 `ecutrho` 同时设成波函数截断的某个固定倍数，否则能量变化会混入两个来源。完整文件可直接核对：[40 Ry 输入](/Atlas/examples/si-pbe/cutoff40/scf.in)、[80 Ry 输入](/Atlas/examples/si-pbe/cutoff80/scf.in)。

```text
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in scf/run.sh cutoff40/
[preston@preston-System-Product-Name si-pbe]$ vi cutoff40/scf.in
```

后续的短作业使用下面这份提交脚本。它在 Preston 上运行 GCC/OpenMPI 版 QE 7.5，使用 4 个 MPI 进程，三个线程变量都设为 1。`cd "$SLURM_SUBMIT_DIR"` 很关键：输入中的 `../pseudo`、`./tmp` 都按提交目录解释。`--bind-to none` 是这台机器本次采用的启动方式；并行方式要与自己的调度环境相符。

```text
[preston@preston-System-Product-Name si-pbe]$ cat rho320/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in scf.in > scf.out 2> scf.err
[preston@preston-System-Product-Name si-pbe]$
```


以电荷密度截断的 320 Ry 对照为例，这次提交得到作业 783；它的 `scf.out`、`scf.err` 和调度日志分别留下来。不要把不同尝试追加到同一个 OUT 中。

```text
[preston@preston-System-Product-Name si-pbe]$ cd rho320
[preston@preston-System-Product-Name rho320]$ sbatch run.sh
Submitted batch job 783
[preston@preston-System-Product-Name rho320]$ cd ..
```

先看一份完成的 SCF 输出的开头，而不是只搜索能量。这里能确认版本、4 个 MPI 进程、读到的输入文件，以及实际使用的晶格、原子数和截断。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 82 scf/scf.out

     Program PWSCF v.7.5 starts on 22Sep2026 at 21:32:23

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
     8639 MiB available memory on the printing compute node when the environment starts

     Reading input from scf.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4

     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


     Parallelization info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Min         571     214     63                18093     4156     682
     Max         572     217     64                18095     4157     686
     Sum        2287     859    253                72377    16625    2733

     Using Slab Decomposition



     bravais-lattice index     =            2
     lattice parameter (alat)  =      10.2000  a.u.
     unit-cell volume          =     265.3020 (a.u.)^3
     number of atoms/cell      =            2
     number of atomic types    =            1
     number of electrons       =         8.00
     number of Kohn-Sham states=            4
     kinetic-energy cutoff     =      60.0000  Ry
     charge density cutoff     =     640.0000  Ry
     scf convergence threshold =      1.0E-10
     mixing beta               =       0.7000
     number of iterations used =            8  plain     mixing
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)

     celldm(1)=  10.200000  celldm(2)=   0.000000  celldm(3)=   0.000000
     celldm(4)=   0.000000  celldm(5)=   0.000000  celldm(6)=   0.000000

     crystal axes: (cart. coord. in units of alat)
               a(1) = (  -0.500000   0.000000   0.500000 )
               a(2) = (   0.000000   0.500000   0.500000 )
               a(3) = (  -0.500000   0.500000   0.000000 )

     reciprocal axes: (cart. coord. in units 2 pi/alat)
               b(1) = ( -1.000000 -1.000000  1.000000 )
               b(2) = (  1.000000  1.000000  1.000000 )
               b(3) = ( -1.000000  1.000000 -1.000000 )


     PseudoPot. # 1 for Si read from file:
     ../pseudo/Si.pbe-n-rrkjus_psl.1.0.0.UPF
     MD5 check sum: fa25574f73a70a4139f2adfbefec430c
     Pseudo is Ultrasoft + core correction, Zval =  4.0
     Generated using &quot;atomic&quot; code by A. Dal Corso  v.6.3
     Using radial grid of 1141 points,  6 beta functions with:
                l(1) =   0
                l(2) =   0
                l(3) =   1
                l(4) =   1
                l(5) =   2
                l(6) =   2
     Q(r) pseudized with 0 coefficients
[preston@preston-System-Product-Name si-pbe]$
```


继续向下，电子迭代从初始电荷开始。`estimated scf accuracy` 会随迭代下降；中间没有感叹号的能量是当前迭代值，不能和已经完成的另一个计算直接放进收敛表。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -A28 'Self-consistent Calculation' scf/scf.out
     Self-consistent Calculation

     iteration #  1     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  1.00E-02,  avg # of iterations =  2.0

     Threshold (ethr) on eigenvalues was too large:
     Diagonalizing with lowered threshold

     Davidson diagonalization with overlap
     ethr =  6.40E-04,  avg # of iterations =  1.5

     total cpu time spent up to now is        1.2 secs

     total energy              =     -22.83581101 Ry
     estimated scf accuracy    <       0.05540955 Ry

     iteration #  2     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  6.93E-04,  avg # of iterations =  1.0

     total cpu time spent up to now is        1.5 secs

     total energy              =     -22.83770169 Ry
     estimated scf accuracy    <       0.00288592 Ry

     iteration #  3     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  3.61E-05,  avg # of iterations =  2.8
[preston@preston-System-Product-Name si-pbe]$
```


输出出现 `convergence has been achieved` 后，带感叹号的总能量才是这次 SCF 要收集的值。这里还会给出分项能量和力；一份完整 OUT 不只有一列最终数字。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -A20 '!    total energy' scf/scf.out
!    total energy              =     -22.83859230 Ry
     estimated scf accuracy    <          4.3E-11 Ry

     The total energy is the sum of the following terms:
     one-electron contribution =       5.30781076 Ry
     hartree contribution      =       1.08523150 Ry
     xc contribution           =     -12.33187599 Ry
     ewald contribution        =     -16.89975857 Ry

     convergence has been achieved in   9 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000000   -0.00000000   -0.00000000
     atom    2 type  1   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000


     Computing stress (Cartesian axis) and pressure

[preston@preston-System-Product-Name si-pbe]$
```


末尾则用于确认程序确实走到结束。`PWSCF` 一行同时给出 CPU 和 WALL 时间；`JOB DONE.` 要和前面的电子收敛信息一起读。最早几次运行的 `scf.err` 含图形环境授权提示，原件仍保留；对应输入、能量迭代和结束标志已逐项核对。后续作业脚本清除了 `DISPLAY` 和 `XAUTHORITY`，但部分后续 MPI 任务仍收到同类提示，错误流仍需逐次检查。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 scf/scf.out
     interpolate  :      0.12s CPU      0.13s WALL (      10 calls)

     Parallel routines

     PWSCF        :      9.22s CPU     13.73s WALL


   This run was terminated on:  21:32:37  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


现在把各个目录的最终能量并排看。先看波函数截断：

```text
[preston@preston-System-Product-Name si-pbe]$ grep '!    total energy' cutoff*/scf.out
cutoff40/scf.out:!    total energy              =     -22.83848017 Ry
cutoff50/scf.out:!    total energy              =     -22.83857229 Ry
cutoff60/scf.out:!    total energy              =     -22.83859230 Ry
cutoff70/scf.out:!    total energy              =     -22.83860349 Ry
cutoff80/scf.out:!    total energy              =     -22.83861255 Ry
[preston@preston-System-Product-Name si-pbe]$
```


再看 k 网格。文件名按字符排序，所以 `k10` 会出现在 `k4` 前面；绘图时按数字排序，不能拿目录显示顺序当成横轴顺序。

```text
[preston@preston-System-Product-Name si-pbe]$ grep '!    total energy' k*/scf.out
k10/scf.out:!    total energy              =     -22.83882782 Ry
k12/scf.out:!    total energy              =     -22.83887072 Ry
k14/scf.out:!    total energy              =     -22.83887935 Ry
k4/scf.out:!    total energy              =     -22.82483572 Ry
k6/scf.out:!    total energy              =     -22.83709393 Ry
k8/scf.out:!    total energy              =     -22.83859230 Ry
[preston@preston-System-Product-Name si-pbe]$
```


下面的表由每份独立 OUT 提取。每组都以本组最后一点为参照，先把原胞能量差从 Ry 换成 eV，再除以两个原子。波函数截断和电荷截断两组固定 `8³` 网格；k 网格组固定 `60/640 Ry`，因此三组的绝对能量不可串成一条曲线。

| 改动项 | 取值 | 总能量 / Ry·原胞⁻¹ | 相对本组最后一点 / meV·atom⁻¹ |
| --- | ---: | ---: | ---: |
| ecutwfc | 40 | -22.83848017 | 0.9006 |
| ecutwfc | 50 | -22.83857229 | 0.2739 |
| ecutwfc | 60 | -22.83859230 | 0.1378 |
| ecutwfc | 70 | -22.83860349 | 0.0616 |
| ecutwfc | 80 | -22.83861255 | 0.0000 |
| ecutrho | 320 | -22.83858862 | 0.0250 |
| ecutrho | 480 | -22.83859183 | 0.0032 |
| ecutrho | 640 | -22.83859230 | 0.0000 |
| kmesh | 4 | -22.82483572 | 95.5367 |
| kmesh | 6 | -22.83709393 | 12.1459 |
| kmesh | 8 | -22.83859230 | 1.9528 |
| kmesh | 10 | -22.83882782 | 0.3506 |
| kmesh | 12 | -22.83887072 | 0.0587 |
| kmesh | 14 | -22.83887935 | 0.0000 |


为了演示如何读表，这次使用 **1 meV/atom** 作为总能量变化的比较线。它是这个小例子的教学条件，不是声子、应力或能隙的通用误差标准。表中最后一点也只是本轮最高参数的参照，并非已经知道的无限基组、无限网格真值；需要一起看末端相邻几次变化，避免某一个点偶然接近参照就停止。波函数截断从 60 增至 80 Ry，总能量只改变约 0.138 meV/atom；电荷截断从 320 增至 640 Ry，改变约 0.025 meV/atom。k 网格却更敏感：`8³→10³` 仍改变约 1.60 meV/atom，`10³→12³` 约 0.292 meV/atom，`12³→14³` 约 0.059 meV/atom。仅凭 `8³` 那份输出的 `conv_thr`，看不出后面这件事。

这也解释了后续例子为什么保留 `60/640 Ry`，而把用于带边精细计算的父 SCF 加密到 `12³`。是否用于别的材料、不同赝势或声子，需要对那个实际要使用的量继续比较。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 7 convergence.csv
parameter,directory,setting,energy_Ry_per_cell,delta_meV_per_atom_vs_last
ecutwfc,cutoff40,40,-22.83848017,0.9005608278120207
ecutwfc,cutoff50,50,-22.83857229,0.27388260258107094
ecutwfc,cutoff60,60,-22.8385923,0.13775764288503814
ecutwfc,cutoff70,70,-22.83860349,0.06163378984719802
ecutwfc,cutoff80,80,-22.83861255,0.0
ecutrho,rho320,320,-22.83858862,0.02503447533917406
[preston@preston-System-Product-Name si-pbe]$
```


[下载能量表](/Atlas/examples/si-pbe/convergence.csv)、[下载提取脚本](/Atlas/examples/si-pbe/analyse_si.py)和[下载绘图脚本](/Atlas/examples/si-pbe/plot_si.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/si-pbe/atlas_plot_style.py)）放在同一组示例目录。提取脚本读取原始 OUT；绘图脚本读取 CSV，不需要波函数文件。安装好 Python、NumPy、Matplotlib 后，在 `si-pbe` 目录运行：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py convergence
<工作目录>/si-pbe/plots/convergence.png
```

![Si 总能量对波函数截断、电荷密度截断和 k 网格的实测变化](/Atlas/examples/si-pbe/plots/convergence.png)

右图采用允许零值的对称对数坐标，既能看到 `4³` 的大偏差，也能读出密网格末端的变化。图上的每一点都有对应输入、输出和独立审计记录；本例三个维度的最后三点通过了上述总能量比较条件。力、应力、能隙和声子尚不能由这张图代替检验。

下一步：固定晶胞下移动原子可接[结构优化](/Atlas/m/relax/qe/)；研究带边时接[带隙](/Atlas/m/band-gap/qe/)和[有效质量](/Atlas/m/effective-mass/qe/)。

```text
同一结构 + 同一赝势
  ├─ 改 ecutwfc，保持 ecutrho 和 k 网格
  ├─ 改 ecutrho，保持 ecutwfc 和 k 网格
  └─ 改 k 网格，保持两个截断
          ↓
      对实际关注的量比较
          ↓
      选择后续计算设置
```
