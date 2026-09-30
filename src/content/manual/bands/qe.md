[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 沿 Γ–X–W–K–Γ–L–X 看 Si 的能级怎样变化

这里沿用 [Si SCF](/Atlas/m/scf/qe/)的固定结构与密度，单独建立一条高对称路径。前面的均匀 [NSCF](/Atlas/m/nscf/qe/)用于 DOS 与布里渊区采样；本页不重做那套流程，而是在相同父 SCF 上求指定路径的本征值。

例子使用 QE 7.5、PBE、两个 Si 原子、无 SOC。当前坐标与原胞约定对应下面的路径；换晶胞基矢后，不能只保留这些点的标签和数字。

本例文件可[一起下载](/Atlas/examples/si-pbe-electronic-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，先完成 [Si SCF](/Atlas/m/scf/qe/)，再由本页的路径计算生成对应 k 点的能量和波函数。

对应的 [bands.err](/Atlas/examples/si-pbe-electronic/bands-cg/bands.err) 为 1604 字节，保留了重复的 `Authorization required, but no authorization protocol specified` 环境提示，以及 `IEEE_DENORMAL` 浮点非正规数提示。本轮最终输出没有未收敛本征值行，后处理读到了完整的 8 条带、121 个路径点；验收时应把这些结果与原始 stderr 一起检查。

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

## 可复制的 AI 编码提示词

将下面的需求和本页示例文件交给代码助手：

```text
编写 Si 路径能带后处理程序，使用 Python 3、NumPy 和 Matplotlib。
输入：bands-cg/si.bands.dat.gnu，空行分为 8 条带，每条 121 点。两列是累计距离（2π/a）和能量（eV）。
方法：沿用文件距离，以路径 band 4 最大值约 6.3970 eV 为零；节点 1、25、37、49、73、97、121 对应 Γ–X–W–K–Γ–L–X，按输出带号连接。
检查：8×121 点完整，各带横坐标一致，节点距离与正文一致，保留 .gnu 打印精度。
输出：源码、依赖与命令、检查摘要、PNG/SVG/PDF。纵轴标 Energy − path VBM (eV)，全区带边搜索另用均匀网格。
```

## 后处理源码与运行

完整源码：[plot_bands.py](/Atlas/examples/si-pbe-electronic/plot_bands.py) · [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

解压本页示例包后，在 `si-pbe` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 plot_bands.py
```


## 画图时明确能量零点

这张图把路径上第 4 条带的最大值设为零，即本例的 VBM；没有使用另一材料的费米能文件。下载包中的 [plot_bands.py](/Atlas/examples/si-pbe-electronic/plot_bands.py) 直接读取 `si.bands.dat.gnu`，核对 8×121 个点和每条带相同的横坐标，再统一减去 6.3970 eV。

同一 XML/胖带 CSV 中的路径价带顶是 `6.397028957255 eV`，而 `.gnu` 按四位小数输出。两者相差约 `2.90×10⁻⁵ eV`，来自文本精度，不能解释成能级移动。普通能带和胖带分别读取两种精度的数据，均以本路径价带顶为零；叠图时应统一采用同一个精确参考。

原始带能没有减去真空能级，不是跨材料可直接比较的绝对能级。此处标注 `Energy − path VBM` 比笼统写“费米能”更明确。

```bash
python3 plot_bands.py
```

![Si 路径能带，能量相对同一路径的价带顶](/Atlas/examples/si-pbe-electronic/plots/bands-direct.png)

先定位节点和 0 eV 水平线。Γ 点的三条价带顶接近简并，Γ–X 段的导带谷降到比 Γ 点导带更低的位置；只看 Γ 点的上下两条线，会漏掉这部分低能导带。交叉或简并处仍按输出带号连接，不表示已追踪同一个轨道分支。

若节点间距不符或带在节点断开，先核对文件是否仍是 8 个 121 行块、各块横坐标是否一致，再检查索引。不要靠均匀重设刻度或平移个别带来修饰图形。

能带图适合看路径上能级如何分散，不能保证路径经过全布里渊区的真实极值。直接/间接带隙的判定与采样对照见 [带隙页](/Atlas/m/band-gap/qe/)；导带谷附近的曲率见 [有效质量](/Atlas/m/effective-mass/qe/)。

## 二维金属异质结 ZrCl₂/Sc₂C：轨道投影能带、水平 PDOS 与二维费米面三联图

对于半导体 Si，能量零点取在路径价带顶（VBM）；对于金属异质结，能量零点取在自洽计算确定的费米能级 `E_F`，高对称路径上穿过 `E = E_F` 的能带分支对应倒空间中的费米面等能线。

在 **`ZrCl₂/Sc₂C`**（[双网格超导计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，计算参数为 `ecutwfc = 100 Ry`、`ecutrho = 800 Ry`、`degauss = 0.0037 Ry`，能量零点采用 `scf/pwx.out` 的 `E_F = 0.3133 eV`。绘图脚本 [`plot_zrcl2_sc2c.py`](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py) 将三组输出并排组合为三联图：
- **子图 a（`Orbital fatbands`）**：读取 `scf/bands.in` 沿二维六角布里渊区 `Γ–M–K–Γ` 路径计算的 `151` 个 k 点、`31` 条能带，以及 `scf/fatbands.projwfc_up` 中的 `45` 个正交化原子轨道（归并为 `Zr-4d` `#9–13`、`Sc-3d` `#31–35, #41–45`、`C-2p` `#15–17`、`Cl-3p` `#19–21, #23–25`），以空心圆（`facecolors='none'`，权重阈值 `w > 0.04`）叠加在能带曲线上；
- **子图 b（`PDOS`）**：与子图 a 共享垂直能量轴 `E − E_F ∈ [−2.5, 2.0] eV`，展示 `zrclscc.pdos_tot` 的灰色填充总态密度及四组轨道的水平分波态密度曲线；
- **子图 c（`2D Fermi surface`）**：由 `FS/zrclscc_fs.bxsf`（`64×64×1` k 网格、`65×65×2` BXSF 节点，`E_F = 0.3154 eV`）插值绘制二维六角第一布里渊区内穿过费米能级的 **Band 26**（蓝色）与 **Band 27**（橙红色）费米面等能线。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 异质结的轨道投影 Fatbands、水平 PDOS 与二维六角布里渊区费米面三联图" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) <code>Γ–M–K–Γ</code> 路径上的 31 条能带与 45 个正交化原子轨道归并后的空心圆轨道权重；(b) 共享 <code>E − E_F</code> 纵轴的水平总 DOS 与轨道分辨 PDOS；(c) 由 <code>zrclscc_fs.bxsf</code> 插值得到的第 26 带（蓝）与第 27 带（橙红）二维六角第一布里渊区费米面。</figcaption></figure>

沿着 `E − E_F = 0` 水平虚线横向对照：子图 a 中沿 `Γ–M` 和 `Γ–K` 穿越费米能级的第 26、27 条能带，在子图 c 的六角布里渊区中对应围绕 Γ 点的内外口袋与围绕 K 点的口袋；而费米能级附近的平缓色散段则直接对应子图 b 在 `E_F` 附近的 `Zr-4d` 与 `Sc-3d` 态密度峰。

下载本算例：[bands.in](/Atlas/examples/zrcl2-sc2c/scf/bands.in) · [pdos.in](/Atlas/examples/zrcl2-sc2c/pdos/pdos.in) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。

## 文献中的相关图件与表达方式

在凝聚态物理与计算材料学文献中，能带图常与水平态密度（DOS）、二维费米面、不同处理（如 SOC 或杂化泛函）对比曲线或超晶格折叠布里渊区配对展示：

### 1. 不含/含 SOC 的能带与水平总 DOS 及费米速度着色的二维费米面

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Bands_DOS_FS_MoW_Bekaert2020_Fig2.jpg" alt="Mo₂C、Mo₂N、W₂C、W₂N 在不含 SOC 与含 SOC 下的能带、水平总 DOS 与费米速度着色二维六角费米面对比" loading="lazy"/><figcaption>二维过渡金属碳/氮化物（<code>Mo₂C, Mo₂N, W₂C, W₂N</code>）在费米能级附近窄窗口 <code>[−1, 1] eV</code> 内的能带与水平总 DOS 对比（红色虚线为不含 SOC，蓝色实线与浅蓝阴影填充为含 SOC），右侧配对展示按费米速度 <code>v_F(k)</code> 着色的二维六角布里渊区费米面。图片来源：Bekaert et al., <em>Nanoscale</em> <strong>12</strong>, 17354 (2020), Fig. 2，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

- **读图与作图要点**：将能量纵轴聚焦在 `E − E_F ∈ [−1, 1] eV` 的近费米窗口，在同一坐标系内用红色虚线（不含 SOC）与蓝色实线加浅蓝阴影（含 SOC）直接对比自旋轨道耦合引起的能带劈裂与总 DOS 变化，并在右侧列出按费米速度 `v_F(k)` 着色的二维六角费米面。

### 2. GGA-PBE 与 HSE06 泛函下两种材料能带的上下行与双色线型对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_PBE_vs_HSE06_Bands_DOS_HfX2_Santos2025_Fig4.jpg" alt="HfBr₂ 与 HfI₂ 在 GGA-PBE（上行）与 HSE06（下行）下的能带结构及直接/间接光学跃迁箭头标注" loading="lazy"/><figcaption>上行子图为 GGA-PBE 能带，下行子图为 HSE06 杂化泛函能带；每个子图内以红色实线表示 <code>HfBr₂</code>、蓝色点线表示 <code>HfI₂</code>，并用竖直与倾斜箭头标出直接与间接光学跃迁路径。图片来源：Santos et al., <em>J. Appl. Phys.</em> <strong>138</strong>, 104302 (2025), Fig. 4，<a href="https://doi.org/10.1063/5.0286460" target="_blank" rel="noopener noreferrer">DOI: 10.1063/5.0286460</a>。</figcaption></figure>

- **读图与作图要点**：当需要同时比较两种泛函（上行 GGA-PBE、下行 HSE06）和两种同构化合物（红色实线 `HfBr₂`、蓝色点线 `HfI₂`）时，固定相同的能量参考与高对称路径，并用竖直箭头和斜箭头分别标出直接跃迁与间接跃迁极值点，便于横向比较化学取代效应、纵向比较杂化泛函对带隙的修正。

### 3. 转角莫尔超晶格的微布里渊区折叠与窄平带色散

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_MoireFolding_MiniBands_TBG_Wu2018_Fig1.jpg" alt="转角双层石墨烯的莫尔布里渊区折叠示意图与费米面附近窄平带微带色散" loading="lazy"/><figcaption>倒空间莫尔微布里渊区（Mini Brillouin Zone）几何关系图与费米能级附近窄能量窗口内的微带（Minibands）色散。图片来源：Wu et al., <em>Phys. Rev. Lett.</em> <strong>121</strong>, 257001 (2018), Fig. 1，<a href="https://doi.org/10.1103/PhysRevLett.121.257001" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevLett.121.257001</a>。</figcaption></figure>

- **读图与作图要点**：对于超胞或转角莫尔体系，在能带图旁给出原胞布里渊区与超胞微布里渊区的几何折叠示意图（标明 `K_+`、`K_-`、`Γ_M`、`M_M`），并将能量纵轴放大到平带所在的窄能量窗口。

下一步：需要 s/p 成分时进入 [逐 k 胖带](/Atlas/m/fatband/qe/)，保留本页的相同 k 点与带号；需要态数分布时进入 [DOS](/Atlas/m/dos/qe/)，读取均匀网格分支。

```text
同一 SCF 密度 → 路径 bands → bands.x → 原始 eV 数据 → 统一能量零点
                              └─ projwfc.x → 逐k逐带投影
均匀 NSCF ──────────────────────────────→ DOS
```
