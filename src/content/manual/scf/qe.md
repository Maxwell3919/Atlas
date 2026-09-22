参考：

- [pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)
- [QE 7.5 的 Si 官方例子](https://github.com/QEF/q-e/blob/qe-7.5/PW/examples/example01/run_example)
- [本例使用的 Si PBE 赝势](https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，从本页的 SCF 输入开始生成自己的保存目录。

## 把结构固定下来，先求一份电子密度

这里在 Preston 上用 QE 7.5 计算两个原子的金刚石 Si 原胞。晶格取自 QE 示例的 10.20 bohr，赝势使用公开库中的 PBE 超软赝势；这是固定结构的教学算例。后面的 NSCF、路径能带和 Γ 点声子都从这份明确的输入出发。

如果结构来自自己的优化，先到[离子弛豫](/Atlas/m/relax/qe/)或[晶胞弛豫](/Atlas/m/vc-relax/qe/)核对最后结构，再把它带进 SCF。截断能与电子网格如何比较，见[收敛测试](/Atlas/m/convergence/qe/)。这一页集中看一份 SCF 怎么提交、输出分几段，以及下一步真正需要保留哪些文件。

## 读完这份小输入，再提交

在 `si-pbe` 下，`pseudo` 放赝势，`scf` 放本次输入与输出。输入使用相对路径 `../pseudo`，所以提交时要先进入 `scf`。本次文件内容如下：

```text
[preston@preston-System-Product-Name scf]$ cat scf.in
&CONTROL
  calculation = 'scf'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  conv_thr = 1.0d-10
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS automatic
8 8 8 0 0 0
```
`ibrav=2` 定义 fcc 原胞，`A` 是常规立方晶格参数，单位 Å。`ATOMIC_POSITIONS alat` 中的坐标按这个晶格参数缩放，不是分数坐标卡片 `crystal`。两种坐标表示不能只换卡片名而不换数值。

`calculation='scf'` 固定晶胞和原子位置。`tprnfor`、`tstress` 让它仍然打印力和应力，供我们判断这个固定结构处在什么状态。8 个价电子在这份非磁性计算中占据 4 条带，所以 `occupations='fixed'` 可用于这个半导体例子；金属的占据处理另见[Al 声子前的 SCF](/Atlas/m/phonon-dfpt/qe/)。

`ecutwfc=60 Ry` 限制波函数的平面波基组，`ecutrho=640 Ry` 控制电荷密度与势使用的截断；超软赝势的增广电荷也需要足够细的表示。两个数的作用不同，比例不能直接搬给另一种赝势。本例的[独立对照](/Atlas/m/convergence/qe/)中，60→80 Ry 的总能变化约 0.138 meV/atom；但 `8³` 与 `14³` 网格仍相差约 1.95 meV/atom。因此这里保留的是清楚记录的教学起点，电子循环收敛后，还要按所求性质比较网格。最后三个零表示不施加半格位移；之后再增加 NSCF 的 k 点，也不会反过来更新这份 SCF 密度。

下面是实际运行的四进程脚本。`ulimit`、线程数和工作目录一起保留；QE 路径按本机安装位置填写。Preston 的这套程序使用 GCC/OpenMPI，环境与其他机器的 Intel MPI 不通用。

```text
[preston@preston-System-Product-Name scf]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to core -np 4 <qe_bin>/pw.x -in scf.in > scf.out 2> scf.err
```
用 `vi scf.in` 检查并保存输入后，提交与查看的命令是：

```bash
sbatch run.sh
squeue -j 765
tail -f scf.out
```
这次作业号是 765，实际 WALL 时间为 13.73 s；重新提交会得到新的号码。`tail -f` 只跟随输出，Ctrl-C 结束的是查看进程。输出一段时间没有新增时，先同时看队列和错误文件，不要立即往同一目录再次提交。

## OUT 的前半段是在告诉你：程序实际读到了什么

`scf.out` 开头记录程序版本、进程数和输入文件。继续往下，会出现结构、电子数、截断能与交换关联设置：

```text
     bravais-lattice index     =            2
     lattice parameter (alat)  =      10.2000  a.u.
     unit-cell volume          =     265.3020 (a.u.)^3
     number of atoms/cell      =            2
     number of atomic types    =            1
     number of electrons       =         8.00
     number of Kohn-Sham states=            4
     kinetic-energy cutoff     =      60.0000  Ry
     charge density cutoff     =     640.0000  Ry
     scf convergence threshold =      1.0E-10
     mixing beta               =       0.7000
     number of iterations used =            8  plain     mixing
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
```
这里的 `alat=10.2000 a.u.` 与输入中的 Å 单位不同；它们描述的是同一个长度。`number of electrons=8.00` 来自两个 Si、每个 4 个价电子。`number of Kohn-Sham states=4` 也解释了为什么这份 SCF 输出没有可供我们研究导带的空带：空带会在后面的 NSCF 或路径计算中明确增加。

下一段是晶格轴、赝势来源、对称性和原子位置。赝势段可以直接核对文件名、类型与价电子数：

```text
     PseudoPot. # 1 for Si read from file:
     ../pseudo/Si.pbe-n-rrkjus_psl.1.0.0.UPF
     MD5 check sum: fa25574f73a70a4139f2adfbefec430c
     Pseudo is Ultrasoft + core correction, Zval =  4.0
```
再往下是 k 点列表。输入写了 8×8×8，输出却只有 29 个点，这里先不要改输入：程序利用当前晶体的对称性只保留不可约点，同时写出权重。29 不代表输入变成了 29×29×29。

```text
     number of k points=    29
                       cart. coord. in units 2pi/alat
        k(    1) = (   0.0000000   0.0000000   0.0000000), wk =   0.0039062
        k(    2) = (  -0.1250000   0.1250000  -0.1250000), wk =   0.0312500
        k(    3) = (  -0.2500000   0.2500000  -0.2500000), wk =   0.0312500
        k(    4) = (  -0.3750000   0.3750000  -0.3750000), wk =   0.0312500
        k(    5) = (   0.5000000  -0.5000000   0.5000000), wk =   0.0156250
```
头部的这些内容应该在计算刚开始时就检查。若元素、原子数、k 点或赝势与预期不同，即使后面得到一个收敛能量，也是在解另一份输入。

## 迭代段要连着看能量和估计误差

第一次电子迭代从初始密度出发。下面保留两轮连续的输出，可以看清每个循环的排列：

```text
     iteration #  1     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  1.00E-02,  avg # of iterations =  2.0

     Threshold (ethr) on eigenvalues was too large:
     Diagonalizing with lowered threshold

     Davidson diagonalization with overlap
     ethr =  6.40E-04,  avg # of iterations =  1.5

     total cpu time spent up to now is        1.2 secs

     total energy              =     -22.83581101 Ry
     estimated scf accuracy    <       0.05540955 Ry

     iteration #  2     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  6.93E-04,  avg # of iterations =  1.0

     total cpu time spent up to now is        1.5 secs

     total energy              =     -22.83770169 Ry
     estimated scf accuracy    <       0.00288592 Ry
```
`total energy` 是当前轮的总能；`estimated scf accuracy` 是程序对电子自洽误差的估计，单位 Ry；`ethr` 属于本征值求解器的内部阈值。三者不是同一个量。能量两轮之间看起来变化很小，仍要继续核对 SCF 的停止条件。

这次第 9 轮结束后，输出先列能带本征值，再打印最高占据态、带感叹号的总能和自洽收敛信息：

```text
     highest occupied level (ev):     6.3971

!    total energy              =     -22.83859230 Ry
     estimated scf accuracy    <          4.3E-11 Ry

     The total energy is the sum of the following terms:
     one-electron contribution =       5.30781076 Ry
     hartree contribution      =       1.08523150 Ry
     xc contribution           =     -12.33187599 Ry
     ewald contribution        =     -16.89975857 Ry

     convergence has been achieved in   9 iterations
```
`4.3E-11 Ry` 小于输入的 `conv_thr=1.0d-10`，并有明确的 9 轮收敛行。这个阈值对应整胞的估计自洽能量误差，不能解释为每个原子的误差，更不包含基组、k 网格和泛函的误差。这里的最高占据态是 6.3971 eV；它不是我们已经求出的带隙，也不是金属计算中的费米能行。后续作图要说明选择的能量零点，不能随手拿另一目录的数来平移。

## 力为零、压力不为零，两件事可以同时发生

```text
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000000   -0.00000000   -0.00000000
     atom    2 type  1   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000


     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=       38.45
   0.00026138   0.00000000   0.00000000           38.45        0.00        0.00
   0.00000000   0.00026138  -0.00000000            0.00       38.45       -0.00
   0.00000000  -0.00000000   0.00026138            0.00       -0.00       38.45
```
两个 Si 的力在打印精度内为零，而压力是 **38.45 kbar**。高对称结构可以使原子力为零；这并不保证晶胞体积已经优化。因此这份结果可用于演示“固定结构电子自洽”，不能据此宣布得到零压平衡晶格。若问题要求平衡晶胞，应回到 `vc-relax`，而不是不断收紧同一固定晶胞的电子阈值。

程序随后写出保存数据，末尾给出分项计时和退出标记：

```text
     Writing all to output data dir ./tmp/si.save/ :
     XML data file, charge density, pseudopotentials, collected wavefunctions
```

```text
     Parallel routines

     PWSCF        :      9.22s CPU     13.73s WALL


   This run was terminated on:  21:32:37  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
把这两处和前面的 SCF 收敛行一起读，才知道电子计算结束、保存步骤也已经执行。完整的 [scf.out](/Atlas/examples/si-pbe/scf/scf.out.txt) 和 [scf.err](/Atlas/examples/si-pbe/scf/scf.err.txt)可以下载；运行日志不能只保留 `JOB DONE.` 一行。这里的 `scf.err` 有 780 字节，包含重复的 `Authorization required, but no authorization protocol specified` 环境提示；应连同输出保存，不能称为空文件，也不能只凭这条提示判定电子迭代失败。

## 下一步要带走保存目录，不只是一份 OUT

`scf.out` 便于人阅读，`tmp/si.save` 才保存后续程序读取的电子态。这个目录里的 `data-file-schema.xml` 记录结构和计算信息，`charge-density.dat` 保存电子密度，`wfc*.dat` 保存波函数；文件分布还会随 QE 版本和并行方式变化。

准备新的分支时，先新建目录并复制这份父数据，避免后续 NSCF 改写 SCF 原件。例如使用：

```bash
mkdir ../nscf
cp -r tmp ../nscf/
cp scf.in ../nscf/nscf.in
cd ../nscf
vi nscf.in
```
这里的 `nscf.in` 还需要按[NSCF 页](/Atlas/m/nscf/qe/)修改计算类型、网格与空带；复制只建立文件关系，没有自动完成那些设置。`prefix` 和 `outdir` 必须指向刚复制的 Si 数据。如果改变了结构、元素、赝势或上游物理设置，应重新建立对应 SCF。

下一步按所需结果选择：[均匀网格 NSCF](/Atlas/m/nscf/qe/)通向 DOS 与布里渊区采样；[路径能带](/Atlas/m/bands/qe/)沿指定高对称线求本征值；[Γ 点声子及虚频对照](/Atlas/m/imaginary-phonon/qe/)读取本例的密度与波函数求响应。

```text
明确结构与赝势 → SCF 输入 → 电子迭代、力和应力 → si.save
                                                   ├─ 均匀 NSCF → DOS
                                                   ├─ 路径 bands → 能带 / 投影
                                                   └─ ph.x → 动力学矩阵
```
