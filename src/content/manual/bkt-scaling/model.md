[Nelson–Kosterlitz 的普适跃变](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.39.1201) · [经典二维 XY 模型的有限尺寸研究](https://arxiv.org/abs/cond-mat/0502556) · [NumPy 随机数生成器](https://numpy.org/doc/stable/reference/random/generator.html)

把一个小箭头放在每个格点上，相邻箭头越平行，能量越低。升高温度后，局部方向会波动；绕某个小方格走一圈，方向还可能完整转过一周。这一页实际运行这样的二维 XY 模型，看自旋构型、涡旋和相位刚度怎样随温度与尺寸变化。

这里是独立的经典统计模型，使用 Python 与 NumPy，不读取 DFT 输入，也没有将参数对应到 SnSe₂/Sr₂N 或其他材料。以 J 作为能量单位、J/kB 作为温度单位；程序令 J=kB=1，因此输入 0.92 表示 kB·T/J=0.92。下文和原始输出中的 T/J 是这一约定下的简写，不能直接标为 K。一次 Monte Carlo sweep 是抽样操作，不是飞秒、皮秒或真实自旋动力学时间。

[下载完整算例](/Atlas/examples/xy-bkt-files.tar.gz)后，可以查看全部随机种子、热化记录、抽样序列和末态构型。[mc.py](/Atlas/examples/xy-bkt/mc.py) 是完整计算输入，[analyse.py](/Atlas/examples/xy-bkt/analyse.py) 提取相位刚度与误差，[verify.py](/Atlas/examples/xy-bkt/verify.py) 核对保存数据，[plot.py](/Atlas/examples/xy-bkt/plot.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/xy-bkt/atlas_plot_style.py)） 重新作图。

## 把模型、边界和一次更新说清楚

方格有 L×L 个格点，两个方向都周期连接。每个格点保存一个角 θ，哈密顿量为

```text
H/J = −Σ cos(θ[i+1,j] − θ[i,j]) − Σ cos(θ[i,j+1] − θ[i,j])
```

两个求和都遍历全格点，下标按 L 取模。每条最近邻键只计一次；所有角都相同时，H/(NJ)=−2，其中 N=L²。这给程序提供了一个容易核对的零温构型。

本次取 L=8、16、24。温度依次为 0.70、0.80、0.88、0.92、1.00、1.10；每种尺寸和温度有两个独立种子，一个从全同向角开始，另一个从 [−π,π) 的随机角开始，共 36 条基础轨迹。改变初态，是为了检查短热化是否仍留下可见影响。

更新采用固定幅度的 Metropolis 提议：给某个角加一个均匀分布在 [−π/2,π/2] 的扰动，计算它与四个邻居之间的能量变化 ΔH，再以 `min(1, exp(−ΔH/T))` 的概率接受。没有在正式采样中继续调整提议幅度。

程序把格点分为棋盘上的黑白两组。同一组中没有最近邻键，可以同时更新；先更新一组，再更新另一组，构成一次 sweep，每个自旋被尝试一次。本例的 L 都是偶数，因此跨周期边界后仍保持这项分组性质。不能原样把这个更新方式用到奇数边长的周期方格。

## 先计时，再提交这一批短轨迹

这次在 Talos 的独立普通目录运行，NumPy 版本为 2.4.6。两个工作进程分别做不同参数的轨迹，每个进程限定一个线程，不需要 Slurm，也没有安装额外软件。

```console
talos@talos-MS-7D54:~/xy-bkt$ export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
talos@talos-MS-7D54:~/xy-bkt$ python3 -B mc.py --benchmark > benchmark.out 2> benchmark.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ cat benchmark.out
SELF_CHECK {"ordered_energy_per_spin": -2.0, "random_local_delta_energy_max_error": 1.5543122344752192e-15, "periodic_net_vorticity": 0, "numpy": "2.4.6"}
BENCHMARK L24 1000 sweeps = 0.176617 s; 36 base + 8 extension cases at 2 workers estimated < 93.6 s plus I/O
```

第一行先核对全同向构型的能量，又对随机构型做了 25 次单自旋变化，将局部公式的 ΔH 与整个体系重新求和的能量差对照，最大差为 1.55×10⁻¹⁵。它检查更新公式，不代表热化或采样已经充分。

正式基础批次的命令是：

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B mc.py --base > base.out 2> base.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ tail -4 base.out
FINISHED base/L24-T1.00-s2026094609 samples=4000 acceptance=0.5436 wall=5.27s
FINISHED base/L24-T1.10-s2026094610 samples=4000 acceptance=0.5832 wall=5.35s
FINISHED base/L24-T1.10-s2026094611 samples=4000 acceptance=0.5836 wall=5.32s
MONTE_CARLO_FINISHED 36 cases wall=75.38s
```

每条轨迹先丢弃 5000 sweep 作为热化段，再进行 20000 sweep 的正式抽样，每隔五次记录一次，因此留下 4000 行。热化序列单独保存在 `warmup.csv`，没有与正式序列混在一起平均。运行中可以用 `tail -f base.out` 看哪些参数已完成，用 `tail -f base.err` 看异常；末尾没有出现的参数仍可能在运行，不能据已有几行就认定全批次结束。

目录名中的 s 后面就是随机种子。以 L=24、T/J=0.92 的全同向起态为例，`run.json` 记录 seed=2026094606、5000 次热化、20000 次正式 sweep、4000 次测量，正式接受率为 0.5171571181。同组随机起态用另一个种子 2026094607，两条轨迹并非把同一段序列复制两次。

## 原始序列里存了什么

```console
talos@talos-MS-7D54:~/xy-bkt$ head -4 base/L24-T0.92-s2026094606/series.csv
sweep,energy_per_spin,M2,cos_x,cos_y,current_x,current_y,current_x2,current_y2,vortex_abs_density
5.000000000000000000e+00,-1.387290803993360022e+00,2.337981439126416983e-01,4.012807560977712455e+02,3.977987470024040704e+02,1.025602657115940275e+01,6.943740528079212382e+00,1.051860810283276919e+02,4.821553252128978073e+01,2.083333333333333218e-02
1.000000000000000000e+01,-1.335394938149527366e+00,2.501137036302885641e-01,3.785037986647218986e+02,3.906836857094058360e+02,5.871106822454554397e+00,5.510315311576374775e+00,3.446989532067241413e+01,3.036357483299304150e+01,1.736111111111111188e-02
1.500000000000000000e+01,-1.426929403562417376e+00,3.185028587959647939e-01,4.126565016448240044e+02,4.092548348071283044e+02,8.377220335896305770e+00,1.037883624951718353e+01,7.017782055615461445e+01,1.077202418942919167e+02,2.083333333333333218e-02
```

`energy_per_spin` 是 H/(NJ)。`M2` 是单位自旋平均矢量的模平方，有限小格子的非零值不能直接当成热力学极限的长程磁序。`cos_x` 与 `cos_y` 是两个方向全部键余弦的和；两者之和取负、除以 N，应该还原该行能量。

`current_x` 与 `current_y` 分别保存相邻角差正弦的总和，后两列是它们各自的平方。这里的 current 是计算扭转响应所需的模型量，不是安培单位的电流。把这些一阶、二阶矩分别存下来，才能重算涨落项，不能先对每一步随意定义一个“瞬时刚度”再忽略相关性。

最后一列是每个小方格涡旋电荷绝对值的平均。沿小方格四条边，把每个角差回卷到 [−π,π)，总和除以 2π并核对整数，得到电荷 q。一个周期方格的全部电荷和应为零；这一点在每次测量中都检查过。

## 刚度要连着误差一起读

在本页 J=1 的约定下，两个方向平均的 helicity modulus 为

```text
Y = { <Cx+Cy> − [Var(Ix)+Var(Iy)]/T } / (2N)
```

这里 Y 的单位是 J，方差保留 `<I²>−<I>²`。有些文章定义的是 Y/T；那种无量纲量对应的参考值是 2/π。本页画的是 Y/J，因此参考线是 2T/π，不能混用这两个约定。

连续测量会相关，4000 行并不等于 4000 个独立样本。本次把每条轨迹分成 16 个连续块，做删一块 jackknife，重新计算整个含方差的 Y；另外保留 8 块和 32 块的误差结果。基础轨迹每块覆盖 1250 sweep，加长后的每块覆盖 2500 sweep。 分块数改变时误差仍有波动：全部轨迹的 8/16 与 32/16 块误差比范围为 0.300–1.384，其中一条 L=8、T/J=0.80 轨迹的 8 块、16 块误差分别为 0.000515、0.001718。因此本页不把这些诊断误差写成已形成稳定平台的误差估计。

能量及电流平方的自相关时间也随原始序列估计。这次诊断值约为 2.89–52.20 sweep，最短的分块仍约为较大自相关估计的 23.9 倍。这是有限序列上的相关性检查，尤其不能证明局部 Metropolis 已充分访问所有绕行扇区。

合并两个种子时，中心值取两条轨迹估计的平均。图中的误差取“轨迹内分块误差合并值”和“两种子结果差的一半”中较大者。这是明确给出构造方法的诊断误差条，不是已校准的置信区间。每条种子的结果也保留在 [cases.csv](/Atlas/examples/xy-bkt/results/cases.csv)，没有只留下合并曲线。

## 将八条轨迹加长到 40000 sweep

L=16、24 在 T/J=0.88、0.92 的两个种子都继续到 40000 正式 sweep，共八条加长轨迹。程序从各自末态角度和 RNG 状态继续，不再重新热化；原 20000 sweep 数据保持在 `base/`，加长记录单独保存在 `extended/`。

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B mc.py --extended > extended.out 2> extended.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ tail -4 extended.out
FINISHED extended/L24-T0.88-s2026094605 samples=8000 acceptance=0.5046 wall=4.36s
FINISHED extended/L24-T0.92-s2026094606 samples=8000 acceptance=0.5167 wall=4.28s
FINISHED extended/L24-T0.92-s2026094607 samples=8000 acceptance=0.5173 wall=4.42s
MONTE_CARLO_FINISHED 8 cases wall=15.59s
```

加长不保证每个数都静止。例如 L=16、T/J=0.92 的全同向起态，Y 从 0.623675±0.006564 变为 0.613795±0.004536；L=24 同温度的随机起态从 0.612411±0.005743 变为 0.604368±0.008524。这些变化和误差一起保留在 [extension-comparison.csv](/Atlas/examples/xy-bkt/results/extension-comparison.csv)。前后两份估计包含重叠样本，不能把它们当成两次独立实验做显著性检验。

![加长抽样前后的刚度与能量分块记录](/Atlas/examples/xy-bkt/figures/xy-sampling.png)

本次所检查的起态差异、前后半段差异没有越过脚本设置的三倍组合分块误差提示线。这个结果只说明这批检查没有检出那一级差异，不是充分热化的证明，更不是“再加长也不会变”。

## 有限尺寸曲线与 2T/π 相遇在哪里

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B analyse.py > analyse.out 2> analyse.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ head -19 analyse.out
L  T/J    Y/J      display_error   seed_delta/error  minimum_block/tau
 8 0.70  +0.785049   0.001336          1.97             314.4
 8 0.80  +0.734276   0.001520          1.13             252.9
 8 0.88  +0.681421   0.003004          0.54             222.7
 8 0.92  +0.652275   0.003858          0.15             169.8
 8 1.00  +0.570432   0.010481          2.25             136.4
 8 1.10  +0.443103   0.014112          1.73             102.1
16 0.70  +0.778496   0.000443          0.74             279.3
16 0.80  +0.721847   0.001557          1.15             128.8
16 0.88  +0.663836   0.002284          0.44             235.9
16 0.92  +0.614160   0.003609          0.10             117.9
16 1.00  +0.490403   0.011392          1.06             51.9
16 1.10  +0.256825   0.020686          1.43             34.3
24 0.70  +0.778040   0.000581          0.07             236.0
24 0.80  +0.720485   0.001789          0.94             44.6
24 0.88  +0.651180   0.003518          1.12             80.7
24 0.92  +0.610133   0.005765          1.20             66.3
24 1.00  +0.455445   0.022363          1.57             30.7
24 1.10  +0.163436   0.023722          0.88             23.9
```

![三个有限尺寸的相位刚度、参考线与涡旋密度](/Atlas/examples/xy-bkt/figures/xy-helicity.png)

三个尺寸的平均曲线都在采样温度 0.92 与 1.00 之间越过 2T/π。这里没有把两点连线的交点报成 T_BKT：温度间隔还很粗，体系也只有 8²、16²、24²。三个尺寸落在同一温度区间，不能说明尺寸效应已经消失。

右图的涡旋密度随温度增加。它能帮助理解局部角度缺陷如何出现，但仅有密度还没有区分束缚对与自由涡旋，也没有建立热力学极限的 BKT 标度。要研究极限温度，应在更大尺寸上结合对数有限尺寸修正、相关性和更充分的抽样，不能把三个小系统的曲线硬拟合成一个精确数字。

## 把涡旋放在实际构型上看

![实际抽样得到的二维XY构型与涡旋位置](/Atlas/examples/xy-bkt/figures/xy-configurations.png)

箭头来自保存的末态角度，圆圈与方框标记 q=+1 与 q=−1 的小格子中心。它们是某一次构型的快照，不能代替系综平均；周期边缘的箭头和缺陷也需要与另一侧连接起来阅读。图片中的种子写在标题上，可以回到相应目录的 `final-angles.csv` 和 `final-vortices.csv` 核对。

保存数据另做了一次独立检查：用普通循环重新计算全部 44 份末态的能量与涡旋，最大每自旋能量差 2.66×10⁻¹⁵，涡旋电荷逐格一致。八份加长序列的前 4000 行与原数据完全相同；从记录的随机种子重放前 100 次热化，在原 Talos 环境中也精确复现了两次已保存测量。Mac（NumPy 2.3.4）重算这两行时最大差为 7.11×10⁻¹⁵，来自浮点求值与归约的微小差别；下载脚本对这项短重放采用 `rtol=1e-13, atol=1e-13` 的检查。加长序列与原序列的已保存前缀仍要求逐项完全相同，涡旋整数也严格核对。不同 NumPy 版本或硬件上的长随机轨迹不承诺逐位相同；一次接受分支的微小变化就可能使后续路径分开。

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B verify.py > verify.out 2> verify.err; echo "exit=$?"
exit=0
```

[检查记录](/Atlas/examples/xy-bkt/results/independent-check.json)和[完整输出](/Atlas/examples/xy-bkt/verify.out)随包保存。基础抽样、加长抽样、分析与独立检查的最终错误文件均为空；程序结束与统计收敛仍是两项不同判断。

## 下载后继续使用这些数据

已有结果可以直接出图，不必重新抽样。在解压后的 `xy-bkt` 目录，以有 NumPy、Matplotlib 的 Python 运行：

```bash
python3 plot.py
```

它读取原始 CSV 和末态构型，输出 `figures/xy-helicity.png`、`xy-configurations.png`、`xy-sampling.png` 及对应 PDF。图中连线连接实际计算的六个温度点。

相位刚度图读取 `results/helicity.csv` 的 18 行汇总，即 3 个尺寸各 6 个温度。横轴来自 `temperature_J`，纵轴来自 `Y_J`，误差棒使用 `display_error_J`：它取链内分块误差与两个种子之间误差估计的较大者。重画时不要误选单个种子的标准差，也不要把这列再除以样本数。`reference_2T_over_pi` 保存了同一温度的参考值；曲线交点仍只属于这些有限尺寸与离散温度的比较。

加长抽样图读取 `results/extension-comparison.csv`，能量分块记录则来自 `extended/` 中对应两条 L=24、T/J=0.92 链的 `series.csv`。快照读取按名称排序后选定的 L=24 低温与高温目录，并从其中的 `run.json` 取种子。要换一份快照，应同时换它的 `final-angles.csv`、`final-vortices.csv` 与标题中的种子，不能只换箭头图而留下另一条链的缺陷标记。

论文图使用 [Nature 要求的可编辑矢量输出](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)时，在创建画布前选择已安装的 Arial/Helvetica 并设置 `pdf.fonttype=42`；保留现有 PDF 保存步骤即可，字体与布局需重新导出。网页图使用适合屏幕的字号，论文副本再按最终版面检查 5—7 pt 正文与 8 pt 面板号。文字、图例和坐标保持黑色，尺寸 L 用不同标记或线型辅助区分颜色。

快照里箭头方向已经表示角度；若继续用颜色编码角度，应补上带弧度单位的色标，否则可使用单色箭头。q=+1 和 q=−1 继续用圆圈与方框区分，不能只剩红蓝颜色。坐标表示格点位置，可标为 `x / a`、`y / a`，其中 a 是方格间距；这不是材料的 Å 坐标。`2T/π` 参考线、误差棒和周期边界附近的涡旋都保留，不能在整理画面时删掉。

若要重新运行，把四份 Python 脚本复制到一个新的空目录，先做 `--benchmark`，再按 `--base → --extended → analyse.py → verify.py` 的顺序执行。`mc.py` 会拒绝覆盖已有 case 目录；这使原始抽样记录可以保留下来比较。已有包中的 `base/` 与 `extended/` 是结果，不要在原处重跑后覆盖。

下一步可对照[有限尺寸研究中的对数修正](https://arxiv.org/abs/cond-mat/0502556)，设计更大 L、更密温度点和更充分的抽样。本页完成的是无量纲二维模型的数值教案；若要谈真实二维材料，需要另外建立材料参数与有效模型之间的对应关系。

```text
H、J=kB=1、周期边界
  → 两种起态与独立种子
  → 热化记录 → 正式抽样序列
  → 能量 / 涡旋 / helicity modulus
  → 分块误差、相关性、加长抽样
  → 有限尺寸曲线与2T/π对照
  → 更大尺寸与标度检查后，才讨论热力学极限
```
