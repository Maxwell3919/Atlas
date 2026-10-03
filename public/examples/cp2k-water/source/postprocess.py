"""Read CP2K 2026.2 ENERGY_FORCE output and compare density grids and one finite difference."""
from pathlib import Path
import hashlib,json,math,re,sys
HA_EV=27.211386245988;BOHR_A=.529177210903
def case(p):
    t=(p/'cp2k.out').read_text()
    assert 'CP2K version 2026.2' in t and 'PROGRAM ENDED AT' in t
    assert re.search(r'SCF run converged in\s+\d+\s+steps',t) and 'SCF run NOT converged' not in t
    energies=re.findall(r'ENERGY\|\s+Total FORCE_EVAL.*?energy\s*\[hartree\]\s*:?\s*([-+\d.Ee]+)',t);assert energies
    en=float(energies[-1]);assert math.isfinite(en)
    # CP2K2026.2 force_env_utils.F uses FORCES|, atom index and xyz/norm,
    # rather than the older ATOMIC FORCES/Kind/Element table.
    header='FORCES| Atomic forces [hartree/bohr]';assert header in t
    b=t.rsplit(header,1)[1]
    rows=re.findall(r'^\s*FORCES\|\s*(\d+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s*$',b,re.M)[:3]
    assert [int(x[0]) for x in rows]==[1,2,3]
    f=[[float(v) for v in x[1:4]] for x in rows];assert all(math.isfinite(v) for row in f for v in row)
    rec={'status':'NATIVE_ENERGY_FORCE_PARSER_PASS','energy_Ha':en,'forces_Ha_Bohr':f,'forces_eV_A':[[x*HA_EV/BOHR_A for x in row] for row in f],'sum_force_Ha_Bohr':[sum(row[j] for row in f) for j in range(3)],'nonzero_force_above_print_halfunit':max(abs(x) for row in f for x in row)>5e-13,'scientific_acceptance':False,'limits':'Parser/numericalreceipt only; no convergence acceptance or cross-pseudopotential absoluteenergy comparison'}
    (p/'postprocessing.json').write_text(json.dumps(rec,indent=2)+'\n');return rec
def compare(p):
    r={x:json.loads((p/x/'postprocessing.json').read_text()) for x in ['baseline','grid_control','H1_y_plus','H1_y_minus']}
    fd=-(r['H1_y_plus']['energy_Ha']-r['H1_y_minus']['energy_Ha'])/.01*BOHR_A
    f=r['baseline']['forces_Ha_Bohr'][1][1]
    d={'status':'BASELINE_MINIMAL_CONTROL_DIAGNOSTIC_COMPLETE','cases':r,'H1_y_FD_Ha_Bohr':fd,'H1_y_analytic_Ha_Bohr':f,'FD_minus_analytic_Ha_Bohr':fd-f,'grid_delta_energy_Ha':r['grid_control']['energy_Ha']-r['baseline']['energy_Ha'],'grid_force_component_max_delta_Ha_Bohr':max(abs(x-y) for a,b in zip(r['grid_control']['forces_Ha_Bohr'],r['baseline']['forces_Ha_Bohr']) for x,y in zip(a,b)),'scientific_acceptance':False,'limits':['SamePBE/basis/GTH/cell energy differences only.','OneFDstep tests energy-force consistency, noth->0 convergence.','Two density grids do not converge Gaussianbasis orperiodiccell.','SCFcriterion is notrigorous force/energy error bar.','NoPhonopy calculation authorized bythisreceipt.']}
    (p/'energy_force_comparison.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
if __name__=='__main__':
    mode,path=sys.argv[1:];{'case':case,'compare':compare}[mode](Path(path))
