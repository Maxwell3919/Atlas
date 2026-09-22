[Materials Project：形成能与相图方法](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds) · [QE：pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [AFLOW：晶体原型库](https://aflow.org/prototype-encyclopedia/)

[下载同一批形成能与凸包数据](/Atlas/examples/alsi-formation-hull-files.tar.gz)。解压后进入 `alsi-formation-hull`，可直接从原始输出重算表格和图。

形成能页已经把五个候选放在同一套参考能上。现在要回答的是：在某个成分处，允许这些候选彼此混合，最低的能量在哪里？先沿用 [形成能计算](/Atlas/m/formation-energy/qe/) 的数据，结构优化、SCF 与端元处理都从那里进入。这里不重新提交这些计算。

本次集合只有 fcc Al、diamond Si、B2 AlSi、L1₂ Al₃Si 与 L1₂ AlSi₃。图上横轴是 **Si 的原子分数** `x=N(Si)/[N(Al)+N(Si)]`，纵轴是 **每原子形成能**。每个成分只放入了这次真正计算的一个原型，因此这是一张有限候选集的下凸包。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ head -n 6 formation-summary.csv
case,natoms,xSi,total_energy_Ry,formation_eV_atom,above_hull_eV_atom
al-fcc,1,0.0,-5.039590195089586,0.0,0.0
al3si-l12,4,0.25,-26.50736500358702,0.10725675700580338,0.10725675700580338
alsi-b2,2,0.5,-16.420651190216674,0.2657622360640055,0.2657622360640055
alsi3-l12,4,0.75,-39.192394827064,0.36591606137492194,0.36591606137492194
si-diamond,2,1.0,-22.84025464653608,0.0,0.0
[preston@preston-System-Product-Name alsi-formation-hull]$
```

Al 端元的 x=0，Si 端元的 x=1；Al₃Si、AlSi、AlSi₃ 依次在 0.25、0.5、0.75。Si 输入里有两个原子，仍然是 x=1；不能把晶胞原子个数当成组分轴，也不能让四原子晶胞的总能直接和一原子端元的总能比高低。

先用两端元在 x=0.25 处构造一个混合物：其原子分数是 75% Al、25% Si。两端元的形成能都按定义设为零，所以这条连线上任意成分的形成能都是零。与 Al₃Si 晶胞对应的分解反应可写成 `Al₃Si → 3 Al + Si`；方程里的 3:1 是原子数比，图中的权重则是 0.75:0.25。

```text
hull_energy(x) = w_left × ΔE_form(left) + w_right × ΔE_form(right)
w_right = (x − x_left) / (x_right − x_left)
w_left = 1 − w_right
energy_above_hull(x) = ΔE_form(candidate) − hull_energy(x)
```

这些式子也适用于端元之间存在更低中间相的情况；那时要用包住目标成分的两个相邻凸包顶点，不能永远减零。本次三个中间候选都高于 Al–Si 端元连线，所以计算得到的凸包顶点只有两个端元。

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

| 候选 | xSi | 下凸包 / eV·atom⁻¹ | 高于下凸包 / meV·atom⁻¹ | 对应端元组合 |
| --- | --- | --- | --- | --- |
| al-fcc | 0.0 | 0.000000 | 0.000 | 1.00 Al + 0.00 Si（原子分数） |
| al3si-l12 | 0.25 | 0.000000 | 107.257 | 0.75 Al + 0.25 Si（原子分数） |
| alsi-b2 | 0.5 | 0.000000 | 265.762 | 0.50 Al + 0.50 Si（原子分数） |
| alsi3-l12 | 0.75 | 0.000000 | 365.916 | 0.25 Al + 0.75 Si（原子分数） |
| si-diamond | 1.0 | 0.000000 | 0.000 | 0.00 Al + 1.00 Si（原子分数） |

这个距离是相同成分下，相对于本集合允许的最低能量组合的差值。它并没有把“所有可能结构”装进表里：补入其它原型、降对称结构、不同磁态或其它候选，都可能改变下凸包。对这三个正形成能候选，仅用端元就已经给出了更低的组合；这个有限集合的结论无需把它们叫成完整 Al–Si 相图。

提取脚本先按 x 排序，再逐个保留使相邻连线斜率递增的点，得到下边界；然后把每个候选投到对应的边界线段上，计算高度差。处理数值误差时使用很小的几何比较阈值，并保留未四舍五入的形成能。画图时才格式化小数位。代码在 [analyse_alsi.py](/Atlas/examples/alsi-formation-hull/analyse_alsi.py)，输入汇总在 [formation-energy.csv](/Atlas/examples/alsi-formation-hull/formation-energy.csv)；原始 30 项协议对照在 [energy-table.csv](/Atlas/examples/alsi-formation-hull/energy-table.csv)。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ python3 plot_alsi.py hull
plots/convex-hull.png and plots/convex-hull.svg
[preston@preston-System-Product-Name alsi-formation-hull]$
```

![五个真实计算候选的下凸包](/Atlas/examples/alsi-formation-hull/plots/convex-hull.svg)

蓝线连接本集合中的下凸包顶点；方块是三个构造的中间候选；竖直虚线的长度就是表中的能量差。图的横轴是原子分数，纵轴已除以每个晶胞的总原子数。两种端元的零点来自形成能定义，原始 DFT 总能本身都不是零。

绘图只需要 Python、NumPy、Matplotlib 和 CSV。把 [plot_alsi.py](/Atlas/examples/alsi-formation-hull/plot_alsi.py) 与 [formation-energy.csv](/Atlas/examples/alsi-formation-hull/formation-energy.csv) 放在同一目录，运行 `python3 plot_alsi.py hull`；图像写入 `plots/convex-hull.png` 和 `plots/convex-hull.svg`。要同时重画形成能与参数差值图，再加入 [numerical-checks.csv](/Atlas/examples/alsi-formation-hull/numerical-checks.csv) 并运行 `python3 plot_alsi.py all`。

这批 20³→24³ 的形成能最大变化为 1.344 meV/atom，优化与最终静态的压力差也已在前一页给出。图上的正值来自本次电子能量计算；其中没有声子零点能、振动熵或组态熵，不能把这条线当成某个实验温度下的相界。所有候选均受限于指定立方原型，原子力小也不等于声子稳定。

如果后续发现一个新的同成分结构，先按匹配协议计算它的能量，再把对应的真实记录加入候选集合并重建下凸包。要检查现有候选是否存在畸变方向，可接到 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/)；看到负频后，沿 [虚频排查](/Atlas/m/imaginary-phonon/qe/) 核对结构、原始频率和数值设置。

```text
同协议元素与候选总能 → 每原子形成能
                            ↓
                    成分—能量有限候选集
                            ↓
                       构造下凸包
                            ↓
                 相邻顶点组合与 energy above hull
                            ↓
                  新候选 / 声子 / 有限温度项
```
