SnSe₂ 的带边附近由哪些轨道贡献，DOS 的积分又应数到多少电子态？这里直接使用均匀 18×18×1 静态 SCF 写出的 DOSCAR，读总 DOS、原子投影和积分 DOS；它与路径能带属于同一结构及父密度。

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

## DOS 从哪个分支读取

本页使用 `scf/DOSCAR`，没有另做密网格 NSCF。静态 `NSW=0` 避免把不同离子步的 DOS 平均在一起，`LORBIT=11` 使每个原子都有 lm 分辨数据。实际XML的ISYM=2与VASP 5.4.4投影对称化问题的核对见[同链PROCAR页](/Atlas/m/fatband/vasp/#h-procar-要和同一个态配对)，定量比较单个方向分量时应一并读取。线模式的 `bands` 只适合本征值和逐态投影；它的 DOSCAR 不用于这里的布里渊区态数。

```bash
head -n 9 scf/DOSCAR
cat scf/KPOINTS
```
```text
   3   3   1   0
  0.7840219E+02  0.3850053E-09  0.3850053E-09  0.1832253E-08  0.5000000E-15
  1.000000000000000E-004
  CAR 
 SnS2                                    
      7.60848672    -25.37858117  301     -2.39071823      1.00000000
    -25.379  0.0000E+00  0.0000E+00
    -25.269  0.0000E+00  0.0000E+00
    -25.159  0.0000E+00  0.0000E+00
```
```text
K-Spacing Value to Generate K-Mesh: 0.020
0
Gamma
  18  18   1
0.0  0.0  0.0
```

前五行是系统信息，第六行依次是最大能量、最小能量、`NEDOS`、费米能和尾部标记。随后 301 行是 `能量、总 DOS、积分 DOS`。再后面每个原子有一行表头和 301 行投影，非磁性 `LORBIT=11` 的列依次为 `E,s,py,pz,px,dxy,dyz,dz2,dxz,x2-y2`。[VASP DOSCAR](https://vasp.at/wiki/DOSCAR)

投影逐原子归并：Sn 是第一原子，第二、第三原子都是 Se；将三个 p 分量相加，再把两个 Se 相加。总 DOS 的单位是 states/eV/cell，原子投影按选定原子求和后也按这个晶胞展示。积分 DOS 是从低能端累积的态数，不是能窗内每条曲线的最大高度。

这三页使用同一个 `snse2-electronic` 下载包。运行参数和父密度来源见[能带页的回读记录](/Atlas/m/bands/vasp/#h-从输出回读运行参数)；本页DOS来自均匀 SCF 的 `scf/DOSCAR`，物理上的DOS计算不需要先求路径能带。包内共用 `analyse.py` 同时提取能带、轨道投影与DOS，因此运行该脚本仍须保留整包 `scf` 和 `bands` 文件，具体依赖见下文。

## 数据配对与提取要求

先核对总 DOS 与每个原子块的行数、能量网格、列数，再做轨道求和。读取文件中已经给出的积分 DOS，而不是用一条粗采样曲线重新定义电子数。图与能带共用能量纵轴，能够同时看出“哪里有态”和“这些态怎样色散”。

可以使用这个 coding prompt：

```text
读取 scf/DOSCAR、POSCAR、KPOINTS、vasprun.xml 与 EIGENVAL，确认均匀静态18×18×1网格、无SOC、ISPIN=1。
解析总DOS的301行及Sn、Se、Se三个lm投影块，校验每个能量网格，禁止把bands/DOSCAR当BZ积分。
输出完整能窗的总DOS、IDOS、Sn-s/p/d与两个Se合计s/p/d的CSV，不把投影和强制归一到总DOS。
以父SCF XML的efermi统一零点；在EF处读取IDOS，并用EIGENVAL权重与二重自旋简并核对电子数。
用论文式能带加水平DOS共轴图展示原始采样。保留锯齿，不增加拟合峰或任意平滑，输出PNG/SVG/PDF。
```

## 从文件到表格，再到图

先保存数据表，再画图。现有 `analyse.py` 没有DOS独立模式：它固定读取 `scf/vasprun.xml`、`scf/EIGENVAL`、`scf/DOSCAR` 以及 `bands/vasprun.xml`、`bands/POSCAR`、`bands/EIGENVAL`、`bands/PROCAR`，并从包内路径设置核对节点，检查模型、状态数、PROCAR 配对和DOS列数。读取本下载包时保留整包两支数据，再输出能级、投影、DOS、路径节点及带单位的数值CSV；只重画已经保存的结果时直接运行 `python3 plot.py`，该脚本只读CSV。若仅重新计算均匀DOS分支，须采用DOS专用提取器，或将共用脚本改成独立DOS模式，不能只留 `scf` 目录仍直接执行本版 `analyse.py`。共轴图中的路径曲线来自独立 `bands` 分支，不参与DOS的布里渊区积分。下面的完整源码已用本次整包数据实际运行。

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

## 态数与轨道贡献

| 核对量 | 本次输出 |
|---|---|
| 价电子数 | Sn_d 的 14 + 两个 Se 的 6，共 26 |
| EIGENVAL 加权占据 | 26.00000205；偏差来自打印权重的有限精度 |
| 积分 DOS 在父 SCF E_F 处 | 26.00000000 |
| 能窗低端 / 高端积分 DOS | 0 / 40，覆盖本次20条非磁性能带 |
| 总能窗 | −25.379 至 7.608 eV（绝对能量） |
| 输出能量步长 / Gaussian 宽度 | 约 0.11 eV / 0.05 eV |

`EIGENVAL` 的占据列在此为 0 或 1，加权态数乘二才与 26 个价电子一致。积分 DOS 的高端为 40 则对应 20 条带的二重自旋简并，其中包含未占据态，不能把 40 读成电子数。直接对有限步长的总 DOS 作梯形积分约为 40.00675；文件中的 IDOS 与这种数值积分并非逐点完全相同。

实际读一段能窗时先明确要读哪条量：总积分DOS给出的 $N(E_2)-N(E_1)$ 是该范围的累计态数差；对选定轨道的PDOS求面积，得到的则是该轨道投影谱权重。两者都不能用峰的最大高度代替。这里高端40与费米能处26相差14，表示本次20带模型的完整能窗还包含14个未占据态；不是多出14个电子。总IDOS已包含非磁性自旋简并，既不用再乘二，也不用因为有三个原子再乘三。

本页301点横跨约32.99 eV，打印步长约0.11 eV，是Gaussian宽度0.05 eV的约2.2倍。因此一个窄峰可能落在相邻打印点之间；曲线的折线顶点只是已有采样的连接，不是峰位拟合。增加NEDOS可以改善能量轴表达，但它不会补上18×18×1电子网格漏采的态，改变SIGMA又会同时改变峰宽。核对峰形时将这三种改变分开，读本页历史数据时则保留原曲线和IDOS。

<figure><img src="/Atlas/examples/vasp/snse2-electronic/figures/bands-dos.png" alt="SnSe2的路径色散与实际均匀网格总态密度和轨道态密度" loading="lazy"/><figcaption>共轴图在 −7 至4 eV能窗显示总DOS及Sn-s、Se-p投影；表格与CSV保留完整能窗和全部s/p/d组。右侧的细节来自301个能量点，未平滑或重新展宽。</figcaption></figure>

<figure>
<img src="/Atlas/figures/literature/fan2025-snse2-ptte2-fig1cfi.png" alt="Fan等原文Fig.1(c,f,i)：孤立SnSe₂、PtTe₂与界面的能带和共轴PDOS" />
<figcaption>Fan 等，arXiv:2502.13690v1 (2025)，原文第 3 页 Fig. 1(c,f,i)。三行依次为孤立 SnSe₂、PtTe₂ 与界面；各自以 E_F 为零点，红/蓝在界面面板分别标 SnSe₂/PtTe₂ 层来源。<a href="https://arxiv.org/pdf/2502.13690v1#page=3">论文原文</a>。</figcaption>
</figure>

[相关论文 PDF 第3页 Fig. 1(c)](https://arxiv.org/pdf/2502.13690v1#page=3)右栏将总DOS与Sn-s、Sn-p、Se-p画成水平曲线，纵轴与左侧能带共用E−E_F，DOS轴标states/eV。先定位价带/导带能区，再沿同一高度读轨道贡献：价带边以Se-p为主，导带边同时有Sn-s与Se-p。PDOS重叠不证明同一个态内杂化，仍要回到波函数逐态投影。

本站共轴图保留灰色总DOS、Sn-s与两个Se合计的Se-p，完整s/p/d在CSV。复现这种面板时，DOS取均匀SCF的301点，能量轴与路径用同一父费米能，按三原子胞states/eV/cell展示，既不把各峰归一到一，也不额外乘自旋2。共用提取器按前文保留两分支，只重画运行 `plot.py`；同链[胖带](/Atlas/m/fatband/vasp/)核对带边权重。论文LDA与本页PBE模型不同，分析方法可以对应，数值不替换。

这份 DOS 的步长比展宽还大，曲线有明显采样锯齿。因此它回答态数和轨道来源，不能精确定位窄峰或从展宽尾部读取带隙；更细峰形需要在同一模型下对电子网格、能量点与展宽作独立对照。

用于接触前后比较时，先固定相同的每化学式归一化与投影定义，再在匹配的面内晶胞下检查带边附近是否新增部分占据谱重。当前图只来自孤立层；Se-p 与 Sn-s 的共现可与同链 PROCAR 交叉读取，但与另一层的杂化必须在界面本身的逐态投影中判断。
