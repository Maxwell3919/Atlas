参考：

- [PHonon：负频率与声学和规则的排查](https://www.quantum-espresso.org/Doc/ph_user_guide/node18.html)
- [ph.x 输入与单个 q 点计算](https://www.quantum-espresso.org/Doc/INPUT_PH.html)
- [dynmat.x：读取动力学矩阵与 ASR](https://www.quantum-espresso.org/Doc/INPUT_DYNMAT.html)
- [matdyn.x：路径频率、本征矢与位移文件](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。

## Γ 点出现 −5.59 cm⁻¹，先不要把负号删掉

这次在 Preston 上用 QE 7.5 计算金刚石 Si。原胞有两个原子，Γ 点应有六个振动模式；`ph.x` 打印的前三个频率却是 −5.585702 cm⁻¹。接下来就从这六行输出开始：先看计算是否做完，再看哪些原子在怎样移动，最后对同一份矩阵作 ASR 对照。

这里沿用 QE 随附 Si 例子的固定晶胞，常规立方晶格参数为 5.397607551 Å，使用 PBE、Si 的 USPP、60/640 Ry 截断和 8×8×8 电子网格。它是一个明确的教学输入，不是本次优化并验收过的 Si 平衡晶格。SCF 的操作见[固定结构计算](/Atlas/m/scf/qe/)，本例配套的[完整 SCF 输入](/Atlas/examples/si-pbe/scf/scf.in)和[输出](/Atlas/examples/si-pbe/scf/scf.out.txt)也一起保留；换算例时不要复制其他材料的保存目录。

QE 用负数标记动力学矩阵的负本征值，也就是 ω² < 0。这里打印 −5.59 的含义是一个虚频，而不是“振动反方向传播”。至于它来自数值误差还是结构的真实不稳定，要继续看证据，不能由大小一项直接决定。

## 先认清目录里的几种文件

声子已经运行过，先在原来的 tmux 窗口读取现有文件：


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

如果从下载包重新计算，应先完成上面链接中的 SCF。以下是重新运行时的目录准备顺序：在 `si-pbe` 下另建 `gamma-recheck`，把新 SCF 的整个 `tmp` 复制进去，再复制声子输入和脚本。这个新目录与记录中的原计算目录分开。

```bash
cd si-pbe
mkdir gamma-recheck
cp -a scf/tmp gamma-recheck/
cp gamma-phonon/ph.in gamma-recheck/
cp gamma-phonon/run.sh gamma-recheck/
cd gamma-recheck
ls tmp/si.save
vi ph.in
vi run.sh
```

核对 `tmp/si.save` 中的结构、赝势和电子设置属于刚完成的这份 Si SCF，并将脚本中的 `<qe_bin>` 改为本机的实际路径。确认后执行 `sbatch run.sh`。仅复制公开的 单独保存的 XML不能替代这份保存目录。

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


`thresh` 是内层求解信息，不能直接拿它代替输入的 `tr2_ph`；这里要看响应残差和这组表示的收敛行。第二组也需要分别检查。把两组表示和末尾频率一起定位出来：


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


这一页没有省略错误文件：`ph.err` 和两份 `dynmat` 的标准错误里都出现了重复的环境授权提示：


```text
Authorization required, but no authorization protocol specified
```


所以不能把这次写成“stderr 为空”。与此同时，程序确实完成了两组响应求解、矩阵写出和对角化，并打印 `JOB DONE.`。后面的比较只使用这份实际生成的矩阵；环境提示仍随[ph.err](/Atlas/examples/si-pbe/gamma-phonon/ph.err.txt)保留。完整[ph.out](/Atlas/examples/si-pbe/gamma-phonon/ph.out.txt)从开头到计时段都可以下载查看。

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


最前面是元素、晶胞和两个原子的坐标；`q = (0,0,0)` 说明这是 Γ 点。中间 `1 1`、`1 2`、`2 1`、`2 2` 四个块对应原子对，每块有三个方向的复数分量。后面的 `Diagonalizing` 段才是频率和模式向量，不能把矩阵块里的某个负数当成虚频。

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

## 把六个模式画在一起，保留零附近的细节

下面的图直接读取两份 `.modes`。左图放大声学模式，右图展示光学模式，各自的纵轴范围已经标明；负频率没有被截成零。

![同一 Si Γ 点矩阵的 ASR 前后频率对照](/Atlas/examples/si-pbe/gamma-phonon/si-gamma-asr.svg)

把[si-no.modes](/Atlas/examples/si-pbe/gamma-phonon/si-no.modes)、[si-crystal.modes](/Atlas/examples/si-pbe/gamma-phonon/si-crystal.modes)和[plot_asr.py](/Atlas/examples/si-pbe/gamma-phonon/plot_asr.py)放在同一本地目录，使用装有 NumPy 和 Matplotlib 的 Python 运行：

```bash
python3 plot_asr.py
```

脚本会生成 SVG、PNG、PDF 和[逐模式数据表](/Atlas/examples/si-pbe/gamma-phonon/asr-comparison.csv)。它读取频率行的最后一个数，检查恰有六个有限值，再绘图；不会把文本里的所有负号都当成频率。关键读取部分如下，完整脚本可直接下载：


```python
def frequencies(filename):
    text = Path(filename).read_text()
    values = re.findall(r"freq\s*\(\s*\d+\)\s*=.*?=\s*([-+\d.Ee]+)\s*\[cm-1\]", text)
    result = np.array([float(value) for value in values])
    if len(result) != 6 or not np.isfinite(result).all():
        raise ValueError(f"Expected six finite Gamma frequencies in {filename}")
    return result
```


本次可写下的结论是：这份固定 Si 输入在 Γ 点出现的三支负频率属于整体平移模式；施加 ASR 后，它们回到数值零附近，而光学组基本不变。这支持把该现象作为平移声学和规则偏差来处理。这里没有扫描其它 q 点，也没有针对这些频率完成 cutoff、电子网格和响应阈值的比较，因此不能把结论扩展成“整个材料已通过动力学稳定性验证”。

## 换成一张路径声子图时，先确定负值来自哪里

如果负值来自 `matdyn` 的插值图，先回到[DFPT 声子页](/Atlas/m/phonon-dfpt/qe/)认清文件关系。`.freq.gp` 通常是一行一个路径点：首列为累计路径坐标，其后才是频率；`.freq` 则带有表头、q 坐标和可能换行的频率记录，不能直接套同一段逐列扫描。

定位后，要记下这个点的 **q 坐标、模式、原始/插值来源和 ASR 设置**。横轴累计距离不是 q 的三个分量，不能直接拿去填 `ph.x`。如果已有原始网格点与它重合，先比较那个矩阵；若只在插值路径上出现异常，需要针对同一个实际 q 点做直接计算对照。

下面几种后续检查解决的是不同问题，不要一口气改完所有设置后只留下新图：

| 眼前现象 | 接着对照什么 | 对照后读什么 |
|---|---|---|
| 只有 Γ 附近平移模式偏离零 | 同矩阵的 ASR 前后、本征位移 | 平移模式是否回零，其他模式变化是否明显 |
| 同一 q 的频率随电子设置变化 | 保持结构和赝势，分别改 cutoff、电子网格或阈值 | 同一模式的频率变化，不能只比总能 |
| 金属的软模对展宽很敏感 | 配套增加 k 采样并比较展宽 | 是否形成稳定的频率趋势 |
| 插值有负值，直接网格点没有 | 该 q 的直接结果、不同 q 网格的插值 | 异常是否依赖插值或采样 |
| 明确非平移软模持续存在 | 对应本征位移、相容超胞和位移后的能量/力 | 是否有可继续弛豫的降能方向 |

最后一种情况才需要沿模式构造相容的畸变结构。在非 Γ 点，单胞里随手移动一个原子通常不能表示该波矢的周期位移；应先满足 q 与超胞周期的对应关系，再比较正负位移与后续弛豫。上表是后续计算的选择依据，不是本例已经做过这些对照的声明。

## 下一步

先用[收敛测试](/Atlas/m/convergence/qe/)的方法建立只改变一个量的对照，再回到[声子色散与原始 q 点](/Atlas/m/phonon-dfpt/qe/)扩大检查范围。如果正在准备 EPC，尚未解释的非平移虚频不能靠手工把负 ω² 改成零后继续积分；应先解决上游问题，再读取[谱函数](/Atlas/m/eliashberg-a2f/qe/)。

```text
负频率 → q 与原始矩阵 → 响应是否完成 → 本征位移
                                             ↓
                       同矩阵 ASR 对照 + 数值设置对照
                                             ↓
                         直接 q / 插值复核 → 后续声子或畸变
```
