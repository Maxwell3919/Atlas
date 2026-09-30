[QE 电子声子系数与 Tc 公式](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html) · [QE 7.5 lambda.x 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90) · [QE 的 k 网格与展宽检查](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html) · [Allen–Dynes 原论文](https://doi.org/10.1103/PhysRevB.12.905)

这里把两条完整计算链的 Tc 曲线放在一起，实际求交点。材料选用单原子 fcc Al：第一条 `pwxall` 为 32³，第二条在新目录改成 48³；两边都接上 16³ 的 `pwx`、4³ q 网格的 `ph.x` 和各自的 `lambda.x`。两次计算采用同一组结构、赝势和参数，比较时只改变致密电子网格。

<span id="tc-from-double-grid"></span>

## 两个目录各自跑到 lambda.x，再读两份 Tc 表

[完整 EPC 会话](/Atlas/m/epc/qe/#double-grid-pwxall)记录了两条路径，第二条的 `cp`、`vi`、完整 Slurm 脚本及运行结果在 [48³ 分支](/Atlas/m/epc/qe/#dense-k48-run)。这里直接接它们的结果，不重新写一次 SCF。

| 计算路径 | pwxall 致密 k | pwx 响应 k | 实算 q 网格 | 留给本页的原件 |
|---|---|---|---|---|
| `epc-q4` | 32×32×32 | 16×16×16 | 4×4×4，8 个不可约 q | 本目录的 8 个 `elph.inp_lambda.*`、`lambda.in/out/dat` |
| `epc-q4-k48` | 48×48×48 | 16×16×16 | 4×4×4，8 个不可约 q | 新目录独立计算的同组文件 |

两边的 `pwxall` 网格分别是响应网格的 2 倍、3 倍；响应网格又是 q 网格的 4 倍，所有网格均不偏移。`lambda.in` 使用相同的 q 权重、14 THz 谱上限、0.12 THz 频率展宽和 μ*=0.10。横轴 σ 则来自 `ph.x` 的十档电子积分展宽：0.005、0.010、…、0.050 Ry。这三个展宽概念要分开：SCF 占据的 `degauss=0.02 Ry` 没有在本图中扫描，谱函数的 0.12 THz 宽度也没有变化。

第二条链已完成 8 个 q × 3 个模式 × 10 个展宽，共 240 条模式记录。两份响应 SCF 的电荷密度文件逐字节相同，32³ 与 48³ 的致密电子数据则各自保存；第二条从头执行了两次 SCF 和所有 q 响应。原生输入、输出、核验表及本节脚本可[一起下载](/Atlas/examples/supercon-al-tc-files.tar.gz)。解包后的 `k32/`、`k48/` 分别对应这两条路径。

<span id="tc-two-dense-grids"></span>

## 两条 Tc(σ) 曲线与实际求交结果

![Al 32³ 与 48³ 实际 Tc 曲线及其逐点差值 ΔTc](/Atlas/examples/supercon-al-tc/figures/supercon-al-k32-k48-tc-delta.png)

上图每个点都来自对应分支的逐 q EPC 原件。上面把两条 Tc(σ) 放在同一坐标轴，下面画 `ΔTc=Tc₃₂−Tc₄₈`，虚线为零。十个共同采样点的 ΔTc 均为正；相邻点按直线连接后，0.005–0.050 Ry 内没有交点，也没有重合区间。最接近的位置是 σ=0.050 Ry：Tc₃₂=0.984588 K、Tc₄₈=0.975366 K，ΔTc=+0.009222 K。求交程序同时检查原生三位小数 Tc 与逐 q 重建值，结果一致。

随后计算的 64³ 分支已经完成致密与响应 SCF；`ph.x` 因三小时 walltime 到限被取消，仅留下六个逐 q EPC 文件，缺少完整八个 q 的结果和 `lambda.x` 输出。目前图中只有 32³、48³ 两条完整曲线。

[配对数值 CSV](/Atlas/examples/supercon-al-tc/comparison-k32-k48/paired-tc.csv) · [求交结果 JSON](/Atlas/examples/supercon-al-tc/comparison-k32-k48/crossings.json) · [矢量 PDF](/Atlas/examples/supercon-al-tc/figures/supercon-al-k32-k48-tc-delta.pdf) · [SVG](/Atlas/examples/supercon-al-tc/figures/supercon-al-k32-k48-tc-delta.svg) · [完整绘图源码](/Atlas/examples/supercon-al-tc/plot_supercon_tc_difference.py)

<details>
<summary>plot_supercon_tc_difference.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Plot the paired Al k32/k48 Tc curves and their signed difference."""
from __future__ import annotations
import argparse
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"no rows in {path}")
    sigma = [float(r["sigma_Ry"]) for r in rows]
    tc32 = [float(r["Tc_rebuilt_K_A"]) for r in rows]
    tc48 = [float(r["Tc_rebuilt_K_B"]) for r in rows]
    delta_saved = [float(r["delta_Tc_rebuilt_K"]) for r in rows]
    mu = [float(r["mu_star"]) for r in rows]
    if any(not math.isfinite(x) for seq in (sigma, tc32, tc48, delta_saved, mu) for x in seq):
        raise ValueError("non-finite input value")
    if sigma != sorted(sigma) or len(set(sigma)) != len(sigma):
        raise ValueError("sigma values must be strictly increasing")
    if max(mu) - min(mu) > 1e-12:
        raise ValueError("mu* differs between paired rows")
    delta = [a - b for a, b in zip(tc32, tc48)]
    if any(abs(x - y) > 2e-9 for x, y in zip(delta, delta_saved)):
        raise ValueError("stored Delta Tc does not equal Tc32 - Tc48")
    return sigma, tc32, tc48, delta, mu[0]


def intersections(sigma, delta):
    points = []
    intervals = []
    i = 0
    while i < len(delta):
        if delta[i] != 0:
            i += 1
            continue
        j = i
        while j + 1 < len(delta) and delta[j + 1] == 0:
            j += 1
        if j > i:
            intervals.append((sigma[i], sigma[j]))
        else:
            points.append((sigma[i], 0.0))
        i = j + 1
    for i in range(len(delta) - 1):
        if delta[i] * delta[i + 1] < 0:
            x = sigma[i] - delta[i] * (sigma[i + 1] - sigma[i]) / (delta[i + 1] - delta[i])
            points.append((x, 0.0))
    return points, intervals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("comparison-k32-k48/paired-tc.csv"))
    ap.add_argument("--out", type=Path, default=Path("figures"))
    ap.add_argument("--prefix", default="supercon-al-k32-k48-tc-delta")
    args = ap.parse_args()
    sigma, tc32, tc48, delta, mu = read_rows(args.data)
    points, intervals = intersections(sigma, delta)
    args.out.mkdir(parents=True, exist_ok=True)

    blue, vermillion = "#0072B2", "#D55E00"
    fig, (ax_tc, ax_delta) = plt.subplots(
        2, 1, figsize=(7.4, 6.1), sharex=True,
        gridspec_kw={"height_ratios": [1.55, 1.0], "hspace": 0.08},
        layout="constrained",
    )
    ax_tc.plot(sigma, tc32, color=blue, marker="o", ms=5, lw=1.8,
               label=r"$32^3$ dense $k$ mesh")
    ax_tc.plot(sigma, tc48, color=vermillion, marker="s", ms=5, lw=1.8,
               ls="--", label=r"$48^3$ dense $k$ mesh")
    ax_tc.set_ylabel(r"$T_c$ (K)")
    ax_tc.set_ylim(0, max(tc32 + tc48) * 1.12)
    ax_tc.legend(frameon=False, ncol=2, loc="upper right")
    ax_tc.text(0.02, 0.94, rf"$\mu^*= {mu:.2f}$; {len(sigma)} calculated widths",
               transform=ax_tc.transAxes, va="top", fontsize=9)

    ax_delta.axhline(0, color="#333333", lw=1.15, ls=(0, (4, 2)), zorder=4)
    ax_delta.plot(sigma, delta, color="#6A3D9A", marker="D", ms=4.5, lw=1.7)
    ax_delta.fill_between(sigma, 0, delta, where=[d >= 0 for d in delta],
                          color="#6A3D9A", alpha=0.10, interpolate=True)
    for x, y in points:
        ax_tc.scatter([x], [y], s=50, facecolor="white", edgecolor="#111111", zorder=5)
        ax_delta.scatter([x], [y], s=45, facecolor="white", edgecolor="#111111", zorder=5)
    ax_delta.set_ylabel(r"$\Delta T_c=T_c(32^3)-T_c(48^3)$ (K)")
    ax_delta.set_xlabel(r"Electronic smearing $\sigma$ (Ry)")
    ax_delta.set_xlim(min(sigma) - 0.002, max(sigma) + 0.002)
    ax_delta.xaxis.set_major_locator(MultipleLocator(0.005))
    span = max(delta) - min(delta)
    lo = min(0.0, min(delta)) - 0.24 * span
    hi = max(0.0, max(delta)) + 0.16 * span
    ax_delta.set_ylim(lo, hi)
    if points or intervals:
        summary = f"{len(points)} isolated crossing(s), {len(intervals)} overlap interval(s)"
    else:
        min_i = min(range(len(delta)), key=delta.__getitem__)
        summary = ("No crossing in sampled range; "
                   rf"min $\Delta T_c={delta[min_i]:.6f}$ K at $\sigma={sigma[min_i]:.3f}$ Ry")
    ax_delta.text(0.02, 0.94, summary, transform=ax_delta.transAxes,
                  va="top", fontsize=8.7)
    for ax in (ax_tc, ax_delta):
        ax.grid(axis="both", color="#B7B7B7", alpha=0.28, lw=0.65)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(direction="out", length=3.5, width=0.8)
    fig.suptitle("Al: paired dense-mesh Allen–Dynes results", fontsize=12, y=1.015)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(args.out / f"{args.prefix}.{ext}", dpi=320 if ext == "png" else None,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"rows={len(sigma)}; mu*={mu:.2f}; isolated crossings={len(points)}; overlap intervals={len(intervals)}")
    print(f"delta_min_K={min(delta):.9f}; delta_max_K={max(delta):.9f}")
    print(f"saved {args.out / (args.prefix + '.png')}, .svg, .pdf")


if __name__ == "__main__":
    main()
```

</details>

## 在解包目录把两份输出配起来

前一个脚本从八个逐 q 原件重新求和，检查文件头的 q 坐标、权重、展宽、DOS(EF)、模式编号，以及结果是否与原生 λ、ωlog、Tc 的打印精度相符。后一个脚本把两边实际写出的 σ 一一配对，保留原生 Tc 与重建值，计算差值并找出所有交点。QE 7.5 `lambda.x` 源码中的 q 坐标检查被注释掉了；本页的重建脚本逐文件检查坐标和输入顺序，允许六位小数输出带来的舍入差。

两个求和都使用星权重 `1, 8, 4, 6, 24, 12, 3, 6`，总和 64。程序以总权重归一化，每一档展宽独立求出 λ 和谱函数。计算 Tc 时使用输出括号外的逐 q 加权 λ；括号内的谱积分 λ 用来核对谱积分，不能换掉这一列后继续引用原来的 Tc。

### 交给代码助手的 Tc 配对、求交与绘图任务

> 读取 k32/、k48/ 各自的 lambda.in、lambda.out 和八个 elph.inp_lambda 文件，只做保存数据的后处理。核对 q 坐标、顺序、权重、展宽与 μ*，按 QE 7.5 lambda.x 的公式分别重建两条 Tc(σ)，并检查原生打印精度。按相同 σ 配对，保存 Tc、λ、ωlog 和逐点 ΔTc。用相邻点的线性差值找出采样范围内所有孤立交点、端点交点和重合区间；若没有交点，明确输出零个，不外推。绘制上方两条 Tc 曲线、下方 ΔTc 与零线，保留十个采样点，用颜色、线型和标记区分分支。保存配对 CSV、求交 JSON、PNG/SVG/PDF 及可独立运行的完整 Python 源码，写明依赖和输入路径；不启动 QE 程序。

已有完整源码：[rebuild_tc.py](/Atlas/examples/supercon-al-tc/rebuild_tc.py)、[compare_tc.py](/Atlas/examples/supercon-al-tc/compare_tc.py)、[plot_supercon_tc_difference.py](/Atlas/examples/supercon-al-tc/plot_supercon_tc_difference.py)。

下载包内已经保留计算结果。在解包目录用完整的 [重建脚本 `rebuild_tc.py`](/Atlas/examples/supercon-al-tc/rebuild_tc.py) 与[配对求交脚本 `compare_tc.py`](/Atlas/examples/supercon-al-tc/compare_tc.py) 复算表格；这里运行的是读取与求交程序，前面的两次 DFT 计算已在 Maxwell 完成。

```console
$ python3 rebuild_tc.py k32 k48 --outdir comparison-k32-k48
k32:10sigma rows reconstructed; native lambda/omega/Tc match their printed precision
k48:10sigma rows reconstructed; native lambda/omega/Tc match their printed precision
$ python3 compare_tc.py --a k32 --b k48 --out comparison-k32-k48
Paired branches: k32 / k48; 10 common sigma points; mu*=0.10
sigma_Ry  Tc_A_native_K  Tc_B_native_K  Delta_Tc_rebuilt_K
   0.005          2.212          1.687        +0.525165797
   0.010          0.916          0.898        +0.017265344
   0.015          0.900          0.883        +0.017302112
   0.020          0.969          0.854        +0.114568219
   0.025          0.971          0.849        +0.122035939
   0.030          0.955          0.868        +0.086939421
   0.035          0.949          0.896        +0.053537300
   0.040          0.955          0.925        +0.030184671
   0.045          0.969          0.952        +0.017352448
   0.050          0.985          0.975        +0.009221798
All in-range intersections, reconstructed from native elph inputs:
No isolated crossing in the sampled range.
Native 0.001 K print check: 0 isolated points, 0 overlap intervals.
Saved paired-tc.csv, crossings.csv, crossings.json.
```

[重建脚本](/Atlas/examples/supercon-al-tc/rebuild_tc.py) · [配对与求交脚本](/Atlas/examples/supercon-al-tc/compare_tc.py) · [完整配对核验](/Atlas/examples/supercon-al-tc/comparison-k32-k48/crossings.json)

<details>
<summary>rebuild_tc.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Rebuild the QE7.5 lambda.x result from its native elph input files. No QE executable is run."""

import argparse, csv, hashlib, json, math, re
from pathlib import Path

NUMBER = r"[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?"
num = lambda x: float(x.replace("D", "E").replace("d", "e"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def reconstruct(root):
    root = Path(root)
    lines = [
        l.split("!")[0].strip()
        for l in (root / "lambda.in").read_text().splitlines()
        if l.split("!")[0].strip()
    ]
    emax, width, order = map(float, lines[0].split())
    assert order == 0, "This script supports the actual simple-Gaussian spectrum only"
    nq = int(lines[1])
    qs = [list(map(float, l.split())) for l in lines[2 : 2 + nq]]
    names = lines[2 + nq : 2 + 2 * nq]
    mu = float(lines[2 + 2 * nq])
    totalweight = sum(q[3] for q in qs)
    native = (root / "lambda.out").read_text()
    details = re.findall(
        r"lambda\s*=\s*("
        + NUMBER
        + r")\s*\(\s*("
        + NUMBER
        + r")\s*\)\s*<log w>=\s*("
        + NUMBER
        + r")\s*K\s*N\(Ef\)=\s*("
        + NUMBER
        + r")\s*at degauss=\s*("
        + NUMBER
        + r")",
        native,
    )
    printed = [
        list(map(num, line.split()))
        for line in native.split("T_c")[-1].strip().splitlines()
        if len(line.split()) == 3
    ]
    assert len(details) == len(printed) == 10
    n = 2000
    step = emax / (n - 1)
    freq = [i * step for i in range(n)]
    lq = [0.0] * 10
    a2f = [[0.0] * n for _ in range(10)]
    sigma0 = None
    dos0 = None
    ef0 = None
    hashes = {p: sha(root / p) for p in ["lambda.in", "lambda.out"]}
    qcheck = []
    for iq, (qinfo, name) in enumerate(zip(qs, names), 1):
        p = root / name
        hashes[name] = sha(p)
        records = p.read_text().splitlines()
        head = records[0].split()
        qread = list(map(num, head[:3]))
        ns, nm = map(int, head[3:])
        w2 = list(map(num, records[1].split()))
        assert ns == 10 and nm == 3 and len(w2) == 3 and min(w2) >= 0
        coordinate_error = max(abs(x - y) for x, y in zip(qinfo[:3], qread))
        assert (
            coordinate_error <= 5.005e-7
        ), "q differs beyond its six-decimal output rounding"
        weight = qinfo[3] / totalweight
        sig = []
        doses = []
        efs = []
        for j in range(ns):
            k = 2 + j * (nm + 2)
            sm = re.search(
                r"Gaussian Broadening:\s*(" + NUMBER + r") Ry, ngauss=\s*(-?\d+)",
                records[k],
            )
            sigma = num(sm.group(1))
            assert int(sm.group(2)) == 0
            d = re.search(
                r"DOS =\s*(" + NUMBER + r").*at Ef=\s*(" + NUMBER + r")", records[k + 1]
            )
            dos, ef = map(num, d.groups())
            sig.append(sigma)
            doses.append(dos)
            efs.append(ef)
            for im in range(nm):
                m = re.search(
                    r"lambda\(\s*(\d+)\)=\s*("
                    + NUMBER
                    + r")\s*gamma=\s*("
                    + NUMBER
                    + r")",
                    records[k + im + 2],
                )
                assert int(m.group(1)) == im + 1
                lam = num(m.group(2))
                om = math.sqrt(w2[im]) * 3289.828
                lq[j] += weight * lam
                coefficient = weight * lam * om * 0.5 / math.sqrt(math.pi) / width
                for i, e in enumerate(freq):
                    a2f[j][i] += coefficient * math.exp(
                        -min(200.0, ((e - om) / width) ** 2)
                    )
        if sigma0 is None:
            sigma0, dos0, ef0 = sig, doses, efs
        else:
            assert (
                sig == sigma0 and doses == dos0 and efs == ef0
            ), "Sigma/DOS/EF metadata mismatch between q files"
        qcheck.append(
            {
                "q_index": iq,
                "q_lambda_in": qinfo[:3],
                "q_elph": qread,
                "weight": qinfo[3],
                "coordinate_error": coordinate_error,
            }
        )
    rows = []
    for j, detail in enumerate(details):
        lp, l2p, wp, dosp, sigmap = map(num, detail)
        assert sigmap == sigma0[j]
        l2 = 2 * step * sum(a2f[j][i] / freq[i] for i in range(1, n))
        wlog = (
            math.exp(
                2
                * step
                * sum(a2f[j][i] * math.log(freq[i]) / freq[i] for i in range(1, n))
                / l2
            )
            * 47.9924
        )
        value = (
            wlog
            / 1.2
            * math.exp(-1.04 * (1 + lq[j]) / (lq[j] - mu * (1 + 0.62 * lq[j])))
        )
        assert (
            abs(lp - lq[j]) <= 0.500001e-6
            and abs(l2p - l2) <= 0.500001e-6
            and abs(wp - wlog) <= 0.500001e-3
        )
        assert (
            abs(printed[j][2] - value) <= 0.500001e-3
        ), "Reconstruction does not round to native Tc"
        rows.append(
            {
                "sigma_Ry": sigmap,
                "mu_star": mu,
                "lambda_qsum": lq[j],
                "lambda_spectrum": l2,
                "omega_log_K": wlog,
                "N_EF": dosp,
                "N_EF_unit": "states/spin/Ry/cell",
                "Tc_K": value,
                "native_printed_Tc_K": printed[j][2],
                "native_lambda_6dp": lp,
                "native_lambda_spectrum_6dp": l2p,
                "native_omega_log_K_3dp": wp,
                "EF_eV": ef0[j],
            }
        )
    metadata = {
        "source_sha256": hashes,
        "q_pairing": qcheck,
        "q_weight_sum": totalweight,
        "nq": nq,
        "spectrum_points": n,
        "spectrum_max_THz": emax,
        "spectrum_gaussian_width_THz": width,
        "mu_star": mu,
        "formula": "Tc=omega_log/1.2*exp(-1.04*(1+lambda_qsum)/(lambda_qsum-mu_star*(1+0.62*lambda_qsum)))",
        "frequency_constants": "3289.828THz/Ry;47.9924K/THz, matching QE7.5lambda.f90",
        "precision_scope": "Reconstruction of lambda.x from the exact printed elph records, not recovery of unprinted DFT precision. Mode lambda is stored to4decimals; final native Tc is printed to3decimals.",
        "source": "https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90",
        "no_QE_executable_run": True,
    }
    return rows, metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "branches",
        nargs="+",
        type=Path,
        help="Directories containing lambda.in/lambda.out/elph_dir",
    )
    p.add_argument("--outdir", type=Path, default=Path("."))
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    for branch in args.branches:
        rows, meta = reconstruct(branch)
        name = branch.name
        with (args.outdir / (name + "-rebuilt.csv")).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        (args.outdir / (name + "-rebuild-checks.json")).write_text(
            json.dumps(meta, indent=2) + "\n"
        )
        print(
            name
            + ":10sigma rows reconstructed; native lambda/omega/Tc match their printed precision"
        )


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>compare_tc.py 的完整源码</summary>

```python
"""Pair two complete QE lambda.x branches and find straight-segment crossings.

Example, after both independent calculations have completed:
    python3 compare_tc.py --a k32 --b k48 --out comparison

Only Python's standard library is required. Keep rebuild_tc.py beside this
script. Curves reconstructed from lambda.x's actual elph inputs retain the
digits lost by its final 0.001 K printing. Printed Tc and a cross-check from
the printed moments are reported separately, without editing native files.
"""

from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
from rebuild_tc import reconstruct

NUMBER = r"[-+0-9.eEdD]+"
MOMENT = re.compile(
    rf"lambda\s*=\s*({NUMBER})\s*\(\s*({NUMBER})\s*\)\s*"
    rf"<log w>\s*=\s*({NUMBER})\s*K\s*N\(Ef\)\s*=\s*({NUMBER})"
    rf"\s*at degauss=\s*({NUMBER})"
)


def number(value):
    result = float(value.replace("D", "E").replace("d", "e"))
    if not math.isfinite(result):
        raise ValueError("Non-finite native value")
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_branch(path):
    text = (path / "lambda.out").read_text()
    rows = []
    for m in MOMENT.finditer(text):
        lam, spectral_lam, omega, nef, sigma = map(number, m.groups())
        rows.append(
            dict(
                sigma_Ry=sigma,
                lambda_qsum=lam,
                lambda_spectrum=spectral_lam,
                omega_log_K=omega,
                N_Ef_native=nef,
            )
        )
    sections = re.split(r"lambda\s+omega_log\s+T_c", text)
    if len(sections) != 2 or not rows:
        raise ValueError(f"{path}: expected one native Tc table")
    table = []
    for line in sections[1].splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 3 or not all(re.fullmatch(NUMBER, x) for x in fields):
            raise ValueError(f"{path}: unexpected native Tc row: {line}")
        table.append(list(map(number, fields)))
    if len(table) != len(rows):
        raise ValueError(f"{path}: incomplete moment/Tc pairing")
    sigmas = [r["sigma_Ry"] for r in rows]
    if len(set(sigmas)) != len(sigmas) or sigmas != sorted(sigmas):
        raise ValueError(f"{path}: duplicated or unordered sigma points")
    input_lines = [
        x.split("!")[0].strip() for x in (path / "lambda.in").read_text().splitlines()
    ]
    input_lines = [x for x in input_lines if x]
    mu = number(input_lines[-1])
    for row, (lam, omega, tc) in zip(rows, table):
        # These bounds follow the native five/three-place output formats.
        if abs(row["lambda_qsum"] - lam) > 0.0000051 or row["omega_log_K"] != omega:
            raise ValueError(f"{path}: lambda/Tc table rows do not correspond")
        denominator = row["lambda_qsum"] - mu * (1 + 0.62 * row["lambda_qsum"])
        if denominator <= 0 or omega <= 0 or tc < 0:
            raise ValueError(f"{path}: formula outside the supported positive regime")
        recomputed = (
            omega / 1.2 * math.exp(-1.04 * (1 + row["lambda_qsum"]) / denominator)
        )
        if abs(recomputed - tc) > 0.00055:
            raise ValueError(
                f"{path}: printed moments do not reproduce native Tc rounding"
            )
        row.update(mu_star=mu, Tc_printed_K=tc, Tc_printed_moments_K=recomputed)
    dat = []
    for line in (path / "lambda.dat").read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            dat.append(list(map(number, line.split())))
    if len(dat) != len(rows):
        raise ValueError(f"{path}: lambda.dat count mismatch")
    for row, fields in zip(rows, dat):
        expected = [
            row[k]
            for k in (
                "sigma_Ry",
                "lambda_qsum",
                "lambda_spectrum",
                "omega_log_K",
                "N_Ef_native",
            )
        ]
        if fields != expected:
            raise ValueError(f"{path}: lambda.dat differs from stdout")
    return rows, {
        n: digest(path / n) for n in ("lambda.in", "lambda.out", "lambda.dat")
    }


def crossings(x, a, b):
    """Return all isolated sampled zeros, sign changes and overlap intervals."""
    difference = [y - z for y, z in zip(a, b)]
    overlaps = []
    overlap_indices = set()
    for i in range(len(x) - 1):
        if difference[i] == 0 and difference[i + 1] == 0:
            if overlaps and overlaps[-1]["right_index"] == i:
                overlaps[-1].update(sigma_hi_Ry=x[i + 1], right_index=i + 1)
            else:
                overlaps.append(
                    dict(
                        kind="overlap",
                        sigma_lo_Ry=x[i],
                        sigma_hi_Ry=x[i + 1],
                        left_index=i,
                        right_index=i + 1,
                    )
                )
            overlap_indices.update((i, i + 1))
    points = []
    for i, d in enumerate(difference):
        if d == 0 and i not in overlap_indices:
            points.append(
                dict(
                    kind="sampled_equality",
                    sigma_Ry=x[i],
                    Tc_K=a[i],
                    sigma_lo_Ry=x[i],
                    sigma_hi_Ry=x[i],
                    delta_lo_K=0.0,
                    delta_hi_K=0.0,
                )
            )
    for i, (d1, d2) in enumerate(zip(difference, difference[1:])):
        if d1 * d2 < 0:
            t = -d1 / (d2 - d1)
            xc = x[i] + t * (x[i + 1] - x[i])
            ya = a[i] + t * (a[i + 1] - a[i])
            yb = b[i] + t * (b[i + 1] - b[i])
            if not x[i] < xc < x[i + 1] or abs(ya - yb) > 1e-12:
                raise ValueError("Crossing interpolation arithmetic failed")
            points.append(
                dict(
                    kind="segment_crossing",
                    sigma_Ry=xc,
                    Tc_K=ya,
                    sigma_lo_Ry=x[i],
                    sigma_hi_Ry=x[i + 1],
                    delta_lo_K=d1,
                    delta_hi_K=d2,
                )
            )
    points.sort(key=lambda r: r["sigma_Ry"])
    for i, p in enumerate(points, 1):
        p["id"] = f"C{i}"
    return dict(points=points, overlap_intervals=overlaps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", type=Path, default=Path("k32"))
    parser.add_argument("--b", type=Path, default=Path("k48"))
    parser.add_argument("--out", type=Path, default=Path("comparison"))
    args = parser.parse_args()
    a, ha = load_branch(args.a)
    b, hb = load_branch(args.b)
    xa = [r["sigma_Ry"] for r in a]
    xb = [r["sigma_Ry"] for r in b]
    if xa != xb or {r["mu_star"] for r in a + b} != {a[0]["mu_star"]}:
        raise ValueError("Branches must have identical native sigma values and mu_star")
    # This reconstruction follows the actual QE 7.5 simple-Gaussian inputs.
    # Its own checks compare each result with native output-format precision.
    precise_a, checks_a = reconstruct(args.a)
    precise_b, checks_b = reconstruct(args.b)
    for native, precise in ((a, precise_a), (b, precise_b)):
        if len(native) != len(precise):
            raise ValueError("Incomplete raw-input reconstruction")
        for record, exact in zip(native, precise):
            if (record["sigma_Ry"], record["mu_star"]) != (
                exact["sigma_Ry"],
                exact["mu_star"],
            ):
                raise ValueError(
                    "Raw-input reconstruction is not paired with the native table"
                )
            record.update(
                Tc_rebuilt_K=exact["Tc_K"],
                lambda_qsum_rebuilt=exact["lambda_qsum"],
                lambda_spectrum_rebuilt=exact["lambda_spectrum"],
                omega_log_rebuilt_K=exact["omega_log_K"],
            )
    paired = []
    for ra, rb in zip(a, b):
        row = {"sigma_Ry": ra["sigma_Ry"], "mu_star": ra["mu_star"]}
        for tag, record in [("A", ra), ("B", rb)]:
            row.update({k + "_" + tag: v for k, v in record.items() if k not in row})
        row["delta_Tc_printed_K"] = ra["Tc_printed_K"] - rb["Tc_printed_K"]
        row["delta_Tc_printed_moments_K"] = (
            ra["Tc_printed_moments_K"] - rb["Tc_printed_moments_K"]
        )
        row["delta_Tc_rebuilt_K"] = ra["Tc_rebuilt_K"] - rb["Tc_rebuilt_K"]
        paired.append(row)
    printed = crossings(
        xa, [r["Tc_printed_K"] for r in a], [r["Tc_printed_K"] for r in b]
    )
    reconstructed = crossings(
        xa,
        [r["Tc_printed_moments_K"] for r in a],
        [r["Tc_printed_moments_K"] for r in b],
    )
    raw = crossings(xa, [r["Tc_rebuilt_K"] for r in a], [r["Tc_rebuilt_K"] for r in b])
    report = {
        "branch_A": args.a.name,
        "branch_B": args.b.name,
        "points_per_branch": len(a),
        "mu_star": a[0]["mu_star"],
        "branch_A_hashes": ha,
        "branch_B_hashes": hb,
        "branch_A_rebuild_checks": checks_a,
        "branch_B_rebuild_checks": checks_b,
        "raw_input_reconstruction": raw,
        "native_printed_curves": printed,
        "printed_moment_crosscheck": reconstructed,
        "native_output_files_identical": ha["lambda.out"] == hb["lambda.out"],
        "scope": "All in-range straight-segment intersections; no fit or extrapolation. The plotted curves are reconstructed from exact elph inputs to lambda.x, whose final Tc print precision is 0.001 K. Reconstruction does not recover unprinted DFPT precision. Source files alone do not establish matched protocols: inspect the accompanying independent run review.",
        "scientific_convergence": "not assessed by this postprocessor",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "paired-tc.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    (args.out / "crossings.json").write_text(json.dumps(report, indent=2) + "\n")
    with (args.out / "crossings.csv").open("w", newline="") as f:
        fields = [
            "id",
            "kind",
            "sigma_Ry",
            "Tc_K",
            "sigma_lo_Ry",
            "sigma_hi_Ry",
            "delta_lo_K",
            "delta_hi_K",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(raw["points"])
    print(
        f'Paired branches: {args.a.name} / {args.b.name}; {len(a)} common sigma points; mu*={a[0]["mu_star"]:.2f}'
    )
    print("sigma_Ry  Tc_A_native_K  Tc_B_native_K  Delta_Tc_rebuilt_K")
    for row in paired:
        print(
            f'{row["sigma_Ry"]:8.3f}  {row["Tc_printed_K_A"]:13.3f}  {row["Tc_printed_K_B"]:13.3f}  {row["delta_Tc_rebuilt_K"]:+18.9f}'
        )
    print("All in-range intersections, reconstructed from native elph inputs:")
    for p in raw["points"]:
        print(
            f'{p["id"]}: sigma={p["sigma_Ry"]:.9f} Ry; Tc={p["Tc_K"]:.9f} K; bracket=[{p["sigma_lo_Ry"]:.3f}, {p["sigma_hi_Ry"]:.3f}] Ry'
        )
    if not raw["points"]:
        print("No isolated crossing in the sampled range.")
    if raw["overlap_intervals"]:
        print("Overlap intervals:", json.dumps(raw["overlap_intervals"]))
    print(
        f'Native 0.001 K print check: {len(printed["points"])} isolated points, {len(printed["overlap_intervals"])} overlap intervals.'
    )
    print("Saved paired-tc.csv, crossings.csv, crossings.json.")


if __name__ == "__main__":
    main()
```

</details>

## 从逐点差值求出交点

令 `dᵢ = Tc₃₂(σᵢ) − Tc₄₈(σᵢ)`。相邻两个采样点的差值异号时，两条折线在这一区间相交：

```text
σ*  = σᵢ − dᵢ × (σᵢ₊₁ − σᵢ) / (dᵢ₊₁ − dᵢ)
Tc* = Tc₃₂(σᵢ) + [Tc₃₂(σᵢ₊₁) − Tc₃₂(σᵢ)] × (σ* − σᵢ) / (σᵢ₊₁ − σᵢ)
```

这次共同采样范围内没有产生孤立交点，因此没有可代入本式的变号区间。

脚本也保留恰落在采样点上的交点；若相邻采样点连续相等，则记录重合区间。原生打印值、由打印 λ/ωlog 复算的曲线和逐 q 原件重建的曲线分别保存在 JSON 中，方便核对舍入是否改变了交点数或位置。

折线交点表示两条 Tc(σ) 在给定展宽处相等。本页保留这一双网格比较结果；网格收敛还需固定 σ 改变 k/q 网格。[EPW 方程页](/Atlas/m/epw-eliashberg/qe/)则通过各向同性线性化 Eliashberg 方程本征值穿过 1 来确定临界温度。

## 再看两条路径的 λ 与 ωlog

![两条 Al 致密网格分支的 λ 和对数平均频率](/Atlas/examples/supercon-al-tc/figures/al-k32-k48-moments.png)

[矢量 PDF](/Atlas/examples/supercon-al-tc/figures/al-k32-k48-moments.pdf) · [SVG](/Atlas/examples/supercon-al-tc/figures/al-k32-k48-moments.svg)

例如，在实际采样的 σ=0.050 Ry 处，32³ 与 48³ 的 λ 分别为 0.376041、0.375505，ωlog 分别为 340.145、340.031 K。本例在十个采样点上，48³ 的 λ 与 ωlog 都低于 32³，二者使 Tc 向同一方向变化。这组数据没有出现两项误差相互抵消形成交点的情况。

本例固定了响应网格和 q 网格；32³ 与 48³ 的致密采样没有交点，不能从中指定一个交点 Tc。QE 官方手册要求检查 k 网格和 Gaussian 展宽，[开发者的说明](https://lists.quantum-espresso.org/pipermail/users/2003-September/000602.html)进一步强调固定 σ 的 k 收敛及稳定区向小展宽延伸。若改变真实 q 网格，还要重新核对 k 与展宽。

## 用谱形、λ 和 ωlog 解释曲线差异

两条 Tc 曲线来自同一公式，差异可以沿 α²F(ω)、耦合积分 λ 和频率矩 ωlog 向上追溯。Poncé 等人的 EPW 论文第 10.3 节、图 12 分别比较 Pb 的采样网格、谱形与 λ，并在充分采样后检查展宽依赖；这里沿用这种分开查看谱与积分的方式，补充解释上面的 Al 双曲线结果。[EPW 论文](https://doi.org/10.1016/j.cpc.2016.07.028)。

本例在相同的十个 σ=0.005–0.050 Ry 上配对 32³ 和 48³ 致密 k 网格的原生 alpha2F.dat。逐频率谱差使用 λ 加权的 L1 距离：
L1λ = ∫₀¹⁴ 2|α²F₃₂(ω)−α²F₄₈(ω)|/ω dω；
表中百分比为 L1λ 除以两条 λspec 的平均值。ω=0 点两谱均为零，积分从原生 2000 个频率点（0–14 THz）计算，不平滑、不外推。Δ 列统一为 32³−48³。

| σ (Ry) | 谱差 L1 / 平均 λspec (%) | Δλq | Δωlog (K) | ΔTc (K) |
|---:|---:|---:|---:|---:|
| 0.005 | 35.5188 | +0.018134 | +16.061 | +0.525166 |
| 0.010 | 17.5246 | +0.000072 | +6.072 | +0.017265 |
| 0.015 | 10.4822 | +0.000775 | +1.949 | +0.017302 |
| 0.020 | 5.5562 | +0.006981 | +1.118 | +0.114568 |
| 0.025 | 3.1187 | +0.007491 | +0.939 | +0.122036 |
| 0.030 | 1.9265 | +0.005323 | +0.722 | +0.086939 |
| 0.035 | 1.1384 | +0.003248 | +0.492 | +0.053537 |
| 0.040 | 0.6381 | +0.001806 | +0.312 | +0.030185 |
| 0.045 | 0.3612 | +0.001022 | +0.204 | +0.017352 |
| 0.050 | 0.1903 | +0.000536 | +0.114 | +0.009222 |

σ=0.010 Ry 时，λq 分别为 0.371061（32³）和 0.370989（48³），Δλq 为 +0.000072；谱 L1 为 17.52%，Δωlog 为 +6.072 K。两条谱的权重分布仍有差异，尽管总 λ 很接近。沿这组展宽扫描，谱 L1 从 35.52% 降至 0.19%。这项谱检查解释了相同 σ 下的上游输入差异。

谱数组 alpha2F.dat 以五位小数保存；λq、λspec、ωlog 和 Tc 则由逐 q 的 elph.inp_lambda 原件按 QE 7.5 算法复建。把保存谱直接积分与逐 q 重建的 λspec 对照，最大差为 4.13×10⁻⁶，符合 alpha2F.dat 的打印精度边界。更多有效位用于复算，不代表材料量的物理精度。

[十个展宽的完整数值表](/Atlas/examples/supercon-al-tc/comparison-k32-k48/spectral-grid-differences.csv) · [分析摘要与输入 SHA-256](/Atlas/examples/supercon-al-tc/comparison-k32-k48/spectral-grid-summary.json) · [完整后处理源码](/Atlas/examples/supercon-al-tc/compare_spectral_grids.py) · [Tc 配对与交点核验](/Atlas/examples/supercon-al-tc/comparison-k32-k48/crossings.json)

<details>
<summary>compare_spectral_grids.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Quantify Al k32/k48 Eliashberg spectral and moment differences; no plotting."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read_a2f(path: Path):
    lines = path.read_text().splitlines()
    header = next((line.split() for line in lines if line.strip()), None)
    if not header or len(header) < 3:
        raise ValueError(f"{path}: missing frequency/sigma header")
    sigmas = [float(x) for x in header[2:]]
    groups = {sigma: [] for sigma in sigmas}
    for line in lines[1:]:
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        values = [float(x) for x in parts]
        if len(values) != len(sigmas) + 1 or any(not math.isfinite(x) for x in values):
            raise ValueError(f"{path}: malformed/non-finite alpha2F row")
        for sigma, a2f in zip(sigmas, values[1:]):
            groups[sigma].append((values[0], a2f))
    for sigma, rows in groups.items():
        xs = [r[0] for r in rows]
        if len(rows) < 2 or any(b <= a for a, b in zip(xs, xs[1:])):
            raise ValueError(f"{path}: invalid frequency axis at sigma={sigma}")
    return groups

def trapezoid(xs, ys):
    return sum((xs[i] - xs[i - 1]) * (ys[i] + ys[i - 1]) / 2 for i in range(1, len(xs)))

def read_pairs(path: Path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return {float(r["sigma_Ry"]): r for r in rows}

def signed_summary(values):
    return {"min": min(values), "max": max(values), "max_abs": max(abs(v) for v in values)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True, help="supercon-al-tc package root")
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args()
    root, outdir = a.root, a.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    path32, path48 = root / "k32/alpha2F.dat", root / "k48/alpha2F.dat"
    s32, s48 = read_a2f(path32), read_a2f(path48)
    paired_path = root / "comparison-k32-k48/paired-tc.csv"
    paired = read_pairs(paired_path)
    sigmas = sorted(set(s32) & set(s48) & set(paired))
    if len(sigmas) != 10 or set(sigmas) != set(s32) or set(sigmas) != set(s48) or set(sigmas) != set(paired):
        raise ValueError("Expected exactly ten common sigma samples in both alpha2F files and paired Tc table")
    result_rows = []
    max_rounded_spectrum_lambda_mismatch = 0.0
    for sigma in sigmas:
        left, right = s32[sigma], s48[sigma]
        if [x[0] for x in left] != [x[0] for x in right]:
            raise ValueError(f"Frequency grids differ at sigma={sigma}")
        row = paired[sigma]
        xs = [r[0] for r in left]
        diff_integrand = [0.0 if x == 0.0 else 2.0 * abs(l[1] - r[1]) / x for x, l, r in zip(xs, left, right)]
        l1 = trapezoid(xs, diff_integrand)
        max_idx = max(range(len(xs)), key=lambda i: abs(left[i][1] - right[i][1]))
        # The native alpha2F.dat prints five decimals; this integral diagnoses spectral-shape
        # differences from that saved output and is not substituted for lambda.x's full-precision moments.
        lam_a2f_32 = trapezoid(xs, [0.0 if x == 0.0 else 2.0 * r[1] / x for x, r in zip(xs, left)])
        lam_a2f_48 = trapezoid(xs, [0.0 if x == 0.0 else 2.0 * r[1] / x for x, r in zip(xs, right)])
        max_rounded_spectrum_lambda_mismatch = max(
            max_rounded_spectrum_lambda_mismatch,
            abs(lam_a2f_32 - float(row["lambda_spectrum_rebuilt_A"])),
            abs(lam_a2f_48 - float(row["lambda_spectrum_rebuilt_B"])),
        )
        record = {
            "sigma_Ry": sigma,
            "lambda_qsum_32": float(row["lambda_qsum_rebuilt_A"]),
            "lambda_qsum_48": float(row["lambda_qsum_rebuilt_B"]),
            "delta_lambda_qsum_32_minus_48": float(row["lambda_qsum_rebuilt_A"]) - float(row["lambda_qsum_rebuilt_B"]),
            "lambda_spectrum_32": float(row["lambda_spectrum_rebuilt_A"]),
            "lambda_spectrum_48": float(row["lambda_spectrum_rebuilt_B"]),
            "delta_lambda_spectrum_32_minus_48": float(row["lambda_spectrum_rebuilt_A"]) - float(row["lambda_spectrum_rebuilt_B"]),
            "weighted_L1_spectral_difference_lambda_from_saved_a2F": l1,
            "weighted_L1_relative_to_mean_lambda_percent": 100.0 * l1 / ((float(row["lambda_spectrum_rebuilt_A"]) + float(row["lambda_spectrum_rebuilt_B"])) / 2.0),
            "max_abs_delta_a2F_from_saved_files": abs(left[max_idx][1] - right[max_idx][1]),
            "frequency_at_max_abs_delta_a2F_THz": xs[max_idx],
            "omega_log_32_K": float(row["omega_log_rebuilt_K_A"]),
            "omega_log_48_K": float(row["omega_log_rebuilt_K_B"]),
            "delta_omega_log_32_minus_48_K": float(row["omega_log_rebuilt_K_A"]) - float(row["omega_log_rebuilt_K_B"]),
            "Tc_32_K": float(row["Tc_rebuilt_K_A"]),
            "Tc_48_K": float(row["Tc_rebuilt_K_B"]),
            "delta_Tc_32_minus_48_K": float(row["Tc_rebuilt_K_A"]) - float(row["Tc_rebuilt_K_B"]),
        }
        result_rows.append(record)
    fields = list(result_rows[0])
    with (outdir / "spectral-grid-differences.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result_rows)
    summary = {
        "method": "For each native sigma, compare the paired saved alpha2F.dat arrays pointwise on their common 0-14 THz grid. Weighted L1 spectral difference is integral 2*abs(alpha2F_32-alpha2F_48)/nu dnu. The source alpha2F.dat values are printed to five decimals; lambda, omega_log and Tc are reconstructed independently from the exact printed elph.inp_lambda records.",
        "source_files": {
            "k32_alpha2F_sha256": sha256(path32),
            "k48_alpha2F_sha256": sha256(path48),
            "paired_tc_sha256": sha256(paired_path),
        },
        "sigma_count": len(result_rows),
        "frequency_bins_per_sigma": len(s32[sigmas[0]]),
        "frequency_range_THz": [s32[sigmas[0]][0][0], s32[sigmas[0]][-1][0]],
        "max_abs_lambda_integral_difference_from_five_decimal_alpha2F_vs_rebuilt_source": max_rounded_spectrum_lambda_mismatch,
        "delta_lambda_qsum_32_minus_48": signed_summary([r["delta_lambda_qsum_32_minus_48"] for r in result_rows]),
        "delta_lambda_spectrum_32_minus_48": signed_summary([r["delta_lambda_spectrum_32_minus_48"] for r in result_rows]),
        "weighted_L1_relative_to_mean_lambda_percent": {
            "min": min(r["weighted_L1_relative_to_mean_lambda_percent"] for r in result_rows),
            "max": max(r["weighted_L1_relative_to_mean_lambda_percent"] for r in result_rows),
            "max_at_sigma_Ry": max(result_rows, key=lambda r: r["weighted_L1_relative_to_mean_lambda_percent"])["sigma_Ry"],
        },
        "delta_omega_log_32_minus_48_K": signed_summary([r["delta_omega_log_32_minus_48_K"] for r in result_rows]),
        "delta_Tc_32_minus_48_K": signed_summary([r["delta_Tc_32_minus_48_K"] for r in result_rows]),
        "tc_curve_crossings": 0 if all(r["delta_Tc_32_minus_48_K"] > 0.0 for r in result_rows) else "review required",
        "interpretation": "This is a dense-k comparison at fixed 16^3 response k, 4^3 q, and common smearing values. It supplies spectral and moment evidence for those two branches, but the smearing scan is not by itself a k/q convergence proof.",
    }
    (outdir / "spectral-grid-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("sigma lambda_q32 lambda_q48 delta_lambda_q L1_spectrum_pct d_omega_log_K delta_Tc_K")
    for r in result_rows:
        print(f"{r['sigma_Ry']:.3f} {r['lambda_qsum_32']:.9f} {r['lambda_qsum_48']:.9f} "
              f"{r['delta_lambda_qsum_32_minus_48']:+.9f} "
              f"{r['weighted_L1_relative_to_mean_lambda_percent']:.5f} "
              f"{r['delta_omega_log_32_minus_48_K']:+.3f} {r['delta_Tc_32_minus_48_K']:+.9f}")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
```

</details>

### 交给代码助手的谱差补充任务

> 只做后处理，不启动 pw.x、ph.x、lambda.x 或其他计算程序，也不生成图。读取 k32/alpha2F.dat、k48/alpha2F.dat 和 comparison-k32-k48/paired-tc.csv；验证十档 sigma 一一对应、频率网格相同且覆盖 0–14 THz、所有数值有限。按 L1λ = ∫₀¹⁴ 2|alpha2F32−alpha2F48|/ω dω 计算逐频谱差，并除以两条 lambda_spectrum_rebuilt 的平均值换算百分比；ω=0 且两谱为零时该点被积函数取零。逐档输出 lambda_qsum、lambda_spectrum、omega_log、Tc 的 32³/48³ 数值及差值。检查 alpha2F.dat 直接积分得到的 lambda_spectrum 与 paired-tc.csv 的逐 q 重建值之差，并写明 alpha2F.dat 的五位小数打印精度。保存 spectral-grid-differences.csv 与 spectral-grid-summary.json，记录输入文件 SHA-256、积分定义、采样点数和频率范围；不做平滑或外推，也不把展宽扫描或无交点写成网格收敛证明。

实际源码 [compare_spectral_grids.py](/Atlas/examples/supercon-al-tc/compare_spectral_grids.py) 只读上述文件，已生成完整 [逐展宽 CSV](/Atlas/examples/supercon-al-tc/comparison-k32-k48/spectral-grid-differences.csv) 与 [复算摘要 JSON](/Atlas/examples/supercon-al-tc/comparison-k32-k48/spectral-grid-summary.json)。运行命令：

```bash
python3 compare_spectral_grids.py --root . --outdir comparison-k32-k48
```

程序逐档打印 λ、谱 L1、Δωlog 和 ΔTc，并保存 CSV/JSON。十档结果及积分误差见上表和摘要文件。

## 复画两条 Tc 曲线与差值

下载包中的源码可以重画本页曲线。原始的 [双图脚本 `plot_tc_crossings.py`](/Atlas/examples/supercon-al-tc/plot_tc_crossings.py) 会重画完整温度曲线以及 λ、ωlog 对照；保留的 [差值图脚本 `plot_supercon_tc_difference.py`](/Atlas/examples/supercon-al-tc/plot_supercon_tc_difference.py) 直接读取配对 CSV，绘制上方 Tc 曲线和下方 ΔTc 零线判据。两段命令都只读取保存的数据：

<details>
<summary>plot_tc_crossings.py 的完整源码</summary>

```python
"""Plot the paired lambda.x reconstructions written by compare_tc.py.

Run with NumPy and Matplotlib installed:
    python3 plot_tc_crossings.py --data comparison --out figures
Keep atlas_plot_style.py beside this script. No smoothing or data filtering
is used; the second Tc panel is explicitly a magnified view.
"""

from pathlib import Path
import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import atlas_plot_style


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("comparison"))
    parser.add_argument("--out", type=Path, default=Path("figures"))
    parser.add_argument("--prefix", default="al-two-dense-grids")
    args = parser.parse_args()
    with (args.data / "paired-tc.csv").open() as f:
        rows = list(csv.DictReader(f))
    report = json.loads((args.data / "crossings.json").read_text())
    if len(rows) != report["points_per_branch"] or len(rows) < 3:
        raise ValueError("Incomplete paired native table")

    def col(name):
        return np.array([float(r[name]) for r in rows])

    sigma = col("sigma_Ry")
    a = col("Tc_rebuilt_K_A")
    b = col("Tc_rebuilt_K_B")
    candidates = report["raw_input_reconstruction"]["points"]
    overlaps = report["raw_input_reconstruction"]["overlap_intervals"]
    atlas_plot_style.install()
    mesh_a = int(report.get('branch_A','k32').removeprefix('k'))
    mesh_b = int(report.get('branch_B','k48').removeprefix('k'))
    styles = {
        32:dict(color='#0072b2',ls='-',marker='o',mfc='white'),
        48:dict(color='#d55e00',ls='--',marker='s',mfc='#d55e00'),
        64:dict(color='#009e73',ls='-.',marker='^',mfc='white'),
    }

    def pair(ax, ya, yb):
        ax.plot(
            sigma,
            ya,
            **styles[mesh_a],
            lw=1.1,
            ms=4,
            mew=0.9,
            label=rf"$k_{{\rm dense}}={mesh_a}^3$",
        )
        ax.plot(
            sigma,
            yb,
            **styles[mesh_b],
            lw=1.1,
            ms=3.5,
            mew=0.8,
            label=rf"$k_{{\rm dense}}={mesh_b}^3$",
        )
        ax.set_xlabel(r"EPC electronic smearing $\sigma$ (Ry)")
        ax.set_xlim(sigma[0] - 0.001, sigma[-1] + 0.001)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.22, top=0.72, wspace=0.31)
    fig.suptitle(
        "Al: two independently calculated $T_c$ curves", x=0.085, y=0.98, ha="left"
    )
    crossing_note = ('Diamonds: all straight-segment intersections.' if candidates else 'No intersection in the sampled range.')
    if overlaps:
        crossing_note += ' Gray bands: overlaps.'
    fig.text(
        0.085,
        0.88,
        r"Response $k=16^3$  |  $q=4^3$  |  $\mu^*=0.10$  |  identical remaining inputs",
    )
    for ax, title in zip(
        axes, ["Full sampled range", "Magnified temperature range"]
    ):
        pair(ax, a, b)
        ax.set_ylabel(r"$T_c$ (K)")
        ax.set_title(title, pad=10)
        for interval in overlaps:
            ax.axvspan(
                interval["sigma_lo_Ry"],
                interval["sigma_hi_Ry"],
                facecolor="#dddddd",
                alpha=0.5,
                zorder=0,
            )
        for c in candidates:
            ax.plot(
                c["sigma_Ry"],
                c["Tc_K"],
                marker="D",
                ms=5,
                mec="#222222",
                mfc="white",
                mew=1,
                zorder=5,
            )
    axes[0].legend(loc="upper right")
    zoom = np.r_[a[1:], b[1:], [c["Tc_K"] for c in candidates]]
    span = max(float(np.ptp(zoom)), 0.01)
    axes[1].set_ylim(float(zoom.min()) - 0.20 * span, float(zoom.max()) + 0.32 * span)
    for i, c in enumerate(candidates):
        dy = 18 if i % 2 == 0 else -27
        axes[1].annotate(
            c["id"],
            xy=(c["sigma_Ry"], c["Tc_K"]),
            xytext=(7, dy),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            arrowprops=dict(arrowstyle="-", lw=0.65, color="#555555"),
        )
    fig.text(
        0.085,
        0.035,
        "Reconstructed from native elph inputs. " + crossing_note,
        fontsize=9,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out / (args.prefix + "-tc.png"))
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.22, top=0.72, wspace=0.31)
    fig.suptitle(
        "Al: moments from the same two EPC calculations", x=0.085, y=0.98, ha="left"
    )
    fig.text(
        0.085,
        0.88,
        r"Response $k=16^3$  |  $q=4^3$  |  same electronic-smearing points",
    )
    pair(axes[0], col("lambda_qsum_rebuilt_A"), col("lambda_qsum_rebuilt_B"))
    pair(axes[1], col("omega_log_rebuilt_K_A"), col("omega_log_rebuilt_K_B"))
    axes[0].set_ylabel(r"$\lambda$ (weighted mode sum)")
    axes[1].set_ylabel(r"$\omega_{\log}$ (K)")
    axes[0].set_title("Coupling constant", pad=10)
    axes[1].set_title("Logarithmic frequency", pad=10)
    axes[0].legend(loc="upper right")
    fig.text(
        0.085,
        0.035,
        "Moments are reconstructed using the same lambda.x algorithm as the $T_c$ curves.",
        fontsize=9,
    )
    fig.savefig(args.out / (args.prefix + "-moments.png"))
    plt.close(fig)
    summary = {
        "rows_per_curve": len(rows),
        "crossing_markers": len(candidates),
        "overlap_intervals": len(overlaps),
        "x_range_Ry": [float(sigma.min()), float(sigma.max())],
        "reconstructed_Tc_range_K": [
            float(min(a.min(), b.min())),
            float(max(a.max(), b.max())),
        ],
        "figures": [args.prefix + "-tc", args.prefix + "-moments"],
        "numerical_treatment": "lambda.x reconstruction from unmodified elph inputs, straight segments, full range plus explicitly magnified Tc view",
    }
    (args.out / (args.prefix + "-plot-checks.json")).write_text(json.dumps(summary, indent=2) + "\n")
    print(f'{len(rows)} points per curve; {len(candidates)} isolated intersections; {len(overlaps)} overlap intervals.')
    for name in summary['figures']:
        print(f'Saved {args.out / name}.png, .svg, .pdf')


if __name__ == "__main__":
    main()
```

</details>

```console
$ python3 plot_tc_crossings.py --data comparison-k32-k48 --out figures --prefix al-k32-k48
10 points per curve; 0 isolated intersections; 0 overlap intervals.
Saved figures/al-k32-k48-tc.png, .svg, .pdf
Saved figures/al-k32-k48-moments.png, .svg, .pdf
$ python3 plot_supercon_tc_difference.py --data comparison-k32-k48/paired-tc.csv --out figures --prefix supercon-al-k32-k48-tc-delta
rows=10; mu*=0.10; isolated crossings=0; overlap intervals=0
delta_min_K=0.009221798; delta_max_K=0.525165797
```

绘图需要 NumPy 和 Matplotlib；[原始曲线样式文件](/Atlas/examples/supercon-al-tc/atlas_plot_style.py)与脚本同目录。差值图脚本核对 CSV 的列名、展宽与数值关系，导出网页 PNG、可编辑 SVG 和矢量 PDF。颜色、线型和标记共同区分路径，所有十个原始展宽样点都保留。相邻点只作直线连接，不向范围外延长。

下面继续展开 32³ 分支的原生输出和公式细节，核对 λ、ωlog 怎样进入 Tc；改变 μ* 或加入 f₁、f₂ 修正时，另作相应对照。它们回答公式与输入假设的问题，两种致密电子网格的实际比较已在上面完成。

## 先把“已有输出”变成一条能执行的命令

前面的[完整 EPC](/Atlas/m/epc/qe/)和[α²F 页](/Atlas/m/eliashberg-a2f/qe/)已经提供真实父计算、八个不可约 q 的权重及 `lambda.in` 全文。这里不再提交 SCF 或 ph.x，而是在已有电声文件的副本上重放后处理。下面是在 Maxwell 独立 tmux 窗口中执行的命令，公开文本将工作路径简写。

```console
maxwell@maxwell:~/tc-route$ mkdir -p replay-lambda/elph_dir evidence
maxwell@maxwell:~/tc-route$ cp <工作目录>/al/epc-q4/lambda.in replay-lambda/
maxwell@maxwell:~/tc-route$ cp <工作目录>/al/epc-q4/elph_dir/elph.inp_lambda.* replay-lambda/elph_dir/
maxwell@maxwell:~/tc-route$ cd replay-lambda
```

复制的是同一组八个 q 文件，不会生成新的响应。输入内的相对文件名仍然指向 `elph_dir`，副本保留相同层级。末尾读到的是：

```console
maxwell@maxwell:~/al/tc-route/replay-lambda$ tail -3 lambda.in
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
0.10
```

最后的 0.10 才是 μ*；第一行的 0.12 是频率轴 Gaussian 宽度，单位 THz。本机 QE 依赖 oneAPI 运行库，载入后运行：

```console
maxwell@maxwell:~/tc-route/replay-lambda$ source /opt/intel/oneapi/setvars.sh > ../evidence/oneapi-env.log 2>&1
maxwell@maxwell:~/tc-route/replay-lambda$ <qe_bin>/lambda.x < lambda.in > lambda.out 2> lambda.err
maxwell@maxwell:~/tc-route/replay-lambda$ wc -c lambda.err
0 lambda.err
```

这次副本生成的 `lambda.out`、`lambda.dat`、`alpha2F.dat` 与原件 SHA-256 完全相同。下面沿着它们的实际输出读数。

## 先知道自己代入的是哪个公式

这次 QE 7.5 的 `lambda.x` 使用的是包含 ω_log 的简化 Allen–Dynes 表达式：

**T<sub>c</sub> = (ω<sub>log</sub> / 1.2) × exp{−1.04(1 + λ) / [λ − μ∗(1 + 0.62λ)]}**

这里 ω_log 以 K 表示，算出的 Tc 也是 K。该式相当于将强耦合与谱形修正因子 f₁、f₂ 设为 1；没有求解各向异性的 Eliashberg 方程。不要把输出里的 K 再当作 THz 乘一次换算系数，也不要把论文中包含 f₁、f₂ 的结果与这行代码当成同一个计算。

源码计算 ωlog 时用内部谱积分的 λ 归一化，计算 Tc 时则取逐 q 求和的 λ；这正是输出中两种 λ 要分列保留的原因。后面另外从同一打印谱提取一致的频率矩，用于完整 f₁、f₂ 对照。

μ* 是有效库仑赝势参数。本例取 0.10，是输入假设，不是这次 DFT 自动求出的物性。

## 从输入的最后一行到程序输出

完整的 `lambda.in` 与执行顺序见 [α²F 页](/Atlas/m/eliashberg-a2f/qe/)；本页从已经生成的 `lambda.out` 接着读。输入第一行的 14.0 和 0.12 都以 THz 为单位，分别控制频率范围和频率展宽；最后一行的 0.10 才是用于 Tc 公式的 μ*。

这份 Al 数据的最高直接计算频率为 9.936574 THz，14 THz 覆盖了谱峰及 Gaussian 尾部。更换材料时，要先核对实际频率范围；落在范围外的谱权重会使 ω_log 和积分失真。

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.out
     lambda = 0.430378 (   0.430442 )  <log w>=  355.877 K  N(Ef)=  2.518161 at degauss= 0.005
     lambda = 0.371061 (   0.371121 )  <log w>=  344.606 K  N(Ef)=  2.624685 at degauss= 0.010
     lambda = 0.370295 (   0.370356 )  <log w>=  343.420 K  N(Ef)=  2.647439 at degauss= 0.015
     lambda = 0.374486 (   0.374547 )  <log w>=  343.741 K  N(Ef)=  2.646097 at degauss= 0.020
     lambda = 0.374613 (   0.374674 )  <log w>=  343.537 K  N(Ef)=  2.643523 at degauss= 0.025
     lambda = 0.373773 (   0.373835 )  <log w>=  342.831 K  N(Ef)=  2.643829 at degauss= 0.030
     lambda = 0.373581 (   0.373643 )  <log w>=  342.006 K  N(Ef)=  2.645823 at degauss= 0.035
     lambda = 0.374086 (   0.374148 )  <log w>=  341.243 K  N(Ef)=  2.648339 at degauss= 0.040
     lambda = 0.375022 (   0.375085 )  <log w>=  340.631 K  N(Ef)=  2.650827 at degauss= 0.045
     lambda = 0.376041 (   0.376104 )  <log w>=  340.145 K  N(Ef)=  2.653067 at degauss= 0.050
lambda        omega_log          T_c
   0.43038       355.877              2.212
   0.37106       344.606              0.916
   0.37030       343.420              0.900
   0.37449       343.741              0.969
   0.37461       343.537              0.971
   0.37377       342.831              0.955
   0.37358       342.006              0.949
   0.37409       341.243              0.955
   0.37502       340.631              0.969
   0.37604       340.145              0.985
```

前十行先给每组电子展宽的 λ、括号中的谱积分 λ、ω_log 和 DOS(EF)。后面的三列表才是 λ、ω_log、Tc，电子展宽的行序与前面相同。`lambda.x` 的这份文本没有常见的大段计时与 `JOB DONE.` 结束框；这次通过零字节 `lambda.err`、十行完整结果、有限数值以及独立公式复算核对结果。前面的 pw.x、ph.x 和 matdyn.x 则分别检查各自的正常结束及收敛输出。

0.020 Ry 对应第 4 行：λ=0.374486，ω_log=343.741 K，μ*=0.10。分母 λ−μ∗(1+0.62λ) 为正，代入得到 0.969046 K，程序按三位小数打印为 0.969 K。若分母接近零或变为非正数，应停止把指数结果解释为可靠的 Tc，而不是让程序给出一个数就继续引用。

复算时也要明确使用哪一列 λ。本页和程序的 Tc 表都采用逐 q 求和的第一列；括号中的数用于检查谱函数积分。如果改用括号值，应重新计算并说明来源，不能保留旧 Tc 却悄悄换掉表中的 λ。ω_log 对频率采取对数加权，低频模式的处理和截断会传递到温度结果；输入有实质性虚频时，不应将频率取绝对值后继续套公式。

这一表中的十行是十种积分展宽设定，不是十次独立实验或随机样本。它们的范围可展示当前采样对展宽的敏感性，不能直接当作统计置信区间。μ* 扫描也是对一个输入假设的敏感性检查，两者应像下图那样分别阅读。


## 自己复算第 4 行，先检查分母

用打印出来的 λ=0.374486、ωlog=343.741 K 和 μ*=0.10，就能在终端复现这一行：

```console
maxwell@maxwell:~/tc-route/replay-lambda$ python3 -c 'import math; lam=0.374486; wlog_K=343.741; mu=0.10; d=lam-mu*(1+0.62*lam); print(f"denominator = {d:.9f}"); print(f"Tc = {wlog_K/1.2*math.exp(-1.04*(1+lam)/d):.6f} K")'
denominator = 0.251267868
Tc = 0.969046 K
```

这是用表格舍入数字得到的复算值；从逐 q 原件重建内部值为 0.969044 K，两者都对应原生输出的 0.969 K。分母非正、近于零或输入非有限时，新增脚本会停止公式计算，不会把一个失去适用意义的指数结果解释成材料温度。这也不能被反过来当成证明材料不超导。

## 先把十组电子展宽一起读完

0.005 Ry 的公式结果是 2.212 K，0.010 Ry 降到约 0.916 K。后几组集中在约 0.90–0.98 K，但这个表只改变了电子双 δ 积分的展宽，致密电子网格和真实 q 网格没有变化。这说明目前最窄展宽对积分采样敏感，不能仅选择一行接近期望值的数字作为最终结果。

`analyse_epc.py` 直接读取 `lambda.dat`，将每一行代入同一个公式，并比较 `lambda.out` 的打印值；该脚本还独立积分 `alpha2F.dat`。

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

## 保持谱函数不变，再改变 μ*

下面固定 0.020 Ry 对应的 λ 与 ω_log，只改变假设的 μ*。这些点没有重新进行 DFT，是同一个简化公式的参数敏感性计算。

```console
maxwell@maxwell:~/al/epc-q4$ cat mu-sensitivity.csv
mu_star,Tc_K
8.000000000000000167e-02,1.610722658499318172e+00
8.999999999999999667e-02,1.264271858038103158e+00
9.999999999999999167e-02,9.690460020124249674e-01
1.099999999999999867e-01,7.226644078867575649e-01
1.199999999999999817e-01,5.220046073518097574e-01
1.299999999999999767e-01,3.632181974234426902e-01
1.399999999999999578e-01,2.417928679277238646e-01
1.499999999999999667e-01,1.526709604922883989e-01
1.599999999999999756e-01,9.043153189929345470e-02
```

![电子展宽及 μ* 对简化公式 Tc 的影响](/Atlas/examples/al/figures/allen-dynes.png)

左图改变 EPC 积分的电子展宽，右图改变公式中的库仑参数。两种变化回答的问题不同。这个例子能展示一条完整的数据读取与复算方法，也能看到假设对数值的影响；尚不支持精确预测材料 Tc。进一步计算要增加致密电子网格和真实 q 网格，并在相同物理协议下检查声子与 EPC 是否收敛，而不是只把频率轴画得更密。


## 从谱中提取二阶矩，才能计算完整 f₁、f₂

只有 λ 与 ωlog 两个数，还不能决定完整 Allen–Dynes 的谱形修正。它还需要耦合加权的均方根频率 ν̄₂，不能拿普通声子 DOS 的平均频率、另一个电子展宽的频率矩，或另一条 matdyn 路线的数据来补。

| 公式版本 | 前因子 | 本例用途 |
|---|---|---|
| 原始 McMillan | ΘD/1.45 | 本例没有计算 ΘD，不拿它代替 ωlog |
| QE 7.5 的 ωlog 修正式 | ωlog/1.2，f₁=f₂=1 | 与原生 `lambda.x` 逐行复算 |
| 含 f₁、f₂ 的 Allen–Dynes | f₁f₂ωlog/1.2 | 从同一非负谱计算完整矩后单列 |

以普通频率 ν 写，同一份谱的三个积分是：

**λspec = 2∫ α²F(ν)/ν dν**

**νlog = exp{(2/λspec)∫ [α²F(ν)/ν] ln(ν) dν}**

**ν̄₂ = {(2/λspec)∫ α²F(ν)ν dν}<sup>1/2</sup>**

这里的归一化 λspec 必须来自这份谱。对数使用同一固定单位，可以理解为对 `ν/(1 THz)` 取对数，最后恢复 THz。νlog、ν̄₂ 随后乘 h×10¹²/kB 得到 K；若写成角频率则使用 ħω/kB，不能多乘 2π。复现 QE 7.5 时沿用源码的 47.9924 K/THz，已经是 K 的打印 ωlog 不再换算。

零频点不直接除以 ν 或取对数。本例零点的谱值为零，可以从正频点积分；这不是允许删掉其他材料中的异常低频峰或实质性虚频。脚本拒绝负谱，不取绝对值、不裁零后再输出一组看似合理的 Tc。

## 将内部求和、打印谱积分和公式逐项对照

新增脚本读取所有 q 文件与权重，先按 QE 7.5 的 Gaussian 定义重建 2000 点内部谱，复现原生 λ、ωlog 与 Tc，再独立积分已打印的 `alpha2F.dat`。这样可以分清舍入误差与错列、错单位或混用公式。

```console
maxwell@maxwell:~/al/tc-route$ python3 scripts/verify_tc_chain.py --source <工作目录>/al/epc-q4 --output data > evidence/verify.out
```
```console
maxwell@maxwell:~/al/tc-route$ cat evidence/verify.out
q points=8; weights=64; modes=3; widths=10; mode records=240
printed-omega^2 reconstruction=0.087851..9.936533 THz; negative omega^2=0
ph.x printed maximum=9.936574 THz; frequency difference comes from printed w2 precision
lambda.x grid=2000 points, 0..14 THz; Gaussian parameter=0.12 THz
sigma_Ry lambda_qsum lambda_spectrum omega_log_K omega2_K Tc_QE_K Tc_full_AD_K
0.005 0.43037813 0.43043738 355.87701 370.56657 2.212105 2.248232
0.010 0.37106094 0.37111797 344.60678 363.11888 0.915532 0.928052
0.015 0.37029531 0.37035355 343.41976 362.60101 0.900170 0.912494
0.020 0.37448594 0.37454456 343.74087 363.33106 0.969044 0.982511
0.025 0.37461250 0.37467149 343.53737 363.44354 0.970568 0.984079
0.030 0.37377344 0.37383269 342.83124 363.00639 0.954746 0.968016
0.035 0.37358125 0.37364098 342.00604 362.39378 0.949304 0.962508
0.040 0.37408594 0.37414604 341.24361 361.79075 0.955437 0.968761
0.045 0.37502188 0.37508257 340.63107 361.29676 0.969100 0.982670
0.050 0.37604063 0.37610138 340.14505 360.89644 0.984588 0.998426
sigma=0.020: f1=1.01206929; f2=1.00080168; spectral simple Tc=0.970016 K
matdyn negative rows by width: 146, 9, 0, 0, 0, 0, 0, 0, 0, 0
Cross-check completed. Material Tc convergence is not established.
```

`lambda_qsum` 按模式 λ 与归一化 q 权重直接相加，`lambda_spectrum` 从打印谱积分得到。频率展宽、积分网格和小数位让它们略有不同。源码算法重建与原生输出在打印精度内吻合，打印谱的独立积分则保留其有限精度。

本次直接 q 文件的 ω² 都为正，这个检查只覆盖已计算点。Γ 三个约 2.93 cm⁻¹ 的正残差低于本版本 `interpolated` 实现的 20 cm⁻¹ 阈值，λ 被程序置零，γ 原文仍保留。不能说这里已经验证了无低频截断的 EPC。

另外，matdyn 的 0.005 Ry 谱有 146 行负值，0.010 Ry 有 9 行；这些列没有被用来输出可接受的谱矩。下面的完整公式使用直接 q 求和的非负 `alpha2F.dat`，并不表示另一条插值路线的问题已经解决。

设 r=ν̄₂/νlog，完整形式为：

**Tc,AD = f₁f₂ (ωlog/1.2) exp{−1.04(1+λspec)/[λspec−μ∗(1+0.62λspec)]}**

**f₁ = [1+(λspec/Λ₁)<sup>3/2</sup>]<sup>1/3</sup>，Λ₁ = 2.46(1+3.8μ*)**

**f₂ = 1+(r−1)λspec²/(λspec²+Λ₂²)，Λ₂ = 1.82(1+6.3μ*)r**

两种频率都换成 K 后，r 仍无量纲。f₁ 是强耦合修正，f₂ 随谱形改变；它们仍属于拟合公式，补上以后并不等于数值求解了 Eliashberg 方程。

0.020 Ry 这列的实际中间量是：

| 量 | 数值 |
|---|---:|
| λspec | 0.37454456 |
| ωlog | 343.74087 K |
| ν̄₂ 对应温度 | 363.33106 K |
| μ* | 0.10 |
| f₁ | 1.01206929 |
| f₂ | 1.00080168 |

三行温度必须分开读：

| 数据与公式 | Tc（K） |
|---|---:|
| QE 原生定义：λqsum 与原生谱 ωlog，简式 | 0.969044 |
| 同一打印谱的 λspec、ωlog，简式 | 0.970016 |
| 同一打印谱的 λspec、ωlog、ν̄₂，乘 f₁f₂ | 0.982511 |

第一到第二行包含归一化与打印谱积分的变化，第二到第三行才是在固定同一组谱矩后加入 f₁f₂。不能把第一到第三行的全部差别都说成强耦合修正，更不能把较高的一行选作更可靠的材料预测。

## 同一谱下，完整公式也要保留 μ* 的假设

固定 0.020 Ry 的谱，只改变 μ*，三种定义得到：

```console
maxwell@maxwell:~/al/tc-route$ cat data/mu-star-scan.csv
mu_star,Tc_QE_rounded_input_K,Tc_spectrum_simple_K,Tc_spectrum_full_AD_K
0.08,1.6107226584993182,1.6120500128520705,1.6347436284357797
0.09,1.2642718580381032,1.2654176885906845,1.2824457531797715
0.1,0.969046002012425,0.970016140785092,0.9825105724541605
0.11,0.7226644078867569,0.7234674219221328,0.732398924745519
0.12,0.5220046073518098,0.5226518506188913,0.5288436032754813
0.13,0.36321819742344197,0.3637237157771725,0.3678633763712934
0.14,0.24179286792772323,0.24217311358934973,0.2448239277483174
0.15,0.1526709604922883,0.15294427830078677,0.15455599724304322
0.16,0.09043153189929327,0.0906173974670778,0.09153761243237504
```

这些点没有重新计算 DFT；它们是同一经验公式的假设敏感性，不是独立实验或统计置信区间。μ* 从 0.08 增到 0.16 时温度明显下降，说明结论若依赖某个选择，就需要报告采用值、范围与依据。

![电子展宽、μ* 与两种公式版本](/Atlas/examples/al/tc-route/figures/tc-formulas.png)

左幅保持 μ*=0.10，改变 EPC 电子展宽；右幅固定 0.020 Ry 的谱，改变 μ*。横轴回答两种不同问题。最窄展宽的离群值并不会因为乘上 f₁f₂ 就变得可信。

## 从文件核对到网格比较

八个不可约 q、星权重和 64、三模式、十档展宽及谱范围在同一父链上闭合，副本后处理与原件一致。真实响应 k/q 网格和截断能的加密会改变上游数据，应在相同 σ 下继续比较 λ、ωlog 与 Tc；`matdyn` 插值网格及谱采样点数控制后处理分辨率。

## 在本机重新出图

在解包后的 `al` 目录中执行：

```bash
cd tc-route
python3 scripts/verify_tc_chain.py --source ../epc-q4 --output data
python3 scripts/plot_tc_chain.py --data data --output figures
```

提取仅需 Python 标准库，绘图使用 NumPy、Matplotlib。`data/tc-formula-scan.csv` 保存十组展宽的中间量，`mu-star-scan.csv` 保存 μ* 扫描，`tc-chain-checks.json` 保存单位、源文件 SHA 与限制。脚本读取原值，不裁负值或倍乘自旋；颜色与线型同时区分曲线。网页 PNG 使用大字号，矢量 PDF 用 7 pt 正文、8 pt 黑色粗体面板标记和可编辑字体，不加背景网格。

下载：[完整 Al 包](/Atlas/examples/al-lesson-files.tar.gz) · [提取与复核脚本](/Atlas/examples/al/tc-route/scripts/verify_tc_chain.py) · [绘图脚本](/Atlas/examples/al/tc-route/scripts/plot_tc_chain.py) · [λ、频率矩与 Tc 表](/Atlas/examples/al/tc-route/data/tc-formula-scan.csv) · [μ* 表](/Atlas/examples/al/tc-route/data/mu-star-scan.csv) · [单位与文件核验](/Atlas/examples/al/tc-route/data/tc-chain-checks.json)。

<details>
<summary>verify_tc_chain.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Read the completed Al lesson; check lineage, units and Tc formulas.
Standard library only. No QE execution and no edits to source calculations.
Source formulas: QE 7.5 lambda.f90; Allen & Dynes, PRB 12, 905 (1975).
"""
from pathlib import Path
import argparse, csv, hashlib, json, math, re, statistics

QE_RY_THZ=3289.828
QE_THZ_K=47.9924
SI_THZ_K=6.62607015e-34*1e12/1.380649e-23
SI_RY_K=(4.3597447222071e-18/2)/1.380649e-23
SI_RY_THZ=(4.3597447222071e-18/2)/6.62607015e-34/1e12

def table(path):
    return [[float(x) for x in s.split()] for s in path.read_text().splitlines()
            if s.strip() and re.match(r'^\s*[-+]?\d',s)]

def trap(x,y):
    return sum((b-a)*(v+u)/2 for a,b,u,v in zip(x,x[1:],y,y[1:]))

def cumulative(x,y):
    out=[0.]
    for a,b,u,v in zip(x,x[1:],y,y[1:]):
        out.append(out[-1]+(b-a)*(u+v)/2)
    return out

def moments(x,y,to_K):
    if any(v<0 for v in y):
        raise ValueError("A negative spectrum is not silently clipped for Tc moments.")
    pairs=[(a,b) for a,b in zip(x,y) if a>0]
    a,b=map(list,zip(*pairs))
    lam=2*trap(a,[v/u for u,v in pairs])
    if lam<=0:raise ValueError("Non-positive spectral lambda")
    logw=math.exp(2*trap(a,[v*math.log(u)/u for u,v in pairs])/lam)
    w2=math.sqrt(2*trap(a,[v*u for u,v in pairs])/lam)
    return lam,logw*to_K,w2*to_K

def formula(lam,wlog_K,w2_K,mu):
    den=lam-mu*(1+.62*lam)
    if lam<=0 or wlog_K<=0 or den<=0:
        raise ValueError("Outside this empirical formula's admissible denominator.")
    simple=wlog_K/1.2*math.exp(-1.04*(1+lam)/den)
    ratio=w2_K/wlog_K
    L1=2.46*(1+3.8*mu);L2=1.82*(1+6.3*mu)*ratio
    f1=(1+(lam/L1)**1.5)**(1/3)
    f2=1+(ratio-1)*lam*lam/(lam*lam+L2*L2)
    return dict(denominator=den,Tc_simple_K=simple,f1=f1,f2=f2,Tc_full_AD_K=f1*f2*simple)

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('data'))
    a=ap.parse_args();r=a.source.resolve();o=a.output.resolve();o.mkdir(parents=True,exist_ok=True)
    source_names=['lambda.in','lambda.dat','lambda.out','alpha2F.dat','al.elph.out','q2r.out','matdyn-dos.out',
                  'al.dense.in','al.scf.in','al.elph.in','q2r.in','matdyn-dos.in','q-weight-source.json']
    inp=[x.strip() for x in (r/'lambda.in').read_text().splitlines() if x.strip()]
    emax,width,kind=map(float,inp[0].split());nq=int(inp[1])
    assert int(kind)==0 and width>0
    qrows=[list(map(float,x.split())) for x in inp[2:2+nq]]
    files=inp[2+nq:2+2*nq];mu=float(inp[2+2*nq])
    wsum=sum(q[3] for q in qrows);assert wsum==64 and nq==8
    ph=(r/'al.elph.out').read_text()
    qblocks=re.split(r'Calculation of q\s*=',ph)[1:];assert len(qblocks)==nq
    modes=[];negative_w2=[];native_ph_frequencies=[]
    for iq,(q,name,block) in enumerate(zip(qrows,files,qblocks),1):
        p=r/name;source_names.append(name);text=p.read_text();lines=text.splitlines()
        h=lines[0].split();ns,nm=map(int,h[3:]);assert ns==10 and nm==3
        assert all(abs(float(h[j])-q[j])<1e-6 for j in range(3))
        native_ph_frequencies.extend(float(v) for v in re.findall(r'freq\s*\(\s*\d+\)\s*=\s*([-\d.]+)\s*\[THz\]',block))
        stars=list(map(int,re.findall(r'Number of q in the star\s*=\s*(\d+)',block)))
        assert stars and set(stars)=={int(q[3])}
        w2=list(map(float,lines[1].split()));assert len(w2)==nm
        for j,v in enumerate(w2):
            if v<=0:negative_w2.append([iq,j+1,v])
        if negative_w2:raise ValueError("Nonpositive direct squared frequencies: "+str(negative_w2))
        chunks=re.split(r'Gaussian Broadening:',text)[1:];assert len(chunks)==ns
        for chunk in chunks:
            sigma=float(re.match(r'\s*([.\d]+)',chunk)[1])
            vals=re.findall(r'lambda\(\s*(\d+)\)=\s*([-\d.]+)\s+gamma=\s*([-\d.]+)\s+GHz',chunk)
            assert len(vals)==nm
            for mode,lam,gamma in vals:
                j=int(mode)-1;freq=math.sqrt(w2[j])*QE_RY_THZ
                row=dict(q_index=iq,mode=j+1,sigma_Ry=sigma,star_weight=int(q[3]),
                         weight=q[3]/wsum,frequency_THz=freq,lambda_mode=float(lam),gamma_GHz=float(gamma))
                modes.append(row)
    direct=table(r/'lambda.dat');af=table(r/'alpha2F.dat')
    assert len(direct)==10 and len(af)==2000 and len(af[0])==11
    assert all(math.isfinite(x) for row in af for x in row) and min(min(row[1:]) for row in af)>=0
    printed_x=[row[0] for row in af]
    exact_x=[i*emax/1999 for i in range(2000)]
    native_tc=table_from_output=(r/'lambda.out').read_text().split('lambda        omega_log          T_c')[-1]
    native_tc=[[float(x) for x in s.split()] for s in native_tc.strip().splitlines()]
    assert len(native_tc)==10
    scans=[];spectrum=[];matdyn=[];pairs=[]
    for j,(sigma,lam_print,li_print,wl_print,dosef) in enumerate(direct):
        selected=[m for m in modes if abs(m['sigma_Ry']-sigma)<1e-9]
        qsum=sum(m['weight']*m['lambda_mode'] for m in selected)
        recon=[]
        for nu in exact_x:
            recon.append(sum(m['weight']*m['lambda_mode']*m['frequency_THz']/2
                             *math.exp(-((nu-m['frequency_THz'])/width)**2)/(math.sqrt(math.pi)*width)
                             for m in selected))
        step=emax/1999
        li_exact=2*step*sum(v/x for x,v in zip(exact_x[1:],recon[1:]))
        log_exact=math.exp(2*step*sum(v*math.log(x)/x for x,v in zip(exact_x[1:],recon[1:]))/li_exact)*QE_THZ_K
        assert abs(qsum-lam_print)<5.1e-7
        assert abs(li_exact-li_print)<5.1e-7 and abs(log_exact-wl_print)<.00051
        y=[row[j+1] for row in af];lam_s,log_s,w2_s=moments(printed_x,y,QE_THZ_K)
        assert abs(lam_s-li_print)<2e-5 and abs(log_s-wl_print)<.02
        f=formula(lam_s,log_s,w2_s,mu)
        native_formula=formula(qsum,log_exact,w2_s,mu)['Tc_simple_K']
        assert abs(native_formula-native_tc[j][2])<.00051
        row=dict(sigma_Ry=sigma,lambda_qsum=qsum,lambda_native_printed=lam_print,
                 lambda_spectrum_internal=li_exact,lambda_spectrum_printed_trapezoid=lam_s,
                 omega_log_native_replay_K=log_exact,omega_log_printed_K=wl_print,
                 omega_log_spectrum_K=log_s,omega2_spectrum_K=w2_s,
                 mu_star=mu,Tc_native_printed_K=native_tc[j][2],Tc_QE_replay_K=native_formula,
                 Tc_spectrum_simple_K=f['Tc_simple_K'],f1=f['f1'],f2=f['f2'],Tc_spectrum_full_AD_K=f['Tc_full_AD_K'])
        scans.append(row)
        cy=cumulative(printed_x,[0 if x==0 else 2*v/x for x,v in zip(printed_x,y)])
        if j in [0,3]:
            for x,v,z in zip(printed_x,y,cy):spectrum.append(dict(route='lambda.x',sigma_Ry=sigma,frequency_THz=x,a2F=v,cumulative_lambda=z))
        apath=r/f'a2F.dos{j+1}';source_names.append(apath.name);atxt=apath.read_text();arr=table(apath)
        assert len(arr)==400 and all(len(v)==5 for v in arr)
        ry=[v[0] for v in arr];ay=[v[1] for v in arr]
        footer=float(re.search(r'lambda\s*=\s*([-\d.Ee+]+)',atxt)[1])
        neg=sum(v<0 for v in ay)
        md=dict(sigma_Ry=sigma,negative_rows=neg,min_a2F=min(ay),lambda_footer=footer,
                lambda_trapezoid=2*trap(ry,[v/x for x,v in zip(ry,ay)]),frequency_unit='Ry',
                moment_status='rejected_negative_spectrum' if neg else 'nonnegative_for_arithmetic')
        if neg==0:
            ml,mw,m2=moments(ry,ay,SI_RY_K);md.update(lambda_spectrum=ml,omega_log_K=mw,omega2_K=m2)
        matdyn.append(md)
        if j in [0,3]:
            cx=[x*SI_RY_THZ for x in ry];cy=cumulative(ry,[2*v/x for x,v in zip(ry,ay)])
            for x,v,z in zip(cx,ay,cy):spectrum.append(dict(route='matdyn.x',sigma_Ry=sigma,frequency_THz=x,a2F=v,cumulative_lambda=z))
    chosen=scans[3];mu_rows=[]
    for i in range(8,17):
        m=i/100;f=formula(chosen['lambda_spectrum_printed_trapezoid'],chosen['omega_log_spectrum_K'],chosen['omega2_spectrum_K'],m)
        simple=formula(chosen['lambda_native_printed'],chosen['omega_log_printed_K'],chosen['omega2_spectrum_K'],m)['Tc_simple_K']
        mu_rows.append(dict(mu_star=m,Tc_QE_rounded_input_K=simple,Tc_spectrum_simple_K=f['Tc_simple_K'],Tc_spectrum_full_AD_K=f['Tc_full_AD_K']))
    write_csv(o/'tc-formula-scan.csv',scans);write_csv(o/'mu-star-scan.csv',mu_rows)
    write_csv(o/'spectra-and-integrals.csv',spectrum);write_csv(o/'mode-check.csv',modes)
    # Rejecting negative spectra is recorded; raw values are always preserved in plots/data.
    (o/'matdyn-spectrum-checks.json').write_text(json.dumps(matdyn,indent=2)+'\n')
    density_hash=hashlib.sha256((r/'tmp/al.a2Fsave').read_bytes()).hexdigest()
    assert density_hash==hashlib.sha256((r/'al.a2Fsave.k32').read_bytes()).hexdigest()
    minfreq=min(m['frequency_THz'] for m in modes);maxfreq=max(m['frequency_THz'] for m in modes)
    for name in ['al.dense','al.scf','al.elph','q2r','matdyn-dos']:
        out=(r/f'{name}.out').read_text();assert 'JOB DONE.' in out and 'convergence NOT achieved' not in out
        assert (r/f'{name}.err').stat().st_size==0
    assert (r/'lambda.err').stat().st_size==0
    report=dict(case='completed fcc Al lesson, QE7.5',q_irreducible=nq,q_star_sum=wsum,nmodes=3,
                electronic_widths_Ry=[row[0] for row in direct],frequency_min_direct_THz=minfreq,
                frequency_max_direct_THz=max(native_ph_frequencies),frequency_max_reconstructed_from_printed_w2_THz=maxfreq,frequency_upper_limit_THz=emax,gaussian_parameter_THz=width,
                direct_negative_squared_frequencies=negative_w2,dense_a2Fsave_sha256=density_hash,
                low_frequency_mode_lambda_cutoff_cm1=20,
                cutoff_source='QE7.5 PHonon/PH/elphon.f90 epsw and elphsum; raw gamma still exists',
                constants=dict(lambda_x_Ry_to_THz=QE_RY_THZ,lambda_x_THz_to_K=QE_THZ_K,
                               SI_THz_to_K=SI_THZ_K,SI_Ry_to_K=SI_RY_K,SI_Ry_to_THz=SI_RY_THZ),
                source_sha256={name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in source_names},
                formula_versions=['QE omega_log modified McMillan/Allen-Dynes with f1=f2=1',
                                  'spectral-moment Allen-Dynes with both f1 and f2'],
                numerical_crosscheck='qsum, source-algorithm replay, printed-spectrum quadrature and native Tc agree within printing/integration tolerances',
                scientific_status='teaching formula results only; k/q/cutoff convergence not established; mu_star assumed; no material Tc accepted',
                selected_sigma_Ry_0p020=chosen)
    (o/'tc-chain-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'q points={nq}; weights={wsum:g}; modes=3; widths=10; mode records={len(modes)}')
    print(f'printed-omega^2 reconstruction={minfreq:.6f}..{maxfreq:.6f} THz; negative omega^2=0')
    print(f'ph.x printed maximum={max(native_ph_frequencies):.6f} THz; frequency difference comes from printed w2 precision')
    print(f'lambda.x grid=2000 points, 0..{emax:g} THz; Gaussian parameter={width:g} THz')
    print('sigma_Ry lambda_qsum lambda_spectrum omega_log_K omega2_K Tc_QE_K Tc_full_AD_K')
    for s in scans:
        print(f"{s['sigma_Ry']:.3f} {s['lambda_qsum']:.8f} {s['lambda_spectrum_printed_trapezoid']:.8f} {s['omega_log_spectrum_K']:.5f} {s['omega2_spectrum_K']:.5f} {s['Tc_QE_replay_K']:.6f} {s['Tc_spectrum_full_AD_K']:.6f}")
    print('sigma=0.020: f1={:.8f}; f2={:.8f}; spectral simple Tc={:.6f} K'.format(chosen['f1'],chosen['f2'],chosen['Tc_spectrum_simple_K']))
    print('matdyn negative rows by width: '+', '.join(str(m['negative_rows']) for m in matdyn))
    print('Cross-check completed. Material Tc convergence is not established.')

if __name__=='__main__':main()
```

</details>

<details>
<summary>plot_tc_chain.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Render verified Al EPC data; run on the visualization machine.
Requires NumPy and Matplotlib. This script never runs QE.
Default: web PNG plus publication PDF, with separate font scales.
"""
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLUE,ORANGE,BLACK='#0072B2','#D55E00','#222222'

def read_rows(path):
    with path.open() as f:return list(csv.DictReader(f))

def number(rows,key):return np.array([float(r[key]) for r in rows])

def style(publication):
    fs=7 if publication else 12
    plt.rcParams.update({'font.family':'sans-serif',
        'font.sans-serif':['Arial','Helvetica','DejaVu Sans'],
        'font.size':fs,'axes.labelsize':fs,'xtick.labelsize':fs,'ytick.labelsize':fs,
        'legend.fontsize':fs,'axes.linewidth':.65,'lines.linewidth':1 if publication else 1.5,
        'xtick.major.width':.65,'ytick.major.width':.65,'xtick.major.size':2.5,'ytick.major.size':2.5,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
        'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
    return fs

def panel(ax,label,publication):
    ax.text(-.15,1.035,label,transform=ax.transAxes,fontweight='bold',
            fontsize=8 if publication else 14,color='black',va='bottom')
    ax.tick_params(direction='out')

def save(fig,out,name,publication):
    fig.savefig(out/(name+('.pdf' if publication else '.png')),
                dpi=240,bbox_inches=None if publication else 'tight',pad_inches=.12)
    plt.close(fig)

def draw(data,out,publication):
    style(publication)
    width,height=(183/25.4,3.35) if publication else (9,4.3)
    spec=read_rows(data/'spectra-and-integrals.csv')
    scan=read_rows(data/'tc-formula-scan.csv');mu=read_rows(data/'mu-star-scan.csv')
    report=json.loads((data/'tc-chain-checks.json').read_text())
    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    for route,color,line,label in [('lambda.x',BLUE,'-','Direct q sum + Gaussian'),
                                  ('matdyn.x',ORANGE,'--','q2r / matdyn interpolation')]:
        rows=[r for r in spec if r['route']==route and abs(float(r['sigma_Ry'])-.02)<1e-9]
        x=number(rows,'frequency_THz')
        ax[0].plot(x,number(rows,'a2F'),color=color,linestyle=line,label=label)
        ax[1].plot(x,number(rows,'cumulative_lambda'),color=color,linestyle=line,label=label)
    ax[0].set(xlabel='Frequency (THz)',ylabel=r'$\alpha^2F$')
    ax[1].set(xlabel='Frequency (THz)',ylabel=r'Cumulative $\lambda$')
    for i,a in enumerate(ax):a.set_xlim(0,14);panel(a,chr(97+i),publication)
    ax[1].legend(frameon=False,loc='lower right')
    save(fig,out,'a2f-route-check',publication)

    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    x=number(scan,'sigma_Ry')
    ax[0].plot(x,number(scan,'Tc_QE_replay_K'),'o-',color=BLACK,markersize=3,label='QE simplified')
    ax[0].plot(x,number(scan,'Tc_spectrum_simple_K'),'--',color=BLUE,label='Spectrum simplified')
    ax[0].plot(x,number(scan,'Tc_spectrum_full_AD_K'),'s:',color=ORANGE,markersize=3,label=r'Spectrum with $f_1f_2$')
    ax[0].set(xlabel='Electronic broadening (Ry)',ylabel=r'Formula $T_c$ (K)')
    x=number(mu,'mu_star')
    ax[1].plot(x,number(mu,'Tc_QE_rounded_input_K'),'o-',color=BLACK,markersize=3,label='QE rounded inputs')
    ax[1].plot(x,number(mu,'Tc_spectrum_simple_K'),'--',color=BLUE,label='Spectrum simplified')
    ax[1].plot(x,number(mu,'Tc_spectrum_full_AD_K'),'s:',color=ORANGE,markersize=3,label=r'Spectrum with $f_1f_2$')
    ax[1].set(xlabel=r'Assumed $\mu^*$',ylabel=r'Formula $T_c$ (K)')
    for i,a in enumerate(ax):a.set_ylim(bottom=0);panel(a,chr(97+i),publication)
    ax[0].legend(frameon=False)
    save(fig,out,'tc-formulas',publication)

    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    for sigma,color,line in [(.005,ORANGE,'--'),(.020,BLUE,'-')]:
        rows=[r for r in spec if r['route']=='matdyn.x' and abs(float(r['sigma_Ry'])-sigma)<1e-9]
        x=number(rows,'frequency_THz');y=number(rows,'a2F')
        ax[0].plot(x,y,color=color,linestyle=line,label=f'{sigma:.3f} Ry')
        # Same raw values; only the viewing limits change for the right panel.
        ax[1].plot(x,y,color=color,linestyle=line)
    ax[0].axhline(0,color=BLACK,linewidth=.6);ax[1].axhline(0,color=BLACK,linewidth=.6)
    ax[0].set(xlabel='Frequency (THz)',ylabel=r'Raw interpolated $\alpha^2F$')
    ax[1].set(xlabel='Frequency (THz)',ylabel=r'Raw $\alpha^2F$ near zero',ylim=(-.007,.015))
    for i,a in enumerate(ax):panel(a,chr(97+i),publication)
    ax[0].legend(frameon=False)
    save(fig,out,'a2f-negative-values',publication)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('data'))
    p.add_argument('--output',type=Path,default=Path('figures'))
    p.add_argument('--mode',choices=['both','web','publication'],default='both')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    for pub in ([False,True] if a.mode=='both' else [a.mode=='publication']):
        draw(a.data,a.output,pub)
    print('Raw values retained; no clipping, absolute-value repair, or extra spin factor.')
    print('Publication PDF: 7 pt text, 8 pt bold black panel labels, embedded type-42 fonts.')
    print('Scientific status: formula demonstration; material Tc convergence not established.')

if __name__=='__main__':main()
```

</details>

## 二维异质结 ZrCl₂/Sc₂C：保存 Tc 表核查与来源状态

前面的三维 Al（32³ 与 48³）在 0.005–0.050 Ry 范围内没有交点。ZrCl₂/Sc₂C 的原始 10 THz ph64/ph96 计算已完成；保存的 18 THz lambdax 表尚未绑定生成输入、运行命令与 QE 可执行文件，ph64.1/ph96.1 只有候选输入而无完整输出对。本节报告表格算术与来源边界，不将其称为已验证 Tc。

1. **先核对输入参数与保存输出之间的对应关系**：
ph64/ph96 原始 lambdax.in 首行为 10 0.12 1：emax=10 THz，ngaussq=1 为 Methfessel–Paxton。QE 7.1 lambda.f90 中 ngaussq=0 才是普通 Gaussian。10 THz 输出的谱积分与直接 λ 在全表的差值为 0.015–0.047；18 THz 保存表最大绝对差为 0.000102。高频模式可通过展宽尾部贡献低于 emax 的频率。由于 18 THz 输出没有生成输入、运行命令或 QE 可执行文件记录，不能将两组差异只归因于 emax。参见 <a href="https://raw.githubusercontent.com/QEF/q-e/qe-7.1/PHonon/PH/lambda.f90">QE 7.1 lambda.f90 源码</a>。
2. **读取两个 Tc 表的线性插值交点**：
按打印到 0.001 K 的 Tc 行分段线性插值，匹配输入的 10 THz 表有两个交点（σ≈0.001750 Ry、Tc≈14.594 K；σ≈0.003091 Ry、Tc≈13.513 K）。来源未闭合的 18 THz 保存表有一个诊断性交点（σ≈0.003579 Ry、Tc≈13.587 K，按两位小数为 13.59 K）。额外插值位数不是物理精度，交点也不能证明 k 网格收敛。Nσ(EF) 在 σ=0.004 与 0.005 Ry 的样点较接近，但不足以宣称进入收敛区。ph64.1/ph96.1 准备输入为 18 0.12 1、el_ph_sigma=0.0005 Ry，目前没有完整 Tc 输出对。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-k64-k96-tc.png" alt="ZrCl₂/Sc₂C 两网格保存 Tc 表及线性插值交点" loading="lazy"/><figcaption>两个展宽表的配对诊断：（左）匹配输入的 10 THz Tc 表和来源未闭合的 18 THz 保存表；（右）由脚本按相邻采样点插值得到的 ΔTc=0 位置。18 THz 根仅描述打印表，不代表物理收敛；加密分支没有完整 Tc 输出对。</figcaption></figure>

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-k64-k96-moments.png" alt="ZrCl₂/Sc₂C 两网格 N(EF)、耦合强度与频率矩保存表的对照" loading="lazy"/><figcaption>保存表的 Nσ(EF)、直接 λ 与匹配 10 THz 谱积分，以及 ωlog 对照。σ=0.004 和 0.005 Ry 的 Nσ(EF) 样点较接近；单凭这两个网格和采样点不能推出收敛。</figcaption></figure>

Tc 表算术核对及其来源标记见 [tc-intersections.json](/Atlas/examples/zrcl2-sc2c/tc-intersections.json)。可下载 ph64/ph96 保存输出表与绘图脚本；其中 18 THz 输出仍缺生成记录。

## 文献中的超导临界温度相图与多口袋能隙分布图例（附 DOI 溯源）

在完成单构型的 `Tc(σ)` 与 `μ*` 收敛检验后，文献常将 `Tc` 映射到外部连续调控参量（双轴应变、载流子掺杂、压力）构建二维相图，或进一步在多口袋费米面上分辨超导能隙分布。下面结合两幅文献原图说明常见的数据呈现方式：

### 1. 应变–掺杂二维连续参量空间中的等 Tc 热力相图

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_2DPhaseDiagram_Strain_Doping_Tc_BC_Fig4d.jpg" alt="应变与载流子掺杂双参量空间中的超导临界温度 Tc 二维热力相图与稳定域边界" loading="lazy"/><figcaption>二维超导体系在双轴应变与载流子掺杂浓度双参量空间中的超导临界温度 T<sub>c</sub> 二维热力相图及晶格动力学稳定域边界。图片来源：<em>Phys. Rev. B</em> <strong>111</strong>, 174524 (2025)，<a href="https://doi.org/10.1103/PhysRevB.111.174524" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.111.174524</a>。</figcaption></figure>

- **数据组织要点**：当研究包含多个应变点或静电掺杂浓度时，将离散构型计算得到的 `Tc` 绘制为二维热力等值线图，并标出声子出现虚频的动力学失稳边界，能够直观展示声子软化增强 `λ` 与晶格失稳之间的竞争关系。

### 2. 单层 NbSe₂ 的超导能隙能量直方图、CDW 反折叠费米面与动量分辨能隙

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_AnisotropicGap_CDW_FS_NbSe2_Zheng2019_Fig2.jpg" alt="单层 NbSe₂ 在不同温度下的超导能隙直方图、3×3 CDW 反折叠费米面谱权重与 2 K 下费米面口袋上的能隙分布" loading="lazy"/><figcaption>单层 NbSe<sub>2</sub> 的三面板超导能隙与费米面分析：(a) 在 T = 2、2.8、3.6、4.4 K 四个温度下费米面上各 k 点超导能隙 Δ<sub>k</sub> 的纵向能量分布直方图，(b) 3×3 电荷密度波（CDW）相反折叠到原始布里渊区的费米面谱权重 W<sub>k</sub>，以及 (c) T = 2 K 时超导能隙 Δ<sub>k</sub> 在 Γ 口袋与 K/K′ 口袋上的二维动量空间色标分布。图片来源：Zheng et al., <em>Phys. Rev. B</em> <strong>99</strong>, 161119(R) (2019)，<a href="https://doi.org/10.1103/PhysRevB.99.161119" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.99.161119</a>。</figcaption></figure>

- **数据组织要点**：当材料费米面同时包含布里渊区中心空穴口袋与角点口袋（如单层 `NbSe₂` 或本页 `ZrCl₂/Sc₂C` 的 Γ 六瓣口袋与 K 三角形口袋）时，各向同性 Allen–Dynes 公式给出的是全布里渊区平均 `Tc`；进入各向异性求解后，结合能量直方图（子图 a）与二维费米面着色图（子图 c），可以直接分辨不同费米面口袋上的能隙大小差异及随温度升高的闭合过程。

下一步：把同一份完整谱交给 [EPW / Eliashberg 方程](/Atlas/m/epw-eliashberg/qe/)，比较相同 μ* 下的公式估算与方程求解；回到 [α²F 与累计 λ](/Atlas/m/eliashberg-a2f/qe/)可以定位频段贡献，需要追到单 q、单模时继续读[声子线宽](/Atlas/m/phonon-linewidth/qe/)。

```text
完整同协议逐 q EPC → q / 权重 / 模式 / 展宽 / 频率范围核对
        ↓
lambda.x 的 λq、ωlog、Tc ↔ 独立源码算法复算
        ↓
同一非负 α²F → λspec、ωlog、ν̄₂ → 明确 μ*
        ↓
简式与含 f₁f₂ 公式对照
        ↓
k / q / 展宽 / 声子稳定性验收后，才决定材料结论
```
