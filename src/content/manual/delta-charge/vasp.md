# VASP 差分电荷密度：三算例相减与网格对齐

**参考**：[ICHARG 标签页](https://www.vasp.at/wiki/index.php/ICHARG) · [LCHARG 标签页](https://www.vasp.at/wiki/index.php/LCHARG)

本页目标：算界面差分电荷 Δρ = ρ_AB − ρ_A − ρ_B。AB（复合体系）与两个单体各做一次自洽，三套 CHGCAR 逐点相减，VESTA 读图。案例体系 Sc2C/ZrCl2。

## 结构处理：单体怎么造、为什么三算例必须对齐

从已收敛的 `../scf/CONTCAR` 切片造单体。切片前先看体系构成（真实输出）：

```bash
head -n 10 ../scf/CONTCAR
```

```text
Sc2C
1.00000000000000
3.3268753886372542 -0.0000000000982961 0.0000000000000000
-1.6634376949064786 2.8811586017376438 0.0000000000000000
0.0000000000000001 -0.0000000000000005 39.5675948821758965
Zr C Cl Sc
1 1 2 2
```

原子顺序 Zr、C、Cl、Cl、Sc、Sc（第 9–14 行）。两条铁律：**晶胞盒子尺寸完全一致**（三个体系都用同一晶格），**原子绝对位置不变**（复制后只删原子、不移动剩余原子）。破坏任何一条，逐点相减在物理上就不成立。切片动作（行号按原子顺序对应，切前用 `head -n 15` 核对）：

```bash
# part_A (ZrCl2)：Zr 1 个 + Cl 2 个
sed -n '1,5p' ../scf/CONTCAR > part_A/POSCAR
echo " Zr Cl" >> part_A/POSCAR; echo " 1 2" >> part_A/POSCAR
echo "Direct" >> part_A/POSCAR
sed -n '9p'     ../scf/CONTCAR >> part_A/POSCAR   # Zr
sed -n '11,12p' ../scf/CONTCAR >> part_A/POSCAR   # Cl x2
# part_B (Sc2C)：C 1 个 + Sc 2 个
sed -n '1,5p'  ../scf/CONTCAR > part_B/POSCAR
echo " C Sc" >> part_B/POSCAR; echo " 1 2" >> part_B/POSCAR
echo "Direct" >> part_B/POSCAR
sed -n '10p'    ../scf/CONTCAR >> part_B/POSCAR   # C
sed -n '13,14p' ../scf/CONTCAR >> part_B/POSCAR   # Sc x2
```

## FFT 网格对齐：先读后写死

三个体系必须落在同一 FFT 网格上，做法是从 OUTCAR 读实测值再写死进三份 INCAR：

```bash
grep -n "dimension x,y,z" ../scf/OUTCAR
```

```text
515: dimension x,y,z NGX =  28 NGY =  28 NGZ = 294
516: dimension x,y,z NGXF=  56 NGYF=  56 NGZF= 588
```

```bash
mkdir -p AB part_A part_B
```

三份 INCAR 完全相同（真实方案，网格行写死）：

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

一个技术提醒：这套 INCAR 继承自的 scf 源文件 `SYSTEM` 行是复制残留的 `SYSTEM = SnS2`，实际体系是 ZrCl2/Sc2C 界面——继承输入前核对体系头。另一个真实参考方案（96 原子大超胞）的差异只在电荷起点：AB/A 用 `ICHARG = 1`（读 CHGCAR 文件起），B 用 `ICHARG = 2`（从赝电荷叠加起），配 `NWRITE = 10`、`AMIX = 0.02` 慢混合；其 `SYSTEM` 行同样是模板残留，且三份均未开 `LVTOT`——复用前逐项与执行者核对。

## POTCAR 按片段重组

删了原子必须按新元素顺序重新拼接，**绝不能整只复制父体系 POTCAR**。先看父 POTCAR 的元素与版本（只看 TITEL，不引用内容）：

```bash
grep "TITEL" ../scf/POTCAR
```

```text
TITEL = PAW_PBE Zr_sv 04Jan2005
TITEL = PAW_PBE C     08Apr2002
TITEL = PAW_PBE Cl    06Sep2000
TITEL = PAW_PBE Sc_sv 07Sep2000
```

从 `<potcar目录>` 按 part_A（Zr、Cl）与 part_B（C、Sc）重新 `cat` 拼接，验证：

```bash
grep "TITEL" part_A/POTCAR   # 应显示 Zr、Cl
grep "TITEL" part_B/POTCAR   # 应显示 C、Sc
```

## 命令主线与判读

```bash
mpirun -np <np> vasp_std > out.log 2>&1     # AB / part_A / part_B 各一次
head -n 20 AB/CHGCAR
```

判据：三套 CHGCAR 头部下方的三维网格数值**严格相同**（对照 head -n 20 的输出逐位核对）；三套 OSZICAR 均到达 `NSW = 0` 单点的收敛末行。

## 相减与出图（本页唯一工具）

```bash
vaspkit -task 314
# 依次输入 AB/CHGCAR、part_A/CHGCAR、part_B/CHGCAR -> 生成 CHGDIFF.vasp
```

`CHGDIFF.vasp` 进 VESTA：正等值面 = AB 比单体叠加多出的电荷（得电子区），负等值面 = 失电子区。结合 Bader 页的分层转移量（Sc2C 层失、ZrCl2 层得，±0.43 e），切面上堆积/耗减位置可直接对上界面转移方向。

失败模式清单：网格不一致 → 相减无意义，回到写死网格重算；POTCAR 元素顺序与 POSCAR 不匹配 → 元素张冠李戴，TITEL 验证兜底；切片行号错位 → 单体组成错误，head -n 15 兜底。

## 思考

1. 为什么 B 参考体用 `ICHARG = 2`（赝电荷叠加）就够，而 AB/A 必须 `ICHARG = 1`？
2. 若 part_A 用了与 AB 不同的 ENCUT，CHGCAR 网格还会一致吗？问题出在哪一步才能被发现？
3. 切片造单体时删的是原子行，为什么绝不能顺手动晶格行？
