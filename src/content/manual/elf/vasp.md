电子位于原子间隙，是从什么数据看出来的？ELF给局域化函数，能窗或带分解密度给选中电子态的空间分布，两者需要放在同一结构中读。总电荷密度含全部占据态，CDD给相对于冻结参考的增减，都不能单独指出某条间隙电子带。

H-ZrCl₂的原文提供一个贴近研究主线的比较：[He等，J. Mater. Chem. C 10, 7674 (2022), Fig. 2](https://doi.org/10.1039/D2TC00564F)。Fig. 2(a)先识别独立价带，(b)用ELF=0.6定位六角中心X，(c)比较空球X投影与原子投影，(d)展示该孤立带的分解密度。作者讨论的是H相ZrCl₂单层；把这些步骤放在一起，才把局域化位置与实际能带联系起来。下文真实bcc Fe存档只演示ELFCAR格式、两个自旋通道和VESTA操作。

前置 [SCF](/Atlas/m/scf/vasp/) 完成固定结构电子态。下载 [Fe输入、OUTCAR与ELFCAR](/Atlas/examples/vasp/fe-bcc-lesson-files.tar.gz)，使用 `charge_elf_192`。Fe结构和本次自旋分支可从该包内 `charge_elf_192/POSCAR`、`charge_elf_192/INCAR` 与 `charge_elf_192/OUTCAR`核对；粗网格对应记录在 `charge_elf`。

## LELF输出来自哪个网格

```text
[bcgong@localhost charge_elf_192]$ cat INCAR
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
NGXF = 192
NGYF = 192
NGZF = 192

NGX = 36
NGY = 36
NGZ = 36
```

```text
[bcgong@localhost charge_elf_192]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-fe-grid192
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

这是VASP 5.4.4、共线ISPIN=2，显式NPAR=1并由8个MPI进程运行；NPAR不是CPU总数。LELF写ELFCAR，本例36³粗网格控制它的采样，192³细网格同时供CHGCAR/AECCAR使用。网格密度不会因绘图插值而增加。

```text
[bcgong@localhost charge_elf_192]$ tail -4 OSZICAR
DAV:  16    -0.164736471272E+02    0.20405E-07   -0.31078E-09  2807   0.760E-04    0.228E-04
DAV:  17    -0.164736471409E+02   -0.13691E-07   -0.30315E-10  2702   0.201E-04    0.489E-05
DAV:  18    -0.164736471451E+02   -0.41252E-08   -0.60352E-11  2639   0.102E-04
   1 F= -.16473647E+02 E0= -.16473764E+02  d E =0.351572E-03  mag=     4.2127
```

```text
[bcgong@localhost charge_elf_192]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```

```text
[bcgong@localhost charge_elf_192]$ grep -E 'dimension x,y,z|LELF' OUTCAR
   dimension x,y,z NGX =    36 NGY =   36 NGZ =   36
   dimension x,y,z NGXF=   192 NGYF=  192 NGZF=  192
   dimension x,y,z NGX =    18 NGY =   18 NGZ =   18
   LELF         =      T    write electronic localiz. function (ELF)
```

```text
[bcgong@localhost charge_elf_192]$ head -15 ELFCAR
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
 
   36   36   36
 0.18012E-01 0.31080E-03 0.73938E-04 0.16325E-03 0.73557E-03 0.30330E-02 0.95991E-02 0.23283E-01 0.44567E-01 0.69501E-01
 0.90951E-01 0.10258     0.10283     0.96336E-01 0.90702E-01 0.91312E-01 0.98696E-01 0.10827     0.11271     0.10827    
 0.98696E-01 0.91312E-01 0.90702E-01 0.96336E-01 0.10283     0.10258     0.90951E-01 0.69501E-01 0.44567E-01 0.23283E-01
```

电子循环达EDIFF，最终磁矩约4.2127 μB/胞。ELFCAR自己写的是36×36×36，共46,656个点。第一块是ELF↑，第二块是ELF↓；它们不是总密度与磁化密度这对CHGCAR变量。函数无量纲，不除体积、不按自身最大值归一化。[ELFCAR官方定义](https://vasp.at/wiki/ELFCAR)。

ELF=1/[1+(D/Dh)²]比较同自旋电子局域化与均匀电子气参照；均匀气对应0.5。空间上高值通常提示局域化增强，但ELF本身没有电子数单位，等值面包围体积或ELF积分不能给载流子数。定义讨论见 [Savin, J. Mol. Struct.: THEOCHEM 727, 127 (2005)](https://doi.org/10.1016/j.theochem.2005.02.034)。

## 分离自旋块并保持原始值

[下载单块文件、场景与脚本](/Atlas/examples/charge-vesta-files.tar.gz)，进入 `charge-vesta`。需要复现分离操作时，可使用下面的需求；[split_elf_spin_channels.py](/Atlas/examples/charge-vesta/scripts/split_elf_spin_channels.py)只依赖Python标准库。

```text
编写 Python 3 标准库命令行程序 split_elf_spin_channels.py。输入 --input 为本例 ISPIN=2、共线自旋 VASP ELFCAR；--output-dir 为新目标目录。保留 POSCAR 风格结构头，识别两次三整数网格尺寸，第一块为 ELF_up、第二块为 ELF_down；检查尺寸相同，逐块恰好 nx*ny*nz 个有限数值，范围0–1。x索引最快。不能把原子坐标误认为网格头，不能合并、平均、除体积或除最大值。检查两块之间及末尾无额外未解析内容，遇到本例以外的布局清楚报错。分别写 ELFCAR_up.vasp、ELFCAR_down.vasp，只含结构与一块网格；JSON记录输入SHA256、网格、通道顺序、每通道min/max/mean。所有目标文件应在写入前检查，已有文件则拒绝覆盖。终端打印验证摘要。GUI操作使用VESTA逐一打开两文件，Properties → Isosurfaces设同一无量纲阈值0.10，保存各场景并File → Export Raster Image导出PNG。保持网格与阈值不变；图注标通道、阈值、36³采样，区分原始网格与显示插值。
```

```bash
python3 -B scripts/split_elf_spin_channels.py --input elf/ELFCAR --output-dir new-elf
```

```text
grid: 36 36 36 (46656 points per spin channel)
ELF_up: min=0.00007131 max=0.13286000 mean=0.09257966
ELF_down: min=0.00011024 max=0.33390000 mean=0.15832494
wrote: ELFCAR_up.vasp
wrote: ELFCAR_down.vasp
```

上下通道各有46,656个有限值，完整范围在 [摘要](/Atlas/examples/charge-vesta/elf/elf-spin-channels.summary.json)。Fe数据的最大ELF很低，因此取0.10观看；H-ZrCl₂论文的0.6不能不看数值范围便照搬。函数值没有被放大到1。

## VESTA的同阈值比较

File → Open打开 `new-elf/ELFCAR_up.vasp`，Properties → Isosurfaces设置ELF=0.10，蓝色半透明等值面、金色Fe球。Export Raster Image导出PNG，并保存场景。再打开down文件，用相同阈值。已保存的 [up场景](/Atlas/examples/charge-vesta/elf/elf-up.vesta) 和 [down场景](/Atlas/examples/charge-vesta/elf/elf-down.vesta)按相对路径导入各自网格。

<figure><img src="/Atlas/examples/elf/elf_up_isosurface.png" alt="bcc Fe上自旋ELF=0.10真实VESTA等值面" loading="lazy"/><figcaption>ELF↑=0.10，36³原始网格。蓝色等值面和金色Fe原子显示这一阈值的空间关系。</figcaption></figure>

<figure><img src="/Atlas/examples/elf/elf_down_isosurface.png" alt="bcc Fe下自旋ELF=0.10真实VESTA等值面" loading="lazy"/><figcaption>ELF↓=0.10，原始网格与阈值相同。两张保存截图视向不同，先按晶轴对应方向；投影面积不用于计算电子数。</figcaption></figure>

形貌不同说明两个自旋通道的局域化函数分布不同。若要归属到d轨道或具体能带，继续读相应投影和态密度；Fe等值面不能作为Sc₂C、H-ZrCl₂或界面的electride证据。

## 从局域化位置到间隙电子态

Ca₂N原文 [Lee等，Nature 494, 336 (2013), Fig. 3(c)](https://doi.org/10.1038/nature11812)把间隙带全部占据态的密度、EF附近窄窗密度和总密度ELF并列。前两幅回答哪一组能态位于层间，第三幅回答局域化函数在哪里较大。近EF窗只是那一小段能态，不能拿它的积分当全部间隙电子；层间局域、面内延展也可以同时出现。Fig. 3(a,b,d)的能带、投影与费米面补充了态的身份与金属性。

对自己的H-ZrCl₂或界面模型，先在能带/投影中选择能窗或带号，写清EF参考、k权重、占据和自旋，再生成该范围的实空间密度。保持同一结构原点，把它与ELF、原子位置及 [DOS](/Atlas/m/dos/qe/) 对照。VASP的 [LPARD](https://vasp.at/wiki/LPARD) 和 [EINT](https://vasp.at/wiki/EINT)给态选择接口；当前Fe资料包没有这条间隙态的完整输出，所以这里不给它安排一份计算结果。孤立单层、层状晶体与界面中的一层要分别核对模型。

[CDD](/Atlas/m/delta-charge/vasp/)与[Bader](/Atlas/m/bader/vasp/)量化接触后的重排和分区数；自由载流子数需要能带占据/费米面。ELF的高值、Bader层净数、窄窗态密度这三种图或数字共同使用时，各自单位与参考仍应保留。


## 完整源码与执行记录

<details>
<summary>split_elf_spin_channels.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Split the two spin-resolved scalar ELF grids in one VASP ELFCAR.

VASP ISPIN=2 writes ELF_up first and ELF_down second. This script copies the
same POSCAR-style geometry header to two VESTA-readable files, each followed
by exactly one scalar grid. It does not add, average, or otherwise combine
the spin channels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

_GRID = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s*$")


def grid_dims(line: str) -> tuple[int, int, int] | None:
    match = _GRID.fullmatch(line)
    return tuple(map(int, match.groups())) if match else None


def read_grid(lines: list[str], start: int, npoints: int, label: str) -> tuple[list[float], int]:
    values: list[float] = []
    cursor = start
    while len(values) < npoints:
        if cursor >= len(lines):
            raise ValueError(f"{label}: ended after {len(values)} of {npoints} values")
        tokens = lines[cursor].split()
        if not tokens:
            raise ValueError(f"{label}: unexpected blank line at grid value {len(values)}")
        row = [float(token.replace("D", "E").replace("d", "e")) for token in tokens]
        if len(values) + len(row) > npoints:
            raise ValueError(f"{label}: extra values on the final grid line")
        values.extend(row)
        cursor += 1
    if not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values):
        raise ValueError(f"{label}: ELF grid contains non-finite or out-of-range values")
    return values, cursor


def write_grid(path: Path, header: list[str], dims: tuple[int, int, int],
               values: list[float], channel: str) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    out_header = list(header)
    out_header[0] = f"Fe bcc FM ELF {channel}; one VASP spin-resolved scalar grid\n"
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.writelines(out_header)
        stream.write("  " + "  ".join(map(str, dims)) + "\n")
        for start in range(0, len(values), 5):
            stream.write(" ".join(f"{value: .8E}" for value in values[start:start + 5]) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="VASP ELFCAR from an ISPIN=2 run")
    parser.add_argument("--output-dir", required=True, type=Path, help="new directory for one-grid VESTA files")
    args = parser.parse_args()

    lines = args.input.read_text(encoding="ascii").splitlines(keepends=True)
    matches = [(index, grid_dims(line)) for index, line in enumerate(lines) if grid_dims(line)]
    matches = [(index, dims) for index, dims in matches if dims is not None]
    if len(matches) != 2:
        raise ValueError(f"Expected exactly two spin-grid headers, found {len(matches)}")
    first_index, dims = matches[0]
    second_index, second_dims = matches[1]
    if second_dims != dims:
        raise ValueError(f"Spin grid mismatch: {dims} vs {second_dims}")
    npoints = math.prod(dims)

    up, after_up = read_grid(lines, first_index + 1, npoints, "ELF_up")
    while after_up < len(lines) and not lines[after_up].strip():
        after_up += 1
    if after_up != second_index:
        raise ValueError(f"Unexpected data between spin channels at line {after_up + 1}")
    down, after_down = read_grid(lines, second_index + 1, npoints, "ELF_down")
    if any(line.strip() for line in lines[after_down:]):
        raise ValueError("Unexpected trailing content after the second ELF grid")

    header = lines[:first_index]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    up_path = args.output_dir / "ELFCAR_up.vasp"
    down_path = args.output_dir / "ELFCAR_down.vasp"
    summary = args.output_dir / "elf-spin-channels.summary.json"
    for path in (up_path, down_path, summary):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}")
    write_grid(up_path, header, dims, up, "spin-up")
    write_grid(down_path, header, dims, down, "spin-down")
    record = {
        "source": str(args.input),
        "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "source_spin_order": ["ELF_up", "ELF_down"],
        "grid": list(dims),
        "points_per_channel": npoints,
        "units": "dimensionless ELF values",
        "channels": {
            "up": {"file": up_path.name, "minimum": min(up), "maximum": max(up), "mean": sum(up) / npoints},
            "down": {"file": down_path.name, "minimum": min(down), "maximum": max(down), "mean": sum(down) / npoints},
        },
        "operation": "split only; no spin summation or averaging",
    }
    summary = args.output_dir / "elf-spin-channels.summary.json"
    if summary.exists():
        raise FileExistsError(f"Refusing to overwrite {summary}")
    summary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"source sha256: {record['source_sha256']}")
    print(f"grid: {dims[0]} {dims[1]} {dims[2]} ({npoints} points per spin channel)")
    for name, values in (("ELF_up", up), ("ELF_down", down)):
        print(f"{name}: min={min(values):.8f} max={max(values):.8f} mean={sum(values)/npoints:.8f}")
    print(f"wrote: {up_path}")
    print(f"wrote: {down_path}")
    print(f"summary: {summary}")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>同一算例的其余输入、检查命令与保存输出</summary>

```text
共线自旋 SCF + LELF + NPAR=1 → ELFCAR 两块验证
  → 分别保存单块 ELF↑/ELF↓ → VESTA 同阈值等值面 → 导出与场景保存
```

</details>
