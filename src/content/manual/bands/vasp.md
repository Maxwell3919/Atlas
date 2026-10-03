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

路径分支的 `bands/CHGCAR` 通过 `../scf/CHGCAR` 读取父SCF密度，两分支保持相同晶胞、原子位置和PAW种类。归档中的 SCF INCAR 后来改成了 520 eV，因此下载包提供 `incar-run.xml` 和从实际 XML/OUTCAR 导出的 `parameters-from-output.txt`，并明确标为运行参数重建，未把后来的文件冒充原输入。旧 `SYSTEM=SnS2` 是标签残留，实际 POSCAR 的元素及 PAW 标识均为 Sn、Se。

</details>

各图统一减去父 SCF 的费米能 `−2.39071823 eV`，取自 `scf/vasprun.xml`，也与 `scf/DOSCAR` 的表头一致。路径输出自己的费米能为 `−2.38897901 eV`；在半导体中它不是可跨材料直接比较的绝对能量标尺。

## 从输出回读运行参数

`parameters-from-output.txt` 列出 XML 与 OUTCAR 中实际读入的参数；完整的原始 XML 随包保留。`IVDW=11` 在这份 VASP 5.4.4 的 OUTCAR 中记录为 DFT-D3 zero damping，XML 的 `<incar>` 部分没有回显这一项，提取程序因此从 OUTCAR 补取。[VASP DFT-D3](https://vasp.at/wiki/DFT-D3)

先把参数来源交代清楚，再请 AI 帮忙写提取程序：

> 回读 scf 与 bands 的原始 vasprun.xml，只提取原程序的 `<incar>` 字段，并从 OUTCAR 核对 XML 没有回显的 IVDW。把实际运行参数列为 parameters-from-output.txt，保留对应 XML 片段。不要把改过的归档 INCAR 当作历史输入，不添加输出中没有记录的参数。保留原结构，输出每个分支实际 ENCUT 和写出的文件名。

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

在包根目录运行：

```text
python3 extract_inputs.py
cat scf/parameters-from-output.txt
cat bands/parameters-from-output.txt
cat bands/POSCAR
```
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

先保存数据表，再画图。`analyse.py` 固定使用 `scf` 和 `bands` 两个数据分支，检查模型、状态数、路径节点、PROCAR 配对和 DOS 列数；输出独立 CSV，`plot.py` 只读取能级、投影、DOS和路径节点CSV。下面的改版源码在Talos读取同一批原生数据实际运行，VASP计算没有重跑。路径节点保存在 `tables/path-nodes.csv`，能量零点、电子数、IDOS和采样间隙保存在 `tables/electronic-values.csv`；这两个表与能级/投影/DOS表一起供后处理使用。下载改版完整源码：[analyse.py](/Atlas/examples/vasp/snse2-electronic/analyse.py) · [plot.py](/Atlas/examples/vasp/snse2-electronic/plot.py)。

<details>
<summary>完整源码：analyse.py</summary>

```python
#!/usr/bin/env python3
"""Read the fixed SnSe2 data set; export paired eigenvalues/projections/DOS."""
from pathlib import Path
import csv
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
table("path-nodes.csv",["k_index","label","distance_Ainv"],
      [(i+1,label,float(distance[i])) for i,label in nodes])
dos_step=float(np.median(np.diff(total[:,0])))
path_gap=float(energy[cbm_index]-energy[vbm_index])
values=[("SCF_Fermi",ef,"eV"),("path_Fermi",ef_path,"eV"),
        ("electrons",nelect,"electrons/cell"),("SCF_irreducible_points",len(sk),"points"),
        ("path_points",nk,"points"),("bands",nb,"bands"),
        ("path_length",float(distance[-1]),"A^-1"),
        ("PROCAR_EIGENVAL_max_difference",energy_difference,"eV"),
        ("DOS_points",nedos,"points"),("DOS_step",dos_step,"eV"),
        ("DOS_SIGMA",0.05,"eV"),("weighted_occupied_states",occupied_count,"electrons/cell"),
        ("IDOS_at_SCF_Fermi",idos_ef,"states/cell"),
        ("IDOS_lower_bound",float(total[0,2]),"states/cell"),
        ("IDOS_upper_bound",float(total[-1,2]),"states/cell"),
        ("DOS_integral_full_window",float(np.trapezoid(total[:,1],total[:,0])),"states/cell"),
        ("path_sampled_gap",path_gap,"eV")]
table("electronic-values.csv",["quantity","value","unit"],values)
print(f"SCF: 18x18x1 -> {len(sk)} irreducible points; weighted occupied states = {occupied_count:.8f}")
print(f"Path: {nk} points x {nb} bands; length = {distance[-1]:.8f} A^-1")
print(f"PROCAR: {len(seen)} paired states; max energy difference = {energy_difference:.3e} eV")
print(f"Energy zero: SCF efermi = {ef:.8f} eV; path efermi = {ef_path:.8f} eV")
print(f"DOS: {nedos} energy points; step = {dos_step:.6f} eV; SIGMA = 0.05 eV")
print(f"IDOS: at SCF EF = {idos_ef:.8f}; lower/upper ends = {total[0,2]:.8f}/{total[-1,2]:.8f}")
print(f"Path extrema: VBM k={vbm_index[0]+1}, band={vbm_index[1]+1}; CBM k={cbm_index[0]+1}, band={cbm_index[1]+1}")
print(f"Path sampled gap = {path_gap:.8f} eV")
print("Wrote path.csv, bands.csv, fatband.csv, dos.csv, path-edges.csv, path-nodes.csv and electronic-values.csv")
```

</details>

<details>
<summary>完整源码：plot.py</summary>

```python
#!/usr/bin/env python3
"""Plot only the paired tables; use the common parent-SCF energy reference."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
bands = np.genfromtxt(ROOT / "tables/bands.csv", delimiter=",", names=True)
dos = np.genfromtxt(ROOT / "tables/dos.csv", delimiter=",", names=True)
fat = np.genfromtxt(ROOT / "tables/fatband.csv", delimiter=",", names=True)
nk, nb = int(np.max(bands["k_index"])), int(np.max(bands["band"]))
x = bands["distance_Ainv"].reshape(nk,nb)[:,0]
energy = bands["energy_minus_scf_EF_eV"].reshape(nk,nb)
with (ROOT / "tables/path-nodes.csv").open(newline="") as f:
    ticks = [float(row["distance_Ainv"]) for row in csv.DictReader(f)]
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

本次在Talos运行改版后处理的实际输出：

```text
SCF: 18x18x1 -> 37 irreducible points; weighted occupied states = 26.00000205
Path: 150 points x 20 bands; length = 2.57419424 A^-1
PROCAR: 3000 paired states; max energy difference = 5.000e-07 eV
Energy zero: SCF efermi = -2.39071823 eV; path efermi = -2.38897901 eV
DOS: 301 energy points; step = 0.110000 eV; SIGMA = 0.05 eV
IDOS: at SCF EF = 26.00000000; lower/upper ends = 0.00000000/40.00000000
Path extrema: VBM k=13, band=13; CBM k=50, band=14
Path sampled gap = 0.76419500 eV
Wrote path.csv, bands.csv, fatband.csv, dos.csv, path-edges.csv, path-nodes.csv and electronic-values.csv
Exported figures/bands-dos.png, .svg and .pdf
Exported figures/fatband.png, .svg and .pdf
```

## 路径结果读到哪里

| 路径内极值 | k 点号 / 带号 | k 分数坐标 | 绝对能量（eV） | 相对父 SCF E_F（eV） |
|---|---|---|---|---|
| 价带最高点 | 13 / 13 | (0.122449, 0, 0) | −2.696780 | −0.306062 |
| 导带最低点 | 50 / 14 | (0.5, 0, 0)，M | −1.932585 | 0.458133 |

两点位于不同 k，路径采样的间隙为 `0.764195 eV`。价带最高点处于 Γ–M 内部，直接读 Γ、M、K 三个节点会漏掉它。这个数来自当前路径；进一步确定整个二维 BZ 的带边，应在同一模型上做均匀搜索与局部加密，见[带隙方法目录](/Atlas/m/band-gap/)。

在图上定位这两个态时，先从 `path.csv` 取真实横坐标：第13点在0.23074793 Å⁻¹，M点在0.94222055 Å⁻¹。VBM不是横轴第13/150处的等距位置，而在第一段内部。能量纵轴上两端分别为−0.30606177与+0.45813323 eV，间隔由 `0.45813323−(−0.30606177)` 得到0.764195 eV；统一换成VBM零点后两端成为0与0.764195，间隙不变。父SCF与路径各自给出的费米能相差1.73922 meV，若左右两栏分别减去各自的值，就会把这个人为偏移带进共轴图。

这套孤立 SnSe₂ 是后续 SnSe₂/Sr₂N 分析的层来源参照，尚未与该界面建立相同面内应变、几何及势参考。接触后若出现穿越 E_F 的分支，要逐态核对是否来自这个原本未占据的导带区；晶格改变和层间接触的影响须用匹配孤立层对照区分。

<figure><img src="/Atlas/examples/vasp/snse2-electronic/figures/bands-dos.png" alt="同一 SnSe2 模型的路径能带与18乘18乘1均匀SCF态密度" loading="lazy"/><figcaption>左：150 个路径点的20条能带；右：父 SCF 的总 DOS、Sn-s 与两原子合计的 Se-p。两侧共用父 SCF 费米能零点。DOS 保留实际采样，不额外平滑。</figcaption></figure>

为了看清第一段内部的价带顶与M点导带底，下面将同一数据放大到−1～1.5 eV。采用原文Fig. 1(c)的共用能量纵轴、左能带/右水平PDOS布局，灰色总DOS、红色Sn-s、紫色Se-p分别读取真实表；VBM/CBM标记仍来自前面的路径极值。右侧的小点保留每个实际能量采样位置，让301点粗网格的折线表达可以直接辨认。

<figure><img src="/Atlas/examples/enrichment-20261003/electronic/snse2-edge-panels.svg" alt="gnuplot绘制的真实SnSe2路径带边和均匀网格水平PDOS放大图" loading="lazy"/><figcaption>由本页3000个路径态与301点DOS原值绘制，统一减父SCF的−2.39071823 eV；左栏累计距离单位Å⁻¹，右栏为三原子胞states/eV/cell。gnuplot只连接已有采样；未拟合峰、未追加展宽。</figcaption></figure>

[打开原尺寸SVG](/Atlas/examples/enrichment-20261003/electronic/snse2-edge-panels.svg) · [打开1440×780 PNG](/Atlas/examples/enrichment-20261003/electronic/snse2-edge-panels.png) · [下载矢量PDF](/Atlas/examples/enrichment-20261003/electronic/snse2-edge-panels.pdf)。手机上可打开原尺寸文件并放大，读取带边标记、轨道图例及右侧采样点。

价带顶旁的紫色Se-p谱重比红色Sn-s明显，导带起始能区两种轨道共同出现；但右栏在同一能量合并了全网格的态，具体M点同一态的0.243与0.292仍要由[PROCAR表](/Atlas/m/fatband/vasp/)读取。本页采用论文看得见的布局和读图顺序；论文LDA界面与本页PBE孤立层是不同计算，也没有公开脚本可用来推断其绘图参数。

<details>
<summary>实际CSV到gnuplot共轴图：处理逻辑、完整源码、命令和输出</summary>

先将长表按(k,band)转为150行、每行20条带的矩阵，重复的路径端点保留；DOS则原样取TDOS、Sn-s和两个Se合计的p。程序核对记录数、路径距离和共同零点，然后gnuplot逐列连接带能，以DOS值为横轴、同一相对能量为纵轴。绘图软件不承担原始电子态提取。

可以向AI编码助手明确提出：

```text
读取已有tables/path.csv、bands.csv和dos.csv，检查150×20个唯一(k,band)、共同父SCF能量零点和301个递增DOS能量。按真实距离转成gnuplot矩阵，不平滑、重展宽或重归一PDOS。以原文Fig.1(c)的共轴能带/水平PDOS表达绘制带边能窗，并标出已有VBM/CBM。给出标准库转换源码、gnuplot源码和实际运行日志；拒绝覆盖旧输出。
```

[转换源码](/Atlas/examples/enrichment-20261003/electronic/prepare_snse2_panels.py) · [gnuplot源码](/Atlas/examples/enrichment-20261003/electronic/snse2-edge-panels.gp) · [带能矩阵](/Atlas/examples/enrichment-20261003/electronic/snse2-bands.dat) · [水平PDOS数据](/Atlas/examples/enrichment-20261003/electronic/snse2-pdos.dat) · [实际输出](/Atlas/examples/enrichment-20261003/electronic/prepare-snse2.out.txt)。标准库转换和gnuplot 6.0足够完成此图，不依赖Matplotlib。

```python
#!/usr/bin/env python3
"""Repack frozen SnSe2 CSVs for gnuplot; no smoothing or recalculation."""
import argparse
import csv
import math
from pathlib import Path


def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_new(path, rows):
    with path.open("x") as f:
        for row in rows:
            f.write(" ".join(format(x, ".12g") for x in row) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tables", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    path = read(args.tables / "path.csv")
    bands = read(args.tables / "bands.csv")
    dos = read(args.tables / "dos.csv")
    if len(path) != 150 or len(bands) != 3000 or len(dos) != 301:
        raise ValueError("This frozen example requires 150 k points, 20 bands, 301 DOS points")
    states = {}
    for row in bands:
        key = (int(row["k_index"]), int(row["band"]))
        if key in states:
            raise ValueError("Duplicate (k, band)")
        states[key] = row
    matrix = []
    zeros = []
    for i, p in enumerate(path, 1):
        if int(p["k_index"]) != i:
            raise ValueError("Path order changed")
        distance = float(p["distance_Ainv"])
        values = [distance]
        for band in range(1, 21):
            row = states[(i, band)]
            if abs(float(row["distance_Ainv"]) - distance) > 1e-10:
                raise ValueError("Path/band distance mismatch")
            relative = float(row["energy_minus_scf_EF_eV"])
            zeros.append(float(row["energy_eV"]) - relative)
            values.append(relative)
        matrix.append(values)
    if max(zeros) - min(zeros) > 1e-9 or abs(zeros[0] + 2.39071823) > 1e-9:
        raise ValueError("Energy zero differs from frozen SCF reference")
    spectra = [[float(row[k]) for k in
                ("total_DOS_states_per_eV_cell", "Sn_s", "Se_p", "energy_minus_scf_EF_eV")]
               for row in dos]
    if any(not math.isfinite(x) for row in matrix + spectra for x in row):
        raise ValueError("Non-finite input")
    if any(spectra[i][3] <= spectra[i - 1][3] for i in range(1, len(spectra))):
        raise ValueError("DOS energies are not increasing")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    destinations = [args.output_dir / n for n in ("snse2-bands.dat", "snse2-pdos.dat")]
    if any(p.exists() for p in destinations):
        raise FileExistsError("Use a new output directory; original results are retained")
    write_new(destinations[0], matrix)
    write_new(destinations[1], spectra)
    print("Bands: 150 rows x 21 columns; all 20 bands and duplicated segment endpoints retained")
    print("DOS: 301 rows x 4 columns; TDOS, Sn-s, summed Se-p, E-SCF_EF; no smoothing")
    print("Energy zero: SCF EF = -2.39071823 eV")


if __name__ == "__main__":
    main()
```

```gnuplot
# Run beside the two .dat files written by prepare_snse2_panels.py.
# gnuplot 6.0; existing CSV values, no fitting or additional smoothing.
# Default: SVG. Use gnuplot -e "raster=1" or -e "pdf=1" for other exports.
if (!exists("raster")) raster=0
if (!exists("pdf")) pdf=0
if (pdf) {set terminal pdfcairo enhanced color size 10.8in,5.85in font "DejaVu Sans,14"; set output "snse2-edge-panels.pdf"} else {if (raster) {set terminal pngcairo size 1440,780 font "DejaVu Sans,18"; set output "snse2-edge-panels.png"} else {set terminal svg size 1080,585 font "DejaVu Sans,14"; set output "snse2-edge-panels.svg"}}
set encoding utf8
set multiplot
set border linewidth 1.2
set tics out nomirror
set yrange [-1:1.5]
set ytics -1,0.5,1.5
set lmargin at screen 0.085
set rmargin at screen 0.68
set bmargin at screen 0.15
set tmargin at screen 0.90
set xrange [0:2.574194239014428]
set xtics ("Γ" 0, "M" 0.9422205454845932, "K" 1.486211776671035, "Γ" 2.574194239014428)
set ylabel "E − E_F (eV)"
set xlabel "Γ–M–K–Γ; cumulative distance (Å^{-1})"
unset key
set title "(a) Frozen PBE SnSe₂: path band edges" offset 0,0.5
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead dt 2 lc rgb "#666666"
set arrow 2 from first 0.9422205454845932, graph 0 to first 0.9422205454845932, graph 1 nohead lc rgb "#dddddd"
set arrow 3 from first 1.486211776671035, graph 0 to first 1.486211776671035, graph 1 nohead lc rgb "#dddddd"
set label 1 "VBM" at 0.23074792714808598,-0.30606177 point pt 7 ps 0.65 offset 1,-0.8
set label 2 "CBM" at 0.9422205454845932,0.45813323 point pt 7 ps 0.65 offset 1,0.8
plot for [n=1:20] "snse2-bands.dat" using 1:(column(n+1)) with lines lw 1.5 lc rgb "#303438"
unset label
unset arrow 2
unset arrow 3
set lmargin at screen 0.735
set rmargin at screen 0.965
unset ylabel
set format y ""
set xrange [0:8]
set xtics 0,2,8
set xlabel "DOS (states/eV/cell)"
set title "(b) Uniform 18×18×1" offset 0,0.5
set key at graph 0.98,0.97 right top font ",11" spacing 0.8 samplen 1.3 opaque
plot "snse2-pdos.dat" using 1:4 with linespoints pt 7 ps 0.22 lw 1.5 lc rgb "#6c737b" title "TDOS", \
     "snse2-pdos.dat" using 2:4 with linespoints pt 7 ps 0.22 lw 1.5 lc rgb "#b83f47" title "Sn-s", \
     "snse2-pdos.dat" using 3:4 with linespoints pt 7 ps 0.22 lw 1.5 lc rgb "#7654a7" title "Se-p (2 atoms)"
unset multiplot
unset output
```

解开原下载包，将两份源码放在 `snse2-electronic` 根目录；先在新目录生成数据，再在该目录作图：

```bash
python3 prepare_snse2_panels.py tables --output-dir edge-panels
cd edge-panels
gnuplot ../snse2-edge-panels.gp
# 同一源文件也可导出用于检查的PNG：
gnuplot -e "raster=1" ../snse2-edge-panels.gp
# PDF矢量导出，坐标、数据和双面板布局来自同一源文件：
gnuplot -e "pdf=1" ../snse2-edge-panels.gp
```

在Talos对本次真实CSV执行后的输出：

```text
Bands: 150 rows x 21 columns; all 20 bands and duplicated segment endpoints retained
DOS: 301 rows x 4 columns; TDOS, Sn-s, summed Se-p, E-SCF_EF; no smoothing
Energy zero: SCF EF = -2.39071823 eV
```

gnuplot生成SVG、PNG与矢量PDF时stderr均为空；PNG与PDF渲染已实际查看，带边标记、共同零能虚线、轨道图例与两个横轴均可辨认。网页集成后的桌面及手机排版另由整站检查。

</details>

<figure>
<img src="/Atlas/figures/literature/fan2025-snse2-ptte2-fig1cfi.png" alt="Fan等原文Fig.1(c,f,i)：孤立SnSe₂、PtTe₂与界面的能带和共轴PDOS" />
<figcaption>Fan 等，arXiv:2502.13690v1 (2025)，原文第 3 页 Fig. 1(c,f,i)。三行依次为孤立 SnSe₂、PtTe₂ 与界面；各自以 E_F 为零点，红/蓝在界面面板分别标 SnSe₂/PtTe₂ 层来源。<a href="https://arxiv.org/pdf/2502.13690v1#page=3">论文原文</a>。</figcaption>
</figure>

[相关论文 PDF 第3页 Fig. 1(c)](https://arxiv.org/pdf/2502.13690v1#page=3)左侧为孤立SnSe₂的 Γ–M–K–Γ 能带，右侧为共用 E−E_F 纵轴的总DOS、Sn-s/p和Se-p，DOS轴标states/eV。先读带边，再沿相同高度看轨道谱重：价带边以Se-p为主，导带边同时有Sn-s与Se-p。Fig. 1(i)才增加界面红/蓝层来源，不能从(c)推出与第二层的杂化。

本页既有共轴图按这一方式组织真实数据：`path.csv`给累计倒格距离，均匀SCF的 `dos.csv`给右栏，两栏减同一个父SCF费米能，DOS按本次三原子胞展示。复现时保留整包，运行共用提取器后由 `plot.py`读CSV，不重新平滑锯齿或把各投影峰归一到一。论文Sec. II主模型为LDA，本页为固定PBE晶胞，参考的是图法与分析，带隙仍用本页路径表；同态来源接[本次胖带](/Atlas/m/fatband/vasp/)。