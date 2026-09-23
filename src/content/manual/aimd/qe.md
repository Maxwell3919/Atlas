[pw.x 的 MD、时间步与温控输入](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [QE 7.5 的 Verlet 实现](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/dynamics_module.f90)

结构优化把原子移向一个局部能量极小值。分子动力学则给原子初速度，让它们按力随时间运动：每走一个离子步，都要重新求电子基态，再用得到的力推进下一步。这样的一份 OUT 会反复出现 SCF、力、坐标、动能和温度。读 AIMD 输出，要按“离子步里包含一段电子自洽”的层次往下看。

这里用实际运行的 8 原子周期 fcc Al 演示。它由 [晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax) 中的单原子原胞沿三个原胞基矢各重复两次得到，原始立方晶格常数为 3.95606780081 Å。保持晶胞不变，使用 QE 7.5、LDA-PZ、`Al.pz-vbc.UPF`、40/160 Ry 截断能和 4³ 超胞 k 网格。后者是本例的短轨迹设置，尚未证明力和统计量对电子采样收敛。

本次有三个完成的分支：100 步 SVR 恒温轨迹，以及两种步长覆盖相同时间的 NVE 轨迹。它们的作用是把输入、监控和验收过程走完整，不足以判断长期热稳定、熔点或扩散。

完整输入、输出、逐步数据和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。在解包后的 `al` 目录运行文末的作图命令；重新进行 MD 时，按实际位置填写赝势库与 QE 可执行文件路径。

## 先准备同一份位置和初速度

8 个原子的初速度来自固定种子 20260922 的正态分布，先减去质心速度，再按 21 个自由度归一化到 300 K。初速度和坐标都写进输入，因此两条 NVE 可以从同一个初态比较步长。最初的输入准备过程保存在 `prepare_aimd.py`，具体初速度记录在 `initial-velocities.json`；没有从一次已经升温的轨迹中任意摘取几行。

下面是最终用于恒温轨迹的完整输入。`ATOMIC_POSITIONS crystal` 是超胞的分数坐标，`ATOMIC_VELOCITIES` 使用 QE 的原子单位，不是 Å/fs。

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ cat al.md.in
&CONTROL
 calculation = 'md'
 nstep = 100
 dt = 20
 iprint = 1
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'low'
/
&SYSTEM
 ibrav = 0
 nosym = .true.
 nat = 8
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 18
/
&ELECTRONS
 diagonalization = 'cg'
 diago_thr_init = 1.0d-9
 diago_full_acc = .true.
 diago_cg_maxiter = 200
 conv_thr = 1.0d-10
/
&IONS
 ion_dynamics = 'verlet'
 ion_velocities = 'from_input'
 ion_temperature = 'svr'
 tempw = 300
 nraise = 20
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
Al 0.50000000000000 0.00000000000000 0.00000000000000
Al 0.00000000000000 0.50000000000000 0.00000000000000
Al 0.50000000000000 0.50000000000000 0.00000000000000
Al 0.00000000000000 0.00000000000000 0.50000000000000
Al 0.50000000000000 0.00000000000000 0.50000000000000
Al 0.00000000000000 0.50000000000000 0.50000000000000
Al 0.50000000000000 0.50000000000000 0.50000000000000
CELL_PARAMETERS angstrom
-3.95606780081072 0.00000000000000 3.95606780081072
0.00000000000000 3.95606780081072 3.95606780081072
-3.95606780081072 3.95606780081072 0.00000000000000
K_POINTS automatic
4 4 4 0 0 0
ATOMIC_VELOCITIES
Al -2.96685438852231e-04 5.46443872130152e-04 3.52588534897630e-04
Al 1.83169591108944e-04 -2.23845342698565e-05 3.04783826563648e-04
Al -3.62394243793356e-04 -5.62805162705629e-04 -3.77915518336268e-04
Al 5.62907234083758e-05 9.24073788215892e-05 -1.03170084336693e-04
Al 3.21602394621728e-04 1.76949229988034e-04 3.06925804418459e-05
Al 2.89759188061222e-04 3.51480144555030e-05 -1.67953236314361e-04
Al -1.50927363418241e-04 -2.43518115575532e-04 1.17081675570922e-04
Al -4.08148511364416e-05 -2.22406828442608e-05 -1.56107778486724e-04
```

`calculation='md'` 表示晶胞固定的分子动力学。`dt=20` 使用 pw.x 的 Rydberg 原子时间单位，换算为 0.9675537306 fs；100 步推进的坐标时间为 96.75537306 fs。不能把 20 当成 20 fs，也不能直接套用 cp.x 的 Hartree 原子时间单位。

`ion_temperature='svr'` 是随机速度缩放温控，`tempw=300` 设置目标温度，`nraise=20` 对应约 19.35 fs 的温控特征时间。它不意味着每一步都等于 300 K。这里固定了初速度，没有固定 QE 内部温控的随机数；重新运行这条 SVR 轨迹，逐点温度不会与下面完全重合。

## 热运动为什么会触发对称性错误

第一次输入没有 `nosym`。完美初始晶体具有很多对称操作，原子按不同初速度移动后却不再满足它们，因此第一次离子移动之后程序停止：

```console
maxwell@maxwell:~/al/aimd$ tail -10 nve-dt20/al.md.out


     Linear momentum :   -0.0000000000    0.0000000000   -0.0000000000

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     Error in routine checkallsym (1):
     some of the original symmetry operations not satisfied
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

     stopping ...
```

这是输入设置与运动后的结构不相容，不是“材料在第一步就不稳定”。原目录保留，另建目录复制并用 `vi` 加入 `nosym=.true.`：

```console
maxwell@maxwell:~/al/aimd$ mkdir nve-dt20-nosym
maxwell@maxwell:~/al/aimd$ cp nve-dt20/al.md.in nve-dt20-nosym/al.md.in
maxwell@maxwell:~/al/aimd$ cp nve-dt20/run.slurm nve-dt20-nosym/run.slurm
maxwell@maxwell:~/al/aimd$ cd nve-dt20-nosym
maxwell@maxwell:~/al/aimd/nve-dt20-nosym$ mkdir tmp
maxwell@maxwell:~/al/aimd/nve-dt20-nosym$ vi al.md.in

```

这次保留时间反演配对，但不再要求运动中的晶体保持初始空间群。均匀 k 网格覆盖范围会相应变化，因此后面的计算比完美晶体的初始 SCF 更费时。

## 提交脚本与正在运行时的读法

恒温分支最终使用 16 个 MPI 进程、8 个 k 点池，每个进程一个 OpenMP 线程。下面是实际提交的完整脚本。两个 NVE 分支各使用 8 个 MPI 进程，自己的脚本随数据一起保存。

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-nvt-cg
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 16 <qe_bin>/pw.x -nk 8 -in al.md.in > al.md.out 2> al.md.err
```

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ sbatch run.slurm
Submitted batch job 1977
```

运行中可以在同一个目录查看队列，再持续看 OUT 文件末尾：

```bash
squeue -j 1977
tail -f al.md.out
```

`tail -f` 中按 Ctrl+C 只结束查看，不会停止 Slurm 作业。看见新的 `Entering Dynamics` 行，说明程序又推进了一个离子步；它前面的一段 `iteration #` 则是该几何下的电子 SCF 迭代。两种 iteration 不要混在一起。

## OUT 中的一步包含哪些内容

先取 NVE 大步长分支的第一个离子步。最初的 SCF 已经收敛，紧接着打印能量分解、力与应力。以下是连续输出节选：

```text
!    total energy              =     -33.52087979 Ry
     estimated scf accuracy    <          2.3E-11 Ry
     smearing contrib. (-TS)   =       0.00028280 Ry
     internal energy E=F+TS    =     -33.52116259 Ry

     convergence has been achieved in   8 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000001    0.00000040   -0.00000005
     atom    2 type  1   force =    -0.00000007    0.00000003   -0.00000003
     atom    3 type  1   force =     0.00000000    0.00000004   -0.00000039
     atom    4 type  1   force =    -0.00000038   -0.00000001    0.00000001
     atom    5 type  1   force =     0.00000035   -0.00000005    0.00000002
     atom    6 type  1   force =     0.00000001   -0.00000010    0.00000035
     atom    7 type  1   force =     0.00000006    0.00000003    0.00000001
     atom    8 type  1   force =     0.00000003   -0.00000034    0.00000008

     Total force =     0.000001     Total SCF correction =     0.000004
     SCF correction compared to forces is large: reduce conv_thr to get better values


     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=        2.98
   0.00002024   0.00000000   0.00000000            2.98        0.00        0.00
   0.00000000   0.00002024  -0.00000000            0.00        2.98       -0.00
   0.00000000  -0.00000000   0.00002024            0.00       -0.00        2.98


     Molecular Dynamics Calculation
     mass Al               =    26.98
     Time step             =    20.00 a.u.,  0.9676 femto-seconds
```

`estimated scf accuracy` 对应电子自洽的残差估计；本例每步要求小于 10⁻¹⁰ Ry。力是接下来推进原子位置所用的量。应力和 `P` 也会随运动变化，这里固定的是晶胞，不是把压力锁定为零。

这一段还保留了力的警告：初始结构的 `Total force` 只有约 10⁻⁶ Ry/bohr，而 `Total SCF correction` 为约 4×10⁻⁶ Ry/bohr，修正相对原力较大。电子残差达到输入阈值，并不能让这条提示自动失效。对本例接近对称极小值的初态，绝对数值很小，但仍不能宣称力已对 `conv_thr` 收敛；若要研究更精细的动力学量，需要另做更紧电子阈值的力与轨迹对照。后面的减半时间步只检查当前电子设置下的积分误差。

随后出现新的坐标与动能、温度：

```text
Entering Dynamics:    iteration =     1
                           time      =   0.0010 pico-seconds


ATOMIC_POSITIONS (crystal)
Al               0.0001375488        0.0008057202        0.0006561644
Al               0.5001926177        0.0006227609       -0.0006826455
Al               0.0007320655        0.4982569085        0.0002374365
Al               0.4996630927        0.5000608996        0.0001863149
Al              -0.0006258245        0.0007079354        0.4997654513
Al               0.4993407332        0.0002099472        0.4998840831
Al               0.0006842362        0.4996289887        0.4997195349
Al               0.4998755303        0.4997068395        0.5002336603


     kinetic energy (Ekin) =           0.01995091 Ry
     temperature           =         299.99999998 K 
     Ekin + Etot (const)   =         -33.50092887 Ry
     Ions kinetic stress =            2.34 (kbar)
                                      2.03           0.64           0.14
                                      0.64           3.10           1.57
                                      0.14           1.57           1.90



     Linear momentum :   -0.0000000000    0.0000000000   -0.0000000000
```

这里 `kinetic energy` 是离子动能；电子 SCF 给出的 `Etot` 与它相加，才是本次 NVE 检查的能量总和。金属展宽仍是电子计算中的数值设置，不应把 `degauss` 换算成离子温度写在这张图上。

前面的 OUT 同时打印了 `total energy` 与 `internal energy E=F+TS`。这条有限电子展宽的轨迹使用程序推进离子时对应的 `Etot` 加离子动能，不把其中一部分时刻换成另一列内部能。此处的 NVE 是固定晶胞、没有离子热浴的积分分支；电子展宽参数仍固定保留，不能进一步称为已经验证的真实有限电子温度系综。

QE 7.5 这段位置 Verlet 输出有一个细节：打印出的新坐标已前进到 n·dt，但同一块里的 Etot 和中心差分速度属于前一个坐标时刻 (n−1)·dt。提取脚本因此分别保存 `position_time_fs` 与 `energy_sample_time_fs`；画能量曲线使用后者，导出的坐标轨迹使用前者。这样才能把不同步长的同一物理时刻对齐。

## 结束后，逐步核对电子部分

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ tail -12 al.md.out
     fftw         :    306.57s CPU    311.40s WALL (  645522 calls)
 
     Parallel routines
 
     PWSCF        :  10m 1.45s CPU  10m14.91s WALL

 
   This run was terminated on:  22:48:37  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

对于指定步数的 MD，输出 `The maximum number of steps has been reached.` 是走完所设步数的正常停止条件。仍需核对实际步数、每步 SCF 是否收敛，以及每步最后一次对角化是否有未解决的警告。

这个例子的第一个 `nvt-dt20-nosym` 分支虽打印了 `JOB DONE.`，第 44 步最后一次 Davidson 对角化却留下 `1 eigenvalues not converged`，因此没有用于本页主图。它保留在原目录，另建 `nvt-dt20-cg`，用 `cp`、`vi` 改为 CG 并收紧本征态精度设置后重新运行。两条 NVT 的随机热浴不同，不能把它们逐点相减当作算法误差。

NVE 大步长分支也有一次对角化警告，但发生在最后一个离子步的中间 SCF 迭代，随后的最终迭代已经消失。提取脚本区分中途警告与最终未解决的警告，不用简单的关键字计数代替这项检查。

```console
maxwell@maxwell:~/al/aimd$ ../.venv/bin/python analyse_aimd.py > analysis.out
maxwell@maxwell:~/al/aimd$ cat analysis.out
case                steps  dt_fs    coord_end_fs  energy_range_meV_atom  mean_T_K
nvt-dt20-cg          100  0.967554  96.755373      51.897811       196.418
nve-dt20-nosym        50  0.967554  48.377687       0.019405       142.856
nve-dt10-nosym       100  0.483777  48.377687       0.004269       142.226
All 250 SCF cycles converged; no final-iteration diagonalization warning; 3 native JOB DONE endings.
Early SCF diagonalization warnings: {'nvt-dt20-cg': 0, 'nve-dt20-nosym': 1, 'nve-dt10-nosym': 0}
NVE position difference at the common final time: 2.272203084249565e-05 angstrom RMS
NVE total-energy conservation tested only over ~48 fs; no thermodynamic convergence claim.
```

最终使用的三条轨迹共有 250 段电子 SCF，均达到设置的残差要求，最终对角化无未解决的警告。这证明它们完成了本例规定的数值流程，还没有证明电子网格、超胞尺寸和轨迹长度对物性收敛。

## 温度下降是否说明轨迹坏了

![恒温和NVE轨迹的瞬时温度](/Atlas/examples/al/figures/aimd-temperature.png)

SVR 的输入目标为 300 K，但这段不足 0.1 ps 的实际平均温度只有 196.418 K，瞬时范围为 90.061–348.887 K。它显然还不能作为充分平衡的 300 K 系综。初始位置接近零温极小值，最初输入的动能会转移为位移的势能；8 原子体系也会有很大的瞬时温度起伏。延长平衡与采样、增大体系，并检查统计量才可能回答热平衡性质。

NVE 没有温控，温度从初始 300 K 下降也不自动意味着程序丢失能量。下面右图把势能变化与动能变化一起画出，两个方向相反；是否守恒，应看左图里的总和。

![等时长NVE的能量变化与动势能交换](/Atlas/examples/al/figures/aimd-energy.png)

两条 NVE 具有相同初始位置、初速度、电子协议和固定晶胞。大步长设置为 `nstep=50, dt=20`，小步长设置为 `nstep=100, dt=10`；两者坐标都推进到 48.377687 fs。

| NVE 步长 | 步数 | 总能量峰峰变化 / meV·atom⁻¹ |
|---:|---:|---:|
| 0.967554 fs | 50 | 0.019405 |
| 0.483777 fs | 100 | 0.004269 |

步长减半后，本段轨迹的能量波动明显减小。两条轨迹在共同终点的原子位置 RMS 差为 2.27×10⁻⁵ Å。这是本例短时间内的积分步长检查；不能把一个小的短时波动范围外推成长期能量稳定，也不能拿 SVR 中随热浴交换而变化的总能量套用 NVE 的守恒要求。

## 提取坐标并重新画图

每个完成目录下的 `thermo.csv` 按离子步保存能量、温度、SCF 迭代数和残差；`trajectory.xyz` 含初始帧及全部推进后的帧，写有晶格与周期边界，长度分别为 101、51、101 帧。原始未回卷坐标被保留，没有用绝对值或人工平滑修饰运动。

```console
maxwell@maxwell:~/al/aimd$ head -4 nve-dt20-nosym/thermo.csv
step,energy_sample_time_fs,position_time_fs,temperature_K,potential_Ry,kinetic_Ry,total_Ry,scf_iterations,early_diagonalization_warning_count,scf_estimated_accuracy_Ry,total_change_meV_atom
1,0.0,0.9675537305999999,299.99999998,-33.52087979,0.01995091,-33.50092887,8,0,2.3e-11,0.0
2,0.9675537305999999,1.9351074611999999,299.25269602,-33.52083006,0.01990121,-33.50092885,7,0,3.4e-11,3.401423562183524e-05
3,1.9351074611999999,2.9026611918,297.01880642,-33.52068143,0.01975265,-33.50092877,7,0,5.3e-11,0.0001700711660248932
```

![短时间原子位移](/Atlas/examples/al/figures/aimd-displacement.png)

图中 RMS 位移是相对初始原子位置的短时变化，没有据此拟合扩散系数。要重新出图，把 `aimd` 子目录和 [plot_aimd.py](/Atlas/examples/al/plot_aimd.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 放在同一 Al 数据目录，运行：

```bash
python plot_aimd.py
```

这会生成温度、能量与位移三组 PNG/PDF。原始提取代码为 [analyse_aimd.py](/Atlas/examples/al/aimd/analyse_aimd.py)，初态记录为 [initial-velocities.json](/Atlas/examples/al/aimd/initial-velocities.json)；最初的输入准备记录为 [prepare_aimd.py](/Atlas/examples/al/prepare_aimd.py)。它保留初态的生成过程；本页实际完成的三条路线使用后续调整过的 `nosym` 与 CG 设置，重跑时应使用上表各目录中的最终输入和 `run.slurm`，不能把最初的生成脚本当成最终三条路线的一键入口。

| 分支 | 输入与脚本 | 完整 OUT | 数值与坐标 |
|---|---|---|---|
| nvt-dt20-cg | [输入](/Atlas/examples/al/aimd/nvt-dt20-cg/al.md.in) / [脚本](/Atlas/examples/al/aimd/nvt-dt20-cg/run.slurm) | [OUT](/Atlas/examples/al/aimd/nvt-dt20-cg/al.md.out) | [CSV](/Atlas/examples/al/aimd/nvt-dt20-cg/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nvt-dt20-cg/trajectory.xyz) |
| nve-dt20-nosym | [输入](/Atlas/examples/al/aimd/nve-dt20-nosym/al.md.in) / [脚本](/Atlas/examples/al/aimd/nve-dt20-nosym/run.slurm) | [OUT](/Atlas/examples/al/aimd/nve-dt20-nosym/al.md.out) | [CSV](/Atlas/examples/al/aimd/nve-dt20-nosym/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nve-dt20-nosym/trajectory.xyz) |
| nve-dt10-nosym | [输入](/Atlas/examples/al/aimd/nve-dt10-nosym/al.md.in) / [脚本](/Atlas/examples/al/aimd/nve-dt10-nosym/run.slurm) | [OUT](/Atlas/examples/al/aimd/nve-dt10-nosym/al.md.out) | [CSV](/Atlas/examples/al/aimd/nve-dt10-nosym/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nve-dt10-nosym/trajectory.xyz) |

下一步：若要看零温附近的振动模式，转到 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 或 [有限位移声子](/Atlas/m/phonon-finite-disp/qe/)。短 AIMD 与这些计算回答的时间尺度和近似不同，应分别检查后再合起来讨论。

```text
明确结构 + 初速度 → 每步电子 SCF → 力 → Verlet 移动 → 温度 / 能量 / 坐标
                                    ├─ NVE：相同步长时间对照与能量守恒
                                    └─ SVR：温控响应与平衡、采样长度检查
```
