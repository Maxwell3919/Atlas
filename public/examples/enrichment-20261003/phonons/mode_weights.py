"""Compare e and normalized-u weights for one saved Gamma mode.
Usage: python3 mode_weights.py gamma-mode-products.json
No force-constant reconstruction or new electronic calculation is performed.
"""
import json
import sys
from pathlib import Path

source = Path(sys.argv[1])
products = json.loads(source.read_text())
grid = products["grids"]["gamma32"]
mode = next(m for m in grid["modes"] if m["optical_mode"] == 1)
weights = lambda vectors: [sum(x * x for x in v) for v in vectors]
e_weights = weights(mode["e"])
u_weights = weights(mode["u"])
assert abs(sum(e_weights) - 1) < 1e-10
assert abs(sum(u_weights) - 1) < 1e-10
assert max(abs(a - b) for a, b in
           zip(e_weights, mode["atom_e_weights"])) < 1e-10
result = {
    "source": source.name,
    "grid": "gamma32",
    "optical_mode": mode["optical_mode"],
    "full_mode_after_three_translations":
        mode["full_mode_after_three_translations"],
    "frequency_cm1": mode["frequency_cm1"],
    "normalization": "each whole-mode vector has squared norm 1",
    "atoms": [{"atom": i, "symbol": symbol,
               "e_squared_weight": e, "u_squared_weight": u}
              for i, (symbol, e, u) in enumerate(
                  zip(grid["symbols"], e_weights, u_weights), 1)],
    "total_e_weight": sum(e_weights),
    "total_u_weight": sum(u_weights),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
