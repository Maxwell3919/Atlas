[DFPT 声子](/Atlas/m/phonon-dfpt/qe/) · [金属 SCF](/Atlas/m/scf/qe/) · [QE 原生双网格流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html)

<span id="double-grid-pwxall"></span>

## 从电子态和晶格振动走到配对谱

界面形成或施加应变后，费米能附近的电子态会重新分布，振动频率和原子位移也会改变。电子–声子耦合计算把这两部分接起来：一个波矢 q、分支 ν 的振动造成自洽势变化，电子从 (n,k) 散射到 (m,k+q)，矩阵元 g 量出这次扰动与电子态的相互作用。声子频率决定振动能量；电子–声子线宽 γ 则同时包含矩阵元与费米面附近可参与散射的电子态。逐模 λ 将 γ 按频率和 DOS(EF) 归一化，整张布里渊区的贡献再汇成 α²F、总 λ 和对数平均频率 ωlog。[QE 系数定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)给出这些量的关系。

因此，看到异质结 DOS(EF) 增大时，还需要问哪些振动与新增电子态耦合、耦合出现在什么 q、谱权重是否转移到低频。线宽最大、逐模 λ 最大和 α²F 峰最高不一定落在同一个模式上。后面用一个真实 fcc Al 算例学习完整文件链，再把读法接到二维材料的模式分析。

Al 原胞只有一个原子、三条声学分支，适合认清网格和程序输出；它没有异质结的层分辨光学振动。实跑环境是 QE 7.5、LDA-PZ、Al.pz-vbc.UPF，晶格常数 3.95606780081 Å，来源见[晶胞优化](/Atlas/m/vc-relax/qe/)。下面展示的提交号和输出属于已完成的 Al 记录。

## 两套 pwxall 网格，各自完成一条链

`pwxall`、`pwx`、`phx`、`lambdax` 是文件或任务命名，分别调用 pw.x、pw.x、ph.x、lambda.x。这里的两次 pw.x 输入实际叫 al.dense.in、al.scf.in。第一条采用32³致密网格，第二条采用48³；它们有各自的临时目录、逐 q 响应和后处理结果。

```text
k32：pwxall 32³ → pwx 16³ → phx q4³ → q2r/matdyn → lambdax → Tc32(σ)
k48：pwxall 48³ → pwx 16³ → phx q4³ → q2r/matdyn → lambdax → Tc48(σ)
```

| 网格 | 真实设置 | 改变它会影响什么 |
|---|---|---|
| 致密电子 k，pwxall | 32³或48³ | 费米面双δ积分的电子本征值、k点和权重 |
| 响应电子 k，pwx | 16³ | 自洽响应与电子–声子矩阵元 |
| 真实 DFPT q | 4³，8个不可约q | 实际计算的扰动波矢与力常数信息 |

`electron_phonon='interpolated'` 将响应网格上的耦合信息插值到致密电子网格做积分。三个网格承担不同工作；输出的实空间 FFT 网格也要另读。所有网格均包含Γ且不偏移：32=2×16、48=3×16、16=4×4，致密网格分别覆盖响应的k及k+q。32与48彼此不必互为整数倍。

<span id="dense-k-branches"></span>

两条链只改变 al.dense.in 的K_POINTS，其余五份输入相同。SCF占据展宽 degauss=0.02 Ry、PH双δ电子展宽σ=0.005–0.050 Ry和谱频率展宽0.12 THz是三个独立设置；后面的Tc曲线横轴是第二个。q权重、频率范围、展宽核函数和μ*=0.10也保持一致。

[双分支完整包](/Atlas/examples/supercon-al-tc-files.tar.gz)中k32/、k48/分别保存两条链。[Tc页](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)按同一σ比较它们；实际结果在采样范围内无交点。

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
两次 SCF 的文件同时存在，是这条双网格链的关键。致密步骤提供积分所需的电子能量，响应步骤提供计算扰动的父态；备份只是保留前者的身份，并没有增加一次声子响应。

| 这一支留下的文件 | 后面由谁读取 | 其中保留的信息 |
|---|---|---|
| `tmp/al.a2Fsave`，另存为 `al.a2Fsave.k32` | `ph.x` 的致密 EPC 积分 | 致密网格的本征值、k 坐标、权重及对称信息 |
| 当前 `tmp/al.save` | `ph.x` 的响应步骤 | 16³ 父计算的结构、电荷密度和波函数等 |
| `dense.data-file-schema.xml` | 人或检查脚本 | 备份时的致密父计算身份；不会作为谱函数输入 |

因此，在 XML 里看到当前网格已变成 16³，同时致密文件仍来自 32³，是这次运行的正常衔接。反过来，只有 `al.a2Fsave.k32` 的文件名、没有对应输入/XML 或文件比较，就无法确认它来自哪一次计算。[Al 存档中的两份 XML](/Atlas/cases/epc-al-verification/#double-grid-pwxall)保留了这项直接核对；后面的完整脚本也在进入响应前比较当前致密文件和备份。


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
这里一阶势与最后的逐模 λ 又是两层信息。一阶势描述电子如何受到振动扰动；矩阵元还要与电子波函数配合，再经费米面求和，才得到线宽和 λ。`elph.inp_lambda.*` 已将电子态信息汇总到每个 q、模式和 σ；它适合给 `lambda.x` 求和，却不能再倒推出逐带、逐 k 的散射矩阵。要进入 Wannier–EPW 路线，需要其匹配的 dyn、patterns、dvscf 和完整电子态文件，具体交接见[原生 EPW 链](/Atlas/m/epw-eliashberg/qe/#wannier-epw-tc)。保存一个名为 dvscf 的文件也不代替这套父计算关系。


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

这份续算脚本执行到 `matdyn.x`。接着在 32³ 分支运行 `lambda.x`，实际输入、命令和输出见 [α²F 页的 lambda.x 记录](/Atlas/m/eliashberg-a2f/qe/#h-输入之后-程序实际留下了什么)。

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

后续响应计算读取的是上一步保存的致密网格 `al.a2Fsave.k32`，文件接续保持同一父结构、密度和电子设置。复制与文件内容相同不等于电子网格已经收敛；仍要用不同网格比较目标物理量。


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
完整性也有不同计数：每个 q 的频率是同一套三个模式，十个 σ 重新计算的是电子积分，所以八个 q 共给出 24 个模式频率、240 条 λ/γ 记录。不能把重复出现在十档展宽中的频率当成 240 个不同声子模。核对文件数之后，再核对每块的三行、σ 的顺序和 DOS(EF)，才能把后面十行总 λ 与 Tc 逐行配对；八份非空文件本身还不足以完成这一步。


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

`diff` 只显示这一行变化。两条分支的 `al.scf.in`、`al.elph.in`、`q2r.in`、`matdyn-dos.in` 和 `lambda.in` 在原位记录中逐份相同；Al 的晶胞、赝势、`ecutwfc=40 Ry`、`ecutrho=160 Ry`、`nbnd=6`、SCF 的 `degauss=0.02 Ry` 均没有随分支改变。

两个 `pw.x` 输入仍写 `prefix='al'`、`outdir='./tmp'`，但相对路径现在落在各自的工作目录内。`epc-q4-k48/tmp` 由这次运行重新产生，没有从 32³ 分支复制 `.save`、动力学矩阵或 EPC 输出。致密计算里的 `la2F=.true.` 会保存供后续积分使用的致密网格电子数据；第二次 16³ SCF 不打开这个选项，而是重新写出响应计算需要的电荷密度和波函数。

## 在一个作业里依次运行，并在两次 SCF 之间留下核对文件

原分支的续算脚本可以作为编辑起点，但这次要从致密 SCF 开始，并把 `lambda.x` 放到末尾。下面从实际脚本提取计算次序与停止检查，供读者编辑；完整原脚本见 [run.slurm](/Atlas/examples/supercon-al-tc/k48/run.slurm) 和[两分支计算包](/Atlas/examples/supercon-al-tc-files.tar.gz)。执行时把 `<qe_bin>` 换成本机 QE 7.5 可执行程序目录。

```bash
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

`set -e` 让程序返回错误、SCF 未出现收敛行或文件比较失败时停下来。第一次 SCF 后立刻复制 `.a2Fsave` 和 XML，第二次 SCF 后再复制一份 XML；这样即使同名 `tmp/al.save` 已被 16³ 结果更新，仍能看清两次计算各用了什么网格。`cmp` 无输出表示两份文件相同。这些检查先保证流程没有误接，EPC 数值是否随网格和展宽稳定还要在结果出来后比较。

```console
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ sbatch run.slurm
Submitted batch job 2016
maxwell@maxwell:<工作目录>/al/epc-q4-k48$ squeue -o '%.10i %.18j %.8T %.10M %.6C %R'
     JOBID               NAME    STATE       TIME   CPUS NODELIST(REASON)
      2016       atlas-al-k48  RUNNING       0:00      8 maxwell
```

两次 SCF 的 XML 分别保存 48³ 与 16³ 网格；第二次 SCF 后 `.a2Fsave` 与本分支保存的备份相同。作业 2016 最终返回 `COMPLETED`、`ExitCode=0:0`；两次 SCF 和八个 q 点响应正常结束。完整监控、逐 q 文件头及结束检查见 [48³ 会话](/Atlas/cases/epc-al-verification/#dense-k48-run)。

## 后处理输入与两条输出路线

`q2r.x → matdyn.x` 用力常数与 EPC 数据做实空间变换、插值；`lambda.x` 直接读取逐 q 文件与星权重，并不读取 `matdyn` 的谱。后处理输入如下，两条分支逐字相同。

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

`q2r` 的 `zasr` 作用于 Born 有效电荷；力常数的平移声学求和规则由 `matdyn` 的 `asr` 处理。这里金属 Al 未计算 Born 有效电荷，输出的 `Z* not found` 与此一致。`matdyn` 的 24³ 是插值积分网格，400 是频率取样点数。48³ 分支的 `a2F.dos1/2/3` 分别有 145、88、5 行负总谱值，原件保留在附件；下面的 Tc 使用直接逐 q 求和的 `lambda.x` 路线。

`lambda.in` 的 `14.0 0.12 0` 指 14 THz 上限、0.12 THz 频率展宽和普通高斯。八行 q 必须与八个文件头逐个配对，星权重 `1,8,4,6,24,12,3,6` 合计 64；末行 `0.10` 是 μ*。它们与 `ph.x` 扫描的 0.005–0.050 Ry 电子展宽属于不同参数。

## 沿输出追到模式，再比较 Tc

0.020 Ry时，32³链得到λ=0.374486、ωlog=343.741 K、Tc=0.969 K；48³链得到λ=0.367505、ωlog=342.622 K、Tc=0.854 K。两条完整输出的十档σ都可按相同位置配对，Tc32−Tc48均为正，分段直线求交为0个交点、0个重合区间。最近的0.050 Ry处，重建Tc分别为0.984588、0.975366 K，差0.009222 K。曲线、全部表和完整求交源码集中在[Tc比较](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)，这里接着关心差异来自哪些振动。

单个elph文件里每行的λ只是该q、该模式的贡献，必须按星权重汇总。把这些贡献放到频率轴上得到α²F，再积分2α²F/ω，才得到总λ。高对称路径能定位耦合热点，却不能替代全q网格的积分。程序对Γ低频的处理、谱上限和电子展宽都沿这条链传递到Tc；两条曲线恰好相等时，也需要确认谱形与频率矩没有互相补偿。

<span id="ba2n-mode-analysis"></span>

## Ba₂N 怎样把谱峰追到原子振动

<figure>
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig3.png" alt="Ba2N论文Fig.3原图：声子色散红点线宽、原子PHDOS、a2F与Ba位移模式" />
<figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，原文第 3 页 Fig. 3(a–d)：未应变 Ba₂N 的声子色散、原子 PHDOS、α²F 与 Γ 附近约 55 cm⁻¹ 光学模。红点大小正比于线宽 γ；位移箭头表示原子运动幅度。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文原文</a>。</figcaption>
</figure>

[Qiu等，PRB105,165101](https://doi.org/10.1103/PhysRevB.105.165101)图3把未应变Ba₂N的色散、投影PHDOS、α²F和振动模式并列。图3(a)的红点大小正比于γ；约55 cm⁻¹的Γ光学模对应图3(d)中上下Ba层相反的面内振动。PHDOS说明低于130 cm⁻¹主要由Ba振动构成，而160–220 cm⁻¹的N振动也在α²F中出现尖峰。由此先定位q与分支，再确认原子和方向，最后检查它们对频率积分的贡献。

[原文 Fig. 3(a–d)，PDF第3页](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.105.165101)可以沿同一频率逐面板读：先在(a)以高对称路径距离定位红点较大的模式，再在(b)看原子PHDOS、在(c)看配对谱，最后到(d)检查两层Ba相反的实际位移。色散不是布里渊区积分，红点不是原子振幅，PHDOS也不是电子配对权重。本页Al的逐q文件给出频率、γ与λ，正好对应前两个耦合量；波函数网格、q星权重和后续谱文件仍需保持同一父链。要复现这种组合图，先按实际q坐标把频率和γ配对，另外绘制α²F，再用同一矩阵的位移文件在XCrySDen中显示原子运动。具体谱图与完整处理源码见[谱函数页](/Atlas/m/eliashberg-a2f/qe/)，位移文件及共同显示尺度见[DFPT模式页](/Atlas/m/phonon-dfpt/qe/)。Al单原子原胞与文献的三层Ba₂N采用各自结构，本文不从文献箭头给Al或旧异质结指定模式方向。

图6采用同样读法比较4%拉伸状态：Γ光学模移到约49 cm⁻¹，K点软化声学模在α²F中对应约24 cm⁻¹的低频峰。作者用√3×√3超胞将K折叠到Γ显示图6(e)的位移；Ba包含面内、面外运动，N主要在面内运动。这种有限q模式图须包括跨原胞相位，不能把原胞Γ箭头复制成所有q的模式。图7随后考察各向异性能隙随温度的消失，与前面的平均谱公式估计分开，见[EPW求解](/Atlas/m/epw-eliashberg/qe/#material-anisotropic-route)。

用于界面分析时，按相同应变和协议比较异质结与匹配单层的电子态、声子和耦合，再判断频率软化、散射相空间与矩阵元各自的变化。模式位移的层归属说明哪个原子在动；配对电子属于哪一层还需带/空间投影和耦合矩阵信息。

<span id="double-grid-research-record"></span>
<span id="zrcl2-sc2c-k64-k96-record"></span>
<span id="epc-literature-aesthetics"></span>

原始材料启动与中止记录：[SnSe₂/Sr₂N](/Atlas/cases/epc-research-notes/#double-grid-research-record)、[ZrCl₂/Sc₂C双网格与谱窗](/Atlas/cases/epc-research-notes/#zrcl2-sc2c-k64-k96-record)。这些记录保持自己的科学接受范围，不与Al链混接。接着读[逐模线宽](/Atlas/m/phonon-linewidth/qe/)、[α²F与累计λ](/Atlas/m/eliashberg-a2f/qe/)和[Tc公式](/Atlas/m/allen-dynes/qe/)。
