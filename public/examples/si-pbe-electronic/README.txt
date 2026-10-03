si-pbe electronic postprocessing example

Python 3; dependencies: NumPy, Matplotlib.
Data extraction checked on Talos using Python 3.12.3 and NumPy 2.4.6. Existing figures are retained; no figure regenerated in this packaging step.

Fixed Si PBE cell, no SOC. Original inputs, outputs, XML and data for electronic results. Recalculating QE eigenstates requires the matching parent SCF density.

From the extracted si-pbe directory:
python3 analyse_electronic.py
python3 analyse_mass_checks.py
python3 plot_bands.py
python3 plot_si.py dos
python3 plot_si.py fatband
python3 plot_si.py gap
python3 plot_si.py mass
python3 plot_si.py band3d

No original QE save directory is included.
