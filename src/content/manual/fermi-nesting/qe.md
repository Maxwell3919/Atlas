[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [Johannes 与 Mazin：费米面嵌套与 CDW](https://doi.org/10.1103/PhysRevB.77.165135)

如果把一张费米面平移 q，哪些位置还能和原来的面重叠？可以先把这个几何问题写成一个能在完整 k 网格上计算的量。它有助于比较 q 的方向和尺度，但不能直接替代电子易感率，更不能单独给出 CDW 或超导结论。

这里从 [费米面](/Atlas/m/fermi-surface/qe/) 已验收的 Al 24³/32³ NSCF 继续。SCF 和 NSCF 不再重复；需要的是该页保存的 `fermi-grid.npz`，其中每个格点、每条能带的 Eₙ(k)−E_F 都能追到同一份 QE XML。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

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

下载包中的 [extract_fermi.py](/Atlas/examples/al/fermi/extract_fermi.py) 会重新读取两套 NSCF 的 XML、标准输出和错误文件，再生成 `fermi-grid.npz` 与四份嵌套 CSV。本机已有 NumPy 时，在解包后的 `al` 根目录执行：

```bash
python3 fermi/extract_fermi.py
```

后面的 `.venv/bin/python` 是原计算主机的环境路径，不随包提供。包内两处 `tmp/al.save/` 保留了这个提取步骤需要的 XML，却没有完整电荷密度与波函数；它们足以重算这里的 J(q)，不能直接用于继续运行 QE。若只要重画现有曲线，可以跳过提取，直接使用后面的四份 CSV。

```console
maxwell@maxwell:~/al/fermi/..$ .venv/bin/python fermi/extract_fermi.py
k=24^3 nks=13824 EF=8.39793432 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.61975726 J(X)=0.09968022 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.31708865 J(X)=0.06123457 eV^-2; direct-sum check passed
k=32^3 nks=32768 EF=8.38150272 eV crossing bands=[2, 3]; all grid cells assigned once
 sigma=0.10 eV J(0)=0.53305558 J(X)=0.04490039 eV^-2; direct-sum check passed
 sigma=0.20 eV J(0)=0.28204495 J(X)=0.03678119 eV^-2; direct-sum check passed
```
脚本先验收 XML 点阵，再针对 σ=0.10、0.20 eV 两个窗口计算。此处的 σ 与 SCF 输入中的 `degauss=0.02 Ry` 属于不同阶段，单位也不同；修改后处理窗口不会改变已经计算好的电子电荷密度。

缩小 σ 后，贡献更集中在费米能附近，有限网格可能只剩少量点承担较大权重，结果通常更依赖 k 点采样。增大 σ 会平滑这种离散性，也会把费米能上下更宽范围的态一起计入。因此下面同时比较网格与窗口，不能只挑峰最尖的一组来判断嵌套。

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

网格加密后，尤其窄窗口的 X 点数值变化明显。这一组数据足以演示从真实费米面到 J(q) 的过程，也清楚告诉我们：当前采样还不支持把某个尖峰当作收敛的嵌套特征。不能挑一条看起来最尖的曲线，再用别的网格的声子异常去解释它。

<figure><img src="/Atlas/examples/al/figures/fermi-nesting.png" alt="Al Γ到X方向的费米面几何嵌套网格与窗口比较" loading="lazy"/><figcaption>左：原始 J(q)；右：J(q)/J(0)。四条曲线来自两个真实网格与两个后处理窗口。</figcaption></figure>

[plot_nesting.py](/Atlas/examples/al/plot_nesting.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 读取四份 `nesting-GX-*.csv`，同时画绝对量和归一化曲线。在下载的 Al 示例根目录运行：

```bash
python3 plot_nesting.py
```

还要留意 Γ 点为什么总是很高。J(0) 是 W(k) 与自身完全重合的结果；对这种自相关定义，q=0 的大值本身就是自然结果。它不能被直接命名为某个有限波矢的不稳定性。要讨论 CDW，需进一步计算相关的电子响应和声子，并检查电子—声子耦合；要讨论超导，仍需 [EPC](/Atlas/m/epc/qe/) 和后续谱函数链条。

## 二维异质结 ZrCl₂/Sc₂C：多口袋费米面几何与动量分辨电声散射的对照

在 **`ZrCl₂/Sc₂C`**（[双网格超导计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，将二维六角布里渊区费米面（[`zrcl2-sc2c-electronic.png`](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png) 子图 c）与动量分辨声子线宽 `γ_qν` 及模式耦合 `λ_qν`（[`zrcl2-sc2c-phonon-epc.png`](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png) 子图 a）对照，可以看到费米面几何与真实电声散射之间的联系与区别：
- Band 26（蓝色）与 Band 27（橙红色）在 Γ 点周围形成内外口袋，同时 Band 26 在 K 点周围形成口袋；
- 口袋内的小动量散射（`q → Γ`）对应 Γ 点高频 `C-2p` 光学支的大线宽（`γ_{Γ,17–18} ≈ 322 GHz`），而有限动量分布在 `q = 7, ν = 1` 声学软化支处给出强电声耦合（`ω = 1.42 THz`，`γ = 141.72 GHz`，`λ_{qν} = 4.6873`）。

## 文献中的相关图件与表达方式

在研究电荷密度波（CDW）或声子软化机制时，文献常将二维费米面上的嵌套矢量箭头标注与全布里渊区电子磁化率 `χ'(q)`、嵌套函数 `χ''(q)` 及声子线宽 `γ(q)` 对照展示：

### 1. 单层 1L-CoTe₂ 轨道分辨费米面与嵌套波矢箭头标注

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_FS_NestingVectors_CoTe2_Chen2026_Fig2c.jpg" alt="单层 1L-CoTe₂ 的轨道分辨二维六角费米面及连接平行费米面片段的红色嵌套波矢 q_CDW = (1/2) b₁ 箭头" loading="lazy"/><figcaption>单层 1L-CoTe₂ 在二维六角第一布里渊区内的轨道分辨费米面等能线，红色箭头标出连接平行费米面片段的特征嵌套波矢 <code>q_CDW = (1/2) b₁</code>。图片来源：Chen, Zhang, and Zheng (2026), Fig. 2(c)。</figcaption></figure>

- **读图与作图要点**：在二维六角第一布里渊区费米面图上标注嵌套波矢 `q_CDW = (1/2) b₁` 时，将红色箭头起点和终点直接画在平行的费米面等能线段之间，并保留第一布里渊区六边形边界和高对称点标记，便于核对公度超胞的波矢比例。

### 2. 单层 BN₂Si 声子软模、二维磁化率/嵌套热力图与声子线宽四子图横排对比

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Susceptibility_Nesting_Linewidth_BN2Si_Shang2026_Fig5.jpg" alt="六角单层 BN₂Si 的声子色散软模、二维布里渊区电子磁化率实部 χ'(q) 热力图、嵌套函数虚部 χ''(q) 热力图与声学支声子线宽 γ(q) 四子图横排图" loading="lazy"/><figcaption>六角单层 BN₂Si 的四子图横排对照：(a) 沿 <code>Γ–M–K–Γ</code> 含 CDW 软模的一维声子色散，(b) 二维六角布里渊区内的电子磁化率实部 <code>χ'(q)</code> 热力图，(c) 二维六角布里渊区内的费米面嵌套函数 <code>χ''(q)</code> 热力图，(d) 沿 <code>Γ–M–K–Γ</code> 的一维声学支声子线宽 <code>γ(q)</code>。图片来源：Shang et al., <em>Phys. Rev. B</em> (2026), Fig. 5，<a href="https://doi.org/10.1103/jmys-zkgs" target="_blank" rel="noopener noreferrer">DOI: 10.1103/jmys-zkgs</a>。</figcaption></figure>

- **读图与作图要点**：仅凭 `q → 0` 处自相关峰很强的几何嵌套函数 `χ''(q)` 不足以判定晶格失稳；通过将沿 `Γ–M–K–Γ` 的声子色散软模（a）、二维六角布里渊区 `χ'(q)` 与 `χ''(q)` 热力图（b, c）以及声学支电声线宽 `γ(q)`（d）横排并列，可以严格区分纯几何嵌套峰值与包含电声耦合矩阵元后的真实声子软化动量位置。

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
