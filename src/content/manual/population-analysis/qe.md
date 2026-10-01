Si 的价电子在选定的原子 s、p 轨道子空间中如何分配，这个子空间又覆盖了多少电子？本页用 `projwfc.x` 读取均匀 `18³` 网格的 `gap18-cg` 波函数，提取两个等价 Si 的 Löwdin 布居，并将总投影电子数与 spilling 对照。等价原子的结果应一致；每原子布居与四个价电子之间的差额需要结合投影覆盖解释。结构和父密度见[SCF](/Atlas/m/scf/qe/)，波函数积分网格见[NSCF](/Atlas/m/nscf/qe/)。

[Sánchez-Portal、Artacho 和 Soler](https://doi.org/10.1088/0953-8984/8/21/012)在 Sec. II、Eqs. (1)–(2) 用投影子空间定义 spilling，并在 Sec. VII 讨论布居对原子轨道基组的依赖。本页使用 [QE 7.5 的 Löwdin 原子投影](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html)，不是该论文的非正交 Mulliken 布居；两者都要求说明轨道子空间和投影缺口，原子的空间盆地电荷则另由 Bader 定义。

[projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [后处理用户手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

[下载 Si 算例](/Atlas/examples/si-pbe-lesson-files.tar.gz)后保留目录结构，在 `si-pbe` 中读取 `population-cg` 的投影输入、原始输出与 `lowdin.csv` 布居表。包中不含波函数与可接续计算的 `tmp/si.save`；重新运行 `projwfc.x` 时，需要按下文前提完成 SCF 和匹配的均匀网格 NSCF。

## 准备均匀网格波函数与投影输入

布居需要对布里渊区积分，所以这次复制的是均匀网格计算后的完整 `tmp`，包含波函数。普通能带路径只沿几条线走，不能用它的权重积分来代替这一份布居。

```text
[preston@preston-System-Product-Name si-pbe]$ mkdir -p population-cg
[preston@preston-System-Product-Name si-pbe]$ cp -a gap18-cg/tmp population-cg/
[preston@preston-System-Product-Name si-pbe]$ cp population/projwfc.in population/run.sh population-cg/
```

复制后再检查目录。`tmp` 是计算数据，`projwfc.in` 控制后处理，生成的 `si.pdos_*` 是能量分辨的投影态密度；布居数字在 `projwfc.out` 末段。

```text
[preston@preston-System-Product-Name si-pbe]$ ls population-cg
 _err.798.log      data-file-schema.xml   projwfc.in    si-projections.projwfc_up    'si.pdos_atm#2(Si)_wfc#1(s)'   tmp
 _out.798.log      lowdin.csv             projwfc.out  'si.pdos_atm#1(Si)_wfc#1(s)'  'si.pdos_atm#2(Si)_wfc#2(p)'
 atomic_proj.xml   projwfc.err            run.sh       'si.pdos_atm#1(Si)_wfc#2(p)'   si.pdos_tot
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name si-pbe]$ cat population-cg/projwfc.in
&PROJWFC
  prefix = 'si'
  outdir = './tmp'
  filpdos = 'si'
  filproj = 'si-projections'
  ngauss = 0
  degauss = 0.01
  DeltaE = 0.02
/
[preston@preston-System-Product-Name si-pbe]$
```


`prefix='si'` 和 `outdir='./tmp'` 必须对应那次 NSCF 的实际文件。`filproj` 保存逐态投影，`filpdos` 命名 PDOS；`degauss=0.01` 的单位是 Ry，`DeltaE=0.02` 的单位是 eV，二者用于同时生成的展宽 PDOS。不要因为输入里出现了展宽参数，就把投影电子数误读成某个能量点上的 DOS 值。

这份输入的 `ngauss=0` 选择 Gaussian 展宽；`degauss` 控制每个离散能级在能量轴上铺开的宽度，`DeltaE` 控制输出曲线的取样间隔。减小 `DeltaE` 可以把已有曲线写得更细，但不会增加 NSCF 的 k 点，也不会补全赝势原子轨道没有覆盖的投影空间。

## 运行 projwfc.x，核对原子轨道编号

```text
[preston@preston-System-Product-Name si-pbe]$ cat population-cg/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-pop
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/projwfc.x -in projwfc.in > projwfc.out 2> projwfc.err
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name population-cg]$ sbatch run.sh
Submitted batch job 798
[preston@preston-System-Product-Name population-cg]$ cd ..
```

先读 OUT 开头，确认它从 `./tmp/si.save/` 读到了 PBE 数据。接下来会列出原子波函数数量、能带数量和 k 点数量，再列出每个投影状态属于哪个原子、哪个角动量。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 67 population-cg/projwfc.out

     Program PROJWFC v.7.5 starts on 22Sep2026 at 22: 2:44

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     4 processors

     MPI processes distributed on     1 nodes
     R & G space division:  proc/nbgrp/npool/nimage =       4
     5948 MiB available memory on the printing compute node when the environment starts


     Reading xml data from directory:

     ./tmp/si.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want


     Parallelization info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Min         571     214     63                18093     4156     684
     Max         572     217     64                18095     4157     688
     Sum        2287     859    253                72377    16625    2741

     Using Slab Decomposition


     Gaussian broadening (read from input): ngauss,degauss=   0    0.010000


     Calling projwave ....
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


  Problem Sizes
  natomwfc =            8
  nbnd     =            8
  nkstot   =          195
  npwx     =          531
  nkb      =           36


     Atomic states used for projection
     (read from pseudopotential files):

     state #   1: atom   1 (Si ), wfc  1 (l=0 m= 1)
     state #   2: atom   1 (Si ), wfc  2 (l=1 m= 1)
     state #   3: atom   1 (Si ), wfc  2 (l=1 m= 2)
     state #   4: atom   1 (Si ), wfc  2 (l=1 m= 3)
     state #   5: atom   2 (Si ), wfc  1 (l=0 m= 1)
     state #   6: atom   2 (Si ), wfc  2 (l=1 m= 1)
     state #   7: atom   2 (Si ), wfc  2 (l=1 m= 2)
     state #   8: atom   2 (Si ), wfc  2 (l=1 m= 3)
[preston@preston-System-Product-Name si-pbe]$
```


本例 `natomwfc=8`：每个 Si 有一组 s 和三组 p，两个原子一共八个投影通道。`state #1` 是第一个 Si 的 s，`#2–4` 是它的 p；`#5` 是第二个 Si 的 s，`#6–8` 是它的 p。这些编号由本次赝势中的原子态决定，换赝势后应重新读这一段。

## 读取 Löwdin 布居与 spilling

中间部分逐 k 点、逐能带列出投影，最后才对占据态和 k 权重求和得到布居。末尾的完整关键段如下：

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 25 population-cg/projwfc.out
==== e(   7) =    11.86270 eV ====
     psi = 0.108*[#   1]+0.108*[#   5]+0.083*[#   2]+0.083*[#   3]+0.083*[#   4]
          +0.083*[#   6]+0.083*[#   7]+0.083*[#   8]
    |psi|^2 = 0.713
==== e(   8) =    11.86270 eV ====
     psi = 0.108*[#   1]+0.108*[#   5]+0.083*[#   2]+0.083*[#   3]+0.083*[#   4]
          +0.083*[#   6]+0.083*[#   7]+0.083*[#   8]
    |psi|^2 = 0.713

Lowdin Charges:

     Atom #   1: total charge =   3.9634, s =  1.1520,
     Atom #   1: total charge =   3.9634, p =  2.8114, pz=  0.9371, px=  0.9371, py=  0.9371,
     Atom #   2: total charge =   3.9634, s =  1.1520,
     Atom #   2: total charge =   3.9634, p =  2.8114, pz=  0.9371, px=  0.9371, py=  0.9371,
     Spilling Parameter:   0.0092

     PROJWFC      :      1.15s CPU      1.23s WALL


   This run was terminated on:  22: 2:45  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


同一个原子被打印在两行，是为了分开展示 s 和 p，不是两份需要再相加的总电荷。每个 Si 的 `total charge` 是 **3.9634 e**，其中 s 为 **1.1520 e**，p 合计 **2.8114 e**；p 的三个分量各为 0.9371 e，舍入后相加可能出现最后一位的小差别。

两个原子的结果一致，这是这个对称结构首先应该满足的核对。再看 `Spilling Parameter=0.0092`：两个原子的投影电子数合计为 7.9268 e，相比原胞的 8 个价电子少了约 0.0732 e，比例约 0.00915，与报告的 spilling 舍入值一致。

每个 Si 的 `4−3.9634=0.0366 e` 是有限原子轨道投影留下的缺口。这里两个等价原子的布居相同，差额应结合 spilling 解释；若要确定原子净电荷，还需采用相应的电荷分区与参考定义。

这组 Si 结果用于认识“轨道占据”和“空间电荷”是两种定义。比较界面内层与匹配孤立层时，按原子编号把同一组 s/p/d 布居相加，再报告轨道变化和各自 spilling。投影基和几何都可能改变覆盖，因而层布居减少不能直接写成相同数目的电子转移；电荷转移另由[差分电荷积分](/Atlas/m/delta-charge/)和空间盆地分析读取。

```text
[preston@preston-System-Product-Name si-pbe]$ cat population-cg/lowdin.csv
atom,total_electrons,s_electrons,p_electrons,pz_electrons,px_electrons,py_electrons
1,3.9634,1.1520000000000001,2.8114,0.9371,0.9371,0.9371
2,3.9634,1.1520000000000001,2.8114,0.9371,0.9371,0.9371
[preston@preston-System-Product-Name si-pbe]$
```


## 从原始布居输出整理表格

| 原子 | 总布居 / e | s / e | p / e | pz / e | px / e | py / e |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Si1 | 3.9634 | 1.1520 | 2.8114 | 0.9371 | 0.9371 | 0.9371 |
| Si2 | 3.9634 | 1.1520 | 2.8114 | 0.9371 | 0.9371 | 0.9371 |

[原始 projwfc.out](/Atlas/examples/si-pbe/population-cg/projwfc.out) 与[原有布居表](/Atlas/examples/si-pbe/population-cg/lowdin.csv)可直接下载。可复制给 AI 编程助手的需求如下：

```text
编写Python 3标准库extract_lowdin.py，输入QE projwfc.out，读取最后Lowdin Charges段。每原子s与p打印在不同重复Atom行，按原子编号合并而非将total charge相加。解析total、s、p、pz、px、py，检查同原子两行total相同、s+p与total在输出舍入精度内一致、px+py+pz与p差小于2e-4e。只对本例两个Si、8价电子核验，解析Spilling Parameter及JOB DONE，缺项报错。CSV保留原始打印精度，终端打印总投影电子数、8-total与比例，并对照spilling；不能把投影缺口当成净电荷转移。命令为python3 extract_lowdin.py projwfc.out --output new-lowdin.csv，拒绝覆盖已有CSV。只整理表格，不重画柱图，不运行QE；输入保持只读。
```

[完整源码：extract_lowdin.py](/Atlas/examples/charge-vesta/scripts/extract_lowdin.py)。环境为 Python 3 标准库。把源码与原始输出放在同一目录，在新目标文件执行：

<details>
<summary>extract_lowdin.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Extract the two-atom Si Löwdin table from a completed QE projwfc.out."""
import argparse
import csv
from pathlib import Path
import re

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('input', type=Path)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
if a.output.exists():
    raise FileExistsError(f'Refusing to overwrite {a.output}')
text = a.input.read_text()
if 'JOB DONE.' not in text or 'Lowdin Charges:' not in text:
    raise ValueError('Missing completed Löwdin output')
section = text.rsplit('Lowdin Charges:', 1)[1]
rows = {}
for match in re.finditer(r'Atom #\s*(\d+):\s*([^\n]+)', section):
    atom = int(match[1])
    fields = dict((k, float(v)) for k, v in re.findall(r'(total charge|s|p|pz|px|py)\s*=\s*([+-]?[\d.]+)', match[2]))
    row = rows.setdefault(atom, {})
    for key, value in fields.items():
        if key in row and abs(row[key] - value) > 1e-8:
            raise ValueError(f'Inconsistent atom {atom} field {key}')
        row[key] = value
if sorted(rows) != [1, 2]:
    raise ValueError('This example requires atoms 1 and 2')
for atom, row in rows.items():
    if set(row) != {'total charge', 's', 'p', 'pz', 'px', 'py'}:
        raise ValueError(f'Incomplete atom {atom}: {row}')
    if abs(row['s'] + row['p'] - row['total charge']) > 2e-4:
        raise ValueError('s+p differs from total beyond printed precision')
    if abs(row['pz'] + row['px'] + row['py'] - row['p']) > 2e-4:
        raise ValueError('p components differ from p beyond printed precision')
sp = re.search(r'Spilling Parameter:\s*([\d.]+)', section)
if not sp:
    raise ValueError('Missing spilling')
total = sum(row['total charge'] for row in rows.values())
a.output.parent.mkdir(parents=True, exist_ok=True)
with a.output.open('x', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['atom', 'total_electrons', 's_electrons', 'p_electrons', 'pz_electrons', 'px_electrons', 'py_electrons'])
    for atom, row in sorted(rows.items()):
        writer.writerow([atom] + [f'{row[k]:.4f}' for k in ('total charge', 's', 'p', 'pz', 'px', 'py')])
print(f'atoms: {len(rows)}; projected electrons: {total:.4f} e')
print(f'8-total: {8-total:.4f} e; fraction: {(8-total)/8:.5f}; reported spilling: {float(sp[1]):.4f}')
print(f'wrote: {a.output}')
```

</details>

```bash
python3 -B extract_lowdin.py projwfc.out --output new-lowdin.csv
```

实际输出的检查值为总投影电子数7.9268 e、缺口0.0732 e、缺口比例0.00915，原文件spilling=0.0092。末位差异来自原始输出舍入。Löwdin 布居依赖所选择的原子轨道子空间；比较材料或构型时，应固定赝势、投影定义与积分网格，再检查变化和spilling。

本页的投影来自 QE 赝势原子轨道。使用 ADF 等原子中心局域基组得到的轨道占据有不同基组定义；间隙空球投影、Bader与Born有效电荷也各自定义不同，不能直接放进同一个“原子失电子”表。

[Ba₂N 原文 Fig. 2(a–d)](https://doi.org/10.1103/PhysRevB.105.165101)用间隙空球补充原子 PDOS，并结合 ELF 确认其空间位置；本文只有赝势原子投影，没有加入这样的间隙投影。若研究无核电子区域，应把[能窗密度与 ELF](/Atlas/m/elf/)放到同一空间位置核对，而不是由 0.0366 e 的投影缺口判断电子化合物身份。

下一步：看逐 k 点的轨道组成接[胖带](/Atlas/m/fatband/qe/)；看实空间分区可参照[Bader 电荷的 VASP 例程](/Atlas/m/bader/vasp/)，看成键前后的空间变化可参照[差分电荷的 VASP 例程](/Atlas/m/delta-charge/vasp/)。后两页说明另一种分析方法，读取的是 CHGCAR 等 VASP 文件，不能直接接用这里的 QE `save` 目录。

```text
均匀 NSCF 网格 + 波函数 → projwfc.x → 轨道编号与逐态投影
                                             ↓
                                  占据数与 k 权重积分
                                             ↓
                               Löwdin 布居 + spilling 核对
```
