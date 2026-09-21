# VASP Bader 电荷：LAECHG 全链与层间转移记账

**参考**：[LAECHG 标签页](https://www.vasp.at/wiki/index.php/LAECHG) · [Bader 分析代码主页](https://theory.cm.utexas.edu/henkelman/code/bader/)

本页目标：在已收敛 scf 之上重算一套带全电荷输出的静态计算，跑 Henkelman 组 Bader 划分，得到逐原子电荷，并按层归并出界面转移量。案例体系：Sc2C/ZrCl2 界面，6 原子原胞。

## Bader 需要什么电荷密度（先讲清楚）

普通 scf 只输出价电子电荷（CHGCAR）；Bader 要**全电荷密度**（价 + 芯），对应两个文件：`AECCAR0`（芯）、`AECCAR2`（自洽价）。两者叠加成参考密度 `CHGCAR_sum`。两点工程要求：`PREC = Accurate` 保证精细 FFT 网格（本例实测 56×56×588），划分精度直接受益；`LAECHG = .TRUE.` 的代价是多写两份全网格文件，原胞级别无感，大超胞要预留磁盘。

## 输入文件：INCAR

准备动作只有复制与改两行（真实目录方案）：

```bash
cp ../scf/POSCAR ../scf/POTCAR ../scf/KPOINTS ../scf/WAVECAR ./
```

```fortran
SYSTEM = Sc2C_ZrCl2     ! 源文件此处是复制残留的 SYSTEM = SnS2，运行前改回本体系
LPLANE = .TRUE.
NPAR = 4
NSIM = 4
ISTART = 1              ! 拷了 WAVECAR，几步即可完成自洽（原文件为 0）
LWAVE = F               ! whether write WAVECAR
LCHARG = T              ! whether write CHGCAR and CHG
LAECHG = T              ! 开启全电荷输出：AECCAR0 + AECCAR2
PREC = Accurate         ! 精细 FFT 网格，Bader 积分精度的前提
LREAL = A
LASPH = T
LORBIT = 11
ISIF = 2
IBRION = -1             ! 固定离子
NSW = 0
```

其余参数（EDIFF 等）与 scf 保持一致。POTCAR 用标准 PBE PAW 文件，内容不引用，记账时用 ZVAL 查询（见后）。

## 命令主线

```bash
mpirun -np <np> vasp_std > out.log 2>&1
chgsum.pl AECCAR0 AECCAR2        # 标准：生成 CHGCAR_sum
bader CHGCAR -ref CHGCAR_sum
```

## 事故时间线：bader 读完网格才崩溃

第一次运行直接报错（真实输出）：

```text
GRID BASED BADER ANALYSIS (Version 1.05 08/19/23)
OPEN ... CHGCAR
DENSITY-GRID: 56 x 56 x 588
CLOSE ... CHGCAR
RUN TIME: 0.62 SECONDS
forrtl: severe (29): file not found, unit 100, file <工作目录>/bader/CHGCAR_sum
```

现象：bader 正常读完 CHGCAR 全网格才崩。定位：`-ref` 指向的 `CHGCAR_sum` 不存在。根因：环境里没有 chgsum.pl（Henkelman 组的外部 perl 脚本），第一步叠加从未成功。验证根因：`ls CHGCAR_sum` 不存在。修复：不装任何东西，用 python3 逐点求和替代（本页唯一工具，文件名按你的目录改；跑完核对输出行数应等于网格点数）：

```bash
python3 - << 'EOF'
f0 = open("AECCAR0", "r"); f2 = open("AECCAR2", "r")
out = open("CHGCAR_sum", "w")
for line0 in f0:                      # 复制头部，直到网格维度行
    line2 = f2.readline(); out.write(line0)
    tok = line0.strip().split()
    if len(tok) == 3 and all(t.isdigit() for t in tok):
        nx, ny, nz = map(int, tok); break
total = nx * ny * nz
print(f"Grid size: {nx} x {ny} x {nz}, Total points: {total}")
cnt, buf = 0, []
while cnt < total:                    # 逐点相加
    v0 = f0.readline().strip().split(); v2 = f2.readline().strip().split()
    if not v0 or not v2: break
    for a, b in zip(v0, v2):
        buf.append(f"{float(a)+float(b):18.11E}"); cnt += 1
        if len(buf) == 5: out.write(" " + " ".join(buf) + "\n"); buf = []
if buf: out.write(" " + " ".join(buf) + "\n")
print("CHGCAR_sum generated successfully!")
EOF
```

重跑 `bader CHGCAR -ref CHGCAR_sum` 成功（真实输出节选）：

```text
NUMBER OF BADER MAXIMA FOUND: 14225
SIGNIFICANT MAXIMA FOUND: 6
VACUUM CHARGE: 0.0000
NUMBER OF ELECTRONS: 52.00000
```

## 判读：ACF.dat + ZVAL 记账

```bash
cat ACF.dat
```

```text
# X Y Z CHARGE MIN DIST ATOMIC VOL
1 1.663439 0.960385 22.584788 10.850960 1.145626 17.321670
6 1.663439 0.960385 18.635111  9.506927 1.006346 10.796091
```

```bash
grep "ZVAL" POTCAR      # 本例：Zr 12 / C 4 / Cl 7 / Sc 11
```

逐原子 Δq = CHARGE − ZVAL（正=失电子，负=得电子）：

```text
Zr  10.850960-12=+1.149040   C   6.300579- 4=-2.300579
Cl   7.675786- 7=-0.675786   Cl  7.903389- 7=-0.903389
Sc   9.762359-11=+1.237641   Sc  9.506927-11=+1.493073
```

按层归并：Sc2C 层（Sc1+Sc2+C）= **+0.430135 e**（供电子层）；ZrCl2 层（Zr+Cl1+Cl2）= **−0.430135 e**（受电子层）——正负严格闭合。

守恒判据：ACF.dat 末行 `NUMBER OF ELECTRONS`（52.0000）与 `grep "NELECT" OUTCAR` 一致，误差 < 0.001 e；`VACUUM CHARGE = 0` 且 SIGNIFICANT MAXIMA 数 = 原子数（本例 6），说明真空区没分出假极大。

## 思考

1. 为什么 Bader 必须用 AECCAR0+AECCAR2 的和做参考，直接用 CHGCAR 会偏在哪？
2. `LREAL = A` 与 `PREC = Accurate` 组合下网格是 56×56×588，若 PREC 改 Normal 会发生什么？
3. 分层归并的原子 z 坐标依据来自哪个文件？
