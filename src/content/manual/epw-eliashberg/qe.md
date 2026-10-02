[α²F与频率矩](/Atlas/m/eliashberg-a2f/qe/) · [Allen–Dynes近似](/Atlas/m/allen-dynes/qe/) · [EPW超导教程](https://docs.epw-code.org/tutorials/tutorial_04/index.html) · [本例EPW6.0源码](https://github.com/QEF/q-e/tree/qe-7.5/EPW)

## 从平均谱到温度相关的能隙

Allen–Dynes把α²F压缩为λ、ωlog和二阶矩。Migdal–Eliashberg方程保留整个频率依赖，耦合谱与Coulomb项共同构造配对核，再求能隙函数Δ和电子重整化函数Z。在各向同性近似中，它们依赖频率和温度；各向异性求解还保留能带n与动量k，因而能比较不同费米面片上的能隙。

虚频轴的$\omega_j=(2j+1)\pi k_{\mathrm{B}}T$是求解器的Matsubara频率，与声子虚频不同。$\Delta(i\omega_0,T)$是最低正Matsubara频率的能隙函数；只有进一步进行相应解析延拓和实轴求解，才能按该模型讨论准粒子激发能隙。线性化配对核的最大本征值η(T)穿过1定义临界温区，η不是电子–声子总λ。

本页实际完成两条Al等方路线：[QE外部谱直接求解](#external-spectrum-tc)，以及[Wannier–EPW原生插值谱求解](#wannier-epw-tc)。它们都使用EPW6.0、μ*=0.10，但谱生成方式和网格、展宽不同。后面的[材料各向异性路线](#material-anisotropic-route)说明还须保留什么文件和分析量，不把Al等方结果写成界面各向异性结果。

| 真实路线 | 谱来源与参数 | 方程输出 |
|---|---|---|
| 外部QE谱 | Al32³致密/16³响应/q4³，σ=0.020 Ry | wscut=0.10 eV下η=1夹区1.46–1.47 K，9个收敛低温能隙点 |
| 原生EPW谱 | 粗k12³/q4³，细k24³/q12³，0.10 eV电子展宽、0.5 meV谱宽 | 同截断下η=1夹区0.84–0.85 K，0.25 K收敛能隙点 |

保持同一谱时才可把公式与方程差异归因到求解近似；上面两路线间的温差还包含谱、积分和插值设置的变化。当前有限网格用于学习完整数据关系。

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
这一点可以直接从积分看清：令 $E=cf$，则 $\mathrm{d}E/E=\mathrm{d}f/f$，因此按此定义把横轴从 THz 换成 meV 时，α²F 的数值不用再乘 c。普通 PHDOS 是每单位频率的模式数密度，为保持模式数积分却要相应变换纵轴；两种表不能照搬同一种单位处理。这里转换后先核对 λ 和 ωlog，再交给求解器，正是要验证读入的仍是原来的配对谱。


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
将临界附近的能隙视为小量后，方程可写成 $K(T)\Delta=\eta(T)\Delta$。K 已包含这份谱的频率耦合、电子重整化及 Coulomb 项；在 η=1 时，线性化自洽方程才允许非零的无穷小能隙。η>1 与 η<1 分别位于这个模型临界点的两侧，数值夹区来自两个温度的实际解。这也解释了为何 λ 只有约 0.375，η 却能达到 1：它们是两个不同对象，不能用“λ 是否大于 1”代替配对判据。

温度扫描会同时改变 Matsubara 频率间隔。这里以能量表示 $\omega_j$，相邻正频率相差 $2\pi k_{\mathrm B}T$；固定约 0.10 eV 的截断时，温度升高，所需频率点就减少。下方 1.46 K 与 1.47 K 的 nsiw 分别为 127 与 126，是这项离散化的具体表现。细化温度只能缩小 η=1 的夹区；谱输入、截断和 Coulomb 模型的变化还要分别比较。


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

原生输出确认EPW6.0，1个MPI进程、1个OpenMP线程；完整版本与环境信息在下载包的epw.out。

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

然后看非线性方程里的 $\Delta(i\omega_0,T)$。线性表能定位交叉，却不告诉我们低温能隙函数有多大。非线性输入沿用同一个谱、μ* 和截断，改为 `tc_linear=.false.`；每个温度放在独立目录，避免一次温度失败中断后续所有温度的记录。

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

1.45 K的原生迭代在第19步明确打印收敛，最终deltai=0.03188725 meV、ethr=8.607533×10⁻⁷；完整迭代保持在包内。下面从数值文件核对同一结果。

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

| T / K | $\Delta(i\omega_0,T)$ / meV | 收敛迭代数 |
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

连续扫温在1.50 K发生未收敛失败，完整原文保留在nonlinear-w010/epw.out；该温度没有接受的能隙点。很小的失败迭代值不能写成已收敛的零能隙。

它并非“成功得到零能隙”。此时 Δ 已下降到极小量，但相对误差没有满足条件，Broyden 混合器最终无法分解矩阵，程序终止。图中没有把这条失败迭代补成 Δ=0 点；Tc 的判断仍来自已经收敛的线性本征值交叉。下载包保留了该次的 `epw.err` 和 `CRASH`，也保留了早期接口检查失败的输入输出，便于区分格式错误与物理求解过程中的失败。

![同一谱函数下的线性核本征值和已收敛非线性能隙函数](/Atlas/figures/epw-eliashberg/al-spectrum-tc.png)

左图中 η=1 的水平线给出线性化方程的交叉条件，阴影标出 0.01 K 的夹区。右图只连已收敛的独立温度点，标注的 1.50 K 失败不占一个人为的零能隙数据点。两图都固定输入 μ*=0.10 和截断 0.10 eV。

## 截断变化后，交叉点是否稳定

接着检查 Matsubara 截断对这个交叉温区的影响。下面三组只改变 `wscut`，原始 α²F 和输入 μ*=0.10 都保持不变；每组都细化了交叉温区。

| 请求截断 / eV | η>1 的温度与数值 | η<1 的温度与数值 | 实际交叉夹区 / K |
|---:|---|---|---|
| 0.10 | 1.46 K，1.0002425 | 1.47 K，0.9984385 | 1.46–1.47 |
| 0.20 | 1.45 K，1.0008521 | 1.46 K，0.9989809 | 1.45–1.46 |
| 0.40 | 1.57 K，1.0007327 | 1.58 K，0.9990310 | 1.57–1.58 |

![固定输入 Coulomb 赝势时的 Matsubara 截断敏感性](/Atlas/figures/epw-eliashberg/al-cutoff-sensitivity.png)

0.10 与 0.20 eV 的交叉很接近，0.40 eV 却又上移。这份表应该叫“固定输入 `muc=0.10` 的截断敏感性”，不能据此声称截断已经收敛。μ* 的定义与能量截断有关；把相同数值的 μ* 用在不同截断下，不等于已经证明它们代表完全相同的物理 Coulomb 模型。本页没有做相应重整化。原始谱的 k/q 网格、电子展宽、低频处理及结构协议也没有在这里得到新的材料级验收。

## 从原始输出提取温度与能隙

画图从原生输出重新提取，命令保持很短：

### 交给代码助手的任务：分开解析线性判据与非线性解

> 在外部谱 EPW 算例的各温度/截断分支目录读取 epw.in/out/err 与 al.imag_iso_* 文件，编写独立输出解析程序。按输入记录 muc、请求 wscut（eV）、nsiter、温度和求解器，按输出保留实际 Matsubara 截断及迭代次数。线性方程逐温度提取最大本征值 η，仅对正常完成且相邻 η 跨1的点给出 Tc 温区与线性插值；非线性方程逐温度记录明确收敛状态，提取首 Matsubara 点的 Z 和 Δ，将 Δ 从 eV 换为 meV。达到迭代上限或未收敛时保留失败状态，不能写成零能隙。输出 linear.csv、gap.csv、solver-status.json 和 tc-brackets.json，给出完整源码与输入路径。外部谱求解和 Wannier/EPW 原生谱入口分开归档；仅解析已有文件，不运行求解器或其他计算。

[已有完整输出解析源码 analyse_tc.py](/Atlas/examples/al-epw-tc/analyse_tc.py) · [原生结果核对源码 verify_native.py](/Atlas/examples/al-epw-tc/verify_native.py) · [外部谱单位转换源码 prepare_spectrum.py](/Atlas/examples/al-epw-tc/prepare_spectrum.py)。

<details>
<summary>analyse_tc.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from pathlib import Path
import csv,json,re,hashlib
b=Path(__file__).resolve().parent
linear=[]; nonlinear=[]; status=[]
pattern=re.compile(r'^\s*(\d+\.\d+)\s+(-?\d+\.\d{7})\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s*$',re.M)
for d in sorted(b.glob('*linear-w*')):
 if not d.is_dir() or not (d/'epw.out').exists():continue
 inp=(d/'epw.in').read_text();out=(d/'epw.out').read_text();err=(d/'epw.err').read_text() if (d/'epw.err').exists() else ''
 get=lambda k:re.search(r'\b'+k+r'\s*=\s*([^\n!,/]+)',inp,re.I).group(1).strip()
 w=float(get('wscut'));mu=float(get('muc'));ns=int(get('nsiter'))
 islinear=get('tc_linear').lower()=='.true.'
 finish=('Finish: Solving (isotropic) linearized Eliashberg equation' in out) if islinear else ('Finish: Free energy' in out or ('EPW          :' in out and 'Error in routine' not in out))
 status.append({'run':d.name,'native_finish':finish,'stderr_bytes':len(err.encode()),'fatal':'Error in routine' in out or bool(err),'iteration_limit':'Convergence was not reached' in out,'requested_wscut_eV':w,'muc':mu})
 if islinear:
  for T,eta,n,wa,it in pattern.findall(out):
   linear.append({'run':d.name,'T_K':float(T),'max_eigenvalue':float(eta),'nsiw':int(n),'actual_wscut_eV':float(wa),'iterations':int(it),'requested_wscut_eV':w,'muc':mu,'solver':get('tc_linear_solver').strip("'"),'complete':finish and not err,'nsiter':ns})
 else:
  its=[int(x) for x in re.findall(r'Convergence was reached in nsiter =\s*(\d+)',out)]
  temperatures=[float(x) for x in re.findall(r'Temp \(itemp =\s*\d+\) =\s*([\d.]+)',out)]
  for f in sorted(d.glob('al.imag_iso_*')):
   T=float(f.name.split('_')[-1]);row=f.read_text().splitlines()[1].split();vals=[float(x.replace('D','E')) for x in row]
   if T not in temperatures:continue
   idx=temperatures.index(T)
   nonlinear.append({'run':d.name,'T_K':T,'omega0_eV':vals[0],'Z_omega0':vals[1],'Delta_omega0_meV':vals[2]*1000,'converged':idx<len(its),'iterations':its[idx] if idx<len(its) else None,'requested_wscut_eV':w,'muc':mu,'whole_run_complete':finish and not err})
for name,rows in [('linear.csv',linear),('gap.csv',nonlinear)]:
 with (b/name).open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['empty']);wr.writeheader();wr.writerows(rows)
(b/'solver-status.json').write_text(json.dumps(status,indent=2)+'\n')
manifest={str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.rglob('*') if p.is_file() and p.suffix not in ('.gz',) and p.name not in ('terminal.log','SHA256.json') and p.stat().st_size<5000000}
(b/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'linear_rows':len(linear),'converged_gap_rows':len(nonlinear),'status':status},indent=2))

brackets=[]
for requested, run in [(.1,'linear-w010-refine'),(.2,'linear-w020-refine'),(.4,'linear-w040-refine')]:
 rows=sorted([r for r in linear if r['run']==run and r['complete']],key=lambda r:r['T_K'])
 for a,z in zip(rows,rows[1:]):
  if a['max_eigenvalue']>=1 and z['max_eigenvalue']<=1:
   frac=(a['max_eigenvalue']-1)/(a['max_eigenvalue']-z['max_eigenvalue'])
   brackets.append({'run':run,'requested_wscut_eV':requested,'muc':.1,'T_low_K':a['T_K'],'T_high_K':z['T_K'],'eta_low':a['max_eigenvalue'],'eta_high':z['max_eigenvalue'],'linear_interpolation_K':a['T_K']+frac*(z['T_K']-a['T_K']),'claim':'conditional model crossing bracket; interpolation is a plotting estimate, not material accuracy'})
(b/'tc-brackets.json').write_text(json.dumps(brackets,indent=2)+'\n')
```

</details>

<details>
<summary>verify_native.py 的完整源码</summary>

```python
from pathlib import Path
import csv, json, re, hashlib, sys

root=Path(sys.argv[1])
linear=list(csv.DictReader((root/'linear.csv').open()))
gap=list(csv.DictReader((root/'gap.csv').open()))
errors=[]; sources={}; checked_linear=checked_gap=0
for row in linear:
    p=root/row['run']/'epw.out'; text=p.read_text()
    sources[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    table=[m.groups() for m in re.finditer(r'^\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s*$', text, re.M)]
    selected=[r for r in table if abs(float(r[0])-float(row['T_K']))<1e-9]
    if len(selected)!=1:
        errors.append(['linear-row',row['run'],row['T_K'],len(selected)]); continue
    a=selected[0]
    expected=[float(row['max_eigenvalue']),int(row['nsiw']),float(row['actual_wscut_eV']),int(row['iterations'])]
    actual=[float(a[1]),int(a[2]),float(a[3]),int(a[4])]
    if actual!=expected:errors.append(['linear-values',row['run'],actual,expected])
    if 'Finish: Solving (isotropic) linearized Eliashberg equation' not in text:
        errors.append(['linear-no-finish',row['run']])
    if int(row['iterations'])>=int(row['nsiter']):errors.append(['linear-hit-limit',row['run']])
    checked_linear+=1
for row in gap:
    if row['converged']!='True' or row['whole_run_complete']!='True':continue
    d=root/row['run']; p=d/'epw.out'; text=p.read_text()
    sources[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    if 'Convergence was reached' not in text or (d/'epw.err').stat().st_size:
        errors.append(['nonlinear-state',row['run']])
    fs=list(d.glob('*.imag_iso_*'))
    if len(fs)!=1:errors.append(['gap-file-count',row['run'],len(fs)]);continue
    data=[line.split() for line in fs[0].read_text().splitlines() if re.match(r'^\s*[+\-\d.]',line)]
    omega,z,delta=map(float,data[0]); expected=float(row['Delta_omega0_meV'])
    if abs(1000*delta-expected)>1e-10:errors.append(['gap-unit-or-value',row['run'],1000*delta,expected])
    if abs(omega-float(row['omega0_eV']))>1e-14:errors.append(['omega',row['run']])
    sources[str(fs[0].relative_to(root))]=hashlib.sha256(fs[0].read_bytes()).hexdigest()
    checked_gap+=1
report={'linear_rows_checked':checked_linear,'independent_converged_gap_rows_checked':checked_gap,
        'source_sha256':sources,'errors':errors}
print(json.dumps(report,indent=2))
assert checked_gap==9 and checked_linear>=30 and not errors
```

</details>

<details>
<summary>prepare_spectrum.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math,xml.etree.ElementTree as ET
import numpy as np
b=Path(__file__).resolve().parent
raw=b/'source/alpha2F.dat'
a=np.loadtxt(raw); f=a[:,0]; y=a[:,4]
assert a.shape==(2000,11)
assert f[0]==0 and y[0]==0 and np.all(f[1:]>0) and np.all(y>=0)
h_meV_THz=6.62607015e-34/1.602176634e-19*1e15
f1=f[1:]; y1=y[1:]; w=f1*h_meV_THz
n=len(w)
np.savetxt(b/'al-sigma020.a2f',np.column_stack([w,y1]),fmt=['%.12f','%.8f'],header='omega_meV alpha2F ; QE lambda.x sigma=0.020 Ry; zero row removed only',comments='# ')
l_epw=2*w[-1]/n*np.sum(y1/w)
kbeV=8.617333262145e-5
wlogeV=math.exp(float(2*(w[-1]/1000)/n*np.sum(y1*np.log(w/1000)/(w/1000))/l_epw))
l_trap=float(np.sum(np.diff(f1)*((y1/f1)[1:]+(y1/f1)[:-1])))
x=ET.parse(b/'source/data-file-schema.xml').getroot()
aout=x.find('output/atomic_structure'); alat=float(aout.attrib['alat']); nat=int(aout.attrib['nat'])
avec=np.array([[float(v) for v in aout.find('cell/'+z).text.split()] for z in ('a1','a2','a3')]); at=avec/alat
bg=np.linalg.inv(at).T
atoms=list(aout.find('atomic_positions')); tau=np.array([[float(v) for v in a.text.split()] for a in atoms])/alat
species=list(x.find('input/atomic_species')); names=[a.attrib['name'] for a in species]; masses=[float(a.findtext('mass')) for a in species]
noncolin=x.findtext('input/spin/noncolin')=='true'
nelec=float(x.findtext('output/band_structure/nelec'))
fmt=lambda v:' '.join('%.16e'%float(z) for z in np.asarray(v).ravel())
lines=[str(nat),str(3*nat),fmt([nelec,0]),fmt(at),fmt(bg),fmt([abs(np.linalg.det(avec))]),fmt([alat]),fmt(tau),fmt([m*1.66053906660e-27/9.1093837015e-31/2 for m in masses]+[0.0]*(10-len(masses))),' '.join(str(names.index(a.attrib['name'])+1) for a in atoms),'T' if noncolin else 'F','F','! spectrum-only adapter: no Wannier centers calculated','! spectrum-only adapter: no Wannier lattice L calculated']
(b/'crystal.fmt').write_text('\n'.join(lines)+'\n')
r={'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'source_shape':list(a.shape),'selected_sigma_Ry':.020,'source_spectrum_width_THz':.12,'source_mu_star':.1,'solver_mu_star':.1,'source_xml_sha256':hashlib.sha256((b/'source/data-file-schema.xml').read_bytes()).hexdigest(),'frequency_conversion_meV_per_THz':h_meV_THz,'removed_rows':[{'omega_THz':0,'alpha2F':0}],'nqstep':n,'omega_max_meV':float(w[-1]),'epw_rectangle_lambda':float(l_epw),'trapz_lambda_printed_grid':float(l_trap),'epw_omega_log_K':wlogeV/kbeV,'max_print_rounding_step_deviation_THz':float(np.max(abs(np.diff(f)-f[-1]/n))),'crystal_adapter':'QE XML physical fields; amass uses native Rydberg mass unit AMU_RY=AMU_SI/ELECTRONMASS_SI/2, fixed ntypx=10 with unused species slots zero; no computed Wannier centers; trailing comments are skipped records in EPW6.0 isotropic fila2f reader','material_Tc_acceptance':'not assessed'}
(b/'spectrum-checks.json').write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))
```

</details>

```bash
python3 analyse_tc.py
python3 plot_tc.py
```

`analyse_tc.py` 生成 `linear.csv`、`gap.csv`、`solver-status.json` 和 `tc-brackets.json`；它从线性表读 η、实际频率数和迭代数，从原生 `imag_iso` 文件读第一频率点。`gap.csv` 同时保留早期连续扫温已收敛的前四点，绘图只选 `whole_run_complete=True` 的独立单温目录，避免重复画点。脚本不从失败迭代里寻找一个很小的数字冒充正常态。`plot_tc.py` 与 `atlas_plot_style.py` 放在同一目录，需要 NumPy 和 Matplotlib。上述命令在本机也可执行：它把同一份数据分别导出为便于网页阅读的 PNG、SVG，以及宽 183 mm、保留文字的矢量 PDF，文件写入 `figures/`。

绘图保留所有通过验收的点，用符号区分采样点，用细线连接而不做平滑拟合。第一张图的灰带来自相邻温度对 η=1 的夹区；第二张图的短横线也是采样夹区，不是统计误差棒。坐标轴、单位和曲线说明都应保留到论文图中。字体、线宽与矢量导出方式见[科研绘图与导出](/Atlas/plotting/)；这些版式设置不改变数值或截断范围。

EPW 6.0 对上述 Al 谱函数求解了各向同性虚频轴方程。低温非线性能隙函数保留逐温度收敛记录，线性方程给出 η=1 的夹区和 LAPACK 对照。不同 `wscut` 下的夹区仍有差别，引用温度时需同时给出谱来源、μ*、Matsubara 截断和各向同性近似。

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

实跑程序为 QE 7.5、EPW 6.0。在线[输入参数页](https://docs.epw-code.org/Inputs/Inputs.html)目前标为EPW6.1，教程可用于理解流程；本例精确接口按QE7.5标签下的EPW6.0源码与原生输出解释。

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

局域化输入中的投影是设计的初始猜测，中心和空间展布应读取 `al.wout`，不能拿输入投影充当结果：

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

Wannier 函数的空间展布较小、局域化迭代达到停止条件，仍不能替代插值能带的检查。本次取 Wannier90 原生 `al_band.kpt` 中的 166 个路径点，让 `pw.x` 在同一份 SCF 势上直接计算，并与 `al_band.dat` 逐点比较。每个 k 点按能量升序配对前 4 个本征值；该检查比较能谱，不跨交叉点追踪轨道身份。两边统一减去响应 SCF 输出的 8.4122 eV，没有单独对齐每轮的费米能，也没有拟合或平移曲线。

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

还需显式给出电子粗网格 `nk1..3=12`、声子粗网格 `nq1..3=4` 以及本例细网格 `nkf1..3`、`nqf1..3`。这里把 `fsthick=1.0` 作为积分中保留费米能附近态的窗口控制，不把它当作 Wannier 冻结窗。谱文件 `al.a2f` 前三列为 ω（meV）、α²F(ω) 和累计 λ(ω)；脚本读取数值行，保留文件尾部的电子展宽、Fermi 窗口、DOS 与耦合总和，不把尾部说明误读成数据。

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
| 力常数 / 声学求和规则 | `lifc=.true.` 读取力常数；EPW 的 `asr_typ='crystal'` 施加平移声学求和规则 |

父链 `q2r.x` 输入中的 `zasr='simple'` 针对 Born 有效电荷，这份金属 Al 计算没有求 Born 电荷。EPW 在 `lifc=.true.` 读取力常数后，按 `asr_typ='crystal'` 对力常数施加声学求和规则；这次粗矩阵、细积分和全 q 频率检查的原生输出均打印 `Imposed crystal ASR`。两种参数的作用对象不同，应分别记录。[q2r 的 zasr 定义](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html#zasr)

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
这些误差为什么要在生成谱前读？本次电子展宽是 100 meV，而近 EF 路径上的最大能量偏差为 92.3 meV，已接近这个能量选择尺度。偏差可能改变哪些电子态落入双 δ 的有效范围；RMS 较小也不能抹去局部偏差。这只是量级比较，不是把能带误差直接传播成 Tc 误差。加密 24³ 的细网格会更密地取样同一个插值函数，不能自动修复粗网格或能窗造成的插值偏差。先核对这里的直接能带与插值能带，再比较粗网格、细积分和展宽，才能解释后面 α²F 的变化。


![同一路径上的直接 QE 与 Wannier 能带，以及四套设置的误差对比](/Atlas/figures/epw-eliashberg/al-wannier-validation.png)

左图只放大共同费米参考附近 ±2 eV 的部分；右图取直接 QE 能带中落在 ±1 eV 内的 47 个态，分别显示 RMS 和最大绝对误差。横轴同时列出粗网格与冻结窗上限，避免把最初两项参数同时改变的效果全算到网格上。这里的 8.4122 eV 只是共同绘图零点；实际精细网格 EPC 输出的费米能为 8.424415 eV，二者用途不同。全四带的 RMS 误差仍为 0.2853 eV，不能把费米能附近的精度推广到全部能带。

解包后运行 `python3 plot_wannier_validation.py` 可由 `derived/band-*.csv` 重画此图。`plot_wannier_validation.py` 与 `atlas_plot_style.py` 保留能量零点、样本筛选和每套设置的参数，输出在 `figures/`，不拟合或移动两条能带。

最终 `al.wout` 的总 spread 为 11.997746862 Å²，解纠缠和局域化各自满足本次输入的迭代判据。实空间衰减也须结合所覆盖的距离看：对原生 `decay.H`、`decay.epmate` 和 `decay.epmatp`，把距离最外侧 20% 区间的最大幅度除以全局最大幅度，分别为 0.0001289、0.001995、0.02914；对应最大距离为 23.7364、23.7364、7.9121 Å。这些只是可复核的衰减诊断，不是预先接受的容限，声子方向的尾部仍比电子方向更明显。

粗电子网格仍采用 12³。48³ / 24³ 的细积分尝试在约 118 s 时只处理了 942/13563 个筛选后 q 点，估计无法在预定短时作业内完成，故停止并保留输出。最终 24³ / 12³ 路线已经形成完整的谱和方程求解证据；它没有给出电子粗网格、声子粗网格、细积分、展宽、Fermi 窗口及 Matsubara 截断的联合收敛结论。最初 4³ 插值的谱及 1 K 非线性未收敛输出也保留在包中，只用于展示诊断过程。

### 重跑与输出核对

下载包提供完整输入、纯文本原生输出、比较 CSV 和提取脚本，不打包赝势正文、波函数、dvscf 或二进制 Wannier 矩阵。要从头重跑，应先用包内 SCF/DFPT 输入产生声子父链；已有同一父链时，运行只复制文件的收集脚本，再继续 NSCF。

这里采用下载包根目录下的 `00-phonon/`、`01-nscf/`、`02-wannier/`、`03-coarse/`、`04-fine/` 布局，`phonon-save/` 与它们同级。包内 `inputs/epw1-k12.in`、`epw-coarse.in` 和 `epw2-k12-fine24.in` 已使用 `dvscf_dir='../phonon-save'`。前面展示的历史输入写作 `../../phonon-save`，对应当时更深一层的运行目录；若用它建立重跑副本，要在下面的 `vi` 步骤改为 `../phonon-save`。各阶段的 `outdir='./tmp'` 读取自己的临时目录，NSCF 的 `pseudo_dir='./pseudo'` 读取复制进该阶段的赝势目录。

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
vi 02-wannier/epw1.in
cd 02-wannier
mpirun -np 1 epw.x -nk 1 -in epw1.in > epw1.out 2> epw1.err
cd ..

mkdir 03-coarse
cp -r 01-nscf/tmp pseudo 03-coarse/
cp 02-wannier/{al.ukk,al.win,al.bvec,al.mmn} 03-coarse/
cp inputs/epw-coarse.in 03-coarse/epw-coarse.in
vi 03-coarse/epw-coarse.in
cd 03-coarse
mpirun -np 8 epw.x -nk 8 -in epw-coarse.in > epw-coarse.out 2> epw-coarse.err
cd ..

mkdir -p 04-fine/tmp
cp 03-coarse/{crystal.fmt,epwdata.fmt,dmedata.fmt,vmedata.fmt,wigner.fmt,al.ukk} 04-fine/
cp 03-coarse/tmp/al.epmatwp 04-fine/tmp/
cp inputs/epw2-k12-fine24.in 04-fine/epw2.in
vi 04-fine/epw2.in
cd 04-fine
mpirun -np 8 epw.x -nk 8 -in epw2.in > epw2.out 2> epw2.err
```

上面的复制关系也封装在下载包的 `tools/prepare_stage.py` 中，作为可选的重跑辅助。目录已存在时应先读旧输出，不要在上面反复启动新程序。原始记录保留每次执行的独立目录、输入哈希、stdout、stderr、调度记录和失败状态。输入、父计算文件与原生结束状态分别核对。λ 和 Tc 的数值收敛及物理有效性仍需单独检查。

## 原生 EPW 谱的线性判据与低温解

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

第一频率点的 Δ=1.2821328449×10⁻⁴ eV，即 $\Delta(i\omega_0,0.25\,\mathrm{K})=0.1282133\,\mathrm{meV}$。这里有一个通过收敛检查的低温解，没有把单点画成完整的能隙温度曲线，也没有由此声称实轴激发能隙已经求出。

![EPW 原生插值谱和相应的线性化 Eliashberg Tc 求解](/Atlas/figures/epw-eliashberg/al-native-spectrum-tc.png)

重画时在这一支的数据包目录运行：

```bash
python3 analyse_tc.py
python3 plot_native_tc.py
```

`plot_native_tc.py` 需要同目录的 `atlas_plot_style.py`、NumPy 与 Matplotlib，输出 PNG、SVG 和宽 183 mm 的矢量 PDF。`analyse_tc.py` 从这些原件提取绘图数据：`source-spectrum.csv` 保留谱和累计 λ，`linear.csv` 保留每个温度的本征值、实际频率数和迭代数，`gap.csv` 记录这一个收敛的低温点，`tc-brackets.json` 记录实际跨 1 的两端。它们与前面的外部 QE 谱数据分包保存。

这条“QE 粗网格 → Wannier → EPW 精细网格谱 → Eliashberg 求解”给出 0.84–0.85 K 的交叉温区。0.84–0.85 K 应始终连同这组网格、展宽、μ*、截断和各向同性近似一起陈述。它没有代替上游的插值质量检查，也没有证明粗 q 网格、精细积分网格或材料 Tc 已经收敛。

<span id="material-anisotropic-route"></span>

## Ba₂N 图7为什么需要各向异性数据

[Qiu等，PRB105,165101](https://doi.org/10.1103/PhysRevB.105.165101)图7（原文PDF第5页，附录说明在第6页）展示未应变Ba₂N的各向异性能隙随温度变化。每个温度有能隙分布，随升温整体向零收缩，在约6 K消失；该图不是Al最低Matsubara点的单条等方Δ(T)曲线。正文由图3谱代入简式得到3.4 K，这与各向异性ME采用的近似不同，应分别标注。

[Fig. 7，PDF第5页及第6页附录](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.105.165101)把温度放在横轴、能隙Δ（meV）放在纵轴，每个温度展示一条沿能隙方向的分布曲线，并把曲线在对应温度位置横向错开。先看同温度下分布的范围，再看整体随温度向零收缩；图中的蓝线不是一个平均能隙点。原图注没有交代分布高度的归一化或具体实/虚轴采样，本文不据线宽读取概率、费米面权重或准粒子激发能隙。自己的各向异性输出若采用这种图法，先明确所画是哪个频率/能量上的Δnk，再用原始k权重统计分布，固定bin宽和横向显示尺度，并保留能带/费米面片归属。用gnuplot把各温度的分布密度作为横向偏移、Δ作为纵轴即可复现这种排列。当前Al外部谱给九个已收敛Δ(iω₀,T)标量点，原生谱只给一个低温点，已有图按各自数据作点图；逐温度(n,k)分布须来自材料各向异性输出，平均α²F不能生成Fig. 7那样的分布。

图3、6回答“哪些q和模式贡献耦合”；图7进一步回答“不同电子态怎样配对、随温度怎样闭合”。α²F是电子态与散射信息的平均，平均后无法倒推出Δnk。多口袋费米面存在并不自动证明多能隙；必须让逐带逐k的方程结果、口袋归属和收敛证据共同支持判断。

## 从材料 DFPT 与 Wannier 矩阵走到 Δnk(T)

材料路线仍从同一结构、赝势、SOC/自旋模型和SCF密度出发。完整均匀NSCF给出Bloch态，完整粗q DFPT给出dyn、patterns、dvscf；Wannier阶段对费米附近和所用Fermi窗口内的能带作直接对照，再检查电子与声子方向的耦合实空间衰减。这些前置关系与上面的Al原生链相同；二维材料的实际网格、能窗、投影与极化处理要由它自己的输入和质量比较确定。

随后保留电子态和散射分辨的细网格矩阵，按匹配版本写出prefix.ephmat/中的ephmat、freq、egnv、ikmap及相应晶体/采样信息。[EPW6.0读取器](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/io/io_supercond.f90)分别读取这些量；外部fila2f的两列谱不能替代它们。官方[超导教程](https://docs.epw-code.org/tutorials/tutorial_04/index.html)的各向异性步骤用ephwrite保存矩阵，并以laniso进入方程；a2f_iso的谱生成路线本身选择各向同性，不能只在那份平均谱输入中换一个开关就恢复各向异性。

求解时记录Fermi窗口、电子/声子展宽、粗细网格、Coulomb模型、Matsubara截断与温度列表。费米面限制近似围绕EF保留配对态；全带宽方法还处理电子能量方向的信息，两者与等方/各向异性是不同选择维度。

先在温度范围内求得收敛解，再细化能隙趋近零的温区，必要时使用该版本支持的线性化判据。每个温度保存自己的迭代状态、Znk(iωj)、Δnk(iωj)和(n,k)映射。保持同一套k点权重，比较各费米面片的分布、平均及上下界，并在低温把Δnk投影到费米面；若画直方图，应按采样权重归一化，不能把不均匀k点个数直接当DOS。

需要实轴激发能隙时，另外报告解析延拓方法、实轴频率网格及检查；虚轴最低点、延拓后的实频函数和由自洽能隙边缘定义的数值应分列。材料中一次高温迭代失败不能当作能隙已经闭合。

> 读取一个已完成的材料各向异性EPW分支，先根据版本源码确认输出格式和(n,k)映射。逐温度提取明确收敛状态、最低Matsubara点的Z与Δ及单位，按原始k权重生成各费米面片的能隙分布、均值和范围；保留对应输入、温度、Coulomb模型及截断。只对收敛点和实际采样温区报告闭合趋势，失败温度保留状态；实轴/虚轴分别出表。保存完整解析源码与输出，不用平均α²F或Al数据生成材料Δnk。



回到[逐模线宽](/Atlas/m/phonon-linewidth/qe/)定位振动，沿[α²F](/Atlas/m/eliashberg-a2f/qe/)追踪频段贡献，再在相同输入模型下比较[Tc公式](/Atlas/m/allen-dynes/qe/)与方程结果。
