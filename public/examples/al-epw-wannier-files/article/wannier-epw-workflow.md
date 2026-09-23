<span id="wannier-epw-tc"></span>

## 从完整 k 网格到 EPW 自己生成的谱

EPW 的完整计算链需要波函数、声子位移模式和自洽势的一阶响应。只有一张 α²F(ω) 表时，可以研究给定谱下的 Eliashberg 方程；要计算这张谱本身，还需要把粗网格上的电子结构和电子–声子矩阵元变换到 Wannier 表象，再插值到积分网格。本节使用 fcc Al，把这条链的输入、原生输出和质量检查放在同一份计算记录中。

需要先熟悉 [SCF](/Atlas/m/scf/qe/)、[NSCF](/Atlas/m/nscf/qe/)、[DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 和 [Wannier90](/Atlas/m/wannier90/qe/) 的文件关系。已有 α²F 表、只想求解温度依赖时，可以跳到[读取外部谱的 Eliashberg 计算](#external-spectrum-tc)。[原生双网格 EPC](/Atlas/m/epc/qe/#double-grid-pwxall) 与这里共享声子父链；两种程序的积分网格、展宽和插值步骤分别记录，数值不能仅凭材料名称互相替换。

实跑程序为 QE 7.5、EPW 6.0。官方的 [EPW 插值教程](https://docs.epw-code.org/tutorials/tutorial_01/index.html) 和 [超导教程](https://docs.epw-code.org/tutorials/tutorial_04/index.html) 标明这组版本。在线[输入参数页](https://docs.epw-code.org/Inputs/Inputs.html)目前标为 EPW 6.1；本例的精确输入还核对了本机 6.0 源码和原生输出。

### 先核对被继承的物理模型

Al 原胞有一个原子，沿用原先优化得到的晶格常数 3.95606780081072 Å。交换关联为 LDA-PZ，赝势为非相对论模守恒 `Al.pz-vbc.UPF`，波函数和电荷密度截断分别为 40、160 Ry；无自旋极化、SOC、Hubbard 或额外色散项。SCF 使用 6 条能带、Marzari–Vanderbilt 展宽 0.02 Ry、`conv_thr=1.0d-12`。这些数值界定当前教学实例，没有针对 λ 或 Tc 完成联合收敛测试。

赝势来自 [QE 公共下载页](https://pseudopotentials.quantum-espresso.org/upf_files/Al.pz-vbc.UPF)，SHA-256 为：

```text
4eab06b63f87f07ede2d5a193e6d993a09107167fd6b8647afa807342501d6e5
```

原声子父链是响应 SCF 16×16×16、DFPT q 网格 4×4×4，共 8 个不可约 q 点。它之前还执行了供 `ph.x` 双网格 EPC 使用的 32×32×32 电子计算。EPW 沿用这些 DFPT 势响应，并重新计算自己的电子矩阵元和细网格积分；此前 `lambda.x` 的 α²F 不是本节 EPW 插值的输入。

### 收集 dyn、dvscf 和 patterns

本次先核对 `al.dyn0` 中的 `4 4 4` 与 8 个不可约 q 点，再逐个确认 `al.dyn1` 到 `al.dyn8`、`patterns.1.xml` 到 `patterns.8.xml` 及 dvscf 文件。8 份 dvscf 均为 663552 字节，复制前后逐一比较 SHA-256。文件大小相同只是一个完整性检查，还需同时匹配赝势、晶胞、FFT 网格、prefix 和声子模式。

父计算使用 `fildvscf='aldv'`，因此原生文件名是 `al.aldv1`。EPW 读取的整理后名称为：

```text
phonon-save/
  al.dyn_q1 ... al.dyn_q8
  al.dvscf_q1 ... al.dvscf_q8
  al.phsave/
    control_ph.xml
    patterns.1.xml ... patterns.8.xml
    ...
  ifc.q2r
```

Γ 点的响应在 `tmp/_ph0/al.aldv1`，其余在 `tmp/_ph0/al.q_N/al.aldv1`。`ifc.q2r` 是同一套 q4 数据经 `q2r.x`、`zasr='crystal'` 产生的 `al.fc` 副本。本次没有直接在父目录运行 EPW 自带的 `pp.py`：所安装脚本的某些分支还会删除声子目录中的波函数。下载包中的收集脚本只复制所需文件，保留原计算树。

### NSCF 必须提供完整均匀电子网格

响应 SCF 的 145 个不可约 k 点不能直接充当 Wannier 网格。新 NSCF 从那份 SCF 的 `data-file-schema.xml`、`charge-density.dat` 和赝势副本启动，显式列出完整的 Γ 中心网格。网格点为 `(i/N,j/N,k/N)`，各点权重为 `1/N³`，粗 k 网格与 q4 网格相容。

原胞和前述参数保持一致，NSCF 的关键输入为：

```fortran
&CONTROL
 calculation = 'nscf'
 prefix = 'al'
 pseudo_dir = './pseudo'
 outdir = './tmp'
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
Al 0 0 0
CELL_PARAMETERS angstrom
-1.97803390040536 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.97803390040536 1.97803390040536 0.00000000000000
K_POINTS crystal
1728
```

紧随其后的是完整的 1728 行 k 点，完整文件位于下载包。最后这组 12×12×12 NSCF 的原生输出为：

```text
number of k points=  1728
PWSCF        :      9.73s CPU     10.14s WALL
JOB DONE.
```

记录同时检查了退出码、单一版本与结束标记、分开的标准错误文件以及 XML 内的 k 点数量。它说明这一 NSCF 执行结束，不意味着 k 网格已满足 Tc 的收敛要求。

### 把局域化与粗网格 EPC 分为两次执行

本次已安装的 Wannier 库含 MPI 集体通信，而 EPW 6.0 在 `meta_ionode` 分支调用库模式。8 进程的第一轮在解纠缠首轮输出前等待，保留为停止记录。相同输入改成 1 进程后，Wannier 阶段正常推进。这里按程序支持的方式先以 `elph=.false.` 完成局域化，再令 `wannierize=.false.` 读取已有 `al.ukk`，用 8 进程计算粗网格电子–声子矩阵元。不需要改动全局安装。

局域化输入中的投影是设计的初始猜测，中心和展宽必须读原生 `al.wout`，不能拿输入投影充当结果：

```fortran
&INPUTEPW
 prefix = 'al'
 amass(1) = 26.9815385
 outdir = './tmp'
 dvscf_dir = '../../phonon-save'
 elph = .false.
 epbread = .false.
 epbwrite = .false.
 epwread = .false.
 epwwrite = .true.
 nbndsub = 4
 wannierize = .true.
 num_iter = 1000
 dis_win_min = -4.0
 dis_win_max = 26.0
 dis_froz_min = -4.0
 dis_froz_max = 13.5
 proj(1) = 'Al:sp3'
 wdata(11) = 'dis_num_iter = 5000'
 nk1 = 12
 nk2 = 12
 nk3 = 12
 nq1 = 4
 nq2 = 4
 nq3 = 4
 nkf1 = 1
 nkf2 = 1
 nkf3 = 1
 nqf1 = 1
 nqf2 = 1
 nqf3 = 1
/
```

完整输入还给出 Γ–X–W–L–Γ–K 路径、`bands_plot`、`write_hr` 和 `use_ws_distance` 等输出控制。`nbndsub=4` 是将 6 条 Bloch 能带构造为 4 个 Wannier 函数。冻结窗上限 13.5 eV 来自实际本征值检查：本次粗网格第 5 条能带最低为 14.179760 eV，每个 k 点在冻结窗中至多包含 4 个态。能窗中的能量沿用本次 QE 本征值零点，不能换一种赝势后照抄数值。

局域化完成后，把同一份 NSCF save 树及原生 `al.ukk`、`al.bvec`、`al.mmn` 及 `al.win` 复制到新的粗 EPC 执行目录，修改下面三项：

```fortran
elph = .true.
wannierize = .false.
epbwrite = .true.
```

这里不能漏掉 `al.bvec` 和 `al.mmn`：本次拆分阶段的第一次执行确实在 `vmebloch2wan` 报错停止，补齐同一 Wannier 阶段的原生文件后，在新目录读取已完成的 `al.epb*` 继续。

`epwread` 仍为 `.false.`，因为此时还需要读取 DFPT 响应来构造粗网格耦合。完成后，`al.epb*` 是粗 Bloch 表象矩阵元；`tmp/al.epmatwp`、`al.ukk`、`crystal.fmt`、`epwdata.fmt`、`dmedata.fmt`、`vmedata.fmt`、`wigner.fmt` 组成后续插值所需的原生文件组。

### 先比较能带，再检查实空间衰减

小展宽和局域化迭代停止，均不能替代能带检查。本次取 Wannier90 原生 `al_band.kpt` 中的 166 个路径点，让 `pw.x` 在同一份 SCF 势上直接计算，并与 `al_band.dat` 逐点比较。每个 k 点按能量升序配对前 4 个本征值；该检查比较能谱，不跨交叉点追踪轨道身份。两边统一减去响应 SCF 输出的 8.4122 eV，没有单独对齐每轮的费米能，也没有拟合或平移曲线。

初始 4×4×4、冻结窗上限 10 eV 的结果，在 `|E_QE−EF|≤1 eV` 的 47 个态上 RMS 误差为 0.634477 eV、最大误差为 1.524481 eV。这会明显影响后续 0.1 eV 展宽积分。8×8×8、同一能窗降到 RMS 0.126236 eV，但仍有 0.548917 eV 的局部误差。两次解纠缠也都到达 1000 次上限，所以保留其警告，继续检查更宽冻结窗和更密电子粗网格。

程序还输出 `decay.H`、`decay.epmate` 和 `decay.epmatp`。它们分别记录电子哈密顿量、沿电子实空间矢量及沿声子实空间矢量的耦合衰减。读这些文件时应同时看距离、绝对量和尾部相对幅度；仅仅出现文件名，不能证明所选超胞范围已足够。最终比较数值和衰减摘要见后文的本次结果记录。

### 细网格插值生成 α²F

细网格阶段使用 `epwread=.true.` 读取上述 Wannier 文件组，`wannierize=.false.` 避免重新局域化。`a2f_iso=.true.` 在插值过程中形成各向同性谱，随后可交给各向同性 Eliashberg 求解。当前 EPW 的电子展宽 `degaussw` 以 eV 为单位，声子展宽 `degaussq` 以 meV 为单位；前面的 QE `degauss=0.02` 使用 Ry，三者不能写成一个没有单位的“展宽”。

```fortran
elph = .true.
epwread = .true.
epwwrite = .false.
wannierize = .false.
nbndsub = 4
lifc = .true.
asr_typ = 'crystal'
fsthick = 1.0
degaussw = 0.1
degaussq = 0.5
a2f_iso = .true.
liso = .true.
mp_mesh_k = .true.
```

还需显式给出电子粗网格 `nk1..3=12`、声子粗网格 `nq1..3=4` 以及本轮细网格 `nkf1..3`、`nqf1..3`。这里把 `fsthick=1.0` 作为积分中保留费米能附近态的窗口控制，不把它当作 Wannier 冻结窗。谱文件 `al.a2f` 前三列为 ω（meV）、α²F(ω) 和累计 λ(ω)；脚本读取数值行，保留文件尾部的电子展宽、Fermi 窗口、DOS 与耦合总和，不把尾部说明误读成数据。

要检查临界温度，先在已形成的谱上运行 `tc_linear` 并找出本征值跨越 1 的温度括区，再单独检查低温非线性方程的迭代。一次 `epw.x` 正常结束仍可能包含 `Convergence was not reached in nsiter`；这种情况下可以报告已形成的谱，不能称该温度的能隙求解收敛。谱积分定义可接着看 [Eliashberg 谱](/Atlas/m/eliashberg-a2f/qe/)，近似 Tc 公式见 [Allen–Dynes](/Atlas/m/allen-dynes/qe/#tc-from-double-grid)。

### 重跑与输出核对

下载包提供完整输入、纯文本原生输出、比较 CSV 和提取脚本，不打包赝势正文、波函数、dvscf 或二进制 Wannier 矩阵。要从头重跑，应先用包内 SCF/DFPT 输入产生声子父链；已有同一父链时，运行只复制文件的收集脚本，再继续 NSCF。

下面是下载包工作目录中的重跑顺序。先按实际机器修改启动程序路径和 MPI 数；`vi` 是重跑时检查配置的入口，不是必须采用的编辑器。

```bash
cp inputs/al.nscf-k12.in 01-nscf/al.nscf.in
vi 01-nscf/al.nscf.in
cat 01-nscf/al.nscf.in
cd 01-nscf
mpirun -np 8 pw.x -nk 8 -in al.nscf.in > al.nscf.out 2> al.nscf.err
tail -20 al.nscf.out
cd ../02-wannier
mpirun -np 1 epw.x -nk 1 -in epw1.in > epw1.out 2> epw1.err
cd ../03-coarse
mpirun -np 8 epw.x -nk 8 -in epw-coarse.in > epw-coarse.out 2> epw-coarse.err
cd ../04-fine
mpirun -np 8 epw.x -nk 8 -in epw2.in > epw2.out 2> epw2.err
```

每一步的前序复制由下载包脚本完成；不能只建空目录就执行以上命令。原始记录保留每次执行的独立目录、输入哈希、stdout、stderr、调度记录和失败状态。计算规范检查器对 NSCF 的科学接受链及 EPW 高阶功能不提供自动通过结论，本例另列人工输入/父链核对与原生执行证据。λ 和 Tc 的数值收敛及物理有效性仍需单独检查。
