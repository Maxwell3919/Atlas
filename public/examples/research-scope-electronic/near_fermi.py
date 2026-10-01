#!/usr/bin/env python3
"""Read existing ZrCl2/Sc2C tables. No DFT jobs or source writes."""
from pathlib import Path
import argparse, csv, json, math, re


def interp(rows, key, x):
    for a, b in zip(rows, rows[1:]):
        xa, xb = float(a['energy_minus_fermi_eV']), float(b['energy_minus_fermi_eV'])
        if xa <= x <= xb:
            f = (x-xa)/(xb-xa)
            return float(a[key])*(1-f)+float(b[key])*f
    raise ValueError('Energy outside recorded grid')


def integrate(rows, key, lo=-0.1, hi=0.0):
    pts = [(lo, interp(rows,key,lo))]
    pts += [(float(r['energy_minus_fermi_eV']),float(r[key])) for r in rows
            if lo < float(r['energy_minus_fermi_eV']) < hi]
    pts += [(hi, interp(rows,key,hi))]
    return sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(pts,pts[1:]))


def read_frozen(root):
    groups = {}
    with (root/'frozen-controls-pdos_20260929/frozen_pdos_long.csv').open() as f:
        for r in csv.DictReader(f):
            if not all(math.isfinite(float(r[k])) for k in
                       ['energy_minus_fermi_eV','sc2c_pdos','zrcl2_pdos','total_projected_pdos']):
                raise ValueError('Nonfinite PDOS')
            groups.setdefault(r['state'],[]).append(r)
    out=[]
    for state, rows in groups.items():
        xs=[float(r['energy_minus_fermi_eV']) for r in rows]
        if any(b <= a for a,b in zip(xs,xs[1:])): raise ValueError('Nonmonotonic grid')
        row={'state':state,'rows':len(rows)}
        for key in ['sc2c_pdos','zrcl2_pdos','total_projected_pdos']:
            row[key+'_at_EF_states_per_eV_cell']=interp(rows,key,0.0)
            row[key+'_window_weight_states_per_cell']=integrate(rows,key)
        out.append(row)
    return out


def read_crossings(root):
    # The .gnu energies are eV; use the parent SCF Fermi energy of this historical chain.
    text=(root/'scf/pwx.out').read_text()
    ef=float(re.findall(r'the Fermi energy is\s+([-+0-9.]+)',text)[-1])
    raw=[tuple(map(float,l.split())) for l in (root/'scf/bands.dat.gnu').read_text().splitlines() if l.strip()]
    lines=[l for l in (root/'scf/fatbands.projwfc_up').read_text().splitlines() if l.strip()]
    heads=[i for i,l in enumerate(lines[:30]) if len(l.split())==3 and all(x.isdigit() for x in l.split())]
    if len(heads)!=1: raise ValueError('Projection header not unique')
    idx=heads[0];nw,nk,nb=map(int,lines[idx].split())
    if (nw,nk,nb)!=(45,151,31) or lines[idx+1].split()!=['F','F']: raise ValueError('Wrong model/spin shape')
    if len(raw)!=nk*nb: raise ValueError('Band shape mismatch')
    bands=[raw[b*nk:(b+1)*nk] for b in range(nb)]
    if any([x for x,e in b] != [x for x,e in bands[0]] for b in bands): raise ValueError('Path mismatch')
    elements={1:'Zr',2:'C',3:'Cl',4:'Cl',5:'Sc',6:'Sc'}
    channels={'Zr_d':(1,'D'),'Sc_d':(5,'D'),'C_p':(2,'P'),'Cl_p':(3,'P')}
    w={k:[[0.0]*nk for _ in range(nb)] for k in [*channels,'all_projectors']}
    ptr=idx+2
    for expected in range(1,nw+1):
        h=lines[ptr].split();ptr+=1
        sid,atom=int(h[0]),int(h[1]);el=h[2];orb=h[3].upper()
        if sid!=expected or elements.get(atom)!=el: raise ValueError('State identity mismatch')
        angular=[c for c in orb if c in 'SPDF']
        if len(angular)!=1: raise ValueError('Invalid orbital label')
        c={'Zr':'Zr_d','Sc':'Sc_d','C':'C_p','Cl':'Cl_p'}[el]
        selected=angular[0]==('D' if el in ['Zr','Sc'] else 'P')
        for ik in range(nk):
            for ib in range(nb):
                a,b,v=lines[ptr].split();ptr+=1;v=float(v)
                if (int(a),int(b))!=(ik+1,ib+1) or not math.isfinite(v) or v < -1e-6:
                    raise ValueError('Projection row mismatch')
                w['all_projectors'][ib][ik]+=v
                if selected:w[c][ib][ik]+=v
    if ptr!=len(lines):raise ValueError('Trailing projection data')
    # Sum is diagnostic only. No complement is identified as an interstitial orbital.
    crossings=[]
    for ib,band in enumerate(bands):
        for ik,((xa,ea),(xb,eb)) in enumerate(zip(band,band[1:])):
            a,b=ea-ef,eb-ef
            if a*b < 0:
                f=-a/(b-a)
                row={'band':ib+1,'left_k_index':ik+1,'right_k_index':ik+2,
                     'path_distance_tpiba':xa+(xb-xa)*f,'EF_eV':ef}
                for c,arr in w.items():row[c]=arr[ib][ik]*(1-f)+arr[ib][ik+1]*f
                crossings.append(row)
    diagnostic={'shape':[nw,nk,nb],'EF_eV':ef,'all_projector_sum_min':min(v for b in w['all_projectors'] for v in b),
                'all_projector_sum_max':max(v for b in w['all_projectors'] for v in b),
                'crossing_method':'Linear interpolation of adjacent path energy and weights; not a uniform BZ integral.'}
    return crossings,diagnostic


def write_csv(p, rows):
    if not rows: raise ValueError('No result rows')
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    a=argparse.ArgumentParser();a.add_argument('data_root',type=Path);a.add_argument('--output',type=Path,default=Path('near-fermi-results'))
    args=a.parse_args();frozen=read_frozen(args.data_root);cross,checks=read_crossings(args.data_root)
    args.output.mkdir(parents=True,exist_ok=True)
    write_csv(args.output/'frozen-window.csv',frozen);write_csv(args.output/'path-crossings.csv',cross)
    report={'frozen_window_eV':[-0.1,0.0],'frozen':frozen,'historical_path':checks,'crossings':cross,
            'definitions':'Window integral is broadened projected spectral weight. It is not charge transfer or carrier density. Frozen QE7.2 and historical QE7.1 path chains are analyzed separately.'}
    (args.output/'near-fermi.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Frozen cases:',len(frozen),'Path crossings:',len(cross))
    for r in frozen:
        print(r['state'], 'Sc2C D(EF)=',format(r['sc2c_pdos_at_EF_states_per_eV_cell'],'.6f'),
              'W[-0.1,0]=',format(r['sc2c_pdos_window_weight_states_per_cell'],'.6f'))
    for r in cross:print('Band',r['band'],'k bracket',r['left_k_index'],r['right_k_index'],
                         'Zr_d=',format(r['Zr_d'],'.6f'),'Sc_d=',format(r['Sc_d'],'.6f'))


if __name__=='__main__':main()
