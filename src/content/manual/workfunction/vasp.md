功函数把材料的电子化学势放到可比较的真空参照上：$\Phi=V_{\mathrm{vac}}-E_{\mathrm F}$。它依赖表面朝向、终止、几何和占据条件，接触层选择不能只看两个孤立OUTCAR的EF。本例从同一次SnSe₂单层SCF提取势、费米能和带边，以真实输出演示这一取差。

前置 [SCF](/Atlas/m/scf/vasp/)。[下载输入输出、LOCPOT、EIGENVAL和脚本](/Atlas/examples/interface-magnet-workfunction/example-pack.tar.gz)，进入 `example-pack`。POTCAR仅附身份信息，重跑用自己的授权文件。

## 保存同一结构的势与能级

以下是原计算目录的准备与真实输入。复制固定POSCAR、KPOINTS和授权POTCAR，在新目录编辑INCAR；ISTART=0、ICHARG=2从原子叠加密度开始。

```text
[bcgong@localhost vasp]$ mkdir snse2_workfunction
[bcgong@localhost vasp]$ cp snse2_lvhar/POSCAR snse2_lvhar/KPOINTS snse2_lvhar/POTCAR snse2_lvhar/run.slurm snse2_workfunction/
[bcgong@localhost vasp]$ cd snse2_workfunction
[bcgong@localhost snse2_workfunction]$ vi INCAR
```

```text
[bcgong@localhost snse2_workfunction]$ cat POSCAR
"Sn1 Se2"                               
   1.00000000000000     
     3.8464052687627550    0.0000000000015396    0.0000000000000001
    -1.9232026344298054    3.3310846760065127   -0.0000000000000002
     0.0000000000000007   -0.0000000000000005   18.3572978035193977
   Sn   Se
     1     2
Direct
  0.0000000000000000 -0.0000000000000000  0.5000000000000000
  0.6666666670000012  0.3333333329999988  0.5872511780709923
  0.3333333329999988  0.6666666670000012  0.4127488219290077
 
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
```

```text
[bcgong@localhost snse2_workfunction]$ cat INCAR
SYSTEM = SnSe2 self-consistent work function
ISTART = 0
ICHARG = 2
ENCUT = 520
GGA = PE
PREC = Accurate
EDIFF = 1E-7
NELM = 100
ALGO = Normal
ISMEAR = 0
SIGMA = 0.05
IVDW = 11
LREAL = .FALSE.
LASPH = .TRUE.
LORBIT = 11
LMAXMIX = 4
NCORE = 2
NSW = 0
IBRION = -1
LDIPOL = .TRUE.
IDIPOL = 3
DIPOL = 0.5 0.5 0.5
LWAVE = .FALSE.
LCHARG = .TRUE.
LVHAR = .TRUE.
```

```text
[bcgong@localhost snse2_workfunction]$ cat KPOINTS
K-Spacing Value to Generate K-Mesh: 0.010
0
Gamma
  33  33   1
0.0  0.0  0.0
```

一个Sn与两侧Se构成上下对称单层，c约18.3573 Å。原子约在7.58–10.78 Å，后面窗口放在两侧真空。LVHAR写离子+Hartree势，避免LVTOT的交换关联尾部影响真空读数；势值已经是eV。[VASP功函数方法](https://vasp.at/wiki/Computing_the_work_function)。

PBE+D3零阻尼（IVDW=11）用于固定几何；Gaussian展宽0.05 eV决定电子占据，不是离子温度。33×33×1均匀网格提供电子化学势，高对称线不承担这一步。LDIPOL、IDIPOL=3沿法向修正周期误差，DIPOL是分数坐标；改变位置或真空后应重看整胞曲线。

```text
[bcgong@localhost snse2_workfunction]$ grep -E 'TITEL|ZVAL' POTCAR
   TITEL  = PAW_PBE Sn_d 06Sep2000
   POMASS =  118.710; ZVAL   =   14.000    mass and valenz
   TITEL  = PAW_PBE Se 06Sep2000
   POMASS =   78.960; ZVAL   =    6.000    mass and valenz
```

```text
[bcgong@localhost snse2_workfunction]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-snse2-wf
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
[bcgong@localhost snse2_workfunction]$ sbatch run.slurm
Submitted batch job 18191
```

```text
[bcgong@localhost snse2_workfunction]$ scontrol show job 18191 | grep -E 'JobState=|ExitCode=|RunTime=|NumNodes='
   JobState=COMPLETED Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:01:28 TimeLimit=00:15:00 TimeMin=N/A
   NumNodes=1 NumCPUs=8 NumTasks=8 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
```

```text
[bcgong@localhost snse2_workfunction]$ grep -n -E 'aborting loop|General timing|E-fermi|Elapsed time|ICHARG|LVTOT|LVHAR' OUTCAR
496:   ICHARG =      2    charge: 1-file 2-atom 10-const
584:   LVTOT        =      F    write LOCPOT, total local potential
585:   LVHAR        =      T    write LOCPOT, Hartree potential only
2304: E-fermi :  -2.4783     XC(G=0):  -3.7142     alpha+bet : -3.3624
4839:------------------------ aborting loop because EDIFF is reached ----------------------------------------
4987: General timing and accounting informations for this job:
4993:                         Elapsed time (sec):       87.188
```

```text
[bcgong@localhost snse2_workfunction]$ grep -E 'NKPTS|NELECT|dimension x,y,z' OUTCAR
   k-points           NKPTS =    108   k-points in BZ     NKDIM =    108   number of bands    NBANDS=     20
   dimension x,y,z NGX =    30 NGY =   30 NGZ =  140
   dimension x,y,z NGXF=    60 NGYF=   60 NGZF=  280
   NELECT =      26.0000    total number of electrons
```

Sn_d为14个价电子，两个Se各6，共26；输出恢复NELECT=26。电子自洽达EDIFF，VASP 5.4.4耗时约87.2秒，Slurm报告88秒。一次固定几何解只提供这套协议的参考读数；评价Φ精度应改变网格、截断与真空后比较Vvac−EF。

## 平台是一个区间，不是最高点

```text
[bcgong@localhost snse2_workfunction]$ head -16 LOCPOT
SnSe2 self-consistent work function     
   1.00000000000000     
     3.846405    0.000000    0.000000
    -1.923203    3.331085   -0.000000
     0.000000   -0.000000   18.357298
   Sn   Se
     1     2
Direct
  0.000000  0.000000  0.500000
  0.666667  0.333333  0.587251
  0.333333  0.666667  0.412749
 
   60   60  280
 0.33084600381E+01 0.33076277525E+01 0.33075776565E+01 0.33066064425E+01 0.33057828908E+01
 0.33047842371E+01 0.33060151987E+01 0.33063898923E+01 0.33069215644E+01 0.33051810740E+01
 0.33078743625E+01 0.33054753494E+01 0.33058853949E+01 0.33071917898E+01 0.33053963884E+01
```

```python
field = np.asarray(values).reshape((nz, ny, nx))
planar = field.mean(axis=(1, 2))
z = np.arange(nz) * normal_height / nz
```

网格60×60×280，共1,008,000个值。每层平均消去面内起伏，保留法向变化；$z_k=kH/280$，$H=V_{\mathrm{cell}}/\lVert\mathbf a\times\mathbf b\rVert$。对于本例$H=c$，不重复周期末端。格式细节见 [静电势](/Atlas/m/electrostatic-potential/vasp/)。

```text
[bcgong@localhost snse2_workfunction]$ python plane_average.py LOCPOT 1:3 15:17
grid = 60 60 280; scalar values = 1008000
normal height = 18.3572980000 A; output = PLANAR_AVERAGE.dat
window 1.00:3.00 A  N=30  mean=3.306283412 eV  std=1.5602e-05 eV  range=6.06972e-05 eV
window 15.00:17.00 A  N=31  mean=3.306265353 eV  std=3.89608e-05 eV  range=0.000145996 eV
```

1–3 Å与15–17 Å分别得到3.306283412和3.306265353 eV，两侧差仅约18.1 μeV，符合这份上下对称几何。range约0.0000607、0.0001460 eV是窗口内起伏；旧LVTOT文件同窗起伏达0.268、0.407 eV，提示不能只按文件名或窗口机械读取。

## 半导体的EF、带边与真空差分别报告

```text
[bcgong@localhost snse2_workfunction]$ python workfunction_values.py
E_F = -2.478300 eV; VBM = -2.690722 eV; CBM = -1.923449 eV; gap = 0.767273 eV
z = 1.00:3.00 A; V_vac = 3.306283412 eV; Phi(E_F) = 5.784583412 eV; V_vac-VBM = 5.997005412 eV; V_vac-CBM = 5.229732412 eV
z = 15.00:17.00 A; V_vac = 3.306265353 eV; Phi(E_F) = 5.784565353 eV; V_vac-VBM = 5.996987353 eV; V_vac-CBM = 5.229714353 eV
```

EF=−2.478300 eV，程序给两侧Φ约5.78458、5.78457 eV。SnSe₂采样PBE隙0.767273 eV，带隙内的EF随占据处理、掺杂与实验条件变化；它不等于由带边定义的电离能$\mathrm{IP}=V_{\mathrm{vac}}-\mathrm{VBM}$或电子亲和能$\mathrm{EA}=V_{\mathrm{vac}}-\mathrm{CBM}$。这里IP约5.9970 eV、EA约5.2297 eV。

以1–3 Å的下侧平台为例，先把三种能级放到相同真空零点：

| 能级 | 原始SCF能量 / eV | 减去下侧真空后 / eV |
| --- | ---: | ---: |
| VBM | −2.690722 | −5.997005412 |
| EF | −2.478300 | −5.784583412 |
| CBM | −1.923449 | −5.229732412 |

因此EF比VBM高0.212422 eV，CBM比EF高0.554851 eV，两段相加恢复0.767273 eV的采样隙。功函数也可从两个方向核对：$\Phi=\mathrm{IP}-(E_{\mathrm F}-\mathrm{VBM})=\mathrm{EA}+(\mathrm{CBM}-E_{\mathrm F})$。代入本例均为5.784583412 eV，不能把IP或EA中的任意一个直接改名为功函数。原始数据见[同次SCF摘要](/Atlas/examples/interface-magnet-workfunction/workfunction-summary.json)。

若带边与表面势保持固定，只让带隙内化学势上移δ，Φ随之减小δ，而IP、EA不变；这是区分这三个量的参照操作，不是本例新增的掺杂计算。真实掺杂或吸附还可能改变势与带边，需要重新检查同次输出。选上侧平台时三个真空参照能级一起变化约18.1 μeV，带隙及EF距带边的两段差仍不变。

本例非自旋极化、26电子，第13带最高值与第14带最低值用于采样带边。程序先核对均匀k点权重和占据，再做取差；金属或SOC/自旋模型需要按实际占据处理。[EIGENVAL](https://vasp.at/wiki/EIGENVAL)。

![SnSe₂真空参照的整胞势与费米能](/Atlas/examples/interface-magnet-workfunction/interface-magnet-workfunction-profile.svg)

<figure>
<img src="/Atlas/figures/literature/zhang2025-zri2-graphene-fig4d.png" alt="公开论文原始Fig.4(d)面板" />
<figcaption>Zhang 等，Phys. Chem. Chem. Phys. 27, 19410–19417 (2025)，原文第 5 页 Fig. 4(d)：ZrI₂/graphene 的平面平均静电势，横轴为法向位置 Å，纵轴为 eV，图中箭头表示真空能级与费米能之差。<a href="https://doi.org/10.1039/D5CP02349A">论文原文</a>。</figcaption>
</figure>

原图中紫色虚线标真空能级，青色虚线标费米能，黄色势剖面与原子层示意共用法向坐标；两线之差由黑色箭头标出。本站 SnSe₂ 的实际势和两个真空窗口已在上图显示，数值仍来自本页自己的同次 OUTCAR/LOCPOT。对计算图，可参照 [ZrI₂/graphene 原文 Fig. 4(d)](https://doi.org/10.1039/D5CP02349A)的双参照线与差值箭头，而不是UPS横轴：用gnuplot读已有两列法向势，把真空区间均值和同次EF画成水平参考，再标两者之差。本站上方 SnSe₂ 计算图的整条势与EF同时减去下侧Vvac，箭头才表示Φ；两侧真空窗口及原子范围保留。把曲线各自减最大值会毁掉能级关系。图中的输出反映指定结构和PBE，不作为未经精度检查的材料常数。

## 接触前参照怎样进入界面分析

低功函数的一侧具有较高的电子化学势倾向，但转移方向与大小还受界面态、杂化、结构响应和偶极影响。[ZrI₂接触论文Fig. 4、5](https://doi.org/10.1039/D5CP02349A)先比较法向势，再用真实三维/平面CDD确认积累与耗尽方向；这一联合分析比只按孤立功函数差报转移量更完整。

本站 [能级对齐](/Atlas/m/band-alignment/vasp/) 用共同晶胞下冻结的SnSe₂/Sr₂N层作参考；它的SnSe₂面内晶格与本例不同，所以不能将本例Φ或带边直接搬入那组比较。接触后的 [CDD层积分](/Atlas/m/delta-charge/vasp/) 与 [Bader层加总](/Atlas/m/bader/vasp/)各自给分区转移数，再除真实面积。Φ以eV计，面积密度以e/cm²计，两者没有无需电子结构响应就能直接互换的公式。

## 从原始文件重建读数

明确源格式、窗口、化学势与带边读取约定后，可用以下请求复现本例。完整脚本同时核对LVHAR、EDIFF、网格、电子数及占据，不自动猜真空区间。

```text
请为 VASP 5.4.4 的这个非自旋极化 SnSe2 单层示例编写独立 Python 3 命令行分析脚本。输入为当前目录中的 LOCPOT、OUTCAR、EIGENVAL；用户可用 --windows LOW:HIGH 指定一个或多个以 Å 为单位的真空窗口。

LOCPOT 是 POSCAR 头部、三维网格尺寸 nx ny nz 和一个标量势块；该势以 eV 为单位，x 方向变化最快。校验势值数量正好为 nx*ny*nz 且均为有限数，把数组按 (nz,ny,nx) 重排；用每个 xy 平面的算术平均求 Vbar(z)，z_k=k*h/nz，其中 h=abs(c·(a×b))/|a×b|，坐标单位为 Å。

从 OUTCAR 读取 NELECT 和 E-fermi，并确认输出出现 EDIFF 收敛标记、LVHAR=T、LVTOT=F 和 ISPIN=1。解析 EIGENVAL 中的 k 点权重、本征值和占据数；权重和与按权重汇总的电子数分别在 1e-5 和 1e-3 容差内匹配 1 与 NELECT。按 NELECT/2 确定边界，要求所有 k 点的第 13 带占据不低于 0.5、第 14 带不高于 0.5，再检查采样 CBM 高于 VBM。若输入是自旋极化、金属、缺少数据或格式不支持，清楚报错退出，禁止假定费米能、猜测带边、补零或静默接受坏数据。

每个窗口输出采样平面数、Vbar 均值、总体标准差、最大值减最小值，以及 Phi=Vvac-EF、IP=Vvac-VBM、EA=Vvac-CBM。VBM/CBM 只报 EIGENVAL 当前 k 网格采样值。输出 PLANAR_AVERAGE.dat（z_A, planar_potential_eV）和带有输入 SHA256、单位、公式、窗口数据及限制说明的 workfunction-summary.json。

另写单面板绘图脚本，读取上述文件并导出 PNG、SVG、PDF。显示完整晶胞势曲线、费米能、POSCAR 原子层法向范围和被统计的真空窗口；用下方 Vvac 作为唯一能量零点。图注注明 VASP 版本、网格、窗口、E_F 约定和本结果尚未验证的收敛项。不要用平滑、插值或拟合隐藏势斜率，也不要另行放大 −0.0181 meV 的两侧均值差；窗口不平坦时报告诊断，不要把标准差包装成收敛误差。
```

[analyze_workfunction.py](/Atlas/examples/interface-magnet-workfunction/analyze_workfunction.py)、[plane_average.py](/Atlas/examples/interface-magnet-workfunction/plane_average.py)、[workfunction_values.py](/Atlas/examples/interface-magnet-workfunction/workfunction_values.py)和绘图源码在文末。Python 3需要NumPy/Matplotlib，源码与样式模块随资料包提供。

```bash
python3 analyze_workfunction.py --windows 1:3 15:17
python3 plot_workfunction.py
```

先重建两列势与 [摘要](/Atlas/examples/interface-magnet-workfunction/workfunction-summary.json)，再由这些数字生成整胞势图。完整数值：下侧Φ=5.784583412 eV，上侧5.784565353 eV；各能级沿同一参照取差。


## 完整源码与执行记录

<details>
<summary>analyze_workfunction.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Rebuild planar potential and vacuum-referenced levels from VASP outputs.

Required files in the current directory: LOCPOT, OUTCAR, EIGENVAL.
The reader is intentionally restricted to a non-spin-polarized, gapped,
single-scalar LOCPOT case. It rejects unsupported inputs instead of guessing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np

A = np.asarray


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_locpot(path: Path):
    lines = path.read_text(errors="strict").splitlines()
    if len(lines) < 10:
        raise ValueError("LOCPOT is too short to contain a POSCAR header and grid")
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError("This example reader requires a positive POSCAR scale")
    cell = A([[float(x) * scale for x in lines[i].split()[:3]]
              for i in (2, 3, 4)], dtype=float)
    index = 5
    species_or_counts = lines[index].split()
    index += 1
    if all(re.fullmatch(r"\d+", word) for word in species_or_counts):
        counts = [int(word) for word in species_or_counts]
    else:
        counts = [int(word) for word in lines[index].split()]
        index += 1
    mode = lines[index].strip().lower()
    index += 1
    if mode.startswith("s"):
        mode = lines[index].strip().lower()
        index += 1
    if not (mode.startswith("d") or mode.startswith("c") or mode.startswith("k")):
        raise ValueError(f"Unrecognized coordinate mode in LOCPOT header: {mode!r}")
    natoms = sum(counts)
    if natoms <= 0:
        raise ValueError("Invalid atom counts in LOCPOT header")
    index += natoms
    while index < len(lines) and not lines[index].strip():
        index += 1
    grid = tuple(map(int, lines[index].split()))
    index += 1
    if len(grid) != 3 or min(grid) <= 0:
        raise ValueError(f"Invalid LOCPOT grid dimensions: {grid}")
    nx, ny, nz = grid
    expected = nx * ny * nz
    fields = []
    for line in lines[index:]:
        fields.extend(float(token.replace("D", "E").replace("d", "e"))
                      for token in line.split())
    if len(fields) != expected:
        raise ValueError(
            f"Expected one scalar potential block ({expected} values), found {len(fields)}"
        )
    values = np.asarray(fields, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("LOCPOT contains non-finite potential values")
    normal = np.cross(cell[0], cell[1])
    area = np.linalg.norm(normal)
    if area == 0:
        raise ValueError("The first two lattice vectors do not span a surface")
    normal_height = abs(float(np.dot(cell[2], normal))) / area
    if normal_height <= 0:
        raise ValueError("Invalid cell height along the surface normal")
    # VASP writes x fastest, then y, with z as the slowest index.
    field = values.reshape((nz, ny, nx))
    planar = field.mean(axis=(1, 2))
    z = np.arange(nz, dtype=float) * normal_height / nz
    return grid, normal_height, z, planar


def outcar_values(path: Path):
    text = path.read_text(errors="strict")
    if "aborting loop because EDIFF is reached" not in text:
        raise ValueError("OUTCAR has no EDIFF convergence marker")
    if "General timing and accounting" not in text:
        raise ValueError("OUTCAR has no final timing/accounting section")
    if "LVHAR" not in text or not re.search(r"LVHAR\s*=\s*T\b", text):
        raise ValueError("OUTCAR does not confirm LVHAR=T")
    if re.search(r"LVTOT\s*=\s*T\b", text):
        raise ValueError("OUTCAR also has LVTOT=T; this route expects LVHAR only")
    ispin = re.findall(r"^\s*ISPIN\s*=\s*(\d+)", text, flags=re.M)
    nelect = re.findall(r"^\s*NELECT\s*=\s*([-+0-9.]+)", text, flags=re.M)
    efermi = re.findall(r"E-fermi\s*:\s*([-+0-9.]+)", text)
    if not ispin or int(ispin[-1]) != 1:
        raise ValueError("This band-edge reader requires a non-spin-polarized ISPIN=1 run")
    if not nelect or not efermi:
        raise ValueError("OUTCAR is missing NELECT or E-fermi")
    return int(round(float(nelect[-1]))), float(efermi[-1])


def read_eigenval(path: Path, expected_electrons: int):
    with path.open() as stream:
        for _ in range(5):
            if not stream.readline():
                raise ValueError("EIGENVAL ended before its electron/k-point/band header")
        try:
            electrons, nkpoints, nbands = map(int, stream.readline().split())
        except Exception as exc:
            raise ValueError("Invalid EIGENVAL electron/k-point/band header") from exc
        if electrons != expected_electrons:
            raise ValueError(
                f"EIGENVAL has {electrons} electrons but OUTCAR has {expected_electrons}"
            )
        if electrons % 2:
            raise ValueError("An even electron count is required for this ISPIN=1 example")
        nocc = electrons // 2
        if not (0 < nocc < nbands):
            raise ValueError("EIGENVAL does not contain both occupied and empty bands")
        k_weights, energies, occupations = [], [], []
        for _ in range(nkpoints):
            line = stream.readline()
            while line and not line.strip():
                line = stream.readline()
            if not line:
                raise ValueError("EIGENVAL ended before all k-point blocks were read")
            point = list(map(float, line.split()))
            if len(point) != 4:
                raise ValueError("Expected kx ky kz weight on each EIGENVAL k-point line")
            k_weights.append(point[3])
            e_k, occ_k = [], []
            for _ in range(nbands):
                row = stream.readline().split()
                if len(row) != 3:
                    raise ValueError("Expected band index, energy, and occupation (ISPIN=1)")
                band_index, energy, occupation = map(float, row)
                e_k.append(energy)
                occ_k.append(occupation)
            energies.append(e_k)
            occupations.append(occ_k)
    weights = np.asarray(k_weights, dtype=float)
    eigenvalues = np.asarray(energies, dtype=float)
    occ = np.asarray(occupations, dtype=float)
    if abs(float(weights.sum()) - 1.0) > 1e-5:
        raise ValueError(f"EIGENVAL k-point weights sum to {weights.sum():.8g}, not 1")
    weighted_electrons = 2.0 * float(np.sum(weights[:, None] * occ))
    if abs(weighted_electrons - expected_electrons) > 1e-3:
        raise ValueError(
            f"Weighted EIGENVAL occupations give {weighted_electrons:.8f} electrons, "
            f"not {expected_electrons}"
        )
    if float(occ[:, nocc - 1].min()) < 0.5 or float(occ[:, nocc].max()) > 0.5:
        raise ValueError(
            "The NELECT/2 band boundary is partially occupied; this is not a gapped "
            "non-spin-polarized case"
        )
    vbm = float(eigenvalues[:, nocc - 1].max())
    cbm = float(eigenvalues[:, nocc].min())
    if cbm <= vbm:
        raise ValueError("Sampled EIGENVAL band edges do not form a positive gap")
    return {
        "electrons": electrons,
        "nkpoints": nkpoints,
        "bands": nbands,
        "weighted_electrons": weighted_electrons,
        "vbm_eV": vbm,
        "cbm_eV": cbm,
        "indirect_gap_eV": cbm - vbm,
    }


def parse_window(spec: str):
    try:
        low, high = map(float, spec.split(":"))
    except Exception as exc:
        raise argparse.ArgumentTypeError("Use a window such as 1:3 (angstrom)") from exc
    if not (math.isfinite(low) and math.isfinite(high) and low < high):
        raise argparse.ArgumentTypeError("Window endpoints must be finite with low < high")
    return low, high


def main():
    parser = argparse.ArgumentParser(
        description="Average LVHAR from LOCPOT and align the gapped band edges to vacuum."
    )
    parser.add_argument(
        "--windows", nargs="+", type=parse_window, default=[(1.0, 3.0), (15.0, 17.0)],
        metavar="LOW:HIGH", help="vacuum windows in angstrom (default: 1:3 15:17)"
    )
    args = parser.parse_args()
    if not args.windows:
        raise ValueError("At least one vacuum window is required")
    loct = Path("LOCPOT")
    outcar = Path("OUTCAR")
    eigenval = Path("EIGENVAL")
    if not all(path.is_file() for path in (loct, outcar, eigenval)):
        raise FileNotFoundError("Run in a directory containing LOCPOT, OUTCAR, EIGENVAL")

    grid, height, z, potential = read_locpot(loct)
    nelect, ef = outcar_values(outcar)
    bands = read_eigenval(eigenval, nelect)
    windows = []
    for low, high in args.windows:
        if low < 0 or high > height:
            raise ValueError(
                f"Window {low:g}:{high:g} A lies outside 0:{height:.8f} A"
            )
        chosen = (z >= low) & (z <= high)
        values = potential[chosen]
        if values.size == 0:
            raise ValueError(f"Window {low:g}:{high:g} A contains no LOCPOT planes")
        mean = float(values.mean())
        row = {
            "lo_A": low, "hi_A": high, "n": int(values.size),
            "mean_eV": mean,
            "std_eV": float(values.std(ddof=0)),
            "range_eV": float(values.max() - values.min()),
            "vacuum_minus_fermi_eV": mean - ef,
            "vacuum_minus_vbm_eV": mean - bands["vbm_eV"],
            "vacuum_minus_cbm_eV": mean - bands["cbm_eV"],
        }
        windows.append(row)

    order = sorted(windows, key=lambda item: item["lo_A"])
    for left, right in zip(order, order[1:]):
        if left["hi_A"] > right["lo_A"]:
            raise ValueError("Vacuum windows overlap")

    np.savetxt(
        "PLANAR_AVERAGE.dat", np.column_stack((z, potential)),
        fmt=("%.10f", "%.12f"),
        header="z_A  planar_potential_eV",
        comments="# ",
    )
    result = {
        "code": "VASP",
        "potential_component": "LVHAR (ionic + Hartree; LVTOT is false)",
        "surface_normal": "normal to lattice vectors a and b",
        "normal_height_A": height,
        "grid": list(grid),
        "scalar_values": int(np.prod(grid)),
        "ispin": 1,
        "electrons": nelect,
        "nkpoints": bands["nkpoints"],
        "bands": bands["bands"],
        "weighted_electrons": bands["weighted_electrons"],
        "fermi_eV": ef,
        "vbm_eV": bands["vbm_eV"],
        "cbm_eV": bands["cbm_eV"],
        "indirect_gap_eV": bands["indirect_gap_eV"],
        "formula": {
            "work_function_eV": "V_vacuum - E_F",
            "ionization_potential_eV": "V_vacuum - VBM",
            "electron_affinity_eV": "V_vacuum - CBM",
            "potential_spread_eV": "max(Vbar) - min(Vbar) within each selected window",
        },
        "windows": windows,
        "input_sha256": {
            path.name: sha256(path) for path in (loct, outcar, eigenval)
        },
        "limits": [
            "EIGENVAL band edges are extrema on the sampled SCF k mesh, not a continuous-Brillouin-zone search.",
            "E_F in a semiconductor is the chemical potential printed for this occupation setup; it can move within the gap.",
            "Window spread is a local flatness diagnostic, not an uncertainty or convergence estimate.",
        ],
    }
    Path("workfunction-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(
        f"grid={grid}; scalar values={int(np.prod(grid))}; normal height={height:.10f} A"
    )
    print(
        f"NELECT={nelect}; NKPTS={bands['nkpoints']}; weighted electrons="
        f"{bands['weighted_electrons']:.8f}; E_F={ef:.6f} eV"
    )
    print(
        f"sampled VBM={bands['vbm_eV']:.6f} eV; CBM={bands['cbm_eV']:.6f} eV; "
        f"gap={bands['indirect_gap_eV']:.6f} eV"
    )
    for item in windows:
        print(
            f"z={item['lo_A']:.2f}:{item['hi_A']:.2f} A N={item['n']} "
            f"V_vac={item['mean_eV']:.9f} eV std={item['std_eV']:.6g} eV "
            f"range={item['range_eV']:.6g} eV Phi={item['vacuum_minus_fermi_eV']:.9f} eV"
        )


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>plot_workfunction.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Plot the actual full-cell planar LVHAR profile used to inspect the vacuum plateau."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from atlas_plot_style import install

install()


def poscar_atomic_extent(path: Path, normal_height: float, normal: np.ndarray) -> tuple[float, float]:
    """Return the z extent of atomic coordinates projected along the cell normal."""
    lines = path.read_text().splitlines()
    scale = float(lines[1].split()[0])
    cell = np.asarray([[float(x) for x in lines[i].split()[:3]] for i in (2, 3, 4)]) * scale
    i = 5
    fields = lines[i].split()
    i += 1
    if all(word.lstrip("+").isdigit() for word in fields):
        counts = [int(word) for word in fields]
    else:
        counts = [int(word) for word in lines[i].split()]
        i += 1
    if lines[i].strip().lower().startswith("s"):
        i += 1
    mode = lines[i].strip().lower()
    i += 1
    coordinates = np.asarray([
        [float(x) for x in lines[i + j].split()[:3]]
        for j in range(sum(counts))
    ])
    if mode.startswith("d"):
        cartesian = coordinates @ cell
    elif mode.startswith(("c", "k")):
        cartesian = coordinates * scale
    else:
        raise ValueError(f"Unsupported POSCAR coordinate mode: {mode!r}")
    z = np.mod(cartesian @ normal, normal_height)
    return float(z.min()), float(z.max())


profile_path = Path("PLANAR_AVERAGE.dat")
summary_path = Path("workfunction-summary.json")
if not profile_path.is_file() or not summary_path.is_file():
    raise FileNotFoundError("Run analyze_workfunction.py first")

profile = np.loadtxt(profile_path, comments="#")
summary = json.loads(summary_path.read_text())
windows = sorted(summary["windows"], key=lambda item: item["lo_A"])
if profile.ndim != 2 or profile.shape[1] != 2:
    raise ValueError("Expected z_A and planar_potential_eV columns")
if len(windows) != 2:
    raise ValueError("This example expects its two measured surface vacuum windows")
z, potential = profile[:, 0], profile[:, 1]
height = float(summary["normal_height_A"])
if not np.all(np.isfinite(profile)) or z.max() >= height:
    raise ValueError("Profile contains invalid values or an out-of-cell z coordinate")

cell = np.asarray([[float(x) for x in line.split()[:3]]
                   for line in Path("POSCAR").read_text().splitlines()[2:5]], dtype=float)
scale = float(Path("POSCAR").read_text().splitlines()[1].split()[0])
cell *= scale
normal = np.cross(cell[0], cell[1])
normal /= np.linalg.norm(normal)
if np.dot(cell[2], normal) < 0:
    normal *= -1.0
atom_lo, atom_hi = poscar_atomic_extent(Path("POSCAR"), height, normal)

vacuum_reference = float(windows[0]["mean_eV"])
relative_potential = potential - vacuum_reference
fermi_relative = float(summary["fermi_eV"]) - vacuum_reference
work_function = vacuum_reference - float(summary["fermi_eV"])
colors = ("#0072b2", "#d55e00")

fig, ax = plt.subplots(figsize=(8.1, 4.8), layout="constrained")
ax.plot(z, relative_potential, color="#222222", lw=1.25,
        label=r"Planar-averaged $V_{\mathrm{LVHAR}}(z)$")
ax.axhline(0.0, color=colors[0], ls="--", lw=1.0,
           label="Lower-z vacuum reference")
ax.axhline(fermi_relative, color=colors[1], ls="-.", lw=1.0,
           label=r"$E_F$ from the same SCF")
ax.axvspan(atom_lo, atom_hi, color="#777777", alpha=0.12, zorder=0)
for window in windows:
    ax.axvspan(window["lo_A"], window["hi_A"], color=colors[0], alpha=0.08, zorder=0)

handles = [
    Line2D([0], [0], color="#222222", lw=1.25,
           label=r"Planar-averaged $V_{\mathrm{LVHAR}}(z)$"),
    Line2D([0], [0], color=colors[0], ls="--", lw=1.0,
           label="Lower-z vacuum reference"),
    Line2D([0], [0], color=colors[1], ls="-.", lw=1.0,
           label=r"$E_F$ from the same SCF"),
    Patch(facecolor="#777777", alpha=0.12, label="Atomic z extent from POSCAR"),
    Patch(facecolor=colors[0], alpha=0.08, label="Vacuum windows used in the table"),
]
ax.legend(handles=handles, frameon=False, ncols=2, loc="lower left")
arrow_x = 2.55
ax.annotate(
    "", xy=(arrow_x, fermi_relative), xytext=(arrow_x, 0.0),
    arrowprops={"arrowstyle": "<->", "color": colors[1], "lw": 1.1},
)
ax.text(arrow_x + 0.22, 0.5 * fermi_relative,
        rf"$\Phi={work_function:.4f}\ \mathrm{{eV}}$",
        color=colors[1], ha="left", va="center")

span = float(relative_potential.max() - relative_potential.min())
ax.set_xlim(0.0, height)
ax.set_ylim(relative_potential.min() - 0.04 * span,
            relative_potential.max() + 0.04 * span)
ax.set_xlabel("Distance along the surface normal (Å)")
ax.set_ylabel(r"$\bar{V}(z)-V_{\mathrm{vac,lower}}$ (eV)")
ax.set_title(r"SnSe$_2$ monolayer: planar-averaged LVHAR and work-function reference")
ax.grid(False)

output = "interface-magnet-workfunction-profile.png"
fig.savefig(output)
plt.close(fig)

upper_minus_lower = float(windows[1]["mean_eV"] - windows[0]["mean_eV"])
print(f"Wrote interface-magnet-workfunction-profile.png, .svg, and .pdf")
print(f"Lower-z Vvac = {vacuum_reference:.9f} eV; E_F = {summary['fermi_eV']:.6f} eV")
print(f"Phi at the printed E_F = {work_function:.9f} eV")
print(f"Upper-minus-lower vacuum mean = {upper_minus_lower * 1000.0:+.5f} meV")
print("That last difference is reported numerically only; it is not resolved as a material effect.")
```

</details>

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
    if any(math.isnan(x) or math.isinf(x) for x in vals):
        raise ValueError("Non-finite potential value")
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
<summary>workfunction_values.py 的完整源码</summary>

```python
from __future__ import print_function
import json,re,hashlib
out=open('OUTCAR').read()
if 'aborting loop because EDIFF is reached' not in out:
    raise ValueError('Electronic convergence line is absent')
if 'General timing and accounting' not in out:
    raise ValueError('Normal final accounting section is absent')
ef=float(re.findall(r'E-fermi\s*:\s*([-+0-9.]+)',out)[-1])
p=json.load(open('potential-summary.json'))
with open('EIGENVAL') as f:
    for i in range(5): f.readline()
    ne,nk,nb=map(int,f.readline().split())
    if ne % 2: raise ValueError('This band-edge reader expects even-electron, non-spin-polarized input')
    occupied=[];empty=[]
    for ik in range(nk):
        line=f.readline()
        while line and not line.strip(): line=f.readline()
        if not line: raise ValueError('Truncated EIGENVAL before k point')
        if len(line.split())!=4: raise ValueError('Invalid k-point line')
        bands=[list(map(float,f.readline().split())) for ib in range(nb)]
        if any(len(row)!=3 for row in bands): raise ValueError('Invalid or truncated non-spin EIGENVAL band block')
        occupied.append(bands[ne//2-1][1]);empty.append(bands[ne//2][1])
vbm=max(occupied);cbm=min(empty)
r={'fermi_eV':ef,'vbm_eV':vbm,'cbm_eV':cbm,'indirect_gap_eV':cbm-vbm,'nkpoints':nk,'bands':nb,'electrons':ne,'windows':[]}
for w in p['windows']:
    item=dict(w)
    item['vacuum_minus_fermi_eV']=w['mean_eV']-ef
    item['vacuum_minus_vbm_eV']=w['mean_eV']-vbm
    item['vacuum_minus_cbm_eV']=w['mean_eV']-cbm
    r['windows'].append(item)
json.dump(r,open('workfunction-summary.json','w'),indent=2)
print('E_F = %.6f eV; VBM = %.6f eV; CBM = %.6f eV; gap = %.6f eV'%(ef,vbm,cbm,cbm-vbm))
for w in r['windows']:
    print('z = %.2f:%.2f A; V_vac = %.9f eV; Phi(E_F) = %.9f eV; V_vac-VBM = %.9f eV; V_vac-CBM = %.9f eV'%(w['lo_A'],w['hi_A'],w['mean_eV'],w['vacuum_minus_fermi_eV'],w['vacuum_minus_vbm_eV'],w['vacuum_minus_cbm_eV']))
```

</details>

<details>
<summary>同一算例的其余输入、检查命令与保存输出</summary>

```text
[bcgong@localhost snse2_workfunction]$ tail -8 OSZICAR
DAV:  16    -0.118616121789E+02   -0.11011E-04   -0.16797E-07  4460   0.284E-03    0.893E-04
DAV:  17    -0.118616188163E+02   -0.66374E-05   -0.38095E-07  4636   0.216E-03    0.126E-03
DAV:  18    -0.118616239345E+02   -0.51182E-05   -0.15024E-07  4476   0.217E-03    0.320E-04
DAV:  19    -0.118616257043E+02   -0.17698E-05   -0.56160E-08  4528   0.662E-04    0.339E-04
DAV:  20    -0.118616260960E+02   -0.39175E-06   -0.97347E-09  4376   0.391E-04    0.116E-04
DAV:  21    -0.118616262047E+02   -0.10867E-06   -0.18647E-09  4340   0.150E-04    0.186E-05
DAV:  22    -0.118616262492E+02   -0.44434E-07   -0.62584E-10  3884   0.883E-05
   1 F= -.12268138E+02 E0= -.12268138E+02  d E =-.349964E-11
```

```text
[bcgong@localhost snse2_workfunction]$ head -7 OUTCAR
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 executed on             LinuxIFC date 2026.09.22  22:13:18
 running on    8 total cores
 distrk:  each k-point on    8 cores,    1 groups
 distr:  one band on NCORES_PER_BAND=   2 cores,    4 groups
```

```text
[bcgong@localhost snse2_workfunction]$ ls -lh OUTCAR OSZICAR CHGCAR LOCPOT EIGENVAL WAVECAR
-rw-rw-r-- 1 bcgong bcgong  18M Sep 22 22:14 CHGCAR
-rw-rw-r-- 1 bcgong bcgong  77K Sep 22 22:14 EIGENVAL
-rw-rw-r-- 1 bcgong bcgong  18M Sep 22 22:14 LOCPOT
-rw-rw-r-- 1 bcgong bcgong 2.1K Sep 22 22:14 OSZICAR
-rw-rw-r-- 1 bcgong bcgong 189K Sep 22 22:14 OUTCAR
-rw-rw-r-- 1 bcgong bcgong    0 Sep 22 22:13 WAVECAR
```

```text
[bcgong@localhost snse2_workfunction]$ head -5 PLANAR_AVERAGE.dat
# z_A  planar_potential_eV
0.0000000000 3.306285072550
0.0655617786 3.306304853416
0.1311235571 3.306285038010
0.1966853357 3.306304820274
```

```text
固定结构 + 同一套赝势 / 均匀 k 网格
  └─ SCF + LVHAR
       ├─ OUTCAR → 收敛与 E_F
       ├─ EIGENVAL → 当前网格的 VBM / CBM
       └─ LOCPOT → 平面平均 → 平坦真空窗口
                                    └─ V_vac − E_F；同时注明带隙中的化学势
```

</details>


## 与表面测量的条件一起比较

<figure>
<img src="/Atlas/figures/literature/lee2013-ca2n-fig4bc.png" alt="Lee等Ca2N原文Fig.4(b,c)的UPS与偏置对照" />
<figcaption>Lee 等，Nature 494, 336–340 (2013)，PDF 第 4 页 Fig. 4(b,c)：单晶/多晶 UPS 二次电子发射和偏置外推；主图动能为 eV、强度为任意单位，各偏置由图例颜色区分。<a href="https://doi.org/10.1038/nature11812">论文原文</a>。</figcaption>
</figure>

Ca₂N原文 [Lee等，Nature 494, 336 (2013), Fig. 4(b,c)](https://doi.org/10.1038/nature11812)分别显示单晶和多晶的UPS二次电子发射：横轴为动能/eV，纵轴为任意强度，不是DFT静电势。(c)内嵌图将截断能对样品偏置作比较，并外推至零偏置；单晶还区分光子产额，(b)内嵌图检查费米边和价带谱。作者借这些对照辨别表面与光致电压的影响，说明测量条件和表面朝向必须随功函数一起报告。本站则从指定SnSe₂结构的同次SCF求真空势与EF，不用UPS谱线强度或Ca₂N读数替代自己的计算。间隙态的联合图法见 [ELF与选中态密度](/Atlas/m/elf/vasp/)。
