[ph.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [PHonon 用户手册](https://www.quantum-espresso.org/Doc/ph_user_guide/) · [q2r.x](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [matdyn.x](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)

把原子轻轻推开，电子云会重新调整，原子受到的恢复力也随之改变。DFPT 直接求这一响应，不必为每一个位移再建一份超胞。计算结束时得到的是各个 q 点的动力学矩阵；我们还要把它们连成一张能读的声子图。

下面用新计算的 **fcc Al 单原子原胞**走完整条路线。QE 7.5、LDA-PZ、官方 `Al.pz-vbc.UPF` 赝势，晶格由 [晶胞优化](/Atlas/m/vc-relax/qe/) 得到，立方晶格常数为 3.95606780 Å。这是一个明确的小体系计算示例；它不能替代任意材料自己的电子参数与 q 网格收敛检查。

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
本例明确写出原胞的三条晶格矢量，所以采用 `ibrav=0`。程序会提示这不是它最推荐的对称性表达方式；我们保留了完整精度的 fcc 晶格，继续核对程序识别的结构及 q 点对称性，没有把提示从原始输出中删掉。电子网格是 16×16×16，波函数/电荷密度截断为 40/160 Ry，`degauss=0.02 Ry`。这些值定义了这一组教案数据，并不因为 SCF 收敛就自动成为 Al 的最终推荐值。

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

实际提交采用下面的 Slurm 脚本。这里先在本目录重做固定结构 SCF，然后运行 `ph.x`，并在它成功返回后调用后处理程序；脚本里的 `set -e` 会在某一步非零退出时停止。资源是 Maxwell 实際分配的 8 个 MPI 进程，每进程 1 个 OpenMP 线程。

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
读迭代时先看 `Calculation of q`，再看 `Representation`，最后看残差和 `Convergence has been achieved`。一个表示通过后，还会继续同一点的其余表示，再进入下一个 q 点。正在变化的 `thresh` 是内层求解量，不能拿它直接替代输入的 `tr2_ph` 作最终验收。

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
`q2r.x` 已将这些矩阵变为 `al.fc`。输入、输出及全部动力学矩阵可从 [Al 示例文件](/Atlas/examples/al/manifest.json) 对照核验；后处理读取同一套文件，没有混接另一个计算目录。

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
第一列是路径距离，后面 3 列分别对应三支声子频率，单位 cm⁻¹。[绘图脚本](/Atlas/examples/al/plot_phonon.py) 直接读取这 4 列，按节点位置加标签，不再手工抄频率。

```bash
python3 plot_phonon.py
```

<figure><img src="/Atlas/examples/al/figures/phonon-dfpt.png" alt="Al 的 DFPT 声子色散" loading="lazy"/><figcaption>4×4×4 DFPT q 网格经 q2r 和 matdyn 得到的 Γ—X—W—L—Γ 插值色散。</figcaption></figure>

图中没有明显的有限波矢负频支，这是这一次参数组合下的观察。要把它提升为数值收敛的动力学稳定性证据，需要再检查电子 k 网格、展宽、响应阈值和原始 q 网格，并用直接计算的点核对插值结果。不能靠提高画图取点数来代替这些计算。

下一步到 [声子态密度](/Atlas/m/phdos/qe/) 对整个布里渊区做积分；也可以到 [有限位移声子](/Atlas/m/phonon-finite-disp/qe/) 看同一材料如何从实际受力重建力常数。

```text
晶胞优化 → 固定结构 SCF → 完整 q 网格 ph.x
                              ↓
                    动力学矩阵逐点检查 → q2r
                                           ├→ matdyn 路径 → 声子图
                                           └→ matdyn 均匀网格 → 声子 DOS
```
