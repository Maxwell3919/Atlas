[QE 双网格 EPC 流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html) · [ph.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [q2r.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [QE 电子声子系数及谱函数定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

<span id="double-grid-pwxall"></span>

## 两条 pwxall 流程算完后，对照 Tc 曲线

这条 Tc 计算路线需要先完成一整条 `pwxall → pwx → phx → … → lambdax`，再在新目录中更换 `pwxall` 的致密 k 网格，重复相同流程。两次 `lambdax` 各自产生一条 Tc 随电子展宽 σ 变化的曲线，最后把两条曲线放在一起，检查交点及其附近的一致程度。只跑通第一条路径，或只从它的输出中选一行 Tc，还没有完成这项对照。

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

### 两条独立链采用同一比较协议

第二条路径只改变 `al.dense.in` 末尾的 `K_POINTS`。`al.scf.in`、`al.elph.in`、`q2r.in`、`matdyn-dos.in`、`lambda.in` 五份输入逐字相同，分别在自己的目录运行。因而两边采用相同结构、赝势、截断能、电子与声子响应阈值、q 权重、频率积分范围、频率展宽和 μ*。

| 路径 | pwxall 致密 k | pwx 响应 k | DFPT q | 比较时使用的曲线 |
|---|---|---|---|---|
| `epc-q4` | 32×32×32 | 16×16×16 | 4×4×4 | `lambda.out` 中十组展宽的 Tc₃₂(σ) |
| `epc-q4-k48` | 48×48×48 | 16×16×16 | 4×4×4 | 新计算的 `lambda.out` 中十组展宽的 Tc₄₈(σ) |

两套均使用 `0 0 0` 偏移。按每个倒格矢方向检查整数倍关系：32=2×16、48=3×16，而 16=4×4。`pwxall` 网格是 `pwx` 网格的整数倍，`pwx` 网格又是 q 网格的整数倍；32 与 48 彼此不需要互为整数倍。这种不偏移的嵌套设置满足本路线对 k、k+q 点覆盖的要求。

新目录沿用同一组结构、赝势、截断能、电子与响应收敛阈值，并重新生成自己那份致密网格 `a2Fsave`。响应 SCF、逐 q 文件和 `lambda.x` 输入输出也留在各自目录。准备新分支时可以用 `cp` 复制已经核验的输入与提交脚本，用 `vi` 改 `pwxall` 网格；不要把第一条路径的结果文件直接充作第二条的计算结果，也不要让两条路径共用可写的 `outdir`。

两次 `lambda.x` 必须采用相同的 μ*、q 权重、频率积分范围和频率展宽；两次 `ph.x` 的电子展宽序列也要一致。比较图横轴是这组 **EPC 双 δ 积分展宽 σ**，纵轴才是 Tc。它不同于 SCF 的 `degauss`，也不同于 `lambda.in` 中谱函数的频率展宽。

两条曲线的交点提供一个候选的 (σ*, Tc*)，接着要读交点两侧是否仍然接近、λ 与 ωlog 是否各自稳定。QE 开发者对这项检查的说明是：在同一展宽下继续增加 k 点，结果应趋于不变；可用的展宽区间还应向较小 σ 延伸。一个孤立交点不能代替这个区间检查。增加 q 网格后也要重新核对 k–σ 稳定区，不能默认旧区间仍然适用。[QE 开发者关于 k 网格与展宽的说明](https://lists.quantum-espresso.org/pipermail/users/2003-September/000602.html)

第二个目录中的实际 `cp`、`vi`、Slurm 提交与输出检查见[48³ 分支的操作记录](/Atlas/m/epc/qe/#dense-k48-run)。两份输出怎样配对、两条曲线的求交结果与差值，接着看 [Tc 页的实际叠图与交点表](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)。两条链的原生文件、求交脚本和绘图脚本放在[同一个下载包](/Atlas/examples/supercon-al-tc-files.tar.gz)。

Al 使用 QE 7.5、LDA-PZ 与 `Al.pz-vbc.UPF`，晶格常数 3.95606780081 Å；结构来源见 [晶胞优化](/Atlas/m/vc-relax/qe/)。完整终端会话、XML 与文件哈希的逐项解释保存在 [Al 执行与核验记录](/Atlas/cases/epc-al-verification/)。


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

输入设置了 `outdir='./tmp'`，实际文件在 `tmp/al.a2Fsave`，原脚本却从工作目录复制 `al.a2Fsave`。`set -e` 使脚本在这条 `cp` 失败后退出，后面的响应 SCF 尚未开始。保留已经正常结束的致密结果，将复制路径改正后，用下面的 `continue.slurm` 接着运行；下载包同时保留原脚本与错误记录，便于对照。

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


<a id="dense-k48-run"></a>

## 再算一条 48³ 致密电子网格，把两条计算独立走完

前一条 Al 计算使用 32³ 致密电子网格、16³ 响应电子网格和 4³ 声子 q 网格。现在把致密电子网格加到 48³，其余设置保持相同，再从头运行两次 `pw.x`、`ph.x` 和后处理。这样得到的第二条 Tc(σ) 曲线，才有自己完整的输入与输出。这里的 Al 是双网格流程演示；这些 3D 网格不能直接当作其他材料的已收敛参数。

| 分支目录 | 致密电子网格 | 响应电子网格 | 声子 q 网格 |
| --- | --- | --- | --- |
| `epc-q4` | 32 × 32 × 32 | 16 × 16 × 16 | 4 × 4 × 4 |
| `epc-q4-k48` | 48 × 48 × 48 | 16 × 16 × 16 | 4 × 4 × 4 |

[两条分支的输入、原生输出与比较脚本](/Atlas/examples/supercon-al-tc-files.tar.gz)放在同一个文件包内，解压后分别位于 `al-dense-grid-tc/k32/` 和 `al-dense-grid-tc/k48/`。后面的终端记录保留运行时目录名 `epc-q4` 与 `epc-q4-k48`；包内的短目录名用于整理这两套已经产生的文件。

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

两次 SCF 的 XML 分别保存 48³ 与 16³ 网格；第二次 SCF 后 `.a2Fsave` 与本分支备份的 SHA-256 相同。作业 2016 最终返回 `COMPLETED`、`ExitCode=0:0`；两次 SCF 和八个 q 点响应正常结束。完整监控、逐 q 文件头及结束检查见 [48³ 会话](/Atlas/cases/epc-al-verification/#dense-k48-run)。

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

## 两份 Tc 表按相同展宽配对求交

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

`lambda.x` 在此版本不打印 `JOB DONE.`；正常退出、十档有限输出和逐 q 重建共同检查这一段。σ=0.020 Ry 时，32³ 分支给出 λ=0.37449、ωlog=343.741 K、Tc=0.969 K；48³ 分支给出 λ=0.367505、ωlog=342.622 K、Tc=0.854 K。两条曲线使用同一 μ*=0.10。

![Al 32³ 与 48³ 的 Tc 曲线及逐点差值](/Atlas/examples/supercon-al-tc/figures/supercon-al-k32-k48-tc-delta.png)

十个共同采样点的 `Tc₃₂−Tc₄₈` 均为正，分段直线求交得到 **0 个交点、0 个重合区间**。最近的 σ=0.050 Ry 处，重建 Tc 分别为 0.984588、0.975366 K，差值 +0.009222 K。Al 64³ 的致密与响应 SCF 已结束，声子/EPC 因 walltime 到限取消，留下六份逐 q 文件，缺少完整八个 q 和 `lambda.x` 输出，不能加入此图。

### 交给代码助手的配对与求交任务

> 读取 k32/、k48/ 各自的 lambda.in/out 和八个 elph.inp_lambda 文件。逐分支核对 q 坐标、文件顺序、星权重、十档电子展宽和 μ*，按 QE 7.5 算法重建 λ、ωlog、Tc，核对原生打印精度。按同一 σ 配对，计算 ΔTc；检查分段直线的端点交点、异号区间与重合区间，没有交点时输出零个。保存配对 CSV、求交 JSON 和完整可运行源码；画两条 Tc 曲线及 ΔTc 零线，保留原始采样点。只处理保存文件，不外推或补算缺失分支。

完整源码：[rebuild_tc.py](/Atlas/examples/supercon-al-tc/rebuild_tc.py)、[compare_tc.py](/Atlas/examples/supercon-al-tc/compare_tc.py)、[plot_supercon_tc_difference.py](/Atlas/examples/supercon-al-tc/plot_supercon_tc_difference.py)。在 [双分支下载包](/Atlas/examples/supercon-al-tc-files.tar.gz) 解包后的 `al-dense-grid-tc` 运行：

<details>
<summary>rebuild_tc.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Rebuild the QE7.5 lambda.x result from its native elph input files. No QE executable is run."""

import argparse, csv, hashlib, json, math, re
from pathlib import Path

NUMBER = r"[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?"
num = lambda x: float(x.replace("D", "E").replace("d", "e"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def reconstruct(root):
    root = Path(root)
    lines = [
        l.split("!")[0].strip()
        for l in (root / "lambda.in").read_text().splitlines()
        if l.split("!")[0].strip()
    ]
    emax, width, order = map(float, lines[0].split())
    assert order == 0, "This script supports the actual simple-Gaussian spectrum only"
    nq = int(lines[1])
    qs = [list(map(float, l.split())) for l in lines[2 : 2 + nq]]
    names = lines[2 + nq : 2 + 2 * nq]
    mu = float(lines[2 + 2 * nq])
    totalweight = sum(q[3] for q in qs)
    native = (root / "lambda.out").read_text()
    details = re.findall(
        r"lambda\s*=\s*("
        + NUMBER
        + r")\s*\(\s*("
        + NUMBER
        + r")\s*\)\s*<log w>=\s*("
        + NUMBER
        + r")\s*K\s*N\(Ef\)=\s*("
        + NUMBER
        + r")\s*at degauss=\s*("
        + NUMBER
        + r")",
        native,
    )
    printed = [
        list(map(num, line.split()))
        for line in native.split("T_c")[-1].strip().splitlines()
        if len(line.split()) == 3
    ]
    assert len(details) == len(printed) == 10
    n = 2000
    step = emax / (n - 1)
    freq = [i * step for i in range(n)]
    lq = [0.0] * 10
    a2f = [[0.0] * n for _ in range(10)]
    sigma0 = None
    dos0 = None
    ef0 = None
    hashes = {p: sha(root / p) for p in ["lambda.in", "lambda.out"]}
    qcheck = []
    for iq, (qinfo, name) in enumerate(zip(qs, names), 1):
        p = root / name
        hashes[name] = sha(p)
        records = p.read_text().splitlines()
        head = records[0].split()
        qread = list(map(num, head[:3]))
        ns, nm = map(int, head[3:])
        w2 = list(map(num, records[1].split()))
        assert ns == 10 and nm == 3 and len(w2) == 3 and min(w2) >= 0
        coordinate_error = max(abs(x - y) for x, y in zip(qinfo[:3], qread))
        assert (
            coordinate_error <= 5.005e-7
        ), "q differs beyond its six-decimal output rounding"
        weight = qinfo[3] / totalweight
        sig = []
        doses = []
        efs = []
        for j in range(ns):
            k = 2 + j * (nm + 2)
            sm = re.search(
                r"Gaussian Broadening:\s*(" + NUMBER + r") Ry, ngauss=\s*(-?\d+)",
                records[k],
            )
            sigma = num(sm.group(1))
            assert int(sm.group(2)) == 0
            d = re.search(
                r"DOS =\s*(" + NUMBER + r").*at Ef=\s*(" + NUMBER + r")", records[k + 1]
            )
            dos, ef = map(num, d.groups())
            sig.append(sigma)
            doses.append(dos)
            efs.append(ef)
            for im in range(nm):
                m = re.search(
                    r"lambda\(\s*(\d+)\)=\s*("
                    + NUMBER
                    + r")\s*gamma=\s*("
                    + NUMBER
                    + r")",
                    records[k + im + 2],
                )
                assert int(m.group(1)) == im + 1
                lam = num(m.group(2))
                om = math.sqrt(w2[im]) * 3289.828
                lq[j] += weight * lam
                coefficient = weight * lam * om * 0.5 / math.sqrt(math.pi) / width
                for i, e in enumerate(freq):
                    a2f[j][i] += coefficient * math.exp(
                        -min(200.0, ((e - om) / width) ** 2)
                    )
        if sigma0 is None:
            sigma0, dos0, ef0 = sig, doses, efs
        else:
            assert (
                sig == sigma0 and doses == dos0 and efs == ef0
            ), "Sigma/DOS/EF metadata mismatch between q files"
        qcheck.append(
            {
                "q_index": iq,
                "q_lambda_in": qinfo[:3],
                "q_elph": qread,
                "weight": qinfo[3],
                "coordinate_error": coordinate_error,
            }
        )
    rows = []
    for j, detail in enumerate(details):
        lp, l2p, wp, dosp, sigmap = map(num, detail)
        assert sigmap == sigma0[j]
        l2 = 2 * step * sum(a2f[j][i] / freq[i] for i in range(1, n))
        wlog = (
            math.exp(
                2
                * step
                * sum(a2f[j][i] * math.log(freq[i]) / freq[i] for i in range(1, n))
                / l2
            )
            * 47.9924
        )
        value = (
            wlog
            / 1.2
            * math.exp(-1.04 * (1 + lq[j]) / (lq[j] - mu * (1 + 0.62 * lq[j])))
        )
        assert (
            abs(lp - lq[j]) <= 0.500001e-6
            and abs(l2p - l2) <= 0.500001e-6
            and abs(wp - wlog) <= 0.500001e-3
        )
        assert (
            abs(printed[j][2] - value) <= 0.500001e-3
        ), "Reconstruction does not round to native Tc"
        rows.append(
            {
                "sigma_Ry": sigmap,
                "mu_star": mu,
                "lambda_qsum": lq[j],
                "lambda_spectrum": l2,
                "omega_log_K": wlog,
                "N_EF": dosp,
                "N_EF_unit": "states/spin/Ry/cell",
                "Tc_K": value,
                "native_printed_Tc_K": printed[j][2],
                "native_lambda_6dp": lp,
                "native_lambda_spectrum_6dp": l2p,
                "native_omega_log_K_3dp": wp,
                "EF_eV": ef0[j],
            }
        )
    metadata = {
        "source_sha256": hashes,
        "q_pairing": qcheck,
        "q_weight_sum": totalweight,
        "nq": nq,
        "spectrum_points": n,
        "spectrum_max_THz": emax,
        "spectrum_gaussian_width_THz": width,
        "mu_star": mu,
        "formula": "Tc=omega_log/1.2*exp(-1.04*(1+lambda_qsum)/(lambda_qsum-mu_star*(1+0.62*lambda_qsum)))",
        "frequency_constants": "3289.828THz/Ry;47.9924K/THz, matching QE7.5lambda.f90",
        "precision_scope": "Reconstruction of lambda.x from the exact printed elph records, not recovery of unprinted DFT precision. Mode lambda is stored to4decimals; final native Tc is printed to3decimals.",
        "source": "https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90",
        "no_QE_executable_run": True,
    }
    return rows, metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "branches",
        nargs="+",
        type=Path,
        help="Directories containing lambda.in/lambda.out/elph_dir",
    )
    p.add_argument("--outdir", type=Path, default=Path("."))
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    for branch in args.branches:
        rows, meta = reconstruct(branch)
        name = branch.name
        with (args.outdir / (name + "-rebuilt.csv")).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        (args.outdir / (name + "-rebuild-checks.json")).write_text(
            json.dumps(meta, indent=2) + "\n"
        )
        print(
            name
            + ":10sigma rows reconstructed; native lambda/omega/Tc match their printed precision"
        )


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>compare_tc.py 的完整源码</summary>

```python
"""Pair two complete QE lambda.x branches and find straight-segment crossings.

Example, after both independent calculations have completed:
    python3 compare_tc.py --a k32 --b k48 --out comparison

Only Python's standard library is required. Keep rebuild_tc.py beside this
script. Curves reconstructed from lambda.x's actual elph inputs retain the
digits lost by its final 0.001 K printing. Printed Tc and a cross-check from
the printed moments are reported separately, without editing native files.
"""

from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
from rebuild_tc import reconstruct

NUMBER = r"[-+0-9.eEdD]+"
MOMENT = re.compile(
    rf"lambda\s*=\s*({NUMBER})\s*\(\s*({NUMBER})\s*\)\s*"
    rf"<log w>\s*=\s*({NUMBER})\s*K\s*N\(Ef\)\s*=\s*({NUMBER})"
    rf"\s*at degauss=\s*({NUMBER})"
)


def number(value):
    result = float(value.replace("D", "E").replace("d", "e"))
    if not math.isfinite(result):
        raise ValueError("Non-finite native value")
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_branch(path):
    text = (path / "lambda.out").read_text()
    rows = []
    for m in MOMENT.finditer(text):
        lam, spectral_lam, omega, nef, sigma = map(number, m.groups())
        rows.append(
            dict(
                sigma_Ry=sigma,
                lambda_qsum=lam,
                lambda_spectrum=spectral_lam,
                omega_log_K=omega,
                N_Ef_native=nef,
            )
        )
    sections = re.split(r"lambda\s+omega_log\s+T_c", text)
    if len(sections) != 2 or not rows:
        raise ValueError(f"{path}: expected one native Tc table")
    table = []
    for line in sections[1].splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 3 or not all(re.fullmatch(NUMBER, x) for x in fields):
            raise ValueError(f"{path}: unexpected native Tc row: {line}")
        table.append(list(map(number, fields)))
    if len(table) != len(rows):
        raise ValueError(f"{path}: incomplete moment/Tc pairing")
    sigmas = [r["sigma_Ry"] for r in rows]
    if len(set(sigmas)) != len(sigmas) or sigmas != sorted(sigmas):
        raise ValueError(f"{path}: duplicated or unordered sigma points")
    input_lines = [
        x.split("!")[0].strip() for x in (path / "lambda.in").read_text().splitlines()
    ]
    input_lines = [x for x in input_lines if x]
    mu = number(input_lines[-1])
    for row, (lam, omega, tc) in zip(rows, table):
        # These bounds follow the native five/three-place output formats.
        if abs(row["lambda_qsum"] - lam) > 0.0000051 or row["omega_log_K"] != omega:
            raise ValueError(f"{path}: lambda/Tc table rows do not correspond")
        denominator = row["lambda_qsum"] - mu * (1 + 0.62 * row["lambda_qsum"])
        if denominator <= 0 or omega <= 0 or tc < 0:
            raise ValueError(f"{path}: formula outside the supported positive regime")
        recomputed = (
            omega / 1.2 * math.exp(-1.04 * (1 + row["lambda_qsum"]) / denominator)
        )
        if abs(recomputed - tc) > 0.00055:
            raise ValueError(
                f"{path}: printed moments do not reproduce native Tc rounding"
            )
        row.update(mu_star=mu, Tc_printed_K=tc, Tc_printed_moments_K=recomputed)
    dat = []
    for line in (path / "lambda.dat").read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            dat.append(list(map(number, line.split())))
    if len(dat) != len(rows):
        raise ValueError(f"{path}: lambda.dat count mismatch")
    for row, fields in zip(rows, dat):
        expected = [
            row[k]
            for k in (
                "sigma_Ry",
                "lambda_qsum",
                "lambda_spectrum",
                "omega_log_K",
                "N_Ef_native",
            )
        ]
        if fields != expected:
            raise ValueError(f"{path}: lambda.dat differs from stdout")
    return rows, {
        n: digest(path / n) for n in ("lambda.in", "lambda.out", "lambda.dat")
    }


def crossings(x, a, b):
    """Return all isolated sampled zeros, sign changes and overlap intervals."""
    difference = [y - z for y, z in zip(a, b)]
    overlaps = []
    overlap_indices = set()
    for i in range(len(x) - 1):
        if difference[i] == 0 and difference[i + 1] == 0:
            if overlaps and overlaps[-1]["right_index"] == i:
                overlaps[-1].update(sigma_hi_Ry=x[i + 1], right_index=i + 1)
            else:
                overlaps.append(
                    dict(
                        kind="overlap",
                        sigma_lo_Ry=x[i],
                        sigma_hi_Ry=x[i + 1],
                        left_index=i,
                        right_index=i + 1,
                    )
                )
            overlap_indices.update((i, i + 1))
    points = []
    for i, d in enumerate(difference):
        if d == 0 and i not in overlap_indices:
            points.append(
                dict(
                    kind="sampled_equality",
                    sigma_Ry=x[i],
                    Tc_K=a[i],
                    sigma_lo_Ry=x[i],
                    sigma_hi_Ry=x[i],
                    delta_lo_K=0.0,
                    delta_hi_K=0.0,
                )
            )
    for i, (d1, d2) in enumerate(zip(difference, difference[1:])):
        if d1 * d2 < 0:
            t = -d1 / (d2 - d1)
            xc = x[i] + t * (x[i + 1] - x[i])
            ya = a[i] + t * (a[i + 1] - a[i])
            yb = b[i] + t * (b[i + 1] - b[i])
            if not x[i] < xc < x[i + 1] or abs(ya - yb) > 1e-12:
                raise ValueError("Crossing interpolation arithmetic failed")
            points.append(
                dict(
                    kind="segment_crossing",
                    sigma_Ry=xc,
                    Tc_K=ya,
                    sigma_lo_Ry=x[i],
                    sigma_hi_Ry=x[i + 1],
                    delta_lo_K=d1,
                    delta_hi_K=d2,
                )
            )
    points.sort(key=lambda r: r["sigma_Ry"])
    for i, p in enumerate(points, 1):
        p["id"] = f"C{i}"
    return dict(points=points, overlap_intervals=overlaps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", type=Path, default=Path("k32"))
    parser.add_argument("--b", type=Path, default=Path("k48"))
    parser.add_argument("--out", type=Path, default=Path("comparison"))
    args = parser.parse_args()
    a, ha = load_branch(args.a)
    b, hb = load_branch(args.b)
    xa = [r["sigma_Ry"] for r in a]
    xb = [r["sigma_Ry"] for r in b]
    if xa != xb or {r["mu_star"] for r in a + b} != {a[0]["mu_star"]}:
        raise ValueError("Branches must have identical native sigma values and mu_star")
    # This reconstruction follows the actual QE 7.5 simple-Gaussian inputs.
    # Its own checks compare each result with native output-format precision.
    precise_a, checks_a = reconstruct(args.a)
    precise_b, checks_b = reconstruct(args.b)
    for native, precise in ((a, precise_a), (b, precise_b)):
        if len(native) != len(precise):
            raise ValueError("Incomplete raw-input reconstruction")
        for record, exact in zip(native, precise):
            if (record["sigma_Ry"], record["mu_star"]) != (
                exact["sigma_Ry"],
                exact["mu_star"],
            ):
                raise ValueError(
                    "Raw-input reconstruction is not paired with the native table"
                )
            record.update(
                Tc_rebuilt_K=exact["Tc_K"],
                lambda_qsum_rebuilt=exact["lambda_qsum"],
                lambda_spectrum_rebuilt=exact["lambda_spectrum"],
                omega_log_rebuilt_K=exact["omega_log_K"],
            )
    paired = []
    for ra, rb in zip(a, b):
        row = {"sigma_Ry": ra["sigma_Ry"], "mu_star": ra["mu_star"]}
        for tag, record in [("A", ra), ("B", rb)]:
            row.update({k + "_" + tag: v for k, v in record.items() if k not in row})
        row["delta_Tc_printed_K"] = ra["Tc_printed_K"] - rb["Tc_printed_K"]
        row["delta_Tc_printed_moments_K"] = (
            ra["Tc_printed_moments_K"] - rb["Tc_printed_moments_K"]
        )
        row["delta_Tc_rebuilt_K"] = ra["Tc_rebuilt_K"] - rb["Tc_rebuilt_K"]
        paired.append(row)
    printed = crossings(
        xa, [r["Tc_printed_K"] for r in a], [r["Tc_printed_K"] for r in b]
    )
    reconstructed = crossings(
        xa,
        [r["Tc_printed_moments_K"] for r in a],
        [r["Tc_printed_moments_K"] for r in b],
    )
    raw = crossings(xa, [r["Tc_rebuilt_K"] for r in a], [r["Tc_rebuilt_K"] for r in b])
    report = {
        "branch_A": args.a.name,
        "branch_B": args.b.name,
        "points_per_branch": len(a),
        "mu_star": a[0]["mu_star"],
        "branch_A_hashes": ha,
        "branch_B_hashes": hb,
        "branch_A_rebuild_checks": checks_a,
        "branch_B_rebuild_checks": checks_b,
        "raw_input_reconstruction": raw,
        "native_printed_curves": printed,
        "printed_moment_crosscheck": reconstructed,
        "native_output_files_identical": ha["lambda.out"] == hb["lambda.out"],
        "scope": "All in-range straight-segment intersections; no fit or extrapolation. The plotted curves are reconstructed from exact elph inputs to lambda.x, whose final Tc print precision is 0.001 K. Reconstruction does not recover unprinted DFPT precision. Source files alone do not establish matched protocols: inspect the accompanying independent run review.",
        "scientific_convergence": "not assessed by this postprocessor",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "paired-tc.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    (args.out / "crossings.json").write_text(json.dumps(report, indent=2) + "\n")
    with (args.out / "crossings.csv").open("w", newline="") as f:
        fields = [
            "id",
            "kind",
            "sigma_Ry",
            "Tc_K",
            "sigma_lo_Ry",
            "sigma_hi_Ry",
            "delta_lo_K",
            "delta_hi_K",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(raw["points"])
    print(
        f'Paired branches: {args.a.name} / {args.b.name}; {len(a)} common sigma points; mu*={a[0]["mu_star"]:.2f}'
    )
    print("sigma_Ry  Tc_A_native_K  Tc_B_native_K  Delta_Tc_rebuilt_K")
    for row in paired:
        print(
            f'{row["sigma_Ry"]:8.3f}  {row["Tc_printed_K_A"]:13.3f}  {row["Tc_printed_K_B"]:13.3f}  {row["delta_Tc_rebuilt_K"]:+18.9f}'
        )
    print("All in-range intersections, reconstructed from native elph inputs:")
    for p in raw["points"]:
        print(
            f'{p["id"]}: sigma={p["sigma_Ry"]:.9f} Ry; Tc={p["Tc_K"]:.9f} K; bracket=[{p["sigma_lo_Ry"]:.3f}, {p["sigma_hi_Ry"]:.3f}] Ry'
        )
    if not raw["points"]:
        print("No isolated crossing in the sampled range.")
    if raw["overlap_intervals"]:
        print("Overlap intervals:", json.dumps(raw["overlap_intervals"]))
    print(
        f'Native 0.001 K print check: {len(printed["points"])} isolated points, {len(printed["overlap_intervals"])} overlap intervals.'
    )
    print("Saved paired-tc.csv, crossings.csv, crossings.json.")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>plot_supercon_tc_difference.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Plot the paired Al k32/k48 Tc curves and their signed difference."""
from __future__ import annotations
import argparse
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"no rows in {path}")
    sigma = [float(r["sigma_Ry"]) for r in rows]
    tc32 = [float(r["Tc_rebuilt_K_A"]) for r in rows]
    tc48 = [float(r["Tc_rebuilt_K_B"]) for r in rows]
    delta_saved = [float(r["delta_Tc_rebuilt_K"]) for r in rows]
    mu = [float(r["mu_star"]) for r in rows]
    if any(not math.isfinite(x) for seq in (sigma, tc32, tc48, delta_saved, mu) for x in seq):
        raise ValueError("non-finite input value")
    if sigma != sorted(sigma) or len(set(sigma)) != len(sigma):
        raise ValueError("sigma values must be strictly increasing")
    if max(mu) - min(mu) > 1e-12:
        raise ValueError("mu* differs between paired rows")
    delta = [a - b for a, b in zip(tc32, tc48)]
    if any(abs(x - y) > 2e-9 for x, y in zip(delta, delta_saved)):
        raise ValueError("stored Delta Tc does not equal Tc32 - Tc48")
    return sigma, tc32, tc48, delta, mu[0]


def intersections(sigma, delta):
    points = []
    intervals = []
    i = 0
    while i < len(delta):
        if delta[i] != 0:
            i += 1
            continue
        j = i
        while j + 1 < len(delta) and delta[j + 1] == 0:
            j += 1
        if j > i:
            intervals.append((sigma[i], sigma[j]))
        else:
            points.append((sigma[i], 0.0))
        i = j + 1
    for i in range(len(delta) - 1):
        if delta[i] * delta[i + 1] < 0:
            x = sigma[i] - delta[i] * (sigma[i + 1] - sigma[i]) / (delta[i + 1] - delta[i])
            points.append((x, 0.0))
    return points, intervals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("comparison-k32-k48/paired-tc.csv"))
    ap.add_argument("--out", type=Path, default=Path("figures"))
    ap.add_argument("--prefix", default="supercon-al-k32-k48-tc-delta")
    args = ap.parse_args()
    sigma, tc32, tc48, delta, mu = read_rows(args.data)
    points, intervals = intersections(sigma, delta)
    args.out.mkdir(parents=True, exist_ok=True)

    blue, vermillion = "#0072B2", "#D55E00"
    fig, (ax_tc, ax_delta) = plt.subplots(
        2, 1, figsize=(7.4, 6.1), sharex=True,
        gridspec_kw={"height_ratios": [1.55, 1.0], "hspace": 0.08},
        layout="constrained",
    )
    ax_tc.plot(sigma, tc32, color=blue, marker="o", ms=5, lw=1.8,
               label=r"$32^3$ dense $k$ mesh")
    ax_tc.plot(sigma, tc48, color=vermillion, marker="s", ms=5, lw=1.8,
               ls="--", label=r"$48^3$ dense $k$ mesh")
    ax_tc.set_ylabel(r"$T_c$ (K)")
    ax_tc.set_ylim(0, max(tc32 + tc48) * 1.12)
    ax_tc.legend(frameon=False, ncol=2, loc="upper right")
    ax_tc.text(0.02, 0.94, rf"$\mu^*= {mu:.2f}$; {len(sigma)} calculated widths",
               transform=ax_tc.transAxes, va="top", fontsize=9)

    ax_delta.axhline(0, color="#333333", lw=1.15, ls=(0, (4, 2)), zorder=4)
    ax_delta.plot(sigma, delta, color="#6A3D9A", marker="D", ms=4.5, lw=1.7)
    ax_delta.fill_between(sigma, 0, delta, where=[d >= 0 for d in delta],
                          color="#6A3D9A", alpha=0.10, interpolate=True)
    for x, y in points:
        ax_tc.scatter([x], [y], s=50, facecolor="white", edgecolor="#111111", zorder=5)
        ax_delta.scatter([x], [y], s=45, facecolor="white", edgecolor="#111111", zorder=5)
    ax_delta.set_ylabel(r"$\Delta T_c=T_c(32^3)-T_c(48^3)$ (K)")
    ax_delta.set_xlabel(r"Electronic smearing $\sigma$ (Ry)")
    ax_delta.set_xlim(min(sigma) - 0.002, max(sigma) + 0.002)
    ax_delta.xaxis.set_major_locator(MultipleLocator(0.005))
    span = max(delta) - min(delta)
    lo = min(0.0, min(delta)) - 0.24 * span
    hi = max(0.0, max(delta)) + 0.16 * span
    ax_delta.set_ylim(lo, hi)
    if points or intervals:
        summary = f"{len(points)} isolated crossing(s), {len(intervals)} overlap interval(s)"
    else:
        min_i = min(range(len(delta)), key=delta.__getitem__)
        summary = ("No crossing in sampled range; "
                   rf"min $\Delta T_c={delta[min_i]:.6f}$ K at $\sigma={sigma[min_i]:.3f}$ Ry")
    ax_delta.text(0.02, 0.94, summary, transform=ax_delta.transAxes,
                  va="top", fontsize=8.7)
    for ax in (ax_tc, ax_delta):
        ax.grid(axis="both", color="#B7B7B7", alpha=0.28, lw=0.65)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(direction="out", length=3.5, width=0.8)
    fig.suptitle("Al: paired dense-mesh Allen–Dynes results", fontsize=12, y=1.015)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(args.out / f"{args.prefix}.{ext}", dpi=320 if ext == "png" else None,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"rows={len(sigma)}; mu*={mu:.2f}; isolated crossings={len(points)}; overlap intervals={len(intervals)}")
    print(f"delta_min_K={min(delta):.9f}; delta_max_K={max(delta):.9f}")
    print(f"saved {args.out / (args.prefix + '.png')}, .svg, .pdf")


if __name__ == "__main__":
    main()
```

</details>

```bash
python3 rebuild_tc.py k32 k48 --outdir comparison-k32-k48
python3 compare_tc.py --a k32 --b k48 --out comparison-k32-k48
python3 plot_supercon_tc_difference.py --data comparison-k32-k48/paired-tc.csv --out figures --prefix supercon-al-k32-k48-tc-delta
```

[原始求交结果](/Atlas/examples/supercon-al-tc/comparison-k32-k48/crossings.json) 与 [配对 CSV](/Atlas/examples/supercon-al-tc/comparison-k32-k48/paired-tc.csv) 留下计算结果。交点算法、原生输出与重建值的核对接着读 [Tc 页](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)；谱积分和频率矩读 [α²F 页](/Atlas/m/eliashberg-a2f/qe/)，逐模线宽读 [声子线宽页](/Atlas/m/phonon-linewidth/qe/)，完整谱求解读 [EPW 页](/Atlas/m/epw-eliashberg/qe/)。这组比较固定了 16³ 响应和 4³ q 网格；无交点是当前采样结果，尚未确定网格收敛的材料 Tc。

<span id="double-grid-research-record"></span>

## 材料启动与排错记录

SnSe₂/Sr₂N 的 BFGS 状态、质量索引修正、两步 SCF 与声子启动会话已移至 [研究记录](/Atlas/cases/epc-research-notes/#double-grid-research-record)。这里保留入口，完整命令与输出在附件中。

<span id="zrcl2-sc2c-k64-k96-record"></span>

ZrCl₂/Sc₂C 的 ph64/ph96、18 THz 候选后处理输入和来源核验保存在 [保存双网格结果与谱积分上限记录](/Atlas/cases/epc-research-notes/#zrcl2-sc2c-k64-k96-record)。

<span id="epc-literature-aesthetics"></span>

[文献图例与 DOI](/Atlas/cases/epc-al-verification/#epc-literature-aesthetics) 展示模式投影、谱函数、累计耦合与能隙的组合画法。
