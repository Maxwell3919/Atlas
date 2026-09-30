#!/usr/bin/env python3
"""Recompute the acoustic deformation-potential estimate and expose sensitivities.

Reads only the accepted analysis tables; it does not launch Quantum ESPRESSO.
The reported E1-only propagated error is a regression contribution, not a total
uncertainty or a confidence interval for material mobility.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E_CHARGE_C = 1.602176634e-19
HBAR_J_S = 1.054571817e-34
KB_J_K = 1.380649e-23
ELECTRON_MASS_KG = 9.1093837015e-31
EV_PER_ANGSTROM2_TO_N_PER_M = 16.02176634


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def mobility_cm2_vs(C_N_m: float, E1_eV: float, mx_me: float,
                    md_me: float, temperature_K: float) -> float:
    if C_N_m <= 0 or mx_me <= 0 or md_me <= 0 or temperature_K <= 0:
        raise ValueError("C, masses and temperature must be positive")
    if not math.isfinite(E1_eV) or abs(E1_eV) == 0:
        raise ValueError("E1 must be finite and nonzero")
    mx_kg = mx_me * ELECTRON_MASS_KG
    md_kg = md_me * ELECTRON_MASS_KG
    E1_J = E1_eV * E_CHARGE_C
    mu_m2_vs = (E_CHARGE_C * HBAR_J_S**3 * C_N_m /
                (KB_J_K * temperature_K * mx_kg * md_kg * E1_J**2))
    return mu_m2_vs * 1.0e4


def main() -> None:
    summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    cases = {row["case"]: row for row in read_csv("cases.csv")}
    if summary["failures"]:
        raise SystemExit(f"model gates failed: {summary['failures']}")
    if summary["completed_cases"] != summary["expected_cases"]:
        raise SystemExit("the accepted case set is incomplete")

    fit_to_mass_case = {
        "five_strains": "zero",
        "three_strains": "zero",
        "k16": "k16-zero",
        "vacuum28": "vacuum28-zero",
    }
    rows = {}
    for fit_name, mass_case in fit_to_mass_case.items():
        fit = summary["fits"][fit_name]
        mass = cases[mass_case]
        rows[fit_name] = {
            "mass_case": mass_case,
            "C2D_N_m": fit["C2D_N_m"],
            "E1_eV": fit["E1_eV"],
            "E1_fit_standard_error_eV": fit["E1_standard_error_eV"],
            "mx_me": float(mass["mx_me"]),
            "md_me": float(mass["md_me"]),
            "mobility_cm2_Vs": mobility_cm2_vs(
                fit["C2D_N_m"], fit["E1_eV"],
                float(mass["mx_me"]), float(mass["md_me"]),
                float(summary["temperature_K"])),
        }
    base = rows["five_strains"]["mobility_cm2_Vs"]
    for row in rows.values():
        row["relative_to_five_strains"] = row["mobility_cm2_Vs"] / base - 1.0

    accepted_value = summary["mobility_cm2_Vs"]
    if not math.isclose(base, accepted_value, rel_tol=1e-10, abs_tol=1e-8):
        raise SystemExit(
            f"formula check failed: recomputed {base:.12g}, summary {accepted_value:.12g}")

    e1 = rows["five_strains"]["E1_eV"]
    e1_sigma = rows["five_strains"]["E1_fit_standard_error_eV"]
    relative_mu_sigma_e1_only = 2.0 * e1_sigma / abs(e1)
    report = {
        "model": "K-valley longitudinal acoustic deformation potential only",
        "mobility_cm2_Vs": base,
        "temperature_K": float(summary["temperature_K"]),
        "formula": "e*hbar^3*C2D/(kB*T*mx*md*E1^2)",
        "input_units": {
            "C2D": "N/m",
            "E1": "eV, converted to joule before substitution",
            "mx_md": "multiples of m_e, converted to kg before substitution",
            "output_before_area_conversion": "m^2/(V s)",
            "output_after_area_conversion": "cm^2/(V s); multiply m^2/(V s) by 1e4",
        },
        "conversion_constants": {
            "elementary_charge_C": E_CHARGE_C,
            "hbar_J_s": HBAR_J_S,
            "kB_J_K": KB_J_K,
            "electron_mass_kg": ELECTRON_MASS_KG,
            "1_eV_per_A2_to_N_per_m": EV_PER_ANGSTROM2_TO_N_PER_M,
        },
        "fit_group_sensitivities": rows,
        "E1_fit_only_error_propagation": {
            "E1_standard_error_eV": e1_sigma,
            "relative_mu_standard_error_from_E1_only": relative_mu_sigma_e1_only,
            "mu_standard_error_from_E1_only_cm2_Vs": base * relative_mu_sigma_e1_only,
            "derivative": "d ln(mu)/d ln(|E1|) = -2",
            "limitation": "Excludes C2D/mass-fit, numerical-protocol and physical-model errors; not a total uncertainty.",
        },
        "full_transport_calculation": False,
        "status": "acoustic-DP estimate only; no full electron-phonon scattering integral or Boltzmann transport solution",
    }
    out = ROOT / "transport-parameter-checks.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name, row in rows.items():
        print(f"{name:13s} C2D={row['C2D_N_m']:.6f} N/m  "
              f"E1={row['E1_eV']:.6f} eV  "
              f"mx={row['mx_me']:.6f} me  md={row['md_me']:.6f} me  "
              f"mu={row['mobility_cm2_Vs']:.6f} cm^2/(V s)")
    print(f"E1-fit-only propagated contribution: "
          f"{relative_mu_sigma_e1_only * 100:.4f}% = "
          f"{base * relative_mu_sigma_e1_only:.6f} cm^2/(V s)")
    print(f"Full electron-phonon transport: not calculated; wrote {out.name}")


if __name__ == "__main__":
    main()
