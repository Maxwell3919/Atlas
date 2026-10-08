# Derived toy-model contract

Candidate, not integrated or published; original HTML remains unlocated. Original files and private sources were not searched. No material identity or space group is assigned.

The primary symmetry reference is Šmejkal, Sinova and Jungwirth, PRX12 031042 (2022), DOI10.1103/PhysRevX.12.031042, especially pp1–3 on collinear compensated order and opposite-spin sublattices related by crystal rotations rather than inversion/translation. PRX12 040501 (2022), DOI10.1103/PhysRevX.12.040501, supplies context for even-parity d-wave and higher angular forms. Verified publisher primary pages and first-paper PDF; both CC BY4.0. No paper text, figures or author example code is copied. No official author downloadable example was adopted; this is a new derived pedagogical implementation.

Assumptions: periodic 2D square reciprocal domain; a conserved spin-z label; neglect spin-orbit coupling; prescribe equal opposite collinear local moments A:+M, B:−M as a background only. No self-consistent order or microscopic sublattice Hamiltonian. Such a cartoon alone is insufficient to identify altermagnetism: actual crystal potentials and sublattice-related spin-group operations must be established for a material.

Define H=epsilon I+Delta sigma_z, epsilon=-2t(cos kx+cos ky), Delta=J(cos kx-cos ky), t=1 arbitrary E0. This cosine basis is our periodic B1g choice, not a quoted material Hamiltonian. Near Gamma Delta≈J(ky²-kx²)/2. Its nodal lines satisfy cos kx=cos ky, and its full spin splitting is 2Delta.

Direct algebra: inversion leaves epsilon and Delta unchanged. C4:(kx,ky)->(-ky,kx) preserves epsilon and reverses Delta, exchanging spin branches. At J=0 branches coincide. Flipping J exchanges branches. For fixed nonzero J, the conventional spin time-reversal condition E_up(k)=E_down(-k) fails away from nodes; even-k parity alone is not time reversal. A C4 operation combined with spin exchange is an effective-model symmetry; no physical crystal space group is inferred.

Grid N=64 fixed, ix,iy=0..63, ki=-pi+2pi(i+.5)/N; uniform weight1/4096, no repeated endpoints, no interpolation. C4 permutes (ix,iy)->(N-1-iy,ix). J/E0 in[-1,1] step.05; common mu/E0 in[-4,4] step.1. Theta=.05E0 is solely an occupation smoothing scale, not a measured temperature. f_sigma=.5[1-tanh((E_sigma-mu)/(2theta))]. Grid-averaged Delta and f_up-f_down vanish by C4 pairing. Vanishing Delta average alone would not imply equal populations without the shared epsilon/C4 relation. These occupancy statements do not prove prescribed local-moment compensation or physical magnetic order. Diagonal Hamiltonian uses sigma as conserved spin label; J is a phenomenological amplitude, not a fitted exchange constant.

Plots: sign heat map uses fixed Delta/E0 range[-2,2]; discrete energy-shell samples obey |E_sigma-mu|<=.08E0. Neither exact continuum contours nor material Fermi surfaces. CSV exports 4096 analytically evaluated rows plus current parameters/units/model/disclaimer; PNG includes same model/units/current parameters and disclaimer. Default data J=.6,mu=.5. No transport, SOC, DFT, interpolation or scientific acceptance.

Independent stdlib script: `python3 consistency.py --output-dir <own-output>`; fixed analytic point (0,pi):epsilon0,Delta2J; inversion, C4 spin swap, nodal degeneracy, J0, J sign, C4 grid permutation and population compensation; absolute tolerance2e-13. Observed results in analytic-results.json. Later reviewers must independently assess science binding and page readability; code is not evidence of a material result.

Integration only by the existing unique website author after separate science and reader review. Preserve original HTML bounded absence and all external HOLD/owner/job states.
