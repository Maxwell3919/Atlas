[VASP：DFT+U](https://vasp.at/wiki/DFT%2BU) · [LDAUTYPE](https://vasp.at/wiki/LDAUTYPE) · [LMAXMIX](https://vasp.at/wiki/LMAXMIX) · [MAGMOM](https://vasp.at/wiki/MAGMOM)

这份 VGe₂P₄ 静态计算给 V 的 d 轨道加了 U。先把元素顺序、U 的作用轨道和程序实际采用的参数连起来，再看电子迭代有没有结束。这里使用已有的完整输入与 OUTCAR；U = 3 eV 是这份算例的选择，不能仅凭计算收敛就推广给其他结构或其他材料。

[下载本例的输入与原始输出](/Atlas/examples/vasp/vge2p4-dft-u3-files.tar.gz)。包内 `INCAR.active` 仅去除了原输入的注释，计算参数原样保留，附原文件哈希；复制为 INCAR 即可读入。归档未保存原提交脚本、CHGCAR 或 WAVECAR，因此这里使用 OUTCAR 核验已结束的 SCF，提交方法接 [SCF](/Atlas/m/scf/vasp/)。

结构准备与普通静态计算接 [结构优化](/Atlas/m/relax/vasp/) 和 [SCF](/Atlas/m/scf/vasp/)。进入复制出来的计算目录后，先读 POSCAR，而不是先改 U。

```text
[bcgong@localhost vge2p4_u3]$ head -16 POSCAR
POSCAR                                  
   1.00000000000000     
     2.8149939055363911    0.0000000000000003    0.0000000000000000
    -1.4074969527681953    2.4378562356984528   -0.0000000000000000
     0.0000000000000000   -0.0000000000000000   29.4512358517314254
   V    Ge   P 
     1     2     4
Direct
  0.0000000000000000  0.0000000000000000  0.5000000000000000
  0.6666666870000029  0.3333333429999996  0.6541508807422820
  0.6666666870000029  0.3333333429999996  0.3458491192577181
  0.6666666870000029  0.3333333429999996  0.5605945852015912
  0.6666666870000029  0.3333333429999996  0.4394054147984089
  0.3333333429999996  0.6666666870000029  0.7349860889032125
  0.3333333429999996  0.6666666870000029  0.2650139110967873
```
第六行的元素顺序是 `V Ge P`，下一行的原子数是 `1 2 4`。INCAR 中 `LDAUL`、`LDAUU`、`LDAUJ` 的三个位置都跟这个顺序对应；`MAGMOM` 则要展开成七个原子的初始磁矩。

```text
[bcgong@localhost vge2p4_u3]$ grep -Ev '^[[:space:]]*(#|$)' INCAR
SYSTEM  = VGe2P4_scf
ENCUT   = 520      # 和 relax 保持一致（暂定）
EDIFF   = 1E-6
ISMEAR  = 0
SIGMA   = 0.05
ISPIN   = 2
NELM    = 120
LCHARG  = .TRUE.
LWAVE   = .TRUE.
LDAU    = .TRUE.
LDAUTYPE= 2
LDAUL   = 2 -1 -1      # V Ge P
LDAUU   = 3.0 0.0 0.0
LDAUJ   = 0.0 0.0 0.0
MAGMOM  = 1*2.0 2*0.1 4*0.0
ISIF    = 2
LASPH   = .TRUE.
```
`LDAUTYPE = 2` 使用 Dudarev 形式，这时有意义的组合是 U − J。本例 V 的数值是 3 − 0 = 3 eV；`LDAUL = 2 -1 -1` 表示只对 V 的 d 轨道加这一项，Ge 和 P 不加。`MAGMOM = 1*2.0 2*0.1 4*0.0` 给的是初始条件，最终磁矩仍要从收敛输出读出来。

这里没有将 U = 3 eV 当成程序自动求出的数值。要确定 U 的来源，可以沿用经过验证的文献协议，也可以另做 U 的计算或敏感性研究；它与 `EDIFF` 这样的数值停止阈值是两回事。

```text
[bcgong@localhost vge2p4_u3]$ cat KPOINTS
K-Spacing Value to Generate K-Mesh: 0.025
0
Gamma
  18  18   1
0.0  0.0  0.0
```
这次固定结构 SCF 使用 Γ 中心 18 × 18 × 1 网格。拿它与不加 U 的结果比较时，还需保留相同结构、赝势、截断能、展宽和 k 网格；不同设置下的能量不能直接归因于 U。

```text
[bcgong@localhost vge2p4_u3]$ grep -A3 'LDA+U is selected' OUTCAR
 LDA+U is selected, type is set to LDAUTYPE =  2
   angular momentum for each species LDAUL =     2   -1   -1
   U (eV)           for each species LDAUU =   3.0  0.0  0.0
   J (eV)           for each species LDAUJ =   0.0  0.0  0.0
```
这段是程序读入参数后的回显，已经把 `LDAUTYPE = 2`、各元素的 l、U 与 J 写出来了。只在 INCAR 里看见 `LDAU = .TRUE.` 还不够；应当检查这一段是否与预期一致。

```text
[bcgong@localhost vge2p4_u3]$ head -8 OSZICAR
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1     0.429957043731E+03    0.42996E+03   -0.31480E+04  9072   0.172E+03
DAV:   2     0.479829596538E+01   -0.42516E+03   -0.40318E+03  9492   0.422E+02
DAV:   3    -0.349698840372E+02   -0.39768E+02   -0.39509E+02 11620   0.905E+01
DAV:   4    -0.360306295688E+02   -0.10607E+01   -0.10606E+01  9940   0.155E+01
DAV:   5    -0.360657628363E+02   -0.35133E-01   -0.35133E-01 12992   0.295E+00    0.252E+01
DAV:   6    -0.353472830584E+02    0.71848E+00   -0.19261E+01 12012   0.160E+01    0.804E+00
DAV:   7    -0.421168924339E+02   -0.67696E+01   -0.65047E+01 12572   0.145E+01    0.150E+01
```
OSZICAR 每一条 DAV 行是一次电子迭代：依次记录能量、相邻迭代能量变化、波函数残差等。它与最下面的离子步摘要是不同层次。固定几何的计算仍然会有一条 `1 F=...`，这个 1 不代表结构做过一次有效优化。

```text
[bcgong@localhost vge2p4_u3]$ tail -7 OSZICAR
DAV:  26    -0.340985351321E+02   -0.56191E-02   -0.44178E-05 11536   0.142E-02    0.177E-02
DAV:  27    -0.340991323552E+02   -0.59722E-03   -0.16916E-05 10696   0.108E-02    0.625E-03
DAV:  28    -0.340992725958E+02   -0.14024E-03   -0.44292E-06 10528   0.561E-03    0.298E-03
DAV:  29    -0.340992994665E+02   -0.26871E-04   -0.12861E-06 10248   0.323E-03    0.208E-03
DAV:  30    -0.340993026995E+02   -0.32330E-05   -0.16672E-07  8708   0.142E-03    0.115E-03
DAV:  31    -0.340993033925E+02   -0.69305E-06   -0.34108E-08  9520   0.662E-04
   1 F= -.34099303E+02 E0= -.34096946E+02  d E =-.471526E-02  mag=     0.5781
```
```text
[bcgong@localhost vge2p4_u3]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
最后一步的能量变化约 −6.93 × 10⁻⁷ eV，已经进入 `EDIFF = 1E-6` 的范围；OUTCAR 同时确认停止条件达到。末行的 `mag=0.5781` 是这份计算的最终总磁矩摘要，不能拿输入里 2.0、0.1、0.0 的初值代替它。

```text
[bcgong@localhost vge2p4_u3]$ grep -E 'free  energy|energy  without entropy|E-fermi' OUTCAR | tail -3
 E-fermi :   2.4194     XC(G=0):  -6.8213     alpha+bet : -7.9488
  free  energy   TOTEN  =       -34.09930339 eV
  energy  without entropy=      -34.09458813  energy(sigma->0) =      -34.09694576
```
`TOTEN` 是有限展宽下的自由能，`energy(sigma->0)` 是程序给出的零展宽外推量；同一比较要统一选用能量定义。这里 `E-fermi = 2.4194 eV` 只属于本份势参考，不能直接与另一份独立计算的费米能做绝对比较。

```text
[bcgong@localhost vge2p4_u3]$ tail -15 OUTCAR
  
 General timing and accounting informations for this job:
 ========================================================
  
                  Total CPU time used (sec):      124.456
                            User time (sec):      113.656
                          System time (sec):       10.800
                         Elapsed time (sec):      125.728
  
                   Maximum memory used (kb):      281700.
                   Average memory used (kb):           0.
  
                          Minor page faults:        62427
                          Major page faults:            0
                 Voluntary context switches:          847
```
程序统计段表明这份计算结束，电子收敛行说明它没有仅仅跑满 NELM。但文件里还保留了一个会影响下一步的设置：

```text
[bcgong@localhost vge2p4_u3]$ grep -E 'LMAXMIX|LORBIT' OUTCAR
   LMAXMIX     =    2 max onsite mixed and CHGCAR
   LORBIT       =      0    0 simple, 1 ext, 2 COOP (PROOUT), +10 PAW based schemes
```
本例没有显式设置 LMAXMIX，实际采用了 2；LORBIT 也采用 0。因此，这份旧 SCF 可以用来核对 DFT+U 的输入与电子收敛，但不能直接把它产生的 CHGCAR 当作一份已经准备好做固定电荷 d 轨道能带的起点。VASP 对 d 电子的 DFT+U 推荐 `LMAXMIX = 4`；要接 `ICHARG = 11` 的能带或 DOS，应在新的 SCF 目录中显式设为 4 并重新生成 CHGCAR。若要检查每个原子的局域磁矩，可同时设 `LORBIT = 11`，然后读取 OUTCAR 的 magnetization 表。

修改这些参数应保留旧结果：先用 `cp` 把原始输入复制到新目录，再用 `vi INCAR` 编辑，并用 `cat INCAR` 核对。重新运行后，应再次读取 OUTCAR 的 LMAXMIX 回显，并确认生成的 CHGCAR 与新输入对应，再接后续计算。

下一步接 [磁基态比较](/Atlas/m/magnetic-gs/vasp/)，比较不同初始磁构型最终收敛到的状态。准备好含所需局域占据矩阵的 SCF 后，再接 [能带](/Atlas/m/bands/vasp/) 或 [DOS](/Atlas/m/dos/vasp/)。

```text
确定结构、元素顺序与 U 的来源
  └─ DFT+U SCF → OUTCAR 的 l/U/J 回显 → 电子收敛
                                           ├─ 磁构型比较
                                           └─ LMAXMIX 与 CHGCAR 核验 → 能带 / DOS
```
