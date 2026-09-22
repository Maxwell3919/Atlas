[ph.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [q2r.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [matdyn.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [QE 电子声子系数及谱函数定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

声子态密度把每个振动模式按频率计数。α²F 又多问了一件事：这些振动与费米面附近电子的耦合有多强？有很多声子模式的频段，不一定就是耦合贡献最大的频段。要画这张图，手里必须有电子声子矩阵元，只有声子频率表还不够。

下面用一份实际完成的 fcc Al 小体系计算，从逐 q 文件走到 α²F，再积分回 λ。QE 版本为 7.5，单原子原胞采用 LDA-PZ 与官方 `Al.pz-vbc.UPF`，晶格常数为 3.95606780081 Å。结构来源及优化过程见 [晶胞优化](/Atlas/m/vc-relax/qe/)，DFPT 的输入结构和逐个响应迭代见 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/)。这里增加的是一套与 EPC 对应的致密电子网格和后处理，不能把普通声子目录的文件名改一改就当作 EPC 结果。

本例依次使用 32×32×32 致密电子网格、16×16×16 响应所依赖的 SCF 网格，以及完整的 4×4×4 q 网格。它们都是不平移的网格。这套网格用于展示一条能走通、可检查的计算路线；尚未通过更密 k/q 网格和截断能的收敛测试。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al`，按正文运行绘图命令。

## 把两次 SCF 的身份认清

先看第一次 SCF。`la2F=.true.` 让程序为后续 EPC 保存致密网格的本征值数据。

```console
maxwell@maxwell:~/al/epc-q4$ cat al.dense.in
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
 la2F = .true.
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
32 32 32 0 0 0
```

这份文件的 `outdir` 为 `./tmp`。因此本次实际生成的文件是 `tmp/al.a2Fsave`。第一次脚本把它误写成当前目录下的 `al.a2Fsave`，致密 SCF 已完成，随后的 `cp` 失败。应先读 SCF 末尾与文件位置，避免把脚本退出误判成电子自洽失败。

```console
maxwell@maxwell:~/al/epc-q4$ tail -10 al.dense.out
     Parallel routines
 
     PWSCF        :      8.06s CPU      9.34s WALL

 
   This run was terminated on:  22: 6:27  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

```console
maxwell@maxwell:~/al/epc-q4$ cp tmp/al.a2Fsave al.a2Fsave.k32
maxwell@maxwell:~/al/epc-q4$ cp tmp/al.save/data-file-schema.xml dense.data-file-schema.xml

```

保存致密网格文件后，第二次 SCF 使用下列输入。原胞、赝势、截断能、展宽和前缀均保持相同，电子网格换成 16³。保存在同一个 `tmp` 下的当前电荷密度随后供 ph.x 读取；先前另存的 `al.a2Fsave.k32` 用来核对致密网格数据没有被替换。

```console
maxwell@maxwell:~/al/epc-q4$ cat al.scf.in
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

接着是 ph.x 输入。这里 `el_ph_sigma=0.005` 表示双 δ 积分的电子展宽间距，配合 `el_ph_nsigma=10`，实际输出 0.005、0.010、…、0.050 Ry 十组数据。它与 SCF 中 `degauss=0.02` 的作用不同。

```console
maxwell@maxwell:~/al/epc-q4$ cat al.elph.in
&INPUTPH
 prefix = 'al'
 outdir = './tmp'
 fildyn = 'al.dyn'
 fildvscf = 'aldv'
 electron_phonon = 'interpolated'
 el_ph_sigma = 0.005
 el_ph_nsigma = 10
 amass(1) = 26.9815385
 tr2_ph = 1.0d-14
 ldisp = .true.
 nq1 = 4
 nq2 = 4
 nq3 = 4
/
```

`electron_phonon='interpolated'` 对应这次实跑的路线；`fildvscf` 保存势的一阶变化。完整计算共生成 8 个不可约 q 点，每个点有 3 个振动模式。

## 按真实脚本串行运行与检查

致密 SCF 已经正常结束后，实际提交了下面的继续运行脚本。脚本中的 `cmp` 没有输出且返回成功，才会继续到 ph.x；`set -e` 会在前面的命令失败时停止脚本。

```console
maxwell@maxwell:~/al/epc-q4$ cat continue.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-epc4
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
cp tmp/al.a2Fsave al.a2Fsave.k32
cp tmp/al.save/data-file-schema.xml dense.data-file-schema.xml
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cmp tmp/al.a2Fsave al.a2Fsave.k32
mpirun -np 8 <qe_bin>/ph.x -in al.elph.in > al.elph.out 2> al.elph.err
<qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err
<qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
```

```console
maxwell@maxwell:~/al/epc-q4$ sbatch continue.slurm
Submitted batch job 1970
```

队列里的任务消失只说明它不再处于排队或运行状态。运行期间可用 `squeue -j 1970` 查看调度状态，用 `tail -f al.elph.out` 看响应迭代；退出实时查看按 Ctrl+C，不会终止后台任务。结束后读取 ph.x 的末尾，并检查每个 q 点是否有频率、十组展宽和完整模式行。

```console
maxwell@maxwell:~/al/epc-q4$ tail -12 al.elph.out
     h_psi:calbec :      5.28s CPU      6.36s WALL (  859163 calls)
     s_psi_bgrp   :      1.64s CPU      1.96s WALL ( 1409957 calls)
 
 
     PHONON       :   6m 3.20s CPU   6m35.37s WALL

 
   This run was terminated on:  22:14:10  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

```console
maxwell@maxwell:~/al/epc-q4$ sha256sum tmp/al.a2Fsave al.a2Fsave.k32
2e2e5db92227e752d80ca7b1a0b86ee410c665b218d4ea534162ba4e92fdb3f8  tmp/al.a2Fsave
2e2e5db92227e752d80ca7b1a0b86ee410c665b218d4ea534162ba4e92fdb3f8  al.a2Fsave.k32
```

这两个散列一致，说明后续步骤使用的致密网格文件与保存下来的那一份相同。它只是文件身份检查；电子网格是否足够密，仍要改变网格计算比较。

## 两条谱函数后处理路线分别留下什么

脚本先执行 `q2r.x`，把完整 q 网格的力常数和 EPC 数据一起变换到实空间，再交给 `matdyn.x`。两份输入如下。

```console
maxwell@maxwell:~/al/epc-q4$ cat q2r.in
&INPUT
 fildyn='al.dyn'
 flfrc='al.fc'
 zasr='simple'
 la2F=.true.
/
```

```console
maxwell@maxwell:~/al/epc-q4$ cat matdyn-dos.in
&INPUT
 flfrc='al.fc'
 asr='simple'
 amass(1)=26.9815385
 la2F=.true.
 dos=.true.
 nk1=24
 nk2=24
 nk3=24
 ndos=400
 fldos='al.phdos.dat'
/
```

`matdyn.x` 的 24³ 是对已有实空间数据的积分网格，并没有增加真实计算的 DFPT q 点。它生成 `a2F.dos1` 到 `a2F.dos10`，编号依次对应十组电子展宽；同目录的 `lambda` 文件记录该路线的 λ 和对数平均频率。

这里 `nk1/nk2/nk3` 虽然名字带 k，在 `matdyn.x` 中却是声子 DOS 积分使用的 q 网格。增加它们可以检查后处理积分的离散误差，但无法补回原先 4³ DFPT 网格没有提供的力常数范围。`asr='crystal'` 处理平移声学求和规则，也不会自动修复电子声子矩阵元或证明材料没有虚频。

同样的 `la2F` 出现在不同程序里，要跟着程序名读：`pw.x` 负责保存致密电子本征值，`q2r.x` 处理配套 EPC 实空间数据，`matdyn.x` 才在这条插值路线中输出谱函数。仅在普通声子后处理中打开最后一个开关，并不能产生前面从未计算的耦合。三份程序输入与逐 q 文件必须属于同一次完整计算链。

```console
maxwell@maxwell:~/al/epc-q4$ head -8 a2F.dos4
 
 # Eliashberg function a2F (per both spin)
 #  frequencies in Rydberg  
 # DOS normalized to E in Rydberg: a2F_total, a2F(mode) 
 
       0.378477E-05    0.138515E-09    0.613987E-10    0.351279E-10    0.419882E-10
       0.113543E-04    0.373996E-08    0.165777E-08    0.948475E-09    0.113372E-08
       0.189239E-04    0.173147E-07    0.767484E-08    0.439111E-08    0.524872E-08
```

文件头直接写着 `frequencies in Rydberg`。第一列是 Ry，第二列是总谱函数，后面三列按模式编号分解；单原子原胞有三个模式，因此数据区共五列。文件最后还有 `lambda = ... Delta = ...` 一行，它不是数值数据行，读表时不能直接把整份文件强行当成五列数组。

```console
maxwell@maxwell:~/al/epc-q4$ tail -3 a2F.dos4
       0.301648E-02    0.281188E-02    0.000000E+00    0.000000E+00    0.281188E-02
       0.302405E-02    0.000000E+00    0.000000E+00    0.000000E+00    0.000000E+00
  lambda =  0.374096616223644         Delta =   7.569579561024077E-006
```

另一条路线是 `lambda.x`：直接读取这 8 个 q 点的 `elph.inp_lambda.*`，按星权重求和并在频率轴做 Gaussian 展宽。本页主图使用这条路线，文件名是 `alpha2F.dat`，频率单位为 THz。两个文件名很相似，单位和积分方式却不同，应分别保存与标注。

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.in
14.0 0.12 0
8
0.000000000 0.000000000 0.000000000 1.0
-0.176776700 0.176776700 -0.176776700 8.0
0.353553400 -0.353553400 0.353553400 4.0
0.000000000 0.353553400 0.000000000 6.0
0.530330100 -0.176776700 0.530330100 24.0
0.353553400 0.000000000 0.353553400 12.0
0.000000000 -0.707106800 0.000000000 3.0
-0.353553400 -0.707106800 0.000000000 6.0
elph_dir/elph.inp_lambda.1
elph_dir/elph.inp_lambda.2
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
0.10
```

第一行依次是频率上限 14 THz、频率展宽 0.12 THz 和 Gaussian 类型 0。第二行是不可约 q 点数；随后八行是 q 坐标及其星权重。坐标沿用 ph.x 输出的笛卡尔坐标、单位为 2π/alat；权重之和为 64，程序会归一化，不能给八个点都填 1。再往下的八行对应这八个点的文件，最后一行的 0.10 是用于公式估计 Tc 的 μ* 假设。

本次直接计算的最高模式为 9.936574 THz。14 THz 的上限还为频率展宽的尾部留出了空间。换材料时应先检查真实最高频率与高频尾部；沿用一个过小的上限，会使谱函数积分漏掉贡献，即使程序正常退出也不能接受。

```console
maxwell@maxwell:~/al/epc-q4$ <qe_bin>/lambda.x < lambda.in > lambda.out 2> lambda.err

```

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.dat
# degauss   lambda    int alpha2F  <log w>     N(Ef)
  0.005    0.430378    0.430442   355.877    2.518161
  0.010    0.371061    0.371121   344.606    2.624685
  0.015    0.370295    0.370356   343.420    2.647439
  0.020    0.374486    0.374547   343.741    2.646097
  0.025    0.374613    0.374674   343.537    2.643523
  0.030    0.373773    0.373835   342.831    2.643829
  0.035    0.373581    0.373643   342.006    2.645823
  0.040    0.374086    0.374148   341.243    2.648339
  0.045    0.375022    0.375085   340.631    2.650827
  0.050    0.376041    0.376104   340.145    2.653067
```

从左到右是电子展宽（Ry）、逐 q 点求和的 λ、对程序内部谱函数积分得到的 λ、ω_log（K），以及单自旋 DOS(EF)，后者单位是 states/spin/Ry/cell。0.020 Ry 这一行的前两种 λ 分别为 0.374486 和 0.374547，差约 0.000061；频率展宽与数值积分会造成小差别。

## 把图积分回输出里的 λ

```console
maxwell@maxwell:~/al/epc-q4$ head -5 alpha2F.dat
# E(THz)     0.005     0.010     0.015     0.020     0.025     0.030     0.035     0.040     0.045     0.050
  0.0000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0070   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0140   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0210   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
```

第一列后的十列依次对应文件头十组电子展宽。不要取第二列画图，却拿 0.020 Ry 那一行的 λ 做标题。下面的提取脚本检查 q 坐标、模式数、权重和十组展宽，然后用谱函数独立计算 `2∫α²F(ν)/ν dν`。零频点不参加除法，也没有对负数取绝对值。

```console
maxwell@maxwell:~/al/epc-q4$ ../.venv/bin/python analyse_epc.py > analysis.out
maxwell@maxwell:~/al/epc-q4$ cat analysis.out
8 irreducible q points; star weights sum to 64; 3 modes; 10 electronic widths; 240 mode records
80 q2r el-ph inputs; 10 real-space el-ph files; dense a2Fsave hash preserved
Maximum computed mode = 9.936574 THz; spectrum end = 14.000 THz
sigma_Ry  lambda_qsum  lambda_integral  omega_log_K  Tc_mu0.10_K
0.005     0.430378      0.430437       355.877      2.212103
0.010     0.371061      0.371118       344.606      0.915531
0.015     0.370295      0.370354       343.420      0.900166
0.020     0.374486      0.374545       343.741      0.969046
0.025     0.374613      0.374671       343.537      0.970575
0.030     0.373773      0.373833       342.831      0.954739
0.035     0.373581      0.373641       342.006      0.949300
0.040     0.374086      0.374146       341.243      0.955437
0.045     0.375022      0.375083       340.631      0.969102
0.050     0.376041      0.376101       340.145      0.984595
Native calculation completed; scientific convergence not established.
```

打印后的 α²F 只保留有限小数，0.020 Ry 一列独立积分得到 0.374545，与程序内部积分 0.374547 的差别很小。这个交叉核对用于发现列号、单位或截断范围错误，不能代替 k/q 网格收敛。

![fcc Al 的 α²F 及累计 λ](/Atlas/examples/al/figures/eliashberg-a2f.png)

上图能看到谱权重集中在哪些频率；下面的累计积分则直接显示这些频段对 λ 的贡献。由于被积函数带有 1/ν，相同的谱函数面积放在不同频率，对 λ 的影响也不一样。

![电子展宽下的 λ 与对数平均频率](/Atlas/examples/al/figures/epc-smearing.png)

0.005 Ry 的结果明显偏离更宽的几组。后面几组接近，只能说明在当前网格上对这一段展宽不太敏感；没有更密电子网格和真实 q 网格对照，不能据此宣布 λ 已收敛。图中也保留了 matdyn 路线的结果。这次 matdyn 在 0.005 Ry 的谱中还有 146 行负值，最小值为 −0.00554175；0.010 Ry 有 9 行微小负值。原文件保留这些数值，不取绝对值或截零；这些列需要继续检查实空间插值与 q 网格，不能作为已接受的非负谱使用。两条路线的数值积分与插值不同，尤其在较大展宽时差别可见，不能从其中各挑一个数拼成一组结果。

要重新画图，将 `epc-q4` 与绘图脚本放在同一个 Al 数据目录，安装 NumPy、Matplotlib，在该目录运行：

```bash
python plot_epc.py
```

原始输入、程序输出和独立检查脚本可以逐个查看：[al.dense.in](/Atlas/examples/al/epc-q4/al.dense.in), [al.dense.out](/Atlas/examples/al/epc-q4/al.dense.out), [al.scf.in](/Atlas/examples/al/epc-q4/al.scf.in), [al.scf.out](/Atlas/examples/al/epc-q4/al.scf.out), [al.elph.in](/Atlas/examples/al/epc-q4/al.elph.in), [al.elph.out](/Atlas/examples/al/epc-q4/al.elph.out), [continue.slurm](/Atlas/examples/al/epc-q4/continue.slurm), [q2r.in](/Atlas/examples/al/epc-q4/q2r.in), [q2r.out](/Atlas/examples/al/epc-q4/q2r.out), [matdyn-dos.in](/Atlas/examples/al/epc-q4/matdyn-dos.in), [matdyn-dos.out](/Atlas/examples/al/epc-q4/matdyn-dos.out), [lambda.in](/Atlas/examples/al/epc-q4/lambda.in), [lambda.out](/Atlas/examples/al/epc-q4/lambda.out), [lambda.dat](/Atlas/examples/al/epc-q4/lambda.dat), [alpha2F.dat](/Atlas/examples/al/epc-q4/alpha2F.dat), [analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py), [tc-scan.csv](/Atlas/examples/al/epc-q4/tc-scan.csv)。绘图代码为 [plot_epc.py](/Atlas/examples/al/plot_epc.py)。

下一步：到 [Allen–Dynes 公式](/Atlas/m/allen-dynes/qe/) 看 μ* 和输入 λ 怎样影响公式给出的 Tc；若要知道某个 q 点的哪个振动模式贡献较大，转到 [声子线宽](/Atlas/m/phonon-linewidth/qe/)。

```text
同结构致密 SCF + 响应 SCF → 完整 q 网格 EPC → 逐 q、逐模 λ/γ
                                             ├─ q2r → matdyn → a2F.dos*（Ry）
                                             └─ lambda.x → alpha2F.dat（THz）→ λ / ω_log
```
