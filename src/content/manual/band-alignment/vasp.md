SnSe₂带边和Sr₂N费米能能否比较，取决于能量零点。两份孤立SCF的EF不能直接相减；先把每个能级减去它自己的表面真空势，再比较共同参照下的位置。本例从六原子SnSe₂/Sr₂N结构拆层，保留共同面内晶胞与内部几何，只平移至居中位置；结果是接触前的冻结层参照。

[Choudhary等，arXiv:2004.03025v2, Fig. 2(a–d)](https://arxiv.org/abs/2004.03025v2)给出一个完整比较：(a,b)是孤立MoS₂、WSe₂的DOS，(c)是显式双层的投影DOS，前三幅各自以所在体系的EF归零，主要检查层投影的形状、带隙和杂化是否变化；(d)另以各自真空为共同能量参考画带边。Fig. 5(b)将MoS₂/WSe₂的两个VBM/CBM放在同一真空轴上，才显示它们的相对错位。各自EF归零的DOS和真空参照图回答不同问题，不能把前两幅DOS横轴直接叠在一起读带边偏移。本例Sr₂N有费米能交叉，比较的是半导体带边与金属EF，不能套半导体—半导体type-I/II/III分类。[金属/Ca₂N/MoS₂原文Fig. 3](https://doi.org/10.1039/D4CP04577G)比较Ca₂N/MoS₂的Geometry A、B：横轴为 $E-E_{\mathrm F}$，MoS₂投影DOS按整个异质双层的总原子数归一，插图标出B中Mo骨架的畸变。原文§2.1采用Löwdin投影与相同0.1 eV高斯展宽，再把谱变化和结构畸变一起讨论；不能将两种超胞的DOS峰高直接当作载流子多少。

[下载两层输入、完整原始输出与源码](/Atlas/examples/interface-magnet-band-alignment/example-pack.tar.gz)，进入 `example-pack`。准备结构见 [异质结构建模](/Atlas/m/heterostructure-modeling/vasp/)，固定结构自洽见 [SCF](/Atlas/m/scf/vasp/)，势参考见 [静电势](/Atlas/m/electrostatic-potential/vasp/)。

## 原位几何与相向表面

```text
[bcgong@localhost vasp]$ mkdir -p band_alignment/snse2 band_alignment/sr2n
[bcgong@localhost vasp]$ cd band_alignment
[bcgong@localhost band_alignment]$ cp <工作目录>/POSCAR POSCAR.reference
[bcgong@localhost band_alignment]$ cp <工作目录>/POTCAR POTCAR.reference
[bcgong@localhost band_alignment]$ cp POSCAR.reference snse2/POSCAR
[bcgong@localhost band_alignment]$ vi snse2/POSCAR
[bcgong@localhost band_alignment]$ cp POSCAR.reference sr2n/POSCAR
[bcgong@localhost band_alignment]$ vi sr2n/POSCAR
```

```text
[bcgong@localhost band_alignment]$ cat snse2/POSCAR
snse2 frozen isolated layer in common cell
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
Sn Se
1 2
Direct
 0.0000000000000000 0.0000000000000000 0.5036394637538087
 0.6666666670000012 0.3333333329999988 0.5421918198149582
 0.3333333329999988 0.6666666670000012 0.4578081801850417
[bcgong@localhost band_alignment]$ cat sr2n/POSCAR
sr2n frozen isolated layer in common cell
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
N Sr
1 2
Direct
 0.6666666670000012 0.3333333329999988 0.4948574488156312
 0.0000000000000000 -0.0000000000000000 0.5343094980558125
 0.3333333329999988 0.6666666670000012 0.4656905019441875
```

```text
[bcgong@localhost band_alignment]$ python analyze_alignment.py --geometry-only
snse2: 3 atoms; rigid dz=-0.090381737230 fractional; thickness=3.324900015 A; empty height=36.077287778 A
sr2n: 3 atoms; rigid dz=0.040884040820 fractional; thickness=2.703738571 A; empty height=36.698449223 A
Common cell, INCAR and KPOINTS: identical
```

原结构元素Sn Se N Sr、计数1 2 1 2；SnSe₂前三个原子，Sr₂N后三个。两份面内边长3.9501156207 Å，法向39.4021877938 Å。只沿z作整体平移，各层厚度与面内坐标保持；它们不是独立弛豫的自由单层。

SnSe₂原来在上，面向界面的是lower-z；Sr₂N在下，面向界面的是upper-z。居中没有翻转表面，也没有人为恢复上下对称。本站另一 [SnSe₂功函数算例](/Atlas/m/workfunction/vasp/) 的面内边长3.8464052688 Å，读数不能直接混入本例。

POTCAR按POSCAR元素顺序拆分完整数据集，不公开许可正文。SnSe₂总价电子26，Sr₂N25；原拆分输出保留在执行记录。

## 同一协议求两份孤立SCF

```text
[bcgong@localhost band_alignment]$ vi snse2/INCAR
[bcgong@localhost band_alignment]$ cp snse2/INCAR sr2n/INCAR
[bcgong@localhost band_alignment]$ cat snse2/INCAR
SYSTEM = isolated frozen layer vacuum reference
ISTART = 0
ICHARG = 2
ISPIN = 1
ENCUT = 520
GGA = PE
PREC = Accurate
EDIFF = 1E-7
NELM = 100
ALGO = Normal
ISMEAR = 0
SIGMA = 0.05
IVDW = 11
LREAL = .FALSE.
LASPH = .TRUE.
LORBIT = 11
LMAXMIX = 4
NCORE = 2
NSW = 0
IBRION = -1
LDIPOL = .TRUE.
IDIPOL = 3
DIPOL = 0.5 0.5 0.5
LWAVE = .FALSE.
LCHARG = .TRUE.
LVHAR = .TRUE.
[bcgong@localhost band_alignment]$ cat snse2/KPOINTS
Common-cell vacuum-reference mesh
0
Gamma
21 21 1
0 0 0
```

```text
[bcgong@localhost band_alignment]$ cat snse2/run.slurm
#!/bin/bash
#SBATCH --job-name=align-snse2
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
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

```text
[bcgong@localhost band_alignment]$ cd snse2
[bcgong@localhost snse2]$ squeue -o "%.18i %.14j %.10u %.2t %.6C %.10M"
             JOBID           NAME       USER ST   CPUS       TIME
             18180   srnsnse-ph64     bcgong  R     16    2:46:16
[bcgong@localhost snse2]$ sbatch run.slurm
Submitted batch job 18198
```

```text
[bcgong@localhost snse2]$ tail -n 7 OSZICAR
DAV:  20    -0.116412516655E+02   -0.37855E-05   -0.59417E-08  1960   0.601E-04    0.184E-04
DAV:  21    -0.116412522450E+02   -0.57954E-06   -0.35421E-09  2236   0.228E-04    0.113E-04
DAV:  22    -0.116412531128E+02   -0.86775E-06   -0.76089E-09  1972   0.276E-04    0.720E-05
DAV:  23    -0.116412533720E+02   -0.25926E-06   -0.60865E-10  1992   0.129E-04    0.275E-05
DAV:  24    -0.116412535934E+02   -0.22140E-06   -0.12387E-09  1776   0.115E-04    0.430E-05
DAV:  25    -0.116412536906E+02   -0.97141E-07   -0.93296E-11  1972   0.754E-05
   1 F= -.12025617E+02 E0= -.12025616E+02  d E =-.313107E-06
[bcgong@localhost snse2]$ grep -E "EDIFF is reached|E-fermi|Elapsed time" OUTCAR
E-fermi :  -4.1160     XC(G=0):  -1.7219     alpha+bet : -1.4843
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):      160.816
```

```text
[bcgong@localhost band_alignment]$ cd sr2n
[bcgong@localhost sr2n]$ sbatch run.slurm
Submitted batch job 18199
[bcgong@localhost sr2n]$ tail -n 7 OSZICAR
DAV:  24    -0.125492168021E+02   -0.75953E-06   -0.36601E-08  1472   0.529E-04    0.331E-04
DAV:  25    -0.125492176987E+02   -0.89652E-06   -0.15999E-08  1392   0.379E-04    0.896E-05
DAV:  26    -0.125492184397E+02   -0.74100E-06   -0.16093E-08  1392   0.249E-04    0.313E-04
DAV:  27    -0.125492186592E+02   -0.21954E-06   -0.19763E-09  1256   0.151E-04    0.124E-04
DAV:  28    -0.125492187704E+02   -0.11117E-06   -0.74655E-10  1192   0.975E-05    0.613E-05
DAV:  29    -0.125492188144E+02   -0.44009E-07    0.19619E-11  1160   0.647E-05
   1 F= -.12799026E+02 E0= -.12797556E+02  d E =-.294088E-02
[bcgong@localhost sr2n]$ grep -E "EDIFF is reached|E-fermi|Elapsed time" OUTCAR
E-fermi :  -2.1582     XC(G=0):  -1.8451     alpha+bet : -1.4302
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):      160.448
```

固定结构、非磁标量PBE+D3零阻尼、无SOC、21×21×1、Gaussian0.05 eV，两项电子参数相同。LDIPOL/IDIPOL=3去除周期偶极误差，真实非对称层两侧仍可以有不同平台。8个MPI进程的脚本中核号来自原现场分配；重跑需遵循新分配。

SnSe₂25次、Sr₂N29次电子迭代达EDIFF，正常结束，均约161秒。LWAVE=.FALSE.的零字节WAVECAR不参与本例分析。LOCPOT、CHGCAR、EIGENVAL与EF来自各自同一次SCF，分别用于势参考、真空密度和能级。

## 采样带边与金属交叉

```text
[bcgong@localhost band_alignment]$ head -n 25 snse2/EIGENVAL
    3    3    1    1
  0.1774800E+03  0.3950116E-09  0.3950116E-09  0.3940219E-08  0.5000000E-15
  1.000000000000000E-004
  CAR 
 isolated frozen layer vacuum reference  
     26     48     20
 
  0.0000000E+00  0.0000000E+00  0.0000000E+00  0.2267574E-02
    1      -25.719623   1.000000
    2      -25.719623   1.000000
    3      -25.690023   1.000000
    4      -25.683909   1.000000
    5      -25.683909   1.000000
    6      -17.722152   1.000000
    7      -16.244606   1.000000
    8      -10.190616   1.000000
    9       -5.596384   1.000000
   10       -5.389675   1.000000
   11       -5.389675   1.000000
   12       -4.254365   0.999954
   13       -4.254365   0.999954
   14       -3.484356   0.000000
   15       -1.566439   0.000000
   16       -0.240462   0.000000
   17       -0.240462   0.000000
```

SnSe₂第六行26 48 20给电子数、不可约k点数与带数。这个VASP5.4.4非磁输出满占据为1，乘2与k权重求和应恢复26电子。Γ点第13/14带间隔不是全网格带隙；遍历48点后导带最低点约(0.4761905,0,0)，间接隙为0.278103 eV。

Sr₂N是25电子、第13和14带的能量范围跨EF=−2.1582 eV，按这组采样的金属处理。单个Γ点占据不能代表全BZ电子数；它也没有供type-I/II分类使用的一对VBM/CBM。

## 每个表面使用自己的真空平台

```text
[bcgong@localhost band_alignment]$ cd snse2
[bcgong@localhost snse2]$ python ../plane_average.py LOCPOT 6:10 29:33
grid = 60 60 588; scalar values = 2116800
normal height = 39.4021880000 A; output = PLANAR_AVERAGE.dat
window 6.00:10.00 A  N=60  mean=1.738360141 eV  std=2.2732e-05 eV  range=6.14621e-05 eV
window 29.00:33.00 A  N=60  mean=1.194360347 eV  std=2.9865e-05 eV  range=6.821e-05 eV
[bcgong@localhost snse2]$ cd ../sr2n
[bcgong@localhost sr2n]$ python ../plane_average.py LOCPOT 6:10 29:33
grid = 60 60 588; scalar values = 2116800
normal height = 39.4021880000 A; output = PLANAR_AVERAGE.dat
window 6.00:10.00 A  N=60  mean=0.872342013 eV  std=5.30532e-06 eV  range=2.4683e-05 eV
window 29.00:33.00 A  N=60  mean=1.273814882 eV  std=4.78083e-06 eV  range=2.37907e-05 eV
```

```text
[bcgong@localhost band_alignment]$ python check_vacuum_density.py
snse2: integrated valence electrons=26.000001016; volume=532.439868220 A^3
  z=6.0:10.0 A: mean density=1.70073e-08; max abs density=2.65706e-08 e/A^3
  z=29.0:33.0 A: mean density=3.87515e-09; max abs density=1.32019e-08 e/A^3
sr2n: integrated valence electrons=25.000000037; volume=532.439868220 A^3
  z=6.0:10.0 A: mean density=6.51407e-08; max abs density=3.89415e-07 e/A^3
  z=29.0:33.0 A: mean density=3.38004e-08; max abs density=3.2739e-07 e/A^3
```

两侧窗口6–10与29–33 Å远离原子和修正跳变，range均小于0.00007 eV，真空平面密度最大绝对值低于3.9×10⁻⁷ e/Å³。CHGCAR平均先除体积，LOCPOT直接平均eV，这两种数组不能套同一单位换算。

SnSe₂两侧平台相差约0.5440 eV，Sr₂N约0.4015 eV；平台平坦和两侧相等是不同条件。本例明确选相向表面。真空高度敏感性需要增加高度后重比较，不能由一个窗口的平坦程度替代。

## 真空参照偏移的实际含义

```text
[bcgong@localhost band_alignment]$ python analyze_alignment.py
snse2: 3 atoms; rigid dz=-0.090381737230 fractional; thickness=3.324900015 A; empty height=36.077287778 A
sr2n: 3 atoms; rigid dz=0.040884040820 fractional; thickness=2.703738571 A; empty height=36.698449223 A
Common cell, INCAR and KPOINTS: identical
snse2: NELECT=26; weighted electrons=25.99999588; NKPTS=48; NBANDS=20; elapsed=160.816 s
  E_F=-4.116000 eV; classification=gapped_on_sampled_mesh; crossing bands=[]
  VBM=-4.254365 eV; CBM=-3.976262 eV; sampled gap=0.278103 eV
  lower_z V_vac=1.738360141 eV; range=6.14621e-05 eV; Phi=5.854360141 eV
  upper_z V_vac=1.194360347 eV; range=6.821e-05 eV; Phi=5.310360347 eV
sr2n: NELECT=25; weighted electrons=24.99999595; NKPTS=48; NBANDS=16; elapsed=160.448 s
  E_F=-2.158200 eV; classification=metallic_on_sampled_mesh; crossing bands=[13, 14]
  band 13: Emin=-3.494134 eV; Emax=-1.288695 eV; occupation=0.000000:1.000000
  band 14: Emin=-2.418358 eV; Emax=-0.876122 eV; occupation=0.000000:1.000000
  lower_z V_vac=0.872342013 eV; range=2.4683e-05 eV; Phi=3.030542013 eV
  upper_z V_vac=1.273814882 eV; range=2.37907e-05 eV; Phi=3.432014882 eV
Facing isolated references: CBM(SnSe2)-E_F(Sr2N)=-2.282607 eV; E_F(Sr2N)-VBM(SnSe2)=2.560710 eV
```

| 冻结孤立层表面 | $V_{\mathrm{vac}}$ / eV | $E-V_{\mathrm{vac}}$ / eV |
| --- | ---: | --- |
| SnSe₂ lower-z | 1.738360141 | VBM −5.992725141；CBM −5.714622141 |
| Sr₂N upper-z | 1.273814882 | EF −3.432014882 |

$\mathrm{CBM}(\mathrm{SnSe}_2)-E_{\mathrm F}(\mathrm{Sr}_2\mathrm N)=-2.282607260\,\mathrm{eV}$，是这组冻结孤立层真空参照下的偏移。接触后共用EF、电荷重排、界面偶极和杂化会重构这些位置；这个负偏移不能直接作为已算出的接触势垒或转移电子数。它也不能和各自以EF归零的DOS横轴混用。

要读实际界面的电子/空穴势垒，应在完整接触体系中找到仍可识别的SnSe₂层带边与共同EF，检查杂化/隙内态；平面势峰相对EF给的隧穿势垒属于另一种量。参考 [金属/Ca₂N/MoS₂论文Sec. 2.2、Fig. 3](https://doi.org/10.1039/D4CP04577G)，把层投影谱、电荷与几何一起检查。

选相向表面是一个实际数值选择。保留同一套原始带边和EF，仅更换用于取差的表面平台，所得CBM−EF为：

| SnSe₂所选表面 | Sr₂N所选表面 | 真空参照CBM−EF / eV | 对应关系 |
| --- | --- | ---: | --- |
| lower-z | upper-z | −2.282607 | 原结构的两个相向表面 |
| upper-z | upper-z | −1.738607 | 改用了SnSe₂背面 |
| lower-z | lower-z | −2.684080 | 改用了Sr₂N背面 |

三个偏移由[四表面原始表](/Atlas/examples/interface-magnet-band-alignment/band-edges-vacuum-referenced.csv)直接相减得到。更换SnSe₂一侧使读数移动约0.5440 eV，更换Sr₂N一侧移动约0.4015 eV；不是原子突然接触后改变了能带，而是选了不同表面的真空零点。论文中画一条共同真空线时，每个材料用哪个朝向、哪个终止必须随图说明。

[Choudhary等Fig. 2(d)](https://arxiv.org/abs/2004.03025v2)的纵轴明确写能量相对真空/eV，横向按WSe₂、MoS₂分别排列：绿色块的下边界给CBM，红色块的上边界给VBM，两者之间是各自带隙，蓝色虚线另标水氧化/还原参照。该面板读的是带边的位置；(a–c)的彩色DOS曲线则按元素分解，横轴能量/eV各以所在体系EF归零。颜色在这两类面板中承担不同含义，需要分别读图例。本站采用(d)的共同真空纵轴与按材料并列的方式，用短线和浅色带隙区显示自己CSV中的采样带边，再单独标金属EF；蓝、棕分别区分两层，虚线真空为0。每条能级线都由所选表面的真空平台取差得到。

![冻结SnSe₂相向面带边与Sr₂N相向面费米能，统一真空为零](/Atlas/examples/enrichment-20261003/charge/frozen-facing-alignment.svg)

图中SnSe₂的两个短线围出采样带隙，Sr₂N只标金属EF；箭头的有符号差定义为SnSe₂ CBM减Sr₂N EF。原始孤立计算各有自己的化学势，真空对齐只提供接触前能级参照，并没有让这两个EF达到平衡。两份居中过的LOCPOT可以分别读各自真空，若继续逐点CDD相减，则必须恢复完整AB中的原位片段。

[gnuplot源码](/Atlas/examples/enrichment-20261003/charge/frozen-facing-alignment.gnuplot)直接读取上述原始CSV，按材料与表面名选择带边和EF；下载两份文件后运行 `gnuplot -e "datafile='band-edges-vacuum-referenced.csv'" frozen-facing-alignment.gnuplot` 可导出SVG、PDF、PNG，没有插值、拟合或给金属补造带边。

## 结果表与接触后的转移分析

表格导出只读已验证摘要，按表面保留平台范围、带边和EF。这个写码需求可复现所列两张表：

```text
请编写一个 Python 3 标准库脚本，读取同目录的 alignment-summary.json。文件内含 SnSe2 与 Sr2N 两层的 sampled-mesh 分类、能带边、E_F、两侧 LOCPOT 真空窗口，以及已指定的 interface_facing_isolated_reference。输出 band-edges-vacuum-referenced.csv，每种材料和表面各一行，至少含材料、表面、窗口范围、真空势均值、窗口势差、E_F−Vvac、VBM−Vvac、CBM−Vvac、采样带隙和金属/半导体分类；金属的 VBM/CBM 与带隙字段留空，不要伪造带边。另输出 facing-surface-offsets.csv，逐行写出 SnSe2 lower-z 与 Sr2N upper-z 的 CBM−EF、EF−VBM 值及“冻结孤立层参考，不是界面势垒”的范围说明。数值保持 eV，CSV 用 UTF-8，写入脚本所在目录，固定列序，确保重跑可复现。若缺少任一预期字段或 JSON 无法解析，应以清楚错误退出；不要画图、填补缺失数据或推断接触后的性质。
```

[analyze_alignment.py](/Atlas/examples/interface-magnet-band-alignment/analyze_alignment.py)、[check_vacuum_density.py](/Atlas/examples/interface-magnet-band-alignment/check_vacuum_density.py)、[plane_average.py](/Atlas/examples/interface-magnet-band-alignment/plane_average.py)以及[export_alignment_tables.py](/Atlas/examples/interface-magnet-band-alignment/export_alignment_tables.py)在文末给完整源码。它们使用Python标准库；从原始LOCPOT开始时，先分别在snse2、sr2n中执行前面平台命令，再回根目录运行：

```bash
python3 analyze_alignment.py
python3 check_vacuum_density.py
python3 export_alignment_tables.py
```

复现真空对齐图时，直接读取下面的 `band-edges-vacuum-referenced.csv`，以真空为0，用gnuplot画SnSe₂的VBM/CBM短线与Sr₂N的EF短线，并标明所选表面；本例金属层保持EF标记，不给它补一对不存在的半导体带边。若进一步比较接触前后PDOS，按原文Fig. 2(a–c)先统一投影、展宽与归一化，再将完整接触的层谱和冻结层谱并列；这一步连接 [DOS](/Atlas/m/dos/vasp/)，当前孤立层能级表仍只作接触前参考。

输出四个表面读数和两个相向偏移：[真空参照表](/Atlas/examples/interface-magnet-band-alignment/band-edges-vacuum-referenced.csv) · [偏移表](/Atlas/examples/interface-magnet-band-alignment/facing-surface-offsets.csv)。

继续 [CDD](/Atlas/m/delta-charge/vasp/) 时，完整AB与冻结A/B必须留在同一坐标，不能把这里居中过的层直接逐点相减。平面平均$\overline{\Delta n}$乘真实面积再累计，给指定边界的层净增电子数；[Bader](/Atlas/m/bader/vasp/)给盆地加总，两者各有分区。转移面积密度反映静态重排，导带/费米面占据才说明自由载流子。将它们与接触后的层投影电子结构对应，才能讨论界面给哪组能态增减电子。


## 完整源码与执行记录

<details>
<summary>export_alignment_tables.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Export vacuum-referenced band-edge and facing-surface tables from analysis JSON.

Standard library only. Run from this directory after analyze_alignment.py.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "alignment-summary.json"


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    summary = json.loads(SOURCE.read_text(encoding="utf-8"))
    layer_rows: list[dict[str, object]] = []
    for material, layer in summary["layers"].items():
        extrema = {
            "vbm_minus_vacuum_eV": "",
            "cbm_minus_vacuum_eV": "",
        }
        for window in layer["windows"]:
            layer_rows.append({
                "material": material,
                "surface": window["side"],
                "vacuum_window_A": f'{window["lo_A"]:.1f}:{window["hi_A"]:.1f}',
                "vacuum_mean_eV": f'{window["mean_eV"]:.9f}',
                "vacuum_range_eV": f'{window["range_eV"]:.9g}',
                "fermi_minus_vacuum_eV": f'{window["fermi_minus_vacuum_eV"]:.9f}',
                "vbm_minus_vacuum_eV": f'{window.get("vbm_minus_vacuum_eV", ""):.9f}' if "vbm_minus_vacuum_eV" in window else "",
                "cbm_minus_vacuum_eV": f'{window.get("cbm_minus_vacuum_eV", ""):.9f}' if "cbm_minus_vacuum_eV" in window else "",
                "sampled_gap_eV": f'{layer["gap_eV"]:.9f}' if "gap_eV" in layer else "",
                "classification": layer["classification"],
            })
    write_csv(ROOT / "band-edges-vacuum-referenced.csv", [
        "material", "surface", "vacuum_window_A", "vacuum_mean_eV",
        "vacuum_range_eV", "fermi_minus_vacuum_eV",
        "vbm_minus_vacuum_eV", "cbm_minus_vacuum_eV",
        "sampled_gap_eV", "classification",
    ], layer_rows)

    facing = summary["interface_facing_isolated_reference"]
    offsets = [
        {
            "quantity": "CBM(SnSe2, lower-z) - EF(Sr2N, upper-z)",
            "value_eV": f'{facing["cbm_minus_metal_fermi_eV"]:.9f}',
            "meaning": "vacuum-referenced isolated-layer edge offset",
            "scope": facing["scope"],
        },
        {
            "quantity": "EF(Sr2N, upper-z) - VBM(SnSe2, lower-z)",
            "value_eV": f'{facing["metal_fermi_minus_vbm_eV"]:.9f}',
            "meaning": "vacuum-referenced isolated-layer edge offset",
            "scope": facing["scope"],
        },
    ]
    write_csv(ROOT / "facing-surface-offsets.csv", [
        "quantity", "value_eV", "meaning", "scope",
    ], offsets)

    print(f"Wrote {len(layer_rows)} surface rows to band-edges-vacuum-referenced.csv")
    print(f"Wrote {len(offsets)} facing offsets to facing-surface-offsets.csv")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>analyze_alignment.py 的完整源码</summary>

```python
from __future__ import print_function
import os,re,json,math,hashlib

def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def poscar(p):
 l=open(p).read().splitlines(); s=float(l[1]); cell=[[s*float(x) for x in r.split()] for r in l[2:5]]
 if s<=0 or not l[7].lower().startswith('d'): raise ValueError('Expected positive-scale direct-coordinate POSCAR')
 species=l[5].split(); counts=list(map(int,l[6].split())); n=sum(counts)
 xyz=[list(map(float,r.split()[:3])) for r in l[8:8+n]]
 if len(xyz)!=n: raise ValueError('Truncated POSCAR')
 return cell,species,counts,xyz

def geometry():
 ref,sp,n,r=poscar('POSCAR.reference')
 if sp!=['Sn','Se','N','Sr'] or n!=[1,2,1,2]: raise ValueError('Reference species changed')
 out={}
 for name,offset,expect in [('snse2',0,['Sn','Se']),('sr2n',3,['N','Sr'])]:
  cell,species,counts,xyz=poscar(name+'/POSCAR')
  if cell!=ref or species!=expect or counts!=[1,2]: raise ValueError('Cell/species mismatch')
  old=r[offset:offset+3]; shifts=[x[2]-y[2] for x,y in zip(xyz,old)]
  if max(shifts)-min(shifts)>1e-12: raise ValueError('Internal layer geometry changed')
  if any(abs(x[i]-y[i])>1e-12 for x,y in zip(xyz,old) for i in [0,1]): raise ValueError('In-plane registry changed')
  z=[x[2]*cell[2][2] for x in xyz]
  out[name]={'atoms':3,'z_shift_fractional':sum(shifts)/3,'z_min_A':min(z),'z_max_A':max(z),'thickness_A':max(z)-min(z),'empty_height_A':cell[2][2]-(max(z)-min(z))}
  print('%s: 3 atoms; rigid dz=%.12f fractional; thickness=%.9f A; empty height=%.9f A'%(name,out[name]['z_shift_fractional'],out[name]['thickness_A'],out[name]['empty_height_A']))
 if open('snse2/INCAR').read()!=open('sr2n/INCAR').read(): raise ValueError('INCAR protocols differ')
 if open('snse2/KPOINTS').read()!=open('sr2n/KPOINTS').read(): raise ValueError('KPOINTS protocols differ')
 out['common_cell_A']=ref
 print('Common cell, INCAR and KPOINTS: identical')
 return out

def read_eigenval(p):
 f=open(p); head=[f.readline() for _ in range(5)]
 if int(head[0].split()[-1])!=1: raise ValueError('Only ISPIN=1 scalar EIGENVAL is supported')
 ne,nk,nb=map(int,f.readline().split()); points=[]
 for ik in range(nk):
  l=f.readline()
  while l and not l.strip(): l=f.readline()
  k=list(map(float,l.split()))
  if len(k)!=4: raise ValueError('Invalid or truncated k-point header')
  bands=[]
  for ib in range(nb):
   row=list(map(float,f.readline().split()))
   if len(row)!=3 or row[0]!=ib+1: raise ValueError('Invalid band row')
   if not all(not math.isnan(x) and not math.isinf(x) for x in row): raise ValueError('Non-finite eigenvalue')
   if row[2]<-1e-6 or row[2]>1+1e-6: raise ValueError('Unexpected non-spin occupation convention')
   bands.append(row[1:])
  points.append((k,bands))
 f.close()
 w=sum(k[3] for k,rows in points)
 if abs(w-1)>1e-6: raise ValueError('Expected normalized SCF k weights')
 # VASP 5.4.4 scalar EIGENVAL occupations are per spin, in [0,1].
 count=2*sum(k[3]*sum(row[1] for row in rows) for k,rows in points)
 if abs(count-ne)>2e-4: raise ValueError('Weighted occupations do not reproduce NELECT: %.9f vs %d'%(count,ne))
 return ne,nk,nb,points,count

def result(name):
 out=open(name+'/OUTCAR').read()
 if 'aborting loop because EDIFF is reached' not in out or 'General timing and accounting' not in out:
  raise ValueError(name+': SCF convergence/final accounting missing')
 if int(re.search(r'ISPIN\s*=\s*(\d+)',out).group(1))!=1: raise ValueError('Wrong ISPIN')
 ef=float(re.findall(r'E-fermi\s*:\s*([-+0-9.]+)',out)[-1])
 elapsed=float(re.findall(r'Elapsed time \(sec\):\s*([0-9.]+)',out)[-1])
 ne,nk,nb,points,count=read_eigenval(name+'/EIGENVAL')
 if abs(float(re.search(r'NELECT\s*=\s*([0-9.]+)',out).group(1))-ne)>1e-8: raise ValueError('OUTCAR/EIGENVAL electron counts differ')
 crossing=[]; ext=[]; partial=[]
 for ib in range(nb):
  energies=[r[ib][0] for k,r in points]; occ=[r[ib][1] for k,r in points]
  item={'band':ib+1,'emin_eV':min(energies),'emax_eV':max(energies),'occ_min':min(occ),'occ_max':max(occ)}
  ext.append(item)
  if min(energies)<ef<max(energies): crossing.append(ib+1)
  if any(1e-3<x<1-1e-3 for x in occ): partial.append(ib+1)
 res={'fermi_eV':ef,'electrons':ne,'weighted_electrons':count,'nkpoints':nk,'bands':nb,'crossing_bands':crossing,'partially_occupied_bands':partial,'band_extrema':ext,'elapsed_seconds':elapsed,'windows':[],'hashes':{x:sha(name+'/'+x) for x in ['INCAR','POSCAR','KPOINTS','OUTCAR','OSZICAR','EIGENVAL','LOCPOT']}}
 if ne%2==0:
  ib=ne//2
  val=[(r[ib-1][0],i,k[:3]) for i,(k,r) in enumerate(points)]
  con=[(r[ib][0],i,k[:3]) for i,(k,r) in enumerate(points)]
  vbm=max(val);cbm=min(con);gap=cbm[0]-vbm[0]
  if gap>0 and not crossing:
   res.update({'classification':'gapped_on_sampled_mesh','vbm_eV':vbm[0],'cbm_eV':cbm[0],'gap_eV':gap,'vbm_k_fractional':vbm[2],'cbm_k_fractional':cbm[2],'vbm_band':ib,'cbm_band':ib+1})
  else: res['classification']='metallic_on_sampled_mesh' if crossing else 'no_global_gap'
 else:
  if not crossing: raise ValueError(name+': odd-electron scalar case has no sampled crossing; inspect manually')
  res['classification']='metallic_on_sampled_mesh'
 p=json.load(open(name+'/potential-summary.json'))
 if p['source_sha256']!=sha(name+'/LOCPOT'): raise ValueError('Potential summary is stale')
 if len(p['windows'])!=2: raise ValueError('Expected exactly two vacuum windows')
 for side,w in zip(['lower_z','upper_z'],p['windows']):
  if w['range_eV']>0.005: raise ValueError(name+' '+side+': vacuum not flat within 5 meV')
  item=dict(w); item['side']=side; item['fermi_minus_vacuum_eV']=ef-w['mean_eV'];item['workfunction_eV']=w['mean_eV']-ef
  if 'vbm_eV' in res:
   item['vbm_minus_vacuum_eV']=res['vbm_eV']-w['mean_eV'];item['cbm_minus_vacuum_eV']=res['cbm_eV']-w['mean_eV']
  res['windows'].append(item)
 print('%s: NELECT=%d; weighted electrons=%.8f; NKPTS=%d; NBANDS=%d; elapsed=%.3f s'%(name,ne,count,nk,nb,elapsed))
 print('  E_F=%.6f eV; classification=%s; crossing bands=%s'%(ef,res['classification'],crossing))
 for ib in crossing:
  e=ext[ib-1];print('  band %d: Emin=%.6f eV; Emax=%.6f eV; occupation=%.6f:%.6f'%(ib,e['emin_eV'],e['emax_eV'],e['occ_min'],e['occ_max']))
 if 'gap_eV' in res: print('  VBM=%.6f eV; CBM=%.6f eV; sampled gap=%.6f eV'%(res['vbm_eV'],res['cbm_eV'],res['gap_eV']))
 for w in res['windows']:
  print('  %s V_vac=%.9f eV; range=%.6g eV; Phi=%.9f eV'%(w['side'],w['mean_eV'],w['range_eV'],w['workfunction_eV']))
 return res

if __name__=='__main__':
 import sys
 g=geometry()
 if '--geometry-only' in sys.argv:
  json.dump(g,open('geometry-check.json','w'),indent=2,sort_keys=True)
 else:
  results={name:result(name) for name in ['snse2','sr2n']}
  a=results['snse2'];b=results['sr2n']
  if a['classification']!='gapped_on_sampled_mesh' or b['classification']!='metallic_on_sampled_mesh': raise ValueError('The expected semiconductor/metal scope is not supported')
  av=a['windows'][0];bv=b['windows'][1]
  ref={'snse2_side':'lower_z','sr2n_side':'upper_z','cbm_minus_metal_fermi_eV':av['cbm_minus_vacuum_eV']-bv['fermi_minus_vacuum_eV'],'metal_fermi_minus_vbm_eV':bv['fermi_minus_vacuum_eV']-av['vbm_minus_vacuum_eV'],'scope':'Frozen isolated layers, scalar nonmagnetic PBE-D3 (zero damping); not an interface barrier'}
  summary={'geometry':g,'layers':results,'interface_facing_isolated_reference':ref}
  json.dump(summary,open('alignment-summary.json','w'),indent=2,sort_keys=True)
  print('Facing isolated references: CBM(SnSe2)-E_F(Sr2N)=%.6f eV; E_F(Sr2N)-VBM(SnSe2)=%.6f eV'%(ref['cbm_minus_metal_fermi_eV'],ref['metal_fermi_minus_vbm_eV']))
```

</details>

<details>
<summary>check_vacuum_density.py 的完整源码</summary>

```python
from __future__ import print_function
import json,math
from plane_average import read_grid,cross,dot
summary={}
for name in ['snse2','sr2n']:
 cell,grid,v=read_grid(name+'/CHGCAR')
 volume=abs(dot(cell[0],cross(cell[1],cell[2])))
 nxy=grid[0]*grid[1];height=abs(dot(cell[2],cross(cell[0],cell[1])))/math.sqrt(dot(cross(cell[0],cell[1]),cross(cell[0],cell[1])))
 z=[height*i/grid[2] for i in range(grid[2])]
 density=[sum(v[i*nxy:(i+1)*nxy])/nxy/volume for i in range(grid[2])]
 electrons=sum(v)/len(v)
 expected={'snse2':26,'sr2n':25}[name]
 if abs(electrons-expected)>1e-4: raise ValueError('CHGCAR integral does not match NELECT')
 row={'electrons':electrons,'volume_A3':volume,'grid':grid,'windows':[]}
 print('%s: integrated valence electrons=%.9f; volume=%.9f A^3'%(name,electrons,volume))
 for lo,hi in [(6.,10.),(29.,33.)]:
  a=[n for zz,n in zip(z,density) if lo<=zz<=hi]
  r={'lo_A':lo,'hi_A':hi,'mean_e_per_A3':sum(a)/len(a),'max_abs_e_per_A3':max(abs(x) for x in a)}
  row['windows'].append(r)
  print('  z=%.1f:%.1f A: mean density=%.6g; max abs density=%.6g e/A^3'%(lo,hi,r['mean_e_per_A3'],r['max_abs_e_per_A3']))
 summary[name]=row
json.dump(summary,open('vacuum-density.json','w'),indent=2,sort_keys=True)
```

</details>

<details>
<summary>plane_average.py 的完整源码</summary>

```python
from __future__ import print_function
import sys, math, json, hashlib

def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def read_grid(name):
    f=open(name)
    title=f.readline().strip()
    scale=float(f.readline().split()[0])
    cell=[[float(x)*scale for x in f.readline().split()[:3]] for i in range(3)]
    if scale <= 0: raise ValueError('This reader requires a positive POSCAR scale')
    words=f.readline().split()
    if all(x.isdigit() for x in words):
        counts=list(map(int,words))
    else:
        counts=list(map(int,f.readline().split()))
    mode=f.readline().strip()
    if mode.lower().startswith('s'): mode=f.readline().strip()
    coords=[f.readline().split()[:3] for i in range(sum(counts))]
    line=f.readline()
    while line and not line.strip(): line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0: raise ValueError('Invalid FFT grid')
    n=grid[0]*grid[1]*grid[2]
    vals=[]
    while len(vals)<n:
        line=f.readline()
        if not line: raise ValueError('Truncated potential: %d/%d'%(len(vals),n))
        vals.extend(float(x.replace('D','E')) for x in line.split())
    if len(vals)!=n: raise ValueError('Unexpected extra values in scalar block')
    f.close()
    if any(math.isnan(x) or math.isinf(x) for x in vals):
        raise ValueError("Non-finite potential value")
    return cell,grid,vals

if __name__=='__main__':
    name=sys.argv[1] if len(sys.argv)>1 else 'LOCPOT'
    cell,grid,v=read_grid(name)
    area=math.sqrt(dot(cross(cell[0],cell[1]),cross(cell[0],cell[1])))
    height=abs(dot(cell[2],cross(cell[0],cell[1])))/area
    nxy=grid[0]*grid[1]
    avg=[sum(v[i*nxy:(i+1)*nxy])/nxy for i in range(grid[2])]
    zz=[height*i/grid[2] for i in range(grid[2])]
    with open('PLANAR_AVERAGE.dat','w') as f:
        f.write('# z_A  planar_potential_eV\n')
        for z,p in zip(zz,avg): f.write('%.10f %.12f\n'%(z,p))
    summary={'grid':grid,'points':len(v),'normal_height_A':height,'source_sha256':hashlib.sha256(open(name,'rb').read()).hexdigest(),'windows':[]}
    print('grid = %d %d %d; scalar values = %d'%tuple(grid+[len(v)]))
    print('normal height = %.10f A; output = PLANAR_AVERAGE.dat'%height)
    for spec in sys.argv[2:]:
        lo,hi=map(float,spec.split(':'))
        a=[p for z,p in zip(zz,avg) if lo<=z<=hi]
        if not a: raise ValueError('Empty averaging window')
        mean=sum(a)/len(a); std=math.sqrt(sum((x-mean)**2 for x in a)/len(a)); span=max(a)-min(a)
        row={'lo_A':lo,'hi_A':hi,'n':len(a),'mean_eV':mean,'std_eV':std,'range_eV':span}
        summary['windows'].append(row)
        print('window %.2f:%.2f A  N=%d  mean=%.9f eV  std=%.6g eV  range=%.6g eV'%(lo,hi,len(a),mean,std,span))
    with open('potential-summary.json','w') as f: json.dump(summary,f,indent=2,sort_keys=True)
```

</details>

<details>
<summary>同一算例的其余输入、检查命令与保存输出</summary>

```text
[bcgong@localhost band_alignment]$ python split_paw.py
snse2 SHA256 5f3cbe84c6fe6bf10909ed09324ce2b0bdcd886a81e4b163eba45f3d16624e2f
sr2n SHA256 96913914225d67d7590b8fe9bbd0003c981e9097a9e13e583aec31706f54600a
[bcgong@localhost band_alignment]$ cat snse2/POTCAR.identity.txt sr2n/POTCAR.identity.txt
SHA256 5f3cbe84c6fe6bf10909ed09324ce2b0bdcd886a81e4b163eba45f3d16624e2f
TITEL  = PAW_PBE Sn_d 06Sep2000
POMASS =  118.710; ZVAL   =   14.000    mass and valenz
TITEL  = PAW_PBE Se 06Sep2000
POMASS =   78.960; ZVAL   =    6.000    mass and valenz
SHA256 96913914225d67d7590b8fe9bbd0003c981e9097a9e13e583aec31706f54600a
TITEL  = PAW_PBE N 08Apr2002
POMASS =   14.001; ZVAL   =    5.000    mass and valenz
TITEL  = PAW_PBE Sr_sv 07Sep2000
POMASS =   87.620; ZVAL   =   10.000    mass and valenz
```

```bash
watch -n 5 'squeue -o "%.18i %.14j %.10u %.2t %.6C %.10M"'
tail -f out
```

```text
[bcgong@localhost band_alignment]$ grep -A 5 "FREE ENERGIE" snse2/OUTCAR
FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =       -12.02561657 eV

  energy  without entropy=      -12.02561626  energy(sigma->0) =      -12.02561641
```

```text
[bcgong@localhost band_alignment]$ ls -lh snse2/{INCAR,POSCAR,KPOINTS,OUTCAR,OSZICAR,EIGENVAL,LOCPOT,CHGCAR,WAVECAR}
-rw-rw-r-- 1 bcgong bcgong  37M Sep 22 23:33 snse2/CHGCAR
-rw-rw-r-- 1 bcgong bcgong  35K Sep 22 23:33 snse2/EIGENVAL
-rw-rw-r-- 1 bcgong bcgong  369 Sep 22 23:30 snse2/INCAR
-rw-rw-r-- 1 bcgong bcgong   57 Sep 22 23:30 snse2/KPOINTS
-rw-rw-r-- 1 bcgong bcgong  37M Sep 22 23:33 snse2/LOCPOT
-rw-rw-r-- 1 bcgong bcgong 2.4K Sep 22 23:33 snse2/OSZICAR
-rw-rw-r-- 1 bcgong bcgong 135K Sep 22 23:33 snse2/OUTCAR
-rw-rw-r-- 1 bcgong bcgong  464 Sep 22 23:30 snse2/POSCAR
-rw-rw-r-- 1 bcgong bcgong    0 Sep 22 23:31 snse2/WAVECAR
```

```text
明确的共同晶胞与六原子结构
  └─ 分出两层 → 保留内部形变与表面方向 → 各自居中
       └─ 相同协议的两份独立静态 SCF
            ├─ OUTCAR / OSZICAR：电子收敛与结束验收
            ├─ EIGENVAL：半导体带边或金属费米面交叉
            └─ LOCPOT + CHGCAR：双侧平坦真空区间
                 └─ 每个能级减去对应表面的真空势
                      └─ 孤立层参考表 → 后续直接检查界面体系
```

</details>


<details>
<summary>冻结层相向表面真空对齐图的完整gnuplot源码</summary>

```gnuplot
# Actual frozen-layer SCF table; no fitting and no synthetic metal band edges.
# Download band-edges-vacuum-referenced.csv beside this script, then run gnuplot.
if (!exists('datafile')) datafile = 'band-edges-vacuum-referenced.csv'
if (!exists('prefix')) prefix = 'frozen-facing-alignment'
set datafile separator comma
stats datafile using (strcol(1) eq 'snse2' && strcol(2) eq 'lower_z' ? column(7) : 1/0) nooutput
if (STATS_records != 1) { print 'Need exactly one SnSe2 lower-z VBM'; exit error }
vbm = STATS_mean
stats datafile using (strcol(1) eq 'snse2' && strcol(2) eq 'lower_z' ? column(8) : 1/0) nooutput
if (STATS_records != 1) { print 'Need exactly one SnSe2 lower-z CBM'; exit error }
cbm = STATS_mean
stats datafile using (strcol(1) eq 'sr2n' && strcol(2) eq 'upper_z' ? column(6) : 1/0) nooutput
if (STATS_records != 1) { print 'Need exactly one Sr2N upper-z EF'; exit error }
ef = STATS_mean
offset = cbm - ef
set encoding utf8
set border 2 lc rgb '#444444'
set tics nomirror out
set xrange [0.5:2.8]
set yrange [-6.65:0.65]
set ylabel 'Energy relative to the selected vacuum (eV)'
set xtics ('SnSe₂  lower-z' 1, 'Sr₂N  upper-z' 2.2) scale 0
set ytics 1
set key off
set grid ytics lc rgb '#dddddd'
set object 1 rect from 0.75,vbm to 1.25,cbm fc rgb '#e9f0f5' fs solid 1 noborder behind
set arrow 1 from 0.75,vbm to 1.25,vbm nohead lw 3 lc rgb '#205a83'
set arrow 2 from 0.75,cbm to 1.25,cbm nohead lw 3 lc rgb '#205a83'
set arrow 3 from 1.95,ef to 2.45,ef nohead lw 3 lc rgb '#ae542f'
set arrow 4 from 1.60,ef to 1.60,cbm heads size screen 0.012,15 lw 1.3 lc rgb '#555555'
set arrow 5 from 1.27,cbm to 1.60,cbm nohead dt 2 lc rgb '#777777'
set arrow 6 from 1.60,ef to 1.93,ef nohead dt 2 lc rgb '#777777'
set label 1 sprintf('VBM  %.6f',vbm) at 0.78,vbm-0.24 left font ',12'
set label 2 sprintf('CBM  %.6f',cbm) at 0.78,cbm+0.25 left font ',12'
set label 3 sprintf('EF  %.6f',ef) at 2.2,ef+0.25 center font ',12'
set label 4 'CBM − EF' at 1.69,(ef+cbm)/2+0.12 left font ',12'
set label 6 sprintf('= %.6f eV',offset) at 1.69,(ef+cbm)/2-0.18 left font ',12'
set label 5 'Vacuum = 0' at 0.58,0.18 left font ',12'
set title 'Frozen isolated layers before contact' font ',17'
do for [export_index=1:3] {
 if (export_index==1) { set terminal svg size 960,680 font 'Liberation Sans,16'; set output prefix.'.svg' }
 if (export_index==2) { set terminal pdfcairo enhanced color size 7in,5in font 'Liberation Sans,11'; set output prefix.'.pdf' }
 if (export_index==3) { set terminal pngcairo size 960,680 font 'Liberation Sans,16'; set output prefix.'.png' }
 plot 0 with lines lw 1.3 dt 2 lc rgb '#777777' notitle
 unset output
}
print sprintf('VBM=%.9f; CBM=%.9f; Sr2N EF=%.9f; CBM-EF=%.9f eV',vbm,cbm,ef,offset)
```

</details>
