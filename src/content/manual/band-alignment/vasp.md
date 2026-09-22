[VASP：功函数](https://vasp.at/wiki/Computing_the_work_function) · [LVHAR](https://vasp.at/wiki/LVHAR) · [LDIPOL](https://vasp.at/wiki/LDIPOL) · [EIGENVAL](https://vasp.at/wiki/EIGENVAL)

把两份 OUTCAR 中的 `E-fermi` 直接画到一根能量轴上，会漏掉它们各自的能量零点。这里从一个六原子的 SnSe₂/Sr₂N 结构中拆出两层，保持共同面内晶胞，分别做固定结构 SCF；每一层都用自己的真空势换算带边或费米能，最后才放到同一张图上。

[下载本例的输入、原始输出和分析脚本](/Atlas/examples/vasp/snse2-sr2n-alignment-files.tar.gz)。包内保留两份完整 `LOCPOT`、`CHGCAR`、`OUTCAR`、`EIGENVAL`，以及产生本文数字的脚本。POTCAR 仅提供标题、价电子数与哈希，需要使用自己的授权文件。平面平均和能级提取可以在服务器上运行，绘图在本机完成。

这组结构沿用 [异质结构建模](/Atlas/m/heterostructure-modeling/vasp/) 中的原始参考结构，各层的内部形变也保留。它回答的是共同晶胞下、指定冻结几何的孤立层参考能级。自由单层的平衡几何、接触后电荷转移和界面势垒，需要另外的计算来回答。固定结构 SCF 的文件和步骤见 [SCF](/Atlas/m/scf/vasp/)，势文件的格式见 [静电势](/Atlas/m/electrostatic-potential/vasp/)。

## 保留共同晶胞与原来的表面朝向

先复制已有六原子结构。在以下命令中，`<工作目录>` 是原异质结构 SCF 的目录；新目录与原计算分开。

```text
[bcgong@localhost vasp]$ mkdir -p band_alignment/snse2 band_alignment/sr2n
[bcgong@localhost vasp]$ cd band_alignment
[bcgong@localhost band_alignment]$ cp <工作目录>/POSCAR POSCAR.reference
[bcgong@localhost band_alignment]$ cp <工作目录>/POTCAR POTCAR.reference
[bcgong@localhost band_alignment]$ cp POSCAR.reference snse2/POSCAR
[bcgong@localhost band_alignment]$ vi snse2/POSCAR
[bcgong@localhost band_alignment]$ cp POSCAR.reference sr2n/POSCAR
[bcgong@localhost band_alignment]$ vi sr2n/POSCAR
```

原文件元素顺序是 `Sn Se N Sr`，计数为 `1 2 1 2`。SnSe₂ 取前三个原子，Sr₂N 取后三个原子；后者继续按 `N Sr`、`1 2` 的顺序书写。不要只删坐标而忘记更新元素名与计数。每一层仅整体沿 z 平移，使最上、最下原子的中点落在晶胞中央：

```text
[bcgong@localhost band_alignment]$ cat snse2/POSCAR
snse2 frozen isolated layer in common cell
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
Sn Se
1 2
Direct
 0.0000000000000000 0.0000000000000000 0.5036394637538087
 0.6666666670000012 0.3333333329999988 0.5421918198149582
 0.3333333329999988 0.6666666670000012 0.4578081801850417
[bcgong@localhost band_alignment]$ cat sr2n/POSCAR
sr2n frozen isolated layer in common cell
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
N Sr
1 2
Direct
 0.6666666670000012 0.3333333329999988 0.4948574488156312
 0.0000000000000000 -0.0000000000000000 0.5343094980558125
 0.3333333329999988 0.6666666670000012 0.4656905019441875
```

两个晶胞的面内边长都是 3.9501156207 Å，法向长度都是 39.4021877938 Å。本站 [SnSe₂ 功函数例子](/Atlas/m/workfunction/vasp/) 的面内边长是 3.8464052688 Å，不能把那个目录的带边直接搬来与这里的 Sr₂N 比较。相对于那份结构文件，这里的面内伸长为 2.6963%；这个百分比本身不代表相对于已验证平衡晶格的应变。

上下表面也没有被人为对称化。SnSe₂ 中 Sn 到两侧 Se 平面的距离不相等，Sr₂N 中 N 到两侧 Sr 平面的距离也不相等。原异质结构中，SnSe₂ 位于上方，朝向另一层的是它的 **lower z** 表面；Sr₂N 位于下方，朝向另一层的是它的 **upper z** 表面。把每层居中以后，这个方向关系仍然保留。

下载包中的 `analyze_alignment.py` 会逐项比较新旧结构：晶格、元素、原子数和面内坐标必须匹配，同一层三个原子的 z 平移量必须一致。先在提交前运行几何检查：

```text
[bcgong@localhost band_alignment]$ python analyze_alignment.py --geometry-only
snse2: 3 atoms; rigid dz=-0.090381737230 fractional; thickness=3.324900015 A; empty height=36.077287778 A
sr2n: 3 atoms; rigid dz=0.040884040820 fractional; thickness=2.703738571 A; empty height=36.698449223 A
Common cell, INCAR and KPOINTS: identical
```

这里的 `empty height` 是相邻周期层之间的法向空白高度，不是层厚。两层都超过 36 Å；这给后面选择远离原子的真空区间留出了空间，但仍然要看实际势和电荷密度。

POTCAR 的元素顺序要跟着 POSCAR 一起改变。本次使用同一份原异质结构 POTCAR 中的四个完整数据集，脚本先核对标题和 `End of Dataset` 边界，再把前两个、后两个分别写入两个新目录。它不会覆盖已有 POTCAR，也不会把许可正文写入公开数据包。

```text
[bcgong@localhost band_alignment]$ python split_paw.py
snse2 SHA256 5f3cbe84c6fe6bf10909ed09324ce2b0bdcd886a81e4b163eba45f3d16624e2f
sr2n SHA256 96913914225d67d7590b8fe9bbd0003c981e9097a9e13e583aec31706f54600a
[bcgong@localhost band_alignment]$ cat snse2/POTCAR.identity.txt sr2n/POTCAR.identity.txt
SHA256 5f3cbe84c6fe6bf10909ed09324ce2b0bdcd886a81e4b163eba45f3d16624e2f
TITEL  = PAW_PBE Sn_d 06Sep2000
POMASS =  118.710; ZVAL   =   14.000    mass and valenz
TITEL  = PAW_PBE Se 06Sep2000
POMASS =   78.960; ZVAL   =    6.000    mass and valenz
SHA256 96913914225d67d7590b8fe9bbd0003c981e9097a9e13e583aec31706f54600a
TITEL  = PAW_PBE N 08Apr2002
POMASS =   14.001; ZVAL   =    5.000    mass and valenz
TITEL  = PAW_PBE Sr_sv 07Sep2000
POMASS =   87.620; ZVAL   =   10.000    mass and valenz
```

SnSe₂ 的价电子数为 `14 + 2 × 6 = 26`，Sr₂N 为 `5 + 2 × 10 = 25`。这一步既核对顺序，也为后面检查 OUTCAR 和电荷积分提供整数参考。若从各元素的授权库重新组合文件，仍须先核对版本、标题和价电子数。

## 用同一套设置完成两份 SCF

两份 INCAR 与 KPOINTS 完全相同：

```text
[bcgong@localhost band_alignment]$ vi snse2/INCAR
[bcgong@localhost band_alignment]$ cp snse2/INCAR sr2n/INCAR
[bcgong@localhost band_alignment]$ cat snse2/INCAR
SYSTEM = isolated frozen layer vacuum reference
ISTART = 0
ICHARG = 2
ISPIN = 1
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
[bcgong@localhost band_alignment]$ cat snse2/KPOINTS
Common-cell vacuum-reference mesh
0
Gamma
21 21 1
0 0 0
```

这里明确使用 `ISPIN = 1`，沿用原始参考计算的标量非磁性 PBE-D2 协议，没有开启 SOC。这是本例结果的范围，不能据此排除磁性态或 SOC 对带边的改变。`NSW = 0` 固定所有离子；`ISTART = 0` 和 `ICHARG = 2` 从原子电荷开始，两份目录均没有复用另一层的 CHGCAR。

`LVHAR = .TRUE.` 写出离子势加 Hartree 势。`LDIPOL = .TRUE.`、`IDIPOL = 3` 在法向加入偶极修正，`DIPOL` 放在居中后的层附近。非对称层可以具有两个不同的真空平台；偶极修正并不要求把这两个平台强行变成一个值。[LDIPOL 官方说明](https://vasp.at/wiki/LDIPOL) 也指出，这类修正可能让电子收敛变慢，所以是否达到 EDIFF 必须从输出中确认。

提交脚本如下。此次使用的节点共有 64 个调度核，原研究任务占 16 核，新例子每次只开 8 个 MPI 进程，两个单层串行运行。

```text
[bcgong@localhost band_alignment]$ cat snse2/run.slurm
#!/bin/bash
#SBATCH --job-name=align-snse2
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
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

脚本中的 16–23 是这次现场核验过的空闲 CPU 编号，用来避开已有任务。更换机器时，需要依据当时的分配重新设置，不能照搬编号。这里取消的是子进程环境中的 `SLURM_CPUS_PER_TASK`，Slurm 申请仍是 `8 × 1`；该版本 Intel MPI 否则会优先采用由它推断的绑定域。`OMP_NUM_THREADS=1` 则避免每个 MPI 进程再展开额外的 OpenMP 线程。

```text
[bcgong@localhost band_alignment]$ cd snse2
[bcgong@localhost snse2]$ squeue -o "%.18i %.14j %.10u %.2t %.6C %.10M"
             JOBID           NAME       USER ST   CPUS       TIME
             18180   srnsnse-ph64     bcgong  R     16    2:46:16
[bcgong@localhost snse2]$ sbatch run.slurm
Submitted batch job 18198
```

运行中可以在另一终端查看队列与电子迭代：

```bash
watch -n 5 'squeue -o "%.18i %.14j %.10u %.2t %.6C %.10M"'
tail -f out
```

`Ctrl+C` 只结束这两个观察命令。队列中的 `R` 表示正在运行；它不能说明 SCF 已经收敛。结束后，把 OSZICAR 的最后几步与 OUTCAR 的收敛标记、最终计时一起看：

```text
[bcgong@localhost snse2]$ tail -n 7 OSZICAR
DAV:  20    -0.116412516655E+02   -0.37855E-05   -0.59417E-08  1960   0.601E-04    0.184E-04
DAV:  21    -0.116412522450E+02   -0.57954E-06   -0.35421E-09  2236   0.228E-04    0.113E-04
DAV:  22    -0.116412531128E+02   -0.86775E-06   -0.76089E-09  1972   0.276E-04    0.720E-05
DAV:  23    -0.116412533720E+02   -0.25926E-06   -0.60865E-10  1992   0.129E-04    0.275E-05
DAV:  24    -0.116412535934E+02   -0.22140E-06   -0.12387E-09  1776   0.115E-04    0.430E-05
DAV:  25    -0.116412536906E+02   -0.97141E-07   -0.93296E-11  1972   0.754E-05
   1 F= -.12025617E+02 E0= -.12025616E+02  d E =-.313107E-06
[bcgong@localhost snse2]$ grep -E "EDIFF is reached|E-fermi|Elapsed time" OUTCAR
E-fermi :  -4.1160     XC(G=0):  -1.7219     alpha+bet : -1.4843
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):      160.816
```

`DAV` 行中的 `dE` 是相邻电子迭代的能量变化，`d eps` 是本征值相关变化。第 25 步后出现 `EDIFF is reached`，而文件末尾有完整计时；这说明本次固定几何的电子自洽结束了。它不是离子优化通过的证据。OSZICAR 中最后的 `F=`、`E0=` 与 OUTCAR 的总能段对应：

```text
[bcgong@localhost band_alignment]$ grep -A 5 "FREE ENERGIE" snse2/OUTCAR
FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =       -12.02561657 eV

  energy  without entropy=      -12.02561626  energy(sigma->0) =      -12.02561641
```

本页使用的是单粒子能级与静电势，仍把这个总能段保留在原始输出里，便于核查这是一份完成的静态计算，而不是只拷贝了几行带边数据。

确认第一个任务结束、资源仍符合限制后，再进入另一个目录提交。Sr₂N 的脚本仅把作业名改成 `align-sr2n`。

```text
[bcgong@localhost band_alignment]$ cd sr2n
[bcgong@localhost sr2n]$ sbatch run.slurm
Submitted batch job 18199
[bcgong@localhost sr2n]$ tail -n 7 OSZICAR
DAV:  24    -0.125492168021E+02   -0.75953E-06   -0.36601E-08  1472   0.529E-04    0.331E-04
DAV:  25    -0.125492176987E+02   -0.89652E-06   -0.15999E-08  1392   0.379E-04    0.896E-05
DAV:  26    -0.125492184397E+02   -0.74100E-06   -0.16093E-08  1392   0.249E-04    0.313E-04
DAV:  27    -0.125492186592E+02   -0.21954E-06   -0.19763E-09  1256   0.151E-04    0.124E-04
DAV:  28    -0.125492187704E+02   -0.11117E-06   -0.74655E-10  1192   0.975E-05    0.613E-05
DAV:  29    -0.125492188144E+02   -0.44009E-07    0.19619E-11  1160   0.647E-05
   1 F= -.12799026E+02 E0= -.12797556E+02  d E =-.294088E-02
[bcgong@localhost sr2n]$ grep -E "EDIFF is reached|E-fermi|Elapsed time" OUTCAR
E-fermi :  -2.1582     XC(G=0):  -1.8451     alpha+bet : -1.4302
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):      160.448
```

Sr₂N 用了 29 次电子迭代，实际运行时间同样约 161 秒；两个任务的错误日志均为 0 字节。`LWAVE=.FALSE.` 使 WAVECAR 为 0 字节，这次分析也不需要它；`LCHARG=.TRUE.` 生成 CHGCAR，`LVHAR=.TRUE.` 生成 LOCPOT。文件作用与大小可以一起核对：

```text
[bcgong@localhost band_alignment]$ ls -lh snse2/{INCAR,POSCAR,KPOINTS,OUTCAR,OSZICAR,EIGENVAL,LOCPOT,CHGCAR,WAVECAR}
-rw-rw-r-- 1 bcgong bcgong  37M Sep 22 23:33 snse2/CHGCAR
-rw-rw-r-- 1 bcgong bcgong  35K Sep 22 23:33 snse2/EIGENVAL
-rw-rw-r-- 1 bcgong bcgong  369 Sep 22 23:30 snse2/INCAR
-rw-rw-r-- 1 bcgong bcgong   57 Sep 22 23:30 snse2/KPOINTS
-rw-rw-r-- 1 bcgong bcgong  37M Sep 22 23:33 snse2/LOCPOT
-rw-rw-r-- 1 bcgong bcgong 2.4K Sep 22 23:33 snse2/OSZICAR
-rw-rw-r-- 1 bcgong bcgong 135K Sep 22 23:33 snse2/OUTCAR
-rw-rw-r-- 1 bcgong bcgong  464 Sep 22 23:30 snse2/POSCAR
-rw-rw-r-- 1 bcgong bcgong    0 Sep 22 23:31 snse2/WAVECAR
```

`OUTCAR` 保存参数回显、电子过程、能量和最终计时；`OSZICAR` 是便于监控的短记录；`EIGENVAL` 给出每个 k 点的能带与占据；`LOCPOT` 给出三维势网格。CHGCAR 在这里用于检查真空窗口内是否还有明显的电子密度。文件存在只是第一步，后面分别核对其内部数据。

## 从 EIGENVAL 分别读取带边和金属交叉

先看 SnSe₂ 的 EIGENVAL 开头：

```text
[bcgong@localhost band_alignment]$ head -n 25 snse2/EIGENVAL
    3    3    1    1
  0.1774800E+03  0.3950116E-09  0.3950116E-09  0.3940219E-08  0.5000000E-15
  1.000000000000000E-004
  CAR 
 isolated frozen layer vacuum reference  
     26     48     20
 
  0.0000000E+00  0.0000000E+00  0.0000000E+00  0.2267574E-02
    1      -25.719623   1.000000
    2      -25.719623   1.000000
    3      -25.690023   1.000000
    4      -25.683909   1.000000
    5      -25.683909   1.000000
    6      -17.722152   1.000000
    7      -16.244606   1.000000
    8      -10.190616   1.000000
    9       -5.596384   1.000000
   10       -5.389675   1.000000
   11       -5.389675   1.000000
   12       -4.254365   0.999954
   13       -4.254365   0.999954
   14       -3.484356   0.000000
   15       -1.566439   0.000000
   16       -0.240462   0.000000
   17       -0.240462   0.000000
```

第六行 `26 48 20` 依次是电子数、不可约 k 点数和能带数。随后每个 k 点用一行写三个倒空间坐标和权重，再跟 20 行能带数据。这里能带行的三列是序号、能量和占据。本版本非磁性输出中，占据数按单自旋归一化，满占据写成 1；脚本用 `2 × Σ(k 权重 × 占据)` 复核总电子数。

Γ 点的第 13 带为 −4.254365 eV，第 14 带为 −3.484356 eV。只减这两个数会得到 Γ 点的直接间隔。遍历整个 21×21×1 网格后，最低导带出现在采样坐标约 `(0.4761905, 0, 0)`，得到的间接隙只有 0.278103 eV。因此这页的带边来自全体采样 k 点，不是从一张路径图上目测的。

Sr₂N 的开头写着 `25 48 16`。在 Γ 点，前 14 条带都处于费米能以下，这并不意味着每个 k 点都填满 14 条带；其他 k 点的占据会变化。解析全部 48 个 k 点后，第 13、14 带的能量范围都跨过了 `E_F=-2.1582 eV`，所以这一指定非磁模型按金属处理，不为它安排一对人为的 VBM/CBM。

## 为每一侧表面找到真空参考

接着读取真空势。平面平均脚本按 VASP 的网格顺序读取首个标量场，要求数值个数等于 `NGXF × NGYF × NGZF`，并检查截断与非有限值。LOCPOT 中的量已经是 eV；求平面平均时不再除以晶胞体积。

```text
[bcgong@localhost band_alignment]$ cd snse2
[bcgong@localhost snse2]$ python ../plane_average.py LOCPOT 6:10 29:33
grid = 60 60 588; scalar values = 2116800
normal height = 39.4021880000 A; output = PLANAR_AVERAGE.dat
window 6.00:10.00 A  N=60  mean=1.738360141 eV  std=2.2732e-05 eV  range=6.14621e-05 eV
window 29.00:33.00 A  N=60  mean=1.194360347 eV  std=2.9865e-05 eV  range=6.821e-05 eV
[bcgong@localhost snse2]$ cd ../sr2n
[bcgong@localhost sr2n]$ python ../plane_average.py LOCPOT 6:10 29:33
grid = 60 60 588; scalar values = 2116800
normal height = 39.4021880000 A; output = PLANAR_AVERAGE.dat
window 6.00:10.00 A  N=60  mean=0.872342013 eV  std=5.30532e-06 eV  range=2.4683e-05 eV
window 29.00:33.00 A  N=60  mean=1.273814882 eV  std=4.78083e-06 eV  range=2.37907e-05 eV
```

两个窗口分别取 6–10 Å 和 29–33 Å，避开原子层及晶胞边界附近的偶极修正跳变。`range` 是所选窗口内势的最大值减最小值，这里均小于 0.00007 eV。SnSe₂ 两侧平台却相差约 0.5440 eV，Sr₂N 两侧相差约 0.4015 eV：平台本身很平坦，并不意味着两侧平台必须相等。

同一组窗口再用 CHGCAR 核对。CHGCAR 首个电荷网格采用与 LOCPOT 不同的归一化；全网格平均给出总价电子数，而平面平均再除以晶胞体积才得到电子密度，单位为 e/Å³。

```text
[bcgong@localhost band_alignment]$ python check_vacuum_density.py
snse2: integrated valence electrons=26.000001016; volume=532.439868220 A^3
  z=6.0:10.0 A: mean density=1.70073e-08; max abs density=2.65706e-08 e/A^3
  z=29.0:33.0 A: mean density=3.87515e-09; max abs density=1.32019e-08 e/A^3
sr2n: integrated valence electrons=25.000000037; volume=532.439868220 A^3
  z=6.0:10.0 A: mean density=6.51407e-08; max abs density=3.89415e-07 e/A^3
  z=29.0:33.0 A: mean density=3.38004e-08; max abs density=3.2739e-07 e/A^3
```

26 与 25 的总价电子数得到了恢复，真空窗口中的平面平均密度最大绝对值低于 `3.9×10⁻⁷ e/Å³`。结合平坦的势，这些窗口可以用于本次参考能级读取。这里没有把一次真空厚度的检查写成对所有真空尺寸都已收敛。

## 相向表面的能级如何对齐

最后从同一次 SCF 的 OUTCAR、EIGENVAL、LOCPOT 汇总结果。脚本会拒绝没有电子收敛标记或最终计时的 OUTCAR，检查 EIGENVAL 电子数、k 点权重、带序号和占据，并核对势摘要的源文件哈希。

```text
[bcgong@localhost band_alignment]$ python analyze_alignment.py
snse2: 3 atoms; rigid dz=-0.090381737230 fractional; thickness=3.324900015 A; empty height=36.077287778 A
sr2n: 3 atoms; rigid dz=0.040884040820 fractional; thickness=2.703738571 A; empty height=36.698449223 A
Common cell, INCAR and KPOINTS: identical
snse2: NELECT=26; weighted electrons=25.99999588; NKPTS=48; NBANDS=20; elapsed=160.816 s
  E_F=-4.116000 eV; classification=gapped_on_sampled_mesh; crossing bands=[]
  VBM=-4.254365 eV; CBM=-3.976262 eV; sampled gap=0.278103 eV
  lower_z V_vac=1.738360141 eV; range=6.14621e-05 eV; Phi=5.854360141 eV
  upper_z V_vac=1.194360347 eV; range=6.821e-05 eV; Phi=5.310360347 eV
sr2n: NELECT=25; weighted electrons=24.99999595; NKPTS=48; NBANDS=16; elapsed=160.448 s
  E_F=-2.158200 eV; classification=metallic_on_sampled_mesh; crossing bands=[13, 14]
  band 13: Emin=-3.494134 eV; Emax=-1.288695 eV; occupation=0.000000:1.000000
  band 14: Emin=-2.418358 eV; Emax=-0.876122 eV; occupation=0.000000:1.000000
  lower_z V_vac=0.872342013 eV; range=2.4683e-05 eV; Phi=3.030542013 eV
  upper_z V_vac=1.273814882 eV; range=2.37907e-05 eV; Phi=3.432014882 eV
Facing isolated references: CBM(SnSe2)-E_F(Sr2N)=-2.282607 eV; E_F(Sr2N)-VBM(SnSe2)=2.560710 eV
```

把所选表面的真空能级设为零，使用的是 `E′ = E − V_vac`。原来面向界面的两侧给出：

| 孤立层及表面 | 真空势 / eV | 相对于该侧真空的能级 / eV |
| --- | ---: | --- |
| SnSe₂，lower z | 1.738360 | VBM = −5.992725；CBM = −5.714622 |
| Sr₂N，upper z | 1.273815 | E_F = −3.432015 |

因此，把这两份孤立层的面向表面按真空能级对齐，会得到 `CBM(SnSe₂) − E_F(Sr₂N) = −2.282607 eV`。这个数表达指定参考模型的能级相对位置。接触以后，电荷转移、界面偶极、杂化与结构响应都会改变势和能带，不能把这里的差值当作已经计算出的实际界面势垒，也不能用它直接定量推算转移电子数。Sr₂N 在本次模型中是金属，半导体—半导体的 type I / II 分类也不适用于这张图。

这次结果还保留了四项具体范围：共同晶胞下的冻结几何、非磁性约束、没有 SOC、单个 21×21×1 网格。PBE 带隙也不是经过准粒子修正的带隙。文章中的数值是可复核的计算示例；若要用它们讨论真实接触性质，应先补相应的结构、磁性与数值收敛检查，再直接分析界面体系。

## 从原始文件重画这张图

把下载包解压到本机，在安装了 NumPy 和 Matplotlib 的 Python 环境中运行：

```bash
cd snse2
python3 ../plane_average.py LOCPOT 6:10 29:33
cd ../sr2n
python3 ../plane_average.py LOCPOT 6:10 29:33
cd ..
python3 analyze_alignment.py
python3 check_vacuum_density.py
python3 plot_alignment.py
```

前三类脚本从原始文件重建数据，最后一条生成 `band-alignment.png` 与 PDF。图上方保留每层原始势曲线，并给出实际选取的窗口；下方将四个表面分别以当地真空为零，SnSe₂ 画 VBM/CBM，Sr₂N 只画金属费米能。朝向原界面的两个表面会在横轴文字中标出。

![同一共同晶胞中两份冻结孤立层的双侧真空势与参考能级](/Atlas/figures/band-alignment-vasp/band-alignment.png)

下一步若要看接触后的变化，转到 [差分电荷密度](/Atlas/m/delta-charge/vasp/)，在同一异质结构晶胞与冻结几何下比较 AB、A、B 的电荷；若要读整个异质结构的势变化，转到 [静电势](/Atlas/m/electrostatic-potential/vasp/)。这两类结果再与实际界面能带结合，才能继续讨论接触后的能级重排。

```text
明确的共同晶胞与六原子结构
  └─ 分出两层 → 保留内部形变与表面方向 → 各自居中
       └─ 相同协议的两份独立静态 SCF
            ├─ OUTCAR / OSZICAR：电子收敛与结束验收
            ├─ EIGENVAL：半导体带边或金属费米面交叉
            └─ LOCPOT + CHGCAR：双侧平坦真空区间
                 └─ 每个能级减去对应表面的真空势
                      └─ 孤立层参考图 → 后续直接检查界面体系
```
