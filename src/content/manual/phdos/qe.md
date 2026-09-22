[matdyn.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [q2r.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [PHonon 用户手册](https://www.quantum-espresso.org/Doc/ph_user_guide/)

声子色散告诉我们一条指定路径上的频率怎样变化。声子态密度换了一个问法：在整个布里渊区里，有多少振动模式落在这一小段频率内？路径上的点再密，也不能代替布里渊区积分。

这里接着 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 的结果做。例子是新计算的单原子 fcc Al 原胞，使用 QE 7.5 和官方示例中的 `Al.pz-vbc.UPF`。这次完整计算了 4×4×4 q 网格；下面每一个文件都来自同一个 Al 结构、同一份 SCF 电荷密度。结构优化与 SCF 的步骤见 [晶胞优化](/Atlas/m/vc-relax/qe/) 和 [SCF](/Atlas/m/scf/qe/)，在这里从声子计算已经结束的目录开始。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

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

## 把积分数和图放在一起检查

解包本页开头的 Al 算例并保留目录结构，在 `al` 目录运行[绘图脚本](/Atlas/examples/al/plot_phdos.py)。脚本从 `dfpt/al.phdos.dat` 和 `dfpt/al.phdos32.dat` 读取 24³、32³ 两份数据；[单独下载的原始 DOS 数据](/Atlas/examples/al/dfpt/al.phdos.dat)也应放回对应的 `dfpt` 子目录。它先输出积分再画曲线，这样能发现列读错、单位弄错或数据截断的问题。

```bash
python3 plot_phdos.py
```

本次 24³ 网格的积分是 **2.99953038**；32³ 网格为 **2.99931874**。完整频率范围是约 0—332 cm⁻¹。两次积分都应与 3 对照，而不是强行归一化后再宣布通过。

<figure><img src="/Atlas/examples/al/figures/phdos.png" alt="Al 声子态密度，24与32网格积分比较" loading="lazy"/><figcaption>同一份 4×4×4 DFPT 力常数上的两种积分网格。曲线是实际输出的 DOS，没有手工平滑或补点。</figcaption></figure>

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
比较时要分开两个问题：积分网格变密后峰形和积分是否稳定；原始 DFPT q 网格变密后力常数是否稳定。这里已完成前一项检查的两组计算，后一项仍需独立 q 网格系列。当前这张图可以用于理解声子 DOS 和检查数据链条，不能直接作为 Al 声子谱已数值收敛的证明。

下一步可以回到 [声子色散](/Atlas/m/phonon-dfpt/qe/) 对照峰主要来自哪些近乎平坦的声子支，也可以到 [虚频排查](/Atlas/m/imaginary-phonon/qe/) 检查低频端的残差。

```text
固定结构 SCF → 完整 q 网格 DFPT → q2r 力常数
                                  ├→ matdyn 高对称路径 → 声子色散
                                  └→ matdyn 均匀网格 → 声子 DOS → 积分与网格检查
```
