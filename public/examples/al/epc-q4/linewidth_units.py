from pathlib import Path
import csv,json,math
r=Path(__file__).resolve().parent
h=6.62607015e-34
hartree=4.3597447222071e-18
ry_to_THz=(hartree/2)/h/1e12
rows=list(csv.DictReader((r/'linewidth.csv').open()))
results=[]
for row in rows:
    f=float(row['frequency_THz']);g=float(row['gamma_GHz']);dos=float(row['DOS_EF_states_spin_Ry_cell']);printed=float(row['lambda_mode'])
    w_Ry=f/ry_to_THz;g_Ry=g/(1000*ry_to_THz)
    lam=g_Ry/(math.pi*dos*w_Ry*w_Ry)
    tolerance=.005*ry_to_THz/(1000*math.pi*dos*f*f)+.00005+1e-6
    below_cutoff=float(row['frequency_cm1'])<=20.0
    if below_cutoff: assert printed==0.0
    else: assert abs(lam-printed)<=tolerance
    results.append(dict(q_index=int(row['q_index']),sigma_Ry=float(row['sigma_Ry']),mode=int(row['mode']),frequency_THz=f,gamma_GHz=g,DOS_EF_states_spin_Ry_cell=dos,frequency_Ry=w_Ry,gamma_Ry=g_Ry,lambda_from_printed_gamma=lam,lambda_printed=printed,rounding_tolerance=tolerance,below_20_cm1_cutoff=below_cutoff))
chosen=next(x for x in results if x['q_index']==2 and x['mode']==3 and abs(x['sigma_Ry']-.02)<1e-9)
receipt={'source':'QE7.5 PHonon/PH/elphon.f90 elphsum: lamb=gam/pi/w2/dosfit; then gam*=RY_TO_GHZ. Modules/constants.f90: RY_TO_GHZ=1000*RY_TO_THZ; RY_TO_THZ=Ry/h/1e12.','ry_to_THz':ry_to_THz,'number_of_records_checked':len(results),'formula_records_above_cutoff':sum(not x['below_20_cm1_cutoff'] for x in results),'low_frequency_lambda_cutoff_cm1':20.0,'cutoff_records':sum(x['below_20_cm1_cutoff'] for x in results),'gamma_printing_step_GHz':.01,'lambda_printing_step':.0001,'chosen_example':chosen,'convention':'Use printed ordinary-frequency THz/GHz through native Ry conversion. Do not insert an extra 2pi or double the per-spin DOS.'}
(r/'linewidth-unit-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'QE7.5: 1 Ry / h = {ry_to_THz:.9f} THz')
print('q2, mode3, electronic width 0.020 Ry')
for k,v in chosen.items():print(k,'=',v)
print('210 above-cutoff rows agree within printed rounding; 30 Gamma rows have lambda set to zero by the native 20 cm^-1 cutoff.')
