[VASP：CHGCAR 文件结构](https://vasp.at/wiki/CHGCAR) · [VASP：细 FFT 网格 NGXF](https://vasp.at/wiki/NGXF) · [VASP：初始磁矩 MAGMOM](https://vasp.at/wiki/MAGMOM)

把两个 H 原子放在一起，成键后哪些地方的电子密度增加了，哪些地方减少了？这里用一个固定键长的 H₂ 小体系，把同一晶胞中的三份真实计算连起来：完整分子 AB，以及在原位置各保留一个 H 的 A、B。

```text
Δn(r) = n_AB(r) − n_A(r) − n_B(r)
```

这里的 n 是电子数密度，正值表示相对于冻结原子参考的电子积累，负值表示电子耗尽。它不是带负号的电荷密度 −en；也不能把正值区域的积分直接当成从一个 H 转移给另一个 H 的电子数。

[下载输入、小体积原始输出、分析与绘图脚本](/Atlas/examples/h2-delta-charge-files.tar.gz)，解压为 `h2-delta-charge`。三份密度单独提供：[AB/CHGCAR.gz](/Atlas/examples/h2-delta-charge/AB/CHGCAR.gz)、[A/CHGCAR.gz](/Atlas/examples/h2-delta-charge/A/CHGCAR.gz)、[B/CHGCAR.gz](/Atlas/examples/h2-delta-charge/B/CHGCAR.gz)。分别放回解压目录的 AB、A、B 子目录，保留文件名 `CHGCAR.gz`，解析程序可以直接读取，不必先解压。只重新画图时，包内 CSV 已经足够。POTCAR 正文不随包分发；重新运行 VASP 需要自行准备有使用权限的同一份 H 赝势，并核对包内指纹。

## 三份结构，保留同一个坐标系

本例人为构造一个边长 10 Å 的立方晶胞，两个 H 在 (5,5,4.63) 和 (5,5,5.37) Å，键长 0.74 Å。本轮没有优化这个键长，它只是用来观察成键电子密度的明确几何。对照原子保持在分子里的位置，删去另一个原子后没有移到原点，也没有单独弛豫。

下面是现场直接读回的三个 POSCAR：

```console
[bcgong@localhost grid144]$ cat AB/POSCAR A/POSCAR B/POSCAR
H2 charge difference AB
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
2
Cartesian
5.000000 5.000000 4.630000
5.000000 5.000000 5.370000

H2 charge difference A
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
1
Cartesian
5.000000 5.000000 4.630000

H2 charge difference B
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
1
Cartesian
5.000000 5.000000 5.370000
[bcgong@localhost grid144]$
```

三份晶胞矩阵完全相同；AB 有两个原子，A 和 B 各一个。不同原子数会让 CHGCAR 的结构头长度不同，所以不能按同一个固定行号跳过表头，然后直接相减整个文本。

## 先让电子协议和 FFT 网格一致

这一轮重新计算的目录叫 `grid144`。完整分子实际使用的输入为：

```console
[bcgong@localhost grid144]$ cat AB/INCAR
SYSTEM = H2 fixed geometry charge difference
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 100
ALGO = Normal
ISMEAR = 0
SIGMA = 0.02
ISPIN = 2
MAGMOM = 1 -1
ISYM = 0
NBANDS = 8
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
LMAXMIX = 2
NCORE = 1
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .TRUE.
NGX = 72
NGY = 72
NGZ = 72
NGXF = 144
NGYF = 144
NGZF = 144
[bcgong@localhost grid144]$
```

`ISTART=0`、`ICHARG=2` 让三项各自从原子叠加电荷开始做自洽。这里需要的是三个独立自洽结果，不能把 AB 的密度直接复制成 A、B 的最终密度。`IBRION=-1`、`NSW=0` 保持结构不动。

三项统一使用 400 eV 截断、`PREC=Accurate`、Gaussian 展宽 `SIGMA=0.02 eV` 和 `EDIFF=1E-8 eV`。相同设置是逐点相减的前提；这个例子没有额外扫描截断、盒长与展宽，所以不把这些数当成所有分子的推荐收敛值。

`ISPIN=2` 让单个 H 可以得到一个未配对电子。A 的初始 `MAGMOM=1`，B 为 `−1`，分子为 `1 -1`；除了 `SYSTEM` 和 `MAGMOM`，三份 INCAR 的电子参数逐项一致。MAGMOM 是初始条件，最终磁矩还要从输出和密度积分验证，不能只按输入预期填写。

`LCHARG=.TRUE.` 写出后面要相减的 CHGCAR。`LWAVE=.FALSE.` 关闭波函数写出；本次目录内的 WAVECAR 是零字节文件，不能拿它当成可用重启文件。`LREAL=.FALSE.` 在倒空间处理投影，`LASPH=.TRUE.` 保留 PAW 球内非球形贡献；这些选择在三份输入中保持一致。

密度使用 144×144×144 的细网格，粗网格为 72×72×72。这两套网格各有用途，不能只保证最终 CHGCAR 的行数一致，却忽略电子计算本身的网格警告。

本例前一次 48³/96³ 尝试虽然结束并写出了密度，OUTCAR 仍明确提醒：

```console
[bcgong@localhost grid144]$ grep -A 8 -B 2 "Your FFT grids" ../AB/OUTCAR
|           W    W  A    A  R    R  N    N  II  N    N   GGGG   !!!           |
|                                                                             |
|      Your FFT grids (NGX,NGY,NGZ) are not sufficient for an accurate        |
|      calculation.                                                           |
|      The results might be wrong                                             |
|      good settings for NGX NGY and  NGZ are                                 |
|                        70  70  and  70                                      |
|     Mind: This setting results in a small but reasonable wrap around error  |
|     It is also necessary to adjust these  values to the FFT routines you use|
|                                                                             |
 -----------------------------------------------------------------------------
[bcgong@localhost grid144]$
```

因此这次把三项一起改为 72³/144³ 后重新计算。这个处理修复了程序明确报告的网格不足；它不是已经完成系统性的网格收敛测试。旧尝试没有被混进下面三份密度中。

孤立分子用大盒子与 Γ 点作周期近似，实际 KPOINTS 为：

```console
[bcgong@localhost grid144]$ cat AB/KPOINTS
Gamma for an isolated molecule in a periodic box
0
Gamma
1 1 1
0 0 0
[bcgong@localhost grid144]$
```

盒长仍需按研究问题检查。仅仅用了 Γ 点和 10 Å 晶胞，并不自动证明周期镜像效应可以忽略。

## 三份 SCF 串行完成，再读输出

AB 的真实提交脚本如下。此现场用 4 个 MPI 进程；A、B 脚本对应各自目录，电子参数不变。

```console
[bcgong@localhost grid144]$ cat AB/run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-h2g144-AB
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
unset SLURM_CPUS_PER_TASK
export I_MPI_PIN_PROCESSOR_LIST=16,17,18,19
cd "$SLURM_SUBMIT_DIR"
mpirun -np 4 <vasp_bin>/vasp_std > out
[bcgong@localhost grid144]$
```

`OMP_NUM_THREADS=1` 避免每个 MPI 进程再启动额外线程。`I_MPI_PIN_PROCESSOR_LIST` 是这个节点现场使用的核绑定，换机器应遵循其调度配置。这里按 AB、A、B 的次序串行提交，每项结束并核对之后才继续下一项。

```console
[bcgong@localhost AB]$ sbatch run.slurm
Submitted batch job 18203
[bcgong@localhost AB]$ tail -4 out
DAV:  26    -0.675757525392E+01   -0.96419E-07   -0.89909E-10    32   0.964E-05    0.141E-05
DAV:  27    -0.675757527955E+01   -0.25634E-07   -0.32106E-10    32   0.582E-05    0.892E-06
DAV:  28    -0.675757528376E+01   -0.42084E-08   -0.20943E-11    32   0.152E-05
   1 F= -.67575753E+01 E0= -.67575753E+01  d E =-.395750E-14  mag=    -0.0000
[bcgong@localhost AB]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       37.584
[bcgong@localhost AB]$ cd ../A
[bcgong@localhost A]$ sbatch run.slurm
Submitted batch job 18204
[bcgong@localhost A]$ tail -3 out
DAV:  31    -0.111553427162E+01   -0.37212E-07    0.11147E-11    40   0.712E-07    0.109E-07
DAV:  32    -0.111553427860E+01   -0.69796E-08    0.21005E-11    32   0.517E-07
   1 F= -.11155343E+01 E0= -.11155343E+01  d E =-.379612E-12  mag=     1.0000
[bcgong@localhost A]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       43.484
[bcgong@localhost A]$ cd ../B
[bcgong@localhost B]$ sbatch run.slurm
Submitted batch job 18205
[bcgong@localhost B]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       42.155
[bcgong@localhost B]$ cd ..
```

`aborting loop because EDIFF is reached` 在这里表示电子循环达到所设精度后退出，不是程序异常。三项分别耗时 37.584、43.484、42.155 秒，末尾都有完整运行统计，也不再出现 FFT 网格不足提示。

等待时可在对应目录运行 `tail -f out` 或 `watch -n 2 "tail -n 8 out"`；Ctrl-C 退出的是监视。看到文件不再增长以后，仍要读收敛与正常结束段，不能只看任务已离开队列。

## OUT 的头部、电子迭代与末尾分别告诉我们什么

先看 AB 的标准输出开头：

```console
[bcgong@localhost grid144]$ head -n 24 AB/out
 running on    4 total cores
 distrk:  each k-point on    4 cores,    1 groups
 distr:  one band on    1 cores,    4 groups
 using from now: INCAR     
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 POSCAR found type information on POSCAR  H 
 POSCAR found :  1 types and       2 ions
 scaLAPACK will be used
 LDA part: xc-table for Pade appr. of Perdew
 POSCAR, INCAR and KPOINTS ok, starting setup
 FFT: planning ...
 WAVECAR not read
 entering main loop
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1     0.330307833686E+01    0.33031E+01   -0.36026E+02    32   0.737E+01
DAV:   2    -0.473855047208E+01   -0.80416E+01   -0.80416E+01    32   0.253E+01
DAV:   3    -0.523992505854E+01   -0.50137E+00   -0.50137E+00    40   0.977E+00
DAV:   4    -0.524239736218E+01   -0.24723E-02   -0.24723E-02    32   0.677E-01
DAV:   5    -0.524242226125E+01   -0.24899E-04   -0.24899E-04    32   0.648E-02    0.455E+00
DAV:   6    -0.656955046096E+01   -0.13271E+01   -0.55591E+00    32   0.924E+00    0.337E+00
DAV:   7    -0.655514804124E+01    0.14402E-01   -0.10946E+00    32   0.371E+00    0.163E+00
DAV:   8    -0.660675599031E+01   -0.51608E-01   -0.24393E-01    32   0.135E+00    0.950E-01
DAV:   9    -0.674177913766E+01   -0.13502E+00   -0.19305E-01    32   0.123E+00    0.399E-01
[bcgong@localhost grid144]$
```

这里确认了 VASP 版本、实际 4 个进程、1 种元素和 2 个原子。`WAVECAR not read` 与本次从头计算的输入一致。`DAV` 行是电子迭代，列中有当前能量、能量变化 dE、本征值求解变化 d eps 与残差；它们属于迭代过程，前几步的能量不能用作最终结果。

再读 OUTCAR 中与这次密度对应的实际参数：

```console
[bcgong@localhost grid144]$ grep -E "NELECT|dimension x,y,z|aborting loop|Elapsed time" AB/OUTCAR
   dimension x,y,z NGX =    72 NGY =   72 NGZ =   72
   dimension x,y,z NGXF=   144 NGYF=  144 NGZF=  144
   dimension x,y,z NGX =    70 NGY =   70 NGZ =   70
   NELECT =       2.0000    total number of electrons
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       37.584
[bcgong@localhost grid144]$
```

输出中的实际粗、细网格为 72³ 和 144³。另一个 70³ 行是程序给出的网格尺度信息，不应覆盖已经明确写出的实际设置；最终还要从 CHGCAR 表头核对密度数组的真实尺寸。电子数 `NELECT=2` 是完整 H₂ 的价电子数，A、B 各为 1。

目录中的文件有不同分工：`out` 和 `OSZICAR` 便于看电子步，`OUTCAR` 保留实际参数、能量、磁矩、力与结束统计；`CHGCAR` 提供总密度和磁化密度网格；`vasprun.xml` 是结构化输出；`CONTCAR` 保存最终结构。这个固定构型例子中没有新的离子移动。

## 读 CHGCAR 时，把总密度与磁化密度分开

先看 AB/CHGCAR 的头部：

```console
[bcgong@localhost grid144]$ head -n 15 AB/CHGCAR
H2 fixed geometry charge difference     
   1.00000000000000     
    10.000000    0.000000    0.000000
     0.000000   10.000000    0.000000
     0.000000    0.000000   10.000000
   H 
     2
Direct
  0.500000  0.500000  0.463000
  0.500000  0.500000  0.537000
 
  144  144  144
 -.14180101703E-06 0.15839254613E-05 0.82756458881E-05 0.18919626660E-04 0.24598790238E-04
 0.17342576419E-04 0.32962757902E-05 -.14502942528E-05 0.91047738927E-05 0.21835186348E-04
 0.20713305658E-04 0.74212176581E-05 -.14663704630E-05 0.36751736964E-05 0.14473913947E-04
[bcgong@localhost grid144]$
```

结构头后面的 `144 144 144` 才是第一份体数据的网格尺寸，共 2,985,984 个值。数值按 x 最快、再 y、再 z 的顺序存放。第一块是 `n↑+n↓`，后面还包括 PAW 单中心信息和第二块 `n↑−n↓`；不能把后续所有数字都当成同一份总密度接在一起。

在这份文件的写出约定下，设第一块原始值为 Dᵢ，晶胞体积 V=1000 Å³：

```text
n_i = D_i / V                         单位：e/Å³
NELECT = Σ_i D_i / Ngrid
Δn_i = (D_AB,i − D_A,i − D_B,i) / V
∫ Δn(r) dr ≈ Σ_i (D_AB,i − D_A,i − D_B,i) / Ngrid
```

这里的网格体积元是 V/Ngrid。保留原始数组再按实际体积换算，可以同时检查单位和电子数；不需要用未知比例把积分强行调整成期望值。

[analyze_charge.py](/Atlas/examples/h2-delta-charge/analyze_charge.py) 逐份检查完整电子收敛与正常退出、同一晶胞、同一网格、同一 k 点和赝势指纹。它还核对 A、B 的坐标确实等于 AB 中对应原子的坐标，并分别积分总密度与磁化密度。实际执行得到：

```console
[bcgong@localhost grid144]$ python -B analyze_charge.py | tee analysis.out
AB NELECT=2.0 integral=2.0000000029 e mag(OSZICAR)=-0.0000 mag(grid)=-0.0000000000
A NELECT=1.0 integral=1.0000000012 e mag(OSZICAR)=1.0000 mag(grid)=1.0000000012
B NELECT=1.0 integral=1.0000000012 e mag(OSZICAR)=-1.0000 mag(grid)=-1.0000000012
grid = 144 144 144; points = 2985984; volume = 1000.000000 A^3
integral_delta = 4.362638146422e-10 e; accumulated = 0.2578313944 e; depleted = -0.2578313940 e
delta_n range = -0.0555594237 to 0.8029641058 e/A^3
cumulative endpoint = 4.362638192728e-10 e
Wrote CHGDIFF.vasp, delta-charge.cube, delta-planar.csv, delta-y5.csv, charge-difference-summary.json
[bcgong@localhost grid144]$
```

AB 的总密度积分为 2.0000000029 e，A、B 各为 1.0000000012 e。第二块积分与 OSZICAR 的最终磁矩相符：分子约为 0，两个冻结原子分别约为 +1、−1 μB。后面的差分使用三份文件的第一块，并没有把磁化密度当成总电子数密度。

差分的全胞积分为 4.36×10⁻¹⁰ e，与零相符；正值区域积累 0.2578313944 e，负值区域耗尽 0.2578313940 e，二者相抵。这个数是相对于指定冻结参考的空间重排量。H₂ 两个相同原子具有对称性，它不能被解读为“0.258 e 从 A 转移到了 B”。

## 用切片、平面平均和累计积分读同一份数据

包内的 [plot_charge.py](/Atlas/examples/h2-delta-charge/plot_charge.py)（同时下载 [atlas_plot_style.py](/Atlas/examples/atlas_plot_style.py)，放在同一目录） 读取 [delta-y5.csv](/Atlas/examples/h2-delta-charge/delta-y5.csv)、[delta-planar.csv](/Atlas/examples/h2-delta-charge/delta-planar.csv) 与 [charge-difference-summary.json](/Atlas/examples/h2-delta-charge/charge-difference-summary.json)。在装有 NumPy 和 Matplotlib 的本机运行：

```bash
cd h2-delta-charge
python3 plot_charge.py
```

它生成 `h2-charge-difference.png/pdf/svg` 和 `plot-checks.json`。

![固定 H₂ 相对于两个冻结 H 原子的电子密度重排](/Atlas/examples/h2-delta-charge/h2-charge-difference.png)

左图是穿过两个 H 的 y=5 Å 切片，圆点标出真实原子坐标。颜色使用保留实际极值的线性对称范围；橙实线与蓝虚线分别标出正、负等值线，便于看见幅度较小的耗尽区域。曲线没有通过插值改变原始密度数值。这里 Δn 的最小、最大值分别为 −0.0555594、+0.8029641 e/Å³。

中图先在 xy 平面平均，再乘以面积 A=100 Å²，得到每单位 z 长度的电子数变化，单位 e/Å。右图从晶胞边界 z=0 开始累计积分，单位为 e。累计曲线在晶胞另一端返回近零，与全胞守恒检查一致；局部曲线的正负取决于选定边界与区域，不能用其最大值替代 Bader 分区后的净电荷。

如果需要三维等值面，先把三份 CHGCAR.gz 放回子目录，再运行：

```bash
python3 analyze_charge.py
```

程序会另写 `CHGDIFF.vasp` 与 `delta-charge.cube`。前者保留 AB 的几何头，只有用于可视化的差分标量块，不是用于重启 SCF 的完整 CHGCAR。Cube 文件把长度换成 bohr、密度换成 e/bohr³，并按 Cube 的 z 最快次序写出；不能给两种文件使用同一个未经换算的等值面数值。完整网格转换由脚本完成，不必手工剪贴百万行数据。

这条路线已经把三份真实输入、SCF、网格相减、单位、电子数与图像对应起来。它展示的是固定 0.74 Å 几何、10 Å 周期盒和当前参数下的重排，未对键长、盒长、截断或密度极值作系统收敛。研究异质结时仍按同一个坐标系拆分片段，并另行核验片段的电荷与自旋参考态。

下一步：若要给空间区域分配净电子数，可接 [Bader 分析](/Atlas/m/bader/vasp/)；若要看电子局域特征，可接 [ELF](/Atlas/m/elf/vasp/)。这两种量与 Δn 的定义不同，需要各自读取对应的输出。

```text
固定 AB 几何 → 原位保留 A、B → 匹配参数的三份 SCF
                                  ↓
                        CHGCAR 结构、网格、电子数
                                  ↓
                       第一密度块 AB − A − B
                                  ↓
                    切片 / 平面平均 / 累计积分
```
