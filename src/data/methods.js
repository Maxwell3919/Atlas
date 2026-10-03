// Property directory and explicit research scope. Sources of hidden cases remain in the repository.
import researchScope from './research-scope.json';

export const engines = [
  { "id": "cp2k", "name": "CP2K" },
  {
    "id": "qe",
    "name": "Quantum ESPRESSO"
  },
  {
    "id": "vasp",
    "name": "VASP"
  },
  {
    "id": "mace",
    "name": "MACE"
  },
  {
    "id": "model",
    "name": "数值模型（Python）"
  }
];

export const categories = [
  {
    "id": "interface",
    "name": "界面结构与稳定性",
    "order": [
      "heterostructure-modeling",
      "exfoliation-energy",
      "aimd"
    ]
  },
  {
    "id": "electronic",
    "name": "电子结构与成键",
    "order": [
      "bands",
      "dos",
      "fatband",
      "fermi-surface",
      "band-unfolding",
      "effective-mass",
      "population-analysis",
      "cohp",
      "dft-plus-u"
    ]
  },
  {
    "id": "charge",
    "name": "界面电荷与间隙电子",
    "order": [
      "delta-charge",
      "bader",
      "elf",
      "electrostatic-potential",
      "workfunction",
      "band-alignment"
    ]
  },
  {
    "id": "phonons",
    "name": "声子与振动模式",
    "order": [
      "phonon-dfpt",
      "phonon-finite-disp",
      "imaginary-phonon",
      "phdos"
    ]
  },
  {
    "id": "supercon",
    "name": "电子–声子耦合与超导",
    "order": [
      "epc",
      "phonon-linewidth",
      "eliashberg-a2f",
      "allen-dynes",
      "epw-eliashberg"
    ]
  },
  {
    "id": "strain",
    "name": "应变响应",
    "order": [
      "strain-doping-scan",
      "fermi-nesting",
      "temperature-effective-fc"
    ]
  },
  {
    "id": "soc",
    "name": "SOC 与拓扑分析",
    "order": [
      "spin-texture",
      "wannier90",
      "berry-chern",
      "magnetic-gs"
    ]
  },
  {
    "id": "basics",
    "name": "共同计算基础",
    "order": [
      "convergence",
      "relax",
      "vc-relax",
      "scf",
      "nscf"
    ]
  }
];

export const methods = {
  "convergence": {
    "zh": "收敛测试",
    "category": "basics",
    "needs": [],
    "produces": [
      "收敛参数结论"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "relax": {
    "zh": "离子弛豫",
    "category": "basics",
    "needs": [
      "convergence"
    ],
    "produces": [
      "优化后结构"
    ],
    "engines": [
      "qe",
      "vasp",
      "mace"
    ],
    "needsByEngine": {
      "mace": []
    }
  },
  "vc-relax": {
    "zh": "晶胞弛豫",
    "category": "basics",
    "needs": [
      "convergence"
    ],
    "produces": [
      "优化晶胞与结构"
    ],
    "engines": [
      "qe",
      "vasp",
      "mace"
    ],
    "needsByEngine": {
      "mace": []
    }
  },
  "scf": {
    "zh": "电子自洽 SCF",
    "category": "basics",
    "needs": [
      "convergence",
      "relax",
      "vc-relax"
    ],
    "needsNote": "relax 与 vc-relax 按结构自由度选择，不要求依次完成两者。",
    "produces": [
      "电荷密度"
    ],
    "engines": [
      "qe",
      "vasp",
      "cp2k"
    ],
    "needsByEngine": { "cp2k": [] }
  },
  "nscf": {
    "zh": "非自洽 NSCF",
    "category": "basics",
    "needs": [
      "scf"
    ],
    "produces": [
      "固定电荷下的本征值"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "formation-energy": {
    "zh": "形成能与参考态",
    "category": "thermo",
    "needs": [
      "relax"
    ],
    "produces": [
      "同协议参照的形成能"
    ],
    "engines": [
      "qe",
      "vasp"
    ],
    "needsByEngine": {
      "qe": [
        "vc-relax"
      ]
    },
    "producesByEngine": {
      "qe": [
        "同协议元素参照的形成能"
      ]
    }
  },
  "convex-hull": {
    "zh": "凸包相图 / Energy-above-hull",
    "category": "thermo",
    "needs": [
      "formation-energy"
    ],
    "produces": [
      "凸包距离 / 相稳定性判定"
    ],
    "engines": [
      "qe",
      "vasp"
    ],
    "producesByEngine": {
      "qe": [
        "有限候选集凸包 / 凸包距离"
      ]
    }
  },
  "exfoliation-energy": {
    "zh": "层间分离能",
    "category": "interface",
    "needs": [
      "relax"
    ],
    "produces": [
      "指定分离操作的面积归一化能量差"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "adsorption-energy": {
    "zh": "吸附能",
    "category": "interface",
    "needs": [
      "relax"
    ],
    "produces": [
      "吸附能"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "phonon-dfpt": {
    "zh": "DFPT 声子与模式分析",
    "category": "phonons",
    "needs": [
      "scf"
    ],
    "produces": [
      "声子谱"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "phonon-finite-disp": {
    "zh": "有限位移声子",
    "category": "phonons",
    "needs": [
      "scf"
    ],
    "produces": [
      "力常数与声子谱"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "imaginary-phonon": {
    "zh": "虚频与软模分析",
    "category": "phonons",
    "needs": [
      "phonon-dfpt",
      "phonon-finite-disp"
    ],
    "produces": [
      "模式指认与软模结构分析"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "elastic-born": {
    "zh": "弹性常数与 Born 判据",
    "category": "mechanics",
    "needs": [
      "vc-relax"
    ],
    "produces": [
      "弹性常数与 Born 力学稳定性判据"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "aimd": {
    "zh": "短时 AIMD",
    "category": "interface",
    "needs": [
      "vc-relax"
    ],
    "produces": [
      "短时 MD 轨迹"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "phdos": {
    "zh": "声子态密度与层投影",
    "category": "phonons",
    "needs": [
      "phonon-dfpt",
      "phonon-finite-disp"
    ],
    "produces": [
      "声子态密度 / 投影声子"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "elastic-moduli": {
    "zh": "弹性模量 / 泊松比",
    "category": "mechanics",
    "needs": [
      "elastic-born"
    ],
    "produces": [
      "弹性模量 / 泊松比"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "mlip-md": {
    "zh": "机器学习势 MD",
    "category": "stability",
    "needs": [
      "relax"
    ],
    "needsByEngine": {
      "mace": [
        "vc-relax"
      ]
    },
    "produces": [
      "MLIP 分子动力学轨迹"
    ],
    "engines": [
      "mace"
    ]
  },
  "bands": {
    "zh": "能带",
    "category": "electronic",
    "needs": [
      "scf"
    ],
    "needsNote": "路径能带与 DOS 的均匀网格 NSCF 是从同一 SCF 出发的两个分支。",
    "produces": [
      "能带图"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "band-gap": {
    "zh": "带隙（直接 / 间接）",
    "category": "electronic",
    "needs": [
      "nscf"
    ],
    "produces": [
      "直接 / 间接带隙"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "band-3d": {
    "zh": "3D 能带",
    "category": "electronic",
    "needs": [
      "nscf"
    ],
    "produces": [
      "3D 能带 E(kx,ky) 面"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "band-unfolding": {
    "zh": "能带反折叠",
    "category": "electronic",
    "needs": [
      "bands"
    ],
    "produces": [
      "原胞 BZ 能带 / 光谱权重"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "dos": {
    "zh": "态密度 DOS / PDOS",
    "category": "electronic",
    "needs": [
      "nscf"
    ],
    "produces": [
      "DOS/PDOS"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "fatband": {
    "zh": "投影能带 / 胖带",
    "category": "electronic",
    "needs": [
      "bands",
      "dos"
    ],
    "needsByEngine": {
      "qe": [
        "bands"
      ]
    },
    "produces": [
      "投影能带"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "fermi-surface": {
    "zh": "费米面",
    "category": "electronic",
    "needs": [
      "nscf"
    ],
    "produces": [
      "费米面"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "spin-texture": {
    "zh": "SOC 自旋投影",
    "category": "soc",
    "needs": [
      "bands"
    ],
    "produces": [
      "自旋纹理图"
    ],
    "producesByEngine": {
      "vasp": [
        "SOC 路径上的自旋投影"
      ]
    },
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "electrostatic-potential": {
    "zh": "静电势 / 平面平均电势",
    "category": "charge",
    "needs": [
      "scf"
    ],
    "produces": [
      "平面平均静电势 / 电势阶跃"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "fermi-nesting": {
    "zh": "费米面几何嵌套",
    "category": "strain",
    "needs": [
      "fermi-surface"
    ],
    "produces": [
      "几何联合权重J(q)，不是完整chi(q)"
    ],
    "producesByEngine": {
      "qe": [
        "费米面几何联合权重 J(q)"
      ]
    },
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "effective-mass": {
    "zh": "有效质量",
    "category": "electronic",
    "needs": [
      "band-gap"
    ],
    "produces": [
      "有效质量 m*"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "delta-charge": {
    "zh": "差分电荷",
    "category": "charge",
    "needs": [
      "scf"
    ],
    "produces": [
      "差分电荷密度"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "bader": {
    "zh": "Bader 电荷",
    "category": "charge",
    "needs": [
      "scf"
    ],
    "produces": [
      "Bader 电荷"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "elf": {
    "zh": "ELF",
    "category": "charge",
    "needs": [
      "scf"
    ],
    "produces": [
      "ELF 图"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "cohp": {
    "zh": "COHP / ICOHP（LOBSTER）",
    "category": "electronic",
    "needs": [
      "scf"
    ],
    "produces": [
      "COHP / ICOHP 成键分析"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "population-analysis": {
    "zh": "布居分析",
    "category": "electronic",
    "needs": [
      "scf"
    ],
    "produces": [
      "原子 / 轨道布居"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "wannier90": {
    "zh": "Wannier90",
    "category": "soc",
    "needs": [
      "scf"
    ],
    "produces": [
      "最大局域化 Wannier 函数"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "epc": {
    "zh": "电声耦合与模式分析",
    "category": "supercon",
    "needs": [
      "wannier90",
      "phonon-dfpt",
      "phonon-finite-disp"
    ],
    "needsByEngine": {
      "qe": [
        "scf",
        "phonon-dfpt"
      ]
    },
    "needsNote": "本页 QE interpolated 路线不以 Wannier90 或有限位移声子为必经步骤。",
    "produces": [
      "λ / α²F / Tc"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "eliashberg-a2f": {
    "zh": "Eliashberg谱函数与累计耦合",
    "category": "supercon",
    "needs": [
      "epc"
    ],
    "produces": [
      "α²F(ω) / λ(ω)"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "allen-dynes": {
    "zh": "超导Tc公式与网格比较",
    "category": "supercon",
    "needs": [
      "eliashberg-a2f"
    ],
    "produces": [
      "Tc 估算"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "epw-eliashberg": {
    "zh": "EPW能隙方程与各向异性路线",
    "category": "supercon",
    "needs": [
      "eliashberg-a2f"
    ],
    "needsNote": "已有完整各向同性 α²F 可直接求解；从头生成谱函数时，按正文另一入口接上 DFPT 和 Wannier 插值。",
    "produces": [
      "超导能隙随温度变化",
      "线性化方程的 Tc"
    ],
    "engines": [
      "qe"
    ]
  },
  "phonon-linewidth": {
    "zh": "声子线宽与模式耦合",
    "category": "supercon",
    "needs": [
      "epc"
    ],
    "produces": [
      "声子线宽 γ_qν / 散射热点"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "bkt-scaling": {
    "zh": "二维 XY：相位刚度与涡旋",
    "category": "model",
    "needs": [],
    "produces": [
      "有限尺寸 Monte Carlo / 相位刚度 / 涡旋"
    ],
    "engines": [
      "model"
    ]
  },
  "workfunction": {
    "zh": "功函数",
    "category": "charge",
    "needs": [
      "scf"
    ],
    "produces": [
      "功函数"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "band-alignment": {
    "zh": "真空参考能级对齐",
    "category": "charge",
    "needs": [
      "bands",
      "workfunction"
    ],
    "produces": [
      "能带对齐图"
    ],
    "engines": [
      "qe",
      "vasp"
    ],
    "needsByEngine": {
      "vasp": [
        "workfunction",
        "heterostructure-modeling"
      ]
    },
    "producesByEngine": {
      "vasp": [
        "冻结孤立层的真空参考能级"
      ]
    }
  },
  "magnetic-gs": {
    "zh": "磁构型与能量比较",
    "category": "soc",
    "needs": [
      "relax",
      "vc-relax",
      "scf"
    ],
    "produces": [
      "FM/AFM/NM 能量比较"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "dft-plus-u": {
    "zh": "DFT+U",
    "category": "electronic",
    "needs": [
      "scf"
    ],
    "produces": [
      "U 修正后的结果"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "mae": {
    "zh": "磁各向异性能 MAE",
    "category": "magnet",
    "needs": [
      "magnetic-gs"
    ],
    "produces": [
      "磁各向异性能"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "exchange-j": {
    "zh": "磁能量映射与有效 J",
    "category": "magnet",
    "needs": [
      "magnetic-gs"
    ],
    "produces": [
      "交换参数 J"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "strain-doping-scan": {
    "zh": "应变下的电荷、电子态与声子/EPC",
    "category": "strain",
    "needs": [
      "vc-relax"
    ],
    "produces": [
      "应变结构与应力",
      "冻结态层PDOS对照",
      "电荷与声子/EPC/Tc比较的来源关系"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "heterostructure-modeling": {
    "zh": "异质结构建模",
    "category": "interface",
    "needs": [
      "convergence"
    ],
    "produces": [
      "异质结 / 莫尔超晶格模型"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "berry-chern": {
    "zh": "占据态 Berry 相位与切片陈数",
    "category": "soc",
    "needs": [],
    "produces": [
      "占据态重叠相位 / 周期切片陈数"
    ],
    "engines": [
      "qe",
      "vasp"
    ],
    "producesByEngine": {
      "qe": [
        "占据态重叠相位 / 周期切片 Chern 和"
      ]
    }
  },
  "carrier-mobility": {
    "zh": "二维声学形变势迁移率",
    "category": "transport",
    "needs": [
      "bands"
    ],
    "produces": [
      "声学形变势近似的迁移率"
    ],
    "engines": [
      "qe",
      "vasp"
    ]
  },
  "temperature-effective-fc": {
    "zh": "有限温度有效力常数",
    "category": "strain",
    "needs": [
      "aimd"
    ],
    "produces": [
      "有限温度有效二阶力常数与声子"
    ],
    "engines": [
      "qe",
      "vasp",
      "mace"
    ],
    "needsByEngine": {
      "mace": [
        "mlip-md",
        "vc-relax"
      ]
    },
    "producesByEngine": {
      "mace": [
        "有限温度有效二阶力常数与声子"
      ]
    }
  }
};

export const methodRouteAliases = { "anharmonic-sscha": "temperature-effective-fc" };
const hiddenMethods = new Set(researchScope.hidden_methods);
const hiddenManuals = new Set(researchScope.hidden_manual_ids);
export function isManualVisible(id) { return !hiddenMethods.has(id.split('/')[0]) && !hiddenManuals.has(id); }
export function methodList() { return categories.flatMap(c => c.order.filter(slug => !hiddenMethods.has(slug)).map(slug => ({ slug, ...methods[slug] }))); }
export function routeMethodList() { return Object.entries(methods).filter(([slug]) => !hiddenMethods.has(slug)).map(([slug, method]) => ({ slug, ...method })); }
export function normalizeBase(raw) { return raw.endsWith("/") ? raw.slice(0,-1) : raw; }
