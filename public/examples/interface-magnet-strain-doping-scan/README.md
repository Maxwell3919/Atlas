# strain-doping-scan: reproducible existing-output analysis

Extract the archive and enter example-pack. Environment: Python 3 standard library; plotting additionally requires NumPy and Matplotlib.

```bash
python3 analyse_strain.py
python3 plot_strain.py
```

Inputs and original outputs are retained unchanged. POTCAR payload is excluded; safe PAW identity/hash records substitute in parser checks. No DFT executable is invoked by these commands. The article defines the energy/density/geometry scope. SOURCE evidence and earlier plots remain separately in the Talos provenance tree.
