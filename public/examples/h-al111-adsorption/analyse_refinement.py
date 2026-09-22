#!/usr/bin/env python3
from pathlib import Path
import json,numpy as np
from analyse_adsorption import read_run,save_csv,RY_EV
ROOT=Path(__file__).resolve().parent
def main():
    names={'clean-k12-relax':'relax','ads-k12-relax':'relax','clean-k16':'scf','ads-k16':'scf','h2-10A':'relax'}
    runs={n:read_run(n,stem) for n,stem in names.items()}
    for clean,ads in [('clean-k12-relax','ads-k12-relax'),('clean-k16','ads-k16')]:
        assert np.allclose(runs[clean][1]['cell_A'],runs[ads][1]['cell_A'],atol=1e-10,rtol=0)
    forces=[]
    for child,parent in [('clean-k16','clean-k12-relax'),('ads-k16','ads-k12-relax')]:
        cg=runs[child][1];pg=runs[parent][1]
        assert cg['symbols']==pg['symbols']
        assert np.allclose(cg['cell_A'],pg['cell_A'],atol=1e-10,rtol=0)
        assert np.allclose(cg['positions_A'],pg['positions_A'],atol=1e-10,rtol=0)
        delta=float(np.abs(np.array(cg['forces_Ry_Bohr'])-np.array(pg['forces_Ry_Bohr'])).max())
        force16=runs[child][0]['max_force_component_Ry_Bohr']
        forces.append(dict(case=child,parent=parent,max_force_k12_Ry_Bohr=runs[parent][0]['max_force_component_Ry_Bohr'],max_force_k16_Ry_Bohr=force16,max_force_change_Ry_Bohr=delta,k16_within_2e4=force16<=2e-4,change_within_2e4=delta<=2e-4))
    gas=runs['h2-10A'][0]['total_energy_Ry'];energies=[]
    for label,clean,ads in [('k12-relaxed','clean-k12-relax','ads-k12-relax'),('k16-fixed','clean-k16','ads-k16')]:
        rc=runs[clean][0];ra=runs[ads][0]
        assert (rc['nAl'],rc['nH'],ra['nAl'],ra['nH'])==(3,0,3,2)
        e=(ra['total_energy_Ry']-rc['total_energy_Ry']-gas)*RY_EV/2
        energies.append(dict(protocol=label,clean_case=clean,adsorbed_case=ads,gas_case='h2-10A',clean_energy_Ry=rc['total_energy_Ry'],adsorbed_energy_Ry=ra['total_energy_Ry'],h2_energy_Ry=gas,adsorption_eV_H=e))
    delta=(energies[1]['adsorption_eV_H']-energies[0]['adsorption_eV_H'])*1000
    save_csv('refined-energy-table.csv',[r[0] for r in runs.values()])
    save_csv('refined-adsorption-energy.csv',energies);save_csv('refined-force-check.csv',forces)
    (ROOT/'refined-structures.json').write_text(json.dumps({k:v[1] for k,v in runs.items()},indent=2)+'\n')
    result={'scientific_acceptance':'not_assessed','scope':'Two meshes on the k12-relaxed, nonmagnetic three-layer one-ML atop model; does not establish a complete converged series or all physical/model dimensions','energy_change_meV_H':delta,'energy_comparison_within_10meV_H':abs(delta)<=10,'force_checks':forces,'both_energy_and_force_comparisons_pass':abs(delta)<=10 and all(f['k16_within_2e4'] and f['change_within_2e4'] for f in forces),'energies':energies,'runs':[v[0] for v in runs.values()]}
    (ROOT/'evidence/refined-analysis-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in energies:print(f"{r['protocol']:<13} Eads = {r['adsorption_eV_H']:.8f} eV/H")
    print(f'k12 -> k16 fixed-geometry energy change: {delta:+.6f} meV/H')
    for f in forces:print(f"{f['case']:<10} max|F|={f['max_force_k16_Ry_Bohr']:.8f} Ry/Bohr; max force change={f['max_force_change_Ry_Bohr']:.8f} Ry/Bohr")
    print('Named energy comparison:',result['energy_comparison_within_10meV_H'])
    print('Named energy and force comparisons:',result['both_energy_and_force_comparisons_pass'])
if __name__=='__main__':main()
