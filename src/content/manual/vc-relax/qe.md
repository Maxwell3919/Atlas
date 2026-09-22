参考：

- QE 官方文档 INPUT_PW：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## vc-relax（变胞结构优化）

这次先让原子位置和允许的晶胞自由度一起调整，观察力怎样变化。二维模型的真空方向不能随意跟着收缩，所以这里使用 `cell_dofree='fixc'`。下面保留这次没有达到 BFGS 收敛的过程：它适合用来学习检查输出，不能当成已接受结构的范例。

### 建目录、写输入文件

输入文件建议先在本地编辑好，再用 cat 指令在服务器中输入（heredoc）。目录用数字编号，在 Linux 里输入数字后 Tab 补全很方便，这是日常使用的小技巧。另外 `outdir = './out_rx/'` 指向的文件夹会在运行时自动创建，不需要手动建：

```bash
[hzw@localhost QE]$ cd <工作目录>/QE

[hzw@localhost QE]$ mkdir -p 05_relax
[hzw@localhost QE]$ cd 05_relax

[hzw@localhost 05_relax]$ cat > rx.in <<'EOF'
&CONTROL
  calculation = 'vc-relax'
  etot_conv_thr = 1.0000000000d-08
  forc_conv_thr = 1.0000000000d-10
  outdir = './out_rx/'
  prefix = 'HfCl2_PbO2'
  pseudo_dir = '<赝势库路径>'
  tprnfor = .true.
  tstress = .true.
  verbosity = 'high'
/

&SYSTEM
  ibrav = 0
  nat = 6
  ntyp = 4
  ecutwfc = 90
  ecutrho = 720
  input_dft = 'vdw-DF3-opt1'
  force_symmorphic = .true.
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
/

&ELECTRONS
  conv_thr = 1.0000000000d-08
  electron_maxstep = 200
  mixing_beta = 7.0000000000d-01
/

&IONS
/

&CELL
  cell_dofree = 'fixc'
/

ATOMIC_SPECIES
Hf  178.49   Hf.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl   35.45   Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Pb  207.20   Pb.pbe-dn-kjpaw_psl.1.0.0.UPF
O    15.999  O.pbe-n-kjpaw_psl.1.0.0.UPF

CELL_PARAMETERS angstrom
! 此处放入你的结构块（CELL_PARAMETERS 三行；本例初始 a≈3.37559 Å，c = 30 Å）

ATOMIC_POSITIONS crystal
! 此处放入你的结构块（ATOMIC_POSITIONS 各行）

K_POINTS automatic
24 24 1 0 0 0
EOF

[hzw@localhost 05_relax]$ cat rx.in
```

写完 `cat` 一遍回看，是防止 heredoc 手滑的最低成本检查。

### Slurm 脚本

```bash
[hzw@localhost 05_relax]$ cat > rx.slurm <<'EOF'
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

#unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/pw.x<rx.in>rx.out
EOF
[hzw@localhost 05_relax]$
```

np 后的 56 是这个任务占用的 MPI 进程数；`ulimit -s` 设置栈限制，`ulimit -l` 设置可锁定内存限制；它们不能解除 Slurm 的时间或作业内存配额。

### 提交与监控

任务提交后用 `squeue` 看是否在运行，建议提交 5–10 秒后再查，避免短运行后已报错。也可以用 `htop` 对比提交前后的线程数。更完整的优化进展我更推荐：

```bash
watch -n 5 "grep -E 'iteration #|convergence has been achieved|Total force|total stress|CELL_PARAMETERS|ATOMIC_POSITIONS|End of BFGS Geometry Optimization|JOB DONE' rx.out | tail -n 80"
```

也可以单独盯最后输出：`tail -f rx.out`。建议再开一个监控：

```bash
watch -n 10 "squeue -j <jobid>; echo; grep 'Total force' rx.out | tail -n 80"
```

真实输出（每个 BFGS 步内部是一次完整 SCF，力逐级下降）：

```text
Every 5.0s: grep -E 'iteration #|convergence has been achieved|...'  Fri Sep  4 18:44:04 2026

     iteration #  8     ecut=    90.00 Ry     beta= 0.70
     ...
     convergence has been achieved in  14 iterations
     Total force =     0.002185     Total SCF correction =     0.000036
CELL_PARAMETERS (angstrom)
ATOMIC_POSITIONS (crystal)
     iteration #  1     ecut=    90.00 Ry     beta= 0.70
     ...
     convergence has been achieved in  21 iterations
     Total force =     0.001389     Total SCF correction =     0.000278
```

### 结束后验收：JOB DONE 不等于收敛

任务结束后：

```bash
[hzw@localhost 05_relax]$ grep -E \
> 'Begin final coordinates|End final coordinates|Total force|total stress|Final enthalpy|End of BFGS Geometry Optimization|JOB DONE' \
> rx.out | tail -n 100
     Total force =     0.037945     Total SCF correction =     0.000117
     Total force =     0.020507     Total SCF correction =     0.000242
     ...
     Total force =     0.000039     Total SCF correction =     0.000054
     Total force =     0.000095     Total SCF correction =     0.000031
     End of BFGS Geometry Optimization
     Final enthalpy           =   -1795.6890425495 Ry
Begin final coordinates
End final coordinates
   JOB DONE.
[hzw@localhost 05_relax]$
```

从输出看，力总体从 0.037945 Ry/Bohr 降到了 10⁻⁴–10⁻⁵ 量级，随后给出了 End of BFGS / Final enthalpy / JOB DONE 的完整结尾——看起来一切正常。**但 `JOB DONE.` 仅表示程序到达结束段，还必须检查 BFGS 是否收敛。**

本次程序已结束，但 **BFGS 未收敛，不能判定为结构优化通过**。上面的 grep 没有检索 BFGS 收敛信息，需要把相应的行一起读出来。

### 把遗漏的失败行一起找出来

失败信息就在结束段前面：

```text
[hzw@localhost 05_relax]$ grep -Ei 'bfgs failed|End of BFGS|JOB DONE' rx.out
     bfgs failed after  30 scf cycles and  27 bfgs steps, convergence not achieved
     End of BFGS Geometry Optimization
   JOB DONE.
[hzw@localhost 05_relax]$
```

![本次结构优化的总力变化，BFGS 未收敛](/Atlas/figures/relax-force.svg)

力整体下降，但末段并非单调下降。图的横轴是输出中的力报告序号，不是保证接受的 BFGS 步数；判断优化通过仍需看明确的收敛条件。这正是保留失败行比只截取结尾更有用的地方。

## 保存候选结构时，把未收敛状态一起记住

读取末尾结构时，可以用 `vi rx.out` 搜索 `Begin final coordinates`，同时确认对应的 `CELL_PARAMETERS` 与 `ATOMIC_POSITIONS` 单位。若失败输出没有完整结束块，则回到最后一个完整的结构更新记录；不要把不同离子步的晶胞与位置拼在一起。

这一轮保留下来的两个结构片段如下。文件名含有 `relaxed`，仍然只代表保存时的命名，不能覆盖前面的 BFGS 失败信息：

```text
[hzw@localhost 05_relax]$ cat ../01_structure/relaxed_cell.inc
CELL_PARAMETERS (angstrom)
   3.356510437   0.000000000  -0.000000000
  -1.678255218   2.906823306   0.000000000
    0.000000000  -0.000000000  30.000000000
[hzw@localhost 05_relax]$ cat ../01_structure/relaxed_atoms.inc
ATOMIC_POSITIONS (crystal)
Hf            0.0000000000        0.0000000000        0.3750750598
Cl            0.6666666667        0.3333333333        0.4300153898
Cl            0.6666666667        0.3333333333        0.3192017432
Pb           -0.0000000000       -0.0000000000        0.5521514583
O             0.6666666667        0.3333333333        0.5876371921
O             0.3333333333        0.6666666667        0.5147767817
[hzw@localhost 05_relax]$
```

面内晶格从约 3.37559 Å 变为 3.35651 Å，第三晶格矢量仍为 30 Å，与 `cell_dofree='fixc'` 的受限自由度相符。文件记录了这次计算走到的候选结构；继续做正式声子前，需要先解决优化未收敛的问题，并重新核对最后的力和应力。

<a id="al-vc-relax"></a>

## 一份完整走到最后坐标的 Al 晶胞优化

上面的失败记录说明怎样识别停止原因。再看一个已经走完的独立算例：Maxwell 上的 QE 7.5、单原子 fcc Al 原胞，使用 QE 官方库的 `Al.pz-vbc.UPF`。这里是 LDA-PZ 金属设置，与前面的材料不是同一条计算链。它的最后结构将用于本站的 Al 声子、弹性与费米面算例。

完整输入如下。一个原子位于原点，晶胞保留 fcc 对称性；`cell_dofree='ibrav'` 让优化遵守所选 Bravais 晶格约束。在这份 `ibrav=2` 输入里，直接照搬另一种晶格使用的 `volume` 选项会报错，因此保留实际可运行的设置。

```text
maxwell@maxwell:<工作目录>/relax-ibrav$ cat al.relax.in
&CONTROL
 calculation = 'vc-relax'
 prefix = 'al'
 pseudo_dir = '../pseudo'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 etot_conv_thr = 1.0d-8
 forc_conv_thr = 1.0d-5
 nstep = 50
/
&SYSTEM
 ibrav = 2
 celldm(1) = 7.50
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
&IONS
 ion_dynamics = 'bfgs'
/
&CELL
 cell_dynamics = 'bfgs'
 cell_dofree = 'ibrav'
 press = 0.0
 press_conv_thr = 0.05
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.0 0.0 0.0
K_POINTS automatic
16 16 16 0 0 0
```
`press=0.0` 是目标外压，`press_conv_thr=0.05` 的单位为 kbar。这里保持电子网格 16×16×16、40/160 Ry 截断和 0.02 Ry 冷展宽；这组设置支持本次完整操作演示，后面若需要定量弹性常数，还要针对应力与其导数继续比较参数。

真实提交脚本同时写出程序输出与标准错误：

```text
maxwell@maxwell:<工作目录>/relax-ibrav$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-relax
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
mpirun -np 8 <qe_bin>/pw.x -in al.relax.in > al.relax.out 2> al.relax.err
```
保存输入后使用 `sbatch run.slurm` 提交。本次作业号为 1954。用 `tail -f al.relax.out` 观察时，SCF 迭代、应力张量、BFGS 步与新晶胞会交替出现；不同层次的步数不要混在一起数。

这一轮优化从 −7.91 kbar 开始，BFGS 经过三个晶胞更新。输出明确给出收敛及最终坐标块：

```text
     bfgs converged in   4 scf cycles and   3 bfgs steps
     (criteria: energy <  1.0E-08 Ry, force <  1.0E-05 Ry/Bohr, cell <  5.0E-02 kbar)

     End of BFGS Geometry Optimization

     Final enthalpy           =      -4.1908934915 Ry

     File ./tmp/al.bfgs deleted, as requested
Begin final coordinates
     new unit-cell volume =    104.45465 a.u.^3 (    15.47858 Ang^3 )
     density =      2.89457 g/cm^3

CELL_PARAMETERS (alat=  7.50000000)
  -0.498392314   0.000000000   0.498392314
   0.000000000   0.498392314   0.498392314
  -0.498392314   0.498392314   0.000000000

ATOMIC_POSITIONS (crystal)
Al               0.0000000000        0.0000000000        0.0000000000
End final coordinates
```
`CELL_PARAMETERS` 旁边写着 `alat=7.50000000`，它仍是初始长度单位（bohr）。不能把矩阵中的小数直接当 Å，也不能看见 `alat` 未变就说晶胞没有变化。把矩阵乘上这个长度，得到最终 fcc 晶格，常规立方晶格常数为 **3.95606780 Å**。

最终坐标后，程序还会按最后晶胞重新计算电子态。所以下面这一段也要读完，不能在第一次看见 `bfgs converged` 时就截断文件：

```text
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000


     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=        0.02
   0.00000014   0.00000000  -0.00000000            0.02        0.00       -0.00
   0.00000000   0.00000014  -0.00000000            0.00        0.02       -0.00
  -0.00000000  -0.00000000   0.00000014           -0.00       -0.00        0.02
```
最后的压力为 0.02 kbar，原子力在打印精度内为零；这次有 BFGS 收敛、完整最后坐标、重新计算的电子收敛和末尾 `JOB DONE.`。完整[输入](/Atlas/examples/al/relax-ibrav/al.relax.in)、[输出](/Atlas/examples/al/relax-ibrav/al.relax.out)和[提交脚本](/Atlas/examples/al/relax-ibrav/run.slurm)保留了这些相邻段落。

准备后续静态计算时，将最后晶胞和位置带进新的 SCF 输入。本站 [Al 的 DFPT 声子页](/Atlas/m/phonon-dfpt/qe/)展示了实际使用的 `celldm(1)`、SCF 与保存目录，后续计算没有继续读取优化前的 7.50 bohr 晶胞。

## 下一步

固定优化后结构，进入 [SCF](/Atlas/m/scf/qe/)；需要检查晶胞形变后的应力，再进入 [弹性常数](/Atlas/m/elastic-born/qe/)。两个示例的元素、赝势与保存目录分别保留，不交叉复制。

```text
vc-relax → 每轮 SCF + 力 / 应力 → BFGS 收敛
                                  ↓
                         最终晶胞与位置 + 最后电子计算
                                  ↓
                             新 SCF → 后续性质
```
