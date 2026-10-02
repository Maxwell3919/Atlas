#!/usr/bin/env python3
"""Read archived QE7.5 Al files and expose q/mode contributions at one sigma.
Usage: python3 q_contributions.py k32 k48 --outdir ledger --sigma 0.020
Only the output directory is written; no QE executable is called.
"""
import argparse, csv, json, math, re
from pathlib import Path

NUMBER = r"[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?"
def number(value):
    return float(value.replace('D', 'E').replace('d', 'e'))

def read_branch(root, sigma):
    lines = [x.split('!')[0].strip() for x in (root/'lambda.in').read_text().splitlines()]
    lines = [x for x in lines if x]
    nq = int(lines[1])
    points = [list(map(number, x.split())) for x in lines[2:2+nq]]
    filenames = lines[2+nq:2+2*nq]
    weight_sum = sum(x[3] for x in points)
    assert nq == 8 and weight_sum == 64
    modes, qs, dos_values = [], [], []
    for iq, (point, filename) in enumerate(zip(points, filenames), 1):
        raw = (root/filename).read_text().splitlines()
        head = raw[0].split()
        assert max(abs(number(x)-y) for x,y in zip(head[:3], point[:3])) <= 5.005e-7
        nsig, nmodes = map(int, head[3:])
        assert nsig == 10 and nmodes == 3
        w2 = list(map(number, raw[1].split()))
        assert len(w2) == nmodes and min(w2) >= 0
        selected = []
        for isig in range(nsig):
            pos = 2 + isig*(nmodes+2)
            match = re.search(r'Gaussian Broadening:\s*('+NUMBER+r') Ry, ngauss=\s*(-?\d+)', raw[pos])
            if not math.isclose(number(match[1]), sigma, abs_tol=1e-12):
                continue
            assert int(match[2]) == 0
            dos = number(re.search(r'DOS =\s*('+NUMBER+r')', raw[pos+1])[1])
            dos_values.append(dos)
            for imode in range(nmodes):
                match = re.search(r'lambda\(\s*(\d+)\)=\s*('+NUMBER+r')\s*gamma=\s*('+NUMBER+r')', raw[pos+2+imode])
                assert int(match[1]) == imode+1
                lam, gamma = map(number, match.groups()[1:])
                row = dict(branch=root.name, sigma_Ry=sigma, q_index=iq,
                    mode=imode+1, qx=point[0], qy=point[1], qz=point[2],
                    star_weight=point[3], normalized_weight=point[3]/weight_sum,
                    frequency_THz_from_printed_w2=math.sqrt(w2[imode])*3289.828,
                    gamma_GHz=gamma, lambda_mode=lam,
                    weighted_lambda=lam*point[3]/weight_sum, source=filename)
                selected.append(row)
                modes.append(row)
        assert len(selected) == nmodes
        qs.append(dict(q_index=iq, star_weight=point[3],
            lambda_modes_sum=sum(x['lambda_mode'] for x in selected),
            weighted_lambda=sum(x['weighted_lambda'] for x in selected)))
    assert len(set(dos_values)) == 1 and len(modes) == 24
    total = sum(x['weighted_lambda'] for x in qs)
    native = re.findall(r'lambda\s*=\s*('+NUMBER+r')\s*\(\s*('+NUMBER+r')\s*\)\s*<log w>=\s*('+NUMBER+r')\s*K\s*N\(Ef\)=\s*('+NUMBER+r')\s*at degauss=\s*('+NUMBER+r')', (root/'lambda.out').read_text())
    selected_native = [list(map(number,x)) for x in native if math.isclose(number(x[-1]),sigma,abs_tol=1e-12)]
    assert len(selected_native) == 1 and abs(selected_native[0][0]-total) <= 0.500001e-6
    for q in qs:
        q['share_percent'] = 100*q['weighted_lambda']/total
    return modes, dict(branch=root.name, sigma_Ry=sigma, q_weight_sum=weight_sum,
        lambda_qsum=total, native_printed_lambda_qsum=selected_native[0][0],
        native_printed_lambda_spectrum=selected_native[0][1],
        N_EF_states_per_spin_Ry_cell=dos_values[0], q_contributions=qs,
        frequency_note='QE7.5 lambda.x constant 3289.828 THz/Ry and printed w2; not recovery of unprinted phonon precision',
        no_QE_executable_run=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('branches', nargs='+', type=Path)
    parser.add_argument('--sigma', type=float, default=0.020)
    parser.add_argument('--outdir', type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    for branch in args.branches:
        modes, summary = read_branch(branch, args.sigma)
        with (args.outdir/(branch.name+'-mode-contributions.csv')).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(modes[0]))
            writer.writeheader(); writer.writerows(modes)
        (args.outdir/(branch.name+'-q-contributions.json')).write_text(json.dumps(summary, indent=2)+'\n')
        print(f"{branch.name}: sigma={args.sigma:.3f} Ry; 24 modes; weight sum=64; lambda_qsum={summary['lambda_qsum']:.10f}; native rounding matched")
if __name__ == '__main__':
    main()
