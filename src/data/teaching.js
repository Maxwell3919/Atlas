// Teaching scope and actual file dependencies, reviewed against the articles.
export const methodTeaching = {
  "convergence": {
    "overview": "改变截断能、网格等数值参数，观察目标量何时稳定。比较时保留同一结构、参考和能量定义。",
    "aliases": [
      "收敛",
      "ecut",
      "k网格"
    ]
  },
  "relax": {
    "overview": "固定晶胞，利用原子力调整内部坐标。末态需要同时读取优化停止信息和最终力。",
    "aliases": [
      "结构优化",
      "离子优化",
      "BFGS"
    ]
  },
  "vc-relax": {
    "overview": "让晶胞与原子坐标参与优化，寻找指定外压与自由度下的结构。晶胞约束决定结果代表的几何条件。",
    "aliases": [
      "晶格优化",
      "晶胞优化",
      "压力"
    ]
  },
  "scf": {
    "overview": "在给定结构中求相互一致的电子密度与有效势，生成后续计算所需的电子状态。",
    "aliases": [
      "自洽",
      "电荷密度",
      "pw.x"
    ]
  },
  "nscf": {
    "overview": "保持已收敛密度，在新的 k 点求本征态。均匀网格常用于积分，路径采样用于色散。",
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
    "overview": "比较层状结构分离前后的匹配能量。剥离、解理和有限距离分离功需说明各自的结构参考与分离操作。",
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
    "overview": "由原子位移扰动引起的电子线性响应和力的变化构造动力学矩阵，再求频率、位移与声子色散。",
    "aliases": [
      "DFPT",
      "ph.x",
      "动力学矩阵"
    ]
  },
  "phonon-finite-disp": {
    "overview": "对超胞原子施加小位移，以实际原子力重建力常数和声子频率。",
    "aliases": [
      "有限位移",
      "Phonopy",
      "力常数"
    ]
  },
  "imaginary-phonon": {
    "overview": "从动力学矩阵、模式位移和数值对照诊断负本征值，判断软模或平移模式的来源。",
    "aliases": [
      "虚频",
      "软模",
      "ASR"
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
    "overview": "用第一性原理原子力推进短时轨迹，读取温度和能量并检查时间步长及电子求解。",
    "aliases": [
      "分子动力学",
      "AIMD",
      "NVE"
    ]
  },
  "phdos": {
    "overview": "对布里渊区中的振动模式做积分，得到声子态密度；路径色散与态密度使用不同取样。",
    "aliases": [
      "声子DOS",
      "PHDOS",
      "matdyn"
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
  "anharmonic-sscha": {
    "overview": "研究有限温度振动如何偏离谐近似。当前 MACE 路线用位移与力拟合有效二阶力常数。",
    "aliases": [
      "非谐",
      "有效力常数",
      "symfc",
      "SSCHA"
    ]
  },
  "bands": {
    "overview": "沿指定倒空间路径计算和绘制电子色散，读图时核对坐标、能量零点和本征值求解。",
    "aliases": [
      "能带",
      "band structure",
      "高对称路径"
    ]
  },
  "band-gap": {
    "overview": "在足够的倒空间采样中定位价带顶和导带底，区分直接与间接间隙及其采样误差。",
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
    "overview": "对均匀布里渊区取样的电子态做能量分布统计，进一步可按原子或轨道投影。",
    "aliases": [
      "态密度",
      "DOS",
      "PDOS"
    ]
  },
  "fatband": {
    "overview": "把逐 k、逐带的原子轨道投影与色散对应，用权重观察能带组成。",
    "aliases": [
      "胖带",
      "投影能带",
      "projwfc"
    ]
  },
  "fermi-surface": {
    "overview": "从完整倒空间取样中寻找能量等于费米能的位置，辨认电子和空穴口袋与周期边界。",
    "aliases": [
      "费米面",
      "Fermi surface",
      "口袋"
    ]
  },
  "spin-texture": {
    "overview": "读取含 SOC 本征态的自旋投影，并在明确的自旋基底和 k 空间采样上解释方向。",
    "aliases": [
      "自旋纹理",
      "Rashba",
      "Ising",
      "PROCAR"
    ]
  },
  "electrostatic-potential": {
    "overview": "从势网格求法向平均，识别真空平台或界面势变化，并核对势的组成与能量单位。",
    "aliases": [
      "静电势",
      "LOCPOT",
      "平面平均"
    ]
  },
  "fermi-nesting": {
    "overview": "比较费米面平移后的几何重叠；几何联合权重与包含占据差、能量分母的响应函数需分别定义。",
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
    "overview": "在相同晶胞和冻结位置下相减组合体系与片段密度，观察电子积累和耗尽。",
    "aliases": [
      "差分电荷",
      "密度差",
      "CHGCAR"
    ]
  },
  "bader": {
    "overview": "按实空间密度拓扑划分原子盆地，积分电子数并检查网格、参考密度和总数。",
    "aliases": [
      "Bader",
      "ACF.dat",
      "原子盆地"
    ]
  },
  "elf": {
    "overview": "读取电子局域化函数，在统一阈值与原始采样上观察局域化空间分布。",
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
    "overview": "在明确的投影基底中统计原子或轨道布居，并核对未被基底覆盖的电子部分。",
    "aliases": [
      "布居",
      "Löwdin",
      "Lowdin"
    ]
  },
  "wannier90": {
    "overview": "构造局域 Wannier 表象并插值电子色散，使用直接计算检查插值精度。",
    "aliases": [
      "Wannier",
      "MLWF",
      "pw2wannier90"
    ]
  },
  "epc": {
    "overview": "连接电子态与声子响应计算耦合，区分电子、声子取样和积分展宽对结果的影响。",
    "aliases": [
      "电声耦合",
      "电子声子耦合",
      "双网格"
    ]
  },
  "eliashberg-a2f": {
    "overview": "把声子频率和电子声子权重组成谱函数，再求耦合积分与对数平均频率。",
    "aliases": [
      "α²F",
      "alpha2F",
      "谱函数"
    ]
  },
  "allen-dynes": {
    "overview": "把谱函数矩与指定库仑赝势代入经验公式估算 Tc，并检查数值输入的敏感性。",
    "aliases": [
      "Allen-Dynes",
      "McMillan",
      "Tc"
    ]
  },
  "epw-eliashberg": {
    "overview": "以完整电子声子谱求解 Eliashberg 方程，区分线性化 Tc 与非线性能隙函数的求解。",
    "aliases": [
      "EPW",
      "Eliashberg",
      "超导能隙"
    ]
  },
  "phonon-linewidth": {
    "overview": "读取声子模式的电子声子线宽，核对频率、q 权重与采用的展宽和单位约定。",
    "aliases": [
      "线宽",
      "γ",
      "linewidth"
    ]
  },
  "bkt-scaling": {
    "overview": "利用二维相位模型的刚度、涡旋和尺寸依赖研究 BKT 行为，明确温度与抽样时间的模型单位。",
    "aliases": [
      "BKT",
      "XY",
      "相位刚度",
      "涡旋"
    ]
  },
  "workfunction": {
    "overview": "把同一次计算的真空势与电子化学势相减，读取指定表面的功函数并说明占据条件。",
    "aliases": [
      "功函数",
      "真空能级",
      "LVHAR"
    ]
  },
  "band-alignment": {
    "overview": "先将各材料的带边或费米能转换到明确参考，再比较能级位置与接触后的界面响应。",
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
    "overview": "在明确的形变或电子数条件下逐点比较性质，分别说明应变自由度与带电边界。",
    "aliases": [
      "应变",
      "掺杂",
      "调控"
    ]
  },
  "heterostructure-modeling": {
    "overview": "定义共同晶胞、层内几何和配准，再检查层间距与周期边界；不同堆垛或扭角需相应建模。",
    "aliases": [
      "异质结",
      "层间距",
      "莫尔",
      "堆垛"
    ]
  },
  "berry-chern": {
    "overview": "从本征态的几何关系构造回路或平面不变量。当前 QE 算例计算占据子空间的周期二维切片陈数。",
    "aliases": [
      "Berry",
      "Chern",
      "陈数",
      "ℤ₂"
    ]
  },
  "carrier-mobility": {
    "overview": "将电子色散与指定散射模型连接到迁移率。当前 MoS₂ 算例使用二维纵向声学形变势近似。",
    "aliases": [
      "迁移率",
      "形变势",
      "声学散射"
    ]
  }
};

export const manualTeaching = {
  "adsorption-energy/qe": {
    "title": "Al(111) 两面 H 吸附与 H₂ 参考",
    "kind": "DFT",
    "summary": "比较三层洁净薄膜、两面各 1 ML 顶位 H 与气相 H₂ 的匹配能量，检查几何和数值设置对吸附能的影响。",
    "inputs": [],
    "related": [
      "relax",
      "scf"
    ],
    "files": [
      "relax.in",
      "relax.out",
      "adsorption-energy.csv"
    ]
  },
  "aimd/qe": {
    "title": "Al 短时 AIMD 与步长比较",
    "kind": "DFT",
    "summary": "在 8 原子 fcc Al 固定超胞中完成 SVR 恒温与两种步长的 NVE 轨迹，读取温度、能量和坐标。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "Al 最终晶格与坐标"
      }
    ],
    "related": [
      "scf",
      "phonon-dfpt"
    ],
    "files": [
      "initial-velocities.json",
      "thermo.csv",
      "trajectory.npz"
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
  "anharmonic-sscha/mace": {
    "title": "Si 有限温度有效二阶力常数拟合",
    "kind": "机器学习势",
    "summary": "从 MACE 轨迹中提取位移与力，用 symfc 拟合有效二阶力常数，再由 phonopy 比较不同样本数下的频率。",
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
    "related": [],
    "files": [
      "mapped-dataset.npz",
      "independent-dataset.npz",
      "fit-summary.json",
      "learning-curve.csv"
    ]
  },
  "bader/vasp": {
    "title": "bcc Fe 的 Bader 盆地电荷",
    "kind": "DFT",
    "summary": "用共线 FM Fe 的 CHGCAR 和全电子参考密度划分盆地，比较包含 96³ 与 192³ 细网格的两套实空间设置及整胞积分。",
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
    "title": "SnSe₂/Sr₂N 冻结孤立层的能级参考",
    "kind": "DFT",
    "summary": "保留共同面内晶胞与层内几何，用各层相向表面的真空势比较 SnSe₂ 带边和金属 Sr₂N 费米能。",
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
    "title": "Si 高对称路径能带",
    "kind": "DFT",
    "summary": "从固定 Si 的 SCF 密度计算 121 个路径点，读取本征值并核对路径与求解状态。",
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
    "title": "Si 占据子空间的周期切片陈数",
    "kind": "DFT",
    "summary": "从两套完整网格的原生重叠矩阵构造 FHS 回路，十个固定 k₃ 切片得到 C=0，并检查规范与周期链接。",
    "inputs": [],
    "related": [
      "wannier90",
      "bands"
    ],
    "files": [
      "silicon.mmn",
      "silicon.nnkp",
      "slices.csv",
      "independent-check.json"
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
    "title": "固定 Si 的截断与网格比较",
    "kind": "DFT",
    "summary": "在同一两原子金刚石 Si 晶胞内逐项改变数值参数，比较匹配的总能量。",
    "inputs": [],
    "related": [
      "scf",
      "relax"
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
    "title": "固定 H₂ 的成键差分电子密度",
    "kind": "DFT",
    "summary": "在同一 10 Å 晶胞和冻结原子位置下计算 H₂、H_A、H_B，逐网格相减并检查电子数与空间分布。",
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
    "title": "Si 均匀 NSCF 上的总态密度",
    "kind": "DFT",
    "summary": "用 dos.x 读取 24³ 网格的带能和权重，比较能量步长、展宽与 DOS 的积分含义。",
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
    "title": "HfCl₂/PbO₂ 的平面平均静电势",
    "kind": "DFT",
    "summary": "读取固定几何静态计算的 LVHAR 势，重建 56×56×480 网格的法向平均与两侧平台。",
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
    "title": "bcc Fe 两自旋通道的 ELF",
    "kind": "DFT",
    "summary": "用共线 FM Fe 计算并读取 ELFCAR，检查真实采样网格与同阈值下的三维等值面。",
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
    "title": "HfI₂ 冻结六层薄膜的分离曲线",
    "kind": "DFT",
    "summary": "读取零位移与 2–20 Å 的 20 个完整单点，提取有限距离分离功；七个未完成目录另列排除表。",
    "inputs": [],
    "related": [
      "scf",
      "heterostructure-modeling"
    ],
    "files": [
      "OUTCAR",
      "exfoliation.csv",
      "excluded.csv"
    ]
  },
  "fatband/qe": {
    "title": "Si 路径态的 s/p 投影胖带",
    "kind": "DFT",
    "summary": "读取同一 121 点路径的波函数，将两原子 s、p 逐态投影与能量按索引合并。",
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
    "title": "Al 费米面几何联合权重 J(q)",
    "kind": "DFT",
    "summary": "从完整 24³/32³ 点阵的 Eₙ(k)−E_F 求周期联合权重，比较网格和能量窗口；采用几何权重定义。",
    "inputs": [
      {
        "method": "fermi-surface",
        "label": "24³/32³ 的 fermi-grid.npz"
      }
    ],
    "related": [
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
    "title": "SnSe₂/Sr₂N 的层距几何构造",
    "kind": "DFT",
    "summary": "从已有共同晶胞出发，将法向层间距设为 3 Å 并居中，检查层厚、配准和周期镜像空白。",
    "inputs": [],
    "related": [
      "band-alignment",
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
    "title": "bcc Fe 的 FM、AFM 与非磁候选",
    "kind": "DFT",
    "summary": "在固定 a=2.8 Å 的两原子胞比较三种自洽解，结合局域磁矩区分抵消与无自旋极化。",
    "inputs": [],
    "related": [
      "scf",
      "mae",
      "exchange-j"
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
      "anharmonic-sscha"
    ],
    "files": [
      "initial.traj",
      "nve-1fs.traj",
      "nve-0p5fs.csv",
      "trajectory-check.json"
    ]
  },
  "nscf/qe": {
    "title": "Si 固定密度的 24³ 本征值",
    "kind": "DFT",
    "summary": "从 8³ SCF 密度求 8 条能带，保留 Davidson 未收敛记录并读取 CG 完成分支。",
    "inputs": [
      {
        "method": "scf",
        "label": "8³ 父 SCF 的完整 si.save"
      }
    ],
    "related": [
      "dos",
      "band-gap",
      "population-analysis"
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
    "title": "固定 Si 晶胞的位移恢复",
    "kind": "DFT",
    "summary": "固定第一个原子和晶胞，从第二个原子的 x 向位移出发进行位置优化，读取 BFGS 轨迹和末态力。",
    "inputs": [],
    "related": [
      "scf",
      "convergence",
      "vc-relax"
    ],
    "files": [
      "relax.in",
      "relax.out"
    ]
  },
  "scf/qe": {
    "title": "两原子 Si 的固定结构 SCF",
    "kind": "DFT",
    "summary": "用指定 Si 结构完成电子自洽，核对迭代、总能、力与压力以及后续保存目录。",
    "inputs": [],
    "related": [
      "convergence",
      "nscf",
      "bands"
    ],
    "files": [
      "scf.in",
      "scf.out",
      "charge-density.dat",
      "data-file-schema.xml"
    ]
  },
  "scf/vasp": {
    "title": "两原子 bcc Fe 的固定结构 SCF",
    "kind": "DFT",
    "summary": "读取实际 VASP 输入、电子迭代、能量和磁矩，区分电子收敛与几何优化。",
    "inputs": [],
    "related": [
      "magnetic-gs",
      "workfunction"
    ],
    "files": [
      "INCAR",
      "OUTCAR",
      "OSZICAR"
    ]
  },
  "spin-texture/vasp": {
    "title": "SnSe₂/Sr₂N 路径上的 SOC 自旋投影",
    "kind": "DFT",
    "summary": "沿 Γ–M–K–Γ 读取 150×72 组 PROCAR 数据与自旋基底，保留高对称线上的原始投影。",
    "inputs": [],
    "related": [
      "scf",
      "mae"
    ],
    "files": [
      "PROCAR",
      "spin-path.dat",
      "spin-summary.json"
    ]
  },
  "strain-doping-scan/qe": {
    "title": "Al 六点纵向应变的能量与应力",
    "kind": "DFT",
    "summary": "保持电子数与横向晶胞分量，逐点读取 xx 应变的 F 和应力，并统一拉伸为正的符号。",
    "inputs": [
      {
        "method": "vc-relax",
        "label": "Al 优化晶格参数"
      }
    ],
    "related": [
      "elastic-born",
      "scf"
    ],
    "files": [
      "strain-stress.csv",
      "strain-summary.json"
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
    "title": "Al 晶胞优化与未收敛结构对照",
    "kind": "DFT",
    "summary": "沿 fcc 晶格约束完成 Al 的 vc-relax，读取最后坐标与压力；另保留 HfCl₂/PbO₂ 的 BFGS 停止记录。",
    "inputs": [],
    "related": [
      "scf",
      "phonon-dfpt",
      "elastic-born"
    ],
    "files": [
      "al.relax.in",
      "al.relax.out"
    ]
  },
  "wannier90/qe": {
    "title": "Si 四条价带的 Wannier 插值",
    "kind": "DFT",
    "summary": "从本例独立 SCF、完整 NSCF 与接口矩阵构造四个 Wannier 函数，再与直接 DFT 路径点比较。",
    "inputs": [],
    "related": [
      "scf",
      "nscf",
      "berry-chern"
    ],
    "files": [
      "silicon.win",
      "silicon.mmn",
      "silicon.nnkp",
      "spread-history.csv"
    ]
  },
  "workfunction/vasp": {
    "title": "SnSe₂ 单层的真空参考功函数",
    "kind": "DFT",
    "summary": "从同次 SCF 的 LVHAR 势、费米能和带边读取两侧能级差，并结合半导体占据条件解释数值。",
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
  }
};
