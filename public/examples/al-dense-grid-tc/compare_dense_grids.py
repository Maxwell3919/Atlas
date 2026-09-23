#!/usr/bin/env python3
"""Pair every printed native lambda.x row; report every linear crossing."""
import argparse,csv,hashlib,json,math,re
from pathlib import Path

def read_branch(root):
    text=(root/'lambda.out').read_text()
    rows=re.findall(r'lambda\s*=\s*([\d.]+)\s*\(\s*([\d.]+)\s*\)\s*<log w>=\s*([\d.]+)\s*K\s*N\(Ef\)=\s*([\d.]+)\s*at\s*degauss=\s*([\d.]+)',text)
    table=text.split('lambda        omega_log          T_c')[-1]
    triplets=[list(map(float,l.split())) for l in table.splitlines() if len(l.split())==3]
    lin=(root/'lambda.in').read_text().splitlines()
    nq=int(lin[1]); weights=[float(l.split()[-1]) for l in lin[2:2+nq]];mu=float(lin[-1])
    assert len(rows)==len(triplets)==10 and nq==8 and sum(weights)==64
    assert len(list((root/'elph_dir').glob('elph.inp_lambda.*')))==nq
    parsed=[]
    for r,t in zip(rows,triplets):
        lam,spec,wlog,nef,sigma=map(float,r)
        assert abs(lam-t[0])<5.1e-6 and abs(wlog-t[1])<1e-8
        denom=lam-mu*(1+.62*lam)
        assert denom>0
        derived=wlog/1.2*math.exp(-1.04*(1+lam)/denom)
        assert abs(derived-t[2])<.00051
        parsed.append(dict(sigma_Ry=sigma,lambda_native=lam,lambda_spectrum_native=spec,omega_log_K=wlog,N_Ef_native=nef,mu_star=mu,Tc_native_K=t[2],Tc_from_printed_lambda_wlog_K=derived))
    return parsed,{'lambda_out_sha256':hashlib.sha256((root/'lambda.out').read_bytes()).hexdigest(),'lambda_in_sha256':hashlib.sha256((root/'lambda.in').read_bytes()).hexdigest(),'q_count':nq,'q_weight_sum':sum(weights),'mu_star':mu}

def all_intersections(rows,key):
    crosses=[]; endpoints=[]; overlaps=[]
    delta=[r[key+'_B']-r[key+'_A'] for r in rows]
    for i,d in enumerate(delta):
        if d==0: endpoints.append({'sigma_Ry':rows[i]['sigma_Ry'],'Tc_K':rows[i][key+'_A'],'position':'boundary' if i in (0,len(rows)-1) else 'sampled point'})
    for i,(d0,d1) in enumerate(zip(delta[:-1],delta[1:])):
        x0,x1=rows[i]['sigma_Ry'],rows[i+1]['sigma_Ry']
        if d0==0 and d1==0: overlaps.append([x0,x1])
        elif d0*d1<0:
            f=-d0/(d1-d0); tc=rows[i][key+'_A']+f*(rows[i+1][key+'_A']-rows[i][key+'_A'])
            crosses.append({'sigma_Ry':x0+f*(x1-x0),'Tc_K':tc,'bracket_sigma_Ry':[x0,x1],'delta_B_minus_A_at_bracket_K':[d0,d1],'fraction':f,'printed_rounding_sign_unresolved':min(abs(d0),abs(d1))<=.001})
    return {'linear_segment_crossings':crosses,'exact_printed_equalities':endpoints,'overlapping_printed_segments':overlaps,'difference_convention':'B - A','scientific_convergence_established':False}

p=argparse.ArgumentParser()
p.add_argument('--a',type=Path,required=True);p.add_argument('--b',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
a,ma=read_branch(args.a);b,mb=read_branch(args.b)
assert ma['mu_star']==mb['mu_star'] and ma['lambda_in_sha256']==mb['lambda_in_sha256']
assert ma['lambda_out_sha256']!=mb['lambda_out_sha256']
merged=[]
for ra,rb in zip(a,b):
    assert ra['sigma_Ry']==rb['sigma_Ry']
    row={'sigma_Ry':ra['sigma_Ry']}
    for suffix,r in [('A',ra),('B',rb)]:
        row.update({k+'_'+suffix:v for k,v in r.items() if k!='sigma_Ry'})
    row['delta_Tc_native_B_minus_A_K']=rb['Tc_native_K']-ra['Tc_native_K']
    merged.append(row)
with (args.out/'tc-sigma-paired.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(merged[0]));w.writeheader();w.writerows(merged)
result={'A':ma,'B':mb,'raw_printed':all_intersections(merged,'Tc_native_K'),'recomputed_from_printed_lambda_and_wlog':all_intersections(merged,'Tc_from_printed_lambda_wlog_K'),'note':'Native Tc has 0.001 K print resolution. Linear interpolation is only between the ten sampled widths; every crossing is reported, none selected as a material Tc.'}
(args.out/'intersections.json').write_text(json.dumps(result,indent=2)+'\n')
print('sigma_Ry lambda_A lambda_B omega_log_A_K omega_log_B_K Tc_A_K Tc_B_K delta_B-A_K')
for r in merged:
    print(f"{r['sigma_Ry']:.3f} {r['lambda_native_A']:.6f} {r['lambda_native_B']:.6f} {r['omega_log_K_A']:.3f} {r['omega_log_K_B']:.3f} {r['Tc_native_K_A']:.3f} {r['Tc_native_K_B']:.3f} {r['delta_Tc_native_B_minus_A_K']:+.3f}")
print(json.dumps(result['raw_printed'],indent=2))

