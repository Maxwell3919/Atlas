界面形成后，一层材料得到多少电子？Bader 分析先把整个密度场按零通量边界划成盆地，再给每个盆地积分；把属于同一层的原子相加，就得到这一分区定义下的层电子数。本例先用两个等价 Fe 原子检验这条操作链：文件读法、参考密度、电子守恒和网格变化都能直接从真实输出复核。Fe 的结果用于学习分区，不承担电子化合物或异质结转移的材料结论。

在金属/Ca₂N/MoS₂ 接触的原文中，作者把 MoS₂ 原子电荷加总并按化学式单元报告，借此比较不同接触；Fig. 2(c) 将转移量和接触距离放在一起读。[The role of the metal in metal–MoS₂ and metal–Ca₂N–MoS₂ interfaces, PCCP 27, 6438 (2025)](https://doi.org/10.1039/D4CP04577G)。它采用 Yu–Trinkle/critic2；下文采用 Henkelman Bader 1.05，分区实现与参考密度应跟着数值一起记录。

先完成固定几何的 [SCF](/Atlas/m/scf/vasp/)。[下载本例真实输入、OUTCAR 和两套网格资料](/Atlas/examples/vasp/fe-bcc-lesson-files.tar.gz)，进入 `fe-bcc/charge_elf`。POTCAR 仅附身份信息，重跑时使用自己的授权文件。本次Fe结构与自旋设置的出处是该包内的 `charge_elf/POSCAR`、`charge_elf/INCAR` 和 `charge_elf/OUTCAR`；加密网格的对应记录在 `charge_elf_192`。

## 价电子积分与全电子分区参考

CHGCAR 是实际积分目标；AECCAR0+AECCAR2 提供核附近的全电子参考密度，用来寻找盆地边界。LAECHG 同时写出的 AECCAR1 是原子叠加价电子密度，不能代替自洽的 AECCAR2。在原目录用 `vi INCAR` 编辑后读回：

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

细网格 96³ 表示密度的空间采样；ENCUT 决定波函数基组。此次一并打开 LELF，所以保留 `NPAR=1`，后面仍使用 8 个 MPI 进程。ELFCAR 的网格另看它自己的文件头。

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

最后电子步达到 EDIFF，程序已完整结束，才可以使用 AECCAR2。一次静态自洽没有改变结构，也没有替目标层电荷完成网格收敛检查。

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

结构后的 96 96 96 给出 884,736 个点。若原始值是 D，体积 V=21.952 Å³，则数密度 n=D/V，价电子总数 N=ΣD/Ngrid；磁化块与 PAW 一中心数据不进入这一积分。[VASP CHGCAR 格式与归一化](https://vasp.at/wiki/CHGCAR)。

## 相加参考，再看 ACF.dat

相加程序核对晶胞、元素、坐标和网格后，只处理第一标量块。需要编写同样的程序时可使用这一需求：

```text
用 Python 3 标准库编写 sum_charge.py。读取同目录 AECCAR0、AECCAR2、CHGCAR，解析结构头，核对晶胞、元素顺序、坐标和网格一致。每份只读取第一块 nx*ny*nz 个总密度值，排除磁化密度和 augmentation occupancies；用 Σg/N 打印各自电子数积分。逐点相加 AECCAR0+AECCAR2，保留结构头写入 CHGCAR_sum，用写出前的相加数组计算 reference_integral=Σg/N；再读回检查网格尺寸和数组长度。回读检查不重新计算参考积分。源文件只读，不修正或归一化原始数值。
```

[sum_charge.py](/Atlas/examples/charge-vesta/scripts/sum_charge.py) 的完整源码在文末。实际运行得到：

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

CHGCAR 积分恢复 16 个价电子；AECCAR0 的 39.5201 e 偏离此赝势应有的 36 个芯电子，提示粗网格采样核区的误差。这个参考积分与稍后的价电子盆地数各有含义。

```text
[bcgong@localhost charge_elf]$ <bader_bin>/bader CHGCAR -ref CHGCAR_sum
```

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

`CHARGE` 是价电子盆地数。取净电荷 Qᵢ=ZVALᵢ−Nᵢ，两个 Fe 分别为 −0.000303 和 +0.000303 e；取净增电子数 Nᵢ−ZVALᵢ，符号相反。两个等价原子的微小差异用于检查离散分区。两个 `ATOMIC VOL` 相加为21.952 Å³，盆地数相加为16 e，分别核对空间覆盖和电子数。`MIN DIST` 是原子到盆地边界的最短距离，不能拿来读键长。

## 加密后的变化有多大

另一份 `charge_elf_192` 保持几何、赝势、k 网格和电子协议，并将细网格改为192³；同次 ELF 粗网格也从18³改为36³。它是两套实空间设置的比较。

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

| 细网格 | Fe1 盆地数 / e | Fe2 盆地数 / e | 芯密度全胞积分 / e |
| --- | ---: | ---: | ---: |
| 96³ | 8.000303 | 7.999697 | 39.5201 |
| 192³ | 7.999923 | 8.000077 | 36.2910 |

每个 Fe 的盆地数改变约0.000380 e，等价原子之间的差异减小；芯密度积分也更接近36 e。研究界面时，加密后应比较关心的层加总，精度由这个量的变化判断。

[下载两份 ACF.dat 和积分记录](/Atlas/examples/charge-vesta-files.tar.gz)，进入 `charge-vesta/bader`，用 [extract_bader_grid.py](/Atlas/examples/charge-vesta/scripts/extract_bader_grid.py) 复现表格。源码与写码需求保留在文末。

```bash
python3 -B ../scripts/extract_bader_grid.py --output new-bader-grid.csv
cat new-bader-grid.csv
```

## 从原子加总到层转移与面积密度

先按结构确定每层的原子编号，再求 Nᴮ_AB,A=Σᵢ∈A Nᵢ。对于中性层，Nᴮ_AB,A−Σᵢ∈A ZVALᵢ 是以中性价电子数为参考的层净增电子数；若使用冻结孤立层的 Bader 对照，则 ΔNᴮ_A=Nᴮ_AB,A−Nᴮ_A,A。后者包含接触前后盆地边界的变化，必须说明参考结构和算法。分子/晶胞有净电荷，或算法把间隙极大值另列为盆地时，需把相应电子数一同核对，不能遗漏后再把每层强制凑成整数。

层得到电子时 ΔNᴮ_A>0，它的电荷变化 ΔQ_A=−eΔNᴮ_A。若报告每原胞转移量，面积 S=|a×b| 用该异质结的真实面内晶胞；面积密度为 ΔNᴮ_A/S，单位 e/Å²，乘10¹⁶得到 e/cm²。论文按化学式单元报告时，要先确认该胞含几个单元，不能将每单元数和超胞面积直接混用。这里的面积密度描述分区电荷，金属/半导体自由载流子数还需能带占据或费米面分析。

空间分区也决定数字的含义。[差分电荷密度](/Atlas/m/delta-charge/vasp/) 在固定几何上直接积分 Δn，按法向区间分层；它的层积分与 Bader 加总可以并列比较，各自保留边界。两者相近支持趋势一致，差异则需要查看界面重叠区域。ELF 给局域化函数，能窗密度给选中态的空间权重，都不替代这些积分。

Bader 原算法的网格上升路径见 [Henkelman 等, Comput. Mater. Sci. 36, 354 (2006), Secs. 1–2](https://doi.org/10.1016/j.commatsci.2005.04.010)；VASP 输出对应 [LAECHG](https://vasp.at/wiki/LAECHG)。


## 完整源码与执行记录

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

<details>
<summary>同一算例的其余输入、检查命令与保存输出</summary>

```text
[bcgong@localhost charge_elf]$ ls -lh AECCAR0 AECCAR2 CHGCAR ELFCAR
-rw-rw-r-- 1 bcgong bcgong  16M Sep 22 21:42 AECCAR0
-rw-rw-r-- 1 bcgong bcgong  16M Sep 22 21:42 AECCAR2
-rw-rw-r-- 1 bcgong bcgong  31M Sep 22 21:42 CHGCAR
-rw-rw-r-- 1 bcgong bcgong 139K Sep 22 21:42 ELFCAR
```

```text
用 Python 3 标准库写 extract_bader_grid.py，只解析已经完成的96³和192³ bcc Fe Bader输出，不运行VASP/Bader。读取每目录ACF.dat原子行的编号、X/Y/Z、CHARGE、MIN DIST、ATOMIC VOL，以及底部VACUUM CHARGE、VACUUM VOLUME、NUMBER OF ELECTRONS。CHARGE是价电子盆地数，坐标/距离单位Å，体积Å³；本例ZVAL=8，两Fe，总价电子16，晶胞体积21.952Å³。输出N_Bader、N_Bader-ZVAL、Q=ZVAL-N_Bader，保留两种符号定义；核对原子数和总量到原文件打印精度，打印残差而非宣称严格为零。另读取sum_charge.py记录的AECCAR0/2、CHGCAR与reference_integral，不把芯电子积分与盆地稳定性混成同一指标。输出CSV，拒绝覆盖输入。不画柱图或另加无来源材料数据；若要查看空间形貌，交给专业GUI读取真实密度。完整脚本应附命令行运行说明。
```

```text
收敛的固定几何 SCF
  ├─ CHGCAR：积分价电子
  └─ AECCAR0 + AECCAR2：找分区边界的参考
                 └─ 相同结构与完整网格检查 → Bader → ACF.dat
                                                   └─ 总数、等价性与网格加密检查
```

</details>
