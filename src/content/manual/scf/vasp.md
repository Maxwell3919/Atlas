[VASP：输入文件](https://vasp.at/wiki/Input_files) · [输出文件](https://vasp.at/wiki/Output_files) · [EDIFF](https://vasp.at/wiki/EDIFF) · [电子最小化](https://vasp.at/wiki/Category:Electronic_minimization)

先跑一个两个原子的 bcc Fe 固定结构计算，再沿着它实际生成的文件读一遍。电子自洽这一步解决的是：在指定晶格、原子位置和计算设置下，找到相互一致的电荷密度与有效势。它可以计算能量、磁矩和力，但不会因为电子收敛就自动把几何结构变成平衡结构。

[下载本次 SCF 的输入和输出](/Atlas/examples/vasp/fe-scf-files.tar.gz)。包内保留输入、OUTCAR、OSZICAR 和本例生成的其他小输出文件；POTCAR 只提供 TITEL、ZVAL 与 SHA256，使用前需从自己的授权赝势库准备对应文件。下面保留这次已执行的终端操作和结果。

```text
[bcgong@localhost vasp]$ mkdir -p fe_bcc/fm
[bcgong@localhost vasp]$ cd fe_bcc/fm
[bcgong@localhost fm]$ vi POSCAR
```

保存后重新读取文件，可以确认原子数量和坐标模式没有输错。

```text
[bcgong@localhost fm]$ cat POSCAR
Fe bcc conventional cell, a=2.8 A
1.0
2.8 0.0 0.0
0.0 2.8 0.0
0.0 0.0 2.8
Fe
2
Direct
0.0 0.0 0.0
0.5 0.5 0.5
```

第一行是标题，第二行是缩放系数，接下来三行是晶格矢量。`Fe` 和下一行的 `2` 说明这里只有一种元素、两个原子。`Direct` 后的坐标以晶格矢量为单位，所以第二个原子在体心，即笛卡尔坐标 (1.4, 1.4, 1.4) Å。

这里选 a = 2.8 Å 的 bcc 常规胞作为小算例。它同时能容纳两个 Fe 的不同初始磁矩；磁构型比较在 [磁性基态候选态](/Atlas/m/magnetic-gs/vasp/) 中继续，本页先把一份 SCF 算完。

```text
[bcgong@localhost fm]$ vi INCAR
```

```text
[bcgong@localhost fm]$ cat INCAR
SYSTEM = Fe bcc FM
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 100
ALGO = Normal
ISMEAR = 1
SIGMA = 0.1
ISPIN = 2
MAGMOM = 3 3
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
NCORE = 2
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .FALSE.
```

INCAR 控制计算怎样进行。`ENCUT = 400` 指定平面波截断能，单位 eV；`EDIFF = 1E-8` 是电子循环停止条件，`NELM = 100` 是最多电子步数。达到 NELM 只是用完迭代次数，不能代替达到 EDIFF。

`EDIFF` 同时约束相邻电子步的总自由能变化和带能变化，单位是整个晶胞的 eV；它不是原子力阈值，也不是“总能已经精确到这个数”。本例把电子迭代收紧，是为了让后续磁构型比较少受电子循环残差干扰。400 eV 与下面的 12³ 网格仍需各自做取样检查；把 EDIFF 再调小不能补回平面波或 k 点取样不足。

`ISPIN = 2` 开启共线自旋极化，`MAGMOM = 3 3` 给两个 Fe 同向的初始磁矩；迭代后的磁矩从输出读取。`ISMEAR = 1`、`SIGMA = 0.1` 是本例金属使用的占据展宽。`NSW = 0`、`IBRION = -1` 表示固定结构，原子位置和晶格都不会在这次运行中更新。

这里每个初始磁矩以 μB 计；修改 MAGMOM 可能把自洽过程引到另一种磁性解，因此结束后要回读磁矩，而不只比较总能。`ISMEAR = 1` 是一阶 Methfessel–Paxton 展宽，SIGMA 的单位为 eV。改变宽度会改变费米面附近的占据和能量修正；它需要与 k 网格一起检查，不能直接把这组金属参数搬到有带隙的材料。

`ISTART = 0`、`ICHARG = 2` 从新的波函数和原子电荷开始。输出开关也要在开始前确定：这里 `LWAVE` 和 `LCHARG` 均关闭，适合只比较能量和磁矩的短例子；若下一步需要重用密度或波函数，就要分别开启相应输出。

`PREC = Accurate` 控制默认 FFT 网格等数值设置；这里已经显式给出 ENCUT，不能把 Accurate 读成另一个截断能。两个原子的算例采用 `LREAL = .FALSE.`，在倒空间计算投影，便于避免实空间投影近似混入小能量差。`LASPH = .TRUE.` 保留 PAW 球内密度梯度的非球形贡献，对后续 Fe 磁态比较也保持一致。`ALGO = Normal` 选择电子求解算法，`NCORE = 2` 分配每条轨道的并行工作；它们改变求解过程或资源使用，不能替代精度检查。

```text
[bcgong@localhost fm]$ cat KPOINTS
Fe bcc 12x12x12
0
Gamma
12 12 12
0 0 0
```

第二行的 0 让 VASP 自动生成网格，Gamma 表示 Γ 中心，下一行 12 12 12 给三个方向的划分。最后一行没有额外偏移。12³ 是完整均匀网格的尺寸；程序还会利用晶体对称性减少实际计算的 k 点。

```text
[bcgong@localhost fm]$ grep -E 'TITEL|ZVAL' POTCAR
   TITEL  = PAW_PBE Fe 06Sep2000
   POMASS =   55.847; ZVAL   =    8.000    mass and valenz
```

POTCAR 给出元素的 PAW 数据集，元素顺序必须与 POSCAR 一致。这里只有 Fe；标题确认采用 `PAW_PBE Fe 06Sep2000`，`ZVAL = 8` 表示每个 Fe 显式处理 8 个价电子。两个原子的中性晶胞因此应有 16 个价电子。

这四份文件分别负责结构、计算控制、k 点取样和 PAW 数据，缺一项都不能把本例完整复现。提交脚本负责在服务器上启动程序，它不属于上述四种物理输入。

```text
[bcgong@localhost fm]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-fe-fm
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
unset SLURM_CPUS_PER_TASK
export I_MPI_PIN_PROCESSOR_LIST=16,17,18,19,20,21,22,23
cd $SLURM_SUBMIT_DIR
mpirun -np 8 /data/software/vasp.5.4.4/bin/vasp_std > out
```

这次使用 8 个 MPI 进程和单线程，提交前节点已有 16 核研究任务，总申请保持在 24/64 核。脚本中的 16–23 是现场核验后的 CPU 编号；它与本节点 Intel MPI 的绑核行为有关，不是 Fe 计算的物理参数，也不是通用服务器设置。换节点时要跟着调度器分配核验实际亲和性。

```text
[bcgong@localhost fm]$ sbatch run.slurm
Submitted batch job 18184
```

提交后，可以用 `squeue -j 18184` 读取队列状态，`tail -f out` 查看程序的实时输出。`out` 是脚本中重定向的标准输出，`_out.18184.log` 是 Slurm 脚本日志，两者作用不同。需要退出实时查看时按 Ctrl-C，它不会取消 Slurm 作业。

这次计算结束后，OSZICAR 内容如下：

```text
[bcgong@localhost fm]$ cat OSZICAR
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1     0.635915219673E+02    0.63592E+02   -0.66234E+03  5728   0.111E+03
DAV:   2    -0.165260323318E+02   -0.80118E+02   -0.71807E+02  5424   0.207E+02
DAV:   3    -0.181830241659E+02   -0.16570E+01   -0.16280E+01  6696   0.417E+01
DAV:   4    -0.181928977094E+02   -0.98735E-02   -0.98728E-02  6088   0.272E+00
DAV:   5    -0.181930383505E+02   -0.14064E-03   -0.14064E-03  6760   0.322E-01    0.169E+01
DAV:   6    -0.165850769302E+02    0.16080E+01   -0.89129E+00  5720   0.614E+01    0.695E+00
DAV:   7    -0.165011390407E+02    0.83938E-01   -0.58034E-01  6064   0.145E+01    0.453E+00
DAV:   8    -0.164884198881E+02    0.12719E-01   -0.11484E-02  6672   0.912E-01    0.193E+00
DAV:   9    -0.164737236473E+02    0.14696E-01   -0.39427E-03  7896   0.747E-01    0.338E-01
DAV:  10    -0.164736232960E+02    0.10035E-03   -0.85939E-04  6312   0.347E-01    0.981E-02
DAV:  11    -0.164736551655E+02   -0.31870E-04   -0.74484E-05  6240   0.103E-01    0.434E-02
DAV:  12    -0.164736601352E+02   -0.49697E-05   -0.66644E-06  5864   0.295E-02    0.295E-02
DAV:  13    -0.164736575912E+02    0.25440E-05   -0.32095E-06  6688   0.179E-02    0.147E-02
DAV:  14    -0.164736558456E+02    0.17455E-05   -0.64595E-07  7024   0.113E-02    0.231E-03
DAV:  15    -0.164736559442E+02   -0.98581E-07   -0.19652E-08  5632   0.162E-03    0.504E-04
DAV:  16    -0.164736559240E+02    0.20253E-07   -0.26883E-09  3104   0.664E-04    0.225E-04
DAV:  17    -0.164736559385E+02   -0.14517E-07   -0.28991E-10  2984   0.189E-04    0.542E-05
DAV:  18    -0.164736559415E+02   -0.30582E-08   -0.59411E-11  3008   0.941E-05
   1 F= -.16473656E+02 E0= -.16473773E+02  d E =0.351602E-03  mag=     4.2127
```

第一行列出了后续 DAV 行的含义：N 是电子步数，E 是当前能量，dE 与 d eps 分别是能量和带能变化，ncg 是迭代中的工作量计数，rms 与 rms(c) 是波函数和电荷相关残差。并不是每一步都打印所有残差列。

前几步的能量降得很快，第 6 步又上升了。自洽过程不断更新有效势和混合密度，所以不能要求 OSZICAR 中的 E 每一步都单调降低；应观察残差和停止条件。这里第 18 步的 dE 约为 −3.06×10⁻⁹ eV，之后打印出这一固定结构的 `F=`、`E0=` 和 `mag=` 汇总。

```text
[bcgong@localhost fm]$ grep -n -E 'aborting loop|General timing|Elapsed time' OUTCAR
5065:------------------------ aborting loop because EDIFF is reached ----------------------------------------
5207: General timing and accounting informations for this job:
5213:                         Elapsed time (sec):       12.997
```

OUTCAR 明确写出电子循环因为 EDIFF 已达到而停止，并在末尾给出正常计时；实际耗时约 13 秒。把这两条与迭代末尾一起核验，比只看队列里任务消失更可靠。

```text
[bcgong@localhost fm]$ head -7 OUTCAR
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 executed on             LinuxIFC date 2026.09.22  21:38:21
 running on    8 total cores
 distrk:  each k-point on    8 cores,    1 groups
 distr:  one band on NCORES_PER_BAND=   2 cores,    4 groups
```

开头先确认运行的 VASP 版本和核数。再往下是 PAW 数据说明、读入的参数、对称性和 k 点信息；先核对几个会直接改变结果的参数。

```text
[bcgong@localhost fm]$ grep -E 'NKPTS|NELECT|ENCUT|EDIFF |ISPIN|LWAVE|LCHARG' OUTCAR
   k-points           NKPTS =     84   k-points in BZ     NKDIM =     84   number of bands    NBANDS=     16
   ISPIN  =      2    spin polarized calculation?
   ENCUT  =  400.0 eV  29.40 Ry    5.42 a.u.   4.57  4.57  4.57*2*pi/ulx,y,z
   EDIFF  = 0.1E-07   stopping-criterion for ELM
   NELECT =      16.0000    total number of electrons
   LWAVE        =      F    write WAVECAR
   LCHARG       =      F    write CHGCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```

OUTCAR 中实际采用的 ENCUT=400 eV、ISPIN=2、NELECT=16 都与输入一致。`NKPTS = 84` 是对称性约化后的 k 点数，不能拿它与 12³ 直接比较后判定网格变少了；`NBANDS = 16` 则是本次使用的带数。

IBZKPT 保存约化后的 k 点与权重，可以继续查看其内部结构：

```text
[bcgong@localhost fm]$ head -10 IBZKPT
Automatically generated mesh
      84
Reciprocal lattice
    0.00000000000000    0.00000000000000    0.00000000000000             1
    0.08333333333333    0.00000000000000    0.00000000000000             6
    0.16666666666667    0.00000000000000    0.00000000000000             6
    0.25000000000000    0.00000000000000    0.00000000000000             6
    0.33333333333333    0.00000000000000    0.00000000000000             6
    0.41666666666667    0.00000000000000    0.00000000000000             6
    0.50000000000000    0.00000000000000    0.00000000000000             3
```

第三行给出倒空间坐标模式，后面的三列是 k 点坐标，最后一列是该点代表的权重。这里 Γ 点权重为 1，其他点因对称等价点数量不同而有不同权重。

```text
[bcgong@localhost fm]$ grep -A 6 'FREE ENERGIE' OUTCAR
  FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =       -16.47365594 eV

  energy  without entropy=      -16.47400754  energy(sigma->0) =      -16.47377314
```

最终自由能 TOTEN 为 −16.47365594 eV/晶胞，外推到零展宽的 `energy(sigma->0)` 为 −16.47377314 eV/晶胞。它们与 OSZICAR 的 F 和 E0 对应。比较两个计算时要选同一种能量定义，保持展宽与其他计算设置一致；不能在不同文件中各挑一个更低的数。

再看力和压力：

```text
[bcgong@localhost fm]$ grep -A 5 'POSITION ' OUTCAR
 POSITION                                       TOTAL-FORCE (eV/Angst)
 -----------------------------------------------------------------------------------
      0.00000      0.00000      0.00000        -0.000000     -0.000000     -0.000000
      1.40000      1.40000      1.40000         0.000000      0.000000      0.000000
 -----------------------------------------------------------------------------------
    total drift:                                0.000000     -0.000000      0.000000
```

```text
[bcgong@localhost fm]$ grep 'external pressure' OUTCAR
  external pressure =       56.94 kB  Pullay stress =        0.00 kB
```

两个高对称位置上的力接近零，但外压为 56.94 kbar，约 5.694 GPa。这个例子清楚地区分了电子收敛与晶胞平衡：对称性可以让原子受力抵消，固定的晶格常数仍可能远离零压位置。若要优化几何，先确定需要开放哪些自由度：只移动原子时查看 [固定晶胞结构优化](/Atlas/m/relax/)，连晶格一起调整时查看 [晶胞优化](/Atlas/m/vc-relax/)。这两处进入方法目录，各条计算路线会说明自己的程序和结构前提。

```text
[bcgong@localhost fm]$ ls -lh INCAR POSCAR KPOINTS OUTCAR OSZICAR CONTCAR IBZKPT EIGENVAL DOSCAR PROCAR CHGCAR WAVECAR vasprun.xml
-rw-rw-r-- 1 bcgong bcgong     0 Sep 22 21:38 CHGCAR
-rw-rw-r-- 1 bcgong bcgong   512 Sep 22 21:38 CONTCAR
-rw-rw-r-- 1 bcgong bcgong  153K Sep 22 21:38 DOSCAR
-rw-rw-r-- 1 bcgong bcgong   82K Sep 22 21:38 EIGENVAL
-rw-rw-r-- 1 bcgong bcgong  6.3K Sep 22 21:38 IBZKPT
-rw-rw-r-- 1 bcgong bcgong   260 Sep 22 21:38 INCAR
-rw-rw-r-- 1 bcgong bcgong    40 Sep 22 21:38 KPOINTS
-rw-rw-r-- 1 bcgong bcgong  1.8K Sep 22 21:38 OSZICAR
-rw-rw-r-- 1 bcgong bcgong  195K Sep 22 21:38 OUTCAR
-rw-rw-r-- 1 bcgong bcgong   111 Sep 22 21:38 POSCAR
-rw-rw-r-- 1 bcgong bcgong  956K Sep 22 21:38 PROCAR
-rw-rw-r-- 1 bcgong bcgong 1011K Sep 22 21:38 vasprun.xml
-rw-rw-r-- 1 bcgong bcgong     0 Sep 22 21:38 WAVECAR
```

这组文件可以按实际用途读：

| 文件 | 本例中的内容与用途 |
| --- | --- |
| INCAR / POSCAR / KPOINTS / POTCAR | 控制参数、结构、k 点和 PAW 数据四项输入 |
| OUTCAR | 完整文字日志，含有效参数、电子步、力、应力、能量、磁矩和计时 |
| OSZICAR | 电子步与每个离子步的短记录，适合运行中跟踪 |
| CONTCAR | 最后结构；本次没有离子移动，不能把文件出现当作优化成功 |
| IBZKPT | 对称性约化后的 k 点和权重 |
| EIGENVAL | 各 k 点上的本征值及占据；自旋极化时含两个通道 |
| DOSCAR | 当前取样下的态密度数据；出现文件不代表 DOS 已经过专门取样收敛 |
| PROCAR | LORBIT=11 产生的原子与轨道投影，用于后续分辨轨道成分 |
| vasprun.xml | 程序结构化输出，分析工具可从中读取参数、结构和结果 |
| CHGCAR | 本例为 0 字节，因为 LCHARG 被关闭；没有可继承的密度 |
| WAVECAR | 本例为 0 字节，因为 LWAVE 被关闭；没有可继承的波函数 |

CHGCAR 的非空内容包括结构、三维密度及 PAW 一中心信息；WAVECAR 则是波函数的二进制文件。二者用途不同，也不能只看名字是否存在。读取本例 EIGENVAL 的开头，可以看到自旋极化时的两套能量列：

```text
[bcgong@localhost fm]$ head -10 EIGENVAL
    2    2    1    2
  0.1097600E+02  0.2800000E-09  0.2800000E-09  0.2800000E-09  0.5000000E-15
  1.000000000000000E-004
  CAR 
 Fe bcc FM                               
     16     84     16
 
  0.0000000E+00  0.0000000E+00  0.0000000E+00  0.5787037E-03
    1       -2.449130     -2.285036   1.000000   1.000000
    2        1.134743      2.908667   1.000000   1.000000
```

第六行的 `16 84 16` 分别对应电子数、k 点数和带数。一个 k 点行后，带数据给出带号、两套自旋能量和两套占据；后处理时若按非自旋极化文件的列数读入，就会错列。

这次最初的短计算没有写电荷密度。之后实际运行的 `charge_elf` 目录保留了同一 Fe 结构与磁态的密度输出，可以直接核对：

```text
[bcgong@localhost charge_elf]$ grep -E 'LCHARG|LWAVE|LAECHG|LELF' INCAR
LWAVE = .FALSE.
LCHARG = .TRUE.
LAECHG = .TRUE.
LELF = .TRUE.
```

```text
[bcgong@localhost charge_elf]$ ls -lh CHGCAR WAVECAR
-rw-rw-r-- 1 bcgong bcgong 31M Sep 22 21:42 CHGCAR
-rw-rw-r-- 1 bcgong bcgong   0 Sep 22 21:42 WAVECAR
```

它开启 LCHARG 后得到非空 CHGCAR，WAVECAR 仍为空；附加的 LAECHG 和 LELF 用来写 Bader 与 ELF 所需文件，详见 [Bader](/Atlas/m/bader/vasp/) 和 [ELF](/Atlas/m/elf/vasp/)。需要复用密度时，应核对结构、赝势、泛函、自旋设置及 PAW 一中心信息的兼容性，再按后续任务设置 k 点，不能把不同磁态或不同结构的 CHGCAR 混用。

下一步若比较磁构型，接 [磁性基态候选态](/Atlas/m/magnetic-gs/vasp/)；若读真空能级，接 [功函数](/Atlas/m/workfunction/vasp/)。这些页面各自说明需要继承哪些文件，SCF 的一般读法不再重复展开。

```text
POSCAR + INCAR + KPOINTS + POTCAR
  └─ SCF 电子循环
       ├─ OSZICAR / OUTCAR → 电子收敛、能量、力与磁矩
       ├─ LCHARG 开启 → CHGCAR → 兼容的密度后处理
       └─ LWAVE 开启 → WAVECAR → 兼容的波函数重启
```
