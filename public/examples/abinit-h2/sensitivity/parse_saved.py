"""ABINIT 9.10.4 two-point teaching parser. No process launches. NOT_COMPUTE_RELEASE."""
import csv, json, re
import ast, hashlib
from pathlib import Path
import yaml
from decimal import Decimal as D, localcontext, ROUND_FLOOR, ROUND_CEILING

class GateError(ValueError): pass

def require(ok, reason):
    if not ok: raise GateError(reason)

NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'

def token(s, nonnegative=False):
    require(re.fullmatch(NUMBER, s) is not None, 'invalid/nonfinite numeric token: '+s)
    mantissa, *exponent = re.split('[EeDd]', s)
    places = len(mantissa.split('.')[1]) if '.' in mantissa else 0
    require(places <= 100 and abs(int(exponent[0]) if exponent else 0) <= 300, 'unsupported numeric range')
    with localcontext() as c:
        c.prec = 160
        v = D(s.replace('D','E').replace('d','e'))
        q = D(10) ** ((int(exponent[0]) if exponent else 0)-places)
        lo, hi = v-q/2, v+q/2
        if nonnegative:
            require(v >= 0, 'negative squared residual')
            lo = max(D(0), lo)
        return {'token':s, 'value':str(v), 'quantum':str(q), 'lower':str(lo), 'upper':str(hi)}

def interval(lo, hi): return {'lower':str(lo), 'upper':str(hi)}

def subtract(a,b):
    with localcontext() as c:
        c.prec=160
        return {'value':str(D(a['value'])-D(b['value'])), **interval(D(a['lower'])-D(b['upper']),D(a['upper'])-D(b['lower'])), 'left_token':a.get('token'), 'right_token':b.get('token')}

def norm(vec):
    """Outward-rounded enclosure; sqrt is correctly rounded then widened one ulp."""
    with localcontext() as c:
        c.prec=160
        mins=[D(0) if D(x['lower'])<=0<=D(x['upper']) else min(abs(D(x['lower'])),abs(D(x['upper']))) for x in vec]
        maxs=[max(abs(D(x['lower'])),abs(D(x['upper']))) for x in vec]
        c.rounding=ROUND_FLOOR
        lower2=sum((x*x for x in mins),D(0))
        lower=max(D(0),lower2.sqrt().next_minus())
        c.rounding=ROUND_CEILING
        upper2=sum((x*x for x in maxs),D(0))
        upper=upper2.sqrt().next_plus()
        # Only interval bounds, never an invented precise point estimate.
        return interval(lower,upper)

ETOT = re.compile(r'^\s*ETOT\s+(\d+)\s+('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')\s*$')
MARKER = re.compile(r'^\s*At SCF step\s+(\d+)\s+vres2\s*=\s*('+NUMBER+r')\s*<\s*tolvrs=\s*('+NUMBER+r')\s*=>converged\.\s*$')

# BaseLoader preserves literal scalars (including Fortran D); no executable tags.
class NativeLoader(yaml.BaseLoader):
    pass

def unique_mapping(loader,node):
    out={}
    for key,value in node.value:
        k=loader.construct_object(key,deep=True)
        require(isinstance(k,str) and k not in out,'duplicate/invalid YAML key')
        out[k]=loader.construct_object(value,deep=True)
    return out
NativeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,unique_mapping)

def native_records(section):
    docs=[]; spans=[]
    starts=list(re.finditer(r'^--- !([A-Za-z][A-Za-z0-9_]*)\s*$',section,re.M))
    for start in starts:
        end=re.search(r'^\.\.\.\s*$',section[start.end():],re.M)
        require(end is not None,'unterminated native YAML')
        stop=start.end()+end.end()
        require(not spans or start.start()>=spans[-1][1],'overlapping native YAML')
        body=section[start.end():start.end()+end.start()]
        require(not re.search(r'(^|\s)[&*][A-Za-z]',body),'native YAML aliases not supported')
        try: data=yaml.load(body,Loader=NativeLoader)
        except yaml.YAMLError as exc: raise GateError('malformed native YAML') from exc
        require(isinstance(data,dict),'native YAML not mapping')
        tag=start[1]
        if tag in ('DatasetInfo','BeginCycle','ResultsGS','EnergyTerms') or 'iteration_state' in data:
            state=data.get('iteration_state')
            require(isinstance(state,dict) and state.get('dtset')=='1','dataset YAML binding missing/mismatch')
        docs.append({'tag':tag,'data':data}); spans.append((start.start(),stop))
    for tag in ('DatasetInfo','BeginCycle','ResultsGS','EnergyTerms'):
        require(any(x['tag']==tag for x in docs),'missing required native YAML '+tag)
    for tag in ('DatasetInfo','BeginCycle'):
        require(sum(x['tag']==tag for x in docs)==1,'ambiguous native setup/cycle')
    # An unstructured iteration_state outside a native YAML record cannot supply binding.
    for match in re.finditer(r'^\s*iteration_state\s*:',section,re.M):
        require(any(a<=match.start()<b for a,b in spans),'unbound iteration_state outside YAML')
    return docs

def outvars_blocks(text):
    starts=list(re.finditer(r'^\s*-outvars: echo values of (preprocessed input variables|variables after computation)\s*-+\s*$',text,re.M))
    require(len(starts)==2 and [x[1] for x in starts]==['preprocessed input variables','variables after computation'],'missing/ambiguous initial/final outvars')
    blocks=[]
    for start in starts:
        tail=text[start.end():]; end=re.search(r'^={5,}\s*$',tail,re.M)
        require(end is not None,'unterminated outvars')
        blocks.append(tail[:end.start()])
    return blocks

def echo_values(blocks,key,n=1):
    unit={'ecut':'Hartree','acell':'Bohr'}.get(key)
    rows=[]
    for block in blocks:
        matches=re.findall(r'^\s*(?:[-P]\s*)?'+key+r'\s+([^\n]+)$',block,re.M)
        require(len(matches)==1,'missing/duplicate outvars '+key)
        parts=matches[0].split()
        require(len(parts)==n+(1 if unit else 0),'unknown outvars grammar '+key)
        if unit: require(parts[-1]==unit,'unknown outvars unit '+key)
        rows.append([token(x) for x in parts[:n]])
    require([x['value'] for x in rows[0]]==[x['value'] for x in rows[1]],'conflicting initial/final echo '+key)
    return rows[0]

def gamma_record(section):
    lines=[line for line in section.splitlines() if 'wavevector=' in line]
    require(len(lines)==1,'missing/ambiguous wavevector')
    match=re.fullmatch(r'\s*getcut:\s*wavevector=\s*(.*?)\s+ngfft=\s*\d+\s+\d+\s+\d+\s*',lines[0])
    require(match is not None,'malformed complete wavevector record')
    parts=match[1].split(); require(len(parts)==3,'wavevector component count')
    coords=[token(x) for x in parts]
    require(all(D(x['value'])==0 for x in coords),'non-Gamma wavevector')
    return coords

INPUT_PINS={'A10-tight':'6ccb30a898aa8ebb5ef1bf834f816464f89d2a1c30d1dd5b37f162be6ba447dc', 'B20-tight':'c841eef7bd075f632c173f572ad88255c362283b4c3c0fe4d01d1b35f4f21d6f'}
DEFAULT_SOURCE=Path(__file__).resolve().parent/'sources/variables_abinit.py'
DEFAULT_SOURCE_SHA='3dbd1f92ee8beb24edd78c5043eef50be62a233d5f62e8998d9b620ab315a263'

def bind_input(point,input_bytes):
    require(isinstance(input_bytes,bytes),'exact immutable input bytes required')
    require(hashlib.sha256(input_bytes).hexdigest()==INPUT_PINS[point],'input identity mismatch')
    text=input_bytes.decode('utf-8')
    active='\n'.join(line.split('#',1)[0] for line in text.splitlines())
    def scalar(key):
        matches=re.findall(r'^\s*'+key+r'\s+('+NUMBER+r')\s*$',active,re.M)
        require(len(matches)==1,'missing/ambiguous input '+key)
        return token(matches[0])
    cap=scalar('nstep'); stop=scalar('tolvrs')
    require(D(cap['value'])==30 and D(stop['value'])==D('1e-12'),'input cap/stop mismatch')
    return {'sha256':INPUT_PINS[point],'nstep':cap,'tolvrs':stop}

def default_nstep_contract():
    raw=DEFAULT_SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==DEFAULT_SOURCE_SHA,'official default source identity mismatch')
    tree=ast.parse(raw)
    values=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Variable':
            kw={x.arg:x.value for x in node.keywords}
            if isinstance(kw.get('abivarname'),ast.Constant) and kw['abivarname'].value=='nstep':
                require(isinstance(kw.get('defaultval'),ast.Constant),'unknown official nstep default')
                values.append(kw['defaultval'].value)
    require(values==[30],'official9.10.4 default contract mismatch')
    return {'version':'9.10.4','default':30,'source':str(DEFAULT_SOURCE),'sha256':DEFAULT_SOURCE_SHA,'scope':'Permits only absent nstep outvars; never replaces input or selected solver binding.'}

def bind_nstep_echo(blocks,input_binding,solver):
    require(solver.get('nstep')=='30' and D(input_binding['nstep']['value'])==30,'missing/conflicting solver/input nstep')
    contract=default_nstep_contract(); records=[]
    for block in blocks:
        matches=re.findall(r'^\s*(?:[-P]\s*)?nstep\s+([^\n]+)$',block,re.M)
        require(len(matches)<=1,'ambiguous optional nstep echo')
        if matches:
            parts=matches[0].split(); require(len(parts)==1,'unknown optional nstep grammar')
            value=token(parts[0]); require(D(value['value'])==30,'conflicting optional nstep echo')
            records.append({'present':True,'value':value})
        else: records.append({'present':False,'source_default_contract':True})
    return {'input':input_binding['nstep'],'selected_BeginCycle_nstep':solver['nstep'],'outvars':records,'official_default_contract':contract}

def parse(abo, stdout, stderr, point, receipt, input_bytes=None):
    require(point in ('A10-tight','B20-tight'), 'unknown point')
    input_binding=bind_input(point,input_bytes)
    require(receipt.get('exit_code')==0 and not receipt.get('timed_out') and receipt.get('cleanup_complete') is True,'process failure/timeout/unknown cleanup')
    require(receipt.get('identity_verified') is True,'identity not verified')
    raw=abo+'\n'+stdout+'\n'+stderr
    require(not re.search(r'(?i)\b(?:nan|infinity|inf)\b|^\s*(?:ERROR|FATAL)\b|!ERROR|SIGSEGV|segmentation fault',raw,re.M),'native error/nonfinite')
    require('.Version 9.10.4 of ABINIT' in abo,'version banner mismatch')
    require('Calculation completed.' in abo,'missing native completion')
    datasets=list(re.finditer(r'^== DATASET\s+(\d+)\s+=+',abo,re.M))
    ends=list(re.finditer(r'^== END DATASET\(S\)',abo,re.M))
    require(len(datasets)==len(ends)==1 and datasets[0][1]=='1' and ends[0].start()>datasets[0].end(),'missing/ambiguous dataset')
    section=abo[datasets[0].end():ends[0].start()]
    records=native_records(section)
    cycle=next(x['data'] for x in records if x['tag']=='BeginCycle')
    solver=cycle.get('solver',{})
    require(solver.get('iscf')=='7' and solver.get('nstep')=='30','solver echo mismatch')
    tols=cycle.get('tolerances',{})
    require(isinstance(tols,dict) and set(tols)=={'tolvrs'} and D(token(tols['tolvrs'])['value'])==D('1e-12'),'not sole tolvrs')
    blocks=outvars_blocks(abo)
    nstep_binding=bind_nstep_echo(blocks,input_binding,solver)
    for stopkey in ('toldfe','toldff','tolwfr','tolrff','tolrde','tolimg'):
        for block in blocks:
            for value in re.findall(r'^\s*'+stopkey+r'\s+('+NUMBER+r')',block,re.M):
                require(D(token(value)['value'])==0,'additional active echoed stopping tolerance')
    echoes={k:echo_values(blocks,k,n) for k,n in [('tolvrs',1),('ecut',1),('acell',3),('natom',1),('nband',1),('ngfft',3),('nsym',1),('ixc',1),('nkpt',1),('kptopt',1),('typat',2),('occ',2),('znucl',1),('diemac',1),('fftalg',1)]}
    expected={'tolvrs':['1e-12'],'ecut':['10' if point=='A10-tight' else '20'],'acell':['10']*3,'natom':['2'],'nband':['2'],'nsym':['16'],'ixc':['-1012'],'nkpt':['1'],'kptopt':['0'],'typat':['1','1'],'occ':['2','0'],'znucl':['1'],'diemac':['2'],'fftalg':['112']}
    for k,v in expected.items(): require([D(x['value']) for x in echoes[k]]==list(map(D,v)),'echo mismatch '+k)
    require(all(D(x['value'])>0 and D(x['value'])==D(x['value']).to_integral_value() for x in echoes['ngfft']),'invalid FFT')
    require(re.search(r'nspden\s*=\s*1\b',abo) and re.search(r'nsppol\s*=\s*1\b',abo) and re.search(r'nspinor\s*=\s*1\b',abo),'spin defaults missing/mismatch')
    require('psp file is ../data/H.psp8' in section and re.search(r'8\s+-1012\s+.*pspcod,pspxc',section),'pseudo echo mismatch')
    coord=re.findall(r'^\s*xcart\s+('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')\s*\n\s*('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')','\n'.join(blocks),re.M)
    require(coord and all(list(map(D,row))==list(map(D,['-.7','0','0','.7','0','0'])) for row in coord),'geometry mismatch/missing')
    gamma=gamma_record(section)
    grid=re.search(r'ngfft=\s*(\d+)\s+(\d+)\s+(\d+)',section)
    require(grid and list(map(D,grid.groups()))==[D(x['value']) for x in echoes['ngfft']],'grid echo mismatch')
    require(re.search(r'avg\. npw.*?are\s+('+NUMBER+r')\s+('+NUMBER+r')',section),'missing npw')
    box=re.search(r'boxcut\(ratio\)=\s*('+NUMBER+r')',section); require(box and D(token(box[1])['value'])>=2,'boxcut missing/invalid')
    require('Etot(hartree)' in section and re.search(r'Etot\(hartree\).*vres2',section),'missing energy/residual units header')
    ledger=[]
    for line_no,line in enumerate(abo.splitlines(),1):
        if re.match(r'^\s*ETOT\b',line):
            match=ETOT.fullmatch(line); require(match is not None,'malformed ETOT')
            require(datasets[0].end() < abo.find(line) < ends[0].start(),'ETOT outside dataset')
            i=int(match[1]); vals=[token(match[j],nonnegative=j in (4,5)) for j in range(2,6)]
            require(re.fullmatch(r'[+-]?\d\.\d{3}[EeDd][+-]\d+',match[5]),'unknown ETOT residual precision')
            ledger.append({'dataset':1,'iteration':i,'line':line_no,'energy_Ha':vals[0],'deltaE_Ha':vals[1],'residm':vals[2],'vres2_Ha2':vals[3]})
    require(ledger and [x['iteration'] for x in ledger]==list(range(1,len(ledger)+1)) and len(ledger)<=30,'missing/duplicate/noncontiguous/too many iterations')
    markers=[MARKER.fullmatch(x) for x in section.splitlines() if '=>converged.' in x]
    require(len(markers)==1 and markers[0] is not None,'missing/ambiguous/wrong potential marker')
    require(not re.search(r'At SCF step.*(?:nres2|etot is converged)',section),'old/wrong criterion')
    mark=markers[0]; require(int(mark[1])==ledger[-1]['iteration'],'marker iteration mismatch')
    require(re.fullmatch(r'[+-]?\d\.\d{2}[EeDd][+-]\d+',mark[2]),'unknown marker residual precision')
    mr=token(mark[2],True); last=ledger[-1]['vres2_Ha2']
    require(D(token(mark[3])['value'])==D('1e-12'),'marker threshold mismatch')
    require(D(mr['upper'])<D('1e-12') and D(last['upper'])<D('1e-12'),'residual upper bound not strictly below threshold')
    require(max(D(mr['lower']),D(last['lower']))<=min(D(mr['upper']),D(last['upper'])),'residual intervals do not overlap')
    # stdout may lack units header; require exact numeric record correspondence to unit-bearing abo.
    outrows=[ETOT.fullmatch(x) for x in stdout.splitlines() if re.match(r'^\s*ETOT\b',x)]
    require(all(x is not None for x in outrows) and [x.groups() for x in outrows]==[ETOT.fullmatch(x).groups() for x in abo.splitlines() if ETOT.fullmatch(x)],'stdout/abo ETOT mismatch')
    outmarks=[MARKER.fullmatch(x) for x in stdout.splitlines() if '=>converged.' in x]
    require(len(outmarks)==1 and outmarks[0] and outmarks[0].groups()==mark.groups(),'stdout/abo marker mismatch')
    require(section.find('cartesian forces (hartree/bohr) at end:')>section.find(mark[0]),'forces precede convergence marker')
    forceheads=[i for i,x in enumerate(section.splitlines()) if x.strip()=='cartesian forces (hartree/bohr) at end:']
    require(len(forceheads)==1,'missing/ambiguous force units')
    lines=section.splitlines(); forces=[]
    for atom,line in enumerate(lines[forceheads[0]+1:forceheads[0]+3],1):
        fields=line.split(); require(len(fields)==4 and fields[0]==str(atom),'force atom/vector mismatch')
        forces.append([token(x) for x in fields[1:]])
    require(len(forces)==2,'incomplete forces')
    require(forceheads[0]+3>=len(lines) or not re.match(r'^\s*\d+\s+'+NUMBER,lines[forceheads[0]+3]),'extra force atom')
    with localcontext() as c:
        c.prec=160
        net=[{'value':str(sum((D(forces[i][j]['value']) for i in range(2)),D(0))),**interval(sum((D(forces[i][j]['lower']) for i in range(2)),D(0)),sum((D(forces[i][j]['upper']) for i in range(2)),D(0)))} for j in range(3)]
    netnorm=norm(net); require(D(netnorm['upper'])<=D('1e-5'),'raw netforce smoke guard')
    return {'status':'NATIVE_PARSER_GATES_PASS_NOT_MATERIAL_ACCURACY','point':point,'ledger':ledger,'energy':ledger[-1]['energy_Ha'],'forces':forces,'netforce_interval_Ha_Bohr':netnorm,'marker_residual':mr,'echoes':echoes,'immutable_input_binding':input_binding,'nstep_binding':nstep_binding,'native_YAML_tags':[x['tag'] for x in records],'wavevector_tokens':gamma,'grid':grid.groups(),'boxcut':token(box[1]),'raw_logs_preserve_all_warnings':True,'later_XC_prefloor_recurrence':'UNKNOWN','warning_lines':[{'line':i,'text':x} for i,x in enumerate(raw.splitlines(),1) if re.search(r'(?i)warning|not supported|negative|density|floor',x)],'raw_native_logs':{'abo':abo,'stdout':stdout,'stderr':stderr}}

def baseline_measurement(b):
    return {'energy':token(b['final_ETOT_Ha']),'forces':[[token(x) for x in row] for row in b['raw_force_Ha_Bohr']], 'scope':'CACHED_LOOSE_SCF_BASELINE_NO_RERUN'}

def compare(new,old,label):
    with localcontext() as c:
        c.prec=160
        vectors=[[subtract(x,y) for x,y in zip(a,b)] for a,b in zip(new['forces'],old['forces'])]
        norms=[norm(v) for v in vectors]
        return {'comparison':label,'signed_energy_Ha':subtract(new['energy'],old['energy']),'per_atom_force_differences_Ha_Bohr':vectors,'per_atom_norm_intervals_Ha_Bohr':norms,'max_atom_norm_interval_Ha_Bohr':interval(max(D(x['lower']) for x in norms),max(D(x['upper']) for x in norms)),'classification':'NONE_MEASUREMENTS_REGARDLESS_SIGN_OR_MAGNITUDE'}

def write_tables(root,result,comparisons):
    """All scalar representations are literal tokens or interval bounds; no added precision."""
    with (root/'scf-ledger.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['point','dataset','iteration','energy_Ha_token','deltaE_Ha_token','residm_token','vres2_Ha2_token','line','residual_lower','residual_upper'])
        for row in result['ledger']: w.writerow([result['point'],row['dataset'],row['iteration'],*[row[k]['token'] for k in ('energy_Ha','deltaE_Ha','residm','vres2_Ha2')],row['line'],row['vres2_Ha2']['lower'],row['vres2_Ha2']['upper']])
    with (root/'comparisons.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['comparison','observable','atom','component','value_or_literal','lower','upper','units'])
        for comp in comparisons:
            e=comp['signed_energy_Ha']; w.writerow([comp['comparison'],'signed_energy','','',e['value'],e['lower'],e['upper'],'Ha'])
            for i,vec in enumerate(comp['per_atom_force_differences_Ha_Bohr'],1):
                for axis,x in zip('xyz',vec): w.writerow([comp['comparison'],'signed_force',i,axis,x['value'],x['lower'],x['upper'],'Ha/Bohr'])
                x=comp['per_atom_norm_intervals_Ha_Bohr'][i-1]; w.writerow([comp['comparison'],'vector_norm',i,'','',x['lower'],x['upper'],'Ha/Bohr'])
            x=comp['max_atom_norm_interval_Ha_Bohr']; w.writerow([comp['comparison'],'maximum_vector_norm','','','',x['lower'],x['upper'],'Ha/Bohr'])
    with (root/'forces.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['point','atom','component','token','lower','upper','units'])
        for i,vec in enumerate(result['forces'],1):
            for axis,x in zip('xyz',vec): w.writerow([result['point'],i,axis,x['token'],x['lower'],x['upper'],'Ha/Bohr'])
