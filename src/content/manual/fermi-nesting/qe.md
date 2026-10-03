费米面上两个区域能由某个 q 连起来，说明该散射有几何相空间；真正作用于哪个声子模式，还取决于电子态与该模式扰动的矩阵元。这里用真实 fcc Al 网格计算费米能附近的联合权重 $J(\mathbf q)$，先看同一量对采样和窗口有多敏感，再拆开能带配对，最后与原生电子–声子输出对照。这样可以知道几何图给出了什么，以及从它走到软模归因还缺什么。

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

这一定义还有一个直接的读图约束。高斯权重 W 非负，周期平移又不改变 W² 的网格平均；由 Cauchy–Schwarz 不等式，对本例同一权重场的自相关有 $0\le J(\mathbf q)\le J(\mathbf 0)$。所以 Γ 成为最大值是定义允许并保证的结果，不是寻找到了最强有限 q 失稳。除以 J(0) 后每组 Γ 都等于 1，也会隐藏不同网格上绝对权重的差别。需要看的是 Γ 以外的局部结构、它对采样的稳定性，以及是否与声子响应位于同一 q。这个上界只用于本页的周期几何自相关，不能拿去约束含能量分母或矩阵元的响应函数。

## 确认网格来源，再运行提取和求和

从完整下载包的 `al` 根目录读取这次均匀 NSCF 的原生 OUT：

```bash
grep -E 'number of k points|Fermi energy|JOB DONE' fermi/k32-cg/al.nscf.out
```

```text
     number of k points= 32768  Marzari-Vanderbilt smearing, width (Ry)=  0.0200
     the Fermi energy is     8.3815 ev
   JOB DONE.
```

OUT 的费米能按打印精度显示；后处理能量网格使用对应 XML 的完整读数，零点为 `8.381502717320133 eV`。在这份完整网格中，第 2、3 带的 E−E_F 范围跨过零能：

| 带号 | 最低 E−E_F / eV | 最高 E−E_F / eV |
|---|---:|---:|
| 2 | -4.487132561119 | 12.944767171884 |
| 3 | -0.326782082253 | 12.944767173295 |

点数、能量参考和穿越带来自同一份原生输出与 XML。不能对一条能带路径直接做下面的循环卷积，因为路径上的数组不是一个周期三维均匀网格。

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

把同一窗口的 X 点进一步拆开，就能看到总值里的不同几何配对。令每条带的高斯权重为 $w_n(\mathbf k)$，则

$$
\begin{aligned}
J_{nm}(\mathbf q)&=\frac{1}{N_k}\sum_{\mathbf k}w_n(\mathbf k)w_m(\mathbf k+\mathbf q),\\
J(\mathbf q)&=\sum_{n,m}J_{nm}(\mathbf q).
\end{aligned}
$$

下面从存档六条带全部求和，分别合计 n=m 与 n≠m 的项，单位仍为 eV⁻²。不是只保留“穿过 EF”的两条带，也没有假设远离 EF 的高斯尾部严格为零。

| 电子网格 | σ / eV | J(X) | 相同带号配对和 | 不同带号配对和 |
|---|---:|---:|---:|---:|
| 24³ | 0.10 | 0.09968022 | 0.08261356 | 0.01706666 |
| 24³ | 0.20 | 0.06123457 | 0.04361909 | 0.01761549 |
| 32³ | 0.10 | 0.04490039 | 0.04085972 | 0.00404068 |
| 32³ | 0.20 | 0.03678119 | 0.02803631 | 0.00874488 |

在 32³、0.20 eV 这组中，2→2、3→3 的项分别约为 0.02455538、0.00348093 eV⁻²；2→3 与 3→2 各约 0.00437243 eV⁻²。不同带号的几何配对确实存在，但这仍没有说它主要属于哪个原子、哪一层或哪种振动。这里的带号沿用存档的能量排序；遇到交叉或简并时，相同带号也不自动等于同一个连续费米口袋，需要波函数或轨道投影继续追踪。

[CoTe₂ 原文 Fig. 2(b,c)，PDF 第 4 页](https://doi.org/10.1103/l89c-t2s4)为进一步归属提供了具体画法：(b) 在能带上以 Co-d/Te-p 投影着色，(c) 把 0–1 的轨道权重画到费米线上，并标 BZ 边界。要将上面的 2→3 配对说成某两种轨道或层之间的通道，需要这样的逐态投影，随后还要核对对应模式的矩阵元；本例六带能量数组足以做几何配对，不能产生那张彩色投影费米线。

这次加密不仅改变总 J(X)，也改变配对组成。例如 0.10 eV 下不同带号配对和从 0.01706666 降到 0.00404068 eV⁻²；在网格敏感性尚明显时，把一张粗网格费米面上的口袋连线指定为耦合通道还过早。[全部 432 条配对记录](/Atlas/examples/enrichment-20261003/strain/band-pairs.csv)保留 Γ、q=(1/4,0,1/4) 和 X 的六带配对，下面给出求和逻辑、完整源码和实际运行输出。

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

### 把 J 拆成能带配对，核对三种求和

处理顺序是先按存档能量生成每条带的窗口权重，再在同一周期网格平移到 k+q；36 项带配对合计应恢复原 J。FFT 一次得到全部 q，直接平移则在三个指定点独立核对。下载 [band_pair_weights.py](/Atlas/examples/enrichment-20261003/strain/band_pair_weights.py)，可将以下需求交给编程助手：

```text
编写 Python 3+NumPy 程序 band_pair_weights.py，只读解包后 al/fermi/k24-cg 与 k32-cg 中的 fermi-grid.npz、grid-info.json、四份 nesting-GX-s*.csv。核对完整24³/32³六带数组、有限能量、grid和EF一致。按存档定义生成逐带高斯权重，全部六带求和，不额外乘自旋简并。对σ=0.10/0.20 eV计算周期FFT J，逐点核对原Γ–X绝对与归一化CSV，并检查J(0)=mean(W²)、0≤J(q)≤J(0)。在Γ、(1/4,0,1/4)、X分别计算36项J_nm，和直接周期平移求和、FFT互校；保存相同带号与不同带号合计，但不将带号换成轨道/层/模式归属。输出432条配对CSV、12行摘要CSV、JSON和真实运行摘要。新输出目录才允许写入，不重算DFT，不引入占据差/能量分母或EPC矩阵元。
```

<details>
<summary>band_pair_weights.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Resolve original Al J(q) into band pairs without phonon matrix elements."""
from pathlib import Path
import argparse, csv, json
import numpy as np

def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--al-root", type=Path, required=True,
                    help="Extracted al directory containing fermi/k24-cg and k32-cg")
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    if args.output_dir.exists():
        raise FileExistsError("Use a new output directory: " + str(args.output_dir))
    pairs, summaries, checks = [], [], []
    for n in [24, 32]:
        folder = args.al_root / "fermi" / f"k{n}-cg"
        with np.load(folder / "fermi-grid.npz", allow_pickle=False) as saved:
            energies = saved["energy_eV"].copy()
            grid = int(saved["grid"])
            ef = float(saved["fermi_eV"])
        info = json.loads((folder / "grid-info.json").read_text())
        if grid != n or energies.shape != (n, n, n, 6):
            raise ValueError("Expected the archived six-band complete Al grid")
        if not np.all(np.isfinite(energies)) or not np.isfinite(ef):
            raise ValueError("Non-finite energies or Fermi reference")
        if info["nks"] != n**3 or abs(info["fermi_eV"] - ef) > 1e-10:
            raise ValueError("Grid metadata differs")
        for sigma in [0.10, 0.20]:
            band_weight = np.exp(-0.5 * (energies / sigma)**2) / (
                sigma * np.sqrt(2 * np.pi))
            total_weight = band_weight.sum(axis=3)
            transform = np.fft.fftn(total_weight)
            joint = np.fft.ifftn(transform.conj() * transform).real / n**3
            zero = float(joint[0, 0, 0])
            tolerance = 1e-10 * max(1.0, zero)
            if zero <= 0 or np.min(joint) < -tolerance:
                raise ValueError("Invalid joint weight")
            if np.max(joint) > zero + tolerance:
                raise ValueError("Periodic autocorrelation exceeds J(0)")
            if abs(zero - float(np.mean(total_weight**2))) > tolerance:
                raise ValueError("q=0 direct sum differs")
            cut = np.loadtxt(folder / f"nesting-GX-s{sigma:.2f}.csv",
                             delimiter=",", skiprows=1)
            indices = np.arange(n//2 + 1)
            computed = joint[indices, 0, indices]
            if cut.shape != (n//2 + 1, 3):
                raise ValueError("Unexpected stored cut shape")
            if not np.allclose(cut[:, 0], indices/n, rtol=0, atol=1e-12):
                raise ValueError("Stored q coordinates differ")
            if not np.allclose(cut[:, 1], computed, rtol=1e-10, atol=1e-12):
                raise ValueError("Stored absolute J differs from FFT")
            if not np.allclose(cut[:, 2], computed/zero, rtol=1e-10, atol=1e-12):
                raise ValueError("Stored normalized J differs")
            for name, i in [("Gamma", 0), ("quarter", n//4), ("X", n//2)]:
                shift = (i, 0, i)
                shifted = np.roll(band_weight, tuple(-v for v in shift),
                                  axis=(0, 1, 2))
                matrix = (band_weight.reshape(-1, 6).T @
                          shifted.reshape(-1, 6)) / n**3
                direct = float(np.mean(total_weight *
                                       np.roll(total_weight, tuple(-v for v in shift),
                                               axis=(0, 1, 2))))
                total = float(matrix.sum())
                if abs(total - direct) > tolerance or abs(total - joint[shift]) > tolerance:
                    raise ValueError("Band-pair, direct and FFT sums differ")
                diagonal = float(np.trace(matrix))
                offdiagonal = float(matrix[~np.eye(6, dtype=bool)].sum())
                for band_n in range(6):
                    for band_m in range(6):
                        pairs.append({"kmesh": n, "sigma_eV": sigma,
                                      "q_name": name, "q_fraction_b1_plus_b3": i/n,
                                      "initial_band": band_n+1, "final_band": band_m+1,
                                      "J_pair_eV_minus2": float(matrix[band_n, band_m])})
                summaries.append({"kmesh": n, "sigma_eV": sigma,
                                  "q_name": name, "q_fraction_b1_plus_b3": i/n,
                                  "J_eV_minus2": total, "same_band_eV_minus2": diagonal,
                                  "different_band_eV_minus2": offdiagonal,
                                  "J_over_J0": total/zero})
                if name == "X":
                    print(f'{n}^3 sigma={sigma:.2f} eV: J(X)={total:.8f}; '
                          f'same-band={diagonal:.8f}; different-band={offdiagonal:.8f} eV^-2')
            checks.append({"kmesh": n, "sigma_eV": sigma,
                           "fermi_eV": ef, "all_six_bands_used": True,
                           "complete_grid_points": n**3, "stored_cut_reproduced": True,
                           "nonnegative_and_J_not_above_J0": True,
                           "band_pair_direct_FFT_agree": True})
    report = {"source_root": str(args.al_root), "numpy_version": np.__version__,
              "definition": "J_nm(q)=mean_k delta_sigma(E_n(k)-EF) delta_sigma(E_m(k+q)-EF)",
              "units": "eV^-2; all six bands; no added spin factor",
              "scope": "Geometric band-pair weights, not orbital/layer-resolved EPC or static susceptibility",
              "checks": checks, "summaries": summaries}
    args.output_dir.mkdir(parents=True)
    write_csv(args.output_dir / "band-pairs.csv", pairs)
    write_csv(args.output_dir / "band-pair-summary.csv", summaries)
    (args.output_dir / "band-pair-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f'{len(summaries)} q-point summaries; {len(pairs)} band-pair records; '
          'pair/direct/FFT sums, stored cuts and J(q)<=J(0) checked.')
    print("No matrix elements, mode assignment, occupation denominator or DFT calculation added.")

if __name__ == "__main__":
    main()
```

</details>

在解包得到的 al 根目录保存该脚本，运行命令；band-pairs 必须是新目录：

```bash
python3 band_pair_weights.py --al-root . --output-dir band-pairs
```

Talos 用公开包中的原 NPZ 与 CSV 实际读取输出为：

```text
24^3 sigma=0.10 eV: J(X)=0.09968022; same-band=0.08261356; different-band=0.01706666 eV^-2
24^3 sigma=0.20 eV: J(X)=0.06123457; same-band=0.04361909; different-band=0.01761549 eV^-2
32^3 sigma=0.10 eV: J(X)=0.04490039; same-band=0.04085972; different-band=0.00404068 eV^-2
32^3 sigma=0.20 eV: J(X)=0.03678119; same-band=0.02803631; different-band=0.00874488 eV^-2
12 q-point summaries; 432 band-pair records; pair/direct/FFT sums, stored cuts and J(q)<=J(0) checked.
No matrix elements, mode assignment, occupation denominator or DFT calculation added.
```

[12 个 q 点摘要](/Atlas/examples/enrichment-20261003/strain/band-pair-summary.csv)与[检查记录](/Atlas/examples/enrichment-20261003/strain/band-pair-check.json)保留未舍入值。三种求和一致验证的是当前数组、周期索引和配对加法；24³ 与 32³ 的差别仍保留，不能用实现检查替代采样收敛。

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

<figure>
<img src="/Atlas/figures/literature/chen2026-cote2-fig2.png" alt="公开原文 Fig. 2(a–f) 的实际面板" />
<figcaption>Chen、Zhang 与 Zheng，arXiv:2603.22101v2，PDF 第 4 页 Fig. 2(a–f)：CoTe₂ 的轨道投影、最低声子支与两种响应。声子采用 0.018 Ry 展宽；红点大小为 λ，(e,f) 的色条各自标 high/low，没有共同数值标尺。 <a href="https://arxiv.org/pdf/2603.22101v2">论文原文</a>。</figcaption>
</figure>

[Chen、Zhang 与 Zheng，Phys. Rev. B 114, 055413](https://doi.org/10.1103/l89c-t2s4)原文 PDF 第 4 页的 Fig. 2 把同一单层 CoTe₂ 的电子、声子和响应放在一组面板中。(b)的纵轴是 E−EF，蓝/橙投影分别对应 Co-d、Te-p；(c)将同样的轨道权重画到费米线上，色条为 0–1，虚线六角形标出 BZ，双向箭头标的是 (e) 中增强的 q。因此它先用轨道投影识别两个口袋的成分，再检查箭头所连散射是否也出现在响应图中，没有把画出的箭头本身当作矩阵元证据。

(a)在 Γ–M–K–Γ 上画声子，红点大小表示 $\lambda_{\mathbf q\nu}$，不是 Ba₂N Fig. 6(a) 所用的线宽；(d)在扩展二维 BZ 中画最低支 $\omega_{\mathbf q,\nu=1}$，色条单位 meV。(e)是带 EPC 矩阵元的广义静态响应，(f)是去掉矩阵元后的常矩阵元响应，仍含占据差和能量分母，因而都不是本页 J(q)。作者比较的是 (f) 的较宽增强区如何在 (e) 中变成 M–K 附近热点，并与 (d) 的软化位置对应。(e)、(f)各自只标 high/low，不能按颜色相近断言数值相等。该组机制图还明确采用 0.018 Ry 的较大电子展宽来取得正频率；它不是把原正常展宽下的虚频系统验收为稳定。

把这种图法用于异质结，需要在同一倒空间坐标系中准备轨道投影费米线、二维 q 网格和对应模式数据；gnuplot 的二维 pm3d map 可画原网格，叠加 BZ 边界和可核对的 q，而不从曲线截图补造热图。先从本页真实 Al CSV 复现一维 J，再与[费米面](/Atlas/m/fermi-surface/qe/)和[模式线宽](/Atlas/m/phonon-linewidth/qe/)的数据接续，才有条件比较二维峰位。几何权重与模式散射是不同量，不能只画两口袋间的箭头就认定它们负责软化。

本页 J 没有模式指标 ν：给定同一电子谱和 q，它不会知道原子沿哪个方向运动。原生 EPC 则先计算电子态对扰动的矩阵元，再投影到声子本征位移。QE 7.5 的 [elphon.f90](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/elphon.f90)在带求和中保留两个费米能窗口和扰动矩阵元，之后用模式向量收缩得到逐模线宽，并按频率平方与单自旋 DOS 得到 λ；这些信息都不在本页的 fermi-grid.npz 中。

真实 Al 的第二个不可约 q 原件提供了具体对照。在[elph.inp_lambda.2](/Atlas/examples/al/epc-q4/elph_dir/elph.inp_lambda.2)的 0.020 Ry 一档，同一个 q 下打印：

| 模式 | γ / GHz | λ |
|---|---:|---:|
| 1 | 1.96 | 0.0599 |
| 2 | 1.88 | 0.0576 |
| 3 | 23.94 | 0.1845 |

原件的三个模式共享 q 与电子展宽，却有不同线宽；一个不带 ν 的 J(q) 无法替代这三列。第三模线宽约为第一模 12 倍，λ 只约为 3 倍，因为频率与 DOS 归一化也参与比较，单位核对见[线宽页的原始频率和源码换算](/Atlas/m/phonon-linewidth/qe/)。这里没有把 Γ—X 的 0.10/0.20 eV 几何数据配给这份 q 文件：两套 q、窗口定义与电子积分来源须先逐项对齐，不能仅把 eV 换成 Ry 就拿 γ/J 推断矩阵元。

现有 ZrCl₂/Sc₂C 费米面展示可以帮助提出候选口袋，但本例没有提取该体系的完整二维 J(q)，也没有闭合口袋到模式的矩阵元归属。本文因此保留 Al 的真实 J(q) 数据与实现，材料讨论接[费米面](/Atlas/m/fermi-surface/qe/)、[声子线宽](/Atlas/m/phonon-linewidth/qe/)及[应变比较](/Atlas/m/strain-doping-scan/qe/)。只有这些同结构、同 q 的证据成立以后，才能判断软化主要来自几何相空间、矩阵元还是两者共同变化。

## 原文中怎样区分几何权重与响应

<figure>
<div>
<img src="/Atlas/figures/literature/johannes2008-fig4.png" alt="公开原文Fig.4(a,b)实际面板" />
</div>
<figcaption>Johannes 与 Mazin，arXiv:0708.1744，PDF 第 6 页 Fig. 4(a,b)：TaSe₂ 的响应虚部与实部曲面。原图无可读数值轴或共同色条，分别比较峰的位置；不能从颜色恢复绝对响应值。<a href="https://arxiv.org/pdf/0708.1744">论文原文</a>。</figcaption>
</figure>

[Johannes 与 Mazin，Phys. Rev. B 77, 165135，原作者稿 PDF 第 6 页 Fig. 4](https://arxiv.org/pdf/0708.1744#page=6)的 (a) 左图显示 TaSe₂ 与几何嵌套相关的虚部量，(b) 右图显示实部静态响应。同一倒空间中的强嵌套峰与实部弱峰不在同一位置，图注指出后者才对应观察到的 CDW 波矢。原图用倒空间曲面的高度和蓝绿至黄的着色表现响应起伏，但没有可读的 q 轴刻度、数值纵轴或共同色条；两峰位置与 CDW 的关系需结合图注和正文，不能从这张截图标定自己的 K 点或比较绝对高度。本页左侧 J 与右侧 J/J(0) 则是同一几何量的绝对幅值和形状对照，并没有增加一份实部响应。若以后有完整二维数据，可用相同 q 网格、BZ 边界和各自有定义的纵轴或色标并排绘图；仅凭现有 Al Γ—X 切线不能复现原图的二维响应面。

原文式 (2) 用低频极限 $\lim_{\omega\to0}\chi''(\mathbf q,\omega)/\omega$ 定义双 δ 函数几何权重，式 (1) 的静态实部还包含占据数差与能量差。本文的高斯 J(q) 是前述离散双窗口联合权重，保持本例的等权平均和自旋约定；不能重命名为静态 $\operatorname{Im}\chi(\mathbf q,0)$，也不能由它补出 (b) 的响应峰。

想把这项分析用于应变软模，下一步应先取得对应结构的完整均匀电子网格，再按同一定义比较候选 q；Al 的四组数表和曲线仍作为网格与窗口敏感性的操作参照。
