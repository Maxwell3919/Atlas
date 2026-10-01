Read existing data: python3 analyze_nscf.py
Required files are scf/{INCAR,POSCAR,KPOINTS,OUTCAR,OSZICAR,CHGCAR,script_std}, dos/{INCAR,POSCAR,KPOINTS,OUTCAR,OSZICAR,EIGENVAL,DOSCAR,script_std}, potcar-metadata.json, scripts and results.
POTCAR is not supplied. Prepare it from your licensed library. The parent CHGCAR is supplied once; use a new rerun directory if reusing it.
OUTCAR PAW startup detail echo was removed; the numerical tail from Dimension of arrays onward is unchanged. script_std preserves the recorded oneAPI and VASP installation paths; use vi to adapt them to your host. No VASP calculation was run during preparation; the Python postprocessing was executed on the archived records.
