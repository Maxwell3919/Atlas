#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math,xml.etree.ElementTree as ET
import numpy as np
b=Path(__file__).resolve().parent
raw=b/'source/alpha2F.dat'
a=np.loadtxt(raw); f=a[:,0]; y=a[:,4]
assert a.shape==(2000,11)
assert f[0]==0 and y[0]==0 and np.all(f[1:]>0) and np.all(y>=0)
h_meV_THz=6.62607015e-34/1.602176634e-19*1e15
f1=f[1:]; y1=y[1:]; w=f1*h_meV_THz
n=len(w)
np.savetxt(b/'al-sigma020.a2f',np.column_stack([w,y1]),fmt=['%.12f','%.8f'],header='omega_meV alpha2F ; QE lambda.x sigma=0.020 Ry; zero row removed only',comments='# ')
l_epw=2*w[-1]/n*np.sum(y1/w)
kbeV=8.617333262145e-5
wlogeV=math.exp(float(2*(w[-1]/1000)/n*np.sum(y1*np.log(w/1000)/(w/1000))/l_epw))
l_trap=float(np.sum(np.diff(f1)*((y1/f1)[1:]+(y1/f1)[:-1])))
x=ET.parse(b/'source/data-file-schema.xml').getroot()
aout=x.find('output/atomic_structure'); alat=float(aout.attrib['alat']); nat=int(aout.attrib['nat'])
avec=np.array([[float(v) for v in aout.find('cell/'+z).text.split()] for z in ('a1','a2','a3')]); at=avec/alat
bg=np.linalg.inv(at).T
atoms=list(aout.find('atomic_positions')); tau=np.array([[float(v) for v in a.text.split()] for a in atoms])/alat
species=list(x.find('input/atomic_species')); names=[a.attrib['name'] for a in species]; masses=[float(a.findtext('mass')) for a in species]
noncolin=x.findtext('input/spin/noncolin')=='true'
nelec=float(x.findtext('output/band_structure/nelec'))
fmt=lambda v:' '.join('%.16e'%float(z) for z in np.asarray(v).ravel())
lines=[str(nat),str(3*nat),fmt([nelec,0]),fmt(at),fmt(bg),fmt([abs(np.linalg.det(avec))]),fmt([alat]),fmt(tau),fmt([m*1.66053906660e-27/9.1093837015e-31/2 for m in masses]+[0.0]*(10-len(masses))),' '.join(str(names.index(a.attrib['name'])+1) for a in atoms),'T' if noncolin else 'F','F','! spectrum-only adapter: no Wannier centers calculated','! spectrum-only adapter: no Wannier lattice L calculated']
(b/'crystal.fmt').write_text('\n'.join(lines)+'\n')
r={'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'source_shape':list(a.shape),'selected_sigma_Ry':.020,'source_spectrum_width_THz':.12,'source_mu_star':.1,'solver_mu_star':.1,'source_xml_sha256':hashlib.sha256((b/'source/data-file-schema.xml').read_bytes()).hexdigest(),'frequency_conversion_meV_per_THz':h_meV_THz,'removed_rows':[{'omega_THz':0,'alpha2F':0}],'nqstep':n,'omega_max_meV':float(w[-1]),'epw_rectangle_lambda':float(l_epw),'trapz_lambda_printed_grid':float(l_trap),'epw_omega_log_K':wlogeV/kbeV,'max_print_rounding_step_deviation_THz':float(np.max(abs(np.diff(f)-f[-1]/n))),'crystal_adapter':'QE XML physical fields; amass uses native Rydberg mass unit AMU_RY=AMU_SI/ELECTRONMASS_SI/2, fixed ntypx=10 with unused species slots zero; no computed Wannier centers; trailing comments are skipped records in EPW6.0 isotropic fila2f reader','material_Tc_acceptance':'not assessed'}
(b/'spectrum-checks.json').write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))
