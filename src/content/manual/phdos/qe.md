声子色散告诉我们一条指定路径上的频率怎样变化。声子态密度换了一个问法：在整个布里渊区里，有多少振动模式落在这一小段频率内？路径上的点再密，也不能代替布里渊区积分。

这里接着 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 的结果做。例子是单原子 fcc Al 原胞，使用 QE 7.5 和官方示例中的 `Al.pz-vbc.UPF`。这次完整计算了 4×4×4 q 网格；需要准备 `al.dyn0` 和八份编号动力学矩阵，它们对应同一个 Al 结构和父 SCF；下面从声子计算结束的目录开始。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

本例从同一组力常数比较 24³ 与 32³ 后处理网格，读取谱形及总积分是否接近单原子原胞的三个振动自由度。这也为振动热力学准备了谱：例如 [Hellman 等的 TDEP 方法论文式 (18)](https://arxiv.org/html/1303.1145)用全布里渊区的声子态密度积分振动自由能。本页只计算态密度，还没有执行这一步自由能计算。

## 先看手上的动力学矩阵

```console
maxwell@maxwell:~/al/dfpt$ ls al.dyn*
al.dyn0
al.dyn1
al.dyn2
al.dyn3
al.dyn4
al.dyn5
al.dyn6
al.dyn7
al.dyn8
```
`al.dyn0` 是 q 网格的索引，后面的编号文件才存放各个不可约 q 点的动力学矩阵。8 个不可约点不等于只计算了 8 个任意 q 点；它们借助晶体对称性覆盖这里的完整 64 点网格。

```console
maxwell@maxwell:~/al/dfpt$ cat al.dyn0
   4   4   4
   8
   0.000000000000000E+00   0.000000000000000E+00   0.000000000000000E+00
  -0.176776695296637E+00   0.176776695296637E+00  -0.176776695296637E+00
   0.353553390593273E+00  -0.353553390593273E+00   0.353553390593273E+00
   0.000000000000000E+00   0.353553390593273E+00   0.000000000000000E+00
   0.530330085889910E+00  -0.176776695296637E+00   0.530330085889910E+00
   0.353553390593273E+00   0.000000000000000E+00   0.353553390593273E+00
   0.000000000000000E+00  -0.707106781186547E+00   0.000000000000000E+00
  -0.353553390593273E+00  -0.707106781186547E+00   0.000000000000000E+00
```
先核对网格，再看程序是否真的走到末尾。一个文件刚出现时，程序还可能在写它。这里末尾的运行时间和 `JOB DONE.` 是程序结束证据；SCF 和各个响应分量的收敛还要在前面的输出中逐项检查。

```console
maxwell@maxwell:~/al/dfpt$ tail -12 al.ph.out
     h_psi:calbec :      5.55s CPU      6.68s WALL (  859163 calls)
     s_psi_bgrp   :      1.70s CPU      2.04s WALL ( 1409957 calls)
 
 
     PHONON       :   2m40.10s CPU   3m11.61s WALL

 
   This run was terminated on:  21:38:17  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
## 从 q 空间回到实空间力常数

动力学矩阵按 q 点存放，`q2r.x` 把这一整套相容的网格变成实空间力常数。原来的 `al.dyn*` 留在原处，转换结果另写成 `al.fc`。

```console
maxwell@maxwell:~/al/dfpt$ cat q2r.in
&INPUT
 fildyn='al.dyn'
 flfrc='al.fc'
 zasr='simple'
/
```
这里 `fildyn` 对应文件名前缀，`flfrc` 是即将写出的力常数文件。`q2r.x` 的 `zasr` 针对 Born 有效电荷的和规则；这份金属 Al 数据没有 Born 有效电荷，不能把 `zasr='simple'` 当作已经修正声学支的依据。下面 `matdyn.x` 的 `asr='crystal'` 才对力常数施加三条平移和规则。它约束整体平移的恢复力，不能消除原始 q 网格或电子参数造成的误差。不要从另一份结构的目录借几个编号文件来凑齐网格。

```console
maxwell@maxwell:~/al/dfpt$ <qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err

```
```console
maxwell@maxwell:~/al/dfpt$ tail -12 q2r.out
      q-space grid ok, #points =   64

      fft-check success (sum of imaginary terms < 10^-12)
 
     Q2R          :      0.00s CPU      0.00s WALL

 
   This run was terminated on:  21:38:19  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
这里的 `#points = 64` 与 4×4×4 相符，`fft-check success` 说明这一轮读入的数据通过了程序的 Fourier 一致性检查。它不回答 q 网格是否足够密；那个问题要增加真正的 DFPT q 采样，再比较目标频率或 DOS。

## 用均匀网格积分，而不是沿高对称线计数

```console
maxwell@maxwell:~/al/dfpt$ cat matdyn-dos.in
&INPUT
 flfrc='al.fc'
 asr='crystal'
 dos=.true.
 nk1=24
 nk2=24
 nk3=24
 deltaE=1.0
 fldos='al.phdos.dat'
/
```
`dos=.true.` 让 `matdyn.x` 在均匀 q 网格上用四面体方法计算 DOS。`nk1`、`nk2`、`nk3` 是声子积分网格，不是 SCF 的电子 k 网格，也不是重新调用 `ph.x` 计算响应。这里从 4×4×4 的力常数插值到 24×24×24 点；`deltaE=1.0` 指定输出频率轴的步长为 1 cm⁻¹，不是 Gaussian 展宽，输出文件名为 `al.phdos.dat`。减小这个步长只会把频率轴取样写得更细，不会补充原始 DFPT 响应点。

```console
maxwell@maxwell:~/al/dfpt$ <qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err

```
```console
maxwell@maxwell:~/al/dfpt$ tail -12 matdyn-dos.out

     Message from routine matdyn:
     Z* not found in file al.fc, TO-LO splitting at q=0 will be absent!
 
     MATDYN       :      5.32s CPU      5.32s WALL

 
   This run was terminated on:  21:38:25  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
这份输出写着 `Z* not found`。本例是金属 Al，没有在这条路线中计算绝缘体的 Born 有效电荷和非解析项；所以不能把这句话解释成已经处理了极性材料的 LO–TO 分裂。若换成极性绝缘体，应回到 DFPT 计算相应的电场响应，保持同一套结构与参数。

```console
maxwell@maxwell:~/al/dfpt$ head -8 al.phdos.dat
 # Frequency[cm^-1] DOS PDOS
 -2.9127447802E-06  0.0000000000E+00  0.0000E+00
  9.9999708726E-01  6.8963092060E-08  6.8963E-08
  1.9999970873E+00  2.7585269581E-07  2.7585E-07
  2.9999970873E+00  6.2066881126E-07  6.2067E-07
  3.9999970873E+00  1.1034114384E-06  1.1034E-06
  4.9999970873E+00  1.7240805772E-06  1.7241E-06
  5.9999970873E+00  2.4826762278E-06  2.4827E-06
```
第一列是频率，单位 cm⁻¹；第二列是总 DOS；第三列是这里唯一一个原子的投影贡献。单原子原胞只有 3 条声子支，所以对总 DOS 积分应接近 3，而不是电子 DOS 中常见的电子态数。文件开头的约 −0.000003 cm⁻¹ 在这个计算中对应数值零，不能据此画出一个有物理意义的负频峰。

换 32³ 的过程只改变后处理积分网格，保留原输出：

```console
maxwell@maxwell:~/al/dfpt$ cp matdyn-dos.in matdyn-dos32.in
maxwell@maxwell:~/al/dfpt$ vi matdyn-dos32.in
maxwell@maxwell:~/al/dfpt$ cat matdyn-dos32.in
&INPUT
 flfrc='al.fc'
 asr='crystal'
 dos=.true.
 nk1=32
 nk2=32
 nk3=32
 deltaE=1.0
 fldos='al.phdos32.dat'
/
```
保存后仍在 `al/dfpt` 目录运行第二份输入，再检查它自己的输出与错误文件：

```bash
<qe_bin>/matdyn.x -in matdyn-dos32.in > matdyn-dos32.out 2> matdyn-dos32.err
tail -n 14 matdyn-dos32.out
cat matdyn-dos32.err
```

本次保存的 [matdyn-dos32.out](/Atlas/examples/al/dfpt/matdyn-dos32.out) 记录了 22.21 s WALL 与 `JOB DONE.`，[matdyn-dos32.err](/Atlas/examples/al/dfpt/matdyn-dos32.err) 为空。`fldos` 使用新的文件名，因此两份 `al.phdos*.dat` 都会保留。先完成这一步，再运行同时读取两份数据的绘图脚本。

## 把积分数和图放在一起检查

解包本页开头的 Al 算例并保留目录结构，在 `al` 目录运行[绘图脚本](/Atlas/examples/al/plot_phdos.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)）。脚本从 `dfpt/al.phdos.dat` 和 `dfpt/al.phdos32.dat` 读取 24³、32³ 两份数据；[单独下载的原始 DOS 数据](/Atlas/examples/al/dfpt/al.phdos.dat)也应放回对应的 `dfpt` 子目录。它先输出积分再画曲线，这样能发现列读错、单位弄错或数据截断的问题。


绘图脚本读取两份总 DOS，先按频率列积分并与单原子原胞的 3 个振动自由度比较，再叠画 24³ 与 32³ 积分网格的结果。下面的需求对应这一步：

```text
编写 plot_phdos.py，从 Al 根目录读取 dfpt/al.phdos.dat 与 dfpt/al.phdos32.dat，比较 24³ 和 32³ 后处理积分网格。第一列频率单位 cm⁻¹，第二列总 DOS 单位 states/(cm⁻¹)；用梯形积分打印原始积分，与单原子原胞的 3 个模式比较，不强制归一化。以真实频率列画 DOS 曲线、标单位和网格，输出 figures/phdos.png 与 PDF，复用 atlas_plot_style.py。
```

下面是算例实际使用的完整源码。

<details>
<summary>plot_phdos.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(6.8,4.3),layout="constrained")
for n,file in [(24,"al.phdos.dat"),(32,"al.phdos32.dat")]:
    d=np.loadtxt(root/"dfpt"/file)
    print(f"mesh={n} integral={np.trapezoid(d[:,1],d[:,0]):.8f}")
    ax.plot(d[:,0],d[:,1],label=f"{n}³ integration mesh",lw=1.8)
ax.set(xlabel="Frequency (cm⁻¹)",ylabel="Phonon DOS (states / cm⁻¹)",xlim=(0,None))
ax.legend(frameon=False);ax.grid(alpha=.18)
(root/"figures").mkdir(exist_ok=True)
fig.savefig(root/"figures/phdos.png",dpi=220)
fig.savefig(root/"figures/phdos.pdf")
```

</details>

```bash
python3 plot_phdos.py
```

本次 24³ 网格的积分是 **2.99953038**；32³ 网格为 **2.99931874**。完整频率范围是约 0—332 cm⁻¹。两次积分都应与 3 对照，而不是强行归一化后再宣布通过。

<figure><img src="/Atlas/examples/al/figures/phdos.png" alt="Al 声子态密度，24与32网格积分比较" loading="lazy"/><figcaption>同一份 4×4×4 DFPT 力常数上的两种积分网格。曲线是实际输出的 DOS，没有手工平滑或补点。</figcaption></figure>

比较时要分开两个问题：积分网格变密后峰形和积分是否稳定；原始 DFPT q 网格变密后力常数是否稳定。这里已完成前一项检查的两组计算，后一项仍需独立 q 网格系列。当前这张图可以用于理解声子 DOS 和检查数据链条，不能直接作为 Al 声子谱已数值收敛的证明。

## 二维异质结 ZrCl₂/Sc₂C 与 SnSe₂/Sr₂N：多元素原子投影 PHDOS 与声子色散共享频率轴对齐

单质 Al 的 `.phdos` 文件只有一列原子投影，而在含 `N_at` 个原子的化合物或异质结中，`matdyn.x`（开启 `dos = .true.`）输出的 `.phdos` 文件格式为：

```text
# Frequency[cm^-1] DOS PDOS_1 PDOS_2 ... PDOS_nat
```

其中第 1 列为波数频率（`cm⁻¹`），第 2 列为原胞总声子态密度，第 `3` 至 `N_at + 2` 列依次对应原胞内第 `1` 至 `N_at` 个原子的分波声子态密度（满足 `∑_I PDOS_I(ω) = DOS(ω)`）。将其转换到 `THz` 单位时，横轴频率除以 `33.3564095`，纵轴态密度同步乘以 `33.3564095`，从而保持全频段积分等于总自由度数 `3 N_at`（对 6 原子原胞即为 `18`）。

在 **`ZrCl₂/Sc₂C`**（[完整计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)，使用 `nk1=48, nk2=48, nk3=1` 插值网格生成 [`zrclscc.phdos`](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.phdos)）与 **`SnSe₂/Sr₂N`**（[`srnsnse.phdos`](/Atlas/examples/snse2-sr2n/ph64/srnsnse.phdos)）中，将同种元素的原子列相加（如 `Cl = site 3 + site 4`，`Sc = site 5 + site 6`），并将 PHDOS 旋转为**水平图（X 轴为 PHDOS，Y 轴为频率 ω）**与左侧声子色散共享纵轴：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png" alt="ZrCl₂/Sc₂C 的声子色散、原子分辨水平 PHDOS 与 Eliashberg 谱函数联立图" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的原子分辨 PHDOS（中面板）与声子色散（左面板）、Eliashberg α<sup>2</sup>F(ω)（右面板）共享频率纵轴（0–18 THz）。中面板显示 Zr、Sc、Cl 振动分布在 0–10.11 THz，12.49–17.11 THz（原始 DFPT 网格为 12.38–17.11 THz）的高频光学带以 C 原子位移为主。</figcaption></figure>

这种“左色散 + 中水平 PHDOS”的共享纵轴排版比单独画一张横置 PHDOS 图多传递两层关键信息：
1. **比较色散与态密度的频段**：共享频率轴便于判断 PHDOS 峰附近有哪些近乎平坦的分支及原子贡献。PHDOS 对整个布里渊区积分，高对称路径只取部分 q 点；要确定峰来自哪个鞍点，还需检查该频段的完整 q 网格或等频分布。
2. **轻重元素频段分离与积分上限核验**：在 `ZrCl₂/Sc₂C` 中，`Zr/Sc/Cl` 分支位于 `0–10.11 THz`（直接 DFPT 网格为 `0–10.02 THz`），经 `10.11–12.49 THz` 的声子带隙后，以 `C` 原子位移为主的高频分支位于 `12.49–17.11 THz`（直接 DFPT 网格为 `12.38–17.11 THz`）；在 `SnSe₂/Sr₂N` 中，恢复 `M_N = 14.007` 后的 `N` 原子（锈红）高频光学支从错误质量下的 `4.49–6.70 THz` 移至 `7.99–11.94 THz`（已绘路径范围 `7.42–11.94 THz`）。这为设定 `lambda.x` 的频率积分上限 `emax` 提供了直接依据。

## 文献中的声子态密度（PHDOS）与色散对照图例（附 DOI 溯源）

在晶格动力学与超导文献中，声子态密度常与高对称路径声子色散或 Eliashberg 谱函数共享同一频率纵轴并列展示。下面结合两幅文献原图说明其常见布局：

### 1. 声子色散与元素分辨 PHDOS 的多体系并列对比（含 SOC 与 CDW 软模）

<figure class="research-figure"><img src="/Atlas/figures/literature/M5_Phonon_PHDOS_CDW_MoW_Bekaert2020_Fig3.jpg" alt="四种二维过渡金属碳氮化物在有无自旋轨道耦合及应变调控下的声子色散与元素分辨 PHDOS 对比图" loading="lazy"/><figcaption>四个子面板 (a)–(d) 依次展示 Mo<sub>2</sub>C、Mo<sub>2</sub>N、W<sub>2</sub>C 及 4% 双轴应变 W<sub>2</sub>N 在不含自旋轨道耦合（红虚线）与含自旋轨道耦合（蓝实线）下的声子色散及右侧共享频率轴的元素分辨 PHDOS；子面板 (d) 同时以绿色点线（标有 <code>CDW &lt;-</code>）叠绘未应变 W<sub>2</sub>N 在 M 点的电荷密度波软模虚频支。图片来源：Bekaert et al., <em>Nanoscale</em> <strong>12</strong>, 17354 (2020)，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

色散与右侧元素投影 PHDOS 使用同一频率轴，先读取每种材料的振动组成，再比较 SOC 与应变。碳化物具有较清楚的频段间隔；Mo₂N 的相应间隔闭合，氮化物中的金属与 N 振动不能按同一条频率线分开。W₂N 的未应变软模与 4% 应变结果另作对照。

### 2. 声子色散、模式耦合强度、元素分辨 PHDOS 与 Eliashberg α²F(ω) 多面板并列

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_5Panel_FatPhonon_PHDOS_a2F_BZ_hAlH2_Jiang_Fig3.jpg" alt="二维 h-AlH₂ 的振动方向投影色散、模式电声耦合常数、元素分辨 PHDOS、Eliashberg 谱函数与布里渊区耦合分布五面板图" loading="lazy"/><figcaption>二维金属氢化物 h-AlH<sub>2</sub> 的五面板组合图：(a) 振动方向与原子投影声子色散，(b) 模式分辨电声耦合强度 λ<sub>qν</sub>，(c) Al 与 H 的分波声子态密度 PHDOS，(d) Eliashberg 谱函数 α<sup>2</sup>F(ω) 与累计 λ(ω)，以及 (e) 二维布里渊区中的 λ(q) 分布。图片来源：Jiang et al., <em>Phys. Status Solidi RRL</em> <strong>18</strong>, 2300417 (2024)，<a href="https://doi.org/10.1002/pssr.202300417" target="_blank" rel="noopener noreferrer">DOI: 10.1002/pssr.202300417</a>。</figcaption></figure>

把 PHDOS 与 α²F 放在共同频率轴上，可以比较声子态数与耦合加权谱的差别。不过 α²F 还包含电子态的散射相空间和矩阵元权重；仅凭两条曲线的峰值对应，不能唯一分解各项贡献。解释具体频段时应继续检查逐 q、逐模的耦合与原子位移。

下一步可以回到 [声子色散](/Atlas/m/phonon-dfpt/qe/) 对照峰主要来自哪些近乎平坦的声子支，也可以到 [虚频排查](/Atlas/m/imaginary-phonon/qe/) 检查低频端的残差。

```text
固定结构 SCF → 完整 q 网格 DFPT → q2r 力常数
                                  ├→ matdyn 高对称路径 → 声子色散
                                  └→ matdyn 均匀网格 → 声子 DOS → 积分与网格检查
```

## 参考资料

[matdyn.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [q2r.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [PHonon 用户手册](https://www.quantum-espresso.org/Doc/ph_user_guide/)
