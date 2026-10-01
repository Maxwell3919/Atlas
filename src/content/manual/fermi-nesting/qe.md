在应变下发现某个有限 q 的声子软化后，可以先问：这个 q 是否连接了较多费米能附近的电子态？完整 k 网格上的几何联合权重 J(q) 能量化这一线索。这里用真实 Al 的 24³/32³ NSCF 展示周期求和及窗口敏感性，随后说明怎样与二维异质结的声子/EPC 对照。

这个计算用于寻找值得进一步检查的散射波矢，并观察候选峰是否随采样与能量窗口移动。[Johannes 与 Mazin 的 Sec. II、Fig. 4（arXiv PDF 第 6 页）](https://arxiv.org/pdf/0708.1744)比较 TaSe₂ 的几何嵌套与电子响应：费米面的几何重叠峰不能代替完整的电荷响应峰。本页保留 Al 的几何联合权重定义，若要研究某个软模，还需把相同 q 处的声子与 EPC 数据接上。

这里从 [费米面](/Atlas/m/fermi-surface/qe/) 已完成本征值检查的 Al 24³/32³ NSCF 继续。SCF 和 NSCF 不再重复；需要的是该页保存的 `fermi-grid.npz`，其中每个格点、每条能带的 $E_n(\mathbf{k})-E_{\mathrm F}$ 都能追到同一份 QE XML。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [Johannes 与 Mazin：费米面嵌套与 CDW](https://doi.org/10.1103/PhysRevB.77.165135)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-electronic-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 先把所计算的量说清楚

我们定义一个归一化高斯窗口 $\delta_\sigma(E)$，宽度 σ 用 eV 表示。把同一 k 点所有带的费米能附近权重相加，记作 W(k)。实际计算的是

$$
\begin{aligned}
\delta_\sigma(E) &= \frac{\exp[-E^2/(2\sigma^2)]}{\sqrt{2\pi}\,\sigma},\\
W(\mathbf{k}) &= \sum_n \delta_\sigma[E_n(\mathbf{k})-E_{\mathrm F}],\\
J(\mathbf{q}) &= \frac{1}{N_k}\sum_{\mathbf{k}}W(\mathbf{k})\,W(\mathbf{k}+\mathbf{q}).
\end{aligned}
$$

所以 J 的单位是 eV⁻²，布里渊区平均采用等权完整网格。本例没有另外乘一个自旋简并因子；这条定义与所有数表保持一致。不同文献的归一化可能不同，比较数值前要先对齐定义。

J(q) 是费米能附近的几何联合权重。静态 Lindhard 易感率还涉及占据数差与能量差，完整响应还可能包含矩阵元；这里没有这些项，因此文件名和纵轴都写 J，不写 χ。

## 确认网格来源，再运行提取和求和

```console
maxwell@maxwell:~/al/fermi/k32-cg$ cat grid-info.json
{
  "kmesh": 32,
  "nks": 32768,
  "fermi_eV": 8.381502717320133,
  "crossing_bands": [
    2,
    3
  ],
  "band_ranges": [
    {
      "band": 1,
      "min_eV": -11.548066959202437,
      "max_eV": -0.8934928889577716
    },
    {
      "band": 2,
      "min_eV": -4.487132561119305,
      "max_eV": 12.944767171883965
    },
    {
      "band": 3,
      "min_eV": -0.3267820822530947,
      "max_eV": 12.94476717329531
    },
    {
      "band": 4,
      "min_eV": 1.3928520531046082,
      "max_eV": 14.105570788518774
    },
    {
      "band": 5,
      "min_eV": 5.798257429908023,
      "max_eV": 16.25759930823918
    },
    {
      "band": 6,
      "min_eV": 9.493962986363178,
      "max_eV": 20.080026299221082
    }
  ],
  "source_xml_sha256": "e8fa22aa590135fc71cf93ab82ac0b52844112240d8a8be195ffe962acb8e46f",
  "nscf_out_sha256": "986abf2e10830fc5cd5cca0b7b56f55854cf5e4c8afaa88a521888f609226ed7",
  "definition": "Energy grid includes all k, no interpolation, E-EF in eV."
}
```
这份摘要记录了 32768 个真实 k 点、E_F、跨过费米能的带号和源 XML 哈希。不能对一条能带路径直接做下面的循环卷积，因为路径上的数组不是一个周期三维均匀网格。

下载包中的 [extract_fermi_electronic.py](/Atlas/examples/al-electronic/fermi/extract_fermi_electronic.py) 会重新读取两套 NSCF 的 XML、标准输出和错误文件，再生成 `fermi-grid.npz` 与四份嵌套 CSV。本机已有 NumPy 时，在解包后的 `al` 根目录执行：

```bash
python3 fermi/extract_fermi_electronic.py
```

下载包把 XML 放在 `fermi/k24-cg/data-file-schema.xml` 和 `fermi/k32-cg/data-file-schema.xml`，提取脚本读取这些外置文件。`.venv/bin/python` 是原执行记录中的环境路径；本机使用 `python3`。重画现有曲线可直接读取四份 CSV。

脚本先检查 XML 点阵，再针对 σ=0.10、0.20 eV 两个窗口计算。此处的 σ 与 SCF 输入中的 `degauss=0.02 Ry` 属于不同阶段，单位也不同；修改后处理窗口不会改变已经计算好的电子电荷密度。

缩小 σ 后，贡献更集中在费米能附近，有限网格可能只剩少量点承担较大权重，结果通常更依赖 k 点采样。增大 σ 会平滑这种离散性，也会把费米能上下更宽范围的态一起计入。因此下面同时比较网格与窗口，判断嵌套时应保留四组对照。

## 同一份定义，用 FFT 与直接求和互相核对

完整网格具有周期性。把 W 的离散 Fourier 变换乘以它的复共轭，再逆变换，就得到周期自相关；最后除以 $N_k$：

```python
weight = np.exp(-0.5*(energies/sigma)**2).sum(axis=3)
weight /= sigma*np.sqrt(2*np.pi)
spectrum = np.fft.fftn(weight)
J = np.fft.ifftn(spectrum.conj()*spectrum).real / Nk
```

实际脚本另外检查 q=0 是否等于 W² 的平均，并对 q=(1/4,0,1/4) 的网格平移做一次直接求和。二者不一致就停止。这个检查验证数值实现和周期索引，没有替代 k 网格收敛。

```console
maxwell@maxwell:~/al/fermi/k32-cg$ head -6 nesting-GX-s0.20.csv
q_fraction_along_b1_plus_b3,J_eV_minus2,J_over_J0
0.000000000000000000e+00,2.820449455834066477e-01,1.000000000000000000e+00
3.125000000000000000e-02,1.074530198570142897e-01,3.809783566046502923e-01
6.250000000000000000e-02,6.208887126318497068e-02,2.201382163922663837e-01
9.375000000000000000e-02,5.844105637735387548e-02,2.072047639657900453e-01
1.250000000000000000e-01,5.256713802710741290e-02,1.863785855774614530e-01
```
第一列是沿 b₁+b₃ 方向的倒空间分数坐标，从 0 到 0.5 对应本例 Γ—X。第二列是原始 J(q)，第三列只是为了便于比较形状所用的 J(q)/J(0)；原始量也保留，避免归一化后看不见幅值变化。

## 把窗口和网格交叉着比较

| 电子网格 | σ / eV | J(Γ) / eV⁻² | J(X) / eV⁻² |
|---|---:|---:|---:|
| 24³ | 0.10 | 0.61975726 | 0.09968022 |
| 24³ | 0.20 | 0.31708865 | 0.06123457 |
| 32³ | 0.10 | 0.53305558 | 0.04490039 |
| 32³ | 0.20 | 0.28204495 | 0.03678119 |

加密网格后，窄窗口的 X 点权重由 0.09968 降到 0.04490 eV⁻²，显示明显的采样敏感性。讨论有限 q 特征前，需要继续交叉比较电子网格与 σ。

<span id="把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
## 周期求和与直接计算对照

下面将 J(q) 的周期求和、FFT 实现与直接求和对照写成后处理任务。输出要保留窗口宽度和归一化，不把几何权重改称完整响应函数。

```text
编写 Al 几何联合权重 J(q) 分析程序，使用 Python 3、NumPy 和 Matplotlib。
输入：24³/32³ 的 fermi-grid.npz，以及 σ=0.10/0.20 eV 四份 nesting-GX-*.csv。列为 q_fraction_along_b1_plus_b3、J_eV_minus2、J_over_J0。
方法：W(k)=sum_n exp[−(En−EF)^2/(2σ²)]/(σ√(2π))；J(q)=mean_k[W(k)W(k+q)]，单位 eV⁻²。以周期 FFT 自相关计算，取 Γ–X，保留原始 J 和 J/J(0)。
检查：J(0)=mean(W²)，q=(1/4,0,1/4) 与直接求和一致；点序、网格/窗口标签、J/J0 起点为 1，对照正文四组 Γ/X 值。
输出：源码、依赖、命令、CSV/JSON、PNG/SVG/PDF，展示网格与窗口敏感性。电子易感率还需占据数差与能量分母。
```

## 后处理源码与运行

完整源码：[extract_fermi_electronic.py](/Atlas/examples/al-electronic/fermi/extract_fermi_electronic.py) · [plot_nesting.py](/Atlas/examples/al-electronic/plot_nesting.py) · [atlas_plot_style.py](/Atlas/examples/al-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

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
<summary>plot_nesting.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
fig,axes=plt.subplots(1,2,figsize=(10.5,4.2),layout="constrained")
for n in [24,32]:
    for sigma in [.10,.20]:
        x=np.loadtxt(r/f"fermi/k{n}-cg/nesting-GX-s{sigma:.2f}.csv",delimiter=",",skiprows=1)
        label=f"{n}³, σ={sigma:.2f} eV"
        for ax,col in zip(axes,[1,2]):ax.plot(x[:,0],x[:,col],"o-",ms=3,lw=1.3,label=label)
for ax in axes:ax.set(xlabel="q = t(b₁+b₃), Γ → X",xlim=(0,.5));ax.grid(alpha=.2)
axes[0].set_ylabel("J(q) (eV⁻²)");axes[1].set_ylabel("J(q) / J(0)");axes[1].legend(frameon=False,fontsize=8)
(r/"figures").mkdir(exist_ok=True)
fig.savefig(r/"figures/fermi-nesting.png",dpi=220);fig.savefig(r/"figures/fermi-nesting.pdf")
```

</details>

解压本页示例包后，在 `al` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 fermi/extract_fermi_electronic.py
python3 plot_nesting.py
```

本例保存的提取运行记录如下：

```console
maxwell@maxwell:~/al/fermi/..$ .venv/bin/python fermi/extract_fermi_electronic.py
k=24^3 nks=13824 EF=8.39793432 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.61975726 J(X)=0.09968022 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.31708865 J(X)=0.06123457 eV^-2; direct-sum check passed
k=32^3 nks=32768 EF=8.38150272 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.53305558 J(X)=0.04490039 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.28204495 J(X)=0.03678119 eV^-2; direct-sum check passed
```

绘图程序读取四份 `nesting-GX-*.csv`，同时画绝对量和归一化曲线。
<figure><img src="/Atlas/examples/al-electronic/figures/fermi-nesting.png" alt="Al Γ到X方向的费米面几何嵌套网格与窗口比较" loading="lazy"/><figcaption>左：原始 J(q)；右：J(q)/J(0)。四条曲线来自两个真实网格与两个后处理窗口。</figcaption></figure>

现有图左侧保留 J(q) 的 eV⁻² 幅值，右侧才除以同组 J(0)；四组在同一 q=t(b₁+b₃) 横轴上比较。右图曲线接近，不代表左图幅值已收敛。要用 gnuplot 复现，下载[完整绘图源码](/Atlas/examples/research-strain-literature/plot_nesting.gnu)，在上面解包得到的 al 根目录执行以下命令。脚本直接读取四份 CSV 的第 1/2/3 列，保留离散点和网格/窗口标签，不插值、不平滑，也不对每组峰值再次归一化。

```bash
gnuplot plot_nesting.gnu
```

<details>
<summary>plot_nesting.gnu 完整源码</summary>

```gnuplot
# Run from the extracted al/ directory: gnuplot plot_nesting.gnu
if (!exists("data_root")) data_root="."
if (!exists("output_path")) output_path="fermi-nesting-gnuplot.png"
set encoding utf8
set datafile separator comma
file(n,s)=sprintf("%s/fermi/k%d-cg/nesting-GX-s%.2f.csv",data_root,n,s)
set terminal pngcairo enhanced font "DejaVu Sans,12" size 1500,600
set output output_path
set multiplot layout 1,2 margins 0.075,0.98,0.17,0.83 spacing 0.10
set xrange [0:0.5]
set yrange [0:*]
set xlabel "q = t(b_1+b_3), Gamma to X"
set grid ytics lc rgb "#dddddd"
set tics nomirror
set key top right font ",10"
set title "(a) Absolute joint weight"
set ylabel "J(q) (eV^{-2})"
plot file(24,0.10) using 1:2 with linespoints lw 1.5 pt 7 ps 0.55 lc rgb "#0072b2" title "24^3, sigma=0.10 eV", \
 file(24,0.20) using 1:2 with linespoints lw 1.5 pt 5 ps 0.55 lc rgb "#d55e00" title "24^3, sigma=0.20 eV", \
 file(32,0.10) using 1:2 with linespoints lw 1.5 pt 9 ps 0.55 lc rgb "#009e73" title "32^3, sigma=0.10 eV", \
 file(32,0.20) using 1:2 with linespoints lw 1.5 pt 11 ps 0.55 lc rgb "#cc79a7" title "32^3, sigma=0.20 eV"
set title "(b) Shape normalized to q=0"
set ylabel "J(q) / J(0)"
plot file(24,0.10) using 1:3 with linespoints lw 1.5 pt 7 ps 0.55 lc rgb "#0072b2" title "24^3, sigma=0.10 eV", \
 file(24,0.20) using 1:3 with linespoints lw 1.5 pt 5 ps 0.55 lc rgb "#d55e00" title "24^3, sigma=0.20 eV", \
 file(32,0.10) using 1:3 with linespoints lw 1.5 pt 9 ps 0.55 lc rgb "#009e73" title "32^3, sigma=0.10 eV", \
 file(32,0.20) using 1:3 with linespoints lw 1.5 pt 11 ps 0.55 lc rgb "#cc79a7" title "32^3, sigma=0.20 eV"
unset multiplot
print "Read the four original CSVs; no interpolation, smoothing or peak normalization beyond stored column3 J/J(0)."
```

</details>

Γ 点对应 J(0)=mean[W²]，即权重场与自身重合的自相关。有限 q 的机制分析接电子响应与声子，超导分析接 [EPC](/Atlas/m/epc/qe/) 和谱函数链条。

## 软化波矢怎样与二维异质结比较

如果 ZrCl₂/Sc₂C 的 K 点出现软支，先将声子 q 写成所用结构的倒格矢分数坐标，再与同一应变态的电子网格对齐。应变会改变倒格矢长度，同一个分数坐标的物理波矢也随之改变。Al 的 q=t(b₁+b₃) 对应它的 Γ—X；不能把该路径或三维网格直接搬到二维六角结构上。

二维计算采用完整面内均匀 k 网格，z 方向的处理与实际模型一致。若启用 SOC 或自旋极化，应保留相应能带和权重约定，不能额外随手乘二。不同应变使用相同窗口 σ 和相当的网格精度，并同时报告原始 J 与 J/J(0)，这样才能判断峰位和幅值怎样变化。Γ 的自相关通常很大，它衡量权重与自身重合，不能作为有限 q 失稳的机制证据。

[Chen、Zhang 与 Zheng，Phys. Rev. B 114, 055413](https://doi.org/10.1103/l89c-t2s4)原文 PDF 第 4 页的 Fig. 2 把同一单层 CoTe₂ 的电子、声子和响应放在一组面板中。(b)的纵轴是 E−EF，蓝/橙投影分别对应 Co-d、Te-p；(c)将同样的轨道权重画到费米线上，色条为 0–1，虚线六角形标出 BZ，双向箭头标的是 (e) 中增强的 q。因此它先用轨道投影识别两个口袋的成分，再检查箭头所连散射是否也出现在响应图中，没有把画出的箭头本身当作矩阵元证据。

(a)在 Γ–M–K–Γ 上画声子，红点大小表示 $\lambda_{\mathbf q\nu}$，不是 Ba₂N Fig. 6(a) 所用的线宽；(d)在扩展二维 BZ 中画最低支 $\omega_{\mathbf q,\nu=1}$，色条单位 meV。(e)是带 EPC 矩阵元的广义静态响应，(f)是去掉矩阵元后的常矩阵元响应，仍含占据差和能量分母，因而都不是本页 J(q)。作者比较的是 (f) 的较宽增强区如何在 (e) 中变成 M–K 附近热点，并与 (d) 的软化位置对应。(e)、(f)各自只标 high/low，不能按颜色相近断言数值相等。该组机制图还明确采用 0.018 Ry 的较大电子展宽来取得正频率；它不是把原正常展宽下的虚频系统验收为稳定。

把这种图法用于异质结，需要在同一倒空间坐标系中准备轨道投影费米线、二维 q 网格和对应模式数据；gnuplot 的二维 pm3d map 可画原网格，叠加 BZ 边界和可核对的 q，而不从曲线截图补造热图。先从本页真实 Al CSV 复现一维 J，再与[费米面](/Atlas/m/fermi-surface/qe/)和[模式线宽](/Atlas/m/phonon-linewidth/qe/)的数据接续，才有条件比较二维峰位。几何权重与模式散射是不同量，不能只画两口袋间的箭头就认定它们负责软化。


现有 ZrCl₂/Sc₂C 费米面展示可以帮助提出候选口袋，但本例没有提取该体系的完整二维 J(q)，也没有闭合口袋到模式的矩阵元归属。本文因此保留 Al 的真实 J(q) 数据与实现，材料讨论接[费米面](/Atlas/m/fermi-surface/qe/)、[声子线宽](/Atlas/m/phonon-linewidth/qe/)及[应变比较](/Atlas/m/strain-doping-scan/qe/)。只有这些同结构、同 q 的证据成立以后，才能判断软化主要来自几何相空间、矩阵元还是两者共同变化。

## 原文中怎样区分几何权重与响应

[Johannes 与 Mazin，Phys. Rev. B 77, 165135，原作者稿 PDF 第 6 页 Fig. 4](https://arxiv.org/pdf/0708.1744#page=6)的 (a) 左图显示 TaSe₂ 与几何嵌套相关的虚部量，(b) 右图显示实部静态响应。同一倒空间中的强嵌套峰与实部弱峰不在同一位置，图注指出后者才对应观察到的 CDW 波矢。读图要比较峰的坐标，而不是把两图的高度或颜色当作共同归一化。本页左侧 J 与右侧 J/J(0) 则是同一几何量的绝对幅值和形状对照，并没有增加一份实部响应。若以后有完整二维数据，可用相同 q 网格、BZ 边界和各自有定义的纵轴或色标并排绘图；仅凭现有 Al Γ—X 切线不能复现原图的二维响应面。

原文式 (2) 用低频极限 $\lim_{\omega\to0}\chi''(\mathbf q,\omega)/\omega$ 定义双 δ 函数几何权重，式 (1) 的静态实部还包含占据数差与能量差。本文的高斯 J(q) 是前述离散双窗口联合权重，保持本例的等权平均和自旋约定；不能重命名为静态 $\operatorname{Im}\chi(\mathbf q,0)$，也不能由它补出 (b) 的响应峰。


想把这项分析用于应变软模，下一步应先取得对应结构的完整均匀电子网格，再按同一定义比较候选 q；Al 的四组数表和曲线仍作为网格与窗口敏感性的操作参照。
