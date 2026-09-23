- [EPW 官方超导教程：谱函数、线性与非线性 Eliashberg 方程](https://docs.epw-code.org/tutorials/tutorial_04/index.html)
- [本次 EPW 6.0 对应的 QE 7.5 源码：外部谱函数的读法](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/io/io_supercond.f90#L1281)
- [同版本的线性 Tc 求解和收敛检查](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/supercond.f90#L1575)
- [同版本的非线性能隙迭代](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/supercond_iso.f90)

[α²F 页](/Atlas/m/eliashberg-a2f/qe/)已经有 fcc Al 的实际谱函数。在[Allen–Dynes 页](/Atlas/m/allen-dynes/qe/)，我们把它压缩成 λ、ωlog 等少数谱矩，再代入经验公式。现在保留整条 α²F(ω)，交给 EPW 求解各向同性 Migdal–Eliashberg 方程，看看不同温度下的能隙函数，以及线性化方程的本征值如何变化。

本页有两个入口：[已有完整 α²F，直接求解](#external-spectrum-tc)；[从 DFPT 与 Wannier 插值生成谱](#wannier-epw-tc)。

先走现成谱函数这条路线。这里的电子–声子数据仍来自 QE 双网格计算：32³ 密 k 网格、16³ 响应 k 网格、4³ q 网格；选取的电子展宽是 σ=0.020 Ry。下面没有重新计算电子–声子矩阵元，也没有把这份谱称为 EPW Wannier 插值的产物。完整插值路线会有自己的输入、输出和谱文件，不能拿两条链的文件互相冒名。

[下载本页的输入、原生输出和绘图程序](/Atlas/examples/al-epw-tc-files.tar.gz)。压缩包不包含 QE/EPW 可执行程序；重算需要匹配的 EPW 6.0 环境。只读输出、重画图不需要启动 EPW。本次没有做各向异性方程，也没有计算解析延拓后的实频准粒子能隙。

<span id="external-spectrum-tc"></span>

## 把 QE 谱转换成 EPW 读取的两列

先看目录里已经有什么。绝对工作路径在命令提示符中省略，文件名、参数和程序输出保留。

```console
preston@preston-System-Product-Name:epw-tc$ head -n 6 source/alpha2F.dat
# E(THz)     0.005     0.010     0.015     0.020     0.025     0.030     0.035     0.040     0.045     0.050
  0.0000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0070   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0140   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0210   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0280   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
preston@preston-System-Product-Name:epw-tc$ tail -n 4 source/lambda.in
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
0.10
```

这不是只有两列的文件。第一列是 THz，后面十列分别对应表头的十个电子展宽。σ=0.020 Ry 是总表的第 5 列；Python 的列号从零开始，写作 `a[:, 4]`。`lambda.in` 首行的 0.12 是构造谱时采用的频率展宽，单位 THz；末行的 0.10 才是这份 Tc 估算使用的 μ*。谱本身不依赖 μ*，本次求解器另外明确设置 `muc=0.10`。

这里用的是 `lambda.x` 写出的 `alpha2F.dat`。它与 `matdyn.x` 另写的 `a2F.dos4` 不是同一个文件，不能只看文件名里都有 a2F 就互换。本列没有负的谱值。父计算中 Γ 点的三个声学残余模和 QE 的低频 EPC 处理仍按[前一页](/Atlas/m/eliashberg-a2f/qe/)的范围解释：程序对低于 20 cm⁻¹ 的相应 λ 贡献置零，不能因此推断真实材料在这些模式上没有耦合。

EPW 6.0 的 `fila2f` 读取器先跳过一行，再读恰好 `nqstep` 行，每行前两列为频率和 α²F。频率必须是 **meV**，读入后程序除以 1000 转成 eV。第二列不乘换算因子；改变频率单位不应改变 λ=2∫α²F(ω)dω/ω。转换程序保留原始十列文件，另写 `al-sigma020.a2f`。下方 JSON 摘录其中的数值核对项，完整记录含原件 SHA-256，可在下载包中查看。

```console
preston@preston-System-Product-Name:epw-tc$ python3 prepare_spectrum.py
{
  "source_shape": [
    2000,
    11
  ],
  "selected_sigma_Ry": 0.02,
  "source_spectrum_width_THz": 0.12,
  "source_mu_star": 0.1,
  "solver_mu_star": 0.1,
  "frequency_conversion_meV_per_THz": 4.135667696923859,
  "nqstep": 1999,
  "omega_max_meV": 57.89934775693402,
  "epw_rectangle_lambda": 0.37454699239805433,
  "trapz_lambda_printed_grid": 0.3745445563188833,
  "epw_omega_log_K": 343.74096331806055
}
preston@preston-System-Product-Name:epw-tc$ head -n 5 al-sigma020.a2f
# omega_meV alpha2F ; QE lambda.x sigma=0.020 Ry; zero row removed only
0.028949673878 0.00000000
0.057899347757 0.00000000
0.086849021635 0.00000000
0.115798695514 0.00000000
preston@preston-System-Product-Name:epw-tc$ tail -n 3 al-sigma020.a2f
57.841448409177 0.00000000
57.870398083056 0.00000000
57.899347756934 0.00000000
```

原表有 2000 个频率点，含第一行 (0, 0)。读取器后面直接计算 α²F/ω 和 lnω，因此这个零频点不能原样送进去。转换只删除这一行，不裁切正频率谱，不重新展宽，也不补点，得到 1999 行。1 THz=4.135667696923859 meV，来自精确 SI 的 h/e；频率上限 14 THz 变为 57.899347756934 meV。

积分也在这里核对。按原表实际频率间隔作梯形积分，λ=0.3745445563；按 EPW 6.0 读取器的 `dω=ωmax/nqstep` 作矩形求和，λ=0.3745469924。约 2.44×10⁻⁶ 的差别来自打印后的频率网格舍入及积分口径。二者都应接近父程序的谱积分结果 0.374547，而不是要求它们逐字相等。ωlog 约为 343.74 K。转换后若 λ 差一个数量级，应先停下来检查列号、单位和第二列是否被多乘了单位因子。

`prepare_spectrum.py` 还从同一 Al 的真实 QE XML 读取晶格、原子、质量、电子数和自旋状态，生成外部谱接口需要的 `crystal.fmt`。这是明确标记的格式适配文件，并非一次 Wannier 化的输出。它没有虚构 Wannier 中心；当前读取器跳过的尾部记录写为说明。质量由 XML 的 amu 按同版本 `AMU_RY=AMU_SI/(2m_e)` 转成内部 Rydberg 质量单位：Al 为 24592.1679360396，而不是 26.9815385。这个单位已与同晶胞的原生 EPW `crystal.fmt` 交叉核对，下面全部求解也用修正后的适配文件重新运行。质量数组按该版本 `ntypx=10` 写足十个数，第一项是真实 Al 质量，其余是未使用物种槽的零值，不是十种元素。

## 用线性方程夹住 Tc

先做线性方程。在临界温度附近，非线性方程可能因为能隙太小而难以迭代；线性问题直接跟踪核最大本征值 η(T)。**η=1 的交叉定义这组输入下的线性化 Tc。这里的 η 不是电子–声子耦合常数 λ。**

```console
preston@preston-System-Product-Name:epw-tc$ cp crystal.fmt linear-w010/crystal.fmt
preston@preston-System-Product-Name:epw-tc$ cat linear-w010/epw.in
&inputepw
 prefix = 'al'
 ep_coupling = .false.
 elph = .false.
 epwread = .true.
 epwwrite = .false.
 wannierize = .false.
 eliashberg = .true.
 liso = .true.
 laniso = .false.
 limag = .true.
 lpade = .false.
 fila2f = '../al-sigma020.a2f'
 nqstep = 1999
 muc = 0.10
 wscut = 0.10
 nsiter = 500
 conv_thr_iaxis = 1.0d-6
 nstemp = 7
 temps = 0.50 2.00
 tc_linear = .true.
 tc_linear_solver = 'power'
 ! These nonzero dimensions satisfy EPW 6.0 input checks only.
 ! fila2f bypasses all k/q interpolation in this spectrum-only run.
 nkf1 = 1, nkf2 = 1, nkf3 = 1
 nqf1 = 1, nqf2 = 1, nqf3 = 1
/
```

`ep_coupling=.false.` 与 `elph=.false.` 表示这一步不再生成电子–声子矩阵元。`epwread=.true.` 走读取现成数据的路径；`fila2f` 明确指向刚转换的谱。`eliashberg` 打开求解，`liso` 选择各向同性，`limag` 选择虚频轴，`tc_linear` 选择线性化方程。没有设置 `laniso=.true.`，所以这不是在费米面上逐 k、逐能带求解各向异性能隙。

末尾的六个 1 只是 EPW 6.0 输入检查所需的非零维数。这一版会对 `nkf/nqf` 做整数取模检查，Fortran 不保证逻辑表达式短路；即使已给 `fila2f`，默认零值也可能先导致整数除零。本次 `fila2f` 路线没有使用这些维数进行插值，不能把它们写成“完成了 1³ 精细网格计算”。

`wscut=0.10` 的单位是 eV，是 Matsubara 求和的截断设置；它既不是温度，也不是 `alpha2F.dat` 的频率上限。`muc=0.10` 是模型中输入的 Coulomb 赝势。`nstemp=7` 配合两个端点 `temps=0.50 2.00`，在这个版本里生成 7 个等间隔温度。`conv_thr_iaxis=1e-6` 在 power 本征值求解器里约束归一化本征向量的残差范数，`nsiter=500` 是迭代上限；二者不代表材料 Tc 已达到某个实验精度。

这里每个作业只启动一个 MPI 进程，OpenMP 线程数也为 1。矩阵由给定谱构建，多起几个独立同目录程序不会加速同一个问题，反而会争写输出。当前机器已有的 `env.sh` 加载 oneAPI 及它自己的运行库兼容配置；重算时应换成你已经核验的 EPW 环境和可执行路径。

```console
preston@preston-System-Product-Name:epw-tc$ cat linear-w010/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-epw-linear-w010
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source <软件环境>/env.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 1 <qe_bin>/epw.x -in epw.in > epw.out 2> epw.err
preston@preston-System-Product-Name:epw-tc$ cd linear-w010
preston@preston-System-Product-Name:linear-w010$ sbatch run.sh
Submitted batch job 888
```

提交后可以用 `squeue -u preston` 看队列，用 `tail -f epw.out` 跟踪当前输出。若作业很短，队列里很快就没有它；此时应读取原生输出和 Slurm 的结束状态。本次线性粗扫用了约 1 s 程序墙时。

开头的 EPW 图案之后是版本和并行信息：

```text
     Program EPW v.6.0 starts on 23Sep2026 at 15:22:40 

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org", 
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI & OpenMP), running on       1 processor cores
     Number of MPI processes:                 1
     Threads/MPI process:                     1

     MPI processes distributed on     1 nodes
     3495 MiB available memory on the printing compute node when the environment starts
```

外部谱路线的前置摘要可能打印零 k 点、零 G 向量。那是本次跳过 `pw.x` 波函数读取后的摘要，不能据此描述父 SCF，更不能把它当成新的 SCF 验收。真正与本步骤有关的输出从 `Solve isotropic Eliashberg equations` 开始：

```text
     Finish reading a2f file

     Electron-phonon coupling strength =    0.3745470
 
     Estimated Tc using McMillan expression =   0.9701 K for muc =   0.1000
  
     Estimated Tc using Allen-Dynes modified McMillan expression =   0.9826 K
  
     Estimated Tc using SISSO machine learning model =   1.0276 K
  
     Estimated w_log =  29.6213 meV
  
     Estimated BCS superconducting gap using McMillan Tc =   0.1471 meV
  
  
     WARNING WARNING WARNING 
  
     The code may crash since tempsmax =    2.000 K is larger than McMillan Tc =     0.970 K
```

注意三个 `Estimated Tc` 都出现在真正求解之前。它们分别来自经验表达式或拟合模型，用于估算和初始化；即使这一段已经有非零 Tc，后面的 ME 求解仍可能失败。这里完整 Allen–Dynes 估计约 0.983 K，而线性化 ME 的交叉温度还要继续看下面的表。

```console
preston@preston-System-Product-Name:epw-tc$ grep -A 13 "Nr. of iters" linear-w010-refine/epw.out
             Temp.       Max.         nsiw     wscut    Nr. of iters
             (K)       eigenvalue    (itemp)   (eV)      to Converge
      -----------------------------------------------------------------
             1.43      1.0060504      129      0.1003       11
             1.44      1.0041981      128      0.1002       11
             1.45      1.0023633      127      0.1001       11
             1.46      1.0002425      127      0.1008       11
             1.47      0.9984385      126      0.1007       11
             1.48      0.9966515      125      0.1006       11
             1.49      0.9948812      124      0.1004       11
             1.50      0.9931277      123      0.1003       11
      -----------------------------------------------------------------
```

粗扫先发现 1.25 K 时 η=1.0423226、1.50 K 时 η=0.9931277，交叉在两者之间。上面是随后实际完成的 0.01 K 步长扫描。1.46 K 的 η=1.0002425，大于 1；1.47 K 的 η=0.9984385，小于 1。因此本组 `wscut=0.10 eV、μ*=0.10` 输入的交叉被夹在 **1.46–1.47 K**。只作两点直线插值会得到约 1.4613 K，它是定位交叉的插值数，不是把材料预测精度提升到了四位小数。

同在 1.46 K，把求解器从 `power` 换成 `lapack`，实际得到 η=1.0002422；与 power 的差是 3×10⁻⁷。这个检查针对本征值求解，不涉及上游 k/q 网格收敛。表中 `nsiw` 是程序实际采用的 Matsubara 频率数，`wscut` 一列随温度略变，是离散频率取整后的值；不要用输入文件的 0.10 覆盖这些输出。

## 读取每个温度的能隙函数

然后看非线性方程里的 Δ(iω₀,T)。线性表能定位交叉，却不告诉我们低温能隙函数有多大。非线性输入沿用同一个谱、μ* 和截断，改为 `tc_linear=.false.`；每个温度放在独立目录，避免一次温度失败中断后续所有温度的记录。

```console
preston@preston-System-Product-Name:epw-tc$ cat nonlinear-w010-T1.45/epw.in
&inputepw
 prefix = 'al'
 ep_coupling = .false.
 elph = .false.
 epwread = .true.
 epwwrite = .false.
 wannierize = .false.
 eliashberg = .true.
 liso = .true.
 laniso = .false.
 limag = .true.
 lpade = .false.
 fila2f = '../al-sigma020.a2f'
 nqstep = 1999
 muc = 0.10
 wscut = 0.10
 nsiter = 500
 conv_thr_iaxis = 1.0d-6
 nstemp = 1
 temps = 1.45
 tc_linear = .false.
 tc_linear_solver = 'power'
 ! These nonzero dimensions satisfy EPW 6.0 input checks only.
 ! fila2f bypasses all k/q interpolation in this spectrum-only run.
 nkf1 = 1, nkf2 = 1, nkf3 = 1
 nqf1 = 1, nqf2 = 1, nqf3 = 1
/
```

单温度输入使用 `nstemp=1` 与 `temps=1.45`。这里没有启用 Padé 或其他解析延拓：`lpade=.false.`。输出的 `deltai` 是最低正 Matsubara 频率处的能隙函数，而不是解析延拓后、再由实轴能隙方程确定的准粒子激发能隙。

1.45 K 的迭代末段如下，完整输出也在包中：

```text
        iter      ethr          znormi      deltai [meV]
          1   2.174502E+00   1.341340E+00   1.491447E-01
          2   6.997688E-02   1.341342E+00   1.467866E-01
          3   4.813545E-02   1.341345E+00   1.431243E-01
          4   3.291689E-02   1.341348E+00   1.387074E-01
          5   2.732357E-01   1.341364E+00   1.090273E-01
          6   2.793093E-01   1.341375E+00   8.525206E-02
          7   3.121520E-01   1.341382E+00   6.498217E-02
          8   3.200741E-01   1.341386E+00   4.923357E-02
          9   1.332549E-01   1.341387E+00   4.344642E-02
         10   1.199923E-01   1.341388E+00   3.879302E-02
         11   5.761376E-02   1.341388E+00   3.668027E-02
         12   1.127631E-01   1.341389E+00   3.296399E-02
         13   2.501625E-02   1.341389E+00   3.215963E-02
         14   6.937778E-03   1.341389E+00   3.193809E-02
         15   1.458320E-03   1.341389E+00   3.189159E-02
         16   1.602579E-04   1.341389E+00   3.188648E-02
         17   1.451305E-05   1.341389E+00   3.188694E-02
         18   8.954613E-06   1.341389E+00   3.188723E-02
         19   8.607533E-07   1.341389E+00   3.188725E-02
     Convergence was reached in nsiter =     19
```

`ethr` 在非线性求解器中是两次迭代能隙数组差的相对量 Σ|Δnew−Δold|/Σ|Δnew|，不是 eV。本次第 19 步降到 8.61×10⁻⁷，输出明确写出收敛。仅有 `al.imag_iso_001.45` 文件还不够：这个版本到达迭代上限时也可能写文件，必须读对应温度的收敛信息。

```console
preston@preston-System-Product-Name:epw-tc$ head -n 6 nonlinear-w010-T1.45/al.imag_iso_001.45
              w [eV]            znorm(w)       delta(w) [eV]
    3.9254618761E-04    1.3413889366E+00    3.1887253157E-05
    1.1776385628E-03    1.3411813046E+00    3.1833635005E-05
    1.9627309381E-03    1.3407677746E+00    3.1726964694E-05
    2.7478233133E-03    1.3401517535E+00    3.1568351089E-05
    3.5329156885E-03    1.3393382028E+00    3.1359401980E-05
```

文件三列分别为频率 eV、重整化函数 Z、能隙函数 eV。第一行的 Δ=3.1887253157×10⁻⁵ eV，即 **0.0318873 meV**。这一行的频率不是零，而是 πkBT；温度越高，最低 Matsubara 频率也随之变化。

独立温度目录得到的收敛点为：

| T / K | Δ(iω₀,T) / meV | 收敛迭代数 |
|---:|---:|---:|
| 0.25 | 0.222056 | 11 |
| 0.50 | 0.220672 | 11 |
| 0.75 | 0.211328 | 11 |
| 1.00 | 0.187057 | 12 |
| 1.25 | 0.137256 | 12 |
| 1.35 | 0.102240 | 11 |
| 1.40 | 0.076484 | 14 |
| 1.43 | 0.054565 | 15 |
| 1.45 | 0.031887 | 19 |

这些点表现为随温度升高而减小的有限能隙函数。到 1.45 K，它还没有变成零，与线性表在 1.46–1.47 K 之间跨越 1 相容。

前面的连续扫温尝试在 1.50 K 发生了真实失败，保留在 `nonlinear-w010`：

```console
preston@preston-System-Product-Name:epw-tc$ tail -n 20 nonlinear-w010/epw.out
        157   5.089638E+01   1.341504E+00   1.979312-142
        158   3.242441E+01   1.341504E+00   5.900896-144
        159   1.521331E+00   1.341504E+00  -1.137050-143
        160   1.421569E+00   1.341504E+00  -4.693708-144
        161   3.456376E+01   1.341504E+00   1.397568-145
        162   2.960763E+00   1.341504E+00  -7.128842-146
        163   4.963284E+00   1.341504E+00  -1.195026-146
        164   4.316475E+00   1.341504E+00   3.605912-147
        165   7.877499E+00   1.341504E+00   4.060307-148
        166   4.974606E+00   1.341504E+00   6.795587-149
        167   1.637161E+01   1.341504E+00   3.911668-150
        168   2.693770E+00   1.341504E+00  -2.309885-150
        169   4.792926E+00   1.341504E+00  -3.987562-151

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     Error in routine mix_broyden (5):
     factorization
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

     stopping ...
```

它并非“成功得到零能隙”。此时 Δ 已下降到极小量，但相对误差没有满足条件，Broyden 混合器最终无法分解矩阵，程序终止。图中没有把这条失败迭代补成 Δ=0 点；Tc 的判断仍来自已经收敛的线性本征值交叉。下载包保留了该次的 `epw.err` 和 `CRASH`，也保留了早期接口检查失败的输入输出，便于区分格式错误与物理求解过程中的失败。

![同一谱函数下的线性核本征值和已收敛非线性能隙函数](/Atlas/figures/epw-eliashberg/al-spectrum-tc.png)

左图中 η=1 的水平线给出线性化方程的交叉条件，阴影标出 0.01 K 的夹区。右图只连已收敛的独立温度点，标注的 1.50 K 失败不占一个人为的零能隙数据点。两图都固定输入 μ*=0.10 和截断 0.10 eV。

## 截断变化后，交叉点是否稳定

不能在这里收起输出就把 1.46 K 当作 Al 的验收 Tc。至少还要看看 Matsubara 截断改变后发生什么。下面三组只改变 `wscut`，原始 α²F 和输入 μ*=0.10 都保持不变；每组都实际细化了交叉温区。

| 请求截断 / eV | η>1 的温度与数值 | η<1 的温度与数值 | 实际交叉夹区 / K |
|---:|---|---|---|
| 0.10 | 1.46 K，1.0002425 | 1.47 K，0.9984385 | 1.46–1.47 |
| 0.20 | 1.45 K，1.0008521 | 1.46 K，0.9989809 | 1.45–1.46 |
| 0.40 | 1.57 K，1.0007327 | 1.58 K，0.9990310 | 1.57–1.58 |

![固定输入 Coulomb 赝势时的 Matsubara 截断敏感性](/Atlas/figures/epw-eliashberg/al-cutoff-sensitivity.png)

0.10 与 0.20 eV 的交叉很接近，0.40 eV 却又上移。这份表应该叫“固定输入 `muc=0.10` 的截断敏感性”，不能据此声称截断已经收敛。μ* 的定义与能量截断有关；把相同数值的 μ* 用在不同截断下，不等于已经证明它们代表完全相同的物理 Coulomb 模型。本页没有做相应重整化。原始谱的 k/q 网格、电子展宽、低频处理及结构协议也没有在这里得到新的材料级验收。

## 从原始输出重画两张图

画图从原生输出重新提取，命令保持很短：

```bash
python3 analyse_tc.py
python3 plot_tc.py
```

`analyse_tc.py` 生成 `linear.csv`、`gap.csv`、`solver-status.json` 和 `tc-brackets.json`；它从线性表读 η、实际频率数和迭代数，从原生 `imag_iso` 文件读第一频率点。`gap.csv` 同时保留早期连续扫温已收敛的前四点，绘图只选 `whole_run_complete=True` 的独立单温目录，避免重复画点。脚本不从失败迭代里寻找一个很小的数字冒充正常态。`plot_tc.py` 与 `atlas_plot_style.py` 放在同一目录，需要 NumPy 和 Matplotlib。上述命令在本机也可执行：它把同一份数据分别导出为便于网页阅读的 PNG、SVG，以及宽 183 mm、保留文字的矢量 PDF，文件写入 `figures/`。

绘图保留所有通过验收的点，用符号区分采样点，用细线连接而不做平滑拟合。第一张图的灰带来自相邻温度对 η=1 的夹区；第二张图的短横线也是采样夹区，不是统计误差棒。坐标轴、单位和曲线说明都应保留到论文图中。字体、线宽与矢量导出方式见[科研绘图与导出](/Atlas/plotting/)；这些版式设置不改变数值或截断范围。

本次真正得到的是：EPW 6.0 已对指定 Al 谱函数求解各向同性虚频轴方程；低温非线性能隙函数有逐温度收敛记录，线性方程有 η=1 的实际夹区和 LAPACK 对照；截断敏感性仍然可见。因此这些数字应随“谱来源、μ*、截断、各向同性近似”一起引用，不能替代对材料超导性的完整论证。

下一步回到[电子–声子耦合](/Atlas/m/epc/qe/)补齐原谱的数值比较，或沿下面另一条路线直接从粗 k/q 网格的波函数和扰动势做 EPW Wannier 插值。两条路线最后都能进入 Eliashberg 求解器，但中间数据的来源必须一直分清。

```text
同协议 QE 结构与 SCF
  → 密 k 网格 / 响应 k 网格 / q 网格
  → lambda.x 的真实 α²F(ω)
  → 单位与积分核对
  → EPW 各向同性线性 η(T) + 非线性 Δ(iω₀,T)
  → 条件明确的交叉夹区

另一条独立路线：
同协议 QE SCF + 全粗 k 网格 NSCF + 粗 q 网格 DFPT
  → Wannier 质量核对
  → EPW 精细 k/q 网格插值的 α²F(ω)
  → Eliashberg 求解与相同层次的验收
```

<span id="wannier-epw-tc"></span>

## 从完整 k 网格到 EPW 自己生成的谱

EPW 的完整计算链需要波函数、声子位移模式和自洽势的一阶响应。只有一张 α²F(ω) 表时，可以研究给定谱下的 Eliashberg 方程；要计算这张谱本身，还需要把粗网格上的电子结构和电子–声子矩阵元变换到 Wannier 表象，再插值到积分网格。本节使用 fcc Al，把这条链的输入、原生输出和质量检查放在同一份计算记录中。

需要先熟悉 [SCF](/Atlas/m/scf/qe/)、[NSCF](/Atlas/m/nscf/qe/)、[DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 和 [Wannier90](/Atlas/m/wannier90/qe/) 的文件关系。已有 α²F 表、只想求解温度依赖时，可以跳到[读取外部谱的 Eliashberg 计算](#external-spectrum-tc)。[原生双网格 EPC](/Atlas/m/epc/qe/#double-grid-pwxall) 与这里共享声子父链；两种程序的积分网格、展宽和插值步骤分别记录，数值不能仅凭材料名称互相替换。

实跑程序为 QE 7.5、EPW 6.0。官方的 [EPW 插值教程](https://docs.epw-code.org/tutorials/tutorial_01/index.html) 和 [超导教程](https://docs.epw-code.org/tutorials/tutorial_04/index.html) 标明这组版本。在线[输入参数页](https://docs.epw-code.org/Inputs/Inputs.html)目前标为 EPW 6.1；本例的精确输入还核对了本机 6.0 源码和原生输出。

本节的[完整输入、原生输出、比较数据与提取脚本](/Atlas/examples/al-epw-wannier-files.tar.gz)可一起下载。它与上面的外部 QE 谱包分别保存。

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

Γ 点的响应在 `tmp/_ph0/al.aldv1`，其余在 `tmp/_ph0/al.q_N/al.aldv1`。`ifc.q2r` 是同一套 q4 数据经 `q2r.x`、`zasr='simple'` 产生的 `al.fc` 副本。本次没有直接在父目录运行 EPW 自带的 `pp.py`：所安装脚本的某些分支还会删除声子目录中的波函数。下载包中的收集脚本只复制所需文件，保留原计算树。

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

### 细网格原生谱与实际求解结果

最终采用电子粗网格 12³、声子粗网格 4³，在 24³ 电子细网格和 12³ 声子细网格上积分。与旧的 `lambda.x` 谱相比，这里重新完成了均匀全布里渊区 NSCF、Wannier 化、粗网格矩阵转换和 EPW 细网格插值；两条路线的谱文件及展宽单位各自保留。以下数值只属于这一组有限网格和输入参数。

| 控制量 | 本次实际输入 |
| --- | --- |
| 电子粗网格 / 声子粗网格 | 12³ / 4³ |
| 电子细网格 / 声子细网格 | 24³ / 12³ |
| 电子展宽 `degaussw` | 0.1 eV |
| 声子谱展宽 `degaussq` | 0.5 meV |
| Fermi 窗口 `fsthick` | 1.0 eV |
| 声学阈值 `eps_acoustic` | 0.1 cm⁻¹，约 0.0123984 meV |
| 力常数 / 声学和规则 | `lifc=.true.`、`asr_typ='crystal'`；父链 `q2r.x` 使用 `zasr='simple'` |

父链的 `q2r.x` 使用 `zasr='simple'`。EPW 在 `lifc=.true.` 读取力常数后，又按 `asr_typ='crystal'` 施加声学和规则；这次粗矩阵、细积分和全 q 频率检查的原生输出均打印 `Imposed crystal ASR`。因此，父 q2r 的选项与 EPW 最终施加的选项要分别记下，不能把前者改写成后者。

`interpolate-003` 在 8 个 MPI 进程上完成，EPW 报告墙钟时间 42.13 s，退出码为 0、stderr 为空。原生 `al.a2f` 有 500 行正频率点，范围为 0.0904076–45.2038042 meV。文件前三列是 ω、α²F(ω)、累计 λ(ω)，完整尾部说明如下：

```text
 Phonon smearing (meV)
  #            0.5000000
Electron smearing (eV)   0.1000000
Fermi window (eV)   1.0000000
DOS (eV)   0.2560645
Summed el-ph coupling    0.3507955
```

这里有两个应分开记录的 λ。模式和电子声子矩阵的离散直接求和给出 **0.3507955**；谱文件最后一个累计值为 **0.3508982**。从公开的 500 行舍入数据重新作正频率梯形积分，得到 λ=0.3508982379、ωlog=26.44613456 meV。谱末端求解器读取的是 α²F，后续引用 λ 时采用谱积分值。两种离散汇总相差约 0.000103，不把它们改写为一个逐字相同的输出。

原生文件是 `runs/interpolate-003/al.a2f`，SHA-256 为 `f48a3230b47468b6fb813d9b5cabe6df5b7133ae1f13af1f2317300e3dd3cabf`。提取表 `derived/epw-a2f-k12-q4-fine24-q12.csv` 的列名为 `omega_meV,alpha2F,native_cumulative_lambda`；`analyse_final.py` 从原生文件重新提取这些列，并保留直接求和 λ 的独立元数据。

### 声学模和插值质量怎样核对

EPW 6.0 的谱构造对每个声子模判断 `wq > eps_acoustic`；负频率及低于阈值的频率不会贡献到 α²F。因此，一张全为正的谱图不能证明采样声子没有虚频。本次另用同一粗网格矩阵、同一力常数和同一 ASR 设置，令 `band_plot=.true.`、`filqf='qmesh12.dat'`，显式检查全部 1728 个 12³ q 点。该输入不再同时设置 `nqf1..3`，否则 EPW 6.0 会拒绝这组相互冲突的细网格指定。

成功检查保存在 `runs/phononcheck-002/phband.freq`。共有 5184 个频率，原生输出精度为 0.0001 meV；Γ 点三支为 `-0.0000, -0.0000, 0.0000` meV，非 Γ 点最低值为 **5.9373 meV**，最高值为 **41.0944 meV**。在这张采样网格和打印精度上没有有限负频率；不高于 0.1 cm⁻¹ 阈值的恰是 Γ 点三支声学模。这个检查没有证明整个连续布里渊区动力学稳定，也没有证明声子网格收敛。完整逐模表是 `derived/phonons-all-q12-native-EPW.csv`，原生频率文件 SHA-256 为 `cabdd5b96b58fc1169763485b108e11b95bb172ddb418c3510c7cf028e36be40`。

能带检查采用同一条 166 点路径、固定 EF=8.4122 eV 和相同的四个逐点能量排序，交叉附近比较能谱排序而非声称跟踪同一轨道。对直接 QE 能带满足 |E−EF|≤1 eV 的 47 个态，最终 12³ 插值的 RMS 误差为 **25.9 meV**，最大绝对误差为 **92.3 meV**。这比早期 4³ / 冻结窗上限 10 eV 的 RMS 634.5 meV 明显改善，但不构成为 Tc 选定的误差容限。8³ 到 12³ 的比较使用冻结窗上限 13.5 eV；完整 CSV 保留窗外能带，图中须标明粗网格与窗口同时变化的早期分支。

![同一路径上的直接 QE 与 Wannier 能带，以及四套设置的误差对比](/Atlas/figures/epw-eliashberg/al-wannier-validation.png)

左图只放大共同费米参考附近 ±2 eV 的部分；右图取直接 QE 能带中落在 ±1 eV 内的 47 个态，分别显示 RMS 和最大绝对误差。横轴同时列出粗网格与冻结窗上限，避免把最初两项参数同时改变的效果全算到网格上。这里的 8.4122 eV 只是共同绘图零点；实际精细网格 EPC 输出的费米能为 8.424415 eV，二者用途不同。全四带的 RMS 误差仍为 0.2853 eV，不能把费米能附近的精度推广到全部能带。

解包后运行 `python3 plot_wannier_validation.py` 可由 `derived/band-*.csv` 重画此图。`plot_wannier_validation.py` 与 `atlas_plot_style.py` 保留能量零点、样本筛选和每套设置的参数，输出在 `figures/`，不拟合或移动两条能带。

最终 `al.wout` 的总 spread 为 11.997746862 Å²，解纠缠和局域化各自满足本次输入的迭代判据。实空间衰减也须结合所覆盖的距离看：对原生 `decay.H`、`decay.epmate` 和 `decay.epmatp`，把距离最外侧 20% 区间的最大幅度除以全局最大幅度，分别为 0.0001289、0.001995、0.02914；对应最大距离为 23.7364、23.7364、7.9121 Å。这些只是可复核的衰减诊断，不是预先接受的容限，声子方向的尾部仍比电子方向更明显。

本轮没有继续扩展粗电子网格。48³ / 24³ 的细积分尝试在约 118 s 时只处理了 942/13563 个筛选后 q 点，估计无法在预定短时作业内完成，故停止并保留输出。最终 24³ / 12³ 路线已经形成完整的谱和方程求解证据；它没有给出电子粗网格、声子粗网格、细积分、展宽、Fermi 窗口及 Matsubara 截断的联合收敛结论。最初 4³ 插值的谱及 1 K 非线性未收敛输出也保留在包中，只用于展示诊断过程。

### 重跑与输出核对

下载包提供完整输入、纯文本原生输出、比较 CSV 和提取脚本，不打包赝势正文、波函数、dvscf 或二进制 Wannier 矩阵。要从头重跑，应先用包内 SCF/DFPT 输入产生声子父链；已有同一父链时，运行只复制文件的收集脚本，再继续 NSCF。

下面是从下载包重跑时的普通目录操作。开始前，应已按包内父链输入得到 `00-phonon/tmp/al.save`，并把同一套 dyn、dvscf、patterns 和力常数整理到 `phonon-save/`；`pseudo/` 中的赝势须与前述 SHA 一致。先按实际机器设置运行环境、程序路径与可用 MPI 数，再逐步复制和运行。每一步结束后先检查原生输出，再执行下一段。

```bash
mkdir -p 01-nscf/tmp/al.save
cp -r pseudo 01-nscf/
cp 00-phonon/tmp/al.save/{data-file-schema.xml,charge-density.dat,Al.pz-vbc.UPF} 01-nscf/tmp/al.save/
cp inputs/al.nscf-k12.in 01-nscf/al.nscf.in
vi 01-nscf/al.nscf.in
cat 01-nscf/al.nscf.in
cd 01-nscf
mpirun -np 8 pw.x -nk 8 -in al.nscf.in > al.nscf.out 2> al.nscf.err
tail -20 al.nscf.out
cd ..

mkdir 02-wannier
cp -r 01-nscf/tmp pseudo 02-wannier/
cp inputs/epw1-k12.in 02-wannier/epw1.in
cd 02-wannier
mpirun -np 1 epw.x -nk 1 -in epw1.in > epw1.out 2> epw1.err
cd ..

mkdir 03-coarse
cp -r 01-nscf/tmp pseudo 03-coarse/
cp 02-wannier/{al.ukk,al.win,al.bvec,al.mmn} 03-coarse/
cp inputs/epw-coarse.in 03-coarse/epw-coarse.in
cd 03-coarse
mpirun -np 8 epw.x -nk 8 -in epw-coarse.in > epw-coarse.out 2> epw-coarse.err
cd ..

mkdir -p 04-fine/tmp
cp 03-coarse/{crystal.fmt,epwdata.fmt,dmedata.fmt,vmedata.fmt,wigner.fmt,al.ukk} 04-fine/
cp 03-coarse/tmp/al.epmatwp 04-fine/tmp/
cp inputs/epw2-k12-fine24.in 04-fine/epw2.in
cd 04-fine
mpirun -np 8 epw.x -nk 8 -in epw2.in > epw2.out 2> epw2.err
```

上面的复制关系也封装在下载包的 `tools/prepare_stage.py` 中，作为可选的重跑辅助。目录已存在时应先读旧输出，不要在上面反复启动新程序。原始记录保留每次执行的独立目录、输入哈希、stdout、stderr、调度记录和失败状态。输入、父计算文件与原生结束状态分别核对。λ 和 Tc 的数值收敛及物理有效性仍需单独检查。

## 把新生成的 EPW 谱接到 Tc 求解

现在将这份完成前述能带对照的原生 EPW 谱接到求解器。这里使用粗网格 12³ k / 4³ q、精细网格 24³ k / 12³ q，电子展宽 0.10 eV、声子谱展宽 0.5 meV，`eps_acoustic=0.1 cm⁻¹`、`asr_typ='crystal'`。它与前面从 QE `lambda.x` 读取的谱分别保存；两组 λ 和 Tc 的差异不能只归因于“换了求解器”，因为谱的生成流程、网格和展宽也不同。

[下载这一支的原生谱、输入输出和解析程序](/Atlas/examples/al-epw-wannier-tc-files.tar.gz)。目录中的 `source/al.a2f` 和 `source/crystal.fmt` 都直接复制自本次 EPW 插值输出，不需要前面 THz→meV 的转换，也不需要晶体文件适配器。

```console
preston@preston-System-Product-Name:epw-native-tc$ head -n 6 source/al.a2f
 w[meV] a2f and integrated 2*a2f/w for   10 smearing values
   0.0904076   0.0000000   0.0000000
   0.1808152   0.0000000   0.0000000
   0.2712228   0.0000000   0.0000000
   0.3616304   0.0000000   0.0000000
   0.4520380   0.0000000   0.0000000
```

原文件表头保留了“10 smearing values”这段程序文字，但本次实际只有三列：频率 meV、α²F、累计 λ。正频率数据共 500 行，末尾另有人工阅读的说明和参数。求解器设置 `nqstep=500`，读取前两列，读完 500 行后结束；第三列和文件尾不会被误当作另一条谱。不应因为表头文字而自行补出其他展宽数据。

该谱末点的累计 λ=0.3508982；独立按 EPW 的积分步长重算为 0.3508982377。插值输出另写的 `Summed el-ph coupling=0.3507955` 是离散网格求和量，与频率谱积分的口径不同，后面的 Eliashberg 求解应对应实际读入谱的 λ。

这里仍固定 `muc=0.10`、`wscut=0.10 eV`。粗扫先在 0.75 K 得到 η=1.0298194，在 1.00 K 得到 η=0.9587645；再用 0.01 K 的步长缩小交叉区间。实际细扫输入为：

```console
preston@preston-System-Product-Name:epw-native-tc$ cat linear-refine/epw.in
&inputepw
 prefix = 'al'
 ep_coupling = .false.
 elph = .false.
 epwread = .true.
 epwwrite = .false.
 wannierize = .false.
 eliashberg = .true.
 liso = .true.
 laniso = .false.
 limag = .true.
 lpade = .false.
 fila2f = '../source/al.a2f'
 nqstep = 500
 muc = 0.10
 wscut = 0.10
 nsiter = 500
 conv_thr_iaxis = 1.0d-6
 nstemp = 9
 temps = 0.82 0.90
 tc_linear = .true.
 tc_linear_solver = 'power'
 ! These nonzero dimensions satisfy EPW 6.0 input checks only.
 ! fila2f bypasses all k/q interpolation in this spectrum-only run.
 nkf1 = 1, nkf2 = 1, nkf3 = 1
 nqf1 = 1, nqf2 = 1, nqf3 = 1
/
```

这些 `nkf/nqf=1` 仍只是独立谱求解的输入检查字段。谱的真实精细网格是上游的 24³ k / 12³ q，不由这六个数重新计算。

```console
preston@preston-System-Product-Name:epw-native-tc$ grep -A 14 "Nr. of iters" linear-refine/epw.out
             Temp.       Max.         nsiw     wscut    Nr. of iters
             (K)       eigenvalue    (itemp)   (eV)      to Converge
      -----------------------------------------------------------------
             0.82      1.0077843      225      0.1001       11
             0.83      1.0047199      223      0.1004       11
             0.84      1.0017989      220      0.1003       11
             0.85      0.9989208      217      0.1001       11
             0.86      0.9959791      215      0.1003       11
             0.87      0.9931824      212      0.1001       11
             0.88      0.9903180      210      0.1003       11
             0.89      0.9874912      208      0.1005       11
             0.90      0.9848099      205      0.1001       11
      -----------------------------------------------------------------
```

0.84 K 的核最大本征值为 1.0017989，0.85 K 为 0.9989208，实际夹区是 **0.84–0.85 K**。两点插值约 0.8463 K，仅用于图上定位，不代表材料预测达到这个精度。本次三个作业 905、906、907 都以 `COMPLETED / ExitCode=0:0` 结束，原生 stderr 为空；每个线性温度也均完成本征值迭代。

读同一输出的前半段，还会看到 λ=0.3508982、ωlog=26.4461 meV（约 306.89 K），以及 McMillan 估计 0.5559 K、完整 Allen–Dynes 估计 0.5628 K。这些仍是求解前的估计，与刚才真正解出的 ME 本征值交叉有明确区别。

再单独检查低温非线性解。0.25 K 时令 `tc_linear=.false.`，其他谱、μ* 和截断保持不变，程序在 11 次迭代后打印收敛：

```console
preston@preston-System-Product-Name:epw-native-tc$ grep -n "Convergence" nonlinear-T0.25/epw.out
145:     Convergence was reached in nsiter =     11
preston@preston-System-Product-Name:epw-native-tc$ head -n 3 nonlinear-T0.25/al.imag_iso_000.25
              w [eV]            znorm(w)       delta(w) [eV]
    6.7680377175E-05    1.3230115257E+00    1.2821328449E-04
    2.0304113152E-04    1.3230014045E+00    1.2820252788E-04
```

第一频率点的 Δ=1.2821328449×10⁻⁴ eV，即 **Δ(iω₀,0.25 K)=0.1282133 meV**。这里有一个通过收敛检查的低温解，没有把单点画成完整的能隙温度曲线，也没有由此声称实轴激发能隙已经求出。

![EPW 原生插值谱和相应的线性化 Eliashberg Tc 求解](/Atlas/figures/epw-eliashberg/al-native-spectrum-tc.png)

重画时在这一支的数据包目录运行：

```bash
python3 analyse_tc.py
python3 plot_native_tc.py
```

`plot_native_tc.py` 需要同目录的 `atlas_plot_style.py`、NumPy 与 Matplotlib，输出 PNG、SVG 和宽 183 mm 的矢量 PDF。`analyse_tc.py` 从这些原件提取绘图数据：`source-spectrum.csv` 保留谱和累计 λ，`linear.csv` 保留每个温度的本征值、实际频率数和迭代数，`gap.csv` 记录这一个收敛的低温点，`tc-brackets.json` 记录实际跨 1 的两端。它们与前面的外部 QE 谱数据分包保存。

至此，这一条真实的“QE 粗网格 → Wannier → EPW 精细网格谱 → Eliashberg 求解”已连通。0.84–0.85 K 应始终连同这组网格、展宽、μ*、截断和各向同性近似一起陈述。它没有代替上游的插值质量检查，也没有证明粗 q 网格、精细积分网格或材料 Tc 已经收敛。

下一步：把[原生双网格 EPC](/Atlas/m/epc/qe/#double-grid-pwxall)、[谱函数积分](/Atlas/m/eliashberg-a2f/qe/)和[Allen–Dynes 公式](/Atlas/m/allen-dynes/qe/)放回同一组物理设置下比较。真正做材料 Tc 时，沿每一条分支分别检查结构、声子、粗细 k/q 网格、展宽和截断，不能从不同目录各挑一个数拼成结果。

```text
同一结构、赝势与 SCF 势
  → 完整均匀 NSCF + 完整 DFPT q 网格
  → Wannier 解纠缠、局域化及直接能带对照
  → EPW 粗矩阵 → 精细 k/q 积分 → 原生 α²F
  → 谱积分、低频规则和采样声子检查
  → 线性 η(T)=1 的夹区 + 独立低温非线性解
  → 在固定协议下继续数值收敛比较
```
