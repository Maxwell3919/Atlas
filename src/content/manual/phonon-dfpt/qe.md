界面形成后，声子谱的变化可以来自键长、层间相互作用和电子占据的共同变化。先知道哪一支变软，再看参与运动的原子与方向，才能把频率变化接回界面结构。对于六原子原胞的 ZrCl₂/Sc₂C，18 条分支既包含整个异质结的声学运动，也包含层内振动和两层之间的相对运动；一条低频支不能仅按频率命名为层间剪切或呼吸模。

下面先用单原子 fcc Al 走通 `ph.x → q2r.x → matdyn.x`。它展示完整 q 网格、原始矩阵与插值色散的文件关系；单原子原胞只有三条声学支，不包含异质结的层间光学模式。Al 采用 QE 7.5、LDA-PZ 和官方 `Al.pz-vbc.UPF`，结构来自 [Al 晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax)，立方晶格常数为 3.95606780 Å。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

[Baroni 等 DFPT 综述](https://doi.org/10.1103/RevModPhys.73.515)式 (81)–(84) 将力常数、质量与频率联系起来，式 (99) 给出均匀 q 网格到实空间力常数的变换。这条关系也决定了后面怎样解释不同原子参与的振动。

## SCF 目录里要留下什么

SCF 的建立与迭代过程见 [固定结构 SCF](/Atlas/m/scf/qe/)。到声子这一步，最关心的是使用了哪一份结构、`prefix`、`outdir`，以及目录里的电荷密度和波函数是否属于刚检查过的那次 SCF。

```console
maxwell@maxwell:~/al/dfpt$ cat al.scf.in
&CONTROL
 calculation = 'scf'
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 0
 nat = 1
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 6
/
&ELECTRONS
 conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.97803390040536 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.97803390040536 1.97803390040536 0.00000000000000
K_POINTS automatic
16 16 16 0 0 0
```
本例明确写出原胞的三条晶格矢量，所以采用 `ibrav=0`。程序会提示这不是它最推荐的对称性表达方式；我们保留了完整精度的 fcc 晶格，继续核对程序识别的结构及 q 点对称性，没有把提示从原始输出中删掉。电子网格是 16×16×16，波函数/电荷密度截断为 40/160 Ry，`degauss=0.02 Ry`。这些值定义了本例的电子采样与基组；声子频率对它们的敏感性需要另外检查。

Al 的能带穿过费米能，因此这里用 `occupations='smearing'` 和 `smearing='mv'` 处理部分占据。0.02 Ry 约为 0.272 eV，是本次冷展宽参数；把它减小会改变费米面附近的占据和响应，需要同时比较电子 k 网格。`nbnd=6` 保留空态，让展宽附近的占据有足够的能带可用；换成另一材料时，应在 OUT 中核对最高带的占据是否已经可以忽略。较紧的 `conv_thr=1.0d-12` 先约束基态电子误差，下面的 `tr2_ph` 则另管响应迭代。

```console
maxwell@maxwell:~/al/dfpt$ grep -A6 "convergence has been achieved" al.scf.out
     convergence has been achieved in   7 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
```
这里的 7 次迭代说明固定结构电子循环达到输入的阈值。单原子 fcc 原胞的三个力分量为零；这来自对称性，仍需要从结构优化的应力与 BFGS 结束信息检查晶格。

```console
maxwell@maxwell:~/al/dfpt$ ls tmp/al.save
Al.pz-vbc.UPF  charge-density.dat  data-file-schema.xml  wfc1.dat  ...
```
`data-file-schema.xml` 记录结构、计算参数与能带等信息，`charge-density.dat` 是 SCF 电荷密度，`wfc*.dat` 是波函数文件。上面的文件列表省略了后续波函数编号；[完整 SCF 输出](/Atlas/examples/al/dfpt/al.scf.out) 保留程序实际读取与写出的记录。不要只复制 `al.scf.out` 后就删除 `tmp`，`ph.x` 还需要里面的二进制数据。

## 给 ph.x 一张完整网格

```console
maxwell@maxwell:~/al/dfpt$ cat al.ph.in
&INPUTPH
 prefix = 'al'
 outdir = './tmp'
 fildyn = 'al.dyn'
 amass(1) = 26.9815385
 tr2_ph = 1.0d-14
 ldisp = .true.
 nq1 = 4
 nq2 = 4
 nq3 = 4
/
```
`prefix` 和 `outdir` 与 SCF 完全相同。`ldisp=.true.` 连同 `nq1=nq2=nq3=4` 请求完整均匀 q 网格；文件名 `al.dyn` 会扩展为索引与各个不可约点的动力学矩阵。`amass(1)` 是这里 Al 的质量，不能照抄另一个元素的质量。声子频率包含质量因子，电子 SCF 不报错也不能说明质量填对了。

`tr2_ph=1.0d-14` 要在每个 q 点、每个实际求解的表示上满足。它限制的是响应自洽，不是直接给频率设一个误差条。`4³` 是本次直接求解的 q 网格；后面把绘图路径加密，只是在这组矩阵之间插值。要检查力常数的实空间范围和色散是否受网格限制，需要另算更密的原始 q 网格再比较。

实际提交采用下面的 Slurm 脚本。这里先在本目录重做固定结构 SCF，然后运行 `ph.x`，并在它成功返回后调用后处理程序；脚本里的 `set -e` 会在某一步非零退出时停止。资源是 Maxwell 实际分配的 8 个 MPI 进程，每进程 1 个 OpenMP 线程。

```console
maxwell@maxwell:~/al/dfpt$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-ph4
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
mpirun -np 8 <qe_bin>/ph.x -in al.ph.in > al.ph.out 2> al.ph.err
<qe_bin>/dynmat.x -in dynmat-no.in > dynmat-no.out 2> dynmat-no.err
<qe_bin>/dynmat.x -in dynmat-simple.in > dynmat-simple.out 2> dynmat-simple.err
<qe_bin>/dynmat.x -in dynmat-crystal.in > dynmat-crystal.out 2> dynmat-crystal.err
<qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err
<qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
<qe_bin>/matdyn.x -in matdyn-band.in > matdyn-band.out 2> matdyn-band.err
```
```console
maxwell@maxwell:~/al/dfpt$ sbatch run.slurm
Submitted batch job 1955
```
运行时可以开另一个终端查看队列，再看输出的新行。`squeue` 里的 R 只说明程序正在占用计算资源，不表示某个 q 点已经通过；`tail -f` 不会重新执行计算，按 Ctrl-C 退出的是查看命令。

```bash
squeue -j 1955 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f al.ph.out
```

## 从 OUT 中认出程序正在做哪一层

声子输出开头先报程序版本、MPI 进程数、读取的 SCF 目录和交换关联泛函。检查这些信息，是为了发现看似运行正常却读到了另一套母体文件的情况。

```console
maxwell@maxwell:~/al/dfpt$ head -35 al.ph.out

     Program PHONON v.7.5 starts on 22Sep2026 at 21:35: 5 

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org", 
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     8 processors

     MPI processes distributed on     1 nodes
     12199 MiB available memory on the printing compute node when the environment starts
 
     Reading input from al.ph.in
      Title line not specified: using 'default'.

     Reading xml data from directory:

     ./tmp/al.save/
 
     R & G space division:  proc/nbgrp/npool/nimage =       8
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PZ
                           (   1   1   0   0   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want
```
接下来程序列出实际要算的不可约 q 点：

```console
maxwell@maxwell:~/al/dfpt$ grep -A11 "Dynamical matrices for" al.ph.out
Dynamical matrices for ( 4, 4, 4)  uniform grid of q-points
     (   8 q-points):
       N         xq(1)         xq(2)         xq(3) 
       1   0.000000000   0.000000000   0.000000000
       2  -0.176776695   0.176776695  -0.176776695
       3   0.353553391  -0.353553391   0.353553391
       4   0.000000000   0.353553391   0.000000000
       5   0.530330086  -0.176776695   0.530330086
       6   0.353553391   0.000000000   0.353553391
       7   0.000000000  -0.707106781   0.000000000
       8  -0.353553391  -0.707106781   0.000000000
```
这里的 8 个点通过对称性对应 4×4×4 的全部 64 点；它不是一条高对称线。每个 q 点下还分为若干不可约表示。原胞有 1 个原子，总共有 3 个振动自由度；简并会让表示数与模式数不同。

```console
maxwell@maxwell:~/al/dfpt$ less al.ph.out
     Representation #   1 modes #   1   2   3

     Self-consistent Calculation
 
     Pert. #  1: Fermi energy shift (Ry) =     1.8849E-27     8.6203E-38
     Pert. #  2: Fermi energy shift (Ry) =     0.0000E+00    -7.2881E-37
     Pert. #  3: Fermi energy shift (Ry) =    -2.1878E-27    -1.1755E-38

      iter #   1 total cpu time :     0.6 secs   av.it.:   3.5
      thresh= 1.000E-02 alpha_mix =  0.700 |ddv_scf|^2 =  3.930E-09
 
     Pert. #  1: Fermi energy shift (Ry) =     2.2887E-27    -1.3775E-40
     Pert. #  2: Fermi energy shift (Ry) =    -1.0771E-27    -1.1632E-39
     Pert. #  3: Fermi energy shift (Ry) =     6.7316E-28     1.7602E-40

      iter #   2 total cpu time :     1.1 secs   av.it.:   6.2
      thresh= 6.269E-06 alpha_mix =  0.700 |ddv_scf|^2 =  4.151E-10
 
     Pert. #  1: Fermi energy shift (Ry) =     4.7121E-27     2.4872E-41
     Pert. #  2: Fermi energy shift (Ry) =    -2.1541E-27    -1.5306E-40
     Pert. #  3: Fermi energy shift (Ry) =    -5.0487E-27    -8.6096E-42

      iter #   3 total cpu time :     1.6 secs   av.it.:   6.0
      thresh= 2.037E-06 alpha_mix =  0.700 |ddv_scf|^2 =  3.973E-14
 
     Pert. #  1: Fermi energy shift (Ry) =    -5.1160E-27    -1.6741E-42
     Pert. #  2: Fermi energy shift (Ry) =    -5.3853E-28    -2.8699E-42
     Pert. #  3: Fermi energy shift (Ry) =     7.4048E-28     4.6635E-42

      iter #   4 total cpu time :     2.1 secs   av.it.:   6.8
      thresh= 1.993E-08 alpha_mix =  0.700 |ddv_scf|^2 =  3.401E-15

     End of self-consistent calculation

     Convergence has been achieved
```
读迭代时先看 `Calculation of q`，再看 `Representation`，最后看残差和 `Convergence has been achieved`。一个表示通过后，还会继续同一点的其余表示，再进入下一个 q 点。正在变化的 `thresh` 是内层求解量，不能拿它直接替代输入的 `tr2_ph` 判断响应收敛。

## 动力学矩阵与最终收尾要一起检查

```console
maxwell@maxwell:~/al/dfpt$ tail -18 al.dyn1

    1    1
  0.00001754   0.00000000    -0.00000000   0.00000000    -0.00000000   0.00000000
 -0.00000000   0.00000000     0.00001754   0.00000000     0.00000000   0.00000000
 -0.00000000   0.00000000     0.00000000   0.00000000     0.00001754   0.00000000

     Diagonalizing the dynamical matrix

     q = (    0.000000000   0.000000000   0.000000000 ) 

 **************************************************************************
     freq (    1) =       0.087851 [THz] =       2.930394 [cm-1]
 ( -0.004507  0.000000 -0.776815  0.000000  0.629712  0.000000 ) 
     freq (    2) =       0.087851 [THz] =       2.930394 [cm-1]
 ( -0.561009  0.000000 -0.519320  0.000000 -0.644651  0.000000 ) 
     freq (    3) =       0.087851 [THz] =       2.930394 [cm-1]
 ( -0.827797  0.000000  0.356180  0.000000  0.433460  0.000000 ) 
 **************************************************************************
```
每个频率后面的 6 个数是这个原子在 x、y、z 三个方向位移的实部/虚部，不是 6 个原子坐标。这里 Γ 点原始 3 支都是 +2.930394 cm⁻¹，显示了有限数值精度的平移残差；本例的同矩阵 ASR 对照保存在 [gamma-check](/Atlas/examples/al/dfpt/gamma-check/dynmat-crystal.out)。如何连同本征位移解释这类变化，见 [Si 的虚频排查算例](/Atlas/m/imaginary-phonon/qe/)。

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
本次 `ph.x` 用时 3 分 11.61 秒，8 个不可约点全部走完。随后 `q2r.out` 还必须确认完整网格重建成功：

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
`q2r.x` 已将这些矩阵变为 `al.fc`。[本次 q2r.in](/Atlas/examples/al/dfpt/q2r.in) 中，`fildyn='al.dyn'` 指向刚完成的矩阵，`flfrc='al.fc'` 指定实空间力常数文件。输入还保留 `zasr='simple'`；q2r 的这个选项针对 Born 有效电荷，不能当成下一步对力常数施加 `asr='crystal'` 的替代。本例是金属 Al，`q2r.out` 明确打印 `Dielectric Tensor not found`，没有把缺少非金属介电张量当作计算中断。输入、输出及全部动力学矩阵可从 [Al 示例文件](/Atlas/examples/al/manifest.json) 对照核验。

## 沿 Γ—X—W—L—Γ 把频率画出来

```console
maxwell@maxwell:~/al/dfpt$ cat matdyn-band.in
&INPUT
 flfrc='al.fc'
 asr='crystal'
 flfrq='al.freq'
 q_in_cryst_coord=.true.
 q_in_band_form=.true.
/
5
0 0 0 40
0.5 0 0.5 40
0.5 0.25 0.75 40
0.5 0.5 0.5 40
0 0 0 1
```
这里的 q 坐标是与本例原胞对应的倒格矢分数坐标。节点后面的 40 控制到下一节点的取点数；不能把另一种原胞定义下的标签直接贴到这份坐标上。`asr=crystal` 记录了插值时采用的声学和规则。

```console
maxwell@maxwell:~/al/dfpt$ head -6 al.freq.gp
  0.000000      -0.0000   -0.0000    0.0000
  0.017678       8.4332    8.4332   15.7366
  0.035355      16.8532   16.8532   31.4113
  0.053033      25.2468   25.2468   46.9631
  0.070711      33.6004   33.6004   62.3325
  0.088388      41.9005   41.9005   77.4626
```
第一列是路径距离，后面 3 列分别对应三支声子频率，单位 cm⁻¹。[绘图脚本](/Atlas/examples/al/plot_phonon.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 直接读取这 4 列，按节点位置加标签，不再手工抄频率。


绘图脚本读取 `dfpt/al.freq.gp` 的路径距离和三列频率，再按五个节点放置标签。下面的编程需求对应这份路径数据：

```text
编写 plot_phonon.py，从 Al 根目录读取 dfpt/al.freq.gp，要求 161 行、4 列。首列是路径累计距离，后三列为 cm⁻¹ 频率，直接绘制全部三条分支并保留负号。以行 0、40、80、120、160 的距离标 Γ—X—W—L—Γ，画零线和分段界线，输出 figures/phonon-dfpt.png 与 PDF。使用同目录 atlas_plot_style.py，读取文件而不是从示意图拟合曲线。
```

<details>
<summary>plot_phonon.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=np.loadtxt(r/"dfpt/al.freq.gp")
assert d.shape==(161,4), d.shape
fig,ax=plt.subplots(figsize=(7,4.3),layout="constrained")
for i in range(1,4):ax.plot(d[:,0],d[:,i],lw=1.6,color="#0072b2")
ticks=d[[0,40,80,120,160],0]
ax.set_xticks(ticks,["Γ","X","W","L","Γ"])
for x in ticks:ax.axvline(x,color="0.8",lw=.7)
ax.axhline(0,color="0.4",lw=.7)
ax.set(xlim=(ticks[0],ticks[-1]),ylabel="Frequency (cm⁻¹)")
(r/"figures").mkdir(exist_ok=True)
fig.savefig(r/"figures/phonon-dfpt.png",dpi=220);fig.savefig(r/"figures/phonon-dfpt.pdf")
```

</details>

```bash
python3 plot_phonon.py
```

<figure><img src="/Atlas/examples/al/figures/phonon-dfpt.png" alt="Al 的 DFPT 声子色散" loading="lazy"/><figcaption>4×4×4 DFPT q 网格经 q2r 和 matdyn 得到的 Γ—X—W—L—Γ 插值色散。</figcaption></figure>

这条路径上三条声学支从 Γ 的零频附近展开，未出现明显的有限 q 负频支。它来自 4³ 原始响应网格；161 个绘图点只是对这组力常数插值。检查某一异常频段时，应把该 q 的直接矩阵与插值结果对应起来，路径加密本身不会增加电子响应信息。

## 将频率、本征矢和原子位移连起来

动力学矩阵是力常数的质量加权形式。若 $C(\mathbf q)$ 是未除质量的 Fourier 力常数、$M_I$ 是原子质量，则

$$
\begin{aligned}
D_{I\alpha,J\beta}(\mathbf q)&=\frac{C_{I\alpha,J\beta}(\mathbf q)}{\sqrt{M_I M_J}},\\
D(\mathbf q)e_{\mathbf q\nu}&=\omega_{\mathbf q\nu}^{2}e_{\mathbf q\nu}.
\end{aligned}
$$

频率与向量是一对结果：模式编号 ν 必须对应同一个 q、同一次对角化和同一种 ASR 设置。上面的 `.freq.gp` 只有路径距离与频率，没有原子运动；模式归属要回到逐模向量文件。QE 的 `fleig` 保存正交动力学矩阵本征矢 e；`flvec` 保存 e 除以 √M 后逐模归一化的原子位移 u。多元素体系里，轻原子的位移权重会与其本征矢权重不同。[matdyn 字段说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)分别定义了这两个输出。

用 e 做原子或层投影时，某一层 L 的权重为 $W_L=\sum_{I\in L,\alpha}|e_{I\alpha}|^2$；用归一化 u 做方向分析时，$W_z=\sum_I|u_{Iz}|^2$，面内权重为 $W_{xy}=\sum_I(|u_{Ix}|^2+|u_{Iy}|^2)$。写图例时应说明所用向量。判断两层相对运动还要看位移的相位：两层沿 z 反向移动才可能构成层间呼吸，两层沿面内反向移动才可能构成层间剪切。仅把同一层的平方权重相加，会丢掉这项信息。

在 Γ 点，整个异质结的三个刚性平移应接近零，而两层之间有恢复力的相对移动可以是低频光学模。这也是为什么不能把 Γ 点所有低频模式都交给 ASR 消去。对于简并模式，单个本征矢的方向可以在简并子空间内变化；比较应变前后的运动时，应比较整组简并模式及其层/方向权重。

## 界面存档中的质量与频段

ZrCl₂/Sc₂C 的六个原子按 [原始结构输入](/Atlas/examples/zrcl2-sc2c/ph64/pwx.in) 排列为 `Zr, C, Cl, Cl, Sc, Sc`。其中第 1、3、4 个原子构成 ZrCl₂ 层，第 2、5、6 个原子构成 Sc₂C 层。原子序号用于位移与 PHDOS 列；`amass(i)` 的 i 则按 `ATOMIC_SPECIES` 的元素类型顺序，两个索引不能混用。

已有 8×8×1 q 网格的[路径频率](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.freq.gp)显示，中低频 15 支覆盖约 0–10.11 THz，高频 3 支位于 12.49–17.11 THz。结合[原子 PHDOS](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.phdos)，高频段主要投影在 C 上。这个元素归属描述的是谱中的模态组成；若要判定 C 沿面内还是面外移动，或某一支是否改变界面间距，还要读取对应的 e 或 u。这套历史完整 q 分支的公开资源提供输入、路径频率与 PHDOS；下面独立的 +1.5% Γ 对照则提供原始矩阵与完整模式向量。

SnSe₂/Sr₂N 的存档提供了另一种具体问题：旧输入将 N 的类型质量写为 118.71，而真实质量为 14.007。[错误质量色散](/Atlas/examples/snse2-sr2n/ph64/srnsnse.wrong_mass.freq.gp)与[恢复质量后的色散](/Atlas/examples/snse2-sr2n/ph64/srnsnse.freq.gp)中，高频三支的 Γ 频率由 4.60、5.56、6.70 THz 变为 7.99、7.99、10.74 THz。单一 N 运动极限下，质量比会使频率缩小约 $\sqrt{118.71/14.007}=2.91$ 倍；实际混合模式不要求逐支满足这个比例。这段存档说明质量如何进入动力学矩阵，不能把质量修正解释为应变软化或电子掺杂效应。对应 PHDOS 的原子列与积分复核见[声子态密度](/Atlas/m/phdos/qe/#h-按真实原子顺序合成元素与层投影)。

## 一组真实界面 Γ 模式的矩阵与位移

ZrCl₂/Sc₂C 的 +1.5% 结构已有固定 32² 电荷密度下的 Γ16²/Γ32² 响应对照。它与上一节历史完整 q 网格分支分别保存，不能拼成一份新的全布里渊区谱。这里读取已经过独立 QA 的 [Γ16² 原始矩阵](/Atlas/examples/phonons-interface-gamma/gamma16.dyn)和[Γ32² 原始矩阵](/Atlas/examples/phonons-interface-gamma/gamma32.dyn)，采用同一实 Γ `crystal` 平移投影，重建全部 18 个频率，并保留 15 维光学子空间的向量。

矩阵头部给出原子顺序 `Zr, C, Cl, Cl, Sc, Sc`；τ 是以 alat 为单位的笛卡尔坐标，`alat=6.3466021 Bohr`。导出位置按 $r=\tau\times\mathrm{alat}\times0.529177210903\,\text{\AA}$ 换算；动力学矩阵中的质量保留 QE 内部单位。后处理先在未质量加权实力常数上施加三个平移约束，再除以 $\sqrt{M_I M_J}$ 对角化，不把层间相对运动删掉。

对最低的光学双态，脚本将本征矢投影到两层刚性面内相对移动的质量加权模板，并与整体平移正交。这项权重约为 0.863，说明其运动主要是层间面内相对位移，同时仍含层内变形。逐原子的 e、归一化 u、元素和层权重可从[Γ32 向量表](/Atlas/examples/phonons-interface-gamma/gamma32-vectors.csv)及[完整模式结果](/Atlas/examples/phonons-interface-gamma/gamma-mode-products.json)查看。

```text
gamma16 lowest optical cm-1: 86.60094036 86.60094036 120.22328804
  lowest E pair relative-inplane weight: 0.86281512 0.86281512
  raw matrix reproduction max error: 1.066e-05 cm-1
gamma32 lowest optical cm-1: 75.22373393 75.22373393 121.49161046
  lowest E pair relative-inplane weight: 0.86283674 0.86283674
  raw matrix reproduction max error: 7.552e-06 cm-1
```

同身份低频双态从 Γ32² 的 75.22373 cm⁻¹ 到 Γ16² 的 86.60094 cm⁻¹，相差约 15.12%；两组相对层移动权重几乎相同，运动身份没有因频率变化而变成另一类模式。固定密度和结构仍不足以把差别完全归于网格密度：Γ16 采用严格外部 NSCF，既有 Γ32 使用自适应电子求解，电子求解路径也有差别。这组对照显示该低频运动的实际敏感性，Γ32 不是已确定的真值，也没有由此建立有限 q 或完整 EPC 收敛。

[Γ32 最低光学双态的第一个成员动画](/Atlas/examples/phonons-interface-gamma/gamma32-optical-1.axsf)、[第二个成员](/Atlas/examples/phonons-interface-gamma/gamma32-optical-2.axsf)和[第三个光学模式](/Atlas/examples/phonons-interface-gamma/gamma32-optical-3.axsf)可在 XCrySDen 中打开。每个动画有 36 个相位帧，所有原子共用一个显示比例，最大原子偏移为 0.10 Å；方向与相对振幅直接来自该矩阵的 $e/\sqrt{M}$，没有为不同原子单独调整箭头或振幅。这个放大幅度用于看清运动，不表示热振幅。简并双态的单个方向随所选基底改变，因此应把两个成员一起读。

复算这组后处理可[下载完整包](/Atlas/examples/phonons-interface-gamma-files.tar.gz)，进入 `phonons-interface-gamma` 后执行：

```bash
python3 analyse_gamma_modes.py
```

源码使用 NumPy 2.4.6、SciPy 1.18.0，实际运行只读取两份矩阵。下面的编程需求对应这组真实数据：

```text
读取 gamma16.dyn 与 gamma32.dyn 的六原子实 Γ 矩阵，核对源身份、原子顺序、晶胞、q=0 和 Hermitian 性。保留原生质量单位；用 QE 7.2 频率换算重现文件的18个原始频率。对实力常数施加三个整体平移 crystal 投影，再在质量加权光学子空间对角化。保留15个光学模式的频率、e、e/√M归一化后的u、逐原子和逐层本征矢权重，计算层间面内/面外相对运动模板的权重。为前三个光学模式导出36相位帧的周期AXSF，整模共同放大到最大原子偏移0.10 Å；注明显示比例和简并基底。不得重跑DFT或由排序直接宣称模式身份。
```

<details>
<summary>analyse_gamma_modes.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Read accepted real-Gamma QE 7.2 matrices; export mode weights and AXSF frames.

crystal ASR acts on real Cartesian force constants before mass weighting.
Only these real Hermitian Gamma data are supported. No DFT or job submission.
"""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np
from scipy.linalg import null_space

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "gamma16": "c692eab1e220ed8f43a9d8714755f5462d227e6ccaa4d1a331ebb8b40e13b5e6",
    "gamma32": "833f0fbe22d8bb679acfe785b92add032223f6d48fb539ba15eafb2013e154e7",
}
H_PLANCK = 6.62607015e-34
HARTREE = 4.3597447222071e-18
C_LIGHT = 2.99792458e8
AU_PS = H_PLANCK / (2 * np.pi * HARTREE) * 1e12
RY_CM = 1e10 / (AU_PS * 4 * np.pi * C_LIGHT)
BOHR_A = 0.529177210903
LAYERS = {"ZrCl2": [0, 2, 3], "Sc2C": [1, 4, 5]}


def load(path):
    lines = path.read_text().splitlines()
    ntype, nat = map(int, lines[2].split()[:2])
    alat = float(lines[2].split()[3])
    i = lines.index("Basis vectors")
    cell = np.array([list(map(float, l.split())) for l in lines[i+1:i+4]]) * alat * BOHR_A
    species = {}
    for line in lines[i+4:i+4+ntype]:
        match = re.fullmatch(r"\s*(\d+)\s+'([^']+)'\s+(\S+)\s*", line)
        species[int(match[1])] = (match[2].strip(), float(match[3]))
    atomlines = [l.split() for l in lines[i+4+ntype:i+4+ntype+nat]]
    symbols = [species[int(l[1])][0] for l in atomlines]
    mass = np.array([species[int(l[1])][1] for l in atomlines])
    positions = np.array([list(map(float, l[2:5])) for l in atomlines]) * alat * BOHR_A
    qline = next(j for j, l in enumerate(lines) if re.match(r"\s*q\s*=", l))
    q = np.fromstring(re.search(r"\(([^)]+)\)", lines[qline])[1], sep=" ")
    assert np.allclose(q, 0) and symbols == ["Zr", "C", "Cl", "Cl", "Sc", "Sc"]
    force = np.zeros((3*nat, 3*nat), complex)
    j = qline + 1
    for _ in range(nat*nat):
        while not lines[j].strip(): j += 1
        a, b = map(int, lines[j].split())
        for alpha in range(3):
            row = np.array(list(map(float, lines[j+1+alpha].split())))
            force[3*(a-1)+alpha, 3*(b-1):3*b] = row[::2] + 1j*row[1::2]
        j += 4
    printed = np.array([float(m[1]) for l in lines
                        for m in [re.search(r"freq.*=\s*([-+\d.]+)\s*\[cm-1\]", l)] if m])
    assert printed.size == 3*nat
    assert np.max(np.abs(force.imag)) < 1e-12
    assert np.linalg.norm(force-force.conj().T) < 1e-12
    return force.real, mass, symbols, cell, positions, printed


def frequency(v):
    return np.sign(v) * np.sqrt(np.abs(v)) * RY_CM


def save_axsf(path, symbols, cell, positions, normalized_u):
    # Common scale for the entire mode; max atomic excursion = 0.10 Angstrom.
    # 36 equally spaced phases cover one period. This is a visualization scale,
    # not a thermal displacement or a finite-distortion energy calculation.
    amplitude = 0.10 / np.max(np.linalg.norm(normalized_u, axis=1))
    frames = ["ANIMSTEPS 36", "CRYSTAL", "PRIMVEC"]
    frames += [" ".join(f"{x:.12f}" for x in row) for row in cell]
    for step, phase in enumerate(np.linspace(0, 2*np.pi, 36, endpoint=False), 1):
        frames += [f"PRIMCOORD {step}", f"{len(symbols)} 1"]
        displaced = positions + amplitude * np.cos(phase) * normalized_u
        frames += [s + " " + " ".join(f"{x:.12f}" for x in row)
                   for s, row in zip(symbols, displaced)]
    path.write_text("\n".join(frames) + "\n")
    return amplitude


def main():
    report = {"q_fractional": [0, 0, 0], "structure": "ZrCl2/Sc2C +1.5%",
              "ASR": "real force-constant crystal projection; three translations",
              "frequency_unit": "cm-1", "mass_unit": "QE native amu_ry",
              "vector_definitions": {"e": "orthonormal mass-weighted eigenvector",
                  "u": "e/sqrt(M), then normalized over all atoms and directions"},
              "animation": "36 phases; shared mode scale, maximum excursion 0.10 Angstrom",
              "grids": {}}
    for label, expected in EXPECTED.items():
        source = ROOT / (label + ".dyn")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == expected, (label, digest)
        force, mass, symbols, cell, positions, printed = load(source)
        repeated = np.repeat(mass, 3)
        massscale = np.sqrt(repeated[:, None]*repeated[None, :])
        raw, _ = np.linalg.eigh(force/massscale)
        reproduction = float(np.max(np.abs(frequency(raw)-printed)))
        assert reproduction < 1e-4
        translation = np.kron(np.sqrt(mass[:, None]/mass.sum()), np.eye(3))
        uniform = np.kron(np.ones((len(mass), 1))/np.sqrt(len(mass)), np.eye(3))
        projector = np.eye(len(repeated)) - uniform @ uniform.T
        corrected = projector @ force @ projector
        optical = null_space(translation.T)
        value, basis = np.linalg.eigh(optical.T @ (corrected/massscale) @ optical)
        eigenvectors = optical @ basis
        displacements = eigenvectors/np.sqrt(repeated[:, None])
        displacements /= np.linalg.norm(displacements, axis=0)
        is_a = np.array([True, False, True, True, False, False])
        ma, mb = mass[is_a].sum(), mass[~is_a].sum()
        relative_atom = np.where(is_a, np.sqrt(mass)*np.sqrt(mb/(ma*(ma+mb))),
                                -np.sqrt(mass)*np.sqrt(ma/(mb*(ma+mb))))
        relative = np.kron(relative_atom[:, None], np.eye(3))
        relative_weight = np.abs(relative.T @ eigenvectors)**2
        modes = []
        with (ROOT / (label + "-vectors.csv")).open("w") as handle:
            writer = csv.writer(handle)
            writer.writerow(["optical_mode", "frequency_cm1", "atom", "symbol",
                             "ex", "ey", "ez", "ux", "uy", "uz", "atom_e_weight"])
            for k, w in enumerate(frequency(value)):
                e = eigenvectors[:, k].reshape(-1, 3)
                u = displacements[:, k].reshape(-1, 3)
                weights = np.sum(e**2, axis=1)
                for atom, symbol in enumerate(symbols):
                    writer.writerow([k+1, w, atom+1, symbol, *e[atom], *u[atom], weights[atom]])
                mode = {"optical_mode": k+1, "full_mode_after_three_translations": k+4,
                        "frequency_cm1": float(w), "e": e.tolist(), "u": u.tolist(),
                        "atom_e_weights": weights.tolist(),
                        "layer_e_weights": {g: float(weights[ids].sum()) for g, ids in LAYERS.items()},
                        "relative_inplane_template_weight": float(relative_weight[:2, k].sum()),
                        "relative_outofplane_template_weight": float(relative_weight[2, k])}
                if k < 3:
                    mode["axsf_common_scale_A"] = save_axsf(
                        ROOT / f"{label}-optical-{k+1}.axsf", symbols, cell, positions, u)
                modes.append(mode)
        report["grids"][label] = {"source": source.name, "sha256": digest,
                                 "raw_reproduction_max_error_cm1": reproduction,
                                 "symbols": symbols, "positions_A": positions.tolist(),
                                 "cell_A": cell.tolist(), "modes": modes}
        print(label, "lowest optical cm-1:", " ".join(f"{m['frequency_cm1']:.8f}" for m in modes[:3]))
        print("  lowest E pair relative-inplane weight:",
              " ".join(f"{m['relative_inplane_template_weight']:.8f}" for m in modes[:2]))
        print(f"  raw matrix reproduction max error: {reproduction:.3e} cm-1")
    (ROOT / "gamma-mode-products.json").write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__": main()
```

</details>

## 用论文中的真实模式图理解应变软化

[Qiu 等的 Ba₂N 论文](https://doi.org/10.1103/PhysRevB.105.165101) Fig. 3(a–d)（原文 165101-3 页）按 Γ–M–K–Γ 路径和 cm⁻¹ 频率连接色散、原子 PHDOS、α²F 与振动模式。先在 (a) 找到 Γ 附近约 55 cm⁻¹ 的光学支，再用 (b) 的 Ba 投影确定参与原子，用 (d) 的俯视与侧视辨认上下 Ba 层的面内反向运动。图 (a) 的红点大小正比于线宽 $\gamma_{\mathbf q\nu}$，(d) 的箭头长度表示位移幅度，两种长度不编码同一物理量；图注也未给出不同面板之间的共同振幅或热振幅归一化。最后对照 (c) 中相应频段，才能把运动与耦合联系起来。论文第 2 页的声子/EPC 方法为 QE DFPT、6×6×1 直接 q 网格与 72×72×1 电子积分网格；这组设置属于 Ba₂N，不替代本页 Al 或界面的收敛检查。

同一论文 Fig. 6（原文第 5 页）给出 4% 双轴拉伸后的对照。Γ 光学模降到约 49 cm⁻¹；K 点出现约 24 cm⁻¹ 的软化声学模。作者用 √3×√3 超胞把原胞 K 点折叠到超胞 Γ，在 Fig. 6(e) 显示真实模式：Ba 同时有面内和面外分量，N 主要在面内移动。读这组图时，先按 q 和频率定位模式，再看箭头与原子投影，最后结合线宽和 α²F 讨论耦合。不能把图上的红色圆点当成原子振幅，Fig. 3(a) 与 Fig. 6(a) 的点大小表示声子线宽。

在本页已有数据上复现这套读法，Al 的 freq.gp 路径文件可以画色散，却不能产生层间光学箭头；界面 Γ32 的三份真实 AXSF 和对应向量表可以显示模式。用 XCrySDen 打开同一模式动画，分别观察面内俯视和含 z 方向的侧视，在相同相位记录结构视图，并在图注标明矩阵分支、频率和最大显示偏移 0.10 Å；简并双态保留两个成员。本页没有与这组 +1.5% Γ 矩阵匹配的完整 q 色散和线宽，不能将历史 ph64 曲线或论文红点接到它上面。

比较界面或应变结构时，沿用这种配对方式：结构、同一 q 的频率、原子位移、原子/层权重一起记录。应变改变倒格矢，跨结构比较 K、M 等点应使用各自晶胞的倒格矢分数坐标；频率排序交叉时，可结合向量重叠和简并子空间追踪模式。这样才知道软化发生在哪一种运动，而不是只看到整张图向下移动。

从这里继续到[有限位移声子](/Atlas/m/phonon-finite-disp/qe/)读取实际受力，或到[虚频与软模](/Atlas/m/imaginary-phonon/qe/)比较 Γ 平移残差与有限 q 结构畸变。若要讨论某一频段对超导的贡献，再接到[模式线宽](/Atlas/m/phonon-linewidth/qe/)和[谱函数](/Atlas/m/eliashberg-a2f/qe/)。

## 参考资料

[ph.x](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [q2r.x](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [matdyn.x](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [Ba₂N 原文与 Fig. 3、6](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.105.165101)
