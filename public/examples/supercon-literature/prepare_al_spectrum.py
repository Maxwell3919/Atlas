#!/usr/bin/env python3
"""Prepare a saved Al k32/k48 spectrum comparison; no response calculation.

python3 prepare_al_spectrum.py --data-dir . --out .
Reads the original 2000-row alpha2F.dat of both independent Al chains.
Column 3 (1-based) is sigma=0.010 Ry. No smoothing or spectral normalization.
"""
from pathlib import Path
import argparse, csv, json, math

def load(path):
    lines=path.read_text().splitlines()
    assert lines[0].split()[3]=='0.010', lines[0]
    rows=[[float(x) for x in l.split()] for l in lines[1:] if l.strip()]
    assert len(rows)==2000 and all(len(r)==11 for r in rows)
    assert all(math.isfinite(x) for r in rows for x in r)
    frequency=[r[0] for r in rows]; spectrum=[r[2] for r in rows]
    assert frequency[0]==0 and spectrum[0]==0 and abs(frequency[-1]-14)<1e-8
    assert all(b>a for a,b in zip(frequency,frequency[1:]))
    assert min(spectrum)>=0
    integrand=[0 if f==0 else 2*a/f for f,a in zip(frequency,spectrum)]
    cumulative=[0.0]
    for i in range(1,len(rows)):
        cumulative.append(cumulative[-1]+(frequency[i]-frequency[i-1])*(integrand[i]+integrand[i-1])/2)
    return frequency,spectrum,cumulative

def main():
    parser=argparse.ArgumentParser()
    sources=parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('--data-dir',type=Path,help='Directory containing k32/ and k48/')
    sources.add_argument('--public-root',type=Path,help='Atlas public directory')
    parser.add_argument('--out',type=Path,default=Path('.'))
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    folder=args.data_dir if args.data_dir is not None else args.public_root/'examples/supercon-al-tc'
    x,a,c=load(folder/'k32/alpha2F.dat');y,b,d=load(folder/'k48/alpha2F.dat')
    assert x==y
    with (args.out/'al-sigma010-spectrum.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['frequency_THz','alpha2F_k32','alpha2F_k48','lambda_cumulative_k32','lambda_cumulative_k48'])
        writer.writerows(zip(x,a,b,c,d))
    difference=[0 if f==0 else 2*abs(aa-bb)/f for f,aa,bb in zip(x,a,b)]
    l1=sum((x[i]-x[i-1])*(difference[i]+difference[i-1])/2 for i in range(1,len(x)))
    summary={'source_files':['examples/supercon-al-tc/k32/alpha2F.dat','examples/supercon-al-tc/k48/alpha2F.dat'],
             'sigma_Ry':.010,'frequency_unit':'THz','alpha2F':'native lambda.x output convention, no rescaling',
             'lambda_integral':'2 integral alpha2F(f)/f df; trapezoid on original printed frequencies',
             'rows':len(x),'lambda_k32_printed_spectrum':c[-1],'lambda_k48_printed_spectrum':d[-1],
             'L1_lambda':l1,'L1_percent_of_mean_printed_spectrum':l1/((c[-1]+d[-1])/2)*100,
             'normalization':'none; cumulative lambda is dimensionless, separate panel',
             'notes':'This integrates five-decimal printed spectra. Native internal qsum/spec tables retain their own precision.'}
    (args.out/'al-sigma010-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
