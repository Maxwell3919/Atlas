[VASP：功函数](https://vasp.at/wiki/Computing_the_work_function) · [LVHAR](https://vasp.at/wiki/LVHAR) · [LOCPOT](https://vasp.at/wiki/LOCPOT) · [LDIPOL](https://vasp.at/wiki/LDIPOL)

真空势应当从一段平坦的区域读取。只找到 `LOCPOT`，或者从文件末尾拿一个数，都不能说明已经找到了真空能级。这个例子把三原子 SnSe₂ 单层重新做一次固定结构 SCF，在同一次计算中写出电荷密度、静电势和费米能，再沿层法向求平面平均。

[下载本例的真实输入、输出和分析脚本](/Atlas/examples/vasp/snse2-workfunction-files.tar.gz)。包内有 `LOCPOT`、`CHGCAR`、`OUTCAR`、`EIGENVAL` 和本文使用的 Python 脚本；POTCAR 只附元素标题、价电子数和哈希，需从自己的授权赝势库取得对应文件。图在本机绘制，远端不需要安装图形界面。

固定结构 SCF 的基本操作见 [SCF](/Atlas/m/scf/vasp/)。这里保留已有计算的 POSCAR、KPOINTS 和 POTCAR，用一个新目录重新生成电荷密度：

```text
[bcgong@localhost vasp]$ mkdir snse2_workfunction
[bcgong@localhost vasp]$ cp snse2_lvhar/POSCAR snse2_lvhar/KPOINTS snse2_lvhar/POTCAR snse2_lvhar/run.slurm snse2_workfunction/
[bcgong@localhost vasp]$ cd snse2_workfunction
[bcgong@localhost snse2_workfunction]$ vi INCAR
```

`snse2_lvhar` 是同一结构的前一次计算目录。此处没有复制其中的 CHGCAR 或 WAVECAR；新的 INCAR 用 `ISTART = 0`、`ICHARG = 2` 从原子电荷开始。因此本页的势与费米能不依赖一次来源不清的固定电荷重启。

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

`LDIPOL = .TRUE.`、`IDIPOL = 3` 沿 z 加偶极修正，`DIPOL = 0.5 0.5 0.5` 选在层中心。这里的晶格第三矢量垂直于层；若你的晶胞倾斜，应先确认所采用修正方向与真空法向一致。`LCHARG = .TRUE.` 保留本次自洽密度，`LWAVE = .FALSE.` 则节省波函数存储空间。

```text
[bcgong@localhost snse2_workfunction]$ cat KPOINTS
K-Spacing Value to Generate K-Mesh: 0.010
0
Gamma
  33  33   1
0.0  0.0  0.0
```

这是覆盖整个二维布里渊区的 33×33×1 均匀网格。费米能从这次均匀网格 SCF 读取，不采用能带高对称线计算报告的费米能。

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

本例实际申请 8 个 MPI 进程，限时 15 分钟。提交时节点共有 64 核，已有研究任务使用 16 核；运行中也核验了所有用户进程，新任务使总用核达到 24 核。

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

输出确认 ICHARG=2，写出的势来自 LVHAR，电子循环达到了 EDIFF，文件末尾有正常计时汇总。本次程序耗时约 87.2 秒，调度器计时 88 秒。这个验收说明当前固定结构、截断能和 k 网格的电子问题已求解；它没有替代结构、真空高度或 k 网格的收敛检查。

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

LOCPOT 的前半部分像 POSCAR：标题、缩放系数、三条晶格矢量、元素和数量、坐标。空行后出现 `60 60 280`，表示网格沿三个晶格方向各有这么多点；再往后才是势值，x 最快变化，z 最慢。总共应读到 60×60×280 = 1,008,000 个标量值。

下载包中的 `plane_average.py` 按这个结构读取文件，先检查网格尺寸、数值个数和有限性，再对每个 z 平面的 60×60 个值求平均。它把结果写成两列文本，而不去改动 LOCPOT：

```text
[bcgong@localhost snse2_workfunction]$ python plane_average.py LOCPOT 1:3 15:17
grid = 60 60 280; scalar values = 1008000
normal height = 18.3572980000 A; output = PLANAR_AVERAGE.dat
window 1.00:3.00 A  N=30  mean=3.306283412 eV  std=1.5602e-05 eV  range=6.06972e-05 eV
window 15.00:17.00 A  N=31  mean=3.306265353 eV  std=3.89608e-05 eV  range=0.000145996 eV
```

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

第一列是层法向距离，第二列是平面平均势。处理 LOCPOT 的方法和它的单位已闭合；接下来从同一份 OUTCAR 取费米能，并从 EIGENVAL 取当前均匀网格的带边。

```text
[bcgong@localhost snse2_workfunction]$ python workfunction_values.py
E_F = -2.478300 eV; VBM = -2.690722 eV; CBM = -1.923449 eV; gap = 0.767273 eV
z = 1.00:3.00 A; V_vac = 3.306283412 eV; Phi(E_F) = 5.784583412 eV; V_vac-VBM = 5.997005412 eV; V_vac-CBM = 5.229732412 eV
z = 15.00:17.00 A; V_vac = 3.306265353 eV; Phi(E_F) = 5.784565353 eV; V_vac-VBM = 5.996987353 eV; V_vac-CBM = 5.229714353 eV
```

功函数按 Φ = V_vac − E_F 计算，两个表面分别为 5.78458 与 5.78457 eV。这里的 E_F = −2.4783 eV 是本次 `ISMEAR = 0`、`SIGMA = 0.05` 计算报告的电子化学势。

这个例子有约 0.7673 eV 的 PBE 带隙。对半导体，费米能在带隙中的位置会随占据处理、掺杂和实验条件变化，因此这组 Φ 应连同所用化学势一起报告。脚本还给出真空到价带顶约 5.9970 eV、真空到导带底约 5.2297 eV；这两个带边差有助于说明所画能量参考，但仍受泛函、k 点取样和几何影响，不能作为未经收敛检验的最终材料常数。

`workfunction_values.py` 的带边读取针对本例的偶数电子、非自旋极化体系：26 个电子对应 13 条占据带，它在所有 108 个不可约 k 点上取第 13 带的最高值和第 14 带的最低值。金属、自旋极化或非共线体系需要按实际占据和数据结构处理，不能直接套用这个计数。

把解包后的 `snse2-workfunction` 目录留在本机，安装了 NumPy 和 Matplotlib 的 Python 环境中执行：

```bash
python3 plot_workfunction.py
```

脚本读取 `PLANAR_AVERAGE.dat` 与 `workfunction-summary.json`，上图保留整个晶胞的势、费米能和两个浅色统计窗口，下图把真空平台附近放大到 ±0.002 eV，输出 `workfunction-z.png` 和 `workfunction-z.pdf`。保留这两个尺度，既能看清原子区，也能看见真空中是否仍有倾斜。

![SnSe₂ 平面平均势、费米能与两侧真空平台](/Atlas/examples/vasp/snse2_workfunction/workfunction-z.png)

下一步接 [能带对齐](/Atlas/m/band-alignment/vasp/)。把两个材料放到同一能量参考前，需要分别取得它们自己的真空势和带边；不能直接比较两个计算各自打印的 E_F。若只需要三维势和平面平均的文件读法，接 [静电势](/Atlas/m/electrostatic-potential/vasp/)。

```text
固定结构 + 同一套赝势 / 均匀 k 网格
  └─ SCF + LVHAR
       ├─ OUTCAR → 收敛与 E_F
       ├─ EIGENVAL → 当前网格的 VBM / CBM
       └─ LOCPOT → 平面平均 → 平坦真空窗口
                                    └─ V_vac − E_F；同时注明带隙中的化学势
```
