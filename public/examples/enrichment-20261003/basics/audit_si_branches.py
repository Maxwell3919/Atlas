#!/usr/bin/env python3
"""Read this Si archive's OUT/XML; do not submit jobs or inspect remote save data."""
import argparse
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

CASES = [('scf', 'scf.out'), ('gap24-cg', 'nscf.out'), ('bands-cg', 'bands.out')]

def numbers(text):
    values = [float(x) for x in text.split()]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Non-finite XML numbers')
    return tuple(round(x, 11) for x in values)

def read_case(root, name, outname):
    x = ET.parse(root / name / 'data-file-schema.xml').getroot()
    b = x.find('output/band_structure')
    ks = b.findall('ks_energies')
    nbnd, nks = int(b.findtext('nbnd')), int(b.findtext('nks'))
    if len(ks) != nks or any(len(numbers(k.findtext('eigenvalues'))) != nbnd for k in ks):
        raise ValueError(f'{name}: XML counts/eigenvalues disagree')
    g = x.find('output/atomic_structure')
    species = [(s.attrib['name'], s.findtext('pseudo_file'))
               for s in x.findall('input/atomic_species/species')]
    model = [x.findtext('input/dft/functional'), species,
             [x.findtext('input/spin/' + tag) for tag in ('lsda', 'noncolin', 'spinorbit')],
             [x.findtext('input/basis/' + tag) for tag in ('ecutwfc', 'ecutrho')],
             [(q.tag, numbers(q.text)) for q in g.find('cell')],
             [(q.attrib['name'], numbers(q.text)) for q in g.find('atomic_positions')]]
    out = (root / name / outname).read_text()
    report = dict(calculation=x.findtext('input/control_variables/calculation'),
                  nks=nks, nbnd=nbnd, nelec=float(b.findtext('nelec')),
                  xml_exit_status=int(x.findtext('exit_status')),
                  job_done='JOB DONE.' in out,
                  eigenvalue_warning_lines=len(re.findall(r'c_bands:.*not converged', out)))
    return report, model

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path, help='the extracted si-pbe directory')
    p.add_argument('--json', type=Path, help='optional report destination')
    args = p.parse_args()
    rows, models = {}, []
    for name, outname in CASES:
        rows[name], model = read_case(args.root, name, outname)
        models.append(model)
        q = rows[name]
        print(f"{name}: calculation={q['calculation']} nks={q['nks']} nbnd={q['nbnd']} "
              f"nelec={q['nelec']:g} xml_exit={q['xml_exit_status']} "
              f"JOB_DONE={q['job_done']} eigenvalue_warning_lines={q['eigenvalue_warning_lines']}")
    same = all(m == models[0] for m in models[1:])
    saved = (args.root / 'scf/tmp/si.save').is_dir()
    print(f'same_geometry_and_model={same}; scf_save_directory_in_archive={saved}')
    result = dict(cases=rows, same_geometry_and_model=same,
                  scf_save_directory_in_archive=saved,
                  boundary='XML/OUT consistency only; no proof of saved density identity or target convergence')
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + '\n')
    if not same:
        raise ValueError('Geometry or selected physical-model fields differ')

if __name__ == '__main__':
    main()
