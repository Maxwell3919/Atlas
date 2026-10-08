# ABINIT H₂：收紧 SCF 后，10 与 20 Ha 两点改变了什么？

同一固定 H₂ 模型，把 10 Ha 的松 SCF 停止改为严格势残差停止，再将截断能升到 20 Ha，保存的能量与力怎样改变？这里读的是实际 A、B 两次原生计算和已有松阈值记录，展示有符号差值及输出精度边界。两点同时改变截断能和自动 FFT 网格，不能据此宣布基组收敛或材料准确性。

[ABINIT 安装、版本与命令](/Atlas/tools/abinit/) · [原六步 smoke 案例](/Atlas/cases/abinit-h2/)

## 三份记录：固定物理模型，改变停止条件与数值设置

原生版本是 Ubuntu `9.10.4-2ubuntu3` 的 ABINIT 9.10.4；日志保留该版本不受支持的提示。这是固定旧版本的复现路线，不是最新生产版本建议。NC-LDA、标量相对论 PSP8 H、10 Bohr 周期盒、H 在 x=±0.7 Bohr、Γ 点、两能带占据 2/0、自旋非极化、`iscf=7` 与 `fftalg=112` 保持一致；不做几何优化或盒长扫描。

旧记录使用 10 Ha、`nstep=10`、`toldfe=1e-6 Ha`，实际六步，是缓存基线，没有重跑。A 为 10 Ha，B 为 20 Ha，两者只使用 `tolvrs=1e-12`、`nstep=30` 的停止设置，实际各十步。原生科学调用合计两次，零重试；A 首次保存数据解析曾失败，之后使用同一 A 原生输出重新解析，没有把解析失败说成 SCF 失败，也没有重跑 A。本站此页只整合已保存的数据。

[设置 CSV](/Atlas/examples/abinit-h2/sensitivity/tables/settings.csv) · [A 完整输入](/Atlas/examples/abinit-h2/sensitivity/cases/A/inputs/h2.abi) · [B 完整输入](/Atlas/examples/abinit-h2/sensitivity/cases/B/inputs/h2.abi) · [缓存输入](/Atlas/examples/abinit-h2/sensitivity/cases/cached-loose-baseline/inputs/h2.abi)

表格可左右滑动；键盘聚焦表框后用左右方向键查看全部列。数字沿用保存记录的 token，不添加物理有效位数。

| 记录 | ecut（Ha） | 自动 FFT | 平均 NPW 原始 token | boxcut | 输入停止 / 最多步 | 实际步 |
| --- | --- | --- | --- | --- | --- | --- |
| 缓存松 SCF | 10 | 30 × 30 × 30 | 1503.000 | 2.10744 | toldfe=1e-6 Ha / 10 | 6 |
| A | 1.00000000E+01 | 30 × 30 × 30 | 1503.000 | 2.10744 | tolvrs=1e-12 / 30 | 10 |
| B | 2.00000000E+01 | 45 × 45 × 45 | 4337.000 | 2.18561 | tolvrs=1e-12 / 30 | 10 |

从 A 到 B，`ecut` 10→20 Ha，同时自动 FFT 30³→45³、平均平面波数 1503→4337、boxcut 2.10744→2.18561；盒与原子位置不变。这是联动数值设置的两点敏感性观察，不是纯基组/网格隔离试验，也不是截断能收敛序列。

## 原生 SCF 停止：势残差的单位和归一化

此设置的 `vres2` 是输出势减输入势、去掉全局均值后的平方和，在全局 FFT/MPI 点上求和；没有除以 NFFT，也没有乘晶胞体积，尺度为 Ha²。它不是 RMS、密度误差或力误差。不同网格上相同 `tolvrs` 不能解释为相同逐点误差。[9.10.4 rhotov 源码](https://github.com/abinit/abinit/blob/9.10.4/src/67_common/m_rhotov.F90#L509-L548)、[sqnorm_v 源码](https://github.com/abinit/abinit/blob/9.10.4/src/44_abitools/m_cgtools.F90)和[scprqt 停止逻辑](https://github.com/abinit/abinit/blob/9.10.4/src/67_common/m_common.F90)对应公开源文件索引。

[全部 SCF token 与舍入区间 CSV](/Atlas/examples/abinit-h2/sensitivity/tables/scf-records.csv)。下表仅列实际末步；每个源 token 的半末位界保留在 CSV 中，解析还要求末残差及原生停止标记的上界严格低于 1e-12 并相互重叠。这是程序停止检查，不是物理精度标准。

| 记录 | 实际末步 | ETOT（Ha，原 token） | 势残差（Ha²，原 token） |
| --- | --- | --- | --- |
| cached-loose-baseline | 6 | -1.1171843463443 | 3.672E-07 |
| A | 10 | -1.1171843463515 | 1.268E-14 |
| B | 10 | -1.1368127131014 | 9.715E-15 |

![实际 A/B 各十步：全局去均值势平方和（Ha²）对数轴；原生 tolvrs=1e-12 停止线只用于 SCF 过程，不表示材料准确性](/Atlas/examples/abinit-h2/sensitivity/figures/scf-residual.png)

[图旁 CSV：全部 20 个正残差及区间](/Atlas/examples/abinit-h2/sensitivity/figures/scf-residual.csv) · [原尺寸 PNG](/Atlas/examples/abinit-h2/sensitivity/figures/scf-residual.png)。保留实际正残差，不剪掉不利的迭代点。

## 有符号能量与完整力：读数而非大小分类

[有符号比较及传播区间 CSV](/Atlas/examples/abinit-h2/sensitivity/tables/signed-comparisons.csv) · [全 18 个原始力分量 CSV](/Atlas/examples/abinit-h2/sensitivity/tables/raw-forces.csv)

| 比较 | 有符号能差（Ha） | 下界（Ha） | 上界（Ha） |
| --- | --- | --- | --- |
| A-minus-cached-loose-baseline | -7.2E-12 | -7.30E-12 | -7.10E-12 |
| B-minus-A | -0.0196283667499 | -0.01962836675000 | -0.01962836674980 |

A−缓存为 −7.2e-12 Ha；B−A 为 −0.0196283667499 Ha。这些是保存输出 token 的有符号差，不用能量方向、差值大小、局部稳定性或人为容差给模型分类，也不能借用 GPAW-PBE 能量作 oracle。下列力保留完整两原子 Cartesian 分量与负零，单位 Ha/Bohr。

| 记录 | 原子 | Fx（Ha/Bohr） | Fy（Ha/Bohr） | Fz（Ha/Bohr） |
| --- | --- | --- | --- | --- |
| cached-loose-baseline | 1 | -0.02690211036781 | -0.00000000000000 | -0.00000000000000 |
| cached-loose-baseline | 2 | 0.02690211036781 | -0.00000000000000 | -0.00000000000000 |
| A | 1 | -0.02690140666364 | -0.00000000000000 | -0.00000000000000 |
| A | 2 | 0.02690140666364 | -0.00000000000000 | -0.00000000000000 |
| B | 1 | -0.02136465667753 | -0.00000000000000 | -0.00000000000000 |
| B | 2 | 0.02136465667753 | -0.00000000000000 | -0.00000000000000 |

| 比较 | 原子 | ΔFx（Ha/Bohr） | ΔFy（Ha/Bohr） | ΔFz（Ha/Bohr） |
| --- | --- | --- | --- | --- |
| A-minus-cached-loose-baseline | 1 | 7.0370417E-7 | 0E-14 | 0E-14 |
| A-minus-cached-loose-baseline | 2 | -7.0370417E-7 | 0E-14 | 0E-14 |
| B-minus-A | 1 | 0.00553674998611 | 0E-14 | 0E-14 |
| B-minus-A | 2 | -0.00553674998611 | 0E-14 | 0E-14 |

每原子范数和两原子中的最大范数均保留向外舍入包络，以下最大值与两原子的相应区间一致；完整区间仍以 CSV 为准。这些是打印 token 的算术包络，不是创造出来的物理有效位数。

| 比较 | 最大原子力差范数下界（Ha/Bohr） | 上界（Ha/Bohr） |
| --- | --- | --- |
| A-minus-cached-loose-baseline | 7.03704159999E-7 | 7.03704180001E-7 |
| B-minus-A | 0.00553674998609 | 0.00553674998613 |

原始净力 ≤1e-5 Ha/Bohr 只是接口 smoke guard，不投影或修正力，也不证明个体原子力准确。几何固定，不能由净力抵消宣布平衡结构。

![保存设置差：两张能差图各用独立线性尺度并包含零；力差范数为不连线的正值对数点，单位 Ha 与 Ha/Bohr；没有收敛或物理大小分类](/Atlas/examples/abinit-h2/sensitivity/figures/setting-comparisons.png)

[图旁 CSV：能差区间和向外力范数界](/Atlas/examples/abinit-h2/sensitivity/figures/setting-comparisons.csv) · [原尺寸 PNG](/Atlas/examples/abinit-h2/sensitivity/figures/setting-comparisons.png)。图用浮点数显示，精确值、原 token 与区间在 CSV；独立能量面板尺度不能拿柱高直接互比。

## 密度裁剪与旧版本提示一起保留

[A stdout](/Atlas/examples/abinit-h2/sensitivity/cases/A/outputs/stdout.txt)和缓存记录在首次迭代前有一个可见严重负值告警：1275 点，最低 −0.34E−04（即 −3.4e-5）el/Bohr³，正下限 1e-14。[mkdenpos 非自旋分支](https://github.com/abinit/abinit/blob/9.10.4/shared/common/src/33_xc_lowlevel/m_drivexc.F90#L703-L717)把 `rho < +xc_denpos` 的值设为正下限，但 `numneg` 和最低值 `worst` 只统计 `rho < -xc_denpos`；[告警分支](https://github.com/abinit/abinit/blob/9.10.4/shared/common/src/33_xc_lowlevel/m_drivexc.F90#L773-L786)要求 `numneg>0` 且 `iwarn=0`。因此 1275 是严重负值告警计数，不是全部下限修改点数；`[-xc_denpos, +xc_denpos)` 中的值也可能被设为下限，却不触发这项告警。零可见告警不能证明没有这种下限修改。B 有零个可见 WARNING 块，仍保留不受支持的版本提示；这只是可见文本观察，不能说 B 没有裁剪。

[完整告警表](/Atlas/examples/abinit-h2/sensitivity/tables/warnings.json)不代替原始日志。按官方 9.10.4 标签源码，[rhotoxc 每次调用先置 iwarn=0](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L415-L425)；`iwarn` 只可能抑制[同一次调用的 ishift 循环](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L619-L630)内另一轮平移网格的严重负值告警。本例 `intxc=0`，只有[intxc=0 的单次网格遍历](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L619-L620)，不会因此静默后续 SCF 的新调用。此处解释的是该标签源码；尚未证明它与实际 Ubuntu 9.10.4-2ubuntu3 构建所用源码逐字等价。

A、B 的后续及最终 XC 裁剪前密度仍为 **UNKNOWN**：保存记录没有该时刻的 XC 工作缓冲区，下限附近的修改也不全由告警报告。不能从告警数或返回的密度文件倒推出完整修改次数、裁剪前最低值或最终未裁剪；UNKNOWN 不应归因于贯穿整个 SCF 的永久告警锁存。零/一个可见告警以及 DEN/GSR 不能充当最终未裁剪的证明。两点没有建立基组、网格、盒长、孤立分子、个体力、材料或实验准确性。

## 阅读输入输出与重放保存后处理

每点的 `inputs/h2.abi` 通过 `../data/H.psp8` 读取相邻赝势；原生输出是 `.abo`、stdout 和 stderr。A/B 的输入与完整输出都在下面索引中，科学调用已发生的历史保持两次、零重试。本页不发起新的科学计算。

如需复查表图，先按索引保存完整 44 项目录为 `saved-abinit-h2-sensitivity/`，保持 `cases/`、`sources/`、`tables/`、`figures/` 和脚本的相对布局。Python 3、PyYAML 6.0.1 与 Matplotlib 须已可用；此处不安装依赖。只在新副本执行：

```sh
(
set -eu
cp -R saved-abinit-h2-sensitivity replay-abinit-h2-sensitivity
cd replay-abinit-h2-sensitivity
python3 -B postprocess.py
)
```

[postprocess.py](/Atlas/examples/abinit-h2/sensitivity/postprocess.py)与[parse_saved.py](/Atlas/examples/abinit-h2/sensitivity/parse_saved.py)只读包内原生文本、输入、公开同版本源及 `raw-source-manifest.json`，先核源 SHA，再写本副本 `tables/` 的七项 CSV/JSON 与 `figures/` 的两组 CSV/PNG，共 11 项派生输出；`tables/regeneration-summary.json` 记录 A/B 十步、缓存六步、`native_invocations=0`。输入/源身份或解析检查失败会停止，不把解析退出当科学结论。这不是新的 ABINIT 求解，也不下载文件。独立复核已在另一目录重放并核对派生文件；任意新 Matplotlib 环境的 PNG 字节一致性未保证。本站作者本轮没有运行这些分析脚本。

公开原件中的 pending 或 NOT_PUBLISHED 字样保留生成时状态；本次已接受的范围是保存数据、公开源绑定及表图，网页本身仍待独立复核，尚未发布。

## 文件索引与许可

下面仅包含已核公开成员；可逐项打开或下载。自有解析、后处理、文字及派生表图为 MIT；ABINIT 同版本源、教程与输入衍生物按 GPL-3.0-or-later 及原许可例外，H 数据另为 CC BY 4.0。PseudoDojo 与 ONCVPSP 归属保留在 H-NOTICE；许可不能混套。没有原生二进制、deb 或 DEN/WFK/netCDF 文件。

- [README.md](/Atlas/examples/abinit-h2/sensitivity/README.md)
- [cases/A/data/H.psp8](/Atlas/examples/abinit-h2/sensitivity/cases/A/data/H.psp8)
- [cases/A/inputs/h2.abi](/Atlas/examples/abinit-h2/sensitivity/cases/A/inputs/h2.abi)
- [cases/A/inputs/h2.abo](/Atlas/examples/abinit-h2/sensitivity/cases/A/inputs/h2.abo)
- [cases/A/outputs/stderr.txt](/Atlas/examples/abinit-h2/sensitivity/cases/A/outputs/stderr.txt)
- [cases/A/outputs/stdout.txt](/Atlas/examples/abinit-h2/sensitivity/cases/A/outputs/stdout.txt)
- [cases/B/data/H.psp8](/Atlas/examples/abinit-h2/sensitivity/cases/B/data/H.psp8)
- [cases/B/inputs/h2.abi](/Atlas/examples/abinit-h2/sensitivity/cases/B/inputs/h2.abi)
- [cases/B/inputs/h2.abo](/Atlas/examples/abinit-h2/sensitivity/cases/B/inputs/h2.abo)
- [cases/B/outputs/stderr.txt](/Atlas/examples/abinit-h2/sensitivity/cases/B/outputs/stderr.txt)
- [cases/B/outputs/stdout.txt](/Atlas/examples/abinit-h2/sensitivity/cases/B/outputs/stdout.txt)
- [cases/cached-loose-baseline/data/H.psp8](/Atlas/examples/abinit-h2/sensitivity/cases/cached-loose-baseline/data/H.psp8)
- [cases/cached-loose-baseline/inputs/h2.abi](/Atlas/examples/abinit-h2/sensitivity/cases/cached-loose-baseline/inputs/h2.abi)
- [cases/cached-loose-baseline/inputs/h2.abo](/Atlas/examples/abinit-h2/sensitivity/cases/cached-loose-baseline/inputs/h2.abo)
- [cases/cached-loose-baseline/outputs/stderr.txt](/Atlas/examples/abinit-h2/sensitivity/cases/cached-loose-baseline/outputs/stderr.txt)
- [cases/cached-loose-baseline/outputs/stdout.txt](/Atlas/examples/abinit-h2/sensitivity/cases/cached-loose-baseline/outputs/stdout.txt)
- [figures/scf-residual.csv](/Atlas/examples/abinit-h2/sensitivity/figures/scf-residual.csv)
- [figures/scf-residual.png](/Atlas/examples/abinit-h2/sensitivity/figures/scf-residual.png)
- [figures/setting-comparisons.csv](/Atlas/examples/abinit-h2/sensitivity/figures/setting-comparisons.csv)
- [figures/setting-comparisons.png](/Atlas/examples/abinit-h2/sensitivity/figures/setting-comparisons.png)
- [license-map.json](/Atlas/examples/abinit-h2/sensitivity/license-map.json)
- [licenses/ABINIT-COPYING](/Atlas/examples/abinit-h2/sensitivity/licenses/ABINIT-COPYING)
- [licenses/ABINIT-Ubuntu-copyright](/Atlas/examples/abinit-h2/sensitivity/licenses/ABINIT-Ubuntu-copyright)
- [licenses/H-NOTICE.txt](/Atlas/examples/abinit-h2/sensitivity/licenses/H-NOTICE.txt)
- [licenses/OWN-ANALYSIS-MIT.txt](/Atlas/examples/abinit-h2/sensitivity/licenses/OWN-ANALYSIS-MIT.txt)
- [licenses/PseudoDojo-source-license-statement.md](/Atlas/examples/abinit-h2/sensitivity/licenses/PseudoDojo-source-license-statement.md)
- [measurement-provenance.json](/Atlas/examples/abinit-h2/sensitivity/measurement-provenance.json)
- [official-source-provenance.json](/Atlas/examples/abinit-h2/sensitivity/official-source-provenance.json)
- [parse_saved.py](/Atlas/examples/abinit-h2/sensitivity/parse_saved.py)
- [postprocess.py](/Atlas/examples/abinit-h2/sensitivity/postprocess.py)
- [raw-source-manifest.json](/Atlas/examples/abinit-h2/sensitivity/raw-source-manifest.json)
- [sources/base1.md](/Atlas/examples/abinit-h2/sensitivity/sources/base1.md)
- [sources/m_cgtools.F90](/Atlas/examples/abinit-h2/sensitivity/sources/m_cgtools.F90)
- [sources/m_common.F90](/Atlas/examples/abinit-h2/sensitivity/sources/m_common.F90)
- [sources/m_drivexc.F90](/Atlas/examples/abinit-h2/sensitivity/sources/m_drivexc.F90)
- [sources/m_rhotov.F90](/Atlas/examples/abinit-h2/sensitivity/sources/m_rhotov.F90)
- [sources/variables_abinit.py](/Atlas/examples/abinit-h2/sensitivity/sources/variables_abinit.py)
- [tables/measurements.json](/Atlas/examples/abinit-h2/sensitivity/tables/measurements.json)
- [tables/raw-forces.csv](/Atlas/examples/abinit-h2/sensitivity/tables/raw-forces.csv)
- [tables/regeneration-summary.json](/Atlas/examples/abinit-h2/sensitivity/tables/regeneration-summary.json)
- [tables/scf-records.csv](/Atlas/examples/abinit-h2/sensitivity/tables/scf-records.csv)
- [tables/settings.csv](/Atlas/examples/abinit-h2/sensitivity/tables/settings.csv)
- [tables/signed-comparisons.csv](/Atlas/examples/abinit-h2/sensitivity/tables/signed-comparisons.csv)
- [tables/warnings.json](/Atlas/examples/abinit-h2/sensitivity/tables/warnings.json)
