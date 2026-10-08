# ABINIT H₂：固定 NC-LDA 模型的六步原生 SCF

ABINIT 安装、版本与调用 · [软件算例](/Atlas/software/)

这是 Ubuntu `9.10.4-2ubuntu3`（原生 ABINIT 9.10.4）直接单进程的一次保存观察。独立复核已接受该固定输入、精确原生输出、停止记录和派生表图的公开教学范围。没有新增计算，没有结构优化、基组/盒长或单原子力准确性接受。公开 README/JSON 中的 pending review 是生成当时的历史标签，原样保留；网页的接受范围另行说明，不改历史报告。

## 固定模型与停止条件

H₂ 位于 10 × 10 × 10 Bohr 周期盒，两个 H 的 x 坐标为 −0.7 与 +0.7 Bohr，几何固定。NC、标量相对论、LDA Perdew–Wang PSP8（`ixc=-1012`）；平面波截断 10 Ha，单 Γ 点，最多 10 步，`toldfe=1e-6 Ha`，`diemac=2`。输入与 H 文件保持精确审定字节。

实际日志显示六条 ETOT 和原生能量停止标记。`toldfe` 要求连续两次总能量变化绝对值低于阈值，不是密度、力或基组准确性阈值。保存的精确末三步能量给出 $|E_5-E_4|=6.85479\times10^{-8}$ Ha 与 $|E_6-E_5|=4.681\times10^{-10}$ Ha；最终 $E_6=-1.1171843463443$ Ha。程序退出和此停止条件分别核过；它们仍不等于材料物理准确性。

## 密度裁剪：必须随结果一起读

首次 ITER 之前，原生告警报告 1275 个严重负值点，最低 `−3.4e-5 el/Bohr³`，正下限 `xc_denpos=1e-14`；不能归为无关舍入噪声。[mkdenpos 非自旋分支](https://github.com/abinit/abinit/blob/9.10.4/shared/common/src/33_xc_lowlevel/m_drivexc.F90#L703-L717)把 `rho < +xc_denpos` 的值设为正下限，但 `numneg` 和最低值 `worst` 只统计 `rho < -xc_denpos`；[告警分支](https://github.com/abinit/abinit/blob/9.10.4/shared/common/src/33_xc_lowlevel/m_drivexc.F90#L773-L786)要求 `numneg>0` 且 `iwarn=0`。因此 1275 是严重负值告警计数，不是全部下限修改点数；`[-xc_denpos, +xc_denpos)` 中的值也可能被设为下限，却不触发这项告警。零可见告警不能证明没有这种下限修改。

按官方 9.10.4 标签源码，[rhotoxc 每次调用先置 iwarn=0](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L415-L425)；`iwarn` 只可能抑制[同一次调用的 ishift 循环](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L619-L630)内另一轮平移网格的严重负值告警。本例 `intxc=0`，只有[intxc=0 的单次网格遍历](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L619-L620)，不会因此静默后续 SCF 的新调用。此处解释的是该标签源码；尚未证明它与实际 Ubuntu 9.10.4-2ubuntu3 构建所用源码逐字等价。

后续及最终 XC 裁剪前密度仍为 **UNKNOWN**：保存记录没有该时刻的 XC 工作缓冲区，下限附近的修改也不全由告警报告。不能从告警数或返回的密度文件倒推出完整修改次数、裁剪前最低值或最终未裁剪；UNKNOWN 不应归因于贯穿整个 SCF 的永久告警锁存。`warnings.json` 中历史 `no_native_warnings_suppressed` 指保存过程未删原始日志，不证明没有下限修改。完整 stdout/abo 保留初始警告及 9.10.4 不受支持的 notice；固定 Ubuntu 路线是已有记录复现入口，不是当前生产版本建议。

## 六步 ETOT 与原生力

[精确 ETOT CSV](/Atlas/examples/abinit-h2/scf-ledger.csv) · [完整 h2.abo](/Atlas/examples/abinit-h2/inputs/h2.abo) · [stdout](/Atlas/examples/abinit-h2/outputs/h2.stdout)

| 实际步 | 总能量（Ha） | 相邻精确能差（Ha） |
| --- | --- | --- |
| 1 | -1.1093804698962 | — |
| 2 | -1.1170431098364 | -0.0076626399402 |
| 3 | -1.1171736936408 | -0.0001305838044 |
| 4 | -1.1171842773283 | -0.0000105836875 |
| 5 | -1.1171843458762 | -6.85479E-8 |
| 6 | -1.1171843463443 | -4.681E-10 |

[完整力 CSV](/Atlas/examples/abinit-h2/forces.csv)，保留两个原子的所有分量，包括原生负零；单位 Ha/Bohr。

| 原子 | Fx（Ha/Bohr） | Fy（Ha/Bohr） | Fz（Ha/Bohr） |
| --- | --- | --- | --- |
| 1 H | -0.02690211036781 | -0E-14 | -0E-14 |
| 2 H | 0.02690211036781 | -0E-14 | -0E-14 |

原始力和在显示精度为零，通过 `1e-5 Ha/Bohr` 的净力 smoke guard。这只检查抵消；对称性本身可强制净零，不证明 individual force accuracy，也不表示结构已达平衡。与 GPAW 的 PBE/PAW 不同模型不能拿总能量作跨引擎 oracle。

## 图与逐点数据

![ABINIT 9.10.4 固定 NC-LDA H₂：10 Ha / 10 Bohr；相对末态能量及相邻绝对能差，单位 Ha；toldfe=1e-6 Ha；基组、盒长、力准确性未确立](/Atlas/examples/abinit-h2/figures/scf-convergence.png)

[图旁 CSV：每个实际 SCF 点及 Ha 单位](/Atlas/examples/abinit-h2/figures/scf-convergence.csv) · [原 PNG](/Atlas/examples/abinit-h2/figures/scf-convergence.png) · [原 SVG](/Atlas/examples/abinit-h2/figures/scf-convergence.svg)。末态是本次保存计算的末态；图不是另一次求解，也不验证 cutoff/box 精度。

## 公开文件与许可

下面 22 项按原布局逐字提供。下载后以 `saved-abinit-h2/` 为根，保留 `inputs/../data/`；输入和所有数值不作网页清理或替换。无二进制和 deb。解析与绘图只能在新副本中执行，命令与 IN/OUT 见工具页。

- [README.md](/Atlas/examples/abinit-h2/README.md)
- [data/H.psp8](/Atlas/examples/abinit-h2/data/H.psp8)
- [echoed-native-settings.json](/Atlas/examples/abinit-h2/echoed-native-settings.json)
- [figures/scf-convergence.csv](/Atlas/examples/abinit-h2/figures/scf-convergence.csv)
- [figures/scf-convergence.png](/Atlas/examples/abinit-h2/figures/scf-convergence.png)
- [figures/scf-convergence.svg](/Atlas/examples/abinit-h2/figures/scf-convergence.svg)
- [forces.csv](/Atlas/examples/abinit-h2/forces.csv)
- [inputs/h2.abi](/Atlas/examples/abinit-h2/inputs/h2.abi)
- [inputs/h2.abo](/Atlas/examples/abinit-h2/inputs/h2.abo)
- [licenses/ABINIT-COPYING](/Atlas/examples/abinit-h2/licenses/ABINIT-COPYING)
- [licenses/ABINIT-Ubuntu-copyright](/Atlas/examples/abinit-h2/licenses/ABINIT-Ubuntu-copyright)
- [licenses/H-NOTICE.txt](/Atlas/examples/abinit-h2/licenses/H-NOTICE.txt)
- [licenses/PseudoDojo-source-license-statement.md](/Atlas/examples/abinit-h2/licenses/PseudoDojo-source-license-statement.md)
- [native-criterion-checks.json](/Atlas/examples/abinit-h2/native-criterion-checks.json)
- [official-source-provenance.json](/Atlas/examples/abinit-h2/official-source-provenance.json)
- [outputs/h2.stderr](/Atlas/examples/abinit-h2/outputs/h2.stderr)
- [outputs/h2.stdout](/Atlas/examples/abinit-h2/outputs/h2.stdout)
- [parse-native.py](/Atlas/examples/abinit-h2/parse-native.py)
- [plot-native.py](/Atlas/examples/abinit-h2/plot-native.py)
- [run-metadata.json](/Atlas/examples/abinit-h2/run-metadata.json)
- [scf-ledger.csv](/Atlas/examples/abinit-h2/scf-ledger.csv)
- [warnings.json](/Atlas/examples/abinit-h2/warnings.json)

ABINIT GPL-3.0-or-later 与少量其他许可依上述 COPYING/Ubuntu copyright；H 数据独立 CC BY 4.0，保留 PseudoDojo/ONCVPSP 归属。本次接受的是固定设置的原生保存观察及公开教学文件，不包含结构/材料/实验结论。原生程序、Ubuntu 包和同版本教程来源详见工具页与 `official-source-provenance.json`。
