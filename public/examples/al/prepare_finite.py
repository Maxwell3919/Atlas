from pathlib import Path
import json
import numpy as np
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
r=Path(__file__).resolve().parent
j=json.loads((r/"structure.json").read_text())
u=PhonopyAtoms(symbols=["Al"],cell=j["cell_angstrom"],scaled_positions=[[0,0,0]],masses=[26.9815385])
output=r/"finite-generated-check";output.mkdir(exist_ok=True)
for dim,amp in [(2,.01),(2,.02),(3,.01)]:
    ph=Phonopy(u,np.eye(3,dtype=int)*dim,primitive_matrix="P")
    ph.generate_displacements(distance=amp,is_plusminus=True)
    dst=output/f"n{dim}-d{amp:.2f}";dst.mkdir(exist_ok=True)
    ph.save(dst/"phonopy_disp.yaml")
    for i,sc in enumerate(ph.supercells_with_displacements,1):
        np.savetxt(dst/f"cell-{i:03d}.txt",sc.cell,fmt="%.14f")
        np.savetxt(dst/f"positions-{i:03d}.txt",sc.scaled_positions,fmt="%.14f")
    print(dst.name,len(ph.supercells_with_displacements),"displaced supercells")
