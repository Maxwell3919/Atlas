#!/usr/bin/env python3
from pathlib import Path
import csv
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "delivery"
OUT.mkdir(exist_ok=True)
CASES = [
    ("hetero_0", "hetero_0", "Heterostructure 0%", 0.0, True),
    ("0", "sc2c_frozen_0", "Isolated Sc2C 0%", 0.0, False),
    ("hetero_0015", "hetero_0015", "Heterostructure +1.5%", 1.5, True),
    ("0015", "sc2c_frozen_0015", "Isolated Sc2C +1.5%", 1.5, False),
]
WINDOW = (-2.0, 2.0)
def load_case(spec):
    folder, prefix, name, strain, is_hetero = spec
    d = ROOT / folder
    pw = (d / "pwx.out").read_text(errors="replace")
    pr = (d / "projwfc.out").read_text(errors="replace")
    if "convergence has been achieved" not in pw:
        raise ValueError("SCF not converged: " + name)
    if "JOB DONE." not in pw or "JOB DONE." not in pr:
        raise ValueError("QE output incomplete: " + name)
    fm = next((x for x in pw.splitlines()
               if "the Fermi energy is" in x), None)
    if fm is None:
        raise ValueError("Fermi energy missing: " + name)
    ef = float(fm.split()[-2])
    total = np.loadtxt(d / (prefix + ".pdos_tot"), comments="#")
    energy = total[:, 0] - ef
    sc = np.zeros(len(energy))
    zr = np.zeros(len(energy))
    files = sorted(d.glob(prefix + ".pdos_atm#*_wfc#*"))
    expected = 19 if is_hetero else 10
    if len(files) != expected:
        raise ValueError(name + ": wrong projector file count")
    for f in files:
        match = re.search(r"atm#([0-9]+)", f.name)
        if match is None:
            raise ValueError("Bad projector filename: " + f.name)
        atom = int(match.group(1))
        part = np.loadtxt(f, comments="#")
        if len(part) != len(total):
            raise ValueError("PDOS row count differs: " + f.name)
        if not np.allclose(part[:, 0], total[:, 0], atol=1e-9):
            raise ValueError("PDOS energy grid differs: " + f.name)
        value = part[:, 2:].sum(axis=1)
        if not is_hetero or atom in (2, 5, 6):
            sc += value
        elif atom in (1, 3, 4):
            zr += value
        else:
            raise ValueError("Unexpected heterostructure atom")
    diff = sc + zr - total[:, 2]
    mask = np.abs(energy) <= 0.1
    area = np.trapz(np.abs(total[mask, 2]), energy[mask])
    l1 = 100 * np.trapz(np.abs(diff[mask]), energy[mask]) / area
    peak = np.max(np.abs(total[:, 2]))
    maxerr = 100 * np.max(np.abs(diff)) / peak
    return {"name": name, "strain": strain,
            "hetero": is_hetero, "ef": ef, "energy": energy,
            "sc": sc, "zr": zr, "total": total[:, 2],
            "rows": len(total), "step": np.median(np.diff(total[:, 0])),
            "nproj": len(files), "l1": l1, "maxerr": maxerr,
            "diff": diff}
states = [load_case(item) for item in CASES]
with (OUT / "frozen_pdos_long.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["state", "strain_percent", "fermi_eV",
                     "energy_minus_fermi_eV", "sc2c_pdos",
                     "zrcl2_pdos", "total_projected_pdos",
                     "projected_sum_error"])
    for s in states:
        for i, x in enumerate(s["energy"]):
            writer.writerow([s["name"], s["strain"], s["ef"], x,
                             s["sc"][i], s["zr"][i],
                             s["total"][i], s["diff"][i]])
with (OUT / "frozen_pdos_summary.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["state", "fermi_eV", "rows", "grid_step_eV",
                     "projector_files", "L1_sum_error_pct_EF_pm_0p1eV",
                     "max_sum_error_pct_total_peak"])
    for s in states:
        writer.writerow([s["name"], s["ef"], s["rows"], s["step"],
                         s["nproj"], s["l1"], s["maxerr"]])
fig, axes = plt.subplots(1, 2, figsize=(11, 6), sharex=True,
                         sharey=True)
blue, orange = "#0072B2", "#D55E00"
peaks = []
for strain, ax in zip((0.0, 1.5), axes):
    h = next(s for s in states if s["hetero"]
             and s["strain"] == strain)
    iso = next(s for s in states if not s["hetero"]
               and s["strain"] == strain)
    mask = (h["energy"] >= WINDOW[0]) & (h["energy"] <= WINDOW[1])
    mi = (iso["energy"] >= WINDOW[0]) & (iso["energy"] <= WINDOW[1])
    ax.plot(h["energy"][mask], h["sc"][mask], color=blue,
            lw=1.8, label="Sc2C layer: C#2 + Sc#5-6")
    ax.plot(iso["energy"][mi], iso["sc"][mi], color=blue,
            lw=1.8, ls="--", label="isolated Sc2C: Sc#1-2 + C#3")
    ax.plot(h["energy"][mask], h["zr"][mask], color=orange,
            lw=1.8, label="ZrCl2 layer: Zr#1 + Cl#3-4")
    peaks.extend([np.max(h["sc"][mask]),
                  np.max(iso["sc"][mi]), np.max(h["zr"][mask])])
    ax.axvline(0, color="#555555", lw=0.8, ls=":")
    ax.set_xlim(*WINDOW)
    ax.set_title("0% strain" if strain == 0 else "+1.5% strain")
    ax.set_xlabel("Energy relative to each Fermi level (eV)")
    ax.grid(axis="y", color="#DDDDDD", lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
for ax in axes:
    ax.set_ylim(0, max(peaks) * 1.05)
axes[0].set_ylabel("Projected DOS (states / eV / simulation cell)")
fig.suptitle("Frozen-cell projected DOS near the Fermi level",
             y=0.985, fontsize=14)
fig.text(0.5, 0.94,
         "Atom index = QE input order: hetero #1 Zr, #2 C, #3-4 Cl, #5-6 Sc.",
         ha="center", fontsize=9)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center",
           bbox_to_anchor=(0.5, 0.895), ncol=3,
           frameon=False, fontsize=8)
fig.text(0.5, 0.02,
         "Frozen coordinates, not relaxed equilibrium. EF alignment gives no absolute band offsets or charge transfer.",
         ha="center", fontsize=8, color="#444444")
fig.tight_layout(rect=[0, 0.07, 1, 0.83])
fig.savefig(OUT / "frozen_pdos.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "frozen_pdos.pdf", bbox_inches="tight")
plt.close(fig)
print("Wrote products to", OUT)
for s in states:
    print(s["name"], "EF", s["ef"], "rows", s["rows"],
          "projectors", s["nproj"], "L1 error %", s["l1"],
          "max error %", s["maxerr"])

