[VASP：OUTCAR 输出](https://vasp.at/wiki/OUTCAR) · [VASP：展宽与能量选择](https://vasp.at/wiki/Smearing_technique) · [VASP：IVDW 色散修正](https://vasp.at/wiki/IVDW) · [Jung 等：剥离能与参考态](https://arxiv.org/abs/1805.04527)

一个六层 slab 的最上面一层被逐渐抬高，能量会怎样变化？这里读取一组已经存在的 HfI₂ 固定结构单点：位移零点与 2–20 Å 共 20 个完整结果。另有 7 个目录缺少完整电子收敛或正常结束记录，单独列出，图中没有为它们补数。

[下载本例原始输入、OUTCAR、提取与绘图脚本](/Atlas/examples/hfi2-frozen20-files.tar.gz)，解压为 `hfi2-frozen20`。包内 `raw/` 保留各目录的实际文件，电子失败的长标准输出以 `out.gz` 保存；读取能量与验收使用 OUTCAR。重新提取已有结果不需要 VASP，重新计算则需要自行准备有权限的匹配 POTCAR。

## 先确认这是什么结构

进入整理后的目录，先看位移零点的结构头：

```console
[bcgong@localhost hfi2-frozen20]$ head -n 12 raw/scf_eq/POSCAR
HfI2_from_ZrBr2_ClE_scf_eq
   1.00000000000000     
     3.5392721285805808   -0.0000000000003520    0.0000000000000000
    -1.7696360642408731    3.0650995742385150   -0.0000000000000000
    -0.0000000000000000    0.0000000000000001   82.1873167285724548
   I   Hf
     12     6
Direct
  0.0000000000000000  0.0000000000000000  0.0623995784225782
 -0.0000000000000000 -0.0000000000000000  0.1069198184137017
  0.6666666670000012  0.3333333329999988  0.1462730983045202
  0.6666666670000012  0.3333333329999988  0.1907129027046066
[bcgong@localhost hfi2-frozen20]$
```

元素行是 I、Hf，个数为 12、6，共 18 个原子，对应六个 I–Hf–I 层。标题中的 `from_ZrBr2` 保留了原型构造痕迹。这一组没有附带已通过验收的 HfI₂ 结构优化结果，所以 `scf_eq` 只作为**位移零点**，不能根据目录名宣称它已经是平衡结构。

实际第三晶格长度为 82.187316728572 Å，面内面积从前两根晶格矢量的叉积得到：

```text
A = |a1 × a2| = 10.848221494426 Å²
```

原子坐标按 POSCAR 顺序编号。每个位移点只移动第 11、12、18 号原子，也就是最上层的两个 I 与一个 Hf；其余 15 个原子保持原位。提取程序实际比较了所有接受点的晶胞、元素、原子个数与逐原子坐标，确认移动的是这一整层。

位移 d 的定义是相对 `scf_eq` 沿笛卡尔 z 方向增加的长度，不是两层之间的实际间隙。对于本例沿 z 的第三晶格矢量，分数坐标改变量为：

```text
Δz_fractional = d / 82.18731672857245
```

如果复制这个体系准备新的位移点，可用 `cp` 复制原输入，再在 `vi POSCAR` 中修改同一组三个原子的 z 分数坐标，保存后核对所有坐标。移动后的原子不单独弛豫；因此下面得到的是这份明确冻结几何的分离曲线，尚不是充分弛豫材料的剥离能。

## 同一套单点设置贯穿所有接受点

这批文件使用 18×18×1 Γ 网格：

```console
[bcgong@localhost hfi2-frozen20]$ cat raw/scf_eq/KPOINTS
K-Spacing Value to Generate K-Mesh: 0.020
0
Gamma
  18  18   1
0.0  0.0  0.0
[bcgong@localhost hfi2-frozen20]$
```

`1` 是真空方向的采样数；面内 18×18 对应本例较小的面内晶胞。它是一套实际使用的网格，本组没有提供改变它之后的成对能量差对照。

<details>
<summary>位移零点的完整原始 INCAR</summary>

```console
[bcgong@localhost hfi2-frozen20]$ cat raw/scf_eq/INCAR
SYSTEM = SnS2

########## about parallelation ###########
   LPLANE =.TRUE.
   NPAR = 4
   NSIM = 4
##########################################

############### about I/O ################
   ISTART =      0    job   : 0-new  1-cont  2-samecut
#  ICHARG =      1    charge: 1-file 2-atom 10+ const
##########################################

########### about switch control ##########
   LWAVE = F                 whether write WAVECAR
   LCHARG = T                whether write CHGCAR and CHG
#  LVTOT = T                 whether write LOCPOT
   LCORR = T
   LREAL = A                 projection done in reciprocal space
   LASPH = T                 whether include non-spherical contributions
#  LMIXTAU = F               whether kinetic energy density through mixer
   LORBIT = 11               DOSCAR and lm decomposed PROCAR file
#  LBERRY = F                whether evaluate the Berry phase expression
#  LNONCOLLINEAR = T         whether perform non-colli-mag calculation
#  LSORBIT = F               whether perform soc calculation
#  LORBMOM = T               Whether write orbital magnetic moment
#  LDAU = T                  whether perform LDA+U calculation
#  LDAUTYPE = 2              :2-default,only(U-J)is meaningfull
#  LDAUL =   -1 -1 2          :-1=no on-site terms added;  1=p;  2=d 3=f
#  LDAUU =  0 0 3 
#  LDAUJ = 0 0 0 
#  LDAUPRINT = 0             :0=silent; 1=write occupancy matrix to OUTCAR;  2=idem 1.,plus potential matrix dumped to stdout
#  LHFCALC = F               whether perform HSE calculation
#  LOPTICS = F               whether calculates dielectric matrix
###########################################

############# about ionic relax ############
   ISIF = 2
   IBRION = -1               :-1-no update 0-MD 1-quasi-New 2-CG
#  NSW = 200                 :ionic step number
#  EDIFFG = -0.01            :break condition for ionic relaxation loop
#  PSTRESS = 50              :about external presssure
#  IDIPOL = 3                :slab calculation corrections
#  POTIM = 0.5               :dynamics-timestep relax-with default is OK
#  NBLOCK = 1                :with default is OK
#  KBLOCK = NSW              :with default is OK
#  TEBEG = 270               :start temperature for dynamics
#  TEEND = 270               :end temperature for dynamics
#  SMASS = -3                :ensemble for dynamics
###########################################

########### about electron scf ############
#  VCA =  0.75 0.25 1.00 1.00 1.00
#  NELECT = 226.5
   ENCUT = 400 eV
   GGA = PE
#  METAGGA = MBJ
   VOSKOWN = 1
   EDIFF = 1E-6              :break condition for electron scf loop
   NELMIN = 4                :min electron step
   NELM =  160               :max electron step
#  NELMDL = -6               :with default is often OK
#  GGA_COMPAT = F            
##############################################

############### about magnetic ###############
#  ISPIN = 2                 :1-without or 2-with spin polarized
#  MAGMOM =   16*0  4*3  :magnetic moment for per atom
#  SAXIS = 0 0 1             :quantisation axis for soc caiculation
#############################################

############### about mixer ###############
#  IMIX = 1
   AMIX = 0.1                 fast converge for slab,molecules,clusters
   BMIX = 0.0001
   AMIX_MAG = 0.4
   BMIX_MAG = 0.0001
   MAXMIX = 80
   LMAXMIX = 4                d-elements-4 f-elements-6
   IVDW = 11
###########################################

############### other important parameter ###############
   ALGO = N
   PREC = Accurate
#  ISYM = 2
   ISMEAR = 0                 :-5-tet -1-fermi 0-gauss
   SIGMA  = 0.05              :boadening in eV
#  NBANDS = 240               :with default is often OK
#  NEDOS = 2700
########################################################

##################k-mesh################# with default is often OK
#  NGX = 16
#  NGY = 16
#  NGZ = 16
#  NGXF = 32
#  NGYF = 32
#  NGZF = 32
########################################
[bcgong@localhost hfi2-frozen20]$
```

</details>

`SYSTEM=SnS2` 是模板标题，不能覆盖 POSCAR 与实际赝势给出的材料身份。真正进入计算的设置是 PBE、400 eV 截断、`PREC=Accurate`、`ISMEAR=0`、`SIGMA=0.05 eV`、`EDIFF=1E-6 eV` 与 `IVDW=11`。脚本核对了全部 20 个接受点，INCAR 与 KPOINTS 的文件哈希分别一致，输出中的赝势标题也一致。

`IBRION=-1`、未启用离子步的输入让每个点保持冻结坐标。`LCHARG=T` 会写密度，`LWAVE=F` 不保存用于重启的波函数；本页的能量相减只需要完整 OUTCAR，不需要把 CHGCAR 与 WAVECAR 当成必需的绘图文件。

`IVDW=11` 对应 DFT-D3 零阻尼色散修正。虽然原子不弛豫，移动层以后距离改变，色散能仍会随 d 改变，因此零点和位移点必须用同一种色散设置。若比较另一种色散模型，要在该模型下重新计算匹配的整组能量。

原 INCAR 中 `LREAL=A` 后面的英文注释把投影说成倒空间处理，这个注释不准确；该值选择自动实空间投影。这里保留原文件内容，并按实际参数解释，不依据注释判断计算方法。

原运行脚本保存在每个目录的 `script_std` 中：

```console
[bcgong@localhost hfi2-frozen20]$ cat raw/scf_eq/script_std
#!/bin/bash



#SBATCH -o _out.%j.log

#SBATCH -e _err.%j.log



#unlimit memory

ulimit -s unlimited

ulimit -l unlimited



# load path

source /data/intel/oneapi/setvars.sh



cd $SLURM_SUBMIT_DIR



mpirun -np 16  <vasp_bin>/vasp_std > out
[bcgong@localhost hfi2-frozen20]$
```

标准输出确认这些历史单点实际使用了 16 个进程。脚本没有把申请进程数写成 SBATCH 参数，复算时应明确申请与 `-np 16` 对应的资源，例如 `sbatch --nodes=1 --ntasks=16 script_std`，并根据当前队列保留公共节点所需的空闲资源。本次整理只读取这些已存在结果，没有重新提交这一系列任务。

## 能搜到能量，不等于这一点可以进入曲线

`scf_eq/out` 开头记录了程序版本、并行数与体系规模：

```console
[bcgong@localhost hfi2-frozen20]$ head -n 30 raw/scf_eq/out
 running on   16 total cores
 distrk:  each k-point on   16 cores,    1 groups
 distr:  one band on    4 cores,    4 groups
 using from now: INCAR     
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 POSCAR found type information on POSCAR  I  Hf
 POSCAR found :  2 types and      18 ions
 scaLAPACK will be used
 LDA part: xc-table for Pade appr. of Perdew

 ----------------------------------------------------------------------------- 
|                                                                             |
|           W    W    AA    RRRRR   N    N  II  N    N   GGGG   !!!           |
|           W    W   A  A   R    R  NN   N  II  NN   N  G    G  !!!           |
|           W    W  A    A  R    R  N N  N  II  N N  N  G       !!!           |
|           W WW W  AAAAAA  RRRRR   N  N N  II  N  N N  G  GGG   !            |
|           WW  WW  A    A  R   R   N   NN  II  N   NN  G    G                |
|           W    W  A    A  R    R  N    N  II  N    N   GGGG   !!!           |
|                                                                             |
|      One of the lattice vectors is very long (>50 A), but AMIN is rather    |
|      large. This can spoil convergence since charge sloshing might occur    |
|      along the long lattice vector. If problems with convergence are        |
|      observed, try to decrease AMIN to a smaller values (e.g. 0.01).        |
|      Note: this warning only applies if the selfconsistency cycle is used.  |
|                                                                             |
 ----------------------------------------------------------------------------- 

 POSCAR, INCAR and KPOINTS ok, starting setup
 FFT: planning ...
[bcgong@localhost hfi2-frozen20]$
```

原输出也提醒第三晶格很长、混合参数可能引发 charge sloshing。这个警告保留在包中。对已经结束的点，继续检查它实际如何收敛；若某点随后电子发散，不能因为其它目录正常就一并接收。

先看零点最后几次电子步：

```console
[bcgong@localhost hfi2-frozen20]$ tail -n 5 raw/scf_eq/OSZICAR
DAV:  18    -0.102318541915E+03    0.63870E-05   -0.27894E-06  7576   0.410E-03    0.203E-01
DAV:  19    -0.102318465570E+03    0.76346E-04   -0.18776E-04  8160   0.381E-02    0.120E-01
DAV:  20    -0.102318474337E+03   -0.87675E-05   -0.94614E-05  8392   0.203E-02    0.692E-02
DAV:  21    -0.102318473687E+03    0.65089E-06   -0.94136E-06  7480   0.822E-03
   1 F= -.10779327E+03 E0= -.10779327E+03  d E =-.877719E-06
[bcgong@localhost hfi2-frozen20]$
```

再看完整 OUTCAR 中与该点有关的参数和结束记录：

```console
[bcgong@localhost hfi2-frozen20]$ grep -E "TITEL|NELECT|aborting loop|energy  without entropy|Elapsed time" raw/scf_eq/OUTCAR
   TITEL  = PAW_PBE I 08Apr2002                                                 
   TITEL  = PAW_PBE Hf_sv 10Jan2008 GW suitable                                 
   NELECT =     156.0000    total number of electrons
------------------------ aborting loop because EDIFF is reached ----------------------------------------
  energy  without entropy=     -107.79327340  energy(sigma->0) =     -107.79327383
                         Elapsed time (sec):      610.807
[bcgong@localhost hfi2-frozen20]$
```

`NELECT=156` 与 12 个 I、6 个 Hf_sv 的实际价电子设置一致。赝势标题只用于核对身份；POTCAR 的完整正文不随教案发布。`aborting loop because EDIFF is reached` 是达到电子阈值的退出条件，下面的运行统计给出正常结束的另一条证据。

```console
[bcgong@localhost hfi2-frozen20]$ tail -n 18 raw/scf_eq/OUTCAR
   wavefun   :      58877. kBytes
 
  
  
 General timing and accounting informations for this job:
 ========================================================
  
                  Total CPU time used (sec):      608.778
                            User time (sec):      585.284
                          System time (sec):       23.493
                         Elapsed time (sec):      610.807
  
                   Maximum memory used (kb):      234160.
                   Average memory used (kb):           0.
  
                          Minor page faults:        70727
                          Major page faults:            0
                 Voluntary context switches:          747
[bcgong@localhost hfi2-frozen20]$
```

本次提取要求一个固定结构点同时具备：唯一一组最终能量、EDIFF 达到行、完整运行统计，并且没有已知的电子求解错误。它不会从反复发散的文本末尾抓一个数字就纳入表格。

例如 `scf_d0.25` 的实际尾部是：

```console
[bcgong@localhost hfi2-frozen20]$ tail -n 5 raw/scf_d0.25/out
 WARNING: Sub-Space-Matrix is not hermitian in DAV           15
   345.050755254447     
 WARNING: Sub-Space-Matrix is not hermitian in DAV           16
   3053.33523221011     
Error EDDDAV: Call to ZHEGV failed. Returncode =  10 2  16
[bcgong@localhost hfi2-frozen20]$
```

这项没有形成可接受的最终单点能量。目录还存在，不代表对应位移已经有有效数据。完整失败输出经过 gzip 压缩后保留；读教案时展示错误所在的一小段即可。

## 从实际 OUTCAR 重建 20 个点

在本例的整理目录运行提取程序：

```console
[bcgong@localhost hfi2-frozen20]$ python -B extract_scan.py | tee extraction.out
accepted=20 excluded=7 atoms=18 moved=11,12,18
area=10.848221494426 A^2 c=82.187316728572 A
d= 0.0 A E= -107.79327340 eV dE=   0.00000 meV W=  0.000000 meV/A^2 outer_gap= 43.99324 A
d= 2.0 A E= -107.67298978 eV dE= 120.28362 meV W= 11.087865 meV/A^2 outer_gap= 41.99324 A
d= 3.0 A E= -107.61525753 eV dE= 178.01587 meV W= 16.409682 meV/A^2 outer_gap= 40.99324 A
d= 4.0 A E= -107.58649411 eV dE= 206.77929 meV W= 19.061124 meV/A^2 outer_gap= 39.99324 A
d= 5.0 A E= -107.57080700 eV dE= 222.46640 meV W= 20.507177 meV/A^2 outer_gap= 38.99324 A
d= 6.0 A E= -107.56258844 eV dE= 230.68496 meV W= 21.264772 meV/A^2 outer_gap= 37.99324 A
d= 7.0 A E= -107.55688561 eV dE= 236.38779 meV W= 21.790465 meV/A^2 outer_gap= 36.99324 A
d= 8.0 A E= -107.55363213 eV dE= 239.64127 meV W= 22.090374 meV/A^2 outer_gap= 35.99324 A
d= 9.0 A E= -107.55116220 eV dE= 242.11120 meV W= 22.318055 meV/A^2 outer_gap= 34.99324 A
d=10.0 A E= -107.54937619 eV dE= 243.89721 meV W= 22.482691 meV/A^2 outer_gap= 33.99324 A
d=11.0 A E= -107.54835199 eV dE= 244.92141 meV W= 22.577103 meV/A^2 outer_gap= 32.99324 A
d=12.0 A E= -107.54706879 eV dE= 246.20461 meV W= 22.695389 meV/A^2 outer_gap= 31.99324 A
d=13.0 A E= -107.54685999 eV dE= 246.41341 meV W= 22.714637 meV/A^2 outer_gap= 30.99324 A
d=14.0 A E= -107.54599033 eV dE= 247.28307 meV W= 22.794803 meV/A^2 outer_gap= 29.99324 A
d=15.0 A E= -107.54585927 eV dE= 247.41413 meV W= 22.806884 meV/A^2 outer_gap= 28.99324 A
d=16.0 A E= -107.54552844 eV dE= 247.74496 meV W= 22.837380 meV/A^2 outer_gap= 27.99324 A
d=17.0 A E= -107.54522826 eV dE= 248.04514 meV W= 22.865051 meV/A^2 outer_gap= 26.99324 A
d=18.0 A E= -107.54525486 eV dE= 248.01854 meV W= 22.862599 meV/A^2 outer_gap= 25.99324 A
d=19.0 A E= -107.54475578 eV dE= 248.51762 meV W= 22.908605 meV/A^2 outer_gap= 24.99324 A
d=20.0 A E= -107.54517866 eV dE= 248.09474 meV W= 22.869623 meV/A^2 outer_gap= 23.99324 A
16--20 A energy range=0.77266 meV
excluded scf_d0.25: Incomplete static SCF energy=0 EDIFF=0 end=0
excluded scf_d0.50: Incomplete static SCF energy=0 EDIFF=0 end=0
excluded scf_d0.75: Incomplete static SCF energy=0 EDIFF=0 end=0
excluded scf_d1: OUTCAR absent energy=0 EDIFF=0 end=0
excluded scf_d1.00: Incomplete static SCF energy=0 EDIFF=0 end=0
excluded scf_d1.25: OUTCAR absent energy=0 EDIFF=0 end=0
excluded scf_d1.50: OUTCAR absent energy=0 EDIFF=0 end=0
[bcgong@localhost hfi2-frozen20]$ cat excluded.csv
directory,reason,energy_lines,ediff,normal_end
scf_d0.25,Incomplete static SCF,0,0,0
scf_d0.50,Incomplete static SCF,0,0,0
scf_d0.75,Incomplete static SCF,0,0,0
scf_d1,OUTCAR absent,0,0,0
scf_d1.00,Incomplete static SCF,0,0,0
scf_d1.25,OUTCAR absent,0,0,0
scf_d1.50,OUTCAR absent,0,0,0
[bcgong@localhost hfi2-frozen20]$
```

d=1 Å 没有完整结果；0.25、0.50、0.75、1.00、1.25、1.50 Å 的相关尝试也没有全部验收条件。因此实际采样集合是 `0,2,3,…,20 Å`。曲线连接线只是帮助阅读离散点，不表示中间空缺位移已经计算过。

同一行 OUTCAR 会写出 `energy without entropy` 和 `energy(sigma->0)`。这一表统一取前者；没有逐点挑选两列中的较小值，也不与自由能 TOTEN 混用。原始两列都保存在 [exfoliation.csv](/Atlas/examples/hfi2-frozen20/exfoliation.csv)，便于核查所取的能量定义。

| 顶层位移 d / Å | energy without entropy / eV·cell⁻¹ | E(d)−E(0) / meV·cell⁻¹ | [E(d)−E(0)]/A / meV·Å⁻² |
| ---: | ---: | ---: | ---: |
| 0 | -107.79327340 | 0.00000 | 0.000000 |
| 2 | -107.67298978 | 120.28362 | 11.087865 |
| 3 | -107.61525753 | 178.01587 | 16.409682 |
| 4 | -107.58649411 | 206.77929 | 19.061124 |
| 5 | -107.57080700 | 222.46640 | 20.507177 |
| 6 | -107.56258844 | 230.68496 | 21.264772 |
| 7 | -107.55688561 | 236.38779 | 21.790465 |
| 8 | -107.55363213 | 239.64127 | 22.090374 |
| 9 | -107.55116220 | 242.11120 | 22.318055 |
| 10 | -107.54937619 | 243.89721 | 22.482691 |
| 11 | -107.54835199 | 244.92141 | 22.577103 |
| 12 | -107.54706879 | 246.20461 | 22.695389 |
| 13 | -107.54685999 | 246.41341 | 22.714637 |
| 14 | -107.54599033 | 247.28307 | 22.794803 |
| 15 | -107.54585927 | 247.41413 | 22.806884 |
| 16 | -107.54552844 | 247.74496 | 22.837380 |
| 17 | -107.54522826 | 248.04514 | 22.865051 |
| 18 | -107.54525486 | 248.01854 | 22.862599 |
| 19 | -107.54475578 | 248.51762 | 22.908605 |
| 20 | -107.54517866 | 248.09474 | 22.869623 |

零点的真实能量为 −107.79327340 eV/cell，20 Å 点为 −107.54517866 eV/cell。这里每个 cell 都是同一个 18 原子晶胞，先统一相减，再转换单位：

```text
ΔE(20) = −107.54517866 − (−107.79327340)
       = 0.24809474 eV/cell

W(20) = ΔE(20) / A
      = 22.86962339 meV/Å²
      = 0.36641176 J/m²
```

换算使用 `1 meV/Å² = 0.01602176634 J/m²`。本次只从一个面分离一个三原子层，按这次操作的能量差除以面内面积，不因出现两个表面再机械地除以 2。若改为同时分离两层，必须重新定义操作与计数。

## 放大末段以后，还能看到什么

[plot_exfoliation.py](/Atlas/examples/hfi2-frozen20/plot_exfoliation.py)（同时下载 [atlas_plot_style.py](/Atlas/examples/atlas_plot_style.py)，放在同一目录） 直接读取 CSV，输出 PNG、PDF 与 SVG。在装有 NumPy 和 Matplotlib 的本机运行：

```bash
cd hfi2-frozen20
python3 extract_scan.py
python3 plot_exfoliation.py
```

![HfI₂ 冻结结构分离曲线与末段能量变化](/Atlas/examples/hfi2-frozen20/hfi2-exfoliation.png)

左图按面积归一化，从零点画到 20 Å；右图把 d≥12 Å 的原始能量差放大。没有用平滑或拟合让末段变成单调平台。16–20 Å 的能量差范围为 **0.77266 meV/cell**；19→20 Å 实际降低 **0.42288 meV/cell**，而不是继续单调增加。

这个范围描述已采样五点的变化，不是已知的总误差条。当前数据没有预先完成所需的 k 点、截断、展宽或层数对照，也没有更大 c 的成对结果，因而不能仅凭整图看起来变平，就宣布取得收敛剥离能。

晶胞高度始终固定。把顶层抬高时，它与下面五层的距离增加，同时与上方周期镜像的空隙减小。由真实坐标计算，最外层原子之间的周期边界空隙从 43.993243 Å 减少到 23.993243 Å。这个空隙仍是几何距离，不是周期镜像误差的数值证明；检查时应在更大 c 下重算匹配的零点与分离点，再比较同一定义的差值。

这组结果支持的是：在给定原型构型、冻结坐标和当前 PBE-D3 协议下，分离一层到 d=20 Å 的电子能量代价为上述数值。要把它作为材料剥离能，还需要先取得可接受的 HfI₂ 参考几何，再检查有限厚度、面内约束、层内松弛和相应数值参数。原子不移动的单点不能替代这些条件。

下一步：用[结构优化](/Atlas/m/relax/vasp/)处理参考几何；希望观察结合时电子密度的变化，可接[差分电荷](/Atlas/m/delta-charge/vasp/)。后者的 H₂ 教学例子演示的是处理方法，其数值不能移来解释本例 HfI₂。

```text
明确的冻结构型 → 只移动顶层 11、12、18 号原子
                          ↓
                 各点单独检查电子收敛与结束
                          ↓
               20 个接受点 / 7 个排除目录
                          ↓
               同一定义相减 → 面积归一化
                          ↓
             末段、周期镜像与参考几何检查
```
