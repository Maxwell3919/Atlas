[dos.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_DOS.html) · [projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 在能量轴上数状态，先用均匀 k 网格

这里接 [Si 的 24³ NSCF](/Atlas/m/nscf/qe/)。那一页已经保留 8 条能带并检查本征值求解；`dos.x` 在这些带能量上做布里渊区加权，不再求一份新的电荷密度。高对称路径的点分布服务于画线，不能代替这里的均匀采样。

本例文件可[一起下载](/Atlas/examples/si-pbe-electronic-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，先完成 [24³ NSCF](/Atlas/m/nscf/qe/)，再把这份保存数据复制到本页的 `dos-cg` 目录。

## 让 dos.x 读取正确的那份保存数据

本次从已检查的 `gap24-cg/tmp` 复制到 `dos-cg/tmp`，后处理有自己的目录。用 `vi dos.in` 保存下列实际输入：

```text
[preston@preston-System-Product-Name dos-cg]$ cat dos.in
&DOS
  prefix = 'si'
  outdir = './tmp'
  fildos = 'si.dos.dat'
  Emin = -8.0
  Emax = 16.0
  DeltaE = 0.02
  ngauss = 0
  degauss = 0.01
/
```
`Emin/Emax/DeltaE` 使用 **eV**，而 `degauss` 使用 **Ry**。这里 0.01 Ry 约为 0.1361 eV，不能把它读成 0.01 eV。`ngauss=0` 选择普通 Gaussian 展宽；能量轴上采样更密只会让曲线绘得更细，并没有增加电子 k 点。

`DeltaE=0.02 eV` 比这次的展宽小，用来在能量轴上取足够细的绘图点；曲线看起来平滑，不等于能分辨 0.02 eV 的细节。减小 `degauss` 后，原先被抹平的细节和 k 采样造成的锯齿都可能出现，需要配合更密的 NSCF 网格比较。`Emin=-8`、`Emax=16` 只规定本次输出能窗；若想分析更高能量，先核对 8 条带是否已经覆盖，而不是只扩大这两个数。

`dos.x` 根据保存的带能量和权重计算总 DOS，本身不需要再读取所有波函数。需要轨道投影时，`projwfc.x` 才沿另一条依赖读取相应波函数，见 [布居与投影](/Atlas/m/population-analysis/qe/)。

```text
[preston@preston-System-Product-Name dos-cg]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-dos
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/dos.x -in dos.in > dos.out 2> dos.err
```
这份短后处理仍以 Slurm 脚本运行，`sbatch run.sh` 提交后，先读 `dos.out` 和 `dos.err`，确认保存目录、交换关联设置和展宽都与预期对应。本次输出中的这几段是：

```text
     Reading xml data from directory:

     ./tmp/si.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want
```

```text
     Gaussian broadening (read from input): ngauss,degauss=   0    0.010000


     DOS          :      0.70s CPU      0.73s WALL


   This run was terminated on:  22: 2:58  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
本次实际 WALL 时间为 0.73 s。[dos.err](/Atlas/examples/si-pbe-electronic/dos-cg/dos.err) 为 1300 字节，包含重复的 `Authorization required, but no authorization protocol specified` 环境提示；原始文件随结果保留。本轮已写出完整 DOS 表，输出未见致命错误。`JOB DONE.` 表明这一步执行完毕；图的可靠范围仍取决于 NSCF 的空带数、k 网格与后处理展宽。

## 数据文件的第三列不是“又一条 DOS”

```text
[preston@preston-System-Product-Name dos-cg]$ head -n 6 si.dos.dat
#  E (eV)   dos(E)     Int dos(E) EFermi =    6.397 eV
  -8.000  0.9182E-85  0.1836E-86
  -7.980  0.9182E-85  0.3673E-86
  -7.960  0.9182E-85  0.5509E-86
  -7.940  0.9182E-85  0.7345E-86
  -7.920  0.9182E-85  0.9182E-86
```
三列依次为能量 eV、总 DOS（states/eV/cell）和累计态数。这里是非自旋极化体系，总 DOS 已计入自旋简并；不要再额外乘 2。

这里的 cell 是输入中的两原子 Si 原胞。若报告每原子 DOS，曲线与累计态数都除以 2，纵轴同步改成 `states/eV/atom`。换超胞后不归一化，量级会随胞内态数变化，不能据此判断电子态增多。

第三列从文件下限累计态数。在占据区上方、导带开始之前的平台，可结合 8 个价电子检查归一化；高能端继续增长，是因为开始累计空态。共线自旋极化 `nspin=2` 则有 `E、DOSup、DOSdw、Int DOS` 四列，总 DOS 为 up+down；将 down 镜像到负侧只是显示约定，求和不能使用镜像后的负数。SOC/非共线输出需按自己的表头解析，本例脚本限定非自旋三列格式。

开头的 DOS 约 10⁻⁸⁵，位于本次能带范围以外。这个小数不能单独被命名为某种物理“下限”；应结合采样能区、有限展宽与程序的数值处理来读。再看文件末尾：

```text
[preston@preston-System-Product-Name dos-cg]$ tail -n 4 si.dos.dat
  15.940  0.2460E-01  0.1597E+02
  15.960  0.2901E-01  0.1597E+02
  15.980  0.3403E-01  0.1597E+02
  16.000  0.3945E-01  0.1597E+02
```
积分到 16 eV 时约为 15.97 个态，接近 8 条带乘自旋简并的 16；它包含空态，因此不是应当等于整胞 8 个电子的电子数验收。有限能窗也可能漏掉高能端的部分带和展宽尾部。

独立对打印数据做梯形积分得到 `15.97326485`，与第三列末尾 `15.97` 在打印精度内相符。用同一 `gap24-cg` 的价带顶 `6.397028955497 eV` 和采样导带底 `6.937158523640 eV` 定位带隙中点，读取累计列得到 `8.0000`。

在价带顶本身，累计列约为 `7.997`：Gaussian 展宽将部分边缘谱重带到了价带顶以上。不能为了让该端点等于整数而重新缩放曲线。`degauss` 是 QE 的展宽参数，不是能量步长、仪器分辨率或真实温度。

## 可复制的 AI 编码提示词

将下面的需求和本页示例文件交给代码助手：

```text
编写 Si 总 DOS 后处理程序，使用 Python 3、NumPy 和 Matplotlib。
输入：dos-cg/si.dos.dat 三列为能量（eV）、DOS（states/eV/cell）、累计态数（states/cell）；Gaussian degauss=0.01 Ry。零点取 gap-results.json 的 gap24-cg VBM=6.397028955497 eV。
方法：平移能量轴，保留原始 DOS 和 Gaussian 尾部；本例非自旋总 DOS 已含简并。
检查：1201 个严格递增点、间隔约 0.02 eV、有限值；梯形积分约 15.9733，与累计末值 15.97 在打印精度内相符，带隙中点累计态数约 8。
输出：源码、依赖、命令、摘要、PNG/SVG/PDF；坐标为 E−VBM (eV)、DOS (states/eV/cell)，显示 −13…8 eV。精确带边取本征值，DOS 用于态数分布。
```

## 后处理源码与运行

完整源码：[plot_si.py](/Atlas/examples/si-pbe-electronic/plot_si.py) · [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

解压本页示例包后，在 `si-pbe` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 plot_si.py dos
```


## 从原始能量转到相对价带顶的图

在解包后的 `si-pbe` 目录运行：

完整绘图源码见 [plot_si.py](/Atlas/examples/si-pbe-electronic/plot_si.py) 与同目录 [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)，原始输入表见 [si.dos.dat](/Atlas/examples/si-pbe-electronic/dos-cg/si.dos.dat)。重画需要 Python 3、NumPy 和 Matplotlib。
```bash
python3 plot_si.py dos
```

![Si 的总态密度，能量相对同一 24³ NSCF 的价带顶](/Atlas/examples/si-pbe-electronic/plots/dos.png)


Gaussian 展宽会把带边附近的权重扩展到相邻能量，不能从这一张有展宽的图上量出高精度带隙。带边位置与采样依赖回到 [带隙页](/Atlas/m/band-gap/qe/)核对；DOS 峰形需要另做 k 网格与展宽的交叉比较。

图上 0 eV 是同一父链的价带顶，正能侧的 Gaussian 尾巴不能单独判为金属性。比较峰位和峰高前，先固定每原胞/每原子的归一化、能量参考和展宽。

区分 s/p 可读已有[布居页](/Atlas/m/population-analysis/qe/)的均匀 18³ 分支。它与本页 24³ DOS 的网格不同；下面只核对该 18³ 分支内部的关系，不把它逐行扣到 24³ 曲线上。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 4 population-cg/si.pdos_tot
# E (eV)  dos(E)    pdos(E)
  -6.101  0.475E-06  0.473E-06
  -6.081  0.120E-05  0.119E-05
  -6.061  0.291E-05  0.290E-05
[preston@preston-System-Product-Name si-pbe]$ head -n 4 'population-cg/si.pdos_atm#1(Si)_wfc#2(p)'
# E (eV)   ldos(E)   pdos(E)    pdos(E)    pdos(E)   
  -6.101  0.394E-08  0.131E-08  0.131E-08  0.131E-08
  -6.081  0.104E-07  0.347E-08  0.347E-08  0.347E-08
  -6.061  0.265E-07  0.883E-08  0.883E-08  0.883E-08
```

`si.pdos_tot` 第二列是该分支总 DOS，第三列是所有投影态的 PDOS 和，不能将两列相加。p 文件第二列 `ldos` 已是三个 p 分量之和，后三列依次 `pz、px、py`；加完后三列再加第二列，会把 p 权重数两次。s 文件的 ldos 与唯一 s 分量同样重复表示同一壳层。

整胞投影和应取两个原子的 s 文件各一份 ldos，加上两个原子的 p 文件各一份 ldos，对应 `si.pdos_tot` 第三列。有限投影空间未覆盖的部分保留下来，不能强行放大 PDOS 去等于总 DOS。本例文本只保留有限有效位数，逐行求和最大差 `0.006 states/eV/cell`，全部在各列舍入界内；不能把这点打印差当成额外丢失的物理态。

共线自旋极化时，`pdos_tot` 变为 `E、DOSup、DOSdw、PDOSup、PDOSdw`；原子文件也分别给 up/down 的 ldos 和 m 分量。按同一自旋、同一能量点求和后，再合并通道。本例非磁数据已含自旋简并，不再乘 2。

## 二维异质结 ZrCl₂/Sc₂C：轨道分辨 PDOS 与能带、二维费米面的共享能量轴对准

在多元素金属异质结中，除总态密度外，常通过 `projwfc.x` 生成按原子和角动量拆解的分波态密度（PDOS）。在 **`ZrCl₂/Sc₂C`**（[完整计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，子图 **b**（`PDOS`）以 `scf/pwx.out` 的 `E_F = 0.3133 eV` 为能量零点，绘制 `zrclscc.pdos_tot` 的灰色填充总 DOS 以及 `Zr-4d`、`Sc-3d`、`C-2p`、`Cl-3p` 四组投影态密度曲线，与左侧子图 **a** 的轨道投影能带共享纵轴 `E − E_F ∈ [−2.5, 2.0] eV`；右侧子图 **c** 则展示由 `zrclscc_fs.bxsf` 插值得到的第 26、27 带二维六角布里渊区费米面：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 的轨道投影能带、共享能量纵轴的水平分波态密度 PDOS 与二维六角费米面" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) 轨道投影能带；(b) 与能带共享 <code>E − E_F</code> 纵轴的水平总 DOS（<code>zrclscc.pdos_tot</code> 灰色填充）及 <code>Zr-4d</code>、<code>Sc-3d</code>、<code>C-2p</code>、<code>Cl-3p</code> 分波态密度；左图投影权重已按实际 <code>scf/fatbands.projwfc_up</code> 中每态头的原子号和角动量逐态求和核对；曲线原子映射：Zr-4d[#1]、Sc-3d[#5+#6]、C-2p[#2]、Cl-3p[#3+#4]；(c) 由 <code>zrclscc_fs.bxsf</code> 提取的第 26、27 带二维六角费米面。</figcaption></figure>

<figure class="research-figure">
<img src="/Atlas/examples/zrcl2-sc2c/site-index-map.svg" alt="QE 7.1 ZrCl2/Sc2C atom sites by fractional z, with atom indices grouped into orbital curves" loading="lazy"/>
<figcaption>QE 7.1 ZrCl2/Sc2C site mapping. Layer labels and fractional z values follow the scf/pwx.in crystal coordinates; horizontal spacing is schematic.</figcaption>
</figure>

通过共享能量纵轴，便于将子图 b 中费米能级附近的态密度峰与子图 a 中平缓的 `Zr-4d` / `Sc-3d` 能带色散对应起来。在[双网格电声计算](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)的 `lambdax.emax18.out` 中，`σ = 0.003 Ry` 处由双高斯展宽计算的费米面态密度 `N_σ(E_F)` 在 `ph64`（`64²`）与 `ph96`（`96²`）网格下分别为 `30.598` 与 `30.772 states/spin/Ry/cell`（完整 `N_σ(E_F)` 随展宽 `σ` 的变化曲线见 [`zrcl2-sc2c-k64-k96-moments.png`](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-k64-k96-moments.png) 的子图 a）。

### 冻结几何对照：异质结与孤立 Sc₂C 的 PDOS

这组控制计算在 0% 与 +1.5% 两种应变设置下，分别比较异质结中的 Sc₂C 层、ZrCl₂ 层与孤立 Sc₂C。所有坐标均保持冻结，因此它们不代表弛豫平衡结构。图中每条谱都以各自计算的费米能级为零点；这种分别对齐可以比较费米能级附近的谱形和权重，不能据此判断绝对能带偏移或电荷转移。

<figure class="research-figure"><img src="/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos.png" alt="0% 与 +1.5% 设置下，异质结 Sc₂C 层、ZrCl₂ 层以及冻结孤立 Sc₂C 的费米能级附近投影态密度对照" loading="lazy"/>
<figcaption>冻结坐标下的投影态密度，能量窗为各自费米能级附近 −2 至 +2 eV。左、右面板分别为 0% 与 +1.5%；实线为异质结中的 Sc₂C 层，虚线为孤立 Sc₂C 对照，另示异质结中的 ZrCl₂ 层。图例按输入原子编号归并：异质结中 Sc₂C = C#2 + Sc#5-6、ZrCl₂ = Zr#1 + Cl#3-4；孤立 Sc₂C = Sc#1-2 + C#3。
纵轴单位为 states/eV/simulation cell。</figcaption></figure>

各计算的费米能级与网格信息如下；异质结在 +1.5% 下的 E_F = 0.3133 eV，与上文电子结构图所用值一致。

| 状态 | E_F (eV) | 能量点数（步长 0.005 eV） | 投影文件数 |
|---|---:|---:|---:|
| 异质结，0% | 0.3522 | 10,533 | 19 |
| 孤立 Sc₂C，0% | −2.1388 | 10,387 | 10 |
| 异质结，+1.5% | 0.3133 | 10,527 | 19 |
| 孤立 Sc₂C，+1.5% | −2.1362 | 10,378 | 10 |

母体异质结的力残差为 0% 时 2.40×10⁻⁴、+1.5% 时 1.20×10⁻⁴ Ry/Bohr；本图只用于冻结几何的电子态对照。
数据与复现文件：[矢量 PDF 图](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos.pdf) · [长表数据 CSV](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos_long.csv) · [汇总与求和检查 CSV](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos_summary.csv) · [复现绘图及检查脚本](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/plot_frozen_pdos.py) · [数据说明](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/README.txt)。

## 文献中的相关图件与表达方式

在文献中，态密度（DOS / PDOS）常横置拼接在能带图右侧，或与二维费米面、晶体轨道哈密顿布居（COHP）并排对照，避免单独成图造成能量标尺脱节：

### 1. 1T-Ta₂N 与金属性 1T-Sc₂C 的能带、水平总 DOS 及费米面对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Bands_DOS_FS_Ta2N_Sc2C_Bekaert2020_Fig5.jpg" alt="1T-Ta₂N 与金属性 1T-Sc₂C 在不含 SOC 与含 SOC 下的能带、水平总 DOS 及费米速度着色二维费米面对比" loading="lazy"/><figcaption><code>1T-Ta₂N</code> 与金属性 <code>1T-Sc₂C</code> 的电子能带及共享能量轴的水平总 DOS 对比（红色虚线为不含 SOC，蓝色实线与浅蓝阴影填充为含 SOC），右侧并列展示按费米速度 <code>v_F(k)</code> 着色的二维六角费米面。图片来源：Bekaert et al., <em>Nanoscale</em> <strong>12</strong>, 17354 (2020), Fig. 5，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

- **读图与作图要点**：将水平总 DOS 紧贴在能带图右侧，并用红色虚线（不含 SOC）与蓝色实线加浅蓝阴影（含 SOC）区分自旋轨道耦合前后的态密度变化，同时配合右侧按 `v_F(k)` 着色的二维六角费米面，便于比较 `1T-Ta₂N` 与 `1T-Sc₂C` 在费米能级处的态密度峰位置。

### 2. 二维费米面、能带、水平元素分辨 PDOS 与总 COHP 四子图横排对齐

<figure class="research-figure"><img src="/Atlas/figures/literature/M4_FS_Bands_DOS_COHP_Mo2ScN2O2_Keivanloo2026_Fig3.jpg" alt="Mo₂ScN₂O₂ 的二维六角费米面、电子能带、元素分辨 PDOS 与总 COHP 曲线四子图横排联立" loading="lazy"/><figcaption>将二维六角布里渊区费米面、高对称路径能带、水平元素分辨 PDOS（Mo、Sc、N、O 与 Total）与总 COHP 成键/反键曲线沿同一能量纵轴 <code>E − E_F</code> 横向并排展示。图片来源：Keivanloo et al., <em>npj Comput. Mater.</em> <strong>12</strong>, 46 (2026), Fig. 3，<a href="https://doi.org/10.1038/s41524-026-02245-0" target="_blank" rel="noopener noreferrer">DOI: 10.1038/s41524-026-02245-0</a>。</figcaption></figure>

- **读图与作图要点**：当费米能级附近存在显著的元素分波态密度峰时，在水平 PDOS 右侧继续并排放置共享能量轴的总 [COHP](/Atlas/m/cohp/qe/) 曲线，可以同时读出各元素对 `N(E_F)` 的贡献以及对应能量区间的总体成键或反键特征。

## 下一步

需要 s/p 总贡献时进入 [投影与布居](/Atlas/m/population-analysis/qe/)；需要知道每个 k、每条带的 s/p 权重时进入 [胖带](/Atlas/m/fatband/qe/)。后者保留 k 分辨信息，与沿整个布里渊区积分的 PDOS 用途不同。

```text
SCF → 均匀 NSCF → dos.x → 总 DOS 与累计态数
                 └─ projwfc.x → 轨道投影与布居
SCF → 路径 bands ── projwfc.x → 逐 k 胖带
```
