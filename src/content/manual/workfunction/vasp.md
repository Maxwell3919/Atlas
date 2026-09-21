参考：

- VASP wiki INCAR 标签总表：<https://www.vasp.at/wiki/index.php/Category:All_INCAR_Tags>

## 功函数

功函数 Φ = E_vac − E_F：真空静电势平台与费米能级之差。 slab 计算沿 z 做平面平均后，远离 slab 的静电势平台就是真空能级。结构处理有三件事：真空层要够厚；偶极修正中心放在 slab 中央；结构固定（NSW = 0、IBRION = −1）只做电子自洽。

记录体系：SnSe2 单层 slab，下面全部输入与数值为 SSH 只读实取的真实文件与真实输出。

### 结构处理（slab 与偶极修正）

```bash
[<user>@<cluster> wf]$ sed -n '1,5p' POSCAR
"Sn1 Se2"
   1.00000000000000
     3.8464052687627550    0.0000000000015396    0.0000000000000001
    -1.9232026344298054    3.3310846760065127   -0.0000000000000002
     0.0000000000000007   -0.0000000000000005   18.3572978035193977
```

判读：a ≈ 3.846 Å、c ≈ 18.357 Å——单层 slab 厚约 7 Å，真空约 10 Å，两侧真空互联，保证势能平台有干净的平坦段。偶极修正沿 z：IDIPOL = 3，修正中心 DIPOL = 0.5 0.5 0.5 放胞中心（slab 居中时即 slab 中央），避免表面偶极在周期镜像间引起锯齿状的势能台阶。NSW = 0 配 IBRION = −1 固定离子；INCAR 里残留的 EDIFFG = −0.01、ISIF = 2 在固定结构下不参与迭代（模板残留行）。

### INCAR（SSH 实取全文）

```bash
[<user>@<cluster> wf]$ cat INCAR
SYSTEM = SnSe2 wf   # SnSe2 Slab 功函数计算 (Work Function)

##################################################
# 并行控制
##################################################
LPLANE  = .TRUE.
NPAR    = 4
NSIM    = 4

##################################################
# I/O 控制
##################################################
ISTART  = 1
ICHARG  = 11
LWAVE   = .TRUE.
LCHARG  = .TRUE.
LVTOT   = .TRUE.
LCORR   = .TRUE.
LASPH   = .TRUE.
LORBIT  = 11

##################################################
# 离子部分（固定结构）
##################################################
NSW     = 0
IBRION  = -1
ISIF    = 2
EDIFFG  = -0.01
LDIPOL  = .TRUE.
IDIPOL  = 3
DIPOL   = 0.5 0.5 0.5

##################################################
# 电子自洽(SCF)参数
##################################################
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

##################################################
# 混合器参数（slab加快收敛）
##################################################
AMIX     = 0.1
BMIX     = 0.0001
AMIX_MAG = 0.4
BMIX_MAG = 0.0001
MAXMIX   = 80
LMAXMIX  = 4
```

逐段判读：ISTART = 1 复用 WAVECAR；ICHARG = 11 是非自洽方案——读入已有 CHGCAR 固定密度、只解 Kohn–Sham 本征值，费米能级与静电势都来自这份密度，前提是那份 CHGCAR 用完全相同的 ENCUT/网格/结构生成。LVTOT = .TRUE. 输出 LOCPOT（静电势），LCORR = .TRUE. 把偶极修正项计入势能文件——少这一项，E_vac 会差一个台阶。AMIX = 0.1 / BMIX = 1e-4 / MAXMIX = 80 是 slab 类体系加速收敛的常用组合。K 网格由间距自动生成：

```bash
[<user>@<cluster> wf]$ cat KPOINTS
K-Spacing Value to Generate K-Mesh: 0.010
0
Gamma
  33  33   1
0.0  0.0  0.0
```

### 提交

script_std 与 Bader 页同款（进程数不同）：

```bash
mpirun -np 32 <vasp 路径>/vasp_std > out
```

```bash
[<user>@<cluster> wf]$ sbatch script_std
```

### E-fermi 与平面平均

```bash
[<user>@<cluster> wf]$ grep "E-fermi" OUTCAR | head -3
 E-fermi :  -2.4741     XC(G=0):  -3.7120     alpha+bet : -3.3624

[<user>@<cluster> wf]$ head -8 PLANAR_AVERAGE.dat
#Distance(A) Planar-Average-Potential(eV)/Densitiy(e/A)
  0.0000             3.27267
  0.0656             3.27993
  0.1311             3.27892
  0.1967             3.28602
  0.2622             3.28413
  0.3278             3.28633
  0.3934             3.27903

[<user>@<cluster> wf]$ sort -k2 -g PLANAR_AVERAGE.dat | tail -3
 18.1606             3.28602
  0.3278             3.28633
 18.0295             3.28633
```

判读：PLANAR_AVERAGE.dat 共 281 行，步长 0.0656 Å = c(18.3573 Å)/280。slab 居中时 z = 0 与 z = c 相邻，是同一片真空的两个周期镜像——所以最高值同时出现在 0.3278 与 18.0295，互为印证。取平台最高点 E_vac = 3.2863 eV（VASP wiki 惯例：以平台最大值作真空能级），则

Φ = E_vac − E_F = 3.2863 − (−2.4741) ≈ 5.76 eV。

（若两端平台数值不一致，说明 slab 有净偶极未修正或真空层不够厚，先回头检查 IDIPOL/DIPOL 再读数。）

平面平均的生成：LOCPOT 在目录里，PLANAR_AVERAGE.dat 由平面平均脚本生成；当时目录中没有留下该脚本的执行记录，生成命令 待填充。

### QE 对照一句

QE 侧同一件事的做法：pp.x 提取静电势（plot_num = 1）后用 average.x 做平面平均，同样取平台减 E_F；二维体系配合假设孤立边界时注意平面平均的取段仍要落在真空区。

### 下一步

```text
slab SCF（固定结构 + 偶极修正）
    ↓
LVTOT → LOCPOT → 平面平均
    ↓
E_vac − E_F = Φ      ← 本页
    ↓
能带/态密度（费米能级参照下的电子结构）
    ↓
表面电荷转移 → Bader/差分电荷
```

一个提醒：Φ 是"态密度参照下的差值"——E_F 随 smearing 参数略有移动，比较不同体系的 Φ 时必须用同一 ISMEAR/SIGMA 与同一套修正设置。
