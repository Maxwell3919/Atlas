# EPC 研究记录：材料分支与历史输出

SnSe₂/Sr₂N和ZrCl₂/Sc₂C各有独立结构、赝势、质量、k/q网格与运行记录。这些记录用于理解输入错误、保存数据和谱窗怎样影响解释；当前计算安排继续由材料自己的唯一README维护。下方提交和队列片段是历史证据，不意味着作业仍在运行或允许恢复。

SnSe₂/Sr₂N旧config3的BFGS没有收敛，历史N质量被Sn质量覆盖，旧0.713–2.944 K不作为有效预测。修正质量后的链完成两步固定结构SCF，Γ响应在表示9途中中止，dyn1空、无完整q点EPC，ph96没有完整输出。旧q1/q2快照不代表这轮完成，也不能作为restart依据。

ZrCl₂/Sc₂C历史ph64/ph96分别采用64²/96²致密电子网格、16²响应网格和同一q8²。+1.5%原始10 THz输出链保存完整，谱窗漏掉高频模式；18 THz保存表未绑定生成输入/命令/可执行文件。ph64.1/ph96.1加密链没有完整Tc输出对，已停止。材料后来核验的Γ对照仍属于声子阶段，不据此宣称完整各向异性EPW或材料Tc验收。

方法与分析读[EPC正文](/Atlas/m/epc/qe/)、[高频谱窗](/Atlas/m/eliashberg-a2f/qe/#spectral-window)、[逐模线宽](/Atlas/m/phonon-linewidth/qe/#heterostructure-modes)及[Tc表诊断](/Atlas/m/allen-dynes/qe/#material-tc-record)。[Ba₂N原文](https://doi.org/10.1103/PhysRevB.105.165101)图3/6的模式–PHDOS–谱峰对应，是这里采用的分析顺序；文献结论与本存档接受范围分开。

<span id="double-grid-research-record"></span>

## 另一份材料的实际启动记录

下面保留 bcgong 的 SnSe₂/Sr₂N 终端会话。它包含 BFGS 尚未通过的结构、质量索引修正、两步 SCF 与声子任务启动；这份记录没有提供完整十个不可约 q 的验收结果，也没有该材料可采用的 Tc。Al 的数值不能移到这条研究计算上。

<details>
<summary>展开 SnSe₂/Sr₂N 的目录整理、两步 SCF 与 ph.x 启动记录</summary>

## 从 SnSe₂/Sr₂N 的计算目录接着做

这次在 bcgong 的 tmux 窗口里准备 EPC 输入。`qe` 下已经建好了两个空目录：`ph64` 和 `ph96`。它们用来比较两套致密电子网格。先看文件从哪里来，再开始复制。

以下保留终端里的真实账号和命令；工作目录、程序路径和赝势库路径作了简写。

```text
[bcgong@localhost qe]$ pwd
<工作目录>/qe
[bcgong@localhost qe]$ grep -n 'bfgs failed' config3/relax/rx.out
49794:     bfgs failed after  43 scf cycles and  40 bfgs steps, convergence not achieved
[bcgong@localhost qe]$
```


这条输出要先读完：程序在 43 次 SCF、40 步 BFGS 后结束，**BFGS 没有收敛，不能判定为结构优化通过**。下面沿用它的末步结构准备输入，并继续做两步固定结构 SCF；这能检查电子迭代与数据衔接，不能替代结构验收。下面也继续观察这份固定结构的声子任务如何启动；最终使用声子与 EPC 结果时，结构问题仍需解决。如何看力、应力与优化结束信息，见[结构优化](/Atlas/m/vc-relax/qe/)。

还有一处会直接影响声子频率的输入错误：

```text
[bcgong@localhost qe]$ grep amass config3/ph64/phx.in
  amass(1)=87.620
  amass(2)=14.007
  amass(2)=118.71
  amass(4)=78.971
[bcgong@localhost qe]$
```


`amass(2)` 写了两次。对照本材料 `ATOMIC_SPECIES` 的顺序 Sr、N、Sn、Se，118.71 应该属于第三种元素 Sn。新目录中修正这一行，同时检查 `matdynxline.in`；旧结果原样保留，不能把改过质量的输入和旧声子输出拼成一套结果。

## 先复制输入，再用 vi 改

参考 hzw 上 Sc₂C 的步骤：致密网格 SCF → 粗网格 SCF → 声子与 EPC → 后处理。那个算例使用 QE 7.2 和 USPP；这里使用 bcgong 上的 QE 7.1，保留 SnSe₂/Sr₂N 原有的 PAW 赝势、泛函和截断能。借用的是计算步骤，材料参数仍来自本材料。

先只复制输入。新目录里不放旧的 `out/`、动力学矩阵或电声输出。

```text
[bcgong@localhost qe]$ cp config3/ph64/pwx.in config3/ph64/pwxall.in config3/ph64/phx.in config3/ph64/q2rx.in config3/ph64/matdynxline.in ph64/
[bcgong@localhost qe]$ cd ph64
[bcgong@localhost ph64]$
```


用 `vi` 打开输入，按 `i` 编辑，完成后按 `Esc`，输入 `:wq` 保存退出。两份 SCF 输入均打开 `tprnfor` 和 `tstress`，使后续输出包含力和应力；`pwxall.in` 保留 `la2F=.true.` 和 64×64×1 网格。

```text
[bcgong@localhost ph64]$ vi pwxall.in
```


保存后用 `cat` 读回整个文件：

```text
[bcgong@localhost ph64]$ cat pwxall.in
&CONTROL
  calculation = 'scf'
  outdir = './out/'
  prefix = 'srnsnse'
  pseudo_dir = '<赝势库路径>'
  tprnfor = .true.
  tstress = .true.
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0,
  nat = 6,
  ntyp = 4,
  ecutwfc = 120,
  ecutrho = 960,
  input_dft = 'vdw-DF3-opt1'
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
  la2F=.true.
/
&ELECTRONS
  conv_thr = 1.0000000000d-12
  mixing_beta = 4.0000000000d-01
/
&ions
/
&cell
/
ATOMIC_SPECIES
Sr  87.620  Sr.pbe-spn-kjpaw_psl.1.0.0.UPF
N   14.007  N.pbe-n-kjpaw_psl.1.0.0.UPF
Sn  118.71  Sn.pbe-dn-kjpaw_psl.1.0.0.UPF
Se  78.971  Se.pbe-dn-kjpaw_psl.1.0.0.UPF
CELL_PARAMETERS (angstrom)
   3.915211298  -0.000000000   0.000000000
  -1.957605649   3.390672445   0.000000000
   0.000000000   0.000000000  40.000000000
ATOMIC_POSITIONS (crystal)
Sr            0.3333333333        0.6666666667        0.4858621609
Sr            0.6666666667        0.3333333333        0.4189402327
Sn            0.3333333333        0.6666666667        0.5848669832
Se            0.0000000000        0.0000000000        0.6229981775
Se            0.6666666667        0.3333333333        0.5395777160
N             0.0000000000        0.0000000000        0.4476047279
K_POINTS automatic
  64 64 1 0 0 0
[bcgong@localhost ph64]$
```


文件从上到下依次是控制项、体系设置、电子迭代、元素与赝势、晶胞、原子坐标和 k 网格。`nat=6` 对应六行坐标，`ntyp=4` 对应四种元素；`prefix='srnsnse'` 与 `outdir='./out/'` 后面还要在声子输入中对上。

这里的 120/960 Ry、0.0037 Ry 展宽和电子阈值沿用现有输入，尚不是针对超导温度完成的收敛结论。两套 SCF 的一般操作见[固定结构 SCF](/Atlas/m/scf/qe/)；本页继续看它们与 EPC 相接的地方。

对照输入读 OUT 时，先把容易混在一起的几个量分开：

| 输入项 | 在这一轮中的作用 | 读输出时核对什么 |
| --- | --- | --- |
| `ecutwfc=120`、`ecutrho=960` | 分别限制波函数与电荷密度/势的平面波展开，单位 Ry | 两次 SCF 的截断与 FFT 网格回显是否匹配；这个比值来自当前协议，不能机械套给所有赝势 |
| `degauss=0.0037` | 配合 Gaussian 占据处理金属费米面附近的占据 | 电子网格变化时保留相同设置；这不是稍后给谱峰画宽的参数 |
| `conv_thr=1.0d-12` | 电子自洽残差的能量估计阈值，单位 Ry | 最后一次 `estimated scf accuracy` 与收敛信息；不是只算相邻两个总能量之差 |
| `la2F=.true.` | 在致密网格步骤保存后续 EPC 所需的本征值数据 | `a2Fsave` 的带数、k 点、网格及文件身份；文件名含 a2F 仍不代表已经得到谱函数 |

因此，先用致密网格取得费米面积分所需的电子采样，再用响应计算所依赖的粗网格保存 SCF 父链。两步共享结构与物理协议，承担的数值任务不同。后面的 `nq1/nq2/nq3` 则采样声子扰动波矢 q；把电子 k 网格加密，不会同时增加实际求解的声子 q 点。

## 声子输入里，质量与 q 网格一起核对

打开 `phx.in`，把 Sn 的质量索引改为 3，并去掉旧文件只计算第一点的 `start_q/last_q` 限制。这次先保留完整 8×8×1 q 网格输入；如果后续需要分批，范围应来自本材料实际列出的不可约 q 点。

```text
[bcgong@localhost ph64]$ vi phx.in
```

```text
[bcgong@localhost ph64]$ cat phx.in
  &inputph
  tr2_ph=1.0d-16
  nmix_ph=12
  verbosity='high'
  prefix='srnsnse'
  fildvscf='srnsnsedv'
  amass(1)=87.620
  amass(2)=14.007
  amass(3)=118.71
  amass(4)=78.971
  outdir='./out/'
  fildyn='srnsnse.dyn'
  electron_phonon='interpolated'
  el_ph_sigma=0.002
  el_ph_nsigma=20
  trans=.true.
  ldisp=.true.
  nq1=8
  nq2=8
  nq3=1
/
[bcgong@localhost ph64]$
```


此处四个 `amass` 与元素表逐一对应。`el_ph_sigma=0.002`、`el_ph_nsigma=20` 也只是当前准备使用的设置，后面要结合实际逐 q 输出检查展宽依赖。Sc₂C 的不可约 q 点数量和分段不能直接照搬过来。

该记录使用QE7.1；精确参数含义可查[QE7.1 INPUT_PH定义](https://github.com/QEF/q-e/blob/qe-7.1/PHonon/Doc/INPUT_PH.def)，不以新版默认值替代原输入。这套 PAW、泛函与 EPC 的兼容性仍需在本地版本上验证，文件准备完成不等于这些检查已经通过。

## 脚本里的进程数要和申请资源一致

致密网格 SCF 的脚本已在 `vi` 中写入，读回如下：

```text
[bcgong@localhost ph64]$ cat pwxall.slurm
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR" || exit 1

mpirun -np 32 <qe_bin>/pw.x -in pwxall.in > pwxall.out 2> pwxall.err
[bcgong@localhost ph64]$
```


这里申请 32 个任务，`mpirun` 也使用 32 个进程。程序输出写到 `pwxall.out`，标准错误单独写到 `pwxall.err`；Slurm 自身仍保留 `_out.%j.log` 和 `_err.%j.log`。粗网格脚本 `pwx.slurm` 对应 `pwx.in → pwx.out`。

声子脚本使用 16 个 MPI 进程，并设 `OMP_NUM_THREADS=1`：

```text
[bcgong@localhost ph64]$ cat phx.slurm
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR" || exit 1

mpirun -np 16 <qe_bin>/ph.x -in phx.in > phx.out 2> phx.err
[bcgong@localhost ph64]$
```


两个 SCF 与声子步骤需要依次完成并检查。下面实际提交的是 64×64×1 的 `pwxall`；它结束并核对通过后，才接 16×16×1 的 `pwx`。声子任务另行处理。

## 把 ph96 只改成另一套致密网格

输入和脚本在 ph64 核对后，复制到 ph96：

```text
[bcgong@localhost ph64]$ cp *.in *.slurm ../ph96/
[bcgong@localhost ph64]$ cd ../ph96
[bcgong@localhost ph96]$
```

```text
[bcgong@localhost ph96]$ vi pwxall.in
```


在 `vi` 中把最后一行的 `64 64 1 0 0 0` 改成 `96 96 1 0 0 0`。保存后看差异：

```text
[bcgong@localhost ph96]$ diff ../ph64/pwxall.in pwxall.in
47c47
<   64 64 1 0 0 0
---
>   96 96 1 0 0 0
[bcgong@localhost ph96]$ grep -A1 K_POINTS pwx.in pwxall.in
pwx.in:K_POINTS automatic
pwx.in-  16 16 1 0 0 0
--
pwxall.in:K_POINTS automatic
pwxall.in-  96 96 1 0 0 0
[bcgong@localhost ph96]$
```


`diff` 只显示致密网格这一行变化；`pwx.in` 仍为 16×16×1。两目录的声子输入都是 8×8×1 q 网格。这样后续比较时，才知道这两套输入改变的是哪一个量。

再把声子和插值输入中的质量一起读出来：

```text
[bcgong@localhost ph96]$ grep amass phx.in matdynxline.in
phx.in:  amass(1)=87.620
phx.in:  amass(2)=14.007
phx.in:  amass(3)=118.71
phx.in:  amass(4)=78.971
matdynxline.in:  amass(1)=87.620
matdynxline.in:  amass(2)=14.007
matdynxline.in:  amass(3)=118.71
matdynxline.in:  amass(4)=78.971
[bcgong@localhost ph96]$
```


四个索引和四个数值现在一致。ph96 的设置更密，但是否足够，需要比较后续 λ、谱函数及目标物理量；目录名本身不能说明收敛。

## 后处理先把文件关系接好

回到 ph64，`q2rx.in` 把逐 q 动力学矩阵接到力常数文件，`matdynxline.in` 再读取同名力常数：

```text
[bcgong@localhost ph96]$ cd ../ph64
[bcgong@localhost ph64]$ cat q2rx.in
&input
zasr='crystal'
fildyn='srnsnse.dyn'
flfrc='srnsnse.fc'
la2F=.true.
/
[bcgong@localhost ph64]$ cat matdynxline.in
&input
  asr='crystal'
  amass(1)=87.620
  amass(2)=14.007
  amass(3)=118.71
  amass(4)=78.971
  flfrc='srnsnse.fc'
  flfrq='srnsnse.freq'
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
[bcgong@localhost ph64]$
```


`fildyn='srnsnse.dyn'` 与声子输入相同，`flfrc='srnsnse.fc'` 在两份后处理输入中相同。末尾列的是 Γ–M–K–Γ 路径；它用于画声子色散，完整 q 网格的稳定性仍要另外核对。已有输出的读取方法见[DFPT 声子](/Atlas/m/phonon-dfpt/qe/)。

`lambda.x` 的脚本也准备好了。它从标准输入读取 `lambdax.in`：

```text
[bcgong@localhost ph64]$ cat lambdax.slurm
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR" || exit 1

mpirun -np 1 <qe_bin>/lambda.x < lambdax.in > lambdax.out 2> lambdax.err
[bcgong@localhost ph64]$
```


**这份启动记录截取时尚未生成 `lambdax.in`。** 它要用本次计算实际得到的不可约 q 点、权重与逐 q 电声文件；频率积分上限也要覆盖实际声子范围。先复制另一材料的 q 列表和频率上限，会让后面的积分失去依据。

最后看一次目录：

```text
[bcgong@localhost ph64]$ ls -1
lambdax.slurm
matdynxline.in
matdynxline.slurm
phx.in
phx.slurm
pwxall.in
pwxall.slurm
pwx.in
pwx.slurm
q2rx.in
q2rx.slurm
README.md
[bcgong@localhost ph64]$
```


每套目录都有五份输入、六份 Slurm 脚本和一份说明。脚本分别做过 `bash -n` 检查，远端文件也已回读；这些检查只验证文件和 shell 语法。输入准备到这里完成，接着在同一个 ph64 目录提交致密网格 SCF。

<!-- ph64-scf-session-start -->
## 提交 pwxall，先确认程序确实读对了文件

在 ph64 中检查网格和脚本，然后提交：

```text
[bcgong@localhost ph64]$ grep -A1 K_POINTS pwxall.in
K_POINTS automatic
  64 64 1 0 0 0
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ bash -n pwxall.slurm
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ sbatch -J srnsnse-k64 pwxall.slurm
Submitted batch job 18178
[bcgong@localhost ph64]$
```


`18178` 是调度器返回的作业号。先记住它，接下来的队列和日志检查都指向这一份作业，避免读到其他目录的同名 `pwxall.out`。

```text
[bcgong@localhost ph64]$ squeue -j 18178 -o "%.10i %.16j %.8T %.10M %.6D %R"
     JOBID             NAME    STATE       TIME  NODES NODELIST(REASON)
     18178      srnsnse-k64  RUNNING       0:33      1 localhost
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ scontrol show job 18178 | grep -E 'JobId=|JobState=|RunTime=|NumNodes=|WorkDir='
JobId=18178 JobName=srnsnse-k64
   JobState=RUNNING Reason=None Dependency=(null)
   RunTime=00:00:35 TimeLimit=365-00:00:00 TimeMin=N/A
   NumNodes=1 NumCPUs=32 NumTasks=32 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
   WorkDir=<工作目录>/qe/ph64
[bcgong@localhost ph64]$
```


`RUNNING` 表示调度器已经启动作业。这里申请并分配了 32 个任务，工作目录也确实是 ph64。此时还不能判断 SCF 是否收敛，继续打开程序输出的开头：

```text
[bcgong@localhost ph64]$ head -n 43 pwxall.out

     Program PWSCF v.7.1 starts on 22Sep2026 at 18:53:36

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on    32 processors

     MPI processes distributed on     1 nodes
     76371 MiB available memory on the printing compute node when the environment starts

     Reading input from pwxall.in
Warning: card &CELL ignored
Warning: card / ignored

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4
     file Sr.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  4P renormalized
     file N.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S renormalized
     file Sn.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized
     file Se.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  4S 4P 3D renormalized

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= VDW-DF3-OPT1
                           (   1   4  45   0   3   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want

     Message from routine setup:
     using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead

     R & G space division:  proc/nbgrp/npool/nimage =      32
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used

[bcgong@localhost ph64]$
```


这一段先核对三件事：程序是 QE 7.1，使用 32 个 MPI 进程，读取的是 `pwxall.in`。`&CELL ignored` 来自 SCF 输入里保留的空晶胞控制块；这条提示不表示程序进行了晶胞优化。赝势波函数归一化、强制指定泛函和 `ibrav=0` 的提示也保留在输出中，需要结合本次输入逐项读，不能只摘出没有提示的几行。

再读实际采用的体系与数值设置：

```text
[bcgong@localhost ph64]$ grep -E 'number of atoms|number of atomic types|number of electrons|Kohn-Sham states|kinetic-energy cutoff|charge density cutoff|convergence threshold|number of k points' pwxall.out
     number of atoms/cell      =            6
     number of atomic types    =            4
     number of electrons       =        71.00
     number of Kohn-Sham states=           43
     kinetic-energy cutoff     =     120.0000  Ry
     charge density cutoff     =     960.0000  Ry
     scf convergence threshold =      1.0E-12
     number of k points=   374  Gaussian smearing, width (Ry)=  0.0037
[bcgong@localhost ph64]$
```


这里的 374 是程序经过对称性处理后列出的 k 点数，不能拿它和 `64×64×1` 的完整网格直接比较大小。六个原子、四种元素、120/960 Ry 截断、0.0037 Ry 展宽以及 `1.0E-12` 的电子阈值，都应与输入对应。

## 运行中看队列，也看电子迭代

在这个窗口实际使用的两个连续查看命令是：

```text
[bcgong@localhost ph64]$ watch -n 10 'squeue -j 18178 -o "%.10i %.16j %.8T %.10M %.6D %R"'
```

按 `Ctrl-C` 退出队列监视，再跟随程序输出：

```text
[bcgong@localhost ph64]$ tail -f pwxall.out
```

这里的 `Ctrl-C` 结束的是 `watch` 或 `tail -f`；已经交给 Slurm 的计算仍在后台运行。输出在一次较长的对角化期间可能暂时不增加，不能因此马上重复提交。

初次查看时，程序进入了第一轮迭代：

```text
[bcgong@localhost ph64]$ tail -n 20 pwxall.out

     Starting wfcs are   47 randomized atomic wfcs
     Checking if some PAW data can be deallocated...
       PAW data deallocated on   20 nodes for type:  1
       PAW data deallocated on   27 nodes for type:  2
       PAW data deallocated on   27 nodes for type:  3
       PAW data deallocated on   22 nodes for type:  4

     total cpu time spent up to now is       39.4 secs

     Self-consistent Calculation

     iteration #  1     ecut=   120.00 Ry     beta= 0.40
     Davidson diagonalization with overlap

---- Real-time Memory Report at c_bands before calling an iterative solver
           800 MiB given to the printing process from OS
             0 MiB allocation reported by mallinfo(arena+hblkhd)
         53432 MiB available memory on the node where the printing process lives
------------------
[bcgong@localhost ph64]$
```


`iteration #` 是电子迭代编号。每一轮完成后，继续看 `total energy` 和 `estimated scf accuracy`。接受这次电子迭代时，要对照输入阈值检查最终误差和程序的收敛信息；相邻两轮总能量看起来接近，不能代替这个检查。

在本机这个作业中，计算节点就是当前主机，因此还可以查看进程。这里只截取前四行：

```text
[bcgong@localhost ph64]$ ps -u bcgong -o pid,ppid,stat,etime,%cpu,%mem,args | grep '[p]w.x' | head -n 4
124342 124325 S          02:18  0.0  0.0 /bin/sh /data/intel/oneapi/mpi/2021.5.0//bin/mpirun -np 32 <qe_bin>/pw.x -in pwxall.in
124347 124342 S          02:18  0.0  0.0 mpiexec.hydra -np 32 <qe_bin>/pw.x -in pwxall.in
124373 124364 R          02:17  100  0.3 <qe_bin>/pw.x -in pwxall.in
124374 124364 R          02:17  100  0.3 <qe_bin>/pw.x -in pwxall.in
[bcgong@localhost ph64]$
```


启动器本身占用 CPU 很少，后面的 `pw.x` 工作进程则在计算。这是当时的进程快照；在计算节点与登录节点分开的集群上，应使用该集群允许的节点监控方式，不能把登录节点的 `ps` 当成远端计算节点的状态。

错误日志也单独检查：

```text
[bcgong@localhost ph64]$ wc -c pwxall.err _err.18178.log
0 pwxall.err
0 _err.18178.log
0 total
[bcgong@localhost ph64]$
```


两份文件在这次查看时都是零字节。运行中为空只表示截至这一刻没有写入错误，结束后还要再读一次。

这台机器的历史记账命令返回：

```text
[bcgong@localhost ph64]$ sacct -j 18178 --format=JobID,State,ExitCode,Elapsed,MaxRSS
Slurm accounting storage is disabled
[bcgong@localhost ph64]$
```


因此这里不能从 `sacct` 获取最终退出码和内存统计。作业结束后要及时用 [scontrol](https://slurm.schedmd.com/scontrol.html) 读取 `scontrol show job 18178` 并保留结果，再结合程序输出、错误日志和保存文件判断。作业从 `squeue` 消失，只表示它不再排队或运行。

## pwxall 结束后，怎样决定能否接 pwx

任务退出后，先按下面的顺序检查；这一轮的实际结果接在后面：

```bash
scontrol show job 18178
tail -n 30 pwxall.out
grep -E 'convergence has been achieved|estimated scf accuracy|^!|JOB DONE' pwxall.out | tail -n 8
cat pwxall.err
cat _err.18178.log
grep -niE 'error in routine|convergence NOT achieved|eigenvalues not converged|MPI_ABORT|killed|out of memory|IEEE_' pwxall.out pwxall.err _out.18178.log _err.18178.log
```

先看调度状态与退出码，再看 QE 是否正常结束、电子迭代是否达到本输入的阈值。任何报错、未收敛本征值或异常退出，都需要先解释清楚；即使出现 `JOB DONE.`，也不能跳过它们。`grep` 没有输出时仍要读尾部和错误文件，因为一个关键词列表不可能覆盖全部故障。

致密网格这一步还承担保存电子本征值数据的任务。核对本机 QE 7.1 的写出代码后，对应文件应位于 `out/srnsnse.a2Fsave`。它不是已经积分得到的 α²F 谱。结束后要核实文件非空、内部带数与 k 点数和本次输出一致，并确认记录的是 64×64×1 网格。

进入粗网格 SCF 前，还要保留这份数据和致密网格的 XML 描述。两次 SCF 使用相同的 `prefix/outdir`，粗网格会更新 `.save` 里的内容；保存文件不能只看最后一次修改后的样子来追认上一步。

这里验收的是“这一份固定结构 SCF 是否正常完成、能否用于下一步数据衔接”。结构优化、赝势适用性和 k/q/展宽对目标物理量的收敛仍是另外的检查，不能由这次 SCF 通过一并代替。

## 密网格这一轮实际怎样结束

先读调度器记录，再读输出末尾的收敛信息：

```text
[bcgong@localhost ph64]$ scontrol show job 18178 | grep -E 'JobId=|JobState=|RunTime=|ExitCode='
JobId=18178 JobName=srnsnse-k64
   JobState=COMPLETED Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:40:37 TimeLimit=365-00:00:00 TimeMin=N/A
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -E 'iteration #|estimated scf accuracy|convergence has|^!|JOB DONE' pwxall.out | tail -n 10
     estimated scf accuracy    <          1.0E-10 Ry
     iteration # 21     ecut=   120.00 Ry     beta= 0.40
     estimated scf accuracy    <          2.3E-12 Ry
     iteration # 22     ecut=   120.00 Ry     beta= 0.40
     estimated scf accuracy    <          2.0E-12 Ry
     iteration # 23     ecut=   120.00 Ry     beta= 0.40
!    total energy              =   -1784.37924631 Ry
     estimated scf accuracy    <          5.5E-13 Ry
     convergence has been achieved in  23 iterations
   JOB DONE.
[bcgong@localhost ph64]$
```


作业 18178 在 40 分 37 秒后结束，退出码为 `0:0`。电子迭代共 23 轮，最后打印的误差上界为 `5.5E-13 Ry`，低于本输入的 `1.0E-12 Ry`，并出现 `JOB DONE.`。

结束后再检查错误日志与异常信息：

```text
[bcgong@localhost ph64]$ wc -c pwxall.err _err.18178.log
0 pwxall.err
0 _err.18178.log
0 total
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -niE 'Error in routine|convergence NOT achieved|eigenvalues not converged|MPI_ABORT|out.of.memory|IEEE_' pwxall.out pwxall.err _out.18178.log _err.18178.log
[bcgong@localhost ph64]$
```


两份错误文件都是零字节，上面的关键词检查没有匹配。但仍应阅读完整输出：例如本次 vdW-DF 的文献说明也用了百分号边框，单独搜索一长串 `%` 会把正常说明一起找出来。

把实际 23 轮的误差画在一起，可以看到前几轮上升、后期小幅反弹，以及最后跨过输入阈值的过程：


逐次电子迭代保存在[完整 pwxall.out](/Atlas/examples/snse2-sr2n/ph64/pwxall.out.txt)中；[原绘图脚本](/Atlas/examples/snse2-sr2n/ph64/plot_scf_accuracy.py)和[样式脚本](/Atlas/examples/snse2-sr2n/ph64/atlas_plot_style.py)仍可下载。最终电子收敛看输出末尾误差与所设阈值；迭代误差下降不能代替参数收敛。


纵轴是输出打印的 `estimated scf accuracy` 上界，采用对数刻度，虚线为本次输入阈值。[下载这张图的数据](/Atlas/figures/snse2-sr2n-k64-scf-accuracy.csv)，或直接阅读[完整 pwxall.out（路径已简写）](/Atlas/examples/snse2-sr2n/ph64/pwxall.out.txt)。这张图对应一次固定输入的电子迭代，k 网格的物理量收敛仍需另外比较。

## 先保留密网格数据，再让粗网格写入

这次结束后实际留下了以下文件：

```text
[bcgong@localhost ph64]$ ls -lh out/srnsnse.a2Fsave out/srnsnse.save/data-file-schema.xml out/srnsnse.save/charge-density.dat
-rw-rw-r-- 1 bcgong bcgong 419K Sep 22 19:34 out/srnsnse.a2Fsave
-rw-rw-r-- 1 bcgong bcgong  49M Sep 22 19:33 out/srnsnse.save/charge-density.dat
-rw-rw-r-- 1 bcgong bcgong 859K Sep 22 19:33 out/srnsnse.save/data-file-schema.xml
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ head -n 1 out/srnsnse.a2Fsave
          43         374
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep monkhorst_pack out/srnsnse.save/data-file-schema.xml
      <monkhorst_pack nk1="64" nk2="64" nk3="1" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
        <monkhorst_pack nk1="64" nk2="64" nk3="1" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
[bcgong@localhost ph64]$
```


`a2Fsave` 第一行的 43 和 374 分别对应带数和 k 点数，与本次输出一致；XML 中记录的网格为 64×64×1，三个偏移都是 0。文件内部的本征值、k 点、权重和网格记录也已核对。电荷密度和波函数文件均已写出。

接下来粗网格仍使用同一个 `out/`，先把致密网格的本征值文件和 XML 描述复制出来：

```text
[bcgong@localhost ph64]$ cp out/srnsnse.a2Fsave srnsnse.a2Fsave.k64
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ cp out/srnsnse.save/data-file-schema.xml pwxall.data-file-schema.xml
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ sha256sum out/srnsnse.a2Fsave srnsnse.a2Fsave.k64
2018a5862cef0070aa3e872f48961dd555080509d6cc0fc39fc970d5a8b0a2fb  out/srnsnse.a2Fsave
2018a5862cef0070aa3e872f48961dd555080509d6cc0fc39fc970d5a8b0a2fb  srnsnse.a2Fsave.k64
[bcgong@localhost ph64]$
```


两行哈希相同，说明这份复制与原文件逐字节一致。`srnsnse.a2Fsave.k64` 保存密网格数据，`pwxall.data-file-schema.xml` 保存这一轮的 XML 描述。随后 `.save` 中的 XML 会由粗网格计算更新。

打开力的输出，还能看到为什么电子迭代通过不代表结构已经优化通过：

```text
[bcgong@localhost ph64]$ grep -A8 'Forces acting on atoms' pwxall.out
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000    0.00000000    0.00047248
     atom    2 type  1   force =     0.00000000    0.00000000    0.00017962
     atom    3 type  3   force =     0.00000000    0.00000000    0.00006384
     atom    4 type  4   force =     0.00000000    0.00000000   -0.00032075
     atom    5 type  4   force =     0.00000000    0.00000000   -0.00006845
     atom    6 type  2   force =     0.00000000    0.00000000   -0.00032673
     The non-local contrib.  to forces
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -E 'Total force|negative rho' pwxall.out | tail -n 3
     negative rho (up, down):  3.709E-05 0.000E+00
     Total force =     0.000688     Total SCF correction =     0.000002
     negative rho (up, down):  3.709E-05 0.000E+00
[bcgong@localhost ph64]$
```


这是固定结构上的力，单位为 Ry/au。程序打印的 `Total force` 为 0.000688，`Total SCF correction` 为 0.000002。输出中的 `negative rho` 诊断也保留在这里；它需要结合赝势、网格与数值设置复核。原来的 BFGS 未收敛问题仍然存在，不能用本次电子收敛行替代结构验收。

## 在同一窗口串行提交 pwx

密网格的结束和保存文件核对完后，再看一次粗网格输入并提交：

```text
[bcgong@localhost ph64]$ grep -A1 K_POINTS pwx.in
K_POINTS automatic
  16 16 1 0 0 0
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ sbatch -J srnsnse-k16 pwx.slurm
Submitted batch job 18179
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ squeue -j 18179 -o "%.10i %.16j %.8T %.10M %.6D %R"
     JOBID             NAME    STATE       TIME  NODES NODELIST(REASON)
     18179      srnsnse-k16  RUNNING       0:02      1 localhost
[bcgong@localhost ph64]$
```


作业 18179 使用 `pwx.in`。提交发生在 18178 完成并保留密网格数据之后，两份 SCF 没有同时写入同一个目录。

```text
[bcgong@localhost ph64]$ head -n 35 pwx.out

     Program PWSCF v.7.1 starts on 22Sep2026 at 19:36:47

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on    32 processors

     MPI processes distributed on     1 nodes
     55847 MiB available memory on the printing compute node when the environment starts

     Reading input from pwx.in
Warning: card &CELL ignored
Warning: card / ignored

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4
     file Sr.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  4P renormalized
     file N.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S renormalized
     file Sn.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized
     file Se.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  4S 4P 3D renormalized

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= VDW-DF3-OPT1
                           (   1   4  45   0   3   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -E 'number of atoms|number of atomic types|number of electrons|Kohn-Sham states|kinetic-energy cutoff|charge density cutoff|convergence threshold|number of k points' pwx.out
     number of atoms/cell      =            6
     number of atomic types    =            4
     number of electrons       =        71.00
     number of Kohn-Sham states=           43
     kinetic-energy cutoff     =     120.0000  Ry
     charge density cutoff     =     960.0000  Ry
     scf convergence threshold =      1.0E-12
     number of k points=    30  Gaussian smearing, width (Ry)=  0.0037
[bcgong@localhost ph64]$
```


程序读取的是 `pwx.in`，仍使用 QE 7.1 和 32 个 MPI 进程。网格改变后，这一轮列出 30 个 k 点；元素数、截断、展宽和电子阈值保持配套。监控时把前面的作业号换成 18179，输出文件换成 `pwx.out`，错误文件换成 `pwx.err` 和 `_err.18179.log`。


## 粗网格结束后，再核对数据有没有接错

```text
[bcgong@localhost ph64]$ scontrol show job 18179 | grep -E 'JobId=|JobState=|RunTime=|ExitCode='
JobId=18179 JobName=srnsnse-k16
   JobState=COMPLETED Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:04:15 TimeLimit=UNLIMITED TimeMin=N/A
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -E 'iteration #|estimated scf accuracy|convergence has|^!|JOB DONE' pwx.out | tail -n 10
     estimated scf accuracy    <          7.4E-11 Ry
     iteration # 21     ecut=   120.00 Ry     beta= 0.40
     estimated scf accuracy    <          6.6E-12 Ry
     iteration # 22     ecut=   120.00 Ry     beta= 0.40
     estimated scf accuracy    <          2.5E-12 Ry
     iteration # 23     ecut=   120.00 Ry     beta= 0.40
!    total energy              =   -1784.37930124 Ry
     estimated scf accuracy    <          4.6E-13 Ry
     convergence has been achieved in  23 iterations
   JOB DONE.
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ wc -c pwx.err _err.18179.log
0 pwx.err
0 _err.18179.log
0 total
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep monkhorst_pack out/srnsnse.save/data-file-schema.xml
      <monkhorst_pack nk1="16" nk2="16" nk3="1" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
        <monkhorst_pack nk1="16" nk2="16" nk3="1" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ sha256sum out/srnsnse.a2Fsave srnsnse.a2Fsave.k64
2018a5862cef0070aa3e872f48961dd555080509d6cc0fc39fc970d5a8b0a2fb  out/srnsnse.a2Fsave
2018a5862cef0070aa3e872f48961dd555080509d6cc0fc39fc970d5a8b0a2fb  srnsnse.a2Fsave.k64
[bcgong@localhost ph64]$
```


粗网格作业用时 4 分 15 秒，23 轮电子迭代后打印的误差上界为 `4.6E-13 Ry`，低于输入的 `1.0E-12 Ry`。这一轮同样结合了调度器退出状态、电子收敛、错误文件和 XML 检查。当前 `.save` 的 XML 网格已经变成 16×16×1，而致密网格 `a2Fsave` 与复制出来的文件哈希仍相同；后续所需的两套电子数据没有被混成同一个网格。

再看当前 XML 的 k 点数与几个波函数文件的时间：

```text
[bcgong@localhost ph64]$ grep nks out/srnsnse.save/data-file-schema.xml
      <nks>30</nks>
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ ls -lh out/srnsnse.save/wfc1.dat out/srnsnse.save/wfc30.dat out/srnsnse.save/wfc31.dat out/srnsnse.save/wfc374.dat
-rw-rw-r-- 1 bcgong bcgong 54M Sep 22 19:40 out/srnsnse.save/wfc1.dat
-rw-rw-r-- 1 bcgong bcgong 54M Sep 22 19:41 out/srnsnse.save/wfc30.dat
-rw-rw-r-- 1 bcgong bcgong 54M Sep 22 19:33 out/srnsnse.save/wfc31.dat
-rw-rw-r-- 1 bcgong bcgong 54M Sep 22 19:34 out/srnsnse.save/wfc374.dat
[bcgong@localhost ph64]$
```

当前 XML 记录 `nks=30`。前 30 份波函数已在粗网格运行时重新写入，后面的编号仍保留密网格运行时的文件。因此，数一遍 `wfc*.dat` 得到的 374 不能当作当前粗网格的 k 点数；读取保存数据要以当前 XML、对应输出和实际写入的文件为准。

可以继续阅读[完整 pwx.out（路径已简写）](/Atlas/examples/snse2-sr2n/ph64/pwx.out.txt)，从程序开头、参数回显、逐轮电子迭代一直看到力、应力、计时和结束标记。两步 SCF 的运行和保存数据核对到这里完成，接下来在同一目录启动 ph.x。

<!-- ph64-scf-session-end -->

<!-- ph64-phonon-session-start -->
## 接着提交 ph.x

两步 SCF 留下的文件已经对上。声子输入继续使用 `prefix='srnsnse'`、`outdir='./out/'`，读取粗网格的保存数据；密网格本征值仍保存在 `out/srnsnse.a2Fsave`。本次沿用前面展示的 `phx.in` 和 `phx.slurm`，完整计算 8×8×1 q 网格，没有设置 `start_q/last_q` 分段。

提交前再检查脚本，然后交给 Slurm：

```text
[bcgong@localhost ph64]$ bash -n phx.slurm
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ sbatch -J srnsnse-ph64 phx.slurm
Submitted batch job 18180
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ squeue -j 18180 -o "%.10i %.16j %.8T %.10M %.6D %R"
     JOBID             NAME    STATE       TIME  NODES NODELIST(REASON)
     18180     srnsnse-ph64  RUNNING       0:02      1 localhost
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ scontrol show job 18180 | grep -E 'JobId=|JobState=|RunTime=|NumNodes=|WorkDir='
JobId=18180 JobName=srnsnse-ph64
   JobState=RUNNING Reason=None Dependency=(null)
   RunTime=00:00:04 TimeLimit=UNLIMITED TimeMin=N/A
   NumNodes=1 NumCPUs=16 NumTasks=16 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
   WorkDir=<工作目录>/qe/ph64
[bcgong@localhost ph64]$
```


作业号是 18180，申请的 16 个任务已经分配。这里 `RUNNING` 只说明作业正在运行；继续读 `phx.out`，确认启动的是哪一个程序、读了哪一份输入和保存目录：

```text
[bcgong@localhost ph64]$ head -n 34 phx.out

     Program PHONON v.7.1 starts on 22Sep2026 at 20:44:51

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on    16 processors

     MPI processes distributed on     1 nodes
     R & G space division:  proc/nbgrp/npool/nimage =      16
     56695 MiB available memory on the printing compute node when the environment starts

     Reading input from phx.in
      Title line not specified: using 'default'.

     Reading xml data from directory:

     ./out/srnsnse.save/
     file Sr.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  4P renormalized
     file N.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S renormalized
     file Sn.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized
     file Se.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  4S 4P 3D renormalized

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= VDW-DF3-OPT1
                           (   1   4  45   0   3   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want
[bcgong@localhost ph64]$
```


输出确认本次运行的是 PHONON 7.1，使用 16 个 MPI 进程，读取 `phx.in` 和 `./out/srnsnse.save/`。脚本里的 `OMP_NUM_THREADS=1` 与前面的 16 个 MPI 进程配置相配。没有写标题行时，本次程序使用了 `default`；这条提示之后仍继续读取 SCF 数据。

页首的官方输入文档目前标注为 QE 7.5；这里逐项记录的是本机 QE 7.1 的实际输入与输出，不能用新版手册直接保证旧版本所有组合都适用。当前任务成功启动，也不等于 PAW、泛函与电声计算的数值结果已经通过验证。

## 先看 q 点，再看原子质量和位移模式

程序开头先列出这次真正要处理的 q 点：

```text
[bcgong@localhost ph64]$ grep -A12 'uniform grid of q-points' phx.out
     Dynamical matrices for ( 8, 8, 1)  uniform grid of q-points
     (  10 q-points):
       N         xq(1)         xq(2)         xq(3)
       1   0.000000000   0.000000000   0.000000000
       2   0.000000000   0.144337567   0.000000000
       3   0.000000000   0.288675135   0.000000000
       4   0.000000000   0.433012702   0.000000000
       5   0.000000000  -0.577350269   0.000000000
       6   0.125000000   0.216506351   0.000000000
       7   0.125000000   0.360843918   0.000000000
       8   0.125000000   0.505181486   0.000000000
       9   0.250000000   0.433012702   0.000000000
      10   0.250000000   0.577350269   0.000000000
[bcgong@localhost ph64]$
```


8×8×1 是完整均匀网格，经过本次结构的对称性处理后，需要处理的是上面 10 个不可约 q 点。第一个为 Γ 点。后面的逐 q 文件应与这份列表相对应；不能只从目录名 ph64 推断有多少个声子 q 点。

再看程序实际采用的质量。前面修正过 N/Sn 的索引，这里要从输出再核对一次：

```text
[bcgong@localhost ph64]$ grep -A7 'site n.  atom      mass' phx.out
     site n.  atom      mass           positions (alat units)
        1     Sr  87.6200   tau(    1) = (   -0.00000    0.57735    4.96384  )
        2     Sr  87.6200   tau(    2) = (    0.50000    0.28868    4.28013  )
        3     Sn 118.7100   tau(    3) = (   -0.00000    0.57735    5.97533  )
        4     Se  78.9710   tau(    4) = (    0.00000    0.00000    6.36490  )
        5     Se  78.9710   tau(    5) = (    0.50000    0.28868    5.51263  )
        6     N   14.0070   tau(    6) = (    0.00000    0.00000    4.57298  )

[bcgong@localhost ph64]$
```


N 现在打印为 14.0070，Sn 为 118.7100。六行依次对应六个原子；同一种元素可以出现多次，`amass(i)` 的索引仍按 `ATOMIC_SPECIES` 中的元素种类排列。

Γ 点接着给出了这些表示：

```text
[bcgong@localhost ph64]$ grep -E 'Calculation of q|irreducible representations|Representation.*modes' phx.out
     Calculation of q =    0.0000000   0.0000000   0.0000000
     There are   12 irreducible representations
     Representation     1      1 modes -  To be done
     Representation     2      1 modes -  To be done
     Representation     3      1 modes -  To be done
     Representation     4      1 modes -  To be done
     Representation     5      1 modes -  To be done
     Representation     6      1 modes -  To be done
     Representation     7      2 modes -  To be done
     Representation     8      2 modes -  To be done
     Representation     9      2 modes -  To be done
     Representation    10      2 modes -  To be done
     Representation    11      2 modes -  To be done
     Representation    12      2 modes -  To be done
[bcgong@localhost ph64]$
```


这份输出中，前六个表示各含一个模式，后六个各含两个，一共 18 个，正好对应六个原子的 18 个位移自由度。这里的 12 个表示和前面的 10 个 q 点是不同层次。`To be done` 表示这份启动输出还没有把它们算完，下面列出的位移图样也不能当成已经得到的声子频率。

## 运行时有哪些文件，怎样继续看进度

此时 `srnsnse.dyn0` 已经出现：

```text
[bcgong@localhost ph64]$ cat srnsnse.dyn0
   8   8   1
  10
   0.000000000000000E+00   0.000000000000000E+00   0.000000000000000E+00
   0.000000000000000E+00   0.144337567308136E+00   0.000000000000000E+00
   0.000000000000000E+00   0.288675134616271E+00   0.000000000000000E+00
   0.000000000000000E+00   0.433012701924407E+00   0.000000000000000E+00
   0.000000000000000E+00  -0.577350269232543E+00   0.000000000000000E+00
   0.125000000000007E+00   0.216506350962204E+00   0.000000000000000E+00
   0.125000000000007E+00   0.360843918270339E+00   0.000000000000000E+00
   0.125000000000007E+00   0.505181485578475E+00   0.000000000000000E+00
   0.250000000000014E+00   0.433012701924407E+00   0.000000000000000E+00
   0.250000000000014E+00   0.577350269232543E+00   0.000000000000000E+00
[bcgong@localhost ph64]$
```


第一行是网格，第二行是 10，后面是十个 q 点坐标。这个文件在初始化时就能写出，因此看到 `dyn0` 不能认定全部动力学矩阵已经完成。

再打开声子保存目录：

```text
[bcgong@localhost ph64]$ ls -1 out/_ph0/srnsnse.phsave
control_ph.xml
patterns.10.xml
patterns.1.xml
patterns.2.xml
patterns.3.xml
patterns.4.xml
patterns.5.xml
patterns.6.xml
patterns.7.xml
patterns.8.xml
patterns.9.xml
status_run.xml
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ cat out/_ph0/srnsnse.phsave/status_run.xml
<?xml version="1.0" encoding="UTF-8"?>
<Root>
  <STATUS_PH>
    <STOPPED_IN>phq_setup.</STOPPED_IN>
    <RECOVER_CODE>-40</RECOVER_CODE>
    <CURRENT_Q>1</CURRENT_Q>
    <CURRENT_IU>1</CURRENT_IU>
  </STATUS_PH>
</Root>
[bcgong@localhost ph64]$
```


现在已经有十份 `patterns.*.xml`。结合刚才输出中的 `To be done`，可以看到“位移模式文件已经建立”与“响应求解已经完成”是两件事。这份状态文件记录 `CURRENT_Q=1`、`CURRENT_IU=1`；尽管字段叫 `STOPPED_IN`，当时 Slurm 仍为 `RUNNING`，16 个 ph.x 工作进程也在使用 CPU，不能单凭这个字段名认定任务已终止。

在共享窗口中继续跟随输出：

```text
[bcgong@localhost ph64]$ tail -f phx.out
```

按 `Ctrl-C` 退出查看后，再用下面两条命令分别看队列和最近的响应迭代：

```bash
squeue -j 18180 -o "%.10i %.16j %.8T %.10M %R"
grep -E 'Calculation of q|Representation|iter #|Convergence|convergence|freq' phx.out | tail -n 30
```

较长的一次求解中，输出可能暂时停在同一段。先联合检查队列、进程和错误日志，再判断是否异常；不要因为屏幕不滚动就重复提交，让两个 ph.x 同时写这个目录。

随后，Γ 点第一个表示开始出现自洽响应迭代：

```text
[bcgong@localhost ph64]$ tail -n 20 phx.out

     PHONON       :   2m42.11s CPU   2m44.00s WALL


     Representation #   1 mode #   1

     Self-consistent Calculation

     Pert. #  1: Fermi energy shift (Ry) =     2.3174E-01     0.0000E+00

      iter #   1 total cpu time :   206.5 secs   av.it.:   5.4
      thresh= 1.000E-02 alpha_mix =  0.700 |ddv_scf|^2 =  1.884E-04

     Pert. #  1: Fermi energy shift (Ry) =    -4.6446E+00     0.0000E+00

      iter #   2 total cpu time :   271.4 secs   av.it.:  12.8
      thresh= 1.372E-03 alpha_mix =  0.700 |ddv_scf|^2 =  9.325E-02

     Pert. #  1: Fermi energy shift (Ry) =    -1.1181E+00     0.0000E+00
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -E 'convergence threshold|number of atoms|number of k points' phx.out
     number of atoms/cell      =            6
     convergence threshold     =      1.0E-16
     number of k points=    30  Gaussian smearing, width (Ry)=  0.0037
[bcgong@localhost ph64]$
```


这部分已经进入声子响应求解。迭代行中的 `thresh` 是内层线性方程求解使用的阈值，不能把它当成输入的 `tr2_ph`。本次程序在前面的设置回显中打印 `convergence threshold = 1.0E-16`；继续看 `|ddv_scf|^2` 的变化和该表示的最终收敛信息。初始几轮残差可以上升，一两行输出还不足以判断整段求解是否失败。

同时再检查错误文件：

```text
[bcgong@localhost ph64]$ wc -c phx.err _err.18180.log
0 phx.err
0 _err.18180.log
0 total
[bcgong@localhost ph64]$
```

```text
[bcgong@localhost ph64]$ grep -niE 'Error in routine|convergence NOT|eigenvalues not converged|MPI_ABORT|IEEE_' phx.out phx.err _err.18180.log
[bcgong@localhost ph64]$
```


两份错误文件此时为空，关键词检查也没有匹配；这只是启动与早期迭代的观察。可以阅读[本次 phx.out 的启动快照（路径已简写）](/Atlas/examples/snse2-sr2n/ph64/phx.startup.out.txt)，从程序开头、q 点列表、对称性和位移模式一路看到 Γ 点开始迭代。该文件是当时截取的静态副本，后续进度仍以计算目录中的 `phx.out` 为准。

## ph.x 结束后，怎样决定能否进入后处理

结束时仍要及时保存 `scontrol show job 18180`，因为这台机器的 `sacct` 没有开启。先核对正常退出、错误日志和程序结束信息：

```bash
scontrol show job 18180
tail -n 50 phx.out
cat phx.err
cat _err.18180.log
grep -niE 'Error in routine|convergence NOT|eigenvalues not converged|MPI_ABORT|IEEE_|JOB DONE' phx.out phx.err _out.18180.log _err.18180.log
```

随后逐 q 核对：本次列表中的十个 q 点是否全部处理，每个点所需的不可约表示是否都求解完成，有没有未收敛提示。再核对 `srnsnse.dyn1` 到 `srnsnse.dyn10` 的 q 坐标、六原子结构、质量与频率内容；文件存在或总数等于十，都不足以证明其中内容完整。

本次还要求计算电声耦合，因此要另外检查 `elph_dir` 中对应的逐 q 数据，确认模数与本体系的 18 个模式相符，展宽记录与 `el_ph_nsigma=20` 配套，且没有混入旧质量、其他网格或其他材料的结果。完整文件尚未生成前，不能把 Sc₂C/ZrCl₂ 的 λ 表接到这条计算链上。

动力学矩阵齐全且核对通过后，才接 q2r.x 与 matdyn.x。当前 matdynxline.in 的 dos=false 表示沿给定 q 列表生成声子频散路径；la2F 只控制电声系数插值，并不代替 lambda.x 对完整不可约 q 网格作权重积分。生成 lambda.x 输入前，必须逐项核对输入 q 坐标、顺序和权重与 elph.inp_lambda.* 文件头；QE 7.1 lambda.f90 中的 q 坐标一致性检查已注释。参见 <a href="https://raw.githubusercontent.com/QEF/q-e/qe-7.1/PHonon/PH/lambda.f90">QE 7.1 lambda.f90</a> 与 <a href="https://raw.githubusercontent.com/QEF/q-e/qe-7.1/PHonon/Doc/INPUT_MATDYN.def">QE 7.1 INPUT_MATDYN.def</a>。
<!-- ph64-phonon-session-end -->

## 质量修正后的高频声子范围、逐 q 快照与当前任务状态

本节保留了旧计算的逐 q 快照和提交时的队列输出。它们不代表当前任务状态。2026-09-29 核查显示：作业 18344 与 18345 的两步 SCF 均已完成，分别经过 23 轮迭代，最终误差约为 5.5×10⁻¹³ Ry 与 4.6×10⁻¹³ Ry，低于输入阈值 1.0×10⁻¹² Ry；随后作业 18346 的 Γ 点 ph.x 在第 9 个不可约表示、第 11/12 个位移时于 15:56:15 被取消，残差为 2.225×10⁻¹¹，未达到 tr2_ph=1.0×10⁻¹⁶。dyn1 为零字节，且没有 elph_dir。ph96 目录只有输入和脚本，没有计算输出。因此当前没有完成的 q 网格、EPC、α²F 或 Tc；文中的 q=1、2 耦合数字是错误氮质量修正前的历史输出。

历史声子范围记录：
现存新目录的 lambdax.in 预设频率上限为 12 THz，首行是 12 0.12 1；第三列 1 表示 Methfessel–Paxton 展宽。因为当前声子响应没有完成，这个输入仍是计划设置，不能据此称 12 THz 谱范围已经验证。
历史 q=1、2 的逐模耦合与低频阈值记录：
   阶段性留存的 [`elph.inp_lambda.1`](/Atlas/examples/snse2-sr2n/ph64/elph.inp_lambda.1) 与 [`elph.inp_lambda.2`](/Atlas/examples/snse2-sr2n/ph64/elph.inp_lambda.2) 记录了质量修正前（`M_N = 118.71`）前两个 q 点的逐模输出：在 `q = 1`（Γ 点）处，第 13 支（`4.23 THz`）与第 16 支（`4.60 THz`）在 `σ = 0.040 Ry` 下分别给出 `λ = 0.0328`（`γ = 7.70 GHz`）与 `λ = 0.0233`（`γ = 6.44 GHz`），而在 `σ = 0.004 Ry` 下分别升至 `λ = 0.3102`（`γ = 89.08 GHz`）与 `λ = 0.1620`（`γ = 54.86 GHz`）；在 `q = 2` 处，第一支声学模 `ν = 1` 的频率为 `0.5318 THz`（`17.74 cm⁻¹`），因低于 QE 7.1 `elph.f90` 中 `20 cm⁻¹` 的低频阈值，程序将其 `λ` 置为 `0.0000`（保留 `γ = 0.09 GHz`），而紧邻的 `ν = 2`（`0.7075 THz = 23.60 cm⁻¹`）与 `ν = 3`（`1.1465 THz = 38.24 cm⁻¹`）在 `σ = 0.040 Ry` 下分别给出 `λ = 0.0572` 与 `0.0336`（在 `σ = 0.032 Ry` 下 `ν = 2` 达 `0.0647`）。

下面的 squeue 记录是依赖链提交时的快照，不是当前排队状态。原计划将 8×8×1 网格的 10 个不可约 q 点分为四批，再接 q2r.x、matdyn.x 与 lambda.x；但 2026-09-29 的现场状态如上，本链未完成。

```text
[bcgong@localhost ph64]$ head -n 5 lambdax.in
12 0.12 1
       10
    0.000000000   0.000000000   0.000000000   1.00
    0.000000000   0.144337567   0.000000000   6.00
    0.000000000   0.288675135   0.000000000   6.00
[bcgong@localhost ph64]$ grep -E 'start_q|last_q|recover' phx.in phx1.in phx2.in phx3.in
phx.in:  start_q=1
phx.in:  last_q=3
phx1.in:  start_q=4
phx1.in:  last_q=5
phx1.in:  recover=.true.
phx2.in:  start_q=6
phx2.in:  last_q=7
phx2.in:  recover=.true.
phx3.in:  start_q=8
phx3.in:  last_q=10
phx3.in:  recover=.true.
[bcgong@localhost ph64]$ squeue -u bcgong -o "%.10i %.16j %.8T %.10M %.6D %R"
     JOBID             NAME    STATE       TIME  NODES NODELIST(REASON)
     18344     pwxall.slurm  RUNNING      56:17      1 localhost
     18345        pwx.slurm  PENDING       0:00      1 (Dependency)
     18346        phx.slurm  PENDING       0:00      1 (Dependency)
     18347       phx1.slurm  PENDING       0:00      1 (Dependency)
     18348       phx2.slurm  PENDING       0:00      1 (Dependency)
     18349       phx3.slurm  PENDING       0:00      1 (Dependency)
     18350       q2rx.slurm  PENDING       0:00      1 (Dependency)
     18351 matdynxline.slur  PENDING       0:00      1 (Dependency)
     18352    lambdax.slurm  PENDING       0:00      1 (Dependency)
     18353     pwxall.slurm  PENDING       0:00      1 (Dependency)
     18354        pwx.slurm  PENDING       0:00      1 (Dependency)
     18355        phx.slurm  PENDING       0:00      1 (Dependency)
     18356       phx1.slurm  PENDING       0:00      1 (Dependency)
     18357       phx2.slurm  PENDING       0:00      1 (Dependency)
     18358       phx3.slurm  PENDING       0:00      1 (Dependency)
     18359       q2rx.slurm  PENDING       0:00      1 (Dependency)
     18360 matdynxline.slur  PENDING       0:00      1 (Dependency)
     18361    lambdax.slurm  PENDING       0:00      1 (Dependency)
```

上述两步 SCF 在 2026-09-29 完成；错误质量诊断和质量修正前 q=1、2 的文件是历史快照，不能接入质量修正后的 PH/EPC 链。


配套输入、历史输出和绘图脚本见 snse2-sr2n/ph64 与 snse2-sr2n/ph96。2026-09-29 仅确认两步 SCF 收敛及 Γ 点 PH 中止；后续是否重提由材料计算协调决定，此处不把旧快照写成当前完整 Tc(σ) 结果。

</details>

<span id="zrcl2-sc2c-k64-k96-record"></span>

## 二维异质结 ZrCl₂/Sc₂C 的保存双网格结果与谱积分上限核对

本节记录 ZrCl₂/Sc₂C 的 64×64×1（ph64）与 96×96×1（ph96）原始计算链，以及对应保存输出表的核查。原始结构相对 a₀=3.308845 Å 拉伸至 a=3.358477221 Å，即 +1.499986%（约 +1.5%）。两条原始 10 THz 分支完成 10 个不可约 q 点；另外存有 18 THz 的 lambdax 输出表，但它们没有与已执行输入、命令和 QE 可执行文件对应起来。ph64.1/ph96.1是另一轮准备并启动过的加密链，部分SCF/PH输出存在，随后因资源停止；没有完整加密Tc输出对。

本节依次保留电子结构诊断、原始 10 THz 谱表和保存 Tc 表的算术核对。18 THz 来源未闭合，故交点仅用于描述现有表格。


1. 电子轨道投影能带（Fatbands）、分波态密度（PDOS）与二维费米面（Fermi Surface）如何与电声耦合模式相互印证；
2. 如何用有匹配输入的 10 THz 输出比较直接 λ 与谱积分，并识别频率网格上限对 α²F 与 ωlog 的影响；18 THz 保存表的来源仍未闭合，不能据此称为已验证修正。
3. 对保存 Tc 表作线性插值：匹配输入的 10 THz 表有两个交点；18 THz 保存表有一个诊断性交点，来源仍未闭合。交点只用于说明现有打印表，不代表经验证的 Tc 或网格收敛。

### 体系设置与已保存的双网格分支

`ZrCl₂/Sc₂C` 原胞含 6 个原子（1 个 Zr、1 个 C、2 个 Cl、2 个 Sc，共 18 条声子支），采用 `vdw-DF3-opt1` 泛函、PAW 赝势与 `ecutwfc = 100 Ry`、`ecutrho = 800 Ry`、SCF 展宽 `degauss = 0.0037 Ry`（`3.7d-3`）。两套双网格分支的目录结构与参数对照如下：

| 分支目录 | 致密电子网格 (`pwxall.in`) | 响应粗网格 (`pwx.in`) | 声子 q 网格 (`phx*.in`) | 双 δ 展宽步长与档数 | `lambdax.in` 积分上限 |
| --- | --- | --- | --- | --- | --- |
| ph64 | 64 × 64 × 1，la2F=true | 16 × 16 × 1 | 8 × 8 × 1，10 个不可约 q，分 4 批 | el_ph_sigma=0.001，20 档（0.001–0.020 Ry） | 10 THz：输入记录为 10 0.12 1；18 THz：保存输出表，来源未核实 |
| ph96 | 96 × 96 × 1，la2F=true | 16 × 16 × 1 | 8 × 8 × 1，10 个不可约 q，分 4 批 | el_ph_sigma=0.001，20 档（0.001–0.020 Ry） | 10 THz：输入记录为 10 0.12 1；18 THz：保存输出表，来源未核实 |
| ph64.1 / ph96.1 | 64 × 64 × 1 / 96 × 96 × 1 | 16 × 16 × 1 | 输入准备为 8 × 8 × 1、10 个不可约 q | el_ph_sigma=0.0005，20 档 | 18 0.12 1 为候选输入；没有完整 Tc 输出对 |

原始 ph64 与 ph96 使用相同的 8×8×1 q 网格，10 个不可约 q 点分四批完成，随后得到 10 THz 的原生 lambdax 数据。18 THz 保存表目前没有执行输入或命令可追溯；准备好的 ph64.1/ph96.1 输入不能替代输出生成记录。完整输入与原始输出见 zrcl2-sc2c/ph64 和 zrcl2-sc2c/ph96。

```text
[bcgong@localhost ph64]$ ls -1 zrclscc.dyn* elph_dir/elph.inp_lambda.*
elph_dir/elph.inp_lambda.1
elph_dir/elph.inp_lambda.2
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
elph_dir/elph.inp_lambda.9
elph_dir/elph.inp_lambda.10
zrclscc.dyn0
zrclscc.dyn1
zrclscc.dyn2
zrclscc.dyn3
zrclscc.dyn4
zrclscc.dyn5
zrclscc.dyn6
zrclscc.dyn7
zrclscc.dyn8
zrclscc.dyn9
zrclscc.dyn10
[bcgong@localhost ph64]$ diff ../ph64/pwxall.in ../ph96/pwxall.in
47c47
<   64 64 1 0 0 0
---
>   96 96 1 0 0 0
```

### 电子结构与模式分析的衔接

电子投影与费米面分别从[投影能带](/Atlas/m/fatband/qe/)、[态密度](/Atlas/m/dos/qe/)及[费米面](/Atlas/m/fermi-surface/qe/)进入。旧电子三联图的部分投影来源尚未闭合，因此这里不重复展示，也不据它给q7指定某个电子口袋或认定层间成键。声子本征位移说明哪个原子在动，电子轨道投影说明哪些电子态参与，两者要靠分辨耦合连接。

### 第二步后处理：从 `lambda` 与 `int alpha2F` 的偏差定位 `emax = 10 THz` 截断

打开 `ph64` 与 `ph96` 最初由 `lambdax.in`（首行 `10 0.12 1`）生成的 [`lambdax.out`](/Atlas/examples/zrcl2-sc2c/ph64/lambdax.out)，对比每一行的直接求和 `lambda` 与括号内的谱积分 `( int alpha2F )`：

```text
[bcgong@localhost ph64]$ head -n 6 lambdax.out
     lambda = 3.405555 (   3.390234 )  <log w>=   81.606 K  N(Ef)= 25.881772 at degauss= 0.001
     lambda = 2.766416 (   2.740642 )  <log w>=   82.499 K  N(Ef)= 29.975283 at degauss= 0.002
     lambda = 2.459034 (   2.427435 )  <log w>=   83.155 K  N(Ef)= 30.598111 at degauss= 0.003
     lambda = 2.237823 (   2.204605 )  <log w>=   83.519 K  N(Ef)= 29.793451 at degauss= 0.004
     lambda = 2.045189 (   2.011305 )  <log w>=   83.916 K  N(Ef)= 28.780891 at degauss= 0.005
     lambda = 1.883891 (   1.849465 )  <log w>=   84.375 K  N(Ef)= 27.843494 at degauss= 0.006
```

在前面的 Al 算例中，括号内外两个数仅相差 `6 × 10⁻⁵`；而这里在 `σ = 0.003 Ry` 处 `2.459034` 与 `2.427435` 相差 `0.0316`（在 `σ = 0.020 Ry` 处 `1.059142` 与 `1.012117` 更相差 `0.0470`）。为什么 `alpha2F.dat` 的频率积分会系统性地漏掉一部分耦合？检查 `q = 1`（Γ 点）的 [`elph_dir/elph.inp_lambda.1`](/Atlas/examples/zrcl2-sc2c/ph64/elph_dir/elph.inp_lambda.1) 和声子色散 [`zrclscc.freq.gp`](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.freq.gp) 可以先检查积分范围是否漏掉高频模式：

```text
[bcgong@localhost ph64]$ sed -n '45,64p' elph_dir/elph.inp_lambda.1
     Gaussian Broadening:   0.003 Ry, ngauss=   0
     DOS = 30.598111 states/spin/Ry/Unit Cell at Ef=  0.313512 eV
     lambda(    1)=  0.0181   gamma=    0.81 GHz
     lambda(    2)=  0.0181   gamma=    0.81 GHz
     lambda(    3)=  0.0238   gamma=    2.03 GHz
     lambda(    4)=  0.0249   gamma=    7.69 GHz
     lambda(    5)=  0.0250   gamma=    7.70 GHz
     lambda(    6)=  0.0269   gamma=   15.47 GHz
     lambda(    7)=  0.0580   gamma=   44.85 GHz
     lambda(    8)=  0.0584   gamma=   45.14 GHz
     lambda(    9)=  0.0299   gamma=   34.58 GHz
     lambda(   10)=  0.0302   gamma=   39.03 GHz
     lambda(   11)=  0.0302   gamma=   39.08 GHz
     lambda(   12)=  0.0099   gamma=   17.16 GHz
     lambda(   13)=  0.0100   gamma=   17.30 GHz
     lambda(   14)=  0.0066   gamma=   16.18 GHz
     lambda(   15)=  0.0462   gamma=  133.87 GHz
     lambda(   16)=  0.0581   gamma=  260.01 GHz
     lambda(   17)=  0.0454   gamma=  315.55 GHz
     lambda(   18)=  0.0458   gamma=  318.58 GHz
```

`ZrCl₂/Sc₂C` 的声子谱明显分成两个频段：
- `0–10.11 THz`（直接 DFPT q 网格上为 `0–10.02 THz`）：PHDOS中以Zr、Sc、Cl投影为主的声学与中低频光学频段，共 15 条，其中 Γ 点 `ν = 7, 8`（`5.15 THz`）给出 `λ = 0.0580 / 0.0584`，而在有限波矢 `q = 7`（`(0.125000, 0.360844, 0)`）处最低声学支 `ν = 1`（`1.42 THz`）给出 `γ = 280.36 GHz`、单模耦合高达 **`λ = 4.7525`**（`ph96` 为 `4.7043`）；
- `12.49–17.11 THz`（`416.6–570.7 cm⁻¹`，原始 DFPT 网格为 `12.38–17.11 THz`）：逐原子PHDOS中C投影占优的高频段，含三条光学支（`ν = 16, 17, 18`），其中Γ点高频光学模 `ν = 16`（`12.38 THz`）与高频双重简并组 `ν = 17, 18`（`15.42 THz`）的声子线宽高达 **`γ = 260.01、315.55、318.58 GHz`**（`ph96` 中为 `297.74、318.99、322.13 GHz`），单模耦合分别为 `λ = 0.0581、0.0454、0.0458`（`ph96` 中为 `0.0662、0.0456、0.0461`）。

QE 7.1 的 lambda.f90 说明，lambdax.in 第一列是 emax，第三列 ngaussq 控制频率展宽核：0 为普通 Gaussian，1 为 Methfessel–Paxton。实际 ph64/ph96 输入首行为 10 0.12 1，因此原始输入不是 Gaussian。源码中的直接 λ 求和遍历逐 q EPC 数据；α²F 与 ωlog 则由 emax 限定的频率网格计算，高于上限的模式仍可能通过展宽尾部贡献低于上限的频率。18 THz 文件没有可核验的执行输入、命令或可执行文件身份，故不能断言该组输出只改变了 emax。参见 QE 7.1 的 <a href="https://raw.githubusercontent.com/QEF/q-e/qe-7.1/PHonon/PH/lambda.f90">lambda.f90 源码</a>。

```text
[bcgong@localhost ph64]$ head -n 6 lambdax.emax18.out
     lambda = 3.405555 (   3.405453 )  <log w>=   82.396 K  N(Ef)= 25.881772 at degauss= 0.001
     lambda = 2.766416 (   2.766329 )  <log w>=   84.148 K  N(Ef)= 29.975283 at degauss= 0.002
     lambda = 2.459034 (   2.458955 )  <log w>=   85.447 K  N(Ef)= 30.598111 at degauss= 0.003
     lambda = 2.237823 (   2.237751 )  <log w>=   86.178 K  N(Ef)= 29.793451 at degauss= 0.004
     lambda = 2.045189 (   2.045122 )  <log w>=   86.896 K  N(Ef)= 28.780891 at degauss= 0.005
     lambda = 1.883891 (   1.883828 )  <log w>=   87.678 K  N(Ef)= 27.843494 at degauss= 0.006
```

已保存的 18 THz 表中，σ=0.003 Ry 的 ph64 行直接 λ 为 2.459034、谱积分为 2.458955；全表最大绝对差为 0.000102，因此不能写成严格小于 1×10⁻⁴。该比较是输出表算术，因生成来源未闭合，不代表已验证的 emax-only 修正。原始10 THz谱与逐模式量在各自文件中核对；旧图只作为下载资料，不能以混合散点面积读单独γ或λ。

[原三联图下载](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png)保留历史版式：左侧面积按clip(26λ+0.14γ,4,95)混合编码，颜色为γ；右侧累计λ乘0.36共用横轴。频段归属按原子PHDOS，逐支位移方向仍需同一父链本征矢，不能用另一组Γ动画替代。独立数据与方法见[模式表](/Atlas/m/phonon-linewidth/qe/#heterostructure-modes)和[谱积分页](/Atlas/m/eliashberg-a2f/qe/#spectral-window)。

### 保存 Tc 表的插值核查与来源边界

下表并列展示已保存输出中的 10 THz 与 18 THz 数据。18 THz 列来自现存打印表，但来源链没有闭合；所有交点均由打印到 0.001 K 的 Tc 采样值作线性插值，只用于表格诊断。

| 电子展宽 `σ` (Ry) | `N_64(EF)` | `N_96(EF)` | `λ_64` | `λ_96` | `ω_log,64` (K, 18 THz) | `ω_log,96` (K, 18 THz) | `Tc,64` (K, 18 THz) | `Tc,96` (K, 18 THz) | `ΔTc = Tc,64 − Tc,96` (K) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0.001` | 25.882 | 31.638 | 3.4056 | 3.1835 | 82.396 | 84.843 | 15.620 | 15.658 | `−0.038` |
| `0.002` | 29.975 | 31.560 | 2.7664 | 2.7267 | 84.148 | 85.364 | 14.588 | 14.696 | `−0.108` |
| `0.003` | 30.598 | 30.772 | 2.4590 | 2.4511 | 85.447 | 85.664 | 13.947 | 13.958 | `−0.011` |
| `0.004` | 29.793 | 29.802 | 2.2378 | 2.2329 | 86.178 | 86.239 | 13.325 | 13.317 | `+0.008` |
| `0.005` | 28.781 | 28.781 | 2.0452 | 2.0410 | 86.896 | 86.949 | 12.689 | 12.680 | `+0.009` |
| `0.010` | 25.941 | 25.941 | 1.4945 | 1.4914 | 91.633 | 91.701 | 10.409 | 10.397 | `+0.012` |
| `0.020` | 26.058 | 26.058 | 1.0591 | 1.0576 | 103.462 | 103.529 | 7.846 | 7.835 | `+0.011` |

保存表的数值说明：
1. 在 18 THz 保存表中，Nσ(EF) 在 σ=0.004 Ry 为 29.793 对 29.802、在 σ=0.005 Ry 为 28.780891 对 28.781039；这两个采样点较接近，但不足以证明电子网格收敛。
2. 按打印 Tc 表逐段线性插值，匹配输入的 10 THz 表有两个交点：σ≈0.001750 Ry、Tc≈14.594 K，以及 σ≈0.003091 Ry、Tc≈13.513 K。18 THz 保存表有一个诊断性交点：σ≈0.003579 Ry、Tc≈13.587 K；按两位小数为 13.59 K。插值用到的 Tc 仅打印到 0.001 K，额外小数不是物理精度，而且该 18 THz 输出缺少生成记录。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-k64-k96-tc.png" alt="ZrCl₂/Sc₂C 两网格保存 Tc 表及线性插值交点核对" loading="lazy"/><figcaption>存储 Tc 表的算术核对：（左）10 THz 匹配输入数据与来源未闭合的 18 THz 保存表；（右）由 Tc 表相邻采样点插值得到的 ΔTc=0 位置。所有标记由脚本动态计算。18 THz 交点只代表保存表，不能证明更改 emax 后的物理结果或电子网格收敛；ph64.1/ph96.1 尚无完整 Tc 输出对。</figcaption></figure>

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-k64-k96-moments.png" alt="ZrCl₂/Sc₂C 两个网格的存储 N(EF)、λ、积分 α²F 与 ωlog 对照" loading="lazy"/><figcaption>保存表的物理量对照：（左）Nσ(EF)；（中）与匹配 10 THz 输入对应的直接 λ 和谱积分；（右）10 THz 输出中的 ωlog。两个网格在部分展宽点较接近，但这些点不构成收敛证明。</figcaption></figure>

ph64.1 与 ph96.1 的准备输入首行均为 18 0.12 1，el_ph_sigma 设为 0.0005 Ry。它们是候选输入，不是现存 18 THz 输出的已证实来源；目前没有完整加密 Tc 输出对，因此这里不把它们描述为已完成的复核计算。

```text
[bcgong@localhost 0015]$ diff -u ph64/phx.in ph64.1/phx.in
--- ph64/phx.in
+++ ph64.1/phx.in
@@ -11,7 +11,7 @@
   outdir='./out/'
   fildyn='zrclscc.dyn'
   electron_phonon='interpolated'
-  el_ph_sigma=0.001
+  el_ph_sigma=0.0005
   el_ph_nsigma=20
   trans=.true.
   ldisp=.true.
[bcgong@localhost 0015]$ head -n 2 ph64.1/lambdax.in ph96.1/lambdax.in
==> ph64.1/lambdax.in <==
18 0.12 1
       10

==> ph96.1/lambdax.in <==
18 0.12 1
       10
```

Tc 表核查结果以机器可读文件保存为 [tc-intersections.json](/Atlas/examples/zrcl2-sc2c/tc-intersections.json)。绘图脚本可从保存表重绘；该脚本不补造 18 THz 的输入或运行来源。
