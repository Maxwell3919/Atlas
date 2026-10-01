## 固定 HfCl₂ 薄层的晶格，调整内部坐标

这份 24 原子 HfCl₂ 薄层输入有 8 个 Hf、16 个 Cl。本次问题是：在已有面内晶格与层间排布下，原子能否走到残余力低于 0.01 eV/Å 的构型？固定晶胞后，原子力驱动内部坐标调整，为后续同晶格的结构比较准备明确末态。面内晶格是否处于平衡，需要另行开放晶胞自由度。

记录来自 bcgong 上于 2026 年 5 月 29 日执行的 VASP 5.4.4。本页读取那次输入、输出与末态，原子位置与晶胞自由度的区别可参照 [QE 方法论文第 4.1 节](https://doi.org/10.1088/0953-8984/21/39/395502)，本例实际的共轭梯度、固定胞设置和力停止条件按 VASP 的 [IBRION](https://vasp.at/wiki/IBRION)、[ISIF](https://vasp.at/wiki/ISIF)、[EDIFFG](https://vasp.at/wiki/EDIFFG) 读取。

[下载完整输入、结果与后处理脚本](/Atlas/examples/vasp/hfcl2-relax-files.tar.gz)，解包得到 `hfcl2-relax`。POTCAR 正文未包含，只有 TITEL/ZVAL，需从自己的授权库按 Cl、Hf 顺序准备。公开 OUTCAR 移除开头 PAW 数据细节回显并标注，`Dimension of arrays` 到结束的计算记录保留原样；运行脚本保留原记录中的环境与程序路径。

## 读完整结构，再指定可动自由度

面内矢量组成六方晶格，面内长度约 3.38753 Å，第三矢量为 100.23893 Å。它是沿 z 排列的多层 slab，第三矢量包含真空，不能当作体相晶格常数。坐标按 Direct 给出，24 行依次对应 Cl、Hf。尾部零速度来自原始文件，本次没有用它们执行 MD。完整 POSCAR：


```text
HfCl2_3                                 
   1.00000000000000     
     3.3875278554720047    0.0000000000000933    0.0000000000000000
    -1.6937639276858394    2.9336851788810048    0.0000000000000000
     0.0000000000000001    0.0000000000000000  100.2389326567762424
   Cl   Hf
    16     8
Direct
  0.0000000000000000  0.0000000000000000  0.0817212629607980
  0.0000000000000000  0.0000000000000000  0.0474751620923470
  0.0000000000000000  0.0000000000000000  0.2754922467159560
  0.0000000000000000  0.0000000000000000  0.2413517818014199
  0.0000000000000000  0.0000000000000000  0.4692826183104657
  0.0000000000000000  0.0000000000000000  0.4351453761044226
  0.6666666670000012  0.3333333329999988  0.1462954755516392
  0.6666666670000012  0.3333333329999988  0.1121589348619025
  0.6666666670000012  0.3333333329999988  0.3400878891636410
  0.6666666670000012  0.3333333329999988  0.3059469155457393
  0.6666666670000012  0.3333333329999988  0.5339608958693560
  0.6666666670000012  0.3333333329999988  0.4997145044005293
  0.3333333329999988  0.6666666670000012  0.1767506600555748
  0.3333333329999988  0.6666666670000012  0.2108909492501496
  0.3333333329999988  0.6666666670000012  0.3705473355759707
  0.3333333329999988  0.6666666670000012  0.4046884588129842
  0.0000000000000000  0.0000000000000000  0.1938228266249880
  0.0000000000000000  0.0000000000000000  0.3876198307693812
  0.6666666670000012  0.3333333329999988  0.0646320241692067
  0.6666666670000012  0.3333333329999988  0.2584248429255922
  0.6666666670000012  0.3333333329999988  0.4522162930600402
  0.3333333329999988  0.6666666670000012  0.1292292648167006
  0.3333333329999988  0.6666666670000012  0.3230192771685267
  0.3333333329999988  0.6666666670000012  0.5168051483926703
 
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
```

原输入没有 Selective dynamics，全部原子坐标可以调整，固定晶胞由 INCAR 指定。

### 完整 INCAR 与 KPOINTS


```text
SYSTEM = HfCl2_relax
   LPLANE =.TRUE.
   NPAR = 4
   NSIM = 4
   ISTART = 0
   LWAVE = F
   LCHARG = T
   LCORR = T
   LREAL = A
   LASPH = T
   LORBIT = 11
   ISIF = 2
   IBRION = 2
   NSW = 200
   EDIFFG = -0.01
   ENCUT = 400
   GGA = PE
   VOSKOWN = 1
   EDIFF = 1E-6
   NELMIN = 4
   NELM = 160
   AMIX = 0.1
   BMIX = 0.0001
   AMIX_MAG = 0.4
   BMIX_MAG = 0.0001
   MAXMIX = 80
   LMAXMIX = 4
   IVDW = 11
   ALGO = N
   PREC = Accurate
   ISMEAR = 0
   SIGMA = 0.05
```

`ISIF=2` 计算应力并移动原子，晶胞不更新；`IBRION=2` 使用共轭梯度。`NSW=200` 是上限，实际步数从输出数。负的 `EDIFFG=-0.01` 用原子力范数停止，单位 eV/Å；`EDIFF=1E-6` 用于电子迭代，不能替代力判据。

`ENCUT=400`、`GGA=PE` 与 PAW-PBE 数据定义这份模型。`IVDW=11` 为 D3 零阻尼色散，它贡献能量、力和应力，见 [IVDW](https://vasp.at/wiki/IVDW)。`ISMEAR=0`、`SIGMA=0.05` 是高斯展宽。没有开启 ISPIN=2 或 SOC，实际 ISPIN=1。`LREAL=A` 使用自动优化的实空间投影；本次记录没有另做倒空间投影或基组/网格的收敛对照。

KPOINTS 注释来自生成工具，实际执行显式 Γ 中心 18×18×1：


```text
K-Spacing Value to Generate K-Mesh: 0.020
0
Gamma
  18  18   1
0.0  0.0  0.0
```

OUTCAR 中实际不可约网格为 37 点、NBANDS=124、NELECT=208。PAW 元数据：


```json
{
  "ZVAL": [
    7.0,
    12.0
  ],
  "TITEL": [
    "PAW_PBE Cl 06Sep2000",
    "PAW_PBE Hf_sv 10Jan2008 GW suitable"
  ]
}
```

16×7+8×12=208，与电子数相符。TITEL 中“GW suitable”只是数据集标题，本次仍为 PBE 加 D3 的结构优化。

## 实际运行脚本与停止记录

原脚本使用 16 个 MPI 进程，下面仅替换安装路径：


```bash
#!/bin/bash



#SBATCH -o _out.%j.log

#SBATCH -e _err.%j.log



#unlimit memory

ulimit -s unlimited

ulimit -l unlimited



# load path

source /data/intel/oneapi/setvars.sh



cd $SLURM_SUBMIT_DIR



mpirun -np 16  /data/software/vasp.5.4.4/bin/vasp_std > out
```

复算需另建目录，保护已有存档。准备新目录时，用 vi 按自己的安装位置修改脚本，从授权库准备 POTCAR 后，按本机调度方式运行。

```bash
mkdir hfcl2-relax-rerun
cp hfcl2-relax/{INCAR,POSCAR,KPOINTS,script_std} hfcl2-relax-rerun/
cd hfcl2-relax-rerun
# 准备 POTCAR，使用 vi 编辑 script_std 的环境与可执行文件路径
```

存档 `out` 的实际结束段：


```text
 search vector abs. value=  0.249E-04
 bond charge predicted
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1    -0.167593850106E+03    0.41702E-04   -0.65214E-03 10080   0.214E-01    0.388E-02
DAV:   2    -0.167593890276E+03   -0.40170E-04   -0.27970E-04 10760   0.506E-02    0.181E-01
DAV:   3    -0.167593874709E+03    0.15568E-04   -0.47258E-05 10024   0.172E-02    0.564E-02
DAV:   4    -0.167593871834E+03    0.28749E-05   -0.15935E-05 10048   0.921E-03    0.130E-02
DAV:   5    -0.167593871722E+03    0.11150E-06   -0.15214E-06  7576   0.512E-03
  10 F= -.17234076E+03 E0= -.17234076E+03  d E =-.144518E-04
 trial-energy change:   -0.000014  1 .order   -0.000015   -0.000031    0.000002
 step:   1.1819(harm=  1.1819)  dis= 0.00052  next Energy=  -172.340760 (dE=-0.147E-04)
 reached required accuracy - stopping structural energy minimisation
```

最后 5 轮 DAV 后，dE=1.115×10⁻⁷ eV、d eps=−1.5214×10⁻⁷ eV，达到电子阈值。`reached required accuracy` 是离子停止信息，OUTCAR 还有 timing 段；下面直接读取力与能量检查它们。

## 从每个离子步的力块生成数值表

从前面的复算准备目录返回下载包中的存档目录，再运行后处理：

```bash
cd ../hfcl2-relax
python3 analyze_relax.py
```

若只读取存档，直接在解包后的 `hfcl2-relax` 目录运行。程序使用 Python 标准库，得到以下输出：


```text
ionic_steps=10; final_F=-172.34075938 eV; final_fmax=0.006312 eV/A
cell_unchanged=True; volume_relative_change=0; structural_accuracy_reached=True
final_DAV=5; dE=1.115e-07 eV; d_eps=-1.5214e-07 eV
```

每个力向量来自 `POSITION ... TOTAL-FORCE`，取向量范数的最大值。能量来自每步 `FREE ENERGIE OF THE ION-ELECTRON SYSTEM`，与 OSZICAR 的离子 F 对应；不能把电子步的 TOTEN 混入，否则会把 10 步误读成 77 个能量点。

| 离子步 | F / eV（整个 24 原子胞） | 最大力 / eV·Å⁻¹ |
| --- | --- | --- |
| 1 | -172.32314602 | 0.146942 |
| 2 | -172.33505579 | 0.084492 |
| 3 | -172.34070553 | 0.018939 |
| 4 | -172.34074447 | 0.012281 |
| 5 | -172.34074490 | 0.012470 |
| 6 | -172.34074475 | 0.012931 |
| 7 | -172.34074493 | 0.012444 |
| 8 | -172.34074488 | 0.012789 |
| 9 | -172.34074493 | 0.012570 |
| 10 | -172.34075938 | 0.006312 |

末力 0.006312 eV/Å 小于阈值，初末晶格矢量逐项一致。相对第一份已自洽离子步，F 降低 0.01761336 eV；中间最大力不是单调下降，判读应回到真实末态与停止条件。

末态 xx、yy 应力为 −18.01091 kbar，zz 为 −1.70918 kbar，采用 VASP 压缩为正的约定。小原子力没有把固定晶胞变成零压平衡结构。继续声子或其他研究性质时，按对应目标检查几何与数值协议。

[CONTCAR](/Atlas/examples/vasp/hfcl2-relax/CONTCAR)、[逐步 CSV](/Atlas/examples/vasp/hfcl2-relax/results/ionic-history.csv)、[摘要](/Atlas/examples/vasp/hfcl2-relax/results/summary.json)随包保留。下一步另建[固定结构 SCF](/Atlas/m/scf/vasp/) 时，用这份 CONTCAR 准备本材料的 POSCAR；需要调整晶格时，接[晶胞优化](/Atlas/m/vc-relax/)。对应页面介绍操作方法，计算仍须沿用本材料的结构和电子设置。

如果让 AI 帮忙整理这一步，可以把要读取的文件、提取规则和输出单位一起交代：

> 读取当前目录的 POSCAR、CONTCAR、OUTCAR 和 OSZICAR。按每个离子步的 POSITION / TOTAL-FORCE 块计算最大原子力范数；只从 FREE ENERGIE OF THE ION-ELECTRON SYSTEM 后的 TOTEN 提取离子步自由能，不能混入电子迭代。核对力块与能量块数量、初末晶胞、最后 DAV 的两个能量变化以及停止和 timing 信息。用 Python 标准库输出逐步 CSV、JSON 摘要和短终端结果，数据不齐时给出具体错误。

<details><summary>完整后处理源码 analyze_relax.py</summary>


```python
"""Read existing VASP relaxation records; no calculation is submitted."""
from pathlib import Path
import csv, json, math, re

def structure(path):
    ls = path.read_text().splitlines()
    scale = float(ls[1])
    cell = [[float(x) * scale for x in ls[i].split()[:3]] for i in range(2, 5)]
    if scale <= 0:
        raise ValueError('This parser expects a positive POSCAR scale.')
    names = ls[5].split()
    counts = list(map(int, ls[6].split()))
    i = 7
    if ls[i].strip().lower().startswith('s'):
        i += 1
    mode = ls[i].strip().lower()
    coords = [list(map(float, ls[i + 1 + j].split()[:3])) for j in range(sum(counts))]
    if not mode.startswith('d'):
        raise ValueError('This example uses Direct coordinates.')
    a, b, c = cell
    volume = abs(a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return dict(elements=names, counts=counts, cell_A=cell, volume_A3=volume, coordinates_fractional=coords)

def main():
    root = Path(__file__).resolve().parent
    t = (root / 'OUTCAR').read_text()
    ls = t.splitlines()
    forces = []
    for i, l in enumerate(ls):
        if 'POSITION' in l and 'TOTAL-FORCE' in l:
            rows = []
            for s in ls[i + 2:]:
                try:
                    vals = list(map(float, s.split()))
                except ValueError:
                    break
                if len(vals) != 6:
                    break
                rows.append(vals)
            if rows:
                forces.append(rows)
    energies = [float(x) for x in re.findall('FREE ENERGIE OF THE ION-ELECTRON SYSTEM[\\s\\S]*?free\\s+energy\\s+TOTEN\\s*=\\s*([-0-9.]+)', t)]
    if len(forces) != len(energies):
        raise ValueError('Force and free-energy block counts differ.')
    initial = structure(root / 'POSCAR')
    final = structure(root / 'CONTCAR')
    steps = [dict(step=i + 1, free_energy_eV=e, max_force_eV_A=max((math.sqrt(sum((v * v for v in row[3:]))) for row in f))) for i, (e, f) in enumerate(zip(energies, forces))]
    osz = (root / 'OSZICAR').read_text()
    dav = re.findall('^DAV:\\s*(\\d+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)', osz, re.M)
    out = root / 'results'
    out.mkdir(exist_ok=True)
    with (out / 'ionic-history.csv').open('w', newline='') as g:
        w = csv.DictWriter(g, fieldnames=list(steps[0]))
        w.writeheader()
        w.writerows(steps)
    stresses = re.findall('in kB\\s+([-0-9.\\s]+)\\n', t)
    summary = dict(version=ls[0].strip(), ionic_steps=len(steps), structural_accuracy_reached='reached required accuracy' in t, timing_footer='General timing and accounting' in t, first_free_energy_eV=energies[0], final_free_energy_eV=energies[-1], energy_change_eV=energies[-1] - energies[0], final_max_force_eV_A=steps[-1]['max_force_eV_A'], initial_structure=initial, final_structure=final, cell_unchanged=initial['cell_A'] == final['cell_A'], volume_relative_change=final['volume_A3'] / initial['volume_A3'] - 1, final_electronic_iteration=int(dav[-1][0]), final_electronic_dE_eV=float(dav[-1][2]), final_electronic_d_eps_eV=float(dav[-1][3]), last_stress_compressive_positive_kbar=list(map(float, stresses[-1].split())) if stresses else None)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('ionic_steps={}; final_F={:.8f} eV; final_fmax={:.6f} eV/A'.format(len(steps), energies[-1], steps[-1]['max_force_eV_A']))
    print('cell_unchanged={}; volume_relative_change={:.9g}; structural_accuracy_reached={}'.format(summary['cell_unchanged'], summary['volume_relative_change'], summary['structural_accuracy_reached']))
    print('final_DAV={}; dE={:.8g} eV; d_eps={:.8g} eV'.format(summary['final_electronic_iteration'], summary['final_electronic_dE_eV'], summary['final_electronic_d_eps_eV']))
if __name__ == '__main__':
    main()
```

</details>
