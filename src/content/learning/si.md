从一份 Si 输入到两张电子结构图，最容易混淆的是三件事：计算胞中的两个原子怎样代表整块晶体，k 点怎样代表电子态的不同空间周期，以及同一份自洽密度为什么还要分出能带与 DOS 两条支路。本页用 Preston 上真实运行的 QE 7.5 把它们接起来：金刚石 Si，两原子原胞，固定晶格 10.20 bohr，PBE 超软赝势，无自旋极化、无 SOC（自旋–轨道耦合）。PBE 指本例采用的交换关联近似；下文的数字都属于这套固定结构和设置。

## 先读一次 SCF 的完整输出

先打开 [Si SCF 的完整输入与运行过程](/Atlas/m/scf/qe/)。SCF 是电子自洽计算：给定原子与晶胞，用电子密度生成有效势，求电子态，再由占据的态更新密度，反复进行直到误差低于指定阈值。原子和晶胞在本次 `calculation='scf'` 中保持固定。输入中的结构片段是：

```text
  ibrav = 2
  A = 5.397607551
  nat = 2
  ntyp = 1
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
```

### 两个原子怎样构成周期晶体

晶格描述可重复的平移，原子基元描述每个重复单元内部放什么。这里 `ibrav=2` 规定面心立方（FCC）的平移晶格，两个 Si 的相对位置与它共同构成金刚石结构。`nat=2` 是计算胞内两个原子，`ntyp=1` 是只有一种原子类型。将这个单元沿三条晶格矢量平移，就得到无限周期晶体。

`A` 以 Å 给出常规立方胞边长 a，输出换算为 `alat=10.2000 a.u.`；这里 a.u. 的长度单位是 bohr。实际原胞的三条边并非三条长为 a 的直角边。[原 OUT](/Atlas/examples/si-pbe/scf/scf.out)给出：

```text
     crystal axes: (cart. coord. in units of alat)
               a(1) = (  -0.500000   0.000000   0.500000 )
               a(2) = (   0.000000   0.500000   0.500000 )
               a(3) = (  -0.500000   0.500000   0.000000 )
```

这三条矢量张成的体积是 a³/4，对应输出中的 `265.3020 bohr³`。原胞是能生成整个晶体的最小平移单元，本例含 2 个 Si；边长 a 的常规立方胞体积为它的 4 倍，含 8 个 Si。原胞有利于减少计算量，常规胞便于看出立方对称性。

`ATOMIC_POSITIONS alat` 的三列是以 a 为单位的**笛卡尔坐标**，因此第二个 Si 在 (a/4,a/4,a/4)。`crystal` 则表示沿三条原胞矢量的分数坐标。本例原胞基矢下，同一位置可写成 `(-0.25,0.75,-0.25)`；直接把 `alat` 改成 `crystal` 而保留 `(0.25,0.25,0.25)`，原子就移到了另一个位置。坐标与单位的约定可核对 [QE 7.5 的 ibrav、A 与 ATOMIC_POSITIONS 说明](https://github.com/QEF/q-e/blob/qe-7.5/PW/Doc/INPUT_PW.def)。

超胞是在原胞的基础上扩大周期。若将这三条原胞矢量各加倍并完整复制原子，2×2×2 原胞超胞就含 16 个 Si、体积变为 8 倍。无缺陷的重复仍描述同一个晶体，但总能量和态数按更大的计算胞累计，能带也会折叠到更小的布里渊区。加入缺陷或位移后，超胞还规定了缺陷或位移在空间中多久重复一次。因此后面比较能量和 DOS 时，要先确认“每胞”到底是哪一个胞。

### 从价电子数读懂占据带

赝势用有效离子势处理原子核与芯电子的作用，只把选定的价电子显式纳入求解。本例的超软赝势（USPP）在输出中标为 `Zval=4.0`，每个 Si 提供 4 个价电子，两个原子合计 8 个。这里的 8 不是两个 Si 的全部核外电子数。SCF 输出相邻几行正好可以互相核对：

```text
     number of electrons       =         8.00
     number of Kohn-Sham states=            4
     highest occupied level (ev):     6.3971

!    total energy              =     -22.83859230 Ry
     estimated scf accuracy    <          4.3E-11 Ry
     convergence has been achieved in   9 iterations
```

Kohn–Sham 态是用来构建密度的有效单电子态。它的本征值随 k 改变，连起来就是一条能带；同一条带在不同 k 点有不同能量。本例无自旋极化，一条填满的带按自旋简并容纳每原胞 2 个电子，4 条占据带对应 8 个价电子。后续 `nbnd=8` 会再求 4 条未占据带，电子数仍是 8；增加空带是为了看到导带，既不增加原子也不掺入电子。NSCF 打印的占据数 `1 1 1 1 0 0 0 0` 采用自己的计数约定，不能脱离自旋简并与 k 权重解释成“只有 4 个电子”。

`-22.83859230 Ry` 是整原胞的总能量，包含电子与离子等各项贡献；`6.3971 eV` 是最高占据的单电子能级。两者含义和单位都不同，总能量也不是占据本征值的简单相加。读能带要选共同的能量零点，比较结构稳定性则要比较相同协议、明确组成和参考态的总能量。

本次电子自洽在 9 次迭代后达到 `conv_thr=1.0d-10 Ry`。两个原子的力在打印精度内为零，晶胞压力却为 38.45 kbar：电子求解完成后，固定胞仍可能偏离零压体积。力与压力的用途在后面的结构分支继续说明。

后续程序读取 `tmp/si.save` 的密度、XML 和所需波函数。公开[算例包](/Atlas/examples/si-pbe-lesson-files.tar.gz)保留输入、OUT、XML 和后处理数据，未打包密度与波函数；阅读存档可以直接进行，复算须先生成自己的 SCF 保存目录。

## 再比较数值设置引起的变化

### 截断能与 k 网格分别细化什么

周期晶体中的电子态用平面波展开。对每个 k，平面波具有 k+G 的波矢，其中 G 是倒格矢；`ecutwfc` 限制纳入展开的平面波动能。增大它是在同一个采样位置改进描述电子态的基组。`ecutrho` 则控制密度与势的展开，本例超软赝势还要处理增广电荷，因此单独检验密度截断能。这里的 60/640 Ry 是波函数/密度截断，不是两种电子能级。

倒格矢由实空间晶格矢量定义，满足 $\mathbf a_i\cdot\mathbf b_j=2\pi\delta_{ij}$；$\delta_{ij}$ 在 i=j 时为 1，否则为 0。实空间沿晶格矢量平移，电子态的相位由 k 决定；彼此只相差一个倒格矢的 k 可以用等价的周期描述。布里渊区是倒空间中的一个基本区域。对它取样，才能把不同 k 的电子态按权重合起来得到密度或态数分布。

本例 OUT 把倒格矢写成以下数值，实际长度还要乘以 `2π/alat`：

```text
     reciprocal axes: (cart. coord. in units 2 pi/alat)
               b(1) = ( -1.000000 -1.000000  1.000000 )
               b(2) = (  1.000000  1.000000  1.000000 )
               b(3) = ( -1.000000  1.000000 -1.000000 )
```

`K_POINTS automatic` 的 `8 8 8 0 0 0` 沿三条倒格矢各取 8 份，三个 0 指不加半步偏移。完整网格有 512 个点；利用本结构的对称性，SCF 实际只需算 29 个不可约点，其权重代表完整网格。它们既不是 29 个原子，也不是 29 条能带。增加 k 网格是在更多倒空间位置求解，增大截断能是在各位置改进平面波展开，两种操作不能相互代替。

超胞变大时倒格矢缩短，沿扩大方向使用相同网格数会获得更密的物理采样；缺陷也可能降低对称性，使不可约点数增加。由此比较两次计算的 k 采样，既要看网格整数，也要看晶胞、偏移和实际倒空间间距。参数约定见 [QE 7.5 的 ecutwfc、ecutrho 和 K_POINTS](https://github.com/QEF/q-e/blob/qe-7.5/PW/Doc/INPUT_PW.def)。

### 用同一结构比较差值

[收敛测试](/Atlas/m/convergence/qe/)在同一结构上分别改变 `ecutwfc`、`ecutrho` 和均匀 k 网格，给出从实际 OUT 提取的总能量表。原始能量单位是 Ry/整胞；本例要转换到 meV/atom，用 1 Ry = 13.605693122994 eV，再除以 2 个原子。

例如 8³ 与本组最后一个 14³ 点的能量分别为 `-22.83859230` 和 `-22.83887935 Ry`。差值 `0.00028705 Ry/cell` 换算后为 `1.952757 meV/atom`。同样相对各组最后一点，60 Ry 波函数截断的差值为 `0.137758 meV/atom`，480 Ry 密度截断为 `0.003197 meV/atom`。这些数值来自[现存扫描表](/Atlas/examples/si-pbe/convergence.csv)，所用参照分别是 80 Ry、640 Ry、14³，不能把不同组的最后一点当成同一组联合设置。

如果暂以相对末点 1 meV/atom 来读本组数据，8³ 尚未达到这个示例标准；这并不与上文电子自洽完成矛盾。自洽阈值约束一次求解的迭代误差，参数扫描检查有限基组与采样改变后目标量是否稳定。完整提取需求、Python 源码、实际输出及现有 gnuplot 图均在收敛页，参照也保持为有限扫描末点。

三组最低设置来自独立扫描，没有组合运行。迁移到界面问题时，直接检查关心的结合能、层间距、电荷积分、带边或声子频率；Si 的总能量选点不能接替那些物理量的检查。

## 从同一密度分出路径与均匀网格

已有匹配的 SCF 密度后，可以保持这个有效势，在新的 k 点求本征态。这一步不会通过密度混合再次建立自洽密度。路径能带和均匀网格 NSCF 都从这里分出，分别复制父保存目录，保留对应 `prefix/outdir`：

```text
Si SCF：8³ 网格，2 原子，8 电子，4 条占据带
  ├─ bands-cg：高对称路径，121 点，8 条带
  │    └─ bands.x → si.bands.dat.gnu → 路径能带
  └─ gap24-cg：24³ 均匀网格，413 个不可约点，8 条带
       ├─ 全部采样点的本征值 → 采样带边
       └─ dos.x → si.dos.dat → DOS 与累计态数
```

### 在路径图里找位置，在均匀网格里统计态数

读色散时，进入[路径能带](/Atlas/m/bands/qe/)；读布里渊区积分的态分布时，进入[均匀网格 NSCF](/Atlas/m/nscf/qe/)，再接 [DOS](/Atlas/m/dos/qe/)。路径能带不需要先跑 DOS 的均匀 NSCF。

路径图中的 Γ 是 k=0，X、W、K、L 是本 FCC 晶格的高对称位置。这里 `tpiba_b` 用 `2π/a` 为单位的笛卡尔坐标给出节点；其第四列控制到下一个节点的取点数。均匀网格中的权重用来积分，路径节点后的数字用来展开线段，两者用途不同。程序依照输入中的 7 个节点展开为 121 个实际点。

![Si 原有路径能带：横轴 Γ–X–W–K–Γ–L–X，纵轴相对路径价带顶的能量 eV](/Atlas/examples/si-pbe-electronic/plots/bands-direct.svg)

这张现有图来自 [si.bands.dat.gnu](/Atlas/examples/si-pbe/bands-cg/si.bands.dat.gnu)，8 个数据块分别是一条带，每块有 121 行。横轴沿实际 k 坐标累加距离，不能把点编号均匀排开：Γ→X 长度是 1，X→W 是 0.5，单位都是 `2π/a`，所以图中前一段确实比后一段长。两个 Γ 是同一个倒空间点，在累计路径上出现了两次。

纵轴减去本路径最高占据带的最大值，称为路径价带顶（VBM），数值为 `6.3970 eV`。未占据带的最低处称为导带底（CBM）。图上价带顶在 Γ，而低导带谷在 Γ→X 段、接近 X；两者 k 不同，说明本路径显示的是间接带隙。这里线按输出带号相连；在交叉或简并处追踪轨道身份，需进一步看投影。[原作图源码和依赖](/Atlas/m/bands/qe/#h-后处理源码与运行)保留了节点位置与单位检查。

能量零点只是选定参考后整体平移，本征值差保持不变。本例没有真空平台参照，也没有用金属的费米能作为零点。DOS 表头虽然写着 `EFermi=6.397 eV`，绘图仍明确采用同一采样的 VBM。对有带隙的本例，仅凭这个表头不能认定费米能必须固定在价带顶；跨材料比较带边还需要共同的参考。

![Si 原有总 DOS：24³ 均匀 NSCF，Gaussian 展宽 0.01 Ry，横轴相对 VBM 的能量 eV，纵轴 states/eV/cell](/Atlas/examples/si-pbe-electronic/plots/dos.svg)

DOS 是每单位能量区间内的态数分布，将均匀网格的能级按 k 权重累计。本例 [dos.in](/Atlas/examples/si-pbe/dos-cg/dos.in)指定 Gaussian 展宽 `degauss=0.01 Ry`，约为 0.136057 eV；能量表的步长 `DeltaE=0.02 eV` 决定横轴取点间距。一个控制谱线展宽，一个控制输出采样间隔。[QE 7.5 的 dos.x 说明](https://github.com/QEF/q-e/blob/qe-7.5/PP/Doc/INPUT_DOS.def)逐项列出单位。

图中峰高表示这个能区累积了较多态，面积才给出一个能窗内的态数；DOS 丢失了每个态的具体 k 位置，不能凭峰高把它对应为某一条路径线。纵轴的 cell 是两原子原胞，总 DOS 已包含自旋简并。若改成每原子，应将纵轴和累计态数都除以 2；若拿 16 原子超胞比较，须先按相同原子数或化学式归一。

原始 [si.dos.dat](/Atlas/examples/si-pbe/dos-cg/si.dos.dat) 的三列是能量（eV）、DOS（states/eV/cell）和累计态数（states/cell）。带隙中点附近的第三列为 8，对应四条占据带；积分到 16 eV 则约为 15.97，已把所求空态累计进去。Gaussian 尾部使 VBM 位置的累计数约为 7.997，DOS 图上带边也变得平滑。因此精确带隙要从本征值取，不能用人为的 DOS 峰高阈值截取。

### 用现存文件核对两条分支

先检查 OUT 的退出信息与本征值警告，再查 XML 中的电子数、带数和 k 点数。存档保留早先本征值未收敛的原输出及独立 CG（共轭梯度求解器）复算；本页两图采用 CG 分支。NSCF 不再自洽密度，每个 k 点的本征值仍需数值收敛，`JOB DONE.` 本身不足以排除 `eigenvalues not converged`。完整检查在[均匀 NSCF 页](/Atlas/m/nscf/qe/)。

后处理的逻辑也可以直接核对：先确认两条分支的规模，再从均匀网格的第 4、5 带寻找最大价带能与最小导带能，最后检查 DOS 的积分。均匀网格 XML 中能量是 Hartree，转换到 eV 才能与 `.gnu` 和 DOS 的 eV 比较；OUT 中总能量则是 Ry，不能共用同一个换算因子。下面程序只读取文件，不启动 DFT，不写回数据。

可以把这份具体需求和算例包交给编程助手：

```text
用 Python 3 标准库检查 si-pbe 中 scf、bands-cg、gap24-cg 的 data-file-schema.xml。
核对 nks、nbnd、nelec；仅解析本例无自旋极化的 output/band_structure。
从 gap24-cg 的全部 ks_energies 读第4带最大值和第5带最小值，XML Hartree 转 eV。
把 bands-cg/si.bands.dat.gnu 按空行分块，检查8块、各121点、相同横坐标。
从 dos-cg/si.dos.dat 读三列，检查有限值、单调能量和0.02 eV步长。
梯形积分与累计末值比较；在带隙中点附近读累计态数，保留展宽尾部。
打印检查摘要，不重标定DOS，不把路径带边当作全区带边，不写回原文件。
```

在解压后的 `si-pbe` 根目录，复制运行这段完整代码即可，无额外 Python 包依赖：

```bash
python3 - <<'PY'
from pathlib import Path
import math
import xml.etree.ElementTree as ET

def band_xml(folder):
    root = ET.parse(Path(folder) / 'data-file-schema.xml').getroot()
    assert root.attrib['Units'] == 'Hartree atomic units'
    b = root.find('output/band_structure')
    nks, nbnd = (int(b.find(key).text) for key in ('nks', 'nbnd'))
    nelec = float(b.find('nelec').text)
    rows = b.findall('ks_energies')
    assert len(rows) == nks
    values = [[float(x) * 27.211386245988
               for x in row.find('eigenvalues').text.split()] for row in rows]
    assert all(len(row) == nbnd and all(map(math.isfinite, row)) for row in values)
    print(f'{folder}: nks={nks}, nbnd={nbnd}, nelec={nelec:g}')
    return values

band_xml('scf')
band_xml('bands-cg')
e = band_xml('gap24-cg')
vbm = max(row[3] for row in e)
cbm = min(row[4] for row in e)
print(f'Uniform mesh: VBM={vbm:.6f}, CBM={cbm:.6f}, gap={cbm-vbm:.6f} eV')

blocks, current = [], []
for line in Path('bands-cg/si.bands.dat.gnu').read_text().splitlines() + ['']:
    if line.strip():
        current.append(tuple(map(float, line.split())))
    elif current:
        blocks.append(current)
        current = []
assert len(blocks) == 8 and all(len(b) == 121 for b in blocks)
assert all(len(p) == 2 and all(map(math.isfinite, p)) for b in blocks for p in b)
assert all([p[0] for p in b] == [p[0] for p in blocks[0]] for b in blocks)
assert all(q[0] > p[0] for p, q in zip(blocks[0], blocks[0][1:]))
path_vbm = max(p[1] for p in blocks[3])
print(f'Path: {len(blocks)} bands x {len(blocks[0])} points; VBM={path_vbm:.4f} eV')

dos = [tuple(map(float, line.split()))
       for line in Path('dos-cg/si.dos.dat').read_text().splitlines()
       if line.strip() and not line.lstrip().startswith('#')]
assert len(dos) == 1201 and all(len(row) == 3 for row in dos)
assert all(all(map(math.isfinite, row)) for row in dos)
assert all(abs(q[0] - p[0] - 0.02) < 1e-9 for p, q in zip(dos, dos[1:]))
area = sum((q[0]-p[0]) * (p[1]+q[1]) / 2 for p, q in zip(dos, dos[1:]))
mid = min(dos, key=lambda row: abs(row[0] - (vbm+cbm)/2))
print(f'DOS: {len(dos)} rows; step=0.02 eV; integral={area:.8f}; stored end={dos[-1][2]:.2f}')
print(f'Gap midpoint nearest row: E={mid[0]:.2f} eV; cumulative={mid[2]:.4f} states/cell')
PY
```

本轮从公开原文件实际读取的输出为：

```text
scf: nks=29, nbnd=4, nelec=8
bands-cg: nks=121, nbnd=8, nelec=8
gap24-cg: nks=413, nbnd=8, nelec=8
Uniform mesh: VBM=6.397029, CBM=6.937159, gap=0.540130 eV
Path: 8 bands x 121 points; VBM=6.3970 eV
DOS: 1201 rows; step=0.02 eV; integral=15.97326485; stored end=15.97
Gap midpoint nearest row: E=6.66 eV; cumulative=8.0000 states/cell
```

均匀网格读到的 `VBM=6.397029 eV`、`CBM=6.937159 eV` 相差约 `0.540130 eV`。价带顶在 Γ，采样导带底在 `(0,0.833333,0)`，坐标单位为 `2π/a`。它支持本次有限采样的间接带隙判断；更细的搜索和父密度比较见[带隙](/Atlas/m/band-gap/qe/)。已有 12³、18³、24³ 对照并不严格单调，因为网格可能恰好命中或错过导带谷底。加密子网格还不能消除父 SCF 密度误差，不能仅因曲线更平滑就接受全区带边已收敛。

<figure>
<div>
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig2ab.png" alt="Qiu2022原文Fig.2(a,b)：以 E_F=0 对读 Γ–M–K–Γ 能带和总/投影 DOS；红虚线与蓝实线比较有、无 SOC。" />
</div>
<figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，第 3 页 Fig. 2(a,b)：以 E_F=0 对读 Γ–M–K–Γ 能带和总/投影 DOS；红虚线与蓝实线比较有、无 SOC。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文原文</a>。</figcaption>
</figure>

这两幅图也提供了阅读材料论文的起点。[Ba₂N 原文第 165101-3 页 Fig. 2(a,b)](https://doi.org/10.1103/PhysRevB.105.165101)把同样的两类信息并列：(a)沿 Γ–M–K–Γ 画能带，纵轴 Energy(eV) 以费米能为零，红虚线和蓝实线比较有、无 SOC；(b)横轴 Energy(eV)、纵轴 DOS(states/eV)，比较总 DOS 与投影分量。论文中的带穿过零能，本站 Si 图的零能却是 VBM。先核对参考与占据情况，才判断金属性；路径、标签和零点都由各自结构与计算确定，不能整套照搬。界面中哪些态来自哪一层，还需对应投影和空间密度，不能只从总 DOS 的增减推算电荷转移。

### 按论文的两栏画法重绘本例

Fig. 2(a,b) 值得采用的是把“态出现在哪里”和“各能区有多少态”放在相邻面板，保留清楚的高对称节点、相同能量参考和显式单位。论文对 SOC 的比较用了实/虚线，对总 DOS 和投影用了黑、蓝、红、绿线；若只有本例这一套无 SOC 的总 DOS，就只画实际已有的数据。未来加上投影时，保持同一能量网格、零点与每胞归一，不能把每条分量都拉成相同峰高。

已有 Si 两图可以按这个思路在 gnuplot 中并排重绘：左栏仍保留路径累计距离，右栏以能量为横轴，像论文 Fig. 2(b) 一样显示 DOS；两栏统一减去本例均匀网格 VBM。`.gnu` 能量只印到四位小数，与 XML 的参考有约 0.000029 eV 的打印差。这里只减去同一参考，不作插值平滑、额外展宽或峰高归一。绘图前运行上面的核对代码，绘图后检查 Γ 两处的带顶和 DOS 横轴的零线，再核对路径节点。

在 `si-pbe` 根目录，把下面的完整源码保存为 `si-read.gnu`。数据直接来自 `.gnu` 与 DOS 表，不依赖 Python 作图；本轮用 gnuplot 6.0 patchlevel 0 复现。组合面板与 SVG 输出的参数可查 [gnuplot 6.0 官方手册](https://www.gnuplot.info/docs_6.0/Gnuplot_6.pdf) 中的 `multiplot` 和 `svg` 条目。

```gnuplot
if (!exists("datadir")) datadir = "."
if (!exists("output_file")) output_file = "si-bands-dos.svg"
vbm = 6.397028955497
set encoding utf8
set terminal svg size 1200,500 font "Arial,14" noenhanced
set output output_file
set border 3 linewidth 1
set tics out nomirror
unset key
set multiplot layout 1,2 margins 0.07,0.98,0.15,0.88 spacing 0.12,0.04
set title "(a) Si bands: fixed cell, PBE, no SOC"
set xlabel "Path distance (2π/a)"
set ylabel "Energy - VBM (eV)"
set xrange [0:4.6463]
set yrange [-13:8]
set xtics ("Γ" 0, "X" 1, "W" 1.5, "K" 1.8536, "Γ" 2.9142, "L" 3.7802, "X" 4.6463)
set ytics 5
set grid xtics lc rgb "#dddddd" linewidth 0.6
set arrow 1 from graph 0,first 0 to graph 1,first 0 nohead dt 2 lc rgb "#555555"
plot datadir."/bands-cg/si.bands.dat.gnu" using 1:($2-vbm) with lines lw 1.2 lc rgb "#0072b2"
unset arrow 1
unset grid
set title "(b) Si DOS: 24³ mesh, Gaussian 0.01 Ry"
set xlabel "Energy - VBM (eV)"
set ylabel "DOS (states/eV/cell)"
set xrange [-13:8]
set yrange [0:2.1]
set xtics 5
set ytics 0.5
set arrow 1 from first 0,graph 0 to first 0,graph 1 nohead dt 2 lc rgb "#555555"
plot datadir."/dos-cg/si.dos.dat" using ($1-vbm):2 with lines lw 1.4 lc rgb "#222222"
unset multiplot
unset output
print "Wrote ".output_file
```

```bash
gnuplot si-read.gnu
```

在算例根目录执行时会输出 `Wrote si-bands-dos.svg`。本轮复现时将同一脚本的 `datadir` 指向公开算例、`output_file` 指向 section 检查目录，原数据保持只读；生成结果已核对节点、零点、单位和两栏线型。本站上方仍保留原有图及其完整[能带源码](/Atlas/examples/si-pbe-electronic/plot_bands.py)、[DOS 源码](/Atlas/examples/si-pbe-electronic/plot_si.py)和[共同样式依赖](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)。没有取得论文作者的绘图程序，以上重绘只借鉴图中可见的表达方式。

## 用力与应力判断结构处在什么条件下

力描述能量随原子位移的变化，应力描述能量随晶胞形变的变化；压力是应力张量的各向同性部分。Si 固定胞输出中的两原子零力与 `P=38.45 kbar` 可以同时成立：对称位置的原子没有移动趋势，晶胞体积却仍偏离这套协议的零压条件。更紧的电子阈值不能代替改变晶胞，几何优化也不能代替数值收敛扫描。

[固定晶胞弛豫](/Atlas/m/relax/qe/)把第二个 Si 移开后用 BFGS（根据能量和力更新结构的优化算法）找回内部坐标，保留末态力及更紧电子阈值的静态复核。它可以说明固定胞优化怎样停止；平衡体积由另一份完整的 [fcc Al 变胞算例](/Atlas/m/vc-relax/qe/#al-vc-relax)演示。规定面内应变或界面共同晶格时，应保留那些条件，只开放相应内部自由度。

## 接到声子与材料分析

声子描述周期晶体的小振动，q 是振动在相邻晶胞间变化的波矢，区别于前文电子态的 k；Γ 振动对应 q=0。动力学矩阵把力对位移的响应与原子质量联系起来，本征值给出频率平方，本征矢给出各原子的相对运动。两原子原胞在每个 q 有 6 个振动模式；Γ 点的整体平移应对应零频，数值残差可能使其略偏离零。

Si 的 [Γ 点虚频对照](/Atlas/m/imaginary-phonon/qe/)从六个原始频率读取振动响应，再比较同一矩阵的 ASR（声学求和规则，用于约束整体平移）处理；它练习平移残差的判读。Al 的[DFPT 声子](/Atlas/m/phonon-dfpt/qe/)用密度泛函微扰理论计算小扰动响应，后续 EPC 分析电子–声子耦合，即振动与电子态的相互作用。Al 使用自己的最终几何和金属协议，两份小体系的结构、密度与赝势分别保留。

<figure>
<div class="figure-panels">
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig3a.png" alt="Qiu2022原文Fig.3(a)：声子频率沿 Γ–M–K–Γ 的色散，红点大小正比于线宽 γ。" />
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig3d.png" alt="Qiu2022原文Fig.3(d)：约 55 cm⁻¹ 的 Γ 光学模俯视/侧视：上下 Ba 层作相反的面内运动。" />
</div>
<figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，第 3 页 Fig. 3(a)：声子频率沿 Γ–M–K–Γ 的色散，红点大小正比于线宽 γ。；第 3 页 Fig. 3(d)：约 55 cm⁻¹ 的 Γ 光学模俯视/侧视：上下 Ba 层作相反的面内运动。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文原文</a>。</figcaption>
</figure>

读这些图时，可对照 [Ba₂N 原文 Fig. 3(a,d)，第 165101-3 页](https://doi.org/10.1103/PhysRevB.105.165101)：(a)以 Γ–M–K–Γ 高对称路径为横轴、cm⁻¹ 频率为纵轴，红点大小表示声子线宽；(d)给出 Γ 附近约 55 cm⁻¹ 的两个光学模式，顶视与侧视的箭头显示 Ba 原子在面内相向运动，箭头长度表示相对振幅。先在频率图中定位模式，再看本征矢的原子和方向，才把谱上的特征与几何运动联系起来。本站 Si 页已有真实 Γ 模动画，可按原子和振动方向阅读；它只覆盖 Γ 点和本例的 ASR 对照，没有论文那套全路径线宽。结构、频率和模式展示的具体文件与方法留在对应分析页，不在这份基础导航中借用论文曲线。

到这里，结构、密度、路径本征态与均匀积分各自回答的问题已经能对应到具体文件。回到[性质目录](/Atlas/?open=1)，按界面结构、电子密度、电荷转移或声子/EPC 的问题接续实际材料分析。
