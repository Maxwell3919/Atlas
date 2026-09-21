## 需要 / 产出

- 前置：已收敛的 `scf/` 目录（WAVECAR、CHGCAR 齐全）。
- 产出：ELF 三维数据文件——VASP 一步法直接得 `ELFCAR`；QE 两步法经 pw.x SCF + pp.x 得 `elf.cube`——导入 VESTA 渲染等值面/切面，分析成键与孤对电子局域化。

## 本步与相邻步骤不同之处

- ELF 与差分电荷/Bader 的差别：ELF 是无量纲局域化函数（0–1），刻画电子定域程度，不需要参考单体或电荷划分，只需本体系自洽场。
- VASP 一步法：静态 INCAR 加 `LELF = .TRUE.` 直接输出 ELFCAR，VESTA 原生拖拽打开。
- QE 两步法：先 `pw.x` 自洽，再用 `pp.x`（`plot_num = 8`）计算并导出 cube 格式。

## 参数（只列本步）

- 核心开关 `LELF = .TRUE.`；**`LREAL = .FALSE.`**（ELF 计算必须在倒空间投影，禁止 `LREAL = A`——实空间投影会给动能密度重构带来噪声）。
- `PREC = Accurate`（保证 FFT 网格精细，避免切面锯齿；必要时调大 FFT 网格）。
- 固定离子只做电子步：`IBRION = -1`、`NSW = 0`。
- 赝势依赖度：ELF 对赝势类型敏感，推荐全相对论/标量模守恒（NC）或标准 USPP/PAW；个别超软势在动能密度重建时偶有数值噪声。

## 命令与输出

1. 从 scf 复制文件后一步计算（会话终端原样命令）：

```bash
cp ../scf/CONTCAR ./POSCAR
cp ../scf/POTCAR ./
cp ../scf/KPOINTS ./
cp ../scf/WAVECAR ./
cp ../scf/CHGCAR ./
```

2. INCAR 原样（会话转录；`SYSTEM` 行原 scf 源文件为残留的 `SYSTEM = SnS2`，实际体系为 ZrCl2/Sc2C 界面，此处用正确体系名）：

```fortran
SYSTEM = Sc2C_ZrCl2
############### about I/O ################
 ISTART = 1        ! 读取已有的 WAVECAR
 ICHARG = 1        ! 读取已有的 CHGCAR
 LWAVE = .FALSE.
 LCHARG = .FALSE.
###########################################

########### about switch control ##########
 LELF = .TRUE.     ! 核心开关：计算并输出 ELFCAR
 LREAL = .FALSE.   ! ELF 计算必须在倒空间投影，禁止使用实空间投影(LREAL=A)
 PREC = Accurate   ! 保证 FFT 网格精细，避免切面锯齿
 LASPH = .TRUE.
 LORBIT = 11
###########################################

############# about ionic relax ############
 IBRION = -1       ! 固定离子步，只做电子步
 NSW = 0
###########################################

############ about electron scf ############
 ENCUT = 520
 GGA = PE
 VOSKOWN = 1
 EDIFF = 1E-6
 NELM = 60
###########################################

############### other important parameter ###############
 ALGO = Normal
 ISMEAR = 0
 SIGMA = 0.05
 IVDW = 11
 LMAXMIX = 4
```

计算完成生成 `ELFCAR`，直接拖入 VESTA。

3. QE 对比路线：pw.x 自洽后用 pp.x 两段输出（第二段 `&PLOT` 原样）：

```fortran
&PLOT
 nfile = 1,
 filepp(1) = 'calc_elf',
 weight(1) = 1.0,
 iflag = 3,          ! 3 代表 3D 体系
 output_format = 6,  ! 6 代表 Gaussian cube 格式（VESTA 友好）
 fileout = 'elf.cube'
/
```

## 后处理

- VESTA 打开 ELFCAR，Isosurface level 常见成键/孤对电子分析值取 **0.7 ∼ 0.85**（自由电子气参考值 0.5）；配合 Slice Contour 做 2D 切面。
- QE 路线产物为 `elf.cube`，同样导入 VESTA；二维层状材料建议在 pp.x 中适当加密输出网格，避免真空层边界处的数值发散或等值面截断伪影。
- QE 端 pw.x 自洽的完整输入模板待填充（会话仅含 pp.x 配置与说明）。

## 失败与假阳性

- `LREAL = A` 下算出的 ELF 带实空间投影重构噪声，等值面出现碎斑——必须 `LREAL = .FALSE.` 重算。
- FFT 网格不足时切面出现锯齿；用 `PREC = Accurate` 或显式调大网格解决。
- 赝势选择不当（个别超软势）会让动能密度重建失真，ELF 数值不可信，换标准 PAW/USPP/NC 复核。
- 复制的 INCAR 可能残留错误的 `SYSTEM` 头（如 `SYSTEM = SnS2`），运行前核对改正。

## 可选脚本 + 检查清单

就位检查（VASP 一步法）：

```bash
ls ELFCAR && grep -c "ELF" OUTCAR   # 确认 ELFCAR 生成
```

检查清单：
- [ ] INCAR 含 `LELF = .TRUE.` 且 `LREAL = .FALSE.`（绝不用 LREAL = A）。
- [ ] `PREC = Accurate`，切面无锯齿。
- [ ] `IBRION = -1`、`NSW = 0`，电子步收敛（EDIFF = 1E-6）。
- [ ] VESTA 等值面取值注明（0.7–0.85 常用）。
- [ ] 若走 QE 对比路线：pp.x `plot_num = 8`、`iflag = 3`、`output_format = 6` 配置完整，cube 已生成。
