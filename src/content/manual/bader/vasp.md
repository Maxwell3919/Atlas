连续电子密度怎样分配给原子，分出来的电子数是否保持晶体中原子的等价性？本页用两个等价 Fe 原子的铁磁 bcc 原胞，先以全电子参考密度确定 Bader 盆地，再积分盆地内的价电子密度。对照两套粗、细网格设置，检查每个 Fe 的盆地电子数和整胞总数；两个等价原子之间的小差异用于判断分区采样的影响。

Bader 盆地边界满足密度梯度沿法向为零。[Henkelman、Arnaldsson 和 Jónsson](https://doi.org/10.1016/j.commatsci.2005.04.010)的 Sec. 1–2 说明如何沿网格密度的上升路径把点分配到同一极大值，并讨论赝势核附近的密度问题。本例的 AECCAR0+AECCAR2 用于确定边界，ACF.dat 的电子数来自 CHGCAR；这两份密度承担不同作用。

[Henkelman 组：Bader 程序](https://www.henkelmanlab.org/code/bader/) · [VASP：LAECHG](https://vasp.at/wiki/LAECHG) · [CHGCAR](https://vasp.at/wiki/CHGCAR)

结构和磁态来自 [bcc Fe 磁构型比较](/Atlas/m/magnetic-gs/vasp/) 的 FM 解。下载 [真实输入、OUTCAR、96³ 电荷网格及后处理脚本](/Atlas/examples/vasp/fe-bcc-lesson-files.tar.gz) 后，解包进入 `fe-bcc/charge_elf`。包中保留两套网格的输出与检查结果，POTCAR 仅提供 TITEL、ZVAL 和哈希标识。

## 准备固定结构与密度输出

在新的 `charge_elf` 目录中复制 POSCAR、KPOINTS、POTCAR 和提交脚本，用 `vi INCAR` 打开全电子密度输出。保存后读回输入。

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

## 运行 SCF，检查密度对应的电子收敛

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
该脚本使用 8 个 MPI 进程；任务 18187 用时 26 秒。命令 `tail -f out` 可在运行时查看电子步；结束后仍需读停止行与统计尾段。

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

## 相加参考密度，再运行 Bader

相加时，两份文件的晶胞、元素顺序、坐标和网格都必须一致；只按行号相加，或者对不同长度的数据直接 zip，会把错误静默带入参考密度。

相加程序先核对这四项，再读取两份文件的第一块标量数据，生成找盆地边界用的 `CHGCAR_sum`。可将下面的需求交给 AI 编程助手：

```text
用 Python 3 标准库编写 sum_charge.py。读取同目录 AECCAR0、AECCAR2、CHGCAR，解析结构头，核对晶胞、元素顺序、坐标和网格一致。每份只读取第一块 nx*ny*nz 个总密度值，排除磁化密度和 augmentation occupancies；用 Σg/N 打印各自电子数积分。逐点相加 AECCAR0+AECCAR2，保留结构头写入 CHGCAR_sum，用写出前的相加数组计算 reference_integral=Σg/N；再读回检查网格尺寸和数组长度。回读检查不重新计算参考积分。源文件只读，不修正或归一化原始数值。
```

[完整源码：sum_charge.py](/Atlas/examples/charge-vesta/scripts/sum_charge.py)。将脚本放入 `charge_elf`，用 Python 3 运行。原始执行记录为：

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
CHGCAR 的积分是 16.0000000133，与两个 Fe 各 8 个价电子相符。芯电子密度很尖锐，96³ 对其积分仍不够好：AECCAR0 的积分为 39.5201，而这套 Fe 赝势每胞的芯电子数应为 2 × (26 − 8) = 36。后面通过加密网格检查这个芯电子积分差异，并单独观察价电子盆地数的变化。

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

## 加密网格，比较等价原子的盆地数

在新目录 `charge_elf_192` 中把 NGXF、NGYF、NGZF 改为 192，保持结构、赝势、k 网格和其余电子参数一致。本次同时将 ELF 使用的粗网格从 18³ 改为 36³，VASP 任务 18188 用时 102 秒结束。因此这是两套实空间网格设置的比较，并非只改变细网格一个参数的对照。后处理仍执行同一个相加脚本和 Bader 命令。

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
两原子现在分别得到 7.999923 和 8.000077 个价电子，在所列精度下相加为 16。96³ 到 192³，每个原子的变化约为 0.000380 e，等价原子之间的不对称减小了。与此同时，AECCAR0 积分从 39.5201 靠近到 36.2910：参考密度核区的积分还没有完全闭合，不能把它与价电子盆地积分的稳定程度混为一个指标。

这份小例子可以核对文件、网格、守恒和等价原子。真正比较异质结构的电荷转移时，应逐步加密网格，观察关心的原子或层电荷是否达到所需精度，并在所有对照计算中使用相同分区定义。

## 用原始输出表检查网格变化

| 网格 | N(Fe1) / e | N(Fe2) / e | AECCAR0 全胞积分 / e | 芯电子参考 / e |
| --- | ---: | ---: | ---: | ---: |
| 96³ | 8.000303 | 7.999697 | 39.5201 | 36 |
| 192³ | 7.999923 | 8.000077 | 36.2910 | 36 |

[下载两套 ACF.dat、密度积分记录与提取源码](/Atlas/examples/charge-vesta-files.tar.gz)，解包后进入 `charge-vesta/bader`。以下需求说明可交给 AI 编程助手，复现本例表格：

```text
用 Python 3 标准库写 extract_bader_grid.py，只解析已经完成的96³和192³ bcc Fe Bader输出，不运行VASP/Bader。读取每目录ACF.dat原子行的编号、X/Y/Z、CHARGE、MIN DIST、ATOMIC VOL，以及底部VACUUM CHARGE、VACUUM VOLUME、NUMBER OF ELECTRONS。CHARGE是价电子盆地数，坐标/距离单位Å，体积Å³；本例ZVAL=8，两Fe，总价电子16，晶胞体积21.952Å³。输出N_Bader、N_Bader-ZVAL、Q=ZVAL-N_Bader，保留两种符号定义；核对原子数和总量到原文件打印精度，打印残差而非宣称严格为零。另读取sum_charge.py记录的AECCAR0/2、CHGCAR与reference_integral，不把芯电子积分与盆地稳定性混成同一指标。输出CSV，拒绝覆盖输入。不画柱图或另加无来源材料数据；若要查看空间形貌，交给专业GUI读取真实密度。完整脚本应附命令行运行说明。
```

[完整源码：extract_bader_grid.py](/Atlas/examples/charge-vesta/scripts/extract_bader_grid.py)；[密度相加源码：sum_charge.py](/Atlas/examples/charge-vesta/scripts/sum_charge.py)。需要 Python 3；上述两个脚本均使用标准库。

<details>
<summary>sum_charge.py 的完整源码</summary>

```python
from __future__ import print_function
import sys,math,json

def read_scalar(name):
    f=open(name); header=[]
    title=f.readline(); header.append(title)
    scale_line=f.readline(); header.append(scale_line); scale=float(scale_line.split()[0])
    raw=[f.readline() for _ in range(3)];header+=raw; cell=[[float(x)*scale for x in t.split()[:3]] for t in raw]
    species=f.readline();header.append(species)
    if all(x.isdigit() for x in species.split()): counts=list(map(int,species.split())); species=''
    else:
        countline=f.readline();header.append(countline);counts=list(map(int,countline.split()))
    mode=f.readline();header.append(mode)
    if mode.strip().lower().startswith('s'): mode=f.readline();header.append(mode)
    raw=[f.readline() for _ in range(sum(counts))];header+=raw; coords=[[float(x) for x in t.split()[:3]] for t in raw]
    line=f.readline()
    while line and not line.strip(): line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0: raise ValueError('Invalid grid: '+name)
    n=grid[0]*grid[1]*grid[2]; values=[]
    while len(values)<n:
        line=f.readline()
        if not line: raise ValueError('Truncated scalar grid: '+name)
        values.extend(float(x.replace('D','E')) for x in line.split())
    if len(values)!=n: raise ValueError('Extra scalar values in last line: '+name)
    if not all(math.isfinite(x) if hasattr(math,'isfinite') else not(math.isnan(x) or math.isinf(x)) for x in values): raise ValueError('Nonfinite scalar')
    f.close()
    structure=[species.strip(),counts,mode.strip().lower(),cell,coords]
    return header,structure,grid,values

if __name__=='__main__':
    a=read_scalar('AECCAR0'); b=read_scalar('AECCAR2'); c=read_scalar('CHGCAR')
    if not(a[1]==b[1]==c[1]): raise ValueError('Cell, species, counts or coordinates differ')
    if not(a[2]==b[2]==c[2]): raise ValueError('FFT grids differ')
    if not(len(a[3])==len(b[3])==len(c[3])): raise ValueError('Scalar lengths differ')
    v=[x+y for x,y in zip(a[3],b[3])]; n=len(v)
    with open('CHGCAR_sum','w') as f:
        f.writelines(a[0]);f.write('\n%d %d %d\n'%tuple(a[2]))
        for i in range(0,n,5): f.write(' '.join('%18.11E'%x for x in v[i:i+5])+'\n')
    verify=read_scalar('CHGCAR_sum')
    if verify[2]!=a[2] or len(verify[3])!=n: raise ValueError('Read-back failed')
    report={'grid':a[2],'points':n,'AECCAR0_integral':sum(a[3])/n,'AECCAR2_integral':sum(b[3])/n,'CHGCAR_integral':sum(c[3])/n,'reference_integral':sum(v)/n,'scope':'first total-charge block only; no spin-density or augmentation blocks copied'}
    json.dump(report,open('charge-grid-check.json','w'),indent=2)
    for k in sorted(report): print('%s = %s'%(k,report[k]))
```

</details>

<details>
<summary>extract_bader_grid.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Extract the preserved 96³/192³ Fe ACF.dat tables without running Bader."""
import argparse, csv, json, re
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root', type=Path, default=Path('.'))
p.add_argument('--output', type=Path, default=Path('new-bader-grid.csv'))
a=p.parse_args()
if a.output.exists():raise FileExistsError(f'Refusing to overwrite {a.output}')
rows=[]
for size in (96,192):
    text=(a.root/str(size)/'ACF.dat').read_text()
    entries=[]
    for line in text.splitlines():
        fields=line.split()
        if len(fields)==7 and fields[0].isdigit():
            entries.append([int(fields[0])]+[float(x) for x in fields[1:]])
    if [r[0] for r in entries]!=[1,2]:raise ValueError('Expected two Fe basins')
    footer={}
    for label in ('VACUUM CHARGE','VACUUM VOLUME','NUMBER OF ELECTRONS'):
        match=re.search(re.escape(label)+r':\s*([\d.Ee+-]+)',text)
        if not match:raise ValueError(f'Missing {label}')
        footer[label]=float(match[1])
    basin=sum(r[4] for r in entries);vol=sum(r[6] for r in entries)
    if abs(basin+footer['VACUUM CHARGE']-footer['NUMBER OF ELECTRONS'])>2e-4:raise ValueError('Charge balance outside footer precision')
    if abs(basin-16)>2e-6 or abs(vol-21.952)>2e-6:raise ValueError('Example sum differs')
    check=json.loads((a.root/str(size)/'charge-grid-check.json').read_text())
    if check['grid']!=[size]*3:raise ValueError('Wrong grid')
    for r in entries:
        atom,x,y,z,charge,distance,volume=r
        rows.append([size,atom,x,y,z,charge,charge-8,8-charge,distance,volume,check['AECCAR0_integral'],check['AECCAR2_integral'],check['CHGCAR_integral'],check['reference_integral']])
        print(f'{size}^3 Fe{atom}: N={charge:.6f} e; Q={8-charge:+.6f} e')
    print(f'{size}^3 printed basin sum residual={basin-16:.3e} e; volume residual={vol-21.952:.3e} Å³; core integral={check["AECCAR0_integral"]:.9f} e')
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x',newline='') as f:
    w=csv.writer(f);w.writerow(['grid','atom','x_A','y_A','z_A','basin_e','delta_e','net_charge_e','min_dist_A','volume_A3','core_integral_e','valence_integral_e','CHGCAR_integral_e','reference_integral_e']);w.writerows(rows)
print(f'wrote: {a.output}; zero printed residual does not establish an exact integral')
```

</details>

在解包后的 `charge-vesta/bader` 目录运行：

```bash
python3 -B ../scripts/extract_bader_grid.py --output new-bader-grid.csv
cat new-bader-grid.csv
```

ACF.dat 将总数打印为16.0000 e，两个盆地数在所列六位小数下相加为16 e；这只核对当前输出精度，不证明连续密度的积分严格无误。`VACUUM CHARGE=0.0000` 和 `VACUUM VOLUME=0.0000` 表示本次分区算法没有列出真空盆地，不能据此断言真空中密度处处为零。

## 文献如何比较界面电荷

在金属/MoS₂ 与金属/Ca₂N/MoS₂ 的研究中，Fig. 2(c) 将 MoS₂ 的 Bader 转移量与接触距离联系起来，并区分不同接触强度。[Phys. Chem. Chem. Phys. 27, 6438 (2025)](https://doi.org/10.1039/D4CP04577G)。该文使用 Yu–Trinkle/critic2 分区。本例用 Henkelman Bader 程序验证同质 Fe 的等价性和网格变化；界面比较需要在自己的密度、片段参考与分区定义下重新求值。

下一步接 [差分电荷密度](/Atlas/m/delta-charge/vasp/)，查看电子在空间中的增减位置；或接 [ELF](/Atlas/m/elf/vasp/)，读取这次同一计算写出的局域化函数。盆地电荷与空间分布回答的问题不同，应保留各自的定义。

```text
收敛的固定几何 SCF
  ├─ CHGCAR：积分价电子
  └─ AECCAR0 + AECCAR2：找分区边界的参考
                 └─ 相同结构与完整网格检查 → Bader → ACF.dat
                                                   └─ 总数、等价性与网格加密检查
```
