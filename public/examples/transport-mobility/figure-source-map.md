# Curves, data and literature

## Curves from this example

- transport-deformation-fits: cases.csv gives strain, total energy and vacuum-aligned K conduction edge. summary.json gives quadratic elastic and linear deformation-potential fits. The solid curves fit the baseline five strain samples. Dashed lines connect the denser-k and thicker-vacuum three-point samples; each group subtracts its own zero-strain energy.
- transport-effective-mass-windows: valley-bands.csv gives local K dispersion and mass-windows.csv gives three Hessian fits, masses and residuals. Local k offsets are in inverse Angstrom; md uses the Hessian determinant, including Hxy. The x/y dispersion panels show one-dimensional Cartesian sections and their own quadratic guides; all masses in the window panel come from full two-dimensional fits.
- transport-vacuum-and-valleys: potential-profiles.csv and cases.csv give planar potentials and sampled competing valleys. The article uses numerical tolerances to read small plateau and valley differences.
- plot_mobility.py generates the saved PNG/SVG/PDF files from these tables. analyse_mobility.py reconstructs the underlying numerical tables.

## Literature and physical questions

Sohier, Calandra and Mauri, Physical Review B 94, 085415 (2016), https://doi.org/10.1103/PhysRevB.94.085415:
- Figure 1 locates long-wavelength optical modes.
- Figure 2 compares mode-resolved electron-phonon matrix elements in bulk and isolated monolayer MoS2.
- Figure 7 connects those matrix elements and phonon frequencies to optical-mode inverse relaxation times at room temperature.

These require DFPT phonon and coupling data. This example's strain and dispersion fits supply acoustic deformation-potential parameters; no literature figure or numerical dataset is reproduced in the package.

Kaasbjerg et al., Physical Review B 85, 115317 (2012), https://arxiv.org/abs/1201.5284, provides the full-phonon MoS2 transport context. The longitudinal acoustic model conditions are stated in the article and provenance.json.
