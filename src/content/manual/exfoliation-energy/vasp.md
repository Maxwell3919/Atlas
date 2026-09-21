# VASP 剥离能：E(d) 曲线外推

**参考**：[IVDW 标签页](https://www.vasp.at/wiki/index.php/IVDW) · [NSW 标签页](https://www.vasp.at/wiki/index.php/NSW)

本页目标：把 bilayer 逐步拉开，用 E(d) 曲线的渐近值外推剥离能。核心思想：层间距 d → ∞ 时层间相互作用 → 0，故 E(∞) − E_eq 即剥离能。真实主例：HfI2 bilayer（18 原子，`HfI2_3`），目录方案 `relax` + `scf_eq` + `scf_d1…scf_d20`。

## 结构处理：E(d) 方案怎么搭（本页核心）

三段式目录方案：

1. **relax**：先弛豫出层间平衡结构（平衡层间距 d_eq 与能量 E_eq）；
2. **scf_eq**：平衡结构的单点；
3. **scf_d1…scf_d20**：20 个拉开不同层间距的单点。已逐字节核验：全部 20 个目录的 INCAR 与 scf_eq **完全相同**（diff 无输出），唯一差异是 POSCAR 里的层间距。

这保证了 E(d) 曲线上任何一点与 E_eq 之间只有结构差异、没有参数差异——剥离能是纯物理量而不是参数差的假象。

**参考体系配对要谨慎**。本体系族在 QE 侧有现成对照（真实目录参数）：

- mono 参考（`pristine/HfCl2/mono/rx.in`）：`calculation = 'vc-relax'`，`assume_isolated = '2D'`，`cell_dofree = '2Dxy'`，nat = 3，ecutwfc = 90 / ecutrho = 720，c = 30 Å，K_POINTS 16 16 1；
- 4L slab（`exfoliation/HfCl2/relax/scf.in`）：`calculation = 'relax'`，nat = 12（4 层×3 原子），nbnd = 200，ecutwfc = 70 / ecutrho = 560，c = 100 Å，K_POINTS 16 16 1。

配对规则：同参数、同赝势、同 vdW 修正；mono 参考要考虑 2D 隔离与真空设置。上例两套参数并不成对（ecutwfc 90 vs 70、mono 开 2D 隔离而 slab 无）——直接相减前必须统一。另外该目录树下有个 `bulk` 目录，实为 nat = 3 的单层结构，**不要当体相参考写**；是否另建真体相参考需与执行者核对。

## 输入文件：relax INCAR（全文）

```fortran
SYSTEM = HfI2_relax
   LREAL = A
   LASPH = T
   LCORR = T
   LORBIT = 11
   LWAVE = F
   LCHARG = T
   ISIF = 2             # 只弛豫离子，晶格不动（面内晶格固定）
   IBRION = 2           # 共轭梯度
   NSW = 200
   EDIFFG = -0.01       # 力收敛判据 eV/A
   ENCUT = 520
   GGA = PE
   VOSKOWN = 1
   EDIFF = 1E-6
   NELMIN = 4
   NELM = 60
   AMIX = 0.1           # slab 快收敛混合器
   BMIX = 0.0001
   AMIX_MAG = 0.4
   BMIX_MAG = 0.0001
   MAXMIX = 80
   LMAXMIX = 4
   IVDW = 11            # D3 修正——vdW 层间结合的能量来源
   ALGO = Fast
   PREC = Normal
   ISMEAR = 0
   SIGMA = 0.05
```

relax 收敛后的 CONTCAR（真实头部）就是结构基准：

```text
HfI2_3
   1.00000000000000
     3.8018445870448683 ...
   I    Hf
    12     6
```

## 输入文件：scf_eq INCAR（全文，活跃行）

```fortran
SYSTEM = HfI2_scf       # 源文件此行为复制残留的 SYSTEM = SnS2，运行前改回本体系
LPLANE = .TRUE.
NPAR = 4
NSIM = 4
ISTART = 0
LWAVE = F
LCHARG = T
# LVTOT = T             # 需要静电势时再开（与功函数页衔接）
LCORR = T
LREAL = A
LASPH = T
LORBIT = 11
ISIF = 2
IBRION = -1             # 单点
ENCUT = 400             # 注意：此目录实际用 400 eV（relax 是 520）——引用前核对
GGA = PE
VOSKOWN = 1
EDIFF = 1E-6
NELMIN = 4
NELM = 160
AMIX = 0.1
BMIX = 0.0001
AMIX_MAG = 0.4
BMIX_MAG = 0.0001
MAXMIX = 80
LMAXMIX = 4
IVDW = 11
ALGO = N
PREC = Accurate
ISMEAR = 0
SIGMA = 0.05
```

（其余为模板注释行。）scf_d1…d20 与此逐字节相同——这正是本方案的可信支点。

## 命令主线

批量投递由目录内现成脚本完成（`submit_all_scf.sh`，附 `submitted_jobs.tsv` 记录 dir/jobid/dependency——工程产物，不进主线）。单目录等价命令：

```bash
mpirun -np <np> vasp_std > out.log 2>&1
```

E(d) 提取用本页唯一小工具（逐目录取 OSZICAR 末行）：

```bash
for d in scf_eq scf_d1 scf_d2 scf_d3 scf_d5 scf_d8 scf_d10 scf_d13 scf_d15 scf_d18 scf_d20; do
  echo "$d  $(tail -1 $d/OSZICAR | awk '{print $2, $5}')"
done
```

## 判读：真实 E(d) 表与渐近

```text
scf_eq   F= -.11123310E+03
scf_d1   F= -.11114522E+03
scf_d5   F= -.11100296E+03
scf_d10  F= -.11098760E+03
scf_d15  F= -.11098481E+03
scf_d20  F= -.11098415E+03
```

判据链条：d15→d20 的能量差已缩到 0.66 meV（总能量），曲线进入平台——**渐近值 E(∞) ≈ −110.984 eV**；平衡值 E_eq = −111.233 eV。剥离能 = E(∞) − E_eq ≈ 0.249 eV，按 18 原子归一 ≈ **13.8 meV/atom**。与石墨烯约 70 meV/atom 的量级对照：此方案给出的层间结合明显更弱——数值解读前需与执行者核对 d 的定义（扫描起点是否越过 d_eq）与渐近判据是否足够远。作图建议：E(d)−E_eq 对 d 画曲线，平台高度即剥离能。

## 思考

1. 为什么 E(d) 扫描的 INCAR 必须与 scf_eq 逐字节相同？改一个 SIGMA 会污染哪段结论？
2. d15 与 d20 只差 0.66 meV，就能断定到达渐近了吗？还要什么证据？
3. relax 用 ENCUT=520 而 scf 系列用 400，E_eq 与 E(d) 直接相减合法吗？应先做什么？
