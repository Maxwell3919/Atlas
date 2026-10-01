界面和应变声子图里的负频率需要沿模式读：整个结构的平移偏离了零，还是某种相对位移使能量降低？这两种情况都可以画在零线以下，但对应的结构变化和下一步计算不同。

这次用 Preston 上真实 QE 7.5 金刚石 Si 的 Γ 结果展开。两原子原胞有六个模式，`ph.x` 的前三支是 −5.585702 cm⁻¹。读取原始矩阵可见两个 Si 同向同幅移动；对同一矩阵施加平移声学和规则以后，这三支回到零附近。这个例子适合识别 Γ 平移残差，后面再用 Ba₂N 的有限 K 软模说明另一类问题。

Si 采用 QE 随附例子的固定晶胞，常规立方晶格参数为 5.397607551 Å，PBE、USPP、60/640 Ry 截断和 8³ 电子网格。本例未重新优化晶格。[父 SCF](/Atlas/m/scf/qe/)、[完整输入](/Atlas/examples/si-pbe/scf/scf.in)和[输出](/Atlas/examples/si-pbe/scf/scf.out.txt)记录了该结构。QE 用负频标签表示 ω²<0；它不是负的振动能量。

输入、输出、原始矩阵、两份 `.modes` 与完整后处理可[一起下载](/Atlas/examples/stability-imaginary-si-files.tar.gz)。解包后进入 `stability-imaginary-si` 读取结果。复算响应时还需要由[Si SCF](/Atlas/m/scf/qe/)生成 `scf/tmp/si.save`；教学包没有包含电荷密度与波函数。

[Baroni 综述式 (5)](https://doi.org/10.1103/RevModPhys.73.515)把频率平方与质量加权 Hessian 联系起来。沿一个归一化模坐标 Q，在平衡点附近能量变化的二阶项为 `ΔE≈ω²Q²/2`。整体平移在无限精度下应给出零曲率；持续存在的非平移负曲率则指向一种可使结构离开当前构型的畸变。

## 先认清目录里的几种文件

先进入保存 Γ 点声子输出的目录：


```text
[preston@preston-System-Product-Name si-pbe]$ cd gamma-phonon
[preston@preston-System-Product-Name gamma-phonon]$
```


```text
[preston@preston-System-Product-Name gamma-phonon]$ ls -lh ph.in ph.out ph.err si.dynG dynmat* *.modes
-rw-rw-r-- 1 preston preston  520 Sep 22 21:38 dynmat-crystal.err
-rw-rw-r-- 1 preston preston  107 Sep 22 21:37 dynmat-crystal.in
-rw-rw-r-- 1 preston preston 1.9K Sep 22 21:38 dynmat-crystal.out
-rw-rw-r-- 1 preston preston  520 Sep 22 21:37 dynmat-no.err
-rw-rw-r-- 1 preston preston   92 Sep 22 21:37 dynmat-no.in
-rw-rw-r-- 1 preston preston 1.8K Sep 22 21:37 dynmat-no.out
-rw-rw-r-- 1 preston preston 1.2K Sep 22 21:38 dynmat.axsf
-rw-rw-r-- 1 preston preston  780 Sep 22 21:33 ph.err
-rw-rw-r-- 1 preston preston  170 Sep 22 21:33 ph.in
-rw-rw-r-- 1 preston preston  15K Sep 22 21:37 ph.out
-rw-rw-r-- 1 preston preston 1.6K Sep 22 21:38 si-crystal.modes
-rw-rw-r-- 1 preston preston 1.6K Sep 22 21:37 si-no.modes
-rw-rw-r-- 1 preston preston 2.9K Sep 22 21:37 si.dynG
[preston@preston-System-Product-Name gamma-phonon]$
```


`ph.in` 是输入，`ph.out` 记录响应迭代，`ph.err` 单独接收标准错误。`si.dynG` 是 Γ 点的原始矩阵文件，它后面的频率段和本征矢也值得保留。两组 `dynmat-*` 文件是后面要比较的后处理；各自写出不同名称的 `.modes`，因此一组不会覆盖另一组。

本例直接计算的是 Γ 点，所以矩阵和位移文件都描述这一个 q 点。先从 `ph.out` 确认响应求解完成，再用 `si.dynG` 和两份 `.modes` 分析模式。

## ph.x 实际读了什么，又怎样结束

先打开声子输入：


```text
[preston@preston-System-Product-Name gamma-phonon]$ cat ph.in
Si Gamma phonon
&INPUTPH
  prefix = 'si'
  outdir = './tmp'
  fildyn = 'si.dynG'
  amass(1) = 28.085
  tr2_ph = 1.0d-14
  epsil = .false.
  ldisp = .false.
/
0.0 0.0 0.0
[preston@preston-System-Product-Name gamma-phonon]$
```


`prefix` 和 `outdir` 要与这份 Si 的 SCF 保存数据对应；`fildyn` 是要写出的矩阵文件名。`amass(1)=28.085` 对应唯一一种元素 Si。`ldisp=.false.` 后面紧跟一行 `0.0 0.0 0.0`，说明本次只算 Γ 点；它没有建立均匀 q 网格。`epsil=.false.` 也表明本次没有计算介电张量和 Born 有效电荷。

`tr2_ph=1.0d-14` 设定响应自洽的停止阈值。下面会在每个扰动表示中检查响应残差与收敛行；频率对截断能、电子网格和响应阈值的敏感性，则需要保持结构不变分别比较。

完成上游 Si SCF 后，保留它生成的 `scf/tmp`。将本页文件包与 `si-pbe` 放在同一父目录，从 `si-pbe` 建立独立复算目录：

```bash
cd si-pbe
mkdir gamma-recheck
cp -a scf/tmp gamma-recheck/
cp ../stability-imaginary-si/ph.in gamma-recheck/
cp ../stability-imaginary-si/run.sh gamma-recheck/
cd gamma-recheck
ls tmp/si.save
vi ph.in
vi run.sh
```

进入 `gamma-recheck` 后，核对 `prefix`、`outdir` 与刚复制的 Si 保存目录，并将 `run.sh` 中的 `<qe_bin>` 改为本机安装路径。随后执行 `sbatch run.sh`。

这次用 `vi` 保存输入和脚本，提交的是下面这份四进程脚本。这里只展示实跑配置，核数、MPI 实现和环境路径需要与自己的机器对应：


```text
[preston@preston-System-Product-Name gamma-phonon]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-gamma
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to core -np 4 <qe_bin>/ph.x -in ph.in > ph.out 2> ph.err
[preston@preston-System-Product-Name gamma-phonon]$
```


脚本将 `ph.out` 与 `ph.err` 分开写出，Slurm 的日志还另有 `_out.%j.log` 和 `_err.%j.log`。运行时在第二个终端进入同一目录，可以用：

```bash
squeue -j 768
tail -f ph.out
```

`768` 是这次的作业号，复算时换成 `sbatch run.sh` 返回的号码。按 Ctrl-C 退出 `tail -f`，计算仍由 Slurm 继续运行。本次运行中曾调整 MPI 进程绑定，日志中的耗时包含这段运行过程。

打开 `ph.out`，开头先出现程序版本、MPI 进程数和读取的保存目录。下面摘出对应原文：


```text
     Program PHONON v.7.5 starts on 22Sep2026 at 21:33:27
     Parallel version (MPI), running on     4 processors
     Reading input from ph.in
     Reading xml data from directory:
     ./tmp/si.save/
```


随后会回显晶胞、元素、截断能与电子 k 点；再往后才进入每个不可约表示的响应求解。本次有两个表示，每个包含三个模式，共六个模式。第一组表示的末两轮是：


```text
      iter #   4 total cpu time :   202.9 secs   av.it.:  10.7
      thresh= 4.818E-07 alpha_mix =  0.700 |ddv_scf|^2 =  4.579E-14

      iter #   5 total cpu time :   207.9 secs   av.it.:  11.5
      thresh= 2.140E-08 alpha_mix =  0.700 |ddv_scf|^2 =  5.675E-16

     End of self-consistent calculation

     Convergence has been achieved
```


这一组的响应残差 `|ddv_scf|²` 从 `4.579E-14` 降到 `5.675E-16`，低于所设 `tr2_ph`，随后出现收敛行。`thresh` 是内层求解阈值，与这里用于判断响应自洽的残差不同。第二组表示也要检查；下面把两组收敛行和末尾频率一起定位出来：


```text
[preston@preston-System-Product-Name gamma-phonon]$ grep -n -E 'Representation|Convergence|freq \(|JOB DONE' ph.out
153:     Representation     1      3 modes -  To be done
155:     Representation     2      3 modes -  To be done
164:     Representation #   1 modes #   1   2   3
185:     Convergence has been achieved
188:     Representation #   2 modes #   4   5   6
209:     Convergence has been achieved
220:     freq (    1) =      -0.167455 [THz] =      -5.585702 [cm-1]
221:     freq (    2) =      -0.167455 [THz] =      -5.585702 [cm-1]
222:     freq (    3) =      -0.167455 [THz] =      -5.585702 [cm-1]
223:     freq (    4) =      15.700807 [THz] =     523.722541 [cm-1]
224:     freq (    5) =      15.700807 [THz] =     523.722541 [cm-1]
225:     freq (    6) =      15.700807 [THz] =     523.722541 [cm-1]
230:     freq (   1-   3) =         -5.6  [cm-1]   --> T_1u G_15  G_4- I
231:     freq (   4-   6) =        523.7  [cm-1]   --> T_2g G_25' G_5+ R
321:   JOB DONE.
[preston@preston-System-Product-Name gamma-phonon]$
```


`ph.err` 和两份 `dynmat` 标准错误保留 X11 授权提示：


```text
Authorization required, but no authorization protocol specified
```


程序完成了两组响应求解、矩阵写出和对角化，并打印 `JOB DONE.`。后面的 ASR 比较使用这份实际生成的矩阵；[ph.err](/Atlas/examples/stability-imaginary-si/ph.err.txt) 和完整 [ph.out](/Atlas/examples/stability-imaginary-si/ph.out.txt) 可下载核对。

## 从矩阵文件里找到负频率和原子运动

直接读 `si.dynG` 的前 50 行：


```text
[preston@preston-System-Product-Name gamma-phonon]$ head -n 50 si.dynG
Dynamical matrix file
Si Gamma phonon
  1    2   2  10.2000000   0.0000000   0.0000000   0.0000000   0.0000000   0.0000000
           1  'Si     '    25597.911567706618
    1    1      0.0000000000      0.0000000000      0.0000000000
    2    1      0.2500000000      0.2500000000      0.2500000000

     Dynamical  Matrix in cartesian axes

     q = (    0.000000000   0.000000000   0.000000000 )

    1    1
  0.29148687   0.00000000    -0.00000000   0.00000000     0.00000000   0.00000000
 -0.00000000   0.00000000     0.29148687   0.00000000     0.00000000   0.00000000
  0.00000000   0.00000000    -0.00000000   0.00000000     0.29148687   0.00000000
    1    2
 -0.29155320   0.00000000     0.00000000   0.00000000     0.00000000   0.00000000
  0.00000000   0.00000000    -0.29155320   0.00000000    -0.00000000   0.00000000
  0.00000000   0.00000000    -0.00000000   0.00000000    -0.29155320   0.00000000
    2    1
 -0.29155320   0.00000000     0.00000000   0.00000000     0.00000000   0.00000000
  0.00000000   0.00000000    -0.29155320   0.00000000    -0.00000000   0.00000000
  0.00000000   0.00000000    -0.00000000   0.00000000    -0.29155320   0.00000000
    2    2
  0.29148687   0.00000000    -0.00000000   0.00000000     0.00000000   0.00000000
 -0.00000000   0.00000000     0.29148687   0.00000000     0.00000000   0.00000000
  0.00000000   0.00000000    -0.00000000   0.00000000     0.29148687   0.00000000

     Diagonalizing the dynamical matrix

     q = (    0.000000000   0.000000000   0.000000000 )

 **************************************************************************
     freq (    1) =      -0.167455 [THz] =      -5.585702 [cm-1]
 (  0.380481  0.000000 -0.307987  0.000000  0.510273  0.000000 )
 (  0.380481  0.000000 -0.307987  0.000000  0.510273  0.000000 )
     freq (    2) =      -0.167455 [THz] =      -5.585702 [cm-1]
 (  0.543632  0.000000 -0.068841  0.000000 -0.446906  0.000000 )
 (  0.543632  0.000000 -0.068841  0.000000 -0.446906  0.000000 )
     freq (    3) =      -0.167455 [THz] =      -5.585702 [cm-1]
 (  0.244332  0.000000  0.632776 -0.000000  0.199742 -0.000000 )
 (  0.244332  0.000000  0.632776 -0.000000  0.199742 -0.000000 )
     freq (    4) =      15.700807 [THz] =     523.722541 [cm-1]
 (  0.160426  0.000000  0.688656 -0.000000 -0.004058  0.000000 )
 ( -0.160426  0.000000 -0.688656  0.000000  0.004058  0.000000 )
     freq (    5) =      15.700807 [THz] =     523.722541 [cm-1]
 ( -0.087474  0.000000  0.016244  0.000000 -0.701487  0.000000 )
 (  0.087474  0.000000 -0.016244  0.000000  0.701487  0.000000 )
     freq (    6) =      15.700807 [THz] =     523.722541 [cm-1]
 (  0.683090  0.000000 -0.159653  0.000000 -0.088877  0.000000 )
[preston@preston-System-Product-Name gamma-phonon]$
```


头部记录了元素、晶胞和原子位置。这里 `alat=10.2 Bohr`，原子行的 `tau` 是以 alat 为单位的笛卡尔坐标；第二个 Si 位于 `(0.25,0.25,0.25) alat`。换成 Å 时，将这三个数乘以 alat 的 Å 值。这与[父 SCF 输出](/Atlas/examples/si-pbe/scf/scf.out)中的 `positions (alat units)` 一致；[QE 7.5 的写出代码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/io_dyn_mat_old.f90)直接将 `tau` 保存到头部。

接着的 `q = (0,0,0)` 指明 Γ 点。`1 1`、`1 2`、`2 1`、`2 2` 是四个原子对矩阵块，每块包含三个笛卡尔方向的复数分量。再往下到 `Diagonalizing` 段，才开始列出频率和模式向量。

看第一个模式下面的两行：两个 Si 的向量完全相同。每行六个数按 x、y、z 的实部和虚部成对排列；这里虚部为零。两个同质量原子同向运动，对应整体平移。第四个模式的两行则反号，是两个原子相向运动的光学模式。这个区别把“前三个负值”与“Γ 点平移模式”联系起来，比单看频率接近零更有依据。

`.dyn` 头部的质量采用程序内部单位。核对 Si 的原子质量时，读 `ph.in` 的 `amass(1)=28.085` 和 `ph.out` 中标明的 `mass`，而不是将头部的 `25597.911...` 按 amu 使用。

## 对同一份矩阵做两次 dynmat 对照

先保留原矩阵不动。第一份输入关闭 ASR，第二份只改变 ASR 与输出文件名；两份都读取 `si.dynG`：


```text
[preston@preston-System-Product-Name gamma-phonon]$ cat dynmat-no.in
&INPUT
  fildyn = 'si.dynG'
  asr = 'no'
  filout = 'si-no.modes'
  filmol = 'si-no.mold'
/
[preston@preston-System-Product-Name gamma-phonon]$
```


```text
[preston@preston-System-Product-Name gamma-phonon]$ cat dynmat-crystal.in
&INPUT
  fildyn = 'si.dynG'
  asr = 'crystal'
  filout = 'si-crystal.modes'
  filmol = 'si-crystal.mold'
/
[preston@preston-System-Product-Name gamma-phonon]$
```


这里使用的是 QE 7.5 的 `dynmat.x`。复跑这组后处理时，在该目录依次执行：

```bash
<qe_bin>/dynmat.x -in dynmat-no.in > dynmat-no.out 2> dynmat-no.err
<qe_bin>/dynmat.x -in dynmat-crystal.in > dynmat-crystal.out 2> dynmat-crystal.err
```

两次运行没有重新做 SCF 或 DFPT，只是重新读取这份 Γ 矩阵。`asr='no'` 保留未施加规则的结果；`asr='crystal'` 对矩阵施加三个平移声学和规则。先看关闭 ASR 时输出的结果段：


```text
# mode   [cm-1]    [THz]      IR
    1     -5.59   -0.1675    0.0000
    2     -5.59   -0.1675    0.0000
    3     -5.59   -0.1675    0.0000
    4    523.72   15.7008    0.0000
    5    523.72   15.7008    0.0000
    6    523.72   15.7008    0.0000
```


再看施加 ASR 的结果段：


```text
     Acoustic Sum Rule: || Z*(ASR) - Z*(orig)|| =    0.000000E+00
     Acoustic Sum Rule: ||dyn(ASR) - dyn(orig)||=    1.148869E-04

# mode   [cm-1]    [THz]      IR
    1     -0.00   -0.0000    0.0000
    2     -0.00   -0.0000    0.0000
    3      0.00    0.0000    0.0000
    4    523.72   15.7008    0.0000
    5    523.72   15.7008    0.0000
    6    523.72   15.7008    0.0000
```


ASR 后三支平移模回到零附近，后三支光学模在这里显示的精度内保持不变。`1.148869E-04` 记录的是动力学矩阵的改变量；它与频率的单位和含义不同。IR 列为零，是因为这次没有计算有效电荷，不能据此判断红外活性。

`.modes` 文件保留了更多位数：ASR 后前三支分别是 −0.000009、−0.000001、0.000008 cm⁻¹。它们与原来的 −5.59 cm⁻¹ 相差了几个数量级。原 `ph.x` 打印 −5.585702，而重新读入文本矩阵的 `dynmat` 得到 −5.586079；文件中的矩阵分量只有有限小数位，这两组读数应分别保留，不要悄悄改成完全相同。

简并的三个模式可以在同一子空间内重新选取方向，所以两次 `.modes` 的逐个向量不必逐项相同。判断整体平移时看各原子之间的相对运动，比较光学频率时看整个简并组。

输入中的 `filout` 将动力学矩阵本征矢除以原子质量平方根，再归一化为原子位移；`fileig` 则保存正交本征矢。本次没有设置 `fileig`，下面的模式分析读取两份 `.modes`。两个 Si 质量相同，质量因子不改变它们的相对方向；多元素结构的位移权重与本征矢权重通常不同，使用时应注明所读文件。[dynmat.x 的字段说明](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html)给出了这两种输出的定义。

`filmol` 另存了可供 Molden 显示的文件。把这份已有结果复制到后处理目录后，先看它的频率表：

```text
[talos@talos-MS-7D54 si-gamma-modes]$ head -n 8 si-no.mold
[Molden Format]
[FREQ]
    0.00
    0.00
    0.00
  523.72
  523.72
  523.72
[talos@talos-MS-7D54 si-gamma-modes]$
```

`si-no.mold` 属于未施加 ASR 的分支，却把前三支写成了 `0.00`，丢掉了负频率标签。查看振动方向时可以使用其位移段；核对频率符号与数值时，仍读取 `ph.out`、`si.dynG` 和对应的 `.modes`。

另外，两份历史输入都没有设置 `filxsf`，因而先后写入默认的 `dynmat.axsf`；下载包保留的是后运行的 `crystal` 分支。若复跑时还想对照两套 XCrySDen 文件，可用 `vi` 分别给两个输入设置 `filxsf='si-no.axsf'`、`filxsf='si-crystal.axsf'` 后再运行。不能把一份默认文件当作两次结果。

## 由同一矩阵判断 Γ 点负频是否属于平移残差

`si-no.modes` 和 `si-crystal.modes` 来自同一份 `si.dynG`，分别对应 `asr='no'` 与 `asr='crystal'`。接下来用频率和逐原子位移一起判断：变化是否发生在整体平移模式，光学模式是否仍保持原来的频率。

图的左面板放大前三支声学模，并画出零线；右面板显示光学模，纵轴范围单独标明。未施加 ASR 时，声学三模约为 −5.586079 cm⁻¹；施加 `asr='crystal'` 后回到零附近，光学三模仍约为 523.722542 cm⁻¹。结合前面两个原子的同向位移，可以将本例的 Γ 点负值解释为平移声学和规则残差。其他 q 点的模式要在相应动力学矩阵中继续检查。

![同一 Si Γ 点矩阵在 ASR 前后的频率对照；声学与光学面板使用不同纵轴范围](/Atlas/examples/stability-imaginary-si/si-gamma-asr.svg)

### 输入字段与变换

后处理脚本从每条 `freq (i)` 行最后一个等号后的 `[cm-1]` 数值读取频率。每个模式的两行位移按 x 实部/虚部、y 实部/虚部、z 实部/虚部配成复数向量；脚本同时核对 Γ 点、六个连续模式、每模两个原子和打印精度内的向量范数。

原子位置由 $r=\tau\times\mathrm{alat}$ 得到，alat 先按 `0.529177210903 Å/Bohr` 换算为 Å；频率为 cm⁻¹，`.modes` 位移分量无量纲。

对这两个等质量 Si 原子，脚本计算 $P_T=\frac{\lVert u_1+u_2\rVert^2}{2(\lVert u_1\rVert^2+\lVert u_2\rVert^2)}$。同向同幅运动给出 1，反向同幅运动给出 0。简并模式的方向可在子空间内重新选择，因此脚本另将前三模和后三模分别正交化，比较 ASR 前后的子空间投影矩阵。这里的等权公式针对当前两原子等质量 Γ 点数据。

### 运行后处理并读取结果

实跑环境为 Talos 上 Python 3.12.3、NumPy 2.4.6、Matplotlib 3.11.1。复画命令：

```bash
python3 analyse_modes.py > analysis.out
python3 plot_asr.py
```

本次实际输出：

```text
ASR=no: modes=6, atoms=2, max |norm-1|=3.094e-07
  translation fraction: 1.000000 1.000000 1.000000 0.000000 0.000000 0.000000
ASR=crystal: modes=6, atoms=2, max |norm-1|=4.353e-07
  translation fraction: 1.000000 1.000000 1.000000 0.000000 0.000000 0.000000
acoustic projector difference: 5.489e-16
optical projector difference: 5.439e-16
Wrote mode-diagnostics.csv, mode-vectors.csv, mode-checks.json
asr-comparison.csv; si-gamma-asr.svg/png/pdf
```

前三模的平移成分为 1，后三模为 0，与前面直接读到的同向、反向运动一致。范数偏差约为 `10⁻⁷`，来自文件有限小数位；ASR 前后约 `10⁻¹⁶` 的子空间差说明这些舍入向量张成的空间相同。这个数描述向量比较，不能用作 DFT 频率的误差条。

### 可直接复制给 AI 编程助手的任务说明

```text
读取同目录中的 si-no.modes、si-crystal.modes 和 si.dynG，针对这个 QE 7.5 两原子等质量 Si Γ 点算例生成诊断数据与一张 ASR 频率对照图。保留原始文件；解析约定限定于下面的两原子等质量 Γ 点数据。

输入和单位：
- .modes 的 freq (i) 行末 [cm-1] 数值是频率，保留负号。
- 每个模式后两行各有六列实部/虚部位移，顺序 x、y、z；这是 dynmat.x filout 的质量除权归一化分量，不是 Å 位移。
- 从 si.dynG 头部读取 alat（Bohr）和以 alat 为单位的笛卡尔坐标 tau；用 0.529177210903 Å/Bohr 将 alat 转成 Å，再计算 r=tau*alat。这里 tau 不是 crystal 分数坐标，不乘原胞基矢矩阵。
- 本例平移分量为 P_T=||u1+u2||²/[2(||u1||²+||u2||²)]，只适用于两颗等质量 Si。按 1–3、4–6 模分别构造正交化子空间投影，比较 ASR=no 与 ASR=crystal 的 Frobenius 范数差。
- 先验证 q=(0,0,0)、六个连续模式、每模式恰有两行向量、所有字段有限、范数符合打印精度；不匹配就明确报错，不猜测、不静默跳过、不覆盖输入。
- 写出 mode-diagnostics.csv、mode-vectors.csv、mode-checks.json、asr-comparison.csv；只生成 ASR 前后的频率图。声学面板画零线并放大负频区，光学面板单独标明范围。单位写 cm-1，不要把负频改成零。
- 用 NumPy 和 Matplotlib，记录实际运行命令、stdout 与输出文件。
```

完整数据和脚本：[si-no.modes](/Atlas/examples/stability-imaginary-si/si-no.modes)、[si-crystal.modes](/Atlas/examples/stability-imaginary-si/si-crystal.modes)、[si.dynG](/Atlas/examples/stability-imaginary-si/si.dynG)、[analyse_modes.py](/Atlas/examples/stability-imaginary-si/analyse_modes.py)、[plot_asr.py](/Atlas/examples/stability-imaginary-si/plot_asr.py)、[atlas_plot_style.py](/Atlas/examples/stability-imaginary-si/atlas_plot_style.py)。输出有[诊断表](/Atlas/examples/stability-imaginary-si/mode-diagnostics.csv)、[向量表](/Atlas/examples/stability-imaginary-si/mode-vectors.csv)、[检查 JSON](/Atlas/examples/stability-imaginary-si/mode-checks.json)和[频率对照 CSV](/Atlas/examples/stability-imaginary-si/asr-comparison.csv)；所有文件均收在[下载包](/Atlas/examples/stability-imaginary-si-files.tar.gz)。


<details>
<summary>analyse_modes.py 完整源码</summary>

```python
"""Read the two saved QE 7.5 Si Gamma displacement files; no DFT rerun.

Run in this directory: python3 analyse_modes.py
Requires NumPy. This intentionally validates only the supplied equal-mass,
two-atom Si Gamma example. It is not a general phonon file converter.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parent
BOHR_ANGSTROM = 0.529177210903
NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[EeDd][-+]?\d+)?"

def number(text):
    return float(text.replace("D", "E").replace("d", "e"))

def modes(filename):
    text = (ROOT / filename).read_text()
    q = re.search(r"q\s*=\s*("+NUMBER+r")\s+("+NUMBER+r")\s+("+NUMBER+r")", text)
    if q is None or not np.allclose([number(x) for x in q.groups()], 0, atol=1e-12, rtol=0):
        raise ValueError("This diagnostic requires Gamma: " + filename)
    pattern = re.compile(r"freq\s*\(\s*(\d+)\)\s*=.*?=\s*("+NUMBER+r")\s*\[cm-1\]")
    hits = list(pattern.finditer(text))
    if [int(m[1]) for m in hits] != list(range(1, 7)):
        raise ValueError("Expected six consecutive modes: " + filename)
    frequencies, vectors = [], []
    for i, hit in enumerate(hits):
        end = hits[i+1].start() if i+1 < len(hits) else len(text)
        rows = re.findall(r"^\s*\(\s*([^\n]+?)\s*\)\s*$", text[hit.end():end], re.M)
        if len(rows) != 2:
            raise ValueError("Expected two atomic vectors per mode: " + filename)
        values = np.array([[number(s) for s in row.split()] for row in rows])
        if values.shape != (2, 6) or not np.isfinite(values).all():
            raise ValueError("Expected six finite real/imaginary columns per atom")
        frequencies.append(number(hit[2]))
        vectors.append(values[:, 0::2] + 1j*values[:, 1::2])
    return np.array(frequencies), np.array(vectors)

def geometry():
    lines = (ROOT / "si.dynG").read_text().splitlines()
    header = lines[2].split()
    if [int(x) for x in header[:3]] != [1, 2, 2] or "'Si" not in lines[3]:
        raise ValueError("Expected this two-atom, one-species fcc Si matrix")
    alat = number(header[3]) * BOHR_ANGSTROM
    rows = [line.split() for line in lines[4:6]]
    if [(int(x[0]), int(x[1])) for x in rows] != [(1, 1), (2, 1)]:
        raise ValueError("Unexpected atom/species order")
    # QE .dyn tau is Cartesian in units of alat, not crystal fractional coordinates.
    return alat, np.array([[number(x) for x in row[2:5]] for row in rows])*alat

def projector(vectors):
    matrix = vectors.reshape(3, 6).T
    if np.linalg.matrix_rank(matrix, tol=1e-7) != 3:
        raise ValueError("A three-mode group lost rank")
    q, _ = np.linalg.qr(matrix)
    return q @ q.conj().T

def write_csv(name, header, rows):
    with (ROOT / name).open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)

alat, positions = geometry()
sets = {name: modes(filename) for name, filename in
        [("no", "si-no.modes"), ("crystal", "si-crystal.modes")]}
translation_basis = np.vstack([np.eye(3), np.eye(3)]) / np.sqrt(2)
p_translation = translation_basis @ translation_basis.T
records, arrows = [], []
summary = {"case": "Si, two equal-mass atoms, Gamma, fixed example geometry",
           "numpy_version": np.__version__, "alat_angstrom": alat,
           "input_position_convention": "Cartesian tau in units of alat (QE .dyn header)",
           "position_transform": "r_angstrom = tau_cartesian_alat * alat_angstrom",
           "mode_vector_convention": "dynmat filout: eigenvectors divided by sqrt(mass), then normalized",
           "scope": "Diagnostics of rounded filout displacements; no new phonon calculation",
           "maximum_imaginary_component": 0.0, "sets": {}, "subspace_comparison": {}}
for name, (frequencies, u) in sets.items():
    if not np.isfinite(frequencies).all():
        raise ValueError("Nonfinite frequency")
    norm = np.linalg.norm(u.reshape(6, 6), axis=1)
    if not np.allclose(norm, 1, atol=3e-6, rtol=0):
        raise ValueError("Displacements not normalized to printed precision")
    imaginary = float(np.max(np.abs(u.imag)))
    if imaginary > 1e-12:
        raise ValueError("This real-vector diagnostic requires the supplied real Gamma modes")
    summary["maximum_imaginary_component"] = max(summary["maximum_imaginary_component"], imaginary)
    same = np.linalg.norm(u[:, 0]-u[:, 1], axis=1)/norm
    opposite = np.linalg.norm(u[:, 0]+u[:, 1], axis=1)/norm
    fraction = np.sum(np.abs(u[:, 0]+u[:, 1])**2, axis=1)/(2*norm**2)
    if np.any(fraction < -1e-12) or np.any(fraction > 1+1e-12):
        raise ValueError("Invalid projection fraction")
    acoustic = projector(u[:3])
    optical = projector(u[3:])
    gram = (u.reshape(6, 6)/norm[:, None]) @ (u.reshape(6, 6)/norm[:, None]).conj().T
    summary["sets"][name] = {
        "max_norm_deviation": float(np.max(np.abs(norm-1))),
        "max_gram_deviation": float(np.max(np.abs(gram-np.eye(6)))),
        "acoustic_translation_projector_frobenius": float(np.linalg.norm(acoustic-p_translation)),
        "optical_translation_projector_frobenius": float(np.linalg.norm(optical-(np.eye(6)-p_translation))),
        "acoustic_frequency_range_cm-1": [float(x) for x in (frequencies[:3].min(), frequencies[:3].max())],
        "optical_frequency_range_cm-1": [float(x) for x in (frequencies[3:].min(), frequencies[3:].max())]}
    for i in range(6):
        records.append([name, i+1, frequencies[i], norm[i], same[i], opposite[i], fraction[i]])
        for atom in range(2):
            arrows.append([name, i+1, atom+1, *positions[atom], *u[i, atom].real, *u[i, atom].imag])
    print(f"ASR={name}: modes=6, atoms=2, max |norm-1|={np.max(np.abs(norm-1)):.3e}")
    print("  translation fraction: " + " ".join(f"{x:.6f}" for x in fraction))
for label, group in [("acoustic", slice(0, 3)), ("optical", slice(3, 6))]:
    delta = float(np.linalg.norm(projector(sets["no"][1][group])-projector(sets["crystal"][1][group])))
    summary["subspace_comparison"][label+"_projector_frobenius"] = delta
    print(f"{label} projector difference: {delta:.3e}")
summary["sha256"] = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
                     for f in ["si-no.modes", "si-crystal.modes", "si.dynG"]}
write_csv("mode-diagnostics.csv", ["asr", "mode", "frequency_cm-1", "displacement_norm",
          "same_displacement_residual", "opposite_displacement_residual", "translation_fraction"], records)
write_csv("mode-vectors.csv", ["asr", "mode", "atom", "x_angstrom", "y_angstrom", "z_angstrom",
          "ux_real", "uy_real", "uz_real", "ux_imag", "uy_imag", "uz_imag"], arrows)
(ROOT/"mode-checks.json").write_text(json.dumps(summary, indent=2)+"\n")
print("Wrote mode-diagnostics.csv, mode-vectors.csv, mode-checks.json")
```

</details>

<details>
<summary>plot_asr.py 完整源码</summary>

```python
"""Compare two dynmat runs of one unchanged Si Gamma matrix.

Run next to si-no.modes and si-crystal.modes. Needs NumPy and Matplotlib.
Numbers are read from files; negative frequencies are never clipped.
"""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def frequencies(filename):
    text = Path(filename).read_text()
    values = re.findall(r"freq\s*\(\s*\d+\)\s*=.*?=\s*([-+\d.Ee]+)\s*\[cm-1\]", text)
    result = np.array([float(value) for value in values])
    if len(result) != 6 or not np.isfinite(result).all():
        raise ValueError(f"Expected six finite Gamma frequencies in {filename}")
    return result

raw = frequencies("si-no.modes")
asr = frequencies("si-crystal.modes")
with open("asr-comparison.csv", "w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["mode", "no_asr_cm-1", "crystal_asr_cm-1", "change_cm-1"])
    writer.writerows((i + 1, x, y, y - x) for i, (x, y) in enumerate(zip(raw, asr)))

plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none"})
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.7))
for ax, indices, title in [(axes[0], np.arange(3), "Acoustic modes (zoom)"),
                            (axes[1], np.arange(3, 6), "Optical modes")]:
    x = indices + 1
    ax.scatter(x - .08, raw[indices], s=70, facecolors="none",
               edgecolors="#0072b2", linewidths=1.6, label="ASR = no", zorder=3)
    ax.scatter(x + .08, asr[indices], s=50, marker="x", color="#d55e00",
               linewidths=1.8, label="ASR = crystal", zorder=3)
    ax.set(xticks=x, xlabel="Mode index", title=title, ylabel="Frequency (cm$^{-1}$)")
    ax.grid(axis="y", alpha=.18)
axes[0].axhline(0, color="#404040", lw=.8)
axes[0].set_ylim(-6.4, 1.0)
axes[0].text(2, -5.0, "-5.586079 → about 0", ha="center", fontsize=10)
axes[1].set_ylim(520, 528)
axes[1].text(5, 525, "523.722542 in both runs", ha="center", fontsize=10)
axes[0].legend(frameon=False, loc="center right")
fig.suptitle("Si at Γ: diagonalize the same matrix twice", x=.09, ha="left", fontsize=15)
fig.text(.09, .895, "QE 7.5 · fixed input structure · two separate vertical scales", fontsize=10, color="#555555")
fig.tight_layout(rect=(0, 0, 1, .87))
for ext in ("svg", "png", "pdf"):
    fig.savefig(f"si-gamma-asr.{ext}", dpi=180, facecolor="white")
print("asr-comparison.csv; si-gamma-asr.svg/png/pdf")
```

</details>

## 从 Γ 平移残差读到界面低频模

Si 的矩阵块已经给出一个直接联系：对角分量 0.29148687 与跨原子分量 −0.29155320 几乎抵消。同向移动时两者相加，剩下小的负曲率；反向移动时两者相减，得到约 523.72 cm⁻¹ 的光学振动。ASR 约束的是前一种整体平移。它的作用不是把所有负频模式改成零。

异质结的 Γ 点包含整个结构的平移，也可以包含两层之间的剪切和呼吸。整体平移要求各原子的实际位移 u 相同；在质量加权本征矢 e 中，对应分量应随 √M 变化，不能要求不同元素的 e 逐项相同。两层反向移动则保留相对位移，它可能是稳定低频光学模，也可能因堆叠或层间距不合适而出现负曲率。应先看逐原子位移，再解释 ASR 前后发生变化的是哪组模式。

二维自由薄层的 ZA 支在无外部张力、满足相应不变性的长波极限通常呈二次色散。靠近 Γ 的小负值还需要结合受约束应变下的应力、旋转不变性和 q 采样解释；`asr='crystal'` 只实施三条平移规则，不能由 Si 的 Γ 结果推断任意二维 ZA 支的形状都已修正。

本例已有[crystal 分支的 XCrySDen 动画文件](/Atlas/examples/stability-imaginary-si/dynmat.axsf)和[位移表](/Atlas/examples/stability-imaginary-si/mode-vectors.csv)。AXSF 用于查看实际位移方向，频率和 ASR 分支仍由对应的 `.modes` 确定。显示时使用整模共同的放大系数，保留原子之间的相对振幅；静态箭头只显示一个相位，不给出热振幅。界面的独立 +1.5% Γ 对照已从真实矩阵导出[模式与动画](/Atlas/m/phonon-dfpt/qe/#h-一组真实界面-γ-模式的矩阵与位移)，Si 的模式文件与它分别使用。

ZrCl₂/Sc₂C 的[Γ32 原始矩阵](/Atlas/examples/phonons-interface-gamma/gamma32.dyn)把这个差别进一步具体化：原始最低双态为约 33.93344 cm⁻¹，第三支为 56.973656 cm⁻¹，它们的整体平移投影权重分别约为 0.913、0.913、0.792，包含平移与相对运动混合。采用同一平移投影后，三支整体平移回到数值零，最低光学双态为 75.22373 cm⁻¹。与 Si 不同，这份界面矩阵的部分光学频率也明显变化；所以不能用“前三支回零”代替对 ASR 改变量与光学运动的检查。这里的矩阵来自 +1.5% 固定结构 Γ 对照，不能据此说明整个异质结 q 空间无虚频。

## 有限 q 软模对应什么结构变化

有限 q 振动在不同晶胞间有相位差。若 q 用倒格矢分数坐标表示，对超胞的每个平移矢量 L 都要求 $\mathbf q\cdot\mathbf L$ 为整数，模式才满足该超胞的周期。对于一般复本征矢，一个真实位移图案可写为

$$
\Delta r_{I\alpha}(\mathbf R)=A\,\mathrm{Re}\left[\frac{e_{I\alpha}(\mathbf q\nu)}{\sqrt{M_I}}\,e^{i(\mathbf q\cdot\mathbf R+\phi)}\right].
$$

这里采用相位只含晶胞平移 R 的约定；若向量定义含原子基矢位置 τ，转换时也要保留相应相位。A 是整模共同尺度，φ 决定所取的真实相位。动画中的放大幅度不等于用于能量比较的有限位移幅度。

[Ba₂N 原文 Fig. 6(a,e) 与附录 Fig. 8](https://doi.org/10.1103/PhysRevB.105.165101)给出了“软化”与“负曲率”的具体比较。Fig. 6 位于 165101-5 页：4% 双轴拉伸的 Γ–M–K–Γ 色散用 cm⁻¹ 表示频率，K 附近约 24 cm⁻¹ 的声学模仍在零线上方；(e) 用 √3×√3 超胞将 K 折叠到 Γ，展示 Ba 的面内/面外混合运动与 N 的面内运动。原文第 4 页说明了这一步折叠。Fig. 8 位于 165101-6 页，同一路径的 5% 应变结果在 K 附近进入零线下方，Γ 附近的平移零频与这段有限波矢负频可以直接分开。Fig. 6(a) 的红点表示线宽，Fig. 6(e) 的箭头表示位移；这两张图没有以箭头长度或点面积测量负曲率。

本页已有 Si 图把 Γ 声学残差与光学频率分成两个坐标范围，适合观察同矩阵 ASR 改变量；它不能替代 Fig. 8 那种有限 q 检查。绘制自己的路径时，应保留真实负频、零线和各节点对应的行号，比较不同应变时统一频率单位及纵轴范围；路径累计距离只用于绘图，模式仍由倒格矢分数 q 定位。查看有限 q 位移还需在相容超胞中保留跨胞相位，再由成熟结构查看器显示同一相位的俯视和侧视；当前可直接打开的 Si 与界面 AXSF 都是 Γ 数据，不生成一个未经计算的 K 模图。

若在自己的界面路径中看到负值，先由同一行的 q 坐标定位模式，而不是使用图的累计路径距离。已有原始网格包含该 q 时，直接比较它的矩阵与插值结果；只有插值处出现的异常则需要该 q 的直接结果。随后，沿相容超胞中的真实模分别施加正负小位移，查看能量与力是否沿该方向降低，再决定是否弛豫到新的构型。频率软化仍为正时，只说明恢复力减弱；出现非平移负曲率时才有离开当前构型的方向。

## 电子占据怎样影响金属软模

金属模式会随 k 网格与占据展宽变化，因为力常数包含费米面附近的电子响应。比较同一 q 时保持结构与向量定义一致，并通过模式重叠或简并组追踪运动。冷展宽或 Gaussian 的宽度是积分参数，不能直接当作离子温度；Fermi–Dirac 占据宽度可以参数化电子温度，也仍需与离子热运动区分。

Si 在本例使用固定占据，没有做展宽扫描。界面中的 K 软模若要解释成电荷密度波或 Kohn 异常，应将该模式与电子响应、畸变结构和能量联系起来；仅在一张插值图上看到凹陷还没有识别机制。涉及 EPC 时，先保留 ω² 的符号和原始向量，解释当前结构的振动问题，再进入[谱函数积分](/Atlas/m/eliashberg-a2f/qe/)。

## 参考资料

[PHonon 负频与 ASR 说明](https://www.quantum-espresso.org/Doc/ph_user_guide/node18.html) · [dynmat.x](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html) · [matdyn.x](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [Ba₂N Fig. 6、8](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.105.165101)
