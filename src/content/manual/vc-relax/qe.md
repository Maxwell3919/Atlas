## 让晶胞参与优化，先看完整的 Al 算例

在 [Si SCF](/Atlas/m/scf/qe/) 中，原子力接近零，晶胞压力却仍为 38.45 kbar。原子处于对称位置，并不保证体积已经合适。要寻找给定外压下的结构，需要开放相应的晶胞自由度。本页用单原子 fcc Al 展示 `vc-relax` 的输入、晶胞更新和末态检查；后半页保留一份未收敛记录，用于比较不同的停止原因。

声子和 EPC 的几何起点需要与所选电子模型匹配；Al 的末态在本站的声子与 EPC 演示中沿用，因此先寻找 LDA-PZ 模型在零外压、fcc 约束下的体积。[Giannozzi 等的 QE 方法论文](https://doi.org/10.1088/0953-8984/21/39/395502)第 4.1 节说明晶胞自由度可参与优化；本例的 QE 7.5 [cell_dofree 定义](https://github.com/QEF/q-e/blob/qe-7.5/PW/Doc/INPUT_PW.def)进一步决定哪些自由度开放。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [Al 例子的官方赝势](https://pseudopotentials.quantum-espresso.org/upf_files/Al.pz-vbc.UPF)

Al 算例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 读取文件；赝势按官方来源准备。HfCl₂/PbO₂ 的历史记录放在后面，用来对照 BFGS 未收敛的停止信息。

<a id="al-vc-relax"></a>

## 一份完整走到最后坐标的 Al 晶胞优化

先用完整输入跟随一个独立算例：Maxwell 上的 QE 7.5、单原子 fcc Al 原胞，使用 QE 官方库的 `Al.pz-vbc.UPF`。这里是 LDA-PZ 金属设置。它的最后结构用于后续 Al 声子与 EPC 演示。Al 用来练习完整变胞记录，后面的二维失败记录用来读取受限晶胞的停止原因。

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
`press=0.0` 是目标外压，`press_conv_thr=0.05` 的单位为 kbar，相当于 0.005 GPa。因为本例保持立方对称性，主要观察体积变化与各向同性压力；这个限制没有搜索改变原型后的其他结构。`forc_conv_thr=1.0d-5 Ry/Bohr` 和 `etot_conv_thr=1.0d-8 Ry` 仍然同时参与优化停止判断，`nstep=50` 是步数上限。单原子高对称原胞的力可以恒为零，所以应力和最后晶胞尤其重要。

`celldm(1)=7.50` 用 bohr 给出初始常规立方晶格参数。这里保持电子网格 16×16×16、40/160 Ry 截断和 0.02 Ry 的 Marzari–Vanderbilt 冷展宽，并求 6 条带以容纳金属的部分占据。改变这些设置会影响能量与压力，尤其不能拿很紧的电子 `conv_thr=1.0d-12` 替代截断能对应力的检查。平衡体积是否稳定，要继续比较截断和采样变化引起的压力与晶格变化；若关心声子，再检查相应频率。

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

fcc 原胞的矢量分量含常规立方边长的一半，矢量模长则为常规边长除以 $\sqrt{2}$。从这份打印矩阵读一个非零分量，可核对

$$
a_{\mathrm{cubic}}\simeq 2\times0.498392314\times7.50\times0.52917721\;\mathrm{\AA}
\simeq3.95607\;\mathrm{\AA},\qquad
V_{\mathrm{primitive}}=a_{\mathrm{cubic}}^3/4\simeq15.47858\;\mathrm{\AA}^3.
$$

体积与 OUT 的 15.47858 Å³ 对应，区别在于这里使用有限打印位数作核对；完整晶格精度仍由保存数据决定。初始 7.50 bohr 常规边长约 3.96883 Å，最终略小。初始负压力与这次收缩方向相符，不能将负号单独解释成结构不稳定。

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
最后的压力为 0.02 kbar，原子力在打印精度内为零。最终晶胞的电子重算在第 1 轮出现了 `c_bands` 本征值未收敛警告；第 2 至第 7 轮没有再出现，随后打印电子收敛行。读这份结果时，应同时保留中途警告、BFGS 收敛、完整最后坐标和程序收尾；中途警告与末轮仍有未收敛本征值的处理不同，见 [QE 故障排查](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html)。

4 个 SCF 周期与 3 个 BFGS 步描述优化轨迹；最终晶胞上的电子重算又有自己的 7 轮电子迭代。这 7 轮没有继续更新晶胞，不能加到 BFGS 步数里。fcc 约束使本例主要读各向同性压力；若换成受限二维晶胞，需要读与允许变动方向对应的应力张量，整胞平均 P 不足以说明面内分量是否达到要求。完整[输入](/Atlas/examples/al/relax-ibrav/al.relax.in)、[输出](/Atlas/examples/al/relax-ibrav/al.relax.out)和[提交脚本](/Atlas/examples/al/relax-ibrav/run.slurm)保留了这些相邻段落。

准备后续静态计算时，将最后晶胞和位置带进新的 SCF 输入。本站 [Al 的 DFPT 声子页](/Atlas/m/phonon-dfpt/qe/)将这份最终晶胞写成 `ibrav=0` 与 `CELL_PARAMETERS angstrom`，并展示匹配的 SCF 和保存目录；后续计算使用的是这些最终晶格矢量。

## HfCl₂/PbO₂ 记录：读取未收敛的停止原因

这次先让原子位置和允许的晶胞自由度一起调整，观察力怎样变化。二维模型的真空方向不能随意跟着收缩，所以这里使用 `cell_dofree='fixc'`。下面保留这次没有达到 BFGS 收敛的过程：它适合用来学习检查输出，不能当成已接受结构的范例。

<details>
<summary>原输入设置与运行监控记录</summary>

### 建目录、写输入文件

以下是旧记录中的建目录和输入操作。结构块在公开版本中隐去，文件用于核对设置和失败原因；复现完整可运行输入可使用上面的 Al 算例。`outdir = './out_rx/'` 由程序写入本次保存数据：

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

写完后用 `cat` 回看文件，检查 namelist 的 `/`、元素数量和坐标单位。上面两段结构内容已从公开记录中隐去，整段照抄不能直接运行；上面的 Al 例子保留了完整的小原胞输入。

先看这次设得最紧的一项：`forc_conv_thr=1.0d-10 Ry/Bohr` 约为 `2.57×10⁻⁹ eV/Å`，这是原记录的数值，不能据此当作通常应采用的力精度。`etot_conv_thr=1.0d-8 Ry` 检查相邻离子步的整胞能量变化，`conv_thr=1.0d-8 Ry` 则控制每一步电子自洽。后面实际残余力远大于这份力阈值；要继续优化，应先核对更紧电子计算下的力与应力，再按后续性质需要设定可验证的停止条件，不能仅因力在下降就宣称通过。

`cell_dofree='fixc'` 固定整条第三晶格矢量，本例用它保留 30 Å 的真空方向；它不是把所有原子的 z 坐标固定。`24 24 1` 是电子 k 网格，第三方向的 1 与这个层状模型对应。输入同时指定 `input_dft='vdw-DF3-opt1'`，因此不能只凭赝势文件名中的 `pbe` 就把这轮称为纯 PBE 计算。`degauss=3.7d-3 Ry` 约为 0.0503 eV；它与 Gaussian 占据、90/720 Ry 截断都属于本例协议，需要分别检查对力和应力的影响。

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

任务提交后，用 `squeue` 查看排队或运行状态，并同时读取程序输出和错误日志。很快退出的作业也可能已经报错，队列中没有任务不能单独说明计算成功。下面用 `watch` 定期查看能量和力的变化：

```bash
watch -n 5 "grep -E 'iteration #|convergence has been achieved|Total force|total stress|CELL_PARAMETERS|ATOMIC_POSITIONS|End of BFGS Geometry Optimization|JOB DONE' rx.out | tail -n 80"
```

也可以单独盯最后输出：`tail -f rx.out`。建议再开一个监控：

```bash
watch -n 10 "squeue -j <jobid>; echo; grep 'Total force' rx.out | tail -n 80"
```

实际输出中，每个 BFGS 步内部又有电子 SCF 迭代；这里截取其中相邻片段，后面结合最终力和停止原因读取：

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

</details>

### 连停止原因一起读取结束段

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

力总体从 0.037945 Ry/Bohr 降到了 10⁻⁴–10⁻⁵ 量级，程序也写出了结束段。这条查询漏掉了 BFGS 的停止原因；下一条命令把失败行一起找出来。

### 把遗漏的失败行一起找出来

失败信息就在结束段前面：

```text
[hzw@localhost 05_relax]$ grep -Ei 'bfgs failed|End of BFGS|JOB DONE' rx.out
     bfgs failed after  30 scf cycles and  27 bfgs steps, convergence not achieved
     End of BFGS Geometry Optimization
   JOB DONE.
[hzw@localhost 05_relax]$
```


结束段明确记录了 30 个 SCF 周期、27 个 BFGS 步后仍未收敛。保存末步结构时，应同时保留这条失败信息及对应输入。

### 保存候选结构与对应停止状态

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

## 二维界面与应变需要哪些晶胞自由度

Al 的零外压立方体积优化与薄层面内优化有不同自由度。二维体系的第三矢量包含真空，不能把三维平均压力直接当成片层受到的面内负载，也不应通过缩短真空去消除它。上面的 `fixc` 固定整条第三晶格矢量；更具体的面内对称约束须按实际晶胞与 [QE 7.5 的 cell_dofree 定义](https://github.com/QEF/q-e/blob/qe-7.5/PW/Doc/INPUT_PW.def)选择。

规定某一应变后，面内矢量本身就是输入条件。此时通常在该条件下做[固定晶胞弛豫](/Atlas/m/relax/qe/)；若同时开放应变方向让它回到零压，最后结构就不再代表原先指定的应变。比较界面构型也应先决定是共同晶格下的比较，还是各自平衡晶格的比较，并把相应的单层参照带到后续能量和电荷分析中。

[Prandini 原文 Fig. 2](https://arxiv.org/pdf/1806.05609v2#page=12)（第 12 页）把 Pd 的压力误差转换为等效体积偏差后，与声子、内聚能和能带误差分别检查，圈选通过判据的截断能。它说明晶胞优化后的压力不能只看一次 SCF 的电子误差：按这种图法复核本页 Al，需要在匹配几何下比较不同截断的压力，并有相应状态方程才可转换成论文的体积指标；这里现有的是一次变胞轨迹，不能把其最后 0.02 kbar 直接填到那张收敛图中。[Ba₂N Fig. 1(a)，第 165101-2 页](https://doi.org/10.1103/PhysRevB.105.165101)再提供二维几何的俯视/侧视参照：从自己的最后完整晶胞与坐标建立 VESTA 结构，画出面内晶胞和原子层高，并保留固定第三矢量的真空。Al 的 fcc 末态与旧 HfCl₂/PbO₂ 候选分别对应它们自己的文件；二维失败记录不能借 Ba₂N 的优化图补成已收敛结构。

Al 输出的 `bfgs converged`、最后完整晶胞和电子重算支持该轮受限优化的停止状态；HfCl₂/PbO₂ 的 `bfgs failed` 保留为候选结构记录。把已经接受的几何写入新的 [SCF](/Atlas/m/scf/qe/)，再接[声子与 EPC](/Atlas/m/phonon-dfpt/qe/)；旧失败记录在这里解释停止条件，不作为本轮材料结果。
