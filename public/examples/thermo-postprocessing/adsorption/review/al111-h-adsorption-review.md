# Al(111)-H adsorption energy review

- The stated observable is Eads = (E(Al3H2) - E(Al3) - E(H2)) × 13.605693122994 / 2 in eV per H.
- Energies are read from the supplied Quantum ESPRESSO total_energy_Ry fields; the two adsorbed H atoms account for the divisor 2.
- The 10 meV/H energy comparison and 2×10⁻⁴ Ry/Bohr force limit are the selected teaching thresholds for this case.
- The 6→8 k-grid adsorption-energy change exceeds 10 meV/H; vacuum and H2-box changes are below it.
- The 12-relaxed→16-fixed energy difference is +5.356413 meV/H (within selected 10 meV/H line).
- The 16-grid clean-slab and adsorbed-slab forces are checked separately; both exceed the selected force limit, so the combined energy-and-force acceptance is false.
- Component-wise force changes come from the supplied refined-force-check.csv, generated from matched k12 and k16 force arrays; this script checks their reported threshold flags against the selected limit.
- Scope is the supplied symmetric two-H atop model and its stated finite checks; this review makes no claim about other adsorption sites, coverage, slab thickness, barriers, or vibrational and thermal terms.

## Finite protocol comparisons

| protocol | clean / adsorbed / gas cases | Eads (eV/H) | change from k6 (meV/H) |
| --- | --- | ---: | ---: |
| baseline-k6 | clean-slab / adsorbed / h2-10A | 0.36701220 | +0.000000 |
| k8 | clean-k8 / ads-k8 / h2-10A | 0.38008429 | +13.072091 |
| vacuum20 | clean-vac20 / ads-vac20 / h2-10A | 0.36701288 | +0.000675 |
| H2-box12 | clean-slab / adsorbed / h2-12A | 0.36701462 | +0.002419 |

## 12-grid relaxation to 16-grid fixed-geometry check

| pair | Eads k12 (eV/H) | Eads k16 (eV/H) | Δ (meV/H) | Fmax clean k16 (Ry/Bohr) | Fmax ads k16 (Ry/Bohr) | force limit (Ry/Bohr) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| k12-relaxed → k16-fixed | 0.36515144 | 0.37050785 | +5.356413 | 0.00252060 | 0.00166686 | 2.0e-04 |

The energy difference is within the selected 10 meV/H comparison line. The maximum forces are 12.60× and 8.33× the selected force limit, respectively; energy-only agreement therefore does not pass the combined check.
