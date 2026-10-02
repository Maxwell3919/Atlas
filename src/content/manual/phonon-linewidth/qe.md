[完整EPC父链](/Atlas/m/epc/qe/) · [声子与本征位移](/Atlas/m/phonon-dfpt/qe/) · [QE线宽定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

## 同一个模式，频率、线宽和 λ 分别告诉什么

声子频率给出一个振动的能量。电子–声子线宽γqν包含该模式与费米面电子的矩阵元和可用散射相空间；逐模λqν再按频率平方和DOS(EF)归一化。因此线宽最大的模式不一定贡献最大的λ。要找异质结的配对振动，应先在色散定位q与分支，再核对本征位移、线宽和λ，最后看它进入α²F及累计λ的频段。

这里从真实fcc Al输出学习这一读法。它只有三条声学分支，没有光学模；随后用ZrCl₂/Sc₂C保存表说明轻重元素体系的差别。计算给出电子–声子线宽，非谐声子–声子、缺陷等贡献未包含，不能直接把这列叫总声子寿命。与实验半宽或全宽比较时还需统一频率和宽度约定。

## 一个 q 点的模式与电子展宽

Al完整输入与两次SCF见[EPC页](/Atlas/m/epc/qe/#double-grid-al-inputs)，本段直接读取第2个不可约q的原件。首行是笛卡尔q、10档展宽和3个模式；第二行是QE内部Ry²标度的频率平方。完整十档文件可[下载](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.2)。

```console
maxwell@maxwell:~/al/epc-q4$ head -12 elph_dir/elph.inp_lambda.2
          -0.176777      0.176777     -0.176777    10     3
  0.119399E-05  0.119399E-05  0.474424E-05
     Gaussian Broadening:   0.005 Ry, ngauss=   0
     DOS =  2.518161 states/spin/Ry/Unit Cell at Ef=  8.373640 eV
     lambda(    1)=  0.0484   gamma=    1.50 GHz
     lambda(    2)=  0.0468   gamma=    1.45 GHz
     lambda(    3)=  0.2363   gamma=   29.17 GHz
     Gaussian Broadening:   0.010 Ry, ngauss=   0
     DOS =  2.624685 states/spin/Ry/Unit Cell at Ef=  8.377216 eV
     lambda(    1)=  0.0659   gamma=    2.13 GHz
     lambda(    2)=  0.0639   gamma=    2.07 GHz
     lambda(    3)=  0.2128   gamma=   27.38 GHz
```

主OUT中同一个q给出的频率如下，与原件模式顺序对应：

```text
     freq (    1) =       3.594799 [THz] =     119.909582 [cm-1]
     freq (    2) =       3.594799 [THz] =     119.909582 [cm-1]
     freq (    3) =       7.165696 [THz] =     239.021883 [cm-1]
```

固定σ=0.020 Ry，这三个模式的实际输出为：

| 模式 | 普通频率 $f$ (THz) | $\gamma$ (GHz) | $\lambda_{q\nu}$ |
|---|---:|---:|---:|
| 1 | 3.594799 | 1.96 | 0.0599 |
| 2 | 3.594799 | 1.88 | 0.0576 |
| 3 | 7.165696 | 23.94 | 0.1845 |

第三模线宽约为第一模12倍，λ约为3倍，因为频率也约为2倍、平方项抵消一部分增加。前两模简并；本征矢可在简并子空间内旋转，因此跨网格比较应同时看简并组的总贡献和位移子空间，不能只凭分支编号认定某个原子方向未变。
这时仍停在一个 q 点。第 3 模的 0.1845 乘本点的星权重 8/64，才得到对全局 λ 的贡献 0.0230625；三个模式合计贡献 0.03775。前两模合起来为 0.1175，在简并子空间旋转时应比较这一组的总耦合，而不是要求每一条模式的 γ 都逐字不变。由这里继续到[逐 q 汇总与谱构造](/Atlas/m/eliashberg-a2f/qe/#mode-to-spectrum)，可以看到同一模式的频率如何确定谱中的位置。


Gaussian Broadening是双δ电子积分的数值参数，不是晶格温度。它的Ry单位与模式γ的GHz不同；改变σ是在比较费米面采样敏感性，不能画成声子加热实验。

## 用带单位的数值核对 γ 与 λ

以第 2 个 q 点、第 3 模式、电子展宽 0.020 Ry 为例，原始文件给出 γ=23.94 GHz、频率 f=7.165696 THz、N(EF)=2.646097 states/spin/Ry/cell，打印 λ=0.1845。

QE 7.5 的 [elphsum 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/elphon.f90) 先按 `lambda = gamma / pi / w2 / dosfit` 计算，再把 gamma 乘 `RY_TO_GHZ` 写出。[单位常数](https://github.com/QEF/q-e/blob/qe-7.5/Modules/constants.f90) 定义 C=Ry/h=3289.841960251 THz。因此，将普通频率转回源码的 Ry 单位数值，得到 f/C=0.00217812773、γ/(1000C)=7.27694530×10⁻⁶，进而有：

$$
\begin{aligned}
\lambda&=\frac{\gamma_{\mathrm{GHz}}C}{1000\pi N(E_F)f_{\mathrm{THz}}^2}\\
&=\frac{23.94\times3289.841960251}{1000\pi\times2.646097\times7.165696^2}\\
&=0.184512923.
\end{aligned}
$$

这个结果与输出的 0.1845 相符。原始 γ 只打印两位小数、λ 只打印四位小数，比较时要保留相应舍入误差。这里已经沿源码把 GHz、THz、Ry 的约定接起来，不应再额外乘 2π，也不应把程序打印的单自旋 DOS 擅自乘 2。

核对脚本 [linewidth_units.py](/Atlas/examples/al/epc-q4/linewidth_units.py) 对高于源码阈值的 210 行都做了上述比较；[输出](/Atlas/examples/al/epc-q4/linewidth-unit-check.out) 和 [检查记录](/Atlas/examples/al/epc-q4/linewidth-unit-check.json) 保留了数值与误差容许范围。

## Γ 点的零 λ 还包含程序阈值

原始 ph.x 在 Γ 三个声学模式上打印 0.087851 THz，即 2.930394 cm⁻¹。它们是小的声学残差，不是光学模。在 0.020 Ry 这一组，γ 实际为 0.09、0.09、0.11 GHz，但三个 λ 都为 0。

原因在本次 `electron_phonon='interpolated'` 所调用的 QE 7.5 `elphsum`：源码将 `epsw` 设为 20 cm⁻¹，只有频率高于这个阈值才使用 γ、频率平方和 DOS 计算 λ，否则直接将 λ 设为零；γ 仍照常打印。这三个残差模式落在阈值之下，因此不能把输出的零 λ 当作已经证明的物理零耦合，更不能据此说它们的 γ 也为零。

本例十组展宽中共有 30 行受到这项处理；对应的条件、源码位置已经记入 [EPC 检查记录](/Atlas/examples/al/epc-q4/summary.json)。这是这条原生程序路线自身的限制。实际研究声学长波极限时，还需检查 q→0 采样与数值处理，不能仅引用 Γ 的零值。


## 8 个不可约点怎样代表完整 q 网格

下面的编号严格对应 `elph.inp_lambda.1` 到 `.8`。这是文件顺序，并不是一条连续高对称路径，图里也不把相邻编号连成声子色散。

| 文件编号 | qx, qy, qz（2π/alat） | 星权重 |
|---:|---|---:|
| 1 | 0.0000000, 0.0000000, 0.0000000 | 1 |
| 2 | -0.1767767, 0.1767767, -0.1767767 | 8 |
| 3 | 0.3535534, -0.3535534, 0.3535534 | 4 |
| 4 | 0.0000000, 0.3535534, 0.0000000 | 6 |
| 5 | 0.5303301, -0.1767767, 0.5303301 | 24 |
| 6 | 0.3535534, 0.0000000, 0.3535534 | 12 |
| 7 | 0.0000000, -0.7071068, 0.0000000 | 3 |
| 8 | -0.3535534, -0.7071068, 0.0000000 | 6 |

权重合计 64。全局 λ 是按这些权重归一化后的逐 q、逐模求和。真实 0.020 Ry 表中，第 8 个 q 的三个模式和为 0.4763，比第 5 个 q 的 0.3791 大；乘星权重后，贡献却分别为 0.04465313 和 0.14216250，第 5 个 q 反而约占总 λ 的 37.96%。这就是按本点模式和排序与按全局贡献排序的区别，完整数值见[八个 q 的贡献表](/Atlas/m/eliashberg-a2f/qe/#mode-to-spectrum)。高对称路径还能帮助定位异常模式，但不能替代完整布里渊区的权重求和。

## 后处理先说明列与单位，再运行源码

解析器将每个q文件按σ块拆开，记录模式编号、频率平方、DOS(EF)、λ和γ，再与主OUT频率及lambda.in权重配对。频率由匹配版本常数转成THz，γ保留GHz，DOS仍为states/spin/Ry/cell。高于20 cm⁻¹的210行用于单位公式核对，低频30行另列程序阈值状态。

> 从Al的8个elph文件、lambda.in及al.elph.out生成逐q/逐模/逐σ表。沿QE7.5源码转换Ry²频率和GHz线宽，用统一单位复算λ并保留打印舍入容差。记录20 cm⁻¹低频阈值，不把程序置零写成物理零耦合。按星权重核对总λ，保存完整源码、CSV、检查JSON与错误状态；只读取原件。

[完整linewidth_units.py](/Atlas/examples/al/epc-q4/linewidth_units.py)实现单位检查，[analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py)生成linewidth.csv。完整包在[Al示例](/Atlas/examples/al-lesson-files.tar.gz)。

<details>
<summary>linewidth_units.py 的完整源码</summary>

```python
from pathlib import Path
import csv,json,math
r=Path(__file__).resolve().parent
h=6.62607015e-34
hartree=4.3597447222071e-18
ry_to_THz=(hartree/2)/h/1e12
rows=list(csv.DictReader((r/'linewidth.csv').open()))
results=[]
for row in rows:
    f=float(row['frequency_THz']);g=float(row['gamma_GHz']);dos=float(row['DOS_EF_states_spin_Ry_cell']);printed=float(row['lambda_mode'])
    w_Ry=f/ry_to_THz;g_Ry=g/(1000*ry_to_THz)
    lam=g_Ry/(math.pi*dos*w_Ry*w_Ry)
    tolerance=.005*ry_to_THz/(1000*math.pi*dos*f*f)+.00005+1e-6
    below_cutoff=float(row['frequency_cm1'])<=20.0
    if below_cutoff: assert printed==0.0
    else: assert abs(lam-printed)<=tolerance
    results.append(dict(q_index=int(row['q_index']),sigma_Ry=float(row['sigma_Ry']),mode=int(row['mode']),frequency_THz=f,gamma_GHz=g,DOS_EF_states_spin_Ry_cell=dos,frequency_Ry=w_Ry,gamma_Ry=g_Ry,lambda_from_printed_gamma=lam,lambda_printed=printed,rounding_tolerance=tolerance,below_20_cm1_cutoff=below_cutoff))
chosen=next(x for x in results if x['q_index']==2 and x['mode']==3 and abs(x['sigma_Ry']-.02)<1e-9)
receipt={'source':'QE7.5 PHonon/PH/elphon.f90 elphsum: lamb=gam/pi/w2/dosfit; then gam*=RY_TO_GHZ. Modules/constants.f90: RY_TO_GHZ=1000*RY_TO_THZ; RY_TO_THZ=Ry/h/1e12.','ry_to_THz':ry_to_THz,'number_of_records_checked':len(results),'formula_records_above_cutoff':sum(not x['below_20_cm1_cutoff'] for x in results),'low_frequency_lambda_cutoff_cm1':20.0,'cutoff_records':sum(x['below_20_cm1_cutoff'] for x in results),'gamma_printing_step_GHz':.01,'lambda_printing_step':.0001,'chosen_example':chosen,'convention':'Use printed ordinary-frequency THz/GHz through native Ry conversion. Do not insert an extra 2pi or double the per-spin DOS.'}
(r/'linewidth-unit-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'QE7.5: 1 Ry / h = {ry_to_THz:.9f} THz')
print('q2, mode3, electronic width 0.020 Ry')
for k,v in chosen.items():print(k,'=',v)
print('210 above-cutoff rows agree within printed rounding; 30 Gamma rows have lambda set to zero by the native 20 cm^-1 cutoff.')
```

</details>

```bash
python3 linewidth_units.py
```

实际检查输出和210行误差范围保存在[linewidth-unit-check.out](/Atlas/examples/al/epc-q4/linewidth-unit-check.out)及[检查JSON](/Atlas/examples/al/epc-q4/linewidth-unit-check.json)。Al谱和加权求和的完整运行结果见[α²F复算](/Atlas/m/eliashberg-a2f/qe/#spectral-reproduction)，这里不重复十行Tc表。

<span id="heterostructure-modes"></span>

## 高频大线宽与低频大 λ 的材料例子

ZrCl₂/Sc₂C保存的ph64/ph96数据在σ=0.003 Ry给出以下对照。模式编号、原始DFPT频率与ASR插值频率按该存档分列。逐原子PHDOS支持高频段C投影占优，旧附件没有该链的模式向量，因此不指定逐支面内/面外方向；材料Tc仍受谱窗和数值验收限制。

| q与模式 | 原始频率 | γ64 / γ96 (GHz) | λ64 / λ96 |
|---|---|---:|---:|
| Γ，第16支，高频光学模 | 12.38 THz；ASR12.49 | 260.01 / 297.74 | 0.0581 / 0.0662 |
| Γ，第17支，高频简并组 | 15.42 THz；ASR15.48 | 315.55 / 318.99 | 0.0454 / 0.0456 |
| Γ，第18支，同一高频简并组 | 15.42 THz；ASR15.48 | 318.58 / 322.13 | 0.0458 / 0.0461 |
| q7，第1声学支 | 1.42 THz (47.37 cm⁻¹) | 280.36 / 279.62 | 4.7525 / 4.7043 |

ph64的Γ第7、8中频模约5.15 THz，γ=44.85、45.14 GHz，λ=0.0580、0.0584。它们的线宽远小于C高频模，λ却相近；q7低频模的λ更大，正是频率平方归一化的作用。再乘q星权重才能比较对总λ的贡献。约1.42 THz的模与Γ模式并非同一位置，不能把它画到Γ上。

q7原生笛卡尔坐标为(0.125000,0.360844,0)×2π/alat，在实际晶胞约为(1/8,1/4,0)。换算使用fi=qcart·ai/alat；原生gam.lines的路径峰值141.72 GHz来自另一组采样位置，不能替换这个逐q值。完整[坐标源码](/Atlas/examples/zrcl2-sc2c-q-coordinates/q_coordinates.py)和[两种坐标CSV](/Atlas/examples/zrcl2-sc2c-q-coordinates/q-coordinates.csv)保留转换依据。

<details>
<summary>q_coordinates.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Convert native QE Cartesian q (2*pi/alat) to reciprocal-cell fractions."""
import csv, hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
BOHR_TO_ANGSTROM = 0.529177210903
inp = (ROOT / "pwx.in").read_text()
lines = inp.splitlines()
start = next(i for i, s in enumerate(lines) if s.strip().startswith("CELL_PARAMETERS"))
assert "angstrom" in lines[start].lower()
cell = [list(map(float, s.split())) for s in lines[start + 1:start + 4]]
out = (ROOT / "pwxall.out").read_text()
alat_bohr = float(re.search(r"lattice parameter \(alat\)\s*=\s*([0-9.]+)", out).group(1))
alat_angstrom = alat_bohr * BOHR_TO_ANGSTROM
rows = []
files = sorted((ROOT / "elph_dir").glob("elph.inp_lambda.*"), key=lambda p: int(p.name.rsplit(".", 1)[1]))
for f in files:
    q = [float(x) for x in f.read_text().splitlines()[0].split()[:3]]
    # If q_phys = (2*pi/alat)*q and q_phys = sum_i fraction_i*b_i,
    # with a_i dot b_j = 2*pi*delta_ij, fraction_i = q dot a_i / alat.
    fractions = [sum(q[j] * vector[j] for j in range(3)) / alat_angstrom for vector in cell]
    rows.append(dict(q_index=int(f.name.rsplit(".", 1)[1]), q_cart_x=q[0], q_cart_y=q[1], q_cart_z=q[2], q_fraction_1=fractions[0], q_fraction_2=fractions[1], q_fraction_3=fractions[2]))
with (ROOT / "q-coordinates.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
meta = dict(cell_angstrom=cell, alat_bohr=alat_bohr, alat_angstrom=alat_angstrom, input_q_unit="2*pi/alat", definition="fraction_i = q_cart dot a_i / alat", source_sha256={str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT / "pwx.in", ROOT / "pwxall.out", *files]}, precision="Native q header is rounded to six decimals; alat output is rounded. Fractions inherit those rounding errors.")
(ROOT / "q-coordinate-checks.json").write_text(json.dumps(meta, indent=2) + "\n")
for row in rows: print(row)
```

</details>

下载[ph96 Γ原件](/Atlas/examples/zrcl2-sc2c/ph96/elph_dir/elph.inp_lambda.1)、[ph96 q7原件](/Atlas/examples/zrcl2-sc2c/ph96/elph_dir/elph.inp_lambda.7)、[路径gam.lines](/Atlas/examples/zrcl2-sc2c/ph96/gam.lines)。色散/PHDOS/α²F的现有三联图集中在[谱窗分析](/Atlas/m/eliashberg-a2f/qe/#spectral-window)。其中散点面积是脚本的λ和γ混合显示权重，不能按它单独读出λ或γ；量值应读本表和原件。

<span id="ba2n-linewidth-analysis"></span>

## Ba₂N 图3与图6的模式判读

[Qiu等原文](https://doi.org/10.1103/PhysRevB.105.165101)图3(a)在声子色散上以红点大小编码γ，图3(d)显示约55 cm⁻¹的Γ光学振动：上下Ba层在面内相反运动。图3(b)的元素PHDOS、图3(c)的谱峰辅助确认频段，却不能代替位移图。图6在4%应变下沿同样的量比较：Γ光学模约49 cm⁻¹，K声学模约24 cm⁻¹且线宽增强，图6(e)用√3×√3超胞显示有限q位移。这里的红点不是连续包络色带，不能从重叠点的视觉宽度读取实验谱峰半宽。

[Fig. 3(a,d)与Fig. 6(a,d,e)，PDF第3/5页](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.105.165101)区分两种“大小”：色散红点表示γ，振动箭头表示原子位移；γ较大的位置还要经频率平方换算才得到逐模λ。原图注说明红点大小正比于线宽，却没有公开点面积或直径的换算常数，因此不能从图上量一个圆就反推出γ。自己的图应公开映射，例如以点面积正比γ并用独立图例标GHz，另把λ保留在数值表；不要把γ和λ相加作为一个点面积。本页八个不可约q是文件顺序，现有表用于逐点核对，不能按编号连成原文那样的高对称路径。要做相同色散展示，需先从同一父链的matdyn路径坐标、频率与线宽插值输出建立逐点对应，再用gnuplot的variable pointsize展示明确的单量编码。原子方向则由同一模式e除以√M后统一缩放，Γ用原胞、K用相容超胞，在XCrySDen中分别读俯视与侧视。

读自己的模式时应同时标明q坐标约定、频率、简并组、原子和层位、面内/面外分量及显示振幅。有限q要保留exp(iq·R)相位，在相容超胞显示运动；声子本征矢的任意整体相位不影响物理。原子振动贡献与电子轨道贡献是两类投影，模式中C在动不等于C-2p电子主导配对。

<span id="1-声子色散上的连续变宽度色带叠加fat-phonon-ribbon"></span>
<span id="h-1-声子色散上的连续变宽度色带叠加-fat-phonon-ribbon"></span>

比较声子软化与[几何嵌套](/Atlas/m/fermi-nesting/qe/)的峰位可提供线索；γ还含有矩阵元，因此峰位对应不能唯一判定软化机制。跨单层与界面要保持相同结构/应变参考，再结合电子态空间分布和分辨耦合比较。

<details>
<summary>SnSe₂/Sr₂N错误质量旧链的阈值诊断</summary>

旧q1/q2使用MN=118.71的错误质量，只保留为代码阈值与输入身份诊断。q2第1模0.5318 THz(17.74 cm⁻¹)在σ=0.040 Ry有γ=0.09 GHz而λ=0；第2模0.7075 THz(23.60 cm⁻¹)跨过QE7.1的20 cm⁻¹阈值，λ=0.0572。旧Γ第13、16模在σ=0.040 Ry为λ=0.0328、0.0233，σ=0.004 Ry为0.3102、0.1620。质量修正后的新链尚未完成完整Γ，不能以旧谱作为其结果。详见[历史研究记录](/Atlas/cases/epc-research-notes/#double-grid-research-record)，原文件保留原值。

</details>

由这里的q、模式、频率、γ和λ进入[α²F及累计λ](/Atlas/m/eliashberg-a2f/qe/)，再结合[ωlog与Tc](/Atlas/m/allen-dynes/qe/)判断软化与耦合增强共同带来的变化。
