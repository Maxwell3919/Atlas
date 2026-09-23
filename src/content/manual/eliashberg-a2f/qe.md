[q2r.x 输入](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [matdyn.x 输入](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [QE 7.5 lambda.x 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90) · [电子声子谱定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

从[已完成的 Al 双网格 EPC 会话](/Atlas/m/epc/qe/#double-grid-pwxall)接着做。前一页的 `al.dense.in` 对应我们平时命名为 `pwxall.in` 的致密网格步骤：32³ 致密 SCF、16³ 响应 SCF、4³ q 网格最终留下八份完整电声文件。这里直接使用这些文件，不重写结构优化与 SCF。α²F 同时包含振动频率和电子声子耦合权重，因此声子 DOS 的峰不一定就是 λ 的主要来源。

所有数字属于同一个单原子 fcc Al、LDA-PZ 计算链。它尚未完成 k/q/截断能收敛；本页的积分闭合检查回答文件和数值有没有接对，不替代材料性质验收。原件在[Al 输入输出包](/Atlas/examples/al-lesson-files.tar.gz)，新增脚本和表放在包内 `al/tc-route/`。

本页逐项拆开的是 32³ 致密网格分支的输出。另一个独立目录把 `pwxall` 改为 48³，保持 16³ 响应网格、4³ q 网格和后处理输入相同，再走完 `pwxall → pwx → phx → … → lambdax`。两份谱各自给出 λ、ωlog 和 Tc，最后按相同电子展宽配对。新目录的真实操作见 [48³ 分支](/Atlas/m/epc/qe/#dense-k48-run)，两条曲线、求交结果与配套 λ/ωlog 图见 [Tc 对照](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)。原生文件与复算脚本在[双分支下载包](/Atlas/examples/al-dense-grid-tc-files.tar.gz)中。

## q2r / matdyn 与 lambda.x 分别留下什么

脚本先执行 `q2r.x`，把完整 q 网格的力常数和 EPC 数据一起变换到实空间，再交给 `matdyn.x`。两份输入如下。

```console
maxwell@maxwell:~/al/epc-q4$ cat q2r.in
&INPUT
 fildyn='al.dyn'
 flfrc='al.fc'
 zasr='simple'
 la2F=.true.
/
```

```console
maxwell@maxwell:~/al/epc-q4$ cat matdyn-dos.in
&INPUT
 flfrc='al.fc'
 asr='simple'
 amass(1)=26.9815385
 la2F=.true.
 dos=.true.
 nk1=24
 nk2=24
 nk3=24
 ndos=400
 fldos='al.phdos.dat'
/
```

`matdyn.x` 的 24³ 是对已有实空间数据的积分网格，并没有增加真实计算的 DFPT q 点。它生成 `a2F.dos1` 到 `a2F.dos10`，编号依次对应十组电子展宽；同目录的 `lambda` 文件记录该路线的 λ 和对数平均频率。

这里 `nk1/nk2/nk3` 虽然名字带 k，在 `matdyn.x` 中却是声子 DOS 积分使用的 q 网格。增加它们可以检查后处理积分的离散误差，但无法补回原先 4³ DFPT 网格没有提供的力常数范围。`asr='simple'` 处理平移声学求和规则，也不会自动修复电子声子矩阵元或证明材料没有虚频。

同样的 `la2F` 出现在不同程序里，要跟着程序名读：`pw.x` 负责保存致密电子本征值，`q2r.x` 处理配套 EPC 实空间数据，`matdyn.x` 才在这条插值路线中输出谱函数。仅在普通声子后处理中打开最后一个开关，并不能产生前面从未计算的耦合。三份程序输入与逐 q 文件必须属于同一次完整计算链。

```console
maxwell@maxwell:~/al/epc-q4$ head -8 a2F.dos4
 
 # Eliashberg function a2F (per both spin)
 #  frequencies in Rydberg  
 # DOS normalized to E in Rydberg: a2F_total, a2F(mode) 
 
       0.378477E-05    0.138515E-09    0.613987E-10    0.351279E-10    0.419882E-10
       0.113543E-04    0.373996E-08    0.165777E-08    0.948475E-09    0.113372E-08
       0.189239E-04    0.173147E-07    0.767484E-08    0.439111E-08    0.524872E-08
```

文件头直接写着 `frequencies in Rydberg`。第一列是 Ry，第二列是总谱函数，后面三列按模式编号分解；单原子原胞有三个模式，因此数据区共五列。文件最后还有 `lambda = ... Delta = ...` 一行，它不是数值数据行，读表时不能直接把整份文件强行当成五列数组。

```console
maxwell@maxwell:~/al/epc-q4$ tail -3 a2F.dos4
       0.301648E-02    0.281188E-02    0.000000E+00    0.000000E+00    0.281188E-02
       0.302405E-02    0.000000E+00    0.000000E+00    0.000000E+00    0.000000E+00
  lambda =  0.374096616223644         Delta =   7.569579561024077E-006
```


## 输入之后，程序实际留下了什么

原作业按顺序执行这两条命令。先读齐同一 q 网格及其电声数据，再让 matdyn 读新写出的实空间文件；第一步失败时不能继续拿旧的 `al.fc` 画图。

```bash
<qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err
<qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
```

```console
maxwell@maxwell:~/al/epc-q4$ tail -18 q2r.out
 Broadening =      0.045
      q-space grid ok, #points =   64

      fft-check success (sum of imaginary terms < 10^-12)
 
 Broadening =      0.050
      q-space grid ok, #points =   64

      fft-check success (sum of imaginary terms < 10^-12)
 
     Q2R          :      0.01s CPU      0.01s WALL

 
   This run was terminated on:  22:14:11  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
```console
maxwell@maxwell:~/al/epc-q4$ cat matdyn-dos.out
MPI startup(): PMI server not found. Please set I_MPI_PMI_LIBRARY variable if it is not a singleton case.

     Program MATDYN v.7.5 starts on 22Sep2026 at 22:14:11 

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org", 
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     1 processors

     MPI processes distributed on     1 nodes
     1755 MiB available memory on the printing compute node when the environment starts
 
     Message from routine matdyn:
     Z* not found in file al.fc, TO-LO splitting at q=0 will be absent!
 
     MATDYN       :     26.00s CPU     26.11s WALL

 
   This run was terminated on:  22:14:38  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

本例 `q2r` 输入写有 `zasr='simple'`，它针对 Born 有效电荷；这份金属 Al 计算没有求 Born 电荷。对插值力常数施加平移声学求和规则的是 `matdyn` 中的 `asr='simple'`。24³ 是插值积分网格，`ndos=400` 是输出频率采样，二者都不会新增上游的 DFPT 响应信息。[q2r 的 zasr 定义](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html#zasr) · [matdyn 的 asr 定义](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html#asr)

| 读到的字段 | 本例单位 | 在哪里使用 |
|---|---|---|
| `alpha2F.dat` 第一列 | THz，普通频率 ν | 直接求和谱的 λ 与频率矩 |
| `a2F.dos*` 第一列 | Ry 对应的频率能量 | matdyn 插值谱；先确认单位再比较横轴 |
| `lambda.dat` 的 log w | K | 可直接代入 Tc 公式 |
| `el_ph_sigma` 与谱列标题 | Ry | 电子双 δ 积分的展宽 |
| `lambda.in` 的 0.12 | THz | 频率轴 Gaussian 参数宽度 |
| `lambda.in` 末行 0.10 | 无量纲 | Tc 采用的 μ* 假设 |

普通频率 ν 与角频率 ω 的单位转换分别写成 hν/kB 与 ħω/kB，两者相等，不能再多乘一次 2π。`lambda.f90` 固定使用 47.9924 K/THz；已经打印成 K 的 ωlog 不需要重复转换。它从逐 q 文件的有限小数频率平方重建最高模式约为 9.936533 THz，ph.x 原文打印为 9.936574 THz，差别是文本精度与常数使用造成的，不能强行当作同一全精度读数。

另一条路线是 `lambda.x`：直接读取这 8 个 q 点的 `elph.inp_lambda.*`，按星权重求和并在频率轴做 Gaussian 展宽。本页主图使用这条路线，文件名是 `alpha2F.dat`，频率单位为 THz。两个文件名很相似，单位和积分方式却不同，应分别保存与标注。

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.in
14.0 0.12 0
8
0.000000000 0.000000000 0.000000000 1.0
-0.176776700 0.176776700 -0.176776700 8.0
0.353553400 -0.353553400 0.353553400 4.0
0.000000000 0.353553400 0.000000000 6.0
0.530330100 -0.176776700 0.530330100 24.0
0.353553400 0.000000000 0.353553400 12.0
0.000000000 -0.707106800 0.000000000 3.0
-0.353553400 -0.707106800 0.000000000 6.0
elph_dir/elph.inp_lambda.1
elph_dir/elph.inp_lambda.2
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
0.10
```

第一行依次是频率上限 14 THz、频率展宽 0.12 THz 和 Gaussian 类型 0。第二行是不可约 q 点数；随后八行是 q 坐标及其星权重。坐标沿用 ph.x 输出的笛卡尔坐标、单位为 2π/alat；权重之和为 64，程序会归一化，不能给八个点都填 1。再往下的八行对应这八个点的文件，最后一行的 0.10 是用于公式估计 Tc 的 μ* 假设。

本次直接计算的最高模式为 9.936574 THz。14 THz 的上限还为频率展宽的尾部留出了空间。换材料时应先检查真实最高频率与高频尾部；沿用一个过小的上限，会使谱函数积分漏掉贡献，即使程序正常退出也不能接受。

```console
maxwell@maxwell:~/al/epc-q4$ <qe_bin>/lambda.x < lambda.in > lambda.out 2> lambda.err

```

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.dat
# degauss   lambda    int alpha2F  <log w>     N(Ef)
  0.005    0.430378    0.430442   355.877    2.518161
  0.010    0.371061    0.371121   344.606    2.624685
  0.015    0.370295    0.370356   343.420    2.647439
  0.020    0.374486    0.374547   343.741    2.646097
  0.025    0.374613    0.374674   343.537    2.643523
  0.030    0.373773    0.373835   342.831    2.643829
  0.035    0.373581    0.373643   342.006    2.645823
  0.040    0.374086    0.374148   341.243    2.648339
  0.045    0.375022    0.375085   340.631    2.650827
  0.050    0.376041    0.376104   340.145    2.653067
```

从左到右是电子展宽（Ry）、逐 q 点求和的 λ、对程序内部谱函数积分得到的 λ、ω_log（K），以及单自旋 DOS(EF)，后者单位是 states/spin/Ry/cell。0.020 Ry 这一行的前两种 λ 分别为 0.374486 和 0.374547，差约 0.000061；频率展宽与数值积分会造成小差别。

## 把图积分回输出里的 λ

```console
maxwell@maxwell:~/al/epc-q4$ head -5 alpha2F.dat
# E(THz)     0.005     0.010     0.015     0.020     0.025     0.030     0.035     0.040     0.045     0.050
  0.0000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0070   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0140   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0210   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
```

第一列后的十列依次对应文件头十组电子展宽。不要取第二列画图，却拿 0.020 Ry 那一行的 λ 做标题。下面的提取脚本检查 q 坐标、模式数、权重和十组展宽，然后用谱函数独立计算 `2∫α²F(ν)/ν dν`。零频点不参加除法，也没有对负数取绝对值。

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

打印后的 α²F 只保留有限小数，0.020 Ry 一列独立积分得到 0.374545，与程序内部积分 0.374547 的差别很小。这个交叉核对用于发现列号、单位或截断范围错误，不能代替 k/q 网格收敛。

![fcc Al 的 α²F 及累计 λ](/Atlas/examples/al/figures/eliashberg-a2f.png)

上图能看到谱权重集中在哪些频率；下面的累计积分则直接显示这些频段对 λ 的贡献。由于被积函数带有 1/ν，相同的谱函数面积放在不同频率，对 λ 的影响也不一样。

![电子展宽下的 λ 与对数平均频率](/Atlas/examples/al/figures/epc-smearing.png)

0.005 Ry 的结果明显偏离更宽的几组。后面几组接近，只能说明在当前网格上对这一段展宽不太敏感；没有更密电子网格和真实 q 网格对照，不能据此宣布 λ 已收敛。图中也保留了 matdyn 路线的结果。这次 matdyn 在 0.005 Ry 的谱中还有 146 行负值，最小值为 −0.00554175；0.010 Ry 有 9 行微小负值。原文件保留这些数值，不取绝对值或截零；这些列需要继续检查实空间插值与 q 网格，不能作为已接受的非负谱使用。两条路线的数值积分与插值不同，尤其在较大展宽时差别可见，不能从其中各挑一个数拼成一组结果。


## 从同一份谱同时提取 λ、ωlog 与二阶矩

普通频率 ν 采用同一固定单位时，三个积分分别为：

**λspec = 2∫ α²F(ν)/ν dν**

**νlog = exp{(2/λspec)∫ [α²F(ν)/ν] ln(ν) dν}**

**ν̄₂ = {(2/λspec)∫ α²F(ν)ν dν}<sup>1/2</sup>**

对数可理解为先对 `ν/(1 THz)` 取对数，最终恢复 THz。计算频率矩的归一化 λ 要由同一份谱得到；不能把另一条插值路线的 λ 填进分母。零频点不直接做除法或取对数。本例零频谱为零，可以从正频点积分；这不是允许在其他材料中删掉异常低频峰或实质性虚频。

新增脚本从八份电声原件重建 QE 7.5 的 2000 点 Gaussian 谱，复现程序的内部积分，再对已打印的谱做梯形积分，区分打印舍入与错列、错单位。对负谱不取绝对值、不裁零，也不为它生成可接受的频率矩。

```console
maxwell@maxwell:~/al/tc-route$ mkdir -p evidence
maxwell@maxwell:~/al/tc-route$ python3 scripts/verify_tc_chain.py --source <工作目录>/al/epc-q4 --output data > evidence/verify.out
```
```console
maxwell@maxwell:~/al/tc-route$ cat evidence/verify.out
q points=8; weights=64; modes=3; widths=10; mode records=240
printed-omega^2 reconstruction=0.087851..9.936533 THz; negative omega^2=0
ph.x printed maximum=9.936574 THz; frequency difference comes from printed w2 precision
lambda.x grid=2000 points, 0..14 THz; Gaussian parameter=0.12 THz
sigma_Ry lambda_qsum lambda_spectrum omega_log_K omega2_K Tc_QE_K Tc_full_AD_K
0.005 0.43037813 0.43043738 355.87701 370.56657 2.212105 2.248232
0.010 0.37106094 0.37111797 344.60678 363.11888 0.915532 0.928052
0.015 0.37029531 0.37035355 343.41976 362.60101 0.900170 0.912494
0.020 0.37448594 0.37454456 343.74087 363.33106 0.969044 0.982511
0.025 0.37461250 0.37467149 343.53737 363.44354 0.970568 0.984079
0.030 0.37377344 0.37383269 342.83124 363.00639 0.954746 0.968016
0.035 0.37358125 0.37364098 342.00604 362.39378 0.949304 0.962508
0.040 0.37408594 0.37414604 341.24361 361.79075 0.955437 0.968761
0.045 0.37502188 0.37508257 340.63107 361.29676 0.969100 0.982670
0.050 0.37604063 0.37610138 340.14505 360.89644 0.984588 0.998426
sigma=0.020: f1=1.01206929; f2=1.00080168; spectral simple Tc=0.970016 K
matdyn negative rows by width: 146, 9, 0, 0, 0, 0, 0, 0, 0, 0
Cross-check completed. Material Tc convergence is not established.
```

`Tc_full_AD_K` 是脚本从同一非负谱求得的含 f₁、f₂ 结果，不是 QE 原生打印值。具体公式与 μ* 接着到 [Tc 页](/Atlas/m/allen-dynes/qe/)逐项代入。

![同一电子展宽下，两条谱函数路线及累计 λ](/Atlas/examples/al/tc-route/figures/a2f-route-check.png)

图中固定 0.020 Ry，将 Ry 横轴换成 THz 后比较原值。两条离散处理接近不等于真实 q 网格已收敛。

![matdyn 原生负值与零附近放大](/Atlas/examples/al/tc-route/figures/a2f-negative-values.png)

右幅只改变查看范围，没有修改数据。0.005 Ry 的 146 行负值和 0.010 Ry 的 9 行微小负值需要继续排查；直接求和谱非负，不会自动消除这条插值路线的问题。

在公开包内运行提取与绘图：

在解包后的 `al` 目录中执行：

```bash
cd tc-route
python3 scripts/verify_tc_chain.py --source ../epc-q4 --output data
python3 scripts/plot_tc_chain.py --data data --output figures
```

提取只需 Python 标准库，绘图使用 NumPy、Matplotlib。脚本保留原始符号，不再乘自旋因子；网页 PNG 用大字号，PDF 用 7 pt 正文、8 pt 黑色粗体面板标记和可编辑字体，不加背景网格。

新增下载：[提取与交叉计算](/Atlas/examples/al/tc-route/scripts/verify_tc_chain.py) · [绘图脚本](/Atlas/examples/al/tc-route/scripts/plot_tc_chain.py) · [λ、频率矩与公式表](/Atlas/examples/al/tc-route/data/tc-formula-scan.csv) · [两条谱及累计积分](/Atlas/examples/al/tc-route/data/spectra-and-integrals.csv) · [源文件与单位核验](/Atlas/examples/al/tc-route/data/tc-chain-checks.json)。

原始输入、程序输出和独立检查脚本可以逐个查看：[al.dense.in](/Atlas/examples/al/epc-q4/al.dense.in), [al.dense.out](/Atlas/examples/al/epc-q4/al.dense.out), [al.scf.in](/Atlas/examples/al/epc-q4/al.scf.in), [al.scf.out](/Atlas/examples/al/epc-q4/al.scf.out), [al.elph.in](/Atlas/examples/al/epc-q4/al.elph.in), [al.elph.out](/Atlas/examples/al/epc-q4/al.elph.out), [continue.slurm](/Atlas/examples/al/epc-q4/continue.slurm), [q2r.in](/Atlas/examples/al/epc-q4/q2r.in), [q2r.out](/Atlas/examples/al/epc-q4/q2r.out), [matdyn-dos.in](/Atlas/examples/al/epc-q4/matdyn-dos.in), [matdyn-dos.out](/Atlas/examples/al/epc-q4/matdyn-dos.out), [lambda.in](/Atlas/examples/al/epc-q4/lambda.in), [lambda.out](/Atlas/examples/al/epc-q4/lambda.out), [lambda.dat](/Atlas/examples/al/epc-q4/lambda.dat), [alpha2F.dat](/Atlas/examples/al/epc-q4/alpha2F.dat), [analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py), [tc-scan.csv](/Atlas/examples/al/epc-q4/tc-scan.csv)。绘图代码为 [plot_epc.py](/Atlas/examples/al/plot_epc.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)）。

## 把完整谱函数交给 Tc 求解

走到这里得到的是 α²F。若需要快速比较同一组数据的 μ* 敏感性，可以进入 [Allen–Dynes / McMillan 估算](/Atlas/m/allen-dynes/qe/)；若需要实际求解能隙方程，则进入 [EPW / Eliashberg Tc](/Atlas/m/epw-eliashberg/qe/)。后一页使用原始频率列和谱函数列，核对单位转换后的积分，再把整条曲线交给 EPW。只保留 λ 和 ωlog 两个数，已经不足以重建方程需要的频率依赖。

EPW 的各向同性入口可以读取已有谱函数；各向异性求解还需要保留带、k 点和散射之间的分辨信息。因此，本页由 QE 双网格产生的谱可以接各向同性方程，但不能仅凭这个平均谱恢复各向异性能隙。具体文件要求见 [EPW 的 eliashberg 输入说明](https://docs.epw-code.org/Inputs/Inputs.html#eliashberg)。

```text
pwxall / dense-k → pwx / response-k → 完整逐 q EPC
                                      ↓
                       q2r + matdyn 或 lambda.x
                                      ↓
                             同一展宽的 α²F
                        ┌─────────────┴─────────────┐
                        ↓                           ↓
                   λ、ωlog、频率矩               完整频率与谱列
                        ↓                           ↓
                 Allen–Dynes Tc 估算       EPW 各向同性 Eliashberg 方程
```

下一步：[Tc 公式估算](/Atlas/m/allen-dynes/qe/) · [EPW 方程求解](/Atlas/m/epw-eliashberg/qe/)；需要定位单 q、单模贡献时，转到 [声子线宽](/Atlas/m/phonon-linewidth/qe/)。

```text
同结构致密 SCF + 响应 SCF → 完整 q 网格 EPC → 逐 q、逐模 λ/γ
                                             ├─ q2r → matdyn → a2F.dos*（Ry）
                                             └─ lambda.x → alpha2F.dat（THz）→ λ / ω_log
```
