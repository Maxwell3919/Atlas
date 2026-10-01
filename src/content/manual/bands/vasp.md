单层 SnSe₂ 的最高价带和最低导带出现在同一个 k 点吗？这次读取同一父 SCF 密度上的 Γ–M–K–Γ 能级，先辨认色散与路径内的带边位置，再判断还需要在哪些区域补充带边搜索。

[下载实际结构、运行记录、原始数据、提取表和全部源码](/Atlas/examples/vasp/snse2-electronic-files.tar.gz)后，解包得到 `snse2-electronic`。下面的目录都从这个根目录出发，绘图需要 Python、NumPy、Matplotlib。这里读取的是已经结束的 VASP 5.4.4 结果；包中没有 POTCAR、CHGCAR 或波函数。OUTCAR 的 PAW 启动数据头已删除，运行参数、电子迭代和数值输出保留；赝势仅提供 TITEL/ZVAL 标识。

| 模型与数据 | 本次实际设置 |
|---|---|
| 晶胞 | Sn 1、Se 2；面内晶格常数约 3.850053 Å；第三基矢约 18.322532 Å |
| 电子设置 | PBE，`ENCUT=400 eV`，非自旋极化，无 SOC |
| 父 SCF | Γ 中心 18×18×1；37 个不可约 k 点；`NELECT=26` |
| 展宽与投影 | `ISMEAR=0`、`SIGMA=0.05 eV`、`LORBIT=11` |
| 结构固定 | `IBRION=-1`、`NSW=0`；输出中还记录 `IVDW=11` |
| 路径 | Γ–M–K–Γ，三段各 50 点，共 150 点、20 条带 |

<details>
<summary>历史输入与父密度的核对</summary>

在原位归档核对时，`bands/CHGCAR` 是直接指向 `../scf/CHGCAR` 的软链接；解析目标与父 SCF 文件相同，哈希也相同。两分支的结构、赝势哈希一致，结构又与各自 XML 中的运行晶胞及原子位置相符。归档中的 SCF INCAR 后来改成了 520 eV，因此下载包提供 `incar-run.xml` 和从实际 XML/OUTCAR 导出的 `parameters-from-output.txt`，并明确标为运行参数重建，未把后来的文件冒充原输入。旧 `SYSTEM=SnS2` 是标签残留，实际 POSCAR 的元素及 PAW 标识均为 Sn、Se。

</details>

各图统一减去父 SCF 的费米能 `−2.39071823 eV`，取自 `scf/vasprun.xml`，也与 `scf/DOSCAR` 的表头一致。路径输出自己的费米能为 `−2.38897901 eV`；在半导体中它不是可跨材料直接比较的绝对能量标尺。

## 从输出回读运行参数

`parameters-from-output.txt` 列出 XML 与 OUTCAR 中实际读入的参数；完整的原始 XML 随包保留。`IVDW=11` 在这份 VASP 5.4.4 的 OUTCAR 中记录为 DFT-D3 zero damping，XML 的 `<incar>` 部分没有回显这一项，提取程序因此从 OUTCAR 补取。[VASP DFT-D3](https://vasp.at/wiki/DFT-D3)

先把参数来源交代清楚，再请 AI 帮忙写提取程序：

> 回读 scf 与 bands 的原始 vasprun.xml，只提取原程序的 `<incar>` 字段，并从 OUTCAR 核对 XML 没有回显的 IVDW。把实际运行参数列为 parameters-from-output.txt，保留对应 XML 片段。不要把改过的归档 INCAR 当作历史输入，不添加输出中没有记录的参数。保留原结构，输出每个分支实际 ENCUT 和写出的文件名。

在包根目录运行：

```text
python3 extract_inputs.py
cat scf/parameters-from-output.txt
cat bands/parameters-from-output.txt
cat bands/POSCAR
```
<details>
<summary>完整源码：extract_inputs.py</summary>

```python
#!/usr/bin/env python3
"""Export the actual run's INCAR XML; do not use subsequently edited INCAR."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re

for directory in ("scf", "bands"):
    folder = Path(directory)
    tree = ET.parse(folder / "vasprun.xml")
    incar = tree.getroot().find("incar")
    ET.ElementTree(incar).write(
        folder / "incar-run.xml", encoding="utf-8", xml_declaration=True
    )
    values = {}
    for node in incar:
        key = node.attrib["name"]
        value = " ".join((node.text or "").split())
        if key == "LREAL":
            value = value.split()[0]  # XML includes an echoed trailing comment
        values[key] = value
    # VASP 5.4.4 does not echo IVDW in <incar>; record resolved tags from OUTCAR/XML.
    outcar = (folder / "OUTCAR").read_text()
    match = re.search(r"(?m)^\s*IVDW\s*=\s*(\d+)", outcar)
    assert match, "Missing runtime IVDW record."
    values["IVDW"] = match[1]
    for key in ("NSW", "ISPIN", "LSORBIT", "LNONCOLLINEAR", "NBANDS", "NELECT", "NPAR"):
        values[key] = tree.getroot().find(f".//parameters//*[@name='{key}']").text.strip()
    text = (
        "# Reconstructed from this run's vasprun.xml and resolved OUTCAR tags; not the archived INCAR.\n"
        + "\n".join(f"{key} = {value}" for key, value in values.items()) + "\n"
    )
    (folder / "parameters-from-output.txt").write_text(text)
    print(f"{directory}: ENCUT={values['ENCUT']} eV; exported parameters-from-output.txt and incar-run.xml")
```

</details>
实际导出日志：

```text
scf: ENCUT=400.00000000 eV; exported parameters-from-output.txt and incar-run.xml
bands: ENCUT=400.00000000 eV; exported parameters-from-output.txt and incar-run.xml
```
<details>
<summary>父 SCF 的运行参数摘录与结构</summary>

```text
# Reconstructed from this run's vasprun.xml and resolved OUTCAR tags; not the archived INCAR.
SYSTEM = SnS2
ISTART = 0
PREC = accurate
ALGO = N
NSIM = 4
MAXMIX = 80
AMIX = 0.10000000
BMIX = 0.00010000
AMIX_MAG = 0.40000000
BMIX_MAG = 0.00010000
NELM = 160
NELMIN = 4
IBRION = -1
EDIFF = 0.00000100
ISIF = 2
ENCUT = 400.00000000
LREAL = A
LPLANE = T
ISMEAR = 0
SIGMA = 0.05000000
LCORR = T
LMAXMIX = 4
LWAVE = F
LCHARG = T
LORBIT = 11
LASPH = T
KPOINT_BSE = -1 0 0 0
GGA = PE
VOSKOWN = 1
IVDW = 11
NSW = 0
ISPIN = 1
LSORBIT = F
LNONCOLLINEAR = F
NBANDS = 20
NELECT = 26.00000000
NPAR = 4
```

```text
"Sn1 Se2"                               
   1.00000000000000     
     3.8500526717160253    0.0000000000010754    0.0000000000000000
    -1.9250263359068902    3.3342434196222679    0.0000000000000000
     0.0000000000000004    0.0000000000000001   18.3225321772563952
   Sn   Se
     1     2
Direct
 -0.0000000000000000 -0.0000000000000000  0.5000000000000000
  0.6666666670000012  0.3333333329999988  0.5874030481495341
  0.3333333329999988  0.6666666670000012  0.4125969518504660
 
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
  0.00000000E+00  0.00000000E+00  0.00000000E+00
```

</details>
<details>
<summary>路径计算的运行参数摘录</summary>

```text
# Reconstructed from this run's vasprun.xml and resolved OUTCAR tags; not the archived INCAR.
SYSTEM = SnS2
PREC = accurate
ALGO = N
NSIM = 4
MAXMIX = 80
AMIX = 0.10000000
BMIX = 0.00010000
AMIX_MAG = 0.40000000
BMIX_MAG = 0.00010000
ICHARG = 11
NELM = 160
NELMIN = 4
IBRION = -1
EDIFF = 0.00000100
ISIF = 2
ENCUT = 400.00000000
LREAL = A
LPLANE = T
ISMEAR = 0
SIGMA = 0.05000000
LCORR = T
LMAXMIX = 4
LWAVE = F
LCHARG = F
LORBIT = 11
LASPH = T
KPOINT_BSE = -1 0 0 0
GGA = PE
VOSKOWN = 1
IVDW = 11
NSW = 0
ISPIN = 1
LSORBIT = F
LNONCOLLINEAR = F
NBANDS = 20
NELECT = 26.00000000
NPAR = 4
```

</details>
`ICHARG=11` 让路径计算读入已有密度并固定它，`LCHARG=F` 避免在路径分支重写密度；父 SCF 使用的是覆盖整个 BZ 的均匀网格。`Sn_d` 把 Sn 的 d 电子纳入价层，`LMAXMIX=4` 随本次父文件保留。[VASP ICHARG](https://vasp.at/wiki/ICHARG)

赝势标识只有以下内容：

```text
TITEL = PAW_PBE Sn_d 06Sep2000
ZVAL = 14.000
TITEL = PAW_PBE Se 06Sep2000
ZVAL = 6.000
```
若重新求电子态，须先在自己的同一 SnSe₂ 晶胞、PAW 和运行参数下完成父 SCF，然后把它的 CHGCAR 复制到路径分支。包内的原始数据可直接重画，这些运行参数来自存档的输出，参数收敛仍需按研究目标检查。

## 三段路径怎样展开成 150 点

```bash
cat bands/KPOINTS
head -n 9 bands/EIGENVAL
```
```text
K-Path Generated by VASPKIT.
   50
Line-Mode
Reciprocal
   0.0000000000   0.0000000000   0.0000000000     GAMMA          
   0.5000000000   0.0000000000   0.0000000000     M              
 
   0.5000000000   0.0000000000   0.0000000000     M              
   0.3333333333   0.3333333333   0.0000000000     K              
 
   0.3333333333   0.3333333333   0.0000000000     K              
   0.0000000000   0.0000000000   0.0000000000     GAMMA
```
```text
    3    3    1    1
  0.7840219E+02  0.3850053E-09  0.3850053E-09  0.1832253E-08  0.5000000E-15
  1.000000000000000E-004
  CAR 
 SnS2                                    
     26    150     20
 
  0.0000000E+00  0.0000000E+00  0.0000000E+00  0.6666667E-02
    1      -23.836583   1.000000
```

`Line-Mode` 的 50 是每一段的采样点数，三个线段共 150 点，相邻段的 M、K 端点各写两次。`EIGENVAL` 第六行的 `26 150 20` 是电子数、k 点数、能带数；随后每个 k 点有坐标与权重，再跟 20 行带号、能量、占据。这里的非磁性占据列按单自旋写为 0 或 1，计算电子总数时要包含二重自旋简并。

横轴按实际倒格矢构造：实空间晶格矩阵的行是三个基矢，`B=2π(A⁻¹)ᵀ`，每个分数 k 点转换为笛卡尔波矢后累加距离。M、K 的重复端点不额外增加距离；总路径长度为 `2.57419424 Å⁻¹`。按行号均匀铺开横轴，会把不同物理长度的段画成一样长。

## 数据配对与提取要求

提取时先保留每个 k 点、每条带的编号，不提前排序；计算路径距离，写出绝对能量和相对父 SCF 费米能的能量。20 条带完整写入表格，图仅显示带边附近能窗。DOS 使用同一父 SCF 的均匀网格输出，与线上的采样分开。

可以把下面的要求交给 coding Agent：

```text
读取本目录 bands/POSCAR、KPOINTS、EIGENVAL，以及 scf/vasprun.xml。
确认 Sn1Se2、ISPIN=1、无 SOC、400 eV 和 150×20 个路径本征值。
以 B=2π inv(A).T 把 k 分数坐标转为 Å^-1，累加路径距离，检查 Γ/M/K/Γ 节点和重复端点。
从父 SCF XML 的最终 efermi 取统一零点，不用路径权重生成 DOS，不手调带边。
先输出完整 CSV 和摘要，再用细黑线绘能带；保留绝对能量、带号和 k 点号。导出 PNG/SVG/PDF。
读取同一父 SCF 的 DOSCAR 时单独校验列结构，不插值抹平锯齿，不生成额外参数扫描。
```

## 从文件到表格，再到图

先保存数据表，再画图。`analyse.py` 固定使用 `scf` 和 `bands` 两个数据分支，检查模型、状态数、路径节点、PROCAR 配对和 DOS 列数；输出独立 CSV，`plot.py` 只读取 CSV 与 `summary.json`。下面的源码已用本次下载包的数据实际运行。

<details>
<summary>完整源码：analyse.py</summary>

```python
#!/usr/bin/env python3
"""Read the fixed SnSe2 data set; export paired eigenvalues/projections/DOS."""
from pathlib import Path
import csv
import json
import re
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "tables"
OUT.mkdir(exist_ok=True)

def eigenval(path):
    lines = path.read_text().splitlines()
    assert int(lines[0].split()[-1]) == 1, "This example requires ISPIN=1."
    nelect, nk, nb = map(int, lines[5].split())
    k, weights, energies, occupations = [], [], [], []
    cursor = 6
    for ik in range(nk):
        while not lines[cursor].strip():
            cursor += 1
        head = list(map(float, lines[cursor].split()))
        assert len(head) == 4
        k.append(head[:3])
        weights.append(head[3])
        cursor += 1
        block = [lines[cursor + j].split() for j in range(nb)]
        assert [int(row[0]) for row in block] == list(range(1, nb + 1))
        energies.append([float(row[1]) for row in block])
        occupations.append([float(row[2]) for row in block])
        cursor += nb
    return nelect, np.array(k), np.array(weights), np.array(energies), np.array(occupations)

def table(name, header, rows):
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)

scf_xml = ET.parse(ROOT / "scf/vasprun.xml").getroot()
band_xml = ET.parse(ROOT / "bands/vasprun.xml").getroot()
ef = float(scf_xml.findall('.//i[@name="efermi"]')[-1].text)
ef_path = float(band_xml.findall('.//i[@name="efermi"]')[-1].text)
for model in (scf_xml, band_xml):
    assert float(model.find('./incar/i[@name="ENCUT"]').text) == 400.0
    assert model.find('.//i[@name="ISPIN"]').text.strip() == "1"
    assert model.find('.//i[@name="LSORBIT"]').text.strip() == "F"
    assert model.find('.//i[@name="NSW"]').text.strip() == "0"

poscar = (ROOT / "bands/POSCAR").read_text().splitlines()
scale = float(poscar[1])
assert scale > 0
lattice = scale * np.array([list(map(float, row.split())) for row in poscar[2:5]])
assert poscar[5].split() == ["Sn", "Se"]
assert list(map(int, poscar[6].split())) == [1, 2]
reciprocal = 2 * np.pi * np.linalg.inv(lattice).T

nelect, k, kw, energy, occupation = eigenval(ROOT / "bands/EIGENVAL")
nk, nb = energy.shape
assert (nelect, nk, nb) == (26, 150, 20)
assert np.all(np.isfinite(energy))
cartesian = k @ reciprocal
distance = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(cartesian, axis=0), axis=1))]
nodes = [(0, "Gamma"), (49, "M"), (99, "K"), (149, "Gamma")]
expected = np.array([[0,0,0], [0.5,0,0], [1/3,1/3,0], [0,0,0]])
assert np.allclose(k[[i for i, _ in nodes]], expected, atol=6e-8)
assert np.allclose(k[49], k[50]) and np.allclose(k[99], k[100])
table("path.csv", ["k_index", "kx_frac", "ky_frac", "kz_frac", "distance_Ainv"],
      [(i+1, *k[i], distance[i]) for i in range(nk)])
table("bands.csv", ["k_index", "band", "distance_Ainv", "energy_eV",
                   "energy_minus_scf_EF_eV", "occupation_per_spin"],
      [(i+1, j+1, distance[i], energy[i,j], energy[i,j]-ef, occupation[i,j])
       for i in range(nk) for j in range(nb)])

# Each PROCAR record has one energy and three atom rows plus the tot row.
raw = (ROOT / "bands/PROCAR").read_text().splitlines()
header = re.search(r"# of k-points:\s*(\d+)\s*# of bands:\s*(\d+)\s*# of ions:\s*(\d+)",
                   "\n".join(raw[:4]))
assert tuple(map(int, header.groups())) == (nk, nb, 3)
channels = np.full((nk, nb, 7), np.nan)
procar_energy = np.full_like(energy, np.nan)
procar_k = np.full_like(k, np.nan)
ik = ib = None
atom_rows = []
seen = set()
for line in raw:
    match_k = re.match(r"\s*k-point\s+(\d+)\s*:\s*(\S+)\s+(\S+)\s+(\S+)", line)
    if match_k:
        ik = int(match_k[1])-1
        procar_k[ik] = list(map(float, match_k.groups()[1:]))
        continue
    match_band = re.match(r"\s*band\s+(\d+)\s*# energy\s+(\S+)", line)
    if match_band:
        ib = int(match_band[1])-1
        assert (ik, ib) not in seen
        procar_energy[ik,ib] = float(match_band[2])
        atom_rows = []
        continue
    fields = line.split()
    if ik is None or ib is None or not fields:
        continue
    if fields[0] == "ion":
        assert fields[1:] == ["s","py","pz","px","dxy","dyz","dz2","dxz","x2-y2","tot"]
    elif fields[0] in ("1", "2", "3") and len(fields) == 11:
        assert int(fields[0]) == len(atom_rows)+1
        atom_rows.append(list(map(float, fields[1:])))
    elif fields[0] == "tot" and len(fields) == 11:
        assert len(atom_rows) == 3, "Reject missing/multiple noncollinear blocks."
        atoms = np.array(atom_rows)
        tin = atoms[0]
        selenium = atoms[1:].sum(axis=0)
        channels[ik,ib] = [tin[0],tin[1:4].sum(),tin[4:9].sum(),
                           selenium[0],selenium[1:4].sum(),selenium[4:9].sum(),
                           float(fields[-1])]
        seen.add((ik,ib))
assert len(seen) == nk*nb and np.isfinite(channels).all()
energy_difference = float(np.max(np.abs(procar_energy-energy)))
assert energy_difference < 6e-7
assert np.allclose(procar_k, k, atol=6e-8)
table("fatband.csv", ["k_index","band","distance_Ainv","energy_minus_scf_EF_eV",
                      "Sn_s","Sn_p","Sn_d","Se_s","Se_p","Se_d","projected_total"],
      [(i+1,j+1,distance[i],energy[i,j]-ef,*channels[i,j])
       for i in range(nk) for j in range(nb)])

# DOS comes from the uniform static SCF, never from the line-mode run.
dos_lines = (ROOT / "scf/DOSCAR").read_text().splitlines()
assert list(map(int, dos_lines[0].split()))[:3] == [3,3,1]
dos_header = list(map(float, dos_lines[5].split()))
nedos = int(dos_header[2])
assert nedos == 301 and abs(dos_header[3]-ef) < 1e-8
total = np.array([list(map(float,row.split())) for row in dos_lines[6:6+nedos]])
assert total.shape == (nedos,3)
cursor = 6+nedos
atom_dos = []
for ion in range(3):
    assert int(float(dos_lines[cursor].split()[2])) == nedos
    block = np.array([list(map(float,row.split()))
                      for row in dos_lines[cursor+1:cursor+1+nedos]])
    assert block.shape == (nedos,10)
    assert np.allclose(block[:,0],total[:,0],atol=1e-8)
    atom_dos.append(block[:,1:])
    cursor += nedos+1
assert not any(row.strip() for row in dos_lines[cursor:])
pdos = np.array(atom_dos)
tin = pdos[0]
selenium = pdos[1:].sum(axis=0)
dos_channels = np.column_stack([tin[:,0],tin[:,1:4].sum(axis=1),tin[:,4:9].sum(axis=1),
                               selenium[:,0],selenium[:,1:4].sum(axis=1),
                               selenium[:,4:9].sum(axis=1)])
table("dos.csv", ["energy_eV","energy_minus_scf_EF_eV","total_DOS_states_per_eV_cell",
                  "integrated_DOS_states_per_cell","Sn_s","Sn_p","Sn_d","Se_s","Se_p","Se_d"],
      [(total[i,0],total[i,0]-ef,*total[i,1:],*dos_channels[i]) for i in range(nedos)])
n_scf, sk, sw, se, so = eigenval(ROOT / "scf/EIGENVAL")
assert n_scf == 26 and se.shape == (37,20) and abs(sw.sum()-1)<1e-7
assert so.min() >= 0 and so.max() <= 1
occupied_count = float(2*np.sum(sw[:,None]*so))  # ISPIN=1 EIGENVAL stores 0..1 occupations
assert abs(occupied_count-26)<1e-5  # printed k weights have finite precision
idos_ef = float(np.interp(ef,total[:,0],total[:,2]))
vbm_index = tuple(map(int,np.unravel_index(np.argmax(energy[:,:13]), (nk,13))))
cbm_index_raw = tuple(map(int,np.unravel_index(np.argmin(energy[:,13:]), (nk,nb-13))))
cbm_index = (cbm_index_raw[0],cbm_index_raw[1]+13)
edge_rows = []
for name, (i,j) in [("VBM_path",vbm_index),("CBM_path",cbm_index)]:
    edge_rows.append((name,i+1,j+1,*k[i],energy[i,j],energy[i,j]-ef,*channels[i,j]))
table("path-edges.csv", ["edge","k_index","band","kx_frac","ky_frac","kz_frac","energy_eV",
                        "energy_minus_scf_EF_eV","Sn_s","Sn_p","Sn_d","Se_s","Se_p","Se_d","projected_total"],
      edge_rows)
summary = {
    "version": "VASP 5.4.4", "encut_eV":400, "functional":"PBE",
    "soc":False,"spin_polarized":False, "elements":["Sn","Se"],"counts":[1,2],
    "nelect":nelect,"path_kpoints":nk,"bands":nb,"procar_states":len(seen),
    "scf_mesh":[18,18,1],"scf_irreducible_kpoints":len(sk),
    "energy_zero_source":"scf/vasprun.xml final efermi and scf/DOSCAR header",
    "energy_zero_eV":ef,"path_reported_efermi_eV":ef_path,
    "path_ticks":[{"index":i+1,"label":label,"distance_Ainv":float(distance[i])} for i,label in nodes],
    "path_length_Ainv":float(distance[-1]),"procar_eigenval_max_difference_eV":energy_difference,
    "dos_points":nedos,"dos_energy_bounds_eV":[float(total[0,0]),float(total[-1,0])],
    "dos_grid_step_eV":float(np.median(np.diff(total[:,0]))),
    "dos_sigma_eV":0.05,"weighted_occupied_states":occupied_count,
    "IDOS_at_scf_EF":idos_ef,"IDOS_bottom":float(total[0,2]),"IDOS_top":float(total[-1,2]),
    "trapezoid_total_DOS_full_window":float(np.trapezoid(total[:,1],total[:,0])),
    "vbm_path":{"k_index":vbm_index[0]+1,"band":vbm_index[1]+1,"energy_eV":float(energy[vbm_index])},
    "cbm_path":{"k_index":cbm_index[0]+1,"band":cbm_index[1]+1,"energy_eV":float(energy[cbm_index])},
    "path_sampled_gap_eV":float(energy[cbm_index]-energy[vbm_index]),
    "scope":"Single fixed PBE/no-SOC model; path extrema and finite SCF DOS sampling, no convergence scan or interface model."
}
(ROOT / "summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(f"SCF: 18x18x1 -> {len(sk)} irreducible points; weighted occupied states = {occupied_count:.8f}")
print(f"Path: {nk} points x {nb} bands; length = {distance[-1]:.8f} A^-1")
print(f"PROCAR: {len(seen)} paired states; max energy difference = {energy_difference:.3e} eV")
print(f"Energy zero: SCF efermi = {ef:.8f} eV; path efermi = {ef_path:.8f} eV")
print(f"DOS: {nedos} energy points; step = {summary['dos_grid_step_eV']:.6f} eV; SIGMA = 0.05 eV")
print(f"IDOS: at SCF EF = {idos_ef:.8f}; lower/upper ends = {total[0,2]:.8f}/{total[-1,2]:.8f}")
print(f"Path extrema: VBM k={vbm_index[0]+1}, band={vbm_index[1]+1}; CBM k={cbm_index[0]+1}, band={cbm_index[1]+1}")
print(f"Path sampled gap = {summary['path_sampled_gap_eV']:.8f} eV")
print("Wrote path.csv, bands.csv, fatband.csv, dos.csv, path-edges.csv and summary.json")
```

</details>

<details>
<summary>完整源码：plot.py</summary>

```python
#!/usr/bin/env python3
"""Plot only the paired tables; use the common parent-SCF energy reference."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
summary = json.loads((ROOT / "summary.json").read_text())
bands = np.genfromtxt(ROOT / "tables/bands.csv", delimiter=",", names=True)
dos = np.genfromtxt(ROOT / "tables/dos.csv", delimiter=",", names=True)
fat = np.genfromtxt(ROOT / "tables/fatband.csv", delimiter=",", names=True)
nk, nb = summary["path_kpoints"], summary["bands"]
x = bands["distance_Ainv"].reshape(nk,nb)[:,0]
energy = bands["energy_minus_scf_EF_eV"].reshape(nk,nb)
ticks = [item["distance_Ainv"] for item in summary["path_ticks"]]
labels = [r"$\Gamma$", "M", "K", r"$\Gamma$"]
plt.rcParams.update({"font.family":"DejaVu Serif","font.size":10,
                     "axes.linewidth":0.8,"xtick.direction":"in","ytick.direction":"in",
                     "xtick.top":True,"ytick.right":True,"svg.fonttype":"none",
                     "pdf.fonttype":42,"savefig.bbox":"tight"})
def path_axis(ax):
    ax.set_xlim(x[0],x[-1])
    ax.set_ylim(-7,4)
    ax.set_xticks(ticks,labels)
    ax.axhline(0,color="0.45",lw=0.7,ls="--")
    for tick in ticks[1:-1]:
        ax.axvline(tick,color="0.8",lw=0.6)
def export(fig,stem):
    for suffix in ("png","svg","pdf"):
        fig.savefig(FIG / f"{stem}.{suffix}",dpi=240)
    plt.close(fig)
    print(f"Exported figures/{stem}.png, .svg and .pdf")
fig,(ax,dx) = plt.subplots(1,2,figsize=(6.5,4.1),sharey=True,
                           gridspec_kw={"width_ratios":[2.1,1],"wspace":0.08})
ax.plot(x,energy,color="0.16",lw=0.65)
path_axis(ax)
ax.set_ylabel(r"$E-E_F^{\mathrm{SCF}}$ (eV)")
ax.set_title("(a) SnSe$_2$ bands",loc="left",fontsize=10)
dy = dos["energy_minus_scf_EF_eV"]
dx.plot(dos["total_DOS_states_per_eV_cell"],dy,color="0.12",lw=1,label="Total")
dx.plot(dos["Sn_s"],dy,color="#2B6CB0",lw=0.9,label="Sn s")
dx.plot(dos["Se_p"],dy,color="#B45309",lw=0.9,label="Se p")
visible = (dy >= -7) & (dy <= 4)
dx.set_xlim(0,1.08*np.max(dos["total_DOS_states_per_eV_cell"][visible]))
dx.axhline(0,color="0.45",lw=0.7,ls="--")
dx.set_xlabel("DOS (states/eV/cell)")
dx.set_title("(b) 18x18x1 SCF DOS",loc="left",fontsize=10)
dx.legend(frameon=False,fontsize=8,loc="lower right")
export(fig,"bands-dos")
fig,axes = plt.subplots(1,2,figsize=(6.5,4.1),sharey=True,
                        gridspec_kw={"wspace":0.08})
for ax,channel,color,title in zip(axes,["Sn_s","Se_p"],["#2B6CB0","#B45309"],
                                 ["(a) Sn s projection","(b) Se p projection"]):
    ax.plot(x,energy,color="0.7",lw=0.45,zorder=1)
    weights = fat[channel].reshape(nk,nb)
    ax.scatter(np.repeat(x,nb),energy.ravel(),s=20*weights.ravel(),
               c=color,linewidths=0,alpha=0.75,zorder=2)
    path_axis(ax)
    ax.set_title(title,loc="left",fontsize=10)
axes[0].set_ylabel(r"$E-E_F^{\mathrm{SCF}}$ (eV)")
export(fig,"fatband")
```

</details>

在包根目录执行：

```bash
python3 analyse.py
python3 plot.py
```

实际输出：

```text
SCF: 18x18x1 -> 37 irreducible points; weighted occupied states = 26.00000205
Path: 150 points x 20 bands; length = 2.57419424 A^-1
PROCAR: 3000 paired states; max energy difference = 5.000e-07 eV
Energy zero: SCF efermi = -2.39071823 eV; path efermi = -2.38897901 eV
DOS: 301 energy points; step = 0.110000 eV; SIGMA = 0.05 eV
IDOS: at SCF EF = 26.00000000; lower/upper ends = 0.00000000/40.00000000
Path extrema: VBM k=13, band=13; CBM k=50, band=14
Path sampled gap = 0.76419500 eV
Wrote path.csv, bands.csv, fatband.csv, dos.csv, path-edges.csv and summary.json
Exported figures/bands-dos.png, .svg and .pdf
Exported figures/fatband.png, .svg and .pdf
```

## 路径结果读到哪里

| 路径内极值 | k 点号 / 带号 | k 分数坐标 | 绝对能量（eV） | 相对父 SCF E_F（eV） |
|---|---|---|---|---|
| 价带最高点 | 13 / 13 | (0.122449, 0, 0) | −2.696780 | −0.306062 |
| 导带最低点 | 50 / 14 | (0.5, 0, 0)，M | −1.932585 | 0.458133 |

两点位于不同 k，路径采样的间隙为 `0.764195 eV`。价带最高点处于 Γ–M 内部，直接读 Γ、M、K 三个节点会漏掉它。这个数来自当前路径；进一步确定整个二维 BZ 的带边，应在同一模型上做均匀搜索与局部加密，见[带隙方法目录](/Atlas/m/band-gap/)。

这套孤立 SnSe₂ 是后续 SnSe₂/Sr₂N 分析的层来源参照，尚未与该界面建立相同面内应变、几何及势参考。接触后若出现穿越 E_F 的分支，要逐态核对是否来自这个原本未占据的导带区；晶格改变和层间接触的影响须用匹配孤立层对照区分。

<figure><img src="/Atlas/examples/vasp/snse2-electronic/figures/bands-dos.png" alt="同一 SnSe2 模型的路径能带与18乘18乘1均匀SCF态密度" loading="lazy"/><figcaption>左：150 个路径点的20条能带；右：父 SCF 的总 DOS、Sn-s 与两原子合计的 Se-p。两侧共用父 SCF 费米能零点。DOS 保留实际采样，不额外平滑。</figcaption></figure>

[相关论文 Sec. II、Fig. 1(c) 与 Table I](https://arxiv.org/pdf/2502.13690v1)也先分析孤立 SnSe₂ 的能带与 PDOS，再研究其界面模型。论文的主结果采用 LDA、另一晶格和更密网格，本页采用固定 PBE 晶胞，因此其带隙数值不是这里的复现标准。下一步若问带边由谁贡献，应接[本次胖带](/Atlas/m/fatband/vasp/)逐态比较 Sn-s、Se-p，而不是从曲线形状猜轨道。
