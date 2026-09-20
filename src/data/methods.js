// Atlas — DFT 计算方法手册 · 单一数据源
// slug 保持英文；zh 为页面显示中文名；needs/produces 驱动各引擎页「提及栏」。

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
    diff: '本步不改结构，只回答「参数要多紧才算够用」；相邻的 relax / scf 则直接使用这些结论。',
  },
  'relax': {
    zh: '离子弛豫',
    category: 'basics',
    needs: ['convergence'],
    produces: ['优化后结构'],
    diff: '本步只动原子位置、不动晶胞；vc-relax 会连晶胞一起优化，scf 则完全不动结构。',
  },
  'vc-relax': {
    zh: '晶胞弛豫',
    category: 'basics',
    needs: ['convergence'],
    produces: ['优化晶胞与结构'],
    diff: '本步连晶胞一起优化；relax 只动离子，scf 只解电子、结构完全固定。',
  },
  'scf': {
    zh: '电子自洽 SCF',
    category: 'basics',
    needs: ['convergence', 'relax', 'vc-relax'],
    produces: ['电荷密度'],
    diff: '本步在固定结构上解电子基态；nscf 复用这里的电荷密度、只换 k 网格且不再自洽迭代。',
  },
  'nscf': {
    zh: '非自洽 NSCF',
    category: 'basics',
    needs: ['scf'],
    produces: ['固定电荷下的本征值'],
    diff: '本步固定电荷密度，只在目标 k 网格上解本征值；与 scf 的差别是不再自洽迭代。',
  },

  'phonon-dfpt': {
    zh: 'DFPT 声子',
    category: 'stability',
    needs: ['scf'],
    produces: ['声子谱'],
    diff: '本步用密度泛函微扰在原胞直接得到力常数；有限位移法靠超胞位移差分，两条路线给出同一张声子谱。',
  },
  'phonon-finite-disp': {
    zh: '有限位移声子',
    category: 'stability',
    needs: ['scf'],
    produces: ['力常数与声子谱'],
    diff: '本步用超胞有限位移差分力常数；DFPT 在原胞直接算，对金属等小带隙体系更省事。',
  },
  'elastic-born': {
    zh: '弹性常数与 Born 判据',
    category: 'stability',
    needs: ['vc-relax'],
    produces: ['弹性常数与 Born 有效电荷'],
    diff: '本步问「晶胞被压缩或剪切时能量如何变化」，并用 Born 判据检查力学稳定性；相邻的声子步骤问的是振动，同样依赖弛豫好的晶胞。',
  },
  'aimd': {
    zh: '短时 AIMD',
    category: 'stability',
    needs: ['vc-relax'],
    produces: ['短时 MD 轨迹'],
    diff: '本步让原子带着有限温度跑起来，输出轨迹；relax 找的是 0 K 静态极小，只给单一构型。',
  },

  'bands': {
    zh: '能带',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['能带图'],
    diff: '本步沿高对称路径取 k 点画能带；dos 用稠密均匀网格，二者输入文件的差别基本只在 k 点设置。',
  },
  'dos': {
    zh: '态密度 DOS / PDOS',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['DOS/PDOS'],
    diff: '本步在稠密均匀 k 网格上积分态密度；能带沿路径取点，二者同源于 nscf 的本征值。',
  },
  'fatband': {
    zh: '投影能带 / 胖带',
    category: 'electronic',
    needs: ['bands', 'dos'],
    produces: ['投影能带'],
    diff: '本步在能带图上叠加轨道或原子投影；bands 只画能带本身，dos 给出积分视角。',
  },
  'fermi-surface': {
    zh: '费米面',
    category: 'electronic',
    needs: ['nscf'],
    produces: ['费米面'],
    diff: '本步在三维 k 空间切出费米面；bands 是一维路径视角，dos 是积分视角。',
  },

  'delta-charge': {
    zh: '差分电荷',
    category: 'charge',
    needs: ['scf'],
    produces: ['差分电荷密度'],
    diff: '本步比较两套电荷密度之差；bader 与 elf 都只分析单一密度，不做相减。',
  },
  'bader': {
    zh: 'Bader 电荷',
    category: 'charge',
    needs: ['scf'],
    produces: ['Bader 电荷'],
    diff: '本步把电荷密度按零通量面划分给各原子；差分电荷做相减，ELF 造标量场，三者输入同源。',
  },
  'elf': {
    zh: 'ELF',
    category: 'charge',
    needs: ['scf'],
    produces: ['ELF 图'],
    diff: '本步由电荷密度构造 ELF 标量场来看键合特征；bader 做体积分区，差分电荷做相减。',
  },

  'wannier90': {
    zh: 'Wannier90',
    category: 'supercon',
    needs: ['scf'],
    produces: ['最大局域化 Wannier 函数'],
    diff: '本步把 Bloch 态变换为最大局域化 Wannier 函数；上游 scf 只提供能带与重叠信息。',
  },
  'epc': {
    zh: '电声耦合 EPC',
    category: 'supercon',
    needs: ['wannier90', 'phonon-dfpt', 'phonon-finite-disp'],
    produces: ['λ / α²F / Tc'],
    diff: '本步把声子与 Wannier 插值的电子耦合起来算 λ；声子步骤与 Wannier 步骤各提供一半输入，两条声子路线（DFPT / 有限位移）二选一。',
    note: 'Allen–Dynes 公式写在本页后部（占位待补）。',
  },

  'workfunction': {
    zh: '功函数',
    category: 'interface-magnet',
    needs: ['scf'],
    produces: ['功函数'],
    diff: '本步沿真空方向看静电势台阶；普通 scf 分析体相性质，本步额外要求真空层与偶极修正。',
  },
  'band-alignment': {
    zh: '能带对齐',
    category: 'interface-magnet',
    needs: ['bands', 'workfunction'],
    produces: ['能带对齐图'],
    diff: '本步把两个体系的能带放到同一真空参考上；功函数步骤提供该参考，能带步骤提供带边位置。',
  },
  'magnetic-gs': {
    zh: '磁基态',
    category: 'interface-magnet',
    needs: ['relax', 'vc-relax', 'scf'],
    produces: ['FM/AFM/NM 能量比较'],
    diff: '本步比较 FM / AFM / NM 多种磁组态的能量；relax 与 scf 每次只处理单一组态。',
    note: 'relax 与 vc-relax 二选一，结构弛豫后再接 scf。',
  },
  'dft-plus-u': {
    zh: 'DFT+U',
    category: 'interface-magnet',
    needs: ['scf'],
    produces: ['U 修正后的结果'],
    diff: '本步给局域 d / f 电子加 U 修正后重跑 scf；普通 scf 的泛函在这些轨道上自相互作用误差偏大。',
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
