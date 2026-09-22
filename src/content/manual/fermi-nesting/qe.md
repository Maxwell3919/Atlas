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

[plot_nesting.py](/Atlas/examples/al/plot_nesting.py) 读取四份 `nesting-GX-*.csv`，同时画绝对量和归一化曲线。在下载的 Al 示例根目录运行：

```bash
python3 plot_nesting.py
```

还要留意 Γ 点为什么总是很高。J(0) 是 W(k) 与自身完全重合的结果；对这种自相关定义，q=0 的大值本身就是自然结果。它不能被直接命名为某个有限波矢的不稳定性。要讨论 CDW，需进一步计算相关的电子响应和声子，并检查电子—声子耦合；要讨论超导，仍需 [EPC](/Atlas/m/epc/qe/) 和后续谱函数链条。

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
