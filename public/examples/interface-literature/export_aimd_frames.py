"""Export existing Al NVE frames with their full periodic cells."""
from pathlib import Path
import sys
import numpy as np
from ase.io import read, write

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("nve-frames")
out.mkdir(parents=True, exist_ok=True)
coarse = root / "aimd/nve-dt20-nosym/trajectory.xyz"
fine = root / "aimd/nve-dt10-nosym/trajectory.xyz"
initial = read(coarse, index=0, format="extxyz")
initial_fine = read(fine, index=0, format="extxyz")
assert np.allclose(initial.positions, initial_fine.positions, atol=1e-10, rtol=0)
assert np.allclose(initial.cell, initial_fine.cell, atol=1e-10, rtol=0)
frames = [("initial.POSCAR", initial),
          ("nve-dt20-end.POSCAR", read(coarse, index=-1, format="extxyz")),
          ("nve-dt10-end.POSCAR", read(fine, index=-1, format="extxyz"))]
for name, atoms in frames:
    assert len(atoms) == 8 and atoms.get_chemical_symbols() == ["Al"] * 8
    assert atoms.pbc.all() and np.allclose(atoms.cell, initial.cell, atol=1e-10, rtol=0)
    if name != "initial.POSCAR":
        assert abs(float(atoms.info["time_fs"]) - 48.37768653) < 1e-8
    path = out / name
    write(path, atoms, format="vasp", direct=True, vasp5=True, sort=False)
    restored = read(path, format="vasp")
    assert np.allclose(restored.cell, atoms.cell, atol=1e-10, rtol=0)
    assert np.allclose(restored.positions, atoms.positions, atol=1e-10, rtol=0)
    print(name, "coordinate_time_fs =", atoms.info["time_fs"])
