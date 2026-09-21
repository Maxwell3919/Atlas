## 需要 / 产出

- 前置：已收敛的界面体系 `scf/`（含 `CONTCAR` 与 `OUTCAR`）。
- 产出：三套自洽（AB 复合体系、part_A、part_B）的 CHGCAR，逐点相减得差分电荷密度 `CHGDIFF.vasp`，VESTA 渲染等值面/切面。Δρ = ρ_AB − ρ_A − ρ_B。

## 本步与相邻步骤不同之处

- 与 Bader 的差别：Bader 按原子划分单套电荷；差分电荷需要**三套**独立自洽（AB / part_A / part_B），且三者的 FFT 网格与晶胞必须完全一致才能逐点相减。
- 单体处理规则：晶格常数不变（三个体系晶胞盒子完全一致）、原子绝对位置不变（直接从 `../scf/CONTCAR` 复制并删去对应原子，不移动剩余原子坐标）。

## 参数（只列本步）

- 在 `../scf/INCAR` 基础上只做自洽不移动离子：`IBRION = -1`、`NSW = 0`、`LWAVE = F`、`LCHARG = T`。
- **必须显式写死 FFT 网格**（数值取自 OUTCAR 实测；本例 `NGX = 28, NGY = 28, NGZ = 294`，精细网格 56/56/588）。
- 继承 scf 基础参数：`PREC = Accurate`、`ENCUT = 520`、`EDIFF = 1E-6`、`NELM = 160`、`ISMEAR = 0`、`SIGMA = 0.05`、`GGA = PE`、`IVDW = 11`。

## 命令与输出

1. 提取固定网格参数：

```bash
grep -n "dimension x,y,z" ../scf/OUTCAR
# 515: dimension x,y,z NGX =  28 NGY =  28 NGZ = 294
# 516: dimension x,y,z NGXF=  56 NGYF=  56 NGZF= 588
mkdir -p AB part_A part_B
```

2. 确认体系构成（`head -n 10 ../scf/CONTCAR`，共 14 行信息可用 `head -n 15` 核对坐标行）：

```text
Sc2C
1.00000000000000
3.3268753886372542 -0.0000000000982961 0.0000000000000000
-1.6634376949064786 2.8811586017376438 0.0000000000000000
0.0000000000000001 -0.0000000000000005 39.5675948821758965
Zr C Cl Sc
1 1 2 2
```

3. 三目录 INCAR 模板（网格行按 OUTCAR 实测值写死）：

```fortran
SYSTEM = sc2c_zrcl2_cod
PREC = Accurate
ENCUT = 520
EDIFF = 1E-6
NELM = 160
NELMIN = 4
ALGO = N
ISMEAR = 0
SIGMA = 0.05
GGA = PE
IVDW = 11
IBRION = -1
NSW = 0
LWAVE = F
LCHARG = T
NGX = 28
NGY = 28
NGZ = 294
```

## 后处理

- 三个体系自洽完成后先核对网格一致：`head -n 20 AB/CHGCAR` 与 `head -n 20 part_A/CHGCAR`、`part_B/CHGCAR` 的三维网格数值严格相同。
- 用 VASPKIT 自动化做差：

```bash
vaspkit -task 314
# 依次输入 AB/CHGCAR、part_A/CHGCAR、part_B/CHGCAR -> 生成 CHGDIFF.vasp
```

- `CHGDIFF.vasp` 直接用 VESTA 打开显示等值面（得失电子区域用正/负等值面对照着看）。

## 失败与假阳性

- **网格不一致无法逐点相减**：三个子体系晶胞参数与 FFT 网格（NGX/NGY/NGZ）必须完全相同，否则 chgadd/VASPKIT 相减无意义。
- **POTCAR 不能整只复制父体系**：删原子后必须按新元素顺序重新拼接对应赝势。本例父 POTCAR 核对：

```bash
grep "TITEL" ../scf/POTCAR
# TITEL = PAW_PBE Zr_sv 04Jan2005
# TITEL = PAW_PBE C     08Apr2002
# TITEL = PAW_PBE Cl    06Sep2000
# TITEL = PAW_PBE Sc_sv 07Sep2000
```

  拼接后验证：`grep "TITEL" part_A/POTCAR` 应显示 Zr、Cl；`grep "TITEL" part_B/POTCAR` 应显示 C、Sc。
- 复制的 INCAR 可能残留错误的 `SYSTEM` 头（本例 scf 源文件写着 `SYSTEM = SnS2`，实际是 ZrCl2/Sc2C 界面），不影响计算但必须核对改正。

## 可选脚本 + 检查清单

从 CONTCAR 切片生成单体 POSCAR（行号按原子顺序对应，切前先 `head -n 15` 核对）：

```bash
# part_A (ZrCl2)：Zr 1 个 + Cl 2 个
sed -n '1,5p' ../scf/CONTCAR > part_A/POSCAR
echo " Zr Cl" >> part_A/POSCAR
echo " 1 2" >> part_A/POSCAR
echo "Direct" >> part_A/POSCAR
sed -n '9p'     ../scf/CONTCAR >> part_A/POSCAR   # Zr
sed -n '11,12p' ../scf/CONTCAR >> part_A/POSCAR   # Cl x2

# part_B (Sc2C)：C 1 个 + Sc 2 个
sed -n '1,5p'  ../scf/CONTCAR > part_B/POSCAR
echo " C Sc" >> part_B/POSCAR
echo " 1 2" >> part_B/POSCAR
echo "Direct" >> part_B/POSCAR
sed -n '10p'    ../scf/CONTCAR >> part_B/POSCAR   # C
sed -n '13,14p' ../scf/CONTCAR >> part_B/POSCAR   # Sc x2
```

检查清单：
- [ ] `grep -n "dimension x,y,z"` 的网格值已写死进三份 INCAR，且三份一致。
- [ ] `head -n 20` 抽查 AB/part_A/part_B 的 CHGCAR 网格数值严格相同。
- [ ] part_A/part_B 的 POSCAR 元素行、数目行、坐标行数逐一对应（原子绝对位置不变）。
- [ ] `grep "TITEL"` 核对两份片段 POTCAR 的元素与顺序。
- [ ] 三个体系均 `LCHARG = T`、`NSW = 0` 正常结束，vaspkit 314 生成 CHGDIFF.vasp。
