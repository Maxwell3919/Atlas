from pathlib import Path
import csv,json,sys
p=Path(sys.argv[1]);rows=[]
for case in ['baseline','grid_control','H1_y_plus','H1_y_minus']:
 r=json.loads((p/'cases'/case/'postprocessing.json').read_text())
 for i,(native,ev) in enumerate(zip(r['forces_Ha_Bohr'],r['forces_eV_A']),1):rows.append([case,r['energy_Ha'],i,['O','H','H'][i-1],*native,*ev])
with (p/'native_energy_forces.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['case','energy_Ha','atom_index','element','Fx_Ha_Bohr','Fy_Ha_Bohr','Fz_Ha_Bohr','Fx_eV_A','Fy_eV_A','Fz_eV_A']);w.writerows(rows)
print('Exported12actualatomrows; nativeHa/HaBohr and converted eV/A')
