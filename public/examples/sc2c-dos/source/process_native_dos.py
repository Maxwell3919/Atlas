"""Export one scalar, nonmagnetic QE DOS case from its actual XML and files."""
from pathlib import Path
import argparse
import csv
import math
import re
import xml.etree.ElementTree as ET

HA_EV = 27.211386245988
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--xml', type=Path, required=True)
parser.add_argument('--dos-input', type=Path, required=True)
parser.add_argument('--dos-data', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
root = ET.parse(args.xml).getroot()
for element in root.iter():
    element.tag = element.tag.split('}')[-1]
band_structure = root.find('./output/band_structure')
if band_structure is None:
    raise ValueError('Missing QE output band_structure')
for flag in ['lsda', 'noncolin', 'spinorbit']:
    element = band_structure.find(flag)
    if element is not None and element.text.strip().lower() in ['true', 't', '.true.']:
        raise ValueError('This scalar NM example does not implement spinor/LSDA export')
ef = float(band_structure.find('fermi_energy').text) * HA_EV
nelec = float(band_structure.find('nelec').text)
nbnd = int(band_structure.find('nbnd').text)
points = band_structure.findall('ks_energies')
if len(points) != int(band_structure.find('nks').text):
    raise ValueError('XML k-point count mismatch')

eigen_rows = []
weights = []
weighted_occupations = 0.0
for index, point in enumerate(points, start=1):
    kpoint = point.find('k_point')
    coordinates = [float(value) for value in kpoint.text.split()]
    weight = float(kpoint.attrib['weight'])
    energies = [float(value) * HA_EV for value in point.find('eigenvalues').text.split()]
    occupations = [float(value) for value in point.find('occupations').text.split()]
    if len(coordinates) != 3 or len(energies) != nbnd or len(occupations) != nbnd:
        raise ValueError('XML band/coordinate count mismatch')
    if weight <= 0 or not all(math.isfinite(v) for v in coordinates + energies + occupations + [weight]):
        raise ValueError('Invalid k-point data')
    weights.append(weight)
    weighted_occupations += weight * sum(occupations)
    for band, energy in enumerate(energies, start=1):
        eigen_rows.append([index, *coordinates, weight, band, energy, energy - ef])
if abs(sum(weights) - 2.0) > 1e-8 or abs(weighted_occupations - nelec) > 1e-6:
    raise ValueError('Scalar NM weight/electron conservation check failed')

namelist = args.dos_input.read_text()
def number(name):
    match = re.search(r'\b' + name + r'\s*=\s*([+\-\d.eEdD]+)', namelist, re.I)
    if match is None:
        raise ValueError('Missing DOS input field: ' + name)
    return float(match.group(1).replace('D', 'e').replace('d', 'e'))
emin, emax, step = number('Emin'), number('Emax'), number('DeltaE')
if step <= 0 or emax <= emin:
    raise ValueError('Invalid DOS energy window')
raw = []
for line in args.dos_data.read_text().splitlines():
    if not line.strip() or line.lstrip().startswith('#'):
        continue
    values = [float(value.replace('D', 'e')) for value in line.split()]
    if len(values) != 3 or not all(math.isfinite(v) for v in values):
        raise ValueError('Invalid native DOS row')
    raw.append(values)
if len(raw) != int(round((emax - emin) / step)) + 1:
    raise ValueError('Native DOS row count does not match this example window')
dos_rows = []
for index, (printed_energy, dos, cumulative) in enumerate(raw):
    exact_energy = emin + index * step
    if abs(printed_energy - exact_energy) > 0.00050001:
        raise ValueError('Native F8.3 energy serialization mismatch')
    dos_rows.append([printed_energy, printed_energy - ef, exact_energy,
                     exact_energy - ef, dos, cumulative])

args.output_dir.mkdir(parents=True, exist_ok=True)
def write_csv(name, fields, rows):
    with (args.output_dir / name).open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        writer.writerows(rows)
write_csv('dos_shifted.csv', ['native_printed_energy_eV_F8p3',
          'native_printed_energy_minus_own_EF_eV', 'exact_input_grid_energy_eV',
          'exact_input_grid_energy_minus_own_EF_eV',
          'DOS_states_per_eV_per_cell_spin_summed', 'native_window_cumulative_DOS_states'], dos_rows)
write_csv('eigenvalues_k16.csv', ['irreducible_k_index', 'kx_2pi_over_alat',
          'ky_2pi_over_alat', 'kz_2pi_over_alat', 'raw_QE_weight_including_spin',
          'band_index', 'energy_eV_raw', 'energy_minus_own_EF_eV'], eigen_rows)
print(f"Fermi energy: {ef:.12f} eV")
print(f"Electrons: {nelec:g}; bands: {nbnd}; irreducible k points: {len(points)}")
print(f"Spin-inclusive weight sum: {sum(weights):.12f}; weighted occupations: {weighted_occupations:.12f}")
print(f"Wrote {len(dos_rows)} DOS rows and {len(eigen_rows)} eigenvalue rows to {args.output_dir}")
print("DOS and window cumulative values retained; energies shifted by the XML Fermi energy.")
