参考：

- [PHonon 用户指南](https://www.quantum-espresso.org/Doc/ph_user_guide/)
- [ph.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PH.html)
- [q2r.x 输入](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html)
- [matdyn.x 输入](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)

## 从十个 q 点到一张声子图

先看这次计算最后得到的图，再沿文件往回找它是怎样生成的。每条线是一支声子频率；横轴是 Γ–M–K–Γ 路径，不是整片布里渊区。

![Sc2C/ZrCl2 沿 Γ–M–K–Γ 的插值声子频率，单位 cm⁻¹](/Atlas/figures/phonon.svg)

这里使用 Sc₂C/ZrCl₂ 主算例的 `ph64` 目录，输出标明 QE 7.1、运行于 2026 年 6 月；以下命令于 2026-09-22 读取这些已有文件。它与前面 HfCl₂/PbO₂ 的结构优化是两个独立算例，结构、赝势和保存目录不能交叉使用。本次没有重新提交计算，也没有把其他机器上的补充尝试并入这条链。页首在线手册用于查阅；涉及旧版本的具体行为，以本算例输出和对应版本文档复核。

## 先核对电子网格与声子网格

目录叫 `ph64`，并不意味着声子用了 64×64×1。打开输入查看：

```text
[<user>@<cluster> 2]$ grep -A1 K_POINTS ph64/pwx.in ph64/pwxall.in ph96/pwxall.in; grep -E 'nq[123]' ph64/phx.in ph96/phx.in
ph64/pwx.in:K_POINTS automatic
ph64/pwx.in-  16 16 1 0 0 0
--
ph64/pwxall.in:K_POINTS automatic
ph64/pwxall.in-  64 64 1 0 0 0
--
ph96/pwxall.in:K_POINTS automatic
ph96/pwxall.in-  96 96 1 0 0 0
ph64/phx.in:  nq1=8
ph64/phx.in:  nq2=8
ph64/phx.in:  nq3=1
ph96/phx.in:  nq1=8
ph96/phx.in:  nq2=8
ph96/phx.in:  nq3=1
[<user>@<cluster> 2]$
```

`pwx.in` 是 16×16×1 的粗电子网格，`pwxall.in` 保存 64×64×1 密电子网格的数据；`phx.in` 的 `nq1/nq2/nq3` 才是 8×8×1 声子网格。这里保留了 EPC 开关，密网格与粗网格的衔接见[电声耦合页](/Atlas/m/epc/qe/)。纯声子计算不需要照搬 EPC 部分。

## 每份输入负责哪些 q 点

先读取第一批输入。四种原子的质量与本算例的 Zr、Cl、Sc、C 顺序对应：

```text
[<user>@<cluster> ph64]$ cat phx.in
  &inputph
  tr2_ph=1.0d-16
  nmix_ph=12
  verbosity='high'
  prefix='zrclscc'
  fildvscf='zrclsccdv'
  amass(1)=91.224
  amass(2)=35.450
  amass(3)=44.956
  amass(4)=12.011
  outdir='./out/'
  fildyn='zrclscc.dyn'
  electron_phonon='interpolated'
  el_ph_sigma=0.001
  el_ph_nsigma=20
  trans=.true.
  ldisp=.true.
  start_q=1
  last_q=1
  nq1=8
  nq2=8
  nq3=1
/
[<user>@<cluster> ph64]$
```

不要只凭文件名猜分工，直接读取范围，再对照各自输出：

```text
[<user>@<cluster> ph64]$ grep -E 'start_q|last_q' phx.in phx1.in phx2.in phx3.in; grep 'JOB DONE' phx.out phx1.out phx2.out phx3.out
phx.in:  start_q=1
phx.in:  last_q=1
phx1.in:  start_q=2
phx1.in:  last_q=4
phx2.in:  start_q=5
phx2.in:  last_q=7
phx3.in:  start_q=8
phx3.in:  last_q=10
phx.out:   JOB DONE.
phx1.out:   JOB DONE.
phx2.out:   JOB DONE.
phx3.out:   JOB DONE.
[<user>@<cluster> ph64]$
```

范围覆盖 1–10，四份输出都有结束标志。这只完成了最初的清点，还要检查各批错误、响应收敛、动力学矩阵是否非空，才能进行后处理。共同读取一个 SCF 目录也不意味着各批可以任意同时写同一套工作文件；新的并行任务必须核对独立工作目录和该版本的分批规则。

计算过程中可以另开终端运行 `tail -f phx.out`，或 `watch -n 5 "grep -E 'Representation|Convergence|Error' phx.out | tail -n 20"`。每个 representation 内部都有响应迭代，不要把某一个 representation 的收敛当成整批结束。

## q2r：先保留警告，再读取力常数

本次留存的输入是：

```text
[<user>@<cluster> ph64]$ cat q2rx.in
&input
zasr='crystal'
fildyn='zrclscc.dyn'
flfrc='zrclscc.fc'
la2F=.true.
/
[<user>@<cluster> ph64]$
```
```text
[<user>@<cluster> ph64]$ grep 'fft-check warning' q2rx.out
      fft-check warning: sum of imaginary terms = 2.414214E-08
      fft-check warning: sum of imaginary terms = 1.207107E-08
      fft-check warning: sum of imaginary terms = 2.414214E-08
      fft-check warning: sum of imaginary terms = 1.207107E-08
[<user>@<cluster> ph64]$
```

文件中既有 `fft-check success`，也有上面的 warning。只 grep success 会漏掉它们。这里如实保留这次输出；是否影响目标频率，需要比较完整动力学矩阵、力常数和直接 q 点结果，不能凭 warning 数字较小就宣布通过。

## matdyn：把力常数沿路径展开

```text
[<user>@<cluster> ph64]$ cat matdynxline.in
&input
  asr='crystal'
  amass(1)=91.224
  amass(2)=35.450
  amass(3)=44.956
  amass(4)=12.011
  flfrc='zrclscc.fc'
  flfrq='zrclscc.freq'
  la2F=.true.
  dos=.false.
  q_in_band_form = .true.
  q_in_cryst_coord = .true.

/
4
0.0000000000   0.0000000000   0.0000000000 50    !G
0.5000000000   0.0000000000   0.0000000000 50    !M
0.3333333333   0.3333333333   0.0000000000 50    !K
0.0000000000   0.0000000000   0.0000000000  1    !G
/
[<user>@<cluster> ph64]$
```

`zrclscc.freq.gp` 是本页作图读取的表。第一列为累计路径坐标，其余 18 列为这个六原子模型的频率。图中按原文件绘线，没有删除负值或人为把曲线抬到零以上。`asr='crystal'` 已是这次后处理的一部分，应与原始动力学矩阵的频率区分。

图的[数值摘录](/Atlas/data/teaching-extracts.json)保留了文件哈希；绘图脚本随网站源码保存，可复现本页图形。沿这条路径没有明显负值，并不足以代替完整 q 空间和数值收敛检查。

## 下一步

继续[检查虚频与原始频率的差别](/Atlas/m/imaginary-phonon/qe/)，再决定是否进入[电声数据检查](/Atlas/m/epc/qe/)。

```text
本算例的电子数据 → 分批 ph.x → 各批输出与 dyn 文件核对
                                      ↓
                                q2r → matdyn
                                      ↓
                        原始频率 / ASR 后频率 / 路径图对照
```
