[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [QE 7.5 的 Si 官方例子](https://github.com/QEF/q-e/blob/qe-7.5/PW/examples/example01/run_example) · [本例 Si 赝势来源](https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF)

本例的输入、输出、能量表和 Python 提取脚本可[一起下载](/Atlas/examples/basics-si-convergence-files.tar.gz)。解包得到 `basics-si-convergence`。原始计算文件在其 `si-pbe/` 子目录；在包的根目录运行后面的提取命令。

下载包保留实际输入、OUT、错误流、提交脚本和数值表。读取与换算能量只需 Python 3 标准库；重跑 QE 时，按官方链接准备赝势并将 `run.sh` 中的 `<qe_bin>` 改为本机安装路径。

先在一个算得快、结果容易核对的结构上看参数到底改了什么。这里用两个 Si 原子的金刚石原胞，晶格取自 QE 官方例子的 `celldm(1)=10.20 bohr`，换算为 `A=5.397607551 Å`。赝势改用公开库的 PBE 超软赝势 `Si.pbe-n-rrkjus_psl.1.0.0.UPF`。下面在这个固定晶胞内比较 PBE 总能量对三个数值参数的响应。

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

做一个截断能对照时，实际操作是复制输入，再用 `vi` 改那一个数。例如 `cutoff40/scf.in` 把 `ecutwfc` 改成 40，保留 `ecutrho=640` 和 `8 8 8 0 0 0`。这样横轴才只有一个变量。这里没有把 `ecutrho` 同时设成波函数截断的某个固定倍数，否则能量变化会混入两个来源。完整文件可直接核对：[40 Ry 输入](/Atlas/examples/basics-si-convergence/si-pbe/cutoff40/scf.in)、[80 Ry 输入](/Atlas/examples/basics-si-convergence/si-pbe/cutoff80/scf.in)。

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

```text
ΔE (meV/atom) = |E_i − E_ref| (Ry/cell) × 13.6056931229905 × 1000 / 2
```

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

k 网格的末端变化最能说明怎样用这条规则：8³ 与 14³ 相差 1.952757 meV/atom，8³→10³ 还改变 1.602206 meV/atom；10³→12³ 和 12³→14³ 分别改变 0.291842、0.058709 meV/atom。因此 10³ 是本表中第一个满足规则的网格。截断组中，40→80 Ry 的总变化为 0.900561 meV/atom，320→640 Ry 的总变化为 0.025034 meV/atom；更低截断没有在这组文件中采样。

后续 Si 教案继续使用 60/640 Ry，并把带边计算的父 SCF 加密到 12³。用于力、应力或声子时，应直接比较那个目标量：`conv_thr` 负责一次 SCF 的电子误差，目标量对截断和网格的变化由相应扫描决定。最高已测点是这张表的有限参照；1 meV/atom 是本例选定的总能量比较线。

## 从原始文件重新生成表格

完整脚本 [analyze_si_convergence.py](/Atlas/examples/basics-si-convergence/analyze_si_convergence.py)读取每个目录的 `scf.in`、`scf.out` 和 `scf.err`，先核对 [原始文件校验和](/Atlas/examples/basics-si-convergence/SHA256SUMS.raw)，再检查原子数、截断回显、QE 版本、SCF 收敛与结束标志。它按数字排序扫描点，并核对每组其余输入相同；`scf`、`cutoff60`、`k8` 的等效设置在同一组中只计一次。

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

EPW 的方法论文同样按目标物理量组织网格检查，Fig. 1 分开比较粗网格、细积分网格和展宽，并展示网格与展宽的共同影响。本例采用同样的控制变量思路，目标量为固定晶胞 Si 总能量。参见 Lee 等，*npj Computational Materials* **9**, 156 (2023)，[DOI: 10.1038/s41524-023-01107-3](https://doi.org/10.1038/s41524-023-01107-3)。单位换算见 [NIST Hartree energy in eV](https://physics.nist.gov/cgi-bin/cuu/Value?hrev)。

接下来进入[离子弛豫](/Atlas/m/relax/qe/)、[晶胞弛豫](/Atlas/m/vc-relax/qe/)或[固定结构 SCF](/Atlas/m/scf/qe/)，按实际要计算的量继续设置输入。
