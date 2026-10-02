"""Relate normal gaps, nearest distances and in-plane areas in the real model."""
from pathlib import Path
import itertools, json, math, sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
sys.path.insert(0, str(root.resolve()))
from check_model import read_poscar, dot, cross, norm

results = {}
for name in ("POSCAR.reference", "POSCAR.gap3p0"):
    cell, frac, xyz, symbols, normal, height = read_poscar(str(root / name))
    upper = [i for i, el in enumerate(symbols) if el in ("Sn", "Se")]
    lower = [i for i, el in enumerate(symbols) if el in ("Sr", "N")]
    normal_gap = min(dot(xyz[i], normal) for i in upper) - max(dot(xyz[j], normal) for j in lower)
    candidates = []
    for i, j, shift in itertools.product(upper, lower, itertools.product((-1, 0, 1), repeat=3)):
        delta = [sum((frac[i][k] - frac[j][k] + shift[k]) * cell[k][d] for k in range(3)) for d in range(3)]
        candidates.append((norm(delta), i, j, shift, dot(delta, normal)))
    distance, i, j, shift, separation = min(candidates)
    lateral = math.sqrt(max(0.0, distance**2 - separation**2))
    assert abs(separation - normal_gap) < 1e-9
    results[name] = dict(normal_gap_A=normal_gap, nearest_distance_A=distance,
                         nearest_pair_1based=[i + 1, j + 1], image_shift=list(shift),
                         lateral_offset_A=lateral, area_A2=norm(cross(cell[0], cell[1])))
    print(f"{name}: normal={normal_gap:.10f} A lateral={lateral:.10f} A nearest={distance:.10f} A")
reference = read_poscar(str(root / "POSCAR.SnSe2.reference"))
area_ref = norm(cross(reference[0][0], reference[0][1]))
area_common = results["POSCAR.reference"]["area_A2"]
results["SnSe2_area_comparison"] = dict(reference_area_A2=area_ref, common_area_A2=area_common,
                                       area_increase_percent=100*(area_common/area_ref-1))
print(f"SnSe2 area: reference={area_ref:.10f} A2 common={area_common:.10f} A2 increase={100*(area_common/area_ref-1):.8f}%")
(root / "geometry-relations.json").write_text(json.dumps(results, indent=2) + "\n")
