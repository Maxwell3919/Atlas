# magnetic-gs: reproducible existing-output analysis

Extract the archive and enter example-pack. Environment: Python 3 standard library.

```bash
python3 magnetic_energies.py
python3 export_magnetic_table.py
```

Inputs and original outputs are retained unchanged. POTCAR payload is excluded; safe PAW identity/hash records substitute in parser checks. No DFT executable is invoked by these commands. The article defines the energy/density/geometry scope. SOURCE evidence and earlier plots remain separately in the Talos provenance tree.
