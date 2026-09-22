[ph.x 输入与 EPC 选项](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [QE 声子线宽和逐模 λ 定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html) · [matdyn.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)

一个声子频率只告诉我们这个振动有多快。电子声子计算还会给出线宽 γ：在 QE 采用的定义下，它包含该模式与费米面附近电子态的耦合及可用散射相空间。本页从真实输出里找到这些数字，把频率、γ 和 λ 放在同一行，再按 q 点比较。

这里沿用 [Al EPC 与 α²F](/Atlas/m/eliashberg-a2f/qe/) 的完整 4³ q 网格。SCF、致密网格与 ph.x 的输入在那里给出，本页从 `elph_dir` 开始。单原子 fcc Al 原胞只有三个声学分支，不存在本例中的光学分支。当前网格用来学习输出结构，尚未给出收敛的线宽预测。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al`，按正文运行绘图命令。

## 一个逐 q 文件的内部结构

先看第 2 个不可约 q 点的整个文件。与主 OUT 里的长迭代相比，这个文件更适合逐模式读数；但它仍须与原来的 q 点和 ph.x 输出对应。

```console
maxwell@maxwell:~/al/epc-q4$ cat elph_dir/elph.inp_lambda.2
          -0.176777      0.176777     -0.176777    10     3
  0.119399E-05  0.119399E-05  0.474424E-05
     Gaussian Broadening:   0.005 Ry, ngauss=   0
     DOS =  2.518161 states/spin/Ry/Unit Cell at Ef=  8.373640 eV
     lambda(    1)=  0.0484   gamma=    1.50 GHz
     lambda(    2)=  0.0468   gamma=    1.45 GHz
     lambda(    3)=  0.2363   gamma=   29.17 GHz
     Gaussian Broadening:   0.010 Ry, ngauss=   0
     DOS =  2.624685 states/spin/Ry/Unit Cell at Ef=  8.377216 eV
     lambda(    1)=  0.0659   gamma=    2.13 GHz
     lambda(    2)=  0.0639   gamma=    2.07 GHz
     lambda(    3)=  0.2128   gamma=   27.38 GHz
     Gaussian Broadening:   0.015 Ry, ngauss=   0
     DOS =  2.647439 states/spin/Ry/Unit Cell at Ef=  8.379158 eV
     lambda(    1)=  0.0619   gamma=    2.02 GHz
     lambda(    2)=  0.0596   gamma=    1.95 GHz
     lambda(    3)=  0.1934   gamma=   25.10 GHz
     Gaussian Broadening:   0.020 Ry, ngauss=   0
     DOS =  2.646097 states/spin/Ry/Unit Cell at Ef=  8.379914 eV
     lambda(    1)=  0.0599   gamma=    1.96 GHz
     lambda(    2)=  0.0576   gamma=    1.88 GHz
     lambda(    3)=  0.1845   gamma=   23.94 GHz
     Gaussian Broadening:   0.025 Ry, ngauss=   0
     DOS =  2.643523 states/spin/Ry/Unit Cell at Ef=  8.379582 eV
     lambda(    1)=  0.0585   gamma=    1.91 GHz
     lambda(    2)=  0.0567   gamma=    1.85 GHz
     lambda(    3)=  0.1813   gamma=   23.50 GHz
     Gaussian Broadening:   0.030 Ry, ngauss=   0
     DOS =  2.643829 states/spin/Ry/Unit Cell at Ef=  8.378390 eV
     lambda(    1)=  0.0579   gamma=    1.89 GHz
     lambda(    2)=  0.0566   gamma=    1.85 GHz
     lambda(    3)=  0.1831   gamma=   23.74 GHz
     Gaussian Broadening:   0.035 Ry, ngauss=   0
     DOS =  2.645823 states/spin/Ry/Unit Cell at Ef=  8.376691 eV
     lambda(    1)=  0.0579   gamma=    1.89 GHz
     lambda(    2)=  0.0571   gamma=    1.86 GHz
     lambda(    3)=  0.1884   gamma=   24.44 GHz
     Gaussian Broadening:   0.040 Ry, ngauss=   0
     DOS =  2.648339 states/spin/Ry/Unit Cell at Ef=  8.374776 eV
     lambda(    1)=  0.0583   gamma=    1.90 GHz
     lambda(    2)=  0.0578   gamma=    1.89 GHz
     lambda(    3)=  0.1952   gamma=   25.35 GHz
     Gaussian Broadening:   0.045 Ry, ngauss=   0
     DOS =  2.650827 states/spin/Ry/Unit Cell at Ef=  8.372817 eV
     lambda(    1)=  0.0589   gamma=    1.93 GHz
     lambda(    2)=  0.0586   gamma=    1.92 GHz
     lambda(    3)=  0.2023   gamma=   26.30 GHz
     Gaussian Broadening:   0.050 Ry, ngauss=   0
     DOS =  2.653067 states/spin/Ry/Unit Cell at Ef=  8.370889 eV
     lambda(    1)=  0.0596   gamma=    1.95 GHz
     lambda(    2)=  0.0594   gamma=    1.94 GHz
     lambda(    3)=  0.2091   gamma=   27.20 GHz
```

首行前三个数是 q 坐标，单位为 2π/alat；后面的 10 和 3 分别是电子展宽组数与模式数。第二行三个数是频率平方，单位为 Ry²，不是 THz，也不是 γ。后面每一组先打印 Gaussian 电子展宽和 DOS(EF)，再给三个模式各自的 λ 与 γ。这里 `gamma` 后面明写了 GHz。

0.020 Ry 这一组，第 3 模式的 λ=0.1845、γ=23.94 GHz；前两个模式的线宽分别为 1.96 和 1.88 GHz。它们的 λ 不能仅凭 γ 的大小同比例推断，因为 QE 的逐模关系还含有频率平方和 DOS(EF)：

**λ<sub>qν</sub> = γ<sub>qν</sub> / [π ℏ N(E<sub>F</sub>) ω<sub>qν</sub>²]**

本页保留程序的 γ 定义与 GHz 单位，不额外把它换成寿命。要与实验或其他程序比较，必须先核实半宽、全宽、角频率或普通频率的约定；不能直接把 `1/gamma` 标成一个确定的寿命。

## 回到主 OUT，核对它是哪三个振动

`al.elph.out` 中同一个 q 点的频率段为：

```text
     freq (    1) =       3.594799 [THz] =     119.909582 [cm-1]
     freq (    2) =       3.594799 [THz] =     119.909582 [cm-1]
     freq (    3) =       7.165696 [THz] =     239.021883 [cm-1]
```

这里第一、第二模式简并，频率相同；逐模 γ 与 λ 有小差异时，还需考虑简并子空间中本征矢的选择和数值精度，比较简并组的总贡献通常更稳妥。完整 OUT 还保留了电荷响应迭代、q 星的生成和模式对称性分析，可沿文件向上读，确认这些模式来自已结束的那个 q 点。

## 用带单位的数值核对 γ 与 λ

以第 2 个 q 点、第 3 模式、电子展宽 0.020 Ry 为例，原始文件给出 γ=23.94 GHz、频率 f=7.165696 THz、N(EF)=2.646097 states/spin/Ry/cell，打印 λ=0.1845。

QE 7.5 的 [elphsum 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/elphon.f90) 先按 `lambda = gamma / pi / w2 / dosfit` 计算，再把 gamma 乘 `RY_TO_GHZ` 写出。[单位常数](https://github.com/QEF/q-e/blob/qe-7.5/Modules/constants.f90) 定义 C=Ry/h=3289.841960251 THz。因此，将普通频率转回源码的 Ry 单位数值，得到 f/C=0.00217812773、γ/(1000C)=7.27694530×10⁻⁶，进而有：

```text
λ = γ_GHz × C / [1000 × π × N(EF) × f_THz²]
  = 23.94 × 3289.841960251 / [1000 × π × 2.646097 × 7.165696²]
  = 0.184512923
```

这个结果与输出的 0.1845 相符。原始 γ 只打印两位小数、λ 只打印四位小数，比较时要保留相应舍入误差。这里已经沿源码把 GHz、THz、Ry 的约定接起来，不应再额外乘 2π，也不应把程序打印的单自旋 DOS 擅自乘 2。

核对脚本 [linewidth_units.py](/Atlas/examples/al/epc-q4/linewidth_units.py) 对高于源码阈值的 210 行都做了上述比较；[输出](/Atlas/examples/al/epc-q4/linewidth-unit-check.out) 和 [检查记录](/Atlas/examples/al/epc-q4/linewidth-unit-check.json) 保留了数值与误差容许范围。

## Γ 点的零 λ 还包含程序阈值

原始 ph.x 在 Γ 三个声学模式上打印 0.087851 THz，即 2.930394 cm⁻¹。它们是小的声学残差，不是光学模。在 0.020 Ry 这一组，γ 实际为 0.09、0.09、0.11 GHz，但三个 λ 都为 0。

原因在本次 `electron_phonon='interpolated'` 所调用的 QE 7.5 `elphsum`：源码将 `epsw` 设为 20 cm⁻¹，只有频率高于这个阈值才使用 γ、频率平方和 DOS 计算 λ，否则直接将 λ 设为零；γ 仍照常打印。这三个残差模式落在阈值之下，因此不能把输出的零 λ 当作已经证明的物理零耦合，更不能据此说它们的 γ 也为零。

本例十组展宽中共有 30 行受到这项处理；对应的条件、源码位置已经记入 [EPC 检查记录](/Atlas/examples/al/epc-q4/summary.json)。这是这条原生程序路线自身的限制。实际研究声学长波极限时，还需检查 q→0 采样与数值处理，不能仅引用 Γ 的零值。


## 8 个不可约点怎样代表完整 q 网格

下面的编号严格对应 `elph.inp_lambda.1` 到 `.8`。这是文件顺序，并不是一条连续高对称路径，图里也不把相邻编号连成声子色散。

| 文件编号 | qx, qy, qz（2π/alat） | 星权重 |
|---:|---|---:|
| 1 | 0.0000000, 0.0000000, 0.0000000 | 1 |
| 2 | -0.1767767, 0.1767767, -0.1767767 | 8 |
| 3 | 0.3535534, -0.3535534, 0.3535534 | 4 |
| 4 | 0.0000000, 0.3535534, 0.0000000 | 6 |
| 5 | 0.5303301, -0.1767767, 0.5303301 | 24 |
| 6 | 0.3535534, 0.0000000, 0.3535534 | 12 |
| 7 | 0.0000000, -0.7071068, 0.0000000 | 3 |
| 8 | -0.3535534, -0.7071068, 0.0000000 | 6 |

权重合计 64。全局 λ 是按这些权重归一化后的逐 q、逐模求和；不能把八个点当作同等权重，也不能只挑线宽最大的 q 点代替整个布里渊区。

下面的脚本读取每个文件，核对 8×10×3=240 条记录，并把主 OUT 的 THz、cm⁻¹ 频率与各模式 λ、GHz 线宽合并到 CSV。

```console
maxwell@maxwell:~/al/epc-q4$ ../.venv/bin/python analyse_epc.py > analysis.out
maxwell@maxwell:~/al/epc-q4$ cat analysis.out
8 irreducible q points; star weights sum to 64; 3 modes; 10 electronic widths; 240 mode records
80 q2r el-ph inputs; 10 real-space el-ph files; dense a2Fsave hash preserved
Maximum computed mode = 9.936574 THz; spectrum end = 14.000 THz
sigma_Ry  lambda_qsum  lambda_integral  omega_log_K  Tc_mu0.10_K
0.005     0.430378      0.430437       355.877      2.212103
0.010     0.371061      0.371118       344.606      0.915531
0.015     0.370295      0.370354       343.420      0.900166
0.020     0.374486      0.374545       343.741      0.969046
0.025     0.374613      0.374671       343.537      0.970575
0.030     0.373773      0.373833       342.831      0.954739
0.035     0.373581      0.373641       342.006      0.949300
0.040     0.374086      0.374146       341.243      0.955437
0.045     0.375022      0.375083       340.631      0.969102
0.050     0.376041      0.376101       340.145      0.984595
Native calculation completed; scientific convergence not established.
```

```console
maxwell@maxwell:~/al/epc-q4$ head -4 linewidth.csv
q_index,qx,qy,qz,star_weight,sigma_Ry,mode,frequency_THz,frequency_cm1,lambda_mode,gamma_GHz,DOS_EF_states_spin_Ry_cell,EF_eV
1,0.0,0.0,0.0,1,0.005,1,0.087851,2.930394,0.0,0.0,2.518161,8.37364
1,0.0,0.0,0.0,1,0.005,2,0.087851,2.930394,0.0,0.0,2.518161,8.37364
1,0.0,0.0,0.0,1,0.005,3,0.087851,2.930394,0.0,0.0,2.518161,8.37364
```

0.020 Ry 下，按星权重对三个模式求和，得到 λ=0.374486，与 `lambda.dat` 对应行一致。这个等式是数据装配检查：文件编号或权重错了，通常会在这里暴露；数值相符仍不代表 k/q 采样已足够密。

![8 个不可约 q 点的逐模线宽与耦合](/Atlas/examples/al/figures/phonon-linewidth.png)

横坐标是上表的文件编号，三种颜色对应同一个 q 点的三个模式。上图保留 γ 的 GHz 单位，下图为无量纲 λ；两张图一起读，能看到较大的线宽并不必然对应最大的 λ。要研究高对称路径上的连续线宽，可以继续在同一套 EPC 实空间数据上设置 matdyn 路径；本图只展示已经直接计算的这 8 个代表点。

下载 [linewidth.csv](/Atlas/examples/al/epc-q4/linewidth.csv)、[analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py) 与 [plot_epc.py](/Atlas/examples/al/plot_epc.py)，保持 `epc-q4` 子目录结构，在 Al 数据目录运行：

```bash
python plot_epc.py
```

全部原始逐 q 文件：[q1](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.1), [q2](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.2), [q3](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.3), [q4](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.4), [q5](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.5), [q6](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.6), [q7](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.7), [q8](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.8)。还可对照 [al.elph.in](/Atlas/examples/al/epc-q4/al.elph.in)、[al.elph.out](/Atlas/examples/al/epc-q4/al.elph.out) 和 [q-weight-source.json](/Atlas/examples/al/epc-q4/q-weight-source.json)。

下一步：到 [α²F](/Atlas/m/eliashberg-a2f/qe/) 把逐模贡献汇总到频率轴，再到 [Allen–Dynes 公式](/Atlas/m/allen-dynes/qe/) 看这一组 λ 与 ω_log 在明确 μ* 下给出什么结果。

```text
ph.x 完整 q 网格 → 每个 q 的频率 / λ / γ → 模式与星权重核对
                                      └─ α²F → λ / ω_log → 公式 Tc
```
