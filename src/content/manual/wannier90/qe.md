[Wannier90 官方 Si 教程](https://wannier90.readthedocs.io/en/latest/tutorials/tutorial_11/) · [Wannier90 参数说明](https://wannier90.readthedocs.io/en/latest/user_guide/wannier90/parameters/) · [QE 的 pw2wannier90 接口](https://www.quantum-espresso.org/Doc/INPUT_pw2wannier90.html) · [pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

一条很密的能带曲线可以逐点运行 DFT，也可以先在均匀 k 网格上构造 Wannier 表象，再做插值。插值很快，但“曲线很平滑”和“与直接 DFT 相符”是两回事。这一页先把接口完整走通，再另算几个路径点，把差异画在图下面。

例子采用 Wannier90 3.1.0 随附官方 example11 的两原子金刚石 Si 结构，晶格常数为 10.2 bohr。结构在本例中保持固定，没有重新优化。赝势从 QE 公开库重新下载 `Si.pbe-n-van.UPF`，是非相对论 PBE 超软赝势；本次使用 QE 7.5、40/320 Ry 截断能。计算目录中的 SCF、NSCF、重叠矩阵与 Wannier 结果均在这次实际运行中生成，没有使用官方示例附带的预计算矩阵。

这里先只做四条价带。两个 Si 原子一共提供八个价电子，在不自旋极化的计算中填满四条能带，因此选择 `nbnd=4`、`num_bands=4`、`num_wann=4`。本例没有导带，不从这四条价带推断带隙，也没有使用纠缠能带的解缠窗口。SCF 和 NSCF 的一般操作分别见 [SCF](/Atlas/m/scf/qe/) 与 [NSCF](/Atlas/m/nscf/qe/)，下面只展开与这次接口有关的文件。

输入、完整输出、接口矩阵、数据表和绘图脚本可[一起下载](/Atlas/examples/si-wannier-lesson-files.tar.gz)。包内不含 QE 的电荷密度与波函数保存目录；重新计算应从本页自己的 SCF 开始。读取结果、核对接口矩阵和重新作图可以使用包内文件。

## 先把 SCF 和均匀 NSCF 网格接好

SCF 输入由官方结构复制后用 `vi` 改为本次路径和数值设置。输出前缀使用 `si`，Wannier 文件前缀稍后使用 `silicon`；它们可以不同，但接口必须明确各自读哪个名字。

```console
maxwell@maxwell:~/si-wannier$ cp evidence/official-silicon.scf k4/si.scf.in
maxwell@maxwell:~/si-wannier$ vi k4/si.scf.in

```

```console
maxwell@maxwell:~/si-wannier/k4$ cat si.scf.in
&CONTROL
 calculation = 'scf'
 prefix = 'si'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 2
 celldm(1) = 10.2
 nat = 2
 ntyp = 1
 ecutwfc = 40
 ecutrho = 320
 nbnd = 4
 occupations = 'fixed'
/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Si 28.0855 Si.pbe-n-van.UPF
ATOMIC_POSITIONS crystal
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
K_POINTS automatic
10 10 10 0 0 0
```

接着看 NSCF 输入。这里列出完整 4³ 网格的 64 个 k 点，并显式设置 `nosym` 与 `noinv`，使这些点按所列的完整网格参与计算。不能用一张高对称路径代替这张均匀网格，也不能把只含不可约点的列表交给下文这份 Wannier 输入。

```console
maxwell@maxwell:~/si-wannier/k4$ cat si.nscf.in
&CONTROL
 calculation = 'nscf'
 prefix = 'si'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 2
 celldm(1) = 10.2
 nat = 2
 ntyp = 1
 ecutwfc = 40
 ecutrho = 320
 nbnd = 4
 occupations = 'fixed'
 nosym = .true.
 noinv = .true.
/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Si 28.0855 Si.pbe-n-van.UPF
ATOMIC_POSITIONS crystal
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
K_POINTS crystal
64
0.000000000000 0.000000000000 0.000000000000 0.015625000000
0.000000000000 0.000000000000 0.250000000000 0.015625000000
0.000000000000 0.000000000000 0.500000000000 0.015625000000
0.000000000000 0.000000000000 0.750000000000 0.015625000000
0.000000000000 0.250000000000 0.000000000000 0.015625000000
0.000000000000 0.250000000000 0.250000000000 0.015625000000
0.000000000000 0.250000000000 0.500000000000 0.015625000000
0.000000000000 0.250000000000 0.750000000000 0.015625000000
0.000000000000 0.500000000000 0.000000000000 0.015625000000
0.000000000000 0.500000000000 0.250000000000 0.015625000000
0.000000000000 0.500000000000 0.500000000000 0.015625000000
0.000000000000 0.500000000000 0.750000000000 0.015625000000
0.000000000000 0.750000000000 0.000000000000 0.015625000000
0.000000000000 0.750000000000 0.250000000000 0.015625000000
0.000000000000 0.750000000000 0.500000000000 0.015625000000
0.000000000000 0.750000000000 0.750000000000 0.015625000000
0.250000000000 0.000000000000 0.000000000000 0.015625000000
0.250000000000 0.000000000000 0.250000000000 0.015625000000
0.250000000000 0.000000000000 0.500000000000 0.015625000000
0.250000000000 0.000000000000 0.750000000000 0.015625000000
0.250000000000 0.250000000000 0.000000000000 0.015625000000
0.250000000000 0.250000000000 0.250000000000 0.015625000000
0.250000000000 0.250000000000 0.500000000000 0.015625000000
0.250000000000 0.250000000000 0.750000000000 0.015625000000
0.250000000000 0.500000000000 0.000000000000 0.015625000000
0.250000000000 0.500000000000 0.250000000000 0.015625000000
0.250000000000 0.500000000000 0.500000000000 0.015625000000
0.250000000000 0.500000000000 0.750000000000 0.015625000000
0.250000000000 0.750000000000 0.000000000000 0.015625000000
0.250000000000 0.750000000000 0.250000000000 0.015625000000
0.250000000000 0.750000000000 0.500000000000 0.015625000000
0.250000000000 0.750000000000 0.750000000000 0.015625000000
0.500000000000 0.000000000000 0.000000000000 0.015625000000
0.500000000000 0.000000000000 0.250000000000 0.015625000000
0.500000000000 0.000000000000 0.500000000000 0.015625000000
0.500000000000 0.000000000000 0.750000000000 0.015625000000
0.500000000000 0.250000000000 0.000000000000 0.015625000000
0.500000000000 0.250000000000 0.250000000000 0.015625000000
0.500000000000 0.250000000000 0.500000000000 0.015625000000
0.500000000000 0.250000000000 0.750000000000 0.015625000000
0.500000000000 0.500000000000 0.000000000000 0.015625000000
0.500000000000 0.500000000000 0.250000000000 0.015625000000
0.500000000000 0.500000000000 0.500000000000 0.015625000000
0.500000000000 0.500000000000 0.750000000000 0.015625000000
0.500000000000 0.750000000000 0.000000000000 0.015625000000
0.500000000000 0.750000000000 0.250000000000 0.015625000000
0.500000000000 0.750000000000 0.500000000000 0.015625000000
0.500000000000 0.750000000000 0.750000000000 0.015625000000
0.750000000000 0.000000000000 0.000000000000 0.015625000000
0.750000000000 0.000000000000 0.250000000000 0.015625000000
0.750000000000 0.000000000000 0.500000000000 0.015625000000
0.750000000000 0.000000000000 0.750000000000 0.015625000000
0.750000000000 0.250000000000 0.000000000000 0.015625000000
0.750000000000 0.250000000000 0.250000000000 0.015625000000
0.750000000000 0.250000000000 0.500000000000 0.015625000000
0.750000000000 0.250000000000 0.750000000000 0.015625000000
0.750000000000 0.500000000000 0.000000000000 0.015625000000
0.750000000000 0.500000000000 0.250000000000 0.015625000000
0.750000000000 0.500000000000 0.500000000000 0.015625000000
0.750000000000 0.500000000000 0.750000000000 0.015625000000
0.750000000000 0.750000000000 0.000000000000 0.015625000000
0.750000000000 0.750000000000 0.250000000000 0.015625000000
0.750000000000 0.750000000000 0.500000000000 0.015625000000
0.750000000000 0.750000000000 0.750000000000 0.015625000000
```

4³ 与后面的 `mp_grid=4 4 4`、`begin kpoints` 必须相互对应。本次两个文件的列表由同一个准备脚本生成，顺序也一致；这件事不只检查点数，还检查每一个坐标及其排序。完整准备代码保存在 [prepare_si_wannier.py](/Atlas/examples/si-wannier/prepare_si_wannier.py)，6³ 对照则有 216 个 k 点。

## 用四个键中心投影开始

```console
maxwell@maxwell:~/si-wannier/k4$ cat silicon.win
num_bands = 4
num_wann = 4
num_iter = 200
conv_tol = 1.0d-10
conv_window = 5
iprint = 2
length_unit = bohr
write_hr = true
write_xyz = true
bands_plot = true
bands_num_points = 80
begin projections
f=-0.125,-0.125,0.375:s
f=0.375,-0.125,-0.125:s
f=-0.125,0.375,-0.125:s
f=-0.125,-0.125,-0.125:s
end projections
begin unit_cell_cart
bohr
-5.10 0.00 5.10
0.00 5.10 5.10
-5.10 5.10 0.00
end unit_cell_cart
begin atoms_frac
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
end atoms_frac
begin kpoint_path
G 0.00 0.00 0.00 X 0.50 0.00 0.50
X 0.50 0.00 0.50 W 0.50 0.25 0.75
W 0.50 0.25 0.75 L 0.50 0.50 0.50
L 0.50 0.50 0.50 G 0.00 0.00 0.00
end kpoint_path
mp_grid = 4 4 4
begin kpoints
0.000000000000 0.000000000000 0.000000000000
0.000000000000 0.000000000000 0.250000000000
0.000000000000 0.000000000000 0.500000000000
0.000000000000 0.000000000000 0.750000000000
0.000000000000 0.250000000000 0.000000000000
0.000000000000 0.250000000000 0.250000000000
0.000000000000 0.250000000000 0.500000000000
0.000000000000 0.250000000000 0.750000000000
0.000000000000 0.500000000000 0.000000000000
0.000000000000 0.500000000000 0.250000000000
0.000000000000 0.500000000000 0.500000000000
0.000000000000 0.500000000000 0.750000000000
0.000000000000 0.750000000000 0.000000000000
0.000000000000 0.750000000000 0.250000000000
0.000000000000 0.750000000000 0.500000000000
0.000000000000 0.750000000000 0.750000000000
0.250000000000 0.000000000000 0.000000000000
0.250000000000 0.000000000000 0.250000000000
0.250000000000 0.000000000000 0.500000000000
0.250000000000 0.000000000000 0.750000000000
0.250000000000 0.250000000000 0.000000000000
0.250000000000 0.250000000000 0.250000000000
0.250000000000 0.250000000000 0.500000000000
0.250000000000 0.250000000000 0.750000000000
0.250000000000 0.500000000000 0.000000000000
0.250000000000 0.500000000000 0.250000000000
0.250000000000 0.500000000000 0.500000000000
0.250000000000 0.500000000000 0.750000000000
0.250000000000 0.750000000000 0.000000000000
0.250000000000 0.750000000000 0.250000000000
0.250000000000 0.750000000000 0.500000000000
0.250000000000 0.750000000000 0.750000000000
0.500000000000 0.000000000000 0.000000000000
0.500000000000 0.000000000000 0.250000000000
0.500000000000 0.000000000000 0.500000000000
0.500000000000 0.000000000000 0.750000000000
0.500000000000 0.250000000000 0.000000000000
0.500000000000 0.250000000000 0.250000000000
0.500000000000 0.250000000000 0.500000000000
0.500000000000 0.250000000000 0.750000000000
0.500000000000 0.500000000000 0.000000000000
0.500000000000 0.500000000000 0.250000000000
0.500000000000 0.500000000000 0.500000000000
0.500000000000 0.500000000000 0.750000000000
0.500000000000 0.750000000000 0.000000000000
0.500000000000 0.750000000000 0.250000000000
0.500000000000 0.750000000000 0.500000000000
0.500000000000 0.750000000000 0.750000000000
0.750000000000 0.000000000000 0.000000000000
0.750000000000 0.000000000000 0.250000000000
0.750000000000 0.000000000000 0.500000000000
0.750000000000 0.000000000000 0.750000000000
0.750000000000 0.250000000000 0.000000000000
0.750000000000 0.250000000000 0.250000000000
0.750000000000 0.250000000000 0.500000000000
0.750000000000 0.250000000000 0.750000000000
0.750000000000 0.500000000000 0.000000000000
0.750000000000 0.500000000000 0.250000000000
0.750000000000 0.500000000000 0.500000000000
0.750000000000 0.500000000000 0.750000000000
0.750000000000 0.750000000000 0.000000000000
0.750000000000 0.750000000000 0.250000000000
0.750000000000 0.750000000000 0.500000000000
0.750000000000 0.750000000000 0.750000000000
end kpoints
```

四个 `f=...:s` 指定四个 Si–Si 键中心的 s 型初始投影。它们只是局域化迭代的起点，最后的中心与展布要从输出读。`num_iter=200` 是上限；`conv_tol=1e-10` 与连续五次迭代的窗口规定本次展布收敛条件。

这里的三个“4”不能只看成相同的数字：QE 的 `nbnd` 决定实际求解多少条 Bloch 带，Wannier90 的 `num_bands` 对应接口提供的带空间，`num_wann` 决定最后保留多少个 Wannier 函数。本例正好是隔离的四条占据带，三个值才相等。若以后加入导带，增加 `nbnd` 不会自动决定合适的投影与解缠窗口，应先说明准备保留哪个能区。

`length_unit=bohr` 与 `unit_cell_cart` 的单位都写得明确。因此本次 `.wout` 中中心坐标以 bohr、spread 以 bohr² 输出。`kpoint_path` 只用于最终插值图，路径是 Γ–X–W–L–Γ；它与前面的均匀网格用途不同。

`length_unit` 控制 `.wout` 中长度的显示单位；它不把所有参数的单位一起改写。按 [Wannier90 参数说明](https://wannier90.readthedocs.io/en/latest/user_guide/wannier90/parameters/#realkinddp-conv_tol)，`conv_tol` 使用 Å²，不能因为这里的 spread 显示为 bohr²，就把阈值也解释成 bohr²。这个阈值检查同一网格内展布的迭代变化，后文直接 DFT 对照检查的是插值能量误差，二者没有相互替代关系。

接口的输入很短，但名字和目录必须对得上：

```console
maxwell@maxwell:~/si-wannier/k4$ cat silicon.pw2wan
&INPUTPP
 outdir='./tmp'
 prefix='si'
 seedname='silicon'
 write_amn=.true.
 write_mmn=.true.
 write_unk=.false.
/
```

`prefix='si'` 对应 QE 的 `tmp/si.save`，`seedname='silicon'` 则对应 `silicon.win`、`silicon.nnkp` 等 Wannier 文件。`write_unk=.false.` 说明本次不导出用于轨道等值面绘图的实空间 Bloch 波函数；仍可以得到重叠矩阵、投影矩阵和插值能带，不能据此声称已经有完整的 Wannier 轨道等值面数据。

## 一份脚本里五个程序步骤的顺序

下载包保留输入、输出和后处理数据，没有包含体积较大的 SCF/NSCF 保存目录。重新运行前，先在包根目录建立两个验证用的临时目录：

```bash
mkdir -p k4/validation/tmp k6/validation/tmp
```

这样脚本中的 `cp -r tmp/si.save validation/tmp/` 会得到 `validation/tmp/si.save/`。直接 DFT 路径计算需要这个 SCF 父目录；不要把 `si.save` 的内容误放到 `validation/tmp` 这一层。

下面是实际提交的脚本。SCF 结束后，先复制 `si.save` 到独立的验证目录；随后 NSCF 在自己的 `tmp` 中继续写入均匀网格的波函数。这样后面直接 DFT 路径点的计算不会覆盖供接口读取的 NSCF 文件。

```console
maxwell@maxwell:~/si-wannier/k4$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-si-w4
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
mpirun -np 8 <qe_bin>/pw.x -in si.scf.in > si.scf.out 2> si.scf.err
cp tmp/si.save/data-file-schema.xml scf.data-file-schema.xml
cp -r tmp/si.save validation/tmp/
mpirun -np 8 <qe_bin>/pw.x -in si.nscf.in > si.nscf.out 2> si.nscf.err
cp tmp/si.save/data-file-schema.xml nscf.data-file-schema.xml
<qe_bin>/wannier90.x -pp silicon > wannier-pp.out 2> wannier-pp.err
mpirun -np 8 <qe_bin>/pw2wannier90.x -in silicon.pw2wan > pw2wan.out 2> pw2wan.err
<qe_bin>/wannier90.x silicon > wannier.out 2> wannier.err
```

```console
maxwell@maxwell:~/si-wannier/k4$ sbatch run.slurm
Submitted batch job 1978
```

同样的固定结构、赝势和 SCF 设置在 `k6` 目录重新运行了一条 6³ 路线，作业号为 1979；没有把 4³ 的 `.mmn` 改名后交给 6³。运行时可查看队列、SCF/NSCF 输出与接口日志：

```bash
squeue -j 1978
tail -f si.nscf.out
tail -f pw2wan.out
```

这里 `wannier90.x -pp silicon` 先生成相邻 k 点及投影需求，写到 `silicon.nnkp`。之后 `pw2wannier90.x` 才读取实际的 QE 波函数，产生 `.mmn`、`.amn`、`.eig`，最后 `wannier90.x silicon` 进行局域化与能带插值。前后次序不能互换。

```console
maxwell@maxwell:~/si-wannier/k4$ tail -10 pw2wan.out
 
     PW2WANNIER   :      0.70s CPU      0.86s WALL

 
   This run was terminated on:  22:45:15  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

这个结束框说明接口完成；前面的 SCF 和 NSCF 也要分别读末尾、检查电子收敛和本征值警告。本次两条路线均正常完成，检查未发现未收敛本征值。

## 这些新文件各自存了什么

```console
maxwell@maxwell:~/si-wannier/k4$ head -5 silicon.mmn
 Created on 22Sep2026 at 22:45:14                            
           4          64           8
         1         2         0         0         0
   -0.492079364532   -0.864070322919
   -0.024177177982    0.008600504483
```

`.mmn` 的第二行 `4 64 8` 对应四条能带、64 个 k 点及每点八个近邻方向。后面一个块先标记 k 点、邻点与倒格矢位移，再写复数重叠矩阵。它记录相邻 Bloch 态如何连接，不是能量表。

```console
maxwell@maxwell:~/si-wannier/k4$ head -5 silicon.amn
 Created on 22Sep2026 at 22:45:14                            
           4          64           4
         1         1         1    0.893516554225   -0.081197481344
         2         1         1   -0.037961261089    0.444139156106
         3         1         1    0.008289841576    0.136503227241
```

`.amn` 的 `4 64 4` 表示四条能带、64 个 k 点与四个初始投影，数据行最后两列是投影的实部与虚部。它描述实际 Bloch 态与选定局域轨道的重叠。

```console
maxwell@maxwell:~/si-wannier/k4$ head -5 silicon.eig
         1         1   -5.699221902813
         2         1    6.386039243324
         3         1    6.386039243240
         4         1    6.386039243468
         1         2   -4.886581912211
```

`.eig` 则是能带编号、k 点编号、能量（eV）。第一点 Γ 的三个最高价态简并在约 6.386 eV；这个数使用 DFT 当前的能量零点，还没有减去价带顶。图里的零点会在两种网格和直接 DFT 之间统一处理。

## 从 .wout 里读中心和展布

Wannier 的详细优化日志在 `silicon.wout`，不是根据标准输出文件是否很长来判断运行情况。这次 4³ 的末尾连续输出为：

```text
             <<<     Delta < 1.000E-10  over  5 iterations     >>>
             <<< Wannierisation convergence criteria satisfied >>>

 Final State
  WF centre and spread    1  ( -1.275001,  1.275000, -1.275000 )     5.69160675
  WF centre and spread    2  ( -1.274999, -1.275000,  1.274999 )     5.69160661
  WF centre and spread    3  (  1.274999,  1.275000,  1.275000 )     5.69160759
  WF centre and spread    4  (  1.275000, -1.275000, -1.275000 )     5.69160649
  Sum of centres and spreads ( -0.000001,  0.000000, -0.000002 )    22.76642744
 
        Spreads (Bohr^2)       Omega I      =    20.758666132
        ================       Omega D      =     0.000000000
                               Omega OD     =     2.007761309
   Final Spread (Bohr^2)       Omega Total  =    22.766427441
 ------------------------------------------------------------------------------

 Wannier centres written to file silicon_centres.xyz
```

四个中心位于 Si–Si 键中间。每个轨道的 spread 约 5.6916 bohr²，四个之和是 22.766427441 bohr²。Omega I 为给定离散子空间的规范不变部分，Omega D 和 Omega OD 属于局域化迭代要减小的部分；本次已经满足输入指定的连续迭代条件。

![Wannier展布随迭代的变化](/Atlas/examples/si-wannier/figures/wannier-spread.png)

6³ 的最终总展布为 26.905582236 bohr²，比 4³ 更大。不能据此说较密网格得到的轨道更差：这两个离散 k 网格对 spread 的表示并不相同，Omega I 也改变了。网格内部的迭代收敛，与网格之间的插值精度应分开检查。

`silicon_centres.xyz` 还给出可供查看的原子及轨道中心，XYZ 中坐标为 Å，与上面 `.wout` 的 bohr 要分清。

```console
maxwell@maxwell:~/si-wannier/k4$ cat silicon_centres.xyz
     6
 Wannier centres, written by Wannier90 on22Sep2026 at 22:45:15 
X         -0.67470121       0.67470111      -0.67470109
X         -0.67470067      -0.67470110       0.67470045
X          0.67470057       0.67470088       0.67470078
X          0.67470096      -0.67470072      -0.67470110
Si         1.34940188       1.34940188       1.34940188
Si         0.00000000       0.00000000       0.00000000
```

## 在网格外另算 DFT，再谈插值好不好

仅在训练网格上比较，可能掩盖网格之间的插值误差。因此本次沿同一条 Γ–X–W–L–Γ 路径选择了 13 个位置做直接 DFT；首尾 Γ 重复，对应 12 个不同 k 点，其中包含两套均匀网格之外的点。验证输入如下，完整 SCF 电荷密度来自先前独立保存的副本。

```console
maxwell@maxwell:~/si-wannier/k4/validation$ cat si.bands.in
&CONTROL
 calculation = 'bands'
 prefix = 'si'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 2
 celldm(1) = 10.2
 nosym = .true.
 noinv = .true.
 nat = 2
 ntyp = 1
 ecutwfc = 40
 ecutrho = 320
 nbnd = 4
 occupations = 'fixed'
/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Si 28.0855 Si.pbe-n-van.UPF
ATOMIC_POSITIONS crystal
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
K_POINTS crystal
13
0.00000000000000 0.00000000000000 0.00000000000000 1.0
0.08125000000000 0.00000000000000 0.08125000000000 1.0
0.19375000000000 0.00000000000000 0.19375000000000 1.0
0.35625000000000 0.00000000000000 0.35625000000000 1.0
0.50000000000000 0.00000000000000 0.50000000000000 1.0
0.50000000000000 0.09375000000000 0.59375000000000 1.0
0.50000000000000 0.25000000000000 0.75000000000000 1.0
0.50000000000000 0.33333333333333 0.66666666666667 1.0
0.50000000000000 0.42543859649123 0.57456140350877 1.0
0.50000000000000 0.50000000000000 0.50000000000000 1.0
0.36231884057971 0.36231884057971 0.36231884057971 1.0
0.19565217391304 0.19565217391304 0.19565217391304 1.0
0.00000000000000 0.00000000000000 0.00000000000000 1.0
```

这一步实际提交了独立作业 1980。它只在这些 k 点求本征值，不重新拟合 Wannier 轨道，也没有用直接结果去平移某一条插值能带以缩小误差。

```console
maxwell@maxwell:~/si-wannier/k4/validation$ sbatch run.slurm
Submitted batch job 1980
```

```console
maxwell@maxwell:~/si-wannier/k4/validation$ tail -10 si.bands.out
     Parallel routines
 
     PWSCF        :      0.20s CPU      0.31s WALL

 
   This run was terminated on:  22:49:11  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

核对脚本读取 QE XML 里的本征值，明确从 Hartree 换成 eV，再按相同 k 点与能带排序比较。作图统一减去直接 DFT Γ 点的最高占据态 6.386039243 eV，原始能量与误差在 CSV 中同时保留。

### 交给代码助手的任务：核对接口、展布与插值误差

> 在保存的 Si Wannier 算例目录中编写独立 Python 后处理程序。读取 k4/、k6/ 下的 si.win、si.wout、接口输出及直接 DFT 验证数据；核对 mp_grid、显式 k 点数/坐标/顺序、四个价带的 num_wann/num_bands 和接口正常结束状态。提取逐次 spread 与最终四个 Wannier 函数展布，单位保留 bohr²；以 direct-bands.csv 和相同 k 坐标上的 Wannier 插值值计算逐带误差及最大绝对误差，单位 eV，沿用原脚本的能量参考和带排序。输出检查 JSON 与逐点 CSV，标出缺文件或不匹配项，不以零填充。只解析已有结果，不运行 QE/Wannier90，也不将四价带 Si 模型外推到金属费米面。

[已有完整核对源码 analyse_wannier.py](/Atlas/examples/si-wannier/analyse_wannier.py) · [完整准备源码 prepare_si_wannier.py](/Atlas/examples/si-wannier/prepare_si_wannier.py)。

<details>
<summary>prepare_si_wannier.py 的完整源码</summary>

```python
from pathlib import Path
import shutil,json,hashlib
r=Path(__file__).resolve().parent
source=Path('<Wannier90源码目录>/examples/example11')
for name in ['silicon.scf','silicon.nscf','silicon.pw2wan','silicon.win']:
 shutil.copy2(source/name,r/'evidence'/('official-'+name))
common=f'''&CONTROL
 calculation = '{{calculation}}'
 prefix = 'si'
 pseudo_dir = '{r}/pseudo'
 outdir = './tmp'
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 2
 celldm(1) = 10.2
 nat = 2
 ntyp = 1
 ecutwfc = 40
 ecutrho = 320
 nbnd = 4
 occupations = 'fixed'
{{sym}}/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-10
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Si 28.0855 Si.pbe-n-van.UPF
ATOMIC_POSITIONS crystal
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
'''
for n in [4,6]:
 d=r/f'k{n}';(d/'tmp').mkdir(parents=True,exist_ok=True);(d/'validation/tmp').mkdir(parents=True,exist_ok=True)
 kpts=[(i/n,j/n,k/n) for i in range(n) for j in range(n) for k in range(n)]
 (d/'si.scf.in').write_text(common.format(calculation='scf',sym='')+'K_POINTS automatic\n10 10 10 0 0 0\n')
 (d/'si.nscf.in').write_text(common.format(calculation='nscf',sym=' nosym = .true.\n noinv = .true.\n')+f'K_POINTS crystal\n{n**3}\n'+''.join(' '.join(f'{v:.12f}' for v in p)+f' {1/n**3:.12f}\n' for p in kpts))
 win=f'''num_bands = 4
num_wann = 4
num_iter = 200
conv_tol = 1.0d-10
conv_window = 5
iprint = 2
length_unit = bohr
write_hr = true
write_xyz = true
bands_plot = true
bands_num_points = 80
begin projections
f=-0.125,-0.125,0.375:s
f=0.375,-0.125,-0.125:s
f=-0.125,0.375,-0.125:s
f=-0.125,-0.125,-0.125:s
end projections
begin unit_cell_cart
bohr
-5.10 0.00 5.10
0.00 5.10 5.10
-5.10 5.10 0.00
end unit_cell_cart
begin atoms_frac
Si -0.25 0.75 -0.25
Si 0.00 0.00 0.00
end atoms_frac
begin kpoint_path
G 0.00 0.00 0.00 X 0.50 0.00 0.50
X 0.50 0.00 0.50 W 0.50 0.25 0.75
W 0.50 0.25 0.75 L 0.50 0.50 0.50
L 0.50 0.50 0.50 G 0.00 0.00 0.00
end kpoint_path
mp_grid = {n} {n} {n}
begin kpoints
'''+''.join(' '.join(f'{v:.12f}' for v in p)+'\n' for p in kpts)+'end kpoints\n'
 (d/'silicon.win').write_text(win)
 (d/'silicon.pw2wan').write_text("&INPUTPP\n outdir='./tmp'\n prefix='si'\n seedname='silicon'\n write_amn=.true.\n write_mmn=.true.\n write_unk=.false.\n/\n")
 script=f'''#!/bin/bash
#SBATCH --job-name=atlas-si-w{n}
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
mpirun -np 8 <qe_bin>/pw.x -in si.scf.in > si.scf.out 2> si.scf.err
cp tmp/si.save/data-file-schema.xml scf.data-file-schema.xml
cp -r tmp/si.save validation/tmp/
mpirun -np 8 <qe_bin>/pw.x -in si.nscf.in > si.nscf.out 2> si.nscf.err
cp tmp/si.save/data-file-schema.xml nscf.data-file-schema.xml
<qe_bin>/wannier90.x -pp silicon > wannier-pp.out 2> wannier-pp.err
mpirun -np 8 <qe_bin>/pw2wannier90.x -in silicon.pw2wan > pw2wan.out 2> pw2wan.err
<qe_bin>/wannier90.x silicon > wannier.out 2> wannier.err
'''
 # Keep a plain numeric job label.
 script=script.replace(f'{{n}}',str(n))
 (d/'run.slurm').write_text(script)
(r/'structure-source.json').write_text(json.dumps({'source':'Wannier90 3.1.0 official example11 shipped with QE7.5','structure':'diamond Si, 2 atoms, ibrav=2, celldm(1)=10.2 bohr','not_relaxed_here':True,'modifications':['40/320 Ry cutoffs','explicit fixed occupations and 4 valence bands','full k grid with nosym/noinv','four bond-centred s projections; isolated valence subspace; no disentanglement','4^3 and 6^3 uniform meshes'],'protocol_convergence':'not established'},indent=2)+'\n')
print('Prepared independent k4 and k6 SCF -> NSCF -> interface -> Wannier chains')
```

</details>

<details>
<summary>analyse_wannier.py 的完整源码</summary>

```python
from pathlib import Path
import numpy as np,xml.etree.ElementTree as ET,re,json,csv,hashlib
r=Path(__file__).resolve().parent;HAEV=27.211386245988
sel=np.loadtxt(r/'validation-kpoints.csv',delimiter=',',skiprows=1);inds=sel[:,0].astype(int);nsel=len(sel)
valid=r/'k4/validation'
out=(valid/'si.bands.out').read_text();assert 'JOB DONE.' in out and 'eigenvalues not converged' not in out and (valid/'si.bands.err').stat().st_size==0
xml=ET.parse(valid/'bands.data-file-schema.xml').getroot();ks=xml.findall('./output/band_structure/ks_energies');assert len(ks)==nsel
rec=xml.find('./output/basis_set/reciprocal_lattice');B=np.array([list(map(float,rec.find(t).text.split())) for t in ['b1','b2','b3']])
kfrac=np.array([list(map(float,x.find('k_point').text.split())) for x in ks])@np.linalg.inv(B)
assert np.max(np.abs(kfrac-sel[:,1:4]))<2e-10
energy=np.array([list(map(float,x.find('eigenvalues').text.split())) for x in ks])*HAEV;assert energy.shape==(nsel,4)
reference=float(max(energy[0]));summary={'qe_version':'7.5','wannier90_version':'3.1.0','validation_unique_kpoints':len(np.unique(np.round(sel[:,1:4],12),axis=0)),'validation_points':nsel,'validation_eigenvalues':nsel*4,'energy_reference':'highest occupied direct DFT Gamma eigenvalue','energy_reference_eV':reference,'direct_DFT_source':'k4/validation/si.bands.in and bands.data-file-schema.xml','scope':'4 isolated valence bands only; no conduction bands, gap or transport claim','kmesh_results':{}}
records=[]
for mesh in [4,6]:
 d=r/f'k{mesh}'
 for prog in ['si.scf','si.nscf','pw2wan']:
  txt=(d/f'{prog}.out').read_text();assert 'JOB DONE.' in txt and not re.search('eigenvalues not converged|convergence NOT achieved|Error in routine',txt);assert (d/f'{prog}.err').stat().st_size==0
 for name in ['wannier.err','wannier-pp.err']:assert (d/name).stat().st_size==0
 wo=(d/'silicon.wout').read_text();assert 'Wannierisation convergence criteria satisfied' in wo and 'All done: wannier90 exiting' in wo
 eig=np.loadtxt(d/'silicon.eig');assert eig.shape==(mesh**3*4,3)
 nxml=ET.parse(d/'nscf.data-file-schema.xml').getroot();nks=nxml.findall('./output/band_structure/ks_energies');assert len(nks)==mesh**3
 nbasis=nxml.find('./output/basis_set/reciprocal_lattice');nB=np.array([list(map(float,nbasis.find(t).text.split())) for t in ['b1','b2','b3']])
 xmlk=np.array([list(map(float,x.find('k_point').text.split())) for x in nks])@np.linalg.inv(nB)
 wink=np.array([list(map(float,l.split())) for l in (d/'silicon.win').read_text().split('begin kpoints')[1].split('end kpoints')[0].strip().splitlines()])
 assert wink.shape==xmlk.shape and np.max(np.abs((xmlk-wink+.5)%1-.5))<2e-10
 assert list(map(int,(d/'silicon.mmn').read_text().splitlines()[1].split()))==[4,mesh**3,8]
 assert list(map(int,(d/'silicon.amn').read_text().splitlines()[1].split()))==[4,mesh**3,4]
 xmlE=np.array([list(map(float,x.find('eigenvalues').text.split())) for x in nks])*HAEV
 assert np.max(np.abs(eig[:,2].reshape(-1,4)-xmlE))<1e-7
 x=np.loadtxt(d/'silicon_band.dat');assert x.shape==(247*4,2)
 band=x[:,1].reshape(4,247).T;distance=x[:247,0]
 assert np.max(np.abs(distance[inds]-sel[:,-1]))<1e-7
 err=band[inds]-energy
 spread=float(re.search(r'Final Spread \(Bohr\^2\)\s+Omega Total\s*=\s*([.\d]+)',wo).group(1))
 convrows=re.findall(r'^\s*(\d+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+).*?<-- CONV',wo,re.M)
 conv=np.array([[int(v[0]),float(v[1]),float(v[2]),float(v[3])] for v in convrows]);assert conv.ndim==2
 np.savetxt(d/'spread-history.csv',conv,delimiter=',',header='iteration,delta_spread_bohr2,rms_gradient,total_spread_bohr2',comments='')
 np.savetxt(d/'bands.csv',np.column_stack([distance,band,band-reference]),delimiter=',',header='distance_Ainv,E1_eV,E2_eV,E3_eV,E4_eV,E1_minus_VBM_eV,E2_minus_VBM_eV,E3_minus_VBM_eV,E4_minus_VBM_eV',comments='')
 maxerr=float(np.max(np.abs(err)));rms=float(np.sqrt(np.mean(err**2)))
 summary['kmesh_results'][str(mesh)]={'num_kpoints':mesh**3,'num_bands':4,'num_wann':4,'spread_bohr2':spread,'spread_angstrom2':spread*.529177210903**2,'wannier_iterations':int(conv[-1,0]),'validation_max_abs_error_eV':maxerr,'validation_RMSE_eV':rms,'native_complete':True,'scientific_protocol_convergence':'not established'}
 for i,idx in enumerate(inds):
  for ib in range(4):
   records.append(dict(training_mesh=mesh,path_index=int(idx),k1=sel[i,1],k2=sel[i,2],k3=sel[i,3],distance_Ainv=sel[i,4],band=ib+1,E_DFT_eV=energy[i,ib],E_Wannier_eV=band[idx,ib],error_eV=err[i,ib]))
with (r/'validation-errors.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
np.savetxt(r/'direct-bands.csv',np.column_stack([sel,energy,energy-reference]),delimiter=',',header='path_index,k1,k2,k3,distance_Ainv,E1_eV,E2_eV,E3_eV,E4_eV,E1_minus_VBM_eV,E2_minus_VBM_eV,E3_minus_VBM_eV,E4_minus_VBM_eV',comments='')
summary['pseudopotential']={'filename':'Si.pbe-n-van.UPF','source':'https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-van.UPF','sha256':hashlib.sha256((r/'pseudo/Si.pbe-n-van.UPF').read_bytes()).hexdigest(),'type':'USPP','functional':'PBE','relativistic':'nonrelativistic','valence_electrons':4}
(r/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Direct DFT validation: 13 path points, 4 valence eigenvalues at each point')
print(f'Common energy reference: direct Gamma valence maximum = {reference:.9f} eV')
print('mesh   n_k   spread_bohr2   MLWF_iterations   max_error_eV   RMSE_eV')
for n,v in summary['kmesh_results'].items(): print(f"{n}^3    {v['num_kpoints']:3d}    {v['spread_bohr2']:.9f}      {v['wannier_iterations']:3d}           {v['validation_max_abs_error_eV']:.9f}   {v['validation_RMSE_eV']:.9f}")
print('Interpolation comparison is limited to these 13 points; no full-grid convergence or conduction-band claim.')
```

</details>

```console
maxwell@maxwell:~/si-wannier$ python3 analyse_wannier.py > analysis.out
maxwell@maxwell:~/si-wannier$ cat analysis.out
Direct DFT validation: 13 path points, 4 valence eigenvalues at each point
Common energy reference: direct Gamma valence maximum = 6.386039243 eV
mesh   n_k   spread_bohr2   MLWF_iterations   max_error_eV   RMSE_eV
4^3     64    22.766427441        9           0.214117881   0.082717233
6^3    216    26.905582236       13           0.083242336   0.026945536
Interpolation comparison is limited to these 13 points; no full-grid convergence or conduction-band claim.
```

| Wannier均匀网格 | k 点数 | 总展布 / bohr² | 13个路径位置的最大误差 / eV | 均方根误差 / eV |
|---:|---:|---:|---:|---:|
| 4³ | 64 | 22.766427441 | 0.214118 | 0.082717 |
| 6³ | 216 | 26.905582236 | 0.083242 | 0.026946 |

![Wannier插值与直接DFT采样点的比较](/Atlas/examples/si-wannier/figures/wannier-bands.png)

上图画四条价带，下图在每个验证点取四条带中最大的绝对误差。6³ 比 4³ 明显改善，但这 13 个位置上仍有约 0.083 eV 的最大误差。因此不能称这条 6³ 曲线已经高精度收敛；它只完成了本例的一次网格对照。若后续用途需要更小误差，应继续加密并扩展直接 DFT 检查点，同时明确用途能接受的误差。

这张图也不验证导带、带隙、费米面或输运。要将这些量纳入 Wannier 模型，必须重新选择能带数、投影和必要的解缠窗口，再对目标能区单独验证。

## 下载后重新画图

将 `k4`、`k6`、`direct-bands.csv`、`validation-errors.csv` 与 [plot_wannier.py](/Atlas/examples/si-wannier/plot_wannier.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/si-wannier/atlas_plot_style.py)） 放在同一目录，运行：

<details>
<summary>plot_wannier.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;out=r/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
cols={4:'#ad623e',6:'#277f8e'}
def load(p):return np.loadtxt(r/p,delimiter=',',skiprows=1)
b4=load('k4/bands.csv');b6=load('k6/bands.csv');direct=load('direct-bands.csv');e=list(csv.DictReader((r/'validation-errors.csv').open()))
labels=[x.split() for x in (r/'k4/silicon_band.labelinfo.dat').read_text().splitlines()];ticks=[float(x[2]) for x in labels];names=['Γ' if x[0]=='G' else x[0] for x in labels]
fig,ax=plt.subplots(2,1,figsize=(7.5,7),sharex=True,gridspec_kw={'height_ratios':[3,1.3]})
for mesh,b,ls in [(4,b4,'--'),(6,b6,'-')]:
 for ib in range(4):ax[0].plot(b[:,0],b[:,5+ib],color=cols[mesh],ls=ls,lw=1.2,label=f'{mesh}³ Wannier' if ib==0 else None)
for ib in range(4):ax[0].plot(direct[:,4],direct[:,9+ib],'o',mfc='white',mec='#24242a',ms=4,label='Direct DFT checks' if ib==0 else None)
ax[0].set(ylabel='Energy relative to direct Γ valence maximum (eV)',title='Si | four valence bands only');ax[0].legend(frameon=False,ncol=3,fontsize=9)
for mesh in [4,6]:
 rows=[v for v in e if int(v['training_mesh'])==mesh];ix=sorted(set(int(v['path_index']) for v in rows));x=[];y=[]
 for j in ix:
  values=[v for v in rows if int(v['path_index'])==j];x.append(float(values[0]['distance_Ainv']));y.append(max(abs(float(v['error_eV'])) for v in values)*1000)
 ax[1].plot(x,y,'o-',color=cols[mesh],label=f'{mesh}³ mesh')
ax[1].set(ylabel='Maximum band error (meV)',xticks=ticks,xticklabels=names,xlim=(ticks[0],ticks[-1]))
for a in ax:
 for x in ticks:a.axvline(x,color='#bfbfc4',lw=.6,zorder=0)
fig.tight_layout();fig.savefig(out/'wannier-bands.png',bbox_inches='tight');fig.savefig(out/'wannier-bands.pdf',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(9,3.8))
for mesh in [4,6]:
 x=load(f'k{mesh}/spread-history.csv');ax[0].plot(x[:,0],x[:,3],'o-',color=cols[mesh],label=f'{mesh}³')
 ax[1].semilogy(x[:,0],np.maximum(abs(x[:,1]),1e-16),'o-',color=cols[mesh],label=f'{mesh}³')
ax[0].set(xlabel='Wannier iteration',ylabel='Total spread (bohr²)');ax[0].legend(frameon=False)
ax[1].axhline(1e-10,color='#777',ls='--',lw=1,label='Tolerance');ax[1].set(xlabel='Wannier iteration',ylabel='Absolute spread change (bohr²)');ax[1].legend(frameon=False)
fig.suptitle('Spread convergence within a mesh does not establish interpolation accuracy',fontsize=11)
fig.tight_layout();fig.savefig(out/'wannier-spread.png',bbox_inches='tight');fig.savefig(out/'wannier-spread.pdf',bbox_inches='tight');plt.close(fig)
print('Wrote wannier-bands and wannier-spread as PNG/PDF')
```

</details>

```bash
python plot_wannier.py
```

脚本生成能带与误差对照、展布迭代两组 PNG/PDF。原始文件 [k4/silicon_band.dat](/Atlas/examples/si-wannier/k4/silicon_band.dat) 按能带分块，每条带有 247 个路径点；[k4/silicon_band.kpt](/Atlas/examples/si-wannier/k4/silicon_band.kpt) 是相应 k 点，[k4/silicon_band.labelinfo.dat](/Atlas/examples/si-wannier/k4/silicon_band.labelinfo.dat) 给出高对称点的位置。不要把四条带的四个数据块接成一条折线。

| 内容 | 4³ 路线 | 6³ 路线 |
|---|---|---|
| SCF输入 | [si.scf.in](/Atlas/examples/si-wannier/k4/si.scf.in) | [si.scf.in](/Atlas/examples/si-wannier/k6/si.scf.in) |
| NSCF输入 | [si.nscf.in](/Atlas/examples/si-wannier/k4/si.nscf.in) | [si.nscf.in](/Atlas/examples/si-wannier/k6/si.nscf.in) |
| Wannier输入 | [silicon.win](/Atlas/examples/si-wannier/k4/silicon.win) | [silicon.win](/Atlas/examples/si-wannier/k6/silicon.win) |
| 接口输入 | [silicon.pw2wan](/Atlas/examples/si-wannier/k4/silicon.pw2wan) | [silicon.pw2wan](/Atlas/examples/si-wannier/k6/silicon.pw2wan) |
| 完整脚本 | [run.slurm](/Atlas/examples/si-wannier/k4/run.slurm) | [run.slurm](/Atlas/examples/si-wannier/k6/run.slurm) |
| SCF输出 | [si.scf.out](/Atlas/examples/si-wannier/k4/si.scf.out) | [si.scf.out](/Atlas/examples/si-wannier/k6/si.scf.out) |
| NSCF输出 | [si.nscf.out](/Atlas/examples/si-wannier/k4/si.nscf.out) | [si.nscf.out](/Atlas/examples/si-wannier/k6/si.nscf.out) |
| 接口输出 | [pw2wan.out](/Atlas/examples/si-wannier/k4/pw2wan.out) | [pw2wan.out](/Atlas/examples/si-wannier/k6/pw2wan.out) |
| 完整Wannier日志 | [silicon.wout](/Atlas/examples/si-wannier/k4/silicon.wout) | [silicon.wout](/Atlas/examples/si-wannier/k6/silicon.wout) |
| 能带数值 | [bands.csv](/Atlas/examples/si-wannier/k4/bands.csv) | [bands.csv](/Atlas/examples/si-wannier/k6/bands.csv) |
| 展布迭代 | [spread-history.csv](/Atlas/examples/si-wannier/k4/spread-history.csv) | [spread-history.csv](/Atlas/examples/si-wannier/k6/spread-history.csv) |

直接验证的 [输入](/Atlas/examples/si-wannier/k4/validation/si.bands.in)、[输出](/Atlas/examples/si-wannier/k4/validation/si.bands.out)、[逐带误差](/Atlas/examples/si-wannier/validation-errors.csv) 和 [核对脚本](/Atlas/examples/si-wannier/analyse_wannier.py) 也随数据保存。

## 文献中基于 Wannier 紧束缚模型的表面态与谱函数应用

构造出经过验证的最大局域化 Wannier 函数实空间哈密顿量 `*_hr.dat` 后，除了做体相能带插值，还常将其输入到 WannierTools 等后处理程序中，采用迭代格林函数法计算半无限大晶体表面的局域态密度（表面谱函数）及三维表面态色散，直接与 ARPES 测量结果对照。

<figure class="research-figure"><img src="/Atlas/figures/literature/M7_SurfaceStates_3DVHS_ARPES_ZrAs2_Fig4.jpg" alt="由最大局域化 Wannier 紧束缚哈密顿量计算的 ZrAs2 (001) 半无限表面谱函数与三维鞍点色散" loading="lazy"/><figcaption>由最大局域化 Wannier 紧束缚哈密顿量结合 WannierTools 计算得到的 ZrAs<sub>2</sub> (001) 半无限表面谱函数与三维鞍点色散，并与高分辨 ARPES 实验谱进行对比。引自 <em>Nat. Commun.</em> <strong>16</strong>, 2831 (2025)，Fig. 4，<a href="https://doi.org/10.1038/s41467-025-58024-w" target="_blank" rel="noopener noreferrer">DOI: 10.1038/s41467-025-58024-w</a>。</figcaption></figure>

另一项重要应用是在 EPW 等程序中利用 Wannier 表象对电子本征态与电子—声子耦合矩阵元同时做精细动量网格插值，进而计算有限温度下的电子谱函数 A(k, ω)，将多体自能重整化后的能带色散、声子伴峰与未重整化的白色 DFT 裸能带曲线叠加展示。

<figure class="research-figure"><img src="/Atlas/figures/literature/M9_SpectralFunction_Akw_EPW2016_Fig6.jpg" alt="硼掺杂金刚石中通过 Wannier 插值计算的电子声子耦合谱函数与白色裸 DFT 能带对比" loading="lazy"/><figcaption>硼掺杂金刚石在 1 K 与 300 K 下通过 Wannier 插值计算的电子—声子相互作用谱函数 <em>A</em>(<strong>k</strong>, ω) 热力图，图中叠加白色实线表示未计入电声自能修正的 DFT 裸能带色散。引自 Poncé 等人，<em>Comput. Phys. Commun.</em> <strong>209</strong>, 116 (2016)，Fig. 6，<a href="https://doi.org/10.1016/j.cpc.2016.07.028" target="_blank" rel="noopener noreferrer">DOI: 10.1016/j.cpc.2016.07.028</a>。</figcaption></figure>

下一步：回到 [能带](/Atlas/m/bands/qe/) 对照直接 DFT 的路径与能量零点。如果需要 [费米面](/Atlas/m/fermi-surface/qe/)，应先构建覆盖费米能附近的模型；本页只含 Si 价带的四轨道模型不具备该用途。

```text
SCF电荷密度 → 均匀网格NSCF波函数 → nnkp需求 + pw2wannier90 → amn/mmn/eig
                                                              ↓
                                                       Wannier局域化 → 插值能带
SCF副本 → 独立路径点DFT ────────────────────────────────────────────┘ 比较误差
```
