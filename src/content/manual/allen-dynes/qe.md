[QE 电子声子系数与 Tc 公式](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html) · [PHonon 用户手册](https://www.quantum-espresso.org/Doc/ph_user_guide/) · [ph.x 电子展宽参数](https://www.quantum-espresso.org/Doc/INPUT_PH.html)

有了 λ 和 ω_log，代入公式得到一个温度只需要一行运算。真正费时间的是前面的电子网格、q 网格、声子稳定性与 EPC 积分检查。下面把这两件事连起来：先确认手上的数来自哪里，再明确 μ* 的假设，最后看同一份数据对电子展宽和 μ* 有多敏感。

这里接着 [Al 的 α²F 计算](/Atlas/m/eliashberg-a2f/qe/) 的真实结果，输入与响应过程在那里展开。本页使用单原子 fcc Al、32³ 致密电子网格、16³ SCF 网格和 4³ q 网格的 `lambda.x` 输出。该网格尚未证明收敛，因此下文温度是这组输入下的公式结果，不是已验证的 Al 超导转变温度。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al`，按正文运行绘图命令。

## 先知道自己代入的是哪个公式

这次 QE 7.5 的 `lambda.x` 使用的是包含 ω_log 的简化 Allen–Dynes 表达式：

**T<sub>c</sub> = (ω<sub>log</sub> / 1.2) × exp{−1.04(1 + λ) / [λ − μ*(1 + 0.62λ)]}**

这里 ω_log 以 K 表示，算出的 Tc 也是 K。该式相当于将强耦合与谱形修正因子 f₁、f₂ 设为 1；没有求解各向异性的 Eliashberg 方程。不要把输出里的 K 再当作 THz 乘一次换算系数，也不要把论文中包含 f₁、f₂ 的结果与这行代码当成同一个计算。

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

重新绘图时，在含有 `epc-q4` 子目录的 Al 数据目录运行：

```bash
python plot_epc.py
```

复算所需文件：[lambda.in](/Atlas/examples/al/epc-q4/lambda.in), [lambda.dat](/Atlas/examples/al/epc-q4/lambda.dat), [lambda.out](/Atlas/examples/al/epc-q4/lambda.out), [alpha2F.dat](/Atlas/examples/al/epc-q4/alpha2F.dat), [analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py), [tc-scan.csv](/Atlas/examples/al/epc-q4/tc-scan.csv), [mu-sensitivity.csv](/Atlas/examples/al/epc-q4/mu-sensitivity.csv)；[完整绘图脚本](/Atlas/examples/al/plot_epc.py) 同时生成 α²F、展宽扫描和本页的两幅 Tc 图。

下一步：回到 [α²F](/Atlas/m/eliashberg-a2f/qe/) 检查积分范围与谱权重，或到 [声子线宽](/Atlas/m/phonon-linewidth/qe/) 追踪各个 q 点、各个模式的贡献。

```text
同一套 EPC → α²F → λ / ω_log + 明确的 μ* → 简化公式 Tc
                           ↑
                 k/q/展宽收敛检查仍决定结果能否采用
```
