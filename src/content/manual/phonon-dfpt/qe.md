把原子轻轻推开，电子云会重新调整，原子受到的恢复力也随之改变。DFPT 直接求这一响应，不必为每一个位移再建一份超胞。计算结束时得到的是各个 q 点的动力学矩阵；我们还要把它们连成一张能读的声子图。

下面用 **fcc Al 单原子原胞**计算 SCF、q 网格动力学矩阵和路径频率。QE 7.5、LDA-PZ、官方 `Al.pz-vbc.UPF` 赝势，晶格由 [Al 的晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax) 得到，立方晶格常数为 3.95606780 Å。这是一个明确的小体系计算示例；它不能替代任意材料自己的电子参数与 q 网格收敛检查。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

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


后处理的输入字段和单位已经确定，可以用下面的说明让 AI 编程助手写出脚本：

```text
编写 plot_phonon.py，从 Al 根目录读取 dfpt/al.freq.gp，要求 161 行、4 列。首列是路径累计距离，后三列为 cm⁻¹ 频率，直接绘制全部三条分支并保留负号。以行 0、40、80、120、160 的距离标 Γ—X—W—L—Γ，画零线和分段界线，输出 figures/phonon-dfpt.png 与 PDF。使用同目录 atlas_plot_style.py，读取文件而不是从示意图拟合曲线。
```

下面是算例实际使用的完整源码。

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

图中没有明显的有限波矢负频支，这是这一次参数组合下的观察。要把它提升为数值收敛的动力学稳定性证据，需要再检查电子 k 网格、展宽、响应阈值和原始 q 网格，并用直接计算的点核对插值结果。不能靠提高画图取点数来代替这些计算。

## 二维异质结 SnSe₂/Sr₂N 与 ZrCl₂/Sc₂C：原子质量索引核验与高频轻元素光学支分离

在多元素二维异质结的 `ph.x` 与 `matdyn.x` 计算中，`amass(i)` 的顺序必须严格对应 `pw.x` 输入里 `ATOMIC_SPECIES` 的元素声明顺序。因为实空间力常数矩阵 `C_Iα,Jβ(R)` 本身不依赖原子质量，而动力学矩阵对角化求解本征频率时要除以质量平方根：

`D_Iα,Jβ(q) = C_Iα,Jβ(q) / sqrt(M_I M_J)`

质量索引写错会改变动力学矩阵。对单一元素主导的模式，近似有 `ω_wrong/ω_true ≈ sqrt(M_true/M_wrong)`；混合模式还取决于本征矢。在 **`SnSe₂/Sr₂N`**（[完整排查记录](/Atlas/m/epc/qe/#double-grid-research-record)）中，元素表顺序为 `Sr (87.620)、N (14.007)、Sn (118.71)、Se (78.971)`，而旧输入误将 `amass(2)=118.71` 写了两次，把轻原子 N 当成了重原子 Sn（质量放大 `8.475` 倍，单一 N 运动极限下估算频率降低约 `2.91` 倍）。下图中间面板将旧质量色散 [`srnsnse.wrong_mass.freq.gp`](/Atlas/examples/snse2-sr2n/ph64/srnsnse.wrong_mass.freq.gp)（灰虚线）与恢复真实质量后的色散 [`srnsnse.freq.gp`](/Atlas/examples/snse2-sr2n/ph64/srnsnse.freq.gp)（深蓝与锈红实线）叠加在同一坐标系中：错误质量下第 `16–18` 支被压低在 **`4.49–6.70 THz`**（Γ 点为 `4.60、5.56、6.70 THz`）；恢复 `M_N = 14.007` 后，主要由 Sn/Se/Sr 贡献的中低频支（`0–6.65 THz`）几乎不变，而由 N 主导的三条高频光学支（`ν = 16–18`）跃升至 **`7.99–11.94 THz`**（Γ 点为 `7.99、7.99、10.74 THz`，已绘路径跨度 `7.42–11.94 THz`），直接越过了旧 `lambdax.in` 的 `10 THz` 积分上限。

<figure><img src="/Atlas/figures/snse2-sr2n/snse2-sr2n-scf-ph-progress.png" alt="SnSe₂/Sr₂N 质量恢复前后的 DFPT 声子色散、原子分辨 PHDOS 与 q=1,2 逐模耦合" loading="lazy"/><figcaption>SnSe₂/Sr₂N 的 DFPT 声子与后处理诊断：（中）错误质量（M<sub>N</sub> = 118.71，灰色虚线，第 16–18 支位于 4.49–6.70 THz）与真实质量（M<sub>N</sub> = 14.007，实线）下的 Γ–M–K–Γ 声子色散及共享频率轴的原子投影 PHDOS，锈红色高亮恢复后的三条 N 原子主导的高频光学支（7.99–11.94 THz）。</figcaption></figure>

同样地，在 **`ZrCl₂/Sc₂C`**（[双网格计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，8×8×1 DFPT 网格经 `q2r.x → matdyn.x` 插值得到的色散 [`zrclscc.freq.gp`](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.freq.gp) 在已计算的高对称路径上无虚频：下方 15 条 `Zr/Sc/Cl` 声学与中低频光学支分布在 `0–10.11 THz`（`0–337.2 cm⁻¹`，直接 DFPT q 网格上为 `0–10.02 THz`），中间存在 `10.11–12.49 THz` 的声子带隙，上方 3 条由轻原子 `C` 主导的高频光学支（`ν = 16–18`）分布在 `12.49–17.11 THz`（原始 DFPT 网格上为 `12.38–17.11 THz`）。

## 文献中的 DFPT 声子色散与本征模式图例（附 DOI 溯源）

在展示 DFPT 声子色散时，除了绘制本征频率曲线外，文献常结合**振动方向与元素投影着色**、**软模频率随电子展宽的演化曲线**以及**实空间本征位移矢量与点群不可约表示标注**来分析晶格动力学与结构相变。下面结合四幅文献原图说明常见的数据组织方式：

### 1. 振动方向投影声子色散（面内与面外分量编码）

<figure class="research-figure"><img src="/Atlas/figures/literature/M5_DirectionalFatPhonon_NbSi2As4_PRB2025_Fig3b.jpg" alt="按原子振动方向（面内与面外）及元素权重着色的二维材料声子色散谱" loading="lazy"/><figcaption>在 NbSi<sub>2</sub>As<sub>4</sub> 声子色散曲线上用颜色或散点大小区分面内（in-plane）与面外（out-of-plane）振动本征矢分量。图片来源：<em>Phys. Rev. B</em> <strong>111</strong>, L140508 (2025)，<a href="https://doi.org/10.1103/PhysRevB.111.L140508" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.111.L140508</a>。</figcaption></figure>

- **数据提取与绘图方式**：先明确向量约定。QE 7.5 的 `fleig='matdyn.eig'` 保存正交的动力学矩阵本征矢 `e_Iα(q,ν)`，可用 `Σ_I |e_Iz|²` 表示面外权重。`flvec='matdyn.modes'` 则保存 `e_Iα/√M_I` 再逐模归一化的原子位移，适合计算位移方向权重。两种权重在不同质量原子之间通常不同，图例应注明采用哪一种；见[matdyn.x 官方字段说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)。

### 2. 软模本征频率随电子展宽 σ 的演化曲线

<figure class="research-figure"><img src="/Atlas/figures/literature/M5_CDW_SmearingEvolution_NbSi2As4_PRB2025_Fig3a.jpg" alt="NbSi2As4 指定 q1 处最低 LA 模频率随 Fermi–Dirac 电子展宽的变化" loading="lazy"/><figcaption>NbSi<sub>2</sub>As<sub>4</sub> 指定 q₁ 处最低 LA 模频率随 Fermi–Dirac 电子占据展宽 σ 的变化，横轴为 mRy、纵轴为 meV，水平零线区分虚频与正频。图片来源：<em>Phys. Rev. B</em> <strong>111</strong>, L140508 (2025)，Fig. 3a，<a href="https://doi.org/10.1103/PhysRevB.111.L140508" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.111.L140508</a>。</figcaption></figure>

- **数据提取与绘图方式**：固定结构、赝势、q 点与占据方案，逐项记录电子展宽和同一软模的频率，并配套检查 k 网格收敛。Fermi–Dirac σ 可参数化电子占据温度，但不是离子温度；跨零趋势需结合本征位移、电子响应或畸变能量来解释软模机制。上面的曲线来自 NbSi₂As₄ 文献，本页 Si 与 Al 算例未进行此扫描。

### 3. 强耦合声子模式的俯视/侧视本征矢与 Γ 点群论不可约表示标注

<figure class="research-figure"><img src="/Atlas/figures/literature/M5_PhononEigenvectors_TopSide_hAlH2_Jiang_Fig4.jpg" alt="关键高耦合声子模式在晶体结构俯视图与侧视图中的原子振动箭头可视化" loading="lazy"/><figcaption>结合俯视图（Top view）与侧视图（Side view）展示二维 h-AlH<sub>2</sub> 布里渊区中 6 个主要电声耦合声子模式（I–VI）的实空间原子位移方向。图片来源：Jiang et al., <em>Phys. Status Solidi RRL</em> <strong>18</strong>, 2300417 (2024)，<a href="https://doi.org/10.1002/pssr.202300417" target="_blank" rel="noopener noreferrer">DOI: 10.1002/pssr.202300417</a>。</figcaption></figure>

<figure class="research-figure"><img src="/Atlas/figures/literature/M5_PhononEigenvectors_Irreps_AlH2_Yang2023_Fig3a.jpg" alt="按点群不可约表示分类标注的声子振动模式与红外拉曼活性对照图" loading="lazy"/><figcaption>将单层 AlH<sub>2</sub> 在 Γ 点的 9 个声子模式按 D<sub>3h</sub> 点群不可约表示（E′、A<sub>2</sub>″、E″、A<sub>1</sub>′）及红外（I）/拉曼（R）活性逐一配对展示。图片来源：Yang, Jiang, and Zhao, <em>Chin. Phys. Lett.</em> <strong>40</strong>, 107401 (2023)，<a href="https://doi.org/10.1088/0256-307X/40/10/107401" target="_blank" rel="noopener noreferrer">DOI: 10.1088/0256-307X/40/10/107401</a>。</figcaption></figure>

- **数据提取与绘图方式**：`ph.x` 与 `dynmat.x` 在 Γ 点会输出点群对称性与不可约表示标签。将关键模式的俯视/侧视原子位移矢量图与点群符号、红外/拉曼活性并列标注，便于同实验光谱直接比对。

下一步到 [声子态密度](/Atlas/m/phdos/qe/) 对整个布里渊区做积分；也可以到 [有限位移声子](/Atlas/m/phonon-finite-disp/qe/) 看同一材料如何从实际受力重建力常数。

```text
晶胞优化 → 固定结构 SCF → 完整 q 网格 ph.x
                              ↓
                    动力学矩阵逐点检查 → q2r
                                           ├→ matdyn 路径 → 声子图
                                           └→ matdyn 均匀网格 → 声子 DOS
```

## 参考资料

[ph.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [PHonon 用户手册](https://www.quantum-espresso.org/Doc/ph_user_guide/) · [q2r.x](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [matdyn.x](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)
