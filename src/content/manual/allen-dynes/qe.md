[QE 电子声子系数与 Tc 公式](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html) · [QE 7.5 lambda.x 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90) · [Allen–Dynes 原论文](https://doi.org/10.1103/PhysRevB.12.905) · [完整修正形式与频率矩](https://link.springer.com/article/10.1007/s10948-017-4295-y)

有了 λ 和 ω_log，代入公式得到一个温度只需要一行运算。真正费时间的是前面的电子网格、q 网格、声子稳定性与 EPC 积分检查。下面把这两件事连起来：先确认手上的数来自哪里，再明确 μ* 的假设，最后看同一份数据对电子展宽和 μ* 有多敏感。

这里接着 [Al 的 α²F 计算](/Atlas/m/eliashberg-a2f/qe/) 的真实结果，输入与响应过程见 [完整 EPC 会话](/Atlas/m/epc/qe/)。本页使用单原子 fcc Al、32³ 致密电子网格、16³ SCF 网格和 4³ q 网格的 `lambda.x` 输出。该网格尚未证明收敛，因此下文温度是这组输入下的公式结果，不是已验证的 Al 超导转变温度。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al`，按正文运行绘图命令。


## 先把“已有输出”变成一条能执行的命令

前面的[完整 EPC](/Atlas/m/epc/qe/)和[α²F 页](/Atlas/m/eliashberg-a2f/qe/)已经提供真实父计算、八个不可约 q 的权重及 `lambda.in` 全文。这里不再提交 SCF 或 ph.x，而是在已有电声文件的副本上重放后处理。下面是在 Maxwell 独立 tmux 窗口中执行的命令，公开文本将工作路径简写。

```console
maxwell@maxwell:~/tc-route$ mkdir -p replay-lambda/elph_dir evidence
maxwell@maxwell:~/tc-route$ cp <工作目录>/al/epc-q4/lambda.in replay-lambda/
maxwell@maxwell:~/tc-route$ cp <工作目录>/al/epc-q4/elph_dir/elph.inp_lambda.* replay-lambda/elph_dir/
maxwell@maxwell:~/tc-route$ cd replay-lambda
```

复制的是同一组八个 q 文件，不会生成新的响应。输入内的相对文件名仍然指向 `elph_dir`，副本保留相同层级。末尾读到的是：

```console
maxwell@maxwell:~/al/tc-route/replay-lambda$ tail -3 lambda.in
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
0.10
```

最后的 0.10 才是 μ*；第一行的 0.12 是频率轴 Gaussian 宽度，单位 THz。本机 QE 依赖 oneAPI 运行库，载入后运行：

```console
maxwell@maxwell:~/tc-route/replay-lambda$ source /opt/intel/oneapi/setvars.sh > ../evidence/oneapi-env.log 2>&1
maxwell@maxwell:~/tc-route/replay-lambda$ <qe_bin>/lambda.x < lambda.in > lambda.out 2> lambda.err
maxwell@maxwell:~/tc-route/replay-lambda$ wc -c lambda.err
0 lambda.err
```

这次副本生成的 `lambda.out`、`lambda.dat`、`alpha2F.dat` 与原件 SHA-256 完全相同。下面沿着它们的实际输出读数。这里没有新算 DFT，也不能把已有 Al 数据的重放称作 SnSe₂/Sr₂N 已经获得 Tc。

## 先知道自己代入的是哪个公式

这次 QE 7.5 的 `lambda.x` 使用的是包含 ω_log 的简化 Allen–Dynes 表达式：

**T<sub>c</sub> = (ω<sub>log</sub> / 1.2) × exp{−1.04(1 + λ) / [λ − μ*(1 + 0.62λ)]}**

这里 ω_log 以 K 表示，算出的 Tc 也是 K。该式相当于将强耦合与谱形修正因子 f₁、f₂ 设为 1；没有求解各向异性的 Eliashberg 方程。不要把输出里的 K 再当作 THz 乘一次换算系数，也不要把论文中包含 f₁、f₂ 的结果与这行代码当成同一个计算。

源码计算 ωlog 时用内部谱积分的 λ 归一化，计算 Tc 时则取逐 q 求和的 λ；这正是输出中两种 λ 要分列保留的原因。后面另外从同一打印谱提取一致的频率矩，用于完整 f₁、f₂ 对照。

μ* 是有效库仑赝势参数。本例取 0.10，是输入假设，不是这次 DFT 自动求出的物性。

## 从输入的最后一行到程序输出

完整的 `lambda.in` 与执行顺序见 [α²F 页](/Atlas/m/eliashberg-a2f/qe/)；本页从已经生成的 `lambda.out` 接着读。输入第一行的 14.0 和 0.12 都以 THz 为单位，分别控制频率范围和频率展宽；最后一行的 0.10 才是用于 Tc 公式的 μ*。

这份 Al 数据的最高直接计算频率为 9.936574 THz，14 THz 覆盖了谱峰及 Gaussian 尾部。更换材料时，要先核对实际频率范围；落在范围外的谱权重会使 ω_log 和积分失真。

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.out
     lambda = 0.430378 (   0.430442 )  <log w>=  355.877 K  N(Ef)=  2.518161 at degauss= 0.005
     lambda = 0.371061 (   0.371121 )  <log w>=  344.606 K  N(Ef)=  2.624685 at degauss= 0.010
     lambda = 0.370295 (   0.370356 )  <log w>=  343.420 K  N(Ef)=  2.647439 at degauss= 0.015
     lambda = 0.374486 (   0.374547 )  <log w>=  343.741 K  N(Ef)=  2.646097 at degauss= 0.020
     lambda = 0.374613 (   0.374674 )  <log w>=  343.537 K  N(Ef)=  2.643523 at degauss= 0.025
     lambda = 0.373773 (   0.373835 )  <log w>=  342.831 K  N(Ef)=  2.643829 at degauss= 0.030
     lambda = 0.373581 (   0.373643 )  <log w>=  342.006 K  N(Ef)=  2.645823 at degauss= 0.035
     lambda = 0.374086 (   0.374148 )  <log w>=  341.243 K  N(Ef)=  2.648339 at degauss= 0.040
     lambda = 0.375022 (   0.375085 )  <log w>=  340.631 K  N(Ef)=  2.650827 at degauss= 0.045
     lambda = 0.376041 (   0.376104 )  <log w>=  340.145 K  N(Ef)=  2.653067 at degauss= 0.050
lambda        omega_log          T_c
   0.43038       355.877              2.212
   0.37106       344.606              0.916
   0.37030       343.420              0.900
   0.37449       343.741              0.969
   0.37461       343.537              0.971
   0.37377       342.831              0.955
   0.37358       342.006              0.949
   0.37409       341.243              0.955
   0.37502       340.631              0.969
   0.37604       340.145              0.985
```

前十行先给每组电子展宽的 λ、括号中的谱积分 λ、ω_log 和 DOS(EF)。后面的三列表才是 λ、ω_log、Tc，电子展宽的行序与前面相同。`lambda.x` 的这份文本没有常见的大段计时与 `JOB DONE.` 结束框；这次通过零字节 `lambda.err`、十行完整结果、有限数值以及独立公式复算核对结果。前面的 pw.x、ph.x 和 matdyn.x 则分别检查各自的正常结束及收敛输出。

0.020 Ry 对应第 4 行：λ=0.374486，ω_log=343.741 K，μ*=0.10。分母 λ−μ*(1+0.62λ) 为正，代入得到 0.969046 K，程序按三位小数打印为 0.969 K。若分母接近零或变为非正数，应停止把指数结果解释为可靠的 Tc，而不是让程序给出一个数就继续引用。

复算时也要明确使用哪一列 λ。本页和程序的 Tc 表都采用逐 q 求和的第一列；括号中的数用于检查谱函数积分。如果改用括号值，应重新计算并说明来源，不能保留旧 Tc 却悄悄换掉表中的 λ。ω_log 对频率采取对数加权，低频模式的处理和截断会传递到温度结果；输入有实质性虚频时，不应将频率取绝对值后继续套公式。

这一表中的十行是十种积分展宽设定，不是十次独立实验或随机样本。它们的范围可展示当前采样对展宽的敏感性，不能直接当作统计置信区间。μ* 扫描也是对一个输入假设的敏感性检查，两者应像下图那样分别阅读。


## 自己复算第 4 行，先检查分母

用打印出来的 λ=0.374486、ωlog=343.741 K 和 μ*=0.10，就能在终端复现这一行：

```console
maxwell@maxwell:~/tc-route/replay-lambda$ python3 -c 'import math; lam=0.374486; wlog_K=343.741; mu=0.10; d=lam-mu*(1+0.62*lam); print(f"denominator = {d:.9f}"); print(f"Tc = {wlog_K/1.2*math.exp(-1.04*(1+lam)/d):.6f} K")'
denominator = 0.251267868
Tc = 0.969046 K
```

这是用表格舍入数字得到的复算值；从逐 q 原件重建内部值为 0.969044 K，两者都对应原生输出的 0.969 K。分母非正、近于零或输入非有限时，新增脚本会停止公式计算，不会把一个失去适用意义的指数结果解释成材料温度。这也不能被反过来当成证明材料不超导。

## 先把十组电子展宽一起读完

0.005 Ry 的公式结果是 2.212 K，0.010 Ry 降到约 0.916 K。后几组集中在约 0.90–0.98 K，但这个表只改变了电子双 δ 积分的展宽，致密电子网格和真实 q 网格没有变化。这说明目前最窄展宽对积分采样敏感，不能仅选择一行接近期望值的数字作为最终结果。

`analyse_epc.py` 直接读取 `lambda.dat`，将每一行代入同一个公式，并比较 `lambda.out` 的打印值；该脚本还独立积分 `alpha2F.dat`。

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

## 保持谱函数不变，再改变 μ*

下面固定 0.020 Ry 对应的 λ 与 ω_log，只改变假设的 μ*。这些点没有重新进行 DFT，是同一个简化公式的参数敏感性计算。

```console
maxwell@maxwell:~/al/epc-q4$ cat mu-sensitivity.csv
mu_star,Tc_K
8.000000000000000167e-02,1.610722658499318172e+00
8.999999999999999667e-02,1.264271858038103158e+00
9.999999999999999167e-02,9.690460020124249674e-01
1.099999999999999867e-01,7.226644078867575649e-01
1.199999999999999817e-01,5.220046073518097574e-01
1.299999999999999767e-01,3.632181974234426902e-01
1.399999999999999578e-01,2.417928679277238646e-01
1.499999999999999667e-01,1.526709604922883989e-01
1.599999999999999756e-01,9.043153189929345470e-02
```

![电子展宽及 μ* 对简化公式 Tc 的影响](/Atlas/examples/al/figures/allen-dynes.png)

左图改变 EPC 积分的电子展宽，右图改变公式中的库仑参数。两种变化回答的问题不同。这个例子能展示一条完整的数据读取与复算方法，也能看到假设对数值的影响；尚不支持精确预测材料 Tc。进一步计算要增加致密电子网格和真实 q 网格，并在相同物理协议下检查声子与 EPC 是否收敛，而不是只把频率轴画得更密。


## 从谱中提取二阶矩，才能计算完整 f₁、f₂

只有 λ 与 ωlog 两个数，还不能决定完整 Allen–Dynes 的谱形修正。它还需要耦合加权的均方根频率 ν̄₂，不能拿普通声子 DOS 的平均频率、另一个电子展宽的频率矩，或另一条 matdyn 路线的数据来补。

| 公式版本 | 前因子 | 本例用途 |
|---|---|---|
| 原始 McMillan | ΘD/1.45 | 本例没有计算 ΘD，不拿它代替 ωlog |
| QE 7.5 的 ωlog 修正式 | ωlog/1.2，f₁=f₂=1 | 与原生 `lambda.x` 逐行复算 |
| 含 f₁、f₂ 的 Allen–Dynes | f₁f₂ωlog/1.2 | 从同一非负谱计算完整矩后单列 |

以普通频率 ν 写，同一份谱的三个积分是：

**λspec = 2∫ α²F(ν)/ν dν**

**νlog = exp{(2/λspec)∫ [α²F(ν)/ν] ln(ν) dν}**

**ν̄₂ = {(2/λspec)∫ α²F(ν)ν dν}<sup>1/2</sup>**

这里的归一化 λspec 必须来自这份谱。对数使用同一固定单位，可以理解为对 `ν/(1 THz)` 取对数，最后恢复 THz。νlog、ν̄₂ 随后乘 h×10¹²/kB 得到 K；若写成角频率则使用 ħω/kB，不能多乘 2π。复现 QE 7.5 时沿用源码的 47.9924 K/THz，已经是 K 的打印 ωlog 不再换算。

零频点不直接除以 ν 或取对数。本例零点的谱值为零，可以从正频点积分；这不是允许删掉其他材料中的异常低频峰或实质性虚频。脚本拒绝负谱，不取绝对值、不裁零后再输出一组看似合理的 Tc。

## 将内部求和、打印谱积分和公式逐项对照

新增脚本读取所有 q 文件与权重，先按 QE 7.5 的 Gaussian 定义重建 2000 点内部谱，复现原生 λ、ωlog 与 Tc，再独立积分已打印的 `alpha2F.dat`。这样可以分清舍入误差与错列、错单位或混用公式。

```console
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

`lambda_qsum` 按模式 λ 与归一化 q 权重直接相加，`lambda_spectrum` 从打印谱积分得到。频率展宽、积分网格和小数位让它们略有不同。源码算法重建与原生输出在打印精度内吻合，打印谱的独立积分则保留其有限精度。

本次直接 q 文件的 ω² 都为正，这个检查只覆盖已计算点。Γ 三个约 2.93 cm⁻¹ 的正残差低于本版本 `interpolated` 实现的 20 cm⁻¹ 阈值，λ 被程序置零，γ 原文仍保留。不能说这里已经验证了无低频截断的 EPC。

另外，matdyn 的 0.005 Ry 谱有 146 行负值，0.010 Ry 有 9 行；这些列没有被用来输出可接受的谱矩。下面的完整公式使用直接 q 求和的非负 `alpha2F.dat`，并不表示另一条插值路线的问题已经解决。

设 r=ν̄₂/νlog，完整形式为：

**Tc,AD = f₁f₂ (ωlog/1.2) exp{−1.04(1+λspec)/[λspec−μ*(1+0.62λspec)]}**

**f₁ = [1+(λspec/Λ₁)<sup>3/2</sup>]<sup>1/3</sup>，Λ₁ = 2.46(1+3.8μ*)**

**f₂ = 1+(r−1)λspec²/(λspec²+Λ₂²)，Λ₂ = 1.82(1+6.3μ*)r**

两种频率都换成 K 后，r 仍无量纲。f₁ 是强耦合修正，f₂ 随谱形改变；它们仍属于拟合公式，补上以后并不等于数值求解了 Eliashberg 方程。

0.020 Ry 这列的实际中间量是：

| 量 | 数值 |
|---|---:|
| λspec | 0.37454456 |
| ωlog | 343.74087 K |
| ν̄₂ 对应温度 | 363.33106 K |
| μ* | 0.10 |
| f₁ | 1.01206929 |
| f₂ | 1.00080168 |

三行温度必须分开读：

| 数据与公式 | Tc（K） |
|---|---:|
| QE 原生定义：λqsum 与原生谱 ωlog，简式 | 0.969044 |
| 同一打印谱的 λspec、ωlog，简式 | 0.970016 |
| 同一打印谱的 λspec、ωlog、ν̄₂，乘 f₁f₂ | 0.982511 |

第一到第二行包含归一化与打印谱积分的变化，第二到第三行才是在固定同一组谱矩后加入 f₁f₂。不能把第一到第三行的全部差别都说成强耦合修正，更不能把较高的一行选作更可靠的材料预测。

## 同一谱下，完整公式也要保留 μ* 的假设

固定 0.020 Ry 的谱，只改变 μ*，三种定义得到：

```console
maxwell@maxwell:~/al/tc-route$ cat data/mu-star-scan.csv
mu_star,Tc_QE_rounded_input_K,Tc_spectrum_simple_K,Tc_spectrum_full_AD_K
0.08,1.6107226584993182,1.6120500128520705,1.6347436284357797
0.09,1.2642718580381032,1.2654176885906845,1.2824457531797715
0.1,0.969046002012425,0.970016140785092,0.9825105724541605
0.11,0.7226644078867569,0.7234674219221328,0.732398924745519
0.12,0.5220046073518098,0.5226518506188913,0.5288436032754813
0.13,0.36321819742344197,0.3637237157771725,0.3678633763712934
0.14,0.24179286792772323,0.24217311358934973,0.2448239277483174
0.15,0.1526709604922883,0.15294427830078677,0.15455599724304322
0.16,0.09043153189929327,0.0906173974670778,0.09153761243237504
```

这些点没有重新计算 DFT；它们是同一经验公式的假设敏感性，不是独立实验或统计置信区间。μ* 从 0.08 增到 0.16 时温度明显下降，说明结论若依赖某个选择，就需要报告采用值、范围与依据。

![电子展宽、μ* 与两种公式版本](/Atlas/examples/al/tc-route/figures/tc-formulas.png)

左幅保持 μ*=0.10，改变 EPC 电子展宽；右幅固定 0.020 Ry 的谱，改变 μ*。横轴回答两种不同问题。最窄展宽的离群值并不会因为乘上 f₁f₂ 就变得可信。

## 文件与算术核对完成后，再决定能否用于材料结论

本次已核对同一父计算、八个不可约 q、星权重和 64、三模式、十组电子展宽及频率覆盖范围。副本后处理与原件一致，逐 q 求和、源码算法重建、打印谱积分和 Tc 复算相互对应。这些证据说明从文件到数值的过程能复现。

材料层面的验收仍要在同一协议下加密真实 k/q 网格，比较相同电子展宽的 λ、ωlog、Tc，并核对结构、声子稳定性、赝势与截断能。只增大 matdyn 插值网格、增加频率采样或把图画得更细，不会增加上游响应信息。存在未解决的实质性虚频或负谱时，有限的公式温度不能成为绕过问题的理由。

`lambda.x` 没有常见的 `JOB DONE.` 框；这里用错误文件、完整有限输出及独立复算检查它。pw.x、ph.x、q2r.x 和 matdyn.x 则分别核对自己的退出与收敛信息。程序完成、算术复现和材料结果可用是不同的判断。

## 在本机重新出图

在解包后的 `al` 目录中执行：

```bash
cd tc-route
python3 scripts/verify_tc_chain.py --source ../epc-q4 --output data
python3 scripts/plot_tc_chain.py --data data --output figures
```

提取仅需 Python 标准库，绘图使用 NumPy、Matplotlib。`data/tc-formula-scan.csv` 保存十组展宽的中间量，`mu-star-scan.csv` 保存 μ* 扫描，`tc-chain-checks.json` 保存单位、源文件 SHA 与限制。脚本读取原值，不裁负值或倍乘自旋；颜色与线型同时区分曲线。网页 PNG 使用大字号，矢量 PDF 用 7 pt 正文、8 pt 黑色粗体面板标记和可编辑字体，不加背景网格。

下载：[完整 Al 包](/Atlas/examples/al-lesson-files.tar.gz) · [提取与复核脚本](/Atlas/examples/al/tc-route/scripts/verify_tc_chain.py) · [绘图脚本](/Atlas/examples/al/tc-route/scripts/plot_tc_chain.py) · [λ、频率矩与 Tc 表](/Atlas/examples/al/tc-route/data/tc-formula-scan.csv) · [μ* 表](/Atlas/examples/al/tc-route/data/mu-star-scan.csv) · [单位与文件核验](/Atlas/examples/al/tc-route/data/tc-chain-checks.json)。

下一步：回到 [α²F 与累计 λ](/Atlas/m/eliashberg-a2f/qe/)定位频段贡献；需要追到单 q、单模时继续读[声子线宽](/Atlas/m/phonon-linewidth/qe/)。

```text
完整同协议逐 q EPC → q / 权重 / 模式 / 展宽 / 频率范围核对
        ↓
lambda.x 的 λq、ωlog、Tc ↔ 独立源码算法复算
        ↓
同一非负 α²F → λspec、ωlog、ν̄₂ → 明确 μ*
        ↓
简式与含 f₁f₂ 公式对照
        ↓
k / q / 展宽 / 声子稳定性验收后，才决定材料结论
```
