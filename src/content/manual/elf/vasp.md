# VASP ELF：LELF 一步法与 QE 两步对照

**参考**：[LELF 标签页](https://www.vasp.at/wiki/index.php/LELF) · [QE INPUT_PP 文档](https://www.quantum-espresso.org/Doc/INPUT_PP.html)

本页目标：对同一体系（Sc2C/ZrCl2 界面）算电子局域化函数 ELF（0–1 无量纲），VESTA 读图分析成键与孤对局域化。VASP 走一步法（静态计算直接出 ELFCAR），QE 走两步法（pw.x 自洽 + pp.x 导出 cube）作对照。

## 输入文件：VASP INCAR

从已收敛 `scf/` 复制基准文件（真实目录命令）：

```bash
cp ../scf/CONTCAR ./POSCAR
cp ../scf/POTCAR ../scf/KPOINTS ../scf/WAVECAR ../scf/CHGCAR ./
```

INCAR 原样（真实文件转录，体系行按实际体系修正）：

```fortran
SYSTEM = Sc2C_ZrCl2     ! 继承的 scf 源文件此行为复制残留的 SnS2，运行前改正
ISTART = 1              ! 读取已有的 WAVECAR
ICHARG = 1              ! 读取已有的 CHGCAR
LWAVE = .FALSE.
LCHARG = .FALSE.
LELF = .TRUE.           ! 核心开关：计算并输出 ELFCAR
LREAL = .FALSE.         ! ELF 必须在倒空间投影，禁止 LREAL=A（理由见下）
PREC = Accurate         ! 保证 FFT 网格精细，避免切面锯齿
LASPH = .TRUE.
LORBIT = 11
IBRION = -1             ! 固定离子，只做电子步
NSW = 0
ENCUT = 520
GGA = PE
VOSKOWN = 1
EDIFF = 1E-6
NELM = 60
ALGO = Normal
ISMEAR = 0
SIGMA = 0.05
IVDW = 11
LMAXMIX = 4
```

三处有明确理由，抄时不要抄丢：`LREAL = .FALSE.` 是硬要求——ELF 需要动能密度，实空间投影（`LREAL = A`）会在动能密度重构时引入噪声，等值面出现碎斑；`PREC = Accurate` 保证网格精细；`IBRION = -1`/`NSW = 0` 固定离子，ELF 只对静态构型有意义。`ISTART = 1`/`ICHARG = 1` 复用 scf 的波函数与电荷，电子步几步收完。

## 命令主线

```bash
mpirun -np <np> vasp_std > out.log 2>&1
ls ELFCAR        # 就位检查：文件生成即成
```

## QE 两步对照

pw.x 自洽后用 pp.x：第一段 namelist 计算 ELF 到中间文件（`outdir`、`filplot = 'calc_elf'`、`plot_num = 8`——8 代表 ELF），第二段转 cube。`&PLOT` 段原样：

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

```bash
pw.x < scf.in > scf.out 2>&1
pp.x < pp.in > pp.out 2>&1
```

如实说明：这段 pp.x 配置来自会话记录，集群上未见真实的 QE ELF 产物文件——把它当配置模板用，跑前按 INPUT_PP 文档核对一遍参数名。二维层状材料建议在 pp.x 里适当加密输出网格，避免真空层边界的数值发散或等值面截断伪影。QE 端 pw.x 自洽的完整输入模板待填充，SCF 本身与手册其余 QE 页同规格。

## 判读：VESTA 等值面取值

VESTA 打开 ELFCAR（或 elf.cube），Isosurface level 常用 **0.7 ∼ 0.85**（自由电子气参考值 0.5），配合 Slice Contour 做 2D 切面。读法：高值区（≥0.7）对应局域共价键/孤对；层间持续低值说明该方向无局域键——这正是插层体系结合方式的直观证据。图注必须注明所取等值面数值。

## 可信度边界（与 Bader 互补）

ELF 与 Bader 互补：Bader 按原子划分电荷量，ELF 看键的局域形态。两边共同的软肋都在赝势：ELF 对赝势类型敏感，推荐全相对论/标量模守恒（NC）或标准 USPP/PAW，个别超软势动能密度重建偶有数值噪声；VASP 一侧最典型的假阳性就是 `LREAL = A` 的碎斑——异常时先查这一项，改 `.FALSE.` 重算。网格不足（切面锯齿）用 `PREC = Accurate` 或显式调大 FFT 网格解决。

## 思考

1. `LREAL = A` 为什么只对 ELF 致命，而对总能、能带这类量无伤大雅？
2. 等值面取 0.5、0.7、0.85 三档对比看，分别强调什么结构特征？
3. 若某层间区域 ELF 高于 0.7，与 Bader 的层间转移结果矛盾吗？各自说明什么？
