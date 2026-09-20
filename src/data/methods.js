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
export const categories = [
  { id: 'basics',    name: '基础',     order: ['convergence', 'relax', 'vc-relax', 'scf', 'nscf'] },
  { id: 'stability', name: '稳定',     order: ['phonon-dfpt', 'phonon-finite-disp', 'elastic-born', 'aimd'] },
  { id: 'electronic', name: '电子',    order: ['bands', 'dos', 'fatband', 'fermi-surface'] },
  { id: 'charge',    name: '电荷',     order: ['delta-charge', 'bader', 'elf'] },
  { id: 'supercon',  name: '超导',     order: ['wannier90', 'epc'] },
  { id: 'interface-magnet', name: '界面与磁', order: ['workfunction', 'band-alignment', 'magnetic-gs', 'dft-plus-u'] },
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

  'bands': {
    zh: '能带',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['能带图'],
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
