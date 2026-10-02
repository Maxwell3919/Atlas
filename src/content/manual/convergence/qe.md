## 先量出数值误差，再比较材料性质

界面结合能是几份总能量的差，电荷转移是几份密度的差，声子又来自能量对位移的响应。一次电子自洽通过之后，还要知道这些量会怎样随截断能、k 网格和占据展宽改变。比较的对象决定所需精度：能量差稳定，不自动保证层间距、力、应力或费米能附近的态密度已经稳定。

这里先用两个原子的金刚石 Si 原胞练习最容易复核的量——固定晶胞总能量。QE 7.5 使用 PBE 超软赝势 `Si.pbe-n-rrkjus_psl.1.0.0.UPF`，常规立方晶格参数为 10.20 bohr（5.397607551 Å），所有扫描保持晶胞和原子位置不变。分别改变波函数截断、电荷密度截断和均匀网格，再用每组最高已测点作有限参照。完成一份输入的方法见 [SCF](/Atlas/m/scf/qe/)。

[Prandini 等的 SSSP 方法论文 Fig. 2](https://arxiv.org/pdf/1806.05609v2#page=12)（原文第 12 页）用同一截断能横轴比较 Pd 的不同赝势，每一行分别跟踪声子、内聚能、压力和能带误差，再与各自的水平虚线阈值比较；圈出的点才是满足所选判据的赝势与截断组合。各误差相对论文的 200 Ry 参照计算，压力还转换为等效体积偏差，不能把它们都读成总能量误差。本页只借用“参照值、采样点、比较线并列”的图法：下面 Si 表的纵量是固定晶胞总能量差，不是论文的内聚能，因为这里没有计算孤立 Si 原子。[QE 方法论文](https://doi.org/10.1088/0953-8984/21/39/395502)第 4.1 节解释超软赝势为何需要波函数与增广密度的两套网格。

[完整算例包](/Atlas/examples/basics-si-convergence-files.tar.gz)解包为 `basics-si-convergence`，含 `si-pbe/` 下实际输入、OUT、错误流、提交脚本、数值表和完整提取源码。读取和换算只需 Python 3 标准库；复算时另建目录，按[官方来源](https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF)准备赝势，并修改脚本中的 `<qe_bin>`。

## 为每个参数点保留独立输入与输出

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

做一个新的截断能对照时，先在 `si-pbe` 下建立独立目录（如 `mkdir cutoff40`），再复制输入和提交脚本，用 `vi` 只改截断能。下载包中的这些目录已有原始结果，复算时另建目录。例如 `cutoff40/scf.in` 把 `ecutwfc` 改成 40，保留 `ecutrho=640` 和 `8 8 8 0 0 0`。这样横轴才只有一个变量。这里没有把 `ecutrho` 同时设成波函数截断的某个固定倍数，否则能量变化会混入两个来源。完整文件可直接核对：[40 Ry 输入](/Atlas/examples/basics-si-convergence/si-pbe/cutoff40/scf.in)、[80 Ry 输入](/Atlas/examples/basics-si-convergence/si-pbe/cutoff80/scf.in)。

```text
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in scf/run.sh cutoff40/
[preston@preston-System-Product-Name si-pbe]$ vi cutoff40/scf.in
```

后续的短作业使用下面这份提交脚本。它在 Preston 上运行 GCC/OpenMPI 版 QE 7.5，使用 4 个 MPI 进程，三个线程变量都设为 1。脚本会切换到作业的提交目录，因此输入中的相对赝势与临时目录路径均从该目录解释。--bind-to none 是这台机器本次采用的启动方式；并行方式要与自己的调度环境相符。

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

## 每份能量都要对应一次完整电子计算

提取时先核对 OUT 头部的结构、原子数、截断能和实际版本，再把末轮 `! total energy`、`estimated scf accuracy`、`convergence has been achieved` 与文件结束段连起来读。[SCF 页](/Atlas/m/scf/qe/)已逐段解释这份基线 OUT；这里重点比较不同参数点，不重复展开同一电子迭代。

<details>
<summary>本组基线 OUT：头部、电子迭代、最终能量与收尾原记录</summary>


先看一份完成的 SCF 输出的开头。这里能确认版本、4 个 MPI 进程、读到的输入文件，以及实际使用的晶格、原子数和截断。

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


提取带感叹号的最终总能量时，同时核对相邻的 `convergence has been achieved` 信息和末轮误差。这里还会给出分项能量和力；一份完整 OUT 不只有一列最终数字。

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


末尾用于确认程序走到结束；`PWSCF` 行给出 CPU 和 WALL 时间，`JOB DONE.` 与前面的电子收敛信息一起读取。最早几次 `scf.err` 保留 X11 授权提示；对应 OUT 的电子迭代已收敛并正常结束。

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


</details>

## 在同一组内比较能量差

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


再看 k 网格。文件名按字符排序，所以 `k10` 会出现在 `k4` 前面；汇总时按数字排序，不能拿目录显示顺序当成横轴顺序。

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

| 改动项 | 设置 | 固定条件 |
| --- | --- | --- |
| ecutwfc | 40、50、60、70、80 Ry | ecutrho=640 Ry，8³ 零偏移网格 |
| ecutrho | 320、480、640 Ry | ecutwfc=60 Ry，8³ 零偏移网格 |
| k 网格 | 4³、6³、8³、10³、12³、14³ | 60/640 Ry，零偏移 |

把原胞能量差换成每原子能量差。本例有两个 Si 原子，使用 NIST 2022 CODATA 的 `1 Ry = 13.6056931229905 eV`：

$$
\begin{aligned}
\Delta E\;(\mathrm{meV/atom})
&= \lvert E_i-E_{\mathrm{ref}}\rvert\;(\mathrm{Ry/cell}) \\
&\quad\times 13.6056931229905\times\frac{1000}{2}
\end{aligned}
$$

每组以最高已测设置为参照：80 Ry、640 Ry 或 14³。相邻变化则比较同一组中连续两个已测点。

| 参数 | 设置 | 总能量 (Ry/原胞) | 与本组参照差值 (meV/atom) | 与前一点的变化 (meV/atom) |
| --- | ---: | ---: | ---: | ---: |
| ecutwfc | 40 Ry | -22.83848017 | 0.900561 | — |
| ecutwfc | 50 Ry | -22.83857229 | 0.273883 | 0.626678 |
| ecutwfc | 60 Ry | -22.83859230 | 0.137758 | 0.136125 |
| ecutwfc | 70 Ry | -22.83860349 | 0.061634 | 0.076124 |
| ecutwfc | 80 Ry | -22.83861255 | 0.000000 | 0.061634 |
| ecutrho | 320 Ry | -22.83858862 | 0.025034 | — |
| ecutrho | 480 Ry | -22.83859183 | 0.003197 | 0.021837 |
| ecutrho | 640 Ry | -22.83859230 | 0.000000 | 0.003197 |
| kmesh | 4³ | -22.82483572 | 95.536660 | — |
| kmesh | 6³ | -22.83709393 | 12.145938 | 83.390722 |
| kmesh | 8³ | -22.83859230 | 1.952757 | 10.193181 |
| kmesh | 10³ | -22.83882782 | 0.350551 | 1.602206 |
| kmesh | 12³ | -22.83887072 | 0.058709 | 0.291842 |
| kmesh | 14³ | -22.83887935 | 0.000000 | 0.058709 |

用 **1 meV/atom** 作为本例的比较线，从低到高选择第一个点：它与本组参照的差值不超过比较线，而且它之后的每次相邻变化也不超过比较线。这样得到 40 Ry、320 Ry 和 10³。三个最低设置来自各自的独立扫描，尚未组合为同一次计算。

这条比较线以每原子计，本例的 1 meV/atom 等于两个原子整胞的 2 meV。40 Ry 点相对 80 Ry 的 0.900561 meV/atom，对应约 1.801122 meV/原胞；8³→10³ 的 1.602206 meV/atom 则对应约 3.204413 meV/原胞。比较异质结与两份组分的能量时，先统一整胞、每原子或每面积的定义，并让各份参照采用匹配条件；不能把这个两原子例子的比较线直接当作任意界面结合能的允许误差。

k 网格的末端变化最能说明怎样用这条规则：8³ 与 14³ 相差 1.952757 meV/atom，8³→10³ 还改变 1.602206 meV/atom；10³→12³ 和 12³→14³ 分别改变 0.291842、0.058709 meV/atom。因此 10³ 是本表中第一个满足规则的网格。截断组中，40→80 Ry 的总变化为 0.900561 meV/atom，320→640 Ry 的总变化为 0.025034 meV/atom；更低截断没有在这组文件中采样。

### 把本表画成可复核的误差图

![Si 三组独立扫描的总能量残差，由现有 CSV 经 gnuplot 绘制](/Atlas/examples/basics-literature/si-convergence/convergence.svg)

三个面板分别改变波函数截断、电荷密度截断和网格边长，纵轴统一为 meV/atom，红虚线是本例的 1 meV/atom 比较线，绿圈标出表中选点。纵轴使用对数尺度，因此零残差的参照点 80 Ry、640 Ry 和 14³ 不画在曲线上；这些点仍保留在 CSV 中，未人为加上正数。蓝点是实际已测设置，连线只帮助按顺序读点。尤其看右图：8³ 仍在比较线上方，10³ 才落到下方；是否满足后续相邻变化条件，还要回到上表核对。

这幅图从本页的 [convergence.csv](/Atlas/examples/basics-si-convergence/results/convergence.csv) 直接读取，没有增加计算或拟合。下载 [同一 CSV 副本](/Atlas/examples/basics-literature/si-convergence/convergence.csv) 和 [plot.gp](/Atlas/examples/basics-literature/si-convergence/plot.gp)，放在同一目录运行 `gnuplot plot.gp`，同时生成 SVG、PNG 和 PDF（[SVG](/Atlas/examples/basics-literature/si-convergence/convergence.svg)、[PDF](/Atlas/examples/basics-literature/si-convergence/convergence.pdf)）。脚本不使用 SSSP 的 Pd 数值或筛选阈值。

为何通过能量线后还要检查别的量，可以读 [SSSP 原文 Fig. 6，第 15 页](https://arxiv.org/pdf/1806.05609v2#page=15)：横轴是满足声子频率判据的截断能，纵轴是满足内聚能判据的截断能，单位都是 Ry；圆点颜色按右侧色条表示落在同一截断组合的赝势个数。两种判据来自该文 Table 2 的 efficiency 条件，许多点的横纵值不同。因此，针对一种性质选出的截断能，不能自动转用于另一种性质。本页三图都读总能量残差，没有力、压力或频率数据；若下一步要弛豫，应在匹配结构上看力对电子阈值、截断和采样的变化，变胞还要看应力。若下一步读 DOS，则比较目标能区随 k 网格与展宽的变化。原子能量差、力和费米能附近峰形各自决定应增加哪一组数据，而不是把一条总能量曲线重复当成它们的证据。

<details>
<summary>生成上图的完整 gnuplot 源码</summary>

```gnuplot
# Exact existing CSV; no smoothing, fitting, interpolation or new DFT.
set datafile separator ','
set encoding utf8
set border linewidth 1
set tics out nomirror
set style line 1 lc rgb '#205493' lw 1.6 pt 7 ps 1.0
set style line 2 lc rgb '#ae3b2d' lw 1.5 dt 2
set style line 3 lc rgb '#237747' lw 1.6 pt 6 ps 1.6
unset key
set logscale y
set yrange [0.001:120]
set ylabel '|E-E(ref)| (meV/atom)'
parameters='ecutwfc ecutrho kmesh'
labels='ecutwfc ecutrho k-mesh'
do for [fmt in 'svg png pdf'] {
 if (fmt eq 'svg') { set terminal svg size 1140,430 enhanced font 'Arial,13' }
 if (fmt eq 'png') { set terminal pngcairo size 1140,430 enhanced font 'DejaVu Sans,13' }
 if (fmt eq 'pdf') { set terminal pdfcairo size 11.4in,4.3in enhanced font 'DejaVu Sans,13' }
 set output 'convergence.'.fmt
 set multiplot layout 1,3 margins 0.08,0.985,0.16,0.82 spacing 0.095,0.04 title 'Si: independent scans; highest measured point in each scan is its reference'
 do for [i=1:3] {
  par=word(parameters,i)
  set xlabel (i<3 ? word(labels,i).' (Ry)' : 'Uniform mesh edge N (N x N x N)')
  set title sprintf('(%s) %s',word('a b c',i),word(labels,i))
  if (i==1) { set xrange [40:80]; set xtics 40,10,80; set ylabel "|E-E(ref)| (meV/atom)" }
  if (i==2) { set xrange [320:640]; set xtics 320,160,640; unset ylabel }
  if (i==3) { set xrange [4:14]; set xtics 4,2,14; unset ylabel }
  set key top right font ',10'
  plot 'convergence.csv' using (strcol(1) eq par && $6>0 ? $3 : 1/0):6 with linespoints ls 1 title 'Sampled residual', \
       1 with lines ls 2 title '1 meV/atom', \
       'convergence.csv' using (strcol(1) eq par && strcol(8) eq 'True' && $6>0 ? $3 : 1/0):6 with points ls 3 title 'Selected'
 }
 unset multiplot
 unset output
}
```

</details>

后续 Si 教案继续使用 60/640 Ry，并把带边计算的父 SCF 加密到 12³。用于力、应力或声子时，应直接比较那个目标量：`conv_thr` 负责一次 SCF 的电子误差，目标量对截断和网格的变化由相应扫描决定。最高已测点是这张表的有限参照；1 meV/atom 是本例选定的总能量比较线。

## 用 AI 编写同类提取工具

[完整编程提示词](/Atlas/examples/basics-si-convergence/ai_prompt.md)说明输入文件、单位、分组与选点规则。可复制下述需求，请 AI 生成脚本，再用原始 OUT 核对结果：

```text
用 Python 3 标准库读取 si-pbe/*/scf.in、scf.out、scf.err，按 SHA256SUMS.raw 核对文件。
只把同时有最终 ! total energy、SCF 收敛行和 JOB DONE 的两原子 SCF 纳入能量表；
不完整目录保留在运行清单。核对输入与输出的截断和原子数，并验证每组只有一个参数改变。
分别整理 ecutwfc、ecutrho 和均匀 k 网格。每组最高已测点为参照，计算
|E_i-E_ref|*13.6056931229905*1000/2 和相邻差，单位 meV/atom。
按 1 meV/atom 比较线选取参照差及后续相邻差均满足的最低采样点。
输出完整 CSV、SCF 迭代表、JSON 摘要和 Markdown 数值报告，保留原始文件的相对路径与哈希。
```

## 从原始文件重新生成表格

完整脚本 [analyze_si_convergence.py](/Atlas/examples/basics-si-convergence/analyze_si_convergence.py)读取每个目录的 `scf.in`、`scf.out` 和 `scf.err`，先核对 [原始文件校验和](/Atlas/examples/basics-si-convergence/SHA256SUMS.raw)，再检查原子数、截断回显、QE 版本、SCF 收敛与结束标志。它按源码 `AXES` 中列出的递增顺序整理这三组扫描，并核对每组其余输入相同；`scf`、`cutoff60`、`k8` 的等效设置在同一组中只计一次。

<details>
<summary>analyze_si_convergence.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Read the supplied Si QE SCF files and tabulate total-energy changes.

Usage: python3 analyze_si_convergence.py si-pbe --outdir reproduced
Python standard library only. SHA256SUMS.raw is read beside this script.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

RY_EV = 13.6056931229905
AXES = {
    'ecutwfc': ['cutoff40', 'cutoff50', 'cutoff60', 'cutoff70', 'cutoff80'],
    'ecutrho': ['rho320', 'rho480', 'scf'],
    'kmesh': ['k4', 'k6', 'k8', 'k10', 'k12', 'k14'],
}
LOGISTICS = {'prefix', 'outdir', 'pseudo_dir', 'wfcdir'}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(package):
    records = []
    for line in (package / 'SHA256SUMS.raw').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = package / name
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f'Raw-file checksum mismatch: {name}')
        records.append({'file': name, 'sha256': digest})
    return records


def read_input(path):
    lines = [re.sub(r'\s+', ' ', line.split('!', 1)[0].strip()).lower()
             for line in path.read_text().splitlines() if line.split('!', 1)[0].strip()]
    params = {}
    for line in lines:
        match = re.fullmatch(r'([a-z][a-z0-9_]*)\s*=\s*(.*?)\s*,?', line)
        if match:
            params[match[1]] = match[2].rstrip(',').strip().strip("'\"")
    index = lines.index('k_points automatic')
    grid = tuple(int(value) for value in lines[index + 1].split())
    if len(grid) != 6 or len(set(grid[:3])) != 1:
        raise ValueError(f'{path}: expected an n x n x n automatic grid')
    return params, grid, lines, index


def read_run(directory, source_names, package):
    inp = directory / 'scf.in'
    out = directory / 'scf.out'
    err = directory / 'scf.err'
    for path in (inp, out, err):
        if path.exists() and path.relative_to(package).as_posix() not in source_names:
            raise ValueError(f'Raw file missing from SHA256SUMS.raw: {path.name}')
    params, grid, lines, index = read_input(inp)
    text = out.read_text(errors='replace') if out.is_file() else ''
    energies = re.findall(r'^\s*!\s*total energy\s*=\s*([-+\d.eEdD]+)\s+Ry', text, re.M)
    completed = 'JOB DONE.' in text and len(re.findall('convergence has been achieved', text)) == 1
    reasons = []
    if not out.is_file():
        reasons.append('missing scf.out')
    if len(energies) != 1 or not completed:
        reasons.append('one converged SCF energy and normal end required')
    energy = float(energies[0].replace('D', 'E').replace('d', 'e')) if len(energies) == 1 else None
    if energy is not None and not math.isfinite(energy):
        reasons.append('nonfinite energy')
    version = re.search(r'Program PWSCF v\.([^\s]+)', text)
    if text:
        echoes = {'nat': r'number of atoms/cell\s*=\s*(\d+)',
                  'ecutwfc': r'kinetic-energy cutoff\s*=\s*([-+\d.]+)',
                  'ecutrho': r'charge density cutoff\s*=\s*([-+\d.]+)'}
        for key, pattern in echoes.items():
            match = re.search(pattern, text)
            if not match or not math.isclose(float(match[1]), float(params[key]), abs_tol=1e-6):
                reasons.append(f'{key} input/output mismatch')
        if not version or version[1] != '7.5':
            reasons.append('expected QE 7.5')
        if not re.search(r'Exchange-correlation\s*=\s*PBE', text):
            reasons.append('expected PBE output')
    if params.get('calculation') != 'scf' or int(params['nat']) != 2:
        reasons.append('expected a two-atom SCF input')
    stderr = [line.strip() for line in err.read_text(errors='replace').splitlines() if line.strip()] if err.is_file() else []
    errclass = ('empty' if not stderr else 'X11 authorization notice' if all(
        line == 'Authorization required, but no authorization protocol specified' for line in stderr
    ) else 'inspect stderr')
    if errclass == 'inspect stderr':
        reasons.append('unclassified stderr')
    return {'directory': directory.name, 'params': params, 'grid': grid,
            'lines': lines, 'grid_line': index + 1, 'energy': energy,
            'complete': not reasons, 'reasons': '; '.join(reasons),
            'stderr': errclass, 'input_sha256': sha256(inp),
            'output_sha256': sha256(out) if out.is_file() else ''}


def signature(run, axis):
    kept = []
    for index, line in enumerate(run['lines']):
        assignment = re.match(r'([a-z][a-z0-9_]*)\s*=', line)
        if assignment and (assignment[1] in LOGISTICS or assignment[1] == axis):
            continue
        if axis == 'kmesh' and index == run['grid_line']:
            kept.append(' '.join(str(value) for value in run['grid'][3:]))
        else:
            kept.append(line)
    return tuple(kept)


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def scf_history(path):
    history = []
    for match in re.finditer(r'iteration #\s*(\d+)(.*?)(?=iteration #|\Z)', path.read_text(), re.S):
        energy = re.search(r'(?:!\s*)?total energy\s*=\s*([-+\d.]+)\s+Ry', match[2])
        accuracy = re.search(r'estimated scf accuracy\s*<\s*([-+\d.Ee]+)\s+Ry', match[2])
        if not energy or not accuracy:
            raise ValueError(f'incomplete SCF iteration {match[1]}')
        history.append({'iteration': int(match[1]), 'energy_Ry_per_cell': float(energy[1]),
                        'estimated_scf_accuracy_Ry': float(accuracy[1])})
    return history


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--outdir', type=Path, default=Path('results'))
    parser.add_argument('--tolerance', type=float, default=1.0, help='meV/atom')
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance <= 0:
        raise ValueError('tolerance must be finite and positive')
    raw = args.raw.resolve()
    package = Path(__file__).resolve().parent
    sources = verify_sources(package)
    source_names = {row['file'] for row in sources}
    runs = [read_run(path.parent, source_names, package) for path in sorted(raw.glob('*/scf.in'))]
    by_name = {run['directory']: run for run in runs}
    base = by_name['scf']
    for name in ('cutoff60', 'k8'):
        other = by_name[name]
        if signature(other, '') != signature(base, '') or not other['complete'] or not base['complete']:
            raise ValueError(f'{name}: baseline copy differs')
        if abs(other['energy'] - base['energy']) > 1e-8:
            raise ValueError(f'{name}: baseline energies differ beyond output precision')
    rows, selections = [], []
    for axis, names in AXES.items():
        members = [by_name[name] for name in names]
        if not all(run['complete'] for run in members):
            raise ValueError(f'{axis}: a required scan point is incomplete')
        if len({signature(run, axis) for run in members}) != 1:
            raise ValueError(f'{axis}: fixed input settings differ')
        reference = members[-1]['energy']
        series = []
        previous = None
        for run in members:
            setting = run['grid'][0] if axis == 'kmesh' else float(run['params'][axis])
            adjacent = None if previous is None else abs(run['energy'] - previous) * RY_EV * 1000 / 2
            series.append({'parameter': axis, 'directory': run['directory'], 'setting': setting,
                'natoms': 2, 'energy_Ry_per_cell': run['energy'],
                'delta_meV_per_atom': abs(run['energy'] - reference) * RY_EV * 1000 / 2,
                'adjacent_meV_per_atom': adjacent, 'selected': False,
                'input_sha256': run['input_sha256'], 'output_sha256': run['output_sha256']})
            previous = run['energy']
        chosen = next(i for i, row in enumerate(series) if row['delta_meV_per_atom'] <= args.tolerance
                      and all(later['adjacent_meV_per_atom'] <= args.tolerance for later in series[i + 1:]))
        series[chosen]['selected'] = True
        selections.append({'parameter': axis, 'selected': series[chosen]['setting'],
            'reference': series[-1]['setting'], 'delta_meV_per_atom': series[chosen]['delta_meV_per_atom']})
        rows.extend(series)
    inventory = [{key:run[key] for key in ('directory','complete','reasons','stderr','input_sha256','output_sha256')} for run in runs]
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / 'convergence.csv', rows)
    write_csv(args.outdir / 'run-inventory.csv', inventory)
    write_csv(args.outdir / 'scf-history.csv', scf_history(raw/'scf/scf.out'))
    summary = {'QE_version': '7.5', 'Ry_to_eV': RY_EV, 'natoms': 2,
        'tolerance_meV_per_atom': args.tolerance, 'candidate_runs': len(runs),
        'complete_runs': sum(run['complete'] for run in runs), 'table_rows': len(rows),
        'reference': 'highest sampled setting in each axis', 'selections': selections,
        'independent_scans': True, 'joint_selected_settings_calculated': False}
    (args.outdir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (args.outdir/'source-files.json').write_text(json.dumps(sources,indent=2)+'\n')
    report = ['# Si 固定晶胞总能量扫描', '',
        f'QE 7.5；两个原子/原胞；1 Ry = {RY_EV} eV。', '',
        '| 参数 | 设置 | 总能量 (Ry/原胞) | 与最高点差值 (meV/atom) | 相邻变化 (meV/atom) | 选择 |',
        '| --- | ---: | ---: | ---: | ---: | --- |']
    for row in rows:
        adjacent = '—' if row['adjacent_meV_per_atom'] is None else f"{row['adjacent_meV_per_atom']:.6f}"
        report.append(f"| {row['parameter']} | {row['setting']:g} | {row['energy_Ry_per_cell']:.8f} | {row['delta_meV_per_atom']:.6f} | {adjacent} | {'✓' if row['selected'] else ''} |")
    report.extend(['', f'按 {args.tolerance:g} meV/atom 比较线，选择同时满足参照差和后续相邻差的最低采样点。',
        '参照是每组最高已测设置。三组分别固定其余参数；所选最低设置尚未组合为同一次计算。',
        'conv_thr 控制单次电子自洽；力、应力及后续性质按各自目标量继续比较。', ''])
    (args.outdir/'energy-report.md').write_text('\n'.join(report),encoding='utf-8')
    print(f"raw_checksums={len(sources)} complete_runs={summary['complete_runs']} excluded_runs={len(runs)-summary['complete_runs']} table_rows={len(rows)}")
    for item in selections:
        setting = f"{int(item['selected'])}x{int(item['selected'])}x{int(item['selected'])}" if item['parameter']=='kmesh' else f"{item['selected']:g} Ry"
        print(f"{item['parameter']}: {setting}; difference to reference = {item['delta_meV_per_atom']:.6f} meV/atom")
    print(f'Results: {args.outdir}')


if __name__ == '__main__':
    main()
```

</details>

解压下载包后，实际运行命令和输出如下：

```text
$ cd basics-si-convergence
$ python3 analyze_si_convergence.py si-pbe --outdir results
raw_checksums=62 complete_runs=15 excluded_runs=1 table_rows=14
ecutwfc: 40 Ry; difference to reference = 0.900561 meV/atom
ecutrho: 320 Ry; difference to reference = 0.025034 meV/atom
kmesh: 10x10x10; difference to reference = 0.350551 meV/atom
Results: results
```

16 个含 `scf.in` 的目录中，15 个有完整 SCF 输出；`gamma-phonon` 只有输入，列在运行清单中。三组得到 14 行数据。脚本还输出 [9 轮电子迭代表](/Atlas/examples/basics-si-convergence/results/scf-history.csv)，其最后一轮的估计精度为 4.3×10⁻¹¹ Ry。

可分别下载 [能量表](/Atlas/examples/basics-si-convergence/results/convergence.csv)、[运行清单](/Atlas/examples/basics-si-convergence/results/run-inventory.csv)、[设置摘要](/Atlas/examples/basics-si-convergence/results/summary.json)、[文件哈希](/Atlas/examples/basics-si-convergence/results/source-files.json)、[数值报告](/Atlas/examples/basics-si-convergence/results/energy-report.md)及[实际命令输出](/Atlas/examples/basics-si-convergence/run.log)。将源码与原始文件目录一起保存，便可重算所有差值。

## 将总能量比较接到界面与声子分析

这张表支持的是同一固定 Si 晶胞下的总能量误差。计算界面结合能时，异质结与两个组分应采用同一能量定义和对应的结构约束，直接比较结合能差随数值设置的变化；层间距和内部坐标则从各次优化的末态检查。电荷转移要继续检查密度网格、Bader 积分或平面平均积分的变化。声子和 EPC 分别比较频率、谱函数、λ 等目标量，不能由 Si 的 1 meV/atom 选点接替这些检查。

二维体系的面内 k 点密度与真空长度也应分开考虑。kz=1 表示薄层的采样方式，不能证明周期镜像已经隔离；真空厚度应对功函数、密度分布或所关心的响应另做比较。金属还要把 k 网格与展宽放在同一轮目标量检验中。[Ba₂N 论文](https://doi.org/10.1103/PhysRevB.105.165101)第 II 节为结构/电子性质与 EPC 使用不同采样，便是按问题分配计算精度的实例；这些材料参数属于论文中的 Ba₂N。

本表的 40 Ry、320 Ry、10³ 分别来自独立扫描，没有把三者组合运行。后续 Si 算例保留其实际采用的 60/640 Ry 设置；若建立新的研究协议，选点后仍需以组合参数检查目标量。单位换算使用 [NIST Hartree energy in eV](https://physics.nist.gov/cgi-bin/cuu/Value?hrev)。

接下来可用[离子弛豫](/Atlas/m/relax/qe/)观察原子位置的调整，或继续固定结构的[均匀 NSCF](/Atlas/m/nscf/qe/)与[路径能带](/Atlas/m/bands/qe/)；需要优化晶胞时，另读[Al 的变胞算例](/Atlas/m/vc-relax/qe/#al-vc-relax)。
