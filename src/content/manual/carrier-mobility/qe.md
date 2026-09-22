[QE：pw.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE：电势后处理 pp.x](https://www.quantum-espresso.org/Doc/INPUT_PP.html) · [二维形变势模型与拟合方法](https://www.nature.com/articles/ncomms5475) · [MoS₂ 完整声子散射的原始研究](https://arxiv.org/abs/1201.5284)

有效质量轻，并不能单独说明迁移率高。电子受到的散射同样影响输运。这一页从一个明确的简化模型出发，把实际应变能量、带边移动和带边曲率连成一条计算路线：先求纵向弹性系数 C₂D，再求真空对齐的导带形变势 E₁，最后检查 K 谷附近的有效质量，计算 300 K 的纵向声学形变势模型值。

体系是公开构造的三原子 2H-MoS₂ 单层，PBE、标量相对论、无 SOC。模型只保留低载流子浓度、近抛物 K 谷中的纵向声学形变势散射。光学声子、Fröhlich 相互作用、谷间散射、压电、杂质和衬底效应均不在这个公式里，不能把所得数字称为材料完整的室温迁移率。

[下载本例输入、完整输出、原始数值、分析和绘图脚本](/Atlas/examples/mos2-mobility-files.tar.gz)。包内还保留未完成的原尝试与随后采用的 bands-retry 分支；分析按 config.json 选择已经验收的结果。运行原生 QE 需先将脚本中的程序路径改为自己的位置。

## 从公开结构开始，先把母体优化好

结构由 [ASE 官方 mx2 构造器](https://wiki.fysik.dtu.dk/ase/_modules/ase/build/surface.html#mx2)生成：`MoS2`、`2H`、初始 a=3.18 Å、S–S 厚度 3.19 Å、上下各 10 Å 真空。初始 c=23.19 Å。这个初始几何不是优化结果，因此先在固定 c 的条件下优化面内晶格和内部坐标。

进入计算目录，准备两份来自 QE 官方库的赝势。下载链接分别为 [Mo PBE USPP](https://pseudopotentials.quantum-espresso.org/upf_files/Mo.pbe-spn-rrkjus_psl.1.0.0.UPF)与 [S PBE USPP](https://pseudopotentials.quantum-espresso.org/upf_files/S.pbe-n-rrkjus_psl.1.0.0.UPF)。文件头中的价电子数为 Mo 14、S 6，每个三原子晶胞共 26 个价电子。

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ sha256sum pseudo/*.UPF
0d7c57996e624698242e6428a34d5f13a1e52b4cddac2ce215be4dce429073dd  pseudo/Mo.pbe-spn-rrkjus_psl.1.0.0.UPF
90fb585e830674f2de7b4cbace28d5dd0c05ca1a919d1f92a59b54d6b95cbfc4  pseudo/S.pbe-n-rrkjus_psl.1.0.0.UPF
```

本次下载 Mo 文件时发生过一次网络超时，未完整的文件留在本地证据目录，续传后完整解析 UPF 并记录上面的哈希，再启动计算。只看扩展名是 `.UPF`，不能证明下载已经完整。

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

电子步骤完成和离子优化完成是两件事。这里不仅有末尾的 `JOB DONE.`，还明确写着 BFGS 达到能量、力和晶胞阈值。最后的几何读出 a=3.18272795064 Å，面积 A₀=8.77262707611 Å²，c 仍为 23.19 Å。后面的所有应变均从这一母体出发，不再使用最初的 3.18 Å。

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

本轮应变任务实际提交为 1984–1988。每个任务 8 个 MPI 进程，最多同时运行 4 个。排队中的任务等资源释放，不额外启动第二组 MPI 进程。查看运行状态时结合队列与输出：

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

零应变固定 SCF 的最初迭代曾出现两条 `1 eigenvalues not converged`，随后继续迭代，最终第 20 次电子步没有该告警并达到阈值。原告警没有删除，表格分别保留整个运行的告警数与最终迭代告警数。能带计算没有后续电子自洽来修复未收敛本征值，因此它的任意此类告警都会阻止本轮验收。

这些输出还保留了 `negative rho` 诊断。零应变最终 SCF 打印的两自旋分量为 `3.851E-04 0.000E+00`，十一配置的末次第一分量为约 3.845×10⁻⁴–4.815×10⁻⁴。这条信息不能因为电子迭代结束而删去。本轮没有增加截断能或 FFT 网格对照，因此后文的通过仅限于已列出的应变、k 网格、真空和曲率一致性条件，不代表赝势与电荷密度离散误差已经全部收敛。

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

![平面平均电势、真空平台与谷竞争](/Atlas/examples/mos2-mobility/vacuum-and-valleys.png)

左图显示完整势垒和中间的原子层；中图放大真空区域，阴影标出实际选用的两段平台窗口。右图显示三个 Q 方向以及 Γ 相对 K 谷底的距离，能量参考在相同应变内部比较时相消。

## 沿应变后的谷底拟合有效质量

K 谷附近取一个二维局部网格，笛卡尔步长为 0.01 Å⁻¹，x、y 各取 −0.03 到 +0.03 Å⁻¹ 的 7 个值，共 49 点。每个应变使用自己的倒格矢变换。用二维二次曲面拟合局部极小值的位置，而不是始终读取一个固定 k 点的能量。

此外还显式计算 Γ、M、K′，并沿三个 Γ–K 方向各取 15 点，总计 97 点。Q 区域在 Γ–K 比例 0.40–0.80 内比较；完整的 15 点数据保留，用图检查局部谷形。SCF 的规则网格导带最低值也单独与拟合 K 谷比较。这是对所列候选谷的实际检查，不能替代任意材料的全布里渊区搜索。

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

质量拟合使用 ±0.01、±0.02、±0.03 Å⁻¹ 三种窗口。写成 E(q)=E₀+v·q+½qᵀHq，极小值偏移是 −H⁻¹v，x 方向质量为 ħ²/Hxx，态密度质量取 ħ²/√det(H)。这些量使用同一基态 K 谷和同一套能量单位。

![K 谷的曲率与有效质量窗口检查](/Atlas/examples/mos2-mobility/effective-mass-windows.png)

```text
maxwell@maxwell:<工作目录>/mos2-mobility$ grep -e '^case,' -e '^zero,' mass-windows.csv
case,window_invA,mx_me,my_me,md_me,shift_x_invA,shift_y_invA,CBM_eV,fit_RMS_eV,fit_max_residual_eV,Hxy_eVA2
zero,0.01,0.45444614613586326,0.45471246278793787,0.45457928495910044,2.560123752940156e-05,-2.2897226725836738e-09,0.022172588993759075,4.543397079072445e-06,8.607535101394503e-06,1.4141009224159214e-06
zero,0.02,0.4560118247455952,0.4559465055835881,0.4559791639949692,6.659653068904663e-05,-1.226809186630084e-09,0.022177867166625027,3.164977028524813e-05,6.14986367195626e-05,-1.2565446092228515e-06
zero,0.03,0.45893936618406683,0.4589364866081122,0.45893792639383113,0.00012499550864600306,-6.094468692460792e-10,0.022201726043026494,9.177831588345768e-05,0.00019741314053896286,-2.0659789278941693e-07
```

零应变的中间窗口得到 mx=0.456012mₑ、my=0.455947mₑ，态密度质量 md=0.455979mₑ。单位 Å⁻¹ 不可漏掉：把晶体分数坐标直接当作笛卡尔 k，会使有效质量的量纲和数值都出错。

## 应变曲线、k 网格和真空厚度一起验收

从总能量拟合 E(ε)=E₀+a₁ε+a₂ε²，Cxx²ᴰ=2a₂/A₀。面积用母体的真实面内面积，不除以含真空的三维体积；1 eV/Å²=16.02176634 N/m。带边则拟合 Ecb(ε)−Vvac(ε)=b₀+E₁ε，E₁ 的单位是 eV，进入散射公式的是 E₁²。

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

较密网格的 SCF 只复用同晶胞的电荷密度，重新计算新网格的波函数。加厚真空后的 FFT 网格已经改变，因此该组从原子电荷起点开始，没有直接挪用不同高度的波函数。较密网格和零应变厚真空的复核用 `-nk 4` 将同一作业的 8 个 MPI 进程分为 4 个 k 点池。现场运行时间并未因此缩短，两个尚未开始的厚真空应变分支保留原脚本后改回单个 k 点池。总申请进程数保持不变，不能从 k 点池数量直接推断速度。

原先的 `vacuum28-zero`、`k16-minus005`、`k16-plus005` 三个作业分别为 1990、1991、1992。它们已经完成各自 SCF 和电势处理，但 15 分钟时限在 bands 阶段到达，因此原 OUT 没有完整结束，原尝试全部保留。随后分别在各自 `bands-retry/` 中从同一配置已收敛的电荷密度与 SCF XML 重新求解这 97 个点，作业 1997、1998、1999 采用单个 k 点池、8 个 MPI 进程和 30 分钟时限，并正常完成。物理配置、带数、截断和本征值阈值没有改变。

分析脚本读取每个 `config.json` 的 `bands_subdir`，明确选用续算结果，未把原来截断的输出算成完成。其余配置直接使用本目录的 bands。以下是最后一个续算的完整脚本，重新执行它需要同一配置的已收敛 SCF 保存目录：

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

最终不仅核对 `JOB DONE.`，还逐配置检查 SCF 的最终迭代、本征值告警、BFGS、原子力、SCF 与 bands 的几何一致性，以及 XML 中的实际 k 点坐标与输入顺序。前期 SCF 的本征值告警保留在原 OUT；这些分支最终迭代均不再有该告警，最终采用的 bands 中没有未收敛本征值。

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

![弹性与真空对齐导带的应变拟合](/Atlas/examples/mos2-mobility/deformation-fits.png)

| 拟合组 | Cxx²ᴰ / N·m⁻¹ | E₁ / eV | E₁ 拟合标准误差 / eV |
| --- | --- | --- | --- |
| five_strains | 132.110909 | -8.217569 | 0.014778 |
| three_strains | 130.271104 | -8.217723 | 0.012272 |
| k16 | 132.908806 | -8.217444 | 0.014064 |
| vacuum28 | 132.101395 | -8.218970 | 0.014673 |

表中的 E₁ 标准误差只来自线性回归残差，不包含截断、赝势、SOC 或散射模型带来的系统误差。

阈值在分析之前写入 `quality-gates.json`：应变窗口与 k 网格对 C₂D、E₁ 的相对影响不超过 5%，真空厚度的影响不超过 2%，质量窗口变化不超过 5%。形变势绝对值小于 0.1 eV、相对拟合误差超过 10%、曲率非正、谷底离开局部网格、候选最低谷改变或金属化，均阻止输出迁移率。这些是本轮模型一致性检查，不把两档参数比较称为所有数值参数已经收敛。

这些检查在本轮全部通过。使用五应变拟合的 C₂D=132.110909 N/m、E₁=-8.217569 eV，以及零应变中间窗口的 mx、md，得到 300 K 声学形变势模型 μx=200.386 cm²/(V·s)。

五点与中央三点相比，C₂D 改变 1.4123%，E₁ 改变 0.00188%；16×16×1 的中央三点使 C₂D 改变 2.0248%，E₁ 改变 0.00340%。增加 5 Å 真空后，两项变化分别为 1.4050% 与 0.01517%。这些实际差异落在上面预先设置的窗口内；没有进一步把当前截断、无 SOC 协议或两档网格称为所有材料参数已经收敛。

公式为：

<p>μx = e ħ³ Cxx²ᴰ / (kB T mx md E₁²)。</p>

计算时 C₂D 用 N/m，质量换成 kg，E₁ 从 eV 换成 J，先得到 m²/(V·s)，再乘 10⁴ 换成 cm²/(V·s)。它使用经典声学声子、低载流子浓度和近抛物带近似，没有进行完整电子声子散射积分或玻尔兹曼输运求解。

Kaasbjerg 等对单层 MoS₂ 的第一性原理研究表明，室温光学声子与 Fröhlich 散射很重要。只保留声学形变势的数值不应与完整室温迁移率直接比较，更不能称为实验预测；同一篇论文与另一个低温声学模型的温区也不能混用。[原始研究](https://arxiv.org/abs/1201.5284)

## 在本机重画三组图

保存 `cases.csv`、`mass-windows.csv`、`valley-bands.csv`、`potential-profiles.csv`、`summary.json` 与 `plot_mobility.py`，在同一目录执行：

```bash
python3 plot_mobility.py
```

脚本只依赖 NumPy 和 Matplotlib，生成三组 PNG/SVG：`deformation-fits`、`vacuum-and-valleys`、`effective-mass-windows`。原始势能和导带数据没有人为平移成同一条线；绘图中减去各组零应变值仅用于显示差分，真空对齐及绝对值保存在 CSV。若要重新核验分析，则同时保存各配置的输入、OUT、SCF/bands XML 与 `avg.dat`，运行 `python3 analyse_mobility.py`。

<details>
<summary>完整绘图脚本 plot_mobility.py</summary>

```python

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
 for ext in ['png','svg']:fig.savefig(R/f'{name}.{ext}',dpi=220)
 plt.close(fig)
base=['minus010','minus005','zero','plus005','plus010'];eps=np.array([float(by[n]['epsilon']) for n in base]);Et=np.array([float(by[n]['etot_eV']) for n in base]);Ec=np.array([float(by[n]['K_CBM_vac_eV']) for n in base]);Ezero=float(by['zero']['etot_eV']);Czero=float(by['zero']['K_CBM_vac_eV'])
fig,ax=plt.subplots(1,2,figsize=(10,4.5),layout='constrained');xx=np.linspace(-.01,.01,200)
ax[0].plot(eps*100,(Et-Ezero)*1000,'o',color='#246a73',label='12 × 12 × 1; relaxed ions')
ax[0].plot(xx*100,np.polyval(np.polyfit(eps,Et-Ezero,2),xx)*1000,'-',color='#246a73')
ax[1].plot(eps*100,(Ec-Czero)*1000,'o',color='#246a73',label='Vacuum-aligned K-valley minimum')
ax[1].plot(xx*100,np.polyval(np.polyfit(eps,Ec-Czero,1),xx)*1000,'-',color='#246a73')
for fam,color,marker in [('k16','#ad5d41','s'),('vacuum28','#6c54a3','^')]:
 names=[f'{fam}-{n}' for n in ['minus005','zero','plus005']]
 ee=np.array([float(by[n]['epsilon']) for n in names]);en=np.array([float(by[n]['etot_eV']) for n in names]);cb=np.array([float(by[n]['K_CBM_vac_eV']) for n in names])
 ax[0].plot(ee*100,(en-en[1])*1000,marker+'--',color=color,label=fam)
 ax[1].plot(ee*100,(cb-cb[1])*1000,marker+'--',color=color,label=fam)
for a in ax:a.set_xlabel('Longitudinal strain εxx (%)');a.grid(alpha=.2);a.legend(frameon=False,fontsize=8)
ax[0].set_ylabel('E(ε) − E(0) (meV / 3-atom cell)');ax[1].set_ylabel('Aligned conduction edge shift (meV)')
fig.suptitle('MoS₂ acoustic-DP inputs | fixed transverse lattice, relaxed internal coordinates')
save(fig,'deformation-fits')
fig,ax=plt.subplots(1,3,figsize=(13,4.2),layout='constrained')
for name,color in [('minus005','#246a73'),('zero','#3b3b3b'),('plus005','#ad5d41')]:
 rr=[r for r in pot if r['case']==name];z=np.array([float(x['z_A']) for x in rr]);vv=np.array([float(x['potential_eV']) for x in rr]);offset=float(by[name]['vacuum_eV']);height=float(by[name]['height_A'])
 ax[0].plot(z,vv-offset,lw=.8,color=color,label=name)
 outer=(z<.25*height)|(z>.75*height)
 ax[1].plot(z[outer],(vv[outer]-offset)*1000,'.',ms=2,color=color,label=name)
ax[0].set_xlabel('z (Å)');ax[0].set_ylabel('Planar electrostatic potential − vacuum (eV)');ax[0].legend(frameon=False,fontsize=8)
ax[1].set_xlabel('z (Å), vacuum regions');ax[1].set_ylabel('Vacuum plateau residual (meV)');ax[1].set_ylim(-.25,.10)
height0=float(by['zero']['height_A'])
for lo,hi in [(.10,.20),(.80,.90)]:ax[1].axvspan(lo*height0,hi*height0,color='#a9bdac',alpha=.18)
ax[1].text(.5,.97,'Shaded: vacuum reference windows',transform=ax[1].transAxes,ha='center',va='top',fontsize=8)
for key,label,color in [('Q1_minus_K_eV','Q direction 1','#246a73'),('Q2_minus_K_eV','Q direction 2','#ad5d41'),('Q3_minus_K_eV','Q direction 3','#6c54a3'),('Gamma_minus_K_eV','Γ','#888')]:
 ax[2].plot(eps*100,[float(by[n][key]) for n in base],'o-',ms=3,label=label,color=color)
ax[2].axhline(0,color='#333',ls='--',lw=.6);ax[2].set_xlabel('εxx (%)');ax[2].set_ylabel('Competing conduction energy − K minimum (eV)');ax[2].legend(frameon=False,fontsize=8)
fig.suptitle('Vacuum reference and sampled valley competition')
save(fig,'vacuum-and-valleys')
fig,ax=plt.subplots(1,3,figsize=(12,4),layout='constrained')
rr=[r for r in valley if r['case']=='zero' and r['kind']=='K-local'];center=min(rr,key=lambda r:abs(float(r['offsetx_invA']))+abs(float(r['offsety_invA'])));E0=float(center['conduction_eV'])
for a,axis,other in [(ax[0],'offsetx_invA','offsety_invA'),(ax[1],'offsety_invA','offsetx_invA')]:
 subset=sorted([r for r in rr if abs(float(r[other]))<1e-9],key=lambda r:float(r[axis]));k=np.array([float(r[axis]) for r in subset]);en=np.array([float(r['conduction_eV'])-E0 for r in subset]);a.plot(k,en*1000,'o',color='#246a73');kk=np.linspace(k.min(),k.max(),200);a.plot(kk,np.polyval(np.polyfit(k,en,2),kk)*1000,'-',color='#ad5d41');a.set_xlabel('Δkx (Å⁻¹)' if axis.startswith('offsetx') else 'Δky (Å⁻¹)');a.set_ylabel('Conduction energy − E(K) (meV)');a.grid(alpha=.2)
mm=[r for r in mass if r['case']=='zero']
for key,label in [('mx_me','mx'),('my_me','my'),('md_me','DOS mass')]:ax[2].plot([float(r['window_invA']) for r in mm],[float(r[key]) for r in mm],'o-',label=label)
ax[2].set_xlabel('Quadratic-fit half width (Å⁻¹)');ax[2].set_ylabel('Effective mass / electron mass');ax[2].legend(frameon=False);ax[2].grid(alpha=.2)
fig.suptitle('K-valley curvature at the optimized zero-strain structure')
save(fig,'effective-mass-windows')
print('Wrote deformation-fits, vacuum-and-valleys, effective-mass-windows PNG/SVG')
print('Mobility publication status:',summary.get('mobility_status','alldeclaredmodelchecksmet'))

```

</details>

下一步：用[有效质量](/Atlas/m/effective-mass/qe/)核对带边曲率的单位和窗口；用[应变计算](/Atlas/m/strain-doping-scan/qe/)查看固定结构与应变边界；如要进入材料定量输运，需要建立包含实际电子声子矩阵元和相关散射通道的计算链。

```text
公开单层结构 + 同源 PBE 赝势
          ↓
母体面内优化（c 固定）
          ↓
五个 εxx（横向固定，内部坐标分别松弛）
          ├─ 最终 SCF 总能量 → Cxx²ᴰ
          ├─ pp.x → average.x → 各自 Vvac
          └─ 同谷局部网格 + Q/Γ/M → 真空对齐 E₁ 与曲率
                                      ↓
中央三点：更密 k 网格 + 更厚真空复核
                                      ↓
通过模型与数值检查 → 300 K 声学形变势模型
检查不通过 → 保留真实差异，迁移率不输出
```
