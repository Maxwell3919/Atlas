[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [DOS 后处理](https://www.quantum-espresso.org/Doc/INPUT_DOS.html)

## 密度保持不变，把本征值算到更密的网格上

上一份 [Si SCF](/Atlas/m/scf/qe/)在 8×8×8 网格上得到电子密度，保留 4 条占据带。现在需要 DOS 和布里渊区内的带边位置，就在这份密度上使用 24×24×24 网格，并求出 8 条能带。结构、赝势与 60/640 Ry 截断保持一致。

NSCF 不再做一轮轮密度混合，但每个 k 点的本征值仍要数值收敛。这次就遇到了一个具体例子：原 Davidson 运行虽然打印 `JOB DONE.`，还出现了 `c_bands: 1 eigenvalues not converged`。原文件保留在旧目录，下面展示的是另建目录后用 CG 完成的计算。

本例文件可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。

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
`calculation='nscf'` 读取父密度；`nbnd=8` 增加空带；最后一行才定义新的均匀采样。这里仍是非磁性 Si 的固定占据设置。CG、本征值初始阈值和最大迭代次数是这次复算明确记录的求解配置，不是要求所有材料统一改成这一组合。

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

下面两条分别查正常收尾和失败信息，空的第二段才是这份结果实际通过的检查之一：

```bash
grep -n -E 'End of band structure calculation|JOB DONE' nscf.out
grep -ni -E 'not converged|Error in routine|convergence NOT achieved' nscf.out
cat nscf.err
```
本次最终输出没有未收敛本征值行。对应的 [nscf.err](/Atlas/examples/si-pbe/gap24-cg/nscf.err) 为 1300 字节，保留了重复的 `Authorization required, but no authorization protocol specified` 环境提示；它并非空文件。电子态是否求解完成，还要看本征值、保存数据和程序末尾。本次末尾为：

```text
     Parallel routines

     PWSCF        :   1m38.87s CPU   1m44.29s WALL


   This run was terminated on:  22: 2:20  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
`1m44.29s WALL` 是这轮实际耗时。还要核对保存的 XML 中 k 点数与能带数和输入一致，能级是有限数值，文件不是另一轮作业留下的旧件。[完整输入输出](/Atlas/examples/si-pbe/gap24-cg/nscf.out)与对应 XML 一起放在下载包中。

这份检查确认了本征值求解完成，没有证明 24³ 对所有性质都足够密。[带隙页](/Atlas/m/band-gap/qe/)还会把 12³、18³、24³ 的采样结果，以及更密父 SCF 的结果放在一起比较。

## 下一步

保留这份 NSCF 数据，进入 [DOS](/Atlas/m/dos/qe/)；需要布居时，另一个均匀网格算例见 [Löwdin 分析](/Atlas/m/population-analysis/qe/)。如果要沿 Γ–X–W 等线画能带，转到 [路径能带](/Atlas/m/bands/qe/)，从相同 SCF 建立对应分支。

```text
SCF 密度 → 独立保存目录 → 均匀网格 NSCF + 空带
                                   ↓
                         k点 / 本征值 / 完成标记核对
                                   ↓
                      DOS、带边采样或布里渊区投影积分
```
