Read existing data: python3 analyze_relax.py
Inputs, final structure, OUTCAR, OSZICAR, original stdout, run-script template and numerical postprocessing are included.
POTCAR and density/wavefunction files are not supplied. Prepare POTCAR from your licensed library if rerunning.
OUTCAR PAW startup detail echo was removed; the numerical tail from Dimension of arrays onward is unchanged. script_std preserves the recorded oneAPI and VASP installation paths; use vi to adapt them to your host. No VASP calculation was run during preparation; the Python postprocessing was executed on the archived records.
