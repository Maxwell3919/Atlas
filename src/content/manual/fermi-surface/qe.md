二维界面中穿越费米能的分支，在完整倒空间里形成哪些等能轮廓？Al 的三维网格保留作点阵重建基础，ZrCl₂/Sc₂C 的二维 BXSF 展示材料的费米等能线。层来源仍须读对应波函数的投影。

Al 哪些能带穿过费米能，它们在倒空间中形成怎样的连续等能面？本页逐带提取这些面，并用两套完整网格比较其截面。能带图沿一条路径画出电子能量。费米面则在整个三维倒空间里寻找满足 Eₙ(k)=E_F 的位置：一条能带可以贡献一个电子口袋、一个空穴口袋，也可能穿过倒空间单元的边界。只沿高对称线做一次能带计算，没有足够信息画这张面。

[Ba₂N 原文 Fig. 2(a,c)](https://doi.org/10.1103/PhysRevB.105.165101)将穿越费米能的分支与二维口袋配对。下面 Al 先练习完整三维网格的等能面提取，图的颜色区分能带；没有计算费米速度着色。

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

检查符号范围是寻找候选穿越带的第一步。随后程序需要对每条带分别恢复三维数组，检查相邻格点的 $E_n-E_F$ 是否跨过零，才在这些网格单元中插值得到面。若先把六条带的能量混成一个数组，几何算法会把不同带之间的能量跳跃也当成等值面。带号应一路保留到最终图例。

这里的k₃=0截面固定的是第三个倒格矢分数坐标；对于fcc的非正交原胞，不能默认把它叫作笛卡尔k_z=0。看形状时先读坐标基，再比较实线与虚线的位置；若要讨论速度，必须对物理笛卡尔波矢求梯度，当前按带号上色的图没有给出这一量。

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

在 **`ZrCl₂/Sc₂C`**（[完整计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，[`FS/zrclscc_fs.bxsf`](/Atlas/examples/zrcl2-sc2c/FS/zrclscc_fs.bxsf) 对应 `64 × 64 × 1` k 网格（包含 `65 × 65 × 2` 个 BXSF 网格节点，保存第 `25–29` 共 5 条能带，`E_F = 0.3154 eV`），其中穿过费米能级的是 **Band 26** 与 **Band 27**。

65×65×2是文件为周期绘图写出的节点数，64×64×1才是独立采样数。分数坐标0与1是相同周期位置；第三方向的两层节点也是一个采样层的周期副本，不能解读成已经检查了两个不同k_z截面。处理时先验证边界副本一致，再平铺数据以穿过原胞边界，最后裁剪第一BZ。平铺改善几何连接，没有增加物理采样。

文件只保留第25–29带，因此“26、27穿越”是对这五条带的核对。要声明所有费米分支均已列出，还需回到完整本征值输出，检查带号范围以外没有其他穿越带；BXSF的这五个块本身不能完成这个检查。如果直接在分数坐标 `[0, 1] × [0, 1]` 的菱形周期元胞上画等值线，Γ 点会落在四个角上，不便观察围绕 Γ 与 K 的六角对称性。在 [`plot_zrcl2_sc2c.py`](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py) 中，后处理步骤为：
1. 利用周期性将网格平铺扩展，并按平面倒格基矢变换到笛卡尔倒空间 `(k_x, k_y)`；
2. 构造六角形 Wigner–Seitz 第一布里渊区边界（顶点为 6 个 K/K' 点，边中点为 6 个 M 点），将 `E_n(k_x, k_y) = E_F` 的等能线裁剪在第一布里渊区内；
3. 在 `zrcl2-sc2c-electronic.png` 的子图 **c** 中绘制 **Band 26**（蓝色）与 **Band 27**（橙红色）的费米面轮廓，并与子图 **a** 的轨道胖带、子图 **b** 的水平 PDOS 对照展示：

[电子结构三联图的完整绘图源码](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)保留逐态投影、PDOS 归并及 BXSF 读取规则。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 的轨道胖带、水平 PDOS 与二维六角第一布里渊区费米面（Band 26 与 Band 27）" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构与二维费米面（子图 c）三联图。子图 c 由 <code>FS/zrclscc_fs.bxsf</code>（<code>64×64×1</code> k 网格，<code>65×65×2</code> 节点，<code>E_F = 0.3154 eV</code>）在六角形第一布里渊区中插值绘制 Band 26（蓝色）和 Band 27（橙红色）等能线。</figcaption></figure>

先在子图 c 辨认第 26 与第 27 带各自的轮廓，再回到子图 a 看 Γ–M–K–Γ 沿线与轮廓的交点。子图 c 使用 BXSF 自身 E_F=0.3154 eV，路径图使用父 SCF 的 0.3133 eV，二者相差 0.0021 eV；在这种不同采样下，不把视觉重合当成精确一一配对。路径交点的 Sc-d/Zr-d 数字见[胖带交点表](/Atlas/m/fatband/qe/#h-在费米交点读取同一个态的层来源)。该表属于路径波函数，不能将它直接涂满整条费米轮廓。

BXSF 给出了单个历史 +1.5% 状态的费米等能线，支持说明哪些带在这套模型里有金属态。仅凭这张等能线不决定电子口袋/空穴口袋符号；还需检查轮廓内外 E−E_F 的正负，也不由口袋存在推断哪层主导超导配对。


## 从等能口袋回到近费米态

[Ba₂N 原文 PDF 第3页 Fig. 2(a,c)](https://doi.org/10.1103/PhysRevB.105.165101)并列同一材料的路径色散与六角BZ内费米口袋：(a)以实/虚线比较无SOC与SOC，显示两条分支穿过零能；(c)分别显示相关轮廓，正文将Γ和M附近口袋判为电子型。判断类型还要读轮廓内外能量/占据，不能只凭闭合线形；再联读(b)轨道DOS与(d)ELF，才讨论原子及无核区域来源。

复现(c)需要完整BZ本征值网格。本站真实BXSF可由XCrySDen读取，核对文件头EF、倒格矢和带号后按第一BZ看等能面；二维对照固定同一k_z切面，分别保留两条穿越带并记录视角与参考。本站三联图c已按周期平铺、笛卡尔倒格变换和六角Wigner–Seitz裁剪生成，完整源码保留；Al交互图显示原始倒格矢周期单元且有前文说明的边界截断，两者不能当同一种六角图比较。此次不另造费米面，论文Γ/M口袋位置也不移植给本站Band26/27。

比较接触或掺杂前后，应在同一物理倒空间范围和一致能量定义下看口袋是否出现、消失或连接。若晶胞变成超胞，先处理倒空间折叠；若只有刚性平移的 E_F 对照，应明确密度与结构未随之自洽。当前历史 BXSF 仅提供一个状态，不显示真实的接触前后口袋演化。

两张口袋图即使外观或围成的面积相近，也未必有相近的近费米 DOS。零温下，电子型口袋内部的低能态已占据；空穴型口袋内部则是相对于满带缺少电子的区域。对真正的二维能带，在同一物理倒空间里按整个 BZ 面积归一化，口袋面积才对应这部分电子或空穴的计数；三维能带需要口袋体积，Al 的一个截面面积不能代替它。这个计数涉及口袋内的整个区域，而 [DOS](/Atlas/m/dos/qe/#h-在能量轴上数状态-先用均匀-k-网格)问的是一小段能窗里有多少态：若 DOS 在窗内变化不大，窗宽乘 DOS 才近似为该窗态数；电子数还要乘相应占据。沿用 DOS 页的每计算胞约定，k 权重和取 1 时，无自旋极化、无 SOC 的空间带另计两重自旋；若文件权重或输出已含自旋，就不能再乘 2，SOC 或磁性体系则按实际态逐项计数。

要看出窄窗为什么会有不同权重，可以在同一口袋边界附近沿法向稍微移动物理波矢。如果能量变化快，很薄的一层倒空间区域就跨过这个能窗；如果变化慢，同样的能窗会覆盖较厚的一层，纳入更多 k 态。在色散光滑且梯度不为零的局部，这个厚度近似为 $\Delta k_\perp\simeq\Delta E/|\nabla_{\mathbf k}E_n|$。因此二维 DOS 要沿整条等能线累计这种厚度，三维 DOS 要沿整个等能面累计；只看轮廓围成的面积，或只看三维面的面积，都缺了法向能量变化的信息。带边或临界点附近梯度可能为零，这个局部线性估计不再适用，应回到有限能窗的态数和采样检查。这是从 [Yates 等的 BZ 权重与费米能 δ 窗口定义，式 (2)、(4)、(33)](https://arxiv.org/pdf/cond-mat/0702554)得到的局部几何解释，没有替现有口袋算出 DOS。

这里的梯度对应带群速度 $\mathbf v_n(\mathbf k)=\hbar^{-1}\nabla_{\mathbf k}E_n(\mathbf k)$，见 [Yates 等式 (23)](https://arxiv.org/pdf/cond-mat/0702554#page=5)。其中 k 是具有逆长度单位的物理笛卡尔波矢，倒格矢采用与实格矢点积为 2π 的约定；能量与 ℏ 也要使用一致单位。页面的 k₁、k₂、k₃ 是无量纲倒格矢分数坐标，求导后还须用实际倒格基按链式法则变换，并保留非正交基的尺度与夹角，不能把三个分数坐标导数直接当成速度分量。对真正二维的色散取面内梯度；对 Al 的三维带，仅在 k₃=0 平面看一条线不能恢复完整三维梯度。当前 Al 蓝/橙色只表示带号，二维口袋图也没有提供带速度；两幅图都不足以给出哪一个 DOS 更大的数值判断。

这也说明为何 [Wannier 插值](/Atlas/m/wannier90/qe/)要围绕用途选择目标能区。若要积分近费米态，应先让所选带、投影以及必要的解缠窗口覆盖参与积分的能带，再在独立 DFT 点核对同一能量参考下的局部色散；若还要使用速度，能量点的吻合之外还需检查目标区域的斜率与带连接，尤其是交叉、避交叉附近。现有 Si 对照只检查四条价带的有限路径点，不提供金属费米速度证据；[Al 的能带与插值检查](/Atlas/m/epw-eliashberg/qe/#h-声学模和插值质量怎样核对)也不能从路径吻合扩大成整个费米面的速度误差结论。加密细积分网格会更密地采样已有插值函数，目标能区若仍有偏差，还需回到电子粗网格、投影与窗口，而不是把细网格密度当成修复。

带速度较慢带来的窄窗权重仍只是电子态这一层。给定 q 后，[几何联合权重 J(q)](/Atlas/m/fermi-nesting/qe/)把 k 与 k+q 两端的近费米权重相乘并求和，还没有区分声子模式。要继续读 [逐模线宽](/Atlas/m/phonon-linewidth/qe/)与 [EPC 插值](/Atlas/m/epw-eliashberg/qe/)，还需同一父链的位移势响应、电子–声子矩阵元和声子频率、本征位移：[QE 的线宽定义，式 (1)–(3)](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)在双费米窗口中保留矩阵元平方，逐模 λ 又涉及频率平方和费米能 DOS 的归一化。本站 Al 的 J(q) 与模式数据要先对齐结构、q、电子窗口和自旋约定，不能直接相除来反推矩阵元。因而口袋相似、DOS 较大或局部速度较慢，都不足以单独排序模式耦合，也不能据此判定软模或配对机制。

口袋由哪层贡献要回读[逐态投影](/Atlas/m/fatband/qe/)或在完整 k 网格上计算分层权重；几何面积需要按自旋、简并、电子/空穴符号及整个二维 BZ 的归一化计数，才可能讨论自由载流子。空间电荷转移的积分采用另一种定义。只有当具体 q 散射问题需要它时，才接[费米面嵌套](/Atlas/m/fermi-nesting/qe/)；口袋之间看起来能平移重合，还没有给出 EPC 矩阵元。

```text
同一结构 SCF → 全布里渊区 NSCF → 本征值/坐标逐点检查
                                       ↓
                       Eₙ(k) − E_F = 0 → 截面 / 三维费米面
                                       └→ 费米面几何嵌套 J(q)
```


<figure>
<div>
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig2ac.png" alt="Qiu2022原文Fig.2(a,c)：以 E_F=0 的路径能带和两个分支的二维费米轮廓定位穿越零能的电子态。" />
</div>
<figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，第 3 页 Fig. 2(a,c)：以 E_F=0 的路径能带和两个分支的二维费米轮廓定位穿越零能的电子态。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文原文</a>。</figcaption>
</figure>

原图(a)的红虚线/蓝实线比较 SOC 与无 SOC，零能处的穿越分支在(c)中接到完整二维倒空间的口袋。沿 Γ–M–K–Γ 的几条穿越线只是路径采样；(c)分别展示分支轮廓，才能识别口袋所在区域。本站 Al 三维面的蓝/橙色仍只区分第2/3带；它不是论文材料或费米速度着色。
