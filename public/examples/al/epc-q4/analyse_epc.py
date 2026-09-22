from pathlib import Path
import csv,json,re,hashlib
import numpy as np
r=Path(__file__).resolve().parent
qs=json.loads((r/'q-weight-source.json').read_text())['qpoints']
ph=(r/'al.elph.out').read_text()
blocks=re.split(r'Calculation of q\s*=',ph)[1:]
assert len(blocks)==len(qs)==8
rows=[]
for iq,(q,b) in enumerate(zip(qs,blocks),1):
    f=r/'elph_dir'/f'elph.inp_lambda.{iq}'
    lines=f.read_text().splitlines()
    h=lines[0].split(); ns,nm=map(int,h[3:]); assert ns==10 and nm==3
    assert np.allclose(list(map(float,h[:3])),q['q_cart_2pi_alat'],atol=1e-6,rtol=0)
    freq=re.findall(r'freq\s*\(\s*(\d+)\)\s*=\s*([-\d.]+)\s*\[THz\]\s*=\s*([-\d.]+)\s*\[cm-1\]',b)
    assert len(freq)==3
    w2=np.array(list(map(float,lines[1].split())))
    assert np.all(w2>0)
    assert np.allclose(np.sqrt(w2)*3289.828,[float(x[1]) for x in freq],atol=1e-4,rtol=0)
    chunks=re.split(r'Gaussian Broadening:',f.read_text())[1:]; assert len(chunks)==ns
    for ch in chunks:
        sigma=float(re.search(r'^\s*([.\d]+)\s+Ry',ch).group(1))
        dosef,ef=map(float,re.search(r'DOS\s*=\s*([.\d]+).*?Ef=\s*([.\d]+)',ch).groups())
        modes=re.findall(r'lambda\(\s*(\d+)\)=\s*([-\d.]+)\s+gamma=\s*([-\d.]+)\s+GHz',ch)
        assert len(modes)==nm
        for mode,lam,gamma in modes:
            j=int(mode)-1
            rows.append(dict(q_index=iq,qx=q['q_cart_2pi_alat'][0],qy=q['q_cart_2pi_alat'][1],qz=q['q_cart_2pi_alat'][2],star_weight=q['star_weight'],sigma_Ry=sigma,mode=int(mode),frequency_THz=float(freq[j][1]),frequency_cm1=float(freq[j][2]),lambda_mode=float(lam),gamma_GHz=float(gamma),DOS_EF_states_spin_Ry_cell=dosef,EF_eV=ef))
assert sum(x['star_weight'] for x in qs)==64 and len(rows)==240
with (r/'linewidth.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
dat=np.loadtxt(r/'lambda.dat'); af=np.loadtxt(r/'alpha2F.dat'); assert dat.shape==(10,5) and af.shape[1]==11
assert np.all(np.isfinite(dat)) and np.all(np.isfinite(af)) and np.min(af[:,1:])>=0
native_tc=np.array([list(map(float,x.split())) for x in (r/'lambda.out').read_text().split('lambda        omega_log          T_c')[-1].strip().splitlines()])
assert native_tc.shape==(10,3)
mp=[]
for line in (r/'lambda').read_text().splitlines():
    m=re.search(r'Broadening\s+([.\d]+)\s+lambda\s+([.\d]+).*?omega_ln \[K\]\s+([.\d]+)',line)
    if m:mp.append(list(map(float,m.groups())))
assert len(mp)==10
scan=[]
for j,(sigma,lam,li,wlog,dosef) in enumerate(dat):
    weighted=sum(v['star_weight']/64*v['lambda_mode'] for v in rows if abs(v['sigma_Ry']-sigma)<1e-10)
    integ=2*(np.trapezoid if hasattr(np, "trapezoid") else np.trapz)(af[1:,j+1]/af[1:,0],af[1:,0])
    assert abs(weighted-lam)<1e-6 and abs(integ-li)<2e-5
    denom=lam-.1*(1+.62*lam); assert denom>0
    tc=wlog/1.2*np.exp(-1.04*(1+lam)/denom)
    assert abs(tc-native_tc[j,2])<.001
    a2text=(r/f'a2F.dos{j+1}').read_text()
    a2=np.array([list(map(float,line.split())) for line in a2text.splitlines() if re.match(r'^\s*[-+]?\d',line)]); assert a2.shape==(400,5)
    footer_lambda=float(re.search(r'lambda\s*=\s*([-+.\dEe]+)',a2text).group(1))
    scan.append(dict(sigma_Ry=sigma,lambda_qsum=lam,lambda_qsum_from_mode_text=weighted,lambda_native_integral=li,lambda_printed_spectrum_integral=integ,omega_log_K=wlog,mu_star=.1,Tc_formula_K=tc,Tc_native_K=native_tc[j,2],DOS_EF_states_spin_Ry_cell=dosef,lambda_matdyn=mp[j][1],lambda_matdyn_spectrum_footer=footer_lambda,omega_log_matdyn_K=mp[j][2],a2F_matdyn_min=float(np.min(a2[:,1])),a2F_matdyn_negative_rows=int(np.sum(a2[:,1]<0))))
with (r/'tc-scan.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=scan[0].keys());w.writeheader();w.writerows(scan)
mu=np.arange(.08,.161,.01)
chosen=dat[3]; denom=chosen[1]-mu*(1+.62*chosen[1]); assert np.all(denom>0)
np.savetxt(r/'mu-sensitivity.csv',np.column_stack([mu,chosen[3]/1.2*np.exp(-1.04*(1+chosen[1])/denom)]),delimiter=',',header='mu_star,Tc_K',comments='')
summary=dict(low_frequency_lambda_cutoff_cm1=20.0,low_frequency_lambda_cutoff_source='QE7.5 PHonon/PH/elphon.f90:743-744 and 1087-1093, interpolated elphsum',low_frequency_cutoff_scope='lamb is set to zero below 20 cm^-1; gamma is still printed. Three Gamma residual modes fall below it; this does not establish a physical zero coupling.',material='fcc Al, one-atom primitive cell',nmodes=3,dense_k=[32]*3,coarse_k=[16]*3,q_mesh=[4]*3,q_irreducible=8,q_star_weight_sum=64,q_elph_files=len(list((r/'elph_dir').glob('elph.inp_lambda.*'))),q2r_elph_files=len(list((r/'elph_dir').glob('a2Fq2r.*'))),matdyn_elph_files=len(list((r/'elph_dir').glob('a2Fmatdyn.*'))),spectral_rows=af.shape[0],spectral_frequency_unit='THz',matdyn_spectral_frequency_unit='Ry',spectrum_max_THz=float(af[-1,0]),largest_computed_mode_THz=max(x['frequency_THz'] for x in rows),gaussian_spectrum_width_THz=.12,mode_records=len(rows),min_spectrum=float(np.min(af[:,1:])),spectrum_last_nonzero_THz=float(af[np.any(af[:,1:]!=0,axis=1),0][-1]),frequency_upper_margin_in_gaussian_widths=(14-max(x['frequency_THz'] for x in rows))/.12,a2Fsave_unchanged=hashlib.sha256((r/'tmp/al.a2Fsave').read_bytes()).hexdigest()==hashlib.sha256((r/'al.a2Fsave.k32').read_bytes()).hexdigest(),scan=scan,assessment='native complete; q/k/cutoff/smearing convergence not established; mu_star is assumed; no accepted material Tc')
assert summary['q2r_elph_files']==80 and summary['matdyn_elph_files']==10 and summary['a2Fsave_unchanged']
for n in ['al.dense','al.scf','al.elph','q2r','matdyn-dos']:
    assert 'JOB DONE.' in (r/(n+'.out')).read_text()
    assert (r/(n+'.err')).stat().st_size==0
    assert 'convergence NOT achieved' not in (r/(n+'.out')).read_text()
assert (r/'lambda.err').stat().st_size==0
(r/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('8 irreducible q points; star weights sum to 64; 3 modes; 10 electronic widths; 240 mode records')
print('80 q2r el-ph inputs; 10 real-space el-ph files; dense a2Fsave hash preserved')
print(f"Maximum computed mode = {summary['largest_computed_mode_THz']:.6f} THz; spectrum end = {af[-1,0]:.3f} THz")
print('sigma_Ry  lambda_qsum  lambda_integral  omega_log_K  Tc_mu0.10_K')
for s in scan: print(f"{s['sigma_Ry']:.3f}     {s['lambda_qsum']:.6f}      {s['lambda_printed_spectrum_integral']:.6f}       {s['omega_log_K']:.3f}      {s['Tc_formula_K']:.6f}")
print('Native calculation completed; scientific convergence not established.')
