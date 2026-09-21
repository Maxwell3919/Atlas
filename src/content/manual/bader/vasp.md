参考：

- Henkelman 组 Bader 程序（含 chgsum.pl 说明）：<http://theory.cm.utexas.edu/henkelman/code/bader/>
- VASP wiki INCAR 标签总表：<https://www.vasp.at/wiki/index.php/Category:All_INCAR_Tags>

## Bader 电荷分析

Bader 分析把空间电荷沿零通量面（∇ρ·n = 0）划分给各原子，每个原子分到的电子数 Q_Bader 与赝势价电子数 ZVAL 相减即净转移电荷 Δq = ZVAL − Q_Bader。赝势只显式处理价电子，直接对 CHGCAR 积分会在原子核附近切错分区——所以要把 AECCAR0（芯）与 AECCAR2（自洽价）叠加成全电子密度，作为剖分参考。

下面是一次完整的真实操作记录：Sc2C/ZrCl2 异质结超胞（6 原子：Zr C Cl Sc，1 1 2 2），价电子总数 52。

### 准备输入文件

从已收敛的 ../scf 复制基准文件；WAVECAR 可选，拷了它续算只需几步：

```bash
[<user>@<cluster> vasp]$ cd <工作目录>/vasp/bader

[<user>@<cluster> bader]$ cp ../scf/POSCAR ../scf/POTCAR ../scf/KPOINTS ../scf/INCAR ../scf/script_std ./

[<user>@<cluster> bader]$ cp ../scf/WAVECAR ./
```

### INCAR

INCAR 直接继承 ../scf，只加两行关键参数——LAECHG = .TRUE. 输出全电子电荷，PREC = Accurate 提高网格精度：

```bash
[<user>@<cluster> bader]$ cat > INCAR <<'EOF'
SYSTEM = Sc2C_ZrCl2_bader
   LPLANE = .TRUE.
   NPAR = 4
   ISTART = 0
   LWAVE = F
   LCHARG = T
   LCORR = T
   LAECHG = T              ! 输出 AECCAR0（芯）与 AECCAR2（价）
   PREC = Accurate         ! 密集 FFT 网格，提高积分精度
   LREAL = A
   LASPH = T
   LORBIT = 11
   ISIF = 2
   IBRION = -1
   ENCUT = 520
   GGA = PE
   VOSKOWN = 1
   EDIFF = 1E-6
   NELM = 160
   AMIX = 0.1
   BMIX = 0.0001
   MAXMIX = 80
   LMAXMIX = 4
   IVDW = 11
   ALGO = N
   ISMEAR = 0
   SIGMA = 0.05
EOF
```

ISTART 仍是 0——真实记录里提交前才发现：拷了 WAVECAR 却写 0，VASP 会从头自洽。改掉：

```bash
[<user>@<cluster> bader]$ sed -i 's/ISTART =      0/ISTART =      1/g' INCAR
```

### 提交脚本与作业

script_std 继承自 ../scf，进程数按配额改：

```bash
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

# unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 16 <vasp 路径>/vasp_std > out
```

```bash
[<user>@<cluster> bader]$ sbatch script_std
Submitted batch job 18108

[<user>@<cluster> bader]$ watch -n 1 squeue
```

### 结束后验收

```bash
[<user>@<cluster> bader]$ ls
AECCAR0  CONTCAR         INCAR           OUTCAR  REPORT
AECCAR1  DOSCAR          KPOINTS         PCDAT   script_std
AECCAR2  EIGENVAL        OSZICAR         POSCAR  vasprun.xml
CHG      _err.18108.log  out             POTCAR  WAVECAR
CHGCAR   IBZKPT          _out.18108.log  PROCAR  XDATCAR
```

判读：AECCAR0（芯）与 AECCAR2（价）出现，说明 LAECHG 生效；AECCAR1 是初猜密度，不参与求和。

### 第一次失败：chgsum.pl 不存在

```bash
[<user>@<cluster> bader]$ chgsum.pl AECCAR0 AECCAR2
bash: chgsum.pl: command not found...

[<user>@<cluster> bader]$ bader CHGCAR -ref CHGCAR_sum

   GRID BASED BADER ANALYSIS  (Version 1.05 08/19/23)

   DENSITY-GRID:   56 x  56 x 588
   RUN TIME:    0.62 SECONDS
 forrtl: No such file or directory
 forrtl: severe (29): file not found, unit 100, file <工作目录>/bader/CHGCAR_sum
 ...（Fortran 堆栈略）
[<user>@<cluster> bader]$
```

判读：bader 本体在，但 chgsum.pl 没装；缺 CHGCAR_sum 时程序在读参考文件这一步直接 forrtl severe (29) 退出。

### 用 python3 逐点求和

chgsum.pl 的逻辑只是同网格点逐点相加，python3 能做：

```bash
[<user>@<cluster> bader]$ python3 - << 'EOF'
f0 = open("AECCAR0", "r")
f2 = open("AECCAR2", "r")
out = open("CHGCAR_sum", "w")
for line0 in f0:
    line2 = f2.readline()
    out.write(line0)
    tokens = line0.strip().split()
    if len(tokens) == 3 and all(t.isdigit() for t in tokens):
        nx, ny, nz = map(int, tokens)
        break
total_points = nx * ny * nz
print(f"Grid size: {nx} x {ny} x {nz}, Total points: {total_points}")
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
f0.close()
f2.close()
out.close()
print("CHGCAR_sum generated successfully!")
EOF
Grid size: 56 x 56 x 588, Total points: 1843968
CHGCAR_sum generated successfully!
```

### 运行 Bader 分析

```bash
[<user>@<cluster> bader]$ bader CHGCAR -ref CHGCAR_sum

   GRID BASED BADER ANALYSIS  (Version 1.05 08/19/23)
   ...（读文件段同上）
   REFINING AUTOMATICALLY
   ITERATION: 1
   EDGE POINTS:        877273
   REASSIGNED POINTS:   73752

   RUN TIME:      10.52 SECONDS

   ...（最小距离计算段略）

   WRITING BADER ATOMIC CHARGES TO ACF.dat
   WRITING BADER VOLUME CHARGES TO BCF.dat

   NUMBER OF BADER MAXIMA FOUND:          14225
       SIGNIFICANT MAXIMA FOUND:              6
                  VACUUM CHARGE:         0.0000
            NUMBER OF ELECTRONS:       52.00000

[<user>@<cluster> bader]$
```

判读：14225 个局部极大里只有 6 个显著极大，正好等于原子数；VACUUM CHARGE = 0.0000；总电子数 52.00000 与价电子总数严格守恒。

### ACF.dat 与 ZVAL 记账

```bash
[<user>@<cluster> bader]$ cat ACF.dat
    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL
  --------------------------------------------------------------------------
     1    1.663439    0.960385   22.584788   10.850960     1.145626    17.321670
     2    0.000000    0.000000   17.435500    6.300579     1.023854    37.278704
     3   -0.000002    1.920774   24.351995    7.675786     1.249538   159.120073
     4   -0.000002    1.920774   20.600314    7.903389     1.332017    20.918173
     5   -0.000002    1.920774   16.258404    9.762359     1.010728   133.830810
     6    1.663439    0.960385   18.635111    9.506927     1.006346    10.796091
  --------------------------------------------------------------------------
     VACUUM CHARGE:               0.0000
     VACUUM VOLUME:               0.0000
     NUMBER OF ELECTRONS:        52.0000

[<user>@<cluster> bader]$ sed -n '6,7p' POSCAR
   Zr   C    Cl   Sc
      1     1     2     2

[<user>@<cluster> bader]$ grep "ZVAL" POTCAR
    POMASS =   91.224; ZVAL   =   12.000    mass and valenz
    POMASS =   12.011; ZVAL   =    4.000    mass and valenz
    POMASS =   35.453; ZVAL   =    7.000    mass and valenz
```

（第 4 行 Sc_sv 的 ZVAL = 11.000 在记录里被截断，取自下方。）

逐原子 Δq = ZVAL − Q_Bader（单位 e）：Zr 12.000 → 10.850960（Δq +1.149040）；C 4.000 → 6.300579（−2.300579）；Cl1 7.000 → 7.675786（−0.675786）；Cl2 7.000 → 7.903389（−0.903389）；Sc1 11.000 → 9.762359（+1.237641）；Sc2 11.000 → 9.506927（+1.493073）。

判读，分层守恒闭合：Sc2C 层（Sc1+Sc2+C）= +1.237641 + 1.493073 − 2.300579 = **+0.430135 e**，供电子层；ZrCl2 层（Zr+Cl1+Cl2）= +1.149040 − 0.675786 − 0.903389 = **−0.430135 e**，受电子层。两侧严格反号，层间净转移 0.430135 e，总失 +3.8797、总得 −3.8798，代数和为 0。细节：Cl2 在界面侧得电 −0.90 e 而 Bader 体积只有 20.92 Å³，Cl1 在真空侧只得 −0.68 e 却膨胀到 159.12 Å³；Sc2 紧邻界面失电 1.49 e 多于外侧 Sc1 的 1.24 e。

### 下一步

```text
SCF（CHGCAR + AECCAR0/AECCAR2）
    ↓
Bader 电荷分析        ← 本页
    ↓
差分电荷密度（空间分布） → ELF（键合定域性）
```

一个提醒：MIN DIST 是原子核到其 Bader 分割面的最小距离，若小于最近邻键长，说明零通量面切进了分子内部，分区质量可疑，需加密网格复查。
