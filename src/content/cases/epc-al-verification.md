# Al 双网格 EPC：两条独立链的执行证据

Al32³与48³各自执行致密SCF、16³响应SCF、q4³的8个不可约点与后处理。两条链共享比较协议，使用各自的outdir与致密电子数据；q2r/matdyn插值谱和lambda.x直接逐q谱分别保存。下文是历史终端记录，提交号和RUNNING快照对应当次执行，不作为新的运行指令。

完整结果在0.005–0.050 Ry十档电子σ上无孤立交点、无重合区间。最近的0.050 Ry处，Tc32=0.984588 K、Tc48=0.975366 K，差0.009222 K；固定q4³与响应16³的比较不认证材料Tc收敛。普通跟做与物理解释读[EPC正文](/Atlas/m/epc/qe/)、[谱积分](/Atlas/m/eliashberg-a2f/qe/)和[Tc比较](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)。两套原件及复算源码在[双分支包](/Atlas/examples/supercon-al-tc-files.tar.gz)。

<details>
<summary>展开两套Al原始输入、终端操作和结束检查</summary>

<span id="double-grid-pwxall"></span>

## 两条 pwxall 流程算完后，对照 Tc 曲线

本页用单原子 fcc Al 介绍 QE 的双网格电子–声子耦合计算。先分清致密电子网格、响应电子网格和声子 q 网格各自的任务，再完成两条独立的 `pwxall → pwx → phx → … → lambdax` 计算链。第二条只改变致密 k 网格。将两份输出按相同电子展宽 σ 配对，画出 Tc₃₂(σ)、Tc₄₈(σ) 和差值曲线，再逐段求出采样范围内的全部交点；没有交点时也保留这一结果。随后结合 λ、ωlog 和交点附近的差值，检查网格与展宽的稳定性。

`pwxall`、`pwx`、`phx`、`lambdax` 是这里的文件或任务命名，调用的程序分别是 `pw.x`、`pw.x`、`ph.x`、`lambda.x`。本页 Al 算例中的前两份真文件叫 `al.dense.in` 和 `al.scf.in`；研究目录则直接使用 `pwxall.in` 和 `pwx.in`。

这里用单原子 fcc Al 实际走两遍。第一条路径的致密网格为 32³，第二条改为 48³；响应电子网格仍是 16³，q 网格仍是 4³。两条链分别保留输入、输出和自己的临时目录：

```text
epc-q4：    pwxall 32³ → pwx 16³ → phx q=4³ → … → lambdax → Tc₃₂(σ)
                                                                  ↓
                                                   同一 σ 下叠图、求交点
                                                                  ↑
epc-q4-k48：pwxall 48³ → pwx 16³ → phx q=4³ → … → lambdax → Tc₄₈(σ)
```

每条路径内部又有三个网格需要分清：

| 网格 | 本例 Al 设置 | 在这一段计算中负责什么 |
|---|---|---|
| 致密电子 k 网格，`pwxall` | 第一条 32×32×32；第二条 48×48×48 | 保存较密的电子本征值、k 点与权重，用于费米面附近的积分 |
| 响应所用的电子 k 网格，`pwx` | 16×16×16 | 留下电荷密度、波函数与电子网格，供 `ph.x` 计算一阶响应和电声矩阵元 |
| 声子 q 网格 | 4×4×4 | 选择真正进行 DFPT 响应计算的声子波矢；本例对称性约化后有 8 个不可约 q |

`electron_phonon='interpolated'` 将响应电子网格上得到的电声矩阵元信息插值到致密电子网格，再结合致密网格的电子能量做费米面求和。加密第一行、第二行、第三行分别改变不同的数值近似，不能互相替代。输出中的 `Dense grid: ... FFT dimensions` 则是平面波变换用的实空间 FFT 网格，还要与这三行分开读。

官方流程允许直接进行致密 SCF，也允许先 SCF、再在致密网格做 NSCF。本例实际采用前一种。官方同时要求致密网格覆盖后续用到的 k 与 k+q，所有相关网格都不偏移、包含 Γ；这要由实际网格关系核对。[QE 原生插值 EPC 流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html)

<span id="dense-k-branches"></span>

### 第一条完成后，换 pwxall 网格再走一遍

第二条路径只改变 `al.dense.in` 末尾的 `K_POINTS`。`al.scf.in`、`al.elph.in`、`q2r.in`、`matdyn-dos.in`、`lambda.in` 五份输入逐字相同，分别在自己的目录运行。因而两边采用相同结构、赝势、截断能、电子与声子响应阈值、q 权重、频率积分范围、频率展宽和 μ*。

| 路径 | pwxall 致密 k | pwx 响应 k | DFPT q | 比较时使用的曲线 |
|---|---|---|---|---|
| `epc-q4` | 32×32×32 | 16×16×16 | 4×4×4 | `lambda.out` 中十组展宽的 Tc₃₂(σ) |
| `epc-q4-k48` | 48×48×48 | 16×16×16 | 4×4×4 | 新计算的 `lambda.out` 中十组展宽的 Tc₄₈(σ) |

两套均使用 `0 0 0` 偏移。按每个倒格矢方向检查整数倍关系：32=2×16、48=3×16，而 16=4×4。`pwxall` 网格是 `pwx` 网格的整数倍，`pwx` 网格又是 q 网格的整数倍；32 与 48 彼此不需要互为整数倍。这种不偏移的嵌套设置满足本路线对 k、k+q 点覆盖的要求。

新目录沿用同一组结构、赝势、截断能、电子与响应收敛阈值，并重新生成自己那份致密网格 `a2Fsave`。响应 SCF、逐 q 文件和 `lambda.x` 输入输出也留在各自目录。准备新分支时可以用 `cp` 复制已经核验的输入与提交脚本，用 `vi` 改 `pwxall` 网格；不要把第一条路径的结果文件直接充作第二条的计算结果，也不要让两条路径共用可写的 `outdir`。

两次 `lambda.x` 必须采用相同的 μ*、q 权重、频率积分范围和频率展宽；两次 `ph.x` 的电子展宽序列也要一致。比较图横轴是这组 **EPC 双 δ 积分展宽 σ**，纵轴才是 Tc。它不同于 SCF 的 `degauss`，也不同于 `lambda.in` 中谱函数的频率展宽。

两条曲线相交，只说明在该展宽处得到相同 Tc；λ 与 ωlog 的变化还可能相互抵消。应同时检查谱形、两个谱矩和交点附近的差值。更密 k 网格在固定展宽下趋于稳定，并在减小展宽时仍保持一致，才是收敛检查的方向；q 网格改变后也需重新比较。参见 [QE 开发者对 k 网格与展宽的说明](https://lists.quantum-espresso.org/pipermail/users/2003-September/000602.html)。

第二个目录中的实际 `cp`、`vi`、Slurm 提交与输出检查见[48³ 分支的操作记录](/Atlas/m/epc/qe/#dense-k48-run)。两份输出怎样配对、两条曲线的求交结果与差值，接着看 [Tc 页的实际叠图与交点表](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)。两条链的原生文件、求交脚本和绘图脚本放在[同一个下载包](/Atlas/examples/supercon-al-tc-files.tar.gz)。

研究材料使用的 `ph64`、`ph96` 目录沿用相同组织方式，网格关系为 64=4×16、96=6×16、16=2×8；其启动操作保留在[后半页](/Atlas/m/epc/qe/#double-grid-research-record)。下面 Al 的数值只对应本例的结构与计算设置。

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

十行依次对应 0.005—0.050 Ry 的电子展宽。0.020 Ry 的第 4 行给出 λ≈0.37449、ωlog=343.741 K、μ*=0.10 下的原生公式结果 Tc=0.969 K；它是第一条曲线上的一个采样点。完整对照还会读入 48³ 分支的十行，逐个展宽求差，再定位两条折线的交点。

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

32³ 分支最初的作业 1969 已完成致密 SCF，随后在备份文件时停下了。错误文件里是：

```console
maxwell@maxwell:~/al/epc-q4$ cat _err.1969.log
cp: 对 'al.a2Fsave' 调用 stat 失败: 没有那个文件或目录
```

输入设置了 `outdir='./tmp'`，实际文件在 `tmp/al.a2Fsave`，原脚本却从工作目录复制 `al.a2Fsave`。`set -e` 使脚本在这条 `cp` 失败后退出，后面的响应 SCF 尚未开始。保留已经正常结束的致密结果，将复制路径改正后，用下面的 `continue.slurm` 接着运行；这条错误保留在上面的终端记录中；下载包内的 `continue.slurm` 使用修正后的复制路径。

脚本中的 `cmp` 没有输出且返回成功，才会继续到 ph.x；`set -e` 会在前面的命令失败时停止脚本。第二个 48³ 分支的[完整脚本](/Atlas/m/epc/qe/#dense-k48-run)从第一次 SCF 开始，已经使用正确的 `tmp/al.a2Fsave` 路径。

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

### AI 后处理提示词：装配两条 EPC 输出链

> 读取 Al k32/、k48/ 两个独立分支的 SCF/PH 输入输出、lambda.in/out 与八个 elph.inp_lambda 文件。核对材料结构、赝势、截断能、响应 k/q 网格、电子展宽与 μ*，并逐分支记录正常结束/电子响应收敛/缺文件状态。由 lambda.in 获取 q 坐标、顺序和星权重，检查权重和64；解析每个 q 的三条模式、十档 σ、频率平方、λ、γ、DOS(EF) 和单位，输出240条模式记录及按 σ 加权求和表。频率和 EPC 数据分别使用本分支原件，跨网格频率差是比较输出，不要求逐位相同。重建 λ、ωlog、Tc 并与原生打印精度核对，再交给 Tc 配对程序。保存完整源码、CSV、JSON 和输入哈希，不启动新计算；其他材料必须建立各自源文件清单，不能混入 Al 或独立 Sc₂C 的核验结论。

[完整逐模解析源码 analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py) · [完整双分支重建源码 rebuild_tc.py](/Atlas/examples/supercon-al-tc/rebuild_tc.py) · [配对源码 compare_tc.py](/Atlas/examples/supercon-al-tc/compare_tc.py)。

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

<a id="dense-k48-run"></a>

## 再算一条 48³ 致密电子网格，把两条计算独立走完

前一条 Al 计算使用 32³ 致密电子网格、16³ 响应电子网格和 4³ 声子 q 网格。现在把致密电子网格加到 48³，其余设置保持相同，再从头运行两次 `pw.x`、`ph.x` 和后处理。这样得到的第二条 Tc(σ) 曲线，才有自己完整的输入与输出。这里的 Al 是双网格流程演示；这些 3D 网格不能直接当作其他材料的已收敛参数。

| 分支目录 | 致密电子网格 | 响应电子网格 | 声子 q 网格 |
| --- | --- | --- | --- |
| `epc-q4` | 32 × 32 × 32 | 16 × 16 × 16 | 4 × 4 × 4 |
| `epc-q4-k48` | 48 × 48 × 48 | 16 × 16 × 16 | 4 × 4 × 4 |

[两条分支的输入、原生输出与比较脚本](/Atlas/examples/supercon-al-tc-files.tar.gz)放在同一个文件包内，解压后分别位于 `supercon-al-tc/k32/` 和 `supercon-al-tc/k48/`。后面的终端记录保留运行时目录名 `epc-q4` 与 `epc-q4-k48`；包内的短目录名用于整理这两套已经产生的文件。

两套电子网格和 q 网格均不作偏移。48/16 = 3、32/16 = 2，16/4 = 4；在本例的共同倒格基矢下，这保证所用响应网格及其 k + q 点能嵌入对应的致密网格。32 和 48 彼此不必是整数倍，分别满足同一条响应网格的包含关系即可。这里比较的是致密电子积分网格，q 网格保持 4³；对 q 网格的收敛判断还要另做加密。

先在原计算旁边新建目录，只复制六份输入。进入 `vi` 后，将 `al.dense.in` 最后一行的三个 32 改成 48，保存退出。SCF 的输入结构和基本收敛项可接着看[固定结构 SCF](/Atlas/m/scf/qe/)，这里保留这次对照真正改动的部分。

```console
maxwell@maxwell:<工作目录>/al$ mkdir epc-q4-k48
maxwell@maxwell:<工作目录>/al$ cd epc-q4-k48
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ pwd
<工作目录>/al/epc-q4-k48
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cp ../epc-q4/al.dense.in ../epc-q4/al.scf.in ../epc-q4/al.elph.in ../epc-q4/q2r.in ../epc-q4/matdyn-dos.in ../epc-q4/lambda.in .
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ vi al.dense.in
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ diff -u ../epc-q4/al.dense.in al.dense.in
--- ../epc-q4/al.dense.in       2026-09-22 22:04:18.628451799 +0800
+++ al.dense.in 2026-09-23 17:51:17.296318296 +0800
@@ -31,4 +31,4 @@
 0.00000000000000 1.97803390040536 1.97803390040536
 -1.97803390040536 1.97803390040536 0.00000000000000
 K_POINTS automatic
-32 32 32 0 0 0
+48 48 48 0 0 0
```

`diff` 只显示这一行变化。两条分支的 `al.scf.in`、`al.elph.in`、`q2r.in`、`matdyn-dos.in` 和 `lambda.in` 经 SHA-256 比对逐份相同；Al 的晶胞、赝势、`ecutwfc=40 Ry`、`ecutrho=160 Ry`、`nbnd=6`、SCF 的 `degauss=0.02 Ry` 均没有随分支改变。

两个 `pw.x` 输入仍写 `prefix='al'`、`outdir='./tmp'`，但相对路径现在落在各自的工作目录内。`epc-q4-k48/tmp` 由这次运行重新产生，没有从 32³ 分支复制 `.save`、动力学矩阵或 EPC 输出。致密计算里的 `la2F=.true.` 会保存供后续积分使用的致密网格电子数据；第二次 16³ SCF 不打开这个选项，而是重新写出响应计算需要的电荷密度和波函数。

## 在一个作业里依次运行，并在两次 SCF 之间留下核对文件

原分支的续算脚本可以作为编辑起点，但这次要从致密 SCF 开始，并把 `lambda.x` 放到末尾。实际修改后的脚本如下；执行时把 `<qe_bin>` 换成本机 QE 7.5 可执行程序目录。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cp ../epc-q4/continue.slurm run.slurm
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ vi run.slurm
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ bash -n run.slurm
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-k48
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
mpirun -np 8 <qe_bin>/pw.x -in al.dense.in > al.dense.out 2> al.dense.err
grep -q 'JOB DONE.' al.dense.out
grep -q 'convergence has been achieved' al.dense.out
cp tmp/al.a2Fsave al.a2Fsave.k48
cp tmp/al.save/data-file-schema.xml dense.data-file-schema.xml
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
grep -q 'JOB DONE.' al.scf.out
grep -q 'convergence has been achieved' al.scf.out
cp tmp/al.save/data-file-schema.xml response.data-file-schema.xml
cmp tmp/al.a2Fsave al.a2Fsave.k48
sha256sum tmp/al.a2Fsave al.a2Fsave.k48 > a2Fsave-after-response.sha256
mpirun -np 8 <qe_bin>/ph.x -in al.elph.in > al.elph.out 2> al.elph.err
grep -q 'JOB DONE.' al.elph.out
<qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err
grep -q 'JOB DONE.' q2r.out
<qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
grep -q 'JOB DONE.' matdyn-dos.out
<qe_bin>/lambda.x < lambda.in > lambda.out 2> lambda.err
date -u > finished.txt
```

作业申请 8 个 MPI 进程，每个进程 1 个 CPU，`mpirun -np 8` 与申请相同；`OMP_NUM_THREADS=1` 避免 MPI 进程再各自展开 OpenMP 线程。这里载入的是 Maxwell 实际使用的 `/opt/intel/oneapi/setvars.sh`。`q2r.x`、`matdyn.x` 和 `lambda.x` 按这份脚本串行执行。

`set -e` 让程序返回错误、SCF 未出现收敛行或文件比较失败时停下来。第一次 SCF 后立刻复制 `.a2Fsave` 和 XML，第二次 SCF 后再复制一份 XML；这样即使同名 `tmp/al.save` 已被 16³ 结果更新，仍能看清两次计算各用了什么网格。`cmp` 无输出表示两份文件相同，紧接着的 SHA-256 则把这个核对留在磁盘上。这些检查先保证流程没有误接，EPC 数值是否随网格和展宽稳定还要在结果出来后比较。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ sbatch run.slurm
Submitted batch job 2016
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ squeue -o '%.10i %.18j %.8T %.10M %.6C %R'
     JOBID               NAME    STATE       TIME   CPUS NODELIST(REASON)
      2016       atlas-al-k48  RUNNING       0:00      8 maxwell
```

提交后先看队列，再看当前程序自己的输出。`_out.2016.log` 记录的是作业外层输出；这份脚本已将三个主要程序分别重定向到 `al.dense.out`、`al.scf.out` 和 `al.elph.out`，因此声子进度要到 `al.elph.out` 里找。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ grep -E 'Program PWSCF|number of k points|estimated scf accuracy|convergence has|PWSCF        |JOB DONE' al.dense.out al.scf.out | tail -n 24
al.dense.out:     Program PWSCF v.7.5 starts on 23Sep2026 at 17:52:26 
al.dense.out:     number of k points=  2769  Marzari-Vanderbilt smearing, width (Ry)=  0.0200
al.dense.out:     estimated scf accuracy    <       0.00575324 Ry
al.dense.out:     estimated scf accuracy    <       0.00044397 Ry
al.dense.out:     estimated scf accuracy    <       0.00000031 Ry
al.dense.out:     estimated scf accuracy    <          5.9E-09 Ry
al.dense.out:     estimated scf accuracy    <          9.0E-12 Ry
al.dense.out:     estimated scf accuracy    <          1.7E-12 Ry
al.dense.out:     estimated scf accuracy    <          1.4E-15 Ry
al.dense.out:     convergence has been achieved in   7 iterations
al.dense.out:     PWSCF        :     24.60s CPU     28.39s WALL
al.dense.out:   JOB DONE.
al.scf.out:     Program PWSCF v.7.5 starts on 23Sep2026 at 17:52:56 
al.scf.out:     number of k points=   145  Marzari-Vanderbilt smearing, width (Ry)=  0.0200
al.scf.out:     estimated scf accuracy    <       0.00572737 Ry
al.scf.out:     estimated scf accuracy    <       0.00044172 Ry
al.scf.out:     estimated scf accuracy    <       0.00000031 Ry
al.scf.out:     estimated scf accuracy    <          5.7E-09 Ry
al.scf.out:     estimated scf accuracy    <          8.5E-12 Ry
al.scf.out:     estimated scf accuracy    <          1.8E-12 Ry
al.scf.out:     estimated scf accuracy    <          1.5E-15 Ry
al.scf.out:     convergence has been achieved in   7 iterations
al.scf.out:     PWSCF        :      1.31s CPU      1.53s WALL
al.scf.out:   JOB DONE.
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ wc -c al.dense.err al.scf.err al.elph.err _err.2016.log
0 al.dense.err
0 al.scf.err
0 al.elph.err
0 _err.2016.log
0 总计
```

两次 SCF 都用了 7 轮迭代，最后的估计误差分别为 1.4 × 10⁻¹⁵ Ry 和 1.5 × 10⁻¹⁵ Ry，已小于本次 `conv_thr=1.0d-12`，并各自正常结束。2769 和 145 是程序实际处理的不可约 k 点数；它们不是网格每个方向的大小。更直接的网格证据在保存的 XML 中。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ head -1 tmp/al.a2Fsave
           6        2769
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ grep monkhorst_pack dense.data-file-schema.xml response.data-file-schema.xml
dense.data-file-schema.xml:      <monkhorst_pack nk1="48" nk2="48" nk3="48" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
dense.data-file-schema.xml:        <monkhorst_pack nk1="48" nk2="48" nk3="48" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
response.data-file-schema.xml:      <monkhorst_pack nk1="16" nk2="16" nk3="16" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
response.data-file-schema.xml:        <monkhorst_pack nk1="16" nk2="16" nk3="16" k1="0" k2="0" k3="0">Monkhorst-Pack</monkhorst_pack>
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cat a2Fsave-after-response.sha256
0c62b320aaa91c431ed9b15ab1bf57f5d33bef1f01813158e7af4a2152b7a1d3  tmp/al.a2Fsave
0c62b320aaa91c431ed9b15ab1bf57f5d33bef1f01813158e7af4a2152b7a1d3  al.a2Fsave.k48
```

`.a2Fsave` 首行的 6 和 2769 分别对应这次保存的能带数和致密计算的 k 点数。它存的是电子本征值等中间数据，不能当作 α²F(ω) 谱读取。两份 XML 分别保留了 48³ 与 16³ 的网格，所有偏移标志都为 0；第二次 SCF 后，工作文件与 `al.a2Fsave.k48` 的 SHA-256 仍完全相同。到这里，响应计算可以读取自己的 16³ `.save`，同时使用本分支的 48³ 致密电子数据。

## 声子开始输出频率后，继续看 EPC 是否仍在运行

本次 `al.elph.in` 与 32³ 分支相同：`electron_phonon='interpolated'` 选择这里的双网格 EPC 路线，`fildvscf='aldv'` 保存一阶自洽势，`tr2_ph=1.0d-14` 控制响应自洽迭代的停止阈值。`nq1=nq2=nq3=4` 对应完整 4³ q 网格，在这份 Al 晶胞的对称性下需要计算 8 个不可约 q 点。

`el_ph_sigma=0.005`、`el_ph_nsigma=10` 扫描的是电子双 δ 积分展宽，从 0.005 到 0.050 Ry，共十档。它与 SCF 中决定金属占据的 `degauss=0.02 Ry` 作用不同；横向比较两条分支时，要把同一档 EPC 展宽配在一起。

计算时使用的四份输入依次如下。前三份是各自程序的 namelist，最后一份 `lambda.in` 按固定行序读取，不能给它加上 `&INPUT`。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cat al.elph.in q2r.in matdyn-dos.in lambda.in
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
&INPUT
 fildyn='al.dyn'
 flfrc='al.fc'
 zasr='simple'
 la2F=.true.
/
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

`q2r.in` 保留了 `zasr='simple'`，它约束的是 Born 有效电荷；本次金属 Al 没有计算这项响应，不能把该参数当作声子频率已修正的证据。[q2r.x 的参数说明](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html)中区分了这个对象。后续 `matdyn-dos.in` 的 `asr='simple'` 才对力常数施加平移声学求和规则；原始 `al.elph.out` 中的 Γ 点频率仍应保留，不能拿修正后的零频替换原始输出来声称数值已经收敛。

`matdyn-dos.in` 中的 24³ 是声子插值积分网格，`ndos=400` 是频率取样点数，它们控制后处理的分辨率，没有新增 DFPT q 点。`la2F=.true.` 还开启了相应 EPC 量的插值，其定义见 [matdyn.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)。

`lambda.in` 第一行的 `14.0 0.12 0` 分别是 α²F(ω) 的频率上限 14 THz、频率轴高斯展宽 0.12 THz，以及普通高斯类型。0.12 THz 与前面 0.005 Ry 的电子双 δ 展宽不是同一个量。接下来的 `8` 表示读八个 q 点；权重之和是 1 + 8 + 4 + 6 + 24 + 12 + 3 + 6 = 64，程序按总和归一化。八个文件名的顺序必须与这八行 q 及权重对应；最后一行 `0.10` 才是两条分支共用的库仑赝势 μ*。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ grep -E 'Calculation of q|irreducible representations|Representation.*modes' al.elph.out | tail -n 8
     Saving dvscf to file. Distribute only q points, not irreducible representations.
     Calculation of q =    0.0000000   0.0000000   0.0000000
     There are    1 irreducible representations
     Representation     1      3 modes -  To be done
     Representation #   1 modes #   1   2   3
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ tail -n 12 al.elph.out

 **************************************************************************
     freq (    1) =       0.087851 [THz] =       2.930394 [cm-1]
     freq (    2) =       0.087851 [THz] =       2.930394 [cm-1]
     freq (    3) =       0.087851 [THz] =       2.930394 [cm-1]
 **************************************************************************

     Mode symmetry, O_h (m-3m)  point group:

     freq (   1-   3) =          2.9  [cm-1]   --> T_1u G_15  G_4- I  
     Electron-phonon interaction  ...

maxwell@maxwell:<工作目录>/al/epc-q4-k48$ squeue -j 2016 -o '%.10i %.18j %.8T %.10M %.6C %R'
     JOBID               NAME    STATE       TIME   CPUS NODELIST(REASON)
      2016       atlas-al-k48  RUNNING       3:45      8 maxwell
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ grep -E 'Calculation of q|JOB DONE' al.elph.out
     Calculation of q =    0.0000000   0.0000000   0.0000000
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ ls -l lambda.out finished.txt 2>/dev/null
```

这一段监控中，Γ 点已经打印了三条频率，输出却仍停在 `Electron-phonon interaction ...`。Al 原胞只有一个原子，所以每个 q 点有三个振动模；这里 Γ 点的约 2.93 cm⁻¹ 是施加后处理声学求和规则前的原始结果，不能拿它替代全 q 网格的检查。频率先出现并不意味着该 q 点的 EPC 展宽扫描已经写完，队列此时也仍显示 `RUNNING`。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ scontrol show job 2016 | grep -E 'JobState=|RunTime=|NumCPUs='
   JobState=RUNNING Reason=None Dependency=(null)
   RunTime=00:07:53 TimeLimit=01:00:00 TimeMin=N/A
   NumNodes=1 NumCPUs=8 NumTasks=8 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ grep -E 'Calculation of q|JOB DONE' al.elph.out
     Calculation of q =    0.0000000   0.0000000   0.0000000
     Calculation of q =   -0.1767767   0.1767767  -0.1767767
```

继续查看时，`Calculation of q` 已从一行增加到两行，说明程序进入了第二个不可约 q 点。运行中可以反复使用上面的 `squeue`、`grep` 和 `tail`：前者回答作业是否还在调度器中，后两者回答它现在在算哪一个 q、响应或 EPC 的哪一段。一个 q 的 `Convergence has been achieved` 只说明对应响应迭代达到阈值；必须等预定的八个 q 及其十档 EPC 数据都齐全，才能对这条分支做最终汇总。

脚本随后会用 `q2r.x` 将动力学矩阵转为实空间力常数，再由 `matdyn.x` 进行声子插值与相应后处理。`lambda.x` 则按 `lambda.in` 中的八个文件名和 q 权重，直接读取 `elph_dir/elph.inp_lambda.*`；虽然脚本把它放在 `matdyn.x` 之后，它并不读取 `matdyn.x` 的输出。

## 八个 q 点结束后，把每一段输出接起来

这次作业最终运行了 38 分 02 秒，其中 `ph.x` 的墙钟时间为 37 分 02.49 秒。先用 `scontrol` 回读退出状态，下面截取它的状态与耗时部分，再检查各阶段的错误输出和结束标记。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ scontrol show job 2016
JobId=2016 JobName=atlas-al-k48
   UserId=maxwell(1000) GroupId=maxwell(1000) MCS_label=N/A
   Priority=1 Nice=0 Account=(null) QOS=(null)
   JobState=COMPLETED Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:38:02 TimeLimit=01:00:00 TimeMin=N/A
```

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ wc -c al.dense.err al.scf.err al.elph.err q2r.err matdyn-dos.err lambda.err _err.2016.log
0 al.dense.err
0 al.scf.err
0 al.elph.err
0 q2r.err
0 matdyn-dos.err
0 lambda.err
0 _err.2016.log
0 总计
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ grep 'JOB DONE' al.dense.out al.scf.out al.elph.out q2r.out matdyn-dos.out
al.dense.out:   JOB DONE.
al.scf.out:   JOB DONE.
al.elph.out:   JOB DONE.
q2r.out:   JOB DONE.
matdyn-dos.out:   JOB DONE.
```

调度器返回 `COMPLETED`、`ExitCode=0:0`，两次 SCF、`ph.x`、`q2r.x`、`matdyn.x` 都打印了结束标记，七份错误输出为空。这与前面只看到队列仍在运行、部分 q 点已打印频率的状态不同；此时才能检查完整的逐 q 数据。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ head -n 1 elph_dir/elph.inp_lambda.*
==> elph_dir/elph.inp_lambda.1 <==
           0.000000      0.000000      0.000000    10     3

==> elph_dir/elph.inp_lambda.2 <==
          -0.176777      0.176777     -0.176777    10     3

==> elph_dir/elph.inp_lambda.3 <==
           0.353553     -0.353553      0.353553    10     3

==> elph_dir/elph.inp_lambda.4 <==
           0.000000      0.353553      0.000000    10     3

==> elph_dir/elph.inp_lambda.5 <==
           0.530330     -0.176777      0.530330    10     3

==> elph_dir/elph.inp_lambda.6 <==
           0.353553      0.000000      0.353553    10     3

==> elph_dir/elph.inp_lambda.7 <==
           0.000000     -0.707107      0.000000    10     3

==> elph_dir/elph.inp_lambda.8 <==
          -0.353553     -0.707107      0.000000    10     3
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cat al.dyn0
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

每个 EPC 文件首行最后的 `10 3` 表示十档展宽、三个振动模。八个文件的前三列坐标与 `lambda.in` 中八行 q 的顺序一致；表头只打印六位小数，核对时应容许末位舍入。`al.dyn0` 还给出 4 × 4 × 4 网格和八个不可约 q 点，两者对应同一批计算。

这一步不能只检查文件名。QE 7.5 的 `lambda.x` 中，输入 q 与文件头 q 的一致性检查被注释掉了；文件排列错了，程序仍可能把一个 q 的结果乘上另一个 q 的权重。随例包提供的 `rebuild_tc.py` 会逐个核对坐标、十档展宽和模数，并从这些原始记录重建 λ、ωlog 与 Tc。本次八个星权为 1、8、4、6、24、12、3、6，合计覆盖完整网格的 64 个点。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cmp tmp/al.a2Fsave al.a2Fsave.k48
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ sha256sum tmp/al.a2Fsave al.a2Fsave.k48
0c62b320aaa91c431ed9b15ab1bf57f5d33bef1f01813158e7af4a2152b7a1d3  tmp/al.a2Fsave
0c62b320aaa91c431ed9b15ab1bf57f5d33bef1f01813158e7af4a2152b7a1d3  al.a2Fsave.k48
```

计算结束后再比较一次，致密电子文件的 SHA-256 仍与 SCF 后保存的备份一致，确认后续程序没有把它换成另一套网格的数据。`q2r.out` 同时报告 `q-space grid ok, #points = 64` 和 `fft-check success`，并完成了十档展宽的相应变换。

`matdyn-dos.out` 的末尾保留了下面这条提示及正常结束记录：

```text
Message from routine matdyn:
     Z* not found in file al.fc, TO-LO splitting at q=0 will be absent!
 
     MATDYN       :     25.81s CPU     25.93s WALL

 
   This run was terminated on:  18:30:28  23Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

这里的 `Z* not found` 与本例金属 Al 未计算 Born 有效电荷一致，不是八个 q 点中断的标志。仍要检查后处理生成的谱：这次 48³ 分支的 `a2F.dos1`、`a2F.dos2`、`a2F.dos3` 总谱分别出现 145、88、5 行负值，说明这些低展宽下的插值谱需要进一步检查。原文件保留；下面的 Tc 对照使用 `lambda.x` 从逐 q EPC 文件构成的另一套谱与输出表，不能把这两套结果交替使用。

最后直接读本分支的 `lambda.out`。前十行逐档列出参数，后十行给出对应 Tc；两部分的顺序相同。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cat lambda.out
     lambda = 0.412244 (   0.412312 )  <log w>=  339.816 K  N(Ef)=  2.777246 at degauss= 0.005
     lambda = 0.370989 (   0.371052 )  <log w>=  338.534 K  N(Ef)=  2.728336 at degauss= 0.010
     lambda = 0.369520 (   0.369582 )  <log w>=  341.471 K  N(Ef)=  2.702967 at degauss= 0.015
     lambda = 0.367505 (   0.367565 )  <log w>=  342.622 K  N(Ef)=  2.674883 at degauss= 0.020
     lambda = 0.367122 (   0.367183 )  <log w>=  342.598 K  N(Ef)=  2.658974 at degauss= 0.025
     lambda = 0.368450 (   0.368511 )  <log w>=  342.109 K  N(Ef)=  2.652038 at degauss= 0.030
     lambda = 0.370333 (   0.370394 )  <log w>=  341.514 K  N(Ef)=  2.649843 at degauss= 0.035
     lambda = 0.372280 (   0.372342 )  <log w>=  340.931 K  N(Ef)=  2.650081 at degauss= 0.040
     lambda = 0.374000 (   0.374063 )  <log w>=  340.427 K  N(Ef)=  2.651487 at degauss= 0.045
     lambda = 0.375505 (   0.375568 )  <log w>=  340.031 K  N(Ef)=  2.653286 at degauss= 0.050
lambda        omega_log          T_c
   0.41224       339.816              1.687
   0.37099       338.534              0.898
   0.36952       341.471              0.883
   0.36750       342.622              0.854
   0.36712       342.598              0.849
   0.36845       342.109              0.868
   0.37033       341.514              0.896
   0.37228       340.931              0.925
   0.37400       340.427              0.952
   0.37550       340.031              0.975
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ cat finished.txt
2026年 09月 23日 星期三 10:30:28 UTC
```

以 σ = 0.020 Ry 这一行为例，括号外的 λ = 0.367505 来自 q 加权求和，括号内的 0.367565 来自 α²F(ω) 积分。二者接近是谱离散化的一项核对，不是致密 k 网格已经收敛的证明。`<log w>=342.622 K` 是以温度单位表示的 ωlog；后表的 `T_c=0.854 K` 使用固定 μ* = 0.10 和此版本的近似公式计算。

这版 `lambda.x` 不打印 `JOB DONE.`，所以最后一段要结合正常退出状态、十档有限数值以及逐 q 重建结果判断；`finished.txt` 只说明脚本确实走到了末尾。现在第二条原生表已经齐全，48³ 分支的十个 Tc 都低于 32³ 分支在同一 σ 下的值。在已采样的 0.005–0.050 Ry 范围内，按相邻点作分段直线连接，两条曲线没有交点。

32³ 与 48³ 两条完整分支在采样展宽范围内没有交点。Al 64³ 分支的 `pwxall` 与 16³ 响应 SCF 已收敛并正常结束；接续的 q=4³ 声子/EPC 作业因 walltime 到限被取消，仅留下六个 `elph.inp_lambda.*`，没有 `lambda.out`、`lambda.dat` 或 `alpha2F.dat`，尚不能加入 Tc 曲线。32³/48³ 的配对图、差值和实际求交结果见[双网格 Tc 对照](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)。

```text
epc-q4/al.dense.in  32³ → 本目录 16³ SCF → 本目录 q4³ ph.x → 本目录逐 q EPC → lambda.x
                                                                                  ↘
                                                                                   两条 Tc(σ) 配对比较
                                                                                  ↗
epc-q4-k48/al.dense.in 48³ → 本目录 16³ SCF → 本目录 q4³ ph.x → 本目录逐 q EPC → lambda.x
```


</details>

<span id="epc-literature-aesthetics"></span>

## 用原文图理解这些文件支持的分析

[Ba₂N，PRB105,165101](https://doi.org/10.1103/PhysRevB.105.165101)图3、6把线宽编码色散、投影PHDOS、α²F及振动模式接起来；图3(a)/6(a)红点大小编码γ，原图不是连续宽度色带。图7显示未应变材料的各向异性能隙分布随温度闭合，它与Al等方外部谱求解是不同数据路线。

[EPC页](/Atlas/m/epc/qe/#ba2n-mode-analysis)解释图3/6模式追踪，[线宽页](/Atlas/m/phonon-linewidth/qe/#ba2n-linewidth-analysis)区分γ和λ，[EPW页](/Atlas/m/epw-eliashberg/qe/#material-anisotropic-route)解释图7所需的逐带逐k数据。这里保留原图号和文献链接，不以文献材料数值填入Al输出。
