[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 沿 Γ–X–W–K–Γ–L–X 看 Si 的能级怎样变化

这里沿用 [Si SCF](/Atlas/m/scf/qe/)的固定结构与密度，单独建立一条高对称路径。前面的均匀 [NSCF](/Atlas/m/nscf/qe/)用于 DOS 与布里渊区采样；本页不重做那套流程，而是在相同父 SCF 上求指定路径的本征值。

例子使用 QE 7.5、PBE、两个 Si 原子、无 SOC。当前坐标与原胞约定对应下面的路径；换晶胞基矢后，不能只保留这些点的标签和数字。

本例文件可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，先完成 [Si SCF](/Atlas/m/scf/qe/)，再由本页的路径计算生成对应 k 点的能量和波函数。

对应的 [bands.err](/Atlas/examples/si-pbe/bands-cg/bands.err) 为 1604 字节，保留了重复的 `Authorization required, but no authorization protocol specified` 环境提示，以及 `IEEE_DENORMAL` 浮点非正规数提示。本轮最终输出没有未收敛本征值行，后处理读到了完整的 8 条带、121 个路径点；验收时应把这些结果与原始 stderr 一起检查。

## 输入中的四列分别是什么

先把 `scf/tmp` 复制到独立的 `bands-cg` 目录，用 `vi bands.in` 编辑。本次实际输入完整列在下面：

```text
[preston@preston-System-Product-Name bands-cg]$ cat bands.in
&CONTROL
  calculation = 'bands'
  verbosity = 'high'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nbnd = 8
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  diagonalization = 'cg'
  diago_cg_maxiter = 200
  diago_thr_init = 1.0d-10
  conv_thr = 1.0d-10
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS tpiba_b
7
0.0 0.0 0.0 24
1.0 0.0 0.0 12
1.0 0.5 0.0 12
0.75 0.75 0.0 24
0.0 0.0 0.0 24
0.5 0.5 0.5 24
1.0 0.0 0.0 1
```
`tpiba_b` 的前三列是以 2π/a 为单位的笛卡尔 k 坐标，第四列控制到下一个节点的路径采样。7 行是 7 个节点，程序展开后得到 121 个实际 k 点，不是只算 7 个点。`nbnd=8` 保留 4 条占据带与 4 条空带。这里各段的 12 或 24 控制曲线的取点密度；增加它们可以细看交叉和弯曲，却没有增加路径以外的采样，也没有更新父 SCF 密度。需要找全区带边时，应接后面的均匀网格与局部加密对照。

本例使用 CG 复算后未再出现本征值未收敛提示的结果；此前带有该提示的一轮保留在其他目录。求解器的选择与输出核对见 [NSCF 页](/Atlas/m/nscf/qe/)，图源没有沿用那一轮警告数据。

```text
[preston@preston-System-Product-Name bands-cg]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-cg
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in bands.in > bands.out 2> bands.err
```
提交使用 `sbatch run.sh`，运行时用 `tail -f bands.out` 查看当前点。结束后，除了队列状态，还要读 `bands.err`，检查 121 个点、8 条能带、未收敛本征值警告与正常收尾。

## bands.x 整理刚才的路径结果

`pw.x` 完成路径本征值求解后，`bands.x` 才读取同一份 `prefix/outdir` 并导出作图文件：

```text
[preston@preston-System-Product-Name bands-cg]$ cat bands-post.in
&BANDS
  prefix = 'si'
  outdir = './tmp'
  filband = 'si.bands.dat'
  lsym = .false.
/
```
`lsym=.false.` 在本例中不做不可约表示分类；默认 `no_overlap=.true.` 也没有启用相邻点重叠最大化排序。因此图上的连接按输出带序绘制，在简并与交叉处不要据此断言某条线始终保持同一种轨道身份。需要轨道身份时，继续读取同路径的 [胖带](/Atlas/m/fatband/qe/)。

```bash
<qe_bin>/bands.x -in bands-post.in > bands-post.out 2> bands-post.err
```

```text
     Reading collected, re-writing distributed wavefunctions
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   0.0000
     high-symmetry point:  1.0000 0.0000 0.0000   x coordinate   1.0000
     high-symmetry point:  1.0000 0.5000 0.0000   x coordinate   1.5000
     high-symmetry point:  0.7500 0.7500 0.0000   x coordinate   1.8536
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   2.9142
     high-symmetry point:  0.5000 0.5000 0.5000   x coordinate   3.7802
     high-symmetry point:  1.0000 0.0000 0.0000   x coordinate   4.6463

     Plottable bands (eV) written to file si.bands.dat.gnu
     Bands written to file si.bands.dat

     BANDS        :      1.02s CPU      1.11s WALL


   This run was terminated on:  22: 2:52  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
`si.bands.dat` 有一个 `&plot` 表头，后面按 k 坐标与能量分组；`.gnu` 则按能带分块，每块两列，块间空行。先看两种文件的开头：

```text
[preston@preston-System-Product-Name bands-cg]$ head -n 6 si.bands.dat
 &plot nbnd=   8, nks=   121 /
            0.000000  0.000000  0.000000
   -5.692    6.397    6.397    6.397    8.967    8.967    8.967    9.969
            0.041667  0.000000  0.000000
   -5.685    6.347    6.363    6.363    8.947    9.010    9.010   10.018
            0.083333  0.000000  0.000000
```

```text
[preston@preston-System-Product-Name bands-cg]$ head -n 6 si.bands.dat.gnu
    0.0000   -5.6925
    0.0417   -5.6848
    0.0833   -5.6616
    0.1250   -5.6231
    0.1667   -5.5691
    0.2083   -5.4998
```
`.gnu` 第一列是沿路径累计的距离，第二列已经是 eV。不能把每一行当作不同能带，也不能再次把能量乘 Ry→eV 的换算常数。

这里的横轴不是“第几个 k 点”。脚本从实际坐标计算 `sᵢ = Σⱼ |kⱼ₊₁−kⱼ|`，路径每段按长度连接；在这个 `tpiba` 约定下，s 的单位为 `2π/a`。本例 `a=5.397607551 Å`，乘以 `2π/a≈1.16406857 Å⁻¹` 可转换为物理倒空间长度。若直接把 121 个点等距编号，不同路径段就会被拉伸到错误的相对长度。

| 节点 | 1 起始的实际 k 点编号 | 笛卡尔坐标（2π/a） | 累计距离（2π/a） |
| --- | ---: | --- | ---: |
| Γ | 1 | (0, 0, 0) | 0.000000 |
| X | 25 | (1, 0, 0) | 1.000000 |
| W | 37 | (1, 0.5, 0) | 1.500000 |
| K | 49 | (0.75, 0.75, 0) | 1.853553 |
| Γ | 73 | (0, 0, 0) | 2.914214 |
| L | 97 | (0.5, 0.5, 0.5) | 3.780239 |
| X | 121 | (1, 0, 0) | 4.646264 |

索引由真实 121 点展开得到，与 `bands-post.out` 的七个位置一致。两个 Γ 在倒空间是同一点，却在累计路径的不同位置。表中坐标只适用于本页的 FCC 基矢约定，不能连同标签移植到另一种晶胞。

## 画图时明确能量零点

这张图把路径上第 4 条带的最大值设为零，即本例的 VBM；没有使用另一材料的费米能文件。下载包中的 `plot_bands.py` 直接读取 `si.bands.dat.gnu`，核对 8×121 个点和每条带相同的横坐标，再统一减去 6.3970 eV。

同一 XML/胖带 CSV 中的路径价带顶是 `6.397028957255 eV`，而 `.gnu` 按四位小数输出。两者相差约 `2.90×10⁻⁵ eV`，来自文本精度，不能解释成能级移动。普通能带和胖带分别读取两种精度的数据，均以本路径价带顶为零；叠图时应统一采用同一个精确参考。

原始带能没有减去真空能级，不是跨材料可直接比较的绝对能级。此处标注 `Energy − path VBM` 比笼统写“费米能”更明确。

```bash
python3 plot_bands.py
```

![Si 路径能带，能量相对同一路径的价带顶](/Atlas/examples/si-pbe/plots/bands-direct.png)

先定位节点和 0 eV 水平线。Γ 点的三条价带顶接近简并，Γ–X 段的导带谷降到比 Γ 点导带更低的位置；只看 Γ 点的上下两条线，会漏掉这部分低能导带。交叉或简并处仍按输出带号连接，不表示已追踪同一个轨道分支。

若节点间距不符或带在节点断开，先核对文件是否仍是 8 个 121 行块、各块横坐标是否一致，再检查索引。不要靠均匀重设刻度或平移个别带来修饰图形。

能带图适合看路径上能级如何分散，不能保证路径经过全布里渊区的真实极值。直接/间接带隙的判定与采样对照见 [带隙页](/Atlas/m/band-gap/qe/)；导带谷附近的曲率见 [有效质量](/Atlas/m/effective-mass/qe/)。

## 二维金属异质结 ZrCl₂/Sc₂C：能带色散、水平 PDOS 与二维费米面的三联耦合后处理

对于半导体 Si，能量零点取在路径价带顶（VBM）；而对于金属或超导异质结，能量零点必须取在统一自洽或更密 NSCF 网格确定的费米能级 `E_F`，并且高对称路径上穿过 `E = E_F` 的能带分支会直接在倒空间切出费米面口袋。

在 **`ZrCl₂/Sc₂C`**（[双网格超导计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，从 `scf/bands.in`（沿二维六角布里渊区 `Γ–M–K–Γ` 共 151 个 k 点）和 `pdos/pdos.in` 提取 `E_F = 2.7525 eV` 附近的电子结构时，我们将**轨道投影能带（Fatbands）**、**共享能量纵轴 `E − E_F` 的水平分波态密度（PDOS）**以及**第一布里渊区二维费米面（Band 26 与 Band 27）**排成紧凑的横排三联图：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 异质结的轨道投影 Fatbands、水平 PDOS 与二维六角布里渊区费米面拓扑" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的能带–PDOS–费米面三联耦合后处理：（左）Γ–M–K–Γ 能带色散与轨道权重散点；（中）共享 E − E_F 纵轴的水平轨道分辨 PDOS；（右）穿过费米能级的第 26 带（深蓝）与第 27 带（锈红）在二维六角第一布里渊区中的费米面等能线。</figcaption></figure>

这种三联排版让读者沿着 `E − E_F = 0` 水平虚线一眼看清：左图沿 `Γ–M` 和 `Γ–K` 两次穿越费米能级的第 26、27 条色散曲线，在右图六角布里渊区中恰好对应围绕 Γ 点的同心双口袋与围绕 K 点的三角形口袋；而 `Γ–M` 段紧贴费米能级下方的平坦鞍点带，则直接形成中图 `E − E_F ≈ −0.08 eV` 处的尖锐 PDOS 峰值。

下载本算例：[bands.in](/Atlas/examples/zrcl2-sc2c/scf/bands.in) · [pdos.in](/Atlas/examples/zrcl2-sc2c/pdos/pdos.in) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。

## 文献能带结构后处理审美解析（附 DOI 溯源）

在凝聚态物理与计算材料学文献中，孤立的一维黑白能带图已逐渐被**能带 + 水平 DOS + 费米面联立图**、**双泛函叠绘能带**或**莫尔超晶格折叠能带**所取代。下面引入三幅代表性文献原图（均附原始 DOI 号）解析其视觉范式：

### 1. 能带色散 + 水平投影 DOS + 布里渊区费米面黄金三联图

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Bands_DOS_FS_MoW_Bekaert2020_Fig2.jpg" alt="二维超导体系的轨道着色能带、共享能量轴水平 PDOS 与二维六角布里渊区费米面联立图" loading="lazy"/><figcaption>文献案例 1：左面板绘制高对称路径能带（彩色散点标注不同原子/轨道成分），中面板共享能量纵轴绘制水平 PDOS，右面板展示多能带构成的二维六角布里渊区费米面拓扑。图片来源：Bekaert et al., <em>Nanoscale</em> <strong>12</strong>, 17360 (2020)，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

- **审美与后处理要点**：能带与水平 DOS 面板之间压缩间距（`wspace ≈ 0.06`）并隐藏中面板的 Y 轴标签，使 `E − E_F = 0` 水平参考线贯穿左右两图，实现动量空间色散与能量空间态密度的无缝对准。

### 2. PBE 与 HSE06 杂化泛函的双色实虚线同轴叠绘对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_PBE_vs_HSE06_Bands_DOS_HfX2_Santos2025_Fig4.jpg" alt="半导体体系在 PBE 与 HSE06 杂化泛函下的能带与态密度同轴叠绘对比" loading="lazy"/><figcaption>文献案例 2：将 GGA-PBE（虚线）与 HSE06 杂化泛函（实线）计算的能带结构统一对齐在价带顶（VBM = 0 eV）同框叠绘，直观展示导带底（CBM）的上移（剪刀算符效应）与色散曲率变化。图片来源：Santos et al., <em>J. Appl. Phys.</em> (2025)，<a href="https://doi.org/10.1063/5.0286460" target="_blank" rel="noopener noreferrer">DOI: 10.1063/5.0286460</a>。</figcaption></figure>

- **审美与后处理要点**：比较两种泛函（或含/不含 SOC）时，避免并排画两张几乎相同的独立子图；将两套能带对齐在共同的 VBM = 0 eV 并用**实线 + 虚线（配合高对比双色）**叠绘在同一坐标轴上，能一眼看清带隙打开幅度以及谷简并是否改变。

### 3. 大尺度超胞/转角莫尔体系的布里渊区折叠与微带（Minibands）聚焦

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_MoireFolding_MiniBands_TBG_Wu2018_Fig1.jpg" alt="转角双层石墨烯的莫尔布里渊区折叠示意图与费米面附近窄平带微带色散" loading="lazy"/><figcaption>文献案例 3：结合倒空间莫尔微布里渊区（Mini Brillouin Zone）几何嵌套图与费米能级附近窄能量窗口（±50 meV）的微带色散。图片来源：Wu et al., <em>Phys. Rev. Lett.</em> <strong>121</strong>, 257001 (2018)，<a href="https://doi.org/10.1103/PhysRevLett.121.257001" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevLett.121.257001</a>。</figcaption></figure>

- **审美与后处理要点**：对于超胞或转角体系，必须在能带图旁附上原胞布里渊区与超胞微布里渊区的几何折叠关系图（明确标注 `K_+`、`K_-`、`Γ_M`、`M_M`），并将纵轴聚焦在平带所在的 meV 量级窗口。

下一步：需要 s/p 成分时进入 [逐 k 胖带](/Atlas/m/fatband/qe/)，保留本页的相同 k 点与带号；需要态数分布时进入 [DOS](/Atlas/m/dos/qe/)，读取均匀网格分支。

```text
同一 SCF 密度 → 路径 bands → bands.x → 原始 eV 数据 → 统一能量零点
                              └─ projwfc.x → 逐k逐带投影
均匀 NSCF ──────────────────────────────→ DOS
```
