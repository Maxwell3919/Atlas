这次在 Preston 上用 QE 7.5 计算金刚石 Si。原胞有两个原子，Γ 点应有六个振动模式；`ph.x` 打印的前三个频率却是 −5.585702 cm⁻¹。接下来就从这六行输出开始：先看计算是否做完，再看哪些原子在怎样移动，最后对同一份矩阵作 ASR 对照。

这里沿用 QE 随附 Si 例子的固定晶胞，常规立方晶格参数为 5.397607551 Å，使用 PBE、Si 的 USPP、60/640 Ry 截断和 8×8×8 电子网格。本例固定这份晶胞，未重新优化 Si 晶格。SCF 的操作见[固定结构计算](/Atlas/m/scf/qe/)，本例配套的[完整 SCF 输入](/Atlas/examples/si-pbe/scf/scf.in)和[输出](/Atlas/examples/si-pbe/scf/scf.out.txt)也一起保留；换算例时不要复制其他材料的保存目录。

QE 用负数标记动力学矩阵的负本征值，也就是 ω² < 0。这里打印 −5.59 的含义是一个虚频，而不是“振动反方向传播”。至于它来自数值误差还是结构的真实不稳定，要继续看证据，不能由大小一项直接决定。

本页的 QE 输入/输出、动力学矩阵、两份 .modes 文件和后处理脚本可[一起下载](/Atlas/examples/stability-imaginary-si-files.tar.gz)。解包后进入 stability-imaginary-si 目录查看记录和复画图。诊断包不含 SCF XML 或波函数保存目录。若要重算上游响应，另下载[Si 教学输入/输出包](/Atlas/examples/si-pbe-lesson-files.tar.gz)，先按下文完成一致参数的 SCF；该包也不替代 SCF 运行后生成的保存目录。

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

这些文件不是同一层次的结果：看到 `.dyn` 不能跳过 `ph.out`，而看到 `.modes` 也不能反推上游全部 q 点已完成。这里从始至终只有一个直接计算的 Γ 点。

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

`tr2_ph=1.0d-14` 控制每个扰动表示的响应自洽停止条件。这里先把响应求解做得较紧，再观察平移模式；这个数本身并不保证频率误差小于某个 cm⁻¹。收紧它只能继续迭代当前电子参数下的响应，不能补上不足的 cutoff 或 k 网格，后面仍要看实际残差、表示的收敛行和同一模式的参数对照。

如果要重算，应先完成上面链接中的 Si SCF。将原有 Si 教学包解压为 si-pbe，再把本页诊断包解压到同一父目录；以下命令从 si-pbe 目录建立独立复算目录，不覆盖原计算：

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

核对 `tmp/si.save` 中的结构、赝势和电子设置属于刚完成的这份 Si SCF，并将脚本中的 `<qe_bin>` 改为本机的实际路径。确认后执行 `sbatch run.sh`。公开包里单独保留的 XML 不能替代这份保存目录。

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

`768` 是这一次的作业号，重跑时换成 `sbatch run.sh` 返回的号码。退出 `tail -f` 的 Ctrl-C 只结束查看。这里的 MPI 亲和性曾与同时运行的教学任务重叠，运行中已调整本批进程的绑定；耗时因此只代表这一轮实际运行，不能用来估算独占资源下的效率。

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


`thresh` 是内层求解信息，不能直接拿它代替输入的 `tr2_ph`。这里的响应残差 `|ddv_scf|²` 从 `4.579E-14` 降到 `5.675E-16`，随后打印这组表示的收敛行；只读第一组还不够，第二组也需要分别检查。把两组表示和末尾频率一起定位出来：


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


最前面是元素、晶胞和两个原子的坐标。这里 `alat=10.2 Bohr`，原子行的 `tau` 是以 alat 为单位的笛卡尔坐标；第二个 Si 位于 `(0.25,0.25,0.25) alat`，不是原胞晶格基矢下的分数坐标。这与[父 SCF 输出](/Atlas/examples/si-pbe/scf/scf.out)中的 `positions (alat units)` 一致；[QE 7.5 矩阵写出代码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/io_dyn_mat_old.f90)将该 `tau` 直接写入头部。`q = (0,0,0)` 说明这是 Γ 点。中间 `1 1`、`1 2`、`2 1`、`2 2` 四个块对应原子对，每块有三个方向的复数分量。后面的 `Diagonalizing` 段才是频率和模式向量，不能把矩阵块里的某个负数当成虚频。

看第一个模式下面的两行：两个 Si 的向量完全相同。每行六个数按 x、y、z 的实部和虚部成对排列；这里虚部为零。两个同质量原子同向运动，对应整体平移。第四个模式的两行则反号，是两个原子相向运动的光学模式。这个区别把“前三个负值”与“Γ 点平移模式”联系起来，比单看频率接近零更有依据。

`.dyn` 头部的质量以程序内部单位保存，不能把 `25597.911...` 当成 amu。核对元素质量时，读 `ph.in` 以及 `ph.out` 中明确标成 `mass` 的 28.0850；没有弄清文件单位前不要直接修改原矩阵。

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


这里不能只看前三行变成了零：后三个光学模式在所示精度内也保持不变。矩阵变化量 `1.148869E-04` 不是频率，也不是“误差小于这个数就合格”的阈值；它记录这次 ASR 对矩阵的改变量。输出中的 IR 列为零也不能用于讨论红外强度，因为本次没有计算有效电荷。

`.modes` 文件保留了更多位数：ASR 后前三支分别是 −0.000009、−0.000001、0.000008 cm⁻¹。它们与原来的 −5.59 cm⁻¹ 相差了几个数量级。原 `ph.x` 打印 −5.585702，而重新读入文本矩阵的 `dynmat` 得到 −5.586079；文件中的矩阵分量只有有限小数位，这两组读数应分别保留，不要悄悄改成完全相同。

简并的三个模式可以在同一子空间内重新选取方向，所以两次 `.modes` 的逐个向量不必逐项相同。判断整体平移时看各原子之间的相对运动，比较光学频率时看整个简并组。

这里还要区分位移文件的含义。输入里的 `filout` 写出的是先除以原子质量平方根、再归一化的**原子位移**；`fileig` 才对应动力学矩阵的正交本征矢输出。本次没有设置 `fileig`，后面画箭头只读两份 `.modes`。这两个 Si 质量相同，质量因子不会改变两个原子之间的相对方向；换成不同质量的多元素结构时，不能把位移分量直接当成等权的本征矢分量。[dynmat.x 的文件定义](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html)说明了这一区别。

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

这份 **`si-no.mold` 的负频率标签已经丢失**：它属于未施加 ASR 的分支，却把前三支写成了 `0.00`。因此，不能根据 Molden 中的零值判断虚频已经消失；频率的符号和数值仍回到原始 `.dyn`、`ph.out` 和对应 `.modes` 核对。文件后面的位移段可以帮助查看原子运动，但显示文件不能替代这些数值记录。

另外，两份历史输入都没有设置 `filxsf`，因而先后写入默认的 `dynmat.axsf`；下载包保留的是后运行的 `crystal` 分支。若复跑时还想对照两套 XCrySDen 文件，可用 `vi` 分别给两个输入设置 `filxsf='si-no.axsf'`、`filxsf='si-crystal.axsf'` 后再运行。不能把一份默认文件当作两次结果。

## 由同一矩阵判断 Γ 点负频是否属于平移残差

比较对象是两次 `dynmat.x` 对同一 `si.dynG` 的对角化：`si-no.modes` 使用 `asr='no'`，`si-crystal.modes` 使用 `asr='crystal'`。每份文件的 `freq (i)` 行末是模式频率，单位 cm⁻¹；后接的两行各含一个 Si 原子的位移。每行六个实数按 x、y、z 方向的实部与虚部交错排列。这些向量是 QE `filout` 写出的、质量除权并归一化的无量纲位移；频率保留原符号，不把负数截到零。[QE 7.5 dynmat.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html)

下面比较同一矩阵在两种 ASR 设置下的频率。左面板放大声学模并画出零线，右面板显示光学模，两个纵轴尺度分别标明。图展示同一矩阵在两种 ASR 设置下的实际结果：未施加 ASR 时声学三模约为 −5.586079 cm⁻¹；`asr='crystal'` 后三支回到零附近，光学三模仍约为 523.722542 cm⁻¹。这个对照支持“本例 Γ 点负值是平移声学和规则残差”的判断，不检验其它 q 点，也不能推出整个布里渊区稳定。

![同一 Si Γ 点矩阵在 ASR 前后的频率对照；声学与光学面板使用不同纵轴范围](/Atlas/examples/stability-imaginary-si/si-gamma-asr.svg)

### 输入字段与变换

`si-no.modes` 和 `si-crystal.modes` 各有六条频率记录；解析器取每条 `freq (i)` 行最后一个等号后的 `[cm-1]` 数值，并检查模式编号连续且频率有限。每个模式后有两行位移，每行六列实数，顺序为 x 实部/虚部、y 实部/虚部、z 实部/虚部。解析器检查 Γ 点、两个原子、有限值及打印精度内的向量范数。

`analyse_modes.py` 将 `si.dynG` 头部的晶格参数从 Bohr 乘 `0.529177210903 Å/Bohr` 转成 Å，再将以 alat 为单位的笛卡尔坐标乘 alat，得到以 Å 为单位的原子位置。频率单位是 cm⁻¹，向量无量纲，原子位置单位是 Å。对这两个等质量 Si 原子，逐模平移成分采用 `P_T=||u₁+u₂||²/[2(||u₁||²+||u₂||²)]`；同向同幅给出 1，反向同幅给出 0。脚本另对声学三模和光学三模正交化，再比较子空间投影矩阵。该等权公式只适用于当前二原子 Γ 点例子，不可直接用于不同原子质量的晶体。QE 对 `filout` 位移和 `fileig` 正交本征矢有不同定义，见[官方输入说明](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html)。

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

前三模的平移投影为 1，后三模为 0。`10⁻¹⁶` 量级的子空间差只描述舍入后向量的线性代数比较，不是 DFT 频率精度；`10⁻⁷` 量级的范数偏差与 `.modes` 有限小数位相符。复画需要 NumPy 和 Matplotlib；重跑 `ph.x` 另需 QE 7.5 和匹配的 Si SCF save 目录，下载包没有包含波函数目录。

## 换成一张路径声子图时，先确定负值来自哪里

如果负值来自 `matdyn` 的插值图，先回到[DFPT 声子页](/Atlas/m/phonon-dfpt/qe/)认清文件关系。`.freq.gp` 通常是一行一个路径点：首列为累计路径坐标，其后才是频率；`.freq` 则带有表头、q 坐标和可能换行的频率记录，不能直接套同一段逐列扫描。

定位后，要记下这个点的 **q 坐标、模式、原始/插值来源和 ASR 设置**。横轴累计距离不是 q 的三个分量，不能直接拿去填 `ph.x`。如果已有原始网格点与它重合，先比较那个矩阵；若只在插值路径上出现异常，需要针对同一个实际 q 点做直接计算对照。

按负频出现的位置与模式特征选择下一项对照：

| 眼前现象 | 接着对照什么 | 对照后读什么 |
|---|---|---|
| 只有 Γ 附近平移模式偏离零 | 同矩阵的 ASR 前后、本征位移 | 平移模式是否回零，其他模式变化是否明显 |
| 同一 q 的频率随电子设置变化 | 保持结构和赝势，分别改 cutoff、电子网格或阈值 | 同一模式的频率变化，不能只比总能 |
| 金属的软模对展宽很敏感 | 配套增加 k 采样并比较展宽 | 是否形成稳定的频率趋势 |
| 插值有负值，直接网格点没有 | 该 q 的直接结果、不同 q 网格的插值 | 异常是否依赖插值或采样 |
| 明确非平移软模持续存在 | 对应本征位移、相容超胞和位移后的能量/力 | 是否有可继续弛豫的降能方向 |

最后一种情况才需要沿模式构造相容的畸变结构。在非 Γ 点，单胞里随手移动一个原子通常不能表示该波矢的周期位移；应先满足 q 与超胞周期的对应关系，再比较正负位移与后续弛豫。

## 文献中对软模与虚频物理起源的对照方式

单层 NbSi₂As₄ 的 Fig. 3a 追踪指定 q₁ 处最低 LA 模，扫描 Fermi–Dirac 电子占据展宽 σ。横轴为 σ（mRy），纵轴为声子频率（meV），零线区分虚频与正频。它展示了该模式对电子占据的敏感性；σ 不代表离子温度。分析软模机制时，还需结合相同结构下的 k 网格收敛、本征位移、电子响应和相容畸变能量。本页 Si 算例采用固定占据，未进行这项 σ 扫描。

<figure class="research-figure"><img src="/Atlas/figures/literature/M5_CDW_SmearingEvolution_NbSi2As4_PRB2025_Fig3a.jpg" alt="单层 NbSi2As4 最低软模声子频率随电子展宽 σ 的演化" loading="lazy"/><figcaption>单层 NbSi<sub>2</sub>As<sub>4</sub> 中指定 q₁ 处最低 LA 模频率随 Fermi–Dirac 电子占据展宽 σ 的变化；横轴为 mRy，纵轴为 meV，水平零线区分虚频与正频。引自 <em>Phys. Rev. B</em> <strong>111</strong>, L140508 (2025)，Fig. 3a，<a href="https://doi.org/10.1103/PhysRevB.111.L140508" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.111.L140508</a>。</figcaption></figure>

## 下一步

先用[收敛测试](/Atlas/m/convergence/qe/)的方法建立只改变一个量的对照，再回到[声子色散与原始 q 点](/Atlas/m/phonon-dfpt/qe/)扩大检查范围。如果正在准备 EPC，尚未解释的非平移虚频不能靠手工把负 ω² 改成零后继续积分；应先解决上游问题，再读取[谱函数](/Atlas/m/eliashberg-a2f/qe/)。

```text
负频率 → q 与原始矩阵 → 响应是否完成 → 本征位移
                                             ↓
                       同矩阵 ASR 对照 + 数值设置对照
                                             ↓
                         直接 q / 插值复核 → 后续声子或畸变
```

## 参考资料

参考：

- [PHonon：负频率与声学和规则的排查](https://www.quantum-espresso.org/Doc/ph_user_guide/node18.html)
- [ph.x 输入与单个 q 点计算](https://www.quantum-espresso.org/Doc/INPUT_PH.html)
- [dynmat.x：读取动力学矩阵与 ASR](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html)
- [matdyn.x：路径频率、本征矢与位移文件](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)
