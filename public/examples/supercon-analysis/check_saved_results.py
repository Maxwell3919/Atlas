#!/usr/bin/env python3
"""Read-only checks of the existing Atlas Al archives. No solver is started.

Usage: python3 check_saved_results.py --public SITE/public --out OUTPUT
Requires Python standard library and the archive's rebuild_tc.py.
Output contains native/rebuilt Tc, printed-spectrum moments, linewidth-unit
checks and linearized-ME brackets parsed directly from native epw.out files.
"""
from pathlib import Path
import argparse, csv, importlib.util, json, math, re, sys
sys.dont_write_bytecode = True

def trap(x, y):
    return sum((b-a)*(u+v)/2 for a,b,u,v in zip(x,x[1:],y,y[1:]))

def spectrum(path):
    lines=path.read_text().splitlines()
    widths=list(map(float,lines[0].split()[2:]))
    data=[list(map(float,s.split())) for s in lines[1:] if s.strip()]
    assert len(data)==2000 and all(len(r)==11 for r in data)
    x=[r[0] for r in data]
    assert x[0]==0 and x[-1]==14 and all(b>a for a,b in zip(x,x[1:]))
    result=[]
    for j, sigma in enumerate(widths):
        y=[r[j+1] for r in data]
        assert all(math.isfinite(v) and v>=0 for v in y) and y[0]==0
        integrand=[0]+[2*v/f for f,v in zip(x[1:],y[1:])]
        lam=trap(x,integrand)
        log_integrand=[0]+[v*math.log(f) for f,v in zip(x[1:],integrand[1:])]
        wlog=math.exp(trap(x,log_integrand)/lam)*47.9924
        w2=math.sqrt(trap(x,[2*v*f for v,f in zip(y,x)])/lam)*47.9924
        result.append(dict(sigma_Ry=sigma,lambda_spectrum_printed_trapezoid=lam,
                           omega_log_printed_K=wlog,omega2_printed_K=w2))
    return result

def linear(path):
    text=path.read_text()
    assert 'Error in routine' not in text
    assert 'Finish: Solving (isotropic) linearized Eliashberg equation' in text
    pat=r'^\s*(\d+\.\d+)\s+(-?\d+\.\d{7})\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s*$'
    rows=[dict(T_K=float(t),eta=float(e),nsiw=int(n),actual_wscut_eV=float(w),iterations=int(it))
          for t,e,n,w,it in re.findall(pat,text,re.M)]
    assert rows
    brackets=[]
    for a,b in zip(rows,rows[1:]):
        if (a['eta']-1)*(b['eta']-1)<0:
            brackets.append(dict(T_low_K=a['T_K'],T_high_K=b['T_K'],eta_low=a['eta'],eta_high=b['eta']))
    return dict(rows=rows,brackets=brackets)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); public=args.public.resolve();out=args.out.resolve()
    assert not out.is_relative_to(public), 'Output must be outside read-only source tree'
    out.mkdir(parents=True,exist_ok=True)
    root=public/'examples/supercon-al-tc'
    spec=importlib.util.spec_from_file_location('rebuild',root/'rebuild_tc.py')
    rebuild=importlib.util.module_from_spec(spec);spec.loader.exec_module(rebuild)
    branches={}
    for name in ['k32','k48']:
        rows,meta=rebuild.reconstruct(root/name)
        printed=spectrum(root/name/'alpha2F.dat')
        assert len(rows)==len(printed)==10 and meta['nq']==8 and meta['q_weight_sum']==64
        for row,moment in zip(rows,printed):
            assert row['sigma_Ry']==moment['sigma_Ry']
            assert abs(row['lambda_spectrum']-moment['lambda_spectrum_printed_trapezoid'])<5e-6
        branches[name]=dict(native_reconstruction=rows,printed_spectrum=printed,
                            q_points=meta['nq'],q_weight_sum=meta['q_weight_sum'])
    paired=[]
    for a,b in zip(branches['k32']['native_reconstruction'],branches['k48']['native_reconstruction']):
        assert a['sigma_Ry']==b['sigma_Ry'] and a['mu_star']==b['mu_star']==0.1
        paired.append(dict(sigma_Ry=a['sigma_Ry'],Tc32_K=a['Tc_K'],Tc48_K=b['Tc_K'],delta_Tc_K=a['Tc_K']-b['Tc_K']))
    # Every endpoint difference is strictly positive, so each affine interval is positive.
    assert all(r['delta_Tc_K']>0 for r in paired)
    rows=list(csv.DictReader((public/'examples/al/epc-q4/linewidth.csv').open()))
    constant=3289.841960251
    above=below=0
    for row in rows:
        f=float(row['frequency_THz']);g=float(row['gamma_GHz']);dos=float(row['DOS_EF_states_spin_Ry_cell']);lam=float(row['lambda_mode'])
        if float(row['frequency_cm1'])<=20:
            assert lam==0;below+=1
        else:
            rebuilt=g*constant/(1000*math.pi*dos*f*f)
            tolerance=.005*constant/(1000*math.pi*dos*f*f)+.00005+1e-6
            assert abs(rebuilt-lam)<=tolerance;above+=1
    assert (above,below)==(210,30)
    epw=public/'examples/al-epw-tc'
    me={name:linear(epw/name/'epw.out') for name in ['linear-w010-refine','linear-w020-refine','linear-w040-refine']}
    native=public/'examples/al-epw-wannier-tc/linear-refine/epw.out'
    if native.exists(): me['native-spectrum']=linear(native)
    payload=dict(branches=branches,paired_Tc=paired,isolated_crossings=0,overlap_intervals=0,
                 linewidth_above_threshold_rows=above,linewidth_threshold_rows=below,ME=me,
                 scope='Saved finite-grid Al inputs/outputs; no material convergence acceptance; no solver run')
    (out/'saved-results-check.json').write_text(json.dumps(payload,indent=2)+'\n')
    with (out/'paired-tc-rechecked.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
    print('20 Tc rows reconstructed at native printing precision; 10 pairs; 0 crossings; 0 overlaps')
    print('Minimum delta Tc = %.9f K' % min(r['delta_Tc_K'] for r in paired))
    print('210 linewidth rows match units; 30 native threshold rows kept separate')
    for name,result in me.items():print(name,result['brackets'])

if __name__=='__main__':main()
