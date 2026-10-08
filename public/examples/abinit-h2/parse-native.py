from pathlib import Path
import re,json,csv,hashlib,shutil
from decimal import Decimal,getcontext
getcontext().prec=40
p=Path(__file__).resolve().parent;load=lambda f:json.loads(Path(f).read_text());receipt=load(p/'run-metadata.json');failure=None;checks={};rows=[];force_rows=[]
D=lambda v:Decimal(v.replace('D','E').replace('d','E'));num=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
def table(file,rs):
 with (p/file).open('w') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
try:
 assert receipt['exit_code']==0 and receipt['native_invocation_count']==1 and not receipt['timeout_failure']
 stdout=(p/'outputs/h2.stdout').read_text();stderr=(p/'outputs/h2.stderr').read_text();abo=(p/'inputs/h2.abo').read_text()
 for text in [stdout,abo]:
  assert re.search(r'\bABINIT\s+9\.10\.4\b|Version 9\.10\.4 of ABINIT',text)
  assert re.search(r'iter\s+Etot\(hartree\)\s+deltaE\(h\)\s+residm\s+vres2',abo),'unknown native abo ETOT units/header; stdout rows must match abo exactly'
 def etot(text):
  return re.findall(r'^\s*ETOT\s+(\d+)\s+('+num+r')\s+('+num+r')\s+('+num+r')\s+('+num+r')\s*$',text,re.M)
 native=etot(abo);assert native==etot(stdout) and len(native)>=3
 assert [int(x[0]) for x in native]==list(range(1,len(native)+1))
 for i,t in enumerate(native):
  assert all(D(x).is_finite() for x in t[1:]);e=D(t[1]);delta=e-D(native[i-1][1]) if i else None
  rows.append({'iteration':int(t[0]),'energy_Ha':t[1],'native_deltaE_Ha':t[2],'residm_native':t[3],'vres2_native':t[4],'derived_deltaE_Ha':str(delta) if delta is not None else '', 'raw_record':'ETOT '+' '.join(t)})
 table('scf-ledger.csv',rows)
 markers=re.findall(r'At SCF step\s+(\d+), etot is converged',abo);assert len(markers)==1 and int(markers[0])==int(native[-1][0])<=10
 markers_stdout=re.findall(r'At SCF step\s+(\d+), etot is converged',stdout);assert markers==markers_stdout
 diffs=[abs(D(native[-2][1])-D(native[-3][1])),abs(D(native[-1][1])-D(native[-2][1]))]
 # Final precise E rows are rounded; include conservative half-last-digit bounds for each subtraction.
 bounds=[(Decimal(10)**D(native[i][1]).as_tuple().exponent+Decimal(10)**D(native[i-1][1]).as_tuple().exponent)/2 for i in [-2,-1]]
 assert all(x+y<Decimal('1e-6') for x,y in zip(diffs,bounds)),'ambiguous or failed toldfe threshold'
 match=re.search(r'cartesian forces \(hartree/bohr\) at end:\s*\n\s*1\s+('+num+r')\s+('+num+r')\s+('+num+r')\s*\n\s*2\s+('+num+r')\s+('+num+r')\s+('+num+r')',abo,re.I);assert match,'missing exact Cartesian force units/vector'
 v=list(map(D,match.groups()));assert all(x.is_finite() for x in v)
 for i in range(2):force_rows.append({'atom_index':i+1,'species':'H','Fx_Ha_Bohr':str(v[3*i]),'Fy_Ha_Bohr':str(v[3*i+1]),'Fz_Ha_Bohr':str(v[3*i+2]),'source':'h2.abo cartesian forces (hartree/bohr) at end'})
 table('forces.csv',force_rows);sums=[v[j]+v[j+3] for j in range(3)];net=sum(x*x for x in sums).sqrt();assert net<=D('1e-5')
 geom=re.search(r'^\s*xcart\s+('+num+r')\s+('+num+r')\s+('+num+r')\s*\n\s*('+num+r')\s+('+num+r')\s+('+num+r')',abo,re.M);assert geom and list(map(D,geom.groups()))==list(map(D,['-.7','0','0','.7','0','0']))
 required=[r'acell\s+1\.0000000000E\+01\s+1\.0000000000E\+01\s+1\.0000000000E\+01 Bohr',r'ecut\s+1\.00000000E\+01 Hartree',r'toldfe\s+1\.00000000E-06 Hartree',r'nstep\s+10\b',r'natom\s+2\b',r'typat\s+1\s+1\b',r'znucl\s+1\.00000',r'ixc\s+-1012',r'kptopt\s+0',r'nkpt\s+1']
 assert all(re.search(x,abo) for x in required)
 assert re.search(r'kpt=\s+0\.0000\s+0\.0000\s+0\.0000',abo)
 assert 'psp file is ../data/H.psp8' in stdout and '8   -1012' in stdout and 'ONCVPSP-3.3.0' in stdout
 fatal=[]
 for label,t in [('stdout',stdout),('stderr',stderr),('abo',abo)]:
  for i,line in enumerate(t.splitlines(),1):
   if re.search(r'\b(?:NaN|Inf(?:inity)?|FATAL|ERROR)\b|!ERROR',line,re.I):fatal.append({'source':label,'line':i,'text':line})
 assert not fatal,'fatal/nonfinite indicator requires review'
 warningblocks=re.findall(r'--- !WARNING\n.*?\n\.\.\.',stdout,re.S)
 warningnotes=[{'source':label,'line':i,'text':line} for label,t in [('stdout',stdout),('abo',abo),('stderr',stderr)] for i,line in enumerate(t.splitlines(),1) if re.search(r'WARNING|not supported|switch to a more recent|src_file:|set to xc_denpos|Lowest was',line,re.I)]
 warnings={'native_warning_count':len(warningblocks),'full_warning_blocks':warningblocks,'all_warning_related_lines':warningnotes,'old_version_support_notice':'This version of ABINIT is not supported anymore. Action switch to newer version; retained, no automatic change','status':'PENDING_INDEPENDENT_WARNING_REVIEW','no_native_warnings_suppressed':True}
 (p/'warnings.json').write_text(json.dumps(warnings,indent=2))
 settings={'native_version':'9.10.4','MPI_native':'one direct native call, no mpirun','natom':2,'typat':[1,1],'znucl':[1],'cell_Bohr':[10,10,10],'xcart_Bohr':[['-.7','0','0'],['.7','0','0']],'ecut_Ha':'10','nstep':10,'toldfe_Ha':'1e-6','ixc':-1012,'pseudo':'PSP8 ONCVPSP3.3.0 scalarrel NC PseudoDojo0.4LDA PW from exact hash-bound H file','kpt_reduced':['0','0','0'],'nband':2,'nsppol':1,'nspinor':1,'nspden':1,'occopt':1,'occ':['2','0'],'nsym':16,'spgroup':123,'fftalg':112,'ngfft':[30,30,30],'source':'full h2.abo + stdout echoed defaults retained; no blanket10.8.3 equality','geometry_fixed':True}
 (p/'echoed-native-settings.json').write_text(json.dumps(settings,indent=2))
 checks={'status':'EXECUTOR_NUMERIC_CRITERIA_PASS_NOT_INDEPENDENT_ACCEPTANCE','native_convergence_step':int(markers[0]),'ETOT_rows':len(rows),'finite_native_energies':True,'energy_unit':'hartree','final_three_precise_E_Ha':[t[1] for t in native[-3:]],'last_two_absolute_differences_Ha':list(map(str,diffs)),'rounding_error_upper_bounds_Ha':list(map(str,bounds)),'threshold_Ha':'1e-6','two_differences_strictly_below_threshold_even_with_rounding':True,'force_unit':'hartree/bohr','raw_force_vectors':[list(map(str,v[:3])),list(map(str,v[3:]))],'raw_force_sum_components_Ha_Bohr':list(map(str,sums)),'net_force_norm_Ha_Bohr':str(net),'net_force_guard':'1e-5','force_vectors_modified':False,'native_symmetry_cancellation_can_enforce_netzero_not_force_accuracy':True,'input_geometry_version_and_pseudo_echo_checks':True,'process_exit_and_SCF_separate':True,'warnings_review':'pending independent review','basis_box_force_accuracy':False,'GPAW_energy_comparison_oracle':False}
 (p/'native-criterion-checks.json').write_text(json.dumps(checks,indent=2));print(checks['status'],diffs,net)
except Exception as e:
 failure=str(e);(p/'native-criterion-checks.json').write_text(json.dumps({'status':'FAIL_CLOSED_NATIVE_PARSER_OR_CRITERION','reason':failure,'retry_count':0,'input_criteria_changes':0},indent=2));print('PARSER_FAIL_STOP',failure)
(p/'parser-state.json').write_text(json.dumps({'failure':failure,'scientific_invocations':receipt['native_invocation_count'],'native_numeric_checks_pass':failure is None,'independent_acceptance':'PENDING'},indent=2))
