DFT+U 的使用取决于具体材料的局域关联与参数依据。下面 VGe₂P₄ 的一份真实 SCF 用于读懂作用轨道和 Ueff 回显；它没有为当前研究材料提供可转移的 U 值。

局域 d 轨道的占据会影响带隙、磁矩和电子态；DFT+U 通过对这些轨道的占据矩阵加入能量修正来改变自洽解。本例读取 VGe₂P₄ 的一份静态结果，用 Dudarev 形式把 Ueff=U−J=3 eV 加到 V 的 d 轨道，核对元素顺序、轨道与程序读入参数，再读取电子迭代、能量和磁矩。这份记录回答指定 Ueff 下实际算出了什么；Ueff 对该材料性质的影响还需同协议的多点比较。

[Hubbard U 高通量研究](https://doi.org/10.1038/s41524-024-01503-3)的 Computational methods 中 Eq. (1) 定义 Ueff=U−J，Eq. (2) 写出占据矩阵修正 Ueff Tr(ρ−ρ²)/2；它解释了为什么要核对受修正的元素和轨道。计算采用 GPAW，并对指定 3d 元素使用 Ueff=4 eV；这些选择没有为本例 VGe₂P₄ 的 3 eV 提供材料专属标定。VASP 的对应实现见 [LDAUTYPE=2](https://vasp.at/wiki/LDAUTYPE)。

[下载本例的输入与原始输出](/Atlas/examples/interface-magnet-dft-plus-u/example-pack.tar.gz)。包内 `INCAR.active` 仅去除了原输入的注释，计算参数原样保留，附原文件哈希；复制为 INCAR 即可读入。归档未保存原提交脚本、CHGCAR 或 WAVECAR，因此这里使用 OUTCAR 核验已结束的 SCF，提交方法接 [SCF](/Atlas/m/scf/vasp/)。

## 将元素顺序对应到 U 的作用轨道

VASP 静态计算的文件与操作见 [SCF](/Atlas/m/scf/vasp/)。进入复制出来的计算目录后，先读 POSCAR，再核对 U。

```text
[bcgong@localhost vge2p4_u3]$ head -16 POSCAR
POSCAR                                  
   1.00000000000000     
     2.8149939055363911    0.0000000000000003    0.0000000000000000
    -1.4074969527681953    2.4378562356984528   -0.0000000000000000
     0.0000000000000000   -0.0000000000000000   29.4512358517314254
   V    Ge   P 
     1     2     4
Direct
  0.0000000000000000  0.0000000000000000  0.5000000000000000
  0.6666666870000029  0.3333333429999996  0.6541508807422820
  0.6666666870000029  0.3333333429999996  0.3458491192577181
  0.6666666870000029  0.3333333429999996  0.5605945852015912
  0.6666666870000029  0.3333333429999996  0.4394054147984089
  0.3333333429999996  0.6666666870000029  0.7349860889032125
  0.3333333429999996  0.6666666870000029  0.2650139110967873
```
第六行的元素顺序是 `V Ge P`，下一行的原子数是 `1 2 4`。INCAR 中 `LDAUL`、`LDAUU`、`LDAUJ` 的三个位置都跟这个顺序对应；`MAGMOM` 则要展开成七个原子的初始磁矩。

```text
[bcgong@localhost vge2p4_u3]$ grep -Ev '^[[:space:]]*(#|$)' INCAR
SYSTEM  = VGe2P4_scf
ENCUT   = 520      # 和 relax 保持一致（暂定）
EDIFF   = 1E-6
ISMEAR  = 0
SIGMA   = 0.05
ISPIN   = 2
NELM    = 120
LCHARG  = .TRUE.
LWAVE   = .TRUE.
LDAU    = .TRUE.
LDAUTYPE= 2
LDAUL   = 2 -1 -1      # V Ge P
LDAUU   = 3.0 0.0 0.0
LDAUJ   = 0.0 0.0 0.0
MAGMOM  = 1*2.0 2*0.1 4*0.0
ISIF    = 2
LASPH   = .TRUE.
```
`LDAUTYPE = 2` 使用 Dudarev 形式，这时有意义的组合是 U − J。本例 V 的数值是 3 − 0 = 3 eV；`LDAUL = 2 -1 -1` 表示只对 V 的 d 轨道加这一项，Ge 和 P 不加。`MAGMOM = 1*2.0 2*0.1 4*0.0` 给的是初始条件，最终磁矩仍要从收敛输出读出来。

`LASPH = .TRUE.` 保留 PAW 球内密度梯度的非球形贡献。这里对 V 的 d 轨道使用 DFT+U，这个设置会影响势、能带与总能量；做同一 U 下的磁构型比较时，应在各目录中保持一致。[LASPH 官方说明](https://vasp.at/wiki/LASPH)

U 的取值应依据文献协议、独立计算或敏感性研究。改变 U 会改变能量泛函，因此不能把不同 U 的总能量排在一起，以最低者选择“最佳 U”。可以观察带隙、磁矩等量怎样随 U 改变；磁态或结构之间的能量排序则应在相同的 U − J 下比较。`EDIFF` 只控制电子循环的停止条件，不决定 U 的物理取值。[LDAUTYPE 的能量比较说明](https://vasp.at/wiki/LDAUTYPE)

```text
[bcgong@localhost vge2p4_u3]$ cat KPOINTS
K-Spacing Value to Generate K-Mesh: 0.025
0
Gamma
  18  18   1
0.0  0.0  0.0
```
这次固定结构 SCF 使用 Γ 中心 18 × 18 × 1 网格。若要检查 U 对带隙、磁矩等量的影响，应在不加 U 的对照中保留相同结构、赝势、截断能、展宽和 k 网格。比较磁态能量则仍按上一段所述，在同一 U 下进行。

## 读取实际参数和电子收敛结果

```text
[bcgong@localhost vge2p4_u3]$ grep -A3 'LDA+U is selected' OUTCAR
 LDA+U is selected, type is set to LDAUTYPE =  2
   angular momentum for each species LDAUL =     2   -1   -1
   U (eV)           for each species LDAUU =   3.0  0.0  0.0
   J (eV)           for each species LDAUJ =   0.0  0.0  0.0
```
这段是程序读入参数后的回显，已经把 `LDAUTYPE = 2`、各元素的 l、U 与 J 写出来了。只在 INCAR 里看见 `LDAU = .TRUE.` 还不够；应当检查这一段是否与预期一致。

```text
[bcgong@localhost vge2p4_u3]$ head -8 OSZICAR
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1     0.429957043731E+03    0.42996E+03   -0.31480E+04  9072   0.172E+03
DAV:   2     0.479829596538E+01   -0.42516E+03   -0.40318E+03  9492   0.422E+02
DAV:   3    -0.349698840372E+02   -0.39768E+02   -0.39509E+02 11620   0.905E+01
DAV:   4    -0.360306295688E+02   -0.10607E+01   -0.10606E+01  9940   0.155E+01
DAV:   5    -0.360657628363E+02   -0.35133E-01   -0.35133E-01 12992   0.295E+00    0.252E+01
DAV:   6    -0.353472830584E+02    0.71848E+00   -0.19261E+01 12012   0.160E+01    0.804E+00
DAV:   7    -0.421168924339E+02   -0.67696E+01   -0.65047E+01 12572   0.145E+01    0.150E+01
```
OSZICAR 每一条 DAV 行是一次电子迭代：依次记录能量、相邻迭代能量变化、波函数残差等。它与最下面的离子步摘要是不同层次。固定几何的计算仍然会有一条 `1 F=...`，这个 1 不代表结构做过一次有效优化。

```text
[bcgong@localhost vge2p4_u3]$ tail -7 OSZICAR
DAV:  26    -0.340985351321E+02   -0.56191E-02   -0.44178E-05 11536   0.142E-02    0.177E-02
DAV:  27    -0.340991323552E+02   -0.59722E-03   -0.16916E-05 10696   0.108E-02    0.625E-03
DAV:  28    -0.340992725958E+02   -0.14024E-03   -0.44292E-06 10528   0.561E-03    0.298E-03
DAV:  29    -0.340992994665E+02   -0.26871E-04   -0.12861E-06 10248   0.323E-03    0.208E-03
DAV:  30    -0.340993026995E+02   -0.32330E-05   -0.16672E-07  8708   0.142E-03    0.115E-03
DAV:  31    -0.340993033925E+02   -0.69305E-06   -0.34108E-08  9520   0.662E-04
   1 F= -.34099303E+02 E0= -.34096946E+02  d E =-.471526E-02  mag=     0.5781
```
```text
[bcgong@localhost vge2p4_u3]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
最后一步的能量变化约 −6.93 × 10⁻⁷ eV，已经进入 `EDIFF = 1E-6` 的范围；OUTCAR 同时确认停止条件达到。末行的 `mag=0.5781` 是这份计算的最终总磁矩摘要，不能拿输入里 2.0、0.1、0.0 的初值代替它。

```text
[bcgong@localhost vge2p4_u3]$ grep -E 'free  energy|energy  without entropy|E-fermi' OUTCAR | tail -3
 E-fermi :   2.4194     XC(G=0):  -6.8213     alpha+bet : -7.9488
  free  energy   TOTEN  =       -34.09930339 eV
  energy  without entropy=      -34.09458813  energy(sigma->0) =      -34.09694576
```
`TOTEN` 是有限展宽下的自由能，`energy(sigma->0)` 是程序给出的零展宽外推量；同一比较要统一选用能量定义。这里 `E-fermi = 2.4194 eV` 只属于本份势参考，不能直接与另一份独立计算的费米能做绝对比较。

```text
[bcgong@localhost vge2p4_u3]$ tail -15 OUTCAR
  
 General timing and accounting informations for this job:
 ========================================================
  
                  Total CPU time used (sec):      124.456
                            User time (sec):      113.656
                          System time (sec):       10.800
                         Elapsed time (sec):      125.728
  
                   Maximum memory used (kb):      281700.
                   Average memory used (kb):           0.
  
                          Minor page faults:        62427
                          Major page faults:            0
                 Voluntary context switches:          847
```
## 接能带或 DOS 前重新准备 CHGCAR

程序统计段表明这份计算结束，电子收敛行说明它没有仅仅跑满 NELM。但文件里还保留了一个会影响下一步的设置：

```text
[bcgong@localhost vge2p4_u3]$ grep -E 'LMAXMIX|LORBIT' OUTCAR
   LMAXMIX     =    2 max onsite mixed and CHGCAR
   LORBIT       =      0    0 simple, 1 ext, 2 COOP (PROOUT), +10 PAW based schemes
```
本例没有显式设置 LMAXMIX，实际采用了 2；LORBIT 也采用 0。因此，这份旧 SCF 可以用来核对 DFT+U 的输入与电子收敛，但不能直接把它产生的 CHGCAR 当作一份已经准备好做固定电荷 d 轨道能带的起点。VASP 对 d 电子的 DFT+U 推荐 `LMAXMIX = 4`；要接 `ICHARG = 11` 的能带或 DOS，应在新的 SCF 目录中显式设为 4 并重新生成 CHGCAR。若要检查每个原子的局域磁矩，可同时设 `LORBIT = 11`，然后读取 OUTCAR 的 magnetization 表。

修改这些参数应保留旧结果：先用 `cp` 把原始输入复制到新目录，再用 `vi INCAR` 编辑，并用 `cat INCAR` 核对。重新运行后，应再次读取 OUTCAR 的 LMAXMIX 回显，并确认生成的 CHGCAR 与新输入对应，再接后续计算。

## 输入与已收敛结果

| 读取量 | 本次记录 |
| --- | --- |
| 元素顺序 / 作用轨道 | V Ge P / V-d |
| Dudarev U−J（eV） | 3.0 |
| LDAUTYPE / LDAUL | 2 / 2 −1 −1 |
| 实际 LMAXMIX / LORBIT | 2 / 0 |
| 电子步数 | 31 |
| F（eV/胞） | −34.09930339 |
| E0（eV/胞） | −34.09694576 |
| 本次参考下 E_F（eV） | 2.4194 |
| 总磁矩（μB/胞） | 0.5781 |

## 对照文献中的分析方法

*Effect of Hubbard U-corrections on the electronic and magnetic properties of 2D materials: a high-throughput study*，[DOI: 10.1038/s41524-024-01503-3](https://doi.org/10.1038/s41524-024-01503-3)，Methods 的 Eq. (1) 定义 Ueff，Eq. (2) 写出占据矩阵的修正项；原文选取的元素和 U=4 eV 属于自己的计算协议。本例是一份 Ueff=3 eV 的 SCF，适合核对元素—轨道—参数及实际输出。评估 U 对性质的影响需要相同协议下的多个 U 点。LASPH 与 LMAXMIX 的设置依据分别见 [LASPH](https://vasp.at/wiki/LASPH) 和 [LMAXMIX](https://vasp.at/wiki/LMAXMIX) 官方说明。

```text
确定结构、元素顺序与 U 的来源
  └─ DFT+U SCF → OUTCAR 的 l/U/J 回显 → 电子收敛
                                           ├─ 磁构型比较
                                           └─ LMAXMIX 与 CHGCAR 核验 → 能带 / DOS
```

## 从原始文件重建结果

汇总脚本把 POSCAR 的元素顺序与 OUTCAR 的 U 参数回显对应起来，读取实际 LMAXMIX、LORBIT、最终能量和总磁矩，输出一行结果及参数记录。可以把这些读取规则写成下面的请求：

```text
请编写 Python 3 独立后处理程序。读取脚本所在目录的 POSCAR、OUTCAR、OSZICAR；INCAR、KPOINTS 和 EIGENVAL 还需存在，用于记录输入输出哈希。按 V Ge P 顺序核对 Dudarev l/U/J 回显，从实际 OUTCAR 提取 LMAXMIX、LORBIT、F、E0、Efermi，OSZICAR 提取电子步数和最终总磁矩。检查 EDIFF 和计时段，保留单位与输入 SHA256，输出 JSON/CSV。缺失数据明确报错；仅报告 Ueff=3 eV 单点记录，不把 SCF 残差或无序 EIGENVAL 散点当作 U 效应。 缺少文件、格式或非有限数值时明确失败，不猜值、不补零。脚本写入分析结果，保留原始计算文件。
```

[summarize_dftu.py 完整源码](/Atlas/examples/interface-magnet-dft-plus-u/summarize_dftu.py)

<details>
<summary>summarize_dftu.py 的完整源码</summary>

```python
from pathlib import Path
import re, json, csv, hashlib, math
r=Path(__file__).resolve().parent
out=(r/'OUTCAR').read_text(); osz=(r/'OSZICAR').read_text()
if 'aborting loop because EDIFF is reached' not in out or 'General timing' not in out:
    raise ValueError('Missing electronic convergence or timing record')
def last(pattern):
    v=re.findall(pattern,out)
    if not v: raise ValueError('Missing field: '+pattern)
    return v[-1]
species=(r/'POSCAR').read_text().splitlines()[5].split()
if species!=['V','Ge','P']:raise ValueError('Expected V Ge P species order')
F=float(last(r'free  energy\s+TOTEN\s*=\s*([-0-9.]+)'))
E0=float(last(r'energy\(sigma->0\)\s*=\s*([-0-9.]+)'))
EF=float(last(r'E-fermi\s*:\s*([-0-9.]+)'))
M=float(re.findall(r'mag=\s*([-0-9.]+)',osz)[-1])
steps=[int(x) for x in re.findall(r'DAV:\s*(\d+)',osz)]
u=[float(x) for x in last(r'U \(eV\)\s+for each species LDAUU\s*=([^\n]+)').split()]
j=[float(x) for x in last(r'J \(eV\)\s+for each species LDAUJ\s*=([^\n]+)').split()]
l=[int(x) for x in last(r'angular momentum for each species LDAUL\s*=([^\n]+)').split()]
if l!=[2,-1,-1] or len(u)!=3 or len(j)!=3:raise ValueError('Unexpected DFT+U orbital/species arrays')
if not all(math.isfinite(x) for x in [F,E0,EF,M,*u,*j]):raise ValueError('Non-finite output')
row={'elements':' '.join(species),'LDAUTYPE':int(last(r'LDAUTYPE\s*=\s*(\d+)')),'LDAUL':' '.join(map(str,l)),'Ueff_V_d_eV':u[0]-j[0],'LMAXMIX':int(last(r'LMAXMIX\s*=\s*(\d+)')),'LORBIT':int(last(r'LORBIT\s*=\s*(\d+)')),'electron_steps':steps[-1],'F_eV_cell':F,'E0_eV_cell':E0,'EF_eV_run_reference':EF,'M_muB_cell':M}
summary={'result':row,'source_sha256':{n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ['INCAR','POSCAR','KPOINTS','OUTCAR','OSZICAR','EIGENVAL']},'scope':'Single U=3 eV SCF; no U=0 comparison or U-dependence conclusion.'}
(r/'dftu-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (r/'dftu-result-table.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=row);w.writeheader();w.writerow(row)
for k,v in row.items(): print(k,'=',v)
```

</details>

[输入、原始输出与完整后处理包](/Atlas/examples/interface-magnet-dft-plus-u/example-pack.tar.gz)解压后，在 `example-pack` 目录执行：

```bash
python3 summarize_dftu.py
```

实际读取结果见正文表及 [dftu-result-table.csv](/Atlas/examples/interface-magnet-dft-plus-u/dftu-result-table.csv) · [dftu-summary.json](/Atlas/examples/interface-magnet-dft-plus-u/dftu-summary.json)。

相关输入说明：[VASP：DFT+U](https://vasp.at/wiki/DFT%2BU) · [LDAUTYPE](https://vasp.at/wiki/LDAUTYPE) · [LMAXMIX](https://vasp.at/wiki/LMAXMIX) · [MAGMOM](https://vasp.at/wiki/MAGMOM)

这份 VGe₂P₄ 存档只验证 Ueff=3 eV 的一次静态计算，不提供当前 ZrCl₂/Sc₂C 或 SnSe₂/Sr₂N 的 U 标定。仅当具体材料的局域关联证据、采用协议或独立响应计算要求修正时，才把 DFT+U 纳入近费米态比较；不能因为有过渡金属 d 轨道就套用 3 eV。随后能带、DOS 和界面对照都要沿用同一 U、几何和投影定义，且先重新生成可保存 d 占据矩阵的父密度。
