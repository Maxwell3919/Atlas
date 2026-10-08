# SPDX-License-Identifier: MIT
"""Rebuild actual saved-data tables/figures. Never launches any scientific program."""
import csv,json,re,hashlib
from pathlib import Path
from decimal import Decimal as D,localcontext,ROUND_FLOOR,ROUND_CEILING
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from parse_saved import parse,token,ETOT,compare,norm
ROOT=Path(__file__).resolve().parent

def write_json(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def csv_file(path,header,rows):
    with path.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)
def short_bound(value,rounding):
    with localcontext() as ctx:
        ctx.prec=12; ctx.rounding=rounding; return str(+D(value))
def compact_norm(x):
    return {'lower':short_bound(x['lower'],ROUND_FLOOR),'upper':short_bound(x['upper'],ROUND_CEILING),'note':'Outward arithmetic bounds, not physical significant digits'}
def raw_case(name):
    folder=ROOT/'cases'/name
    return (folder/'inputs/h2.abo').read_text(),(folder/'outputs/stdout.txt').read_text(),(folder/'outputs/stderr.txt').read_text(),(folder/'inputs/h2.abi').read_bytes()
def cached_baseline():
    abo,stdout,stderr,inp=raw_case('cached-loose-baseline')
    rows=[ETOT.fullmatch(x) for x in abo.splitlines() if ETOT.fullmatch(x)]
    assert rows and 'etot is converged' in abo and 'cartesian forces (hartree/bohr)' in abo
    body=abo.split('cartesian forces (hartree/bohr) at end:')[1].splitlines()
    force=[]
    for atom in (1,2):
        fields=body[atom].split(); assert fields[0]==str(atom) and len(fields)==4; force.append([token(x) for x in fields[1:]])
    return {'point':'cached-loose-baseline','energy':token(rows[-1][2]),'forces':force,'ledger':[{'iteration':int(x[1]),'energy_Ha':token(x[2]),'deltaE_Ha':token(x[3]),'residm':token(x[4]),'vres2_Ha2':token(x[5],True)} for x in rows],'scope':'Cached accepted10Ha toldfe1e-6/nstep10; no new native call'}
def main():
    manifest=json.loads((ROOT/'raw-source-manifest.json').read_text())
    for item in manifest['members']: assert hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
    provenance=json.loads((ROOT/'measurement-provenance.json').read_text())
    tables=ROOT/'tables'; figures=ROOT/'figures'; tables.mkdir(exist_ok=True); figures.mkdir(exist_ok=True)
    cases={}
    for name in ('A','B'):
        abo,stdout,stderr,inp=raw_case(name); facts=provenance['cases'][name]
        # Facts describe independently accepted saved evidence, not a new process or fabricated receipt.
        receipt={'exit_code':facts['native_exit_code'],'timed_out':False,'cleanup_complete':facts['cleanup_complete'],'identity_verified':facts['pre_post_identity_verified']}
        result=parse(abo,stdout,stderr,'A10-tight' if name=='A' else 'B20-tight',receipt,input_bytes=inp)
        result['nstep_binding']['official_default_contract']['source']='sources/variables_abinit.py'
        result.pop('raw_native_logs') # Full raw files remain alongside, never replaced by warning indexes.
        result['netforce_interval_Ha_Bohr']=compact_norm(result['netforce_interval_Ha_Bohr'])
        cases[name]=result
    cases['cached-loose-baseline']=cached_baseline()
    comparisons=[compare(cases['A'],cases['cached-loose-baseline'],'A-minus-cached-loose-baseline'),compare(cases['B'],cases['A'],'B-minus-A')]
    for c in comparisons:
        c['per_atom_norm_intervals_Ha_Bohr']=[compact_norm(x) for x in c['per_atom_norm_intervals_Ha_Bohr']]
        c['max_atom_norm_interval_Ha_Bohr']=compact_norm(c['max_atom_norm_interval_Ha_Bohr'])
    write_json(tables/'measurements.json',{'scope':'Saved teaching sensitivity only; no smallness/order/stability/physical-accuracy classification','cases':cases,'comparisons':comparisons})
    rows=[]; forces=[]; settings=[]; warnings={}
    for name,result in cases.items():
        for r in result['ledger']:
            e=r['energy_Ha']; v=r['vres2_Ha2']
            rows.append([name,r['iteration'],e['token'],e['lower'],e['upper'],r['deltaE_Ha']['token'],r['residm']['token'],v['token'],v['lower'],v['upper']])
        for i,vec in enumerate(result['forces'],1):
            for axis,x in zip('xyz',vec): forces.append([name,i,axis,x['token'],x['lower'],x['upper'],'Ha/Bohr'])
        abo,stdout,stderr,_=raw_case(name)
        full_blocks=re.findall(r'^--- !WARNING\s*\n.*?^\.\.\.\s*$',stdout,re.M|re.S)
        first_iter=stdout.find('ITER STEP NUMBER')
        events=[]
        for block in full_blocks:
            count=re.search(r'at (\d+) points',block); lowest=re.search(r'Lowest was\s*('+re.escape('')+r'[+\-\d.EeDd]+)',block); floor=re.search(r'xc_denpos\s*=\s*([+\-\d.EeDd]+)',block)
            events.append({'full_block':block,'before_first_iteration':stdout.find(block)<first_iter if first_iter>=0 else None,'count':count[1] if count else None,'minimum_el_Bohr3_token':lowest[1].rstrip('.') if lowest else None,'floor_el_Bohr3_token':floor[1].rstrip('.') if floor else None})
        notices=[x for x in stdout.splitlines() if 'not supported' in x or 'more than 3 years' in x]
        warnings[name]={'visible_WARNING_blocks':events,'visible_count':len(events),'unsupported_notice_lines':notices,'later_XC_prefloor_and_final':'UNKNOWN','raw_stdout':'cases/'+name+'/outputs/stdout.txt','warning_count_not_no_clipping_proof':True}
        if name in ('A','B'):
            npw=re.search(r'avg\. npw.*?are\s+([\d.]+)\s+([\d.]+)',abo)
            ecut=result['echoes']['ecut'][0]['token']
            settings.append([name,ecut,*result['grid'],npw[1],npw[2],result['boxcut']['token'],112,30,'1e-12','NC-LDA PSP8 H;10Bohr;Gamma;H at +/-0.7Bohr'])
    csv_file(tables/'scf-records.csv',['case','iteration','energy_Ha_token','energy_lower_Ha','energy_upper_Ha','native_deltaE_Ha_token','residm_token','potential_sum_residual_Ha2_token','residual_lower_Ha2','residual_upper_Ha2'],rows)
    csv_file(tables/'raw-forces.csv',['case','atom','axis','native_token','lower','upper','units'],forces)
    csv_file(tables/'settings.csv',['case','ecut_Ha_token','ngfft_x','ngfft_y','ngfft_z','npw_avg1_token','npw_avg2_token','boxcut_token','fftalg','nstep_input_and_YAML','tolvrs','fixed_model'],settings)
    write_json(tables/'warnings.json',warnings)
    diffrows=[]
    for c in comparisons:
        e=c['signed_energy_Ha']; diffrows.append([c['comparison'],'signed_energy','','',e['value'],e['lower'],e['upper'],'Ha'])
        for i,vec in enumerate(c['per_atom_force_differences_Ha_Bohr'],1):
            for axis,x in zip('xyz',vec): diffrows.append([c['comparison'],'signed_force',i,axis,x['value'],x['lower'],x['upper'],'Ha/Bohr'])
            x=c['per_atom_norm_intervals_Ha_Bohr'][i-1]; diffrows.append([c['comparison'],'vector_norm',i,'','',x['lower'],x['upper'],'Ha/Bohr'])
        x=c['max_atom_norm_interval_Ha_Bohr']; diffrows.append([c['comparison'],'maximum_atom_norm','','','',x['lower'],x['upper'],'Ha/Bohr'])
    csv_file(tables/'signed-comparisons.csv',['comparison','observable','atom','axis','source_precision_value','lower','upper','units'],diffrows)
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'atlas-saved-h2'})
    fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
    plotrows=[]
    for name,color in [('A','#176b91'),('B','#b84d25')]:
        ledger=cases[name]['ledger']; y=[float(D(x['vres2_Ha2']['value'])) for x in ledger]; assert all(v>0 for v in y)
        ax.semilogy([x['iteration'] for x in ledger],y,'o-',color=color,label=name+(' 10 Ha / FFT30³' if name=='A' else ' 20 Ha / FFT45³'))
        plotrows += [[name,x['iteration'],x['vres2_Ha2']['token'],x['vres2_Ha2']['lower'],x['vres2_Ha2']['upper']] for x in ledger]
    ax.axhline(1e-12,color='black',ls='--',lw=1,label='Native tolvrs = 1e-12')
    ax.set(xlabel='SCF iteration',ylabel='Mean-removed potential sum residual (Ha²)',title='Actual saved SCF records — two fixed settings')
    ax.set_xticks(range(1,11)); ax.grid(alpha=.2); ax.legend(fontsize=9)
    fig.savefig(figures/'scf-residual.png',dpi=160,metadata={'Software':'Saved-data postprocess'}); plt.close(fig)
    csv_file(figures/'scf-residual.csv',['case','iteration','raw_residual_Ha2','lower_Ha2','upper_Ha2'],plotrows)
    fig,axes=plt.subplots(1,3,figsize=(11,4),layout='constrained')
    for j,c in enumerate(comparisons):
        e=c['signed_energy_Ha']; val=float(D(e['value'])); axes[j].bar([0],[val],color=['#176b91','#b84d25'][j],width=.4)
        axes[j].axhline(0,color='black',lw=.8); axes[j].set_xticks([0],['A − cached\nloose baseline' if j==0 else 'B − A\ncutoff + automatic FFT'])
        axes[j].set_ylabel('Signed energy difference (Ha)'); axes[j].set_title('Independent linear scale'); axes[j].text(0,.95,e['value']+' Ha',transform=axes[j].transAxes,va='top',fontsize=9)
    vals=[float((D(c['max_atom_norm_interval_Ha_Bohr']['lower'])+D(c['max_atom_norm_interval_Ha_Bohr']['upper']))/2) for c in comparisons]
    axes[2].scatter([0,1],vals,color=['#176b91','#b84d25'],s=55); axes[2].set_yscale('log'); axes[2].set_ylim(min(vals)/3,max(vals)*3)
    axes[2].set_xticks([0,1],['A − cached','B − A']); axes[2].set_ylabel('Max atom force-difference norm (Ha/Bohr)'); axes[2].set_title('Measured force differences')
    fig.savefig(figures/'setting-comparisons.png',dpi=160,metadata={'Software':'Saved-data postprocess'}); plt.close(fig)
    csv_file(figures/'setting-comparisons.csv',['comparison','energy_Ha','energy_lower_Ha','energy_upper_Ha','max_force_norm_lower_Ha_Bohr','max_force_norm_upper_Ha_Bohr'],[[c['comparison'],c['signed_energy_Ha']['value'],c['signed_energy_Ha']['lower'],c['signed_energy_Ha']['upper'],c['max_atom_norm_interval_Ha_Bohr']['lower'],c['max_atom_norm_interval_Ha_Bohr']['upper']] for c in comparisons])
    write_json(tables/'regeneration-summary.json',{'native_invocations':0,'data_root':'package-relative','actual_saved_A_rows':len(cases['A']['ledger']),'actual_saved_B_rows':len(cases['B']['ledger']),'baseline_rows':len(cases['cached-loose-baseline']['ledger']),'scope':'No new science run; two fixed settings, not cutoff convergence series'})
if __name__=='__main__': main()
