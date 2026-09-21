参考：

- VESTA 官网：<https://jp-minerals.org/vesta/>
- VASP wiki INCAR 标签总表：<https://www.vasp.at/wiki/index.php/Category:All_INCAR_Tags>

## ELF（Electron Localization Function）

ELF 在 0–1 之间度量电子定域性：约 0.5 对应自由电子气参考值，接近 1 是强定域区（共价键、孤对电子、芯区），接近 0 是低密度区（层间范德华间隙、真空）。VASP 只需加 LELF = .TRUE. 一步输出 ELFCAR；核心陷阱是 LREAL——ELF 要重构动能密度，沿用 SCF 里的 LREAL = A 会引入实空间投影的网格噪声，必须改 LREAL = .FALSE.。

记录体系仍是 Sc2C/ZrCl2 异质结。当时 elf 目录已完整跑过一轮（作业 18107），本页按修正后的做法复述全流程。

### 复用 SCF 输入

已有收敛的 WAVECAR 与 CHGCAR，读入续算即可（极快，通常几分钟甚至几十秒）：

```bash
[<user>@<cluster> vasp]$ ls
bader  bands  elf  rx  scf

[<user>@<cluster> elf]$ cp ../scf/POSCAR ../scf/POTCAR ../scf/KPOINTS ../scf/CHGCAR ../scf/WAVECAR ../scf/script_std ./
```

### INCAR

```bash
[<user>@<cluster> elf]$ cat > INCAR <<'EOF'
SYSTEM = Sc2C_ZrCl2_ELF
########## about parallelation ###########
   LPLANE = .TRUE.
   NPAR = 4
   NSIM = 4
##########################################
############### about I/O ################
   ISTART = 1                ! 读取已有的 WAVECAR
   ICHARG = 1                ! 读取已有的 CHGCAR
   LWAVE = .FALSE.
   LCHARG = .FALSE.
##########################################
########### about switch control ##########
   LELF = .TRUE.             ! 核心开关：计算并输出 ELFCAR
   LREAL = .FALSE.           ! ELF 必须在倒空间投影，禁止 LREAL=A
   PREC = Accurate           ! 保证 FFT 网格精细，避免切面锯齿
   LASPH = .TRUE.
   LORBIT = 11
###########################################
############# about ionic relax ############
   IBRION = -1               ! 固定离子步，只做电子步
   NSW = 0
###########################################
########### about electron scf ############
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
###########################################
EOF
```

两个关键改动判读：LELF = .TRUE. 生成 ELFCAR；LREAL 从 SCF 模板继承的 A 改为 .FALSE.——实空间投影近似在动能密度重构时可能产生网格噪声，这是 ELF 计算与普通 SCF 的决定性差别之一。ISTART = 1 与 ICHARG = 1 配合拷来的 WAVECAR/CHGCAR，一两个电子步内完成并写出 ELFCAR。

### 提交与验收

```bash
[<user>@<cluster> elf]$ sbatch script_std

[<user>@<cluster> elf]$ watch -n 1 squeue
```

结束后目录状态（真实记录）：

```bash
[<user>@<cluster> vasp]$ ls elf/
CHG      EIGENVAL        INCAR    _out.18107.log  POTCAR      vasprun.xml
CHGCAR   ELFCAR          KPOINTS  OUTCAR          PROCAR      WAVECAR
CONTCAR  _err.18107.log  OSZICAR  PCDAT           REPORT      XDATCAR
DOSCAR   IBZKPT          out      POSCAR          script_std
```

判读：ELFCAR 在列表里，作业日志 _out.18107.log/_err.18107.log 成对出现——这一轮是修好 LREAL 之后完成的。

### VESTA 出图

ELFCAR 直接拖入 VESTA：

- 3D 等值面（Properties → Isosurfaces → New）：0.5 附近是均匀电子气（金属性区域）；0.75–0.85 是强共价键或孤对电子（如 Cl 外侧的电子对）；接近 0 是层间范德华间隙与真空。
- 2D 截面（Utilities → 2D Data Display → Slice）：用 3 个代表原子定面（如 Sc–C–Zr）或直接指定 Miller 指数（(1 1 0) / (0 0 1)），勾选 Show contour lines，色彩范围设 0.0–1.0 即可直读成键属性（离子键/共价键/金属性）。

### QE 两步对照

QE 侧是两步法：pw.x 正常自洽，再用 pp.x 提取。配置如下（出自当时的对话记录）：

```bash
&INPUTPP
   prefix = 'calc_prefix',
   outdir = './tmp',
   filplot = 'calc_elf',
   plot_num = 8        ! 8 代表 ELF
/
&PLOT
   nfile = 1,
   filepp(1) = 'calc_elf',
   weight(1) = 1.0,
   iflag = 3,          ! 3 代表 3D 体系
   output_format = 6,  ! 6 代表 Gaussian cube 格式（VESTA 友好）
   fileout = 'elf.cube'
/
```

可信度边界：这份 pp.x 配置只是对话记录里的方案，集群上没有对应的 QE ELF 产物文件——它没有经过实测验证，照抄前先在 QE 官方文档里核对 plot_num/iflag/output_format 的当前定义。二维层状材料建议在 pp.x 中适当加密输出网格，避免真空层边界的数值发散或等值面截断伪影。

### 可信度边界

- LREAL = A 是本页最大的坑：ELF 出现网格状条纹或锯齿时，第一嫌疑就是它，改 .FALSE. 重算。
- 赝势类型影响动能密度重构质量：USPP/个别超软势偶有数值噪声，PAW/NC 更稳。
- 等值面取值 0.7–0.85 是成键分析的经验起点，不同体系要按图微调，不是通用标准。
- 自旋极化体系默认输出总 ELF；分自旋时 QE 侧要在 pp.x 里显式指定 spin_component。
- ELF 判断的是"定域性"，与电荷转移量（见 Bader 页）是两个视角，结论互证而非互相替代。

### 下一步

```text
SCF（WAVECAR + CHGCAR 复用）
    ↓
ELF：LELF = .TRUE. + LREAL = .FALSE.   ← 本页
    ↓
VESTA 等值面/切面
    ↓
差分电荷密度（电荷重分布的空间图）
    ↓
Bader 电荷（原子分配的定量记账）
```

一个提醒：ELF 对网格敏感，切面出现锯齿先加 FFT 网格或改 LREAL，再谈物理。
