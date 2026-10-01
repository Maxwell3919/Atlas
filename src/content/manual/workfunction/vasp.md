功函数按 Φ=Vvac−EF 定义，需要同一次计算的真空平台和电子化学势。本页对三原子 SnSe₂ 单层做固定结构 SCF，从 LOCPOT 求法向平面平均，再结合 OUTCAR 的 EF 与 EIGENVAL 的带边解释结果。SnSe₂ 是半导体，带隙内的 EF 还与占据约定有关，因此同时报告真空参考带边，避免把程序给出的一个 EF 当成唯一的材料常数。

[下载本例的输入、原始输出和分析脚本](/Atlas/examples/interface-magnet-workfunction/example-pack.tar.gz)。包内有 `LOCPOT`、`CHGCAR`、`OUTCAR`、`EIGENVAL` 和本文使用的 Python 脚本；POTCAR 只附元素标题、价电子数和哈希，需从自己的授权赝势库取得对应文件。

## 写出同一次 SCF 的势、密度和能级

固定结构 SCF 的基本操作见 [SCF](/Atlas/m/scf/vasp/)。这里保留已有计算的 POSCAR、KPOINTS 和 POTCAR，用一个新目录重新生成电荷密度：

```text
[bcgong@localhost vasp]$ mkdir snse2_workfunction
[bcgong@localhost vasp]$ cp snse2_lvhar/POSCAR snse2_lvhar/KPOINTS snse2_lvhar/POTCAR snse2_lvhar/run.slurm snse2_workfunction/
[bcgong@localhost vasp]$ cd snse2_workfunction
[bcgong@localhost snse2_workfunction]$ vi INCAR
```

`snse2_lvhar` 是同一结构的前一次计算目录。此处没有复制其中的 CHGCAR 或 WAVECAR；新的 INCAR 用 `ISTART = 0`、`ICHARG = 2` 从原子电荷开始。势与费米能由这次新的自洽计算共同产生。

```text
[bcgong@localhost snse2_workfunction]$ cat POSCAR
"Sn1 Se2"                               
   1.00000000000000     
     3.8464052687627550    0.0000000000015396    0.0000000000000001
    -1.9232026344298054    3.3310846760065127   -0.0000000000000002
     0.0000000000000007   -0.0000000000000005   18.3572978035193977
   Sn   Se
     1     2
Direct
  0.0000000000000000 -0.0000000000000000  0.5000000000000000
  0.6666666670000012  0.3333333329999988  0.5872511780709923
  0.3333333329999988  0.6666666670000012  0.4127488219290077
 
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
```

结构中一个 Sn 位于晶胞中面，两个 Se 分列其两侧；第三晶格矢量沿 z，长度约 18.3573 Å。原子集中在约 7.58–10.78 Å，因此后面检查的 1–3 Å 与 15–17 Å 位于两侧真空。真空长度是否足够仍须通过增加晶胞高度检验，这个结构先用于演示完整读数过程。

```text
[bcgong@localhost snse2_workfunction]$ cat INCAR
SYSTEM = SnSe2 self-consistent work function
ISTART = 0
ICHARG = 2
ENCUT = 520
GGA = PE
PREC = Accurate
EDIFF = 1E-7
NELM = 100
ALGO = Normal
ISMEAR = 0
SIGMA = 0.05
IVDW = 11
LREAL = .FALSE.
LASPH = .TRUE.
LORBIT = 11
LMAXMIX = 4
NCORE = 2
NSW = 0
IBRION = -1
LDIPOL = .TRUE.
IDIPOL = 3
DIPOL = 0.5 0.5 0.5
LWAVE = .FALSE.
LCHARG = .TRUE.
LVHAR = .TRUE.
```

`LVHAR = .TRUE.` 写出离子势与 Hartree 势之和；`LVTOT` 则把交换关联势也包含进去。VASP 的功函数说明推荐使用 LVHAR，因为交换关联势在真空中的衰减会影响平台读取。文件单位已经是 eV，后处理时不再除以晶胞体积。

`GGA = PE` 采用 PBE，`IVDW = 11` 对应带零阻尼函数的 DFT-D3 色散修正。D3 为总能、原子力和应力加入色散贡献；由于这里固定几何，它不会自行调整层内结构或真空高度。读取真空静电势时，仍应按本页的 LVHAR 输出和实际结构判断。

这份输入的 `ISMEAR = 0` 是 Gaussian 展宽，`SIGMA = 0.05` 以 eV 计，用于求电子占据；它不是离子温度。后文得到有带隙的解，因此费米能读数要连着占据设置解释。`ENCUT = 520` 与 `EDIFF = 1E-7` 分别控制基组范围和电子迭代残差；判断功函数是否稳定时，应比较提高截断能或收紧迭代后 `V_vac − E_F` 的变化。本例只计算了这一截断能，截断能的敏感性仍需这样比较。

这份 SnSe₂ 结构的上下两侧对称，法向净偶极应接近零；后面的两侧平台也近乎相等。这里保留了实际输入中的 `LDIPOL = .TRUE.`、`IDIPOL = 3`。非对称薄膜若有法向净偶极，三维周期边界会使它与重复的镜像相互作用，在真空中形成额外势斜率；偶极修正用于抵消这部分周期误差。薄膜自身的电荷不对称及其两侧真空势差仍可保留。[偶极修正说明](https://vasp.at/wiki/LDIPOL)

本例第三晶格矢量垂直于层，`IDIPOL = 3` 因而选中了法向；倾斜晶胞需先核对这个方向。`DIPOL = 0.5 0.5 0.5` 选在层中心，`LCHARG = .TRUE.` 保存本次自洽密度，`LWAVE = .FALSE.` 则关闭波函数写出。

`DIPOL` 的三个数是相对于晶格矢量的分数坐标，不是以 Å 为单位的位置。本例将单层放在晶胞中部，便于让两侧真空区与势的修正跳变分开；改动层的位置或真空高度后，应重新画整个势分布，再选择平台窗口，而不是保留旧窗口机械读数。

```text
[bcgong@localhost snse2_workfunction]$ cat KPOINTS
K-Spacing Value to Generate K-Mesh: 0.010
0
Gamma
  33  33   1
0.0  0.0  0.0
```

这是覆盖整个二维布里渊区的 33×33×1 均匀网格。费米能从这次均匀网格 SCF 读取，不采用能带高对称线计算报告的费米能。

前两个方向取样层内的电子态；第三方向只有一个点，对应本例以真空隔开的重复单层。网格首行只是生成工具留下的说明，VASP 真正读取的是下面的 33、33、1。加密层内网格时，需要同时跟踪带边、费米能和平台差；单独把真空方向的点数增加，不能代替层内取样检查。

```text
[bcgong@localhost snse2_workfunction]$ grep -E 'TITEL|ZVAL' POTCAR
   TITEL  = PAW_PBE Sn_d 06Sep2000
   POMASS =  118.710; ZVAL   =   14.000    mass and valenz
   TITEL  = PAW_PBE Se 06Sep2000
   POMASS =   78.960; ZVAL   =    6.000    mass and valenz
```

这套赝势每个 Sn 带 14 个价电子，每个 Se 带 6 个，因此晶胞总价电子数为 26。后面 OUTCAR 中的 NELECT 应与此相符。

```text
[bcgong@localhost snse2_workfunction]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-snse2-wf
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

本次脚本使用 8 个 MPI 进程，限时 15 分钟。

脚本里的 16–23 是这次 Slurm 分配和实际亲和性共同核验过的 CPU 编号。`unset SLURM_CPUS_PER_TASK` 只作用于启动程序的环境，用于处理此节点 Intel MPI 把它解释为 pin domain 的行为；Slurm 的 8 核资源申请仍然保留。换节点或同时存在其他任务时，应按新的分配检查实际亲和性，不能照抄这组编号。

```text
[bcgong@localhost snse2_workfunction]$ sbatch run.slurm
Submitted batch job 18191
```

作业运行时，用 `squeue -j 18191` 看状态，再用 `tail -f out` 跟踪电子步。退出 tail 的 Ctrl-C 只退出查看窗口。完成后读取调度器状态与输出末尾：

```text
[bcgong@localhost snse2_workfunction]$ scontrol show job 18191 | grep -E 'JobState=|ExitCode=|RunTime=|NumNodes='
   JobState=COMPLETED Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:01:28 TimeLimit=00:15:00 TimeMin=N/A
   NumNodes=1 NumCPUs=8 NumTasks=8 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
```

```text
[bcgong@localhost snse2_workfunction]$ tail -8 OSZICAR
DAV:  16    -0.118616121789E+02   -0.11011E-04   -0.16797E-07  4460   0.284E-03    0.893E-04
DAV:  17    -0.118616188163E+02   -0.66374E-05   -0.38095E-07  4636   0.216E-03    0.126E-03
DAV:  18    -0.118616239345E+02   -0.51182E-05   -0.15024E-07  4476   0.217E-03    0.320E-04
DAV:  19    -0.118616257043E+02   -0.17698E-05   -0.56160E-08  4528   0.662E-04    0.339E-04
DAV:  20    -0.118616260960E+02   -0.39175E-06   -0.97347E-09  4376   0.391E-04    0.116E-04
DAV:  21    -0.118616262047E+02   -0.10867E-06   -0.18647E-09  4340   0.150E-04    0.186E-05
DAV:  22    -0.118616262492E+02   -0.44434E-07   -0.62584E-10  3884   0.883E-05
   1 F= -.12268138E+02 E0= -.12268138E+02  d E =-.349964E-11
```

`DAV:` 后的第一列是电子步号，后面依次给出能量、能量变化、带能变化、迭代工作量和残差。第 22 步后出现这一离子步的 `F=`、`E0=` 汇总；因为 `NSW = 0`，这里没有离子位置优化。调度器显示 COMPLETED 还需与程序的收敛行相互印证。

```text
[bcgong@localhost snse2_workfunction]$ grep -n -E 'aborting loop|General timing|E-fermi|Elapsed time|ICHARG|LVTOT|LVHAR' OUTCAR
496:   ICHARG =      2    charge: 1-file 2-atom 10-const
584:   LVTOT        =      F    write LOCPOT, total local potential
585:   LVHAR        =      T    write LOCPOT, Hartree potential only
2304: E-fermi :  -2.4783     XC(G=0):  -3.7142     alpha+bet : -3.3624
4839:------------------------ aborting loop because EDIFF is reached ----------------------------------------
4987: General timing and accounting informations for this job:
4993:                         Elapsed time (sec):       87.188
```

输出确认 ICHARG=2，写出的势来自 LVHAR，电子循环达到了 EDIFF，文件末尾有正常计时汇总。本次程序耗时约 87.2 秒，调度器计时 88 秒。

```text
[bcgong@localhost snse2_workfunction]$ head -7 OUTCAR
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 executed on             LinuxIFC date 2026.09.22  22:13:18
 running on    8 total cores
 distrk:  each k-point on    8 cores,    1 groups
 distr:  one band on NCORES_PER_BAND=   2 cores,    4 groups
```

OUTCAR 开头记录 VASP 版本、执行时间和并行分解。中间依次能找到读入参数、k 点与带数、每次电子迭代的能量和残差、最终力与应力；末尾是电荷投影及计时。不同标签会增加额外段落，因此检查参数时用关键词定位比固定行号更可靠。

```text
[bcgong@localhost snse2_workfunction]$ grep -E 'NKPTS|NELECT|dimension x,y,z' OUTCAR
   k-points           NKPTS =    108   k-points in BZ     NKDIM =    108   number of bands    NBANDS=     20
   dimension x,y,z NGX =    30 NGY =   30 NGZ =  140
   dimension x,y,z NGXF=    60 NGYF=   60 NGZF=  280
   NELECT =      26.0000    total number of electrons
```

```text
[bcgong@localhost snse2_workfunction]$ ls -lh OUTCAR OSZICAR CHGCAR LOCPOT EIGENVAL WAVECAR
-rw-rw-r-- 1 bcgong bcgong  18M Sep 22 22:14 CHGCAR
-rw-rw-r-- 1 bcgong bcgong  77K Sep 22 22:14 EIGENVAL
-rw-rw-r-- 1 bcgong bcgong  18M Sep 22 22:14 LOCPOT
-rw-rw-r-- 1 bcgong bcgong 2.1K Sep 22 22:14 OSZICAR
-rw-rw-r-- 1 bcgong bcgong 189K Sep 22 22:14 OUTCAR
-rw-rw-r-- 1 bcgong bcgong    0 Sep 22 22:13 WAVECAR
```

OUTCAR 是详细日志；OSZICAR 是便于跟踪迭代的短日志。CHGCAR 保存本次密度及 PAW 一中心信息，可供兼容的后续固定电荷计算使用。EIGENVAL 保存本次 k 点上的本征值和占据。LOCPOT 是这一步需要读取的三维势网格。

WAVECAR 在这里为 0 字节，这是 `LWAVE = .FALSE.` 的结果，不能把它当作可重启的波函数。文件名存在不等于内容可用；若后续需要波函数，应在相应 SCF 中开启 LWAVE 并检查非空文件及兼容参数。

```text
[bcgong@localhost snse2_workfunction]$ head -16 LOCPOT
SnSe2 self-consistent work function     
   1.00000000000000     
     3.846405    0.000000    0.000000
    -1.923203    3.331085   -0.000000
     0.000000   -0.000000   18.357298
   Sn   Se
     1     2
Direct
  0.000000  0.000000  0.500000
  0.666667  0.333333  0.587251
  0.333333  0.666667  0.412749
 
   60   60  280
 0.33084600381E+01 0.33076277525E+01 0.33075776565E+01 0.33066064425E+01 0.33057828908E+01
 0.33047842371E+01 0.33060151987E+01 0.33063898923E+01 0.33069215644E+01 0.33051810740E+01
 0.33078743625E+01 0.33054753494E+01 0.33058853949E+01 0.33071917898E+01 0.33053963884E+01
```

## 沿层法向平均势并选择真空窗口

LOCPOT 的前半部分像 POSCAR：标题、缩放系数、三条晶格矢量、元素和数量、坐标。空行后出现 `60 60 280`，表示网格沿三个晶格方向各有这么多点；再往后才是势值，x 最快变化，z 最慢。总共应读到 60×60×280 = 1,008,000 个标量值。

把网格值记为 Vᵢⱼₖ，在第 k 个平面上取 V̄ₖ=ΣᵢⱼVᵢⱼₖ/(60×60)。这里的平均只消去面内 x、y 起伏，保留沿 z 的变化；没有再作沿 z 的滑动平均。对于本例的正交法向，zₖ=k×18.357298/280，k 从 0 到 279，不重复 18.357298 Å 的周期端点。对应的核心操作是：

```python
field = np.asarray(values).reshape((nz, ny, nx))
planar = field.mean(axis=(1, 2))
z = np.arange(nz) * normal_height / nz
```

`normal_height` 来自晶胞体积除以面内面积；它不是斜晶胞第三矢量长度的一概替代名称。原文件的数值已经以 eV 表示，这里没有 CHGCAR 那样的体积归一化。

下载包中的 `plane_average.py` 按这个结构读取文件，先检查网格尺寸、数值个数和有限性，再对每个 z 平面的 60×60 个值求平均。它把结果写成两列文本，而不去改动 LOCPOT：

```text
[bcgong@localhost snse2_workfunction]$ python plane_average.py LOCPOT 1:3 15:17
grid = 60 60 280; scalar values = 1008000
normal height = 18.3572980000 A; output = PLANAR_AVERAGE.dat
window 1.00:3.00 A  N=30  mean=3.306283412 eV  std=1.5602e-05 eV  range=6.06972e-05 eV
window 15.00:17.00 A  N=31  mean=3.306265353 eV  std=3.89608e-05 eV  range=0.000145996 eV
```

输出中的 `std` 是所选空间窗口内网格值的标准差，不是来自多次独立计算的误差条，也不能代替真空厚度或截断能的收敛检查。`range` 则是同一窗口内最大值减最小值；当曲线仍有系统斜率时，两者都应连着整条曲线解释。

两个冒号区间单位为 Å，表示统计 1–3 Å 和 15–17 Å 的平台。第一侧有 30 个采样平面，平均值 3.306283412 eV，最大与最小值相差约 0.0000607 eV；第二侧有 31 个平面，平均值 3.306265353 eV，起伏约 0.0001460 eV。两侧平均相差约 0.0000181 eV，与这个上下对称单层应有的近似一致平台相符。

如果窗口内势仍明显倾斜，就不应先求一个平均数再称作真空能级。先画出整个晶胞，避开原子区域、周期边界的修正跳变，并检查真空厚度和偶极修正。原旧文件使用 LVTOT，在同样的 1–3 Å、15–17 Å 区间分别有约 0.268、0.407 eV 的起伏；这正是不能只按固定窗口自动读数的例子。

```text
[bcgong@localhost snse2_workfunction]$ head -5 PLANAR_AVERAGE.dat
# z_A  planar_potential_eV
0.0000000000 3.306285072550
0.0655617786 3.306304853416
0.1311235571 3.306285038010
0.1966853357 3.306304820274
```

## 把真空平台、费米能和带边放到同一能量轴

第一列是层法向距离，第二列是平面平均势。接下来从同一份 OUTCAR 取费米能，并从 EIGENVAL 取当前均匀网格的带边。

```text
[bcgong@localhost snse2_workfunction]$ python workfunction_values.py
E_F = -2.478300 eV; VBM = -2.690722 eV; CBM = -1.923449 eV; gap = 0.767273 eV
z = 1.00:3.00 A; V_vac = 3.306283412 eV; Phi(E_F) = 5.784583412 eV; V_vac-VBM = 5.997005412 eV; V_vac-CBM = 5.229732412 eV
z = 15.00:17.00 A; V_vac = 3.306265353 eV; Phi(E_F) = 5.784565353 eV; V_vac-VBM = 5.996987353 eV; V_vac-CBM = 5.229714353 eV
```

功函数按 Φ = V_vac − E_F 计算，两个表面分别为 5.78458 与 5.78457 eV。这里的 E_F = −2.4783 eV 是本次 `ISMEAR = 0`、`SIGMA = 0.05` 计算报告的电子化学势。

这个例子有约 0.7673 eV 的 PBE 带隙。对半导体，费米能在带隙中的位置会随占据处理、掺杂和实验条件变化，因此这组 Φ 应连同所用化学势一起报告。脚本还给出真空到价带顶约 5.9970 eV、真空到导带底约 5.2297 eV；这两个带边差有助于说明所画能量参考，但仍受泛函、k 点取样和几何影响，不能作为未经收敛检验的最终材料常数。

`workfunction_values.py` 的带边读取针对本例的偶数电子、非自旋极化体系：26 个电子对应 13 条占据带，它在所有 108 个不可约 k 点上取第 13 带的最高值和第 14 带的最低值。金属、自旋极化或非共线体系需要按实际占据和数据结构处理，不能直接套用这个计数。

## 用整合脚本独立核对

上面的分步脚本用于说明每个文件怎样被读取；资料包还附有 `analyze_workfunction.py`，从原始 `LOCPOT`、`OUTCAR` 和 `EIGENVAL` 重新计算平面平均势和真空参考能级。它会验证 VASP 的 `EDIFF` 收敛标记、`LVHAR` / `LVTOT` 设置、网格大小、费米能与电子数、EIGENVAL 的 k 点权重和占据边界。输入不符合这个自旋非极化半导体示例时，脚本会报错退出，不会猜带边或自动挑一个平台。

按窗口重建的数据用于下图；完整脚本和运行命令在后面列出。

`--windows` 的数字单位是 Å，窗口均值、窗口内标准差与最大-最小差写入 `workfunction-summary.json`；同时重建两列 `PLANAR_AVERAGE.dat`。两侧平台均值相差 −0.0181 meV。

后面的分析与绘图命令在解包目录运行，需要 Python 3、NumPy 和 Matplotlib；`atlas_plot_style.py` 随包提供。整合分析重建数据，绘图脚本据此输出 PNG、SVG 与 PDF。

整胞图把下方窗口 V_vac=3.306283412 eV 选为能量零点，整条 V̄(z) 与 E_F 同时减去这个数，Φ 因而保持不变。图上显示 1–3 Å 与 15–17 Å 的真空取样窗口、POSCAR 中原子 z 坐标覆盖范围、平面平均 LVHAR 势及费米能；Φ 箭头标出实际读取的能量间隔。

原子区势阱低于真空平台。结合原子位置，可检查窗口是否远离原子层，并从同一能量轴读取平台到费米能的间隔。

![SnSe₂ 整胞平面平均 LVHAR 势、真空窗口、原子层范围及费米能标记](/Atlas/examples/interface-magnet-workfunction/interface-magnet-workfunction-profile.svg)

## 真空参考与界面分析

Zhang, Li, Tang, and Cao, “Robust p-type ohmic contact in ZrI₂–Dirac semi-metal van der Waals heterostructures,” *Physical Chemistry Chemical Physics* **27**, 19410 (2025), Fig. 4–5, [DOI: 10.1039/D5CP02349A](https://doi.org/10.1039/D5CP02349A)。正文说明作者对六种半导体 / 半金属接触计算沿 z 的平面平均静电势（Fig. 4），结合两种材料的功函数差讨论电子转移及内建电场方向；随后用三维和一维平面平均差分电荷（Fig. 5）检验界面电荷累积、耗尽的位置。Fig. 4 中势曲线与法向位置、真空和费米能参考共同展示，方便解释界面势变化。

沿 z 检查完整势曲线，并把真空与 E_F 放在同一参考下，是单层功函数和界面势分析的共同步骤。本例的图来自孤立 SnSe₂ 的 LOCPOT、OUTCAR 和 POSCAR；继续分析接触后的电荷重排，需要完整界面的密度和势。

## 从原始文件重建结果

分析程序先检查电子收敛与势文件格式，再对指定真空窗口取平均，把 E_F 和采样带边一起减去同一个 V_vac。绘图读取这些结果和原子法向范围。可以把这些读取规则写成下面的请求：

```text
请为 VASP 5.4.4 的这个非自旋极化 SnSe2 单层示例编写独立 Python 3 命令行分析脚本。输入为当前目录中的 LOCPOT、OUTCAR、EIGENVAL；用户可用 --windows LOW:HIGH 指定一个或多个以 Å 为单位的真空窗口。

LOCPOT 是 POSCAR 头部、三维网格尺寸 nx ny nz 和一个标量势块；该势以 eV 为单位，x 方向变化最快。校验势值数量正好为 nx*ny*nz 且均为有限数，把数组按 (nz,ny,nx) 重排；用每个 xy 平面的算术平均求 Vbar(z)，z_k=k*h/nz，其中 h=abs(c·(a×b))/|a×b|，坐标单位为 Å。

从 OUTCAR 读取 NELECT 和 E-fermi，并确认输出出现 EDIFF 收敛标记、LVHAR=T、LVTOT=F 和 ISPIN=1。解析 EIGENVAL 中的 k 点权重、本征值和占据数；权重和与按权重汇总的电子数分别在 1e-5 和 1e-3 容差内匹配 1 与 NELECT。按 NELECT/2 确定边界，要求所有 k 点的第 13 带占据不低于 0.5、第 14 带不高于 0.5，再检查采样 CBM 高于 VBM。若输入是自旋极化、金属、缺少数据或格式不支持，清楚报错退出，禁止假定费米能、猜测带边、补零或静默接受坏数据。

每个窗口输出采样平面数、Vbar 均值、总体标准差、最大值减最小值，以及 Phi=Vvac-EF、IP=Vvac-VBM、EA=Vvac-CBM。VBM/CBM 只报 EIGENVAL 当前 k 网格采样值。输出 PLANAR_AVERAGE.dat（z_A, planar_potential_eV）和带有输入 SHA256、单位、公式、窗口数据及限制说明的 workfunction-summary.json。

另写单面板绘图脚本，读取上述文件并导出 PNG、SVG、PDF。显示完整晶胞势曲线、费米能、POSCAR 原子层法向范围和被统计的真空窗口；用下方 Vvac 作为唯一能量零点。图注注明 VASP 版本、网格、窗口、E_F 约定和本结果尚未验证的收敛项。不要用平滑、插值或拟合隐藏势斜率，也不要另行放大 −0.0181 meV 的两侧均值差；窗口不平坦时报告诊断，不要把标准差包装成收敛误差。
```

完整源码：[analyze_workfunction.py](/Atlas/examples/interface-magnet-workfunction/analyze_workfunction.py) · [plot_workfunction.py](/Atlas/examples/interface-magnet-workfunction/plot_workfunction.py) · [plane_average.py](/Atlas/examples/interface-magnet-workfunction/plane_average.py) · [workfunction_values.py](/Atlas/examples/interface-magnet-workfunction/workfunction_values.py) · [atlas_plot_style.py](/Atlas/examples/interface-magnet-workfunction/atlas_plot_style.py)。数值输出：[workfunction-summary.json](/Atlas/examples/interface-magnet-workfunction/workfunction-summary.json)。

<details>
<summary>analyze_workfunction.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Rebuild planar potential and vacuum-referenced levels from VASP outputs.

Required files in the current directory: LOCPOT, OUTCAR, EIGENVAL.
The reader is intentionally restricted to a non-spin-polarized, gapped,
single-scalar LOCPOT case. It rejects unsupported inputs instead of guessing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np

A = np.asarray


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_locpot(path: Path):
    lines = path.read_text(errors="strict").splitlines()
    if len(lines) < 10:
        raise ValueError("LOCPOT is too short to contain a POSCAR header and grid")
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError("This example reader requires a positive POSCAR scale")
    cell = A([[float(x) * scale for x in lines[i].split()[:3]]
              for i in (2, 3, 4)], dtype=float)
    index = 5
    species_or_counts = lines[index].split()
    index += 1
    if all(re.fullmatch(r"\d+", word) for word in species_or_counts):
        counts = [int(word) for word in species_or_counts]
    else:
        counts = [int(word) for word in lines[index].split()]
        index += 1
    mode = lines[index].strip().lower()
    index += 1
    if mode.startswith("s"):
        mode = lines[index].strip().lower()
        index += 1
    if not (mode.startswith("d") or mode.startswith("c") or mode.startswith("k")):
        raise ValueError(f"Unrecognized coordinate mode in LOCPOT header: {mode!r}")
    natoms = sum(counts)
    if natoms <= 0:
        raise ValueError("Invalid atom counts in LOCPOT header")
    index += natoms
    while index < len(lines) and not lines[index].strip():
        index += 1
    grid = tuple(map(int, lines[index].split()))
    index += 1
    if len(grid) != 3 or min(grid) <= 0:
        raise ValueError(f"Invalid LOCPOT grid dimensions: {grid}")
    nx, ny, nz = grid
    expected = nx * ny * nz
    fields = []
    for line in lines[index:]:
        fields.extend(float(token.replace("D", "E").replace("d", "e"))
                      for token in line.split())
    if len(fields) != expected:
        raise ValueError(
            f"Expected one scalar potential block ({expected} values), found {len(fields)}"
        )
    values = np.asarray(fields, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("LOCPOT contains non-finite potential values")
    normal = np.cross(cell[0], cell[1])
    area = np.linalg.norm(normal)
    if area == 0:
        raise ValueError("The first two lattice vectors do not span a surface")
    normal_height = abs(float(np.dot(cell[2], normal))) / area
    if normal_height <= 0:
        raise ValueError("Invalid cell height along the surface normal")
    # VASP writes x fastest, then y, with z as the slowest index.
    field = values.reshape((nz, ny, nx))
    planar = field.mean(axis=(1, 2))
    z = np.arange(nz, dtype=float) * normal_height / nz
    return grid, normal_height, z, planar


def outcar_values(path: Path):
    text = path.read_text(errors="strict")
    if "aborting loop because EDIFF is reached" not in text:
        raise ValueError("OUTCAR has no EDIFF convergence marker")
    if "General timing and accounting" not in text:
        raise ValueError("OUTCAR has no final timing/accounting section")
    if "LVHAR" not in text or not re.search(r"LVHAR\s*=\s*T\b", text):
        raise ValueError("OUTCAR does not confirm LVHAR=T")
    if re.search(r"LVTOT\s*=\s*T\b", text):
        raise ValueError("OUTCAR also has LVTOT=T; this route expects LVHAR only")
    ispin = re.findall(r"^\s*ISPIN\s*=\s*(\d+)", text, flags=re.M)
    nelect = re.findall(r"^\s*NELECT\s*=\s*([-+0-9.]+)", text, flags=re.M)
    efermi = re.findall(r"E-fermi\s*:\s*([-+0-9.]+)", text)
    if not ispin or int(ispin[-1]) != 1:
        raise ValueError("This band-edge reader requires a non-spin-polarized ISPIN=1 run")
    if not nelect or not efermi:
        raise ValueError("OUTCAR is missing NELECT or E-fermi")
    return int(round(float(nelect[-1]))), float(efermi[-1])


def read_eigenval(path: Path, expected_electrons: int):
    with path.open() as stream:
        for _ in range(5):
            if not stream.readline():
                raise ValueError("EIGENVAL ended before its electron/k-point/band header")
        try:
            electrons, nkpoints, nbands = map(int, stream.readline().split())
        except Exception as exc:
            raise ValueError("Invalid EIGENVAL electron/k-point/band header") from exc
        if electrons != expected_electrons:
            raise ValueError(
                f"EIGENVAL has {electrons} electrons but OUTCAR has {expected_electrons}"
            )
        if electrons % 2:
            raise ValueError("An even electron count is required for this ISPIN=1 example")
        nocc = electrons // 2
        if not (0 < nocc < nbands):
            raise ValueError("EIGENVAL does not contain both occupied and empty bands")
        k_weights, energies, occupations = [], [], []
        for _ in range(nkpoints):
            line = stream.readline()
            while line and not line.strip():
                line = stream.readline()
            if not line:
                raise ValueError("EIGENVAL ended before all k-point blocks were read")
            point = list(map(float, line.split()))
            if len(point) != 4:
                raise ValueError("Expected kx ky kz weight on each EIGENVAL k-point line")
            k_weights.append(point[3])
            e_k, occ_k = [], []
            for _ in range(nbands):
                row = stream.readline().split()
                if len(row) != 3:
                    raise ValueError("Expected band index, energy, and occupation (ISPIN=1)")
                band_index, energy, occupation = map(float, row)
                e_k.append(energy)
                occ_k.append(occupation)
            energies.append(e_k)
            occupations.append(occ_k)
    weights = np.asarray(k_weights, dtype=float)
    eigenvalues = np.asarray(energies, dtype=float)
    occ = np.asarray(occupations, dtype=float)
    if abs(float(weights.sum()) - 1.0) > 1e-5:
        raise ValueError(f"EIGENVAL k-point weights sum to {weights.sum():.8g}, not 1")
    weighted_electrons = 2.0 * float(np.sum(weights[:, None] * occ))
    if abs(weighted_electrons - expected_electrons) > 1e-3:
        raise ValueError(
            f"Weighted EIGENVAL occupations give {weighted_electrons:.8f} electrons, "
            f"not {expected_electrons}"
        )
    if float(occ[:, nocc - 1].min()) < 0.5 or float(occ[:, nocc].max()) > 0.5:
        raise ValueError(
            "The NELECT/2 band boundary is partially occupied; this is not a gapped "
            "non-spin-polarized case"
        )
    vbm = float(eigenvalues[:, nocc - 1].max())
    cbm = float(eigenvalues[:, nocc].min())
    if cbm <= vbm:
        raise ValueError("Sampled EIGENVAL band edges do not form a positive gap")
    return {
        "electrons": electrons,
        "nkpoints": nkpoints,
        "bands": nbands,
        "weighted_electrons": weighted_electrons,
        "vbm_eV": vbm,
        "cbm_eV": cbm,
        "indirect_gap_eV": cbm - vbm,
    }


def parse_window(spec: str):
    try:
        low, high = map(float, spec.split(":"))
    except Exception as exc:
        raise argparse.ArgumentTypeError("Use a window such as 1:3 (angstrom)") from exc
    if not (math.isfinite(low) and math.isfinite(high) and low < high):
        raise argparse.ArgumentTypeError("Window endpoints must be finite with low < high")
    return low, high


def main():
    parser = argparse.ArgumentParser(
        description="Average LVHAR from LOCPOT and align the gapped band edges to vacuum."
    )
    parser.add_argument(
        "--windows", nargs="+", type=parse_window, default=[(1.0, 3.0), (15.0, 17.0)],
        metavar="LOW:HIGH", help="vacuum windows in angstrom (default: 1:3 15:17)"
    )
    args = parser.parse_args()
    if not args.windows:
        raise ValueError("At least one vacuum window is required")
    loct = Path("LOCPOT")
    outcar = Path("OUTCAR")
    eigenval = Path("EIGENVAL")
    if not all(path.is_file() for path in (loct, outcar, eigenval)):
        raise FileNotFoundError("Run in a directory containing LOCPOT, OUTCAR, EIGENVAL")

    grid, height, z, potential = read_locpot(loct)
    nelect, ef = outcar_values(outcar)
    bands = read_eigenval(eigenval, nelect)
    windows = []
    for low, high in args.windows:
        if low < 0 or high > height:
            raise ValueError(
                f"Window {low:g}:{high:g} A lies outside 0:{height:.8f} A"
            )
        chosen = (z >= low) & (z <= high)
        values = potential[chosen]
        if values.size == 0:
            raise ValueError(f"Window {low:g}:{high:g} A contains no LOCPOT planes")
        mean = float(values.mean())
        row = {
            "lo_A": low, "hi_A": high, "n": int(values.size),
            "mean_eV": mean,
            "std_eV": float(values.std(ddof=0)),
            "range_eV": float(values.max() - values.min()),
            "vacuum_minus_fermi_eV": mean - ef,
            "vacuum_minus_vbm_eV": mean - bands["vbm_eV"],
            "vacuum_minus_cbm_eV": mean - bands["cbm_eV"],
        }
        windows.append(row)

    order = sorted(windows, key=lambda item: item["lo_A"])
    for left, right in zip(order, order[1:]):
        if left["hi_A"] > right["lo_A"]:
            raise ValueError("Vacuum windows overlap")

    np.savetxt(
        "PLANAR_AVERAGE.dat", np.column_stack((z, potential)),
        fmt=("%.10f", "%.12f"),
        header="z_A  planar_potential_eV",
        comments="# ",
    )
    result = {
        "code": "VASP",
        "potential_component": "LVHAR (ionic + Hartree; LVTOT is false)",
        "surface_normal": "normal to lattice vectors a and b",
        "normal_height_A": height,
        "grid": list(grid),
        "scalar_values": int(np.prod(grid)),
        "ispin": 1,
        "electrons": nelect,
        "nkpoints": bands["nkpoints"],
        "bands": bands["bands"],
        "weighted_electrons": bands["weighted_electrons"],
        "fermi_eV": ef,
        "vbm_eV": bands["vbm_eV"],
        "cbm_eV": bands["cbm_eV"],
        "indirect_gap_eV": bands["indirect_gap_eV"],
        "formula": {
            "work_function_eV": "V_vacuum - E_F",
            "ionization_potential_eV": "V_vacuum - VBM",
            "electron_affinity_eV": "V_vacuum - CBM",
            "potential_spread_eV": "max(Vbar) - min(Vbar) within each selected window",
        },
        "windows": windows,
        "input_sha256": {
            path.name: sha256(path) for path in (loct, outcar, eigenval)
        },
        "limits": [
            "EIGENVAL band edges are extrema on the sampled SCF k mesh, not a continuous-Brillouin-zone search.",
            "E_F in a semiconductor is the chemical potential printed for this occupation setup; it can move within the gap.",
            "Window spread is a local flatness diagnostic, not an uncertainty or convergence estimate.",
        ],
    }
    Path("workfunction-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(
        f"grid={grid}; scalar values={int(np.prod(grid))}; normal height={height:.10f} A"
    )
    print(
        f"NELECT={nelect}; NKPTS={bands['nkpoints']}; weighted electrons="
        f"{bands['weighted_electrons']:.8f}; E_F={ef:.6f} eV"
    )
    print(
        f"sampled VBM={bands['vbm_eV']:.6f} eV; CBM={bands['cbm_eV']:.6f} eV; "
        f"gap={bands['indirect_gap_eV']:.6f} eV"
    )
    for item in windows:
        print(
            f"z={item['lo_A']:.2f}:{item['hi_A']:.2f} A N={item['n']} "
            f"V_vac={item['mean_eV']:.9f} eV std={item['std_eV']:.6g} eV "
            f"range={item['range_eV']:.6g} eV Phi={item['vacuum_minus_fermi_eV']:.9f} eV"
        )


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>plot_workfunction.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Plot the actual full-cell planar LVHAR profile used to inspect the vacuum plateau."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from atlas_plot_style import install

install()


def poscar_atomic_extent(path: Path, normal_height: float, normal: np.ndarray) -> tuple[float, float]:
    """Return the z extent of atomic coordinates projected along the cell normal."""
    lines = path.read_text().splitlines()
    scale = float(lines[1].split()[0])
    cell = np.asarray([[float(x) for x in lines[i].split()[:3]] for i in (2, 3, 4)]) * scale
    i = 5
    fields = lines[i].split()
    i += 1
    if all(word.lstrip("+").isdigit() for word in fields):
        counts = [int(word) for word in fields]
    else:
        counts = [int(word) for word in lines[i].split()]
        i += 1
    if lines[i].strip().lower().startswith("s"):
        i += 1
    mode = lines[i].strip().lower()
    i += 1
    coordinates = np.asarray([
        [float(x) for x in lines[i + j].split()[:3]]
        for j in range(sum(counts))
    ])
    if mode.startswith("d"):
        cartesian = coordinates @ cell
    elif mode.startswith(("c", "k")):
        cartesian = coordinates * scale
    else:
        raise ValueError(f"Unsupported POSCAR coordinate mode: {mode!r}")
    z = np.mod(cartesian @ normal, normal_height)
    return float(z.min()), float(z.max())


profile_path = Path("PLANAR_AVERAGE.dat")
summary_path = Path("workfunction-summary.json")
if not profile_path.is_file() or not summary_path.is_file():
    raise FileNotFoundError("Run analyze_workfunction.py first")

profile = np.loadtxt(profile_path, comments="#")
summary = json.loads(summary_path.read_text())
windows = sorted(summary["windows"], key=lambda item: item["lo_A"])
if profile.ndim != 2 or profile.shape[1] != 2:
    raise ValueError("Expected z_A and planar_potential_eV columns")
if len(windows) != 2:
    raise ValueError("This example expects its two measured surface vacuum windows")
z, potential = profile[:, 0], profile[:, 1]
height = float(summary["normal_height_A"])
if not np.all(np.isfinite(profile)) or z.max() >= height:
    raise ValueError("Profile contains invalid values or an out-of-cell z coordinate")

cell = np.asarray([[float(x) for x in line.split()[:3]]
                   for line in Path("POSCAR").read_text().splitlines()[2:5]], dtype=float)
scale = float(Path("POSCAR").read_text().splitlines()[1].split()[0])
cell *= scale
normal = np.cross(cell[0], cell[1])
normal /= np.linalg.norm(normal)
if np.dot(cell[2], normal) < 0:
    normal *= -1.0
atom_lo, atom_hi = poscar_atomic_extent(Path("POSCAR"), height, normal)

vacuum_reference = float(windows[0]["mean_eV"])
relative_potential = potential - vacuum_reference
fermi_relative = float(summary["fermi_eV"]) - vacuum_reference
work_function = vacuum_reference - float(summary["fermi_eV"])
colors = ("#0072b2", "#d55e00")

fig, ax = plt.subplots(figsize=(8.1, 4.8), layout="constrained")
ax.plot(z, relative_potential, color="#222222", lw=1.25,
        label=r"Planar-averaged $V_{\mathrm{LVHAR}}(z)$")
ax.axhline(0.0, color=colors[0], ls="--", lw=1.0,
           label="Lower-z vacuum reference")
ax.axhline(fermi_relative, color=colors[1], ls="-.", lw=1.0,
           label=r"$E_F$ from the same SCF")
ax.axvspan(atom_lo, atom_hi, color="#777777", alpha=0.12, zorder=0)
for window in windows:
    ax.axvspan(window["lo_A"], window["hi_A"], color=colors[0], alpha=0.08, zorder=0)

handles = [
    Line2D([0], [0], color="#222222", lw=1.25,
           label=r"Planar-averaged $V_{\mathrm{LVHAR}}(z)$"),
    Line2D([0], [0], color=colors[0], ls="--", lw=1.0,
           label="Lower-z vacuum reference"),
    Line2D([0], [0], color=colors[1], ls="-.", lw=1.0,
           label=r"$E_F$ from the same SCF"),
    Patch(facecolor="#777777", alpha=0.12, label="Atomic z extent from POSCAR"),
    Patch(facecolor=colors[0], alpha=0.08, label="Vacuum windows used in the table"),
]
ax.legend(handles=handles, frameon=False, ncols=2, loc="lower left")
arrow_x = 2.55
ax.annotate(
    "", xy=(arrow_x, fermi_relative), xytext=(arrow_x, 0.0),
    arrowprops={"arrowstyle": "<->", "color": colors[1], "lw": 1.1},
)
ax.text(arrow_x + 0.22, 0.5 * fermi_relative,
        rf"$\Phi={work_function:.4f}\ \mathrm{{eV}}$",
        color=colors[1], ha="left", va="center")

span = float(relative_potential.max() - relative_potential.min())
ax.set_xlim(0.0, height)
ax.set_ylim(relative_potential.min() - 0.04 * span,
            relative_potential.max() + 0.04 * span)
ax.set_xlabel("Distance along the surface normal (Å)")
ax.set_ylabel(r"$\bar{V}(z)-V_{\mathrm{vac,lower}}$ (eV)")
ax.set_title(r"SnSe$_2$ monolayer: planar-averaged LVHAR and work-function reference")
ax.grid(False)

output = "interface-magnet-workfunction-profile.png"
fig.savefig(output)
plt.close(fig)

upper_minus_lower = float(windows[1]["mean_eV"] - windows[0]["mean_eV"])
print(f"Wrote interface-magnet-workfunction-profile.png, .svg, and .pdf")
print(f"Lower-z Vvac = {vacuum_reference:.9f} eV; E_F = {summary['fermi_eV']:.6f} eV")
print(f"Phi at the printed E_F = {work_function:.9f} eV")
print(f"Upper-minus-lower vacuum mean = {upper_minus_lower * 1000.0:+.5f} meV")
print("That last difference is reported numerically only; it is not resolved as a material effect.")
```

</details>

<details>
<summary>plane_average.py 的完整源码</summary>

```python
from __future__ import print_function
import sys, math, json, hashlib

def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def read_grid(name):
    f=open(name)
    title=f.readline().strip()
    scale=float(f.readline().split()[0])
    cell=[[float(x)*scale for x in f.readline().split()[:3]] for i in range(3)]
    if scale <= 0: raise ValueError('This reader requires a positive POSCAR scale')
    words=f.readline().split()
    if all(x.isdigit() for x in words):
        counts=list(map(int,words))
    else:
        counts=list(map(int,f.readline().split()))
    mode=f.readline().strip()
    if mode.lower().startswith('s'): mode=f.readline().strip()
    coords=[f.readline().split()[:3] for i in range(sum(counts))]
    line=f.readline()
    while line and not line.strip(): line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0: raise ValueError('Invalid FFT grid')
    n=grid[0]*grid[1]*grid[2]
    vals=[]
    while len(vals)<n:
        line=f.readline()
        if not line: raise ValueError('Truncated potential: %d/%d'%(len(vals),n))
        vals.extend(float(x.replace('D','E')) for x in line.split())
    if len(vals)!=n: raise ValueError('Unexpected extra values in scalar block')
    f.close()
    if any(math.isnan(x) or math.isinf(x) for x in vals):
        raise ValueError("Non-finite potential value")
    return cell,grid,vals

if __name__=='__main__':
    name=sys.argv[1] if len(sys.argv)>1 else 'LOCPOT'
    cell,grid,v=read_grid(name)
    area=math.sqrt(dot(cross(cell[0],cell[1]),cross(cell[0],cell[1])))
    height=abs(dot(cell[2],cross(cell[0],cell[1])))/area
    nxy=grid[0]*grid[1]
    avg=[sum(v[i*nxy:(i+1)*nxy])/nxy for i in range(grid[2])]
    zz=[height*i/grid[2] for i in range(grid[2])]
    with open('PLANAR_AVERAGE.dat','w') as f:
        f.write('# z_A  planar_potential_eV\n')
        for z,p in zip(zz,avg): f.write('%.10f %.12f\n'%(z,p))
    summary={'grid':grid,'points':len(v),'normal_height_A':height,'source_sha256':hashlib.sha256(open(name,'rb').read()).hexdigest(),'windows':[]}
    print('grid = %d %d %d; scalar values = %d'%tuple(grid+[len(v)]))
    print('normal height = %.10f A; output = PLANAR_AVERAGE.dat'%height)
    for spec in sys.argv[2:]:
        lo,hi=map(float,spec.split(':'))
        a=[p for z,p in zip(zz,avg) if lo<=z<=hi]
        if not a: raise ValueError('Empty averaging window')
        mean=sum(a)/len(a); std=math.sqrt(sum((x-mean)**2 for x in a)/len(a)); span=max(a)-min(a)
        row={'lo_A':lo,'hi_A':hi,'n':len(a),'mean_eV':mean,'std_eV':std,'range_eV':span}
        summary['windows'].append(row)
        print('window %.2f:%.2f A  N=%d  mean=%.9f eV  std=%.6g eV  range=%.6g eV'%(lo,hi,len(a),mean,std,span))
    with open('potential-summary.json','w') as f: json.dump(summary,f,indent=2,sort_keys=True)
```

</details>

<details>
<summary>workfunction_values.py 的完整源码</summary>

```python
from __future__ import print_function
import json,re,hashlib
out=open('OUTCAR').read()
if 'aborting loop because EDIFF is reached' not in out:
    raise ValueError('Electronic convergence line is absent')
if 'General timing and accounting' not in out:
    raise ValueError('Normal final accounting section is absent')
ef=float(re.findall(r'E-fermi\s*:\s*([-+0-9.]+)',out)[-1])
p=json.load(open('potential-summary.json'))
with open('EIGENVAL') as f:
    for i in range(5): f.readline()
    ne,nk,nb=map(int,f.readline().split())
    if ne % 2: raise ValueError('This band-edge reader expects even-electron, non-spin-polarized input')
    occupied=[];empty=[]
    for ik in range(nk):
        line=f.readline()
        while line and not line.strip(): line=f.readline()
        if not line: raise ValueError('Truncated EIGENVAL before k point')
        if len(line.split())!=4: raise ValueError('Invalid k-point line')
        bands=[list(map(float,f.readline().split())) for ib in range(nb)]
        if any(len(row)!=3 for row in bands): raise ValueError('Invalid or truncated non-spin EIGENVAL band block')
        occupied.append(bands[ne//2-1][1]);empty.append(bands[ne//2][1])
vbm=max(occupied);cbm=min(empty)
r={'fermi_eV':ef,'vbm_eV':vbm,'cbm_eV':cbm,'indirect_gap_eV':cbm-vbm,'nkpoints':nk,'bands':nb,'electrons':ne,'windows':[]}
for w in p['windows']:
    item=dict(w)
    item['vacuum_minus_fermi_eV']=w['mean_eV']-ef
    item['vacuum_minus_vbm_eV']=w['mean_eV']-vbm
    item['vacuum_minus_cbm_eV']=w['mean_eV']-cbm
    r['windows'].append(item)
json.dump(r,open('workfunction-summary.json','w'),indent=2)
print('E_F = %.6f eV; VBM = %.6f eV; CBM = %.6f eV; gap = %.6f eV'%(ef,vbm,cbm,cbm-vbm))
for w in r['windows']:
    print('z = %.2f:%.2f A; V_vac = %.9f eV; Phi(E_F) = %.9f eV; V_vac-VBM = %.9f eV; V_vac-CBM = %.9f eV'%(w['lo_A'],w['hi_A'],w['mean_eV'],w['vacuum_minus_fermi_eV'],w['vacuum_minus_vbm_eV'],w['vacuum_minus_cbm_eV']))
```

</details>

解包后进入 `example-pack`，在有 Python 3、NumPy 和 Matplotlib 的环境运行：

```bash
python3 analyze_workfunction.py --windows 1:3 15:17
python3 plot_workfunction.py
```

本次读取的下侧平台为 3.306283412 eV，Φ 为 5.784583412 eV；上侧平台为 3.306265353 eV，Φ 为 5.784565353 eV。两列势数据写入 `PLANAR_AVERAGE.dat`，窗口和能级写入 `workfunction-summary.json`，绘图脚本据此生成前面的整胞势图。

```text
固定结构 + 同一套赝势 / 均匀 k 网格
  └─ SCF + LVHAR
       ├─ OUTCAR → 收敛与 E_F
       ├─ EIGENVAL → 当前网格的 VBM / CBM
       └─ LOCPOT → 平面平均 → 平坦真空窗口
                                    └─ V_vac − E_F；同时注明带隙中的化学势
```

相关输入说明：[VASP：功函数](https://vasp.at/wiki/Computing_the_work_function) · [LVHAR](https://vasp.at/wiki/LVHAR) · [LOCPOT](https://vasp.at/wiki/LOCPOT) · [LDIPOL](https://vasp.at/wiki/LDIPOL)

下一步接 [能带对齐](/Atlas/m/band-alignment/vasp/)。把两个材料放到同一能量参考前，需要分别取得它们自己的真空势和带边；不能直接比较两个计算各自打印的 `E_F`。若只需要三维势和平面平均的文件读法，接 [静电势](/Atlas/m/electrostatic-potential/vasp/)。
