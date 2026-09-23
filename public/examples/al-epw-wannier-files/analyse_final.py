#!/usr/bin/env python3
from pathlib import Path
import csv,json,math,re,hashlib
B=Path(__file__).resolve().parent
fine=B/'runs/interpolate-003'
def writecsv(path,rows):
 with path.open('w')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def numerical_lines(path,n):
 rows=[]
 for line in path.read_text().splitlines():
  try:a=[float(x.replace('D','E'))for x in line.split()]
  except ValueError:continue
  if len(a)==n:rows.append(a)
 return rows
raw=numerical_lines(fine/'al.a2f',3)
assert len(raw)>100 and all(x[0]>0 and x[1]>=0 for x in raw)
assert all(raw[i+1][0]>raw[i][0]for i in range(len(raw)-1))
rows=[{'omega_meV':x[0],'alpha2F':x[1],'native_cumulative_lambda':x[2]}for x in raw]
writecsv(B/'derived/epw-a2f-k12-q4-fine24-q12.csv',rows)
def trapezoid(ys):return sum((ys[i+1]+ys[i])*(raw[i+1][0]-raw[i][0])/2 for i in range(len(raw)-1))
lam=trapezoid([2*x[1]/x[0]for x in raw])
wlog=math.exp(trapezoid([2*x[1]/x[0]*math.log(x[0])for x in raw])/lam)
summary={'source':'runs/interpolate-003/al.a2f','source_sha256':hashlib.sha256((fine/'al.a2f').read_bytes()).hexdigest(),'positive_rows':len(raw),'omega_min_meV':raw[0][0],'omega_max_meV':raw[-1][0],'native_summed_elph_coupling':float(re.search(r'Summed el-ph coupling\s+([0-9.Ee+\-]+)', (fine/'al.a2f').read_text()).group(1)),'native_cumulative_lambda_last':raw[-1][2],'lambda_trapezoid_from_rounded_export':lam,'omega_log_meV_from_rounded_export':wlog,'native_tail_metadata':(fine/'al.a2f').read_text().splitlines()[-7:],'coarse_k':[12]*3,'coarse_q':[4]*3,'fine_k':[24]*3,'fine_q':[12]*3,'electronic_smearing_eV':.1,'phonon_smearing_meV':.5,'Fermi_window_eV':1.0,'eps_acoustic_cm_1':.1,'ASR':'parent q2r zasr=simple; EPW lifc=true rereads ifc.q2r and imposes asr_typ=crystal','scientific_acceptance':'not_assessed','convergence_status':'not assessed; one completed fine-grid case, larger fine case stopped for runtime'}
(B/'derived/epw-spectrum-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
decays={}
for fn in ['decay.H','decay.epmate','decay.epmatp']:
 vals=numerical_lines(B/'runs/coarse-002'/fn,2)
 peak=max(v[1]for v in vals);rmax=max(v[0]for v in vals);tail=[v for v in vals if v[0]>=.8*rmax]
 dr=[{'distance_angstrom':v[0],'max_abs_matrix_element_Ry':v[1],'amplitude_over_global_max':v[1]/peak}for v in vals]
 writecsv(B/'derived'/f'{fn}.csv',dr)
 decays[fn]={'rows':len(vals),'max_distance_angstrom':rmax,'global_max_abs_Ry':peak,'outer20percent_distance_tail_max_abs_Ry':max(v[1]for v in tail),'outer20percent_distance_tail_to_global_max':max(v[1]for v in tail)/peak,'scope':'diagnostic ratio, not an acceptance threshold'}
(B/'derived/decay-summary.json').write_text(json.dumps(decays,indent=2)+'\n')
p=B/'runs/phononcheck-002/phband.freq'
if p.exists()and(B/'runs/phononcheck-002/exit.status').exists():
 lines=p.read_text().splitlines();freq=[]
 assert 'nks=  1728' in lines[0]
 for j in range(1728):
  q=[float(x)for x in lines[1+2*j].split()];ws=[float(x)for x in lines[2+2*j].split()];assert len(ws)==3
  for m,x in enumerate(ws):freq.append({'q_index':j+1,'qx_cart_2pi_alat':q[0],'qy_cart_2pi_alat':q[1],'qz_cart_2pi_alat':q[2],'mode':m+1,'frequency_meV':x})
 writecsv(B/'derived/phonons-all-q12-native-EPW.csv',freq)
 eps=.1/8.06554429
 ph={'source':'runs/phononcheck-002/phband.freq','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'q_count':1728,'mode_count':5184,'native_output_precision_meV':.0001,'eps_acoustic_cm_1':.1,'eps_acoustic_meV':eps,'minimum_printed_frequency_meV':min(x['frequency_meV']for x in freq),'maximum_printed_frequency_meV':max(x['frequency_meV']for x in freq),'printed_negative_frequencies':sum(x['frequency_meV']<0 for x in freq),'frequencies_at_or_below_eps':sum(x['frequency_meV']<=eps for x in freq),'gamma_printed_frequencies_meV':[x['frequency_meV']for x in freq[:3]],'nonGamma_min_printed_frequency_meV':min(x['frequency_meV']for x in freq[3:]),'exclusion_rule':'EPW6 source supercond_vertex.f90 calculates alpha2F only for wq>eps_acoustic. Negative and lower frequencies contribute nothing.','claim_limit':'No finite imaginary frequency on this sampled q12 grid at printed precision; not a proof of dynamical stability everywhere or phonon convergence.'}
 (B/'derived/phonon-threshold-audit.json').write_text(json.dumps(ph,indent=2)+'\n')
 print(json.dumps(ph,indent=2))
print(json.dumps(summary,indent=2));print(json.dumps(decays,indent=2))
