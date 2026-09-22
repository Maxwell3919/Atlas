[VASP：Fe 单层 SOC 示例](https://vasp.at/wiki/Spin-orbit_coupling_in_a_Fe_monolayer) · [SAXIS](https://vasp.at/wiki/SAXIS) · [LSORBIT](https://vasp.at/wiki/LSORBIT) · [GGA_COMPAT](https://vasp.at/wiki/GGA_COMPAT)

这组 Fe 单层计算的四份 OUTCAR 都写出了 EDIFF 已达到。可是把 k 网格从 9×9×1 改为 15×15×1 后，两个磁化方向的零展宽能量差从 −0.05659 变成 +0.63992 meV/Fe，连符号都改变了。电子循环结束与磁各向异性能量收敛，需要分开核验。

[下载四个真实计算目录及提取、绘图脚本](/Atlas/examples/vasp/fe-monolayer-mae-files.tar.gz)。这里采用 VASP 官方 Fe 单层例子的几何，用同一份结构和 PAW 数据比较面外 z 与面内 x 两个方向；实际采用的截断能、展宽和网格都写在下面的输入中。普通固定结构计算见 [SCF](/Atlas/m/scf/vasp/)。

先读已经完成的 `k09_z` 输入。

```text
[bcgong@localhost k09_z]$ cat POSCAR
Fe (100) monolayer; VASP wiki SOC Fe example
3.45
0.5 0.5 0.0
-0.5 0.5 0.0
0.0 0.0 5.0
Fe
1
Cartesian
0.0 0.0 0.0
```

缩放系数 3.45 同时作用于三条晶格矢量；面内矢量长度约 2.4395 Å，第三方向周期为 17.25 Å。晶胞中只有一个 Fe，因此后面的每晶胞能量差也就是每 Fe 能量差。这个指定几何用于方法演示，没有在本页重新进行结构优化。

```text
[bcgong@localhost k09_z]$ cat INCAR
SYSTEM = Fe monolayer SOC z
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 160
ALGO = Normal
ISMEAR = 1
SIGMA = 0.1
LNONCOLLINEAR = .TRUE.
LSORBIT = .TRUE.
SAXIS = 0 0 1
MAGMOM = 0 0 3
LORBIT = 11
LMAXMIX = 4
GGA_COMPAT = .FALSE.
LREAL = .FALSE.
LASPH = .TRUE.
NCORE = 2
ISYM = 0
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .FALSE.
```

`LSORBIT = .TRUE.` 和非共线计算让能量能够依赖磁化相对晶体的方向；运行程序使用 `vasp_ncl`。`GGA_COMPAT = .FALSE.`、`LASPH = .TRUE.` 在四个目录中保持一致，避免方向比较混入其他协议变化。

本例始终使用 `MAGMOM = 0 0 3`，通过 SAXIS 选择这一初始磁矩在笛卡尔空间中的方向。SAXIS=0 0 1 时它沿 z；改为 SAXIS=1 0 0 后，它沿 x。SAXIS 定义自旋坐标基底，本身不是强制固定最终磁矩方向的约束；因此结束后还要检查磁矩是否仍接近所要比较的方向。

`ISYM = 0` 和其余输入在两个方向之间一致。每次都 `ISTART = 0`、`ICHARG = 2`，没有混用在另一自旋基底下保存的密度或波函数。

```text
[bcgong@localhost k09_z]$ cat KPOINTS
Fe monolayer 9x9x1
0
Gamma
9 9 1
0 0 0
```

```text
[bcgong@localhost k09_z]$ grep -E 'TITEL|ZVAL' POTCAR
   TITEL  = PAW_PBE Fe 06Sep2000
   POMASS =   55.847; ZVAL   =    8.000    mass and valenz
```

```text
[bcgong@localhost k09_z]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-mae9-z
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
mpirun -np 8 /data/software/vasp.5.4.4/bin/vasp_ncl > out
```

脚本实际使用 8 个 MPI 进程。这里的 CPU 编号 16–23 是当时 Slurm 分配与实际亲和性核验过的范围；相关环境设置处理的是该节点 Intel MPI 的绑定行为，换机器时须按实际分配检查。整个系列串行执行，运行中节点总申请为 24/64 核，包含原有的 16 核声子任务。

`k09_z` 的真实作业号是 18189。它结束后，复制四项输入与脚本，建立 x 方向计算：

```text
[bcgong@localhost fe_monolayer_mae]$ cp k09_z/INCAR k09_z/POSCAR k09_z/KPOINTS k09_z/POTCAR k09_z/run.slurm k09_x/
[bcgong@localhost fe_monolayer_mae]$ cd k09_x
[bcgong@localhost k09_x]$ vi INCAR
[bcgong@localhost k09_x]$ vi run.slurm
```

INCAR 中只有标题与 SAXIS 改变；提交脚本改任务名并设为 10 分钟限时。先用 diff 读回差异：

```text
[bcgong@localhost fe_monolayer_mae]$ diff -u k09_z/INCAR k09_x/INCAR
--- k09_z/INCAR	2026-09-22 21:54:22.021335438 +0800
+++ k09_x/INCAR	2026-09-22 22:32:58.119697120 +0800
@@ -1,4 +1,4 @@
-SYSTEM = Fe monolayer SOC z
+SYSTEM = Fe monolayer SOC x
 ISTART = 0
 ICHARG = 2
 ENCUT = 400
@@ -10,7 +10,7 @@
 SIGMA = 0.1
 LNONCOLLINEAR = .TRUE.
 LSORBIT = .TRUE.
-SAXIS = 0 0 1
+SAXIS = 1 0 0
 MAGMOM = 0 0 3
 LORBIT = 11
 LMAXMIX = 4
@@ -24,3 +24,4 @@
 LWAVE = .FALSE.
 LCHARG = .FALSE.
 
+
```

```text
[bcgong@localhost k09_x]$ sbatch run.slurm
Submitted batch job 18192
```

运行时用 `squeue -j 18192` 查看调度状态，用 `tail -f out` 跟踪电子步。达到电子收敛后，再从已经计算好的 z 目录复制一套到 `k15_z`，只改 KPOINTS 中的网格和标题：

```text
[bcgong@localhost fe_monolayer_mae]$ cp k09_z/INCAR k09_z/POSCAR k09_z/KPOINTS k09_z/POTCAR k09_z/run.slurm k15_z/
[bcgong@localhost fe_monolayer_mae]$ cd k15_z
[bcgong@localhost k15_z]$ vi KPOINTS
[bcgong@localhost k15_z]$ vi run.slurm
```

```text
[bcgong@localhost k15_z]$ cat KPOINTS
Fe monolayer 15x15x1
0
Gamma
15 15 1
0 0 0
```

```text
[bcgong@localhost k15_z]$ sbatch run.slurm
Submitted batch job 18193
```

这一方向结束后再准备 `k15_x`，保持 15×15×1 网格，只按前面的方式改 SAXIS 与任务名，提交得到 18194。每个网格都必须有 x、z 成对结果，不能把 9×9 的一个方向和 15×15 的另一个方向相减。

```text
[bcgong@localhost fe_monolayer_mae]$ grep -E 'aborting loop|Elapsed time' k09_z/OUTCAR k09_x/OUTCAR k15_z/OUTCAR k15_x/OUTCAR
k09_z/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
k09_z/OUTCAR:                         Elapsed time (sec):       86.399
k09_x/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
k09_x/OUTCAR:                         Elapsed time (sec):       89.010
k15_z/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
k15_z/OUTCAR:                         Elapsed time (sec):      201.326
k15_x/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
k15_x/OUTCAR:                         Elapsed time (sec):      199.324
```

四份输出均达到电子停止条件并正常计时，耗时分别约 86、89、201、199 秒。先核对方向，再读取能量差。

```text
[bcgong@localhost k15_x]$ grep -A 8 'Euler angles' OUTCAR | head -8
 Euler angles ALPHA=     0.0000000  BETA=     1.5707963

 transformation matrix from SAXIS to cartesian coordinates
 ---------------------------------------------------------
     0.0000000 m_x     0.0000000 m_y     1.0000000 m_z
     0.0000000 m_x     1.0000000 m_y     0.0000000 m_z
    -1.0000000 m_x     0.0000000 m_y     0.0000000 m_z
```

```text
[bcgong@localhost k15_x]$ tail -3 OSZICAR
DAV:  58    -0.633320572465E+01   -0.49650E-07   -0.35186E-09  8292   0.448E-04    0.207E-05
DAV:  59    -0.633320572727E+01   -0.26196E-08   -0.24485E-09  8532   0.418E-04
   1 F= -.63332057E+01 E0= -.63327868E+01  d E =-.125685E-02  mag=     0.0001    -0.0001     2.9668
```

这份 OUTCAR 给出从 SAXIS 自旋基底到笛卡尔坐标的矩阵：m_cart=(m₃,m₂,−m₁)。因此 OSZICAR 中主要落在第三分量的 2.9668 μB，在真实空间沿 x；直接看到 `mag` 的第三列较大就说它沿 z，会把这个方向读反。

包内 `read_mae.py` 对四份输入逐项比较：结构和 PAW 一致，除 SYSTEM/SAXIS 外的有效 INCAR 参数相同，每一对的 KPOINTS 与实际 NKPTS 一致；再要求电子收敛与正常结束，并把磁矩转到笛卡尔坐标。含授权 POTCAR 的原目录使用实际哈希；公开下载包使用保留的原始哈希记录。

```text
[bcgong@localhost fe_monolayer_mae]$ python read_mae.py
same POSCAR/POTCAR; same active INCAR except SYSTEM/SAXIS; x/z k grids match
k09_z: F=-6.32688259 eV; E0=-6.32647774 eV; NKPTS=81; wall=86.399 s
  m_spinor=[-0.0001, 0.0, 2.8108]; m_Cartesian=[-0.0001, 0.0, 2.8108]; angle=0.002038 deg
k09_x: F=-6.32683074 eV; E0=-6.32653433 eV; NKPTS=81; wall=89.010 s
  m_spinor=[-0.0, -0.0002, 2.8257]; m_Cartesian=[2.8257, -0.0002, 0.0]; angle=0.004055 deg
k15_z: F=-6.33383960 eV; E0=-6.33342670 eV; NKPTS=225; wall=201.326 s
  m_spinor=[0.0001, -0.0001, 2.9729]; m_Cartesian=[0.0001, -0.0001, 2.9729]; angle=0.002726 deg
k15_x: F=-6.33320573 eV; E0=-6.33278678 eV; NKPTS=225; wall=199.324 s
  m_spinor=[0.0001, -0.0001, 2.9668]; m_Cartesian=[2.9668, -0.0001, -0.0001]; angle=0.002731 deg
9x9x1: DeltaF(x-z)=+0.05185000 meV/Fe; DeltaE0(x-z)=-0.05659000 meV/Fe
15x15x1: DeltaF(x-z)=+0.63387000 meV/Fe; DeltaE0(x-z)=+0.63992000 meV/Fe
9 -> 15 change in DeltaE0 = +0.69651000 meV/Fe
```

四个最终磁矩相对目标方向的偏角都低于 0.005°，这组计算确实比较了近似 x 与 z 两个方向。总磁矩幅值从 9×9 时约 2.81–2.83 μB 变为 15×15 时约 2.97 μB，也表明当前取样对电子态仍有影响。

本页统一定义 ΔE = E_x − E_z。正值表示在这一计算设置下 z 方向较低，负值表示 x 方向较低。主要比较使用 OUTCAR 的 `energy(sigma->0)`，同时保留自由能 F 的差作为展宽影响的检查，不能在不同目录里换能量定义。

```text
[bcgong@localhost k15_z]$ grep -A 6 'FREE ENERGIE' OUTCAR
  FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =        -6.33383960 eV

  energy  without entropy=       -6.33260091  energy(sigma->0) =       -6.33342670
```

```text
[bcgong@localhost k15_x]$ grep -A 6 'FREE ENERGIE' OUTCAR
  FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =        -6.33320573 eV

  energy  without entropy=       -6.33194887  energy(sigma->0) =       -6.33278678
```

15×15 的 E0 分别为 −6.33342670 和 −6.33278678 eV，相减得到 +0.63992 meV/Fe。读数时先在 eV 中相减，再乘 1000，避免在四舍五入后的总能量上取差。

| k 网格 | ΔF = F_x−F_z（meV/Fe） | ΔE0 = E0_x−E0_z（meV/Fe） |
| --- | ---: | ---: |
| 9×9×1 | +0.05185 | −0.05659 |
| 15×15×1 | +0.63387 | +0.63992 |

9×9 时，展宽修正的方向差已与所求信号同量级，F 与 E0 甚至给出不同符号。15×15 时两种能量差更接近，但主读数相对 9×9 改变了约 0.69651 meV/Fe。仅凭这两组网格还不能把 +0.63992 meV 登记为收敛的材料 MAE，也不能据此确定最终易轴。

下一轮应继续成对加密 k 网格，并在每个网格下成对缩小 SIGMA，直到所选能量差在预先规定的容差内稳定；ENCUT、真空和几何误差也要与所需精度相称。EDIFF=10⁻⁸ eV 限制的是电子迭代停止条件，不能消除有限 k 网格与展宽带来的误差。这个系列已经把两方向计算与验收路线完整走通，同时保留了尚未通过网格检查的真实结果。

在本机进入解包目录，运行：

```bash
python3 read_mae.py
python3 plot_mae.py
```

提取只用 Python 标准库，绘图需要 NumPy 和 Matplotlib。脚本输出 `mae-mesh-check.png` 和 PDF：左图并列给出同一网格上的 ΔE0、ΔF 和零线，右图显示两个方向的磁矩随网格变化。图标题写明固定结构与 SIGMA=0.1 eV，不把曲线包装成已经收敛的易轴结论。

![两个 k 网格下 Fe 单层的方向能量差与磁矩](/Atlas/examples/vasp/fe-monolayer-mae/mae-mesh-check.png)

下一步可回到 [磁性候选态比较](/Atlas/m/magnetic-gs/vasp/)，先确认所研究磁构型，再在同一构型内做更严格的方向与取样检查。

```text
同一结构 / PAW / 泛函 / 电子参数
  └─ SOC + x/z 两个磁化初始方向
       ├─ 最终磁矩 → SAXIS 基底变换 → 方向验收
       └─ 同一能量定义相减 → meV/原子
             └─ k 网格与展宽成对变化 → 差值稳定后再判断易轴
```
