要看接触改变了哪里，先明确与什么状态相比。对冻结的异质结几何，差分电子数密度定义为 $\Delta n(\mathbf r)=n_{AB}(\mathbf r)-n_A(\mathbf r)-n_B(\mathbf r)$：AB 是完整体系，A、B 是删去另一层后保持原位的独立自洽片段。正值表示相对于这组参考的电子积累，负值表示耗尽；电荷密度变化则是 $-e\Delta n$。

先看成键把电子放到了哪里，再问某一侧一共得到多少。H₂的两个H等价：用同一几何的分子减去两个原位、自旋极化的独立H，键区会出现积累，但两半分子的净增电子数仍可接近零。下面的等值面、法向曲线与区间表都来自这组真实存档。

前置计算见 [SCF](/Atlas/m/scf/vasp/)。[下载 H₂ 输入输出、分析源码](/Atlas/examples/h2-delta-charge-files.tar.gz)，解包为 `h2-delta-charge`；三份完整密度分别为 [AB](/Atlas/examples/h2-delta-charge/AB/CHGCAR.gz)、[A](/Atlas/examples/h2-delta-charge/A/CHGCAR.gz)、[B](/Atlas/examples/h2-delta-charge/B/CHGCAR.gz)，放回同名子目录。程序可直接读 gzip，POTCAR 使用自己的授权文件。


## 先看重排发生在哪里

<figure><img src="/Atlas/examples/delta-charge/h2_delta_3d_zoom.png" alt="H2真实差分密度等值面，金黄积累蓝色耗尽" loading="lazy"/><figcaption>H–H=0.74 Å，金黄为+0.03 e/Å³，蓝色为−0.03 e/Å³。VESTA显示范围为分数坐标0.3–0.7，沿a方向观察。键区积累、轴两端耗尽，对应冻结原子参考的成键重排。</figcaption></figure>

金黄在键区，蓝色沿两颗H的轴向外侧。它们表示相对于独立原子的积累与耗尽，不是电子沿某个箭头运动的轨迹。H的实际位置为z=4.63、5.37 Å；分子中面为5 Å。等值面只显示达到±0.03 e/Å³的边界，所有积分仍使用完整网格。

把同一三维差分密度沿xy积分，得到上幅的线密度。这里定义 $\lambda(z)=S\overline{\Delta n}(z)$：平面平均 $\overline{\Delta n}(z)$ 的单位为 e/Å³，乘本例面积100 Å²后，λ的单位为 e/Å。再从胞原点积分，得到下幅累计量 $T(z)=\int_0^z\lambda(z')\,dz'$，单位为e。gnuplot 读取现有 `planar.csv`：第一列 z/Å、第三列 $S\overline{\Delta n}$/e·Å⁻¹、第四列 $T(z)$/e，直接保留 CSV 样本。两条点线是实际 H 位置4.63、5.37 Å，虚线是分区边界5 Å。

![H₂真实面积积分差分密度与累计积分，沿同一z坐标比较](/Atlas/examples/charge-literature/h2-planar-and-cumulative.svg)

上图在 H–H 之间出现积累峰，沿轴向两端出现耗尽；下图先下降再上升，在5 Å边界附近返回零。局部正负峰清楚可见，半胞净数却仍接近零，这正是本例成键重排与层净转移的区别。三维图中的黄色键区与曲线的中间正峰相对应；曲线已汇总整张xy平面，轴两端的负峰则来自平面内耗尽占优的区域。

## 移动边界，为什么读数会变号

以z₍b₎为边界，左侧积分从0到z₍b₎，右侧从z₍b₎到10 Å。正号表示该空间区域相对于独立原子参考多了电子。由同一份145行CSV（含周期端点）得到：

| 边界 z₍b₎ / Å | 左侧净增电子数 / e | 右侧净增电子数 / e |
| ---: | ---: | ---: |
| 4.90 | −0.0320680911 | +0.0320680916 |
| 5.00 | +1.29×10⁻⁹ | −8.50×10⁻¹⁰ |
| 5.10 | +0.0320680936 | −0.0320680932 |

5 Å按等价两H的对称中面分区，两边的积累与耗尽各自抵消，因而没有从一颗H向另一颗H的有限净转移。边界左移到4.9 Å，左区少算了一段键区积累，读数变负；右移到5.1 Å则多算这一段，读数变正。密度、原子与电子数均未变化，变的是空间归属。把这两个非对称读数称为“H向H转移0.032 e”就会把人为边界当作材料变化。

累计曲线在5 Å附近斜率较大，因为这里的线密度为正且接近峰值。因此边界稍移，净数就明显变化。研究界面时，可在所选间隙内移动边界并查看累计曲线是否有稳定区；没有稳定区时，报告边界敏感性，再与明确算法的Bader层加总对照。全胞积分接近零只检验守恒，不能替代这个归属检查。

<!-- atlas-h2-widget-start -->
<details>
<summary>移动分区边界，核对两侧的净增电子数</summary>

<iframe id="h2-charge-widget" src="/Atlas/examples/charge-interactive/h2/?embed=1" title="H₂ 差分密度的边界积分交互" loading="lazy" style="display:block;width:100%;height:1400px;border:0;"></iframe>
<p><a href="/Atlas/examples/charge-interactive/h2/" target="_blank" rel="noopener">打开完整交互页、原始数据与绘图源码</a></p>
</details>
<script>
(() => {
  const frame = document.getElementById('h2-charge-widget');
  if (!frame) return;
  const origin = new URL(frame.src, window.location.href).origin;
  window.addEventListener('message', event => {
    if (event.origin !== origin || event.source !== frame.contentWindow) return;
    if (event.data?.type !== 'atlas-charge-height') return;
    const height = event.data.height;
    if (Number.isFinite(height) && height >= 200 && height <= 10000)
      frame.style.height = String(Math.ceil(height)) + 'px';
  });
  frame.addEventListener('load', () => {
    frame.contentWindow.postMessage({type:'atlas-charge-size-request'}, origin);
  });
})();
</script>
<!-- atlas-h2-widget-end -->

## 一维正区和三维积累区为何不同

上图黄色曲线的正面积为0.2019387395 e，完整三维网格所有正值的积分为0.2578313944 e。它们分别定义为 $P_{1D}=\int_0^H\max[\lambda(z),0]\,dz$ 和 $P_{3D}=\int_V\max[\Delta n(\mathbf r),0]\,dV$。

前者先把同一xy平面内的积累与耗尽相加，得到一个有正负号的线密度，再只积分正段；后者在每个三维网格点先取正值，耗尽点不参与抵消。因此 $P_{1D}\le P_{3D}$：一张平面内同时存在积累和耗尽时，一维曲线会丢掉它们互相抵消的部分。本例相差约0.05589 e，不是脚本少读了网格，也不需要把曲线乘系数“补齐”。

这两个正区量都汇总局部重排；左右半空间的净数则保留该区所有正负贡献。三种读数的区域与运算顺序不同，不能统一写成“转移电荷”。沿其他方向做平面积分还可能得到不同的正区量，完整三维正值积分仍对应原密度。

[边界复核脚本](/Atlas/examples/enrichment-20261003/charge/verify_boundaries.py)使用Python标准库，读取既有 [planar.csv](/Atlas/examples/charge-planar/h2-half-spaces/planar.csv) 与 [summary.json](/Atlas/examples/charge-planar/h2-half-spaces/summary.json)。将三份文件放在同一目录，在一个新输出目录复核：

```console
python3 -B verify_boundaries.py --planar planar.csv --summary summary.json --output-dir h2-boundary-check
```

它按分段线性的线密度积分：网格之间的部分积分为二次函数，正区面积在过零点处分段；不是对累计表简单线性插值。实际执行输出为：

```text
samples=145; full-cell residual=4.362638343170e-10 e
positive 1D=0.2019387395 e; positive 3D=0.2578313944 e
boundary=4.90 A: left=-3.206809111656e-02 e; right=+3.206809155282e-02 e
boundary=5.00 A: left=+1.286514871740e-09 e; right=-8.502510374225e-10 e
boundary=5.10 A: left=+3.206809364178e-02 e; right=-3.206809320551e-02 e
```

[完整11组边界表](/Atlas/examples/enrichment-20261003/charge/h2-boundary-check/boundary-reference.csv)与[检查摘要](/Atlas/examples/enrichment-20261003/charge/h2-boundary-check/boundary-reference.json)同时保留三维正负积分、单位关系和累计量误差。脚本复核现有平面数据；三维积累量保留原密度积分摘要中的结果。

<figure style="max-width:680px;margin:1.5rem auto;"><a href="/Atlas/examples/charge-interactive/h2/zri2-dirac-fig5.jpg"><img src="/Atlas/examples/charge-interactive/h2/zri2-dirac-fig5.jpg" alt="ZrI2与六种Dirac半金属接触的原论文Fig.5，黄色积累、青色耗尽，左下(d)为graphene" loading="lazy" style="width:100%;height:auto;"/></a><figcaption>原论文 Fig. 5(a–f)，本段讨论左下(d)的 ZrI₂/graphene。来源：<a href="https://doi.org/10.1039/D5CP02349A">Robust p-type ohmic contact in ZrI₂–Dirac semi-metal van der Waals heterostructures，DOI:10.1039/D5CP02349A</a>。点击图片查看完整像素原图；各面板纵轴范围分别标示。</figcaption></figure>

界面论文可按相同问题读。[ZrI₂/Dirac半金属原文Fig. 5(d)](https://doi.org/10.1039/D5CP02349A)是ZrI₂/graphene，横轴z-distance/Å、纵轴Δρ/e·Å⁻¹；纵轴单位说明它对应这里的面积积分线密度，而非e/Å³的平面平均。黄色在零线上方、青色在下方，三维插图补充重排的原子位置。插图中的结构没有与横轴作严格等比例坐标映射，不能凭插图原子横向位置读取某个z边界；本例曲线上的H位置直接来自POSCAR。六个面板各有纵轴范围，跨体系比较须使用同定义区域的积分与面积，而不是颜色大小。原文采用QuantumATK可视化，本例用VESTA；接触结论仍属于原文模型。

## 三份参考保持同一几何和网格

10 Å 立方胞内，两颗 H 的坐标为(5,5,4.63)和(5,5,5.37) Å，固定键长0.74 Å。删原子后既不移动余下原子，也不独立优化。

```console
[bcgong@localhost grid144]$ cat AB/POSCAR A/POSCAR B/POSCAR
H2 charge difference AB
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
2
Cartesian
5.000000 5.000000 4.630000
5.000000 5.000000 5.370000

H2 charge difference A
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
1
Cartesian
5.000000 5.000000 4.630000

H2 charge difference B
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
1
Cartesian
5.000000 5.000000 5.370000
[bcgong@localhost grid144]$
```

```console
[bcgong@localhost grid144]$ cat AB/INCAR
SYSTEM = H2 fixed geometry charge difference
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 100
ALGO = Normal
ISMEAR = 0
SIGMA = 0.02
ISPIN = 2
MAGMOM = 1 -1
ISYM = 0
NBANDS = 8
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
LMAXMIX = 2
NCORE = 1
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .TRUE.
NGX = 72
NGY = 72
NGZ = 72
NGXF = 144
NGYF = 144
NGZF = 144
[bcgong@localhost grid144]$
```

三项共同使用400 eV、Gaussian 0.02 eV、EDIFF=1E−8、Γ点和72³/144³网格。A 的初始磁矩为+1，B为−1，分子为1 −1，最终磁矩随后核对。ISPIN=2使单 H 的未配对电子能进入独立自洽参考。除SYSTEM和MAGMOM外，电子协议一致。

```console
[bcgong@localhost grid144]$ cat AB/KPOINTS
Gamma for an isolated molecule in a periodic box
0
Gamma
1 1 1
0 0 0
[bcgong@localhost grid144]$
```

```console
[bcgong@localhost grid144]$ cat AB/run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-h2g144-AB
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
unset SLURM_CPUS_PER_TASK
export I_MPI_PIN_PROCESSOR_LIST=16,17,18,19
cd "$SLURM_SUBMIT_DIR"
mpirun -np 4 <vasp_bin>/vasp_std > out
[bcgong@localhost grid144]$
```

```console
[bcgong@localhost AB]$ sbatch run.slurm
Submitted batch job 18203
[bcgong@localhost AB]$ tail -4 out
DAV:  26    -0.675757525392E+01   -0.96419E-07   -0.89909E-10    32   0.964E-05    0.141E-05
DAV:  27    -0.675757527955E+01   -0.25634E-07   -0.32106E-10    32   0.582E-05    0.892E-06
DAV:  28    -0.675757528376E+01   -0.42084E-08   -0.20943E-11    32   0.152E-05
   1 F= -.67575753E+01 E0= -.67575753E+01  d E =-.395750E-14  mag=    -0.0000
[bcgong@localhost AB]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       37.584
[bcgong@localhost AB]$ cd ../A
[bcgong@localhost A]$ sbatch run.slurm
Submitted batch job 18204
[bcgong@localhost A]$ tail -3 out
DAV:  31    -0.111553427162E+01   -0.37212E-07    0.11147E-11    40   0.712E-07    0.109E-07
DAV:  32    -0.111553427860E+01   -0.69796E-08    0.21005E-11    32   0.517E-07
   1 F= -.11155343E+01 E0= -.11155343E+01  d E =-.379612E-12  mag=     1.0000
[bcgong@localhost A]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       43.484
[bcgong@localhost A]$ cd ../B
[bcgong@localhost B]$ sbatch run.slurm
Submitted batch job 18205
[bcgong@localhost B]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       42.155
[bcgong@localhost B]$ cd ..
```

这是VASP 5.4.4的存档执行，4个MPI进程，AB/A/B分别达到EDIFF并完整结束。前一组48³/96³留下FFT不足警告，正文使用警告消失的72³/144³数据；更细网格、盒长和截断的变化仍应按目标密度检查。旧警告和程序头部保留在执行记录。

## 第一密度块相减，积分先检查总数

```console
[bcgong@localhost grid144]$ head -n 15 AB/CHGCAR
H2 fixed geometry charge difference     
   1.00000000000000     
    10.000000    0.000000    0.000000
     0.000000   10.000000    0.000000
     0.000000    0.000000   10.000000
   H 
     2
Direct
  0.500000  0.500000  0.463000
  0.500000  0.500000  0.537000
 
  144  144  144
 -.14180101703E-06 0.15839254613E-05 0.82756458881E-05 0.18919626660E-04 0.24598790238E-04
 0.17342576419E-04 0.32962757902E-05 -.14502942528E-05 0.91047738927E-05 0.21835186348E-04
 0.20713305658E-04 0.74212176581E-05 -.14663704630E-05 0.36751736964E-05 0.14473913947E-04
[bcgong@localhost grid144]$
```

```text
n_i = D_i / V                         单位：e/Å³
NELECT = Σ_i D_i / Ngrid
Δn_i = (D_AB,i − D_A,i − D_B,i) / V
∫ Δn(r) dr ≈ Σ_i (D_AB,i − D_A,i − D_B,i) / Ngrid
```

x索引最快、z最慢；首块有144³个总密度值，第二块是磁化密度，中间的PAW一中心数字不拼入网格。$\sum D/N_{\mathrm{grid}}$给价电子数，$D/V$给 e/Å³；相减后仍遵循同一约定。[CHGCAR 文件定义](https://vasp.at/wiki/CHGCAR)。

下面的程序需求包含原位、协议、总数与自旋参考检查；完整 [analyze_charge.py](/Atlas/examples/h2-delta-charge/analyze_charge.py) 在文末，可在解包目录直接运行。

```text
编写 Python 3 的 analyze_charge.py，读取 AB、A、B 目录的 CHGCAR 或 CHGCAR.gz 及对应 OUTCAR、OSZICAR、KPOINTS 与赝势指纹。核对电子收敛、正常退出、相同晶胞和网格、相同 k 点及赝势，并确认 A/B 原子保持 AB 中原位。分别读取第一块总密度与第二块磁化密度，各取 nx*ny*nz 个值；按 ΣD/N 积分，检查总数与 NELECT、磁化积分与最终磁矩。用第一块计算 AB−A−B，输出全胞、正值、负值积分及 e/Å³ 极值，保存 CHGDIFF.vasp、delta-charge.cube、delta-planar.csv、delta-y5.csv、charge-difference-summary.json。保持源文件只读，按原始数据计算，不归一化到期望值。
```

```console
[bcgong@localhost grid144]$ python -B analyze_charge.py | tee analysis.out
AB NELECT=2.0 integral=2.0000000029 e mag(OSZICAR)=-0.0000 mag(grid)=-0.0000000000
A NELECT=1.0 integral=1.0000000012 e mag(OSZICAR)=1.0000 mag(grid)=1.0000000012
B NELECT=1.0 integral=1.0000000012 e mag(OSZICAR)=-1.0000 mag(grid)=-1.0000000012
grid = 144 144 144; points = 2985984; volume = 1000.000000 A^3
integral_delta = 4.362638146422e-10 e; accumulated = 0.2578313944 e; depleted = -0.2578313940 e
delta_n range = -0.0555594237 to 0.8029641058 e/A^3
cumulative endpoint = 4.362638192728e-10 e
Wrote CHGDIFF.vasp, delta-charge.cube, delta-planar.csv, delta-y5.csv, charge-difference-summary.json
[bcgong@localhost grid144]$
```

分子积分为2.0000000029 e，两个原子各约1 e；磁化积分分别约0、+1、−1 μB，与OSZICAR对应。差分全胞残差4.36×10⁻¹⁰ e很小，而积累区有0.2578313944 e、耗尽区有−0.2578313940 e。这说明成键把电子重新安排到空间中。正区积分把全胞所有积累区域相加，不等于从一个原子或一层流向另一层的净数。

## 平面平均、累计积分与层电子数

对于面内面积 $S=\lVert\mathbf a\times\mathbf b\rVert$、法向高度 $H=V/S$，在第k层对nx×ny个值平均：$\overline{\Delta n}_k=\frac{\sum_{ij}\Delta D_{ijk}}{n_x n_y V}$，单位 e/Å³。乘S得到线密度 $\lambda(z)=S\overline{\Delta n}(z)$，单位 e/Å。累计量 $T(z)=\int_0^z\lambda(z')\,dz'$，单位e；某层由z₁、z₂划定时，净增电子数 $\Delta N_{\mathrm{layer}}=T(z_2)-T(z_1)$。如果文献把“平面平均”写成未除面积的平面积分，纵轴已经是 e/Å，此时不能再乘S。

积分下限0是所选周期胞的原点；它应放在远离原子的真空区。层边界通常在界面间隙内选择，并检查移动边界时数值是否稳定。只有电子守恒而$T(H)$接近零，不能据此断言中间所有区域都没有转移。对强重叠界面，层归属可能随边界明显变化，需同时给边界和Bader分区。

这里进一步用三份原始H₂密度复算，以0、5、10 Å把晶胞分为两半。S=100 Å²，H=10 Å；周期端点补回首平面，平面值之间用线性插值，梯形积分并对落在网格间的边界积分部分线段。没有按期望值归一化。

程序核对用户给出的三项电子数与网格积分，并要求电子数可加；它不读取各片段的ZVAL或电荷设置，不能据此自动证明片段中性。本例H₂的中性2/1/1电子参考由前面的输入与原输出确认。

[完整 integrate_planar.py](/Atlas/examples/charge-planar/integrate_planar.py) 与 [同目录读取模块 build_delta_chgcar.py](/Atlas/examples/charge-planar/build_delta_chgcar.py) 需要 Python 3、NumPy。把两个脚本放在 `h2-delta-charge` 根目录，在同一目录执行：

```bash
python3 -B integrate_planar.py --ab AB/CHGCAR.gz --a A/CHGCAR.gz --b B/CHGCAR.gz --nelect 2 1 1 --boundaries 0 5 10 --output-dir h2-half-spaces
```

Talos实际重读原密度的输出为：

```text
area=100.000000000 A^2; height=10.000000000 A; grid=144 144 144
full-cell residual=4.362638194610e-10 e; cumulative endpoint=4.362638206950e-10 e
0.000000:5.000000 A: delta_e=+1.286514813409e-09; area_density=+1.286514813409e+05 e/cm^2
5.000000:10.000000 A: delta_e=-8.502509927145e-10; area_density=-8.502509927145e+04 e/cm^2
positive 3D redistribution=0.2578313944 e
```

两个半空间净增电子数都在10⁻⁹ e量级，与这个对称参考的零转移一致；把极小残差乘10¹⁶换算后看起来较大，它仍是数值残差，不能解释成可用掺杂密度。0.2578 e的三维正区积分与近零的半空间净数并存，正好体现成键重排和定向层转移回答不同问题。可下载 [平面值与累计量](/Atlas/examples/charge-planar/h2-half-spaces/planar.csv)、[区间积分](/Atlas/examples/charge-planar/h2-half-spaces/regions.csv)、[来源与积分摘要](/Atlas/examples/charge-planar/h2-half-spaces/summary.json)。



下载 [原CSV](/Atlas/examples/charge-planar/h2-half-spaces/planar.csv) 与 [gnuplot完整脚本](/Atlas/examples/charge-literature/h2-planar-and-cumulative.gnuplot)，放在同一目录，可重建 SVG、PDF和PNG：

```bash
gnuplot -e "datafile='planar.csv'" h2-planar-and-cumulative.gnuplot
```

需要处理自己的匹配密度时，可把以下需求交给编程助手；NELECT与边界由真实输出和结构给出：

```text
编写Python 3+NumPy命令行程序integrate_planar.py，使用随包的read_chgcar读取AB/A/B首个总密度块。核对有限值、相同晶格和FFT网格、片段原子原位，并用ΣD/N检查用户提供的三项NELECT；要求三项电子数满足NELECT_AB=NELECT_A+NELECT_B；这不自动证明A/B中性，片段电荷态须依据各自输入、OUTCAR和价电子协议确定。计算S=|a×b|、H=V/S和法向z=kH/nz；写Δn̄(e/Å³)、SΔn̄(e/Å)和周期线性插值积分T(e)。用户明确提供法向边界，积分各区间，给ΔN、ΔN/S及乘10^16后的e/cm²；检查全胞残差，禁止修正密度或自动把正区积分称为层转移。保留未舍入JSON、输入身份、单位和积分方法，新目录拒绝覆盖。仅作后处理，不运行DFT或画装饰图。
```

异质结中，$\Delta N_{\mathrm{layer}}/S$才是所选空间分区下的转移面积密度。自由载流子还需确认哪些能带改变占据以及费米面体积/面积；满占据成键态的极化也会进入CDD。带电单层的NELECT调控与界面分区数不能直接互换。

## 等值面看位置，数值从完整网格读

[下载VESTA网格、场景与转换脚本](/Atlas/examples/charge-vesta-files.tar.gz)，进入 `charge-vesta`。转换保留AB结构，只写第一差分标量块；[build_delta_chgcar.py](/Atlas/examples/charge-vesta/scripts/build_delta_chgcar.py)的需求、源码和实际命令在文末。VESTA打开 `h2/CHGCAR_DELTA`，核对物理阈值±0.03 e/Å³；存储值为±30，本次显示界面转换为±0.00444555 e/bohr³，读显示单位后再输入。

图的阈值只决定展示哪些区域；减小阈值出现更大体积不表示净转移增加。原平面轮廓截图没有可复核的切面坐标与连续色标，定量讨论改用上面的真实网格表。

原文 Fig. 5(d) 把法向曲线与三维插图并列，六个(a–f)面板的纵轴范围各自不同，比较时先读单位和刻度，不能凭黄色面积大小跨构型排序。本例 VESTA 等值面仍是±0.03 e/Å³，曲线则是 e/Å，两种单位的差别正是是否做过面积积分。若要给层转移数，则继续积分并说明边界；[Bader](/Atlas/m/bader/vasp/)提供另一种盆地加总，[ELF](/Atlas/m/elf/vasp/)则接局域化与能窗态的区别。


## 完整源码与执行记录

<details>
<summary>analyze_charge.py 的完整源码</summary>

```python
from __future__ import print_function
import os, re, math, json, hashlib, csv, gzip, io
BOHR = 0.529177210903

def det(cell):
    a,b,c=cell
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def finite(values):
    return all(not (math.isnan(x) or math.isinf(x)) for x in values)

def open_text(filename):
    if os.path.isfile(filename):
        return io.open(filename, 'r', encoding='ascii')
    if os.path.isfile(filename+'.gz'):
        return io.TextIOWrapper(gzip.open(filename+'.gz', 'rb'), encoding='ascii')
    raise IOError('Missing '+filename+' or '+filename+'.gz')

def digest(filename):
    if os.path.isfile(filename):
        handle=open(filename,'rb')
    elif os.path.isfile(filename+'.gz'):
        handle=gzip.open(filename+'.gz','rb')
    elif filename.endswith('/POTCAR') and os.path.isfile(filename+'.sha256'):
        value=open(filename+'.sha256').read().split()[0]
        if not re.match(r'^[0-9a-f]{64}$',value):
            raise ValueError('Invalid pseudopotential fingerprint')
        return value
    else:
        raise IOError('Missing source '+filename)
    sha=hashlib.sha256()
    while True:
        chunk=handle.read(1024*1024)
        if not chunk:break
        sha.update(chunk)
    handle.close()
    return sha.hexdigest()

def read_charge(filename):
    f=open_text(filename)
    head=[f.readline(),f.readline()]
    scale=float(head[1].split()[0])
    if scale<=0:raise ValueError('This example requires a positive scalar scale')
    lines=[f.readline() for _ in range(3)];head+=lines
    cell=[[float(x)*scale for x in line.split()[:3]] for line in lines]
    species=f.readline();counts_line=f.readline();head += [species,counts_line]
    counts=list(map(int,counts_line.split()));nat=sum(counts)
    mode=f.readline();head.append(mode)
    if mode.lower().startswith('s'):mode=f.readline();head.append(mode)
    coords_lines=[f.readline() for _ in range(nat)];head+=coords_lines
    coords=[[float(x) for x in line.split()[:3]] for line in coords_lines]
    if mode.lower().startswith('d'):
        positions=[[sum(v[k]*cell[k][a] for k in range(3)) for a in range(3)] for v in coords]
    elif mode.lower().startswith(('c','k')):
        positions=[[x*scale for x in v] for v in coords]
    else:raise ValueError('Unknown coordinate mode')
    line=f.readline()
    while line and not line.strip():line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0:raise ValueError('Invalid charge grid')
    n=grid[0]*grid[1]*grid[2]
    def block():
        values=[]
        while len(values)<n:
            line=f.readline()
            if not line:raise ValueError('Truncated scalar block')
            values.extend(float(x.replace('D','E')) for x in line.split())
        if len(values)!=n or not finite(values):raise ValueError('Invalid scalar block length/values')
        return values
    total=block()
    magnetic=None
    while True:
        line=f.readline()
        if not line:break
        words=line.split()
        if len(words)==3 and all(re.match(r'^\d+$',x) for x in words):
            candidate=list(map(int,words))
            if candidate==grid:
                magnetic=block();break
    f.close()
    if magnetic is None:raise ValueError('Expected second spin-density block')
    return dict(header=head,cell=cell,species=species.split(),counts=counts,
                positions=positions,grid=grid,total=total,magnetic=magnetic)

def incar(path):
    result={}
    for line in open(path):
        line=line.split('#',1)[0].split('!',1)[0]
        if '=' in line:
            key,value=line.split('=',1)
            if key.strip().upper() not in ('SYSTEM','MAGMOM'):
                result[key.strip().upper()]=value.strip()
    return result

cases={}
protocol=None
for name,expected_nelect,expected_mag in [('AB',2.,0.),('A',1.,1.),('B',1.,-1.)]:
    out=open(name+'/OUTCAR').read()
    if out.count('aborting loop because EDIFF is reached')!=1 or out.count('General timing and accounting')!=1:
        raise ValueError(name+': missing converged SCF / normal end')
    if re.search(r'VERY BAD NEWS|BRMIX:|Error EDD|ZHEGV failed',out,re.I):
        raise ValueError(name+': solver error')
    if 'Your FFT grids' in out:
        raise ValueError(name+': VASP reports an insufficient FFT grid')
    nelect=float(re.findall(r'NELECT\s*=\s*([-\d.]+)',out)[-1])
    mag=float(re.findall(r'mag=\s*([-\d.Ee+]+)',open(name+'/OSZICAR').read())[-1])
    data=read_charge(name+'/CHGCAR');n=len(data['total'])
    total=math.fsum(data['total'])/n
    spin=math.fsum(data['magnetic'])/n
    if abs(total-nelect)>1e-5 or abs(nelect-expected_nelect)>1e-8:
        raise ValueError(name+': electron count mismatch')
    if abs(mag-expected_mag)>2e-4 or abs(spin-mag)>2e-4:
        raise ValueError(name+': unexpected spin state')
    tags=incar(name+'/INCAR')
    if protocol is None:protocol=tags
    elif tags!=protocol:raise ValueError('Different electronic protocols')
    data.update(nelect=nelect,integral_e=total,mag_OSZICAR_muB=mag,mag_grid_muB=spin)
    cases[name]=data

ab,a,b=[cases[name] for name in ('AB','A','B')]
if not (ab['grid']==a['grid']==b['grid']):raise ValueError('FFT grids differ')
if not (ab['cell']==a['cell']==b['cell']):raise ValueError('Cells differ')
if not (ab['species']==a['species']==b['species']==['H']):raise ValueError('Expected the H model')
if ab['counts']!=[2] or a['counts']!=[1] or b['counts']!=[1]:raise ValueError('Wrong atom counts')
for point,target in [(a['positions'][0],ab['positions'][0]),(b['positions'][0],ab['positions'][1])]:
    if max(abs(x-y) for x,y in zip(point,target))>1e-6:raise ValueError('A fragment moved')
hashes={}
pot_hash=[]
for name in ('AB','A','B'):
    for filename in ('POSCAR','INCAR','KPOINTS','OUTCAR','OSZICAR','CHGCAR','POTCAR'):
        value=digest(name+'/'+filename)
        if filename=='POTCAR':pot_hash.append(value)
        else:hashes[name+'/'+filename]=value
if len(set(pot_hash))!=1:raise ValueError('Different pseudopotentials')
if len(set(open(name+'/KPOINTS').read() for name in ('AB','A','B')))!=1:
    raise ValueError('Different k sampling')
vol=abs(det(ab['cell']));nx,ny,nz=ab['grid'];n=nx*ny*nz
if max(abs(ab['cell'][i][j]-(10. if i==j else 0.)) for i in range(3) for j in range(3))>1e-8:
    raise ValueError('Plot extraction is specific to the 10 Angstrom cubic cell')
delta=[x-y-z for x,y,z in zip(ab['total'],a['total'],b['total'])]
integral=math.fsum(delta)/n
if abs(integral)>1e-5:raise ValueError('Charge difference does not integrate to zero')
positive=math.fsum(x for x in delta if x>0)/n
negative=math.fsum(x for x in delta if x<0)/n
nxy=nx*ny
plane=[math.fsum(delta[k*nxy:(k+1)*nxy])/nxy/vol for k in range(nz)]
linear=[100.*x for x in plane]
dz=10./nz
cumulative=[0.]
for k in range(1,nz+1):
    cumulative.append(cumulative[-1]+.5*(linear[k-1]+linear[k%nz])*dz)
with open('delta-planar.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['z_A','delta_n_e_A3','delta_N_e_A','cumulative_e'])
    for k in range(nz+1):
        writer.writerow(['%.10f'%(k*dz),'%.12e'%plane[k%nz],
                         '%.12e'%linear[k%nz],'%.12e'%cumulative[k]])
j=ny//2
with open('delta-y5.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['x_A','z_A','delta_n_e_A3'])
    for k in range(nz):
        for i in range(nx):
            writer.writerow(['%.10f'%(10.*i/nx),'%.10f'%(10.*k/nz),
                             '%.12e'%(delta[(k*ny+j)*nx+i]/vol)])
with open('CHGDIFF.vasp','w') as handle:
    handle.writelines(ab['header']);handle.write('\n%d %d %d\n'%(nx,ny,nz))
    for k in range(0,n,5):handle.write(' '.join('%.11E'%x for x in delta[k:k+5])+'\n')
# A Gaussian cube uses bohr and electrons/bohr^3; its z index runs fastest.
with open('delta-charge.cube','w') as handle:
    handle.write('H2 minus frozen spin-polarized H fragments\n')
    handle.write('Signed electron-number density in electrons/bohr^3\n')
    handle.write('%5d %13.8f %13.8f %13.8f\n'%(2,0.,0.,0.))
    for count,vector in zip((nx,ny,nz),ab['cell']):
        handle.write('%5d %13.8f %13.8f %13.8f\n'%tuple([count]+[v/count/BOHR for v in vector]))
    for position in ab['positions']:
        handle.write('%5d %13.8f %13.8f %13.8f %13.8f\n'%tuple([1,1.]+[v/BOHR for v in position]))
    line=[]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                line.append('%.10E'%(delta[(k*ny+j)*nx+i]/vol*BOHR**3))
                if len(line)==6:handle.write(' '.join(line)+'\n');line=[]
    if line:handle.write(' '.join(line)+'\n')
summary={'grid':ab['grid'],'volume_A3':vol,'positions_A':ab['positions'],
         'delta_integral_e':integral,'positive_integral_e':positive,'negative_integral_e':negative,
         'minimum_delta_n_e_A3':min(delta)/vol,'maximum_delta_n_e_A3':max(delta)/vol,
         'cumulative_endpoint_e':cumulative[-1],'potcar_sha256':pot_hash[0],
         'definition':'total-charge first block: AB - A - B; density = stored_value / cell_volume',
         'sha256':hashes,'cases':{}}
for name in ('AB','A','B'):
    summary['cases'][name]={key:cases[name][key] for key in
        ('nelect','integral_e','mag_OSZICAR_muB','mag_grid_muB')}
with open('charge-difference-summary.json','w') as handle:json.dump(summary,handle,indent=2,sort_keys=True)
for name in ('AB','A','B'):
    row=summary['cases'][name]
    print('%s NELECT=%.1f integral=%.10f e mag(OSZICAR)=%.4f mag(grid)=%.10f'%
          (name,row['nelect'],row['integral_e'],row['mag_OSZICAR_muB'],row['mag_grid_muB']))
print('grid = %d %d %d; points = %d; volume = %.6f A^3'%(nx,ny,nz,n,vol))
print('integral_delta = %.12e e; accumulated = %.10f e; depleted = %.10f e'%(integral,positive,negative))
print('delta_n range = %.10f to %.10f e/A^3'%(min(delta)/vol,max(delta)/vol))
print('cumulative endpoint = %.12e e'%cumulative[-1])
print('Wrote CHGDIFF.vasp, delta-charge.cube, delta-planar.csv, delta-y5.csv, charge-difference-summary.json')
```

</details>

<details>
<summary>build_delta_chgcar.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Build a VESTA-readable VASP volumetric file for Δρ = ρ(AB) − ρ(A) − ρ(B).

Inputs are CHGCAR files (plain text or gzip-compressed).  The script reads only
VASP's first total-charge grid block; magnetization and PAW augmentation blocks
are not part of the plotted scalar field.  The output keeps VASP's stored
volume-scaled values, so divide a grid value by cell volume (Å³) to get e/Å³.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import Iterable, TextIO

import numpy as np

_INTEGER = re.compile(r"^[+-]?\d+$")


def _open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="ascii", errors="strict")
    return path.open("rt", encoding="ascii", errors="strict")


def _line(stream: TextIO, label: str) -> str:
    value = stream.readline()
    if not value:
        raise ValueError(f"Unexpected end of file while reading {label}")
    return value


def _ints(tokens: list[str]) -> bool:
    return bool(tokens) and all(_INTEGER.fullmatch(token) for token in tokens)


def _float(token: str) -> float:
    return float(token.replace("D", "E").replace("d", "e"))


def _float_values(stream: TextIO) -> Iterable[float]:
    for line in stream:
        for token in line.split():
            yield _float(token)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_uncompressed(path: Path) -> str:
    opener = gzip.open if path.suffix.lower() == ".gz" else open
    digest = hashlib.sha256()
    with opener(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_chgcar(path: Path) -> dict:
    """Parse cell/atoms, one 3-D total-charge block, and its exact VASP header."""
    header: list[str] = []
    with _open_text(path) as stream:
        title = _line(stream, "title")
        header.append(title)
        scale_tokens = _line(stream, "scale factor").split()
        header.append(" ".join(scale_tokens) + "\n")
        if not scale_tokens:
            raise ValueError(f"{path}: missing scale factor")
        scale = _float(scale_tokens[0])

        raw_cell = []
        for axis in "abc":
            row = _line(stream, f"lattice vector {axis}")
            header.append(row)
            values = [_float(token) for token in row.split()[:3]]
            if len(values) != 3:
                raise ValueError(f"{path}: invalid lattice vector {axis}")
            raw_cell.append(values)
        raw_cell = np.asarray(raw_cell, dtype=np.float64)
        raw_volume = abs(float(np.linalg.det(raw_cell)))
        if raw_volume <= 0 or scale == 0:
            raise ValueError(f"{path}: invalid cell volume or scale factor")
        factor = scale if scale > 0 else (abs(scale) / raw_volume) ** (1.0 / 3.0)
        cell = raw_cell * factor

        species_or_counts = _line(stream, "species/count line")
        header.append(species_or_counts)
        fields = species_or_counts.split()
        if _ints(fields):
            counts = [int(token) for token in fields]
            species = [f"X{i + 1}" for i in range(len(counts))]
        else:
            species = fields
            count_line = _line(stream, "atom counts")
            header.append(count_line)
            count_fields = count_line.split()
            if not _ints(count_fields):
                raise ValueError(f"{path}: atom-count line is not integer-valued")
            counts = [int(token) for token in count_fields]
        if len(species) != len(counts) or any(count <= 0 for count in counts):
            raise ValueError(f"{path}: invalid species/count list")
        atom_species = [symbol for symbol, count in zip(species, counts) for _ in range(count)]

        coordinate_line = _line(stream, "coordinate mode or selective-dynamics line")
        header.append(coordinate_line)
        if coordinate_line.strip().lower().startswith("s"):
            coordinate_line = _line(stream, "coordinate mode")
            header.append(coordinate_line)
        mode = coordinate_line.strip().lower()
        if not mode or mode[0] not in {"d", "c", "k"}:
            raise ValueError(f"{path}: unknown coordinate mode {coordinate_line!r}")

        fractional_or_cartesian = []
        for atom_index in range(len(atom_species)):
            atom_line = _line(stream, f"atom coordinate {atom_index + 1}")
            header.append(atom_line)
            xyz = [_float(token) for token in atom_line.split()[:3]]
            if len(xyz) != 3:
                raise ValueError(f"{path}: invalid coordinate for atom {atom_index + 1}")
            fractional_or_cartesian.append(xyz)
        coordinates = np.asarray(fractional_or_cartesian, dtype=np.float64)
        cartesian = coordinates @ cell if mode[0] == "d" else coordinates * factor

        dimensions = None
        for _ in range(40):
            candidate = _line(stream, "grid dimensions")
            header.append(candidate)
            fields = candidate.split()
            if _ints(fields) and len(fields) == 3 and all(int(value) > 0 for value in fields):
                dimensions = tuple(int(value) for value in fields)
                break
        if dimensions is None:
            raise ValueError(f"{path}: no 3-D grid dimensions after the structure header")

        npoints = math.prod(dimensions)
        values = np.fromiter(itertools.islice(_float_values(stream), npoints),
                             dtype=np.float64, count=npoints)
        if values.size != npoints:
            raise ValueError(f"{path}: expected {npoints} charge values, read {values.size}")

    return {
        "path": path,
        "header": header,
        "cell": cell,
        "volume_A3": abs(float(np.linalg.det(cell))),
        "species": atom_species,
        "cartesian_A": cartesian,
        "dimensions": dimensions,
        "values": values,
        "sha256_gz_or_file": _sha256_file(path),
        "sha256_uncompressed": _sha256_uncompressed(path),
    }


def check_same_cell_and_grid(data: dict[str, dict]) -> None:
    reference = data["AB"]
    for label in ("A", "B"):
        item = data[label]
        if item["dimensions"] != reference["dimensions"]:
            raise ValueError(f"{label} grid {item['dimensions']} != AB grid {reference['dimensions']}")
        if not np.allclose(item["cell"], reference["cell"], rtol=0.0, atol=1e-8):
            raise ValueError(f"{label} cell vectors differ from AB")
    if len(reference["species"]) != len(data["A"]["species"]) + len(data["B"]["species"]):
        raise ValueError("AB atom count must equal A plus B")

    # Verify that A and B retain the corresponding AB atomic coordinates.
    remaining = list(range(len(reference["species"])))
    for label in ("A", "B"):
        item = data[label]
        for symbol, xyz in zip(item["species"], item["cartesian_A"]):
            matches = [i for i in remaining
                       if reference["species"][i] == symbol
                       and np.allclose(reference["cartesian_A"][i], xyz, rtol=0.0, atol=1e-6)]
            if not matches:
                raise ValueError(f"{label} atom {symbol} at {xyz} Å is not an AB atom at that position")
            remaining.remove(matches[0])
    if remaining:
        raise ValueError(f"A/B references did not account for AB atom indices {remaining}")


def write_grid(path: Path, header: list[str], values: np.ndarray) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}; choose another output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    out_header = list(header)
    out_header[0] = "H2 delta density rho_AB-rho_A-rho_B; VASP volume-scaled grid values\n"
    with path.open("wt", encoding="ascii", newline="\n") as stream:
        stream.writelines(out_header)
        for start in range(0, values.size, 5):
            chunk = values[start:start + 5]
            stream.write(" ".join(f"{value: .11E}" for value in chunk) + "\n")


def build(ab: Path, a: Path, b: Path, output: Path, summary: Path) -> dict:
    for path in (output, summary):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}; choose a new output path")
    if output.resolve() == summary.resolve():
        raise ValueError("Output and summary must have different paths")
    data = {"AB": read_chgcar(ab), "A": read_chgcar(a), "B": read_chgcar(b)}
    check_same_cell_and_grid(data)
    npoints = math.prod(data["AB"]["dimensions"])
    volume = data["AB"]["volume_A3"]
    delta_stored = data["AB"]["values"] - data["A"]["values"] - data["B"]["values"]
    delta_rho = delta_stored / volume

    total_e = float(np.sum(delta_stored, dtype=np.float64) / npoints)
    positive_e = float(np.sum(np.maximum(delta_stored, 0.0), dtype=np.float64) / npoints)
    negative_e = float(np.sum(np.minimum(delta_stored, 0.0), dtype=np.float64) / npoints)
    if abs(total_e) > 1e-6:
        raise ValueError(f"Difference density does not conserve charge: integral={total_e:.9g} e")

    if not all(np.isfinite(item["values"]).all() for item in data.values()):
        raise ValueError("Input grid contains non-finite values")
    write_grid(output, data["AB"]["header"], delta_stored)
    record = {
        "source": {label: {"path": str(item["path"]),
                           "sha256_file": item["sha256_gz_or_file"],
                           "sha256_uncompressed": item["sha256_uncompressed"]}
                   for label, item in data.items()},
        "output": str(output),
        "formula": "rho_AB(r) - rho_A(r) - rho_B(r)",
        "grid": list(data["AB"]["dimensions"]),
        "volume_A3": volume,
        "points": npoints,
        "grid_value_convention": "VASP CHGCAR values are rho(r) * cell_volume; divide this output's grid values by volume_A3 to obtain e/Angstrom^3.",
        "minimum_delta_rho_e_A3": float(np.min(delta_rho)),
        "maximum_delta_rho_e_A3": float(np.max(delta_rho)),
        "delta_integral_e": total_e,
        "negative_integral_e": negative_e,
        "positive_integral_e": positive_e,
        "vesta_symmetric_threshold_grid_value": 30.0,
        "equivalent_threshold_e_A3": 30.0 / volume,
        "input_grid_integrals_e": {
            label: float(np.sum(item["values"], dtype=np.float64) / npoints)
            for label, item in data.items()
        },
        "output_sha256": _sha256_file(output),
    }
    summary.parent.mkdir(parents=True, exist_ok=True)
    if summary.exists():
        raise FileExistsError(f"Refusing to overwrite {summary}; choose another summary path")
    summary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ab", type=Path, required=True, help="AB CHGCAR or CHGCAR.gz")
    parser.add_argument("--a", type=Path, required=True, help="A CHGCAR or CHGCAR.gz")
    parser.add_argument("--b", type=Path, required=True, help="B CHGCAR or CHGCAR.gz")
    parser.add_argument("--output", type=Path, required=True, help="New VESTA-readable VASP volumetric file")
    parser.add_argument("--summary", type=Path, required=True, help="New JSON validation summary")
    args = parser.parse_args()
    result = build(args.ab, args.a, args.b, args.output, args.summary)
    print(f"grid: {result['grid'][0]} {result['grid'][1]} {result['grid'][2]}")
    print(f"volume: {result['volume_A3']:.6f} Å^3")
    print(f"integrals A/B/AB: {result['input_grid_integrals_e']['A']:.9f} / "
          f"{result['input_grid_integrals_e']['B']:.9f} / {result['input_grid_integrals_e']['AB']:.9f} e")
    print(f"delta integral: {result['delta_integral_e']:.3e} e")
    print(f"delta rho min/max: {result['minimum_delta_rho_e_A3']:.6f} / "
          f"{result['maximum_delta_rho_e_A3']:.6f} e/Å^3")
    print(f"±{result['equivalent_threshold_e_A3']:.3f} e/Å^3 maps to ±{result['vesta_symmetric_threshold_grid_value']:.1f} stored VASP grid values (VESTA display units must be checked)")
    print(f"wrote: {result['output']}")
    print(f"summary: {args.summary}")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>同一算例的其余输入、检查命令与保存输出</summary>

```text
Δn(r) = n_AB(r) − n_A(r) − n_B(r)
```

```console
[bcgong@localhost grid144]$ grep -A 8 -B 2 "Your FFT grids" ../AB/OUTCAR
|           W    W  A    A  R    R  N    N  II  N    N   GGGG   !!!           |
|                                                                             |
|      Your FFT grids (NGX,NGY,NGZ) are not sufficient for an accurate        |
|      calculation.                                                           |
|      The results might be wrong                                             |
|      good settings for NGX NGY and  NGZ are                                 |
|                        70  70  and  70                                      |
|     Mind: This setting results in a small but reasonable wrap around error  |
|     It is also necessary to adjust these  values to the FFT routines you use|
|                                                                             |
 -----------------------------------------------------------------------------
[bcgong@localhost grid144]$
```

```console
[bcgong@localhost grid144]$ head -n 24 AB/out
 running on    4 total cores
 distrk:  each k-point on    4 cores,    1 groups
 distr:  one band on    1 cores,    4 groups
 using from now: INCAR     
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 POSCAR found type information on POSCAR  H 
 POSCAR found :  1 types and       2 ions
 scaLAPACK will be used
 LDA part: xc-table for Pade appr. of Perdew
 POSCAR, INCAR and KPOINTS ok, starting setup
 FFT: planning ...
 WAVECAR not read
 entering main loop
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1     0.330307833686E+01    0.33031E+01   -0.36026E+02    32   0.737E+01
DAV:   2    -0.473855047208E+01   -0.80416E+01   -0.80416E+01    32   0.253E+01
DAV:   3    -0.523992505854E+01   -0.50137E+00   -0.50137E+00    40   0.977E+00
DAV:   4    -0.524239736218E+01   -0.24723E-02   -0.24723E-02    32   0.677E-01
DAV:   5    -0.524242226125E+01   -0.24899E-04   -0.24899E-04    32   0.648E-02    0.455E+00
DAV:   6    -0.656955046096E+01   -0.13271E+01   -0.55591E+00    32   0.924E+00    0.337E+00
DAV:   7    -0.655514804124E+01    0.14402E-01   -0.10946E+00    32   0.371E+00    0.163E+00
DAV:   8    -0.660675599031E+01   -0.51608E-01   -0.24393E-01    32   0.135E+00    0.950E-01
DAV:   9    -0.674177913766E+01   -0.13502E+00   -0.19305E-01    32   0.123E+00    0.399E-01
[bcgong@localhost grid144]$
```

```console
[bcgong@localhost grid144]$ grep -E "NELECT|dimension x,y,z|aborting loop|Elapsed time" AB/OUTCAR
   dimension x,y,z NGX =    72 NGY =   72 NGZ =   72
   dimension x,y,z NGXF=   144 NGYF=  144 NGZF=  144
   dimension x,y,z NGX =    70 NGY =   70 NGZ =   70
   NELECT =       2.0000    total number of electrons
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       37.584
[bcgong@localhost grid144]$
```

```text
编写 Python 3 命令行程序 build_delta_chgcar.py，依赖 NumPy。输入 --ab、--a、--b 是 VASP CHGCAR 或 gzip 压缩 CHGCAR.gz；解析 POSCAR 风格结构头，支持元素/原子数、Direct/Cartesian 坐标以及可选 Selective dynamics。读取结构后的第一块 nx ny nz 总电子密度，恰好 N=nx*ny*nz 个有限值，x 最快；不混入 augmentation 或第二块磁化密度。检查三项晶胞矩阵相同、网格相同、AB 原子数等于 A+B，A/B 元素与坐标保持 AB 中原位。D 是体积缩放的 VASP 存储值，n=D/V，单位 e/Å³；逐点计算 D_AB-D_A-D_B，输出仅用于 VESTA 的单块 CHGCAR_DELTA，保留 AB 结构头。分别计算各输入 ΣD/N、差分全胞/正值/负值积分、极值及源文件 SHA256，写 JSON。若本例差分全胞残差大于 1e-6 e 则报错；打印科学计数法残差，不能把舍入成零称作精确证明。所有目标文件写入前检查存在性，拒绝覆盖。命令参数为 --output 与 --summary。不得归一化到期望电子数或画替代图。GUI 使用 VESTA 打开输出并核对单位：±0.03 e/Å³ 等于 ±30 的原始存储值；本次 VESTA 场景将其转换为 ±0.00444555 e/bohr³。保存场景，导出实际等值面 PNG；记录配色、阈值与显示范围。
```

```bash
python3 -m pip install numpy
python3 -B scripts/build_delta_chgcar.py --ab ../h2-delta-charge/AB/CHGCAR.gz --a ../h2-delta-charge/A/CHGCAR.gz --b ../h2-delta-charge/B/CHGCAR.gz --output new-h2/CHGCAR_DELTA --summary new-h2/summary.json
```

```text
grid: 144 144 144
volume: 1000.000000 Å^3
integrals A/B/AB: 1.000000001 / 1.000000001 / 2.000000003 e
delta integral: 4.363e-10 e
delta rho min/max: -0.055559 / 0.802964 e/Å^3
```

```text
固定 AB 几何 → 原位保留 A、B → 匹配参数的三份 SCF
                                  ↓
                        CHGCAR 结构、网格、电子数
                                  ↓
                       第一密度块 AB − A − B
                                  ↓
                    VESTA 正负等值面 + 完整网格积分
```

</details>


<details>
<summary>integrate_planar.py完整源码</summary>

```python
#!/usr/bin/env python3
"""Integrate matched frozen-fragment CHGCAR first blocks along the a×b normal.
Dependencies: numpy, sibling build_delta_chgcar.py. Input files are read only.
NELECT additivity is checked; fragment neutrality/charge states are not inferred.
Establish each charge state from its own input/OUTCAR and valence protocol.
Boundaries refer to physical normal distance in Angstrom; piecewise linear
interpolation of periodic plane values defines the cumulative integral.
"""
import argparse, csv, json
from pathlib import Path
import numpy as np
from build_delta_chgcar import read_chgcar, check_same_cell_and_grid

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for label in ('ab','a','b'): p.add_argument('--'+label,type=Path,required=True)
    p.add_argument('--nelect',type=float,nargs=3,required=True,metavar=('AB','A','B'))
    p.add_argument('--boundaries',type=float,nargs='+',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    if a.output_dir.exists(): raise FileExistsError('Choose a new output directory')
    if not all(np.isfinite(a.nelect)) or abs(a.nelect[0]-sum(a.nelect[1:]))>1e-8:
        raise ValueError('Additive fragment electron counts are required; fragment charge states must be established from the input protocol')
    data={k:read_chgcar(getattr(a,k.lower())) for k in ('AB','A','B')}
    check_same_cell_and_grid(data)
    for k,n in zip(('AB','A','B'),a.nelect):
        if not np.isfinite(data[k]['values']).all(): raise ValueError('Nonfinite density')
        integral=float(data[k]['values'].mean())
        if abs(integral-n)>1e-5: raise ValueError(k+': integral differs from stated NELECT')
    ref=data['AB'];cell=ref['cell'];volume=ref['volume_A3']
    area=float(np.linalg.norm(np.cross(cell[0],cell[1])));height=volume/area
    nx,ny,nz=ref['dimensions'];dz=height/nz
    edges=np.array(a.boundaries,dtype=float)
    if len(edges)<2 or not np.isfinite(edges).all() or np.any(np.diff(edges)<=0):
        raise ValueError('Need at least two ordered finite boundaries')
    if edges[0]<0 or edges[-1]>height+1e-8: raise ValueError('Boundary outside cell')
    delta=ref['values']-data['A']['values']-data['B']['values']
    density=delta.reshape(nz,ny,nx).mean(axis=(1,2))/volume
    z=np.arange(nz+1)*dz;plane=np.r_[density,density[0]];linear=area*plane
    cumulative=np.r_[0.,np.cumsum(.5*(linear[:-1]+linear[1:])*dz)]
    def at(x):
        if abs(x-height)<1e-8: return float(cumulative[-1])
        k=int(np.floor(x/dz));h=x-z[k]
        return float(cumulative[k]+linear[k]*h+.5*(linear[k+1]-linear[k])*h*h/dz)
    rows=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        number=at(hi)-at(lo)
        rows.append(dict(lo_A=float(lo),hi_A=float(hi),delta_e=number,
                         delta_e_per_A2=number/area,delta_e_per_cm2=number/area*1e16))
    residual=float(delta.mean())
    if abs(residual)>1e-6: raise ValueError('Difference electron count does not close')
    if abs(cumulative[-1]-residual)>1e-10: raise ValueError('Periodic integral mismatch')
    summary=dict(definition='delta_n=n_AB-n_A-n_B; positive means electron gain',
      input_integrals_e={k:float(v['values'].mean()) for k,v in data.items()},
      area_A2=area,height_A=height,volume_A3=volume,grid=list(ref['dimensions']),
      full_cell_residual_e=residual,cumulative_endpoint_e=float(cumulative[-1]),
      positive_3d_e=float(np.maximum(delta,0).mean()),negative_3d_e=float(np.minimum(delta,0).mean()),
      boundaries_A=edges.tolist(),regions=rows,
      source_sha256_uncompressed={k:v['sha256_uncompressed'] for k,v in data.items()},
      quadrature='periodic piecewise linear plane density; exact partial-segment integral',
      scope='spatial redistribution relative to frozen fragments; not mobile carrier density')
    a.output_dir.mkdir(parents=True)
    with (a.output_dir/'planar.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['z_A','delta_n_e_A3','linear_e_A','cumulative_e'])
        w.writerows(zip(z,plane,linear,cumulative))
    with (a.output_dir/'regions.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'area={area:.9f} A^2; height={height:.9f} A; grid={nx} {ny} {nz}')
    print(f'full-cell residual={residual:.12e} e; cumulative endpoint={cumulative[-1]:.12e} e')
    for r in rows: print(f'{r["lo_A"]:.6f}:{r["hi_A"]:.6f} A: delta_e={r["delta_e"]:+.12e}; area_density={r["delta_e_per_cm2"]:+.12e} e/cm^2')
    print(f'positive 3D redistribution={summary["positive_3d_e"]:.10f} e')

if __name__=='__main__': main()
```

</details>


平面积分所导入的 `build_delta_chgcar.py` 与上面的转换脚本逐字一致，因此完整源码只列一次。两份可下载路径分别服务于 [VESTA转换](/Atlas/examples/charge-vesta/scripts/build_delta_chgcar.py) 和 [平面积分模块](/Atlas/examples/charge-planar/build_delta_chgcar.py)，函数与单位约定相同。

<details>
<summary>法向差分密度与累计积分的完整gnuplot源码</summary>

```gnuplot
# Native gnuplot replay of the existing H2 plane-average/integration table.
# CSV: z_A,delta_n_e_A3,linear_e_A,cumulative_e. No smoothing or fitting.
# Put this script in public/examples/charge-literature and run gnuplot.
if (!exists("datafile")) datafile = "../charge-planar/h2-half-spaces/planar.csv"
if (!exists("prefix")) prefix = "h2-planar-and-cumulative"
set datafile separator comma
set encoding utf8
set border 3 back lc rgb "#555555" lw 1
set tics nomirror out scale 0.55
set style fill solid 0.35 noborder
set xrange [0:10]
set key at graph 0.98,0.95 right top horizontal font ",10"
set grid ytics lc rgb "#dddddd" lw 0.5
set format y "%.2f"
set arrow 1 from 4.63, graph 0 to 4.63, graph 1 nohead dt 3 lw 1 lc rgb "#777777" back
set arrow 2 from 5.37, graph 0 to 5.37, graph 1 nohead dt 3 lw 1 lc rgb "#777777" back
set arrow 3 from 5.0, graph 0 to 5.0, graph 1 nohead dt 2 lw 1 lc rgb "#444444" back
set arrow 4 from graph 0, first 0 to graph 1, first 0 nohead lw 0.8 lc rgb "#333333" back
# Three exports use the same measured table and plotting settings.
do for [export_index=1:3] {
 if (export_index==1) { set terminal svg size 1000,700 font "Liberation Sans,15"; set output prefix.".svg" }
 if (export_index==2) { set terminal pdfcairo enhanced color size 7.0in,4.9in font "Liberation Sans,10.5"; set output prefix.".pdf" }
 if (export_index==3) { set terminal pngcairo size 1000,700 font "Liberation Sans,15"; set output prefix.".png" }
 set multiplot layout 2,1 margins 0.13,0.97,0.12,0.86 spacing 0.10 title "Frozen H₂: planar redistribution and cumulative integral" font ",17"
 set ylabel "Area-integrated Δn (e/Å)" offset 0.4,0
 set format x ""
 set xlabel ""
 set label 1 "(a) S × plane-average Δn" at graph 0.02,0.90 front font ",11"
 plot datafile every ::1 using 1:3 with filledcurves above y1=0 lc rgb "#d8a126" title "electron gain", \
      datafile every ::1 using 1:3 with filledcurves below y1=0 lc rgb "#31a9bd" title "electron depletion", \
      datafile every ::1 using 1:3 with lines lw 1.8 lc rgb "#333333" notitle
 unset label 1
 set key off
 set format x "%g"
 set xlabel "z (Å); dotted: H at 4.63 / 5.37 Å, dashed: half-cell boundary at 5 Å"
 set ylabel "T(z) (e)" offset 0.4,0
 set label 2 "(b) Integral from cell origin to z" at graph 0.02,0.90 front font ",11"
 plot datafile every ::1 using 1:4 with lines lw 2 lc rgb "#205a83" notitle
 unset label 2
 unset multiplot
 unset output
 set key at graph 0.98,0.95 right top horizontal font ",10"
}
```

</details>


<details>
<summary>边界与一维正区复核的完整源码</summary>

```python
#!/usr/bin/env python3
"""Check the archived H2 CSV and save exact slider reference values.

This is numerical post-processing only; it does not run DFT or produce a plot.
Supply archived planar.csv and summary.json; choose a new output directory.
"""

import argparse
import bisect
import csv
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--planar', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    DATA = args.output_dir
    require(not DATA.exists(), 'Choose a new output directory')
    with args.planar.open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(
            reader.fieldnames
            == ["z_A", "delta_n_e_A3", "linear_e_A", "cumulative_e"],
            "Unexpected CSV columns",
        )
        rows = [{key: float(value) for key, value in row.items()} for row in reader]
    summary = json.loads(args.summary.read_text())
    require(all(math.isfinite(v) for r in rows for v in r.values()), "Non-finite data")
    z = [r["z_A"] for r in rows]
    line = [r["linear_e_A"] for r in rows]
    stored = [r["cumulative_e"] for r in rows]
    require(len(rows) == summary["grid"][2] + 1, "Missing periodic endpoint")
    require(all(a < b for a, b in zip(z, z[1:])), "Coordinate order")
    require(abs(z[0]) < 1e-12, "Nonzero integral origin")
    require(abs(z[-1] - summary["height_A"]) < 1e-12, "Cell height mismatch")
    require(abs(line[-1] - line[0]) < 1e-12, "Periodic endpoint mismatch")
    area_error = max(
        abs(r["linear_e_A"] - summary["area_A2"] * r["delta_n_e_A3"])
        for r in rows
    )
    require(area_error < 1e-12, "Area factor or units mismatch")

    increments = [
        0.5 * (a + b) * (zb - za)
        for za, zb, a, b in zip(z, z[1:], line, line[1:])
    ]
    cumulative = [0.0]
    for increment in increments:
        cumulative.append(cumulative[-1] + increment)
    cumulative_error = max(abs(a - b) for a, b in zip(cumulative, stored))
    require(cumulative_error < 1e-12, "Stored cumulative values mismatch")
    total = cumulative[-1]
    require(abs(total - summary["full_cell_residual_e"]) < 1e-12, "Total mismatch")

    def integral_at(boundary):
        require(z[0] - 1e-12 <= boundary <= z[-1] + 1e-12, "Boundary outside cell")
        if abs(boundary - z[0]) < 1e-12:
            return 0.0
        if abs(boundary - z[-1]) < 1e-12:
            return total
        boundary = min(max(boundary, z[0]), z[-1])
        if boundary == z[-1]:
            return total
        k = max(0, bisect.bisect_right(z, boundary) - 1)
        h = boundary - z[k]
        width = z[k + 1] - z[k]
        # The line density is piecewise linear, so its partial integral is quadratic.
        return (
            cumulative[k]
            + line[k] * h
            + 0.5 * (line[k + 1] - line[k]) * h * h / width
        )

    for region in summary["regions"]:
        obtained = integral_at(region["hi_A"]) - integral_at(region["lo_A"])
        require(abs(obtained - region["delta_e"]) < 1e-12, "Archived region mismatch")

    positive_parts = []
    for width, a, b in zip((b - a for a, b in zip(z, z[1:])), line, line[1:]):
        if a >= 0 and b >= 0:
            positive_parts.append(0.5 * (a + b) * width)
        elif a <= 0 and b <= 0:
            positive_parts.append(0.0)
        else:
            zero_fraction = -a / (b - a)
            positive_width = width * (zero_fraction if a > 0 else 1 - zero_fraction)
            positive_parts.append(0.5 * max(a, b) * positive_width)
    positive_1d = math.fsum(positive_parts)
    negative_1d = total - positive_1d
    require(positive_1d <= summary["positive_3d_e"] + 1e-12, "Invalid 1D/3D ordering")

    cuts = [0.0, 4.0, 4.63, 4.9, 4.95, 5.0, 5.05, 5.1, 5.37, 6.0, 10.0]
    fixtures = []
    for cut in cuts:
        left = integral_at(cut)
        right = total - left
        require(abs(left + right - total) < 1e-12, "Complement mismatch")
        fixtures.append(
            {"boundary_A": cut, "left_delta_e": left, "right_delta_e": right}
        )
    DATA.mkdir(parents=True)
    with (DATA / "boundary-reference.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fixtures[0]))
        writer.writeheader()
        writer.writerows(fixtures)

    peak = max(rows, key=lambda r: r["linear_e_A"])
    trough = min(rows, key=lambda r: r["linear_e_A"])
    result = {
        "status": "pass",
        "method": "exact integration of each piecewise-linear line-density segment",
        "samples_including_periodic_endpoint": len(rows),
        "area_factor_max_error_e_A": area_error,
        "cumulative_max_error_e": cumulative_error,
        "full_cell_delta_e": total,
        "positive_area_of_1d_profile_e": positive_1d,
        "negative_area_of_1d_profile_e": negative_1d,
        "positive_voxel_integral_3d_e": summary["positive_3d_e"],
        "negative_voxel_integral_3d_e": summary["negative_3d_e"],
        "profile_peak": {"z_A": peak["z_A"], "linear_e_A": peak["linear_e_A"]},
        "profile_trough": {"z_A": trough["z_A"], "linear_e_A": trough["linear_e_A"]},
        "boundary_fixtures": fixtures,
        "input_files": [str(args.planar), str(args.summary)],
        "plot_created": False,
        "raw_chgcar_reprocessed": False,
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (DATA / "boundary-reference.json").write_text(encoded)
    print(f"samples={len(rows)}; full-cell residual={total:.12e} e")
    print(f"positive 1D={positive_1d:.10f} e; positive 3D={summary['positive_3d_e']:.10f} e")
    for fixture in fixtures:
        if fixture['boundary_A'] in (4.9, 5.0, 5.1):
            print(f"boundary={fixture['boundary_A']:.2f} A: left={fixture['left_delta_e']:+.12e} e; right={fixture['right_delta_e']:+.12e} e")
    print(f"checks=pass; wrote {DATA}/boundary-reference.csv and boundary-reference.json")


if __name__ == "__main__":
    main()
```

</details>
