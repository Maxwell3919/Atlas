一份弹性张量含有方向信息。工程中常说的体模量 B、剪切模量 G、杨氏模量 E 和泊松比 ν，是从这份方向信息进一步得到的量；在写下一个数字前，要先说清楚对应单晶的哪个方向，还是某种多晶平均。

这里接着 [应变与 Born 条件](/Atlas/m/elastic-born/qe/) 已经执行的 fcc Al 计算，使用同一批输入和应力输出。前面的 SCF、应变矩阵与 C₁₁/C₁₂/C₄₄ 提取不在这里重做。下面计算的是 **三维立方材料的 Voigt–Reuss–Hill 多晶平均**，不把它当作一个晶向上的单晶杨氏模量。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 先读结果表，避免凭图抄数

```console
maxwell@maxwell:~/al/elastic$ cat elastic-results.csv
strain,C11_GPa,C12_GPa,C44_GPa,C11-C12_GPa,C11+2C12_GPa,B_GPa,Gv_GPa,Gr_GPa,GH_GPa,E_GPa,nu,anisotropy
0.003,168.48434704533332,41.483631432,52.369407056,127.00071561333331,251.45160990933334,83.81720330311111,56.82178735626667,56.31820473137353,56.5699960438201,138.54174158107517,0.2245160974888378,0.8247104247104249
0.005,168.141101868,41.6748680308,52.4870911168,126.4662338372,251.4908379296,83.83027930986667,56.78550143752,56.315243782433875,56.55037260997693,138.5064735462106,0.2246291859248908,0.8300569966267304
0.008,167.32282988275003,42.062857668750006,52.700393477,125.25997221400002,251.44854522025003,83.81618174008334,56.672230529000004,56.26882137387525,56.47052595143762,138.3425022452812,0.22490892296850726,0.841456253669994
```
每行保留应变幅度、三个独立弹性常数、Born 条件使用的组合和派生模量。Cᵢⱼ、这些弹性常数组合以及 B、G、E 的单位为 GPa；`strain`、泊松比 `nu` 和各向异性比 `anisotropy` 都无量纲，不能给整行统一加上 GPa。

立方晶体的体模量为

**B = (C₁₁ + 2C₁₂) / 3**

Voigt 与 Reuss 剪切模量分别给出统一应变和统一应力假设下的平均：

**G<sub>V</sub> = (C₁₁ − C₁₂ + 3C₄₄) / 5**

**G<sub>R</sub> = 5(C₁₁ − C₁₂)C₄₄ / [4C₄₄ + 3(C₁₁ − C₁₂)]**

Hill 平均取两者中点 G<sub>H</sub> = (G<sub>V</sub> + G<sub>R</sub>) / 2。用 B 与 G_H 可继续得到

**E = 9BG<sub>H</sub> / (3B + G<sub>H</sub>)**

**ν = (3B − 2G<sub>H</sub>) / [2(3B + G<sub>H</sub>)]**

这些公式有前提：弹性矩阵应处在可使用的稳定范围内，分母不能接近零。若前一步已经出现负弹性特征值，不能用一串平均公式把它掩盖成正常的 E、ν。

## 用同一个脚本重新读原始输出

下载包带有 [analyse.py](/Atlas/examples/al/elastic/analyse.py)、`cases.json` 和 12 份原始 SCF 输出，不包含计算主机的 `.venv`。本机已有 NumPy 时，从解包后的 `al` 根目录执行下面三行；分析在 `elastic` 中读取输入，最后回到稍后绘图使用的目录：


后处理的输入字段和单位已经确定，可以用下面的说明让 AI 编程助手写出脚本：

```text
编写 analyse.py，在 elastic 目录读取 cases.json 中的成对应变 SCF。检查每份输出唯一 JOB DONE、电子收敛且 stderr 为空；取最后一份 total stress 的左侧 Ry/bohr³ 张量，乘 -14710.5076 转为拉伸为正的 GPa。按 ±ε 中心差分得到 C11，C12 取 yy、zz 平均；剪切输入工程应变 γ 对应变形矩阵 xy=yx=γ/2，用 σxy 对 γ 的差分求 C44。对 0.003、0.005、0.008 分别保存应力与弹性常数，依立方 Voigt–Reuss–Hill 公式计算 B、Gv、Gr、GH、E、nu 和各向异性比；写 strain-stress.csv 与 elastic-results.csv。保持原始应力符号与原文件。
```

下面是算例实际使用的完整源码。

<details>
<summary>analyse.py 完整源码</summary>

```python
from pathlib import Path
import json,re,hashlib,csv
import numpy as np
RY_BOHR3_GPA=14710.5076
rows=[]
for case in json.loads(Path('cases.json').read_text()):
 p=Path(case['label']);s=(p/'al.scf.out').read_text();err=(p/'al.scf.err').read_text()
 assert s.count('JOB DONE.')==1 and 'convergence has been achieved' in s and not err
 assert 'convergence NOT achieved' not in s and 'Error in routine' not in s
 energy=float(re.findall(r'!\s+total energy\s+=\s+([-0-9.]+)',s)[-1])
 block=re.findall(r'total\s+stress[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)',s)[-1]
 stress=-RY_BOHR3_GPA*np.array([[float(x) for x in line.split()[:3]] for line in block])
 row={**case,'energy_Ry':energy,'sigma_xx_GPa':stress[0,0],'sigma_yy_GPa':stress[1,1],'sigma_zz_GPa':stress[2,2],'sigma_xy_GPa':stress[0,1]}
 rows.append(row)
with open('strain-stress.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
results=[]
for mag in [.003,.005,.008]:
 def pair(mode):
  a=[r for r in rows if r['mode']==mode and r['engineering_strain']==mag][0]
  b=[r for r in rows if r['mode']==mode and r['engineering_strain']==-mag][0]
  return a,b
 a,b=pair('xx');c11=(a['sigma_xx_GPa']-b['sigma_xx_GPa'])/(2*mag)
 c12=sum(a[f'sigma_{i}_GPa']-b[f'sigma_{i}_GPa'] for i in ['yy','zz'])/(4*mag)
 a,b=pair('xy');c44=(a['sigma_xy_GPa']-b['sigma_xy_GPa'])/(2*mag)
 B=(c11+2*c12)/3;Gv=(c11-c12+3*c44)/5;Gr=5*(c11-c12)*c44/(4*c44+3*(c11-c12));G=(Gv+Gr)/2
 r={'strain':mag,'C11_GPa':c11,'C12_GPa':c12,'C44_GPa':c44,'C11-C12_GPa':c11-c12,'C11+2C12_GPa':c11+2*c12,'B_GPa':B,'Gv_GPa':Gv,'Gr_GPa':Gr,'GH_GPa':G,'E_GPa':9*B*G/(3*B+G),'nu':(3*B-2*G)/(2*(3*B+G)),'anisotropy':2*c44/(c11-c12)}
 results.append(r)
with open('elastic-results.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
print('All 12 SCFs: one JOB DONE., electronic convergence, empty stderr.')
print('strain     C11       C12       C44       B         GH        E        nu')
for r in results:print(f"{r['strain']:.3f} {r['C11_GPa']:10.4f} {r['C12_GPa']:9.4f} {r['C44_GPa']:9.4f} {r['B_GPa']:9.4f} {r['GH_GPa']:9.4f} {r['E_GPa']:9.4f} {r['nu']:8.4f}")
```

</details>

```bash
cd elastic
python3 analyse.py
cd ..
```

下面保留原计算主机的命令与输出，其中 `../.venv/bin/python` 是当时使用的 Python 环境路径：

```console
maxwell@maxwell:~/al/elastic$ ../.venv/bin/python analyse.py
All 12 SCFs: one JOB DONE., electronic convergence, empty stderr.
strain     C11       C12       C44       B         GH        E        nu
0.003   168.4843   41.4836   52.3694   83.8172   56.5700  138.5417   0.2245
0.005   168.1411   41.6749   52.4871   83.8303   56.5504  138.5065   0.2246
0.008   167.3228   42.0629   52.7004   83.8162   56.4705  138.3425   0.2249
```
脚本先验收每一份 SCF，再做中心差分和上面的代数运算。它输出的 Gv、Gr、GH 分开保存，因此读者能看到平均之前的差异。以下是实际使用的核心计算：

```python
B = (c11 + 2*c12) / 3
Gv = (c11 - c12 + 3*c44) / 5
Gr = 5*(c11-c12)*c44 / (4*c44 + 3*(c11-c12))
G = (Gv + Gr) / 2
E = 9*B*G / (3*B + G)
nu = (3*B - 2*G) / (2*(3*B + G))
```

完整脚本与 [实际结果表](/Atlas/examples/al/elastic/elastic-results.csv) 一起提供，表中的小数可以从原始应力输出重算。这里的 `analyse.py` 对应 16³ 网格的三种应变幅度；下面的 24³、32³、40³、48³ 结果分别保存在包内 `elastic-k24` 至 `elastic-k48` 的同名结果表中，各目录也保留自己的输入、SCF 输出和分析脚本。

## 为什么 B 看起来稳定，E 却变化很大

把相同应变下不同电子网格的结果放在一起，更容易看到误差怎样传递：

| 电子网格 | B / GPa | G_H / GPa | E / GPa | ν |
|---|---:|---:|---:|---:|
| 16³ | 83.830 | 56.550 | 138.506 | 0.2246 |
| 24³ | 83.016 | 26.427 | 71.675 | 0.3561 |
| 32³ | 83.369 | 35.081 | 92.297 | 0.3155 |
| 40³ | 83.458 | 39.169 | 101.611 | 0.2971 |
| 48³ | 83.413 | 36.155 | 94.773 | 0.3106 |

B 使用 C₁₁+2C₁₂ 的组合；这批计算里两个分量的变化部分抵消，于是 B 的变化较小。剪切平均同时依赖 C₁₁−C₁₂ 与 C₄₄，保留了明显的网格敏感性，E 和 ν 因而继续改变。不能看到 B 的三位小数差不多，就把整张模量表当成已收敛。

<figure><img src="/Atlas/examples/al/figures/elastic-moduli.png" alt="Al 的B、Hill剪切模量和杨氏模量网格检查" loading="lazy"/><figcaption>同一组弹性计算导出的多晶平均。图同时展示 B、G_H 和 E，而不是只画最稳定的那一个量。</figcaption></figure>

在下载的 Al 示例目录中运行 [plot_elastic.py](/Atlas/examples/al/plot_elastic.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)）：


画图时沿用上面的数据列。给 AI 编程助手的说明可以写成：

```text
编写 plot_elastic.py，在 Al 根目录按列名读取 elastic/kmesh-comparison.csv。横轴 kmesh，单位为 n×n×n 电子网格；一图比较 C11_GPa、C12_GPa、C44_GPa、B_GPa，另一图比较 B_GPa、GH_GPa、E_GPa。纵轴 GPa，使用全部已保存的网格行，分别输出 figures/elastic-kmesh 与 figures/elastic-moduli 的 PNG/PDF，复用 atlas_plot_style.py。
```

下面是算例实际使用的完整源码。

<details>
<summary>plot_elastic.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
p=np.genfromtxt(r/"elastic/kmesh-comparison.csv",delimiter=",",names=True)
(r/"figures").mkdir(exist_ok=True)
for file,cols in [("elastic-kmesh",["C11_GPa","C12_GPa","C44_GPa","B_GPa"]),("elastic-moduli",["B_GPa","GH_GPa","E_GPa"])]:
    fig,ax=plt.subplots(figsize=(6.8,4.4),layout="constrained")
    for name in cols:ax.plot(p["kmesh"],p[name],"o-",lw=1.6,label=name.replace("_GPa",""))
    ax.set(xlabel="n in the n × n × n electronic mesh",ylabel="Elastic response (GPa)")
    ax.set_xticks(p["kmesh"]);ax.legend(frameon=False);ax.grid(alpha=.2)
    fig.savefig(r/f"figures/{file}.png",dpi=220);fig.savefig(r/f"figures/{file}.pdf")
```

</details>

```bash
python3 plot_elastic.py
```

脚本从 `elastic/kmesh-comparison.csv` 读列名，不依赖表格列的人工顺序。图和表只反映已完成的参数系列；要报告材料常数，还要对所需模量本身设定精度，并进一步检查展宽、截断能、电子网格和形变幅度。各模量的网格变化展示了 Cᵢⱼ 的误差怎样传递到多晶平均。

## 文献中的方向弹性模量与力学图谱表达

对于各向异性显著的二维晶体，仅给出标量平均不足以描述面内不同晶向的刚度差异。研究论文常将二维弹性刚度张量 C<sub>ij</sub> 变换到面内极角 θ，用极坐标曲线同时绘出杨氏模量 E(θ)、剪切模量 G(θ) 和泊松比 ν(θ)。

<figure class="research-figure"><img src="/Atlas/figures/literature/M1_PolarModuli_E_G_nu_ZrI2_Chen2023_Fig3.jpg" alt="α-ZrI2 与 β-ZrI2 单层的面内方向杨氏模量、剪切模量与泊松比极坐标图" loading="lazy"/><figcaption>由二维弹性刚度常数 <em>C</em><sub>ij</sub> 导出的单层 α-ZrI<sub>2</sub> 与 β-ZrI<sub>2</sub> 面内杨氏模量 <em>E</em>(θ)、剪切模量 <em>G</em>(θ) 及泊松比 ν(θ) 极坐标图，直观呈现不同晶向的刚度差异。引自 Chen 等人，<em>Phys. Rev. Applied</em> <strong>20</strong>, 064048 (2023)，Fig. 3，<a href="https://doi.org/10.1103/PhysRevApplied.20.064048" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevApplied.20.064048</a>。</figcaption></figure>

跨多种材料横向比较时，常采用对数坐标的 Ashby 图谱，将小应变求得的二维杨氏模量与大应变拉伸所得的理想断裂强度绘制在同一平面上，标示不同结构家族所处的刚度—强度区间。

<figure class="research-figure"><img src="/Atlas/figures/literature/M1_AshbyStrengthModulus_2DMagnets_Wang2022_Fig59.jpg" alt="二维材料的二维杨氏模量与理想断裂强度双对数 Ashby 图" loading="lazy"/><figcaption>二维材料的二维杨氏模量与理想断裂强度双对数 Ashby 分布图，汇总多类二维晶体的面内刚度与极限强度范围。引自 Wang 等人，<em>ACS Nano</em> <strong>16</strong>, 6859 (2022)，Fig. 59，<a href="https://doi.org/10.1021/acsnano.1c09150" target="_blank" rel="noopener noreferrer">DOI: 10.1021/acsnano.1c09150</a>。</figcaption></figure>

下一步可以回到 [Born 判据](/Atlas/m/elastic-born/qe/) 检查张量正定性，或对照 [声子计算](/Atlas/m/phonon-dfpt/qe/) 的长波声学支；两条证据关注的范围不同，应分别验证。

```text
同一批成对应变 SCF → C₁₁ / C₁₂ / C₄₄
                         ├→ Born 条件
                         └→ B、G_V、G_R → G_H → E、ν
                                                ↓
                                  对目标模量检查数值收敛
```

## 参考资料

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [Born 稳定性条件原始论文](https://doi.org/10.1103/PhysRevB.90.224104)
