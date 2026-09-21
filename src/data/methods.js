// Atlas — DFT 计算方法手册 · 单一数据源
// slug 保持英文；zh 为页面显示中文名；needs/produces 驱动各引擎页「提及栏」。
// engines：该方法当前提供页面、可点击进入的引擎 id（对应路由 /m/<slug>/<id>/）。
// placeholderEngines：尚未接入的引擎显示名，只在方法页渲染为不可点的
// 「未接入」徽标，不生成任何路由；未来接入新引擎时在此做纯数据修改即可。

export const engines = [
  { id: 'qe', name: 'Quantum ESPRESSO' },
  { id: 'vasp', name: 'VASP' },
];

// 分类与类内展示顺序（目录页与全部索引的唯一顺序来源）
// subtitle 仅存档；现有各组标题均为纯文本，各组保持同构，不渲染。
export const categories = [
  { id: 'basics',    name: '基础',     order: ['convergence', 'relax', 'vc-relax', 'scf', 'nscf'] },
  { id: 'thermo',    name: '结构与热力学', subtitle: '这个相在能量上站得住吗？', order: ['formation-energy', 'convex-hull', 'exfoliation-energy', 'adsorption-energy'] },
  { id: 'stability', name: '稳定',     order: ['phonon-dfpt', 'phonon-finite-disp', 'imaginary-phonon', 'elastic-born', 'aimd', 'phdos', 'elastic-moduli', 'mlip-md', 'anharmonic-sscha'] },
  { id: 'electronic', name: '电子',    order: ['bands', 'band-gap', 'band-3d', 'band-unfolding', 'dos', 'fatband', 'fermi-surface', 'spin-texture', 'electrostatic-potential', 'fermi-nesting', 'effective-mass'] },
  { id: 'charge',    name: '电荷',     order: ['delta-charge', 'bader', 'elf', 'cohp', 'population-analysis'] },
  { id: 'supercon',  name: '超导',     order: ['wannier90', 'epc', 'eliashberg-a2f', 'allen-dynes', 'phonon-linewidth', 'bkt-scaling'] },
  { id: 'interface-magnet', name: '界面与磁', order: ['workfunction', 'band-alignment', 'magnetic-gs', 'dft-plus-u', 'mae', 'exchange-j', 'strain-doping-scan', 'heterostructure-modeling'] },
  { id: 'topo',      name: '拓扑',     subtitle: '有没有边缘态？', order: ['berry-chern'] },
  { id: 'transport', name: '输运',     subtitle: '迁移率多高？', order: ['carrier-mobility'] },
];

export const methods = {
  'convergence': {
    zh: '收敛测试',
    category: 'basics',
    needs: [],
    produces: ['收敛参数结论'],
    engines: ['qe', 'vasp'],
  },
  'relax': {
    zh: '离子弛豫',
    category: 'basics',
    needs: ['convergence'],
    produces: ['优化后结构'],
    engines: ['qe', 'vasp'],
    placeholderEngines: ['MACE'],
  },
  'vc-relax': {
    zh: '晶胞弛豫',
    category: 'basics',
    needs: ['convergence'],
    produces: ['优化晶胞与结构'],
    engines: ['qe', 'vasp'],
    placeholderEngines: ['MACE'],
  },
  'scf': {
    zh: '电子自洽 SCF',
    category: 'basics',
    needs: ['convergence', 'relax', 'vc-relax'],
    produces: ['电荷密度'],
    engines: ['qe', 'vasp'],
  },
  'nscf': {
    zh: '非自洽 NSCF',
    category: 'basics',
    needs: ['scf'],
    produces: ['固定电荷下的本征值'],
    engines: ['qe', 'vasp'],
  },

  'formation-energy': {
    zh: '形成能 / 内聚能',
    category: 'thermo',
    needs: ['relax'],
    produces: ['形成能 / 凸包距离'],
    engines: ['qe', 'vasp'],
  },
  'convex-hull': {
    zh: '凸包相图 / Energy-above-hull',
    category: 'thermo',
    needs: ['formation-energy'],
    produces: ['凸包距离 / 相稳定性判定'],
    engines: ['qe', 'vasp'],
  },
  'exfoliation-energy': {
    zh: '剥离能 / 解理能',
    category: 'thermo',
    needs: ['relax'],
    produces: ['剥离能 / 解理能'],
    engines: ['qe', 'vasp'],
  },
  'adsorption-energy': {
    zh: '吸附能 / 界面结合能',
    category: 'thermo',
    needs: ['relax'],
    produces: ['吸附能 / 界面结合能'],
    engines: ['qe', 'vasp'],
  },

  'phonon-dfpt': {
    zh: 'DFPT 声子',
    category: 'stability',
    needs: ['scf'],
    produces: ['声子谱'],
    engines: ['qe', 'vasp'],
  },
  'phonon-finite-disp': {
    zh: '有限位移声子',
    category: 'stability',
    needs: ['scf'],
    produces: ['力常数与声子谱'],
    engines: ['qe', 'vasp'],
  },
  'imaginary-phonon': {
    zh: '虚频 / 软模判据',
    category: 'stability',
    needs: ['phonon-dfpt', 'phonon-finite-disp'],
    produces: ['无虚频判定 / 软模指认'],
    engines: ['qe', 'vasp'],
  },
  'elastic-born': {
    zh: '弹性常数与 Born 判据',
    category: 'stability',
    needs: ['vc-relax'],
    produces: ['弹性常数与 Born 有效电荷'],
    engines: ['qe', 'vasp'],
  },
  'aimd': {
    zh: '短时 AIMD',
    category: 'stability',
    needs: ['vc-relax'],
    produces: ['短时 MD 轨迹'],
    engines: ['qe', 'vasp'],
    placeholderEngines: ['MACE'],
  },
  'phdos': {
    zh: '声子态密度 PHDOS',
    category: 'stability',
    needs: ['phonon-dfpt', 'phonon-finite-disp'],
    produces: ['声子态密度 / 投影声子'],
    engines: ['qe', 'vasp'],
  },
  'elastic-moduli': {
    zh: '弹性模量 / 泊松比',
    category: 'stability',
    needs: ['elastic-born'],
    produces: ['弹性模量 / 泊松比'],
    engines: ['qe', 'vasp'],
  },
  'mlip-md': {
    zh: '机器学习势 MD',
    category: 'stability',
    needs: ['relax'],
    produces: ['MLIP 分子动力学轨迹'],
    engines: ['qe', 'vasp'],
  },
  'anharmonic-sscha': {
    zh: '非谐效应 / SSCHA / TDEP',
    category: 'stability',
    needs: ['phonon-dfpt'],
    produces: ['温度重整化声子 / 非谐自由能'],
    engines: ['qe', 'vasp'],
  },

  'bands': {
    zh: '能带',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['能带图'],
    engines: ['qe', 'vasp'],
  },
  'band-gap': {
    zh: '带隙（直接 / 间接）',
    category: 'electronic',
    needs: ['bands'],
    produces: ['直接 / 间接带隙'],
    engines: ['qe', 'vasp'],
  },
  'band-3d': {
    zh: '3D 能带',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['3D 能带 E(kx,ky) 面'],
    engines: ['qe', 'vasp'],
  },
  'band-unfolding': {
    zh: '能带反折叠',
    category: 'electronic',
    needs: ['bands'],
    produces: ['原胞 BZ 能带 / 光谱权重'],
    engines: ['qe', 'vasp'],
  },
  'dos': {
    zh: '态密度 DOS / PDOS',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['DOS/PDOS'],
    engines: ['qe', 'vasp'],
  },
  'fatband': {
    zh: '投影能带 / 胖带',
    category: 'electronic',
    needs: ['bands', 'dos'],
    produces: ['投影能带'],
    engines: ['qe', 'vasp'],
  },
  'fermi-surface': {
    zh: '费米面',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['费米面'],
    engines: ['qe', 'vasp'],
  },
  'spin-texture': {
    zh: '自旋纹理 / Rashba / Ising',
    category: 'electronic',
    needs: ['bands'],
    produces: ['自旋纹理图'],
    engines: ['qe', 'vasp'],
  },
  'electrostatic-potential': {
    zh: '静电势 / 平面平均电势',
    category: 'electronic',
    needs: ['scf'],
    produces: ['平面平均静电势 / 电势阶跃'],
    engines: ['qe', 'vasp'],
  },
  'fermi-nesting': {
    zh: '费米面嵌套 / Lifshitz',
    category: 'electronic',
    needs: ['fermi-surface'],
    produces: ['嵌套函数 / χ(q)'],
    engines: ['qe', 'vasp'],
  },
  'effective-mass': {
    zh: '有效质量',
    category: 'electronic',
    needs: ['bands'],
    produces: ['有效质量 m*'],
    engines: ['qe', 'vasp'],
  },

  'delta-charge': {
    zh: '差分电荷',
    category: 'charge',
    needs: ['scf'],
    produces: ['差分电荷密度'],
    engines: ['qe', 'vasp'],
  },
  'bader': {
    zh: 'Bader 电荷',
    category: 'charge',
    needs: ['scf'],
    produces: ['Bader 电荷'],
    engines: ['qe', 'vasp'],
  },
  'elf': {
    zh: 'ELF',
    category: 'charge',
    needs: ['scf'],
    produces: ['ELF 图'],
    engines: ['qe', 'vasp'],
  },
  'cohp': {
    zh: 'COHP / ICOHP（LOBSTER）',
    category: 'charge',
    needs: ['scf'],
    produces: ['COHP / ICOHP 成键分析'],
    engines: ['qe', 'vasp'],
  },
  'population-analysis': {
    zh: '布居分析',
    category: 'charge',
    needs: ['scf'],
    produces: ['原子 / 轨道布居'],
    engines: ['qe', 'vasp'],
  },

  'wannier90': {
    zh: 'Wannier90',
    category: 'supercon',
    needs: ['scf'],
    produces: ['最大局域化 Wannier 函数'],
    engines: ['qe', 'vasp'],
  },
  'epc': {
    zh: '电声耦合 EPC',
    category: 'supercon',
    needs: ['wannier90', 'phonon-dfpt', 'phonon-finite-disp'],
    produces: ['λ / α²F / Tc'],
    engines: ['qe', 'vasp'],
  },
  'eliashberg-a2f': {
    zh: 'Eliashberg 谱函数 α²F',
    category: 'supercon',
    needs: ['epc'],
    produces: ['α²F(ω) / λ(ω)'],
    engines: ['qe', 'vasp'],
  },
  'allen-dynes': {
    zh: 'Allen–Dynes / McMillan',
    category: 'supercon',
    needs: ['eliashberg-a2f'],
    produces: ['Tc 估算'],
    engines: ['qe', 'vasp'],
  },
  'phonon-linewidth': {
    zh: '声子线宽',
    category: 'supercon',
    needs: ['epc'],
    produces: ['声子线宽 γ_qν / 散射热点'],
    engines: ['qe', 'vasp'],
  },
  'bkt-scaling': {
    zh: 'Ginzburg–Landau / BKT',
    category: 'supercon',
    needs: ['epc'],
    produces: ['BKT 转变 / 标度分析'],
    engines: ['qe', 'vasp'],
  },

  'workfunction': {
    zh: '功函数',
    category: 'interface-magnet',
    needs: ['scf'],
    produces: ['功函数'],
    engines: ['qe', 'vasp'],
  },
  'band-alignment': {
    zh: '能带对齐',
    category: 'interface-magnet',
    needs: ['bands', 'workfunction'],
    produces: ['能带对齐图'],
    engines: ['qe', 'vasp'],
  },
  'magnetic-gs': {
    zh: '磁基态',
    category: 'interface-magnet',
    needs: ['relax', 'vc-relax', 'scf'],
    produces: ['FM/AFM/NM 能量比较'],
    engines: ['qe', 'vasp'],
  },
  'dft-plus-u': {
    zh: 'DFT+U',
    category: 'interface-magnet',
    needs: ['scf'],
    produces: ['U 修正后的结果'],
    engines: ['qe', 'vasp'],
  },
  'mae': {
    zh: '磁各向异性能 MAE',
    category: 'interface-magnet',
    needs: ['magnetic-gs'],
    produces: ['磁各向异性能'],
    engines: ['qe', 'vasp'],
  },
  'exchange-j': {
    zh: '磁交换耦合 J',
    category: 'interface-magnet',
    needs: ['magnetic-gs'],
    produces: ['交换参数 J'],
    engines: ['qe', 'vasp'],
  },
  'strain-doping-scan': {
    zh: '应变 / 掺杂调控扫描',
    category: 'interface-magnet',
    needs: ['vc-relax'],
    produces: ['性质随应变 / 掺杂的扫描'],
    engines: ['qe', 'vasp'],
  },
  'heterostructure-modeling': {
    zh: '异质结 / 莫尔建模',
    category: 'interface-magnet',
    needs: ['convergence'],
    produces: ['异质结 / 莫尔超晶格模型'],
    engines: ['qe', 'vasp'],
  },

  'berry-chern': {
    zh: 'Berry 曲率 / 陈数 / ℤ₂',
    category: 'topo',
    needs: ['wannier90'],
    produces: ['Berry 曲率 / 陈数 / ℤ₂'],
    engines: ['qe', 'vasp'],
  },

  'carrier-mobility': {
    zh: '载流子迁移率',
    category: 'transport',
    needs: ['bands'],
    produces: ['迁移率 / 弛豫时间'],
    engines: ['qe', 'vasp'],
  },
};

// 展开成扁平列表（getStaticPaths 用）
export function methodList() {
  return categories.flatMap((c) =>
    c.order.map((slug) => ({ slug, ...methods[slug] }))
  );
}

// BASE_URL 规范化：去掉结尾斜杠，方便拼接
export function normalizeBase(raw) {
  return raw.endsWith('/') ? raw.slice(0, -1) : raw;
}
