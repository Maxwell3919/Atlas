参考：

- VESTA 官网：<https://jp-minerals.org/vesta/>
- [VASP LELF](https://vasp.at/wiki/LELF)

## ELF（Electron Localization Function）

ELF 在 0–1 之间度量电子定域性：约 0.5 对应自由电子气参考值，接近 1 是强定域区（共价键、孤对电子、芯区），ELF 本身不是电荷密度，接近 0 不能直接翻译成真空或低密度。本例设置 LELF = .TRUE. 输出 ELFCAR，并使用 LREAL = .FALSE.。遇到网格条纹时应同时检查网格、投影近似和可视化设置，不能仅凭图形就认定原因。

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

判读：ELFCAR 在列表里，作业日志 _out.18107.log/_err.18107.log 成对出现——这只能确认文件存在；它不能单独证明计算完成或 LREAL 是先前问题的原因。

### VESTA 出图

ELFCAR 直接拖入 VESTA：

- 3D 等值面（Properties → Isosurfaces → New）：0.5 附近是均匀电子气（金属性区域）；0.75–0.85 是强共价键或孤对电子（如 Cl 外侧的电子对）；低值区需要结合电荷密度判断。
- 2D 截面（Utilities → 2D Data Display → Slice）：用 3 个代表原子定面（如 Sc–C–Zr）或直接指定 Miller 指数（(1 1 0) / (0 0 1)），勾选 Show contour lines，色彩范围固定为 0.0–1.0，结合结构观察定域区域；不由颜色直接给键分类。

### 读取图像时保留哪些信息
+
+记录切面、等值面阈值和色标，再与原子位置、实际电荷密度对照。单一 ELF 阈值不能自动给出离子键、共价键或金属键的分类；改变色标也不能代替数值检查。
+
+更正（2026-09-22）：原文的 QE ELF 输入仅来自讨论方案，没有对应运行产物，因此已移出操作主线。这里也不再把某类赝势概括为普遍更稳，或把 LREAL 当作所有图像伪影的唯一解释。当前 VASP LELF 文档另有 NPAR 的要求，旧输入是否适用于新版本应逐项核对，不能只复制 LELF 一行。
+
+### 下一步

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

若切面出现锯齿，先检查数据网格、绘图插值与实际输入，再决定如何复算。
