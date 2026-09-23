#!/usr/bin/env python3
"""Read the completed Al lesson; check lineage, units and Tc formulas.
Standard library only. No QE execution and no edits to source calculations.
Source formulas: QE 7.5 lambda.f90; Allen & Dynes, PRB 12, 905 (1975).
"""
from pathlib import Path
import argparse, csv, hashlib, json, math, re, statistics

QE_RY_THZ=3289.828
QE_THZ_K=47.9924
SI_THZ_K=6.62607015e-34*1e12/1.380649e-23
SI_RY_K=(4.3597447222071e-18/2)/1.380649e-23
SI_RY_THZ=(4.3597447222071e-18/2)/6.62607015e-34/1e12

def table(path):
    return [[float(x) for x in s.split()] for s in path.read_text().splitlines()
            if s.strip() and re.match(r'^\s*[-+]?\d',s)]

def trap(x,y):
    return sum((b-a)*(v+u)/2 for a,b,u,v in zip(x,x[1:],y,y[1:]))

def cumulative(x,y):
    out=[0.]
    for a,b,u,v in zip(x,x[1:],y,y[1:]):
        out.append(out[-1]+(b-a)*(u+v)/2)
    return out

def moments(x,y,to_K):
    if any(v<0 for v in y):
        raise ValueError("A negative spectrum is not silently clipped for Tc moments.")
    pairs=[(a,b) for a,b in zip(x,y) if a>0]
    a,b=map(list,zip(*pairs))
    lam=2*trap(a,[v/u for u,v in pairs])
    if lam<=0:raise ValueError("Non-positive spectral lambda")
    logw=math.exp(2*trap(a,[v*math.log(u)/u for u,v in pairs])/lam)
    w2=math.sqrt(2*trap(a,[v*u for u,v in pairs])/lam)
    return lam,logw*to_K,w2*to_K

def formula(lam,wlog_K,w2_K,mu):
    den=lam-mu*(1+.62*lam)
    if lam<=0 or wlog_K<=0 or den<=0:
        raise ValueError("Outside this empirical formula's admissible denominator.")
    simple=wlog_K/1.2*math.exp(-1.04*(1+lam)/den)
    ratio=w2_K/wlog_K
    L1=2.46*(1+3.8*mu);L2=1.82*(1+6.3*mu)*ratio
    f1=(1+(lam/L1)**1.5)**(1/3)
    f2=1+(ratio-1)*lam*lam/(lam*lam+L2*L2)
    return dict(denominator=den,Tc_simple_K=simple,f1=f1,f2=f2,Tc_full_AD_K=f1*f2*simple)

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('data'))
    a=ap.parse_args();r=a.source.resolve();o=a.output.resolve();o.mkdir(parents=True,exist_ok=True)
    source_names=['lambda.in','lambda.dat','lambda.out','alpha2F.dat','al.elph.out','q2r.out','matdyn-dos.out',
                  'al.dense.in','al.scf.in','al.elph.in','q2r.in','matdyn-dos.in','q-weight-source.json']
    inp=[x.strip() for x in (r/'lambda.in').read_text().splitlines() if x.strip()]
    emax,width,kind=map(float,inp[0].split());nq=int(inp[1])
    assert int(kind)==0 and width>0
    qrows=[list(map(float,x.split())) for x in inp[2:2+nq]]
    files=inp[2+nq:2+2*nq];mu=float(inp[2+2*nq])
    wsum=sum(q[3] for q in qrows);assert wsum==64 and nq==8
    ph=(r/'al.elph.out').read_text()
    qblocks=re.split(r'Calculation of q\s*=',ph)[1:];assert len(qblocks)==nq
    modes=[];negative_w2=[];native_ph_frequencies=[]
    for iq,(q,name,block) in enumerate(zip(qrows,files,qblocks),1):
        p=r/name;source_names.append(name);text=p.read_text();lines=text.splitlines()
        h=lines[0].split();ns,nm=map(int,h[3:]);assert ns==10 and nm==3
        assert all(abs(float(h[j])-q[j])<1e-6 for j in range(3))
        native_ph_frequencies.extend(float(v) for v in re.findall(r'freq\s*\(\s*\d+\)\s*=\s*([-\d.]+)\s*\[THz\]',block))
        stars=list(map(int,re.findall(r'Number of q in the star\s*=\s*(\d+)',block)))
        assert stars and set(stars)=={int(q[3])}
        w2=list(map(float,lines[1].split()));assert len(w2)==nm
        for j,v in enumerate(w2):
            if v<=0:negative_w2.append([iq,j+1,v])
        if negative_w2:raise ValueError("Nonpositive direct squared frequencies: "+str(negative_w2))
        chunks=re.split(r'Gaussian Broadening:',text)[1:];assert len(chunks)==ns
        for chunk in chunks:
            sigma=float(re.match(r'\s*([.\d]+)',chunk)[1])
            vals=re.findall(r'lambda\(\s*(\d+)\)=\s*([-\d.]+)\s+gamma=\s*([-\d.]+)\s+GHz',chunk)
            assert len(vals)==nm
            for mode,lam,gamma in vals:
                j=int(mode)-1;freq=math.sqrt(w2[j])*QE_RY_THZ
                row=dict(q_index=iq,mode=j+1,sigma_Ry=sigma,star_weight=int(q[3]),
                         weight=q[3]/wsum,frequency_THz=freq,lambda_mode=float(lam),gamma_GHz=float(gamma))
                modes.append(row)
    direct=table(r/'lambda.dat');af=table(r/'alpha2F.dat')
    assert len(direct)==10 and len(af)==2000 and len(af[0])==11
    assert all(math.isfinite(x) for row in af for x in row) and min(min(row[1:]) for row in af)>=0
    printed_x=[row[0] for row in af]
    exact_x=[i*emax/1999 for i in range(2000)]
    native_tc=table_from_output=(r/'lambda.out').read_text().split('lambda        omega_log          T_c')[-1]
    native_tc=[[float(x) for x in s.split()] for s in native_tc.strip().splitlines()]
    assert len(native_tc)==10
    scans=[];spectrum=[];matdyn=[];pairs=[]
    for j,(sigma,lam_print,li_print,wl_print,dosef) in enumerate(direct):
        selected=[m for m in modes if abs(m['sigma_Ry']-sigma)<1e-9]
        qsum=sum(m['weight']*m['lambda_mode'] for m in selected)
        recon=[]
        for nu in exact_x:
            recon.append(sum(m['weight']*m['lambda_mode']*m['frequency_THz']/2
                             *math.exp(-((nu-m['frequency_THz'])/width)**2)/(math.sqrt(math.pi)*width)
                             for m in selected))
        step=emax/1999
        li_exact=2*step*sum(v/x for x,v in zip(exact_x[1:],recon[1:]))
        log_exact=math.exp(2*step*sum(v*math.log(x)/x for x,v in zip(exact_x[1:],recon[1:]))/li_exact)*QE_THZ_K
        assert abs(qsum-lam_print)<5.1e-7
        assert abs(li_exact-li_print)<5.1e-7 and abs(log_exact-wl_print)<.00051
        y=[row[j+1] for row in af];lam_s,log_s,w2_s=moments(printed_x,y,QE_THZ_K)
        assert abs(lam_s-li_print)<2e-5 and abs(log_s-wl_print)<.02
        f=formula(lam_s,log_s,w2_s,mu)
        native_formula=formula(qsum,log_exact,w2_s,mu)['Tc_simple_K']
        assert abs(native_formula-native_tc[j][2])<.00051
        row=dict(sigma_Ry=sigma,lambda_qsum=qsum,lambda_native_printed=lam_print,
                 lambda_spectrum_internal=li_exact,lambda_spectrum_printed_trapezoid=lam_s,
                 omega_log_native_replay_K=log_exact,omega_log_printed_K=wl_print,
                 omega_log_spectrum_K=log_s,omega2_spectrum_K=w2_s,
                 mu_star=mu,Tc_native_printed_K=native_tc[j][2],Tc_QE_replay_K=native_formula,
                 Tc_spectrum_simple_K=f['Tc_simple_K'],f1=f['f1'],f2=f['f2'],Tc_spectrum_full_AD_K=f['Tc_full_AD_K'])
        scans.append(row)
        cy=cumulative(printed_x,[0 if x==0 else 2*v/x for x,v in zip(printed_x,y)])
        if j in [0,3]:
            for x,v,z in zip(printed_x,y,cy):spectrum.append(dict(route='lambda.x',sigma_Ry=sigma,frequency_THz=x,a2F=v,cumulative_lambda=z))
        apath=r/f'a2F.dos{j+1}';source_names.append(apath.name);atxt=apath.read_text();arr=table(apath)
        assert len(arr)==400 and all(len(v)==5 for v in arr)
        ry=[v[0] for v in arr];ay=[v[1] for v in arr]
        footer=float(re.search(r'lambda\s*=\s*([-\d.Ee+]+)',atxt)[1])
        neg=sum(v<0 for v in ay)
        md=dict(sigma_Ry=sigma,negative_rows=neg,min_a2F=min(ay),lambda_footer=footer,
                lambda_trapezoid=2*trap(ry,[v/x for x,v in zip(ry,ay)]),frequency_unit='Ry',
                moment_status='rejected_negative_spectrum' if neg else 'nonnegative_for_arithmetic')
        if neg==0:
            ml,mw,m2=moments(ry,ay,SI_RY_K);md.update(lambda_spectrum=ml,omega_log_K=mw,omega2_K=m2)
        matdyn.append(md)
        if j in [0,3]:
            cx=[x*SI_RY_THZ for x in ry];cy=cumulative(ry,[2*v/x for x,v in zip(ry,ay)])
            for x,v,z in zip(cx,ay,cy):spectrum.append(dict(route='matdyn.x',sigma_Ry=sigma,frequency_THz=x,a2F=v,cumulative_lambda=z))
    chosen=scans[3];mu_rows=[]
    for i in range(8,17):
        m=i/100;f=formula(chosen['lambda_spectrum_printed_trapezoid'],chosen['omega_log_spectrum_K'],chosen['omega2_spectrum_K'],m)
        simple=formula(chosen['lambda_native_printed'],chosen['omega_log_printed_K'],chosen['omega2_spectrum_K'],m)['Tc_simple_K']
        mu_rows.append(dict(mu_star=m,Tc_QE_rounded_input_K=simple,Tc_spectrum_simple_K=f['Tc_simple_K'],Tc_spectrum_full_AD_K=f['Tc_full_AD_K']))
    write_csv(o/'tc-formula-scan.csv',scans);write_csv(o/'mu-star-scan.csv',mu_rows)
    write_csv(o/'spectra-and-integrals.csv',spectrum);write_csv(o/'mode-check.csv',modes)
    # Rejecting negative spectra is recorded; raw values are always preserved in plots/data.
    (o/'matdyn-spectrum-checks.json').write_text(json.dumps(matdyn,indent=2)+'\n')
    density_hash=hashlib.sha256((r/'tmp/al.a2Fsave').read_bytes()).hexdigest()
    assert density_hash==hashlib.sha256((r/'al.a2Fsave.k32').read_bytes()).hexdigest()
    minfreq=min(m['frequency_THz'] for m in modes);maxfreq=max(m['frequency_THz'] for m in modes)
    for name in ['al.dense','al.scf','al.elph','q2r','matdyn-dos']:
        out=(r/f'{name}.out').read_text();assert 'JOB DONE.' in out and 'convergence NOT achieved' not in out
        assert (r/f'{name}.err').stat().st_size==0
    assert (r/'lambda.err').stat().st_size==0
    report=dict(case='completed fcc Al lesson, QE7.5',q_irreducible=nq,q_star_sum=wsum,nmodes=3,
                electronic_widths_Ry=[row[0] for row in direct],frequency_min_direct_THz=minfreq,
                frequency_max_direct_THz=max(native_ph_frequencies),frequency_max_reconstructed_from_printed_w2_THz=maxfreq,frequency_upper_limit_THz=emax,gaussian_parameter_THz=width,
                direct_negative_squared_frequencies=negative_w2,dense_a2Fsave_sha256=density_hash,
                low_frequency_mode_lambda_cutoff_cm1=20,
                cutoff_source='QE7.5 PHonon/PH/elphon.f90 epsw and elphsum; raw gamma still exists',
                constants=dict(lambda_x_Ry_to_THz=QE_RY_THZ,lambda_x_THz_to_K=QE_THZ_K,
                               SI_THz_to_K=SI_THZ_K,SI_Ry_to_K=SI_RY_K,SI_Ry_to_THz=SI_RY_THZ),
                source_sha256={name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in source_names},
                formula_versions=['QE omega_log modified McMillan/Allen-Dynes with f1=f2=1',
                                  'spectral-moment Allen-Dynes with both f1 and f2'],
                numerical_crosscheck='qsum, source-algorithm replay, printed-spectrum quadrature and native Tc agree within printing/integration tolerances',
                scientific_status='teaching formula results only; k/q/cutoff convergence not established; mu_star assumed; no material Tc accepted',
                selected_sigma_Ry_0p020=chosen)
    (o/'tc-chain-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'q points={nq}; weights={wsum:g}; modes=3; widths=10; mode records={len(modes)}')
    print(f'printed-omega^2 reconstruction={minfreq:.6f}..{maxfreq:.6f} THz; negative omega^2=0')
    print(f'ph.x printed maximum={max(native_ph_frequencies):.6f} THz; frequency difference comes from printed w2 precision')
    print(f'lambda.x grid=2000 points, 0..{emax:g} THz; Gaussian parameter={width:g} THz')
    print('sigma_Ry lambda_qsum lambda_spectrum omega_log_K omega2_K Tc_QE_K Tc_full_AD_K')
    for s in scans:
        print(f"{s['sigma_Ry']:.3f} {s['lambda_qsum']:.8f} {s['lambda_spectrum_printed_trapezoid']:.8f} {s['omega_log_spectrum_K']:.5f} {s['omega2_spectrum_K']:.5f} {s['Tc_QE_replay_K']:.6f} {s['Tc_spectrum_full_AD_K']:.6f}")
    print('sigma=0.020: f1={:.8f}; f2={:.8f}; spectral simple Tc={:.6f} K'.format(chosen['f1'],chosen['f2'],chosen['Tc_spectrum_simple_K']))
    print('matdyn negative rows by width: '+', '.join(str(m['negative_rows']) for m in matdyn))
    print('Cross-check completed. Material Tc convergence is not established.')

if __name__=='__main__':main()
