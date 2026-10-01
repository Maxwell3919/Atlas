界面两侧的能量参考与势变化，要从整条法向势曲线读。先区分LOCPOT里存的是离子+Hartree势还是包含交换关联的总局域势，再沿层面平均；真空平台、原子区域与偶极修正跳变各有位置。本例用已有六原子HfCl₂/PbO₂固定几何存档演示这一读取方法，z晶胞30 Å。它提供势后处理的数据链，材料电子态与稳定性另按相应计算判断。

[金属/Ca₂N/MoS₂原文 Sec. 2.2和Fig. 6(b)](https://doi.org/10.1039/D4CP04577G)采用离子+Hartree势的xy平均，描述相对于EF的势峰与隧穿区域；[ZrI₂/Dirac半金属原文 Fig. 4](https://doi.org/10.1039/D5CP02349A)则把法向势与层位置共同呈现。这些例子告诉我们曲线需要什么参考和坐标，不把其接触结论移到本例。

前置 [SCF](/Atlas/m/scf/vasp/)。[下载原始LOCPOT、输入输出与源码](/Atlas/examples/vasp/hfcl2-pbo2-potential-electronic-files.tar.gz)，进入 `hfcl2-pbo2-potential`。

## 同一次静态计算的势与电子态

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

```text
[bcgong@localhost hfcl2_pbo2_potential]$ cat KPOINTS
HfCl2/PbO2 vacuum convergence 15x15x1
0
Gamma
15 15 1
0 0 0
```

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

LVHAR=.TRUE.写离子势+Hartree势，单位eV；LVTOT还含交换关联势。LDIPOL修正局域势与力，IDIPOL=3选择第三晶格矢量方向；本例c沿z且垂直a、b平面，因此修正方向与层法向一致，DIPOL给参考中心。NSW=0表示固定几何，最后电子步达1E−7 eV，程序有完整计时。参数与输出的组合确认这份势的来源。[LVHAR](https://vasp.at/wiki/LVHAR) · [LOCPOT](https://vasp.at/wiki/LOCPOT) · [IDIPOL](https://vasp.at/wiki/IDIPOL) · [LDIPOL](https://vasp.at/wiki/LDIPOL)。

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

56×56×480共1,505,280个势值，x最快。每个固定z平面平均56×56个值，不像CHGCAR再除体积。法向间隔为30/480 Å；增加采样点数与增加真空厚度解决不同问题。

## 平面平均后，平台按左右分别读取

V̄(z)=S⁻¹∫S V(x,y,z)dxdy。对一般a、b平面，S=|a×b|，法向高度H=Vcell/S，zₖ=kH/nz。这里c正好垂直层面，脚本使用的|c|=30 Å与H一致；若c倾斜，不能用|c|替代H，也不能直接照搬这里的IDIPOL方向。平面平均保留法向变化，没有把原子区势谷滑动抹平。

源格式、单位、平台窗口和处理步骤明确后，可以使用以下写码需求：

```text
按本例现有程序拆成两步，用 Python 3 处理 HfCl₂/PbO₂ 平面平均势。
第一步 plane_average.py 仅使用标准库，读取 LOCPOT 和命令行窗口 2:5、25:28；按 x 最快顺序读取第一标量块，核对正的结构缩放因子、三维正整数网格和完整标量数，逐 z 层平均，对每个非空窗口求均值、标准差与范围。输出 PLANAR_AVERAGE.dat 和 potential-summary.json，后者记录源文件 SHA256、网格、法向高度和窗口统计。
第二步 plot_potential.py 使用 NumPy、Matplotlib，读取上述 dat/json，并从同目录 atlas_plot_style.py 导入绘图样式；保留整个晶胞曲线，标出两侧窗口和窗口均值，输出 potential-z.png、potential-z.pdf。命令依次为 python3 plane_average.py LOCPOT 2:5 25:28 和 python3 plot_potential.py。
INCAR/OUTCAR 由读者核对，两个脚本不解析它们：本例 LVHAR 对应离子势加 Hartree 势，LOCPOT 数值单位为 eV，不除晶胞体积。预期网格 56×56×480，共 1,505,280 个标量，法向高度 30 Å、层间隔 0.0625 Å；两个窗口各 49 点，均值约 2.538191/5.029000 eV，范围均 <0.0003 eV。这些数值用于对照本例输出；现有提取程序没有额外的有限值检查。
若延伸计算功函数，由读者从同一 OUTCAR 读取 EF=−1.2958 eV，再与各侧平台配对相减。提供完整源码、依赖与运行命令。
```

完整 [plane_average.py](/Atlas/examples/vasp/hfcl2_pbo2_potential/plane_average.py)读取标量势；[plot_potential.py](/Atlas/examples/vasp/hfcl2_pbo2_potential/plot_potential.py)与[样式模块](/Atlas/examples/vasp/hfcl2_pbo2_potential/atlas_plot_style.py)读派生结果画整胞曲线。数值分析使用Python标准库，绘图需要NumPy/Matplotlib。

```bash
python3 -m pip install numpy matplotlib
python3 plane_average.py LOCPOT 2:5 25:28
python3 plot_potential.py
```

```text
[bcgong@localhost hfcl2_pbo2_potential]$ python plane_average.py LOCPOT 2:5 25:28
grid = 56 56 480; scalar values = 1505280
normal height = 30.0000000000 A; output = PLANAR_AVERAGE.dat
window 2.00:5.00 A  N=49  mean=2.538190946 eV  std=7.76333e-05 eV  range=0.000294251 eV
window 25.00:28.00 A  N=49  mean=5.029000094 eV  std=7.61576e-05 eV  range=0.000291275 eV
```

两侧窗口2–5 Å与25–28 Å各有49个平面，平均势分别约2.538191、5.029000 eV，窗口内起伏不到0.0003 eV。两侧平台差约2.490809 eV，表示这份非对称薄层两侧真空参考不同。原子约在11–19 Å，窗口避开原子和周期边界的偶极修正跳变；另一结构需要重选区间。

![本例完整法向势及两侧真空窗口](/Atlas/examples/vasp/hfcl2_pbo2_potential/potential-z.png)

图中的原子区势阱、平台和边界必须在同一个坐标轴上读。平台内的range/std是空间起伏，不能作为多次计算的统计误差或真空高度收敛证明。

```text
[bcgong@localhost hfcl2_pbo2_potential]$ head -5 PLANAR_AVERAGE.dat
# z_A  planar_potential_eV
0.0000000000 3.783714602193
0.0625000000 3.303792300942
0.1250000000 2.899977063405
0.1875000000 2.631753663237
```

```text
[bcgong@localhost hfcl2_pbo2_potential]$ grep 'E-fermi' OUTCAR
 E-fermi :  -1.2958     XC(G=0):  -3.9262     alpha+bet : -3.9672
```

EF=−1.2958 eV应与同次计算的平台组合，进入 [功函数](/Atlas/m/workfunction/vasp/) 的逐侧取差。直接取z=0一行会误读修正区域；绝对势零点本身可变，有意义的是同一参照下的差。

## 与差分电荷共同看界面偶极

[ZrI₂原文 Fig. 4、5](https://doi.org/10.1039/D5CP02349A)分别给势与差分密度。对自己的匹配AB/A/B数据，先按 [CDD](/Atlas/m/delta-charge/vasp/) 得Δn̄(z)、SΔn̄(z)和累计层电子数，再把势曲线与它们共用原子位置及z原点。图上积累与耗尽的分离能提示偶极形成在哪里；势谷位置、单个势峰或两侧真空差，都不能直接换算成层转移电子数。

若求界面诱导的势差，三份LOCPOT必须采用相同的势组成（例如都为离子+Hartree势），并先处理各自的势零点和边界条件；不同计算的任意常数需先按物理参考对齐，不能简单逐点相减三份未经对齐的LOCPOT。电子数密度差带正号表示积累，实际电荷为−eΔn；LOCPOT的eV势是电子势能参照，不能未经符号和单位转换就把曲线斜率叫作电场。定量偶极/电场需要另明确电荷密度、边界条件和规范。

金属/Ca₂N/MoS₂论文把势峰相对EF定义为隧穿高度、交点距离定义为宽度；它与半导体CBM/VBM形成的Schottky势垒不同。这里已有输出支持两侧真空读数，尚未给本例划出经能带验证的界面势垒。需要接触能级时继续 [能级对齐](/Atlas/m/band-alignment/vasp/)。


## 完整源码与执行记录

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

<details>
<summary>同一算例的其余输入、检查命令与保存输出</summary>

```text
[bcgong@localhost hfcl2_pbo2_potential]$ ls -lh INCAR POSCAR KPOINTS OUTCAR OSZICAR LOCPOT
-rw-r--r-- 1 bcgong bcgong  324 Sep  4 05:07 INCAR
-rw-r--r-- 1 bcgong bcgong   60 Sep  4 05:07 KPOINTS
-rw-r--r-- 1 bcgong bcgong  27M Sep  4 05:14 LOCPOT
-rw-r--r-- 1 bcgong bcgong 3.8K Sep  4 05:14 OSZICAR
-rw-r--r-- 1 bcgong bcgong 223K Sep  4 05:14 OUTCAR
-rw-r--r-- 1 bcgong bcgong  512 Sep  4 05:07 POSCAR
```

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

```text
固定几何的 SCF
  └─ LVHAR → LOCPOT → 平面平均势
                         ├─ 两侧真空平台 → 功函数
                         └─ 一致的能量参考 → 能带对齐
```

</details>
