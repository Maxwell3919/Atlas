from pathlib import Path
import csv, json, re, hashlib, sys

root=Path(sys.argv[1])
linear=list(csv.DictReader((root/'linear.csv').open()))
gap=list(csv.DictReader((root/'gap.csv').open()))
errors=[]; sources={}; checked_linear=checked_gap=0
for row in linear:
    p=root/row['run']/'epw.out'; text=p.read_text()
    sources[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    table=[m.groups() for m in re.finditer(r'^\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s*$', text, re.M)]
    selected=[r for r in table if abs(float(r[0])-float(row['T_K']))<1e-9]
    if len(selected)!=1:
        errors.append(['linear-row',row['run'],row['T_K'],len(selected)]); continue
    a=selected[0]
    expected=[float(row['max_eigenvalue']),int(row['nsiw']),float(row['actual_wscut_eV']),int(row['iterations'])]
    actual=[float(a[1]),int(a[2]),float(a[3]),int(a[4])]
    if actual!=expected:errors.append(['linear-values',row['run'],actual,expected])
    if 'Finish: Solving (isotropic) linearized Eliashberg equation' not in text:
        errors.append(['linear-no-finish',row['run']])
    if int(row['iterations'])>=int(row['nsiter']):errors.append(['linear-hit-limit',row['run']])
    checked_linear+=1
for row in gap:
    if row['converged']!='True' or row['whole_run_complete']!='True':continue
    d=root/row['run']; p=d/'epw.out'; text=p.read_text()
    sources[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    if 'Convergence was reached' not in text or (d/'epw.err').stat().st_size:
        errors.append(['nonlinear-state',row['run']])
    fs=list(d.glob('*.imag_iso_*'))
    if len(fs)!=1:errors.append(['gap-file-count',row['run'],len(fs)]);continue
    data=[line.split() for line in fs[0].read_text().splitlines() if re.match(r'^\s*[+\-\d.]',line)]
    omega,z,delta=map(float,data[0]); expected=float(row['Delta_omega0_meV'])
    if abs(1000*delta-expected)>1e-10:errors.append(['gap-unit-or-value',row['run'],1000*delta,expected])
    if abs(omega-float(row['omega0_eV']))>1e-14:errors.append(['omega',row['run']])
    sources[str(fs[0].relative_to(root))]=hashlib.sha256(fs[0].read_bytes()).hexdigest()
    checked_gap+=1
report={'linear_rows_checked':checked_linear,'independent_converged_gap_rows_checked':checked_gap,
        'source_sha256':sources,'errors':errors}
print(json.dumps(report,indent=2))
assert checked_gap==1 and checked_linear==15 and not errors
