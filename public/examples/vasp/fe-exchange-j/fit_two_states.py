from __future__ import print_function
import json,math
from fit_exchange import read_case,file_sha,sampling_length

bonds=json.load(open('bonds-summary.json'))
names=['fm2','afm2','fm4','neel4'];rows=[read_case(n) for n in names]
if len(set(file_sha(n+'/POTCAR') for n in names))!=1:raise ValueError('Different PAW')
protocol=[dict((k,v) for k,v in r['active_incar'].items() if k not in ['SYSTEM','MAGMOM']) for r in rows]
if any(p!=protocol[0] for p in protocol):raise ValueError('Protocol mismatch')
for group in [['fm2','afm2'],['fm4','neel4']]:
 for file in ['POSCAR','KPOINTS']:
  if len(set(file_sha(n+'/'+file) for n in group))!=1:raise ValueError('Different '+file)
ks=sampling_length('fm2')
if any(max(abs(x-y) for x,y in zip(sampling_length(n),ks))>1e-9 for n in names):raise ValueError('Different reciprocal mesh density')
for r in rows:
 want=bonds['states'][r['state']]['spin_directions']
 if r['final_spin_signs']!=want and r['final_spin_signs']!=[-x for x in want]:raise ValueError('Final signs changed')
cf=bonds['states']['fm2']['correlation_sum'];ca=bonds['states']['afm2']['correlation_sum']
j=(rows[1]['E0_eV_cell']-rows[0]['E0_eV_cell'])/(cf-ca)
ere=(rows[0]['E0_eV_cell']+j*cf)/rows[0]['n_atoms']
for r in rows:
 corr=bonds['states'][r['state']]['correlation_sum'];pred=ere*r['n_atoms']-j*corr
 r['predicted_E0_eV_cell']=pred;r['correlation_sum']=corr;r['residual_meV_atom']=1000*(r['E0_eV_cell']-pred)/r['n_atoms']
# Read the rejected trial only for diagnosis; it is excluded from fitting and residual validation.
rejected=read_case('stripe4',enforce_moment=False)
rejected['requested_initial_signs']=bonds['states']['stripe4']['spin_directions']
rejected['accepted_as_target_state']=False
rejected['reason']='local moments fall to about 0.007 muB and requested site pattern is not retained'
report={'definition':bonds['definition'],'J_effective_meV_per_bond':j*1000,'Eref_eV_atom':ere,'fit_states':['fm2','afm2'],'folding_checks':['fm4','neel4'],'rows':rows,'rejected_trial':rejected,'independent_third_state_validation':'not passed; the intended third magnetic state was not obtained','scope':'two-state effective parameter; no unique material J or validated nearest-neighbor model claimed'}
json.dump(report,open('exchange-summary.json','w'),indent=2)
print('J_eff = %.8f meV per unique NN bond; Eref = %.10f eV/atom'%(j*1000,ere))
for r in rows:print('%-5s N=%d C=%+3d E0=% .8f predicted=% .8f eV/cell residual=%+.6f meV/atom; moments=%s'%(r['state'],r['n_atoms'],r['correlation_sum'],r['E0_eV_cell'],r['predicted_E0_eV_cell'],r['residual_meV_atom'],r['local_moment_muB']))
print('stripe4: EXCLUDED from fit/model residual; E0=%.8f eV/cell; local moments=%s'%(rejected['E0_eV_cell'],rejected['local_moment_muB']))
print('The intended third magnetic state was not obtained. The nearest-neighbor model has not passed independent validation.')
