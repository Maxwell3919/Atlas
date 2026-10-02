层间分离计算沿一条指定的路径回答：把某一层移开，需要增加多少电子能量？若两张单层形成双层，参照可取各自的单层能量；若从多层表面取走顶层，参照则包含剩余多层。两种操作应先在结构和能量定义中分清。

这里保留一个真实的 HfI₂ 六层冻结 slab：只抬高顶层的三个原子，其余坐标保持不变。从 20 个完成单点得到，顶层位移 20 Å 时 $W=0.36641176\;\mathrm{J/m^2}$。它演示有限距离分离功的提取、面积归一化与周期像检查。研究异质结的构型与两张单层参照先从 [异质结构建模](/Atlas/m/heterostructure-modeling/vasp/) 进入；这份 HfI₂ 数据不能代替 ZrCl₂/Sc₂C 或 SnSe₂/Sr₂N 的界面作用能。

[下载实际输入、OUTCAR 与完整后处理包](/Atlas/examples/hfi2-frozen20-files.tar.gz)，解压后进入 `hfi2-frozen20`。提取已有输出只需 Python 3；重新运行 VASP 需自行准备有权限的匹配 POTCAR。包内不分发其正文。

## 先确定移动的层与参考结构

进入整理后的目录，先看位移零点的结构头：

```console
[bcgong@localhost hfi2-frozen20]$ head -n 12 raw/scf_eq/POSCAR
HfI2_from_ZrBr2_ClE_scf_eq
   1.00000000000000     
     3.5392721285805808   -0.0000000000003520    0.0000000000000000
    -1.7696360642408731    3.0650995742385150   -0.0000000000000000
    -0.0000000000000000    0.0000000000000001   82.1873167285724548
   I   Hf
     12     6
Direct
  0.0000000000000000  0.0000000000000000  0.0623995784225782
 -0.0000000000000000 -0.0000000000000000  0.1069198184137017
  0.6666666670000012  0.3333333329999988  0.1462730983045202
  0.6666666670000012  0.3333333329999988  0.1907129027046066
[bcgong@localhost hfi2-frozen20]$
```

元素行是 I、Hf，个数为 12、6，共 18 个原子，对应六个 I–Hf–I 层。标题中的 `from_ZrBr2` 保留了原型构造痕迹。这一组没有附带已通过验收的 HfI₂ 结构优化结果，所以 `scf_eq` 只作为**位移零点**，不能根据目录名宣称它已经是平衡结构。

实际第三晶格长度为 82.187316728572 Å，面内面积从前两根晶格矢量的叉积得到：

```text
A = |a1 × a2| = 10.848221494426 Å²
```

原子坐标按 POSCAR 顺序编号。每个位移点只移动第 11、12、18 号原子，也就是最上层的两个 I 与一个 Hf；其余 15 个原子保持原位。提取程序实际比较了所有接受点的晶胞、元素、原子个数与逐原子坐标，确认移动的是这一整层。

位移 d 的定义是相对 `scf_eq` 沿笛卡尔 z 方向增加的长度，不是两层之间的实际间隙。对于本例沿 z 的第三晶格矢量，分数坐标改变量为：

```text
Δz_fractional = d / 82.18731672857245
```

如果复制这个体系准备新的位移点，可用 `cp` 复制原输入，再在 `vi POSCAR` 中修改同一组三个原子的 z 分数坐标，保存后核对所有坐标。移动后的原子不单独弛豫；因此下面得到的是这份明确冻结几何的分离曲线，尚不是充分弛豫材料的剥离能。

## 固定几何单点中实际使用的参数

原始输出标识为 VASP 5.4.4。零点和全部接受点使用相同的 INCAR、KPOINTS 与相同的 PAW 类型。主要输入如下；完整 [INCAR](/Atlas/examples/hfi2-frozen20/raw/scf_eq/INCAR)、[KPOINTS](/Atlas/examples/hfi2-frozen20/raw/scf_eq/KPOINTS) 和 [运行脚本](/Atlas/examples/hfi2-frozen20/raw/scf_eq/script_std) 保存在同一组目录。

| 设置 | 实际输入 | 与分离能的关系 |
| --- | --- | --- |
| 泛函与色散 | PBE，`IVDW=11` | D3 零阻尼；移层改变原子间距离，色散能也改变 |
| 平面波与投影 | `ENCUT=400` eV，`PREC=Accurate`，`LREAL=A` | 此处 A 是自动实空间投影；原 INCAR 注释不能替代参数含义 |
| 电子停止条件 | `EDIFF=1E-6` eV，`NELM=160` | 每个位移点需独立达到电子停止条件 |
| 电子占据 | `ISMEAR=0`，`SIGMA=0.05` eV | 全组用同一个能量字段相减 |
| 采样 | Γ 中心 18×18×1 | 真空方向一个点；面内网格仍需针对能量差检验 |
| 原子位置 | `IBRION=-1`，未启用离子步 | 每个点是冻结坐标的静态能量 |

`SYSTEM=SnS2` 是遗留模板标题，元素身份以实际 POSCAR 和 PAW 为准。

## 从输出选取完成点

每份接受的 OUTCAR 同时有最终能量、电子达到 EDIFF 的结束记录和正常结束统计。只检查文件是否存在，或只取最后一个数字，会把未完成的电子计算也混入距离序列。提取器保留两张表：`exfoliation.csv` 是接受点，`excluded.csv` 是被排除的目录。

在数据目录执行原有提取器：

```console
[bcgong@localhost hfi2-frozen20]$ python -B extract_scan.py | tee extraction.out
accepted=20 excluded=7 atoms=18 moved=11,12,18
area=10.848221494426 A^2 c=82.187316728572 A
```

这是提取输出的开头两行，完整 20 点数值在 [exfoliation.csv](/Atlas/examples/hfi2-frozen20/exfoliation.csv)。接受集合为 d=0 和 d=2…20 Å。`scf_d1` 没有 OUTCAR，`scf_d1.00` 是不完整静态 SCF，0.25、0.50、0.75、1.25、1.50 Å 的尝试也未满足接受条件；这些目录没有被插值成新的能量点。[排除表](/Atlas/examples/hfi2-frozen20/excluded.csv)保留了逐项目原因。

## 按一个界面的面积计算分离功

前面的几何与输出确定了能量差的参考：18 原子的冻结六层 slab，以 11、12、18 号原子的共同位移打开一个界面。判断大距离结果时，还要同时查看能量变化和外侧周期镜像间距。

所以本页能报告的是一个冻结六层模型中打开一个界面的有限距离分离功：

$$
\begin{aligned}
W(d)&=\frac{E(d)-E(0)}{A},\\
1\;\mathrm{eV/\mathring A^2}&=16.02176634\;\mathrm{J/m^2}.
\end{aligned}
$$

这里 $E(d)$ 和 $E(0)$ 均取对应 OUTCAR 的 `energy without entropy`，$A$ 是面内面积 10.8482214944 Å²。以最后一个接受点为例，把两份 OUTCAR 的数值代入，而不是先按原子数归一化：

$$
\begin{aligned}
\Delta E(20)&=(-107.54517866)-(-107.79327340)\\
&=0.24809474\;\mathrm{eV/cell},\\
W(20)&=\frac{0.24809474}{10.8482214944}\\
&=0.0228696234\;\mathrm{eV/\mathring A^2}\\
&=22.8696234\;\mathrm{meV/\mathring A^2}\\
&=0.3664117622\;\mathrm{J/m^2}.
\end{aligned}
$$

分子是整个 18 原子晶胞的能量差，分母是被打开的一个界面的面内面积；既不除以 18，也不除以移动层的三个原子。六层模型虽有多个层间接触，这条路径只打开顶层与下方五层之间的一处接触。两侧新露出的面也不等于发生了两次独立的界面分离。

这一定义因此使用 A，表面能关系中的 2A 不能直接搬进来。只有两个新表面等价，且参照态、弛豫和厚度极限均适当时，才可用分离功的一半讨论单面表面能。这里的零点仍是有限六层冻结 slab，0.36641176 J/m² 保留为该路径的有限距离分离功。

### 接受点与末段起伏

接受表共 20 点：d=0 与 d=2…20 Å。名义 d=1 Å 有两次尝试但均未接受：目录 scf_d1 的 OUTCAR 缺失，scf_d1.00 为不完整静态 SCF。另有 scf_d0.25、0.50、0.75、1.25、1.50 未满足接受条件。没有把这些尝试插值进接受表。以下选择 d=0、首个接受的 d=2 和末段五个点；能量均为 eV/cell，ΔE 为 meV/cell，W 为 J/m²。

| 目录 | d (Å) | E without entropy (eV/cell) | ΔE (meV/cell) | W (J/m²) | 外侧周期镜像间距 (Å) |
| --- | ---: | ---: | ---: | ---: | ---: |
| scf_eq | 0 | −107.79327340 | 0.00000 | 0.00000000 | 43.993243 |
| scf_d2 | 2 | −107.67298978 | 120.28362 | 0.17764719 | 41.993243 |
| scf_d16 | 16 | −107.54552844 | 247.74496 | 0.36589517 | 27.993243 |
| scf_d17 | 17 | −107.54522826 | 248.04514 | 0.36633851 | 26.993243 |
| scf_d18 | 18 | −107.54525486 | 248.01854 | 0.36629922 | 25.993243 |
| scf_d19 | 19 | −107.54475578 | 248.51762 | 0.36703631 | 24.993243 |
| scf_d20 | 20 | −107.54517866 | 248.09474 | 0.36641176 | 23.993243 |

d=16…20 Å 的五点能量范围是 0.77266 meV/cell；d=19→20 Å 反而降低 0.42288 meV/cell。这个有限样本显示末段存在起伏，不能据此给出统计误差，也不足以确认能量已经达到解理曲线的平台。与此同时，c 保持固定时，外侧周期镜像间距从 43.993 Å 缩到 23.993 Å。用坐标可以看清这个变化：零点 slab 的 z 跨度为 38.1940736594 Å，d=20 Å 时变成 58.1940736594 Å，第三晶格长度始终是 82.1873167286 Å。因此外侧间距按 $g_{\mathrm{outer}}(d)=43.9932430691\;\mathring A-d$ 缩短；内部接触拉开，外侧周期像却更近了。若之后检验周期像影响，需要在增大 c 的同一晶胞下成对计算零点与分离点，让能量差有一致参照。现有数据还没有这组对照。末段起伏与 `EDIFF=1E-6` 也不是同一量：EDIFF 是每点电子迭代的停止条件，不能作为整条分离曲线或周期像误差的上界。

![HfI₂ 冻结六层模型的分离功与大位移段能量变化](/Atlas/examples/hfi2-frozen20/hfi2-exfoliation.png)

图 (a) 的蓝色实线与圆点使用 CSV 的 `d_A` 与 `W_meV_A2`，将同一冻结路径的能量差除以 10.8482214944 Å²；图 (b) 的橙色虚线与方点保留 d≥12 Å 的 `delta_E_meV`，放大总图里不易看出的末段起伏。两图横轴都是顶层相对零点的位移，不是实际层间隙。标记对应接受的原始点，连线只用于引导视线，d=1 Å 的缺点没有补出。应同时看图 (a) 的整体分离代价和图 (b) 的微小变化，再对照表中的周期像间距；总图看起来平坦并不能消除后者的变化。

可用 gnuplot 直接重画这组已提取的数据。把 [完整脚本](/Atlas/examples/interface-literature/plot_exfoliation.gp)保存为 `plot_exfoliation.gp`，放在解压后的 `hfi2-frozen20` 目录，与 `exfoliation.csv` 同级，运行：

```bash
gnuplot plot_exfoliation.gp
```

脚本逐列读取原 CSV，输出 `hfi2-separation-gnuplot.svg/png/pdf`；没有拟合、平滑或补点。原图与原有生成记录保留，下面给出这条 gnuplot 路线的完整源码。

<details>
<summary>plot_exfoliation.gp 完整源码</summary>

```gnuplot
# Read the accepted CSV; no fit, interpolation, or new energy points.
if (!exists("data_root")) data_root = "."
if (!exists("out_root")) out_root = "."
data = data_root."/exfoliation.csv"
set encoding utf8
set datafile separator ","
set datafile columnheaders
set border 3
set tics out nomirror
set key off
do for [ext in "svg png pdf"] {
    if (ext eq "svg") { set terminal svg size 900,360 enhanced font "DejaVu Sans,11" }
    if (ext eq "png") { set terminal pngcairo size 900,360 enhanced font "DejaVu Sans,11" }
    if (ext eq "pdf") { set terminal pdfcairo size 9,3.6 enhanced font "DejaVu Sans,11" }
    set output out_root."/hfi2-separation-gnuplot.".ext
    set size 1,1
    set origin 0,0
    unset title
    set multiplot layout 1,2 margins 0.08,0.98,0.18,0.83 spacing 0.12,0.05 title "HfI2 | frozen six-layer separation"
    set title "(a) Accepted separation points"
    set xlabel "Top-layer displacement d (Å)"
    set ylabel "[E(d)-E(0)]/A (meV Å^{-2})"
    set xrange [-0.4:20.4]
    set yrange [-0.5:25]
    plot data using 2:6 with linespoints pt 7 ps 0.55 lw 1 lc rgb "#0072B2"
    set title "(b) Large-distance detail"
    set ylabel "E(d)-E(0) (meV/cell)"
    set xrange [11.6:20.4]
    set yrange [*:*]
    plot data using 2:($2>=12 ? $5 : 1/0) with linespoints pt 5 ps 0.55 lw 1 dt 2 lc rgb "#D55E00"
    unset multiplot
    unset output
}
print "Read 20 accepted points; wrote hfi2-separation-gnuplot.svg/.png/.pdf"
```

</details>



## 为什么有限分离功还需要参照厚度与弛豫

[Jung、Park 与 Ihm，DOI: 10.1021/acs.nanolett.7b04201](https://doi.org/10.1021/acs.nanolett.7b04201)的作者版 PDF 第 2 页 [Fig. 1(a,b)](https://arxiv.org/html/1805.04527v1#S0.F1)对照分离前的厚 slab 与取走顶层后的结构；图注还要求分离层和剩余 slab 都弛豫。第 3 页 [Fig. 2(a–e)](https://arxiv.org/html/1805.04527v1#S0.F2)将这个过程拆开：a→b 是整层刚性移走，b→c 允许剩余 slab 重排，c→d 允许分离层改变层内坐标和面内晶格，e 才比较初态 I 与终态 IV。虚线划分表面区和体相区，不是原子层或新的界面。

本例抬高顶层三个原子、其余坐标固定，对应 Fig. 2(a→b) 的有限距离路径；后两步在现有数据中没有能量记录。读者可以在 VESTA 中并排打开 `raw/scf_eq/POSCAR` 与 `raw/scf_d20/POSCAR`，用相同侧视、颜色和比例标出移动层、剩余五层以及外侧周期像间距。这样的结构对照说明能量差对应哪一次操作；两份有限结构本身并不完成 Fig. 2(e) 的体相厚度极限。文献式 (1)–(7)先按体相面内晶胞定义每层能量，再取厚度极限；本页则按实际六层模型的面积报告 meV/Å² 与 J/m²，比较时必须保留这一参照差别。

对异质双层，若定义 $\Delta E_{\mathrm{int}}=E_{AB}-E_A-E_B$，负值代表相对于所选单层参考降低了能量；从该构型把两层分开的冻结功在充分分离极限下与它符号相反。这个比较还要求相同的共同晶胞、电荷、自旋和几何参照。HfI₂ 本例的 B 是剩余五层，不能把它的数值转写为两种材料的异质结结合能。

若要把这条路径用于材料剥离研究，应从接受的参考几何开始，检查层数、分离距离、周期高度和可允许的弛豫，并用成组静态能量检验数值参数。单个有限距离的正分离功说明当前操作提高电子能量，完整的材料热力学稳定性还涉及其它相和相应参照。

## 重建与复核数值

原始提取器读取 `raw/<directory>/` 中的 POSCAR、INCAR、KPOINTS、OUTCAR 和运行记录，确认只有 11、12、18 号原子共同移动，再统一使用 `energy without entropy`。复核程序从 CSV 和零点 POSCAR 独立重算面积、三种单位的能量差与末段范围。两段程序用途不同：前者检查原始输出，后者核对表格的计算关系。

```text
用 Python 3 读取 HfI2 的原始各点目录，检查冻结晶胞、元素/个数、指定顶层共同位移、
相同电子协议、电子达到 EDIFF 与正常结束。用同一 energy without entropy 字段，
以 d=0 为基准，并从 a×b 求面积；写接受点与排除表，保留原始两种能量字段。
再编写独立表格复核程序，从 CSV 和 POSCAR 重算 meV/cell、meV/Å²、J/m²，
报告 d=16…20 Å 的能量范围与 19→20 Å 的变化，不平滑末段或自动拟合平台。
```

[原始提取器](/Atlas/examples/hfi2-frozen20/extract_scan.py) · [独立复核程序](/Atlas/examples/thermo-postprocessing/exfoliation/review_hfi2_exfoliation.py)

<details>
<summary>extract_scan.py 的完整源码</summary>

```python
from __future__ import print_function
import os, re, math, csv, json, hashlib

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read_poscar(path):
    lines=open(path).read().splitlines()
    scale=float(lines[1])
    if scale<=0:raise ValueError('Positive scalar POSCAR scale required')
    cell=[[float(x)*scale for x in line.split()[:3]] for line in lines[2:5]]
    species=lines[5].split();counts=list(map(int,lines[6].split()));nat=sum(counts)
    at=7
    if lines[at].lower().startswith('s'):at+=1
    mode=lines[at].lower();at+=1
    raw=[[float(x) for x in line.split()[:3]] for line in lines[at:at+nat]]
    if mode.startswith('d'):
        pos=[[sum(v[k]*cell[k][j] for k in range(3)) for j in range(3)] for v in raw]
    elif mode.startswith(('c','k')):
        pos=[[x*scale for x in v] for v in raw]
    else:raise ValueError('Unsupported coordinates')
    return cell,species,counts,pos

def area(cell):
    a,b=cell[:2]
    cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    return math.sqrt(sum(x*x for x in cross))

base='raw'
rows=[];excluded=[];fingerprints={}
reference=read_poscar(os.path.join(base,'scf_eq','POSCAR'))
protocol=[digest(os.path.join(base,'scf_eq',f)) for f in ('INCAR','KPOINTS')]
expected_titles=None
for name in sorted(os.listdir(base)):
    folder=os.path.join(base,name)
    if not os.path.isdir(folder) or not name.startswith('scf_'):continue
    outpath=os.path.join(folder,'OUTCAR')
    if not os.path.isfile(outpath):
        excluded.append(dict(directory=name,reason='OUTCAR absent',energy_lines=0,ediff=0,normal_end=0))
        continue
    out=open(outpath).read()
    energies=re.findall(r'energy\s+without entropy=\s*([-\d.]+)\s+energy\(sigma->0\)\s*=\s*([-\d.]+)',out)
    ediff=out.count('aborting loop because EDIFF is reached')
    normal=out.count('General timing and accounting')
    if len(energies)!=1 or ediff!=1 or normal!=1:
        excluded.append(dict(directory=name,reason='Incomplete static SCF',energy_lines=len(energies),ediff=ediff,normal_end=normal))
        continue
    if re.search(r'VERY BAD NEWS|BRMIX:|Error EDD|ZHEGV failed',out,re.I):
        raise ValueError(name+': electronic solver error')
    current=read_poscar(os.path.join(folder,'POSCAR'))
    if current[:3]!=reference[:3]:raise ValueError(name+': cell/species/counts changed')
    if [digest(os.path.join(folder,f)) for f in ('INCAR','KPOINTS')]!=protocol:
        raise ValueError(name+': input protocol differs')
    titles=re.findall(r'TITEL\s*=\s*(.*)',out)
    if expected_titles is None:expected_titles=titles
    if titles!=expected_titles:raise ValueError(name+': output pseudopotentials differ')
    if float(re.findall(r'NELECT\s*=\s*([-\d.]+)',out)[-1])!=156.:
        raise ValueError(name+': unexpected electron count')
    shifts=[[v-w for v,w in zip(p,q)] for p,q in zip(current[3],reference[3])]
    d=0. if name=='scf_eq' else float(name.split('scf_d')[1])
    for index,vec in enumerate(shifts):
        expected=d if index in (10,11,17) else 0.
        if max(abs(vec[0]),abs(vec[1]),abs(vec[2]-expected))>1e-7:
            raise ValueError(name+': incorrect frozen-layer displacement')
    energy=float(energies[0][0]);sigma=float(energies[0][1])
    ez=[v[2] for v in current[3]]
    outer_gap=current[0][2][2]-(max(ez)-min(ez))
    fingerprints[name]={f:digest(os.path.join(folder,f)) for f in
                       ('INCAR','KPOINTS','POSCAR','OUTCAR','OSZICAR','script_std')
                       if os.path.isfile(os.path.join(folder,f))}
    rows.append(dict(directory=name,d_A=d,energy_without_entropy_eV=energy,
                     energy_sigma0_eV=sigma,outer_periodic_gap_A=outer_gap))
rows.sort(key=lambda row:row['d_A'])
if len(rows)!=20 or [row['d_A'] for row in rows]!=[0.]+list(map(float,range(2,21))):
    raise ValueError('Expected exactly the verified 20-point set')
area_A2=area(reference[0]);e0=rows[0]['energy_without_entropy_eV']
for row in rows:
    row['delta_E_meV']=1000*(row['energy_without_entropy_eV']-e0)
    row['W_meV_A2']=row['delta_E_meV']/area_A2
    row['W_J_m2']=row['W_meV_A2']*.01602176634
keys=['directory','d_A','energy_without_entropy_eV','energy_sigma0_eV','delta_E_meV','W_meV_A2','W_J_m2','outer_periodic_gap_A']
with open('exfoliation.csv','w') as f:
    w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
with open('excluded.csv','w') as f:
    w=csv.DictWriter(f,['directory','reason','energy_lines','ediff','normal_end'],lineterminator='\n')
    w.writeheader();w.writerows(excluded)
summary=dict(natoms=18,species=reference[1],counts=reference[2],area_A2=area_A2,
             c_A=reference[0][2][2],moved_atom_indices_1based=[11,12,18],
             accepted_points=len(rows),excluded_points=len(excluded),
             energy_reference_eV=e0,energy_definition='energy without entropy',
             geometry_scope='Frozen prototype-derived HfI2 structure; no accepted HfI2 relaxation in this dataset',
             final_point=rows[-1],tail_16_to_20_range_meV=max(r['delta_E_meV'] for r in rows[-5:])-min(r['delta_E_meV'] for r in rows[-5:]),
             output_potential_titles=expected_titles,sha256=fingerprints)
with open('summary.json','w') as f:json.dump(summary,f,indent=2,sort_keys=True)
print('accepted=%d excluded=%d atoms=18 moved=11,12,18'%(len(rows),len(excluded)))
print('area=%.12f A^2 c=%.12f A'%(area_A2,reference[0][2][2]))
for row in rows:
    print('d=%4.1f A E=%14.8f eV dE=%10.5f meV W=%10.6f meV/A^2 outer_gap=%9.5f A'%
          (row['d_A'],row['energy_without_entropy_eV'],row['delta_E_meV'],row['W_meV_A2'],row['outer_periodic_gap_A']))
print('16--20 A energy range=%.5f meV'%summary['tail_16_to_20_range_meV'])
for row in excluded:
    print('excluded %s: %s energy=%d EDIFF=%d end=%d'%(row['directory'],row['reason'],row['energy_lines'],row['ediff'],row['normal_end']))
```

</details>

<details>
<summary>review_hfi2_exfoliation.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Validate HfI2 separation-energy bookkeeping and emit a focused review table."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

EV_A2_TO_J_M2 = 16.02176634
EXPECTED_AREA_A2 = 10.848221494425957
TAIL_DISTANCES = {16.0, 17.0, 18.0, 19.0, 20.0}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing CSV header")
        return reader.fieldnames, list(reader)


def poscar_area(path: Path) -> float:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 5:
        raise ValueError(f"{path}: incomplete POSCAR lattice")
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError(f"{path}: expected positive POSCAR scale factor")
    a = [float(value) * scale for value in lines[2].split()[:3]]
    b = [float(value) * scale for value in lines[3].split()[:3]]
    if len(a) != 3 or len(b) != 3:
        raise ValueError(f"{path}: malformed first two lattice vectors")
    cross = (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )
    area = math.sqrt(sum(value * value for value in cross))
    if not math.isfinite(area) or area <= 0:
        raise ValueError(f"{path}: non-positive/non-finite in-plane area")
    return area


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted", type=Path, default=Path("exfoliation.csv"))
    parser.add_argument("--excluded", type=Path, default=Path("excluded.csv"))
    parser.add_argument("--poscar", type=Path, default=Path("POSCAR"))
    parser.add_argument("--outdir", type=Path, default=Path("review"))
    args = parser.parse_args()

    accepted_header, accepted_rows = read_csv(args.accepted)
    excluded_header, excluded_rows = read_csv(args.excluded)
    area = poscar_area(args.poscar)
    if not math.isclose(area, EXPECTED_AREA_A2, rel_tol=0, abs_tol=2e-9):
        raise ValueError(
            f"{args.poscar}: area {area:.12f} A^2 differs from reviewed cell "
            f"{EXPECTED_AREA_A2:.12f} A^2"
        )
    required = {
        "directory", "d_A", "energy_without_entropy_eV", "energy_sigma0_eV",
        "delta_E_meV", "W_meV_A2", "W_J_m2", "outer_periodic_gap_A",
    }
    missing = required - set(accepted_header)
    if missing:
        raise ValueError(f"{args.accepted}: missing columns {sorted(missing)}")
    for required_name in ("directory", "reason", "energy_lines", "ediff", "normal_end"):
        if required_name not in excluded_header:
            raise ValueError(f"{args.excluded}: missing column {required_name}")

    by_distance: dict[float, dict[str, str]] = {}
    for row in accepted_rows:
        d = float(row["d_A"])
        if d in by_distance:
            raise ValueError(f"{args.accepted}: duplicate accepted d={d:g} A")
        for column in required - {"directory"}:
            value = float(row[column])
            if not math.isfinite(value):
                raise ValueError(f"{args.accepted}: non-finite {column} at d={d:g} A")
        by_distance[d] = row
    expected_distances = {0.0} | set(float(d) for d in range(2, 21))
    if set(by_distance) != expected_distances:
        missing_d = sorted(expected_distances - set(by_distance))
        unexpected_d = sorted(set(by_distance) - expected_distances)
        raise ValueError(
            f"accepted d set differs: missing={missing_d}, unexpected={unexpected_d}"
        )
    if by_distance[0.0]["directory"] != "scf_eq":
        raise ValueError("the sole d=0 reference must be scf_eq")

    e0 = float(by_distance[0.0]["energy_without_entropy_eV"])
    recalculated: dict[float, tuple[float, float, float]] = {}
    for d, row in by_distance.items():
        energy = float(row["energy_without_entropy_eV"])
        delta_e = energy - e0
        delta_mev = delta_e * 1000.0
        work_mev_a2 = delta_mev / area
        work_j_m2 = delta_e / area * EV_A2_TO_J_M2
        checks = (
            ("delta_E_meV", delta_mev, 2e-5),
            ("W_meV_A2", work_mev_a2, 2e-7),
            ("W_J_m2", work_j_m2, 2e-8),
        )
        for column, calculated, tolerance in checks:
            stored = float(row[column])
            if not math.isclose(calculated, stored, rel_tol=0, abs_tol=tolerance):
                raise ValueError(
                    f"d={d:g} A: recomputed {column}={calculated:.12g}, "
                    f"stored={stored:.12g}"
                )
        recalculated[d] = (delta_mev, work_mev_a2, work_j_m2)

    if len(accepted_rows) != 20 or len(excluded_rows) != 7:
        raise ValueError(
            f"reviewed dataset requires 20 accepted and 7 excluded; "
            f"found {len(accepted_rows)} and {len(excluded_rows)}"
        )
    excluded_by_name = {row["directory"]: row for row in excluded_rows}
    if len(excluded_by_name) != len(excluded_rows):
        raise ValueError(f"{args.excluded}: duplicate excluded directory")
    expected_d1 = {"scf_d1", "scf_d1.00"}
    if expected_d1 - set(excluded_by_name):
        raise ValueError(f"nominal d=1 A exclusions are missing: {sorted(expected_d1 - set(excluded_by_name))}")
    if excluded_by_name["scf_d1"]["reason"] != "OUTCAR absent":
        raise ValueError("scf_d1 exclusion reason no longer matches the reviewed record")
    if excluded_by_name["scf_d1.00"]["reason"] != "Incomplete static SCF":
        raise ValueError("scf_d1.00 exclusion reason no longer matches the reviewed record")

    selected = [0.0, 2.0, 16.0, 17.0, 18.0, 19.0, 20.0]
    selected_rows: list[dict[str, str]] = []
    for d in selected:
        row = by_distance[d]
        delta_mev, work_mev_a2, work_j_m2 = recalculated[d]
        selected_rows.append({
            "directory": row["directory"],
            "d_A": f"{d:.1f}",
            "energy_without_entropy_eV": row["energy_without_entropy_eV"],
            "delta_E_meV": f"{delta_mev:.8f}",
            "W_meV_A2": f"{work_mev_a2:.8f}",
            "W_J_m2": f"{work_j_m2:.10f}",
            "outer_periodic_gap_A": row["outer_periodic_gap_A"],
        })

    args.outdir.mkdir(parents=True, exist_ok=True)
    table_path = args.outdir / "hfi2-selected-separation-review.csv"
    exclusion_path = args.outdir / "hfi2-exclusion-review.csv"
    report_path = args.outdir / "hfi2-separation-review.md"
    write_csv(table_path, [
        "directory", "d_A", "energy_without_entropy_eV", "delta_E_meV",
        "W_meV_A2", "W_J_m2", "outer_periodic_gap_A",
    ], selected_rows)
    write_csv(exclusion_path, excluded_header, excluded_rows)

    tail_energies = [float(by_distance[d]["energy_without_entropy_eV"]) for d in sorted(TAIL_DISTANCES)]
    tail_spread_mev = (max(tail_energies) - min(tail_energies)) * 1000.0
    step_19_20_mev = (
        float(by_distance[20.0]["energy_without_entropy_eV"])
        - float(by_distance[19.0]["energy_without_entropy_eV"])
    ) * 1000.0
    w20 = recalculated[20.0][2]
    report_path.write_text(
        "# HfI2 frozen-slab separation review\n\n"
        f"- POSCAR area: {area:.12f} Å².\n"
        f"- Accepted scan points: {len(accepted_rows)}; excluded directories: {len(excluded_rows)}.\n"
        "- Accepted distances: d=0 and d=2…20 Å. The nominal d=1 Å attempts are not accepted: "
        "scf_d1 has no OUTCAR and scf_d1.00 is an incomplete static SCF.\n"
        "- Energy field used throughout: OUTCAR energy without entropy, eV/cell.\n"
        f"- At d=20 Å, ΔE={recalculated[20.0][0]:.8f} meV/cell and W={w20:.10f} J/m².\n"
        f"- The d=16…20 Å five-point energy spread is {tail_spread_mev:.5f} meV/cell; "
        f"the d=19→20 Å change is {step_19_20_mev:.5f} meV/cell.\n\n"
        "Interpretation: these values describe the frozen six-layer, prototype-derived slab under "
        "one specified layer-separation operation. The d=0 reference is itself a six-layer slab, "
        "not a bulk calculation. The finite-distance energy and non-monotone high-distance spread "
        "do not establish a bulk-referenced exfoliation energy or a converged asymptote.\n",
        encoding="utf-8",
    )
    print(f"accepted={len(accepted_rows)} excluded={len(excluded_rows)} area={area:.12f} A^2")
    print(f"d20: delta_E={recalculated[20.0][0]:.8f} meV/cell W={w20:.10f} J/m^2")
    print(f"d16-20 energy spread={tail_spread_mev:.5f} meV/cell; d19->20={step_19_20_mev:.5f} meV/cell")
    print(table_path)
    print(exclusion_path)
    print(report_path)


if __name__ == "__main__":
    main()
```

</details>

复核脚本默认从当前目录读取 `exfoliation.csv`、`excluded.csv` 和零点 `POSCAR`。把 `raw/scf_eq/POSCAR` 复制为该名字，在同一目录执行：

```bash
python3 review_hfi2_exfoliation.py --outdir review
```

实际结果为：

```text
accepted=20 excluded=7 area=10.848221494426 A^2
d20: delta_E=248.09474000 meV/cell W=0.3664117622 J/m^2
d16-20 energy spread=0.77266 meV/cell; d19->20=-0.42288 meV/cell
```

[复核表与判读](/Atlas/examples/thermo-postprocessing/exfoliation/review/hfi2-separation-review.md)保留了末段起伏。相同几何的电子密度重排可接 [差分电荷](/Atlas/m/delta-charge/vasp/)；观察零温附近的振动模式则接 [声子](/Atlas/m/phonon-finite-disp/)。分离曲线、密度图与振动结果各自对应不同的问题。

[VASP OUTCAR](https://vasp.at/wiki/OUTCAR) · [展宽能量字段](https://vasp.at/wiki/Smearing_technique) · [色散修正](https://vasp.at/wiki/IVDW)
