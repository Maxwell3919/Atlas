怎样从应变计算估算单层 MoS₂ 的二维声学形变势迁移率？需要连接三组 DFT 数据：应变总能量给出纵向弹性系数 C₂D，真空对齐的导带移动给出形变势 E₁，K 谷局部色散给出有效质量。本例在 300 K 得到 μx=200.386 cm²/(V·s)，并用应变区间、电子网格和真空厚度对照检查这些输入量的稳定性。

体系是公开构造的三原子 2H-MoS₂ 单层，使用 QE 7.5、PBE、标量相对论赝势，无 SOC。公式适用于低载流子浓度、近抛物 K 谷中的纵向声学形变势散射；光学、Fröhlich、谷间、压电、杂质与衬底散射需要另行计算。[Kaasbjerg 等的 MoS₂ 输运研究](https://arxiv.org/abs/1201.5284)说明了室温光学与 Fröhlich 散射的重要性。

[下载输入、QE 输出与 XML、原始数值、分析和绘图脚本](/Atlas/examples/transport-mobility-files.tar.gz)。包内保留三份未完成的 bands 原尝试及其完成的 bands-retry 分支，分析按 config.json 选取结果。原生 QE 复算从结构优化或所供最终几何的 SCF 开始，重新生成电荷密度与波函数保存目录；下载包提供 Python 后处理所需数据。

母体的面内优化可先读 [QE 晶胞优化](/Atlas/m/vc-relax/qe/)，应变后的内部坐标优化见 [QE 离子弛豫](/Atlas/m/relax/qe/)。每个构型都需要自己的 [SCF 电荷密度](/Atlas/m/scf/qe/)；局部 k 点和曲率单位可对照 [QE 有效质量](/Atlas/m/effective-mass/qe/)。这里展示的是纵向声学形变势模型所需的应变、真空电势和 K 谷数据。

## 从公开结构开始，先把母体优化好

结构由 [ASE 官方 mx2 构造器](https://wiki.fysik.dtu.dk/ase/_modules/ase/build/surface.html#mx2)生成：`MoS2`、`2H`、初始 a=3.18 Å、S–S 厚度 3.19 Å、上下各 10 Å 真空。初始 c=23.19 Å。这个初始几何不是优化结果，因此先在固定 c 的条件下优化面内晶格和内部坐标。

进入计算目录，准备两份来自 QE 官方库的赝势。下载链接分别为 [Mo PBE USPP](https://pseudopotentials.quantum-espresso.org/upf_files/Mo.pbe-spn-rrkjus_psl.1.0.0.UPF)与 [S PBE USPP](https://pseudopotentials.quantum-espresso.org/upf_files/S.pbe-n-rrkjus_psl.1.0.0.UPF)。文件头中的价电子数为 Mo 14、S 6，每个三原子晶胞共 26 个价电子。

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ sha256sum pseudo/*.UPF
0d7c57996e624698242e6428a34d5f13a1e52b4cddac2ce215be4dce429073dd  pseudo/Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
90fb585e830674f2de7b4cbace28d5dd0c05ca1a919d1f92a59b54d6b95cbfc4  pseudo/S.pbe-n-rrkjus_psl.1.0.0.UPF
```


母体使用 60/480 Ry、12×12×1 网格，固定 c 并保留六方晶格。进入 `base/`，用普通复制和编辑检查文件：

```text
maxwell@maxwell:<工作目录>/mos2-mobility/base$ cp mos2.vc-relax.prepared mos2.vc-relax.in
maxwell@maxwell:<工作目录>/mos2-mobility/base$ vi mos2.vc-relax.in
```

```text
maxwell@maxwell:<工作目录>/mos2-mobility/base$ cat mos2.vc-relax.in
&CONTROL
 calculation = 'vc-relax'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 60
 etot_conv_thr = 1.0d-7
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 4
 A = 3.18
 C = 23.19
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
/
&ELECTRONS
 conv_thr = 1.0d-11
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-9
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
&IONS
 ion_dynamics = 'bfgs'
/
&CELL
 cell_dynamics = 'bfgs'
 cell_dofree = 'ibrav+2Dxy'
 press_conv_thr = 0.1
/
ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
Mo 0.000000000000 0.000000000000 0.500000000000
S 0.666666666667 0.333333333333 0.568779646399
S 0.666666666667 0.333333333333 0.431220353601
K_POINTS automatic
12 12 1 0 0 0
```

`cell_dofree='ibrav+2Dxy'` 保持六方晶格并仅改变面内分量，真空方向保持不变。`forc_conv_thr` 是原子力阈值，`press_conv_thr` 约束允许变化的晶胞自由度。26 个电子占据 13 条自旋简并带；这里保留 16 条带，包含 3 条空带。

```text
maxwell@maxwell:<工作目录>/mos2-mobility/base$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-mos2-vc
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in mos2.vc-relax.in > mos2.vc-relax.out 2> mos2.vc-relax.err
```

```text
maxwell@maxwell:<工作目录>/mos2-mobility/base$ sbatch run.slurm
Submitted batch job 1983
```

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ grep -A 8 "bfgs converged" base/mos2.vc-relax.out
     bfgs converged in  10 scf cycles and   9 bfgs steps
     (criteria: energy <  1.0E-07 Ry, force <  1.0E-05 Ry/Bohr, cell <  1.0E-01 kbar)

     End of BFGS Geometry Optimization

     Final enthalpy           =    -181.5796085632 Ry

     File ./tmp/mos2.bfgs deleted, as requested
Begin final coordinates
```

BFGS 输出给出能量、力和晶胞的收敛阈值。最终几何为 a=3.18272795064 Å、A₀=8.77262707611 Å²、c=23.19 Å；所有应变从这一母体出发。

## 沿 x 拉伸，横向保持固定

只施加笛卡尔 εxx：x 分量乘 1+ε，y 与 z 分量不变。每个应变晶胞内的原子重新松弛，但晶胞不再松弛。因此从这条能量曲线取得的是横向固定、内部坐标松弛的纵向 Cxx²ᴰ，并非允许泊松收缩后的杨氏模量。

实际目录有 `minus010`、`minus005`、`zero`、`plus005`、`plus010`，分别对应 −1%、−0.5%、0、+0.5%、+1%。看 +0.5% 这一份：

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cp mos2.relax.prepared mos2.relax.in
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ vi mos2.relax.in
```

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cat mos2.relax.in
&CONTROL
 calculation = 'relax'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 40
 etot_conv_thr = 1.0d-8
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 0
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
/
&ELECTRONS
 conv_thr = 1.0d-12
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
&IONS
 ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
3.19864159039313 0.00000000000000 0.00000000000000
-1.59932079519656 2.75632325858916 0.00000000000000
0.00000000000000 0.00000000000000 23.19000000000000
ATOMIC_POSITIONS crystal
Mo -0.00000000000000 -0.00000000000000 0.50000000000000
S 0.66666666666700 0.33333333333300 0.56748189913164
S 0.66666666666700 0.33333333333300 0.43251810086836
K_POINTS automatic
12 12 1 0 0 0
```

第二条斜基矢的 x 分量也随 εxx 改变，y 分量保持母体值；仅拉长第一条基矢而遗漏第二条的 x 分量，会施加不同的应变。`calculation='relax'` 只允许原子移动，结束后取最后结构做固定几何 SCF。

每个目录中的完整串行脚本如下。输入转换程序只读取该目录已通过 BFGS 的最终结构，写出其固定结构 SCF 和谷附近的明确 k 点输入；可在下载材料中逐项查看程序和最后生成的文件。

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-mob-plus005
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in mos2.relax.in > mos2.relax.out 2> mos2.relax.err
python3 ../finish_mobility_relax.py > preparation.out
mpirun -np 8 <qe_bin>/pw.x -in mos2.scf.in > mos2.scf.out 2> mos2.scf.err
cp tmp/mos2.save/data-file-schema.xml scf.data-file-schema.xml
mpirun -np 8 <qe_bin>/pp.x -in potential.in > potential.out 2> potential.err
<qe_bin>/average.x < average.in > average.out 2> average.err
mpirun -np 8 <qe_bin>/pw.x -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml
```

每个应变作业申请 8 个 MPI 进程，依次执行离子松弛、固定几何 SCF、电势平均与能带计算。查看队列和几何优化输出：

```bash
squeue -u maxwell
tail -f plus005/mos2.relax.out
```

`Ctrl-C` 只退出 `tail` 的显示。几何优化过程可能反复完成 SCF，然后移动原子继续下一步；必须等 BFGS 自己报告收敛，不能把其中某次电子收敛当成整个优化通过。

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ grep -A 8 "bfgs converged" plus005/mos2.relax.out
     bfgs converged in   7 scf cycles and   6 bfgs steps
     (criteria: energy <  1.0E-08 Ry, force <  1.0E-05 Ry/Bohr)

     End of BFGS Geometry Optimization

     Final energy             =    -181.5795923091 Ry

     File ./tmp/mos2.bfgs deleted, as requested
Begin final coordinates
```

<details>
<summary>+0.5% 最终结构的完整 SCF 输入</summary>

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cat mos2.scf.in
&CONTROL
 calculation = 'scf'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 40
 etot_conv_thr = 1.0d-8
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 0
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
/
&ELECTRONS
 startingpot = 'file'
 startingwfc = 'file'
 conv_thr = 1.0d-12
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
3.19864159039313 0.00000000000000 0.00000000000000
-1.59932079519656 2.75632325858916 0.00000000000000
0.00000000000000 0.00000000000000 23.19000000000000
ATOMIC_POSITIONS crystal
Mo 0.00018719403948 0.00037438807896 0.50000000000000
S 0.66657306964726 0.33314613929352 0.56736815266106
S 0.66657306964726 0.33314613929352 0.43263184733894
K_POINTS automatic
12 12 1 0 0 0
```

</details>

`startingpot='file'`、`startingwfc='file'` 从同目录、同晶胞和同 k 网格的已收敛优化父链开始。这个复用有明确来源，不能从另一个应变目录复制波函数后假定仍然匹配。零应变分支较早启动的固定 SCF 使用原子叠加起点，两种起点最终都按相同电子阈值验收。

输出开头说明采用的原子数、价电子、截断能与 k 点；末段给出总能量分解、最终电子精度、原子力和应力。以下是 +0.5% 固定 SCF 的实际尾部物理信息：

```text
!    total energy              =    -181.57959231 Ry
     estimated scf accuracy    <          7.9E-16 Ry

     The total energy is the sum of the following terms:
     one-electron contribution =   -1374.11696100 Ry
     hartree contribution      =     686.59815959 Ry
     xc contribution           =     -29.68013364 Ry
     ewald contribution        =     535.61934275 Ry

     convergence has been achieved in   1 iterations

     negative rho (up, down):  3.873E-04 0.000E+00

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000   -0.00000678    0.00000000
     atom    2 type  2   force =     0.00000000    0.00000339   -0.00000132
     atom    3 type  2   force =     0.00000000    0.00000339    0.00000132
     The non-local contrib.  to forces
     atom    1 type  1   force =     0.00000000    0.00010271    0.00000000
     atom    2 type  2   force =     0.00000000    0.00019175   -0.27418759
     atom    3 type  2   force =     0.00000000    0.00019175    0.27418759
```

零应变 SCF 前期有两条 <code>1 eigenvalues not converged</code>，最终第 20 次电子步达到阈值且没有该告警。<code>cases.csv</code>分别记录全程与末次迭代的告警数；bands 的本征值需要在该次固定势求解中收敛。

零应变末次 SCF 的 <code>negative rho</code> 为 <code>3.851E-04 0.000E+00</code>，十一配置的第一分量范围约为 3.845×10⁻⁴–4.815×10⁻⁴。当前对照覆盖应变、k 网格、真空厚度和曲率窗口；截断能与 FFT 网格的影响仍需单独扫描。

## 真空平台给每个应变相同的能量参考

不同应变计算的能量零点不相同。直接对 OUT 中的导带数字做线性拟合，会混入任意势能常数。每个目录都从自己的 SCF 电荷密度计算静电势，再以自己的真空平台对齐导带。

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cat potential.in
&INPUTPP
 prefix = 'mos2'
 outdir = './tmp'
 filplot = 'electrostatic-potential.dat'
 plot_num = 11
/
```

`plot_num=11` 输出局域离子势与 Hartree 势之和。中间文件 `electrostatic-potential.dat` 保存三维 FFT 网格上的电势，单位是 Ry 能量。下面用 QE 自带的 `average.x` 沿 z 做平面平均：

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cat average.in
1
electrostatic-potential.dat
1.0
0
3
1.0
```

六行输入依次是文件数、文件名、权重、插值点数、平均方向和宏观平均窗口。本例 `npt=0` 让程序使用实际 FFT 网格，方向 3 对应垂直单层的 z；平面平均读 `avg.dat` 第二列，第三列是宏观平均，不混用两列。

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ head -6 plus005/avg.dat
    0.000000000    0.313251633    0.313250978
    0.136946090    0.313250475    0.313251122
    0.273892180    0.313251607    0.313250981
    0.410838271    0.313250524    0.313251114
    0.547784361    0.313251531    0.313250988
    0.684730451    0.313250618    0.313251100
```

第一列是 bohr，第二列是 Ry。分析时统一换成 Å 和 eV，在 z/c 的 0.10–0.20 与 0.80–0.90 两段分别取平台，比较两侧均值和各段起伏。对称中性单层两侧应给出同一参考，平台有斜率或上下差异明显时，不能直接用一个平均数盖过去。

零应变中，Vvac=4.2804901343 eV，拟合得到的 K 谷底原始本征值约 0.0221778672 eV，相减后为 −4.2583122671 eV。这两个数在同一分支中配对；不能拿零应变的 Vvac 去对齐其他应变。

真空平台与谷排序的实际数值如下，分别与电势起伏和能差容差比较：

| 零应变检查 | 实际结果 | 对照门槛与解释 |
| --- | ---: | --- |
| 左右真空平台最大起伏/差值 | 0.03189 meV | 门槛 1.0 meV，约低 31 倍 |
| K′−K | −0.00349 meV | 绝对差小于 0.010 meV 判定容差；两谷在本精度下简并 |
| 最低 Q−K（三个 Γ–K 方向） | +256.843 meV | 三个方向几乎一致，低于 M 与 Γ，但仍高于 K |
| M−K | +568.865 meV | 高于 K |
| Γ−K | +1087.728 meV | 高于 K |
| 采样能带间隙 | 1.68448 eV | 保持半导体态 |

完整势能与谷偏移复合图：[PNG](/Atlas/examples/transport-mobility/transport-vacuum-and-valleys.png) · [SVG](/Atlas/examples/transport-mobility/transport-vacuum-and-valleys.svg) · [PDF](/Atlas/examples/transport-mobility/transport-vacuum-and-valleys.pdf)。

## 沿应变后的谷底拟合有效质量

K 谷附近取一个二维局部网格，笛卡尔步长为 0.01 Å⁻¹，x、y 各取 −0.03 到 +0.03 Å⁻¹ 的 7 个值，共 49 点。每个应变使用自己的倒格矢变换。用二维二次曲面拟合局部极小值的位置，而不是始终读取一个固定 k 点的能量。

此外显式计算 Γ、M、K′，并沿三个 Γ–K 方向各取 15 点，总计 97 点。Q 区域在无量纲路径比例 t=0.40–0.80 内比较，k=tK；K 的选取随三个方向变化。<code>kpoints.csv</code>的 <code>GammaK_fraction</code>保存 t，<code>offsetx_invA</code>与<code>offsety_invA</code>专用于 K 局部笛卡尔位移。SCF 规则网格的最低导带另与拟合 K 谷比较；谷排序判定覆盖这些采样位置。

<details>
<summary>+0.5% 谷检查的完整 bands 输入：97 个实际 k 点</summary>

```text
maxwell@maxwell:<工作目录>/mos2-mobility/plus005$ cat mos2.bands.in
&CONTROL
 calculation = 'bands'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 40
 etot_conv_thr = 1.0d-8
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 0
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
 nosym = .true.
 noinv = .true.
/
&ELECTRONS
 conv_thr = 1.0d-12
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
3.19864159039313 0.00000000000000 0.00000000000000
-1.59932079519656 2.75632325858916 0.00000000000000
0.00000000000000 0.00000000000000 23.19000000000000
ATOMIC_POSITIONS crystal
Mo 0.00018719403948 0.00037438807896 0.50000000000000
S 0.66657306964726 0.33314613929352 0.56736815266106
S 0.66657306964726 0.33314613929352 0.43263184733894
K_POINTS crystal
97
0.31806094472462 0.32780905349678 0.00000000000000 1.0
0.31806094472462 0.33219587821042 0.00000000000000 1.0
0.31806094472462 0.33658270292405 0.00000000000000 1.0
0.31806094472462 0.34096952763769 0.00000000000000 1.0
0.31806094472462 0.34535635235133 0.00000000000000 1.0
0.31806094472462 0.34974317706496 0.00000000000000 1.0
0.31806094472462 0.35413000177860 0.00000000000000 1.0
0.32315174092753 0.32526365539533 0.00000000000000 1.0
0.32315174092753 0.32965048010896 0.00000000000000 1.0
0.32315174092753 0.33403730482260 0.00000000000000 1.0
0.32315174092753 0.33842412953624 0.00000000000000 1.0
0.32315174092753 0.34281095424987 0.00000000000000 1.0
0.32315174092753 0.34719777896351 0.00000000000000 1.0
0.32315174092753 0.35158460367715 0.00000000000000 1.0
0.32824253713043 0.32271825729388 0.00000000000000 1.0
0.32824253713043 0.32710508200751 0.00000000000000 1.0
0.32824253713043 0.33149190672115 0.00000000000000 1.0
0.32824253713043 0.33587873143479 0.00000000000000 1.0
0.32824253713043 0.34026555614842 0.00000000000000 1.0
0.32824253713043 0.34465238086206 0.00000000000000 1.0
0.32824253713043 0.34903920557569 0.00000000000000 1.0
0.33333333333333 0.32017285919242 0.00000000000000 1.0
0.33333333333333 0.32455968390606 0.00000000000000 1.0
0.33333333333333 0.32894650861970 0.00000000000000 1.0
0.33333333333333 0.33333333333333 0.00000000000000 1.0
0.33333333333333 0.33772015804697 0.00000000000000 1.0
0.33333333333333 0.34210698276061 0.00000000000000 1.0
0.33333333333333 0.34649380747424 0.00000000000000 1.0
0.33842412953624 0.31762746109097 0.00000000000000 1.0
0.33842412953624 0.32201428580461 0.00000000000000 1.0
0.33842412953624 0.32640111051825 0.00000000000000 1.0
0.33842412953624 0.33078793523188 0.00000000000000 1.0
0.33842412953624 0.33517475994552 0.00000000000000 1.0
0.33842412953624 0.33956158465915 0.00000000000000 1.0
0.33842412953624 0.34394840937279 0.00000000000000 1.0
0.34351492573914 0.31508206298952 0.00000000000000 1.0
0.34351492573914 0.31946888770316 0.00000000000000 1.0
0.34351492573914 0.32385571241679 0.00000000000000 1.0
0.34351492573914 0.32824253713043 0.00000000000000 1.0
0.34351492573914 0.33262936184407 0.00000000000000 1.0
0.34351492573914 0.33701618655770 0.00000000000000 1.0
0.34351492573914 0.34140301127134 0.00000000000000 1.0
0.34860572194204 0.31253666488807 0.00000000000000 1.0
0.34860572194204 0.31692348960170 0.00000000000000 1.0
0.34860572194204 0.32131031431534 0.00000000000000 1.0
0.34860572194204 0.32569713902898 0.00000000000000 1.0
0.34860572194204 0.33008396374261 0.00000000000000 1.0
0.34860572194204 0.33447078845625 0.00000000000000 1.0
0.34860572194204 0.33885761316989 0.00000000000000 1.0
0.00000000000000 0.00000000000000 0.00000000000000 1.0
0.50000000000000 0.00000000000000 0.00000000000000 1.0
-0.33333333333333 -0.33333333333333 -0.00000000000000 1.0
0.08333333333333 0.08333333333333 0.00000000000000 1.0
0.10000000000000 0.10000000000000 0.00000000000000 1.0
0.11666666666667 0.11666666666667 0.00000000000000 1.0
0.13333333333333 0.13333333333333 0.00000000000000 1.0
0.15000000000000 0.15000000000000 0.00000000000000 1.0
0.16666666666667 0.16666666666667 0.00000000000000 1.0
0.18333333333333 0.18333333333333 0.00000000000000 1.0
0.20000000000000 0.20000000000000 0.00000000000000 1.0
0.21666666666667 0.21666666666667 0.00000000000000 1.0
0.23333333333333 0.23333333333333 0.00000000000000 1.0
0.25000000000000 0.25000000000000 0.00000000000000 1.0
0.26666666666667 0.26666666666667 0.00000000000000 1.0
0.28333333333333 0.28333333333333 0.00000000000000 1.0
0.30000000000000 0.30000000000000 0.00000000000000 1.0
0.31666666666667 0.31666666666667 0.00000000000000 1.0
-0.16666666666667 0.08333333333333 0.00000000000000 1.0
-0.20000000000000 0.10000000000000 0.00000000000000 1.0
-0.23333333333333 0.11666666666667 0.00000000000000 1.0
-0.26666666666667 0.13333333333333 0.00000000000000 1.0
-0.30000000000000 0.15000000000000 0.00000000000000 1.0
-0.33333333333333 0.16666666666667 0.00000000000000 1.0
-0.36666666666667 0.18333333333333 0.00000000000000 1.0
-0.40000000000000 0.20000000000000 0.00000000000000 1.0
-0.43333333333333 0.21666666666667 0.00000000000000 1.0
-0.46666666666667 0.23333333333333 0.00000000000000 1.0
-0.50000000000000 0.25000000000000 0.00000000000000 1.0
-0.53333333333333 0.26666666666667 0.00000000000000 1.0
-0.56666666666667 0.28333333333333 0.00000000000000 1.0
-0.60000000000000 0.30000000000000 0.00000000000000 1.0
-0.63333333333333 0.31666666666667 0.00000000000000 1.0
0.08333333333333 -0.16666666666667 0.00000000000000 1.0
0.10000000000000 -0.20000000000000 0.00000000000000 1.0
0.11666666666667 -0.23333333333333 0.00000000000000 1.0
0.13333333333333 -0.26666666666667 0.00000000000000 1.0
0.15000000000000 -0.30000000000000 0.00000000000000 1.0
0.16666666666667 -0.33333333333333 0.00000000000000 1.0
0.18333333333333 -0.36666666666667 0.00000000000000 1.0
0.20000000000000 -0.40000000000000 0.00000000000000 1.0
0.21666666666667 -0.43333333333333 0.00000000000000 1.0
0.23333333333333 -0.46666666666667 0.00000000000000 1.0
0.25000000000000 -0.50000000000000 0.00000000000000 1.0
0.26666666666667 -0.53333333333333 0.00000000000000 1.0
0.28333333333333 -0.56666666666667 0.00000000000000 1.0
0.30000000000000 -0.60000000000000 0.00000000000000 1.0
0.31666666666667 -0.63333333333333 0.00000000000000 1.0
```

</details>

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ grep -A 15 "End of band structure calculation" plus005/mos2.bands.out
     End of band structure calculation

          k = 0.3181 0.5650 0.0000 ( 10766 PWs)   bands (ev):

   -62.5290 -36.7834 -36.7361 -36.6248 -13.6358 -13.5442  -7.0365  -6.2743
    -5.6789  -5.2133  -4.5456  -3.7968  -1.7094  -0.0200   1.3897   1.8226

          k = 0.3181 0.5701 0.0000 ( 10757 PWs)   bands (ev):

   -62.5290 -36.7827 -36.7370 -36.6248 -13.6346 -13.5435  -7.0387  -6.2642
    -5.6897  -5.2156  -4.5425  -3.8005  -1.7057  -0.0244   1.3887   1.8268

          k = 0.3181 0.5751 0.0000 ( 10755 PWs)   bands (ev):

   -62.5290 -36.7823 -36.7376 -36.6247 -13.6339 -13.5432  -7.0400  -6.2579
    -5.6964  -5.2169  -4.5406  -3.8027  -1.7035  -0.0271   1.3881   1.8293
```

每点有 16 个本征值，前 13 条占据，第 14 条是本例检查的最低导带。完整 XML 提供比屏幕四位小数更高的精度，曲率拟合使用 XML 的原始数值。第 14 条是否仍与其他带分离、谷底是否留在拟合区域里，也必须检查；金属、交叉带或非抛物谷不能直接代入此公式。

质量拟合使用 ±0.01、±0.02、±0.03 Å⁻¹ 三种二维方形窗口，分别包含 9、25、49 个采样点。写成 E(q)=E₀+v·q+½qᵀHq，极小值偏移是 −H⁻¹v，x 方向曲率质量为 ħ²/Hxx，态密度质量为 ħ²/√det(H)。因为 E 用 eV、q 用 Å⁻¹，H 的单位是 eV·Å²；用 ħ²/mₑ=7.619964231 eV·Å²，便可直接计算 mx/mₑ=7.619964231/Hxx，以及 md/mₑ=7.619964231/√det(H)。

Hxy 非零时，md 与 √(mx my) 不完全相等；后者只在所选坐标使交叉项为零时成立。这里的 mx=ħ²/Hxx 是沿 x 方向曲率所定义的质量；有交叉项时，它不是质量张量 M=ħ²H⁻¹ 的 xx 分量。本例的近各向同性 K 谷适合所用简化模型；推广到旋转的各向异性谷时，需要连同散射模型一起处理张量。

![K 谷的曲率与有效质量窗口检查](/Atlas/examples/transport-mobility/transport-effective-mass-windows.png)

左、中的圆点分别是零应变 K 谷沿笛卡尔 x、y 方向的截面（另一分量为零），实线是各截面的独立一维二次拟合，用于观察局部抛物形状；它们不是 Γ–K 扫描，也不用于替代二维质量。右图的 mx、my、md 来自每个二维方形窗口内全部采样点的 Hessian 拟合，连线仅连接三个窗口结果。

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ grep -e '^case,' -e '^zero,' mass-windows.csv
case,window_invA,mx_me,my_me,md_me,shift_x_invA,shift_y_invA,CBM_eV,fit_RMS_eV,fit_max_residual_eV,Hxy_eVA2
zero,0.01,0.45444614613586326,0.45471246278793787,0.45457928495910044,2.560123752940156e-05,-2.2897226725836738e-09,0.022172588993759075,4.543397079072445e-06,8.607535101394503e-06,1.4141009224159214e-06
zero,0.02,0.4560118247455952,0.4559465055835881,0.4559791639949692,6.659653068904663e-05,-1.226809186630084e-09,0.022177867166625027,3.164977028524813e-05,6.14986367195626e-05,-1.2565446092228515e-06
zero,0.03,0.45893936618406683,0.4589364866081122,0.45893792639383113,0.00012499550864600306,-6.094468692460792e-10,0.022201726043026494,9.177831588345768e-05,0.00019741314053896286,-2.0659789278941693e-07
```

后续迁移率采用 quality-gates.json 指定的 ±0.02 Å⁻¹ 中间窗口。零应变拟合的 Hxx=16.710015 eV·Å²、Hyy=16.712408 eV·Å²，得到 mx=0.456012mₑ、my=0.455947mₑ、md=0.455979mₑ。三个窗口的最大值与最小值之差除以中间窗口值，mx、my、md 分别变化 0.9853%、0.9264%、0.9559%，均低于本例 5% 的窗口检查阈值。单位 Å⁻¹ 不可漏掉：把晶体分数坐标直接当作笛卡尔 k，会使有效质量的量纲和数值都出错。

## 比较应变区间、k 网格与真空厚度

拟合时用无量纲应变 ε，例如 0.5% 写成 0.005、1% 写成 0.01。把各构型三原子晶胞的总能量转成 eV，拟合 E(ε)=E₀+a₁ε+a₂ε²，得到 Cxx²ᴰ=2a₂/A₀；能量不再除以原子数。面积用母体的真实面内面积，不除以含真空的三维体积。五点拟合给出 a₂≈36.168289 eV、A₀≈8.772627 Å²；用未舍入参数计算，Cxx²ᴰ=(2a₂/A₀)×16.02176634=132.110909 N/m，其中 1 eV/Å²=16.02176634 N/m。

带边则拟合 Ecb(ε)−Vvac(ε)=b₀+E₁ε，E₁ 的单位是 eV，进入散射公式的是 E₁²。用下表中央 ±0.5% 的真空对齐带边可先检查斜率：(−4.29929460−(−4.21711737))/(0.005−(−0.005))≈−8.217723 eV，与中央三点拟合一致。加入 ±1% 后，五点最小二乘拟合得到 E₁=−8.217569 eV；后续主结果使用这一五点值。

先比较五点与中央三点拟合，再保持对应已松弛原子结构，计算中央三点的 16×16×1 网格与 c 加厚 5 Å 的两组复核。厚真空组仍用 12×12×1。后一组把单层重新置于晶胞中央，不拉伸 S–Mo–S 厚度。这些复核检查电子采样和真空影响，不是另一套优化母体。

<details>
<summary>较密 k 网格复核的完整提交脚本</summary>

```text
maxwell@maxwell:<工作目录>/mos2-mobility/k16-plus005$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-k16-plus005
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mkdir -p tmp/mos2.save
cp ../plus005/tmp/mos2.save/charge-density.dat tmp/mos2.save/
mpirun -np 8 <qe_bin>/pw.x -nk 4 -in mos2.scf.in > mos2.scf.out 2> mos2.scf.err
cp tmp/mos2.save/data-file-schema.xml scf.data-file-schema.xml
mpirun -np 8 <qe_bin>/pp.x -in potential.in > potential.out 2> potential.err
<qe_bin>/average.x < average.in > average.out 2> average.err
mpirun -np 8 <qe_bin>/pw.x -nk 4 -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml
```

</details>

较密网格 SCF 复用同晶胞的电荷密度，并计算新网格的波函数；加厚真空改变了 FFT 网格，该组从原子电荷起点开始。脚本中的 <code>-nk 4</code>把 8 个 MPI 进程分为 4 个 k 点池，池数应结合本机性能选择。

<code>vacuum28-zero</code>、<code>k16-minus005</code>、<code>k16-plus005</code>的首次计算完成了 SCF 和电势处理，在 bands 阶段达到 15 分钟时限。各自的 <code>bands-retry/</code>随后从匹配的 SCF 电荷密度求解相同 97 个点，并在 30 分钟时限内完成，带数、截断和本征值阈值沿用原输入。

分析按 <code>config.json</code>的 <code>bands_subdir</code>选择三份完成的续算结果，其余配置使用本目录 bands。以下脚本需要匹配构型的已收敛 SCF 保存目录；下载包不含该保存树，执行原生续算前需先重做该构型 SCF：

```text
maxwell@maxwell:<工作目录>/mos2-mobility/k16-plus005/bands-retry$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-k16-plus005-bands
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mkdir -p tmp/mos2.save
cp ../tmp/mos2.save/charge-density.dat tmp/mos2.save/
cp ../scf.data-file-schema.xml tmp/mos2.save/data-file-schema.xml
cp ../../pseudo/*.UPF tmp/mos2.save/
mpirun -np 8 <qe_bin>/pw.x -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml
```

分析逐配置核对程序正常结束、末次 SCF、本征值告警、BFGS 与原子力，以及 SCF/bands 几何和 XML k 点顺序。十一配置的末次 SCF 与采用的 bands 均没有未收敛本征值告警。

下表来自完整 11 个配置，导带已经各自对齐真空：

| 配置 | εxx | 总能量 / eV | K 谷相对真空 / eV | 平台最大起伏 / meV |
| --- | --- | --- | --- | --- |
| k16-minus005 | -0.0050 | -2470.51518099 | -4.21711775 | 0.03422 |
| k16-plus005 | +0.0050 | -2470.51622272 | -4.29929219 | 0.02954 |
| k16-zero | +0.0000 | -2470.51661152 | -4.25832677 | 0.03191 |
| minus005 | -0.0050 | -2470.51517354 | -4.21711737 | 0.03422 |
| minus010 | -0.0100 | -2470.51186545 | -4.17570525 | 0.03648 |
| plus005 | +0.0050 | -2470.51621036 | -4.29929460 | 0.02954 |
| plus010 | +0.0100 | -2470.51408061 | -4.34005585 | 0.02716 |
| vacuum28-minus005 | -0.0050 | -2470.51518865 | -4.21709366 | 0.01714 |
| vacuum28-plus005 | +0.0050 | -2470.51622697 | -4.29928336 | 0.01495 |
| vacuum28-zero | +0.0000 | -2470.51661196 | -4.25831558 | 0.01596 |
| zero | +0.0000 | -2470.51658356 | -4.25831227 | 0.03189 |

![弹性与真空对齐导带的应变拟合](/Atlas/examples/transport-mobility/transport-deformation-fits.png)

绿色实线分别为五应变点的总能量二次拟合与真空对齐带边线性拟合；k16、vacuum28 的虚线连接各组三个实际样点，供网格和真空对照，不代表额外拟合或区间外预测。每组纵轴都减去该组零应变值。

| 拟合组 | Cxx²ᴰ / N·m⁻¹ | E₁ / eV | E₁ 标准误差 / eV | mx / mₑ | md / mₑ | μx / cm²·V⁻¹·s⁻¹ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 五应变 | 132.110909 | −8.217569 | 0.014778 | 0.456012 | 0.455979 | 200.385570 |
| 中央三应变 | 130.271104 | −8.217723 | 0.012272 | 0.456012 | 0.455979 | 197.587526 |
| 16×16×1 网格 | 132.908806 | −8.217444 | 0.014064 | 0.456013 | 0.455981 | 201.600618 |
| 加厚 5 Å 真空 | 132.101395 | −8.218970 | 0.014673 | 0.455467 | 0.455393 | 200.800568 |

表中的 E₁ 标准误差只来自线性回归残差，不包含截断、赝势、SOC 或散射模型带来的系统误差。

<code>quality-gates.json</code>保存本算例选用的检查阈值，并非适用于所有材料的精度标准：应变区间和 k 网格对 C₂D、E₁ 的相对影响不超过 5%，真空厚度的影响不超过 2%，质量窗口变化不超过 5%；|E₁| 至少 0.1 eV，回归相对标准误差不超过 10%。曲率非正、谷底越出窗口、候选最低谷改变或金属化时，分析停止输出迁移率。

十一配置通过所列检查。五应变拟合参数与零应变中间窗口质量给出 300 K 的 μx=200.386 cm²/(V·s)。

相对于中央三应变，五点拟合的 C₂D、E₁ 分别改变 1.4123%、0.00188%；16×16×1 网格分别改变 2.0248%、0.00340%；加厚 5 Å 真空分别改变 1.4050%、0.01517%。这些差异量化了当前采样选择对模型参数的影响。

公式为：

<p>μx = e ħ³ Cxx²ᴰ / (kB T mx md E₁²)。</p>

C₂D 用 N/m，质量换成 kg，E₁ 从 eV 换成 J。取 mₑ=9.1093837015×10⁻³¹ kg 和 1 eV=1.602176634×10⁻¹⁹ J，零应变中间窗口的 mx、md 分别为 4.153986684×10⁻³¹ kg、4.153689165×10⁻³¹ kg，五点 E₁=−1.316599668×10⁻¹⁸ J。300 K 时 kB T=4.141947×10⁻²¹ J。代入 e=1.602176634×10⁻¹⁹ C、ħ=1.054571817×10⁻³⁴ J·s 和 C₂D=132.110909 N/m，得到 μx=0.020038557 m²/(V·s)；乘 10⁴ 后为 200.385570 cm²/(V·s)。计算使用未舍入参数，[独立公式复核结果](/Atlas/examples/transport-mobility/transport-parameter-checks.json)保留逐项 SI 数值。

E₁ 回归标准误差单独传播的相对贡献为 2σ(E₁)/|E₁|=0.3597%，即 0.720739 cm²/(V·s)；它只描述带边线性拟合残差，不是包含弹性、质量、离散误差和散射模型的总误差条。

## 把应变、真空与曲率连成后处理

程序先按 config.json 找到各构型完成的分支，配对同一构型的总能量、真空平台和带边，再拟合弹性、形变势与质量。只有这些参数和候选谷检查都满足所列条件时，才代入迁移率公式。下载包中的配置、判定条件和输出表按下列结构组织：

| 文件 | 每行或条目含义 | 单位与用途 |
| --- | --- | --- |
| cases.csv | 一个计算构型 | εxx 无量纲；总能、真空电势和谷能差为 eV；面积为 Å²；高度为 Å；质量以 mₑ 表示 |
| mass-windows.csv | 一个构型的一种二维拟合窗口 | 窗口半宽与极值位移为 Å⁻¹；质量为 mₑ；残差为 eV；Hxy 为 eV·Å² |
| valley-bands.csv | 一个构型的一个采样 k 点 | K 局部位移为 Å⁻¹；Γ–K 路径比例为无量纲；本征值和真空对齐导带为 eV |
| potential-profiles.csv | 一个沿 z 的采样点 | z 为 Å；平面平均与宏观平均电势为 eV |
| quality-gates.json | 分析判定条件 | 包括单位明确的阈值、采样数、能带索引及温度 |
| summary.json | 拟合和判定结果 | 完成数、失败项、拟合参数、质量与迁移率 |
| config.json | 构型与数据分支 | 应变、网格、真空增量和 bands_subdir |
| FILE_SHA256.json | 下载包文件清单 | 每份文件的大小与 SHA-256 |

下面的具体提示词可交给 AI 编写程序，并与完整源码和保存结果逐项比较。

<details><summary>展开完整提示词</summary><pre><code>为 QE 7.5 单层 MoS2 声学形变势示例编写 Python 3 后处理器，读取下载包的已有文件，输出应变拟合、真空对齐、二维有效质量与参数敏感性表。

输入：逐配置 config.json、QE OUT/XML、avg.dat、kpoints.csv，以及 quality-gates.json。按 bands_subdir 选择 bands；保存未完成原尝试的状态。核对 pw.x、pp.x、average.x 的 JOB DONE.、末次 SCF 收敛、本征值告警、SCF/bands 几何及 XML k 点映射。avg.dat 恰有三列：Bohr 坐标、Ry 平面平均、Ry 宏观平均；检查有限值、坐标单调与晶胞高度，用第二列作真空参考。

真空窗口由 quality-gates.json 指定，在 c 的 10–20% 与 80–90% 分别取均值和起伏。各构型单独计算 Vvac，再拟合 E_CB,K−Vvac 对 εxx 的斜率 E1。总能量二次拟合 E0+a1 ε+a2 ε²，以 C2D=2a2/A0、1 eV/Å²=16.02176634 N/m 转换弹性常数。K 局部 offsetx_invA/offsety_invA 为笛卡尔 Å⁻¹；GammaK_fraction 是无量纲路径比例 t，k=tK，不可混用。

由 E(q)=E0+v·q+½qᵀHq 得极值 −H⁻¹v，要求 H 正定，mx=ħ²/Hxx、my=ħ²/Hyy、md=ħ²/√det(H)。报告三个窗口的质量、Hxy、极值位移与残差。全部判定阈值从 quality-gates.json 读取。

11 个构型齐全且所列判定通过时，计算 μ=eℏ³C2D/(kB T mx md E1²)，先用 N/m、J、kg 得 m²/(V s)，再转 cm²/(V s)。保留 E1 符号，散射式中取平方。给出声学形变势模型状态；判定失败则列明失败项并将迁移率设为空。E1 回归标准误差的传播只作为该项贡献，参数对照组作为敏感性检查。

输出 CSV/JSON 和运行命令，保留原始 OUT/XML。应变与局部曲率需要看拟合形状，可使用实际数据曲线；平台起伏、谷简并容差与判定结果用表格直接比较。注明依赖和单位；不启动 DFT、不补造数据。</code></pre></details>

## 完整源码与逐项结果

[分析器](/Atlas/examples/transport-mobility/analyse_mobility.py)读取每个配置的 OUT、XML、avg.dat 与 k 点表，重建 CSV 和 summary.json；[公式复核脚本](/Atlas/examples/transport-mobility/transport_mobility_check.py)只依赖标准库，用 SI 常数核对迁移率，并写出参数敏感性表。[mobility_common.py](/Atlas/examples/transport-mobility/mobility_common.py)提供 XML 晶胞与原子坐标读取、几何和 k 点坐标转换，应与分析器放在同一目录；OUT 状态和 XML 本征值由分析器读取。保存结果使用 Python 3.12.3、NumPy 2.4.6。

<details>
<summary>analyse_mobility.py 的完整源码</summary>

```python
"""Extract scalar MoS2 acoustic deformation-potential parameters from native QE outputs."""
from pathlib import Path
import numpy as np,xml.etree.ElementTree as ET,csv,json,re
from mobility_common import geometry,BOHR
R=Path(__file__).resolve().parent
HA=27.211386245988;RY=HA/2;HBAR2_ME=7.619964231
records=[];massrows=[];bandrows=[];potentialrows=[];fail=[]
G=json.loads((R/'quality-gates.json').read_text())

def xml_eig(p):
 r=ET.parse(p).getroot();ks=r.findall('output/band_structure/ks_energies')
 e=np.array([np.fromstring(k.find('eigenvalues').text,sep=' ') for k in ks])*HA
 return e,r

def fit_local(x,y,E,window):
 sel=(abs(x)<=window+G['mass_window_inclusion_tolerance_invA'])&(abs(y)<=window+G['mass_window_inclusion_tolerance_invA']);xx=x[sel];yy=y[sel];ee=E[sel]
 X=np.column_stack([np.ones(len(xx)),xx,yy,.5*xx*xx,xx*yy,.5*yy*yy])
 c=np.linalg.lstsq(X,ee,rcond=None)[0];H=np.array([[c[3],c[4]],[c[4],c[5]]]);ev=np.linalg.eigvalsh(H)
 if ev.min()<=G['effective_mass_curvature_min_eV_A2']:raise ValueError('Nonpositivecurvature')
 shift=-np.linalg.solve(H,c[1:3]);emin=c[0]+.5*np.dot(c[1:3],shift)
 return {'window':window,'H':H,'mx':HBAR2_ME/H[0,0],'my':HBAR2_ME/H[1,1],'md':HBAR2_ME/np.sqrt(np.linalg.det(H)),'shift':shift,'emin':emin,'rms':np.sqrt(np.mean((X@c-ee)**2)),'residual_max':np.max(abs(X@c-ee))}

all_dirs=sorted([p for p in R.iterdir() if p.is_dir() and (p/'config.json').exists()])
for d in all_dirs:
 conf=json.loads((d/'config.json').read_text())
 bd=d/conf.get('bands_subdir','.')
 required=['mos2.scf.out','potential.out','average.out','mos2.bands.out']
 if not all(((bd if x=='mos2.bands.out' else d)/x).exists() for x in required):fail.append(d.name+':unfinished');continue
 for out in required:
  text=((bd if out=='mos2.bands.out' else d)/out).read_text()
  if 'JOB DONE.' not in text:fail.append(d.name+':'+out+':noJOBDONE')
  if 'Error in routine' in text:fail.append(d.name+':'+out+':nativeerror')
  if out=='mos2.scf.out':
   if 'not converged' in text.rsplit('iteration #',1)[-1] or 'convergence has been achieved' not in text:fail.append(d.name+':finalSCFnotaccepted')
  elif 'not converged' in text:fail.append(d.name+':'+out+':unconvergedeigenvalues')
 if not (bd/'bands.data-file-schema.xml').exists():continue
 e,r=xml_eig(bd/'bands.data-file-schema.xml');scfe,sr=xml_eig(d/'scf.data-file-schema.xml')
 ne=float(sr.find('output/band_structure/nelec').text)
 if abs(ne-G['expected_valence_electrons'])>G['electron_count_abs_tolerance']:
  fail.append(d.name+':unexpectedvalenceelectroncount');continue
 val=G['analysis_band_indices']['valence'];cb=G['analysis_band_indices']['conduction'];cb_next=G['analysis_band_indices']['next_conduction']
 cell,pos,sp=geometry(d/'scf.data-file-schema.xml');area=np.linalg.norm(np.cross(cell[0],cell[1]));height=cell[2,2]
 etot=float(sr.find('output/total_energy/etot').text)*HA
 forces=np.array([float(v) for v in sr.find('output/forces').text.split()]).reshape(-1,3)*HA/BOHR
 avg=np.loadtxt(d/'avg.dat',ndmin=2)
 if avg.shape[1]!=3 or not np.all(np.isfinite(avg)):
  fail.append(d.name+':avgdatmusthave3finitecolumns');continue
 dz_bohr=float(avg[-1,0]-avg[-2,0])
 if (np.any(np.diff(avg[:,0])<=0) or abs(avg[0,0])>G['average_coordinate_origin_abs_max_bohr'] or abs(avg[-1,0]+dz_bohr-height/BOHR)>G['average_cell_extent_abs_diff_max_bohr']):
  fail.append(d.name+':avgdatcoordinategridmismatch');continue
 z=avg[:,0]*BOHR;V=avg[:,1]*RY;Vm=avg[:,2]*RY
 wleft,wright=G['average_vacuum_windows_c_fraction']
 left=(z>wleft[0]*height)&(z<wleft[1]*height);right=(z>wright[0]*height)&(z<wright[1]*height)
 if left.sum()<G['average_vacuum_window_minimum_points'] or right.sum()<G['average_vacuum_window_minimum_points']:
  fail.append(d.name+':too few points in vacuum windows');continue
 vl=V[left].mean();vr=V[right].mean();vv=(vl+vr)/2
 flat=max(np.ptp(V[left]),np.ptp(V[right]),abs(vl-vr))
 krows=list(csv.DictReader((d/'kpoints.csv').open()))
 if len(krows)!=len(e) or len(krows)!=G['expected_bands_kpoint_count']:
  fail.append(d.name+':unexpectedbandskpointcount');continue
 b=2*np.pi*np.linalg.inv(cell).T
 expected_k=np.array([[float(k[x]) for x in ['k1','k2','k3']] for k in krows])@b
 alat=float(r.find('output/atomic_structure').attrib['alat'])*BOHR
 actual_k=np.array([np.fromstring(kk.find('k_point').text,sep=' ') for kk in r.findall('output/band_structure/ks_energies')])*2*np.pi/alat
 kerr=float(np.max(abs(expected_k-actual_k)))
 if kerr>G['kpoint_mapping_max_abs_error_invA']:fail.append(d.name+':nativekpointorderormappingmismatch')
 bcell,bpos,bsp=geometry(bd/'bands.data-file-schema.xml')
 if np.max(abs(cell-bcell))>G['scf_bands_geometry_max_abs_difference_A'] or np.max(abs(pos-bpos))>G['scf_bands_geometry_max_abs_difference_A'] or sp!=bsp:fail.append(d.name+':SCFbandsgeometrymismatch')
 ids=np.array([x['kind']=='K-local' for x in krows]);x=np.array([float(k['offsetx_invA']) for k in krows if k['kind']=='K-local']);y=np.array([float(k['offsety_invA']) for k in krows if k['kind']=='K-local'])
 try:
  fits=[fit_local(x,y,e[ids,cb],w) for w in G['mass_fit_half_widths_invA']]
 except ValueError as err:
  fail.append(d.name+':massfit:'+str(err).replace(' ','_'));continue
 fit=fits[min(range(len(fits)),key=lambda i:abs(fits[i]['window']-G['mass_fit_reference_half_width_invA']))]
 kp=float(e[[k['kind']=='K-prime' for k in krows],cb][0])
 gamma=float(e[[k['kind']=='Gamma' for k in krows],cb][0]);M=float(e[[k['kind']=='M' for k in krows],cb][0])
 q=[]
 for j in range(1,4):
  qlo,qhi=G['q_valley_scan_GammaK_fraction']
  ind=np.array([k['kind']==f'Gamma-K{j}' and qlo-G['q_scan_bound_tolerance_fraction']<=float(k['GammaK_fraction'])<=qhi+G['q_scan_bound_tolerance_fraction'] for k in krows]);q.append(float(e[ind,cb].min()))
 gap=float(e[:,cb].min()-e[:,val].max())
 coarse_min=float(scfe[:,cb].min())
 row={'case':d.name,'epsilon':conf['epsilon_xx'],'mesh':conf['mesh'],'vacuum_add_A':conf['vacuum_add_A'],'etot_eV':etot,'area_A2':area,'height_A':height,'vacuum_eV':vv,'plateau_left_eV':vl,'plateau_right_eV':vr,'plateau_spread_eV':flat,'CBnext_CBlocal_min_separation_eV':float(np.min(e[ids,cb_next]-e[ids,cb])),'bands_source':str(bd.relative_to(R)),'kpoint_mapping_max_invA':kerr,'K_CBM_eV':float(fit['emin']),'K_CBM_vac_eV':float(fit['emin']-vv),'K_shift_x_invA':float(fit['shift'][0]),'K_shift_y_invA':float(fit['shift'][1]),'Kprime_minus_K_eV':kp-float(fit['emin']),'Gamma_minus_K_eV':gamma-float(fit['emin']),'M_minus_K_eV':M-float(fit['emin']),'Q1_minus_K_eV':q[0]-float(fit['emin']),'Q2_minus_K_eV':q[1]-float(fit['emin']),'Q3_minus_K_eV':q[2]-float(fit['emin']),'coarse_scf_CBM_minus_K_eV':coarse_min-float(fit['emin']),'sampled_gap_eV':gap,'force_max_eVA':float(np.linalg.norm(forces,axis=1).max()),'mx_me':float(fit['mx']),'my_me':float(fit['my']),'md_me':float(fit['md']),'fit_residual_eV':float(fit['residual_max']),'SCF_intermediate_eigenwarning_count':(d/'mos2.scf.out').read_text().count('not converged'),'SCF_final_eigenwarning_count':(d/'mos2.scf.out').read_text().rsplit('iteration #',1)[-1].count('not converged')}
 records.append(row)
 for f in fits:massrows.append({'case':d.name,'window_invA':f['window'],'mx_me':f['mx'],'my_me':f['my'],'md_me':f['md'],'shift_x_invA':f['shift'][0],'shift_y_invA':f['shift'][1],'CBM_eV':f['emin'],'fit_RMS_eV':f['rms'],'fit_max_residual_eV':f['residual_max'],'Hxy_eVA2':f['H'][0,1]})
 for i,k in enumerate(krows):bandrows.append({'case':d.name,'point':i+1,**k,'valence_eV':e[i,val],'conduction_eV':e[i,cb],'conduction_vac_eV':e[i,cb]-vv})
 for zi,vi,vmi in zip(z,V,Vm):potentialrows.append({'case':d.name,'z_A':zi,'potential_eV':vi,'macroscopic_average_eV':vmi})
 if conf['vacuum_add_A']==0 and conf['mesh']==12:
  if 'bfgs converged' not in (d/'mos2.relax.out').read_text().lower():fail.append(d.name+':ionicrelaxnotaccepted')
  if np.max(abs(forces))>G['relaxed_scf_force_component_max_eV_per_A']:fail.append(d.name+':finalSCFforceexceedsionicthreshold')
 if flat>G['vacuum_plateau_spread_eV_max']:fail.append(d.name+':vacuumplateaunotflat')
 if gap<=G['semiconducting_gap_min_eV'] or min(q+[gamma,M,kp])<fit['emin']-G['candidate_valley_energy_tolerance_eV'] or coarse_min<fit['emin']-G['coarse_scf_cbm_tolerance_eV']:fail.append(d.name+':Knotlowestcheckedsemiconductingvalley')
 if np.min(e[ids,cb_next]-e[ids,cb])<G['conduction_band_isolation_min_eV']:fail.append(d.name+':CB14notisolatedfromCB15')
 if max(abs(fit['shift']))>G['K_minimum_shift_max_invA']:fail.append(d.name+':Kminimumoutsidecentralfitwindow')

def write(name,rows):
 if not rows:return
 with (R/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('cases.csv',records);write('mass-windows.csv',massrows);write('valley-bands.csv',bandrows);write('potential-profiles.csv',potentialrows)
by={r['case']:r for r in records};summary={'completed_cases':len(records),'expected_cases':G['expected_case_count'],'failures':fail,'model':'scalar-PBE K-valley longitudinal acoustic deformation potential only','temperature_K':G['model_temperature_K'],'mobility_cm2_Vs':None,'quality_gates':G}
if len(records)==G['expected_case_count']:
 A0=by['zero']['area_A2']
 def params(names):
  rr=sorted([by[n] for n in names],key=lambda x:x['epsilon']);eps=np.array([x['epsilon'] for x in rr]);Et=np.array([x['etot_eV'] for x in rr]);Ec=np.array([x['K_CBM_vac_eV'] for x in rr]);En=Et-Et[len(Et)//2]
  energy=np.polyfit(eps,En,2);coef,cov=np.polyfit(eps,Ec,1,cov=True)
  return {'C2D_N_m':float(2*energy[0]/A0*16.02176634),'E1_eV':float(coef[0]),'E1_standard_error_eV':float(np.sqrt(cov[0,0])),'energy_fit_max_residual_eV':float(np.max(abs(np.polyval(energy,eps)-En))),'edge_fit_max_residual_eV':float(np.max(abs(np.polyval(coef,eps)-Ec)))}
 sets={'five_strains':['minus010','minus005','zero','plus005','plus010'],'three_strains':['minus005','zero','plus005'],'k16':['k16-minus005','k16-zero','k16-plus005'],'vacuum28':['vacuum28-minus005','vacuum28-zero','vacuum28-plus005']}
 ps={k:params(v) for k,v in sets.items()};summary['fits']=ps
 base=ps['three_strains'];full=ps['five_strains']
 for name,limit in [('five_strains',G['C_and_E1_strain_window_relative_max']),('k16',G['kgrid_C_E1_relative_max']),('vacuum28',G['vacuum_C_E1_relative_max'])]:
  for key in ['C2D_N_m','E1_eV']:
   change=abs(ps[name][key]-base[key])/abs(base[key]);ps[name][key+'_relative_vs_three']=float(change)
   if change>limit:fail.append(name+':'+key+':differenceexceedsgate')
 if full['C2D_N_m']<=G['C2D_min_N_m']:fail.append('nonpositiveelasticconstant')
 if abs(full['E1_eV'])<G['E1_abs_min_eV'] or full['E1_standard_error_eV']/abs(full['E1_eV'])>G['E1_relative_fit_uncertainty_max']:fail.append('E1nearzeroorunstable')
 mm=[x for x in massrows if x['case']=='zero']
 for key in ['mx_me','my_me','md_me']:
  refmass=min(mm,key=lambda x:abs(x['window_invA']-G['mass_fit_reference_half_width_invA']))
  spread=np.ptp([x[key] for x in mm])/refmass[key]
  if spread>G['mass_window_relative_max']:fail.append('masswindowunstable:'+key)
 summary['baseline_masses']={k:by['zero'][k] for k in ['mx_me','my_me','md_me']}
 # State the sign ofE1 separately; scattering uses its square.
 if not fail:
  ee=1.602176634e-19;hbar=1.054571817e-34;kb=1.380649e-23;me=9.1093837015e-31
  mu=ee*hbar**3*full['C2D_N_m']/(kb*G['model_temperature_K']*(by['zero']['mx_me']*me)*(by['zero']['md_me']*me)*(full['E1_eV']*ee)**2)*1e4
  summary['mobility_cm2_Vs']=float(mu)
  summary['mobility_status']='acoustic-DP-only estimate; not full electron-phonon transport'
 else:summary['mobility_status']='Not reported: finite-difference/model gates not all met'
else:summary['mobility_status']='Notreported:requiredcasesincomplete'
(R/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('case            strain     Etot(eV)        EC-Vvac(eV)  maxplateau(eV)  Qmin-K(eV)')
for r in records:print(f"{r['case']:19s} {r['epsilon']:+.4f} {r['etot_eV']:15.8f} {r['K_CBM_vac_eV']:12.8f} {r['plateau_spread_eV']:12.3e} {min(r['Q1_minus_K_eV'],r['Q2_minus_K_eV'],r['Q3_minus_K_eV']):10.6f}")
print(json.dumps(summary,indent=2))
```

</details>

<details>
<summary>transport_mobility_check.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Recompute the acoustic deformation-potential estimate and expose sensitivities.

Reads only the accepted analysis tables; it does not launch Quantum ESPRESSO.
The reported E1-only propagated error is a regression contribution, not a total
uncertainty or a confidence interval for material mobility.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E_CHARGE_C = 1.602176634e-19
HBAR_J_S = 1.054571817e-34
KB_J_K = 1.380649e-23
ELECTRON_MASS_KG = 9.1093837015e-31
EV_PER_ANGSTROM2_TO_N_PER_M = 16.02176634


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def mobility_cm2_vs(C_N_m: float, E1_eV: float, mx_me: float,
                    md_me: float, temperature_K: float) -> float:
    if C_N_m <= 0 or mx_me <= 0 or md_me <= 0 or temperature_K <= 0:
        raise ValueError("C, masses and temperature must be positive")
    if not math.isfinite(E1_eV) or abs(E1_eV) == 0:
        raise ValueError("E1 must be finite and nonzero")
    mx_kg = mx_me * ELECTRON_MASS_KG
    md_kg = md_me * ELECTRON_MASS_KG
    E1_J = E1_eV * E_CHARGE_C
    mu_m2_vs = (E_CHARGE_C * HBAR_J_S**3 * C_N_m /
                (KB_J_K * temperature_K * mx_kg * md_kg * E1_J**2))
    return mu_m2_vs * 1.0e4


def main() -> None:
    summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    cases = {row["case"]: row for row in read_csv("cases.csv")}
    if summary["failures"]:
        raise SystemExit(f"model gates failed: {summary['failures']}")
    if summary["completed_cases"] != summary["expected_cases"]:
        raise SystemExit("the accepted case set is incomplete")

    fit_to_mass_case = {
        "five_strains": "zero",
        "three_strains": "zero",
        "k16": "k16-zero",
        "vacuum28": "vacuum28-zero",
    }
    rows = {}
    for fit_name, mass_case in fit_to_mass_case.items():
        fit = summary["fits"][fit_name]
        mass = cases[mass_case]
        rows[fit_name] = {
            "mass_case": mass_case,
            "C2D_N_m": fit["C2D_N_m"],
            "E1_eV": fit["E1_eV"],
            "E1_fit_standard_error_eV": fit["E1_standard_error_eV"],
            "mx_me": float(mass["mx_me"]),
            "md_me": float(mass["md_me"]),
            "mobility_cm2_Vs": mobility_cm2_vs(
                fit["C2D_N_m"], fit["E1_eV"],
                float(mass["mx_me"]), float(mass["md_me"]),
                float(summary["temperature_K"])),
        }
    base = rows["five_strains"]["mobility_cm2_Vs"]
    for row in rows.values():
        row["relative_to_five_strains"] = row["mobility_cm2_Vs"] / base - 1.0

    accepted_value = summary["mobility_cm2_Vs"]
    if not math.isclose(base, accepted_value, rel_tol=1e-10, abs_tol=1e-8):
        raise SystemExit(
            f"formula check failed: recomputed {base:.12g}, summary {accepted_value:.12g}")

    e1 = rows["five_strains"]["E1_eV"]
    e1_sigma = rows["five_strains"]["E1_fit_standard_error_eV"]
    relative_mu_sigma_e1_only = 2.0 * e1_sigma / abs(e1)
    report = {
        "model": "K-valley longitudinal acoustic deformation potential only",
        "mobility_cm2_Vs": base,
        "temperature_K": float(summary["temperature_K"]),
        "formula": "e*hbar^3*C2D/(kB*T*mx*md*E1^2)",
        "input_units": {
            "C2D": "N/m",
            "E1": "eV, converted to joule before substitution",
            "mx_md": "multiples of m_e, converted to kg before substitution",
            "output_before_area_conversion": "m^2/(V s)",
            "output_after_area_conversion": "cm^2/(V s); multiply m^2/(V s) by 1e4",
        },
        "conversion_constants": {
            "elementary_charge_C": E_CHARGE_C,
            "hbar_J_s": HBAR_J_S,
            "kB_J_K": KB_J_K,
            "electron_mass_kg": ELECTRON_MASS_KG,
            "1_eV_per_A2_to_N_per_m": EV_PER_ANGSTROM2_TO_N_PER_M,
        },
        "fit_group_sensitivities": rows,
        "E1_fit_only_error_propagation": {
            "E1_standard_error_eV": e1_sigma,
            "relative_mu_standard_error_from_E1_only": relative_mu_sigma_e1_only,
            "mu_standard_error_from_E1_only_cm2_Vs": base * relative_mu_sigma_e1_only,
            "derivative": "d ln(mu)/d ln(|E1|) = -2",
            "limitation": "Excludes C2D/mass-fit, numerical-protocol and physical-model errors; not a total uncertainty.",
        },
        "full_transport_calculation": False,
        "status": "acoustic-DP estimate only; no full electron-phonon scattering integral or Boltzmann transport solution",
    }
    out = ROOT / "transport-parameter-checks.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name, row in rows.items():
        print(f"{name:13s} C2D={row['C2D_N_m']:.6f} N/m  "
              f"E1={row['E1_eV']:.6f} eV  "
              f"mx={row['mx_me']:.6f} me  md={row['md_me']:.6f} me  "
              f"mu={row['mobility_cm2_Vs']:.6f} cm^2/(V s)")
    print(f"E1-fit-only propagated contribution: "
          f"{relative_mu_sigma_e1_only * 100:.4f}% = "
          f"{base * relative_mu_sigma_e1_only:.6f} cm^2/(V s)")
    print(f"Full electron-phonon transport: not calculated; wrote {out.name}")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>mobility_common.py 的完整源码</summary>

```python
from pathlib import Path
import numpy as np,xml.etree.ElementTree as ET
BOHR=.529177210903
ROOT=Path(__file__).resolve().parent

def geometry(xml):
 r=ET.parse(xml).getroot();st=r.find('output/atomic_structure')
 cell=np.array([np.fromstring(x.text,sep=' ') for x in st.find('cell')])*BOHR
 atoms=list(st.find('atomic_positions'));species=[x.attrib['name'] for x in atoms]
 pos=np.array([np.fromstring(x.text,sep=' ') for x in atoms])*BOHR
 return cell,pos,species

def input_pw(cell,pos,species,calc='scf',mesh=12,kpoints=None):
 ions="&IONS\n ion_dynamics = 'bfgs'\n/\n" if calc=='relax' else ''
 flags=" nosym = .true.\n noinv = .true.\n" if calc=='bands' else ''
 frac=pos@np.linalg.inv(cell)
 cards='CELL_PARAMETERS angstrom\n'+''.join(' '.join(f'{x:.14f}' for x in v)+'\n' for v in cell)+'ATOMIC_POSITIONS crystal\n'+''.join(s+' '+' '.join(f'{x:.14f}' for x in v)+'\n' for s,v in zip(species,frac))
 if kpoints is None:cards+=f'K_POINTS automatic\n{mesh} {mesh} 1 0 0 0\n'
 else:cards+='K_POINTS crystal\n'+str(len(kpoints))+'\n'+''.join(' '.join(f'{x:.14f}' for x in k)+' 1.0\n' for k in kpoints)
 return f"""&CONTROL
 calculation = '{calc}'
 prefix = 'mos2'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 verbosity = 'high'
 tstress = .true.
 tprnfor = .true.
 nstep = 40
 etot_conv_thr = 1.0d-8
 forc_conv_thr = 1.0d-5
/
&SYSTEM
 ibrav = 0
 nat = 3
 ntyp = 2
 ecutwfc = 60
 ecutrho = 480
 nbnd = 16
 occupations = 'fixed'
{flags}/
&ELECTRONS
 conv_thr = 1.0d-12
 mixing_beta = 0.3
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
{ions}ATOMIC_SPECIES
Mo 95.95 Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
S 32.06 S.pbe-n-rrkjus_psl.1.0.0.UPF
{cards}"""

def kset(cell):
 b=2*np.pi*np.linalg.inv(cell).T;rows=[];ks=[]
 K=np.array([1/3,1/3,0.]);Kcart=K@b
 for dx in [-.03,-.02,-.01,0,.01,.02,.03]:
  for dy in [-.03,-.02,-.01,0,.01,.02,.03]:
   k=(Kcart+[dx,dy,0])@np.linalg.inv(b);ks.append(k);rows.append(['K-local',dx,dy,*k,''])
 for label,k in [('Gamma',np.zeros(3)),('M',np.array([.5,0,0])),('K-prime',-K)]:
  ks.append(k);rows.append([label,0,0,*k,''])
 for direction,Kend in enumerate([K,np.array([-2/3,1/3,0.]),np.array([1/3,-2/3,0.])]):
  for t in np.linspace(.25,.95,15):
   k=t*Kend;ks.append(k);rows.append([f'Gamma-K{direction+1}','','',*k,t])
 return np.array(ks),rows

def slurm(name,body):return f'''#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
{body}'''

QE='<qe_bin>/'
BODY=f'''mpirun -np 8 {QE}pw.x -in mos2.scf.in > mos2.scf.out 2> mos2.scf.err
cp tmp/mos2.save/data-file-schema.xml scf.data-file-schema.xml
mpirun -np 8 {QE}pp.x -in potential.in > potential.out 2> potential.err
{QE}average.x < average.in > average.out 2> average.err
mpirun -np 8 {QE}pw.x -in mos2.bands.in > mos2.bands.out 2> mos2.bands.err
cp tmp/mos2.save/data-file-schema.xml bands.data-file-schema.xml
'''
def post_inputs(d):
 (d/'potential.in').write_text("&INPUTPP\n prefix = 'mos2'\n outdir = './tmp'\n filplot = 'electrostatic-potential.dat'\n plot_num = 11\n/\n")
 (d/'average.in').write_text('1\nelectrostatic-potential.dat\n1.0\n0\n3\n1.0\n')
```

</details>

QE 7.5 的 <code>pp.x</code>用 <code>plot_num=11</code>输出 <code>V_bare+V_H</code>；[pp.x 文档](https://www.quantum-espresso.org/Doc/INPUT_PP.html)与[average.f90 源码](https://gitlab.com/QEF/q-e/-/blob/qe-7.5/PP/src/average.f90)给出数据含义。<code>avg.dat</code>三列分别是 Bohr 坐标、Ry 平面平均和 Ry 宏观平均；后处理用第二列取真空参考，并检查三列均有限、坐标递增且覆盖本晶胞。

页面的两组图分别显示应变拟合与 K 谷二次曲率。已有的势能与谷比较复合图也保存在包中。下载图件：[应变拟合 PNG](/Atlas/examples/transport-mobility/transport-deformation-fits.png) · [SVG](/Atlas/examples/transport-mobility/transport-deformation-fits.svg) · [PDF](/Atlas/examples/transport-mobility/transport-deformation-fits.pdf)；[质量窗口 PNG](/Atlas/examples/transport-mobility/transport-effective-mass-windows.png) · [SVG](/Atlas/examples/transport-mobility/transport-effective-mass-windows.svg) · [PDF](/Atlas/examples/transport-mobility/transport-effective-mass-windows.pdf)。

## 运行分析，核对模型与数值

解压后进入 <code>transport-mobility/</code>，使用 Python 3 与 NumPy：

<pre><code>python3 analyse_mobility.py
python3 transport_mobility_check.py
</code></pre>

分析完成后，读取生成的摘要可以确认它使用了哪些构型和模型：

```console
head -n 7 summary.json
```

```text
{
  "completed_cases": 11,
  "expected_cases": 11,
  "failures": [],
  "model": "scalar-PBE K-valley longitudinal acoustic deformation potential only",
  "temperature_K": 300.0,
  "mobility_cm2_Vs": 200.38557021265746,
```

这是保存摘要的开头；后面还有各项阈值、拟合和质量。11 个构型齐全、失败项为空，对应前面的应变区间、网格和真空对照。数值 200.38557021265746 的含义是当前标量 PBE、K 谷纵向声学形变势模型在 300 K 的估算。

[绘图脚本](/Atlas/examples/transport-mobility/plot_mobility.py)与同包的 <code>atlas_plot_style.py</code>读取结果表，以 NumPy、Matplotlib 重画已保存图件：

<details>
<summary>plot_mobility.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
summary=json.loads((R/'summary.json').read_text())
def rows(p):return list(csv.DictReader((R/p).open()))
cs=rows('cases.csv');by={x['case']:x for x in cs};mass=rows('mass-windows.csv');valley=rows('valley-bands.csv');pot=rows('potential-profiles.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
 name=f'transport-{name}'
 fig._atlas_panels_added=True
 fig.savefig(R/f'{name}.png',dpi=220)
 plt.close(fig)
base=['minus010','minus005','zero','plus005','plus010'];eps=np.array([float(by[n]['epsilon']) for n in base]);Et=np.array([float(by[n]['etot_eV']) for n in base]);Ec=np.array([float(by[n]['K_CBM_vac_eV']) for n in base]);Ezero=float(by['zero']['etot_eV']);Czero=float(by['zero']['K_CBM_vac_eV'])
fig,ax=plt.subplots(1,2,figsize=(10,4.5),layout='constrained');xx=np.linspace(-.01,.01,200)
ax[0].plot(eps*100,(Et-Ezero)*1000,'o',color='#009e73',label='12 × 12 × 1; relaxed ions')
ax[0].plot(xx*100,np.polyval(np.polyfit(eps,Et-Ezero,2),xx)*1000,'-',color='#009e73')
ax[1].plot(eps*100,(Ec-Czero)*1000,'o',color='#009e73',label='Vacuum-aligned K-valley minimum')
ax[1].plot(xx*100,np.polyval(np.polyfit(eps,Ec-Czero,1),xx)*1000,'-',color='#009e73')
for fam,color,marker in [('k16','#d55e00','s'),('vacuum28','#6c54a3','^')]:
 names=[f'{fam}-{n}' for n in ['minus005','zero','plus005']]
 ee=np.array([float(by[n]['epsilon']) for n in names]);en=np.array([float(by[n]['etot_eV']) for n in names]);cb=np.array([float(by[n]['K_CBM_vac_eV']) for n in names])
 ax[0].plot(ee*100,(en-en[1])*1000,marker+'--',color=color,label=fam)
 ax[1].plot(ee*100,(cb-cb[1])*1000,marker+'--',color=color,label=fam)
for a in ax:a.set_xlabel('Longitudinal strain εxx (%)');a.grid(alpha=.2);a.legend(frameon=False,fontsize=8)
ax[0].set_ylabel('E(ε) − E(0) (meV / 3-atom cell)');ax[1].set_ylabel('Aligned conduction edge shift (meV)')
ax[0].set_title('Strain energy')
ax[1].set_title('Vacuum-aligned K edge')
fig.suptitle('MoS₂ acoustic-DP inputs | fixed transverse lattice, relaxed internal coordinates')
save(fig,'deformation-fits')
fig,ax=plt.subplots(1,3,figsize=(13,4.2),layout='constrained')
for name,color in [('minus005','#009e73'),('zero','#3b3b3b'),('plus005','#d55e00')]:
 rr=[r for r in pot if r['case']==name];z=np.array([float(x['z_A']) for x in rr]);vv=np.array([float(x['potential_eV']) for x in rr]);offset=float(by[name]['vacuum_eV']);height=float(by[name]['height_A'])
 ax[0].plot(z,vv-offset,lw=.8,color=color,label=name)
 outer=(z<.25*height)|(z>.75*height)
 ax[1].plot(z[outer],(vv[outer]-offset)*1000,'.',ms=2,color=color,label=name)
ax[0].set_xlabel('z (Å)');ax[0].set_ylabel('Potential − vacuum (eV)');ax[0].legend(frameon=False,fontsize=8)
ax[1].set_xlabel('z (Å), vacuum regions');ax[1].set_ylabel('Vacuum plateau residual (meV)');ax[1].set_ylim(-.25,.10)
height0=float(by['zero']['height_A'])
for lo,hi in [(.10,.20),(.80,.90)]:ax[1].axvspan(lo*height0,hi*height0,color='#a9bdac',alpha=.18)
ax[1].set_title('Vacuum-plateau test', fontsize=9)
for key,label,color in [('Q1_minus_K_eV','Q direction 1','#009e73'),('Q2_minus_K_eV','Q direction 2','#d55e00'),('Q3_minus_K_eV','Q direction 3','#6c54a3'),('Gamma_minus_K_eV','Γ','#888')]:
 ax[2].plot(eps*100,[float(by[n][key]) for n in base],'o-',ms=3,label=label,color=color)
ax[2].axhline(0,color='#333',ls='--',lw=.6);ax[2].set_xlabel('εxx (%)');ax[2].set_ylabel('Valley energy − E(K) (eV)');ax[2].legend(frameon=False,fontsize=8)
ax[0].set_title('Plane-averaged potential')
ax[2].set_title('Sampled valley offsets')
fig.suptitle('Vacuum reference and sampled valley competition')
save(fig,'vacuum-and-valleys')
fig,ax=plt.subplots(1,3,figsize=(12,4),layout='constrained')
rr=[r for r in valley if r['case']=='zero' and r['kind']=='K-local'];center=min(rr,key=lambda r:abs(float(r['offsetx_invA']))+abs(float(r['offsety_invA'])));E0=float(center['conduction_eV'])
for a,axis,other in [(ax[0],'offsetx_invA','offsety_invA'),(ax[1],'offsety_invA','offsetx_invA')]:
 subset=sorted([r for r in rr if abs(float(r[other]))<1e-9],key=lambda r:float(r[axis]));k=np.array([float(r[axis]) for r in subset]);en=np.array([float(r['conduction_eV'])-E0 for r in subset]);a.plot(k,en*1000,'o',color='#009e73');kk=np.linspace(k.min(),k.max(),200);a.plot(kk,np.polyval(np.polyfit(k,en,2),kk)*1000,'-',color='#d55e00');a.set_xlabel('Δkx (Å⁻¹)' if axis.startswith('offsetx') else 'Δky (Å⁻¹)');a.set_ylabel('Conduction energy − E(K) (meV)');a.grid(alpha=.2)
ax[0].set_xticks([-.03,0,.03]);ax[1].set_xticks([-.03,0,.03])
mm=[r for r in mass if r['case']=='zero']
for key,label in [('mx_me','mx'),('my_me','my'),('md_me','DOS mass')]:ax[2].plot([float(r['window_invA']) for r in mm],[float(r[key]) for r in mm],'o-',label=label)
ax[2].set_xlabel('Quadratic-fit half width (Å⁻¹)');ax[2].set_ylabel('Effective mass / electron mass');ax[2].legend(frameon=False);ax[2].grid(alpha=.2)
ax[0].set_title('x-direction curvature')
ax[1].set_title('y-direction curvature')
ax[2].set_title('Mass versus fit window')
fig.suptitle('K-valley curvature at the optimized zero-strain structure')
save(fig,'effective-mass-windows')
print('Wrote transport-deformation-fits, transport-vacuum-and-valleys, transport-effective-mass-windows as PNG/SVG/PDF')
print('Model scope status:',summary.get('mobility_status','not reported'))
```

</details>

<pre><code>python3 plot_mobility.py
</code></pre>

## 从声学形变势走向完整散射

[Sohier、Calandra 与 Mauri，Phys. Rev. B 94, 085415 (2016)](https://doi.org/10.1103/PhysRevB.94.085415)给出二维 Fröhlich 相互作用的下一步计算链。第二节使用 QE DFPT 和二维库仑截断，图 1 定位小 q 的 LO 与 A₁ 光学支，图 2 比较体相和单层的模式矩阵元 |gν|（eV）随 q/|Γ−K| 的变化。二维截断后长波 Fröhlich 耦合趋于有限值。

第六节将矩阵元、声子频率和载流子能量按费米黄金律积分为逆弛豫时间；图 7 的室温 LO/A₁ 散射达到亚皮秒尺度，并随材料、能带和模式改变。建立这条链需要声子频率、本征矢及 g(q)，以补充本页从应变和带边提取的参数。[图件与原始数据映射](/Atlas/examples/transport-mobility/figure-source-map.md)列出本例曲线与这些文献图所回答的物理问题。

曲率窗口和应变边界决定这里提取的模型参数，分别可对照 [QE 有效质量](/Atlas/m/effective-mass/qe/)与 [QE 应变计算](/Atlas/m/strain-doping-scan/qe/)。若研究室温输运中的光学与谷间过程，需要进一步计算相应模式的耦合矩阵元和散射率。

[QE：pw.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE：电势后处理 pp.x](https://www.quantum-espresso.org/Doc/INPUT_PP.html) · [二维形变势模型与拟合方法](https://www.nature.com/articles/ncomms5475) · [MoS₂ 完整声子散射的原始研究](https://arxiv.org/abs/1201.5284)
