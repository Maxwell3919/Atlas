export const methodTeaching = {
  "convergence": {
    "overview": "比较所关心的性质随数值设置的变化，先用小体系学习总能量、力和采样的检查。",
    "aliases": [
      "收敛",
      "ecut",
      "k网格"
    ]
  },
  "relax": {
    "overview": "规定晶胞与可动原子，连同末态力读取内部坐标的优化结果。",
    "aliases": [
      "结构优化",
      "离子优化",
      "BFGS"
    ]
  },
  "vc-relax": {
    "overview": "规定晶胞自由度，在应力和原子力条件下寻找对应的结构。",
    "aliases": [
      "晶格优化",
      "晶胞优化",
      "压力"
    ]
  },
  "scf": {
    "overview": "在给定几何和电子模型下求自洽密度，逐段读取实际参数、迭代与保存数据。",
    "aliases": [
      "自洽",
      "电荷密度",
      "pw.x"
    ]
  },
  "nscf": {
    "overview": "沿用匹配的父密度求本征态，按 DOS、带边或费米面的需要选择采样。",
    "aliases": [
      "非自洽",
      "本征值"
    ]
  },
  "formation-energy": {
    "overview": "用匹配的元素参考比较化合物形成的能量；内聚能使用孤立原子参考。两种参考对应不同物理问题。",
    "aliases": [
      "形成能",
      "内聚能",
      "参考态"
    ]
  },
  "convex-hull": {
    "overview": "在明确的组分和候选集合内寻找最低能量混合物，计算候选相离下凸包的距离。",
    "aliases": [
      "凸包",
      "相图",
      "energy above hull"
    ]
  },
  "exfoliation-energy": {
    "overview": "沿指定分离路径读取能量增加，核对参考结构、界面数和面积归一化。",
    "aliases": [
      "剥离",
      "解理",
      "分离功"
    ]
  },
  "adsorption-energy": {
    "overview": "把吸附态与洁净表面、吸附物来源的能量配对，比较指定位点和覆盖度的反应能。",
    "aliases": [
      "吸附",
      "结合能",
      "覆盖度"
    ]
  },
  "phonon-dfpt": {
    "overview": "由电子线性响应求动力学矩阵，将界面和应变频率变化对应到原子位移、层与方向权重。",
    "aliases": [
      "DFPT",
      "ph.x",
      "动力学矩阵",
      "层间振动",
      "本征矢"
    ]
  },
  "phonon-finite-disp": {
    "overview": "将超胞正负位移与全部原子受力配对，求层内和跨层力常数，并检查位移幅度与超胞范围。",
    "aliases": [
      "有限位移",
      "Phonopy",
      "力常数",
      "跨层恢复力"
    ]
  },
  "imaginary-phonon": {
    "overview": "从原始矩阵和真实位移区分Γ平移残差、层间相对运动及有限q结构软模。",
    "aliases": [
      "虚频",
      "软模",
      "ASR",
      "ZA",
      "相容超胞"
    ]
  },
  "elastic-born": {
    "overview": "从应变引起的应力或能量变化提取弹性张量，再使用适合晶体对称性和外压的力学条件。",
    "aliases": [
      "弹性常数",
      "Born",
      "C11"
    ]
  },
  "aimd": {
    "overview": "从原子轨迹读取热运动，先检查温控、步长与力，再分析层间距、滑移和结构变化。",
    "aliases": [
      "分子动力学",
      "AIMD",
      "NVE"
    ]
  },
  "phdos": {
    "overview": "以统一单位积分原子声子谱，按真实原子顺序合成元素和层贡献，再与色散及耦合谱对读。",
    "aliases": [
      "声子DOS",
      "PHDOS",
      "原子投影",
      "层投影"
    ]
  },
  "elastic-moduli": {
    "overview": "从弹性张量得到方向响应或指定多晶平均，区分体模量、剪切模量、杨氏模量与泊松比。",
    "aliases": [
      "VRH",
      "泊松比",
      "杨氏模量"
    ]
  },
  "mlip-md": {
    "overview": "由固定的机器学习势提供原子力进行动力学采样，检查积分误差和模型适用的结构范围。",
    "aliases": [
      "MLIP",
      "MACE",
      "机器学习势MD"
    ]
  },
  "bands": {
    "overview": "沿物理 k 路径读取色散与费米交点，再与孤立层、轨道投影和均匀网格结果配对。",
    "aliases": [
      "能带",
      "band structure",
      "高对称路径"
    ]
  },
  "band-gap": {
    "overview": "在实际采样的布里渊区寻找带边，比较父密度、子网格和局部谷搜索的影响。",
    "aliases": [
      "带隙",
      "VBM",
      "CBM"
    ]
  },
  "band-3d": {
    "overview": "在局部二维或三维 k 点阵上读取能量，观察电子谷的形状和不同方向曲率。",
    "aliases": [
      "三维能带",
      "能量曲面",
      "E(k)"
    ]
  },
  "band-unfolding": {
    "overview": "把超胞本征态投影回指定原胞布里渊区，以谱权重区分折叠与实际电子结构变化。",
    "aliases": [
      "反折叠",
      "unfolding",
      "谱权重"
    ]
  },
  "dos": {
    "overview": "按统一能量参考与归一化读取 DOS 和层投影，比较费米点及选定能窗的谱重。",
    "aliases": [
      "态密度",
      "DOS",
      "PDOS"
    ]
  },
  "fatband": {
    "overview": "把本征值与同一个 (k, band) 的投影配对，辨认层来源和杂化线索。",
    "aliases": [
      "胖带",
      "投影能带",
      "projwfc"
    ]
  },
  "fermi-surface": {
    "overview": "从完整倒空间网格重建费米等能轮廓，再回读对应能带、投影和电子或空穴性质。",
    "aliases": [
      "费米面",
      "Fermi surface",
      "口袋"
    ]
  },
  "spin-texture": {
    "overview": "读取 SOC 本征态的自旋投影，核对坐标基底、电子数、时间反演条件与所覆盖的 k 空间。",
    "aliases": [
      "自旋纹理",
      "Rashba",
      "Ising",
      "PROCAR"
    ]
  },
  "electrostatic-potential": {
    "overview": "说明势的组成，沿层法向平均，并将平台、势阶跃与电荷重排对应。",
    "aliases": [
      "静电势",
      "LOCPOT",
      "平面平均"
    ]
  },
  "fermi-nesting": {
    "overview": "用完整电子网格计算几何联合权重J(q)，在同q上与声子和EPC比较。",
    "aliases": [
      "嵌套",
      "J(q)",
      "Lifshitz"
    ]
  },
  "effective-mass": {
    "overview": "由带边附近的局部曲率求有效质量，检查倒空间单位、谷底位置和拟合窗口。",
    "aliases": [
      "有效质量",
      "曲率",
      "Hessian"
    ]
  },
  "delta-charge": {
    "overview": "在共同几何和密度网格上相减，结合三维分布、平面平均和累计积分读取密度重排。",
    "aliases": [
      "差分电荷",
      "密度差",
      "CHGCAR"
    ]
  },
  "bader": {
    "overview": "按零通量盆地积分密度，对同层原子加总，并检查冻结参照与网格变化。",
    "aliases": [
      "Bader",
      "ACF.dat",
      "原子盆地"
    ]
  },
  "elf": {
    "overview": "将局域化函数放回晶体结构中，结合选带或选能窗密度辨认间隙电子态。",
    "aliases": [
      "ELF",
      "ELFCAR",
      "等值面"
    ]
  },
  "cohp": {
    "overview": "将能带贡献投影到指定原子对，分析能量分辨的成键与反键贡献及积分值。",
    "aliases": [
      "COHP",
      "ICOHP",
      "LOBSTER",
      "pCOHP"
    ]
  },
  "population-analysis": {
    "overview": "在固定投影定义下读取原子与轨道布居，连同投影覆盖率比较电子态变化。",
    "aliases": [
      "布居",
      "Löwdin",
      "Lowdin"
    ]
  },
  "wannier90": {
    "overview": "建立所需电子子空间，先与直接 DFT 检验插值，再接 EPC、WCC 或边界谱。",
    "aliases": [
      "Wannier",
      "MLWF",
      "pw2wannier90"
    ]
  },
  "epc": {
    "overview": "由电子双网格和逐q矩阵追到模式线宽、耦合与配对谱，保留Al32³/48³两条完整链。",
    "aliases": [
      "EPC",
      "双网格",
      "电声耦合",
      "pwxall",
      "界面振动"
    ]
  },
  "eliashberg-a2f": {
    "overview": "从真实谱积分累计λ、对数频率和二阶矩，按模式和频段解释界面与应变变化。",
    "aliases": [
      "α²F",
      "累计λ",
      "谱积分",
      "频段贡献"
    ]
  },
  "allen-dynes": {
    "overview": "区分简化估计与完整f₁f₂公式，以真实两分支谱矩和展宽曲线分析Tc差异。",
    "aliases": [
      "Tc",
      "Allen–Dynes",
      "μ*",
      "网格比较"
    ]
  },
  "epw-eliashberg": {
    "overview": "对照外部谱与Wannier原生谱的等方实算，并说明材料Δnk(T)所需的动量分辨数据。",
    "aliases": [
      "EPW",
      "Eliashberg",
      "能隙",
      "各向异性",
      "Wannier"
    ]
  },
  "phonon-linewidth": {
    "overview": "用真实q模式核对γ与λ的单位和频率权重，再结合原子位移解读低频与高频贡献。",
    "aliases": [
      "线宽",
      "γqν",
      "λqν",
      "原子位移"
    ]
  },
  "bkt-scaling": {
    "overview": "在二维周期方格的 XY 模型中采样相位，读取相位刚度与涡旋，观察有限尺寸下它们怎样随温度变化。",
    "aliases": [
      "BKT",
      "XY",
      "相位刚度",
      "涡旋",
      "Monte Carlo"
    ]
  },
  "workfunction": {
    "overview": "从同一次计算的真空势和费米能求功函数，分别读取薄层两侧的表面。",
    "aliases": [
      "功函数",
      "真空能级",
      "LVHAR"
    ]
  },
  "band-alignment": {
    "overview": "用相向表面的真空势对齐冻结单层能级，再由接触后的电子结构检查界面变化。",
    "aliases": [
      "带边对齐",
      "能级对齐",
      "真空参考"
    ]
  },
  "magnetic-gs": {
    "overview": "在一致结构和参数下比较候选磁构型，读取最终局域磁矩以确认所获得的状态。",
    "aliases": [
      "磁基态",
      "FM",
      "AFM",
      "NM"
    ]
  },
  "dft-plus-u": {
    "overview": "对指定局域轨道加入 Hubbard 修正，核对元素顺序、U−J 与程序实际读入的参数。",
    "aliases": [
      "DFT+U",
      "Hubbard",
      "Dudarev"
    ]
  },
  "mae": {
    "overview": "在同一磁构型和几何中比较磁化相对晶体的方向能量，检查 SOC、网格和展宽的成对一致性。",
    "aliases": [
      "MAE",
      "磁各向异性",
      "SAXIS"
    ]
  },
  "exchange-j": {
    "overview": "用已确认的磁态能量或响应提取指定自旋模型的交换项，数清周期键并检验模型预测。",
    "aliases": [
      "交换参数",
      "Heisenberg",
      "J"
    ]
  },
  "strain-doping-scan": {
    "overview": "明确单/双轴几何应变，在同结构来源和协议下比较电荷、层电子态、声子与超导相关量。",
    "aliases": [
      "应变",
      "掺杂",
      "调控"
    ]
  },
  "heterostructure-modeling": {
    "overview": "在共同面内晶胞中规定堆叠、层间距与可动自由度，建立界面和单层参照。",
    "aliases": [
      "异质结",
      "层间距",
      "莫尔",
      "堆垛"
    ]
  },
  "berry-chern": {
    "overview": "从占据子空间的重叠矩阵计算回路相位，区分总相位、本征相位、切片陈数和自旋子 Z₂。",
    "aliases": [
      "Berry",
      "Chern",
      "陈数"
    ]
  },
  "carrier-mobility": {
    "overview": "将电子色散与指定散射模型连接到迁移率。当前 MoS₂ 算例使用二维纵向声学形变势近似。",
    "aliases": [
      "迁移率",
      "形变势",
      "声学散射"
    ]
  },
  "temperature-effective-fc": {
    "overview": "从有限温度采样的位移与原子力拟合有效二阶力常数，比较样本数与所得振动频率。当前算例采用 MACE、symfc 和 Phonopy。",
    "aliases": [
      "有限温度",
      "有效力常数",
      "symfc",
      "力拟合"
    ]
  }
};

export const manualTeaching = {
  "adsorption-energy/qe": {
    "title": "H/Al(111) 吸附与气相参照记录",
    "kind": "DFT",
    "summary": "保留H2参照、每H归一化和成对网格/力检查；与当前异质双层的结合能参照分别说明。",
    "inputs": [],
    "related": [
      "scf",
      "relax",
      "heterostructure-modeling"
    ],
    "files": [
      "relax.in",
      "relax.out",
      "adsorption-energy.csv"
    ]
  },
  "aimd/qe": {
    "title": "Al AIMD 步长对照与界面轨迹判读",
    "kind": "DFT",
    "summary": "从8原子Al短轨迹比较SVR响应和等时长NVE积分误差，再说明界面热运动应跟踪的层间距、滑移与配位。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "Al算例已接受晶格；界面研究改用自身优化结构"
      }
    ],
    "related": [
      "scf",
      "heterostructure-modeling",
      "phonon-dfpt",
      "phonon-finite-disp"
    ],
    "files": [
      "al.md.in",
      "al.md.out",
      "thermo.csv",
      "trajectory.xyz"
    ]
  },
  "allen-dynes/qe": {
    "title": "Al 双致密网格 Tc 估算对照",
    "kind": "DFT",
    "summary": "读取 32³ 与 48³ 两条计算链的谱矩和 Tc 表，按相同电子展宽配对求交，再比较 λ、ωlog 与 μ* 的影响。",
    "inputs": [
      {
        "method": "epc",
        "label": "32³/48³ 两分支的 lambda.in/out/dat"
      }
    ],
    "related": [
      "eliashberg-a2f",
      "epw-eliashberg"
    ],
    "files": [
      "lambda.in",
      "lambda.dat",
      "paired-tc.csv",
      "crossings.json"
    ]
  },
  "bader/vasp": {
    "title": "从 bcc Fe 分区到层电子数",
    "kind": "DFT",
    "summary": "读取真实密度、盆地和网格对照，再按冻结参考定义层转移。",
    "inputs": [
      {
        "method": "magnetic-gs",
        "label": "FM 的 POSCAR、KPOINTS 和匹配 PAW 标识"
      }
    ],
    "related": [
      "elf",
      "scf"
    ],
    "files": [
      "CHGCAR",
      "AECCAR0",
      "AECCAR2",
      "ACF.dat"
    ]
  },
  "band-3d/qe": {
    "title": "Si 导带谷的三维采样与切面",
    "kind": "DFT",
    "summary": "在 Γ–X 导带谷附近计算 891 个三维 k 点，画出局部纵向、横向能量切面。",
    "inputs": [],
    "related": [
      "band-gap",
      "effective-mass",
      "scf"
    ],
    "files": [
      "grid.in",
      "grid.out",
      "cube.csv"
    ]
  },
  "band-alignment/vasp": {
    "title": "SnSe₂/Sr₂N 冻结层的真空对齐",
    "kind": "DFT",
    "summary": "对齐共同晶胞内的半导体带边与金属费米能，明确接触前参考。",
    "inputs": [
      {
        "method": "heterostructure-modeling",
        "label": "原六原子 POSCAR.reference（冻结几何）"
      }
    ],
    "related": [
      "scf",
      "workfunction",
      "electrostatic-potential"
    ],
    "files": [
      "LOCPOT",
      "EIGENVAL",
      "alignment-summary.json"
    ]
  },
  "band-gap/qe": {
    "title": "Si 均匀网格带边与谷底加密",
    "kind": "DFT",
    "summary": "比较 12³、18³、24³ 采样中的带边，再加密 Γ–X 导带谷，判断直接与间接间隙的取样误差。",
    "inputs": [
      {
        "method": "scf",
        "label": "Si 父 SCF 保存密度：主组 8³，局部细化 12³"
      }
    ],
    "related": [
      "nscf",
      "effective-mass",
      "bands"
    ],
    "files": [
      "nscf.in",
      "nscf.out",
      "gap-results.json"
    ]
  },
  "band-unfolding/qe": {
    "title": "完美 Si 超胞的能带反折叠校验",
    "kind": "DFT",
    "summary": "分别计算原胞与 2×1×1 超胞，用 bands_unfold.x 从超胞波函数恢复原胞谱权重。",
    "inputs": [],
    "related": [
      "bands",
      "scf"
    ],
    "files": [
      "unfold.in",
      "spectral_weights01.dat",
      "wavefunction-audit.csv"
    ]
  },
  "bands/qe": {
    "title": "Si 路径能带与界面费米分支",
    "kind": "DFT",
    "summary": "从真实路径本征值读能带，再比较 ZrCl₂/Sc₂C 的分支和层来源。",
    "inputs": [
      {
        "method": "scf",
        "label": "同结构与参数的 si.save 密度"
      }
    ],
    "related": [
      "nscf",
      "fatband",
      "band-gap"
    ],
    "files": [
      "bands.in",
      "bands.out",
      "bands-post.in"
    ]
  },
  "berry-chern/qe": {
    "title": "Si 占据态的陈数与矩阵 Wilson 回路",
    "kind": "DFT",
    "summary": "从无 SOC 原生重叠矩阵复算十个零陈数切片及 52 个矩阵回路，区分总相位、本征相位与自旋子 Z₂。",
    "inputs": [],
    "related": [
      "wannier90",
      "spin-texture"
    ],
    "files": [
      "silicon.mmn",
      "silicon.nnkp",
      "slices.csv",
      "independent-check.json",
      "wilson_loop.py",
      "si-wilson-loops.csv",
      "si-wilson-summary.json"
    ]
  },
  "bkt-scaling/model": {
    "title": "二维 XY 模型的有限尺寸采样",
    "kind": "数值模型",
    "summary": "对 L=8、16、24 的周期方格进行 Monte Carlo 采样，比较初态、相位刚度、涡旋与有限尺寸变化。",
    "inputs": [],
    "related": [],
    "files": [
      "run.json",
      "final-angles.csv",
      "final-vortices.csv",
      "extension-comparison.csv"
    ]
  },
  "carrier-mobility/qe": {
    "title": "MoS₂ 二维声学形变势迁移率",
    "kind": "DFT",
    "summary": "连接应变能量、真空对齐导带与 K 谷质量，在 300 K 估算纵向声学形变势迁移率并比较采样设置。",
    "inputs": [],
    "related": [
      "effective-mass",
      "strain-doping-scan",
      "scf"
    ],
    "files": [
      "config.json",
      "avg.dat",
      "quality-gates.json",
      "summary.json"
    ]
  },
  "cohp/qe": {
    "title": "金刚石 C–C 键的 LOBSTER pCOHP",
    "kind": "DFT",
    "summary": "从本例独立 QE PAW SCF 的波函数投影四条最近邻 C–C 键，比较 k 网格和截断能对积分值的影响。",
    "inputs": [],
    "related": [
      "scf",
      "population-analysis"
    ],
    "files": [
      "scf.out",
      "data-file-schema.xml",
      "COHPCAR.lobster",
      "ICOHPLIST.lobster"
    ]
  },
  "convergence/qe": {
    "title": "固定 Si 总能量的截断与网格检查",
    "kind": "DFT",
    "summary": "用真实单变量扫描读取总能量误差，区分有限参照、组合参数和界面/声子目标量的接受条件。",
    "inputs": [],
    "related": [
      "scf",
      "relax",
      "phonon-dfpt"
    ],
    "files": [
      "scf.in",
      "scf.out"
    ]
  },
  "convex-hull/qe": {
    "title": "Al–Si 五候选集的下凸包",
    "kind": "DFT",
    "summary": "将两端元与三个结构原型的每原子形成能放到同一组分轴，计算候选集内的分解连线和凸包距离。",
    "inputs": [
      {
        "method": "formation-energy",
        "label": "候选集 formation-energy.csv 与元素参考"
      }
    ],
    "related": [
      "vc-relax"
    ],
    "files": [
      "formation-energy.csv",
      "formation-k32.csv",
      "comparison-k24-k32.csv"
    ]
  },
  "delta-charge/vasp": {
    "title": "差分密度、平面平均与累计积分",
    "kind": "DFT",
    "summary": "用 H₂ 真实三密度学习相减和积分，再说明界面层边界与面积归一化。",
    "inputs": [],
    "related": [
      "scf",
      "bader"
    ],
    "files": [
      "CHGCAR",
      "delta-planar.csv",
      "charge-difference-summary.json"
    ]
  },
  "dft-plus-u/vasp": {
    "title": "VGe₂P₄ 的 Ueff=3 eV 静态结果",
    "kind": "DFT",
    "summary": "将 V 的 d 轨道与 Dudarev 参数对应，读取实际 LMAXMIX、电子收敛、能量和磁矩，说明后续 CHGCAR 准备条件。",
    "inputs": [],
    "related": [
      "scf",
      "magnetic-gs"
    ],
    "files": [
      "INCAR",
      "OUTCAR",
      "dftu-result-table.csv"
    ]
  },
  "dos/qe": {
    "title": "DOS 与近费米能窗的层谱重",
    "kind": "DFT",
    "summary": "读取均匀网格与投影，提取四态冻结对照的费米点及窗口结果。",
    "inputs": [
      {
        "method": "nscf",
        "label": "24³ 带能、k 权重与 XML 保存数据"
      }
    ],
    "related": [
      "population-analysis",
      "bands",
      "band-gap"
    ],
    "files": [
      "dos.in",
      "dos.out"
    ]
  },
  "effective-mass/qe": {
    "title": "Si Γ–X 谷的纵向与横向质量",
    "kind": "DFT",
    "summary": "在局部导带谷加密采样，按明确倒空间单位拟合曲率，并比较窗口和父密度设置。",
    "inputs": [
      {
        "method": "convergence",
        "label": "重建 12³ 父 SCF 保存目录（14³ 用于独立复核）"
      }
    ],
    "related": [
      "band-gap",
      "band-3d",
      "scf"
    ],
    "files": [
      "mass.in",
      "mass.out",
      "mass-fits.json",
      "mass-checks.csv"
    ]
  },
  "elastic-born/qe": {
    "title": "Al 应力差分与立方 Born 条件",
    "kind": "DFT",
    "summary": "从成对纵向和剪切形变的 SCF 应力提取 C₁₁、C₁₂、C₄₄，比较应变幅度和 k 网格。",
    "inputs": [
      {
        "method": "phonon-dfpt",
        "label": "Al 参考 SCF 输入中的优化晶格"
      }
    ],
    "related": [
      "strain-doping-scan",
      "elastic-moduli"
    ],
    "files": [
      "cases.json",
      "strain-stress.csv",
      "elastic-results.csv"
    ]
  },
  "elastic-moduli/qe": {
    "title": "Al 弹性张量的 VRH 多晶平均",
    "kind": "DFT",
    "summary": "从同批立方弹性常数计算 Voigt、Reuss、Hill 平均及泊松比，区分多晶平均与晶向响应。",
    "inputs": [
      {
        "method": "elastic-born",
        "label": "同批形变 SCF 与 C₁₁/C₁₂/C₄₄"
      }
    ],
    "related": [
      "vc-relax"
    ],
    "files": [
      "cases.json",
      "elastic-results.csv",
      "strain-stress.csv"
    ]
  },
  "electrostatic-potential/vasp": {
    "title": "薄层两侧的平面平均电势",
    "kind": "DFT",
    "summary": "从 HfCl₂/PbO₂ 真实势读取平台，说明法向坐标与界面偶极。",
    "inputs": [],
    "related": [
      "scf",
      "workfunction",
      "band-alignment"
    ],
    "files": [
      "LOCPOT",
      "PLANAR_AVERAGE.dat",
      "potential-summary.json"
    ]
  },
  "elf/vasp": {
    "title": "ELF 文件、VESTA 与间隙态分析",
    "kind": "DFT",
    "summary": "读取两自旋块和真实 VESTA 操作，结合 Ca₂N 与 H-ZrCl₂ 的空间电子态。",
    "inputs": [
      {
        "method": "magnetic-gs",
        "label": "FM 的 POSCAR、KPOINTS 和匹配 PAW 标识"
      }
    ],
    "related": [
      "bader",
      "scf"
    ],
    "files": [
      "INCAR",
      "OUTCAR",
      "ELFCAR"
    ]
  },
  "eliashberg-a2f/qe": {
    "title": "Al 逐 q 耦合到 α²F 与谱矩",
    "kind": "DFT",
    "summary": "从完整 4³ q 网格接到 q2r、matdyn 和 lambda.x，分别核对谱函数来源、单位及 λ、ωlog 积分。",
    "inputs": [
      {
        "method": "epc",
        "label": "完整 elph_dir、动力学矩阵与逐 q EPC 文件"
      }
    ],
    "related": [
      "allen-dynes",
      "phonon-linewidth"
    ],
    "files": [
      "q2r.in",
      "matdyn-dos.in",
      "alpha2F.dat",
      "lambda.dat"
    ]
  },
  "epc/qe": {
    "title": "Al 双网格 EPC 的两条完整计算链",
    "kind": "DFT",
    "summary": "分别执行 32³ 与 48³ 致密网格、16³ 响应网格和 4³ q 网格，保留各自的响应与 Tc 输出。",
    "inputs": [],
    "related": [
      "phonon-dfpt",
      "eliashberg-a2f",
      "allen-dynes"
    ],
    "files": [
      "al.dense.in",
      "al.scf.in",
      "al.elph.in",
      "lambda.out"
    ]
  },
  "epw-eliashberg/qe": {
    "title": "Al 各向同性 Eliashberg 求解",
    "kind": "DFT",
    "summary": "从完整 α²F 或 DFPT–Wannier 插值谱进入 EPW，求温度相关能隙函数和线性化 Tc，并检查求解状态。",
    "inputs": [
      {
        "method": "eliashberg-a2f",
        "label": "已有完整 α²F 谱（直接求解入口）"
      }
    ],
    "related": [
      "allen-dynes",
      "wannier90",
      "epc"
    ],
    "files": [
      "epw.in",
      "epw.out",
      "gap.csv",
      "tc-brackets.json"
    ]
  },
  "exchange-j/vasp": {
    "title": "bcc Fe 两态有效交换与超胞检查",
    "kind": "DFT",
    "summary": "枚举周期最近邻键，用 FM/AFM 能量映射有效 J；核对四原子折叠，并保留被排除的 stripe4 磁矩塌缩。",
    "inputs": [
      {
        "method": "magnetic-gs",
        "label": "两原子 FM/AFM 的 OUTCAR 与 POSCAR"
      }
    ],
    "related": [
      "mae",
      "scf"
    ],
    "files": [
      "bonds-2fe.csv",
      "exchange-state-model-checks.csv",
      "exchange-summary.json"
    ]
  },
  "exfoliation-energy/vasp": {
    "title": "HfI₂ 冻结层分离与单位面积能量",
    "kind": "DFT",
    "summary": "从真实20个接受点读有限距离分离功，核对单界面面积、末段起伏和周期像；保留其作为层间分离方法示例的条件用途。",
    "inputs": [],
    "related": [
      "heterostructure-modeling",
      "relax",
      "delta-charge",
      "phonon-finite-disp"
    ],
    "files": [
      "OUTCAR",
      "exfoliation.csv",
      "excluded.csv"
    ]
  },
  "fatband/qe": {
    "title": "逐态投影与界面费米交点",
    "kind": "DFT",
    "summary": "核对能级和投影配对，读取六个真实交点的 Zr-d、Sc-d 与其他轨道权重。",
    "inputs": [
      {
        "method": "bands",
        "label": "121 点路径的 bands-cg/tmp/si.save 波函数"
      }
    ],
    "related": [
      "population-analysis",
      "dos"
    ],
    "files": [
      "projwfc.in",
      "projwfc.out",
      "atomic_proj.xml",
      "fatband.csv"
    ]
  },
  "fermi-nesting/qe": {
    "title": "几何J(q)：Al真实网格与应变软模的对照方法",
    "kind": "DFT",
    "summary": "保存24/32网格与0.10/0.20 eV窗口的联合权重；说明同结构同q对照，不声明异质结嵌套机制。",
    "inputs": [
      {
        "method": "fermi-surface",
        "label": "24³/32³ 的 fermi-grid.npz"
      }
    ],
    "related": [
      "fermi-surface",
      "strain-doping-scan",
      "phonon-linewidth",
      "epc"
    ],
    "files": [
      "fermi-grid.npz",
      "grid-info.json"
    ]
  },
  "fermi-surface/qe": {
    "title": "Al 完整三维网格的费米面",
    "kind": "DFT",
    "summary": "在 Al 自己的父密度上完成 24³/32³ NSCF，检查点阵与本征值，再提取跨费米能的等值面。",
    "inputs": [
      {
        "method": "phonon-dfpt",
        "label": "Al 自己的 SCF 结构与父密度"
      }
    ],
    "related": [
      "nscf",
      "fermi-nesting",
      "epc"
    ],
    "files": [
      "fermi-grid.npz",
      "grid-info.json"
    ]
  },
  "formation-energy/qe": {
    "title": "Al–Si 候选与元素晶体的形成能",
    "kind": "DFT",
    "summary": "计算 fcc Al、diamond Si 及三个候选原型，统一结构优化和静态参数后求每原子形成能。",
    "inputs": [],
    "related": [
      "vc-relax",
      "scf",
      "convex-hull"
    ],
    "files": [
      "vc-relax.in",
      "vc-relax.out",
      "formation-energy.csv"
    ]
  },
  "heterostructure-modeling/vasp": {
    "title": "SnSe₂/Sr₂N 构型与单层结合能参照",
    "kind": "几何建模",
    "summary": "保留真实刚性层移动，说明共同晶胞、侧向配准及冻结/自由单层参照；没有匹配能量组时不报告界面结合能数值。",
    "inputs": [],
    "related": [
      "scf",
      "relax",
      "delta-charge",
      "exfoliation-energy"
    ],
    "files": [
      "POSCAR.reference",
      "POSCAR.gap3p0",
      "model-check.json"
    ]
  },
  "imaginary-phonon/qe": {
    "title": "Si Γ 点虚频与同矩阵 ASR 对照",
    "kind": "DFT",
    "summary": "从六个实际 Γ 模式读取位移与负频率，对同一动力学矩阵比较不施加和施加 ASR 的结果。",
    "inputs": [
      {
        "method": "scf",
        "label": "本例 Si SCF 的密度与波函数保存目录"
      }
    ],
    "related": [
      "scf",
      "phonon-dfpt",
      "phonon-finite-disp"
    ],
    "files": [
      "ph.in",
      "ph.out",
      "asr-comparison.csv",
      "mode-vectors.csv"
    ]
  },
  "mae/vasp": {
    "title": "Fe 单层成对 SOC 方向能量",
    "kind": "DFT",
    "summary": "比较 x/z 两方向和 9×9/15×15 网格，核对磁矩坐标并保留能量差的符号翻转。",
    "inputs": [],
    "related": [
      "magnetic-gs",
      "scf"
    ],
    "files": [
      "OUTCAR",
      "mae-orientation-energies.csv",
      "mae-kmesh-comparison.csv"
    ]
  },
  "magnetic-gs/vasp": {
    "title": "bcc Fe磁候选比较存档",
    "kind": "DFT",
    "summary": "保留三态真实输入输出；H-ZrCl2空穴文献用于说明条件问题，当前文章建议隐藏。",
    "inputs": [],
    "related": [
      "scf",
      "fatband"
    ],
    "files": [
      "OUTCAR",
      "OSZICAR",
      "magnetic-state-energy-table.csv"
    ]
  },
  "mlip-md/mace": {
    "title": "64 原子 Si 的热浴与 NVE 轨迹",
    "kind": "机器学习势",
    "summary": "由优化晶胞建立超胞，运行 300 K 热浴及 NVE，并从同一帧减半步长比较能量守恒。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "relaxed.extxyz"
      },
      {
        "method": "relax",
        "label": "同一 MACE-MP-0 small 模型"
      }
    ],
    "related": [
      "temperature-effective-fc"
    ],
    "files": [
      "initial.traj",
      "nve-1fs.traj",
      "nve-0p5fs.csv",
      "trajectory-check.json"
    ]
  },
  "nscf/qe": {
    "title": "Si 固定密度的 24³ 本征态",
    "kind": "DFT",
    "summary": "沿用 8³ 父密度求 8 条带，读取 CG 求解、413 点 XML 与实际占据，区分父密度和子采样误差。",
    "inputs": [
      {
        "method": "scf",
        "label": "8³ 父 SCF 的完整 si.save"
      }
    ],
    "related": [
      "scf",
      "dos",
      "band-gap",
      "bands"
    ],
    "files": [
      "nscf.in",
      "nscf.out"
    ]
  },
  "phdos/qe": {
    "title": "Al 完整 q 网格的声子态密度",
    "kind": "DFT",
    "summary": "从 4³ DFPT 动力学矩阵经实空间变换做布里渊区积分，比较后处理 q 采样。",
    "inputs": [
      {
        "method": "phonon-dfpt",
        "label": "al.dyn0 与八份编号动力学矩阵"
      }
    ],
    "related": [
      "phonon-finite-disp"
    ],
    "files": [
      "q2r.in",
      "q2r.out",
      "matdyn-dos.in",
      "matdyn-dos32.out"
    ]
  },
  "phonon-dfpt/qe": {
    "title": "Al 的 DFPT 动力学矩阵与色散",
    "kind": "DFT",
    "summary": "在优化 fcc Al 上计算 SCF 与完整 q 网格，连接 q2r 和路径频率并检查声学求和。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "Al 最终晶格与坐标"
      }
    ],
    "related": [
      "scf",
      "phonon-finite-disp",
      "phdos"
    ],
    "files": [
      "charge-density.dat",
      "q2r.in",
      "q2r.out",
      "matdyn-band.in"
    ]
  },
  "phonon-finite-disp/qe": {
    "title": "Al 超胞正负位移的声子",
    "kind": "DFT",
    "summary": "用 8 原子超胞的实际 QE 力构造力常数，检查位移和频率，再与 DFPT 路线比较。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "优化 Al 原胞的晶格与坐标"
      }
    ],
    "related": [
      "phonon-dfpt",
      "imaginary-phonon"
    ],
    "files": [
      "bands.csv",
      "summary.json"
    ]
  },
  "phonon-linewidth/qe": {
    "title": "Al 逐 q、逐模式的电子声子线宽",
    "kind": "DFT",
    "summary": "读取完整 q 网格的频率、γ 与 λ，核对电子展宽、q 权重和模式记录。",
    "inputs": [
      {
        "method": "epc",
        "label": "完整 q 网格的 elph_dir 和原始 ph.x 输出"
      }
    ],
    "related": [
      "eliashberg-a2f",
      "allen-dynes"
    ],
    "files": [
      "linewidth.csv",
      "q-weight-source.json",
      "lambda.dat"
    ]
  },
  "population-analysis/qe": {
    "title": "Si 均匀网格的 Löwdin 布居",
    "kind": "DFT",
    "summary": "从 18³ 均匀网格波函数读取原子轨道投影，比较等价 Si 布居和投影未覆盖部分。",
    "inputs": [
      {
        "method": "band-gap",
        "label": "gap18-cg/tmp 的均匀网格波函数"
      }
    ],
    "related": [
      "nscf",
      "scf",
      "fatband"
    ],
    "files": [
      "projwfc.in",
      "projwfc.out",
      "lowdin.csv"
    ]
  },
  "relax/mace": {
    "title": "MACE 固定 Si 晶胞的原子优化",
    "kind": "机器学习势",
    "summary": "对 8 原子金刚石 Si 的单原子位移做固定晶胞 BFGS，读取能量、原子力与模型哈希。",
    "inputs": [],
    "related": [
      "vc-relax",
      "mlip-md"
    ],
    "files": [
      "initial.extxyz",
      "relax.traj",
      "relaxed.extxyz",
      "result.json"
    ]
  },
  "relax/qe": {
    "title": "Si 固定胞弛豫：末态力与内部坐标",
    "kind": "DFT",
    "summary": "用位移恢复和紧电子阈值复核认识原子优化，接到规定面内晶格的界面与应变条件。",
    "inputs": [],
    "related": [
      "scf",
      "vc-relax",
      "convergence",
      "heterostructure-modeling"
    ],
    "files": [
      "relax.in",
      "relax.out"
    ]
  },
  "scf/cp2k": {
  "title": "周期水的电子解、解析力与网格对照",
  "kind": "DFT",
  "summary": "从CP2K真实OUT提取能量与三行力，比较两套GPW网格并用一个中心有限差分检查解析力。",
  "inputs": [],
  "related": [
    "convergence",
    "relax",
    "phonon-finite-disp"
  ],
  "files": [
    "input.inp",
    "cp2k.out",
    "native_energy_forces.csv",
    "postprocess.py",
    "export_csv.py"
  ]
},
  "scf/qe": {
    "title": "Si 自洽密度与完整 OUT 判读",
    "kind": "DFT",
    "summary": "沿版本、结构、电子迭代、力应力与保存数据读固定结构 SCF，接到密度差和响应分析。",
    "inputs": [],
    "related": [
      "convergence",
      "nscf",
      "delta-charge",
      "phonon-dfpt"
    ],
    "files": [
      "scf.in",
      "scf.out",
      "charge-density.dat",
      "data-file-schema.xml"
    ]
  },
  "scf/vasp": {
    "title": "bcc Fe 的固定结构电子解与输出文件",
    "kind": "DFT",
    "summary": "以小体系认识有效参数、OSZICAR、能量定义及密度保存，区分电子解、几何条件与材料分析。",
    "inputs": [],
    "related": [
      "nscf",
      "relax",
      "delta-charge"
    ],
    "files": [
      "INCAR",
      "OUTCAR",
      "OSZICAR"
    ]
  },
  "spin-texture/vasp": {
    "title": "SnSe₂/Sr₂N 的 SOC 沿线自旋投影",
    "kind": "DFT",
    "summary": "读取 150×72 组 PROCAR 四块投影，解释 K 点真实记录，并连接二维费米面自旋与 Ising 配对所需证据。",
    "inputs": [],
    "related": [
      "bands",
      "wannier90",
      "epc"
    ],
    "files": [
      "PROCAR",
      "spin-path.dat",
      "spin-summary.json"
    ]
  },
  "strain-doping-scan/qe": {
    "title": "应变：从形变输入到界面电子态与声子/EPC",
    "kind": "DFT",
    "summary": "Al六点演示形变和应力；四态冻结PDOS说明应变与界面响应，再按Ba2N原文组织电荷、声子、alpha2F、lambda、omega_log和Tc对照。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "Al优化结构与独立SCF目录"
      },
      {
        "method": "population-analysis",
        "label": "四态冻结几何PDOS及能量参考"
      }
    ],
    "related": [
      "heterostructure-modeling",
      "delta-charge",
      "bader",
      "elf",
      "phonon-dfpt",
      "phonon-linewidth",
      "eliashberg-a2f",
      "allen-dynes"
    ],
    "files": [
      "al.scf.in",
      "al.scf.out",
      "strain-stress.csv",
      "frozen_pdos_long.csv",
      "inspect_frozen_pdos.py",
      "nearest-fermi-pdos.json"
    ]
  },
  "vc-relax/mace": {
    "title": "MACE Si 原子与六应变自由度优化",
    "kind": "机器学习势",
    "summary": "从 5.60 Å 的扰动常规胞出发，用 FrechetCellFilter 同时优化原子、体积和剪切并检查末态应力。",
    "inputs": [
      {
        "method": "relax",
        "label": "同一 MACE-MP-0 small 模型"
      }
    ],
    "related": [
      "mlip-md"
    ],
    "files": [
      "initial.extxyz",
      "vc-relax.traj",
      "relaxed.extxyz",
      "result.json"
    ]
  },
  "vc-relax/qe": {
    "title": "Al 变胞优化与二维受限自由度",
    "kind": "DFT",
    "summary": "读取完整 Al BFGS 末态与最后电子重算，借旧失败记录分清停止原因和二维面内约束。",
    "inputs": [],
    "related": [
      "scf",
      "relax",
      "phonon-dfpt",
      "strain-doping-scan"
    ],
    "files": [
      "al.relax.in",
      "al.relax.out"
    ]
  },
  "wannier90/qe": {
    "title": "Wannier 插值检验与 SOC 子空间",
    "kind": "DFT",
    "summary": "用 Si 真实接口和直接 DFT 检验四价带插值，再说明 SOC 自旋子、占据子空间和 WCC/边界谱的接续条件。",
    "inputs": [],
    "related": [
      "bands",
      "nscf",
      "berry-chern",
      "spin-texture",
      "epw-eliashberg"
    ],
    "files": [
      "silicon.win",
      "silicon.mmn",
      "silicon.nnkp",
      "spread-history.csv"
    ]
  },
  "workfunction/vasp": {
    "title": "SnSe₂ 两侧功函数与半导体带边",
    "kind": "DFT",
    "summary": "用同次真空势、费米能与带边，分别报告功函数、IP 和 EA。",
    "inputs": [],
    "related": [
      "scf",
      "electrostatic-potential",
      "band-alignment"
    ],
    "files": [
      "LOCPOT",
      "EIGENVAL",
      "PLANAR_AVERAGE.dat",
      "workfunction-summary.json"
    ]
  },
  "temperature-effective-fc/mace": {
    "title": "MACE–Si有效二阶力常数存档",
    "kind": "机器学习势",
    "summary": "保存位移力拟合和独立验证；不当作SSCHA或异质结非谐稳定化结果，当前路线建议隐藏。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "relaxed.extxyz 参考晶胞"
      },
      {
        "method": "mlip-md",
        "label": "nve-1fs.traj 与 initial.traj"
      },
      {
        "method": "relax",
        "label": "同一 MACE-MP-0 small 模型"
      }
    ],
    "related": [
      "imaginary-phonon",
      "phonon-finite-disp"
    ],
    "files": [
      "mapped-dataset.npz",
      "independent-dataset.npz",
      "fit-summary.json",
      "learning-curve.csv"
    ]
  },
  "relax/vasp": {
    "title": "HfCl₂ 薄层固定胞优化与残余应力",
    "kind": "DFT",
    "summary": "读取完整模型、10 个离子步和末力，区分固定胞内部坐标接受与晶胞平衡。",
    "inputs": [],
    "related": [
      "scf",
      "vc-relax",
      "heterostructure-modeling"
    ],
    "files": [
      "POSCAR",
      "CONTCAR",
      "OUTCAR",
      "OSZICAR",
      "ionic-history.csv"
    ]
  },
  "nscf/vasp": {
    "title": "SnSe₂/Sr₂N 固定密度与 DOS 读取",
    "kind": "DFT",
    "summary": "父子均为 18×18×1；读取 ICHARG=11 接续、能量轴与真实 DOS 样本，接到界面投影和空间密度。",
    "inputs": [],
    "related": [
      "scf",
      "dos",
      "bands",
      "fatband",
      "delta-charge"
    ],
    "files": [
      "CHGCAR",
      "EIGENVAL",
      "DOSCAR",
      "density-lineage.json"
    ]
  },
  "bands/vasp": {
    "title": "SnSe₂ 路径能带与内部带边",
    "kind": "DFT",
    "summary": "同一18×18×1父SCF密度，沿Γ–M–K–Γ计算150点、20带，以真实倒格矢构造路径距离，辨认路径内价带最高点与M导带底。",
    "inputs": [],
    "related": [
      "scf",
      "band-gap",
      "dos",
      "fatband"
    ],
    "files": [
      "bands/parameters-from-output.txt",
      "bands/incar-run.xml",
      "bands/POSCAR",
      "bands/KPOINTS",
      "bands/OUTCAR",
      "bands/EIGENVAL",
      "scf/vasprun.xml",
      "tables/bands.csv",
      "analysis.out",
      "analyse.py",
      "plot.py"
    ]
  },
  "dos/vasp": {
    "title": "SnSe₂ 静态均匀网格的 DOS 与态数",
    "kind": "DFT",
    "summary": "读取18×18×1静态SCF的301点DOSCAR与原子lm投影，核对26个价电子和40个带态；保留有限网格与步长的峰形，不使用路径DOS。",
    "inputs": [],
    "related": [
      "scf",
      "bands",
      "fatband",
      "population-analysis"
    ],
    "files": [
      "scf/parameters-from-output.txt",
      "scf/incar-run.xml",
      "scf/KPOINTS",
      "scf/OUTCAR",
      "scf/DOSCAR",
      "scf/EIGENVAL",
      "tables/dos.csv",
      "analysis.out",
      "analyse.py",
      "plot.py"
    ]
  },
  "fatband/vasp": {
    "title": "SnSe₂ 的 Sn-s 与 Se-p 逐态胖带",
    "kind": "DFT",
    "summary": "将150×20个路径态的PROCAR投影与EIGENVAL按索引配对，保留两原子Se-p及Sn-s原始权重，给出带边投影表。",
    "inputs": [
      {
        "method": "bands",
        "label": "同一 SnSe₂ 路径的 EIGENVAL 与 LORBIT=11 PROCAR"
      }
    ],
    "related": [
      "dos",
      "population-analysis"
    ],
    "files": [
      "bands/PROCAR",
      "bands/POSCAR",
      "bands/EIGENVAL",
      "tables/fatband.csv",
      "tables/path-edges.csv",
      "analysis.out",
      "analyse.py",
      "plot.py"
    ]
  }
};
