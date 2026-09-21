# VASP 功函数：slab 静电势与真空能级

**参考**：[LVTOT 标签页](https://www.vasp.at/wiki/index.php/LVTOT) · [IDIPOL 标签页](https://www.vasp.at/wiki/index.php/IDIPOL)

本页目标：对一个已收敛的 slab 模型求功函数 Φ = E_vac − E_F。真实主例：SnSe2 slab（`SYSTEM = SnSe2 wf`，非自洽续算），产物 LOCPOT 与 PLANAR_AVERAGE.dat 同目录俱在。

## 结构处理：slab 模型要点

功函数是「真空能级 − 费米能级」，slab 结构直接决定真空能级可不可信，三点必须落实：

1. **真空层要够厚**：真空方向（z）留出真实平台区，slab 表面势在真空端必须衰减到平台；
2. **偶极修正**：不对称 slab 有净偶极，开 `LDIPOL = .TRUE.` + `IDIPOL = 3`（沿 z 修正），`DIPOL = 0.5 0.5 0.5` 把修正中心放在 slab 质心（分数坐标半程）；
3. **固定结构**：`NSW = 0`、`IBRION = -1`，功函数只对特定构型定义，不做离子步。

## 输入文件：INCAR（非自洽续算，一次成块）

本页主例的真实 INCAR 全文，逐段注释：

```fortran
SYSTEM = SnSe2 wf   # SnSe2 Slab 功函数计算 (Work Function)

# 并行控制
LPLANE  = .TRUE.
NPAR    = 4
NSIM    = 4

# I/O 控制
ISTART  = 1         # 读取已有 WAVECAR
ICHARG  = 11        # 关键：非自洽，从已收敛 CHGCAR 读电荷
LWAVE   = .TRUE.
LCHARG  = .TRUE.
LVTOT   = .TRUE.    # 输出 LOCPOT（总局域势）——功函数的数据源
LCORR   = .TRUE.    # 修正项写入 LOCPOT，与偶极修正配套
LASPH   = .TRUE.
LORBIT  = 11

# 离子部分（固定结构）
NSW     = 0
IBRION  = -1
ISIF    = 2
EDIFFG  = -0.01
LDIPOL  = .TRUE.    # 偶极修正开启
IDIPOL  = 3         # 沿 z 修正
DIPOL   = 0.5 0.5 0.5   # 修正中心 = slab 中央

# 电子自洽(SCF)参数
ENCUT   = 520
GGA     = PE
EDIFF   = 1E-6
NELMIN  = 4
NELM    = 60
PREC    = Accurate
ALGO    = Normal
ISMEAR  = 0
SIGMA   = 0.05
IVDW    = 11

# 混合器参数（slab 加快收敛）
AMIX     = 0.1
BMIX     = 0.0001
AMIX_MAG = 0.4
BMIX_MAG = 0.0001
MAXMIX   = 80
LMAXMIX  = 4
```

方案读法：**先有一套已收敛的自洽 slab**（同参数、同结构，含相同的偶极修正设置），本步只是把它的 CHGCAR 拿来做非自洽静电势输出——`ICHARG = 11` 的含义就是「读 CHGCAR、固定电荷、只解势场」。KPOINTS/POSCAR/POTCAR 照常从 scf 目录复制。

## 命令主线

```bash
cp ../scf/POSCAR ../scf/POTCAR ../scf/KPOINTS ../scf/CHGCAR ./
mpirun -np <np> vasp_std > out.log 2>&1
ls LOCPOT        # 产物就位检查
```

LOCPOT 之后做 z 向平面平均得到 PLANAR_AVERAGE.dat（本例目录中两文件并存）；平面平均的具体生成命令按所用后处理工具核对待填充。

## 判读三件套

```bash
grep "E-fermi" OUTCAR
```

```text
 E-fermi :  -2.4741     XC(G=0):  -3.7120     alpha+bet : -3.3624
```

```bash
head -2 PLANAR_AVERAGE.dat && tail -2 PLANAR_AVERAGE.dat
```

```text
#Distance(A) Planar-Average-Potential(eV)/Densitiy(e/A)
  0.0000             3.27267
 18.2262             3.27892
```

判据：平面平均曲线两端（真空区）出现平台，本例平台值 ≈ 3.28 eV；E_F = −2.4741 eV。功函数 = 平台 − E_F ≈ 3.28 − (−2.47) ≈ **5.75 eV**（与 SnSe2 文献量级一致）。判据细则：平台必须平坦（两端数值差 < 0.01 eV 量级才可信），slab 中部势阱深度与平台差即为表面偶极效应的直观量。

## QE 对照一句

QE 侧同思路：pp.x 出静电势（`plot_num = 1` 或 `2`）后用 average.x 做 z 向平面平均，真空平台与 `the Fermi energy is` 行相减即得 Φ——管线与 VASP 一致，读法不变。

## 思考

1. `ICHARG = 11` 与直接在 scf 里开 `LVTOT` 一步做完，差别在哪？为什么主例选续算？
2. 若真空端平台不平（两端差 0.05 eV），先怀疑哪三个设置？
3. DIPOL 放在 (0.5, 0.5, 0.5) 的前提是什么？slab 不在盒子中央时会怎样？
