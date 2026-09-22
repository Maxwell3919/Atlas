[VASP：LOCPOT 文件](https://vasp.at/wiki/LOCPOT) · [LVHAR](https://vasp.at/wiki/LVHAR) · [偶极修正](https://vasp.at/wiki/LDIPOL)

把二维异质结构沿法向剖开，原子附近的势起伏很大，真空区应当逐渐平坦。这里读取一份已经结束的 HfCl₂/PbO₂ 静态计算：六个原子，晶胞沿 z 为 30 Å，使用 PBE、D3(BJ) 和 z 方向的偶极修正。我们从它的 LOCPOT 生成平面平均势，并保留两侧真空平台。

[下载原始 LOCPOT、输入输出和平面平均脚本](/Atlas/examples/vasp/hfcl2-pbo2-potential-files.tar.gz)。解包后可从 56×56×480 的完整势网格重新生成本文的两列表格与平台统计；无需从图中反读数值。

结构和静态自洽的准备接 [SCF](/Atlas/m/scf/vasp/)。进入保存输入与输出的目录，先看文件是否齐全。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ ls -lh INCAR POSCAR KPOINTS OUTCAR OSZICAR LOCPOT
-rw-r--r-- 1 bcgong bcgong  324 Sep  4 05:07 INCAR
-rw-r--r-- 1 bcgong bcgong   60 Sep  4 05:07 KPOINTS
-rw-r--r-- 1 bcgong bcgong  27M Sep  4 05:14 LOCPOT
-rw-r--r-- 1 bcgong bcgong 3.8K Sep  4 05:14 OSZICAR
-rw-r--r-- 1 bcgong bcgong 223K Sep  4 05:14 OUTCAR
-rw-r--r-- 1 bcgong bcgong  512 Sep  4 05:07 POSCAR
```
INCAR 决定了 LOCPOT 里到底写了什么。这里用的是 `LVHAR = .TRUE.`，因此读取的是离子势与 Hartree 势之和，单位为 eV。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ cat INCAR
SYSTEM = HfCl2/PbO2 PBE-D3BJ vacuum 30 A dipole on
ENCUT = 550
PREC = Accurate
EDIFF = 1E-7
NELM = 200
ALGO = Normal
ISMEAR = 0
SIGMA = 0.05
IVDW = 12
LREAL = .FALSE.
LASPH = .TRUE.
ADDGRID = .TRUE.
LMAXMIX = 4
IDIPOL = 3
LDIPOL = .TRUE.
DIPOL = 0.5 0.5 0.5
NCORE = 4
NSW = 0
LWAVE = .FALSE.
LCHARG = .FALSE.
LVHAR = .TRUE.
```
`NSW = 0` 表示这一份输出是在固定几何上求电子态。`LDIPOL` 与 `IDIPOL = 3` 对应 z 方向的偶极修正；`DIPOL` 指定修正的参考中心。不要因为文件名同为 LOCPOT，就把另一份 `LVTOT = .TRUE.` 的总局域势混在一起相减：后者还含交换关联势。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ cat KPOINTS
HfCl2/PbO2 vacuum convergence 15x15x1
0
Gamma
15 15 1
0 0 0
```
先确认这份势来自收敛的静态计算。OSZICAR 最后的电子步和 OUTCAR 中的停止行需要对得上。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ tail -6 OSZICAR
DAV:  36    -0.337630489155E+02   -0.83988E-06   -0.33313E-07  4160   0.317E-03    0.401E-03
DAV:  37    -0.337630491465E+02   -0.23096E-06   -0.73132E-08  3504   0.223E-03    0.322E-03
DAV:  38    -0.337630498424E+02   -0.69589E-06   -0.33545E-07  3976   0.379E-03    0.192E-03
DAV:  39    -0.337630500763E+02   -0.23397E-06   -0.12784E-07  3544   0.219E-03    0.120E-03
DAV:  40    -0.337630501427E+02   -0.66348E-07   -0.47007E-08  3416   0.147E-03
   1 F= -.35058823E+02 E0= -.35057116E+02  d E =-.341425E-02
```
```text
[bcgong@localhost hfcl2_pbo2_potential]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
第 40 步电子能量变化已经小于输入的 `1E-7 eV`，OUTCAR 也明确给出电子收敛行。最后的 `F` 包含本例启用的色散能项，所以不应只拿它与上一行 DAV 的能量列相减。继续看文件末尾，确认程序正常走到了统计部分。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ tail -15 OUTCAR
  
 General timing and accounting informations for this job:
 ========================================================
  
                  Total CPU time used (sec):      237.308
                            User time (sec):      227.779
                          System time (sec):        9.529
                         Elapsed time (sec):      237.381
  
                   Maximum memory used (kb):      422788.
                   Average memory used (kb):           0.
  
                          Minor page faults:       319693
                          Major page faults:            0
                 Voluntary context switches:          952
```
这两处一起证明了当前静态电子计算结束。它们没有替几何优化、真空厚度和 k 网格做验收。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ head -19 LOCPOT
HfCl2/PbO2 PBE-D3BJ vacuum 30 A dipole  
   1.00000000000000     
     3.375590    0.000000    0.000000
    -1.687795    2.923513    0.000000
     0.000000    0.000000   30.000000
   Hf   Cl   Pb   O 
     1     2     1     2
Direct
  0.000000  0.000000  0.427206
  0.666667  0.333333  0.481442
  0.666667  0.333333  0.370286
  0.000000  0.000000  0.593817
  0.666667  0.333333  0.629714
  0.333333  0.666667  0.558126
 
   56   56  480
 0.37837857905E+01 0.37839461294E+01 0.37840180605E+01 0.37846945209E+01 0.37849682004E+01
 0.37848140587E+01 0.37842008761E+01 0.37828714743E+01 0.37824564018E+01 0.37835774956E+01
 0.37847571294E+01 0.37834151924E+01 0.37829010998E+01 0.37846014957E+01 0.37832251633E+01
```
前半段是 POSCAR 风格的晶胞和六个原子的位置；空行后的 `56 56 480` 是三维网格。后面一共应有 1,505,280 个标量势值，x 方向索引变化最快，z 最慢。它们已经是 eV，不能照搬 CHGCAR 的电子数归一化，把势再除一次晶胞体积。

平面平均就是在每个固定 z 层上，对 56 × 56 个点求算术平均。随例子提供的 `plane_average.py` 会先读结构和网格，检查标量块是否完整，再写出 `PLANAR_AVERAGE.dat`。它只读取本例的第一个标量势块；磁性或非共线输出要先确认各块代表的物理量。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ python plane_average.py LOCPOT 2:5 25:28
grid = 56 56 480; scalar values = 1505280
normal height = 30.0000000000 A; output = PLANAR_AVERAGE.dat
window 2.00:5.00 A  N=49  mean=2.538190946 eV  std=7.76333e-05 eV  range=0.000294251 eV
window 25.00:28.00 A  N=49  mean=5.029000094 eV  std=7.61576e-05 eV  range=0.000291275 eV
```
两侧平台分别约为 2.538191 和 5.029000 eV。每个窗口覆盖 49 个 z 网格点，窗口内最大起伏都不到 0.0003 eV；这比只取曲线最高的一个点更容易复核。两侧平台相差约 2.490809 eV，说明这份非对称薄层两侧的真空参考不同。

这里的 2–5 Å 与 25–28 Å 是针对这个晶胞选择的窗口：原子集中在约 11–19 Å，周期边界附近又存在偶极修正带来的势跃变，因此取样窗口避开了这两处。换材料或重新居中后，要跟着图上的原子区域和平台重新选窗口，不能固定照抄这四个数。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ head -5 PLANAR_AVERAGE.dat
# z_A  planar_potential_eV
0.0000000000 3.783714602193
0.0625000000 3.303792300942
0.1250000000 2.899977063405
0.1875000000 2.631753663237
```
第一列是沿层法向的距离，第二列是平面平均势。z = 0 附近的数值不同于两侧平台；把这一行直接当作真空能级会读错参考。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ grep 'E-fermi' OUTCAR
 E-fermi :  -1.2958     XC(G=0):  -3.9262     alpha+bet : -3.9672
```
这份输出的费米能为 −1.2958 eV。若要继续计算两个表面的功函数，需要各自使用同一份计算中的真空平台与这个费米能相减；下一步接 [功函数](/Atlas/m/workfunction/vasp/)。电势差本身不能单独证明电荷转移方向或接触后的带型。

把 `PLANAR_AVERAGE.dat`、`potential-summary.json` 和 `plot_potential.py` 放在本机同一目录后，用 `python3 plot_potential.py` 绘图。脚本读第一列作横轴、第二列作纵轴，把两个统计窗口涂成浅色，并同时输出 PNG 与 PDF。图上保留整个晶胞，才能同时检查原子区、两侧平台和周期边界。

下一步也可接 [能带对齐](/Atlas/m/band-alignment/vasp/)。比较两种材料前，还要准备各自一致的能带边与势参考。

![非对称薄层两侧的平面平均势](/Atlas/examples/vasp/hfcl2_pbo2_potential/potential-z.png)

```text
固定几何的 SCF
  └─ LVHAR → LOCPOT → 平面平均势
                         ├─ 两侧真空平台 → 功函数
                         └─ 一致的能量参考 → 能带对齐
```
