## 需要 / 产出

- 前置：已收敛的 `scf/` 目录（POSCAR/POTCAR/KPOINTS/WAVECAR/CHGCAR 齐全）。
- 产出：`ACF.dat` 中各原子 Bader 电荷，结合 POTCAR 价电子数（ZVAL）得到逐原子电荷转移 Δq，并按层归并（本例 Sc2C/ZrCl2 界面层间转移 ≈ ±0.4301 e，守恒闭合）。

## 本步与相邻步骤不同之处

- 与普通 scf 的差别：scf 只输出价电子电荷（CHGCAR）；Bader 分析需要全电荷密度（价 + 芯），因此必须加 `LAECHG = .TRUE.` 输出 `AECCAR0`（芯）与 `AECCAR2`（价），并把网格精度提到 `PREC = Accurate`。
- 与差分电荷的差别：差分电荷是三套计算的电荷密度相减；Bader 是单套计算后的实空间电荷划分积分，输出按原子归并的电荷。

## 参数（只列本步）

- 新增/修改（在 scf INCAR 基础上）：`LAECHG = .TRUE.`、`PREC = Accurate`、`NSW = 0`、`IBRION = -1`；若拷贝了 WAVECAR 可将 `ISTART = 1`（原文件为 0），几步即可完成自洽。
- 赝势用标准 PBE PAW 文件（POTCAR 本身不在此引用；用 TITEL/ZVAL 核对，见下）。

## 命令与输出

1. 准备目录（从已收敛 scf 复制基准文件）：

```bash
cp ../scf/POSCAR ../scf/POTCAR ../scf/KPOINTS ../scf/INCAR ../scf/script_std ./
cp ../scf/WAVECAR ./   # 可选，加速电子步收敛
```

2. INCAR 原样（会话中 `cat INCAR` 转录，注释行截取至离子弛豫段；`SYSTEM` 行原文件为复制残留的 `SYSTEM = SnS2`，实际体系为 ZrCl2/Sc2C 界面，此处改用正确体系名）：

```fortran
SYSTEM = Sc2C_ZrCl2
LPLANE = .TRUE.
NPAR = 4
NSIM = 4
ISTART = 0          ! job : 0-new 1-cont 2-samecut
LWAVE = F           ! whether write WAVECAR
LCHARG = T          ! whether write CHGCAR and CHG
LAECHG = T
PREC = Accurate
LREAL = A
LASPH = T
LORBIT = 11
ISIF = 2
IBRION = -1         ! -1-no update 0-MD 1-quasi-New 2-CG
NSW = 0
```

3. 叠加全电荷密度（标准做法用 Henkelman 组 chgsum.pl）：

```bash
chgsum.pl AECCAR0 AECCAR2   # 生成 CHGCAR_sum
bader CHGCAR -ref CHGCAR_sum
```

bader 主输出（节选）：

```text
GRID BASED BADER ANALYSIS (Version 1.05 08/19/23)
DENSITY-GRID: 56 x 56 x 588
RUN TIME: 0.62 SECONDS
NUMBER OF BADER MAXIMA FOUND: 14225
SIGNIFICANT MAXIMA FOUND: 6
VACUUM CHARGE: 0.0000
NUMBER OF ELECTRONS: 52.00000
```

## 后处理

- `cat ACF.dat`，`CHARGE` 列即各原子 Bader 电荷（本例 6 原子，节选）：

```text
# X Y Z CHARGE MIN DIST ATOMIC VOL
1 1.663439 0.960385 22.584788 10.850960 1.145626 17.321670
6 1.663439 0.960385 18.635111  9.506927 1.006346 10.796091
```

- 逐原子转移量 Δq = Bader CHARGE − ZVAL，ZVAL 用 `grep "ZVAL" POTCAR` 查（本例 Zr 12 / C 4 / Cl 7 / Sc 11）：

```text
Zr  10.850960 - 12 = +1.149040     C   6.300579 -  4 = -2.300579
Cl   7.675786 -  7 = -0.675786     Cl  7.903389 -  7 = -0.903389
Sc   9.762359 - 11 = +1.237641     Sc  9.506927 - 11 = +1.493073
```

- 符号约定：Δq > 0 失电子（金属原子 Sc、Zr）；Δq < 0 得电子（C、Cl）。
- 按层归并：Sc2C 层（Sc1+Sc2+C）= +1.237641 + 1.493073 − 2.300579 = **+0.430135 e**（供电子层）；ZrCl2 层（Zr+Cl1+Cl2）= +1.149040 − 0.675786 − 0.903389 = **−0.430135 e**（受电子层），层间转移守恒闭合。

## 失败与假阳性

- `chgsum.pl` 缺失时直接跑 bader 会报 `forrtl: severe (29): file not found ... CHGCAR_sum`——bader 本身读完网格才崩溃，容易被误判为网格问题；先确认 CHGCAR_sum 是否生成。
- 守恒校验：`ACF.dat` 末行 `NUMBER OF ELECTRONS` 必须与体系总价电子数（`grep "NELECT" OUTCAR`）严格一致（误差一般小于 0.001 e）；本例 52.0000 e。
- 复制的 INCAR 可能带着错误残留的 `SYSTEM` 头（如 `SYSTEM = SnS2`），不影响力学结果但会造成档案混乱，运行前核对一次。
- 有真空层的 slab 中 Bader 可能给真空区分出假极大：检查 `VACUUM CHARGE`（本例 0.0000）与 `SIGNIFICANT MAXIMA` 数目是否等于原子数（本例 6）。

## 可选脚本 + 检查清单

chgsum.pl 缺失时的逐点求和替代（python3 heredoc，会话原样，输出 `Grid size: 56 x 56 x 588, Total points: 1843968`）：

```bash
python3 - << 'EOF'
import sys
f0 = open("AECCAR0", "r")
f2 = open("AECCAR2", "r")
out = open("CHGCAR_sum", "w")
# 1. 复制头部结构信息（直到网格维度行）
for line0 in f0:
    line2 = f2.readline()
    out.write(line0)
    tokens = line0.strip().split()
    if len(tokens) == 3 and all(t.isdigit() for t in tokens):
        nx, ny, nz = map(int, tokens)
        break
total_points = nx * ny * nz
print(f"Grid size: {nx} x {ny} x {nz}, Total points: {total_points}")
# 2. 逐点相加电荷密度数据
count = 0
line_buf = []
while count < total_points:
    val0 = f0.readline().strip().split()
    val2 = f2.readline().strip().split()
    if not val0 or not val2:
        break
    for v0, v2 in zip(val0, val2):
        s = float(v0) + float(v2)
        line_buf.append(f"{s:18.11E}")
        count += 1
        if len(line_buf) == 5:
            out.write(" " + " ".join(line_buf) + "\n")
            line_buf = []
if line_buf:
    out.write(" " + " ".join(line_buf) + "\n")
f0.close(); f2.close(); out.close()
print("CHGCAR_sum generated successfully!")
EOF
```

检查清单：
- [ ] INCAR 含 `LAECHG=.TRUE.` 与 `PREC = Accurate`，`NSW = 0`、`IBRION = -1`。
- [ ] `AECCAR0`/`AECCAR2` 已生成，CHGCAR_sum 网格与 CHGCAR 一致。
- [ ] `NUMBER OF ELECTRONS`（ACF.dat）与 `NELECT`（OUTCAR）守恒。
- [ ] `VACUUM CHARGE = 0` 且 SIGNIFICANT MAXIMA 数等于原子数。
- [ ] 逐原子 Δq 表与 ZVAL 对应无误，分层求和正负守恒。
