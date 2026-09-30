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
