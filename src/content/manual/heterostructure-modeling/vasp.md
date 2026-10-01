界面能带、电荷转移和层间振动，都对应一份具体的界面结构。两层用了什么面内晶格、怎样配准、层间距从哪里量起，先在模型里说清楚，后面的数值才有共同的参照。这里沿用一份六原子 SnSe₂/Sr₂N 共同晶胞，保持层内几何和侧向配准，把法向间隙设为 3.000 Å，再核对层厚、最近距离和周期空白。这个例子用于学习构型处理；ZrCl₂/Sc₂C 应使用自己的已接受结构和单层参照。

前置操作见 [POSCAR 与电子自洽](/Atlas/m/scf/vasp/) 和 [离子弛豫](/Atlas/m/relax/)。[下载三份结构与完整检查程序](/Atlas/examples/interface-magnet-heterostructure-modeling/example-pack.tar.gz)，解压后进入 `example-pack`。这些文件保留了一次真实的几何操作，没有为 3.000 Å 模型附加能量或优化结果。

## 从共同晶胞辨认两层

先保留源文件，读取元素顺序和所有坐标。

```text
[bcgong@localhost heterostructure]$ cat POSCAR.reference
11                                      
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
   Sn   Se   N    Sr
     1     2     1     2
Direct
  0.0000000000000000  0.0000000000000000  0.5940212009837095
  0.6666666670000012  0.3333333329999988  0.6325735570448590
  0.3333333329999988  0.6666666670000012  0.5481899174149424
  0.6666666670000012  0.3333333329999988  0.4539734079959168
  0.0000000000000000 -0.0000000000000000  0.4934254572360981
  0.3333333329999988  0.6666666670000012  0.4248064611244732
```

标题 `11` 是原文件中的标记，不是原子数。真正的元素与数量在第六、七行：Sn、Se、N、Sr 分别为 1、2、1、2 个，总数为 6。前三个坐标属于 SnSe₂，后三个属于 Sr₂N；换坐标顺序时必须同步维护元素计数与 POTCAR 顺序。

三条晶格矢量定义了共同的周期单元。前两条长度约 3.9501 Å、夹角约 120°，第三条沿 z，长度约 39.4022 Å。本例没有重新寻找公度超胞，而是沿用这个已存在的共同晶胞，专门演示如何改层间距而不误改层内结构。

`Direct` 坐标的第三列要乘以第三晶格矢量才是长度。比如 0.01 在此晶胞中对应约 0.3940 Å，不能把分数坐标增加 0.1 当作移动 0.1 Å。

原文件中的两层占据 z≈16.74–24.92 Å。SnSe₂ 最下方的 Se 在 21.59988 Å，Sr₂N 最上方的 Sr 在 19.44204 Å，它们的 z 差给出法向间距 2.15784 Å。两个原子的平面位置不同，所以三维距离更长。

## 刚性移动两层并将双层居中

这次采用 3.0 Å 作为新模型的法向间距，并把整个异质层居中。操作前先复制原文件：

```text
[bcgong@localhost heterostructure]$ cp POSCAR.reference POSCAR.gap3p0
[bcgong@localhost heterostructure]$ vi POSCAR.gap3p0
```

两层相对拉开的距离为 3.0 − 2.1578395444 = 0.8421604556 Å，分给两层各一半；再把原来的外边界中点从 20.8315430 Å 平移到晶胞中点 19.7010939 Å。合并这两步后，SnSe₂ 的三个分数 z 坐标统一减去 0.0180032870679758，Sr₂N 的三个分数 z 坐标统一减去 0.0393767311013565。虽然两层最终都向下移动了，下面一层移动得更多，两层间距因此增大。

在 vi 中只改标题和第三列，保留面内坐标与晶格矢量。保存后立刻读回：

```text
[bcgong@localhost heterostructure]$ cat POSCAR.gap3p0
SnSe2/Sr2N: rigid layers, normal gap 3.0 A, recentered
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
   Sn   Se   N    Sr
     1     2     1     2
Direct
  0.0000000000000000  0.0000000000000000  0.5760179139157336
  0.6666666670000012  0.3333333329999988  0.6145702699768831
  0.3333333329999988  0.6666666670000012  0.5301866303469666
  0.6666666670000012  0.3333333329999988  0.4145966768945603
  0.0000000000000000  -0.0000000000000000  0.4540487261347416
  0.3333333329999988  0.6666666670000012  0.3854297300231167
```

现在上层三个原子仍共享同一个位移，下层三个原子也共享同一个位移，层内的相对坐标没有变化。只移动其中一个原子，会同时改变层厚和键长；只改晶胞高度却保留全部分数坐标，则会连层内长度也一起缩放。这两种操作都与这里的刚性层平移不同。

## 读回坐标，检查层厚、镜像和面内参考

下载包的 `check_model.py` 重新读取两份 POSCAR，把分数坐标转成笛卡尔坐标，并用 a×b 定义层法向。它核对 6 个原子的种类和数量、面内坐标、层内刚性位移、法向间距、最短跨层距离和周期镜像之间的空白区间。最短距离包含相邻周期单元，避免只比较当前文件内的原子配对。

```text
[bcgong@localhost heterostructure]$ python check_model.py
reference: atoms=6 a=3.9501156207 b=3.9501156194 gamma=120.000000 height=39.4021877938 A
  normal gap=2.1578395444 A; nearest interlayer distance=3.1396511419 A; empty interval=31.2157096630 A
  layer thickness: SnSe2=3.3249000154 A; Sr2N=2.7037385710 A; slab center=20.8315430227 A
gap3p0: atoms=6 a=3.9501156207 b=3.9501156194 gamma=120.000000 height=39.4021877938 A
  normal gap=3.0000000000 A; nearest interlayer distance=3.7684397028 A; empty interval=30.3735492074 A
  layer thickness: SnSe2=3.3249000154 A; Sr2N=2.7037385710 A; slab center=19.7010938969 A
cell unchanged; fractional x/y unchanged; both layers moved rigidly
fractional c shifts SnSe2/Sr2N = -0.0180032870679758 -0.0393767311013565
relative to SnSe2 reference: a extension=2.69629289%; b extension=2.69629286%; a-axis rotation=0.0000000022 deg
Wrote model-check.json, reference-atoms.csv and gap3p0-atoms.csv
```

新模型的法向间距正好为 3.0000000000 Å，跨层最近距离为 3.7684397028 Å。SnSe₂ 层厚仍为 3.3249000154 Å，Sr₂N 层厚仍为 2.7037385710 Å；晶格和分数 x/y 的最大变化均为零。这样才能确认改动的是层间关系。

输出中的 `empty interval` 是相邻周期异质层之间没有原子的完整区间，原模型约 31.2157 Å，新模型约 30.3735 Å。晶胞高度保持不变，层间距增加使整个双层变厚，留给周期镜像之间的空白就会减少。39.4022 Å 是晶胞高度，不能直接把它写成真空厚度。

新模型整体居中后，最低和最高原子到两个边界的距离相等。这个几何条件方便后续设置层法向和偶极修正，但真空是否足以收敛功函数、能量或声子，仍需针对所算物理量检验。

还要说明面内晶格是相对什么参考选的。本例同时保存了一份已有的独立 SnSe₂ 单层 POSCAR：

```text
[bcgong@localhost heterostructure]$ head -8 POSCAR.SnSe2.reference
"Sn1 Se2"                               
   1.00000000000000     
     3.8464052687627550    0.0000000000015396    0.0000000000000001
    -1.9232026344298054    3.3310846760065127   -0.0000000000000002
     0.0000000000000007   -0.0000000000000005   18.3572978035193977
   Sn   Se
     1     2
Direct
```

这份单层参考的 a≈3.8464052688 Å，而共同晶胞的 a≈3.9501156207 Å。按 (a_common/a_reference − 1)×100% 计算，SnSe₂ 相对这份参考的两个面内方向均伸长约 2.69629%。这是有明确参考文件的几何比较；它不能替代两种材料在同一计算协议下的平衡晶格与应变能检验。

共同晶胞的第一矢量与这份 SnSe₂ 参考的第一矢量几乎平行，数值角度约 2×10⁻⁹ 度。这里没有额外施加相对转角，面内堆垛也保持了原文件的配准关系。这个检查说明本次操作没有意外旋转或滑移，本次模型沿用一个配准关系；扭角或不同堆垛需另建模型比较。

`reference-atoms.csv` 和 `gap3p0-atoms.csv` 将元素、层归属以及笛卡尔坐标展开，便于绘图时检查颜色和标签对应是否正确。

```text
[bcgong@localhost heterostructure]$ cat gap3p0-atoms.csv
index,element,layer,x_A,y_A,z_A,normal_A
1,Sn,SnSe2,-5.760179139157337e-17,1.1520358278314673e-16,22.696366016727577,22.696366016727577
2,Se,SnSe2,1.9750578125446223,1.140300157064481,24.215413190144233,24.215413190144233
3,Se,SnSe2,-1.5505510739310572e-09,2.280600317397634,20.890513174717974,20.890513174717974
4,N,Sr2N,1.9750578125446223,1.1403001570644808,16.33601612170426,16.33601612170426
5,Sr,Sr2N,-4.540487261347416e-17,9.080974522694832e-17,17.890513174717974,17.890513174717974
6,Sr,Sr2N,-1.550551059455367e-09,2.280600317397634,15.186774603702489,15.186774603702489
```

使用 Python 标准库执行 `python3 check_model.py`，即可从真实 POSCAR 重建几何表。若用 VESTA 复核，在 File → Open 分别打开 `POSCAR.reference` 与 `POSCAR.gap3p0`，显示相邻面内周期像，再从俯视和侧视检查配准与镜像空白；软件自动绘制的键不作为成键判据。

最后把准备好的模型复制到独立计算目录，不覆盖原文件：

```text
[bcgong@localhost heterostructure]$ mkdir -p model_d3p0
[bcgong@localhost heterostructure]$ cp POSCAR.gap3p0 model_d3p0/POSCAR
```

```text
[bcgong@localhost heterostructure]$ ls -lh POSCAR.reference POSCAR.gap3p0 model_d3p0/POSCAR
-rw-r--r-- 1 bcgong bcgong 705 Sep 22 22:42 model_d3p0/POSCAR
-rw-r--r-- 1 bcgong bcgong 705 Sep 22 22:36 POSCAR.gap3p0
-rw-r--r-- 1 bcgong bcgong 691 Sep 22 21:43 POSCAR.reference
```

## 将几何结果接到构型选择

上面的核对给出两项直接结果：法向间隙由 2.15784 Å 改为 3.00000 Å，两层内部厚度分别保持 3.32490 与 2.70374 Å。共同晶胞相对于所附独立 SnSe₂ 参考有约 2.69629% 的面内伸长。最近跨层距离、法向间隙和晶胞高度是三个不同的量，能量扫描必须始终用同一个距离定义。

要选择一个供后续电子结构和声子计算使用的界面，需要比较有明确侧向位移、相对转角和层间距的候选。若候选使用相同的面内晶胞，可在相同约束下优化原子，再用同一静态协议比较总能量。若候选的共同晶胞也变化，单层应变能随之变化，不能把所有总能量差都解释成层间作用。

Bu 与 Sun 的 [WS₂/Sc₂C 研究](https://doi.org/10.1039/D5CP01402F)在正文 §3.1、Fig. 2 给出六种配准，Fig. 3 比较它们随层间距变化的能量；Fig. 5(a)进一步检查所选 F-I 配准的面内晶格。这里采用的是“先说明配准，再比较距离，最后核对共同晶胞”的分析顺序。文献的最低能构型和晶格属于 WS₂/Sc₂C，不能替代本例的 SnSe₂/Sr₂N 数值，也不能决定 ZrCl₂/Sc₂C 的堆垛。

## 单层参照决定结合能的含义

把选定界面记为 AB，上层为 A，下层为 B。在同一个晶胞中保留 AB 的 A 原子、移去 B，就得到冻结 A 参考；B 参考按相反操作得到。两份单层保留各自在 AB 中的原子位置、面内应变和周期高度，独立完成电子自洽。删除原子时同时修改元素数量和对应 PAW 顺序；不能只删坐标而沿用 AB 的计数和 POTCAR。

三份计算的泛函、相同元素的 PAW、截断能、k 网格、展宽、色散模型和电荷/自旋约定要配套。AB 含两层的全部电子，A 与 B 各自取所定义的电子数和自旋态；电子数加和应与 AB 一致。密度差还需要 [相同的 FFT 网格](/Atlas/m/delta-charge/vasp/)。相同网格便于能量比较，但它本身不能消除单层电荷、自旋或色散设置不相容的问题。

这时可定义冻结几何相互作用能：

$$
\Delta E_{\mathrm{int}}^{\mathrm{frozen}}
=E_{AB}(R_A,R_B;C)-E_A(R_A;C)-E_B(R_B;C),
\qquad
e_{\mathrm{int}}=\frac{\Delta E_{\mathrm{int}}^{\mathrm{frozen}}}{|\mathbf a\times\mathbf b|}.
$$

$C$ 表示共同晶胞，$R_A,R_B$ 是界面中的坐标。三份能量都用同一输出字段，例如 VASP 的 `energy without entropy`；有有限展宽时还应成组检查展宽依赖。单位可以报告 eV/界面胞或 meV/Å²，并注明周期胞包含的界面数。对这里的真空隔开的双层，一胞包含一个目标 A–B 接触，不套用表面能的二倍面积因子。

按这个符号约定，负值说明该固定构型相对于所选冻结单层参照降低了电子能量。若把分离代价定义为 $E_A+E_B-E_{AB}$，符号相反；两种写法都可以，正文和图注必须一致。

若改用分别优化的自由单层作参照，得到的量还包括单层从自由状态变到界面状态的形变代价：

$$
\Delta E_{\mathrm{assemble}}
=\Delta E_{\mathrm{int}}^{\mathrm{frozen}}
+[E_A(R_A;C)-E_A^{\mathrm{free}}]
+[E_B(R_B;C)-E_B^{\mathrm{free}}].
$$

中括号内包含相应的面内应变与层内结构改变。所附 `POSCAR.SnSe2.reference` 有不同的晶胞高度和面内长度，它适合说明几何伸长，不能直接顶替冻结 A 的能量。选择哪一种参照，取决于是在量化既定界面的层间作用，还是研究两张自由单层组装的代价。

文献 §3.1 的 $E_b=E_{\mathrm{hetero}}-E_{\mathrm{layer1}}-E_{\mathrm{layer2}}$ 给出了三能差的符号约定。本教程进一步把冻结参照与自由单层参照写开，便于读者判断各自包括哪些几何变化。式中的同胞冻结要求是这里的比较协议，不声称原文已经逐项报告这些细节。

本例随包提供的是结构与几何表。没有与该界面匹配的 AB/A/B 能量组，因此这里结束在“模型已构造并核对”，不报告界面结合能数值。已有 [H₂ 差分电荷例子](/Atlas/m/delta-charge/vasp/)可帮助理解保留原位的 A/B 构造，但分子的三能差不能作为层状界面的结合能。

## 重建几何表

`check_model.py` 读取正缩放、Direct 坐标的三份 POSCAR，按 $\mathbf a\times\mathbf b$ 定义法向，把分数坐标转为 Å，再检查每层共同位移、面内坐标、最近跨层距离和周期空白。程序输出 JSON 和逐原子 CSV，不改写原结构。可以把处理需求写成：

```text
用 Python 3 标准库读取 POSCAR.reference、POSCAR.gap3p0、POSCAR.SnSe2.reference。
此例限定正缩放系数、Direct 坐标及六原子的 SnSe2/Sr2N 顺序。以 a×b 为法向，
核对晶胞和分数 x/y 不变、每层刚性移动、3.000 Å 间隙与整体居中；
枚举相邻周期像求跨层最近距离，报告层厚、空白区间和相对 SnSe2 参考的伸长。
写 model-check.json、reference-atoms.csv、gap3p0-atoms.csv。
不支持的输入或核对失败应退出；不由几何距离自动判断成键或最低能构型。
```

[完整源码](/Atlas/examples/interface-magnet-heterostructure-modeling/check_model.py)

<details>
<summary>check_model.py 的完整源码</summary>

```python
from __future__ import print_function
import math,sys,json,csv,itertools,hashlib,os

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a,a))
def read_poscar(name):
    s=open(name).readlines(); scale=float(s[1])
    if scale<=0:raise ValueError('Positive POSCAR scale required')
    cell=[[float(x)*scale for x in row.split()[:3]] for row in s[2:5]]
    species=s[5].split();counts=list(map(int,s[6].split()))
    if len(species)!=len(counts):raise ValueError('Species/count mismatch')
    if not s[7].strip().lower().startswith('d'):raise ValueError('This example expects Direct coordinates')
    f=[list(map(float,row.split()[:3])) for row in s[8:8+sum(counts)]]
    if len(f)!=sum(counts) or any(len(row)!=3 for row in f):raise ValueError('Incomplete atomic coordinates')
    if any(not 0<=row[2]<1 for row in f):raise ValueError('Unwrap/recenter fractional c coordinates first')
    syms=[el for el,n in zip(species,counts) for _ in range(n)]
    xyz=[[sum(row[i]*cell[i][j] for i in range(3)) for j in range(3)] for row in f]
    n=cross(cell[0],cell[1]);n=[x/norm(n) for x in n]
    height=dot(cell[2],n)
    if height<=0:raise ValueError('Expected right-handed slab cell')
    return cell,f,xyz,syms,n,height

def analyze(name,label):
    cell,f,xyz,symbols,n,height=read_poscar(name)
    if sorted(symbols)!=sorted(['Sn','Se','Se','N','Sr','Sr']):raise ValueError('Expected SnSe2/Sr2N six-atom model')
    zz=[dot(row,n) for row in xyz]
    a=[i for i,x in enumerate(symbols) if x in ['Sn','Se']];b=[i for i,x in enumerate(symbols) if x in ['Sr','N']]
    za=[zz[i] for i in a];zb=[zz[i] for i in b]
    if min(za)<=max(zb):raise ValueError('Expected separated SnSe2 upper layer and Sr2N lower layer')
    def dist(i,j):
        return min(norm([sum((f[i][k]-f[j][k]+shift[k])*cell[k][d] for k in range(3)) for d in range(3)]) for shift in itertools.product([-1,0,1],repeat=3))
    report={'file':os.path.basename(name),'sha256':hashlib.sha256(open(name,'rb').read()).hexdigest(),'n_atoms':len(symbols),'a_A':norm(cell[0]),'b_A':norm(cell[1]),'gamma_deg':math.degrees(math.acos(dot(cell[0],cell[1])/norm(cell[0])/norm(cell[1]))),'normal_height_A':height,'normal_gap_A':min(za)-max(zb),'minimum_interlayer_distance_A':min(dist(i,j) for i in a for j in b),'empty_interval_A':height-max(zz)+min(zz),'slab_center_normal_A':(max(zz)+min(zz))/2,'SnSe2_thickness_A':max(za)-min(za),'Sr2N_thickness_A':max(zb)-min(zb),'cell':cell}
    with open(label+'-atoms.csv','w') as out:
        w=csv.writer(out);w.writerow(['index','element','layer','x_A','y_A','z_A','normal_A'])
        for i,(el,row) in enumerate(zip(symbols,xyz)):w.writerow([i+1,el,'SnSe2' if el in ['Sn','Se'] else 'Sr2N']+row+[zz[i]])
    return report,(cell,f,xyz,symbols,n,height)

if __name__=='__main__':
    before,old=analyze('POSCAR.reference','reference')
    after,new=analyze('POSCAR.gap3p0','gap3p0')
    ref=read_poscar('POSCAR.SnSe2.reference')
    shift_by_layer=[]
    for ids in [[0,1,2],[3,4,5]]:
        shifts=[new[1][i][2]-old[1][i][2] for i in ids]
        if max(shifts)-min(shifts)>1e-12:raise ValueError('Layer was not moved rigidly')
        shift_by_layer.append(shifts[0])
    maxcell=max(abs(x-y) for a,b in zip(old[0],new[0]) for x,y in zip(a,b))
    maxxy=max(abs(old[1][i][j]-new[1][i][j]) for i in range(6) for j in [0,1])
    if maxcell>1e-12 or maxxy>1e-12:raise ValueError('Unexpected cell or lateral-registry change')
    if abs(after['normal_gap_A']-3)>1e-10:raise ValueError('Target gap was not attained')
    if abs(after['slab_center_normal_A']-after['normal_height_A']/2)>1e-10:raise ValueError('Slab is not centered')
    comp={'max_cell_change_A':maxcell,'max_fractional_xy_change':maxxy,'rigid_fractional_c_shifts_SnSe2_Sr2N':shift_by_layer,'SnSe2_reference_a_A':norm(ref[0][0]),'SnSe2_reference_b_A':norm(ref[0][1]),'SnSe2_a_extension_percent':100*(after['a_A']/norm(ref[0][0])-1),'SnSe2_b_extension_percent':100*(after['b_A']/norm(ref[0][1])-1),'a_vector_angle_to_SnSe2_reference_deg':math.degrees(math.atan2(new[0][0][1],new[0][0][0])-math.atan2(ref[0][0][1],ref[0][0][0]))}
    json.dump({'reference':before,'gap3p0':after,'comparison':comp},open('model-check.json','w'),indent=2)
    for label,r in [('reference',before),('gap3p0',after)]:
        print('%s: atoms=%d a=%.10f b=%.10f gamma=%.6f height=%.10f A'%(label,r['n_atoms'],r['a_A'],r['b_A'],r['gamma_deg'],r['normal_height_A']))
        print('  normal gap=%.10f A; nearest interlayer distance=%.10f A; empty interval=%.10f A'%(r['normal_gap_A'],r['minimum_interlayer_distance_A'],r['empty_interval_A']))
        print('  layer thickness: SnSe2=%.10f A; Sr2N=%.10f A; slab center=%.10f A'%(r['SnSe2_thickness_A'],r['Sr2N_thickness_A'],r['slab_center_normal_A']))
    print('cell unchanged; fractional x/y unchanged; both layers moved rigidly')
    print('fractional c shifts SnSe2/Sr2N = %.16f %.16f'%tuple(shift_by_layer))
    print('relative to SnSe2 reference: a extension=%.8f%%; b extension=%.8f%%; a-axis rotation=%.10f deg'%(comp['SnSe2_a_extension_percent'],comp['SnSe2_b_extension_percent'],comp['a_vector_angle_to_SnSe2_reference_deg']))
    print('Wrote model-check.json, reference-atoms.csv and gap3p0-atoms.csv')
```

</details>

在解包后的 `example-pack` 中运行 `python3 check_model.py`。实际结果见上面的终端输出和 [model-check.json](/Atlas/examples/interface-magnet-heterostructure-modeling/model-check.json)。用 VESTA 打开两份真实 POSCAR，从俯视比较侧向配准，从侧视检查层厚与周期像；自动绘制的键仅用于显示。

同胞冻结 A/B 参照准备好后，可继续 [差分电荷](/Atlas/m/delta-charge/vasp/)；需要研究从多层表面取走一层的代价，则进入 [层间分离](/Atlas/m/exfoliation-energy/vasp/)。后者改变的是多层参考中的一个界面，与两张自由单层组装的参照不同。

[VASP POSCAR](https://vasp.at/wiki/POSCAR) · [ISIF](https://vasp.at/wiki/ISIF) · [展宽能量字段](https://vasp.at/wiki/Smearing_technique) · [VESTA 手册](https://jp-minerals.org/vesta/en/doc.html)
