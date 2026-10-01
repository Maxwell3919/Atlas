把二维异质结构沿法向剖开，原子附近的势起伏很大，真空区应当逐渐平坦。这里读取一份已经结束的 HfCl₂/PbO₂ 静态计算：六个原子，晶胞沿 z 为 30 Å，使用 PBE、D3(BJ) 和 z 方向的偶极修正。我们从它的 LOCPOT 生成平面平均势，并保留两侧真空平台。

结构和静态自洽的准备接 [SCF](/Atlas/m/scf/vasp/)。

[VASP：LOCPOT 文件](https://vasp.at/wiki/LOCPOT) · [LVHAR](https://vasp.at/wiki/LVHAR) · [偶极修正](https://vasp.at/wiki/LDIPOL)

[下载原始 LOCPOT、输入输出和平面平均脚本](/Atlas/examples/vasp/hfcl2-pbo2-potential-electronic-files.tar.gz)。解包后可从 56×56×480 的完整势网格重新生成本文的两列表格与平台统计；无需从图中反读数值。

## 确认势的组成与静态计算输出

进入保存输入与输出的目录，先看文件是否齐全。

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
这两处确认了静态电子计算达到停止条件并正常结束；几何、真空厚度和 k 网格的精度分别由相应收敛检查确定。

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

沿 z 的 480 个点决定这一个 30 Å 晶胞内势的取样密度；增加网格点数并不会增加薄层之间的真空距离。检查平台有没有被取样清楚，与增大晶胞后平台值是否稳定，是两项不同的检查。

## 沿法向平均并选择真空平台

平面平均就是在每个固定 z 层上，对 56 × 56 个点求算术平均。随例子提供的 `plane_average.py` 会先读结构和网格，检查标量块是否完整，再写出 `PLANAR_AVERAGE.dat`。它只读取本例的第一个标量势块；磁性或非共线输出要先确认各块代表的物理量。

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
这份输出的费米能为 −1.2958 eV。若要继续计算两个表面的功函数，需要各自使用同一份计算中的真空平台与这个费米能相减；下一步接 [功函数](/Atlas/m/workfunction/vasp/)。电荷转移方向和接触后的带型还需结合差分电荷与带边对齐。

<span id="把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
## 电势平均与平台统计

下面的读取规则用于从 LOCPOT 重建平面平均势，并分别统计两侧平台。电子势已用 eV 表示，不再按密度文件除以体积。

```text
按本例现有程序拆成两步，用 Python 3 处理 HfCl₂/PbO₂ 平面平均势。
第一步 plane_average.py 仅使用标准库，读取 LOCPOT 和命令行窗口 2:5、25:28；按 x 最快顺序读取第一标量块，核对正的结构缩放因子、三维正整数网格和完整标量数，逐 z 层平均，对每个非空窗口求均值、标准差与范围。输出 PLANAR_AVERAGE.dat 和 potential-summary.json，后者记录源文件 SHA256、网格、法向高度和窗口统计。
第二步 plot_potential.py 使用 NumPy、Matplotlib，读取上述 dat/json，并从同目录 atlas_plot_style.py 导入绘图样式；保留整个晶胞曲线，标出两侧窗口和窗口均值，输出 potential-z.png、potential-z.pdf。命令依次为 python3 plane_average.py LOCPOT 2:5 25:28 和 python3 plot_potential.py。
INCAR/OUTCAR 由读者核对，两个脚本不解析它们：本例 LVHAR 对应离子势加 Hartree 势，LOCPOT 数值单位为 eV，不除晶胞体积。预期网格 56×56×480，共 1,505,280 个标量，法向高度 30 Å、层间隔 0.0625 Å；两个窗口各 49 点，均值约 2.538191/5.029000 eV，范围均 <0.0003 eV。这些数值用于对照本例输出；现有提取程序没有额外的有限值检查。
若延伸计算功函数，由读者从同一 OUTCAR 读取 EF=−1.2958 eV，再与各侧平台配对相减。提供完整源码、依赖与运行命令。
```

## 后处理源码与运行

完整源码：[plane_average.py](/Atlas/examples/vasp/hfcl2_pbo2_potential/plane_average.py) · [plot_potential.py](/Atlas/examples/vasp/hfcl2_pbo2_potential/plot_potential.py) · [atlas_plot_style.py](/Atlas/examples/vasp/hfcl2_pbo2_potential/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

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
<summary>plot_potential.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
x,y=np.loadtxt('PLANAR_AVERAGE.dat',unpack=True)
s=json.load(open('potential-summary.json'))
fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
ax.plot(x,y,color='#25313c',lw=1.4)
for n,w in enumerate(s['windows']):
    ax.axvspan(w['lo_A'],w['hi_A'],color=['#009e73','#d55e00'][n%2],alpha=.14)
    ax.hlines(w['mean_eV'],w['lo_A'],w['hi_A'],color=['#009e73','#d55e00'][n%2],lw=2,label='Window %d: %.4f eV'%(n+1,w['mean_eV']))
ax.set(xlabel='Distance normal to the layer (Angstrom)',ylabel='Planar-averaged potential (eV)')
ax.legend(frameon=False)
ax.grid(alpha=.18)
fig.savefig('potential-z.png',dpi=220)
fig.savefig('potential-z.pdf')
```

</details>

解压本页示例包后，在 `hfcl2-pbo2-potential` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 plane_average.py LOCPOT 2:5 25:28
python3 plot_potential.py
```

本例保存的提取运行记录如下：

```text
[bcgong@localhost hfcl2_pbo2_potential]$ python plane_average.py LOCPOT 2:5 25:28
grid = 56 56 480; scalar values = 1505280
normal height = 30.0000000000 A; output = PLANAR_AVERAGE.dat
window 2.00:5.00 A  N=49  mean=2.538190946 eV  std=7.76333e-05 eV  range=0.000294251 eV
window 25.00:28.00 A  N=49  mean=5.029000094 eV  std=7.61576e-05 eV  range=0.000291275 eV
```

已有 [PLANAR_AVERAGE.dat](/Atlas/examples/vasp/hfcl2_pbo2_potential/PLANAR_AVERAGE.dat) 和 [potential-summary.json](/Atlas/examples/vasp/hfcl2_pbo2_potential/potential-summary.json) 时，直接执行 `python3 plot_potential.py`；第一条命令用于从原始 LOCPOT 重提取平台统计。

只重画已有结果时，把 `PLANAR_AVERAGE.dat`、`potential-summary.json`、`plot_potential.py` 和 `atlas_plot_style.py` 放在本机同一目录。脚本读第一列作横轴、第二列作纵轴，把两个统计窗口涂成浅色，并同时输出 PNG 与 PDF。图上保留整个晶胞，才能同时检查原子区、两侧平台和周期边界。

![非对称薄层两侧的平面平均势](/Atlas/examples/vasp/hfcl2_pbo2_potential/potential-z.png)

## 文献中平面平均静电势与界面电荷的对齐画法

平面平均电势与侧视结构可以共用法向坐标，便于比较势的变化和原子层位置。两者必须使用同一坐标原点与长度单位，不能为了让势谷与原子重合而挪动曲线。势谷也不必严格落在原子平面上：平均后的势由离子与电子分布共同决定。图中另标两侧真空平台及所取窗口，功函数还需同一次计算的电子化学势。

<figure class="research-figure"><img src="/Atlas/figures/literature/M3_ElectrostaticPotential_OverlaidStructure_ZrI2_Zhang2025_Fig4.jpg" alt="平面平均静电势直接叠加在异质结侧视原子结构模型上的对齐图件" loading="lazy"/><figcaption>六种 ZrI<sub>2</sub> 基异质结沿法向 <em>z</em> 的平面平均静电势 <em>V</em><sub>eff</sub>(<em>z</em>) 曲线直接叠加在侧视原子结构模型上，清楚标示各原子层势阱位置及两侧真空能级差。引自 Zhang 等人，<em>Phys. Chem. Chem. Phys.</em> <strong>27</strong>, 19410 (2025)，Fig. 4，<a href="https://doi.org/10.1039/D5CP02349A" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D5CP02349A</a>。</figcaption></figure>

另一类常见表达是将平面平均静电势 V<sub>eff</sub>(Z) 与平面平均差分电荷密度 Δρ(Z) 左右并排放置，共用垂直方向的法向坐标轴 Z，以便在同一位置对照电荷积累、耗尽区域与电势变化。

<figure class="research-figure"><img src="/Atlas/figures/literature/M3_Veff_and_DeltaRho_SharedZ_ZrI2_NbS2_Huang2025_Fig4a.jpg" alt="共用垂直 Z 轴的平面平均静电势与平面平均差分电荷密度并排对照图" loading="lazy"/><figcaption>ZrI<sub>2</sub>/NbS<sub>2</sub> 异质结的平面平均静电势 <em>V</em><sub>eff</sub>(<em>Z</em>) 与平面平均差分电荷密度 Δρ(<em>Z</em>) 共用垂直 <em>Z</em> 轴并排对齐展示，并叠加三维差分电荷密度等值面与侧视原子结构。引自 Huang 等人，<em>J. Phys. Chem. C</em> <strong>129</strong>, 11654 (2025)，Fig. 4a，<a href="https://doi.org/10.1021/acs.jpcc.5c02913" target="_blank" rel="noopener noreferrer">DOI: 10.1021/acs.jpcc.5c02913</a>。</figcaption></figure>

下一步也可接 [能带对齐](/Atlas/m/band-alignment/vasp/)。比较两种材料前，还要准备各自一致的能带边与势参考。

```text
固定几何的 SCF
  └─ LVHAR → LOCPOT → 平面平均势
                         ├─ 两侧真空平台 → 功函数
                         └─ 一致的能量参考 → 能带对齐
```
