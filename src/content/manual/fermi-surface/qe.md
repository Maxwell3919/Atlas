[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [后处理用户手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [Plotly 的三维等值面](https://plotly.com/python/3d-isosurface-plots/)

能带图沿一条路径画出电子能量。费米面则在整个三维倒空间里寻找满足 Eₙ(k)=E_F 的位置：一条能带可以贡献一个电子口袋、一个空穴口袋，也可能穿过倒空间单元的边界。只沿高对称线做一次能带计算，没有足够信息画这张面。

这里使用新计算的 fcc Al。结构与赝势同 [Al 声子示例](/Atlas/m/phonon-dfpt/qe/)，QE 7.5、LDA-PZ、无自旋极化和 SOC。先完成同一结构的 [SCF](/Atlas/m/scf/qe/)，再按 [NSCF](/Atlas/m/nscf/qe/) 的接续方式在整个均匀网格上求本征值。下面只展开费米面需要额外核对的部分。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 均匀网格必须能恢复成完整三维数组

为了让第一次读图容易核对，我们直接保留全部 k 点，而不是先缩到不可约区再重建。24³ 和 32³ 网格分别有 13824 与 32768 个点；输入写明 `nosym` 与 `noinv`，后处理仍再次检查点数和重复点，不能只相信输入文件。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ cat al.nscf.in
&CONTROL
 calculation = 'nscf'
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 0
 nat = 1
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 6
 nosym = .true.
 noinv = .true.
/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-9
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.97803390040536 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.97803390040536 1.97803390040536 0.00000000000000
K_POINTS automatic
32 32 32 0 0 0
```
这是最终用于作图的实际输入。`nbnd=6` 给本例留出足够空带去检查哪些能带越过 E_F，`verbosity=high` 保留文本里的 k 点和本征值；精确提取仍使用 XML，避免文本列数变化影响读取。SCF 的 `prefix=al`、`outdir=./tmp` 在同一个计算目录内相接。

## 程序结束之后，先把没收敛的本征值找出来

第一次 24³/32³ NSCF 使用默认 Davidson。它们都打印了 `JOB DONE.`，但是全文里出现以下原生信息：

```console
maxwell@maxwell:~/al/fermi/k32-cg$ grep "not converged" ../k24/al.nscf.out
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
```
这几行不能被末尾的正常结束覆盖。默认非自洽本征值阈值与 `conv_thr`、电子数有关；本例把 SCF 阈值直接继承到 NSCF 后过于紧。我们保留原来的 `k24`、`k32` 目录，在新目录明确设置 CG 求解、1.0×10⁻⁹ Ry 的本征值阈值、空带同精度以及最大迭代数，再完整重算 SCF→NSCF。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ diff ../k32/al.nscf.in al.nscf.in
24a25,28
>  diagonalization = 'cg'
>  diago_thr_init = 1.0d-9
>  diago_full_acc = .true.
>  diago_cg_maxiter = 200
```
1.0×10⁻⁹ Ry 是这里明确选用的求解阈值，不是“让告警消失”的文本处理；新的输出需要重新检查。它比后面 0.1—0.2 eV 的能量窗口小许多，但仍不等于 k 网格的数值收敛。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-fs32cg
#SBATCH --nodes=1
#SBATCH --ntasks=8
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
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
mpirun -np 8 <qe_bin>/pw.x -nk 8 -in al.nscf.in > al.nscf.out 2> al.nscf.err
```
```console
maxwell@maxwell:~/al/fermi/k32-cg$ sbatch run.slurm
Submitted batch job 1965
```
运行时，均匀网格 NSCF 会不断输出 `Computing kpt #`。本次使用 `-nk 8`，32768 个点分到 8 个 pool，所以一个 pool 的计数到 4096，不能把它误读成总共只算了 4096 个点。

```bash
squeue -j 1965 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f al.nscf.out
```

```console
maxwell@maxwell:~/al/fermi/k32-cg$ tail -9 al.nscf.out
 
     PWSCF        :   2m32.15s CPU   2m44.18s WALL

 
   This run was terminated on:  21:51:25  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
复算后的 stdout 没有 `not converged`，stderr 为空。24³ 和 32³ NSCF 分别用时 1 分 15.35 秒与 2 分 44.18 秒。计算目录保留原始失败信息和新输出，下面只用后者的 XML 生成图。

## XML 里取到的不只是一个费米能数值

```console
maxwell@maxwell:~/al/fermi/k32-cg$ grep "the Fermi energy" al.nscf.out
     the Fermi energy is     8.3815 ev
```
这行方便在终端迅速核对。XML 中的 `fermi_energy` 和 `eigenvalues` 使用 Hartree；[extract_fermi.py](/Atlas/examples/al/fermi/extract_fermi.py) 把它们统一乘以 27.211386245988 转为 eV，再减去同一份 NSCF 的 E_F。不能把文本中已是 eV 的数值再乘一次换算常数。

```console
maxwell@maxwell:~/al/fermi/..$ .venv/bin/python fermi/extract_fermi.py
k=24^3 nks=13824 EF=8.39793432 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.61975726 J(X)=0.09968022 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.31708865 J(X)=0.06123457 eV^-2; direct-sum check passed
k=32^3 nks=32768 EF=8.38150272 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.53305558 J(X)=0.04490039 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.28204495 J(X)=0.03678119 eV^-2; direct-sum check passed
```
提取程序读取 XML 的倒格矢，把每一个 k 点映射到整数网格。它要求每个格点恰好出现一次，再保存 `fermi-grid.npz`；若有缺点、重复点或无法对应的坐标就停止，而不是先画一张插值面掩盖问题。

32³ 网格里的各条带相对 E_F 的范围是：

| 带号 | 最低能量 / eV | 最高能量 / eV | 是否穿过 0 |
|---|---:|---:|---|
| 1 | -11.548067 | -0.893493 | 否 |
| 2 | -4.487133 | 12.944767 | 是 |
| 3 | -0.326782 | 12.944767 | 是 |
| 4 | 1.392852 | 14.105571 | 否 |
| 5 | 5.798257 | 16.257599 | 否 |
| 6 | 9.493963 | 20.080026 | 否 |

第一带在所有采样点都低于 E_F，第四带及以上高于 E_F；本次被网格直接检测到穿越零能的，是第二带和第三带。因此两张费米面分别保留带号，不能把它们叠起来后称作同一个口袋。

## 先看截面，再转动三维等值面

[plot_fermi.py](/Atlas/examples/al/plot_fermi.py) 读两个网格目录里的 `fermi-grid.npz`，生成二维截面对照与一个可在浏览器中旋转的三维 HTML。需要 NumPy、Matplotlib 和 Plotly；在下载的 Al 示例根目录运行：

```bash
python3 plot_fermi.py
```

<figure><img src="/Atlas/examples/al/figures/fermi-slices.png" alt="Al 第2和第3能带的费米面截面" loading="lazy"/><figcaption>k₃=0 截面：实线与虚线对应两个真实 k 网格，颜色区分能带。横纵坐标是倒格矢分数坐标。</figcaption></figure>

网页版本需要联网加载 Plotly；在本机运行 `python3 plot_fermi.py --standalone` 可导出包含绘图库的独立 HTML。

[打开可转动的三维费米面](/Atlas/examples/al/figures/fermi-surface.html)。交互图以 32³ 本征值网格的零等值面构成，能量在相邻采样点间插值。图框是倒格矢坐标下的原始周期单元，不是已经裁剪成 Wigner–Seitz 第一布里渊区的图；边界处被切开的面会周期性地接到另一侧。

两次计算得到 E_F=8.39793432 eV 和 8.38150272 eV，相差约 0.01643 eV。画图时各自减去各自的 E_F，并比较口袋形状随网格的变化。这里确认了第二、第三带穿越费米能这一观察；细小口袋的尺寸、连接方式和后续嵌套峰，仍需要更密网格与展宽检查。

下一步到 [费米面嵌套](/Atlas/m/fermi-nesting/qe/) 看怎样将这些真实网格变成 J(q)，以及为什么几何面看起来能重合，不等于已经算出了电荷密度波或超导。

```text
同一结构 SCF → 全布里渊区 NSCF → 本征值/坐标逐点验收
                                       ↓
                       Eₙ(k) − E_F = 0 → 截面 / 三维费米面
                                       └→ 费米面几何嵌套 J(q)
```
