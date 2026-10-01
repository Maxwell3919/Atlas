Al 哪些能带穿过费米能，它们在倒空间中形成怎样的连续等能面？本页逐带提取这些面，并用两套完整网格比较其截面。能带图沿一条路径画出电子能量。费米面则在整个三维倒空间里寻找满足 Eₙ(k)=E_F 的位置：一条能带可以贡献一个电子口袋、一个空穴口袋，也可能穿过倒空间单元的边界。只沿高对称线做一次能带计算，没有足够信息画这张面。

[Bekaert 等 Sec. 2 与 Fig. 2](https://doi.org/10.1039/D0NR03875J)还用费米速度为二维费米轮廓着色，其中速度取能量对波矢的一阶导数。本页计算的是三维 Al 的费米面几何，颜色区分能带；速度着色需要在同一模型上进一步求导。

本例采用 fcc Al，结构与父 SCF 的准备见 [Al 声子算例](/Atlas/m/phonon-dfpt/qe/)。计算使用 QE 7.5、LDA-PZ，不含自旋极化与 SOC；随后在完整均匀网格上求本征值，寻找与费米能相交的等能面。SCF 与 NSCF 的一般操作可以参考入门页，但保存目录必须由这套 Al 输入生成。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [后处理用户手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [Plotly 的三维等值面](https://plotly.com/python/3d-isosurface-plots/)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-electronic-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 均匀网格必须能恢复成完整三维数组

为了让第一次读图容易核对，我们直接保留全部 k 点，而不是先缩到不可约区再重建。24³ 和 32³ 网格分别有 13824 与 32768 个点；输入写明 `nosym` 与 `noinv`，后处理仍再次检查点数和重复点，不能只相信输入文件。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ cat al.nscf.in
&CONTROL
 calculation = 'nscf'
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 0
 nat = 1
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 6
 nosym = .true.
 noinv = .true.
/
&ELECTRONS
 conv_thr = 1.0d-12
 diagonalization = 'cg'
 diago_thr_init = 1.0d-9
 diago_full_acc = .true.
 diago_cg_maxiter = 200
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.97803390040536 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.97803390040536 1.97803390040536 0.00000000000000
K_POINTS automatic
32 32 32 0 0 0
```
这是最终用于作图的实际输入。`nbnd=6` 给本例留出足够空带去检查哪些能带越过 E_F，`verbosity=high` 保留文本里的 k 点和本征值；精确提取仍使用 XML，避免文本列数变化影响读取。SCF 的 `prefix=al`、`outdir=./tmp` 在同一个计算目录内相接。

`diago_full_acc=.true.` 让空带使用与占据带相同的求解精度，避免在穿越费米能的分支上沿用较松的空带阈值。`noinv=.true.` 关闭 k→−k 的时间反演约化，目的是保留后处理所需的完整点阵；这个采样开关本身不表示材料破坏了时间反演对称性。

## 程序结束之后，先把没收敛的本征值找出来

第一次 24³/32³ NSCF 使用默认 Davidson。输出末尾都有 `JOB DONE.`；本征值求解过程还打印了以下信息：

```console
maxwell@maxwell:~/al/fermi/k32-cg$ grep "not converged" ../k24/al.nscf.out
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
     c_bands:  1 eigenvalues not converged
```
这些提示表明部分本征值尚未达到求解阈值。默认非自洽本征值阈值与 `conv_thr`、电子数有关；原计算在继承的设置下未达到本征值求解阈值；仅凭这条警告不能判断是阈值选择、迭代上限还是求解器造成了困难。我们保留原来的 `k24`、`k32` 目录，在新目录明确设置 CG 求解、1.0×10⁻⁹ Ry 的本征值阈值、空带同精度以及最大迭代数，再完整重算 SCF→NSCF。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ diff ../k32/al.nscf.in al.nscf.in
24a25,28
>  diagonalization = 'cg'
>  diago_thr_init = 1.0d-9
>  diago_full_acc = .true.
>  diago_cg_maxiter = 200
```
新输出按 1.0×10⁻⁹ Ry 的本征值阈值重新检查。它比后面 0.1—0.2 eV 的能量窗口小许多；k 网格对费米面形状的影响则由两种网格的结果比较。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-fs32cg
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
mpirun -np 8 <qe_bin>/pw.x -nk 8 -in al.nscf.in > al.nscf.out 2> al.nscf.err
```
```console
maxwell@maxwell:~/al/fermi/k32-cg$ sbatch run.slurm
Submitted batch job 1965
```
运行时，均匀网格 NSCF 会不断输出 `Computing kpt #`。本次使用 `-nk 8`，32768 个点分到 8 个 pool，所以一个 pool 的计数到 4096，不能把它误读成总共只算了 4096 个点。

```bash
squeue -j 1965 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f al.nscf.out
```

```console
maxwell@maxwell:~/al/fermi/k32-cg$ tail -9 al.nscf.out
 
     PWSCF        :   2m32.15s CPU   2m44.18s WALL

 
   This run was terminated on:  21:51:25  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
复算后的 stdout 没有 `not converged`，stderr 为空。24³ 和 32³ NSCF 分别用时 1 分 15.35 秒与 2 分 44.18 秒。计算目录保留原始失败信息和新输出，下面只用后者的 XML 生成图。

## XML 里取到的不只是一个费米能数值

```console
maxwell@maxwell:~/al/fermi/k32-cg$ grep "the Fermi energy" al.nscf.out
     the Fermi energy is     8.3815 ev
```
这行方便在终端迅速核对。XML 中的 `fermi_energy` 和 `eigenvalues` 使用 Hartree；[extract_fermi_electronic.py](/Atlas/examples/al-electronic/fermi/extract_fermi_electronic.py) 把它们统一乘以 27.211386245988 转为 eV，再减去同一份 NSCF 的 E_F。不能把文本中已是 eV 的数值再乘一次换算常数。

```console
maxwell@maxwell:~/al/fermi/..$ .venv/bin/python fermi/extract_fermi_electronic.py
k=24^3 nks=13824 EF=8.39793432 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.61975726 J(X)=0.09968022 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.31708865 J(X)=0.06123457 eV^-2; direct-sum check passed
k=32^3 nks=32768 EF=8.38150272 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.53305558 J(X)=0.04490039 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.28204495 J(X)=0.03678119 eV^-2; direct-sum check passed
```
提取程序读取 XML 的倒格矢，把每一个 k 点映射到整数网格。它要求每个格点恰好出现一次，再保存 `fermi-grid.npz`；缺点、重复点或无法对应的坐标都会使提取程序停止。

32³ 网格里的各条带相对 E_F 的范围是：

| 带号 | 最低能量 / eV | 最高能量 / eV | 是否穿过 0 |
|---|---:|---:|---|
| 1 | -11.548067 | -0.893493 | 否 |
| 2 | -4.487133 | 12.944767 | 是 |
| 3 | -0.326782 | 12.944767 | 是 |
| 4 | 1.392852 | 14.105571 | 否 |
| 5 | 5.798257 | 16.257599 | 否 |
| 6 | 9.493963 | 20.080026 | 否 |

第一带在所有采样点都低于 E_F，第四带及以上高于 E_F；本次被网格直接检测到穿越零能的，是第二带和第三带。因此两张费米面分别保留带号，不能把它们叠起来后称作同一个口袋。

<span id="把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
## 重建周期点阵与提取等能面

等能面提取前，先将本征值恢复为完整的周期 k 点阵。下面的任务明确网格顺序、费米能来源和异常记录的处理方式。

```text
编写 Al 完整网格费米面后处理程序，使用 Python 3、NumPy、Matplotlib 和 Plotly。
输入：fermi/k24-cg、k32-cg 的 fermi-grid.npz、grid-info.json，energy_eV 已是各 NSCF 的 E−EF，网格分别为 13824 和 32768 点。
方法：分别画 band 2/3 的零等值面与 k3=0 截面，3D 图框标为原始倒格矢周期单元；每套计算使用自己的 EF。当前网格坐标为 −0.5…0.5−1/N，边界面按采样范围截断。
检查：完整网格、六条带、唯一点与单位，分别比较两带和两种网格形状；细小口袋精度由进一步网格比较确定。
输出：源码、依赖、命令、PNG/SVG/PDF 截面及可旋转 HTML；提供 --standalone 导出包含绘图库的 HTML。
```

## 后处理源码与运行

完整源码：[extract_fermi_electronic.py](/Atlas/examples/al-electronic/fermi/extract_fermi_electronic.py) · [plot_fermi.py](/Atlas/examples/al-electronic/plot_fermi.py) · [atlas_plot_style.py](/Atlas/examples/al-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib、Plotly。

<details>
<summary>extract_fermi_electronic.py 的完整源码</summary>

```python
from pathlib import Path
import numpy as np,xml.etree.ElementTree as E,json,hashlib,re
HARTREE_EV=27.211386245988
root=Path(__file__).resolve().parent
summary=[]
for n in [24,32]:
 d=root/f'k{n}-cg';out=(d/'al.nscf.out').read_text();err=(d/'al.nscf.err').read_text()
 assert out.count('JOB DONE.')==1 and not err and 'Error in routine' not in out
 assert 'not converged' not in out.lower()
 xml=d/'data-file-schema.xml';doc=E.parse(xml).getroot();o=doc.find('output');band=o.find('band_structure');nk=int(band.findtext('nks'));nb=int(band.findtext('nbnd'))
 assert nk==n**3
 b=np.array([np.fromstring(o.findtext('basis_set/reciprocal_lattice/'+tag),sep=' ') for tag in ['b1','b2','b3']])
 cell=np.array([np.fromstring(o.findtext('atomic_structure/cell/'+tag),sep=' ') for tag in ['a1','a2','a3']])*0.529177210903
 ef=float(band.findtext('fermi_energy'))*HARTREE_EV
 energies=np.empty((n,n,n,nb));seen=np.zeros((n,n,n),dtype=int)
 for point in band.findall('ks_energies'):
  cart=np.fromstring(point.findtext('k_point'),sep=' ');frac=cart@np.linalg.inv(b)
  scaled=frac*n;assert np.max(np.abs(scaled-np.rint(scaled)))<1e-7
  i=tuple(np.rint(scaled).astype(int)%n);seen[i]+=1
  energies[i]=np.fromstring(point.findtext('eigenvalues'),sep=' ')*HARTREE_EV-ef
 assert np.all(seen==1)
 np.savez_compressed(d/'fermi-grid.npz',energy_eV=energies,fermi_eV=ef,cell_angstrom=cell,grid=n)
 ranges=[{'band':j+1,'min_eV':float(energies[:,:,:,j].min()),'max_eV':float(energies[:,:,:,j].max())} for j in range(nb)]
 crossing=[r['band'] for r in ranges if r['min_eV']<0<r['max_eV']]
 record={'kmesh':n,'nks':nk,'fermi_eV':ef,'crossing_bands':crossing,'band_ranges':ranges,'source_xml_sha256':hashlib.sha256(xml.read_bytes()).hexdigest(),'nscf_out_sha256':hashlib.sha256((d/'al.nscf.out').read_bytes()).hexdigest(),'definition':'Energy grid includes all k, no interpolation, E-EF in eV.'}
 (d/'grid-info.json').write_text(json.dumps(record,indent=2));summary.append(record)
 print(f'k={n}^3 nks={nk} EF={ef:.8f} eV crossing bands={crossing}; all grid cells assigned once')
 for sigma in [.10,.20]:
  weight=np.exp(-0.5*(energies/sigma)**2).sum(axis=3)/(sigma*np.sqrt(2*np.pi))
  spectrum=np.fft.fftn(weight);J=np.fft.ifftn(spectrum.conj()*spectrum).real/nk
  assert np.min(J)>-1e-10
  assert abs(J[0,0,0]-np.mean(weight*weight))<1e-8
  # one nontrivial point cross-check against direct Brillouin-zone sum
  idx=(n//4,0,n//4);direct=np.mean(weight*np.roll(weight,tuple(-x for x in idx),axis=(0,1,2)))
  assert abs(J[idx]-direct)<1e-8
  np.savez_compressed(d/f'nesting-s{sigma:.2f}.npz',nesting_eV_minus2=J,sigma_eV=sigma,grid=n)
  cut=np.array([[i/n,J[i,0,i],J[i,0,i]/J[0,0,0]] for i in range(n//2+1)])
  np.savetxt(d/f'nesting-GX-s{sigma:.2f}.csv',cut,delimiter=',',header='q_fraction_along_b1_plus_b3,J_eV_minus2,J_over_J0',comments='')
  print(f' sigma={sigma:.2f} eV J(0)={J[0,0,0]:.8f} J(X)={J[n//2,0,n//2]:.8f} eV^-2; direct-sum check passed')
(root/'summary.json').write_text(json.dumps(summary,indent=2))
```

</details>

<details>
<summary>plot_fermi.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import plotly.graph_objects as go
r=Path(__file__).resolve().parent;(r/"figures").mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(6.3,5.4),layout="constrained")
for n,style in [(24,"--"),(32,"-")]:
    e=np.load(r/f"fermi/k{n}-cg/fermi-grid.npz")["energy_eV"]
    x=np.arange(-n//2,n//2)/n
    for band,color in [(1,"#0072b2"),(2,"#d55e00")]:
        plane=np.fft.fftshift(e[:,:,0,band])
        ax.contour(x,x,plane.T,levels=[0],colors=[color],linestyles=[style],linewidths=1.5)
ax.set(xlabel="k₁ (reciprocal fractional coordinate)",ylabel="k₂ (reciprocal fractional coordinate)",title="Al Fermi-surface section at k₃=0",aspect="equal")
ax.legend(handles=[Line2D([0],[0],color="#0072b2",label="band 2"),Line2D([0],[0],color="#d55e00",label="band 3"),Line2D([0],[0],color="0.3",ls="--",label="24³ mesh"),Line2D([0],[0],color="0.3",label="32³ mesh")],frameon=False,fontsize=9)
fig.savefig(r/"figures/fermi-slices.png",dpi=220);fig.savefig(r/"figures/fermi-slices.pdf")
e=np.load(r/"fermi/k32-cg/fermi-grid.npz")["energy_eV"];n=e.shape[0]
x=np.arange(-n//2,n//2)/n;X,Y,Z=np.meshgrid(x,x,x,indexing="ij")
p=go.Figure()
for band,color in [(1,"#0072b2"),(2,"#d55e00")]:
    v=np.fft.fftshift(e[:,:,:,band])
    p.add_trace(go.Isosurface(x=X.ravel(),y=Y.ravel(),z=Z.ravel(),value=v.ravel(),isomin=-1e-7,isomax=1e-7,surface_count=1,opacity=.65,colorscale=[[0,color],[1,color]],showscale=False,caps=dict(x_show=False,y_show=False,z_show=False),name=f"band {band+1}",showlegend=True))
p.update_layout(title="Al: Eₙ(k) − E_F = 0, 32³ QE grid",scene=dict(xaxis_title="k₁",yaxis_title="k₂",zaxis_title="k₃",aspectmode="cube"),annotations=[dict(text="Reciprocal fractional cell; not a Wigner–Seitz BZ crop",xref="paper",yref="paper",x=.5,y=-.06,showarrow=False)],margin=dict(l=0,r=0,b=60,t=55))
p.write_html(r/"figures/fermi-surface.html",include_plotlyjs=True if "--standalone" in sys.argv else "cdn",full_html=True)
```

</details>

解压本页示例包后，在 `al` 根目录执行：

```bash
python3 -m pip install numpy matplotlib plotly
python3 fermi/extract_fermi_electronic.py
python3 plot_fermi.py
```

## 先看截面，再转动三维等值面

绘图程序读取两个网格目录里的 `fermi-grid.npz`，生成二维截面对照与可在浏览器中旋转的三维 HTML。

<figure><img src="/Atlas/examples/al-electronic/figures/fermi-slices.png" alt="Al 第2和第3能带的费米面截面" loading="lazy"/><figcaption>k₃=0 截面：实线与虚线对应两个真实 k 网格，颜色区分能带。横纵坐标是倒格矢分数坐标。</figcaption></figure>

网页版本需要联网加载 Plotly；在本机运行 `python3 plot_fermi.py --standalone` 可导出包含绘图库的独立 HTML。

[打开可转动的三维费米面](/Atlas/examples/al-electronic/figures/fermi-surface.html)。交互图以 32³ 本征值网格的零等值面构成，能量在相邻采样点间插值。图框采用倒格矢分数坐标，范围为 `−0.5…0.5−1/N`。当前绘图未补上边界外的周期节点，面在此范围截断；它表示原始倒格矢周期单元的采样部分，未裁剪成 Wigner–Seitz 第一布里渊区。

两次计算得到 E_F=8.39793432 eV 和 8.38150272 eV，相差约 0.01643 eV。画图时各自减去各自的 E_F，并比较口袋形状随网格的变化。这里确认了第二、第三带穿越费米能这一观察；细小口袋的尺寸、连接方式和后续嵌套峰，仍需要更密网格与展宽检查。

## 二维异质结 ZrCl₂/Sc₂C：从 BXSF 网格重建六角第一布里渊区费米面等能线

除直接读取 XML 外，QE 的 `fs.x` 后处理程序会生成 XCrySDen 格式的 `_fs.bxsf` 文件。文件头部记录费米能级与倒格矢基矢，随后按 `BAND: iband` 逐带列出覆盖 `[0, 1] × [0, 1] × [0, 1]` 周期倒格元胞的 `(N₁+1) × (N₂+1) × (N₃+1)` 能量网格。

在 **`ZrCl₂/Sc₂C`**（[完整计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，[`FS/zrclscc_fs.bxsf`](/Atlas/examples/zrcl2-sc2c/FS/zrclscc_fs.bxsf) 对应 `64 × 64 × 1` k 网格（包含 `65 × 65 × 2` 个 BXSF 网格节点，保存第 `25–29` 共 5 条能带，`E_F = 0.3154 eV`），其中穿过费米能级的是 **Band 26** 与 **Band 27**。如果直接在分数坐标 `[0, 1] × [0, 1]` 的菱形周期元胞上画等值线，Γ 点会落在四个角上，不便观察围绕 Γ 与 K 的六角对称性。在 [`plot_zrcl2_sc2c.py`](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py) 中，后处理步骤为：
1. 利用周期性将网格平铺扩展，并按平面倒格基矢变换到笛卡尔倒空间 `(k_x, k_y)`；
2. 构造六角形 Wigner–Seitz 第一布里渊区边界（顶点为 6 个 K/K' 点，边中点为 6 个 M 点），将 `E_n(k_x, k_y) = E_F` 的等能线裁剪在第一布里渊区内；
3. 在 `zrcl2-sc2c-electronic.png` 的子图 **c** 中绘制 **Band 26**（蓝色）与 **Band 27**（橙红色）的费米面轮廓，并与子图 **a** 的轨道胖带、子图 **b** 的水平 PDOS 对照展示：

<details>
<summary>plot_zrcl2_sc2c.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np

ZR_DIR = Path(__file__).resolve().parent
for candidate in (ZR_DIR, ZR_DIR.parent, ZR_DIR.parents[1] / 'scripts'):
    if (candidate / 'atlas_plot_style.py').exists():
        sys.path.insert(0, str(candidate))
        break

import atlas_plot_style

sys.path.insert(0, str(ZR_DIR))
from tc_table_audit import piecewise_linear_crossings, write_report

PALETTE = {
    'Ink': '#162232',
    'Slate': '#324255',
    'Muted': '#5a6b80',
    'Navy': '#0072b2',
    'Blue': '#2968a8',
    'SoftBlue': '#d6e6f4',
    'Teal': '#009e73',
    'SoftTeal': '#d7ece8',
    'Amber': '#e69f00',
    'Rust': '#d55e00',
    'Coral': '#cc79a7',
    'WarmTint': '#f4efe6',
}

CM1_TO_THZ = 1.0 / 33.3564095198152
FIG_OUT_DIR = (
    ZR_DIR.parents[1] / 'figures' / 'zrcl2-sc2c'
    if (ZR_DIR.parents[1] / 'figures').exists()
    else ZR_DIR / 'figures'
)


def apply_atlas_style() -> None:
    atlas_plot_style.install()


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_figure(fig, stem_name: str) -> None:
    FIG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT_DIR / f'{stem_name}.png')
    plt.close(fig)


def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    data_dir = ZR_DIR / 'scf'
    gnu_path = data_dir / 'bands.dat.gnu'
    proj_path = data_dir / 'fatbands.projwfc_up'
    proj_lines = [line for line in proj_path.read_text().splitlines() if line.strip()]
    header_rows = [
        idx for idx, line in enumerate(proj_lines[:30])
        if len(line.split()) == 3 and all(part.isdigit() for part in line.split())
    ]
    if len(header_rows) != 1:
        raise ValueError(f'Expected one projection header; found {len(header_rows)}.')
    header_idx = header_rows[0]
    natomwfc, nk, nbnd = map(int, proj_lines[header_idx].split())
    if header_idx + 2 >= len(proj_lines):
        raise ValueError('Projection header is missing its spin flags or first state.')
    spin_flags = proj_lines[header_idx + 1].split()
    if len(spin_flags) != 2 or any(flag not in {'T', 'F'} for flag in spin_flags):
        raise ValueError(f'Unexpected projection spin flags: {spin_flags}')
    ptr = header_idx + 2

    raw = np.loadtxt(gnu_path)
    if raw.shape != (nbnd * nk, 2) or not np.isfinite(raw).all():
        raise ValueError(f'Unexpected bands.dat.gnu shape or nonfinite values: {raw.shape}')
    band_blocks = raw.reshape(nbnd, nk, 2)
    k_blocks = band_blocks[:, :, 0]
    if not np.allclose(k_blocks, k_blocks[0:1], rtol=0.0, atol=1e-8):
        raise ValueError('The k-distance sequence differs between band blocks.')
    k_dist = k_blocks[0]
    if not np.isclose(k_dist[0], 0.0, rtol=0.0, atol=1e-8):
        raise ValueError(f'Band path does not start at zero: {k_dist[0]}')
    if np.any(np.diff(k_dist) < -1e-8) or k_dist[-1] <= k_dist[0]:
        raise ValueError('Band path distances are not a forward, nonzero path.')
    bands_e = band_blocks[:, :, 1] - ef

    atom_elements = {1: 'Zr', 2: 'C', 3: 'Cl', 4: 'Cl', 5: 'Sc', 6: 'Sc'}
    group_by_site_orbital = {
        (1, 'D'): 'Zr-4d',
        (5, 'D'): 'Sc-3d',
        (6, 'D'): 'Sc-3d',
        (2, 'P'): 'C-2p',
        (3, 'P'): 'Cl-3p',
        (4, 'P'): 'Cl-3p',
    }
    expected_state_counts = {'Zr-4d': 5, 'Sc-3d': 10, 'C-2p': 3, 'Cl-3p': 6}
    grouped = {key: np.zeros((nbnd, nk)) for key in expected_state_counts}
    state_counts = {key: 0 for key in expected_state_counts}
    expected_ik = np.repeat(np.arange(1, nk + 1), nbnd)
    expected_ib = np.tile(np.arange(1, nbnd + 1), nk)
    block_len = nk * nbnd
    seen_state_ids = set()

    for expected_state in range(1, natomwfc + 1):
        if ptr >= len(proj_lines):
            raise ValueError(f'Projection file ended before state {expected_state}.')
        hdr = proj_lines[ptr].split()
        if len(hdr) < 4:
            raise ValueError(f'Malformed state header at line {ptr + 1}: {hdr}')
        state_id, atom_id = int(hdr[0]), int(hdr[1])
        element, orbital = hdr[2], hdr[3].upper()
        if state_id != expected_state or state_id in seen_state_ids:
            raise ValueError(f'Unexpected or duplicate state id {state_id}; expected {expected_state}.')
        seen_state_ids.add(state_id)
        if atom_id not in atom_elements or element != atom_elements[atom_id]:
            raise ValueError(f'State {state_id} has atom/element mismatch: #{atom_id} {element}.')
        angular_parts = [char for char in orbital if char in 'SPDF']
        if len(angular_parts) != 1:
            raise ValueError(f'State {state_id} has unrecognized orbital label {orbital}.')
        key = group_by_site_orbital.get((atom_id, angular_parts[0]))
        ptr += 1
        rows = []
        for row_index in range(block_len):
            if ptr >= len(proj_lines):
                raise ValueError(f'State {state_id} ended at projection row {row_index}.')
            fields = proj_lines[ptr].split()
            if len(fields) != 3:
                raise ValueError(f'Malformed projection row at line {ptr + 1}: {fields}')
            rows.append((int(fields[0]), int(fields[1]), float(fields[2])))
            ptr += 1
        state_data = np.asarray(rows, dtype=float)
        if not np.array_equal(state_data[:, 0].astype(int), expected_ik):
            raise ValueError(f'State {state_id} has an unexpected k-index sequence.')
        if not np.array_equal(state_data[:, 1].astype(int), expected_ib):
            raise ValueError(f'State {state_id} has an unexpected band-index sequence.')
        state_weights = state_data[:, 2]
        if not np.isfinite(state_weights).all():
            raise ValueError(f'State {state_id} contains nonfinite projection weights.')
        if key is not None:
            grouped[key] += state_weights.reshape(nk, nbnd).T
            state_counts[key] += 1

    if ptr != len(proj_lines) or len(seen_state_ids) != natomwfc:
        raise ValueError(f'Projection records do not close cleanly: consumed {ptr}/{len(proj_lines)} lines.')
    if state_counts != expected_state_counts:
        raise ValueError(f'Unexpected selected state counts: {state_counts}')
    if any(not np.isfinite(curve).all() for curve in grouped.values()):
        raise ValueError('Grouped projection weights contain nonfinite values.')
    return k_dist, bands_e, grouped

def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = ZR_DIR / 'pdos'

    def read_ldos(filename: str) -> tuple[np.ndarray, np.ndarray]:
        arr = np.loadtxt(pdos_dir / filename, comments='#')
        return arr[:, 0] - ef, arr[:, 1]

    e_grid, zr_4d = read_ldos('zrclscc.pdos_atm#1(Zr)_wfc#5(d)')
    _, c_2p = read_ldos('zrclscc.pdos_atm#2(C)_wfc#2(p)')
    _, cl1_3p = read_ldos('zrclscc.pdos_atm#3(Cl)_wfc#2(p)')
    _, cl2_3p = read_ldos('zrclscc.pdos_atm#4(Cl)_wfc#2(p)')
    _, sc1_3d = read_ldos('zrclscc.pdos_atm#5(Sc)_wfc#4(d)')
    _, sc2_3d = read_ldos('zrclscc.pdos_atm#6(Sc)_wfc#4(d)')
    tot_arr = np.loadtxt(pdos_dir / 'zrclscc.pdos_tot', comments='#')

    return e_grid, {
        'Total': tot_arr[:, 1],
        'Zr-4d': zr_4d,
        'Sc-3d': sc1_3d + sc2_3d,
        'C-2p': c_2p,
        'Cl-3p': cl1_3p + cl2_3p,
    }


def parse_zrcl2_bxsf() -> tuple[float, np.ndarray, np.ndarray, dict[int, np.ndarray]]:
    bxsf_path = ZR_DIR / 'FS' / 'zrclscc_fs.bxsf'
    lines = [l.strip() for l in bxsf_path.read_text().splitlines() if l.strip()]
    ef = 0.3154
    for l in lines[:20]:
        if 'Fermi Energy:' in l:
            ef = float(l.split(':')[1].strip())
            break

    b_idx = [i for i, l in enumerate(lines) if l.startswith('BEGIN_BANDGRID_3D')][0]
    nx, ny, nz = [int(x) for x in lines[b_idx + 2].split()]
    b1 = np.array([float(x) for x in lines[b_idx + 4].split()[:2]])
    b2 = np.array([float(x) for x in lines[b_idx + 5].split()[:2]])

    bands: dict[int, np.ndarray] = {}
    ptr = b_idx + 7
    while ptr < len(lines):
        line = lines[ptr]
        if line.startswith('BAND:'):
            b_num = int(line.split(':')[1].strip())
            ptr += 1
            vals: list[float] = []
            while ptr < len(lines) and not lines[ptr].startswith('BAND:') and not lines[ptr].startswith('END_BANDGRID_3D'):
                vals.extend([float(x) for x in lines[ptr].split()])
                ptr += 1
            arr3d = np.array(vals).reshape((nx, ny, nz))
            bands[b_num] = arr3d[:, :, 0] - ef
        else:
            ptr += 1

    return ef, b1, b2, bands


def render_zrcl2_sc2c_electronic() -> None:
    apply_atlas_style()
    k_dist, bands_e, grouped_w = parse_zrcl2_fatbands()
    e_dos, pdos = parse_zrcl2_pdos()
    _, b1, b2, fs_bands = parse_zrcl2_bxsf()

    fig = plt.figure(figsize=(10.2, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.85,
        width_ratios=[1.35, 0.72, 1.15], wspace=0.22
    )
    ax_band = fig.add_subplot(gs[0, 0])
    ax_dos = fig.add_subplot(gs[0, 1], sharey=ax_band)
    ax_fs = fig.add_subplot(gs[0, 2])

    for ax in (ax_band, ax_dos, ax_fs):
        style_axis(ax)

    k_ticks = [k_dist[0], k_dist[50], k_dist[100], k_dist[150]]
    for x in k_ticks[1:-1]:
        ax_band.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    ax_band.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_band.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    for ib in range(bands_e.shape[0]):
        e_curve = bands_e[ib]
        if e_curve.max() < -2.7 or e_curve.min() > 2.2:
            continue
        ax_band.plot(k_dist, e_curve, color='#7d8b9d', lw=0.85, alpha=0.75, zorder=2)

    orb_specs = [
        ('Cl-3p', PALETTE['Amber'], 72.0),
        ('C-2p', PALETTE['Rust'], 85.0),
        ('Sc-3d', PALETTE['Teal'], 92.0),
        ('Zr-4d', PALETTE['Navy'], 96.0),
    ]
    for label, color, scale in orb_specs:
        w_mat = grouped_w[label]
        for ib in range(bands_e.shape[0]):
            e_curve = bands_e[ib]
            if e_curve.max() < -2.6 or e_curve.min() > 2.1:
                continue
            w = w_mat[ib]
            mask = w > 0.04
            if np.any(mask):
                ax_band.scatter(
                    k_dist[mask],
                    e_curve[mask],
                    s=w[mask] * scale,
                    facecolors='none',
                    edgecolors=color,
                    linewidths=0.95,
                    alpha=0.88,
                    zorder=4,
                )

    ax_band.set_xlim(k_ticks[0], k_ticks[-1])
    ax_band.set_ylim(-2.5, 2.0)
    ax_band.set_xticks(k_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_band.set_ylabel(r'Energy $E - E_F$ (eV)')
    ax_band.set_title('Orbital fatbands', pad=8)

    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Navy'], markeredgewidth=1.3, markersize=5.2, label=r'Zr-$4d$ [#1]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Teal'], markeredgewidth=1.3, markersize=5.2, label=r'Sc-$3d$ [#5+#6]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Rust'], markeredgewidth=1.3, markersize=5.2, label=r'C-$2p$ [#2]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Amber'], markeredgewidth=1.3, markersize=5.2, label=r'Cl-$3p$ [#3+#4]'),
    ]
    ax_band.legend(handles=legend_handles, loc='lower left', ncol=2, fontsize=8.0)

    ax_band.annotate(
        'Bands 26, 27\n(Zr-$4d$ [#1] / Sc-$3d$ [#5+#6])',
        xy=(k_dist[24], 0.04),
        xytext=(k_dist[8], 0.92),
        fontsize=8.0, zorder=10,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.8),
    )

    mask_dos = (e_dos >= -2.6) & (e_dos <= 2.1)
    ed = e_dos[mask_dos]
    ax_dos.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_dos.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    ax_dos.fill_betweenx(ed, 0, pdos['Total'][mask_dos], color='#dfe6ef', alpha=0.55)
    ax_dos.plot(pdos['Total'][mask_dos], ed, color=PALETTE['Ink'], lw=1.05, label='Total')
    ax_dos.plot(pdos['Zr-4d'][mask_dos], ed, color=PALETTE['Navy'], lw=1.1, label=r'Zr-$4d$ [#1]')
    ax_dos.plot(pdos['Sc-3d'][mask_dos], ed, color=PALETTE['Teal'], lw=1.1, label=r'Sc-$3d$ [#5+#6]')
    ax_dos.plot(pdos['C-2p'][mask_dos], ed, color=PALETTE['Rust'], lw=1.05, label=r'C-$2p$ [#2]')
    ax_dos.plot(pdos['Cl-3p'][mask_dos], ed, color=PALETTE['Amber'], lw=0.95, label=r'Cl-$3p$ [#3+#4]')

    ax_dos.set_xlim(0, 6.8)
    ax_dos.set_xticks([0, 3, 6])
    ax_dos.set_xlabel('PDOS (eV$^{-1}$)')
    ax_dos.set_title('PDOS', pad=8)
    ax_dos.tick_params(labelleft=False)

    B = np.column_stack([b1, b2])
    B_inv = np.linalg.inv(B)
    angles = np.deg2rad(np.arange(0, 360, 60))
    R_k = 2.0 / 3.0
    bz_verts = np.column_stack([R_k * np.cos(angles), R_k * np.sin(angles)])

    nx = 220
    kx_lin = np.linspace(-0.75, 0.75, nx)
    ky_lin = np.linspace(-0.75, 0.75, nx)
    KX, KY = np.meshgrid(kx_lin, ky_lin)
    uv = B_inv @ np.vstack([KX.ravel(), KY.ravel()])
    u_mod = np.mod(uv[0], 1.0) * 64.0
    v_mod = np.mod(uv[1], 1.0) * 64.0

    def interp_periodic(grid65: np.ndarray) -> np.ndarray:
        i0 = np.floor(u_mod).astype(int) % 64
        j0 = np.floor(v_mod).astype(int) % 64
        i1 = (i0 + 1) % 64
        j1 = (j0 + 1) % 64
        du = u_mod - np.floor(u_mod)
        dv = v_mod - np.floor(v_mod)
        val = (
            (1 - du) * (1 - dv) * grid65[i0, j0]
            + du * (1 - dv) * grid65[i1, j0]
            + (1 - du) * dv * grid65[i0, j1]
            + du * dv * grid65[i1, j1]
        )
        return val.reshape(KX.shape)

    E26 = interp_periodic(fs_bands[26])
    E27 = interp_periodic(fs_bands[27])

    m_angles = np.deg2rad([30.0, 90.0, 150.0])
    inside_bz = np.ones_like(KX, dtype=bool)
    for ang in m_angles:
        inside_bz &= np.abs(KX * np.cos(ang) + KY * np.sin(ang)) <= (1.0 / np.sqrt(3.0) + 0.004)

    E26_masked = np.where(inside_bz, E26, np.nan)
    E27_masked = np.where(inside_bz, E27, np.nan)

    ax_fs.contourf(
        KX, KY, E26_masked,
        levels=np.linspace(-0.6, 0.4, 22),
        cmap='Blues_r', alpha=0.25, zorder=1,
    )
    ax_fs.contour(KX, KY, E26_masked, levels=[0.0], colors=[PALETTE['Navy']], linewidths=1.85, zorder=4)
    ax_fs.contour(KX, KY, E27_masked, levels=[0.0], colors=[PALETTE['Rust']], linewidths=1.85, zorder=5)

    bz_poly = Polygon(bz_verts, closed=True, fill=False, edgecolor=PALETTE['Ink'], lw=1.2, zorder=6)
    ax_fs.add_patch(bz_poly)

    gamma_pt = np.array([0.0, 0.0])
    m_pt = np.array([0.5, 1.0 / (2.0 * np.sqrt(3.0))])
    k_pt = np.array([1.0 / 3.0, 1.0 / np.sqrt(3.0)])
    path_pts = np.vstack([gamma_pt, m_pt, k_pt, gamma_pt])
    ax_fs.plot(path_pts[:, 0], path_pts[:, 1], color=PALETTE['Slate'], ls='--', lw=0.95, zorder=6)
    ax_fs.scatter([gamma_pt[0], m_pt[0], k_pt[0]], [gamma_pt[1], m_pt[1], k_pt[1]], color=PALETTE['Ink'], s=16, zorder=7)
    ax_fs.text(-0.07, -0.08, r'$\Gamma$', fontsize=8.5, fontweight='bold')
    ax_fs.text(m_pt[0] + 0.03, m_pt[1] - 0.02, r'$M$', fontsize=8.5, fontweight='bold')
    ax_fs.text(k_pt[0] + 0.02, k_pt[1] + 0.03, r'$K$', fontsize=8.5, fontweight='bold')

    fs_handles = [
        Line2D([0], [0], color=PALETTE['Navy'], lw=1.8, label='Band 26'),
        Line2D([0], [0], color=PALETTE['Rust'], lw=1.8, label='Band 27'),
    ]
    ax_fs.legend(handles=fs_handles, loc='lower center', ncol=2, fontsize=8.0)
    ax_fs.set_aspect('equal')
    ax_fs.set_xlim(-0.74, 0.74)
    ax_fs.set_ylim(-0.74, 0.74)
    ax_fs.set_xticks([-0.5, 0.0, 0.5])
    ax_fs.set_yticks([-0.5, 0.0, 0.5])
    ax_fs.set_xlabel(r'$k_x$ ($2\pi/a$)')
    ax_fs.set_ylabel(r'$k_y$ ($2\pi/a$)')
    ax_fs.set_title('2D Fermi surface', pad=8)

    save_figure(fig, 'zrcl2-sc2c-electronic')


def parse_gam_lines(filepath: Path, target_broadening: float = 0.0030) -> np.ndarray:
    text = filepath.read_text()
    blocks = re.split(r'Broadening\s+([\d.]+)', text)[1:]
    for i in range(0, len(blocks), 2):
        bval = float(blocks[i])
        if abs(bval - target_broadening) < 1e-5:
            lines = [l.strip() for l in blocks[i + 1].strip().splitlines() if l.strip()]
            gam = np.zeros((151, 18))
            ptr = 0
            for iq in range(151):
                ptr += 1
                vals = []
                while len(vals) < 18 and ptr < len(lines):
                    vals.extend([float(x) for x in lines[ptr].split()])
                    ptr += 1
                gam[iq] = np.maximum(0.0, np.array(vals[:18]) * 1000.0)
            return gam
    raise ValueError(f'Broadening {target_broadening} not found in {filepath}')


def render_zrcl2_sc2c_phonon_epc() -> None:
    apply_atlas_style()
    ph96_dir = ZR_DIR / 'ph96'
    freq_arr = np.loadtxt(ph96_dir / 'zrclscc.freq.gp')
    q_dist = freq_arr[:, 0]
    freqs_thz = freq_arr[:, 1:] * CM1_TO_THZ

    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)
    ry_to_thz = 3289.84196
    nef_003 = 30.772452
    w_ry = np.maximum(freqs_thz, 0.25) / ry_to_thz
    g_ry = (gam_qv / 1000.0) / ry_to_thz
    lam_qv = np.where(freqs_thz > 0.25, g_ry / (np.pi * nef_003 * (w_ry ** 2)), 0.0)

    phdos_arr = np.loadtxt(ph96_dir / 'zrclscc.phdos', comments='#')
    w_dos_thz = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    phdos_tot = phdos_arr[:, 1] * dos_scale
    phdos_zr = phdos_arr[:, 2] * dos_scale
    phdos_c = phdos_arr[:, 3] * dos_scale
    phdos_cl = (phdos_arr[:, 4] + phdos_arr[:, 5]) * dos_scale
    phdos_sc = (phdos_arr[:, 6] + phdos_arr[:, 7]) * dos_scale

    a2f_lines = (ph96_dir / 'alpha2F.dat').read_text().splitlines()[2:]
    e_a2f, a2f_003, a2f_001 = [], [], []
    for idx in range(0, len(a2f_lines), 2):
        r1 = [float(x) for x in a2f_lines[idx].split()]
        e_a2f.append(r1[0])
        a2f_001.append(max(0.0, r1[1]))
        a2f_003.append(max(0.0, r1[3]))
    e_a2f = np.array(e_a2f)
    a2f_003 = np.array(a2f_003)
    a2f_001 = np.array(a2f_001)

    de = e_a2f[1] - e_a2f[0]
    cum_lam_003 = np.zeros_like(e_a2f)
    cum_lam_003[1:] = np.cumsum(2.0 * a2f_003[1:] / e_a2f[1:] * de)

    fig = plt.figure(figsize=(10.2, 4.45))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.98, bottom=0.17, top=0.84,
        width_ratios=[1.42, 0.76, 1.02], wspace=0.12
    )
    ax_ph = fig.add_subplot(gs[0, 0])
    ax_pdos = fig.add_subplot(gs[0, 1], sharey=ax_ph)
    ax_a2f = fig.add_subplot(gs[0, 2], sharey=ax_ph)

    for ax in (ax_ph, ax_pdos, ax_a2f):
        style_axis(ax)
        ax.axhline(10.0, color=PALETTE['Coral'], ls='--', lw=1.05, zorder=3)
        ax.axhspan(12.2, 17.3, color=PALETTE['WarmTint'], alpha=0.55, zorder=0)

    q_ticks = [q_dist[0], q_dist[50], q_dist[100], q_dist[150]]
    for x in q_ticks[1:-1]:
        ax_ph.axvline(x, color='#ced8e3', lw=0.85, zorder=1)

    for nu in range(18):
        ax_ph.plot(q_dist, freqs_thz[:, nu], color='#4a5a70', lw=0.9, alpha=0.85, zorder=2)
        g_vals = gam_qv[:, nu]
        l_vals = lam_qv[:, nu]
        idx_sub = np.arange(0, 151, 3)
        sizes = np.clip(l_vals[idx_sub] * 26.0 + g_vals[idx_sub] * 0.14, 4.0, 95.0)
        ax_ph.scatter(
            q_dist[idx_sub],
            freqs_thz[idx_sub, nu],
            s=sizes,
            c=np.clip(g_vals[idx_sub], 0.0, 340.0),
            cmap='YlOrRd',
            vmin=0.0,
            vmax=330.0,
            edgecolors='#2b3a4d',
            linewidths=0.3,
            alpha=0.84,
            zorder=4,
        )

    ax_ph.set_xlim(q_ticks[0], q_ticks[-1])
    ax_ph.set_ylim(0.0, 18.0)
    ax_ph.set_xticks(q_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_ph.set_ylabel(r'Frequency $\omega$ (THz)')
    ax_ph.set_title(r'Fat-phonon $\gamma_{\mathbf{q}\nu}$ & $\lambda_{\mathbf{q}\nu}$', pad=8)

    ax_ph.annotate(
        r'C-atom optical modes ($\nu=16\text{–}18$): $\gamma_{\Gamma,17\text{–}18}\approx 322\ \mathrm{GHz}$',
        xy=(q_dist[8], 15.45),
        xytext=(q_dist[10], 11.20),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.95),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_ph.text(
        q_dist[54], 9.05,
        'Saved input emax = 10 THz',
        fontsize=7.5,
        color=PALETTE['Coral'],
        fontweight='bold',
    )

    ax_pdos.fill_betweenx(w_dos_thz, 0, phdos_tot, color='#dfe6ef', alpha=0.55)
    ax_pdos.plot(phdos_tot, w_dos_thz, color=PALETTE['Ink'], lw=1.0, label='Total')
    ax_pdos.plot(phdos_zr, w_dos_thz, color=PALETTE['Navy'], lw=1.1, label='Zr')
    ax_pdos.plot(phdos_sc, w_dos_thz, color=PALETTE['Teal'], lw=1.1, label='Sc')
    ax_pdos.plot(phdos_cl, w_dos_thz, color=PALETTE['Amber'], lw=1.0, label='Cl')
    ax_pdos.plot(phdos_c, w_dos_thz, color=PALETTE['Rust'], lw=1.2, label='C')

    ax_pdos.set_xlim(0, 3.8)
    ax_pdos.set_xticks([0, 1.5, 3.0])
    ax_pdos.set_xlabel('PHDOS (THz$^{-1}$)')
    ax_pdos.set_title('PHDOS', pad=8)
    ax_pdos.tick_params(labelleft=False)
    ax_pdos.legend(loc='center right', fontsize=7.8)

    ax_a2f.fill_betweenx(e_a2f, 0, a2f_003, color=PALETTE['SoftBlue'], alpha=0.72)
    ax_a2f.plot(a2f_003, e_a2f, color=PALETTE['Navy'], lw=1.35, label=r'$\alpha^2F$ ($\sigma=0.003$)')
    ax_a2f.plot(a2f_001, e_a2f, color=PALETTE['Blue'], lw=0.85, ls=':', alpha=0.85, label=r'$\alpha^2F$ ($\sigma=0.001$)')
    lam_scale = 0.36
    ax_a2f.plot(cum_lam_003 * lam_scale, e_a2f, color=PALETTE['Rust'], lw=1.65, label=r'$0.36\times \lambda(\omega)$')

    ax_a2f.set_xlim(0, 1.05)
    ax_a2f.set_xticks([0.0, 0.4, 0.8])
    ax_a2f.set_xlabel(r'$\alpha^2F(\omega)$ & scaled $\lambda(\omega)$')
    ax_a2f.set_title(r'Saved $\alpha^2F(\omega)$ (emax = 10 THz)', pad=8)
    ax_a2f.tick_params(labelleft=False)

    ax_a2f.text(
        0.22, 13.3,
        'Input: 10 0.12 1\n18-THz output provenance open',
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )
    ax_a2f.legend(loc='center right', bbox_to_anchor=(1.0, 0.36), fontsize=7.6)

    save_figure(fig, 'zrcl2-sc2c-phonon-epc')


def load_zrcl2_lambda_series(tag: str, suffix: str = '') -> dict[str, np.ndarray]:
    base = ZR_DIR / tag
    dat_file = base / (f'lambda{suffix}.dat')
    out_file = base / (f'lambdax{suffix}.out')
    arr = np.loadtxt(dat_file, comments='#')
    lines = out_file.read_text().splitlines()
    tc_idx = [i for i, l in enumerate(lines) if 'omega_log' in l and 'T_c' in l][0] + 1
    tc_vals = [float(lines[tc_idx + i].split()[2]) for i in range(arr.shape[0])]
    return {
        'sigma': arr[:, 0],
        'lambda': arr[:, 1],
        'int_a2f': arr[:, 2],
        'wlog': arr[:, 3],
        'nef': arr[:, 4],
        'tc': np.array(tc_vals),
    }


def render_zrcl2_sc2c_k64_k96_tc() -> None:
    apply_atlas_style()
    p64_10 = load_zrcl2_lambda_series('ph64', '')
    p96_10 = load_zrcl2_lambda_series('ph96', '')
    p64_18 = load_zrcl2_lambda_series('ph64', '.emax18')
    p96_18 = load_zrcl2_lambda_series('ph96', '.emax18')
    sigma = p64_10['sigma']
    write_report(ZR_DIR)
    roots10 = piecewise_linear_crossings(sigma, p64_10['tc'], p96_10['tc'])
    roots18 = piecewise_linear_crossings(sigma, p64_18['tc'], p96_18['tc'])

    fig, (ax_tc, ax_diff) = plt.subplots(1, 2, figsize=(10.0, 4.35))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax_tc)
    style_axis(ax_diff)

    for ax in (ax_tc, ax_diff):
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.72, zorder=0)
        ax.set_xticks([0.005, 0.010, 0.015, 0.020])

    ax_tc.plot(sigma, p64_18['tc'], color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.6, label=r'$64^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p96_18['tc'], color=PALETTE['Rust'], marker='s', ms=3.6, lw=1.6, label=r'$96^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p64_10['tc'], color=PALETTE['Navy'], ls='--', lw=1.05, alpha=0.7, label=r'$64^2$ matched 10-THz input')
    ax_tc.plot(sigma, p96_10['tc'], color=PALETTE['Rust'], ls='--', lw=1.05, alpha=0.7, label=r'$96^2$ matched 10-THz input')

    for i, root in enumerate(roots10):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], marker='^', s=42, color=PALETTE['Amber'], zorder=6, label='10-THz table roots' if i == 0 else None)
    for i, root in enumerate(roots18):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], s=58, facecolors='none', edgecolors=PALETTE['Teal'], linewidths=1.8, zorder=7, label='18-THz stored-table root (source open)' if i == 0 else None)
    if roots18:
        root = roots18[0]
        ax_tc.annotate(
            f"Stored 18-THz table\n$\\sigma={root['sigma_ry']:.6f}$ Ry, $T_c={root['tc_k']:.3f}$ K\ninput/run record unlinked",
            xy=(root['sigma_ry'], root['tc_k']),
            xytext=(0.0062, 11.6),
            fontsize=7.7,
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
            arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
        )

    ax_tc.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_tc.set_ylabel(r'Stored Allen–Dynes $T_c(\sigma)$ (K)')
    ax_tc.set_title(r'Stored $T_c$ tables and interpolated roots', pad=8)
    ax_tc.legend(loc='upper right', fontsize=7.4)

    dtc_18 = p64_18['tc'] - p96_18['tc']
    dtc_10 = p64_10['tc'] - p96_10['tc']
    ax_diff.axhline(0.0, color=PALETTE['Ink'], ls='-', lw=0.95, zorder=2)
    ax_diff.plot(sigma, dtc_18, color=PALETTE['Teal'], marker='o', ms=3.8, lw=1.6, label=r'$\Delta T_c$ (18-THz stored tables)')
    ax_diff.plot(sigma, dtc_10, color=PALETTE['Amber'], marker='^', ms=3.6, lw=1.35, ls='--', label=r'$\Delta T_c$ (matched 10-THz inputs)')
    for root in roots10:
        ax_diff.scatter([root['sigma_ry']], [0.0], marker='^', color=PALETTE['Amber'], s=42, zorder=6)
    for root in roots18:
        ax_diff.scatter([root['sigma_ry']], [0.0], color=PALETTE['Teal'], s=48, zorder=7)
    ax_diff.text(
        0.035, 0.055,
        'Prepared ph64.1/ph96.1\nrefinement has no complete Tc pair',
        transform=ax_diff.transAxes,
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )

    ax_diff.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_diff.set_ylabel(r'$\Delta T_c(\sigma) = T_{c,64} - T_{c,96}$ (K)')
    ax_diff.set_title(r'Linear-interpolation roots of $\Delta T_c=0$', pad=8)
    ax_diff.set_ylim(-0.135, 0.155)
    ax_diff.legend(loc='upper right', fontsize=7.4)

    save_figure(fig, 'zrcl2-sc2c-k64-k96-tc')


def render_zrcl2_sc2c_k64_k96_moments() -> None:
    apply_atlas_style()
    p64 = load_zrcl2_lambda_series('ph64', '')
    p96 = load_zrcl2_lambda_series('ph96', '')
    sigma = p64['sigma']

    fig, (ax_nef, ax_lam, ax_wlog) = plt.subplots(1, 3, figsize=(10.4, 4.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.18, top=0.85, wspace=0.31)
    for ax in (ax_nef, ax_lam, ax_wlog):
        style_axis(ax)
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
        ax.set_xticks([0.005, 0.012, 0.020])

    ax_nef.plot(sigma, p64['nef'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64\times 64\times 1$')
    ax_nef.plot(sigma, p96['nef'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96\times 96\times 1$')
    ax_nef.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_nef.set_ylabel(r'$N_\sigma(E_F)$ (states/spin/Ry)')
    ax_nef.set_title(r'$N_\sigma(E_F)$ from stored tables', pad=8)
    ax_nef.legend(loc='upper right', fontsize=7.6)
    ax_nef.annotate(
        'Close for $\\sigma\\geq0.004$ Ry\n(two grids; no convergence proof)',
        xy=(0.004, p64['nef'][3]),
        xytext=(0.0075, 28.5),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_lam.plot(sigma, p64['lambda'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ direct $\lambda$')
    ax_lam.plot(sigma, p96['lambda'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ direct $\lambda$')
    ax_lam.plot(sigma, p64['int_a2f'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.75, label=r'$64^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.plot(sigma, p96['int_a2f'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.75, label=r'$96^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_lam.set_ylabel(r'Coupling $\lambda(\sigma)$')
    ax_lam.set_title(r'10-THz input: $\lambda$ and $\int\alpha^2F$', pad=8)
    ax_lam.legend(loc='upper right', fontsize=7.2)

    ax_wlog.plot(sigma, p64['wlog'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ (10-THz input)')
    ax_wlog.plot(sigma, p96['wlog'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ (10-THz input)')
    ax_wlog.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_wlog.set_ylabel(r'$\omega_{\log}(\sigma)$ (K)')
    ax_wlog.set_title(r'Stored $\omega_{\log}$ (10-THz input)', pad=8)
    ax_wlog.legend(loc='upper left', fontsize=7.2)
    ax_wlog.text(
        0.04, 0.04,
        'Frequency grid ends at 10 THz',
        transform=ax_wlog.transAxes,
        fontsize=7.3,
        color=PALETTE['Muted'],
    )

    save_figure(fig, 'zrcl2-sc2c-k64-k96-moments')


if __name__ == '__main__':
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
```

</details>

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 的轨道胖带、水平 PDOS 与二维六角第一布里渊区费米面（Band 26 与 Band 27）" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构与二维费米面（子图 c）三联图。子图 c 由 <code>FS/zrclscc_fs.bxsf</code>（<code>64×64×1</code> k 网格，<code>65×65×2</code> 节点，<code>E_F = 0.3154 eV</code>）在六角形第一布里渊区中插值绘制 Band 26（蓝色）和 Band 27（橙红色）等能线。</figcaption></figure>

## 文献中的相关图件与表达方式

在二维与层状材料文献中，费米面与等能面图件常用于展示鞍点分界线（Separatrix）以及三维体态/表面态与角分辨光电子能谱（ARPES）的动量切面对照：

### 1. 二维六角布里渊区等能线与穿过六个鞍点的分界线

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_2DContour_SixSaddleVHS_In2Te2_Zolyomi2014_Fig4.jpg" alt="单层 In₂Te₂ 价带在二维六角布里渊区内的能量等高线与穿过六个鞍点的红色粗实线分界线" loading="lazy"/><figcaption>单层 In₂Te₂ 价带在二维六角第一布里渊区内的纯等高线图（Contour lines），红色粗实线标出穿过围绕 Γ 点对称分布的六个鞍点（Saddle Points）的等能分界线。图片来源：Zólyomi, Drummond, and Fal'ko, <em>Phys. Rev. B</em> <strong>89</strong>, 205426 (2014), Fig. 4，<a href="https://doi.org/10.1103/PhysRevB.89.205426" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.89.205426</a>。</figcaption></figure>

在二维六角第一布里渊区内绘制密集的纯等能线，并用红色粗实线高亮经过六个对称鞍点的临界等能线（Separatrix），可以清楚展示等能面从围绕 Γ 的闭合环向围绕 K 的口袋转变的 Lifshitz 拓扑边界。

### 2. 三维费米面、表面态计算谱与 ARPES 实验等能切面对照

<figure class="research-figure"><img src="/Atlas/figures/literature/M7_SurfaceStates_3DVHS_ARPES_ZrAs2_Fig4.jpg" alt="ZrAs₂ 的三维费米面、表面态与体态计算等能切面及 ARPES 实验强度对照图" loading="lazy"/><figcaption>将第一性原理计算的费米面/等能面切面、<code>k_z</code> 色散与角分辨光电子能谱（ARPES）实验强度图并排对齐，标出表面态与体态在动量空间中的轨迹。图片来源：<em>Nat. Commun.</em> <strong>16</strong>, 2831 (2025), Fig. 4，<a href="https://doi.org/10.1038/s41467-025-58024-w" target="_blank" rel="noopener noreferrer">DOI: 10.1038/s41467-025-58024-w</a>。</figcaption></figure>

与实验 ARPES 对比时，理论计算的二维等能面切面采用与实验一致的动量坐标单位（`Å⁻¹`），将计算能带等能线与实验光电子强度分布并排或半侧叠放，便于区分体态投影与表面态贡献。

下一步到 [费米面嵌套](/Atlas/m/fermi-nesting/qe/) 看怎样将这些真实网格变成 J(q)，以及为什么几何面看起来能重合，不等于已经算出了电荷密度波或超导。

```text
同一结构 SCF → 全布里渊区 NSCF → 本征值/坐标逐点检查
                                       ↓
                       Eₙ(k) − E_F = 0 → 截面 / 三维费米面
                                       └→ 费米面几何嵌套 J(q)
```
