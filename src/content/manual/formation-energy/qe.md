[QE：pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE：结构优化与总能计算](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [Materials Project：形成能与相图方法](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds) · [AFLOW：晶体原型库](https://aflow.org/prototype-encyclopedia/)

[下载本例完整输入、输出、表格与绘图脚本](/Atlas/examples/alsi-formation-hull-files.tar.gz)。解压后在 `alsi-formation-hull` 目录运行分析与绘图；包内包含原始 OUT/XML，足以重新提取本文数值。大体积的电荷密度与波函数另由实际计算生成，重跑时先按下文准备对应父目录。

把 B2 AlSi 的 OUT 打开，可以找到一个以 Ry 为单位的总能。这个数随原子数、元素和赝势改变；要判断形成 AlSi 是否比拆成 Al 和 Si 更有利，必须把三者放到同一套计算约定下相减。这里实际计算了五个小晶胞：fcc Al、金刚石 Si，以及在 B2、L1₂ 原型上替换元素得到的三个 Al–Si 候选。

中间三个结构是明确构造的教学候选。B2 的位点来自 [CsCl 原型](https://aflow.org/prototype-encyclopedia/AB_cP2_221_a_b-002/)，L1₂ 的位点来自 [Cu₃Au 原型](https://aflow.org/prototype-encyclopedia/AB3_cP4_221_a_c-001/)。初始晶格常数只是优化的起点；这套文件没有把它们称为已报道的 Al–Si 稳定化合物。Al 和 Si 分别使用 [fcc](https://aflow.org/prototype-encyclopedia/A_cF4_225_a-001/) 与 [diamond](https://aflow.org/prototype-encyclopedia/A_cF8_227_a-001/) 结构。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ ls -d al-fcc si-diamond alsi-b2 al3si-l12 alsi3-l12
al-fcc  al3si-l12  alsi-b2  alsi3-l12  si-diamond
[preston@preston-System-Product-Name alsi-formation-hull]$
```

| 目录 | 晶胞内原子 | 初始 a / Å | 原子位置的约定 |
| --- | --- | --- | --- |
| al-fcc | 1 Al | 4.05 | fcc 原胞，原子在原点 |
| si-diamond | 2 Si | 5.43 | fcc 原胞，两个原子的笛卡尔坐标相差 (a/4,a/4,a/4) |
| alsi-b2 | 1 Al + 1 Si | 3.32 | 简单立方，角点和体心 |
| al3si-l12 | 3 Al + 1 Si | 4.12 | Si 在角点，Al 在三个面心 |
| alsi3-l12 | 1 Al + 3 Si | 4.25 | Al 在角点，Si 在三个面心 |

所有原子坐标、构造说明和原型链接都保存在 [sources/prototypes.json](/Atlas/examples/alsi-formation-hull/sources/prototypes.json)。五项均为标量相对论、非自旋极化的 PBE 计算，没有加入 SOC、Hubbard U 或色散修正。Al、Si 使用同一个 pslibrary 1.0.0 家族的 USPP：

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ ls -lh pseudo/*.UPF
-rw-rw-r-- 1 preston preston 1.5M Sep 22 22:19 pseudo/Al.pbe-n-rrkjus_psl.1.0.0.UPF
-rw-rw-r-- 1 preston preston 1.5M Sep 22 22:19 pseudo/Si.pbe-n-rrkjus_psl.1.0.0.UPF
[preston@preston-System-Product-Name alsi-formation-hull]$
```

赝势分别可从 QE 的 [Al 文件](https://pseudopotentials.quantum-espresso.org/upf_files/Al.pbe-n-rrkjus_psl.1.0.0.UPF) 和 [Si 文件](https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF) 下载。本次对文件做了独立下载与 SHA 核对。这里的元素参考能来自同批端元计算；不能把另一种泛函、另一份赝势或孤立原子的能量直接填进来。

先在各自原型内优化晶格尺度。完整的 B2 输入是 [alsi-b2/vc-relax.in](/Atlas/examples/alsi-formation-hull/alsi-b2/vc-relax.in)，其余四份对应为 [al-fcc](/Atlas/examples/alsi-formation-hull/al-fcc/vc-relax.in), [si-diamond](/Atlas/examples/alsi-formation-hull/si-diamond/vc-relax.in), [al3si-l12](/Atlas/examples/alsi-formation-hull/al3si-l12/vc-relax.in), [alsi3-l12](/Atlas/examples/alsi-formation-hull/alsi3-l12/vc-relax.in)。普通结构优化的操作见 [vc-relax](/Atlas/m/vc-relax/qe/)；这次为了保留各候选的定义，使用了以下晶胞约束。

```text
&CELL
 cell_dynamics = 'bfgs'
 press = 0.0
 press_conv_thr = 0.1
 cell_dofree = 'ibrav'
/
```

`cell_dofree='ibrav'` 保持初始 Bravais 类型。这里的 fcc 和简单立方晶格都只有一个独立尺度，因此这是各立方原型内部的零压优化。原子的高对称位点也被保留；没有搜索降低对称性的畸变或其它晶体原型。电子阈值为 `1e-10 Ry`，BFGS 的能量、力、压力阈值分别为 `1e-6 Ry`、`1e-4 Ry/Bohr`、`0.1 kbar`。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ cat alsi-b2/run.sh
#!/bin/bash
#SBATCH --job-name=a-alsi-b2
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:40:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in vc-relax.in > vc-relax.out 2> vc-relax.err
[preston@preston-System-Product-Name alsi-formation-hull]$
```

这台 Preston 使用 QE 7.5 的 GCC/OpenMPI 构建。脚本每项申请 4 个 MPI 进程，线程数固定为 1；输出、错误流和调度器日志分别留下。

```console
[preston@preston-System-Product-Name alsi-b2]$ sbatch run.sh
Submitted batch job 808
[preston@preston-System-Product-Name alsi-b2]$
```

BFGS 结束后先读优化段，再读最后一次电子重算。以下是真实的几何优化结尾：

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ grep -A 26 "bfgs converged" alsi-b2/vc-relax.out
     bfgs converged in   6 scf cycles and   5 bfgs steps
     (criteria: energy <  1.0E-06 Ry, force <  1.0E-04 Ry/Bohr, cell <  1.0E-01 kbar)

     End of BFGS Geometry Optimization

     Final enthalpy           =     -16.4203535701 Ry

     File ./tmp/alsi-b2.bfgs deleted, as requested
Begin final coordinates
     new unit-cell volume =    212.45764 a.u.^3 (    31.48297 Ang^3 )
     density =      2.90443 g/cm^3

CELL_PARAMETERS (alat=  6.27389073)
   0.951087557   0.000000000   0.000000000
   0.000000000   0.951087557   0.000000000
   0.000000000   0.000000000   0.951087557

ATOMIC_POSITIONS (alat)
Al               0.0000000000        0.0000000000        0.0000000000
Si               0.4755437783        0.4755437783        0.4755437783
End final coordinates



     Writing config-only to output data dir ./tmp/alsi-b2.save/ :
     XML data file

[preston@preston-System-Product-Name alsi-formation-hull]$
```

`alat=6.27389073` 仍是这一段打印所用的长度单位。晶胞矩阵乘上它、再由 Bohr 转为 Å，得到约 `3.15761069 Å` 的立方边长；原子坐标也要用同样的单位解释。把打印的 `0.4755437783` 当成分数坐标，会把体心原子放错位置。后续输入直接写出 Å 制晶胞，并把体心原子写成 `crystal` 下的 `(0.5,0.5,0.5)`。

五个优化的末次压力均约为 `0±0.01 kbar`。优化中间轮的本征值警告保存在原始 OUT 里；固定几何后另做静态求解，并检查最终电子迭代，而不是只看到 BFGS 或 `JOB DONE.` 就取数。

为了比较数值设置，五个候选分别建立同名子目录；每一行协议都必须凑齐五项才能组成一组形成能。

| 子目录 | k 网格 | ecutwfc / ecutrho（Ry） | mv 展宽 / Ry |
| --- | --- | --- | --- |
| k12 | 12³ | 60 / 640 | 0.01 |
| k16 | 16³ | 60 / 640 | 0.01 |
| k20 | 20³ | 60 / 640 | 0.01 |
| sigma005 | 20³ | 60 / 640 | 0.005 |
| cutoff80 | 20³ | 80 / 640 | 0.005 |
| k24 | 24³ | 80 / 640 | 0.005 |

如果从下载包重新运行 QE，先完成各候选自己的 `vc-relax`，并检查优化与最后一轮电子收敛。公开包没有附带电荷密度和波函数；五个 `k24/scf.in` 都使用 `startingpot='file'`，仅有输入文件还不能直接提交。在全新解压的目录中，以 B2 为例，待其父计算验收后复制整个临时目录：

```bash
cp -a alsi-b2/tmp alsi-b2/k24/
```

结果应为 `alsi-b2/k24/tmp/alsi-b2.save/`。另外四个候选也各自从自己的优化目录复制，不能共享同一份密度。AlSi₃ 的 `k12`、`k16`、`k20`、`sigma005`、`cutoff80` 也需要自己的优化密度；其余四个候选在这些早期协议中使用原子密度开始。检查完输入中的 `pseudo_dir` 和脚本中的 `<qe_bin>` 再提交。

以 B2 的 24³ 静态输入为例，读取的是这一候选自己的已收敛密度，新的 k 点重新生成波函数。这样只借用一个较好的电子迭代起点；总能仍由当前 k 网格、截断和展宽重新自洽得到。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ vi alsi-b2/k24/scf.in
[preston@preston-System-Product-Name alsi-formation-hull]$ cat alsi-b2/k24/scf.in
&CONTROL
 calculation = 'scf'
 prefix = 'alsi-b2'
 outdir = './tmp'
 pseudo_dir = '../../pseudo'
 tstress = .true.
 tprnfor = .true.
/
&SYSTEM
 ibrav = 0
 nat = 2
 ntyp = 2
 nbnd = 10
 ecutwfc = 80
 ecutrho = 640
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.005
/
&ELECTRONS
 startingpot = 'file'
 startingwfc = 'atomic+random'
 conv_thr = 1.0d-10
 diagonalization = 'cg'
 diago_cg_maxiter = 1000
 diago_thr_init = 1.0d-6
/
ATOMIC_SPECIES
Al 26.9815385 Al.pbe-n-rrkjus_psl.1.0.0.UPF
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
3.157610687739 0.000000000000 0.000000000000
0.000000000000 3.157610687739 0.000000000000
0.000000000000 0.000000000000 3.157610687739
ATOMIC_POSITIONS crystal
Al 0.000000000000 0.000000000000 0.000000000000
Si 0.500000000000 0.500000000000 0.500000000000
K_POINTS automatic
24 24 24 0 0 0
[preston@preston-System-Product-Name alsi-formation-hull]$
```

五个候选在所有比较目录里都固定为各自 12³ 优化得到的同一几何；提取程序会核对晶胞与坐标的哈希。`24³` 是每个晶格自身倒格矢方向的网格数，不能把 fcc 原胞与简单立方晶胞的同一网格数理解成完全相同的倒空间间距。

```console
[preston@preston-System-Product-Name k24]$ sbatch run.sh
Submitted batch job 841
[preston@preston-System-Product-Name k24]$
```

运行中用 `watch -n 2 "tail -n 10 alsi-b2/k20/scf.out"` 看尾部；这条命令在会话里实际执行过，按 Ctrl-C 退出的是监视程序。屏幕上 `iteration #` 增加表示电子迭代在推进，仍需等待 `estimated scf accuracy` 达到阈值。

OUT 开头先核对版本、原子数、电子数、截断与晶胞。下面的 12³ 例子只摘录这一部分，[完整 OUT](/Atlas/examples/alsi-formation-hull/alsi-b2/k12/scf.out) 可以同时查看前面的程序说明与后面的本征值列表。

```console
bravais-lattice index     =            0
     lattice parameter (alat)  =       5.9670  a.u.
     unit-cell volume          =     212.4576 (a.u.)^3
     number of atoms/cell      =            2
     number of atomic types    =            2
     number of electrons       =         7.00
     number of Kohn-Sham states=           10
     kinetic-energy cutoff     =      60.0000  Ry
     charge density cutoff     =     640.0000  Ry
     scf convergence threshold =      1.0E-10
     mixing beta               =       0.7000
     number of iterations used =            8  plain     mixing
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)

     celldm(1)=   5.967019  celldm(2)=   0.000000  celldm(3)=   0.000000
     celldm(4)=   0.000000  celldm(5)=   0.000000  celldm(6)=   0.000000

     crystal axes: (cart. coord. in units of alat)
               a(1) = (   1.000000   0.000000   0.000000 )
               a(2) = (   0.000000   1.000000   0.000000 )
               a(3) = (   0.000000   0.000000   1.000000 )

     reciprocal axes: (cart. coord. in units 2 pi/alat)
               b(1) = (  1.000000  0.000000  0.000000 )
               b(2) = (  0.000000  1.000000  0.000000 )
               b(3) = (  0.000000  0.000000  1.000000 )
```

B2 晶胞含 1 个 Al 和 1 个 Si，赝势价电子数合计为 7，所以这里打印 `number of electrons = 7.00`。`ibrav=0` 让输入直接携带优化后的三根晶格矢量；QE 会提醒已知 Bravais 类型时优先使用对应的 `ibrav`。这组实际输出仍保留了立方结构的对称性，输入与输出晶胞也逐项核对。

往后看，电子迭代中间的 `total energy` 还会变化；带感叹号的结果旁边才会同时给出此次达到的误差估计与电子收敛行。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ grep -A 19 "!    total energy" alsi-b2/k12/scf.out
!    total energy              =     -16.42034573 Ry
     estimated scf accuracy    <          3.9E-12 Ry
     smearing contrib. (-TS)   =       0.00002197 Ry
     internal energy E=F+TS    =     -16.42036770 Ry

     The total energy is F=E-TS. E is the sum of the following terms:
     one-electron contribution =       7.29448923 Ry
     hartree contribution      =       0.14256436 Ry
     xc contribution           =      -8.74453257 Ry
     ewald contribution        =     -15.11288871 Ry

     convergence has been achieved in   9 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
     atom    2 type  2   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000

[preston@preston-System-Product-Name alsi-formation-hull]$
```

这里 QE 7.5 已经直接说明：带感叹号的总能是 `F=E-TS`，并另列 `internal energy E=F+TS`。本次相减始终取同一种 `! total energy`，所有元素参考和候选使用相同冷展宽。`mv` 的 σ 是数值积分参数，这些行不能解释成已经计算了某个真实温度下的材料自由能。把某一项改取 `internal energy`、另几项仍取 `F`，会制造额外的不一致。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ grep -A 12 "Forces acting" alsi-b2/k12/scf.out
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
     atom    2 type  2   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000


     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=       -0.01
  -0.00000006   0.00000000   0.00000000           -0.01        0.00        0.00
   0.00000000  -0.00000006   0.00000000            0.00       -0.01        0.00
[preston@preston-System-Product-Name alsi-formation-hull]$
```

对称结构的原子力接近零，只说明这些位点满足当前对称约束下的力条件。是否会沿降对称方向畸变，还需要额外结构或声子证据。压力则会随 k 网格、展宽和截断改变，下面的数值检查保留了这个变化。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ tail -n 12 alsi-b2/k12/scf.out
     interpolate  :      0.08s CPU      0.09s WALL (      10 calls)

     Parallel routines

     PWSCF        :     43.16s CPU     46.37s WALL


   This run was terminated on:  22:44:25  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name alsi-formation-hull]$
```

末尾同时保留了耗时和 `JOB DONE.`。提取脚本要求最后一轮电子迭代没有本征值未收敛行、OUT 给出电子收敛、XML 的收敛标记为 true，并要求 XML 与 OUT 总能一致。初轮警告的数量另存为表列，不会从源文件里删掉。20³ 高截断结果还进行了电子自洽重算。其中四项沿用已完成的密度和波函数；AlSi₃ 的原生输入重复写了 `startingpot` 与 `startingwfc`，实际 OUT 显示读取已有密度、重新生成随机化原子波函数，不能把它也写成波函数延续。五项重算全程均没有本征值未收敛行，与父计算的能量差最大为 `0.000006 meV/atom`；这检验的是同一数值协议下电子求解的一致性，不能替代 k 网格收敛。错误流保留了本机重复出现的 `Authorization required, but no authorization protocol specified` 环境提示，不能写成空文件。示例输入见 [alsi-b2/verify/scf.in](/Atlas/examples/alsi-formation-hull/alsi-b2/verify/scf.in)。

`verify` 的父计算是同一候选的 `cutoff80`，不是 12³ 的优化波函数。重跑时应等 `cutoff80` 验收后，在干净的验证目录中复制：

```bash
cp -a alsi-b2/cutoff80/tmp alsi-b2/verify/
```

AlSi₃ 的原始输入保留在下载包中，便于核对这次输出。如果重新提交这一项，先用 `vi` 删除重复赋值，只保留一组 `startingpot='file'`、`startingwfc='atomic+random'`；这与原始 OUT 实际采用的起始方式一致。最终输入应清楚表达一个选择，不能依靠重复项的读取顺序。

真正取形成能时，先把端元能量换成每原子：`μAl=E(Al原胞)/1`，`μSi=E(Si原胞)/2`。对含 nAl 个 Al、nSi 个 Si 的候选：

```text
ΔE_form (eV/atom) = [E_cell − nAl × μAl − nSi × μSi] × 13.605693122994 / (nAl + nSi)
```

例如这组 24³ 结果中，Al 为 `-5.0395901951 Ry/atom`，Si 两原子原胞为 `-22.8402546465 Ry`，所以 Si 参考需要先除以 2。B2 AlSi 的 `-16.4206511902 Ry/cell` 减去 1 个 Al 和 1 个 Si 的参考后，再除以 2，得到 `0.265762 eV/atom`。

提取程序 [analyse_alsi.py](/Atlas/examples/alsi-formation-hull/analyse_alsi.py) 会从实际输入、OUT 和 XML 生成下表，同时留下各文件的 SHA。画图程序 [plot_alsi.py](/Atlas/examples/alsi-formation-hull/plot_alsi.py) 只读取 CSV，因此可以把数据拉到本机绘图。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ python3 analyse_alsi.py
case           xSi   total_energy(Ry/cell) formation(eV/atom) above_hull(eV/atom)
al-fcc          0.00        -5.0395901951         0.00000000          0.00000000
al3si-l12       0.25       -26.5073650036         0.10725676          0.10725676
alsi-b2         0.50       -16.4206511902         0.26576224          0.26576224
alsi3-l12       0.75       -39.1923948271         0.36591606          0.36591606
si-diamond      1.00       -22.8402546465         0.00000000          0.00000000
Finite-set hull vertices: al-fcc, si-diamond
Numerical differences: numerical-checks.csv (1 meV/atom teaching comparison line)
[preston@preston-System-Product-Name alsi-formation-hull]$
```

| 候选 | xSi | 总能 / Ry·cell⁻¹ | 形成能 / eV·atom⁻¹ | 静态压力 / kbar |
| --- | --- | --- | --- | --- |
| al-fcc | 0.0 | -5.03959020 | 0.000000 | -2.86 |
| al3si-l12 | 0.25 | -26.50736500 | 0.107257 | 1.28 |
| alsi-b2 | 0.5 | -16.42065119 | 0.265762 | 1.16 |
| alsi3-l12 | 0.75 | -39.19239483 | 0.365916 | -0.57 |
| si-diamond | 1.0 | -22.84025465 | 0.000000 | 0.01 |

[全部 30 项能量与输入输出哈希](/Atlas/examples/alsi-formation-hull/energy-table.csv)、[逐项数值变化](/Atlas/examples/alsi-formation-hull/numerical-checks.csv) 和 [24³ 五项汇总](/Atlas/examples/alsi-formation-hull/formation-energy.csv) 可以一起下载。所有能量差都在同一行协议内重新减去同协议端元。

| 候选 | 12→16 | 16→20 | σ .01→.005 | 60→80 Ry | 20→24 |
| --- | --- | --- | --- | --- | --- |
| al3si-l12 | +2.139 | -5.076 | -0.063 | -0.004 | -1.344 |
| alsi-b2 | -0.896 | -4.274 | -0.184 | -0.011 | -0.930 |
| alsi3-l12 | +0.579 | -1.823 | -0.115 | -0.015 | -0.173 |

这张表的单位是 meV/atom；前三档 k 网格在 σ=0.01、60 Ry 下比较，最后一档在 σ=0.005、80 Ry 下比较，中间分别只改变展宽和波函数截断。教学比较线取 1 meV/atom。20³→24³ 的最大变化为 `1.344 meV/atom`，仍高于比较线，因此到这一档还不能宣称形成能已经达到 1 meV/atom 收敛。24³ 静态压力的最大绝对值为 `2.86 kbar`。这些 24³ 静态点沿用初始优化几何，不能直接称为 24³/80 Ry/σ=.005 协议下再次优化后的零压结果。这里也没有检验电荷密度截断、晶体原型完备性或真实有限温度自由能。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ python3 plot_alsi.py formation
plots/formation-energy.png and plots/formation-energy.svg
[preston@preston-System-Product-Name alsi-formation-hull]$
```

![形成能及数值参数变化](/Atlas/examples/alsi-formation-hull/plots/formation-energy.svg)

左图把三个候选与同批端元比较；右图让每次改变参数带来的形成能变化单独可见。重画时，在含 CSV 和 `plot_alsi.py` 的目录运行 `python3 plot_alsi.py formation`，会同时写出 PNG 和 SVG。图中参考值、归一化方式和参数比较都来自 CSV，没有手工挪动能量点。

## 同一协议继续到 32³，先把五项都收齐

24³ 的对照之后，五个候选还完成了同协议的 32³ 静态计算。这里把它们接在前面的表后面读；上面的截断、展宽与 20³→24³ 结果继续保留。

[下载 24³/32³ 独立补充包](/Atlas/examples/alsi-k32-supplement-files.tar.gz)。解压得到 `alsi-k32-supplement`：包内有五对原始输入、OUT、XML、错误流与独立提取脚本，读数和重新画图无需调用 QE。它没有包含电荷密度与波函数。

先回原计算目录，确认五个 32³ 输出都在：

```text
[preston@preston-System-Product-Name alsi-formation-hull]$ ls al-fcc/k32/scf.out si-diamond/k32/scf.out alsi-b2/k32/scf.out al3si-l12/k32/scf.out alsi3-l12/k32/scf.out
al-fcc/k32/scf.out  al3si-l12/k32/scf.out  alsi-b2/k32/scf.out  alsi3-l12/k32/scf.out  si-diamond/k32/scf.out
[preston@preston-System-Product-Name alsi-formation-hull]$
```

这五项的作业号分别为 Al 844、Si 845、B2 AlSi 846、Al₃Si 847、AlSi₃ 848。每项实际使用 4 个 MPI 进程。它们仍固定各自 12³ 原型内优化得到的几何，没有在 32³ 下重新优化晶胞。

把补充包中的两份 B2 输入直接比较：

```text
[preston@preston-System-Product-Name alsi-k32-supplement]$ diff alsi-b2/k24/scf.in alsi-b2/k32/scf.in
39c39
< 24 24 24 0 0 0
---
> 32 32 32 0 0 0
[preston@preston-System-Product-Name alsi-k32-supplement]$
```

只有这一行改变。提取脚本也逐字检查其余四对输入，并从 XML 独立核对几何、元素、PBE、无自旋极化、80/640 Ry 截断、`mv` 展宽 0.005 Ry 和零网格位移。32³ 仍用各自网格的端元重新求形成能，不能继续扣除上表的 24³ 端元能量。

原运行的密度起点也有记录：B2 使用了自己优化目录中的 `tmp`，其它候选同样只复制自己的父数据。若要重跑，把补充包内的 `k32` 目录放回前面的 `alsi-formation-hull/<候选>/` 计算树，先完成对应父计算，再照这个关系准备保存目录：

```text
[preston@preston-System-Product-Name alsi-formation-hull]$ cp -a alsi-b2/tmp alsi-b2/k32/
[preston@preston-System-Product-Name alsi-formation-hull]$
```

`startingpot='file'` 会读取密度，`startingwfc='atomic+random'` 则重新生成适用于当前 k 网格的波函数；这些仍是完整电子自洽 SCF。将 `run.sh` 里的 `<qe_bin>` 改为自己的安装位置、核对赝势和父数据后再提交。补充包的 `scf.in`、OUT 和 XML 保持实跑原文，提交脚本只隐藏了机器上的 QE 安装路径。

读 B2 的实际结果，网格对应 969 个不可约点，电子循环经过 5 次迭代收敛：

```text
[preston@preston-System-Product-Name alsi-formation-hull]$ grep -n -E 'number of k points|!    total energy|convergence has been|JOB DONE' alsi-b2/k32/scf.out
116:     number of k points=   969  Marzari-Vanderbilt smearing, width (Ry)=  0.0050
193:!    total energy              =     -16.42065067 Ry
204:     convergence has been achieved in   5 iterations
274:   JOB DONE.
[preston@preston-System-Product-Name alsi-formation-hull]$
```

另一个结束较晚的候选是 AlSi₃。它的尾部完整保留了约 30 分钟的 WALL 时间与正常退出段：

```text
[preston@preston-System-Product-Name alsi-formation-hull]$ tail -n 13 alsi3-l12/k32/scf.out
     fftw         :    524.23s CPU    542.73s WALL ( 1329784 calls)
     interpolate  :      0.07s CPU      0.07s WALL (       7 calls)

     Parallel routines

     PWSCF        :  29m40.43s CPU  30m21.34s WALL


   This run was terminated on:  23:52:10  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name alsi-formation-hull]$
```

这一步只说明原生程序完成。独立提取还要求五项 XML 的 SCF 收敛标记为真、误差低于 `conv_thr=1e-10 Ry`、OUT 与 XML 的总能一致，以及末轮无本征值未收敛信息。五项本次都满足这些电子求解检查；错误文件仍要一起看：

```text
[preston@preston-System-Product-Name alsi-formation-hull]$ wc -c */k32/scf.err
1300 al-fcc/k32/scf.err
1300 al3si-l12/k32/scf.err
1300 alsi-b2/k32/scf.err
1300 alsi3-l12/k32/scf.err
1300 si-diamond/k32/scf.err
6500 total
[preston@preston-System-Product-Name alsi-formation-hull]$
```

```text
[preston@preston-System-Product-Name alsi-formation-hull]$ head -n 2 alsi-b2/k32/scf.err
Authorization required, but no authorization protocol specified

[preston@preston-System-Product-Name alsi-formation-hull]$
```

每个错误文件都有 1300 字节，内容是这台机器重复出现的环境授权提示，没有被当作空文件删掉。补充包也原样保留自动检查报告；其中的 `blocked` 来自自动输入检查器尚不支持这些起始密度与对角化字段，不能改写成自动审计通过。这里依据实际输入、完整输出和 XML 单独列明已经检查的项目。

进入解压后的补充包目录，重新提取数值：

```text
[preston@preston-System-Product-Name alsi-k32-supplement]$ python3 analyse_k32.py
case           job    E32 (Ry/cell)       formation (eV/atom)  delta24->32 (meV/atom)
al-fcc          844      -5.0397499931           0.00000000             +0.000000
al3si-l12       847     -26.5073157318           0.10905498             +1.798223
alsi-b2         846     -16.4206506696           0.26685287             +1.090635
alsi3-l12       848     -39.1923973703           0.36645097             +0.534909
si-diamond      845     -22.8402546501           0.00000000             +0.000000
Inputs differ only in k mesh: True
Finite-set hull vertices: al-fcc, si-diamond
Maximum formation-energy change: 1.798223 meV/atom
All changes within 1 meV/atom: False
Davidson-CG Al3Si difference: 1.15852021e-07 meV/atom
[preston@preston-System-Product-Name alsi-k32-supplement]$
```

[energy-k24-k32.csv](/Atlas/examples/alsi-k32-supplement/energy-k24-k32.csv) 保留十份计算的总能、压力、迭代误差和文件哈希；[comparison-k24-k32.csv](/Atlas/examples/alsi-k32-supplement/comparison-k24-k32.csv) 还把形成能变化拆成候选能量变化与参考能量变化。这一点在 B2 上很直观：候选本身的每原子总能变化很小，端元参考的变化仍会明显进入最后的形成能差。

| 候选 | 24³ / eV·atom⁻¹ | 32³ / eV·atom⁻¹ | 24³→32³ / meV·atom⁻¹ |
| --- | ---: | ---: | ---: |
| al3si-l12 | 0.107256757 | 0.109054980 | +1.798223 |
| alsi-b2 | 0.265762236 | 0.266852871 | +1.090635 |
| alsi3-l12 | 0.365916061 | 0.366450970 | +0.534909 |

最大变化为 **1.798223 meV/atom**，所以 32³ 完成后仍不能宣布通过 1 meV/atom 比较线。Al₃Si 的变化从 20³→24³ 的负值变成了 24³→32³ 的正值，说明不能按“网格更密，每次差值必然更小”来读表。32³ 的最大绝对压力为 2.37 kbar；这里仍是原优化几何上的静态结果，没有重新得到这一数值协议下的零压晶胞。

另外保留了 Al₃Si 的 [Davidson 对照](/Atlas/examples/alsi-k32-supplement/al3si-l12/k32-davidson/scf.out)，作业号 851。其初轮有 43 条本征值未收敛提示，末轮没有；最终能量与 CG 相差约 `1.16×10⁻⁷ meV/atom`。这个对照只检查同协议下的求解器一致性，形成能表仍统一使用五份 CG 结果，不能用它来替代网格比较。

在装有 NumPy、Matplotlib 的本机进入补充包目录，运行[绘图脚本](/Atlas/examples/alsi-k32-supplement/plot_k32.py)：

```bash
python3 analyse_k32.py
python3 plot_k32.py comparison
```

![AlSi 候选的 24³ 和 32³ 形成能及其差值](/Atlas/examples/alsi-k32-supplement/plots/k32-comparison.svg)

左图保留两组实际形成能，右图单独展开它们的差值；浅蓝色区域是 ±1 meV/atom 比较范围。Al₃Si 与 B2 的柱子超出这个范围，AlSi₃ 这一项位于范围内。图只反映这两档网格的差异，没有把有限差值当作已知的全部数值误差。

三个候选相对这些端元的形成能均为正。接下来把不同成分的结果放到同一张图上，查看候选相对允许分解组合的位置，见 [有限候选集凸包](/Atlas/m/convex-hull/qe/)。数值参数仍可沿 [收敛测试](/Atlas/m/convergence/qe/) 的方式继续增加，但应始终重新计算匹配的端元参考。

```text
公开晶体原型 → 原型内受约束优化 → 同协议静态能量
                                      ↓
                              按原子数归一化并减端元
                                      ↓
                                   形成能
                                      ↓
                               有限候选集凸包
```
