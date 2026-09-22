from pathlib import Path
import csv
import hashlib
import json

source = Path("teaching-extracts.json")
data = json.loads(source.read_text())
points = data["exfoliation"]
assert len(points) == 21
assert [row[0] for row in points] == list(range(21))
e0 = points[0][1]
with open("exfoliation.csv", "w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["displacement_A", "energy_eV_cell", "delta_energy_meV_cell"])
    for displacement, energy in points:
        writer.writerow([f"{displacement:.1f}", f"{energy:.8f}", f"{1000*(energy-e0):.5f}"])
print("source_sha256", hashlib.sha256(source.read_bytes()).hexdigest())
print("points", len(points))
print(f"E20_minus_E0_eV_cell {points[-1][1]-e0:.8f}")
print(f"E20_minus_E15_meV_cell {1000*(points[-1][1]-points[15][1]):.5f}")
print(f"E20_minus_E19_meV_cell {1000*(points[-1][1]-points[19][1]):.5f}")
