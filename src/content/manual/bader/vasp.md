[Henkelman 组：Bader 程序](https://www.henkelmanlab.org/code/bader/) · [VASP：LAECHG](https://vasp.at/wiki/LAECHG) · [CHGCAR](https://vasp.at/wiki/CHGCAR)

Bader 分析把实空间分成一个个原子盆地，再积分盆地内的电子数。先用两个完全等价的 Fe 原子跑通一次：它们的分区电子数应当相同，整胞总数也应与 VASP 的价电子数一致。这个小体系很容易看清输入、三维网格、参考密度与 ACF.dat 之间的关系。

结构和磁态来自 [bcc Fe 磁构型比较](/Atlas/m/magnetic-gs/vasp/) 的 FM 解。下载 [真实输入、OUTCAR、96³ 电荷网格及后处理脚本](/Atlas/examples/vasp/fe-bcc-lesson-files.tar.gz) 后，解包进入 `fe-bcc/charge_elf`。包中保留两套网格的输出与检查结果，POTCAR 仅提供 TITEL、ZVAL 和哈希标识。

这次在新的 `charge_elf` 目录中复制 POSCAR、KPOINTS、POTCAR 和提交脚本，用 `vi INCAR` 打开全电子密度输出。保存后读取实际输入。

```text
[bcgong@localhost charge_elf]$ cat INCAR
SYSTEM = Fe bcc FM charge and ELF
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 100
ALGO = Normal
ISMEAR = 1
SIGMA = 0.1
ISPIN = 2
MAGMOM = 3 3
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
NPAR = 1
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .TRUE.

LAECHG = .TRUE.
LELF = .TRUE.
NGXF = 96
NGYF = 96
NGZF = 96
```
`LAECHG` 写出 AECCAR0、AECCAR1、AECCAR2：分别对应芯电子、原子叠加的价电子密度和最终自洽价电子密度。用来找分区边界的参考是 AECCAR0 + AECCAR2；实际积分的目标仍是 CHGCAR 中的总价电子密度。AECCAR1 不代替已经收敛的 AECCAR2。

本次同时写了 ELFCAR，供 [ELF](/Atlas/m/elf/vasp/) 使用，因此显式设了 `NPAR = 1`。96³ 是 AECCAR 与 CHGCAR 的细网格；ELFCAR 的采样网格要另外从它自己的文件头读取。

`NGXF/NGYF/NGZF` 决定沿三条晶格矢量保存多少个细网格点。它们加密的是密度的空间表示，ENCUT 控制的则是波函数平面波基组，两者不能互相替代。这里 Fe 的核区密度变化很快，先用 96³、再用 192³，是为了直接观察参考密度积分与盆地电荷对网格的敏感性；每个方向翻倍会使三维点数增加到八倍，也相应增加文件和后处理开销。

```text
[bcgong@localhost charge_elf]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-fe-charge
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
unset SLURM_CPUS_PER_TASK
export I_MPI_PIN_PROCESSOR_LIST=16,17,18,19,20,21,22,23
cd $SLURM_SUBMIT_DIR
mpirun -np 8 /data/software/vasp.5.4.4/bin/vasp_std > out
```
这个教学任务使用现场核验过的 8 个空闲核并行运行，与其他教学任务按次序提交；任务 18187 用时 26 秒。命令 `tail -f out` 可在运行时查看电子步；结束后仍需读停止行与统计尾段。

```text
[bcgong@localhost charge_elf]$ tail -4 OSZICAR
DAV:  16    -0.164736467596E+02    0.20496E-07   -0.31079E-09  2807   0.760E-04    0.228E-04
DAV:  17    -0.164736467728E+02   -0.13183E-07   -0.30314E-10  2702   0.201E-04    0.489E-05
DAV:  18    -0.164736467769E+02   -0.41130E-08   -0.60443E-11  2639   0.102E-04
   1 F= -.16473647E+02 E0= -.16473764E+02  d E =0.351572E-03  mag=     4.2127
```
```text
[bcgong@localhost charge_elf]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
```text
[bcgong@localhost charge_elf]$ ls -lh AECCAR0 AECCAR2 CHGCAR ELFCAR
-rw-rw-r-- 1 bcgong bcgong  16M Sep 22 21:42 AECCAR0
-rw-rw-r-- 1 bcgong bcgong  16M Sep 22 21:42 AECCAR2
-rw-rw-r-- 1 bcgong bcgong  31M Sep 22 21:42 CHGCAR
-rw-rw-r-- 1 bcgong bcgong 139K Sep 22 21:42 ELFCAR
```
文件出现只是开始。AECCAR0 很早就会写出，AECCAR2 才对应自洽完成后的密度；要先确认 SCF 完整结束，再进行相加。

```text
[bcgong@localhost charge_elf]$ head -14 AECCAR0
Fe bcc FM charge and ELF                
   1.00000000000000     
     2.800000    0.000000    0.000000
     0.000000    2.800000    0.000000
     0.000000    0.000000    2.800000
   Fe
     2
Direct
  0.000000  0.000000  0.000000
  0.500000  0.500000  0.500000
 
   96   96   96
 0.22196122414E+07 0.11375194526E+06 0.25172471731E+05 0.14564894925E+05 0.78478711560E+04
 0.37607831076E+04 0.17456520963E+04 0.88918058069E+03 0.56326744509E+03 0.44347649245E+03
```
结构块之后的 `96 96 96` 表示 884,736 个点。CHGCAR 第一块的存储值记为 gᵢ，晶胞体积为 V，网格点数为 N，则电子数是 Σgᵢ/N，空间数密度是 gᵢ/V。这里 V=2.8³=21.952 Å³：前一种运算给电子数，后一种才给每 Å³ 的电子数，不能把两个除数互换。[CHGCAR 的归一化约定](https://vasp.at/wiki/CHGCAR)

相加时，两份文件的晶胞、元素顺序、坐标和网格都必须一致；只按行号相加，或者对不同长度的数据直接 zip，会把错误静默带入参考密度。

随例子提供的 `sum_charge.py` 检查这四项，并且要求标量块长度恰好等于三维网格乘积。脚本只取第一块总电荷密度，写成 CHGCAR_sum 后重新读回，既不混入磁化密度块，也不把 augmentation occupancies 当作网格值相加。

```text
[bcgong@localhost charge_elf]$ python sum_charge.py
AECCAR0_integral = 39.5201008301
AECCAR2_integral = 16.0011953963
CHGCAR_integral = 16.0000000133
grid = [96, 96, 96]
points = 884736
reference_integral = 55.5212962264
scope = first total-charge block only; no spin-density or augmentation blocks copied
```
CHGCAR 的积分是 16.0000000133，与两个 Fe 各 8 个价电子相符。芯电子密度很尖锐，96³ 对其积分仍不够好：AECCAR0 的积分为 39.5201，而这套 Fe 赝势每胞的芯电子数应为 2 × (26 − 8) = 36。先保留这个差异，后面加密网格检查，不用一个“总电子数对上了”掩盖参考密度的数值问题。

运行 Bader 时，把 CHGCAR 作为积分目标，把刚得到的 CHGCAR_sum 作为找边界的参考：

```text
[bcgong@localhost charge_elf]$ <bader_bin>/bader CHGCAR -ref CHGCAR_sum
```

本例执行的是服务器上 Bader 1.05 的可执行文件。输出依次读取目标与参考网格、寻找盆地、细化边界，最后写出 ACF.dat；已有记录显示两个 Bader maxima，真空电荷为 0，总价电子数为 16。继续看每个原子分到了多少电子。

```text
[bcgong@localhost charge_elf]$ cat ACF.dat
    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL
 --------------------------------------------------------------------------------
    1    0.000000    0.000000    0.000000    8.000303     1.161917    10.977166
    2    1.400000    1.400000    1.400000    7.999697     1.161917    10.974834
 --------------------------------------------------------------------------------
    VACUUM CHARGE:               0.0000
    VACUUM VOLUME:               0.0000
    NUMBER OF ELECTRONS:        16.0000
```
先把两行 `ATOMIC VOL` 相加：10.977166 + 10.974834 = 21.952 Å³，正好覆盖本例晶胞。再看 `VACUUM VOLUME=0` 与 `NUMBER OF ELECTRONS=16`，可以把空间覆盖与电子数守恒分别核对。这两个检查成立，也不能单独证明每条盆地边界已经达到所需精度。

`CHARGE` 是盆地内积分得到的价电子数。若把净电荷定义为 Q = ZVAL − N_Bader，那么这里两个 Fe 的 Q 约为 −0.000303 与 +0.000303 e。等价原子出现的这点差异首先反映离散网格和边界划分误差，不能解释成 Fe 原子之间发生了有方向的电荷转移。

`MIN DIST` 是原子到盆地边界的最短距离，并不是最近邻键长。这里 MIN DIST 为 1.161917 Å，而 bcc Fe 的最近邻距离约为 2.424871 Å；前者小于后者是几何上很自然的结果，不能作为分区失败的依据。

再在新目录 `charge_elf_192` 中把 NGXF、NGYF、NGZF 改为 192，保持结构、赝势、k 网格和电子参数一致。本次同时将 ELF 使用的粗网格从 18³ 改为 36³，VASP 任务 18188 用时 102 秒结束。后处理仍执行同一个相加脚本和 Bader 命令。

```text
[bcgong@localhost charge_elf_192]$ cat ACF.dat
    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL
 --------------------------------------------------------------------------------
    1    0.000000    0.000000    0.000000    7.999923     1.187177    10.975705
    2    1.400000    1.400000    1.400000    8.000077     1.187177    10.976295
 --------------------------------------------------------------------------------
    VACUUM CHARGE:               0.0000
    VACUUM VOLUME:               0.0000
    NUMBER OF ELECTRONS:        16.0000
```
两原子现在分别得到 7.999923 和 8.000077 个价电子，仍精确汇总为显示精度内的 16。96³ 到 192³，每个原子的变化约为 0.000380 e，等价原子之间的不对称减小了。与此同时，AECCAR0 积分从 39.5201 靠近到 36.2910：参考密度核区的积分还没有完全闭合，不能把它与价电子盆地积分的稳定程度混为一个指标。

这份小例子可以核对文件、网格、守恒和等价原子。真正比较异质结构的电荷转移时，应逐步加密网格，观察关心的原子或层电荷是否达到所需精度，并在所有对照计算中使用相同分区定义。

### 把盆地电荷与参考密度的网格变化分开看

将 [Bader 图数据与脚本](/Atlas/examples/bader-grid-files.tar.gz) 解包后进入 `bader-grid`。两个子目录保留原始 ACF.dat 和相加脚本当时写出的检查结果；下面的脚本从这些文件重新提取数据：

```bash
python3 extract_bader_grid.py
cat bader-grid.csv
python3 plot_bader_grid.py
```

`extract_bader_grid.py` 逐行读取 ACF.dat 中的原子编号、盆地电子数、最短边界距离和体积，再核对两个原子、16 个价电子与 21.952 Å³ 的体积总和。CSV 另外保存 N_Bader−ZVAL 和 Q=ZVAL−N_Bader；二者符号相反。这里使用 Fe 的 ZVAL=8，只适用于随包提供的这套 Fe 例子。

<figure><img src="/Atlas/examples/bader-grid/bader-grid.svg" alt="bcc Fe 网格电荷误差收敛、AECCAR0 芯电子积分及单层 Sc₂C 的 Bader 电荷分区对比" loading="lazy"/><figcaption>Bader 电荷分析的多角度综合诊断：(a) bcc Fe 两个等价原子在 96³ 与 192³ 网格下的价电子盆地偏差（绿色阴影标出 ±10⁻⁴ e 精度带）；(b) AECCAR0 芯电子密度全胞积分随网格向严格 36 个芯电子收敛的过程；(c) 二维单层 Sc₂C（ZVAL = 11, 4）的实际 Bader 盆地电荷与名义价态对比，标出各原子的净转移电荷。</figcaption></figure>

子图 a 的纵轴是 **盆地电子数相对 8 的偏离**，以 10⁻³ e 表示：正值表示盆地中多于 8 个电子，圆点与方块区分两个等价原子。96³ 时的 ±0.303×10⁻³ e 在 192³ 缩减为约 ∓0.077×10⁻³ e，进入绿色阴影所示的高精度区间。子图 b 展示全胞 AECCAR0 积分随网格从 39.52 接近至 36.29 e，虚线为理论 36 芯电子参考值。子图 c 则引入二维单层 Sc₂C 的真实分析案例，直观展示名义价态与实际 Bader 分区电荷的差异。

`plot_bader_grid.py` 直接读取 CSV，保存同名 SVG、PDF 和 PNG。比较异质结构时可以沿用提取思路，但应把等价原子检查改成自己关心的原子组或层，并重新确定 ZVAL；本例没有给出异质结构的电荷转移量。

### 二维层状体系与半芯态元素的 Bader 电荷核验

在三维块体之后，二维单层或异质结体系（如过渡金属碳化物 Sc₂C 或过渡金属卤化物）在进行 Bader 分析时，还会遇到两个特有的规范问题：**半芯态（Semicore）价电子计数**与**真空层空间截断**。

在 VASP 中处理含半芯态元素（如 Sc 选用 `Sc_sv` 赝势，包含 3s² 3p⁶ 3d¹ 4s²，即 `ZVAL = 11`）时，Bader 分析的标准操作包含三步：
1. **全电子电荷密度自洽**：设置 `LAECHG = .TRUE.`、`LCHARG = .TRUE.`、`PREC = Accurate`、`LASPH = .TRUE.`，确保波函数与原子核区域电荷密度均完整记录，并输出 `AECCAR0`（芯态电荷）与 `AECCAR2`（自洽价态电荷）。对过渡金属体系建议显式设置 `LMAXMIX = 4`。
2. **总参考电荷合成**：使用 `chgsum.pl AECCAR0 AECCAR2`，将二者逐点相加生成包含全电子核区贡献的参考密度 `CHGCAR_sum`。
3. **零通量面分割**：调用 `bader CHGCAR -ref CHGCAR_sum`，以包含核电荷梯度的 `CHGCAR_sum` 定位零通量面，并将价电荷密度 `CHGCAR` 积分到各个原子盆地，生成 `ACF.dat`。

在检查 `ACF.dat` 时，应逐项核验三项物理指标：
- **总电子数严格守恒**：检查文件末尾的 `NUMBER OF ELECTRONS` 是否严格等于各元素 `∑ N_i × ZVAL_i`。例如在单层 Sc₂C（包含 2 个 Sc 和 1 个 C）中，总价电子数严格为 `2 × 11 + 4 = 26.0000 e`。
- **真空区域无虚假电荷泄漏**：在 z 方向留有充分真空层（如 20–40 Å）的二维板层模型中，检查 `VACUUM CHARGE = 0.0000` 与 `VACUUM VOLUME = 0.0000`。这确认了电子密度在真空层完全衰减至零，所有价电子均被完整划分至晶格内部原子盆地，没有出现边界数值积分溢出。
- **形式化合价与 Bader 净电荷的区别**：
  若以 `Q = ZVAL − N_Bader` 计算净转移电荷，以单层 Sc₂C 为例：
  每个 Sc 原子的盆地电子数为 `9.7893 e`，净电荷为 `Q(Sc) = 11 − 9.7893 = +1.2107 e`；
  C 原子的盆地电子数为 `6.4214 e`，净电荷为 `Q(C) = 4 − 6.4214 = −2.4214 e`。
  单层整体净电荷为 `2 × (+1.2107) + (−2.4214) = 0.0000 e`。形式化合价假定价电子完全转移（如 Sc²⁺ 与 C⁴⁻），而自洽 Bader 分析揭示出显著的共价–离子混合成键特征（Sc 实际转移约 1.21 e）。在进一步分析异质结层间电荷转移时，必须以各自独立孤立单层的 Bader 电荷为基准做差，不能将孤立单层内部的极化净电荷误当作层间转移电荷。

## 文献中的相关图件与表达方式

得到 `ACF.dat` 的分区电子数后，文献中除了直接列出单体系电荷表，还常将 Bader 净电荷与界面距离、轨道交叠、隧穿势垒高度（TBH）或动力学 Born 有效电荷 `Z*` 绘制成关联散点图：

### 1. 金属/MoS₂ 界面参量随层间距变化的 2×2 四子图散点矩阵

<figure class="research-figure"><img src="/Atlas/figures/literature/M4_Bader_TBH_vs_Distance_MetalMoS2_Fig2.jpg" alt="10 种金属与 MoS₂ 接触界面的轨道交叠比、诱导隙态、MoS₂ 净 Bader 电荷与隧穿势垒高度随界面距离变化的 2×2 散点图" loading="lazy"/><figcaption>10 种金属与单层 MoS₂ 接触界面随界面距离 <code>Δz_S-metal</code>（Å）变化的 2×2 散点矩阵：(a) 轨道交叠比 <code>σ_S-metal</code>，(b) 积分诱导隙态 IGS，(c) MoS₂ 上的净 Bader 电荷 <code>Q_MoS2</code>（e），(d) 隧穿势垒高度 TBH（eV）；数据点与金属标签按接触强度分为弱范德华型（紫色：Au、Bi、Sb）、中间型（黑色：Cu、Pt、Ru、Ag）与强共价型（绿色：Mo、W、Y）三类。图片来源：<em>Phys. Chem. Chem. Phys.</em> <strong>27</strong>, 5786 (2025), Fig. 2a–d，<a href="https://doi.org/10.1039/D4CP04577G" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D4CP04577G</a>。</figcaption></figure>

- **读图与作图要点**：比较多个接触体系时，以界面法向距离 `Δz_S-metal`（Å）为共同横轴，按 2×2 矩阵并列展示交叠比 `σ_S-metal`、积分诱导隙态 IGS、MoS₂ 净 Bader 电荷 `Q_MoS2`（e）和隧穿势垒高度 TBH（eV），并用颜色区分弱范德华（紫：Au、Bi、Sb）、中间（黑：Cu、Pt、Ru、Ag）与强共价（绿：Mo、W、Y）三类接触，比单纯罗列数字表格更容易看出几何间距与界面电荷转移的协同变化。

### 2. 静态 Bader 电荷与 Born 有效电荷张量迹平均值的散点对照

<figure class="research-figure"><img src="/Atlas/figures/literature/M4_Born_vs_Bader_C2DB_Gjerding2021_Fig16.jpg" alt="二维材料数据库中 585 种材料共 3025 个原子的 Born 有效电荷张量迹平均值 Tr(Z*)/3 与静态 Bader 电荷散点图" loading="lazy"/><figcaption>二维材料数据库（C2DB）中 585 种二维材料共 3025 个原子的 Born 有效电荷张量迹平均值 <code>Tr(Z*)/3</code> [e] 与静态 Bader 电荷 [e] 的散点分布，数据点颜色标示化合物的离子性程度。图片来源：Gjerding et al., <em>2D Mater.</em> <strong>8</strong>, 044002 (2021), Fig. 16，<a href="https://doi.org/10.1088/2053-1583/ac1059" target="_blank" rel="noopener noreferrer">DOI: 10.1088/2053-1583/ac1059</a>。</figcaption></figure>

- **读图与作图要点**：静态 Bader 电荷来自基态电子密度的零通量面空间分区积分，而 Born 有效电荷张量迹平均值 `Tr(Z*)/3` 反映原子位移引起的动态极化响应。将 3025 个原子的两类电荷绘制在带对角参考线的散点图中，并按化合物离子性着色，可以直接看出静态电荷分配与动态极化电荷之间的系统差异。

下一步接 [差分电荷密度](/Atlas/m/delta-charge/vasp/)，查看电子在空间中的增减位置；或接 [ELF](/Atlas/m/elf/vasp/)，读取这次同一计算写出的局域化函数。盆地电荷与空间分布回答的问题不同，应保留各自的定义。

```text
收敛的固定几何 SCF
  ├─ CHGCAR：积分价电子
  └─ AECCAR0 + AECCAR2：找分区边界的参考
                 └─ 相同结构与完整网格检查 → Bader → ACF.dat
                                                   └─ 总数、等价性与网格加密检查
```
