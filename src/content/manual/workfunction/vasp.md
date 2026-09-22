参考：

- [VASP 功函数教程](https://vasp.at/wiki/Computing_the_Workfunction)
- [LVTOT](https://vasp.at/wiki/LVTOT)
- [LVHAR](https://vasp.at/wiki/LVHAR)

## 功函数

功函数 Φ = E_vac − E_F：真空静电势平台与费米能级之差。 slab 计算沿 z 做平面平均后，远离 slab 的静电势平台就是真空能级。结构处理有三件事：真空层要够厚；偶极修正中心放在 slab 中央；固定结构后还要分清这次是否重新更新电荷密度。下面旧输入的 ICHARG = 11 使用已有密度，不是重新自洽。

记录体系：SnSe2 单层 slab，保留这次输入和势能曲线，练习如何从输出中选取真空参考。

### 结构处理（slab 与偶极修正）

```bash
[bcgong@localhost wf]$ sed -n '1,5p' POSCAR
"Sn1 Se2"
   1.00000000000000
     3.8464052687627550    0.0000000000015396    0.0000000000000001
    -1.9232026344298054    3.3310846760065127   -0.0000000000000002
     0.0000000000000007   -0.0000000000000005   18.3572978035193977
```

a ≈ 3.846 Å、c ≈ 18.357 Å。仅有晶胞尺寸还不能保证真空平台足够平；需要结合原子位置和下面的势能曲线检查。DIPOL 的位置应与 slab 的实际位置对应。

### 这次保存的 INCAR

```bash
[bcgong@localhost wf]$ cat INCAR
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

ISTART = 1 读取已有 WAVECAR；ICHARG = 11 固定已有电荷密度，因此先核对 CHGCAR 的结构和计算设置。这里的 LVTOT 输出包含离子势、Hartree 势和交换关联势，不能笼统称作纯静电势。当前 VASP 官方功函数教程建议读取离子势与 Hartree 势，并检查真空区；旧文件在此保留，不能把它直接升级为推荐模板。LCORR 也不应被描述成开启偶极修正的开关，相关设置应按 LDIPOL、IDIPOL、DIPOL 逐项核对。

K 网格文件如下：

```bash
[bcgong@localhost wf]$ cat KPOINTS
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
[bcgong@localhost wf]$ sbatch script_std
```

### E-fermi 与平面平均

```bash
[bcgong@localhost wf]$ grep "E-fermi" OUTCAR | head -3
 E-fermi :  -2.4741     XC(G=0):  -3.7120     alpha+bet : -3.3624

[bcgong@localhost wf]$ head -8 PLANAR_AVERAGE.dat
#Distance(A) Planar-Average-Potential(eV)/Densitiy(e/A)
  0.0000             3.27267
  0.0656             3.27993
  0.1311             3.27892
  0.1967             3.28602
  0.2622             3.28413
  0.3278             3.28633
  0.3934             3.27903

[bcgong@localhost wf]$ sort -k2 -g PLANAR_AVERAGE.dat | tail -3
 18.1606             3.28602
  0.3278             3.28633
 18.0295             3.28633
```

![SnSe2 留存的平面平均总局域势曲线](/Atlas/figures/potential.svg)

文件有 280 个数据点，另有一行表头。端点附近的高值区域是检查真空参考的起点，不能直接用全文件最大值替代平台检查。应选取原子之外、密度足够低且势能近乎平坦的区间，并报告区间内的波动与取值方法。

旧记录取 3.2863 eV，减去 −2.4741 eV 得约 5.76 eV。这里保留这次算术读数；它仍受 LVTOT 势的选择、真空尺寸和取段方式影响，不作为已经收敛的功函数。若两侧表面不等价，两侧功函数本来也可能不同，不能把不相等一概归因于计算错误。

原目录没有留下生成 PLANAR_AVERAGE.dat 的执行记录。本页图直接读取保存的这份表，不补写一条声称当时运行过的命令。需要从 LOCPOT 重建时，应先明确所取势的分量和工具版本，再将新生成结果与原表对照。

### 下一步

```text
核对 slab 基准密度与固定结构
    ↓
核对势的分量 → LOCPOT → 平面平均
    ↓
真空区间与波动检查 → E_vac − E_F
    ↓
能带/态密度（费米能级参照下的电子结构）
    ↓
表面电荷转移 → Bader/差分电荷
```

比较不同体系时，应保持势能参考、几何约束和电子设置的定义清楚；尤其要记录真空区间与 smearing，而不是只列最后一个差值。
