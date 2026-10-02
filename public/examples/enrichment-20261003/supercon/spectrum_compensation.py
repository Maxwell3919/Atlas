#!/usr/bin/env python3
"""Resolve signed spectral differences into cumulative gains/losses, no plotting.
Example: python3 spectrum_compensation.py --a k32/alpha2F.dat --b k48/alpha2F.dat --outdir compensation
The archived, printed spectra are read without smoothing or rescaling.
"""
import argparse, csv, json, math
from pathlib import Path

def read(path):
    lines=path.read_text().splitlines()
    header=lines[0].split()[1:]
    assert header[0]=='E(THz)' and header[2]=='0.010'
    values=[[float(x) for x in line.split()] for line in lines[1:] if line.strip()]
    assert len(values)==2000 and all(len(row)==11 for row in values)
    assert all(math.isfinite(x) for row in values for x in row)
    assert values[0][0]==0 and values[0][2]==0 and values[-1][0]==14
    assert all(row[2]>=0 for row in values)
    assert all(b[0]>a[0] for a,b in zip(values,values[1:]))
    return values

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--a', required=True, type=Path)
    parser.add_argument('--b', required=True, type=Path)
    parser.add_argument('--outdir', required=True, type=Path)
    args=parser.parse_args()
    a,b=read(args.a),read(args.b)
    assert all(x[0]==y[0] for x,y in zip(a,b))
    rows=[]; gain=loss=0.; previous=(0.,0.,0.)
    for x,y in zip(a,b):
        f=x[0]
        density=2*(x[2]-y[2])/f if f else 0.
        positive,negative=max(density,0.),max(-density,0.)
        if rows:
            step=f-previous[0]
            gain+=step*(positive+previous[1])/2
            loss+=step*(negative+previous[2])/2
        rows.append(dict(frequency_THz=f,alpha2F_k32=x[2],alpha2F_k48=y[2],
            signed_difference_density_per_THz=density,
            cumulative_positive=gain,cumulative_negative_magnitude=loss,
            cumulative_signed=gain-loss,cumulative_absolute=gain+loss))
        previous=(f,positive,negative)
    assert abs(gain-loss-0.00006931533193377)<1e-12
    assert abs(gain+loss-0.06503158600520108)<1e-12
    args.outdir.mkdir(parents=True,exist_ok=True)
    with (args.outdir/'al-sigma010-compensation.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary=dict(source_files=[str(args.a),str(args.b)],sigma_Ry=.01,
        rows=len(rows),frequency_unit='THz',method='trapezoid on original printed frequency rows; positive and negative parts clipped at sample values before integration',
        cumulative_positive=gain,cumulative_negative_magnitude=loss,
        cumulative_signed=gain-loss,cumulative_absolute=gain+loss,
        source_spectrum_width_THz=.12,response_k='16^3',DFPT_q='4^3',
        smoothing=False,rescaling=False,no_QE_executable_run=True)
    (args.outdir/'al-sigma010-compensation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'2000 paired points; gain={gain:.10f}; loss={loss:.10f}; net={gain-loss:.10f}; L1={gain+loss:.10f}')
if __name__=='__main__':
    main()
