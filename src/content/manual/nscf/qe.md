## 沿用自洽密度，改变本征态的采样

[Si SCF](/Atlas/m/scf/qe/) 在 8×8×8 网格上得到了电子密度和四条占据带。为计算 DOS 并搜索带边，本页保持这份密度不变，在 24×24×24 网格上求八条能带。结构、赝势和 60/640 Ry 截断能均与上游 SCF 一致；更密的采样改变本征态的计算位置，不会重新优化电子密度。

界面杂化、带边和费米能附近的态分布，要从实际采到的本征态分析。DOS 需要布里渊区积分，带边也可能落在稀疏网格没有采到的位置，因此沿用父密度后仍需增加本征态采样。[Giannozzi 等的 QE 方法论文](https://doi.org/10.1088/0953-8984/21/39/395502)附录 A.2 式 (A.8)写出广义本征值问题；固定密度后，本征值求解仍有自己的残差。本页的 CG 分支处理后者，网格是否足够由后续目标量比较决定。

NSCF 不再做一轮轮密度混合，但每个 k 点的本征值仍要数值收敛。这次就遇到了一个具体例子：原 Davidson 运行虽然打印 `JOB DONE.`，还出现了 `c_bands: 1 eigenvalues not converged`。原文件保留在旧目录，下面展示的是另建目录后用 CG 完成的计算。

本例文件可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，读取下述 OUT 与 XML 可直接核对本次能级和采样数；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。读取输出和 XML 可直接使用包内文件；重新计算时，先完成 [Si SCF](/Atlas/m/scf/qe/)，再按下面的顺序复制保存目录并运行 NSCF。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [DOS 后处理](https://www.quantum-espresso.org/Doc/INPUT_DOS.html)

## 从同一份 SCF 复制父数据

在 `si-pbe` 下新建 `gap24-cg`，把 SCF 的保存目录复制进去，再用 `vi` 编辑独立输入。普通操作顺序如下，已有目录不要重复覆盖：

```bash
mkdir gap24-cg
cp -a scf/tmp gap24-cg/
cp scf/scf.in gap24-cg/nscf.in
cd gap24-cg
vi nscf.in
```
本次实际输入是：

```text
[preston@preston-System-Product-Name gap24-cg]$ cat nscf.in
&CONTROL
  calculation = 'nscf'
  verbosity = 'high'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nbnd = 8
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  diagonalization = 'cg'
  diago_cg_maxiter = 200
  diago_thr_init = 1.0d-10
  conv_thr = 1.0d-10
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS automatic
24 24 24 0 0 0
```
`calculation='nscf'` 读取父密度；`nbnd=8` 在 4 条占据带之外再求 4 条空带，后续 DOS 能看到多高的导带，首先受这些实际求出的能级限制。只把作图的能量上限调高，不会生成更多空带。最后一行把采样改为 `24³`，仍保持零位移和非磁性 Si 的固定占据设置。

这次换用 CG 是为了处理原运行中的本征值警告。`diago_thr_init=1.0d-10` 明确给出本征值迭代的阈值，`diago_cg_maxiter=200` 是 CG 允许的最大迭代次数，并非每条带一定要算 200 次。把阈值收紧、把上限增加，都可能增加耗时；是否求完还要逐 k 点查输出。NSCF 中的 `conv_thr` 用于未显式指定时的对角化阈值设置，不代表这里又进行了一套电荷自洽循环。本次已明确设置 `diago_thr_init`，后面实际打印的 `ethr` 应与它对应。

如果复制的 `tmp/si.save` 实际来自别的结构，输入表面上相似也不能接用。需要更换结构、赝势或自洽物理设置时，先重建匹配的 SCF。

## 提交与运行时的输出

```text
[preston@preston-System-Product-Name gap24-cg]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-cg
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in nscf.in > nscf.out 2> nscf.err
```
在此目录用 `sbatch run.sh` 提交，`squeue -u preston` 查看自己的队列，`tail -f nscf.out` 跟随输出。`verbosity='high'` 让本例保留各 k 点能级。开头回显 413 个不可约 k 点；它们带权重表示整个 24³ 网格，并非只有 413 个任意采样点。

计算末段可以看到序号走到最后一个点，然后进入能级列表：

```text
     Computing kpt #:   411  of   413
     total cpu time spent up to now is      103.7 secs

     Computing kpt #:   412  of   413
     total cpu time spent up to now is      103.9 secs

     Computing kpt #:   413  of   413
     total cpu time spent up to now is      104.1 secs

     ethr =  1.00E-10,  avg # of iterations = 35.6

     total cpu time spent up to now is      104.1 secs

     End of band structure calculation

          k = 0.0000 0.0000 0.0000 (  2085 PWs)   bands (ev):

    -5.6925   6.3970   6.3970   6.3970   8.9666   8.9666   8.9666   9.9691

     occupation numbers 
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000
```
第一组 `k=(0,0,0)` 是 Γ 点。8 个能级按 eV 打印，下面是对应占据数；这里前四项为 1、后四项为 0，非自旋极化计算的自旋简并由程序的电子计数处理。不能把这行简单相加后说整胞只有 4 个电子。

输出里虽然写着 `End of band structure calculation`，输入仍然是均匀网格 NSCF。程序用语不能替代输入里的 `calculation` 和 K_POINTS 来区分均匀采样与高对称路径。

## 退出前，连本征值警告一起检查

下面两条 `grep` 分别查正常收尾和失败信息；第二条没有匹配行，是本次本征值检查的一部分。后面仍要单独查看错误文件：

```bash
grep -n -E 'End of band structure calculation|JOB DONE' nscf.out
grep -ni -E 'not converged|Error in routine|convergence NOT achieved' nscf.out
cat nscf.err
```
本次最终输出没有未收敛本征值行。对应的 [nscf.err](/Atlas/examples/si-pbe/gap24-cg/nscf.err) 为 1300 字节，保留重复的 X11 授权提示。输出末尾如下：

```text
     Parallel routines

     PWSCF        :   1m38.87s CPU   1m44.29s WALL


   This run was terminated on:  22: 2:20  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
`1m44.29s WALL` 是这轮实际耗时。还要核对保存的 XML 中 k 点数与能带数和输入一致，能级是有限数值，文件不是另一轮作业留下的旧件。[完整输入输出](/Atlas/examples/si-pbe/gap24-cg/nscf.out)与对应 XML 一起放在下载包中。

413 个点走完、没有残留本征值警告，并且 XML 的计数对应本次输入，支持接受这份有限网格的本征态记录。24³ 是否满足某个分析量，还要看那个量随网格的变化。[带隙页](/Atlas/m/band-gap/qe/)还会把 12³、18³、24³ 的采样结果，以及更密父 SCF 的结果放在一起比较。

在解压后的 `si-pbe` 目录中，读取[本次 XML](/Atlas/examples/si-pbe/gap24-cg/data-file-schema.xml)的实际字段：

```bash
python3 - <<'XML'
import xml.etree.ElementTree as ET
b = ET.parse('gap24-cg/data-file-schema.xml').getroot().find('output/band_structure')
print('nks=', int(b.find('nks').text), 'nbnd=', int(b.find('nbnd').text),
      'nelec=', float(b.find('nelec').text))
XML
```

```text
nks= 413 nbnd= 8 nelec= 8.0
```

实际输入与保存的 XML 对应如下：

| 项目 | 父 SCF | 本次 CG NSCF |
| --- | --- | --- |
| 均匀网格 | 8×8×8，零偏移 | 24×24×24，零偏移 |
| 能带数 | 4 条占据带 | 8 条，占据带外再求 4 条空带 |
| 电子数 | 8 | 8 |
| 密度 | 由电子自洽得到 | 读取父 SCF 密度 |
| 子计算 XML 的不可约 k 点数 | — | 413 |

网格数指完整布里渊区的均匀采样，XML 中的 413 是对称性约化后的 k 点数。本页上面的 Γ 点八个能级直接来自 OUT；带隙页进一步从所有实际 k 点与本征值读取价带顶、导带底，再比较网格变化。

## 从本征态读到界面电子结构

[带隙页](/Atlas/m/band-gap/qe/)从所有实际 k 点读取价带顶与导带底；[DOS](/Atlas/m/dos/qe/)则使用均匀点及权重积分。沿高对称路径画能带时，从同一 SCF 建立[路径分支](/Atlas/m/bands/qe/)。将三种输出互换，容易把路径上的极值误认为整个布里渊区的极值，或把路径点当成 DOS 的积分网格。

[Ba₂N 原文 Fig. 2(a–c)，第 165101-3 页](https://doi.org/10.1103/PhysRevB.105.165101)把路径能带、DOS 与费米面分开画：Fig. 2(a)的横轴是 Γ–M–K–Γ 路径，SOC 与无 SOC 两组带在同一费米能参照下比较；Fig. 2(b)按能量画总态数分布及投影；Fig. 2(c)再定位穿过费米能的二维口袋。路径上看见一条穿越线，还不足以得到整个布里渊区的 DOS。本页 24³ 均匀 NSCF 提供的是积分采样的本征态，[Si DOS 的现有图和源码](/Atlas/m/dos/qe/#从原始能量转到相对价带顶的图)展示后续 `dos.x` 数据；其零点是同一采样的价带顶，纵轴是 states/eV/cell，不能改标为 Ba₂N 的费米能参照。复画时沿用本页父密度，先得到自己的能量/DOS 两列，保持每原胞归一化与实际展宽，再由 gnuplot 或其他成熟绘图软件读列。本例四条空带只覆盖它们实际算到的范围，拉长能量轴不会增加本征态。

密度质量仍由父 SCF 决定。本例的父网格是 8³，NSCF 为 24³；加密子网格可以找到更多带边采样点，却不能消除父密度的误差。[实际带隙对照](/Atlas/m/band-gap/qe/)还比较了更密父 SCF 的结果。若结构、赝势、SOC 或自洽物理设置改变，应先建立对应的父计算，再讨论子网格的变化。
