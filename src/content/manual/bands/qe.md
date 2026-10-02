## 沿 Γ–X–W–K–Γ–L–X 看 Si 的能级怎样变化

Si 的价带与导带沿高对称路径怎样弯曲，导带谷是否恰好落在端点上？这次先把同一父密度下的路径能级画出来，找到值得在后续带边搜索中加密的区域。本页读取 [Si SCF](/Atlas/m/scf/qe/) 的固定结构与密度，沿 Γ–X–W–K–Γ–L–X 建立独立计算。它与用于 DOS 的[均匀网格 NSCF](/Atlas/m/nscf/qe/) 是两个分支，不需要先完成后者。

[Ba₂N 原文 Fig. 2(a–d)](https://doi.org/10.1103/PhysRevB.105.165101)把穿越费米能的能带、DOS、二维费米口袋与 ELF 放在一起判断态的性质。下面先用真实 Si 小体系练习路径能级的读取，再接 ZrCl₂/Sc₂C 历史界面图，分清“哪里有金属态”和“这些态来自谁”。

例子使用 QE 7.5、PBE、两个 Si 原子、无 SOC。当前坐标与原胞约定对应下面的路径；换晶胞基矢后，不能只保留这些点的标签和数字。

本例文件可[一起下载](/Atlas/examples/si-pbe-electronic-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，先完成 [Si SCF](/Atlas/m/scf/qe/)，再由本页的路径计算生成对应 k 点的能量和波函数。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

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

对应的 [bands.err](/Atlas/examples/si-pbe-electronic/bands-cg/bands.err) 为 1604 字节，保留了重复的 `Authorization required, but no authorization protocol specified` 环境提示，以及 `IEEE_DENORMAL` 浮点非正规数提示。这次最终输出没有未收敛本征值行，后处理读到了完整的 8 条带、121 个路径点；验收时应把这些结果与原始 stderr 一起检查。

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

这里的横轴不是“第几个 k 点”。`bands.x` 已按实际 k 点坐标给出累计距离 `sᵢ = Σⱼ |kⱼ₊₁−kⱼ|`，绘图脚本直接沿用 `.gnu` 的第一列；在这个 `tpiba` 约定下，s 的单位为 `2π/a`。本例 `a=5.397607551 Å`，乘以 `2π/a≈1.16406857 Å⁻¹` 可转换为物理倒空间长度。若直接把 121 个点等距编号，不同路径段就会被拉伸到错误的相对长度。

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

<span id="可复制的-ai-编码提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-可复制的-ai-编码提示词" class="legacy-anchor" aria-hidden="true"></span>
## 路径本征值的整理与作图

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

<details>
<summary>plot_bands.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
data=np.loadtxt(r/'bands-cg/si.bands.dat.gnu')
assert data.shape==(8*121,2)
bands=data.reshape(8,121,2)
assert np.allclose(bands[:,:,0],bands[0,:,0])
vbm=bands[3,:,1].max()
ticks=bands[0,[0,24,36,48,72,96,120],0]
fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
for band in bands:ax.plot(band[:,0],band[:,1]-vbm,color='#0072b2',lw=1.1)
for tick in ticks:ax.axvline(tick,color='0.85',lw=.7)
ax.axhline(0,color='0.4',ls='--',lw=.8)
ax.set(xticks=ticks,xticklabels=['Γ','X','W','K','Γ','L','X'],
       xlim=(ticks[0],ticks[-1]),ylim=(-13,7),ylabel='Energy − path VBM (eV)',
       title='Si, PBE, fixed example cell; no SOC')
(r/'plots').mkdir(exist_ok=True)
fig.savefig(r/'plots/bands-direct.png',dpi=240)
fig.savefig(r/'plots/bands-direct.svg')
print('8 bands, 121 k points; path VBM =',vbm,'eV')
```

</details>

同一 XML/胖带 CSV 中的路径价带顶是 `6.397028957255 eV`，而 `.gnu` 按四位小数输出。两者相差约 `2.90×10⁻⁵ eV`，来自文本精度，不能解释成能级移动。普通能带和胖带分别读取两种精度的数据，均以本路径价带顶为零；叠图时应统一采用同一个精确参考。

原始带能没有减去真空能级，不是跨材料可直接比较的绝对能级。此处标注 `Energy − path VBM` 比笼统写“费米能”更明确。

```bash
python3 plot_bands.py
```

![Si 路径能带，能量相对同一路径的价带顶](/Atlas/examples/si-pbe-electronic/plots/bands-direct.png)

先定位节点和 0 eV 水平线。Γ 点的三条价带顶接近简并，Γ–X 段的导带谷降到比 Γ 点导带更低的位置；只看 Γ 点的上下两条线，会漏掉这部分低能导带。交叉或简并处仍按输出带号连接，不表示已追踪同一个轨道分支。

可以把Γ处的两组近简并线作为读图起点：XML中第2–4带约为6.397029 eV，第5–7带约为8.966555 eV，差为约2.569526 eV。减去本路径VBM后，前一组落在零能附近，后一组落在约2.57 eV；向X方向走，第5带继续下降，所以Γ处的这段竖直间隔不是全区间隙。灰线怎样弯曲回答的是本征值随k变化；在交叉附近某种颜色或点面积怎样变化，才需要后续同一路径的轨道投影。

若想从弯曲进一步求有效质量，必须用物理波矢对能量求二阶导数。这里横轴是沿多段路径累积的s，在X、W等拐点前后，倒空间方向已经改变，不能把跨节点的一串点整体拟合成同一个方向的抛物线。应回到[局部谷数据](/Atlas/m/band-gap/qe/)的单一方向、实际Å⁻¹坐标和拟合窗口。

这套 Si 数据支持路径读图与带边搜索的基础操作，不用于说明界面金属化。界面体系要沿着相同物理路径比较层来源和占据变化；轨道身份从对应波函数的投影读取。

若节点间距不符或带在节点断开，先核对文件是否仍是 8 个 121 行块、各块横坐标是否一致，再检查索引。不要靠均匀重设刻度或平移个别带来修饰图形。

能带图适合看路径上能级如何分散，不能保证路径经过全布里渊区的真实极值。直接/间接带隙的判定、均匀采样与局部谷细化见 [带边搜索](/Atlas/m/band-gap/qe/)；辨认分支来源接 [轨道投影](/Atlas/m/fatband/qe/)，穿过费米能的金属分支接 [费米面](/Atlas/m/fermi-surface/qe/)。

## 二维金属异质结 ZrCl₂/Sc₂C：轨道投影能带、水平 PDOS 与二维费米面三联图

对于半导体 Si，能量零点取在路径价带顶（VBM）；对于金属异质结，能量零点取在自洽计算确定的费米能级 `E_F`，高对称路径上穿过 `E = E_F` 的能带分支对应倒空间中的费米面等能线。

在历史 +1.5% **`ZrCl₂/Sc₂C`** 固定几何记录中（QE 7.1、vdW-DF3-opt1；[相关原计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)），计算参数为 `ecutwfc = 100 Ry`、`ecutrho = 800 Ry`、`degauss = 0.0037 Ry`，能量零点采用 `scf/pwx.out` 的 `E_F = 0.3133 eV`。绘图脚本 [`plot_zrcl2_sc2c.py`](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py) 将三组输出并排组合为三联图：
- **子图 a（`Orbital fatbands`）**：读取 `scf/bands.in` 沿二维六角布里渊区 `Γ–M–K–Γ` 路径计算的 `151` 个 k 点、`31` 条能带，以及 `scf/fatbands.projwfc_up` 中的 `45` 个正交化原子轨道（归并为 `Zr-4d` `#9–13`、`Sc-3d` `#31–35, #41–45`、`C-2p` `#15–17`、`Cl-3p` `#19–21, #23–25`），以空心圆（`facecolors='none'`，权重阈值 `w > 0.04`）叠加在能带曲线上；
- **子图 b（`PDOS`）**：与子图 a 共享垂直能量轴 `E − E_F ∈ [−2.5, 2.0] eV`，展示 `zrclscc.pdos_tot` 的灰色填充总态密度及四组轨道的水平分波态密度曲线；
- **子图 c（`2D Fermi surface`）**：由 `FS/zrclscc_fs.bxsf`（`64×64×1` k 网格、`65×65×2` BXSF 节点，`E_F = 0.3154 eV`）插值绘制二维六角第一布里渊区内穿过费米能级的 **Band 26**（蓝色）与 **Band 27**（橙红色）费米面等能线。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 异质结的轨道投影 Fatbands、水平 PDOS 与二维六角布里渊区费米面三联图" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) <code>Γ–M–K–Γ</code> 路径上的 31 条能带与 45 个正交化原子轨道归并后的空心圆轨道权重；(b) 共享 <code>E − E_F</code> 纵轴的水平总 DOS 与轨道分辨 PDOS；(c) 由 <code>zrclscc_fs.bxsf</code> 插值得到的第 26 带（蓝）与第 27 带（橙红）二维六角第一布里渊区费米面。</figcaption></figure>

在子图 a 中沿零能线寻找第 26、27 带的交点，再与子图 c 中相应路径上的等能线交点比较，可以把路径色散与费米口袋联系起来。平缓色散提示该能区可能有较大的态密度，但一条高对称路径不能决定整个布里渊区的 DOS 峰；具体轨道贡献仍以均匀网格 PDOS 为准。这里能带与 PDOS 使用 0.3133 eV 作为零点，BXSF 使用其自身的 0.3154 eV。两者来自不同采样，图适合并列观察；定量配对交点前应检查采样和费米能的一致性。

三栏之间还有一个容易误读的关系：a栏同一能区出现多条线，只说明这条路径采到了这些态；b栏的高峰累加整个均匀网格上该能区的态；c栏把同一能量在二维倒空间中的位置连成轮廓。路径上很平的一小段可能只占全区很少面积，因而不能凭它替代b栏的积分。实际处理时保持三种对象各自的数据键：a按(k,band)配对，b按能量和原子轨道归并，c按带号和二维网格重建；只在核对参考与采样后联读它们。

下载本算例：[bands.in](/Atlas/examples/zrcl2-sc2c/scf/bands.in) · [pdos.in](/Atlas/examples/zrcl2-sc2c/pdos/pdos.in) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。

[电子结构三联图的完整绘图源码](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)保留逐态投影、PDOS 归并及 BXSF 读取规则。

## 从孤立层能带到界面重构

[SnSe₂/PtTe₂ 原文 PDF 第3页 Fig. 1(c,f,i)](https://arxiv.org/pdf/2502.13690v1#page=3)按三行排列孤立SnSe₂、孤立PtTe₂和界面。左侧为 Γ–M–K–Γ 路径能带，右侧为共用 E−E_F 纵轴的总DOS与轨道PDOS；虚线标零能，DOS横轴标states/eV。先在(c)、(f)找各层带边，再在(i)沿红/蓝层权重辨认越过零能的分支，比只数新增线条更有意义。图注没有给出可移用的线宽归一化常数，DOS峰高也不是每原子电子数。

本站三联图保留这一联读结构：a用151个路径点的原始能级与逐态投影，b取均匀网格PDOS，c取完整BXSF。复现时按真实倒空间距离连接能带，将投影按同一(k,band)配对，DOS作为另一个积分分支保持同一能量读法；Si零点仍是路径VBM，历史界面各分支使用前文各自参考，不借用论文零点或数据。

比较界面和单层时，先把单层放进匹配的面内晶胞与几何，保持泛函、赝势和 SOC 约定一致。冻结单层与界面内的同一层可以隔离接触效应，独立弛豫单层则同时包含几何改变。各自减去 E_F 能比较近费米谱形；若要讨论某条能带的绝对移动，应接[静电势](/Atlas/m/electrostatic-potential/)建立共同参考。

沿同一条带看层权重的变化，能辨认两层共同参与的电子态；再在交叉附近检查反交叉、轨道权重交换以及对应态的空间分布，才把这种共同参与进一步解释为层间杂化。界面图比孤立层多了几条线，还可能来自超胞折叠，须先确认倒空间映射。电荷转移量另由[差分电荷](/Atlas/m/delta-charge/)与空间积分确定。

带隙作为能带的带边分析保留在[Si 带边搜索实例](/Atlas/m/band-gap/qe/)；有穿越 E_F 的分支时，转到[胖带](/Atlas/m/fatband/qe/)追踪态来源，再由[费米面](/Atlas/m/fermi-surface/qe/)查看全区等能轮廓。

<details>
<summary>用 gnuplot 核对已有 Si 路径数据</summary>

在完整下载包根目录保存以下 `si-path.gp`，运行 `gnuplot si-path.gp`。它直接读8条带各121点的距离/eV列，减相同6.3970eV路径VBM，不平滑或拟合。已在Talos的gnuplot 6.0上用原包968行数据运行；网页继续展示既有图，不重复增加图片。

```gnuplot
set terminal svg size 880,560 enhanced font 'sans,14'
set output 'si-path-gnuplot.svg'
set xlabel 'Cumulative path distance (2pi/a)'
set ylabel 'Energy - path VBM (eV)'
set xrange [0:4.646264]
set yrange [-6:7]
set xtics ('Gamma' 0,'X' 1,'W' 1.5,'K' 1.853553,'Gamma' 2.914214,'L' 3.780239,'X' 4.646264)
set grid xtics ytics
unset key
plot 'bands-cg/si.bands.dat.gnu' using 1:($2-6.3970) with lines linewidth 1.2 linecolor rgb '#222222'
```

gnuplot呈现已经计算的数据；论文分层线仍需对应投影，不能从普通能带猜出。原始提取与全部绘图源码保留。

</details>

```text
同一 SCF 密度 → 路径 bands → bands.x → 原始 eV 数据 → 统一能量零点
                              └─ projwfc.x → 逐k逐带投影
均匀 NSCF ──────────────────────────────→ DOS
```
