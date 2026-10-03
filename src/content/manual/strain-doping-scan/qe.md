拉伸晶格以后，界面电荷、费米能附近的谱和声子都可能变化。困难在于把这些变化接成一个解释：某层在 $E_{\mathrm F}$ 附近的 PDOS 下降，究竟是能带移出了这个能量点，还是整段谱权重减少？声子变软以后，耦合就一定增强吗？应变扫描需要在同一组结构与参考下依次回答这些问题。能量和应力先核对形变；电子态、空间电荷与逐模耦合再解释材料响应。

这里先用六个真实 fcc Al SCF 点说明怎样修改晶胞、保留独立密度并读出应力，再接 ZrCl₂/Sc₂C 的既有冻结电子对照。Al 是一原子操作样本，采用 LDA-PZ；异质结是六原子界面，采用另一套结构和电子协议。两组结果各自解释，不能将 Al 曲线当作异质结的应变响应。[Al 输入、输出与后处理包](/Atlas/examples/interface-magnet-strain-doping-scan/example-pack.tar.gz)保留完整计算文件。

## 百分比表示应变，应力从输出读取

面内双轴应变定义为 $\varepsilon=\frac{a-a_0}{a_0}$。+1.5% 对应 $\varepsilon=0.015$，即两条面内基矢的面内分量同时乘 1.015，晶格角保持不变；纯面内应变不放大真空方向。单轴 x 应变则只将所有基矢的 x 分量乘 $1+\varepsilon$。本例 Al 使用后一种定义，y、z 均固定。

应变是无量纲的几何变化，常以百分比给出；应力是响应张量，单位为 kbar、GPa 或明确厚度定义下的二维量。“+1.5% 双轴应变”不能写成“+1.5% 应力”。如果研究控制的是外加压力，需另说明压力单位和放松条件。对有真空的二维超胞，程序的三维应力还含超胞体积归一化，比较时固定真空高度；它不是单层厚度无关的二维应力。

多原子界面要先规定哪些内部坐标可以放松。在固定 ε 下进行[离子弛豫](/Atlas/m/relax/qe/)，再用验收结构做 SCF；开放自由面内晶胞的 vc-relax 会释放施加的形变。若采用冻结坐标做机制对照，就明确称冻结快照，并保留它的残余力。这两种结果回答的结构问题不同。

## 先确定哪些量可以动

母体结构来自 [Al 晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax) 的完成分支，立方晶格常数为 3.95606780081 Å，采用 LDA-PZ 与 `Al.pz-vbc.UPF`。原胞的三条基矢并不沿三个直角坐标轴。要施加 x 方向应变 ε，应把**每一条基矢的 x 分量**乘以 $1+\varepsilon$；y、z 分量保持不变。

例如 +0.5% 应变使 −1.97803390040536 Å 变为 −1.98792406990739 Å。两个含非零 x 分量的基矢都要改。若只把第一条基矢整体放大，得到的是另一种形变。

母体输入和保存数据的接续见 [Al 声子前的 SCF](/Atlas/m/phonon-dfpt/qe/)。这里复制的是优化后晶胞上的 `dfpt/al.scf.in`，每个应变点重新做 SCF，不继承一份共用的可写密度。准备新的计算时，先用 `mkdir xx_+0.005` 建立目录，再保存母体输入并编辑应变文件；下载包中已有这六个目录，复算应另建目录。实际交互如下：

```console
maxwell@maxwell:~/al/elastic$ cp ../dfpt/al.scf.in al.reference.in
maxwell@maxwell:~/al/elastic$ cp al.reference.in xx_+0.005/al.scf.in
maxwell@maxwell:~/al/elastic$ vi xx_+0.005/al.scf.in
```

在 `vi` 中用 `/CELL_PARAMETERS` 找到晶胞，修改对应分量，按 Esc 后输入 `:wq` 保存退出。然后重新打开文件核对：

```console
maxwell@maxwell:~/al/elastic$ cat xx_+0.005/al.scf.in
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
-1.98792406990739 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.98792406990739 1.97803390040536 0.00000000000000
K_POINTS automatic
16 16 16 0 0 0
```

原胞只有一个 Al 原子，分数坐标仍为 (0,0,0)，没有需要单独优化的内部相对位置。这里使用 `calculation='scf'`；若再次运行自由晶胞的 `vc-relax`，程序会释放人为施加的应变。多原子结构若需要应变下的内部弛豫，应先做固定晶胞的 `relax`，验收力后再进入同协议 SCF，操作见 [固定晶胞优化](/Atlas/m/relax/qe/)。

六个目录分别对应 ε = −0.008、−0.005、−0.003、+0.003、+0.005、+0.008。每个目录保留自己的 `al.scf.in` 和 `tmp`，不共用可写的电荷密度目录。赝势、40/160 Ry 截断能、16³ k 网格、MV 展宽 0.02 Ry 及电子收敛阈值保持一致。

## 把短 SCF 串起来，逐点读取输出

存档作业另外包含六个剪切点，所以下面完整脚本有十二次 SCF。它们在同一份 8 进程作业内串行执行；本文只读取六个 xx 点。脚本与提交回执是这次 Al 计算的记录。公开文件中的 `<工作目录>` 和 `<qe_bin>` 需要换成自己的位置。

```console
maxwell@maxwell:~/al/elastic$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-elastic
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
cd "<工作目录>/elastic/xx_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
maxwell@maxwell:~/al/elastic$ sbatch run.slurm
Submitted batch job 1956
```

运行时用 `squeue -j 1956` 看队列状态，用 `tail -f xx_+0.005/al.scf.out` 跟踪这个点的电子迭代。按 Ctrl+C 只退出日志查看。由于脚本依次执行各目录，排在后面的 OUT 尚未出现，可能只是前一个点还在计算；结合当前队列和最近更新的文件判断。

计算结束后，用 `less xx_+0.005/al.scf.out` 阅读输出。`/iteration` 定位电子迭代，`/!` 定位带感叹号的最终能量，`/total   stress` 找到应力，按 `G` 到文件末尾。这个点的能量部分为：

```text
!    total energy              =      -4.19087715 Ry
     estimated scf accuracy    <          1.5E-15 Ry
     smearing contrib. (-TS)   =      -0.00000256 Ry
     internal energy E=F+TS    =      -4.19087459 Ry

     The total energy is F=E-TS. E is the sum of the following terms:
     one-electron contribution =       2.94683257 Ry
     hartree contribution      =       0.00985377 Ry
     xc contribution           =      -1.63714978 Ry
     ewald contribution        =      -5.51041115 Ry

     convergence has been achieved in   7 iterations
```

SCF 在七次电子迭代后收敛，估计误差小于 1.5×10⁻¹⁵ Ry。金属计算用了展宽，程序也明确写出 `The total energy is F=E-TS`。本页表格统一使用感叹号行的 F；不要把部分目录的 F 与另一些目录的 `internal energy E=F+TS` 混在一起拟合。

往下读应力，而不只看总能量：

```text
     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=       -4.08
  -0.00005559   0.00000000   0.00000000           -8.18        0.00        0.00
  -0.00000000  -0.00001386   0.00000000           -0.00       -2.04        0.00
   0.00000000   0.00000000  -0.00001386            0.00        0.00       -2.04
```

左侧 3×3 数值的单位是 Ry/bohr³，右侧是 kbar，末尾 `P` 为三个对角分量的平均。QE 这组打印值采用压缩为正的符号；为了按拉伸为正画曲线，表格中的 σ 取相反号，再换成 GPa。于是本例右侧的 −8.18 kbar 对应约 +0.818 GPa 的纵向拉应力。表格从精度更高的左侧数值换算，保留的小数会与两位小数的 kbar 略有差别。

零原子力也不能代替应力检查：这个单原子原胞在均匀应变下依然有零原子力，但有非零应力。应变扫描中这个应力正是要记录的响应。

这里应变沿笛卡尔 x 方向施加，输出应力也按同一笛卡尔坐标系读取，不是沿斜原胞第一条基矢的分量。y、z 没有放松，所以小应变极限的纵向与横向斜率分别联系当前取向下的 C₁₁、C₁₂；不能把纵向斜率直接称为允许横向泊松收缩后的杨氏模量。三维 Al 的应力以体积归一化；若把同样操作换到有真空的单层，GPa 数字还会依赖真空高度，需要重新定义二维弹性量。

文件末尾的计时和结束行说明 pw.x 正常返回；每个目录还应分别确认电子收敛，没有最终的对角化失败，并核对本次输入中的晶胞和 k 网格。当前 +0.5% 点耗时 3.81 s，六个纵向点均保存了独立 OUT。

```text
     PWSCF        :      3.30s CPU      3.81s WALL

   JOB DONE.
```

## 把能量与应力放在同一张图里

提取脚本 [analyse_strain.py](/Atlas/examples/interface-magnet-strain-doping-scan/analyse_strain.py) 从各点 OUT 读取能量和应力，写成 [strain-stress.csv](/Atlas/examples/interface-magnet-strain-doping-scan/elastic/strain-stress.csv)。其中纵向应变的六行为：

| x 应变（%） | F（Ry/原胞） | 拉伸为正的 $\sigma_{xx}$（GPa） | $\sigma_{yy}$（GPa） |
|---:|---:|---:|---:|
| -0.8 | -4.19084711 | -1.395292 | -0.343932 |
| -0.5 | -4.19087241 | -0.863654 | -0.212861 |
| -0.3 | -4.19088294 | -0.515015 | -0.127540 |
| +0.3 | -4.19088572 | +0.495891 | +0.121362 |
| +0.5 | -4.19087715 | +0.817757 | +0.203888 |
| +0.8 | -4.190856 | +1.281874 | +0.329074 |

这里一个原胞只有一个原子，因此每原胞和每原子的能量数值相同。绘图时减去这六个采样点中最低的 F，单位换成 meV/atom；该零点只是绘图参考，并非无应变母体能量。图中的连线连接实际采样点。

![Al 的六点纵向应变扫描：能量与应力](/Atlas/examples/interface-magnet-strain-doping-scan/figures/strain-scan.png)

右图的纵向应力随应变近似线性，横向应力也发生变化。这说明形变约束确实产生了相应响应。当前采样没有零应变点，也未给出应变下的电子谱或声子，因此不能从能量谷底读出超导的最优应变。切换到异质结时，每个 ε 的内部结构与电子密度都要有独立来源。

要重新画图，解包后进入 `example-pack`，在有 NumPy 和 Matplotlib 的环境运行：

```bash
python3 plot_strain.py
```

[完整绘图脚本](/Atlas/examples/interface-magnet-strain-doping-scan/plot_strain.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/interface-magnet-strain-doping-scan/atlas_plot_style.py)） 只读取这张 CSV，筛选 `mode=xx`，按实际应变排序，输出 `figures/strain-scan.png` 和 SVG。连线用于连接相邻采样点；它没有寻找连续曲线的极小值。

## 从应变结构比较电荷与电子态

对界面模型，还要区分面内形变和随后的内部调整。把分数坐标原样保留而改变面内基矢，会仿射改变面内原子间距；在固定晶胞下弛豫原子，则允许键长和层间距离重新平衡。记录实际层间距离、原子位置和残余力，才能知道后面的谱变化来自哪一个结构。两态若一个冻结、一个已经弛豫，就同时改变了应变与结构处理，不能只归因于 ε。计算目录中的结构应跟随该态的密度和声子文件，不靠文件夹名“+1.5%”配对。

ZrCl₂/Sc₂C 的供受层共同形成新的电子态。应变改变键长和层间距离，既可能改变电荷平衡，也可能改变轨道杂化。比较两应变的 PDOS 前，先保留每态的结构、电子数、赝势、k 网格、SCF 展宽和 projwfc 展宽。各态以自己的 EF 对齐可以比较近 EF 谱形，绝对带偏移则要接[静电势参考](/Atlas/m/electrostatic-potential/vasp/)；这两种能量基准不能混用。

已有四态对照在 0% 和 +1.5% 下，分别计算完整异质结与冻结在对应几何的中性 Sc₂C 层。它使用 QE 7.2、100/800 Ry、32×32×1 k 网格，SCF Gaussian 展宽 0.0037 Ry；projwfc 展宽 0.0022 Ry，能量步长 0.005 eV。异质结原子 #2 C 与 #5–6 Sc 合成 Sc₂C 层，#1 Zr 与 #3–4 Cl 合成 ZrCl₂ 层。完整协议与原子映射见[四态说明](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/README.txt)，操作接[投影与布居](/Atlas/m/population-analysis/qe/)。

下表直接读取已经公开的[能量分辨 PDOS](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos_long.csv)，选择离各自 EF 最近的网格点；没有对 EF 处插值。层投影与总投影的单位均为 states/(eV·cell)。

| 冻结体系 | 应变 | 最近 E−EF / eV | Sc₂C 层投影 | ZrCl₂ 层投影 | 总投影 |
|---|---:|---:|---:|---:|---:|
| 异质结 | 0% | +0.0008 | 2.564971 | 2.222928 | 4.78 |
| 中性孤立 Sc₂C | 0% | +0.0008 | 4.232280 | — | 4.23 |
| 异质结 | +1.5% | −0.0023 | 2.080865 | 2.459610 | 4.54 |
| 中性孤立 Sc₂C | +1.5% | +0.0022 | 4.477110 | — | 4.48 |

异质结的近 EF Sc₂C 层投影从 2.564971 降至 2.080865，而匹配几何的孤立 Sc₂C 从 4.232280 升至 4.477110。界面中的层谱变化与中性孤立层的形变响应不同，值得沿完整能窗检查杂化。这里列的是最近能量点的投影态密度，不能把它称为自由载流子数、Bader 电荷或精确 N(EF)。原始父快照的最大残余力为 2.40×10⁻⁴ 与 1.20×10⁻⁴ Ry/Bohr，未达到原力阈值，所以这个对照解释冻结几何的电子响应。

这份冻结对照还保存了完整谱形，见下图。实线是异质结内 Sc₂C、ZrCl₂ 层的原子投影，蓝色虚线是同应变几何中的中性孤立 Sc₂C；两面板共用纵轴，各态用自己的 $E_{\mathrm F}$ 作零点。这样可以同时看界面杂化和单层形变响应，而不把某个最近网格点的高低当作整个能窗的变化。图中投影按 simulation cell 计数，没有各曲线除以自身峰值，也没有归一化成同一条曲线。

![四态冻结几何的层 PDOS 与孤立层对照](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos.png)

这里的“下降”只针对各自 EF 最近的那一个网格点。换一种读法，在每态自身 EF 的 ±0.1 eV 内积分，异质结 Sc₂C 层的谱权重反而从 0.404262 增到 0.416509 states/cell。为避免四态网格零点不一致导致积分范围不同，使用原谱的分段线性表示，只在 −0.1、+0.1 eV 两个端点取线性值，再做梯形积分；谱内部仍使用原有 0.005 eV 网格。下表由同一份 CSV 实际重算：

| 冻结体系 | 应变 | Sc₂C 窗内投影权重 / states·cell⁻¹ | ZrCl₂ 窗内投影权重 / states·cell⁻¹ | 总投影权重 / states·cell⁻¹ |
|---|---:|---:|---:|---:|
| 异质结 | 0% | 0.404262 | 0.317533 | 0.721729 |
| 中性孤立 Sc₂C | 0% | 0.667095 | — | 0.666938 |
| 异质结 | +1.5% | 0.416509 | 0.329840 | 0.746342 |
| 中性孤立 Sc₂C | +1.5% | 0.806143 | — | 0.806404 |

Sc₂C 层的窗内权重在界面中增加约 3.03%，孤立层中则增加约 20.84%。因此，这两态并不支持“应变令整个近 EF 能窗的 Sc₂C 投影减少”；它们显示的是最近点与整段能窗的变化不同，而且接触后的形变响应比这份中性孤立层对照弱。沿图中的蓝色曲线检查峰形和位置，就能理解为什么一个点降低而有限窗口积分升高。窗口宽度仍是这次比较的定义，不能将 ±0.1 eV 的结论推广到整个价带。

下图将原谱放大到 EF±0.5 eV，灰区标出上表真正积分的 ±0.1 eV。两面板共用纵轴；蓝色实线为界面 Sc₂C 层、蓝色虚线为同几何中性孤立层、橙线为界面 ZrCl₂ 层。观察灰区里的线形而不只看零点高度，可以把“谱峰旁一点的下降”与“整个窗口的面积增加”区分开。

<figure><img src="/Atlas/examples/enrichment-20261003/strain/pdos-window.png" alt="四态冻结PDOS的近费米能放大图，灰色标出正负0.1eV积分窗" loading="lazy"/><figcaption>公开四态 CSV 的 gnuplot 重绘：EF 参考来自各态，原投影幅值保留，灰区是固定能窗。连线连接原始能量采样，与表中采用的分段线性积分一致。</figcaption></figure>

这种比较采用了 [Ba₂N 原文 Fig. 4(a–c)，PDF 第 4 页](https://doi.org/10.1103/PhysRevB.105.165101)的相对 EF 能量轴和有标识的投影曲线；原论文颜色区分应变，本图颜色区分层，实/虚线区分接触环境，两个应变用独立面板比较。这里额外画灰区是为了说明自己的积分定义，灰区用于本页的积分定义；下面的 gnuplot 源码按自己的 CSV 编写，只参考原图可见的坐标与曲线表达。下载 [gnuplot 完整源码](/Atlas/examples/enrichment-20261003/strain/plot_window_pdos.gnu)和[矢量 SVG](/Atlas/examples/enrichment-20261003/strain/pdos-window.svg)。脚本直接读同一 CSV，按状态筛选第4列能量和第5/6列投影，共享可见范围内的纵轴，不另拟合峰形。

这里积分的是投影谱，没有占据因子，还包含 EF 以上的态；states/cell 也不等于转移电子数。QE 7.2 的 [projwfc 定义与输出格式](https://github.com/QEF/q-e/blob/qe-7.2/PP/Doc/INPUT_PROJWFC.def)区分总 DOS 和总原子投影，本表仍用后者。层投影相加与文件总投影的微小差异保留为打印与求和检查，不把曲线强制修正成相等。窗内平均 PDOS 等于该权重除以 0.2 eV，可用于同宽窗口的谱强度比较；它也不是精确的 N(EF)。复算脚本、明确的写码需求和实际输出放在下文“重提冻结 PDOS 表的源码与结果”中。

图的原 CSV 和原图均来自上述四态存档。要用 gnuplot 复现相同叠图，下载[完整绘图源码](/Atlas/examples/research-strain-literature/plot_frozen_pdos.gnu)，与 frozen_pdos_long.csv 放在同一目录，执行 gnuplot plot_frozen_pdos.gnu。脚本直接使用第 4 列 E−EF、第 5/6 列层 PDOS，按第 1 列状态筛选；固定线色与实/虚线区分层和环境，并按所有可见曲线确定共享纵轴。默认能窗为 ±2 eV，缩到 ±0.5 eV 的命令如下。缩窗只改变显示范围，既不重算展宽，也不平滑或插值。

```bash
gnuplot plot_frozen_pdos.gnu
gnuplot -e "energy_window=0.5" plot_frozen_pdos.gnu
```

<details>
<summary>plot_frozen_pdos.gnu 完整源码</summary>

```gnuplot
# Read the published CSV directly; all energies are already relative to each EF.
# Run: gnuplot plot_frozen_pdos.gnu
# Optional: gnuplot -e "energy_window=0.5" plot_frozen_pdos.gnu
if (!exists("datafile")) datafile="frozen_pdos_long.csv"
if (!exists("output_path")) output_path="frozen-pdos-gnuplot.png"
if (!exists("energy_window")) energy_window=2.0
set encoding utf8
set datafile separator comma
# Shared y range from every plotted Sc2C/ZrCl2 trace within the chosen window.
stats datafile using (abs($4)<=energy_window ? $5 : 1/0) nooutput
shared_max=STATS_max
stats datafile using (abs($4)<=energy_window ? $6 : 1/0) nooutput
shared_max=1.08*(shared_max>STATS_max ? shared_max : STATS_max)
set terminal pngcairo enhanced font "DejaVu Sans,12" size 1500,620
set output output_path
set multiplot layout 1,2 margins 0.075,0.97,0.18,0.78 spacing 0.06
set xrange [-energy_window:energy_window]
set yrange [0:shared_max]
set xlabel "Energy relative to each Fermi level (eV)"
set ylabel "Projected DOS (states / eV / simulation cell)"
set grid ytics lc rgb "#dddddd"
set border 3
set tics nomirror
set key top right font ",10"
set arrow 1 from 0,graph 0 to 0,graph 1 nohead dt 2 lc rgb "#777777"
set title "(a) 0% strain | frozen geometry"
plot datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $5 : 1/0) with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
 datafile using 4:(stringcolumn(1) eq "Isolated Sc2C 0%" ? $5 : 1/0) with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
 datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $6 : 1/0) with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
set title "(b) +1.5% strain | frozen geometry"
unset ylabel
plot datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $5 : 1/0) with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
 datafile using 4:(stringcolumn(1) eq "Isolated Sc2C +1.5%" ? $5 : 1/0) with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
 datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $6 : 1/0) with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
unset multiplot
print sprintf("Read column4 and layer columns5/6 without resampling; |E-EF|<=%.2f eV; shared_ymax=%.8f", energy_window,shared_max)
```

</details>

应变扫描与改变电子数是两个独立控制变量。中性异质结中的层间重排发生在固定总电子数下；带电单层则还需说明电子数、面积与带电边界，不能将 Bader 分区转移量直接设为带电单层的等效自由载流子数。

要判断应变是否改变层间净转移量，需在每个 ε 下使用同一几何、网格和密度约定的完整界面与两份孤立层密度，接[三密度差分](/Atlas/m/delta-charge/vasp/)和[Bader 分区](/Atlas/m/bader/vasp/)。现有密度操作示例使用 VASP 文件；QE 密度仍需保留自身导出、网格和单位来源。单看某层 PDOS 下降，不能确定该层失去了多少电子。若讨论间隙电子的空间重分布，再接[ELF](/Atlas/m/elf/vasp/)与明确能窗的部分电荷密度；裸 Sc₂C 单层的身份也要由自己的空间证据判断。

这一步的参考也要随应变走：在每个 ε 下，从该态界面结构中删去另一层得到冻结片段，保留原子原位、晶胞、网格和相应电子协议。先核对完整体系与两份片段的电子数是否相加闭合，再比较空间积分或相同原子集合的 Bader 和。如此得到的层净变化，才有明确的“相对于谁”。

若用层净增电子数 $\Delta N_{\mathrm{layer}}$ 表示转移，面密度为 $\Delta N_{\mathrm{layer}}/S$，其中 $S=|\mathbf a\times\mathbf b|$。纯双轴 +1.5% 已使面积变为 $S/S_0=(1.015)^2=1.030225$；即使每胞转移数保持相同，每面积的数值也会改变。因此同时写每胞电子数和实际面积，比只列一个 e/cm² 数字更容易区分电荷重排与几何稀释。当前四态 PDOS 没有提供这套三密度或 Bader 对照，表中的投影差不能充当它的替代数据。

这张表可在纯 Python 环境重新提取，不调用 DFT 或绘图程序。下载[inspect_frozen_pdos.py](/Atlas/examples/research-strain/inspect_frozen_pdos.py)，把上面的能量分辨 CSV 放在同一目录，执行 python3 inspect_frozen_pdos.py。脚本逐态检查能量轴、有限数值与层投影闭合，输出[近 EF 表](/Atlas/examples/research-strain/nearest-fermi-pdos.csv)和[核对摘要](/Atlas/examples/research-strain/nearest-fermi-pdos.json)。完整源码和真实运行结果见下文。

## 把电子变化接到声子、EPC 和 Tc

<figure>
<div>
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig4abc.png" alt="Qiu2022原文Fig.4(a–c)：0–4% 双轴应变下的总 DOS、Ba-5d 和 N-2p 投影；各自保留原纵轴幅值。" />
</div>
<figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，第 4 页 Fig. 4(a–c)：0–4% 双轴应变下的总 DOS、Ba-5d 和 N-2p 投影；各自保留原纵轴幅值。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文原文</a>。</figcaption>
</figure>

[Qiu 等，Phys. Rev. B 105, 165101](https://doi.org/10.1103/PhysRevB.105.165101)的原文 PDF 第 4 页，Fig. 4(a)画总 DOS，(b)、(c)分别画 Ba 5d、N 2p 投影；横轴都是相对费米能的能量，黑至红的线色对应 0% 到 4% 双轴应变。三个面板的纵轴范围不同，读它们时应比较同一投影内的谱形与近零点变化，而不是凭线条高度直接比较两种轨道的总贡献。本页的层 PDOS 与这两种原子轨道投影也有不同定义；可以借用“同能量基准、分开投影、保留原始幅值”的画法，不能把总原子投影换名为完整 DOS。

Fig. 4(d)把各应变下 [−0.1,0] eV 的部分电荷密度放在同一视向，等值面固定为 0.0005 e/Å³。表面和层内的等值面连通形状，结合 (a–c) 的 PDOS，才支持作者关于近费米能电子空间重分布的解释。复现这类图应使用每个结构自己的费米能窗导出三维部分密度，在 VESTA 或 XCrySDen 中保留共同等值面、晶胞边界、观察方向和色表，并显示晶轴；不能让软件对每张图自动选择不同阈值。本页目前可复现的是冻结层谱图；态选择与场的判读另见[能窗密度与 ELF](/Atlas/m/elf/vasp/)和[三密度对照](/Atlas/m/delta-charge/vasp/)，不能从 PDOS 表重建 Fig. 4(d) 那样的空间密度。

同页 Fig. 5(a)以应变百分比为横轴，把红色 $N(0)$〔states/eV〕和蓝色 $\omega_{\log}$〔K〕放在各自标明单位的纵轴；(b)同样比较红色 $T_c$〔K〕与蓝色无量纲 $\lambda$。它的分析来自电子态增加、频率下降与耦合增强的共同变化，而不是只按软化程度排序。低频权重在 $\lambda=2\int \frac{\alpha^2F(\omega)}{\omega}\,d\omega$ 中被放大，同时 $\omega_{\log}$ 可能降低。要复现应变对照，可以用 gnuplot 的共享横轴分面或明确标注的双纵轴，使用同一组已验收结构、$\mu^*$、展宽和积分谱窗；本页的冻结 PDOS 表没有提供这一整组 EPC 数据，因此不另画 $T_c$ 增益曲线。

再对照 PDF 第 3 页 Fig. 3(a–d) 的无应变结果与第 5 页 Fig. 6(a–e) 的 +4% 结果：色散 (a) 中红点大小按声子线宽 $\gamma_{\mathbf q\nu}$ 编码，(b) 的总/分原子 PHDOS 和 (c) 的 $\alpha^2F$ 共用频率坐标，Fig. 6(c) 右侧虽标有红色 $\lambda(\omega)$，但这份 PDF 的累计曲线与刻度无法清晰读取，不据它判断累计台阶或末值；本站累计量由真实原谱积分，可读的画法参照[谱函数页的 Pb Fig. 13 对照](/Atlas/m/eliashberg-a2f/qe/)。这样能把 K 点约 24 cm⁻¹ 的软支、谱峰和 Fig. 6(e) 的位移联系起来，而非将 PHDOS 峰直接叫作强 EPC。复现时在 gnuplot 中对齐频率轴并保存点大小的量与尺度；振型在 XCrySDen 等模式显示工具中保留相位、原子和晶轴。Fig. 6(d) 是 Γ 附近约 49 cm⁻¹ 的光学模式，(e) 才是 K 软模；原文用 $\sqrt{3}\times\sqrt{3}$ 超胞把 K 折叠到 Γ 来展示，不能用原胞 Γ 振型替代它。本站的[声子与振型](/Atlas/m/phonon-dfpt/qe/)、[线宽](/Atlas/m/phonon-linewidth/qe/)及[谱函数](/Atlas/m/eliashberg-a2f/qe/)分别提供这些输入和读法；Ba₂N 的数值与振型仍属于原论文。

对于异质结，应先在统一结构与协议下对照[声子色散及模式](/Atlas/m/phonon-dfpt/qe/)、[声子线宽](/Atlas/m/phonon-linewidth/qe/)与[α²F、累计 λ](/Atlas/m/eliashberg-a2f/qe/)，再按同一 μ*、积分谱窗和展宽比较[Tc](/Atlas/m/allen-dynes/qe/)。模式编号可能随应变交换，追踪软化应结合位移或简并子空间，不能只相减“第几支”。

已有声子记录也给出一个具体的比较提醒。在另一个独立的 +1.5% Γ 响应对照中，同身份的最低光学双态从 Γ16² 的 86.60094 cm⁻¹ 变为 Γ32² 的 75.22373 cm⁻¹，两者相差 11.37721 cm⁻¹；相对 Γ16² 下降约 13.14%，以 Γ32² 为分母则相差约 15.12%。该比较固定了父密度与结构，却还改变了响应网格和电子求解路径，见[原始矩阵、向量与实际输出](/Atlas/m/phonon-dfpt/qe/)。这两个频率不是两个应变点，也不能和冻结 PDOS 直接拼成一条因果曲线；它们说明在解释应变软化前，先要知道同一个结构上的数值敏感性有多大。真正的应变对照应让 ε 变化，同时固定响应协议，并用位移或简并子空间追踪同一运动。

现有 +2/+3% 的 K 点负频提示需要检查稳定范围；不能删除负频以后补一个 Tc。0/+1/+1.5% 历史代表 Tc 又分别取自不同展宽，旧谱窗也有截断问题，因此本文不把它们连成已收敛的应变增益曲线。Γ 点复核只能约束 Γ，完整布里渊区的软模与 EPC 仍要保留各自的验收范围。若研究物理上的非谐稳定化，先读[虚频诊断](/Atlas/m/imaginary-phonon/qe/)，确认数值与结构原因，再决定是否需要有限温度方法。

## 重提冻结 PDOS 表的源码与结果

输入 CSV 一行对应一个状态的一个能量点，包含各自 EF、E−EF、两层投影与总投影。程序选择绝对 E−EF 最小的一行，不插值、不平滑，不将 PDOS 积分叫作转移电荷。近 EF ±0.1 eV 的层投影闭合误差以绝对差之和除以总投影绝对值之和定义。

可以据此提出明确的写码需求：

```text
编写纯 Python 3 程序，读取 frozen_pdos_long.csv。每态独立检查 0.005 eV 的递增能量网格、单一 strain_percent 与 fermi_eV、有限值和投影差列；选择最近 EF 的实际网格点，保留其 E-EF 偏移和两层/总投影，单位 states/(eV cell)。计算 ±0.1 eV 内的投影闭合 L1 相对误差。输出四态 CSV、JSON 与实际读取摘要，不补精确 EF 值，不调用 DFT，不作图。
```

<details>
<summary>inspect_frozen_pdos.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Inspect accepted frozen-control PDOS tables; no DFT or plotting."""
from pathlib import Path
import csv, json, math, sys
root = Path(__file__).resolve().parent
source = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "frozen_pdos_long.csv"
expected = ["Heterostructure 0%", "Isolated Sc2C 0%",
            "Heterostructure +1.5%", "Isolated Sc2C +1.5%"]
groups = {name: [] for name in expected}
with source.open(newline="") as handle:
    reader = csv.DictReader(handle)
    names = ["strain_percent", "fermi_eV", "energy_minus_fermi_eV",
             "sc2c_pdos", "zrcl2_pdos", "total_projected_pdos",
             "projected_sum_error"]
    if not set(["state"] + names).issubset(reader.fieldnames or []):
        raise ValueError("Missing PDOS fields")
    for item in reader:
        state = item["state"]
        if state not in groups:
            raise ValueError("Unknown state: " + state)
        values = {k: float(item[k]) for k in names}
        if not all(math.isfinite(v) for v in values.values()):
            raise ValueError("Non-finite PDOS row")
        discrepancy = values["sc2c_pdos"] + values["zrcl2_pdos"] - values["total_projected_pdos"]
        if abs(discrepancy - values["projected_sum_error"]) > 1e-10:
            raise ValueError("Saved projection mismatch differs")
        groups[state].append(values)
rows, checks = [], []
for state in expected:
    data = groups[state]
    if not data:
        raise ValueError("Empty state: " + state)
    if len({x["strain_percent"] for x in data}) != 1 or len({x["fermi_eV"] for x in data}) != 1:
        raise ValueError("Mixed strain or Fermi reference")
    energy = [x["energy_minus_fermi_eV"] for x in data]
    steps = [b-a for a,b in zip(energy[:-1],energy[1:])]
    if not steps or min(steps) <= 0 or max(abs(x-0.005) for x in steps) > 1e-8:
        raise ValueError("Unexpected energy grid")
    if not min(energy) < 0 < max(energy):
        raise ValueError("Grid does not bracket EF")
    near = min(data, key=lambda x: abs(x["energy_minus_fermi_eV"]))
    if abs(near["energy_minus_fermi_eV"]) > 0.0025 + 1e-8:
        raise ValueError("No near-Fermi grid point")
    window = [x for x in data if abs(x["energy_minus_fermi_eV"]) <= 0.1]
    denominator = sum(abs(x["total_projected_pdos"]) for x in window)
    if not window or denominator <= 0:
        raise ValueError("Invalid closure window")
    closure = 100 * sum(abs(x["projected_sum_error"]) for x in window) / denominator
    row = {"state": state, "strain_percent": near["strain_percent"],
           "nearest_E_minus_EF_eV": near["energy_minus_fermi_eV"],
           "sc2c_pdos": near["sc2c_pdos"], "zrcl2_pdos": near["zrcl2_pdos"],
           "total_projected_pdos": near["total_projected_pdos"]}
    rows.append(row)
    checks.append({"state":state, "rows":len(data), "grid_step_eV":steps[0],
                   "L1_projection_error_percent_EF_pm_0p1":closure})
    print(f'{state}: E-EF={row["nearest_E_minus_EF_eV"]:+.4f} eV; '
          f'Sc2C={row["sc2c_pdos"]:.6f}; ZrCl2={row["zrcl2_pdos"]:.6f}; '
          f'total={row["total_projected_pdos"]:.2f} states/(eV cell)')
with (root/"nearest-fermi-pdos.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
result = {"source":source.name, "method":"Nearest grid point; no interpolation at EF",
          "units":"PDOS: states/(eV cell); E-EF: eV",
          "reference":"Each state has its own Fermi energy",
          "scope":"Frozen geometry; projected DOS is not transferred charge",
          "rows":rows, "checks":checks}
(root/"nearest-fermi-pdos.json").write_text(json.dumps(result,indent=2)+"\n")
print("Four frozen-control PDOS states checked; no DFT invoked.")
```

</details>

在下载数据与脚本的目录执行：

```bash
python3 inspect_frozen_pdos.py
```

实际读取输出：

```text
Heterostructure 0%: E-EF=+0.0008 eV; Sc2C=2.564971; ZrCl2=2.222928; total=4.78 states/(eV cell)
Isolated Sc2C 0%: E-EF=+0.0008 eV; Sc2C=4.232280; ZrCl2=0.000000; total=4.23 states/(eV cell)
Heterostructure +1.5%: E-EF=-0.0023 eV; Sc2C=2.080865; ZrCl2=2.459610; total=4.54 states/(eV cell)
Isolated Sc2C +1.5%: E-EF=+0.0022 eV; Sc2C=4.477110; ZrCl2=0.000000; total=4.48 states/(eV cell)
Four frozen-control PDOS states checked; no DFT invoked.
```

这里四态的列值与前表一致。总投影取文件原列，层投影相加可能因原始打印精度有微小差别；脚本记录该差，没有强迫每行完全相等。[完整运行输出](/Atlas/examples/research-strain/postprocess.out.txt) · [源码、源 CSV 和核对结果包](/Atlas/examples/research-strain/frozen-pdos-table-pack.tar.gz)。

### 为什么最近点与整段能窗会给出不同变化

上面的近 EF 表保留真实网格点。本段补充固定能窗积分，比较相同宽度内的谱权重；两者使用同一份输入，回答的是不同问题。下载 [window_pdos.py 完整源码](/Atlas/examples/enrichment-20261003/strain/window_pdos.py)，与 frozen_pdos_long.csv 放在同一目录。可以将以下处理要求交给编程助手：

```text
编写 Python 3 标准库程序 window_pdos.py，读取公开的 frozen_pdos_long.csv。逐态核对四个状态名、应变和 EF 唯一、所有数值有限、递增 0.005 eV 能量轴以及保存的投影差列。使用每态自身 EF；默认在 [-0.1,+0.1] eV 上积分原谱的分段线性表示，只有边界需要线性取值，内部不重采样。分别保存 Sc2C、ZrCl2 和文件总投影的窗内权重(states/cell)、除以窗宽的平均 PDOS(states/(eV cell))，记录原投影差的 L1 积分，不能强迫闭合。输出四态 CSV、JSON、异质结与孤立 Sc2C 从0到+1.5%的权重变化和真实读取摘要。输入只读，输出必须是新目录；不从谱积分生成电子转移数，不调用 DFT 或绘图。
```

<details>
<summary>window_pdos.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Integrate a fixed own-EF PDOS window from the published frozen controls."""
from pathlib import Path
import argparse, bisect, csv, json, math

STATES = {
    "Heterostructure 0%": 0.0,
    "Isolated Sc2C 0%": 0.0,
    "Heterostructure +1.5%": 1.5,
    "Isolated Sc2C +1.5%": 1.5,
}
COLUMNS = ["sc2c_pdos", "zrcl2_pdos", "total_projected_pdos"]

def integrate(x, y, lo, hi):
    if not x[0] < lo < hi < x[-1]:
        raise ValueError("Window must lie inside the saved energy grid")
    def at(t):
        i = bisect.bisect_right(x, t) - 1
        return y[i] + (y[i+1] - y[i]) * (t - x[i]) / (x[i+1] - x[i])
    points = [(lo, at(lo))]
    points.extend((a, b) for a, b in zip(x, y) if lo < a < hi)
    points.append((hi, at(hi)))
    return math.fsum((b[0] - a[0]) * (a[1] + b[1]) / 2
                     for a, b in zip(points, points[1:]))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--half-width", type=float, default=0.1)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    if not math.isfinite(args.half_width) or args.half_width <= 0:
        raise ValueError("half-width must be a positive finite eV value")
    if args.output_dir.exists():
        raise FileExistsError("Use a new output directory: " + str(args.output_dir))
    groups = {state: [] for state in STATES}
    fields = ["strain_percent", "fermi_eV", "energy_minus_fermi_eV",
              *COLUMNS, "projected_sum_error"]
    with args.input.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"state", *fields}.issubset(reader.fieldnames or []):
            raise ValueError("Missing PDOS fields")
        for item in reader:
            state = item["state"]
            if state not in groups:
                raise ValueError("Unknown state: " + state)
            row = {name: float(item[name]) for name in fields}
            if not all(math.isfinite(v) for v in row.values()):
                raise ValueError("Non-finite data: " + state)
            mismatch = row["sc2c_pdos"] + row["zrcl2_pdos"] - row["total_projected_pdos"]
            if abs(mismatch - row["projected_sum_error"]) > 1e-10:
                raise ValueError("Projection discrepancy column does not match")
            groups[state].append(row)
    rows, checks = [], []
    width = 2 * args.half_width
    for state, strain in STATES.items():
        data = groups[state]
        if not data or {v["strain_percent"] for v in data} != {strain}:
            raise ValueError("Empty or mixed-strain state: " + state)
        if len({v["fermi_eV"] for v in data}) != 1:
            raise ValueError("Mixed Fermi energies: " + state)
        x = [v["energy_minus_fermi_eV"] for v in data]
        steps = [b-a for a, b in zip(x, x[1:])]
        if not steps or any(abs(v - 0.005) > 1e-8 for v in steps):
            raise ValueError("Expected a strictly increasing 0.005 eV grid")
        weights = {col: integrate(x, [v[col] for v in data],
                                  -args.half_width, args.half_width)
                   for col in COLUMNS}
        absolute_mismatch = integrate(x, [abs(v["projected_sum_error"]) for v in data],
                                      -args.half_width, args.half_width)
        if weights["total_projected_pdos"] <= 0:
            raise ValueError("Nonpositive integrated total projection")
        row = {"state": state, "strain_percent": strain,
               "half_width_eV": args.half_width, "fermi_eV": data[0]["fermi_eV"]}
        for col in COLUMNS:
            row[col + "_weight_states_cell"] = weights[col]
            row[col + "_mean_states_eV_cell"] = weights[col] / width
        rows.append(row)
        checks.append({"state": state, "source_rows": len(data),
                       "L1_closure_percent": 100 * absolute_mismatch /
                       weights["total_projected_pdos"]})
        print(f'{state}: Sc2C={weights["sc2c_pdos"]:.6f}; '
              f'ZrCl2={weights["zrcl2_pdos"]:.6f}; '
              f'total projection={weights["total_projected_pdos"]:.6f} states/cell')
    changes = {}
    for tag, first, last in [("heterostructure", rows[0], rows[2]),
                              ("isolated_Sc2C", rows[1], rows[3])]:
        key = "sc2c_pdos_weight_states_cell"
        changes[tag] = 100 * (last[key] / first[key] - 1)
    print(f'Sc2C window-weight change: heterostructure={changes["heterostructure"]:+.4f}%; '
          f'isolated={changes["isolated_Sc2C"]:+.4f}%')
    report = {"source": str(args.input), "half_width_eV": args.half_width,
              "method": "Piecewise-linear spectrum; exact window endpoints; trapezoidal integral",
              "reference": "Each state uses its own saved Fermi energy; no absolute band alignment",
              "units": "Integrated projected spectral weight: states/cell; mean PDOS: states/(eV cell)",
              "scope": "Frozen geometry; no occupation integral, transferred charge, or EPC",
              "rows": rows, "checks": checks, "sc2c_weight_change_percent": changes}
    args.output_dir.mkdir(parents=True)
    with (args.output_dir / "window-pdos.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "window-pdos.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f'Window [-{args.half_width:g}, +{args.half_width:g}] eV; '
          'linear endpoints only; no DFT or charge-transfer inference.')

if __name__ == "__main__":
    main()
```

</details>

在数据与脚本所在目录执行，window-0.1 必须是新目录：

```bash
python3 window_pdos.py --input frozen_pdos_long.csv --half-width 0.1 --output-dir window-0.1
```

Talos 用上述公开 CSV 实际读取的输出如下：

```text
Heterostructure 0%: Sc2C=0.404262; ZrCl2=0.317533; total projection=0.721729 states/cell
Isolated Sc2C 0%: Sc2C=0.667095; ZrCl2=0.000000; total projection=0.666938 states/cell
Heterostructure +1.5%: Sc2C=0.416509; ZrCl2=0.329840; total projection=0.746342 states/cell
Isolated Sc2C +1.5%: Sc2C=0.806143; ZrCl2=0.000000; total projection=0.806404 states/cell
Sc2C window-weight change: heterostructure=+3.0295%; isolated=+20.8438%
Window [-0.1, +0.1] eV; linear endpoints only; no DFT or charge-transfer inference.
```

[四态积分表](/Atlas/examples/enrichment-20261003/strain/window-pdos.csv)和[完整检查与未舍入结果](/Atlas/examples/enrichment-20261003/strain/window-pdos.json)保留原始积分精度。总投影用原列单独积分；没有用两层投影之和替换它。这个有限窗口读法连接上方谱图与数值表，不改变原有最近网格点的结果。

要复现这幅图，可将绘图需求写成：用 gnuplot 6.0 直接读取四态 CSV，画 0%/+1.5% 并排面板；横轴固定 ±0.5 eV，所有可见层谱共用纵轴；固定上述线色与实/虚线，标 E−EF=0 和 ±0.1 eV 边界，灰区放在曲线后；不平滑、不做自身峰值归一化，保存 PNG、SVG 和完整源码。

<details>
<summary>plot_window_pdos.gnu 完整源码</summary>

```gnuplot
# gnuplot 6.0; direct published CSV, piecewise-linear sample connections.
# Run beside frozen_pdos_long.csv: gnuplot plot_window_pdos.gnu
if (!exists("datafile")) datafile="frozen_pdos_long.csv"
if (!exists("output_base")) output_base="pdos-window"
set encoding utf8
set datafile separator comma
stats datafile using (abs($4)<=0.5 ? $5 : 1/0) nooutput
shared_max=STATS_max
stats datafile using (abs($4)<=0.5 ? $6 : 1/0) nooutput
shared_max=1.08*(shared_max>STATS_max ? shared_max : STATS_max)
do for [format_index=1:2] {
    if (format_index==1) {
        set terminal pngcairo enhanced font "DejaVu Sans,12" size 1500,620
        set output output_base.".png"
    } else {
        set terminal svg enhanced font "DejaVu Sans,12" size 1500,620
        set output output_base.".svg"
    }
    set multiplot layout 1,2 margins 0.075,0.97,0.18,0.78 spacing 0.06
    set xrange [-0.5:0.5]
    set yrange [0:shared_max]
    set xlabel "Energy relative to each Fermi level (eV)"
    set ylabel "Projected DOS (states / eV / simulation cell)"
    set grid ytics lc rgb "#dddddd"
    set border 3
    set tics nomirror
    set key top right font ",10"
    set object 1 rect from -0.1,graph 0 to 0.1,graph 1 behind \
        fc rgb "#777777" fs transparent solid 0.10 noborder
    set arrow 1 from 0,graph 0 to 0,graph 1 nohead dt 2 lc rgb "#777777"
    set arrow 2 from -0.1,graph 0 to -0.1,graph 1 nohead dt 3 lc rgb "#aaaaaa"
    set arrow 3 from 0.1,graph 0 to 0.1,graph 1 nohead dt 3 lc rgb "#aaaaaa"
    set label 1 "integrated window" at 0,graph 0.95 center font ",10" tc rgb "#555555"
    set title "(a) 0% strain | frozen geometry"
    plot datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $5 : 1/0) \
        with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
      datafile using 4:(stringcolumn(1) eq "Isolated Sc2C 0%" ? $5 : 1/0) \
        with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
      datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $6 : 1/0) \
        with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
    set title "(b) +1.5% strain | frozen geometry"
    unset ylabel
    plot datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $5 : 1/0) \
        with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
      datafile using 4:(stringcolumn(1) eq "Isolated Sc2C +1.5%" ? $5 : 1/0) \
        with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
      datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $6 : 1/0) \
        with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
    unset multiplot
    unset output
}
print sprintf("Original CSV, common y range 0..%.8f; window +/-0.1 eV; PNG/SVG written.",shared_max)
```

</details>

在该脚本和 frozen_pdos_long.csv 所在目录执行：

```bash
gnuplot plot_window_pdos.gnu
```

Talos 的 gnuplot 6.0 实际读取输出为：

```text
Original CSV, common y range 0..8.19772920; window +/-0.1 eV; PNG/SVG written.
```

## 从原始文件重建结果

逐点读取同一 F 定义和笛卡尔应力，将 QE 压缩为正的应力转换为拉伸为正，再从 CSV 筛选六个 xx 点作图。能量以最低采样 F 为零点。可以把这些读取规则写成下面的请求：

```text
请编写 Python 3 独立后处理程序。读取 elastic/cases.json 所列六个 mode=xx 的 al.scf.in/out/err。检查电子收敛行、唯一 JOB DONE，并要求 stderr 为空；遇到 convergence NOT achieved 或 Error in routine 时停止；统一读取 QE 感叹号行 F（Ry），应力取左侧 Ry/bohr^3 张量，乘 -14710.5076 转成拉伸为正的 GPa。排序实际应变，输出六行 CSV 与输入 SHA256；图只使用这些样本，F 减最低采样值后乘 13.605693122994*1000 得 meV/atom，不加入零应变或掺杂/DOS/EPC 数据。 缺少文件、格式或非有限数值时明确失败，不猜值、不补零。脚本写入分析结果，保留原始计算文件。
```

[analyse_strain.py 完整源码](/Atlas/examples/interface-magnet-strain-doping-scan/analyse_strain.py) · [plot_strain.py 完整源码](/Atlas/examples/interface-magnet-strain-doping-scan/plot_strain.py) · [atlas_plot_style.py 完整源码](/Atlas/examples/interface-magnet-strain-doping-scan/atlas_plot_style.py)

<details>
<summary>analyse_strain.py 的完整源码</summary>

```python
from pathlib import Path
import csv, re, json, hashlib, math
r=Path(__file__).resolve().parent
rows=[]; hashes={}
def cell(text):
    rows=re.findall(r'CELL_PARAMETERS\s+angstrom\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)',text)
    if len(rows)!=1:raise ValueError('Expected one angstrom cell')
    return [[float(v) for v in line.split()] for line in rows[0]]
reference=cell((r/'elastic/al.reference.in').read_text())

for case in json.loads((r/'elastic/cases.json').read_text()):
    if case['mode']!='xx':continue
    p=r/'elastic'/case['label'];s=(p/'al.scf.out').read_text();err=(p/'al.scf.err').read_text()
    if s.count('JOB DONE.')!=1 or 'convergence has been achieved' not in s or err.strip() or 'convergence NOT achieved' in s or 'Error in routine' in s:
        raise ValueError('Incomplete SCF: '+case['label'])
    inp=(p/'al.scf.in').read_text(); current=cell(inp)
    strain=float(case['engineering_strain'])
    for i in range(3):
        for j in range(3):
            expected=reference[i][j]*(1+strain if j==0 else 1)
            if abs(current[i][j]-expected)>1e-10:raise ValueError('Cell/strain mismatch: '+case['label'])
    energy=float(re.findall(r'!\s+total energy\s+=\s+([-0-9.]+)',s)[-1])
    block=re.findall(r'total\s+stress[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)',s)[-1]
    stress=[[-14710.5076*float(x) for x in line.split()[:3]] for line in block]
    if not math.isfinite(energy) or not all(math.isfinite(v) for row in stress for v in row):raise ValueError('Non-finite result')
    rows.append({**case,'energy_Ry':energy,'sigma_xx_GPa':stress[0][0],'sigma_yy_GPa':stress[1][1],'sigma_zz_GPa':stress[2][2],'sigma_xy_GPa':stress[0][1]})
    for n in ['al.scf.in','al.scf.out','al.scf.err']:
        hashes[str((p/n).relative_to(r))]=hashlib.sha256((p/n).read_bytes()).hexdigest()
rows.sort(key=lambda x:x['engineering_strain'])
if len(rows)!=6:raise ValueError('Expected six xx samples')
with (r/'elastic/strain-stress.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(r/'strain-summary.json').write_text(json.dumps({'rows':rows,'source_sha256':hashes,'energy':'QE printed F in Ry/one-atom cell','stress':'Tensile-positive; minus QE Ry/bohr^3 * 14710.5076 GPa','scope':'Six xx fixed-cell SCFs, 16^3 k mesh; no doping/DOS/EPC.'},indent=2)+'\n')
print('Six xx SCFs: electronic convergence, one JOB DONE, empty stderr.')
for x in rows:print(f"{x['engineering_strain']:+.3f} F={x['energy_Ry']:.8f} Ry sigma_xx={x['sigma_xx_GPa']:+.6f} sigma_yy={x['sigma_yy_GPa']:+.6f} GPa")
```

</details>

<details>
<summary>plot_strain.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
rows=sorted((x for x in csv.DictReader((r/'elastic/strain-stress.csv').open()) if x['mode']=='xx'),key=lambda x:float(x['engineering_strain']))
e=np.array([float(x['engineering_strain']) for x in rows])*100
energy=np.array([float(x['energy_Ry']) for x in rows])
sxx=[float(x['sigma_xx_GPa']) for x in rows]
syy=[float(x['sigma_yy_GPa']) for x in rows]
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
axes[0].plot(e,(energy-energy.min())*13.605693122994*1000,'o-',color='#0072b2')
axes[0].set(xlabel='Applied x strain (%)',ylabel='F - lowest sampled F (meV/atom)')
axes[1].plot(e,sxx,'o-',label='Tensile-positive stress xx',color='#0072b2')
axes[1].plot(e,syy,'s-',label='Tensile-positive stress yy',color='#d55e00')
axes[1].set(xlabel='Applied x strain (%)',ylabel='Stress (GPa)')
axes[1].legend(frameon=False,fontsize=8)
for ax in axes:
    ax.axvline(0,color='.6',lw=.7);ax.grid(alpha=.18)
fig.suptitle('fcc Al | fixed electron number, 16³ k mesh, MV width 0.02 Ry',fontsize=11)
(r/'figures').mkdir(exist_ok=True)
fig.savefig(r/'figures/strain-scan.png',dpi=220)
fig.savefig(r/'figures/strain-scan.svg')
```

</details>

[输入、原始输出与完整后处理包](/Atlas/examples/interface-magnet-strain-doping-scan/example-pack.tar.gz)解压后，在 `example-pack` 目录执行：

```bash
python3 analyse_strain.py
python3 plot_strain.py
```

实际读取结果见正文表及 [elastic/strain-stress.csv](/Atlas/examples/interface-magnet-strain-doping-scan/elastic/strain-stress.csv) · [strain-summary.json](/Atlas/examples/interface-magnet-strain-doping-scan/strain-summary.json)。

相关输入说明：[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)

接下来沿同一组应变结构比较[电子态投影](/Atlas/m/population-analysis/qe/)和[电荷转移](/Atlas/m/delta-charge/vasp/)，再用[声子与 EPC](/Atlas/m/epc/qe/)检验这些电子变化怎样影响振动耦合。
