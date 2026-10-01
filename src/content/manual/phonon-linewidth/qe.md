[ph.x 输入与 EPC 选项](https://www.quantum-espresso.org/Doc/INPUT_PH.html) · [QE 声子线宽和逐模 λ 定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html) · [matdyn.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)

一个声子频率只告诉我们这个振动有多快。电子声子计算还会给出线宽 γ：在 QE 采用的定义下，它包含该模式与费米面附近电子态的耦合及可用散射相空间。本页从真实输出里找到这些数字，把频率、γ 和 λ 放在同一行，再按 q 点比较。

把 γ 与逐模 λ 放在一起，是为了辨认哪些模式的电子–声子散射较强，以及它们怎样进入配对谱；频率因子也参与 γ 到 λ 的换算。本页计算的是电子–声子贡献，声子–声子非谐散射需要另一套计算。[Qiu 等的 Ba₂N 研究](https://doi.org/10.1103/PhysRevB.105.165101)式 (2)–(4) 联系 λ、α²F 与 γ，图 3 用红色点的大小在色散上编码 γ，并结合振动模式解释其来源。该文的结构和电子态使用 VASP，声子与 EPC 使用 QE；这里的 Al 则以三个声学分支学习相同量的逐模读法。

这里沿用 [Al EPC 与 α²F](/Atlas/m/eliashberg-a2f/qe/) 的完整 4³ q 网格。SCF、致密网格与 `ph.x` 的完整输入见 [EPC 主教程](/Atlas/m/epc/qe/#double-grid-al-inputs)，本页从 `elph_dir` 开始。单原子 fcc Al 原胞只有三个声学分支，不存在本例中的光学分支。当前网格用来学习输出结构，尚未给出收敛的线宽预测。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al`，按正文运行绘图命令。

## 一个逐 q 文件的内部结构

先看第 2 个不可约 q 点的整个文件。与主 OUT 里的长迭代相比，这个文件更适合逐模式读数；但它仍须与原来的 q 点和 ph.x 输出对应。

```console
maxwell@maxwell:~/al/epc-q4$ cat elph_dir/elph.inp_lambda.2
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
     Gaussian Broadening:   0.015 Ry, ngauss=   0
     DOS =  2.647439 states/spin/Ry/Unit Cell at Ef=  8.379158 eV
     lambda(    1)=  0.0619   gamma=    2.02 GHz
     lambda(    2)=  0.0596   gamma=    1.95 GHz
     lambda(    3)=  0.1934   gamma=   25.10 GHz
     Gaussian Broadening:   0.020 Ry, ngauss=   0
     DOS =  2.646097 states/spin/Ry/Unit Cell at Ef=  8.379914 eV
     lambda(    1)=  0.0599   gamma=    1.96 GHz
     lambda(    2)=  0.0576   gamma=    1.88 GHz
     lambda(    3)=  0.1845   gamma=   23.94 GHz
     Gaussian Broadening:   0.025 Ry, ngauss=   0
     DOS =  2.643523 states/spin/Ry/Unit Cell at Ef=  8.379582 eV
     lambda(    1)=  0.0585   gamma=    1.91 GHz
     lambda(    2)=  0.0567   gamma=    1.85 GHz
     lambda(    3)=  0.1813   gamma=   23.50 GHz
     Gaussian Broadening:   0.030 Ry, ngauss=   0
     DOS =  2.643829 states/spin/Ry/Unit Cell at Ef=  8.378390 eV
     lambda(    1)=  0.0579   gamma=    1.89 GHz
     lambda(    2)=  0.0566   gamma=    1.85 GHz
     lambda(    3)=  0.1831   gamma=   23.74 GHz
     Gaussian Broadening:   0.035 Ry, ngauss=   0
     DOS =  2.645823 states/spin/Ry/Unit Cell at Ef=  8.376691 eV
     lambda(    1)=  0.0579   gamma=    1.89 GHz
     lambda(    2)=  0.0571   gamma=    1.86 GHz
     lambda(    3)=  0.1884   gamma=   24.44 GHz
     Gaussian Broadening:   0.040 Ry, ngauss=   0
     DOS =  2.648339 states/spin/Ry/Unit Cell at Ef=  8.374776 eV
     lambda(    1)=  0.0583   gamma=    1.90 GHz
     lambda(    2)=  0.0578   gamma=    1.89 GHz
     lambda(    3)=  0.1952   gamma=   25.35 GHz
     Gaussian Broadening:   0.045 Ry, ngauss=   0
     DOS =  2.650827 states/spin/Ry/Unit Cell at Ef=  8.372817 eV
     lambda(    1)=  0.0589   gamma=    1.93 GHz
     lambda(    2)=  0.0586   gamma=    1.92 GHz
     lambda(    3)=  0.2023   gamma=   26.30 GHz
     Gaussian Broadening:   0.050 Ry, ngauss=   0
     DOS =  2.653067 states/spin/Ry/Unit Cell at Ef=  8.370889 eV
     lambda(    1)=  0.0596   gamma=    1.95 GHz
     lambda(    2)=  0.0594   gamma=    1.94 GHz
     lambda(    3)=  0.2091   gamma=   27.20 GHz
```

首行前三个数是 q 坐标，单位为 2π/alat；后面的 10 和 3 分别是电子展宽组数与模式数。第二行三个数是频率平方，单位为 Ry²，不是 THz，也不是 γ。后面每一组先打印 Gaussian 电子展宽和 DOS(EF)，再给三个模式各自的 λ 与 γ。这里 `gamma` 后面明写了 GHz。

0.020 Ry 这一组，第 3 模式的 λ=0.1845、γ=23.94 GHz；前两个模式的线宽分别为 1.96 和 1.88 GHz。它们的 λ 不能仅凭 γ 的大小同比例推断，因为 QE 的逐模关系还含有频率平方和 DOS(EF)：

**λ<sub>qν</sub> = γ<sub>qν</sub> / [π ℏ N(E<sub>F</sub>) ω<sub>qν</sub>²]**

本页保留程序的 γ 定义与 GHz 单位，不额外把它换成寿命。要与实验或其他程序比较，必须先核实半宽、全宽、角频率或普通频率的约定；不能直接把 `1/gamma` 标成一个确定的寿命。

还要看清线宽来自哪种相互作用。本例 `ph.x` 给出的是电子声子贡献，不包含另一次非谐计算才能获得的声子声子散射，也没有自动加上缺陷散射或仪器分辨率。把这张表直接命名为“总声子寿命”会超过当前计算的范围。

表中的 Gaussian Broadening 是对费米面双 δ 积分的数值平滑。对同一个 q 和模式改变这一列，是在检查电子积分采样，并非把晶格依次加热到十个温度。模式的 GHz 线宽与这个以 Ry 表示的积分展宽也不是同一种宽度；先分清两者，才有意义比较不同网格的 γ。

## 回到主 OUT，核对它是哪三个振动

`al.elph.out` 中同一个 q 点的频率段为：

```text
     freq (    1) =       3.594799 [THz] =     119.909582 [cm-1]
     freq (    2) =       3.594799 [THz] =     119.909582 [cm-1]
     freq (    3) =       7.165696 [THz] =     239.021883 [cm-1]
```

这里第一、第二模式简并，频率相同；逐模 γ 与 λ 有小差异时，还需考虑简并子空间中本征矢的选择和数值精度，比较简并组的总贡献通常更稳妥。完整 OUT 还保留了电荷响应迭代、q 星的生成和模式对称性分析，可沿文件向上读，确认这些模式来自已结束的那个 q 点。

## 用带单位的数值核对 γ 与 λ

以第 2 个 q 点、第 3 模式、电子展宽 0.020 Ry 为例，原始文件给出 γ=23.94 GHz、频率 f=7.165696 THz、N(EF)=2.646097 states/spin/Ry/cell，打印 λ=0.1845。

QE 7.5 的 [elphsum 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/elphon.f90) 先按 `lambda = gamma / pi / w2 / dosfit` 计算，再把 gamma 乘 `RY_TO_GHZ` 写出。[单位常数](https://github.com/QEF/q-e/blob/qe-7.5/Modules/constants.f90) 定义 C=Ry/h=3289.841960251 THz。因此，将普通频率转回源码的 Ry 单位数值，得到 f/C=0.00217812773、γ/(1000C)=7.27694530×10⁻⁶，进而有：

```text
λ = γ_GHz × C / [1000 × π × N(EF) × f_THz²]
  = 23.94 × 3289.841960251 / [1000 × π × 2.646097 × 7.165696²]
  = 0.184512923
```

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

权重合计 64。全局 λ 是按这些权重归一化后的逐 q、逐模求和；不能把八个点当作同等权重，也不能只挑线宽最大的 q 点代替整个布里渊区。

下面的脚本读取每个文件，核对 8×10×3=240 条记录，并把主 OUT 的 THz、cm⁻¹ 频率与各模式 λ、GHz 线宽合并到 CSV。

### 交给代码助手的任务：线宽单位与逐 q 配对

> 解析 Al 八个 elph.inp_lambda 文件和 lambda.in，逐 q、逐模、逐 σ 保存频率、γ、λ、DOS(EF)、星权重。以本页 QE 7.5 源码定义为准：γ 是 GHz，频率由源文件频率平方和对应换算常数得到 THz，DOS(EF) 保留 states/spin/Ry/cell。将各量统一到公式要求的单位，核对高于20 cm⁻¹源码阈值的210条记录能否还原打印 λ；低频30条另列阈值状态，不把程序置零解释为真实耦合严格为零。星权重归一化后与按 σ 的总 λ 对照。保存完整 Python 源码、逐模 CSV、误差容许范围及检查 JSON。另对异质结 q 坐标使用实际晶胞和2π/alat约定换算，并保留原生逐 q 点与 gam.lines 路径插值结果的不同来源；只做后处理。

[完整单位核对源码 linewidth_units.py](/Atlas/examples/al/epc-q4/linewidth_units.py) · [完整 q 坐标换算源码 q_coordinates.py](/Atlas/examples/zrcl2-sc2c-q-coordinates/q_coordinates.py)。

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

```console
maxwell@maxwell:~/al/epc-q4$ ../.venv/bin/python analyse_epc.py > analysis.out
maxwell@maxwell:~/al/epc-q4$ cat analysis.out
8 irreducible q points; star weights sum to 64; 3 modes; 10 electronic widths; 240 mode records
80 q2r el-ph inputs; 10 real-space el-ph files; dense a2Fsave hash preserved
Maximum computed mode = 9.936574 THz; spectrum end = 14.000 THz
sigma_Ry  lambda_qsum  lambda_integral  omega_log_K  Tc_mu0.10_K
0.005     0.430378      0.430437       355.877      2.212103
0.010     0.371061      0.371118       344.606      0.915531
0.015     0.370295      0.370354       343.420      0.900166
0.020     0.374486      0.374545       343.741      0.969046
0.025     0.374613      0.374671       343.537      0.970575
0.030     0.373773      0.373833       342.831      0.954739
0.035     0.373581      0.373641       342.006      0.949300
0.040     0.374086      0.374146       341.243      0.955437
0.045     0.375022      0.375083       340.631      0.969102
0.050     0.376041      0.376101       340.145      0.984595
Native calculation completed; scientific convergence not established.
```

```console
maxwell@maxwell:~/al/epc-q4$ head -4 linewidth.csv
q_index,qx,qy,qz,star_weight,sigma_Ry,mode,frequency_THz,frequency_cm1,lambda_mode,gamma_GHz,DOS_EF_states_spin_Ry_cell,EF_eV
1,0.0,0.0,0.0,1,0.005,1,0.087851,2.930394,0.0,0.0,2.518161,8.37364
1,0.0,0.0,0.0,1,0.005,2,0.087851,2.930394,0.0,0.0,2.518161,8.37364
1,0.0,0.0,0.0,1,0.005,3,0.087851,2.930394,0.0,0.0,2.518161,8.37364
```

0.020 Ry 下，按星权重对三个模式求和，得到 λ=0.374486，与 `lambda.dat` 对应行一致。这个等式是数据装配检查：文件编号或权重错了，通常会在这里暴露；数值相符仍不代表 k/q 采样已足够密。

![8 个不可约 q 点的逐模线宽与耦合](/Atlas/examples/al/figures/phonon-linewidth.png)

横坐标是上表的文件编号，三种颜色对应同一个 q 点的三个模式。上图保留 γ 的 GHz 单位，下图为无量纲 λ；两张图一起读，能看到较大的线宽并不必然对应最大的 λ。要研究高对称路径上的连续线宽，可以继续在同一套 EPC 实空间数据上设置 matdyn 路径；本图只展示已经直接计算的这 8 个代表点。

下载[完整 Al 示例包](/Atlas/examples/al-lesson-files.tar.gz)，解压后进入 `al` 目录。包内的 [plot_epc.py](/Atlas/examples/al/plot_epc.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 会同时读取 `epc-q4` 下的 `linewidth.csv`、`alpha2F.dat`、`tc-scan.csv` 和 `mu-sensitivity.csv`，生成线宽与 EPC 的配套图：

<details>
<summary>plot_epc.py 的完整源码</summary>

```python
"""Run from the downloaded Al bundle root: python plot_epc.py.
Inputs stay in epc-q4/. Figures are written to figures/.
"""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=r/'epc-q4';out=r/'figures';out.mkdir(exist_ok=True)
a=np.loadtxt(d/'alpha2F.dat')
s=np.genfromtxt(d/'tc-scan.csv',delimiter=',',names=True)
colors=['#009e73','#d55e00','#cc79a7']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
def save(fig,name):
    fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(7.2,6),sharex=True)
for j,c in zip([0,3,9],colors):
    ax[0].plot(a[:,0],a[:,j+1],color=c,label=f"Electronic width {s['sigma_Ry'][j]:.3f} Ry")
    integ=np.zeros(len(a));f=np.zeros(len(a));f[1:]=2*a[1:,j+1]/a[1:,0]
    integ[1:]=np.cumsum(.5*(f[1:]+f[:-1])*np.diff(a[:,0]))
    ax[1].plot(a[:,0],integ,color=c)
ax[0].set(ylabel=r'$\alpha^2 F$');ax[0].legend(frameon=False)
ax[1].set(xlabel='Phonon frequency (THz)',ylabel=r'Cumulative $\lambda(\nu)$',xlim=(0,14))
fig.suptitle('fcc Al | 32³ electron grid, 4³ phonon grid\nUnconverged teaching calculation; Gaussian frequency width 0.12 THz',fontsize=11)
fig.tight_layout();save(fig,'eliashberg-a2f')
fig,ax=plt.subplots(1,2,figsize=(9,3.9))
ax[0].plot(s['sigma_Ry'],s['lambda_qsum'],'o-',color=colors[0],label='q-point sum')
ax[0].plot(s['sigma_Ry'],s['lambda_printed_spectrum_integral'],'x--',color=colors[1],label='Spectrum integral')
ax[0].plot(s['sigma_Ry'],s['lambda_matdyn'],'s:',color=colors[2],label='matdyn real-space interpolation')
ax[0].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'$\lambda$');ax[0].legend(frameon=False,fontsize=8)
ax[1].plot(s['sigma_Ry'],s['omega_log_K'],'o-',color=colors[0]);ax[1].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'$\omega_{\log}$ (K)')
fig.suptitle('Changing electronic width does not establish k/q convergence',fontsize=11);fig.tight_layout();save(fig,'epc-smearing')
mu=np.genfromtxt(d/'mu-sensitivity.csv',delimiter=',',names=True)
fig,ax=plt.subplots(1,2,figsize=(9,3.8))
ax[0].plot(s['sigma_Ry'],s['Tc_formula_K'],'o-',color=colors[0]);ax[0].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'Formula $T_c$ (K)',title=r'Assumed $\mu^*=0.10$')
ax[1].plot(mu['mu_star'],mu['Tc_K'],'o-',color=colors[1]);ax[1].set(xlabel=r'Assumed $\mu^*$',ylabel=r'Formula $T_c$ (K)',title='Electronic width 0.020 Ry')
fig.suptitle('Simplified Allen–Dynes expression (f₁=f₂=1); not a converged Al prediction',fontsize=11);fig.tight_layout();save(fig,'allen-dynes')
rows=list(csv.DictReader((d/'linewidth.csv').open()))
fig,ax=plt.subplots(2,1,figsize=(7.5,6),sharex=True)
for m,c in zip([1,2,3],colors):
    sel=[x for x in rows if int(x['mode'])==m and abs(float(x['sigma_Ry'])-.020)<1e-8]
    q=np.array([int(x['q_index']) for x in sel]);x=q+(m-2)*.22
    ax[0].bar(x,[float(v['gamma_GHz']) for v in sel],.20,color=c,label=f'Mode {m}')
    ax[1].bar(x,[float(v['lambda_mode']) for v in sel],.20,color=c)
ax[0].set(ylabel=r'QE linewidth $\gamma$ (GHz)');ax[0].legend(frameon=False,ncol=3)
ax[1].set(ylabel=r'Mode $\lambda_{q\nu}$',xlabel='Irreducible q-point index (file order; not a band path)',xticks=range(1,9))
fig.suptitle('fcc Al | electronic width 0.020 Ry\nRaw ph.x values; Γ acoustic residual is not an optical mode',fontsize=11)
fig.tight_layout();save(fig,'phonon-linewidth')
print('Wrote eliashberg-a2f, epc-smearing, allen-dynes, phonon-linewidth as PNG and PDF')
```

</details>

```bash
python plot_epc.py
```

全部原始逐 q 文件：[q1](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.1), [q2](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.2), [q3](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.3), [q4](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.4), [q5](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.5), [q6](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.6), [q7](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.7), [q8](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.8)。还可对照 [al.elph.in](/Atlas/examples/al/epc-q4/al.elph.in)、[al.elph.out](/Atlas/examples/al/epc-q4/al.elph.out) 和 [q-weight-source.json](/Atlas/examples/al/epc-q4/q-weight-source.json)。

## 二维异质结 ZrCl₂/Sc₂C 与 SnSe₂/Sr₂N：高频光学支大线宽与低频声学支大耦合的对比

在含轻重元素的多原子体系中，声子线宽 `γ_qν` 与无量纲模式耦合 `λ_qν` 通过前文给出的单位一致公式相联系；其中频率平方出现在分母，所以两者的大小排序可以不同。以本手册计算的 **`ZrCl₂/Sc₂C`**（[完整双网格计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）与 **`SnSe₂/Sr₂N`**（[分批 DFPT 记录](/Atlas/m/epc/qe/#double-grid-research-record)）为例：

1. **在 `ZrCl₂/Sc₂C` 中（`σ = 0.003 Ry`）**：
   - 在 Γ 点（`q = 1`），第 16 支非简并碳面外光学模（`A₁`，原始 DFPT 频率 `12.38 THz`，ASR 修正后 `12.49 THz`）给出 `λ = 0.0581、γ = 260.01 GHz`（`ph64`）与 `λ = 0.0662、γ = 297.74 GHz`（`ph96`）；第 17、18 支双重简并碳面内光学模（`E`，两支的原始 DFPT Γ 点频率均为 `15.42 THz`，ASR 修正后均为 `15.48 THz`，向 M 点升至 `17.11 THz`）拥有 Γ 点最大的声子线宽 **`γ = 315.55 / 318.58 GHz`**（`ph64`，`λ = 0.0454 / 0.0458`）与 **`γ = 318.99 / 322.13 GHz`**（`ph96`，`λ = 0.0456 / 0.0461`）；而第 7、8 支过渡金属中频光学模（`5.15 THz`）的线宽虽仅为 `γ = 44.85 / 45.14 GHz`（`ph64`），无量纲耦合却达到 `λ = 0.0580 / 0.0584`；
   - 在有限波矢 **`q = 7`**（QE 笛卡尔坐标 `(0.125000, 0.360844, 0) 2π/alat`，按实际晶胞换算为倒格分数坐标约 `(1/8, 1/4, 0)`）处，最低频声学支 `ν = 1` 的频率仅为 `ω = 1.42 THz`（`47.37 cm⁻¹`），在 [`elph.inp_lambda.7`](/Atlas/examples/zrcl2-sc2c/ph64/elph_dir/elph.inp_lambda.7) 中线宽达 `γ = 280.36 GHz`（`ph64`）/ `279.62 GHz`（`ph96`），由于分母中的 `ω_qν²` 很小，其单模耦合常数达到 **`λ_qν = 4.7525`**（`ph64`）/ **`4.7043`**（`ph96`）。

这里的 `280.36/279.62 GHz` 是原生 q=7 的逐模输出；`gam.lines` 沿高对称路径插值得到的峰值 `141.72 GHz` 属于另一组采样位置，分别查看其路径坐标。

q 坐标换算使用 `fᵢ=q_cart·aᵢ/alat`，其中 aᵢ 是实际晶胞矢量。此例面内矢量为 `(3.358477221,0,0)`、`(−1.679238611,2.908526592,0)` Å；`alat` 从致密 SCF 输出读取。六位小数的 q 打印值带来末位舍入误差。[完整换算源码](/Atlas/examples/zrcl2-sc2c-q-coordinates/q_coordinates.py)与[逐 q 坐标表](/Atlas/examples/zrcl2-sc2c-q-coordinates/q-coordinates.csv)同时保留原生笛卡尔坐标和换算后的分数坐标。

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

   因此，在后处理绘图中同时采用**散点面积综合反映 `λ_qν` 与 `γ_qν`、颜色色标编码 `γ_qν`（GHz）**，能够在同一面板中兼顾高频碳光学支的大线宽与低频声学支的大无量纲耦合：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png" alt="ZrCl₂/Sc₂C 的声子色散双编码（散点大小与颜色编码 γ_qν 和 λ_qν）、PHDOS 与 α²F(ω)" loading="lazy"/><figcaption>ZrCl₂/Sc₂C（96×96×1 致密电子网格，σ = 0.003 Ry）的声子线宽 γ<sub>qν</sub> 与无量纲耦合 λ<sub>qν</sub> 后处理：（左）声子色散上叠绘模式散点，颜色对应 γ<sub>qν</sub>（GHz），标出 Γ 点附近 15.48 THz 简并碳面内光学支的高线宽（γ ≈ 322 GHz）与红虚线所示的旧 emax = 10 THz 截断位置；（中、右）共享频率轴的原子分辨 PHDOS 与 Eliashberg 谱函数。</figcaption></figure>

2. **在 `SnSe₂/Sr₂N` 的前两个不可约 q 点（`q = 1, 2`）**：
   右面板火柴杆图（Stem Plot）读取了质量修正前单作业运行留下的前两个不可约 q 点文件 [`elph.inp_lambda.1`](/Atlas/examples/snse2-sr2n/ph64/elph.inp_lambda.1) 与 [`elph.inp_lambda.2`](/Atlas/examples/snse2-sr2n/ph64/elph.inp_lambda.2)（对应 `M_N = 118.71` 时的本征频率）。在 `q = 1`（Γ 点）处，第 13 支（`4.23 THz`）与第 16 支（`4.60 THz`）在 `σ = 0.040 Ry` 下分别给出 `λ = 0.0328`（`γ = 7.70 GHz`）与 `λ = 0.0233`（`γ = 6.44 GHz`），而在 `σ = 0.004 Ry` 下分别升至 `λ = 0.3102`（`γ = 89.08 GHz`）与 `λ = 0.1620`（`γ = 54.86 GHz`）。在 `q = 2`（`(0, 0.144338, 0)`）处，第一支声学模 `ν = 1` 的频率为 `0.5318 THz`（`17.74 cm⁻¹`），虽然具有非零线宽 `γ = 0.09 GHz`（`σ = 0.040 Ry`），但因频率低于 QE 7.1 `elph.f90` 的 `20 cm⁻¹`（`0.60 THz`）低频阈值，程序将其 `λ(1)` 置为 `0.0000`；而紧邻的 `ν = 2`（`0.7075 THz = 23.60 cm⁻¹`）跨过阈值后给出显著耦合（在 `σ = 0.040 Ry` 为 `0.0572`，在 `σ = 0.032 Ry` 为 `0.0647`）。在图中标出 `20 cm⁻¹` 竖线，有助于区分代码阈值截断与物理上的零耦合。

<figure><img src="/Atlas/figures/snse2-sr2n/snse2-sr2n-scf-ph-progress.png" alt="SnSe₂/Sr₂N 的 SCF 收敛、质量恢复声子色散与 q=1,2 逐模 λ_qν 诊断" loading="lazy"/><figcaption>SnSe₂/Sr₂N 的阶段性后处理诊断：右面板以火柴杆图对比质量修正前记录的 q = 1（Γ）与 q = 2 逐模 λ<sub>qν</sub>（σ = 0.040 Ry），琥珀色点线标出 QE 的 20 cm<sup>−1</sup> 低频截断阈值，中面板红虚线标出旧 emax = 10 THz 截断线。</figcaption></figure>

下载本算例：[ZrCl₂/Sc₂C elph.inp_lambda.1](/Atlas/examples/zrcl2-sc2c/ph96/elph_dir/elph.inp_lambda.1) · [ZrCl₂/Sc₂C elph.inp_lambda.7](/Atlas/examples/zrcl2-sc2c/ph96/elph_dir/elph.inp_lambda.7) · [ZrCl₂/Sc₂C gam.lines](/Atlas/examples/zrcl2-sc2c/ph96/gam.lines) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。

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

## 文献中的声子线宽与电子散射敏感度图例（附 DOI 溯源）

动量分辨的声子线宽 `γ_qν` 常叠加在声子色散上，或与第一布里渊区的电子磁化率与费米面嵌套函数并列比较。下面结合两幅文献原图说明其表示方式：

<span id="1-声子色散上的连续变宽度色带叠加fat-phonon-ribbon" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-1-声子色散上的连续变宽度色带叠加-fat-phonon-ribbon" class="legacy-anchor" aria-hidden="true"></span>

### 1. 声子色散上的模式分辨线宽叠加

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_FatPhonon_Linewidth_Ba2N_Qiu2022_Fig3a.jpg" alt="二维电子化合物 Ba₂N 的声子色散与电声线宽 γ_qν 变宽度红色色带叠加图" loading="lazy"/><figcaption>二维电子化合物 Ba<sub>2</sub>N 的声子色散与模式分辨声子线宽 γ<sub>qν</sub> 叠加图：黑色实线表示声子本征色散，沿声子支绘制的实心红色色带上下包络宽度正比于对应 (q, ν) 处的电声线宽 γ<sub>qν</sub>。图片来源：Qiu et al., <em>Phys. Rev. B</em> <strong>105</strong>, 165101 (2022)，<a href="https://doi.org/10.1103/PhysRevB.105.165101" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.105.165101</a>。</figcaption></figure>

Qiu 等原论文图 3(a) 的图注说明红色点的大小正比于 γ，属于点大小编码。若另行用 `fill_between` 将 `ω_qν ± c · γ_qν` 填成连续色带，那是另一种可选绘法；图中重叠的红点也不能直接解释为连续包络。下图现有图注仍需按原论文修正。

### 2. 声子软模、二维布里渊区电子磁化率 χ'(q)、嵌套函数 χ''(q) 与声子线宽的四面板对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Susceptibility_Nesting_Linewidth_BN2Si_Shang2026_Fig5.jpg" alt="单层六角 BN₂Si 的声子色散、二维布里渊区电子磁化率实部与虚部热力图以及声学支声子线宽四面板图" loading="lazy"/><figcaption>单层六角 BN<sub>2</sub>Si 的四面板水平并列分析：(a) 沿 Γ–M–K–Γ 路径的声子色散与低频 CDW 软模，(b) 第一布里渊区广义电子磁化率实部 χ′(q) 的二维等高热力图，(c) 费米面嵌套函数 χ″(q) 的二维等高热力图，以及 (d) 沿 Γ–M–K–Γ 路径的三条声学支声子线宽 γ(q)。图片来源：Shang et al., <em>Phys. Rev. B</em> (2026)，<a href="https://doi.org/10.1103/jmys-zkgs" target="_blank" rel="noopener noreferrer">DOI: 10.1103/jmys-zkgs</a>。</figcaption></figure>

把声子软化、线宽、电子易感率和[几何嵌套函数](/Atlas/m/fermi-nesting/qe/)放在共同的 q 坐标中，可以检查峰位是否对应，为机制分析提供线索。不过线宽还受电子–声子矩阵元和电子散射相空间共同影响；几张图峰位相近，并不能唯一证明软化由哪一项驱动。进一步区分两者，需要按一致定义计算响应及矩阵元，并比较相应的数值对照。

下一步：到 [α²F](/Atlas/m/eliashberg-a2f/qe/) 把逐模贡献汇总到频率轴，再到 [Allen–Dynes 公式](/Atlas/m/allen-dynes/qe/) 看这一组 λ 与 ω_log 在明确 μ* 下给出什么结果。

```text
ph.x 完整 q 网格 → 每个 q 的频率 / λ / γ → 模式与星权重核对
                                      └─ α²F → λ / ω_log → 公式 Tc
```
