# QE 能带（bands + bands.x）：沿高对称路径出一套色散

**参考**：[INPUT_PW 文档](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [INPUT_BANDS 文档](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html)

本页目标：在已收敛 scf 的基础上，沿高对称 k 路径非自洽解本征值，再用 bands.x 提取成可绘图数据。案例延续 scf 页的应变扫描体系（ZrCl2/Sc2C，nat=6）。

## 输入文件：bands.in（增量式）

bands.in 与同目录 pwx.in 的唯一差别是 `calculation = 'bands'`——结构块、截断、赝势、smearing 全部照抄 scf，保持参数一致是应变间可比的前提。结构块省略，写法如下：

```fortran
&CONTROL
  calculation = 'bands'          ! 与 scf 唯一的实质区别
  outdir = '<outdir>'
  prefix = '<prefix>'
  pseudo_dir = '<赝势库路径>'
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0,  nat = 6,  ntyp = 4,
  ecutwfc = 100,  ecutrho = 800,
  input_dft = 'vdw-DF3-opt1'
  occupations = 'smearing',  smearing = 'gaussian',  degauss = 3.7d-3
/
&ELECTRONS
  conv_thr = 1.0000000000d-12
  mixing_beta = 4.0000000000d-01
/
ATOMIC_SPECIES
（与 scf 相同）
CELL_PARAMETERS (angstrom)
（与 scf 相同；应变目录里换成该目录弛豫后的值）
ATOMIC_POSITIONS (crystal)
（与 scf 相同）
K_POINTS {crystal_b}
 4
   0.0000000000   0.0000000000   0.0000000000 50    !G
   0.5000000000   0.0000000000   0.0000000000 50    !M
   0.3333333333   0.3333333333   0.0000000000 50    !K
   0.0000000000   0.0000000000   0.0000000000  1    !G
```

路径卡怎么定：`{crystal_b}` 用倒格子分数坐标给顶点，每行末尾的整数是该段插的点数。六角体系标准走法 G–M–K–G：M=(1/2,0,0)、K=(1/3,1/3,0)，最后一段回到 Γ 只给 1 个点（终点不重复加密）。改体系先核对这些分数坐标。

## 输入文件：bandspp.in

```fortran
&BANDS
  filband = 'bands.dat'
  outdir = '<outdir>'
  prefix = '<prefix>'
/
```

## 命令主线

```bash
pw.x < bands.in > bands.out 2>&1
bands.x < bandspp.in > bandspp.out 2>&1
```

批次场景下这条链逐应变目录执行，前一步 `JOB DONE` 验收通过才进下一步（编队脚本不在此展开）。

## 判读三件套

```bash
grep "JOB DONE" bands.out
grep "the Fermi energy is" pwx.out | tail -1
awk '{print $(NF-1)}' <(grep "the Fermi energy is" pwx.out | tail -1)
```

真实输出（节选）：

```text
     the Fermi energy is    -0.3426 ev
```

判据：bands.out 有 `JOB DONE.`；E_F 取 scf 输出**最后一次**出现的值（金属体系迭代中 E_F 会动，`tail -1` 才是收敛值）；产物 `bands.dat.gnu` 非空——bands.x 静默失败偶有发生，空文件就是没跑完。

## 事故：relax 输出差异导致批量提取中断

真实发生过的事故：批量准备脚本从各目录 `rx.out` 抽取最新晶格和坐标，跑到某目录直接退出「提取结构失败」。定位两步：

```bash
grep -E "calculation|CELL_PARAMETERS|ATOMIC_POSITIONS" compress/001/rx/rx.in
```

```text
calculation = 'relax'
CELL_PARAMETERS (angstrom)
ATOMIC_POSITIONS (crystal)
```

根因：提取器同时等 `CELL_PARAMETERS` 和 `ATOMIC_POSITIONS`，而这批目录是固定晶格弛豫（`calculation = 'relax'`）——输出里**只更新** `ATOMIC_POSITIONS`，不会重新打印 `CELL_PARAMETERS`；只有 `vc-relax` 才会输出晶格块。修复：按弛豫类型分流提取，relax 目录晶格沿用输入原值。教训通用化：动弛豫输出前，先 grep 一下 calculation 是什么。

## 产物与作图

`bands.x` 生成 `bands.dat.gnu`（gnuplot/Python 可直接读的网格数据）与 `bands.dat.rap`；作图能量轴整体平移 −E_F。跨应变对比时检查三件事：k 路径与参数一致（否则差异全是假阳性）、E_F 取自本应变自己的 scf、dat 文件非空。

## 思考

1. 为什么 bands 步可以不重跑 scf 的电荷密度，而 dos 步常常要另跑一套稠密网格？
2. 路径卡最后一段回到 Γ 只给 1 个点，若给 50 个会发生什么？
3. 固定晶格弛豫的体系，批量脚本该从哪里拿晶格？
