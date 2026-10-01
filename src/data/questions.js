export const calculationQuestions = [
  { id: 'structure', title: '怎样得到后续计算能用的结构？', detail: '从原子力、晶胞压力和数值参数开始。', methods: ['scf', 'convergence', 'relax', 'vc-relax'] },
  { id: 'energy', title: '比较能量时，该选什么参考？', detail: '配齐比较对象，再算形成、吸附和分离的能量。', methods: ['formation-energy', 'convex-hull', 'adsorption-energy', 'exfoliation-energy'] },
  { id: 'phonon', title: '声子负频来自哪里？', detail: '读动力学矩阵、原子位移和不同条件下的频率。', methods: ['phonon-dfpt', 'phonon-finite-disp', 'imaginary-phonon', 'phdos', 'aimd', 'mlip-md', 'temperature-effective-fc'] },
  { id: 'mechanics', title: '结构受力后会怎样变形？', detail: '给出小应变，比较能量、应力和弹性响应。', methods: ['elastic-born', 'elastic-moduli', 'strain-doping-scan'] },
  { id: 'electronic', title: '带边、轨道和费米面在哪里？', detail: '从能带与态密度，继续读有效质量、输运与拓扑。', methods: ['nscf', 'dft-plus-u', 'bands', 'band-gap', 'dos', 'fatband', 'band-3d', 'band-unfolding', 'fermi-surface', 'fermi-nesting', 'effective-mass', 'spin-texture', 'wannier90', 'berry-chern', 'carrier-mobility'] },
  { id: 'charge', title: '电荷怎样转移，原子怎样成键？', detail: '把密度、原子电荷与成键分析放在一起比较。', methods: ['delta-charge', 'bader', 'elf', 'electrostatic-potential', 'cohp', 'population-analysis'] },
  { id: 'interface', title: '两层的能级怎样放到同一参考？', detail: '建模、读取真空电势，再检查能级的参考。', methods: ['workfunction', 'band-alignment', 'heterostructure-modeling'] },
  { id: 'magnet', title: '哪种磁排列更稳定？', detail: '比较磁排列、方向和相应的能量差。', methods: ['magnetic-gs', 'dft-plus-u', 'mae', 'exchange-j'] },
  { id: 'supercon', title: '怎样从电子–声子耦合得到 Tc？', detail: '核对电子与声子网格，再从 λ、ωlog 读到 Tc。', methods: ['epc', 'eliashberg-a2f', 'allen-dynes', 'epw-eliashberg', 'phonon-linewidth'] },
];
