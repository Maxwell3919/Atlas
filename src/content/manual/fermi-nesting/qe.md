把费米面平移 q 后的重叠程度，可以用完整 k 网格上的几何联合权重 J(q) 定量比较。本页以 Al 为例，计算它对 q、电子网格和能量窗口的依赖。

这里从 [费米面](/Atlas/m/fermi-surface/qe/) 已完成本征值检查的 Al 24³/32³ NSCF 继续。SCF 和 NSCF 不再重复；需要的是该页保存的 `fermi-grid.npz`，其中每个格点、每条能带的 Eₙ(k)−E_F 都能追到同一份 QE XML。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [Johannes 与 Mazin：费米面嵌套与 CDW](https://doi.org/10.1103/PhysRevB.77.165135)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-electronic-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 先把所计算的量说清楚

我们定义一个归一化高斯窗口 δσ(E)，宽度 σ 用 eV 表示。把同一 k 点所有带的费米能附近权重相加，记作 W(k)。实际计算的是

```text
δσ(E) = exp[−E²/(2σ²)] / (sqrt(2π) σ)
W(k)  = Σn δσ[Eₙ(k) − E_F]
J(q)  = (1/Nk) Σk W(k) W(k+q)
```

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

完整网格具有周期性。把 W 的离散 Fourier 变换乘以它的复共轭，再逆变换，就得到周期自相关；最后除以 Nk：

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

## 用电子响应和声子检验机制

电子响应分析在几何权重之外，还需占据数差、跃迁能量分母及相应矩阵元。下面两项研究展示了这些量与声子证据的对应关系。

Shang 等研究 h-BN₂Si 时，用 VASP 求能带/DOS、QE 6.3 计算声子/EPC，并分别分析 Lindhard 响应和声子线宽。Fig. 5(b,c) 展示二维 BZ 上 Re χ(q)、Im χ(q)，(d) 给最低声学支线宽；作者比较响应峰、软模和线宽的 q 位置。作者由这些量的动量位置共同分析软化机制。[Shang et al., Phys. Rev. B 113, 094504 (2026), Fig. 5](https://doi.org/10.1103/jmys-zkgs)

Chen 等在 CoTe₂ 层间耦合研究中，先用 PBE DFT/DFPT 分析单层的软化机制。Fig. 2(c) 标出单层的轨道分辨费米口袋和 q，(e) 为 EPC 加权广义静态 χ_qν，(f) 为常矩阵元 χ′；这种比较用于区分费米面几何与模式分辨 EPC 的作用。[Chen et al., Phys. Rev. B 114, 055413 (2026), Fig. 2(c–f)](https://doi.org/10.1103/l89c-t2s4)

Al 表格给出 J(q) 对网格和 σ 的敏感性。进一步分析材料响应时，可从同一材料的能带与占据计算 Lindhard χ，再与 DFPT 声子、线宽及 EPC 对照。

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

Γ 点对应 J(0)=mean[W²]，即权重场与自身重合的自相关。有限 q 的机制分析接电子响应与声子，超导分析接 [EPC](/Atlas/m/epc/qe/) 和谱函数链条。

## 二维异质结 ZrCl₂/Sc₂C：多口袋费米面几何与动量分辨电声散射的对照

在 **`ZrCl₂/Sc₂C`**（[双网格超导计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，将二维六角布里渊区费米面（[`zrcl2-sc2c-electronic.png`](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png) 子图 c）与动量分辨声子线宽 `γ_qν` 及模式耦合 `λ_qν`（[`zrcl2-sc2c-phonon-epc.png`](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png) 子图 a）对照，可以看到费米面几何与真实电声散射之间的联系与区别：
- Band 26（蓝色）与 Band 27（橙红色）在 Γ 点周围形成内外口袋，同时 Band 26 在 K 点周围形成口袋；
- 模式分辨计算在 Γ 点高频光学支给出 `γ_{Γ,17–18} ≈ 322 GHz`，在 `q = 7, ν = 1` 声学软化支给出 `ω = 1.42 THz`、`γ = 141.72 GHz`、`λ_{qν} = 4.6873`。这些数值来自声子/EPC 输出；把具体电子口袋散射归属到某一振动模式，还需相应矩阵元和模式本征矢。

## 文献中的相关图件与表达方式

研究电荷密度波或声子软化时，可以把费米面几何、电子电荷响应和声子线宽放在同一 q 空间中比较。下列文献的 χ′ 表示相应定义下的电子易感率；一些图将与低频耗散响应有关的嵌套量记作 χ″，其归一化和频率极限应回原文核对，不能直接当作静态 Im χ(q,0)。本页计算的 J(q) 只是前面定义的几何联合权重，不包含完整的电子响应或电子–声子矩阵元。

### 1. 单层 1L-CoTe₂ 轨道分辨费米面与嵌套波矢箭头标注

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_FS_NestingVectors_CoTe2_Chen2026_Fig2c.jpg" alt="单层 1L-CoTe₂ 的轨道分辨二维六角费米面及连接内外费米口袋的红色散射波矢箭头" loading="lazy"/><figcaption>单层 1L-CoTe₂ 在二维六角第一布里渊区内的轨道分辨费米面等能线，红色双箭头连接内外口袋中广义静态响应较强的散射通道。作者将常矩阵元 χ′ 的宽峰与含 EPC 矩阵元 χ_qν 的局域热点比较，解释 M–K 路径附近的声子软化。来源：Chen, Zhang, and Zheng, <em>Phys. Rev. B</em> <strong>114</strong>, 055413 (2026), Fig. 2(c)，<a href="https://doi.org/10.1103/l89c-t2s4">DOI: 10.1103/l89c-t2s4</a>。</figcaption></figure>

图中箭头表示原文选出的内外口袋散射通道；其作用由 Fig. 2(e,f) 的响应及 Fig. 2(d) 的声子动量分布共同解释。

### 2. 单层 BN₂Si 声子软模、二维磁化率/嵌套热力图与声子线宽四子图横排对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Susceptibility_Nesting_Linewidth_BN2Si_Shang2026_Fig5.jpg" alt="六角单层 BN₂Si 的声子色散软模、二维布里渊区电子磁化率实部 χ'(q) 热力图、嵌套函数虚部 χ''(q) 热力图与声学支声子线宽 γ(q) 四子图横排图" loading="lazy"/><figcaption>六角单层 BN₂Si 的四子图横排对照：(a) 沿 <code>Γ–M–K–Γ</code> 含 CDW 软模的一维声子色散，(b) 二维六角布里渊区内的电子磁化率实部 <code>χ'(q)</code> 热力图，(c) 二维六角布里渊区内的费米面嵌套函数 <code>χ''(q)</code> 热力图，(d) 沿 <code>Γ–M–K–Γ</code> 的一维声学支声子线宽 <code>γ(q)</code>。图片来源：Shang et al., <em>Phys. Rev. B</em> (2026), Fig. 5，<a href="https://doi.org/10.1103/jmys-zkgs" target="_blank" rel="noopener noreferrer">DOI: 10.1103/jmys-zkgs</a>。</figcaption></figure>

仅凭 `q → 0` 处自相关峰很强的几何嵌套函数 `χ''(q)` 不足以判定晶格失稳；通过将沿 `Γ–M–K–Γ` 的声子色散软模（a）、二维六角布里渊区 `χ'(q)` 与 `χ''(q)` 热力图（b, c）以及声学支电声线宽 `γ(q)`（d）横排并列，可以比较几何权重、电子响应和声子异常的位置是否一致。因果判断还需矩阵元与收敛对照，不能由峰位对应直接得出。

下一步可以继续加密 k 网格并交叉检查窗口，或者返回 [费米面三维图](/Atlas/m/fermi-surface/qe/) 看同一个 q 实际连接哪两块面。

```text
全布里渊区本征值 → 费米能附近权重 W(k)
                             ↓
                  周期自相关 J(q) → 直接求和校验
                             ↓
                    k网格 × 窗口交叉检查
                             ↓
               与声子 / 电子响应 / EPC 分别比较
```
