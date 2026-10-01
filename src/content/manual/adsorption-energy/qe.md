H₂ 解离后以 H 原子吸附在金属表面，能量参照包含洁净表面和气相分子。这里保留的是三层 Al(111)、上下两面各一个 atop H 的真实算例；它演示气相参照、每个吸附原子的归一化和成对参数检查。两张单层组成异质结时，参照应换成各自明确的单层状态，具体路线见 [异质结构建模与结合能参照](/Atlas/m/heterostructure-modeling/vasp/)。

本例不提供 ZrCl₂/Sc₂C 或 SnSe₂/Sr₂N 的界面结合能。数据包与后处理仍保留，便于核对“用了什么参考态，三能差包含什么”。

[下载完整计算包](/Atlas/examples/h-al111-adsorption-files.tar.gz)，包括 13 项实际计算的输入、OUT、XML 和数值表。普通 [SCF](/Atlas/m/scf/qe/) 与 [固定晶胞弛豫](/Atlas/m/relax/qe/) 从链接进入，下面只展开吸附问题增加的模型和能量关系。

## 表面、覆盖度与分子参照

洁净表面有 3 个 Al，吸附态有 3 个 Al 与 2 个 H。每个表面原胞每面一个 H，所以每面覆盖度都是 1 ML。晶格来自同套 PBE USPP 的 fcc Al 优化，立方晶格常数 4.04281076 Å，对应 Al(111) 面内周期 2.85869891 Å。晶胞高度 22.86823576 Å，初始相邻周期 H 层间空白 15 Å；洁净与吸附表面使用同一个晶胞。

中层 Al 固定，外层与 H 可移动，洁净与吸附表面分别优化。因此后面的能量差包含表面原子的结构调整，不能解释成把 H 放进一份完全冻结表面得到的纯电子作用能。

气相 H₂ 放在 10 Å 立方盒中，用 Γ 点优化，最后 H–H 为 0.75034816 Å。它不能放进横向约 2.86 Å 的表面原胞当作孤立分子；12 Å 分子盒另用于镜像对照。[结构构造记录](/Atlas/examples/h-al111-adsorption/sources/construction.json)和 [实际最终坐标](/Atlas/examples/h-al111-adsorption/structures.json)可直接查阅。

实际软件为 QE 7.5，非自旋极化 PBE，Al/H 使用 pslibrary 1.0.0 的标量相对论 USPP。截断为 60/640 Ry，冷展宽 `mv` 与 `degauss=0.01 Ry`，电子阈值 `1e-9 Ry`。各表面采用二维网格，H₂ 为 Γ 点；三份能量保持相同泛函、元素赝势、截断和能量读取约定。完整 [洁净表面输入](/Atlas/examples/h-al111-adsorption/clean-slab/relax.in)和 [H₂ 输入](/Atlas/examples/h-al111-adsorption/h2-10A/relax.in)与吸附态配套。

## 吸附态输入中的约束

下面保留实际吸附态输入。行末 `0 0 0` 固定中层，`1 1 1` 允许原子移动；使用 `relax` 保持晶胞。BFGS 的力停止线为 `2e-4 Ry/Bohr`，约 0.00514 eV/Å，能量变化线为 `1e-5 Ry`。

```console
[preston@preston-System-Product-Name h-al111-adsorption]$ cat adsorbed/relax.in
&CONTROL
 calculation='relax'
 prefix='adsorbed'
 outdir='./tmp'
 pseudo_dir='../pseudo'
 tstress=.true.
 tprnfor=.true.
 nstep=35
 etot_conv_thr=1.0d-5
 forc_conv_thr=2.0d-4
/
&SYSTEM
 ibrav=0
 nat=5
 ntyp=2
 nbnd=12
 ecutwfc=60
 ecutrho=640
 occupations='smearing'
 smearing='mv'
 degauss=0.01
/
&ELECTRONS
 conv_thr=1.0d-9
/
&IONS
 ion_dynamics='bfgs'
/
ATOMIC_SPECIES
Al 26.9815385 Al.pbe-n-rrkjus_psl.1.0.0.UPF
H 1.00794 H.pbe-rrkjus_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
2.858698905630 0.000000000000 0.000000000000
1.429349452815 2.475705874046 0.000000000000
0.000000000000 0.000000000000 22.868235764697
ATOMIC_POSITIONS angstrom
Al 2.858698905630 1.650470582697 9.100000000000 1 1 1
Al 0.000000000000 0.000000000000 11.434117882349 0 0 0
Al 1.429349452815 0.825235291349 13.768235764697 1 1 1
H 2.858698905630 1.650470582697 7.500000000000 1 1 1
H 1.429349452815 0.825235291349 15.368235764697 1 1 1
K_POINTS automatic
6 6 1 0 0 0
[preston@preston-System-Product-Name h-al111-adsorption]$
```

[完整运行脚本](/Atlas/examples/h-al111-adsorption/adsorbed/run.sh)记录了原 4 个 MPI 进程和分开的标准输出、错误流；此处读取已有结果即可。初始试算虽电子收敛，H 的力仍约 0.00331637 Ry/Bohr，因而又进行了离子优化。最终三份 `relax.out` 都有 BFGS 结束记录，初始三能差使用的是这些最终值。

## 用同一种能量字段相减

取能量时三者都使用 QE 的 `! total energy`。它包含当前冷展宽下的 `F=E−TS` 数值约定；不能从某份输出改取 `internal energy`，再与另两份的 `F` 相减。本次 H₂ 的占据已接近整数，但仍使用同一项读取。按“每一个吸附 H”归一化：

```text
Eads (eV/H) = [E(Al3H2) − E(Al3) − E(H2)] × 13.605693122994 / 2
```

因晶胞内吸附了两个 H，能量差按两个 H 归一化，得到每个 H 的值；气相参考取一整个 H₂ 分子的总能。将三份最终值代入：

```text
[(-17.3494214515) − (-15.0701501110) − (-2.3332211394)] Ry
× 13.605693122994 eV/Ry ÷ 2 = 0.36701220 eV/H
```

这个定义下负值表示相对“洁净薄膜 + 气相 H₂”降低了电子能量，正值表示提高。本次 6×6×1 协议给出正值：在这组指定模型和参考态下，这个解离吸附构型并不放热。它没有给出 H₂ 解离势垒，也没有证明 atop 是最低吸附位点；高对称点的力小，同样不能代替横向位移或振动稳定性检查。



该定义与界面冻结能量差有两个具体差别：H 的来源是气相 H₂，洁净与吸附表面又分别松弛。换成异质双层时，应按 [同胞 A/B 路线](/Atlas/m/heterostructure-modeling/vasp/#单层参照决定结合能的含义)选取参考，不能只把公式中的 H₂ 改成另一个材料名称。

## 参数检查必须成对改变表面

已有三组初始对照使用同一个 H₂ 参照，分别成对增加表面网格、增加周期高度，另有单独扩大 H₂ 盒子的计算。初始 6×6×1 网格给出 0.36701220 eV/H。

| 参数变化 | Eads (eV/H) | 相对 k6 (meV/H) | 本例 10 meV/H 比较线 |
| --- | ---: | ---: | --- |
| 6×6×1 → 8×8×1 | 0.38008429 | +13.072091 | 超出 |
| 晶胞高度 c 增加 5 Å | 0.36701288 | +0.000675 | 线内 |
| H₂ 盒长 10 → 12 Å | 0.36701462 | +0.002419 | 线内 |



增加真空或分子盒对当前三能差的影响较小，而 6→8 网格的变化为 13.072091 meV/H，超过此例选用的 10 meV/H 比较线。这里的线是教学例子的报告标准，不能据此给其他材料统一规定误差容限。

随后在 12×12×1 下分别优化两个表面，再把各自最终几何保持不变，使用 16×16×1 计算能量和力。以下数值来自同一组已有输出：

| 比较 | Eads k12 (eV/H) | Eads k16 (eV/H) | Δ (meV/H) | 洁净表面 Fmax k16 (Ry/Bohr) | 吸附表面 Fmax k16 (Ry/Bohr) | 2×10⁻⁴ 力线 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| k12-relaxed → k16-fixed | 0.36515144 | 0.37050785 | +5.356413 | 0.00252060 | 0.00166686 | 两者均超出 |

这轮能量与力的联合检查未通过：能量差位于本例 10 meV/H 比较线内，洁净与吸附表面的 16 网格最大力分别约为所设力阈值的 12.6 倍和 8.3 倍。



由此得到的判断很具体：这组固定几何下，三能差对 12→16 网格的变化为 5.356413 meV/H，但两个表面的力均超过原优化力线。能量差足够小没有使 12 网格的结构在 16 网格下自动满足停止条件。以此判断吸附几何，需继续用目标网格优化并核对；本次记录在这里结束。

[成组三能差](/Atlas/examples/h-al111-adsorption/refined-adsorption-energy.csv)与[逐结构力表](/Atlas/examples/h-al111-adsorption/refined-force-check.csv)保留原数值。H₂ 的来源、覆盖度和 atop 位点没有在这些检查中改变，所以它们也不能证明其它吸附位点或其它覆盖度的结果。

## 重算三能差与力对照表

后处理输入是五张实际 CSV：`energy-table.csv`、`adsorption-energy.csv`、`refined-energy-table.csv`、`refined-adsorption-energy.csv`、`refined-force-check.csv`。原始读取代码 [analyse_adsorption.py](/Atlas/examples/h-al111-adsorption/analyse_adsorption.py)和 [analyse_refinement.py](/Atlas/examples/h-al111-adsorption/analyse_refinement.py)从 OUT/XML 提取数据；以下独立程序复核表格的参考与归一化，不重新执行 QE。

```text
读取上述五张 Al(111)/H CSV，按每组 clean、adsorbed、H2 的相同协议重算
(Eadsorbed-Eclean-EH2)*13.605693122994/2，输出 eV/H 及相对基准的 meV/H。
核对两 H/三 Al 的模型计数、协议配对和实际力列；分开报告能量变化与力停止线。
原值必须保持，不由能量检查通过替代几何检查，不把 H2 参照改成孤立 H。
```

[完整复核源码](/Atlas/examples/thermo-postprocessing/adsorption/review_al111_adsorption.py)

<details>
<summary>review_al111_adsorption.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Recompute the finite Al(111)-H adsorption checks as audit tables."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

RY_TO_EV = 13.605693122994
FORCE_LIMIT_RY_BOHR = 2e-4
ENERGY_LIMIT_EV_H = 0.010
ROOT = Path(__file__).resolve().parent


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing CSV header")
        return list(reader)


def unique_by(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "")
        if not value or value in out:
            raise ValueError(f"{label}: empty or duplicate {key} {value!r}")
        out[value] = row
    return out


def close(a: float, b: float, label: str, atol: float = 1e-10) -> None:
    if not math.isfinite(a) or not math.isclose(a, b, rel_tol=0, abs_tol=atol):
        raise ValueError(f"{label}: values disagree ({a:.12g} vs {b:.12g})")


def adsorption_eV_H(
    raw: dict[str, dict[str, str]], clean_case: str, ads_case: str, gas_case: str, label: str
) -> tuple[float, dict[str, dict[str, str]]]:
    try:
        clean, ads, gas = raw[clean_case], raw[ads_case], raw[gas_case]
    except KeyError as exc:
        raise ValueError(f"{label}: missing raw case {exc.args[0]!r}") from exc
    if (int(clean["nAl"]), int(clean["nH"])) != (3, 0):
        raise ValueError(f"{label}: clean reference is not the three-Al slab")
    if (int(ads["nAl"]), int(ads["nH"])) != (3, 2):
        raise ValueError(f"{label}: adsorbed reference is not Al3H2")
    if (int(gas["nAl"]), int(gas["nH"])) != (0, 2):
        raise ValueError(f"{label}: gas reference is not H2")
    value = (
        float(ads["total_energy_Ry"])
        - float(clean["total_energy_Ry"])
        - float(gas["total_energy_Ry"])
    ) * RY_TO_EV / 2
    return value, {"clean": clean, "ads": ads, "gas": gas}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "review")
    args = parser.parse_args()
    outdir = args.outdir if args.outdir.is_absolute() else ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    base_raw = unique_by(read_rows(ROOT / "energy-table.csv"), "case", "baseline raw table")
    refined_raw = unique_by(read_rows(ROOT / "refined-energy-table.csv"), "case", "refined raw table")
    summary = read_rows(ROOT / "adsorption-energy.csv")
    summary_by_protocol = unique_by(summary, "protocol", "baseline summary")
    required_protocols = {"baseline-k6", "k8", "vacuum20", "H2-box12"}
    if set(summary_by_protocol) != required_protocols:
        raise ValueError(f"baseline summary protocols differ: {sorted(summary_by_protocol)}")

    baseline_values: dict[str, float] = {}
    baseline_table: list[dict[str, str]] = []
    for protocol in ("baseline-k6", "k8", "vacuum20", "H2-box12"):
        row = summary_by_protocol[protocol]
        value, matched = adsorption_eV_H(
            base_raw, row["clean_case"], row["adsorbed_case"], row["gas_case"], protocol
        )
        close(value, float(row["adsorption_eV_H"]), f"{protocol} summary Eads")
        baseline_values[protocol] = value
        close((value - baseline_values["baseline-k6"]) * 1000, float(row["change_from_baseline_meV_H"]), f"{protocol} summary delta")
        baseline_table.append({
            "protocol": protocol,
            "clean_case": row["clean_case"],
            "adsorbed_case": row["adsorbed_case"],
            "gas_case": row["gas_case"],
            "clean_stage": matched["clean"]["stage"],
            "adsorbed_stage": matched["ads"]["stage"],
            "gas_stage": matched["gas"]["stage"],
            "adsorption_eV_H": f"{value:.12f}",
            "delta_from_baseline_meV_H": f"{(value - baseline_values['baseline-k6']) * 1000:.9f}",
        })

    refined_summary = read_rows(ROOT / "refined-adsorption-energy.csv")
    refined_by_protocol = unique_by(refined_summary, "protocol", "refined summary")
    expected_refined = {"k12-relaxed", "k16-fixed"}
    if set(refined_by_protocol) != expected_refined:
        raise ValueError(f"refined protocols differ: {sorted(refined_by_protocol)}")
    refined_values: dict[str, float] = {}
    for protocol in ("k12-relaxed", "k16-fixed"):
        row = refined_by_protocol[protocol]
        value, matched = adsorption_eV_H(
            refined_raw, row["clean_case"], row["adsorbed_case"], row["gas_case"], protocol
        )
        close(value, float(row["adsorption_eV_H"]), f"{protocol} summary Eads")
        for name, raw_value in (
            ("clean_energy_Ry", matched["clean"]["total_energy_Ry"]),
            ("adsorbed_energy_Ry", matched["ads"]["total_energy_Ry"]),
            ("h2_energy_Ry", matched["gas"]["total_energy_Ry"]),
        ):
            close(float(row[name]), float(raw_value), f"{protocol} {name}")
        refined_values[protocol] = value

    delta_refined_meV = (refined_values["k16-fixed"] - refined_values["k12-relaxed"]) * 1000
    energy_status = (
        "within selected 10 meV/H line"
        if abs(delta_refined_meV) <= ENERGY_LIMIT_EV_H * 1000
        else "outside selected 10 meV/H line"
    )

    force_rows = unique_by(read_rows(ROOT / "refined-force-check.csv"), "case", "force summary")
    refined_table: list[dict[str, str]] = []
    for case, parent_case in (("clean-k16", "clean-k12-relax"), ("ads-k16", "ads-k12-relax")):
        expected = force_rows.get(case)
        if not expected:
            raise ValueError(f"force summary missing {case}")
        current, prior = refined_raw[case], refined_raw[parent_case]
        close(float(expected["max_force_k16_Ry_Bohr"]), float(current["max_force_component_Ry_Bohr"]), f"{case} force")
        close(float(expected["max_force_k12_Ry_Bohr"]), float(prior["max_force_component_Ry_Bohr"]), f"{case} parent force")
        force_k12 = float(prior["max_force_component_Ry_Bohr"])
        force_k16 = float(current["max_force_component_Ry_Bohr"])
        force_change = float(expected["max_force_change_Ry_Bohr"])
        if not math.isfinite(force_change) or force_change < 0:
            raise ValueError(f"{case}: invalid stored component-wise force change")
        k16_flag = expected["k16_within_2e4"].strip().lower() == "true"
        change_flag = expected["change_within_2e4"].strip().lower() == "true"
        if k16_flag != (force_k16 <= FORCE_LIMIT_RY_BOHR):
            raise ValueError(f"{case}: stored k16 force criterion disagrees with recomputed value")
        if change_flag != (force_change <= FORCE_LIMIT_RY_BOHR):
            raise ValueError(f"{case}: stored force-change criterion disagrees with recomputed value")
        refined_table.append({
            "case": case,
            "parent_case": parent_case,
            "k12_Eads_eV_H": f"{refined_values['k12-relaxed']:.12f}",
            "k16_fixed_Eads_eV_H": f"{refined_values['k16-fixed']:.12f}",
            "k12_to_k16_delta_meV_H": f"{delta_refined_meV:.9f}",
            "max_force_k12_Ry_Bohr": f"{force_k12:.12g}",
            "max_force_k16_Ry_Bohr": f"{force_k16:.12g}",
            "max_force_change_k12_to_k16_Ry_Bohr": f"{force_change:.12g}",
            "force_change_within_limit": str(force_change <= FORCE_LIMIT_RY_BOHR),
            "selected_force_limit_Ry_Bohr": f"{FORCE_LIMIT_RY_BOHR:.1e}",
            "k16_force_factor_over_limit": f"{force_k16 / FORCE_LIMIT_RY_BOHR:.6f}",
            "energy_delta_within_10_meV_H": str(abs(delta_refined_meV) <= ENERGY_LIMIT_EV_H * 1000),
            "k16_force_within_limit": str(force_k16 <= FORCE_LIMIT_RY_BOHR),
        })

    write_csv(outdir / "al111-h-adsorption-review.csv", list(baseline_table[0]), baseline_table)
    write_csv(outdir / "al111-h-refined-force-review.csv", list(refined_table[0]), refined_table)

    report = [
        "# Al(111)-H adsorption energy review",
        "",
        "- The stated observable is Eads = (E(Al3H2) - E(Al3) - E(H2)) × 13.605693122994 / 2 in eV per H.",
        "- Energies are read from the supplied Quantum ESPRESSO total_energy_Ry fields; the two adsorbed H atoms account for the divisor 2.",
        "- The 10 meV/H energy comparison and 2×10⁻⁴ Ry/Bohr force limit are the selected teaching thresholds for this case.",
        "- The 6→8 k-grid adsorption-energy change exceeds 10 meV/H; vacuum and H2-box changes are below it.",
        f"- The 12-relaxed→16-fixed energy difference is {delta_refined_meV:+.6f} meV/H ({energy_status}).",
        "- The 16-grid clean-slab and adsorbed-slab forces are checked separately; both exceed the selected force limit, so the combined energy-and-force acceptance is false.",
        "- Component-wise force changes come from the supplied refined-force-check.csv, generated from matched k12 and k16 force arrays; this script checks their reported threshold flags against the selected limit.",
        "- Scope is the supplied symmetric two-H atop model and its stated finite checks; this review makes no claim about other adsorption sites, coverage, slab thickness, barriers, or vibrational and thermal terms.",
        "",
        "## Finite protocol comparisons",
        "",
        "| protocol | clean / adsorbed / gas cases | Eads (eV/H) | change from k6 (meV/H) |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in baseline_table:
        report.append(
            f"| {row['protocol']} | {row['clean_case']} / {row['adsorbed_case']} / {row['gas_case']} | {float(row['adsorption_eV_H']):.8f} | {float(row['delta_from_baseline_meV_H']):+.6f} |"
        )
    report.extend([
        "",
        "## 12-grid relaxation to 16-grid fixed-geometry check",
        "",
        "| pair | Eads k12 (eV/H) | Eads k16 (eV/H) | Δ (meV/H) | Fmax clean k16 (Ry/Bohr) | Fmax ads k16 (Ry/Bohr) | force limit (Ry/Bohr) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| k12-relaxed → k16-fixed | {refined_values['k12-relaxed']:.8f} | {refined_values['k16-fixed']:.8f} | {delta_refined_meV:+.6f} | {float(refined_table[0]['max_force_k16_Ry_Bohr']):.8f} | {float(refined_table[1]['max_force_k16_Ry_Bohr']):.8f} | {FORCE_LIMIT_RY_BOHR:.1e} |",
        "",
        "The energy difference is within the selected 10 meV/H comparison line. The maximum forces are 12.60× and 8.33× the selected force limit, respectively; energy-only agreement therefore does not pass the combined check.",
    ])
    (outdir / "al111-h-adsorption-review.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"baseline_protocols={','.join(sorted(required_protocols))}")
    print(f"baseline_k6={baseline_values['baseline-k6']:.12f} eV/H")
    print(f"k8_change={(baseline_values['k8']-baseline_values['baseline-k6'])*1000:+.6f} meV/H")
    print(f"k12_to_k16_change={delta_refined_meV:+.6f} meV/H ({energy_status})")
    print(f"force_limit={FORCE_LIMIT_RY_BOHR:.1e} Ry/Bohr clean={float(refined_table[0]['max_force_k16_Ry_Bohr']):.8f} ads={float(refined_table[1]['max_force_k16_Ry_Bohr']):.8f}")
    print(f"wrote {outdir / 'al111-h-adsorption-review.csv'}")
    print(f"wrote {outdir / 'al111-h-refined-force-review.csv'}")
    print(f"wrote {outdir / 'al111-h-adsorption-review.md'}")


if __name__ == "__main__":
    main()
```

</details>

将上述 CSV 和程序放在同一目录，执行：

```bash
python3 review_al111_adsorption.py --outdir review
```

实际复核输出的数值部分为：

```text
baseline_protocols=H2-box12,baseline-k6,k8,vacuum20
baseline_k6=0.367012203736 eV/H
k8_change=+13.072091 meV/H
k12_to_k16_change=+5.356413 meV/H (within selected 10 meV/H line)
force_limit=2.0e-04 Ry/Bohr clean=0.00252060 ads=0.00166686
```

[复核报告](/Atlas/examples/thermo-postprocessing/adsorption/review/al111-h-adsorption-review.md)给出成对表和力判读。完整输入、输出及脚本始终保存在页首数据包中。

## 参考态与研究用途

[Kocabas 等，*Determination of Dynamically Stable Electrenes towards Ultra-fast Charging Battery Applications*](https://doi.org/10.1021/acs.jpclett.8b01468)，Fig. 4 与其前面的能量定义采用 $E_{Ad}=E_{AE}-E_P-E_A$，其中 $E_A$ 是金属体相每原子能量；Li、Na、K 用 bcc，Ca 用 fcc。论文在 2×2×1 表面超胞放一个吸附原子，覆盖度 25%，并在 Fig. 5 另行计算迁移势垒。这里借它说明：吸附能首先回答的是相对于哪一种物质来源的能量代价，覆盖度和势垒又是各自的条件与分析量。

本例则是 H₂ 气相参照、每面 1 ML 的 H/Al(111)，没有沿用论文的金属体相参照，也没有迁移势垒。两套数据的数值和研究用途应分别阅读。当前界面电子结构路线需要的是具体异质结的单层参照与界面构型比较；这份通用吸附记录保留其原有教学用途。

[QE 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [ASE 表面构造](https://ase-lib.org/ase/build/surface.html)
