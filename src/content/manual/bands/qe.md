## 沿 Γ–X–W–K–Γ–L–X 看 Si 的能级怎样变化

Si 的价带与导带沿高对称路径怎样弯曲，导带谷是否恰好落在端点上？这次先把同一父密度下的路径能级画出来，找到值得在后续带边搜索中加密的区域。本页读取 [Si SCF](/Atlas/m/scf/qe/) 的固定结构与密度，沿 Γ–X–W–K–Γ–L–X 建立独立计算。它与用于 DOS 的[均匀网格 NSCF](/Atlas/m/nscf/qe/) 是两个分支，不需要先完成后者。

[Bekaert 等的 Fig. 2](https://doi.org/10.1039/D0NR03875J)把二维 Mo/W 碳氮化物的含 SOC 与无 SOC 能带和 DOS 放在一起，用于辨认费米能附近的色散及 SOC 改变的交叉；其 ABINIT 模型与本页无 SOC 的 Si 不同。这里先读一套固定模型的路径能级，带隙的全区搜索另接[带隙页](/Atlas/m/band-gap/qe/)。

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

若节点间距不符或带在节点断开，先核对文件是否仍是 8 个 121 行块、各块横坐标是否一致，再检查索引。不要靠均匀重设刻度或平移个别带来修饰图形。

能带图适合看路径上能级如何分散，不能保证路径经过全布里渊区的真实极值。直接/间接带隙的判定与采样对照见 [带隙页](/Atlas/m/band-gap/qe/)；导带谷附近的曲率见 [有效质量](/Atlas/m/effective-mass/qe/)。

## 二维金属异质结 ZrCl₂/Sc₂C：轨道投影能带、水平 PDOS 与二维费米面三联图

对于半导体 Si，能量零点取在路径价带顶（VBM）；对于金属异质结，能量零点取在自洽计算确定的费米能级 `E_F`，高对称路径上穿过 `E = E_F` 的能带分支对应倒空间中的费米面等能线。

在 **`ZrCl₂/Sc₂C`**（[双网格超导计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，计算参数为 `ecutwfc = 100 Ry`、`ecutrho = 800 Ry`、`degauss = 0.0037 Ry`，能量零点采用 `scf/pwx.out` 的 `E_F = 0.3133 eV`。绘图脚本 [`plot_zrcl2_sc2c.py`](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py) 将三组输出并排组合为三联图：
- **子图 a（`Orbital fatbands`）**：读取 `scf/bands.in` 沿二维六角布里渊区 `Γ–M–K–Γ` 路径计算的 `151` 个 k 点、`31` 条能带，以及 `scf/fatbands.projwfc_up` 中的 `45` 个正交化原子轨道（归并为 `Zr-4d` `#9–13`、`Sc-3d` `#31–35, #41–45`、`C-2p` `#15–17`、`Cl-3p` `#19–21, #23–25`），以空心圆（`facecolors='none'`，权重阈值 `w > 0.04`）叠加在能带曲线上；
- **子图 b（`PDOS`）**：与子图 a 共享垂直能量轴 `E − E_F ∈ [−2.5, 2.0] eV`，展示 `zrclscc.pdos_tot` 的灰色填充总态密度及四组轨道的水平分波态密度曲线；
- **子图 c（`2D Fermi surface`）**：由 `FS/zrclscc_fs.bxsf`（`64×64×1` k 网格、`65×65×2` BXSF 节点，`E_F = 0.3154 eV`）插值绘制二维六角第一布里渊区内穿过费米能级的 **Band 26**（蓝色）与 **Band 27**（橙红色）费米面等能线。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 异质结的轨道投影 Fatbands、水平 PDOS 与二维六角布里渊区费米面三联图" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) <code>Γ–M–K–Γ</code> 路径上的 31 条能带与 45 个正交化原子轨道归并后的空心圆轨道权重；(b) 共享 <code>E − E_F</code> 纵轴的水平总 DOS 与轨道分辨 PDOS；(c) 由 <code>zrclscc_fs.bxsf</code> 插值得到的第 26 带（蓝）与第 27 带（橙红）二维六角第一布里渊区费米面。</figcaption></figure>

在子图 a 中沿零能线寻找第 26、27 带的交点，再与子图 c 中相应路径上的等能线交点比较，可以把路径色散与费米口袋联系起来。平缓色散提示该能区可能有较大的态密度，但一条高对称路径不能决定整个布里渊区的 DOS 峰；具体轨道贡献仍以均匀网格 PDOS 为准。这里能带与 PDOS 使用 0.3133 eV 作为零点，BXSF 使用其自身的 0.3154 eV。两者来自不同采样，图适合并列观察；定量配对交点前应检查采样和费米能的一致性。

下载本算例：[bands.in](/Atlas/examples/zrcl2-sc2c/scf/bands.in) · [pdos.in](/Atlas/examples/zrcl2-sc2c/pdos/pdos.in) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。

<details>
<summary>plot_zrcl2_sc2c.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np

ZR_DIR = Path(__file__).resolve().parent
for candidate in (ZR_DIR, ZR_DIR.parent, ZR_DIR.parents[1] / 'scripts'):
    if (candidate / 'atlas_plot_style.py').exists():
        sys.path.insert(0, str(candidate))
        break

import atlas_plot_style

sys.path.insert(0, str(ZR_DIR))
from tc_table_audit import piecewise_linear_crossings, write_report

PALETTE = {
    'Ink': '#162232',
    'Slate': '#324255',
    'Muted': '#5a6b80',
    'Navy': '#0072b2',
    'Blue': '#2968a8',
    'SoftBlue': '#d6e6f4',
    'Teal': '#009e73',
    'SoftTeal': '#d7ece8',
    'Amber': '#e69f00',
    'Rust': '#d55e00',
    'Coral': '#cc79a7',
    'WarmTint': '#f4efe6',
}

CM1_TO_THZ = 1.0 / 33.3564095198152
FIG_OUT_DIR = (
    ZR_DIR.parents[1] / 'figures' / 'zrcl2-sc2c'
    if (ZR_DIR.parents[1] / 'figures').exists()
    else ZR_DIR / 'figures'
)


def apply_atlas_style() -> None:
    atlas_plot_style.install()


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_figure(fig, stem_name: str) -> None:
    FIG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT_DIR / f'{stem_name}.png')
    plt.close(fig)


def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    data_dir = ZR_DIR / 'scf'
    gnu_path = data_dir / 'bands.dat.gnu'
    proj_path = data_dir / 'fatbands.projwfc_up'
    proj_lines = [line for line in proj_path.read_text().splitlines() if line.strip()]
    header_rows = [
        idx for idx, line in enumerate(proj_lines[:30])
        if len(line.split()) == 3 and all(part.isdigit() for part in line.split())
    ]
    if len(header_rows) != 1:
        raise ValueError(f'Expected one projection header; found {len(header_rows)}.')
    header_idx = header_rows[0]
    natomwfc, nk, nbnd = map(int, proj_lines[header_idx].split())
    if header_idx + 2 >= len(proj_lines):
        raise ValueError('Projection header is missing its spin flags or first state.')
    spin_flags = proj_lines[header_idx + 1].split()
    if len(spin_flags) != 2 or any(flag not in {'T', 'F'} for flag in spin_flags):
        raise ValueError(f'Unexpected projection spin flags: {spin_flags}')
    ptr = header_idx + 2

    raw = np.loadtxt(gnu_path)
    if raw.shape != (nbnd * nk, 2) or not np.isfinite(raw).all():
        raise ValueError(f'Unexpected bands.dat.gnu shape or nonfinite values: {raw.shape}')
    band_blocks = raw.reshape(nbnd, nk, 2)
    k_blocks = band_blocks[:, :, 0]
    if not np.allclose(k_blocks, k_blocks[0:1], rtol=0.0, atol=1e-8):
        raise ValueError('The k-distance sequence differs between band blocks.')
    k_dist = k_blocks[0]
    if not np.isclose(k_dist[0], 0.0, rtol=0.0, atol=1e-8):
        raise ValueError(f'Band path does not start at zero: {k_dist[0]}')
    if np.any(np.diff(k_dist) < -1e-8) or k_dist[-1] <= k_dist[0]:
        raise ValueError('Band path distances are not a forward, nonzero path.')
    bands_e = band_blocks[:, :, 1] - ef

    atom_elements = {1: 'Zr', 2: 'C', 3: 'Cl', 4: 'Cl', 5: 'Sc', 6: 'Sc'}
    group_by_site_orbital = {
        (1, 'D'): 'Zr-4d',
        (5, 'D'): 'Sc-3d',
        (6, 'D'): 'Sc-3d',
        (2, 'P'): 'C-2p',
        (3, 'P'): 'Cl-3p',
        (4, 'P'): 'Cl-3p',
    }
    expected_state_counts = {'Zr-4d': 5, 'Sc-3d': 10, 'C-2p': 3, 'Cl-3p': 6}
    grouped = {key: np.zeros((nbnd, nk)) for key in expected_state_counts}
    state_counts = {key: 0 for key in expected_state_counts}
    expected_ik = np.repeat(np.arange(1, nk + 1), nbnd)
    expected_ib = np.tile(np.arange(1, nbnd + 1), nk)
    block_len = nk * nbnd
    seen_state_ids = set()

    for expected_state in range(1, natomwfc + 1):
        if ptr >= len(proj_lines):
            raise ValueError(f'Projection file ended before state {expected_state}.')
        hdr = proj_lines[ptr].split()
        if len(hdr) < 4:
            raise ValueError(f'Malformed state header at line {ptr + 1}: {hdr}')
        state_id, atom_id = int(hdr[0]), int(hdr[1])
        element, orbital = hdr[2], hdr[3].upper()
        if state_id != expected_state or state_id in seen_state_ids:
            raise ValueError(f'Unexpected or duplicate state id {state_id}; expected {expected_state}.')
        seen_state_ids.add(state_id)
        if atom_id not in atom_elements or element != atom_elements[atom_id]:
            raise ValueError(f'State {state_id} has atom/element mismatch: #{atom_id} {element}.')
        angular_parts = [char for char in orbital if char in 'SPDF']
        if len(angular_parts) != 1:
            raise ValueError(f'State {state_id} has unrecognized orbital label {orbital}.')
        key = group_by_site_orbital.get((atom_id, angular_parts[0]))
        ptr += 1
        rows = []
        for row_index in range(block_len):
            if ptr >= len(proj_lines):
                raise ValueError(f'State {state_id} ended at projection row {row_index}.')
            fields = proj_lines[ptr].split()
            if len(fields) != 3:
                raise ValueError(f'Malformed projection row at line {ptr + 1}: {fields}')
            rows.append((int(fields[0]), int(fields[1]), float(fields[2])))
            ptr += 1
        state_data = np.asarray(rows, dtype=float)
        if not np.array_equal(state_data[:, 0].astype(int), expected_ik):
            raise ValueError(f'State {state_id} has an unexpected k-index sequence.')
        if not np.array_equal(state_data[:, 1].astype(int), expected_ib):
            raise ValueError(f'State {state_id} has an unexpected band-index sequence.')
        state_weights = state_data[:, 2]
        if not np.isfinite(state_weights).all():
            raise ValueError(f'State {state_id} contains nonfinite projection weights.')
        if key is not None:
            grouped[key] += state_weights.reshape(nk, nbnd).T
            state_counts[key] += 1

    if ptr != len(proj_lines) or len(seen_state_ids) != natomwfc:
        raise ValueError(f'Projection records do not close cleanly: consumed {ptr}/{len(proj_lines)} lines.')
    if state_counts != expected_state_counts:
        raise ValueError(f'Unexpected selected state counts: {state_counts}')
    if any(not np.isfinite(curve).all() for curve in grouped.values()):
        raise ValueError('Grouped projection weights contain nonfinite values.')
    return k_dist, bands_e, grouped

def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = ZR_DIR / 'pdos'

    def read_ldos(filename: str) -> tuple[np.ndarray, np.ndarray]:
        arr = np.loadtxt(pdos_dir / filename, comments='#')
        return arr[:, 0] - ef, arr[:, 1]

    e_grid, zr_4d = read_ldos('zrclscc.pdos_atm#1(Zr)_wfc#5(d)')
    _, c_2p = read_ldos('zrclscc.pdos_atm#2(C)_wfc#2(p)')
    _, cl1_3p = read_ldos('zrclscc.pdos_atm#3(Cl)_wfc#2(p)')
    _, cl2_3p = read_ldos('zrclscc.pdos_atm#4(Cl)_wfc#2(p)')
    _, sc1_3d = read_ldos('zrclscc.pdos_atm#5(Sc)_wfc#4(d)')
    _, sc2_3d = read_ldos('zrclscc.pdos_atm#6(Sc)_wfc#4(d)')
    tot_arr = np.loadtxt(pdos_dir / 'zrclscc.pdos_tot', comments='#')

    return e_grid, {
        'Total': tot_arr[:, 1],
        'Zr-4d': zr_4d,
        'Sc-3d': sc1_3d + sc2_3d,
        'C-2p': c_2p,
        'Cl-3p': cl1_3p + cl2_3p,
    }


def parse_zrcl2_bxsf() -> tuple[float, np.ndarray, np.ndarray, dict[int, np.ndarray]]:
    bxsf_path = ZR_DIR / 'FS' / 'zrclscc_fs.bxsf'
    lines = [l.strip() for l in bxsf_path.read_text().splitlines() if l.strip()]
    ef = 0.3154
    for l in lines[:20]:
        if 'Fermi Energy:' in l:
            ef = float(l.split(':')[1].strip())
            break

    b_idx = [i for i, l in enumerate(lines) if l.startswith('BEGIN_BANDGRID_3D')][0]
    nx, ny, nz = [int(x) for x in lines[b_idx + 2].split()]
    b1 = np.array([float(x) for x in lines[b_idx + 4].split()[:2]])
    b2 = np.array([float(x) for x in lines[b_idx + 5].split()[:2]])

    bands: dict[int, np.ndarray] = {}
    ptr = b_idx + 7
    while ptr < len(lines):
        line = lines[ptr]
        if line.startswith('BAND:'):
            b_num = int(line.split(':')[1].strip())
            ptr += 1
            vals: list[float] = []
            while ptr < len(lines) and not lines[ptr].startswith('BAND:') and not lines[ptr].startswith('END_BANDGRID_3D'):
                vals.extend([float(x) for x in lines[ptr].split()])
                ptr += 1
            arr3d = np.array(vals).reshape((nx, ny, nz))
            bands[b_num] = arr3d[:, :, 0] - ef
        else:
            ptr += 1

    return ef, b1, b2, bands


def render_zrcl2_sc2c_electronic() -> None:
    apply_atlas_style()
    k_dist, bands_e, grouped_w = parse_zrcl2_fatbands()
    e_dos, pdos = parse_zrcl2_pdos()
    _, b1, b2, fs_bands = parse_zrcl2_bxsf()

    fig = plt.figure(figsize=(10.2, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.85,
        width_ratios=[1.35, 0.72, 1.15], wspace=0.22
    )
    ax_band = fig.add_subplot(gs[0, 0])
    ax_dos = fig.add_subplot(gs[0, 1], sharey=ax_band)
    ax_fs = fig.add_subplot(gs[0, 2])

    for ax in (ax_band, ax_dos, ax_fs):
        style_axis(ax)

    k_ticks = [k_dist[0], k_dist[50], k_dist[100], k_dist[150]]
    for x in k_ticks[1:-1]:
        ax_band.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    ax_band.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_band.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    for ib in range(bands_e.shape[0]):
        e_curve = bands_e[ib]
        if e_curve.max() < -2.7 or e_curve.min() > 2.2:
            continue
        ax_band.plot(k_dist, e_curve, color='#7d8b9d', lw=0.85, alpha=0.75, zorder=2)

    orb_specs = [
        ('Cl-3p', PALETTE['Amber'], 72.0),
        ('C-2p', PALETTE['Rust'], 85.0),
        ('Sc-3d', PALETTE['Teal'], 92.0),
        ('Zr-4d', PALETTE['Navy'], 96.0),
    ]
    for label, color, scale in orb_specs:
        w_mat = grouped_w[label]
        for ib in range(bands_e.shape[0]):
            e_curve = bands_e[ib]
            if e_curve.max() < -2.6 or e_curve.min() > 2.1:
                continue
            w = w_mat[ib]
            mask = w > 0.04
            if np.any(mask):
                ax_band.scatter(
                    k_dist[mask],
                    e_curve[mask],
                    s=w[mask] * scale,
                    facecolors='none',
                    edgecolors=color,
                    linewidths=0.95,
                    alpha=0.88,
                    zorder=4,
                )

    ax_band.set_xlim(k_ticks[0], k_ticks[-1])
    ax_band.set_ylim(-2.5, 2.0)
    ax_band.set_xticks(k_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_band.set_ylabel(r'Energy $E - E_F$ (eV)')
    ax_band.set_title('Orbital fatbands', pad=8)

    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Navy'], markeredgewidth=1.3, markersize=5.2, label=r'Zr-$4d$ [#1]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Teal'], markeredgewidth=1.3, markersize=5.2, label=r'Sc-$3d$ [#5+#6]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Rust'], markeredgewidth=1.3, markersize=5.2, label=r'C-$2p$ [#2]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Amber'], markeredgewidth=1.3, markersize=5.2, label=r'Cl-$3p$ [#3+#4]'),
    ]
    ax_band.legend(handles=legend_handles, loc='lower left', ncol=2, fontsize=8.0)

    ax_band.annotate(
        'Bands 26, 27\n(Zr-$4d$ [#1] / Sc-$3d$ [#5+#6])',
        xy=(k_dist[24], 0.04),
        xytext=(k_dist[8], 0.92),
        fontsize=8.0, zorder=10,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.8),
    )

    mask_dos = (e_dos >= -2.6) & (e_dos <= 2.1)
    ed = e_dos[mask_dos]
    ax_dos.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_dos.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    ax_dos.fill_betweenx(ed, 0, pdos['Total'][mask_dos], color='#dfe6ef', alpha=0.55)
    ax_dos.plot(pdos['Total'][mask_dos], ed, color=PALETTE['Ink'], lw=1.05, label='Total')
    ax_dos.plot(pdos['Zr-4d'][mask_dos], ed, color=PALETTE['Navy'], lw=1.1, label=r'Zr-$4d$ [#1]')
    ax_dos.plot(pdos['Sc-3d'][mask_dos], ed, color=PALETTE['Teal'], lw=1.1, label=r'Sc-$3d$ [#5+#6]')
    ax_dos.plot(pdos['C-2p'][mask_dos], ed, color=PALETTE['Rust'], lw=1.05, label=r'C-$2p$ [#2]')
    ax_dos.plot(pdos['Cl-3p'][mask_dos], ed, color=PALETTE['Amber'], lw=0.95, label=r'Cl-$3p$ [#3+#4]')

    ax_dos.set_xlim(0, 6.8)
    ax_dos.set_xticks([0, 3, 6])
    ax_dos.set_xlabel('PDOS (eV$^{-1}$)')
    ax_dos.set_title('PDOS', pad=8)
    ax_dos.tick_params(labelleft=False)

    B = np.column_stack([b1, b2])
    B_inv = np.linalg.inv(B)
    angles = np.deg2rad(np.arange(0, 360, 60))
    R_k = 2.0 / 3.0
    bz_verts = np.column_stack([R_k * np.cos(angles), R_k * np.sin(angles)])

    nx = 220
    kx_lin = np.linspace(-0.75, 0.75, nx)
    ky_lin = np.linspace(-0.75, 0.75, nx)
    KX, KY = np.meshgrid(kx_lin, ky_lin)
    uv = B_inv @ np.vstack([KX.ravel(), KY.ravel()])
    u_mod = np.mod(uv[0], 1.0) * 64.0
    v_mod = np.mod(uv[1], 1.0) * 64.0

    def interp_periodic(grid65: np.ndarray) -> np.ndarray:
        i0 = np.floor(u_mod).astype(int) % 64
        j0 = np.floor(v_mod).astype(int) % 64
        i1 = (i0 + 1) % 64
        j1 = (j0 + 1) % 64
        du = u_mod - np.floor(u_mod)
        dv = v_mod - np.floor(v_mod)
        val = (
            (1 - du) * (1 - dv) * grid65[i0, j0]
            + du * (1 - dv) * grid65[i1, j0]
            + (1 - du) * dv * grid65[i0, j1]
            + du * dv * grid65[i1, j1]
        )
        return val.reshape(KX.shape)

    E26 = interp_periodic(fs_bands[26])
    E27 = interp_periodic(fs_bands[27])

    m_angles = np.deg2rad([30.0, 90.0, 150.0])
    inside_bz = np.ones_like(KX, dtype=bool)
    for ang in m_angles:
        inside_bz &= np.abs(KX * np.cos(ang) + KY * np.sin(ang)) <= (1.0 / np.sqrt(3.0) + 0.004)

    E26_masked = np.where(inside_bz, E26, np.nan)
    E27_masked = np.where(inside_bz, E27, np.nan)

    ax_fs.contourf(
        KX, KY, E26_masked,
        levels=np.linspace(-0.6, 0.4, 22),
        cmap='Blues_r', alpha=0.25, zorder=1,
    )
    ax_fs.contour(KX, KY, E26_masked, levels=[0.0], colors=[PALETTE['Navy']], linewidths=1.85, zorder=4)
    ax_fs.contour(KX, KY, E27_masked, levels=[0.0], colors=[PALETTE['Rust']], linewidths=1.85, zorder=5)

    bz_poly = Polygon(bz_verts, closed=True, fill=False, edgecolor=PALETTE['Ink'], lw=1.2, zorder=6)
    ax_fs.add_patch(bz_poly)

    gamma_pt = np.array([0.0, 0.0])
    m_pt = np.array([0.5, 1.0 / (2.0 * np.sqrt(3.0))])
    k_pt = np.array([1.0 / 3.0, 1.0 / np.sqrt(3.0)])
    path_pts = np.vstack([gamma_pt, m_pt, k_pt, gamma_pt])
    ax_fs.plot(path_pts[:, 0], path_pts[:, 1], color=PALETTE['Slate'], ls='--', lw=0.95, zorder=6)
    ax_fs.scatter([gamma_pt[0], m_pt[0], k_pt[0]], [gamma_pt[1], m_pt[1], k_pt[1]], color=PALETTE['Ink'], s=16, zorder=7)
    ax_fs.text(-0.07, -0.08, r'$\Gamma$', fontsize=8.5, fontweight='bold')
    ax_fs.text(m_pt[0] + 0.03, m_pt[1] - 0.02, r'$M$', fontsize=8.5, fontweight='bold')
    ax_fs.text(k_pt[0] + 0.02, k_pt[1] + 0.03, r'$K$', fontsize=8.5, fontweight='bold')

    fs_handles = [
        Line2D([0], [0], color=PALETTE['Navy'], lw=1.8, label='Band 26'),
        Line2D([0], [0], color=PALETTE['Rust'], lw=1.8, label='Band 27'),
    ]
    ax_fs.legend(handles=fs_handles, loc='lower center', ncol=2, fontsize=8.0)
    ax_fs.set_aspect('equal')
    ax_fs.set_xlim(-0.74, 0.74)
    ax_fs.set_ylim(-0.74, 0.74)
    ax_fs.set_xticks([-0.5, 0.0, 0.5])
    ax_fs.set_yticks([-0.5, 0.0, 0.5])
    ax_fs.set_xlabel(r'$k_x$ ($2\pi/a$)')
    ax_fs.set_ylabel(r'$k_y$ ($2\pi/a$)')
    ax_fs.set_title('2D Fermi surface', pad=8)

    save_figure(fig, 'zrcl2-sc2c-electronic')


def parse_gam_lines(filepath: Path, target_broadening: float = 0.0030) -> np.ndarray:
    text = filepath.read_text()
    blocks = re.split(r'Broadening\s+([\d.]+)', text)[1:]
    for i in range(0, len(blocks), 2):
        bval = float(blocks[i])
        if abs(bval - target_broadening) < 1e-5:
            lines = [l.strip() for l in blocks[i + 1].strip().splitlines() if l.strip()]
            gam = np.zeros((151, 18))
            ptr = 0
            for iq in range(151):
                ptr += 1
                vals = []
                while len(vals) < 18 and ptr < len(lines):
                    vals.extend([float(x) for x in lines[ptr].split()])
                    ptr += 1
                gam[iq] = np.maximum(0.0, np.array(vals[:18]) * 1000.0)
            return gam
    raise ValueError(f'Broadening {target_broadening} not found in {filepath}')


def render_zrcl2_sc2c_phonon_epc() -> None:
    apply_atlas_style()
    ph96_dir = ZR_DIR / 'ph96'
    freq_arr = np.loadtxt(ph96_dir / 'zrclscc.freq.gp')
    q_dist = freq_arr[:, 0]
    freqs_thz = freq_arr[:, 1:] * CM1_TO_THZ

    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)
    ry_to_thz = 3289.84196
    nef_003 = 30.772452
    w_ry = np.maximum(freqs_thz, 0.25) / ry_to_thz
    g_ry = (gam_qv / 1000.0) / ry_to_thz
    lam_qv = np.where(freqs_thz > 0.25, g_ry / (np.pi * nef_003 * (w_ry ** 2)), 0.0)

    phdos_arr = np.loadtxt(ph96_dir / 'zrclscc.phdos', comments='#')
    w_dos_thz = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    phdos_tot = phdos_arr[:, 1] * dos_scale
    phdos_zr = phdos_arr[:, 2] * dos_scale
    phdos_c = phdos_arr[:, 3] * dos_scale
    phdos_cl = (phdos_arr[:, 4] + phdos_arr[:, 5]) * dos_scale
    phdos_sc = (phdos_arr[:, 6] + phdos_arr[:, 7]) * dos_scale

    a2f_lines = (ph96_dir / 'alpha2F.dat').read_text().splitlines()[2:]
    e_a2f, a2f_003, a2f_001 = [], [], []
    for idx in range(0, len(a2f_lines), 2):
        r1 = [float(x) for x in a2f_lines[idx].split()]
        e_a2f.append(r1[0])
        a2f_001.append(max(0.0, r1[1]))
        a2f_003.append(max(0.0, r1[3]))
    e_a2f = np.array(e_a2f)
    a2f_003 = np.array(a2f_003)
    a2f_001 = np.array(a2f_001)

    de = e_a2f[1] - e_a2f[0]
    cum_lam_003 = np.zeros_like(e_a2f)
    cum_lam_003[1:] = np.cumsum(2.0 * a2f_003[1:] / e_a2f[1:] * de)

    fig = plt.figure(figsize=(10.2, 4.45))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.98, bottom=0.17, top=0.84,
        width_ratios=[1.42, 0.76, 1.02], wspace=0.12
    )
    ax_ph = fig.add_subplot(gs[0, 0])
    ax_pdos = fig.add_subplot(gs[0, 1], sharey=ax_ph)
    ax_a2f = fig.add_subplot(gs[0, 2], sharey=ax_ph)

    for ax in (ax_ph, ax_pdos, ax_a2f):
        style_axis(ax)
        ax.axhline(10.0, color=PALETTE['Coral'], ls='--', lw=1.05, zorder=3)
        ax.axhspan(12.2, 17.3, color=PALETTE['WarmTint'], alpha=0.55, zorder=0)

    q_ticks = [q_dist[0], q_dist[50], q_dist[100], q_dist[150]]
    for x in q_ticks[1:-1]:
        ax_ph.axvline(x, color='#ced8e3', lw=0.85, zorder=1)

    for nu in range(18):
        ax_ph.plot(q_dist, freqs_thz[:, nu], color='#4a5a70', lw=0.9, alpha=0.85, zorder=2)
        g_vals = gam_qv[:, nu]
        l_vals = lam_qv[:, nu]
        idx_sub = np.arange(0, 151, 3)
        sizes = np.clip(l_vals[idx_sub] * 26.0 + g_vals[idx_sub] * 0.14, 4.0, 95.0)
        ax_ph.scatter(
            q_dist[idx_sub],
            freqs_thz[idx_sub, nu],
            s=sizes,
            c=np.clip(g_vals[idx_sub], 0.0, 340.0),
            cmap='YlOrRd',
            vmin=0.0,
            vmax=330.0,
            edgecolors='#2b3a4d',
            linewidths=0.3,
            alpha=0.84,
            zorder=4,
        )

    ax_ph.set_xlim(q_ticks[0], q_ticks[-1])
    ax_ph.set_ylim(0.0, 18.0)
    ax_ph.set_xticks(q_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_ph.set_ylabel(r'Frequency $\omega$ (THz)')
    ax_ph.set_title(r'Fat-phonon $\gamma_{\mathbf{q}\nu}$ & $\lambda_{\mathbf{q}\nu}$', pad=8)

    ax_ph.annotate(
        r'C-atom optical modes ($\nu=16\text{–}18$): $\gamma_{\Gamma,17\text{–}18}\approx 322\ \mathrm{GHz}$',
        xy=(q_dist[8], 15.45),
        xytext=(q_dist[10], 11.20),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.95),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_ph.text(
        q_dist[54], 9.05,
        'Saved input emax = 10 THz',
        fontsize=7.5,
        color=PALETTE['Coral'],
        fontweight='bold',
    )

    ax_pdos.fill_betweenx(w_dos_thz, 0, phdos_tot, color='#dfe6ef', alpha=0.55)
    ax_pdos.plot(phdos_tot, w_dos_thz, color=PALETTE['Ink'], lw=1.0, label='Total')
    ax_pdos.plot(phdos_zr, w_dos_thz, color=PALETTE['Navy'], lw=1.1, label='Zr')
    ax_pdos.plot(phdos_sc, w_dos_thz, color=PALETTE['Teal'], lw=1.1, label='Sc')
    ax_pdos.plot(phdos_cl, w_dos_thz, color=PALETTE['Amber'], lw=1.0, label='Cl')
    ax_pdos.plot(phdos_c, w_dos_thz, color=PALETTE['Rust'], lw=1.2, label='C')

    ax_pdos.set_xlim(0, 3.8)
    ax_pdos.set_xticks([0, 1.5, 3.0])
    ax_pdos.set_xlabel('PHDOS (THz$^{-1}$)')
    ax_pdos.set_title('PHDOS', pad=8)
    ax_pdos.tick_params(labelleft=False)
    ax_pdos.legend(loc='center right', fontsize=7.8)

    ax_a2f.fill_betweenx(e_a2f, 0, a2f_003, color=PALETTE['SoftBlue'], alpha=0.72)
    ax_a2f.plot(a2f_003, e_a2f, color=PALETTE['Navy'], lw=1.35, label=r'$\alpha^2F$ ($\sigma=0.003$)')
    ax_a2f.plot(a2f_001, e_a2f, color=PALETTE['Blue'], lw=0.85, ls=':', alpha=0.85, label=r'$\alpha^2F$ ($\sigma=0.001$)')
    lam_scale = 0.36
    ax_a2f.plot(cum_lam_003 * lam_scale, e_a2f, color=PALETTE['Rust'], lw=1.65, label=r'$0.36\times \lambda(\omega)$')

    ax_a2f.set_xlim(0, 1.05)
    ax_a2f.set_xticks([0.0, 0.4, 0.8])
    ax_a2f.set_xlabel(r'$\alpha^2F(\omega)$ & scaled $\lambda(\omega)$')
    ax_a2f.set_title(r'Saved $\alpha^2F(\omega)$ (emax = 10 THz)', pad=8)
    ax_a2f.tick_params(labelleft=False)

    ax_a2f.text(
        0.22, 13.3,
        'Input: 10 0.12 1\n18-THz output provenance open',
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )
    ax_a2f.legend(loc='center right', bbox_to_anchor=(1.0, 0.36), fontsize=7.6)

    save_figure(fig, 'zrcl2-sc2c-phonon-epc')


def load_zrcl2_lambda_series(tag: str, suffix: str = '') -> dict[str, np.ndarray]:
    base = ZR_DIR / tag
    dat_file = base / (f'lambda{suffix}.dat')
    out_file = base / (f'lambdax{suffix}.out')
    arr = np.loadtxt(dat_file, comments='#')
    lines = out_file.read_text().splitlines()
    tc_idx = [i for i, l in enumerate(lines) if 'omega_log' in l and 'T_c' in l][0] + 1
    tc_vals = [float(lines[tc_idx + i].split()[2]) for i in range(arr.shape[0])]
    return {
        'sigma': arr[:, 0],
        'lambda': arr[:, 1],
        'int_a2f': arr[:, 2],
        'wlog': arr[:, 3],
        'nef': arr[:, 4],
        'tc': np.array(tc_vals),
    }


def render_zrcl2_sc2c_k64_k96_tc() -> None:
    apply_atlas_style()
    p64_10 = load_zrcl2_lambda_series('ph64', '')
    p96_10 = load_zrcl2_lambda_series('ph96', '')
    p64_18 = load_zrcl2_lambda_series('ph64', '.emax18')
    p96_18 = load_zrcl2_lambda_series('ph96', '.emax18')
    sigma = p64_10['sigma']
    write_report(ZR_DIR)
    roots10 = piecewise_linear_crossings(sigma, p64_10['tc'], p96_10['tc'])
    roots18 = piecewise_linear_crossings(sigma, p64_18['tc'], p96_18['tc'])

    fig, (ax_tc, ax_diff) = plt.subplots(1, 2, figsize=(10.0, 4.35))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax_tc)
    style_axis(ax_diff)

    for ax in (ax_tc, ax_diff):
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.72, zorder=0)
        ax.set_xticks([0.005, 0.010, 0.015, 0.020])

    ax_tc.plot(sigma, p64_18['tc'], color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.6, label=r'$64^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p96_18['tc'], color=PALETTE['Rust'], marker='s', ms=3.6, lw=1.6, label=r'$96^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p64_10['tc'], color=PALETTE['Navy'], ls='--', lw=1.05, alpha=0.7, label=r'$64^2$ matched 10-THz input')
    ax_tc.plot(sigma, p96_10['tc'], color=PALETTE['Rust'], ls='--', lw=1.05, alpha=0.7, label=r'$96^2$ matched 10-THz input')

    for i, root in enumerate(roots10):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], marker='^', s=42, color=PALETTE['Amber'], zorder=6, label='10-THz table roots' if i == 0 else None)
    for i, root in enumerate(roots18):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], s=58, facecolors='none', edgecolors=PALETTE['Teal'], linewidths=1.8, zorder=7, label='18-THz stored-table root (source open)' if i == 0 else None)
    if roots18:
        root = roots18[0]
        ax_tc.annotate(
            f"Stored 18-THz table\n$\\sigma={root['sigma_ry']:.6f}$ Ry, $T_c={root['tc_k']:.3f}$ K\ninput/run record unlinked",
            xy=(root['sigma_ry'], root['tc_k']),
            xytext=(0.0062, 11.6),
            fontsize=7.7,
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
            arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
        )

    ax_tc.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_tc.set_ylabel(r'Stored Allen–Dynes $T_c(\sigma)$ (K)')
    ax_tc.set_title(r'Stored $T_c$ tables and interpolated roots', pad=8)
    ax_tc.legend(loc='upper right', fontsize=7.4)

    dtc_18 = p64_18['tc'] - p96_18['tc']
    dtc_10 = p64_10['tc'] - p96_10['tc']
    ax_diff.axhline(0.0, color=PALETTE['Ink'], ls='-', lw=0.95, zorder=2)
    ax_diff.plot(sigma, dtc_18, color=PALETTE['Teal'], marker='o', ms=3.8, lw=1.6, label=r'$\Delta T_c$ (18-THz stored tables)')
    ax_diff.plot(sigma, dtc_10, color=PALETTE['Amber'], marker='^', ms=3.6, lw=1.35, ls='--', label=r'$\Delta T_c$ (matched 10-THz inputs)')
    for root in roots10:
        ax_diff.scatter([root['sigma_ry']], [0.0], marker='^', color=PALETTE['Amber'], s=42, zorder=6)
    for root in roots18:
        ax_diff.scatter([root['sigma_ry']], [0.0], color=PALETTE['Teal'], s=48, zorder=7)
    ax_diff.text(
        0.035, 0.055,
        'Prepared ph64.1/ph96.1\nrefinement has no complete Tc pair',
        transform=ax_diff.transAxes,
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )

    ax_diff.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_diff.set_ylabel(r'$\Delta T_c(\sigma) = T_{c,64} - T_{c,96}$ (K)')
    ax_diff.set_title(r'Linear-interpolation roots of $\Delta T_c=0$', pad=8)
    ax_diff.set_ylim(-0.135, 0.155)
    ax_diff.legend(loc='upper right', fontsize=7.4)

    save_figure(fig, 'zrcl2-sc2c-k64-k96-tc')


def render_zrcl2_sc2c_k64_k96_moments() -> None:
    apply_atlas_style()
    p64 = load_zrcl2_lambda_series('ph64', '')
    p96 = load_zrcl2_lambda_series('ph96', '')
    sigma = p64['sigma']

    fig, (ax_nef, ax_lam, ax_wlog) = plt.subplots(1, 3, figsize=(10.4, 4.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.18, top=0.85, wspace=0.31)
    for ax in (ax_nef, ax_lam, ax_wlog):
        style_axis(ax)
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
        ax.set_xticks([0.005, 0.012, 0.020])

    ax_nef.plot(sigma, p64['nef'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64\times 64\times 1$')
    ax_nef.plot(sigma, p96['nef'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96\times 96\times 1$')
    ax_nef.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_nef.set_ylabel(r'$N_\sigma(E_F)$ (states/spin/Ry)')
    ax_nef.set_title(r'$N_\sigma(E_F)$ from stored tables', pad=8)
    ax_nef.legend(loc='upper right', fontsize=7.6)
    ax_nef.annotate(
        'Close for $\\sigma\\geq0.004$ Ry\n(two grids; no convergence proof)',
        xy=(0.004, p64['nef'][3]),
        xytext=(0.0075, 28.5),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_lam.plot(sigma, p64['lambda'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ direct $\lambda$')
    ax_lam.plot(sigma, p96['lambda'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ direct $\lambda$')
    ax_lam.plot(sigma, p64['int_a2f'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.75, label=r'$64^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.plot(sigma, p96['int_a2f'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.75, label=r'$96^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_lam.set_ylabel(r'Coupling $\lambda(\sigma)$')
    ax_lam.set_title(r'10-THz input: $\lambda$ and $\int\alpha^2F$', pad=8)
    ax_lam.legend(loc='upper right', fontsize=7.2)

    ax_wlog.plot(sigma, p64['wlog'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ (10-THz input)')
    ax_wlog.plot(sigma, p96['wlog'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ (10-THz input)')
    ax_wlog.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_wlog.set_ylabel(r'$\omega_{\log}(\sigma)$ (K)')
    ax_wlog.set_title(r'Stored $\omega_{\log}$ (10-THz input)', pad=8)
    ax_wlog.legend(loc='upper left', fontsize=7.2)
    ax_wlog.text(
        0.04, 0.04,
        'Frequency grid ends at 10 THz',
        transform=ax_wlog.transAxes,
        fontsize=7.3,
        color=PALETTE['Muted'],
    )

    save_figure(fig, 'zrcl2-sc2c-k64-k96-moments')


if __name__ == '__main__':
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
```

</details>

## 文献中的相关图件与表达方式

在凝聚态物理与计算材料学文献中，能带图常与水平态密度（DOS）、二维费米面、不同处理（如 SOC 或杂化泛函）对比曲线或超晶格折叠布里渊区配对展示：

### 1. 不含/含 SOC 的能带与水平总 DOS 及费米速度着色的二维费米面

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Bands_DOS_FS_MoW_Bekaert2020_Fig2.jpg" alt="Mo₂C、Mo₂N、W₂C、W₂N 在不含 SOC 与含 SOC 下的能带、水平总 DOS 与费米速度着色二维六角费米面对比" loading="lazy"/><figcaption>二维过渡金属碳/氮化物（<code>Mo₂C, Mo₂N, W₂C, W₂N</code>）在费米能级附近窄窗口 <code>[−1, 1] eV</code> 内的能带与水平总 DOS 对比（红色虚线为不含 SOC，蓝色实线与浅蓝阴影填充为含 SOC），右侧配对展示按费米速度 <code>v_F(k)</code> 着色的二维六角布里渊区费米面。图片来源：Bekaert et al., <em>Nanoscale</em> <strong>12</strong>, 17354 (2020), Fig. 2，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

将能量纵轴聚焦在 `E − E_F ∈ [−1, 1] eV` 的近费米窗口，在同一坐标系内用红色虚线（不含 SOC）与蓝色实线加浅蓝阴影（含 SOC）直接对比自旋轨道耦合引起的能带劈裂与总 DOS 变化，并在右侧列出按费米速度 `v_F(k)` 着色的二维六角费米面。

### 2. GGA-PBE 与 HSE06 泛函下两种材料能带的上下行与双色线型对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_PBE_vs_HSE06_Bands_DOS_HfX2_Santos2025_Fig4.jpg" alt="HfBr₂ 与 HfI₂ 在 GGA-PBE（上行）与 HSE06（下行）下的能带结构及直接/间接光学跃迁箭头标注" loading="lazy"/><figcaption>上行子图为 GGA-PBE 能带，下行子图为 HSE06 杂化泛函能带；每个子图内以红色实线表示 <code>HfBr₂</code>、蓝色点线表示 <code>HfI₂</code>，并用竖直与倾斜箭头标出直接与间接光学跃迁路径。图片来源：Santos et al., <em>J. Appl. Phys.</em> <strong>138</strong>, 104302 (2025), Fig. 4，<a href="https://doi.org/10.1063/5.0286460" target="_blank" rel="noopener noreferrer">DOI: 10.1063/5.0286460</a>。</figcaption></figure>

当需要同时比较两种泛函（上行 GGA-PBE、下行 HSE06）和两种同构化合物（红色实线 `HfBr₂`、蓝色点线 `HfI₂`）时，固定相同的能量参考与高对称路径，并用竖直箭头和斜箭头分别标出直接跃迁与间接跃迁极值点，便于横向比较化学取代效应、纵向比较杂化泛函对带隙的修正。

### 3. 转角莫尔超晶格的微布里渊区折叠与窄平带色散

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_MoireFolding_MiniBands_TBG_Wu2018_Fig1.jpg" alt="转角双层石墨烯的莫尔布里渊区折叠示意图与费米面附近窄平带微带色散" loading="lazy"/><figcaption>倒空间莫尔微布里渊区（Mini Brillouin Zone）几何关系图与费米能级附近窄能量窗口内的微带（Minibands）色散。图片来源：Wu et al., <em>Phys. Rev. Lett.</em> <strong>121</strong>, 257001 (2018), Fig. 1，<a href="https://doi.org/10.1103/PhysRevLett.121.257001" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevLett.121.257001</a>。</figcaption></figure>

对于超胞或转角莫尔体系，在能带图旁给出原胞布里渊区与超胞微布里渊区的几何折叠示意图（标明 `K_+`、`K_-`、`Γ_M`、`M_M`），并将能量纵轴放大到平带所在的窄能量窗口。

下一步：需要 s/p 成分时进入 [逐 k 胖带](/Atlas/m/fatband/qe/)，保留本页的相同 k 点与带号；需要态数分布时进入 [DOS](/Atlas/m/dos/qe/)，读取均匀网格分支。

```text
同一 SCF 密度 → 路径 bands → bands.x → 原始 eV 数据 → 统一能量零点
                              └─ projwfc.x → 逐k逐带投影
均匀 NSCF ──────────────────────────────→ DOS
```
