[QE 双网格 EPC 流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html) · [ph.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [q2r.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [QE 电子声子系数及谱函数定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

<span id="double-grid-pwxall"></span>

## 从 pwxall、pwx 两套电子网格走到 Tc

这里把终端里常用的 `pwxall → pwx → ph.x` 路线接完整。`pwxall` 和 `pwx` 是输入文件与任务的命名，两次调用的程序都是 `pw.x`。在本页已经完成的 Al 算例中，对应真文件叫 `al.dense.in` 和 `al.scf.in`；后面的研究目录则直接使用 `pwxall.in` 和 `pwx.in`。

这条路线要分清三个网格：

| 网格 | 本例 Al 设置 | 在这一段计算中负责什么 |
|---|---|---|
| 致密电子 k 网格，`pwxall` | 32×32×32 | 保存较密的电子本征值、k 点与权重，用于费米面附近的积分 |
| 响应所用的电子 k 网格，`pwx` | 16×16×16 | 留下电荷密度、波函数与电子网格，供 `ph.x` 计算一阶响应和电声矩阵元 |
| 声子 q 网格 | 4×4×4 | 选择真正进行 DFPT 响应计算的声子波矢；本例对称性约化后有 8 个不可约 q |

`electron_phonon='interpolated'` 将响应电子网格上得到的电声矩阵元信息插值到致密电子网格，再结合致密网格的电子能量做费米面求和。加密第一行、第二行、第三行分别改变不同的数值近似，不能互相替代。输出中的 `Dense grid: ... FFT dimensions` 则是平面波变换用的实空间 FFT 网格，还要与这三行分开读。

官方流程允许直接进行致密 SCF，也允许先 SCF、再在致密网格做 NSCF。本例实际采用前一种。官方同时要求致密网格覆盖后续用到的 k 与 k+q，所有相关网格都不偏移、包含 Γ；这要由实际网格关系核对。[QE 原生插值 EPC 流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html)

<span id="dense-k-branches"></span>

### ph64 与 ph96 是两条致密网格对照分支

研究目录里的 `ph64` 和 `ph96` 指的是两种致密电子采样方案。每个目录内部都包含自己的 `pwxall → pwx → ph.x` 双电子网格链，响应电子网格与声子 q 网格保持相同，方便以后只比较致密电子采样的影响。

| 实际目录或算例 | pwxall 致密 k | pwx 响应 k | DFPT q | 现有证据到哪一步 |
|---|---|---|---|---|
| Al 完整教学链，QE 7.5 | 32×32×32 | 16×16×16 | 4×4×4 | 两次 SCF、8 个不可约 q、两条谱函数后处理及 `lambda.x` 均有完整输出 |
| SnSe₂/Sr₂N 的 `ph64`，QE 7.1 | 64×64×1 | 16×16×1 | 8×8×1 | 作业 18178、18179 完成两次 SCF；18180 的逐 q 响应仍未闭合，不能据此给该材料 Tc |
| SnSe₂/Sr₂N 的 `ph96` | 96×96×1 | 16×16×1 | 8×8×1 | 已有输入和脚本；当前目录没有对应计算输出或 `a2Fsave`，尚不能形成 64/96 的结果对照 |

这几套均使用 `0 0 0` 偏移。Al 的 32 可容纳 16 与 4 网格上的点；研究输入中的 64 和 96 都可容纳 16 与 8 网格上的点。这里满足的是所选规则网格的嵌套关系，结果对这些采样是否收敛仍需比较目标物理量。

每条分支应保留自己的致密网格文件身份。一次 `ph.x` 从该分支的 `outdir/prefix.a2Fsave` 读入一套致密数据；它不会把 `ph64` 的 64 网格和 `ph96` 的 96 网格同时当作输入。后续比较时，分别从两条完整链得到 λ、ωlog、谱函数及同一 μ* 下的 Tc，并保持同一电子展宽、结构、赝势和其余参数。当前研究记录只支持输入方案已经分开，尚不支持一张完成的 64/96 Tc 对照表。

### 先核对电子网格，再看文件有没有接对

下面是在已经完成的 Al 目录重新读到的原件。`al.dense.in` 就承担 `pwxall` 的角色：

```console
maxwell@maxwell:~/al/epc-q4$ grep -A1 K_POINTS al.dense.in al.scf.in
al.dense.in:K_POINTS automatic
al.dense.in-32 32 32 0 0 0
--
al.scf.in:K_POINTS automatic
al.scf.in-16 16 16 0 0 0
maxwell@maxwell:~/al/epc-q4$ grep -n la2F al.dense.in al.scf.in
al.dense.in:20: la2F = .true.
```

这两份输入只有致密电子步骤打开 `la2F`。它位于 `pw.x` 的 `&SYSTEM` 中，作用是写出专供这条 EPC 路线使用的电子信息；它没有计算声子，也没有在这里产生 λ 或 α²F。完整结构、截断能、带数与输入文件继续见[下面的两次 SCF 输入](/Atlas/m/epc/qe/#double-grid-al-inputs)。

```console
maxwell@maxwell:~/al/epc-q4$ head -1 tmp/al.a2Fsave
           6         897
```

这里的 6 是带数，897 是这次对称性约化后保存的 k 点数，不能把它读成一个 897×897×897 网格。这个文件随后还保存电子本征值、k 坐标、权重、`32 32 32` 网格以及对称信息。它是格式化文本，但并非只有三列的谱函数表；不要直接把它作为 α²F 曲线加载。

在本例 `prefix='al'`、`outdir='./tmp'` 的设置下，文件实际位于 `tmp/al.a2Fsave`。此前已经在致密 SCF 结束后，用普通复制保留了它和对应 XML：

```console
maxwell@maxwell:~/al/epc-q4$ cp tmp/al.a2Fsave al.a2Fsave.k32
maxwell@maxwell:~/al/epc-q4$ cp tmp/al.save/data-file-schema.xml dense.data-file-schema.xml
```

接下来的响应 SCF 会更新当前 `tmp/al.save`。粗网格输入没有开启 `la2F`，本次保存的致密文件未被改写；实际提交脚本在粗网格 SCF 与 `ph.x` 之间使用 `cmp` 检查，比较不相同就停止该脚本。完整执行记录见[运行与检查](/Atlas/m/epc/qe/#double-grid-al-run)。

现在重新读取两个 XML，可以同时看到被保留的致密父计算与当前响应父计算：

```console
maxwell@maxwell:~/al/epc-q4$ grep monkhorst_pack dense.data-file-schema.xml tmp/al.save/data-file-schema.xml
dense.data-file-schema.xml:      <monkhorst_pack nk1="32" nk2="32" nk3="32" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
dense.data-file-schema.xml:        <monkhorst_pack nk1="32" nk2="32" nk3="32" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
tmp/al.save/data-file-schema.xml:      <monkhorst_pack nk1="16" nk2="16" nk3="16" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
tmp/al.save/data-file-schema.xml:        <monkhorst_pack nk1="16" nk2="16" nk3="16" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
maxwell@maxwell:~/al/epc-q4$ cmp tmp/al.a2Fsave al.a2Fsave.k32 && sha256sum tmp/al.a2Fsave al.a2Fsave.k32
2e2e5db92227e752d80ca7b1a0b86ee410c665b218d4ea534162ba4e92fdb3f8  tmp/al.a2Fsave
2e2e5db92227e752d80ca7b1a0b86ee410c665b218d4ea534162ba4e92fdb3f8  al.a2Fsave.k32
```

下载包将响应 XML 单独保存为 [response.data-file-schema.xml](/Atlas/examples/al/epc-q4/response.data-file-schema.xml)，便于在不附带整个波函数目录的情况下核对。只读下载文件时，在 `al/epc-q4` 中使用 `grep monkhorst_pack dense.data-file-schema.xml response.data-file-schema.xml`；上面的会话仍保留实际计算目录中的原位置。

同一 XML 中输入段与输出段各记一行，所以这里每个网格出现两次。两个文件各自一致，当前 `.save` 为 16³，致密本征值文件仍与 32³ 备份逐字节相同。仅仅看见一个 `.a2Fsave` 文件名，不足以完成这项父链检查。

若在自己的独立计算副本中误把粗网格的 `la2F` 也打开，它可能重新写同名文件。应在进入 `ph.x` 前停下，先检查输入与备份的来源；确认同结构、同协议、同带数的致密备份后，才用 `cp al.a2Fsave.k32 tmp/al.a2Fsave` 恢复，并重新比较哈希。若没有可信的致密备份，需要重新完成那一步。本例哈希一直相同，没有发生这次恢复操作；正在运行的 `ph.x` 目录也不应被覆盖文件。

这里的行为已分别核对 QE 7.1 和 7.5 的版本源码：`punch` 仅在 `la2F` 为真时调用写出例程；`ph.x` 的 `elphsum` 从原先的 `outdir` 读取该文件，检查带数，并核对 q 是否落在致密网格中。两个版本在这条读写链上相符，计算文件仍应各自保持同一版本、同一物理设置。[QE 7.1 写出例程](https://github.com/QEF/q-e/blob/qe-7.1/PW/src/a2fmod.f90) · [QE 7.5 写出例程](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/a2fmod.f90) · [QE 7.5 致密积分读取](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/elphon.f90#L838-L943)

`ph.x` 的 `nk1/nk2/nk3` 是另一组参数：显式设置它们会让声子程序在所指定电子网格上重新进行非自洽步骤。它们不负责声明 `a2Fsave` 中的致密网格。本例未填写这些参数，沿用响应父计算的电子网格；致密网格由已保存文件读入。保持这两个入口清楚，才不会把 32³ 同时填入所有看起来像网格的字段。[ph.x 电子网格参数](https://www.quantum-espresso.org/Doc/INPUT_PH.html#nk1)

### 沿同一条链读到真正的 Tc 输出

完整 Al 链中的 `al.dyn0` 已列出 4³ 网格与 8 个不可约 q，`elph_dir/elph.inp_lambda.1` 至 `.8` 对应这些实际响应。后处理由此分成两条：

```text
pwxall：致密电子网格 → outdir/prefix.a2Fsave ───────┐
                                               │
pwx：响应电子网格 → outdir/prefix.save ──────────┤
                                               ↓
                     ph.x：独立 q 网格 + interpolated EPC
                             ├─ dyn 与 elph_dir/elph.* → q2r → matdyn → a2F.dos*
                             └─ elph.inp_lambda.* + q 权重 → lambda.x
                                                               ↓
                                                   alpha2F.dat / λ / ωlog / Tc
```

`q2r/matdyn` 的谱与 `lambda.x` 的直接逐 q 求和谱需要分开读取；后者并不先读入 `matdyn` 的输出。本例 `lambda.x` 已经实际结束，文件末尾是：

```console
maxwell@maxwell:~/al/epc-q4$ tail -11 lambda.out
lambda        omega_log          T_c
   0.43038       355.877              2.212
   0.37106       344.606              0.916
   0.37030       343.420              0.900
   0.37449       343.741              0.969
   0.37461       343.537              0.971
   0.37377       342.831              0.955
   0.37358       342.006              0.949
   0.37409       341.243              0.955
   0.37502       340.631              0.969
   0.37604       340.145              0.985
```

十行依次对应 0.005—0.050 Ry 的电子展宽。0.020 Ry 的第 4 行给出 λ≈0.37449、ωlog=343.741 K、μ*=0.10 下的原生公式结果 Tc=0.969 K；它来自这条已经完整跑通的 Al 双网格链。更密 k/q 网格的数值收敛尚未建立，因此这个温度用于复算与理解公式，不能直接当作材料预测。

如果要保留完整 α²F 的频率结构，继续求解温度依赖的能隙函数和 Tc，可以转到 [EPW / Eliashberg 方程](/Atlas/m/epw-eliashberg/qe/)。其中分别记录读取本页谱函数的各向同性求解，以及从 DFPT、Wannier 插值重新生成谱的路线。两者都需要完整的谱或矩阵元，不能只把 λ、ωlog 两个数写进 EPW 就还原出原来的频率信息。

继续沿这条路线：[Al 两次 SCF 的完整输入](/Atlas/m/epc/qe/#double-grid-al-inputs) → [原生执行脚本与运行检查](/Atlas/m/epc/qe/#double-grid-al-run) → [α²F、权重与谱积分](/Atlas/m/eliashberg-a2f/qe/) → [双网格结果如何进入 Tc 公式](/Atlas/m/allen-dynes/qe/#tc-from-double-grid)。研究材料的历史操作在[ph64/ph96 启动记录](/Atlas/m/epc/qe/#double-grid-research-record)中单独保留。

下面按实际文件重走 Al 这条链。QE 版本为 7.5，单原子原胞采用 LDA-PZ 与官方 `Al.pz-vbc.UPF`，晶格常数为 3.95606780081 Å。结构来源及优化过程见[晶胞优化](/Atlas/m/vc-relax/qe/)，逐个响应迭代见[DFPT 声子](/Atlas/m/phonon-dfpt/qe/)；这里接着看新增的致密电子步骤怎样与响应父计算配合。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al`，按正文读取和重绘。

<span id="double-grid-al-inputs"></span>

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

<span id="double-grid-al-run"></span>

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


## q 点、模式和文件要逐一对应

正常结束框之后，还要检查列表中每个 q 是否完成。单原子原胞有三个模式，4³ 网格经对称性处理后有八个不可约 q；八份文件不是 8³ 网格。

```console
maxwell@maxwell:~/al/epc-q4$ cat al.dyn0
   4   4   4
   8
   0.000000000000000E+00   0.000000000000000E+00   0.000000000000000E+00
  -0.176776695296637E+00   0.176776695296637E+00  -0.176776695296637E+00
   0.353553390593273E+00  -0.353553390593273E+00   0.353553390593273E+00
   0.000000000000000E+00   0.353553390593273E+00   0.000000000000000E+00
   0.530330085889910E+00  -0.176776695296637E+00   0.530330085889910E+00
   0.353553390593273E+00   0.000000000000000E+00   0.353553390593273E+00
   0.000000000000000E+00  -0.707106781186547E+00   0.000000000000000E+00
  -0.353553390593273E+00  -0.707106781186547E+00   0.000000000000000E+00
```
```console
maxwell@maxwell:~/al/epc-q4$ ls elph_dir/elph.inp_lambda.*
elph_dir/elph.inp_lambda.1
elph_dir/elph.inp_lambda.2
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
```
```console
maxwell@maxwell:~/al/epc-q4$ head -12 elph_dir/elph.inp_lambda.2
          -0.176777      0.176777     -0.176777    10     3
  0.119399E-05  0.119399E-05  0.474424E-05
     Gaussian Broadening:   0.005 Ry, ngauss=   0
     DOS =  2.518161 states/spin/Ry/Unit Cell at Ef=  8.373640 eV
     lambda(    1)=  0.0484   gamma=    1.50 GHz
     lambda(    2)=  0.0468   gamma=    1.45 GHz
     lambda(    3)=  0.2363   gamma=   29.17 GHz
     Gaussian Broadening:   0.010 Ry, ngauss=   0
     DOS =  2.624685 states/spin/Ry/Unit Cell at Ef=  8.377216 eV
     lambda(    1)=  0.0659   gamma=    2.13 GHz
     lambda(    2)=  0.0639   gamma=    2.07 GHz
     lambda(    3)=  0.2128   gamma=   27.38 GHz
```

首行前三个数是 q 坐标，`10 3` 是十组电子展宽和三个模式。第二行是三个模式的频率平方，使用 QE 内部的 Ry 频率标度，不能直接当作 THz。后面的每个展宽块先给 DOS(EF) 与费米能，再列各模 λ 和 γ。DOS 的单位为 states/spin/Ry/cell，γ 的单位是 GHz，均在原文写明。

同一个 q 要读完十个块，再换另一个 q。后处理中不能把不同展宽、质量或父 SCF 的文件混进一套输入。QE 7.5 的 `lambda.f90` 中，q 坐标一致性检查被注释掉了，正常退出不会代替核对；新增 `verify_tc_chain.py` 会比较 `lambda.in` 与每份文件首行的坐标，并从 ph.x 原文核验星权重。

Γ 点还需要单独读：

```console
maxwell@maxwell:~/al/epc-q4$ head -12 elph_dir/elph.inp_lambda.1
           0.000000      0.000000      0.000000    10     3
  0.713088E-09  0.713088E-09  0.713088E-09
     Gaussian Broadening:   0.005 Ry, ngauss=   0
     DOS =  2.518161 states/spin/Ry/Unit Cell at Ef=  8.373640 eV
     lambda(    1)=  0.0000   gamma=    0.00 GHz
     lambda(    2)=  0.0000   gamma=    0.00 GHz
     lambda(    3)=  0.0000   gamma=    0.00 GHz
     Gaussian Broadening:   0.010 Ry, ngauss=   0
     DOS =  2.624685 states/spin/Ry/Unit Cell at Ef=  8.377216 eV
     lambda(    1)=  0.0000   gamma=    0.01 GHz
     lambda(    2)=  0.0000   gamma=    0.01 GHz
     lambda(    3)=  0.0000   gamma=    0.01 GHz
```

这三个正频率残差约为 0.08785 THz，即约 2.93 cm⁻¹。本次 QE 7.5 `interpolated` 实现对低于 20 cm⁻¹ 的模式将 λ 置零，而 γ 仍然打印。因此不能把这里的零 λ 解读为已经证明 Γ 声学模没有物理耦合，也不能隐去这个低频处理后称为没有截断的积分。实质性虚频应先回到[虚频排查](/Atlas/m/imaginary-phonon/qe/)，不能取绝对值后继续计算 Tc。

## 完整逐 q 文件之后，后处理分两条路

`q2r.x → matdyn.x` 将动力学矩阵和 EPC 数据变到实空间，再插值。`lambda.x` 则直接读取 `elph.inp_lambda.*` 与 q 权重；它不读取 matdyn 的谱文件，所以两个谱不是同一个数组先后换了名字。

```text
32³ 致密 SCF ── al.a2Fsave ─┐
                            ├→ 16³ 响应 SCF → 4³ q 网格 ph.x
同结构 / 赝势 / 截断 / 展宽 ┘                      ↓
                                     8 q × 3 模 × 10 电子展宽
                                     ├→ q2r → matdyn → a2F.dos*（Ry）
                                     └→ lambda.x → alpha2F.dat（THz）
                                                        ↓
                                                λ、ωlog、明确 μ*
                                                        ↓
                                                公式 Tc + 数值验收
```

这条 Al 链已完成文件和算术核对，但还没有更密真实 k/q 网格与截断能的独立收敛证据。接着读 [α²F、λ 与频率矩](/Atlas/m/eliashberg-a2f/qe/)，然后到 [从 λ、ωlog 获取 Tc](/Atlas/m/allen-dynes/qe/)执行简式和完整 Allen–Dynes 的交叉计算。

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

上方官方输入手册目前为 QE 7.5；本机使用 QE 7.1，尚未找到与它匹配的官方输入手册来核实全部精确行为。这套 PAW、泛函与 EPC 的兼容性仍需在本地版本上验证，文件准备完成不等于这些检查已经通过。

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


**当前没有生成 `lambdax.in`。** 它要用本次计算实际得到的不可约 q 点、权重与逐 q 电声文件；频率积分上限也要覆盖实际声子范围。先复制另一材料的 q 列表和频率上限，会让后面的积分失去依据。

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

![SnSe₂/Sr₂N 64×64×1 网格 SCF 的电子迭代误差](/Atlas/figures/snse2-sr2n-k64-scf-accuracy.svg)

这张图可用[本机绘图脚本](/Atlas/examples/snse2-sr2n/ph64/plot_scf_accuracy.py)重新生成，数据来自[完整 pwxall.out](/Atlas/examples/snse2-sr2n/ph64/pwxall.out.txt)，配套[绘图样式脚本](/Atlas/examples/snse2-sr2n/ph64/atlas_plot_style.py)放在同一目录。读取时保留原始迭代行，不把图中的下降趋势代替最终电子收敛与参数收敛验收。


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

动力学矩阵齐全且核对通过后，才接 `q2r.x → matdyn.x`；电声文件、权重及频率积分范围也检查完后，再准备本材料的 `lambda.x` 输入。结构 BFGS、赝势与泛函适用性、k/q 网格和展宽收敛仍需分别验收，不能由 ph.x 正常结束一并代替。本次只提交 ph.x，后处理和 ph96 尚未启动。
<!-- ph64-phonon-session-end -->


</details>

下一步：[谱函数与积分](/Atlas/m/eliashberg-a2f/qe/) → [Tc 获取方法](/Atlas/m/allen-dynes/qe/)。
