拉伸晶格以后，界面电荷怎样重新分配，费米能附近的电子态来自哪一层，哪些振动变软，最后又怎样影响 $\lambda$、$\omega_{\log}$ 和 $T_c$？应变扫描要把这些量放在同一组结构上比较。能量和应力先帮助核对施加的形变；真正的研究判断来自后面的电子与振动响应。

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

这张表可在纯 Python 环境重新提取，不调用 DFT 或绘图程序。下载[inspect_frozen_pdos.py](/Atlas/examples/research-strain/inspect_frozen_pdos.py)，把上面的能量分辨 CSV 放在同一目录，执行 python3 inspect_frozen_pdos.py。脚本逐态检查能量轴、有限数值与层投影闭合，输出[近 EF 表](/Atlas/examples/research-strain/nearest-fermi-pdos.csv)和[核对摘要](/Atlas/examples/research-strain/nearest-fermi-pdos.json)。完整源码和真实运行结果见下文。

## 把电子变化接到声子、EPC 和 Tc

[Qiu 等，Phys. Rev. B 105, 165101](https://doi.org/10.1103/PhysRevB.105.165101)的原文 PDF 第 4 页，Fig. 4(a)画总 DOS，(b)、(c)分别画 Ba 5d、N 2p 投影；横轴都是相对费米能的能量，黑至红的线色对应 0% 到 4% 双轴应变。三个面板的纵轴范围不同，读它们时应比较同一投影内的谱形与近零点变化，而不是凭线条高度直接比较两种轨道的总贡献。本页的层 PDOS 与这两种原子轨道投影也有不同定义；可以借用“同能量基准、分开投影、保留原始幅值”的画法，不能把总原子投影换名为完整 DOS。

Fig. 4(d)把各应变下 [−0.1,0] eV 的部分电荷密度放在同一视向，等值面固定为 0.0005 e/Å³。表面和层内的等值面连通形状，结合 (a–c) 的 PDOS，才支持作者关于近费米能电子空间重分布的解释。复现这类图应使用每个结构自己的费米能窗导出三维部分密度，在 VESTA 或 XCrySDen 中保留共同等值面、晶胞边界、观察方向和色表，并显示晶轴；不能让软件对每张图自动选择不同阈值。本页目前可复现的是冻结层谱图；态选择与场的判读另见[能窗密度与 ELF](/Atlas/m/elf/vasp/)和[三密度对照](/Atlas/m/delta-charge/vasp/)，不能从 PDOS 表重建 Fig. 4(d) 那样的空间密度。

同页 Fig. 5(a)以应变百分比为横轴，把红色 $N(0)$〔states/eV〕和蓝色 $\omega_{\log}$〔K〕放在各自标明单位的纵轴；(b)同样比较红色 $T_c$〔K〕与蓝色无量纲 $\lambda$。它的分析来自电子态增加、频率下降与耦合增强的共同变化，而不是只按软化程度排序。低频权重在 $\lambda=2\int \frac{\alpha^2F(\omega)}{\omega}\,d\omega$ 中被放大，同时 $\omega_{\log}$ 可能降低。要复现应变对照，可以用 gnuplot 的共享横轴分面或明确标注的双纵轴，使用同一组已验收结构、$\mu^*$、展宽和积分谱窗；本页的冻结 PDOS 表没有提供这一整组 EPC 数据，因此不另画 $T_c$ 增益曲线。

再对照 PDF 第 3 页 Fig. 3(a–d) 的无应变结果与第 5 页 Fig. 6(a–e) 的 +4% 结果：色散 (a) 中红点大小按声子线宽 $\gamma_{\mathbf q\nu}$ 编码，(b) 的总/分原子 PHDOS 和 (c) 的 $\alpha^2F$ 共用频率坐标，(c) 还用另一纵轴画累计 $\lambda(\omega)$。这样能把 K 点约 24 cm⁻¹ 的软支、谱峰和 Fig. 6(e) 的位移联系起来，而非将 PHDOS 峰直接叫作强 EPC。复现时在 gnuplot 中对齐频率轴并保存点大小的量与尺度；振型在 XCrySDen 等模式显示工具中保留相位、原子和晶轴。Fig. 6(d) 是 Γ 附近约 49 cm⁻¹ 的光学模式，(e) 才是 K 软模；原文用 $\sqrt{3}\times\sqrt{3}$ 超胞把 K 折叠到 Γ 来展示，不能用原胞 Γ 振型替代它。本站的[声子与振型](/Atlas/m/phonon-dfpt/qe/)、[线宽](/Atlas/m/phonon-linewidth/qe/)及[谱函数](/Atlas/m/eliashberg-a2f/qe/)分别提供这些输入和读法；Ba₂N 的数值与振型仍属于原论文。

对于异质结，应先在统一结构与协议下对照[声子色散及模式](/Atlas/m/phonon-dfpt/qe/)、[声子线宽](/Atlas/m/phonon-linewidth/qe/)与[α²F、累计 λ](/Atlas/m/eliashberg-a2f/qe/)，再按同一 μ*、积分谱窗和展宽比较[Tc](/Atlas/m/allen-dynes/qe/)。模式编号可能随应变交换，追踪软化应结合位移或简并子空间，不能只相减“第几支”。

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
