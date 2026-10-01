从层状材料表面取走一层，需要付出多少单位面积的能量？这一能量代价是判断机械剥离难易的出发点。本例先回答一个确定的模型问题：固定 HfI₂ 六层 slab 的其余坐标，将最上面一层逐渐抬高时，相对位移零点的能量怎样变化？已有零点与 2–20 Å 共 20 个完整单点，另有 7 个未完成结果列入排除表。能量差除以面内面积，得到 `W(20 Å)=0.36641176 J/m²` 的有限距离分离功；后面再从参考厚度、几何弛豫与周期镜像间距判断如何接到材料剥离能。

[VASP：OUTCAR 输出](https://vasp.at/wiki/OUTCAR) · [VASP：展宽与能量选择](https://vasp.at/wiki/Smearing_technique) · [VASP：IVDW 色散修正](https://vasp.at/wiki/IVDW) · [Jung 等：剥离能与参考态](https://arxiv.org/abs/1805.04527)

[Jung 等的方法论文](https://arxiv.org/html/1805.04527v1)在 Fig. 1–2 区分厚 slab 的逐层剥离与体相—单层参考，式 (1)–(7) 用厚度极限建立二者关系。那里允许剩余薄膜与分离层弛豫；本例保持六层几何冻结，直接计算随位移变化的 ΔE/A。因此先读这条分离曲线，再检查厚度、弛豫和大距离极限，才能讨论对应材料的剥离代价。

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

标准输出确认这些历史单点实际使用了 16 个进程。脚本没有把申请进程数写成 SBATCH 参数，复算时应明确申请与 `-np 16` 对应的资源，例如 `sbatch --nodes=1 --ntasks=16 script_std`，并根据当前队列保留公共节点所需的空闲资源。各目录中的输出对应这批已完成或失败的单点尝试。

## 按电子收敛与完整输出筛选扫描点

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

在每份 OUTCAR 的最终能量行中，`energy without entropy` 与 `energy(sigma->0)` 并列出现。上面零点的输出分别为 −107.79327340 和 −107.79327383 eV；下表统一读取前一列 `energy without entropy`，再减去零点同一列的值。原始两列都保存在 [exfoliation.csv](/Atlas/examples/hfi2-frozen20/exfoliation.csv)，全组保持同一种能量定义。

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

零点的能量为 −107.79327340 eV/cell，20 Å 点为 −107.54517866 eV/cell。两者都是同一个 18 原子晶胞的总能，先相减得到每晶胞的分离功，再除以面内面积 `A=10.8482214944 Å²`，转换单位：

```text
ΔE(20) = −107.54517866 − (−107.79327340)
       = 0.24809474 eV/cell

W(20) = ΔE(20) / A
      = 22.86962339 meV/Å²
      = 0.36641176 J/m²
```

换算使用 `1 meV/Å² = 0.01602176634 J/m²`。本次只从一个面分离一个三原子层，按这次操作的能量差除以面内面积，不因出现两个表面再机械地除以 2。若改为同时分离两层，必须重新定义操作与计数。

## 从有限位移数据判断分离功的范围

前面的几何与输出确定了能量差的参考：18 原子的冻结六层 slab，以 11、12、18 号原子的共同位移打开一个界面。判断大距离结果时，还要同时查看能量变化和外侧周期镜像间距。

所以本页能报告的是一个冻结六层模型中打开一个界面的有限距离分离功：
$$
W(d)=\frac{E_{\rm without\ entropy}(d)-E_{\rm without\ entropy}(0)}{A},\qquad
1\;\mathrm{eV/\mathring A^2}=16.02176634\;\mathrm{J/m^2}.
$$
该量定义为一次界面分离操作的功，不含表面能定义中的二倍面积因子；只有在生成两个等价表面、参照态和厚度极限都适当时，才能用分离功的一半讨论相应表面能；本例的有限多层冻结几何分离曲线不能仅除以 2 就改称单面表面能。d=20 Å 时 ΔE=0.24809474 eV/cell，W=0.36641176 J/m²。由于 d=0 仍是六层 slab，本值不能直接叫作由体相参考得到的 HfI₂ 材料剥离能。

### 接受点与末段起伏

接受表共 20 点：d=0 与 d=2…20 Å。名义 d=1 Å 有两次尝试但均未接受：目录 scf_d1 的 OUTCAR 缺失，scf_d1.00 为不完整静态 SCF。另有 scf_d0.25、0.50、0.75、1.25、1.50 未满足接受条件。没有把这些尝试插值进接受表。以下选择 d=0、首个接受的 d=2 和末段五个点；能量均为 eV/cell，ΔE 为 meV/cell，W 为 J/m²。

| 目录 | d (Å) | E without entropy (eV/cell) | ΔE (meV/cell) | W (J/m²) | 外侧周期镜像间距 (Å) |
| --- | ---: | ---: | ---: | ---: | ---: |
| scf_eq | 0 | −107.79327340 | 0.00000 | 0.00000000 | 43.993243 |
| scf_d2 | 2 | −107.67298978 | 120.28362 | 0.17764719 | 41.993243 |
| scf_d16 | 16 | −107.54552844 | 247.74496 | 0.36589517 | 27.993243 |
| scf_d17 | 17 | −107.54522826 | 248.04514 | 0.36633851 | 26.993243 |
| scf_d18 | 18 | −107.54525486 | 248.01854 | 0.36629922 | 25.993243 |
| scf_d19 | 19 | −107.54475578 | 248.51762 | 0.36703631 | 24.993243 |
| scf_d20 | 20 | −107.54517866 | 248.09474 | 0.36641176 | 23.993243 |

d=16…20 Å 的五点能量范围是 0.77266 meV/cell；d=19→20 Å 反而降低 0.42288 meV/cell。这个有限样本显示末段存在起伏，不能据此给出统计误差，也不足以确认能量已经达到解理曲线的平台。与此同时，c 保持固定时，外侧周期镜像间距从 43.993 Å 缩到 23.993 Å。增加顶层位移并没有保持周期镜像间距不变；还需在更大 c 下成对重算 d=0 与分离点，才可量化这一误差来源。

## 编写分离功分析脚本

原始提取器已经将每个位移目录整理成一行 CSV，保留位移、两种能量、能量差、面积归一化值与周期镜像间距。下面的表格后处理读取这些行，用位移零点 POSCAR 的前两根晶格矢量重算面积，再统一减去 `scf_eq` 的 `energy_without_entropy_eV`。排除表单独保留失败目录；它们不参与能量相减，也不补成曲线上的点。可以按以下需求编写脚本：

~~~text
请用 Python 3 编写 review_hfi2_exfoliation.py，读取同目录的 exfoliation.csv、excluded.csv 和 scf_eq 的 POSCAR；这些输入不可修改。接受点 CSV 的关键字段是 directory、d_A（Å）、energy_without_entropy_eV（eV/cell）、energy_sigma0_eV（eV/cell）、delta_E_meV（meV/cell）、W_meV_A2（meV/Å²）、W_J_m2（J/m²）、outer_periodic_gap_A（Å）。排除表字段为 directory、reason、energy_lines、ediff、normal_end。

用 POSCAR 的正比例因子与 a、b 晶格矢量叉积计算 A（Å²）；对所有点始终选 energy_without_entropy_eV，令 ΔE(eV/cell)=E(d)−E(scf_eq)，W(meV/Å²)=1000*ΔE/A，W(J/m²)=ΔE/A*16.02176634。逐行复算并核对 CSV 存储的 ΔE 与 W。不得把 energy_sigma0_eV 和 energy_without_entropy_eV 混在一个差分里。

校验 d=0 只有一个 scf_eq，20 个接受距离必须为 {0,2,3,…,20} Å，所有数字有限、d 和 directory 无重复；接受表不能包含 d=1。确认名义 d=1 的 scf_d1（OUTCAR absent）与 scf_d1.00（Incomplete static SCF）都在排除表中。缺列、重复、错单位、面积不符、能量差或归一化量超容差、接受/排除计数不是 20/7 时停止并指出文件/目录/字段。

输出 hfi2-selected-separation-review.csv（只列 d=0、2、16、17、18、19、20 的原始能量、重算 ΔE、W 与周期镜像间距）、hfi2-exclusion-review.csv（保留七个排除目录及原因）和 hfi2-separation-review.md。解释 d=16…20 Å 能量范围 0.77266 meV/cell 及 d=19→20 Å 的下降 −0.42288 meV/cell。此处不要生成折线图、柱形图或拟合平台：目前的六层 slab 参考不是体相，名义 d=1 也没有可接受结果。若将来做有科学意义的体相参考距离曲线，先获得 bulk-like 参考与足够大的 c，再保留每个缺失位移的空档，不插值失败结果，并单独报告厚度、k 点、截断和真空误差。

验收检查：A≈10.8482214944 Å²；accepted=20、excluded=7；d20 的 W≈0.36641176 J/m²；16…20 Å 能量范围≈0.77266 meV/cell；所有结果使用同一 OUTCAR 能量定义。不要将本例有限距离的 W 称为已收敛的材料剥离能。
~~~

完整原始输出提取器为 [extract_scan.py](/Atlas/examples/hfi2-frozen20/extract_scan.py)。配套表格分析脚本为 [review_hfi2_exfoliation.py](/Atlas/examples/thermo-postprocessing/exfoliation/review_hfi2_exfoliation.py)；同时下载 [采用点表](/Atlas/examples/thermo-postprocessing/exfoliation/exfoliation.csv)、[排除目录表](/Atlas/examples/thermo-postprocessing/exfoliation/excluded.csv) 与 [scf_eq POSCAR](/Atlas/examples/thermo-postprocessing/exfoliation/POSCAR)。将三份输入分别保存为 `exfoliation.csv`、`excluded.csv`、`POSCAR`，与分析脚本放在同一目录。该脚本只用 Python 标准库，本例运行环境为 Python 3.12.3。

脚本输出选点表、排除表和数据核对记录；本次结果可下载：[采用点表](/Atlas/examples/thermo-postprocessing/exfoliation/review/hfi2-selected-separation-review.csv)、[排除点表](/Atlas/examples/thermo-postprocessing/exfoliation/review/hfi2-exclusion-review.csv)、[数据核对记录](/Atlas/examples/thermo-postprocessing/exfoliation/review/hfi2-separation-review.md)。

<details>
<summary>extract_scan.py 的完整源码</summary>

```python
from __future__ import print_function
import os, re, math, csv, json, hashlib

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read_poscar(path):
    lines=open(path).read().splitlines()
    scale=float(lines[1])
    if scale<=0:raise ValueError('Positive scalar POSCAR scale required')
    cell=[[float(x)*scale for x in line.split()[:3]] for line in lines[2:5]]
    species=lines[5].split();counts=list(map(int,lines[6].split()));nat=sum(counts)
    at=7
    if lines[at].lower().startswith('s'):at+=1
    mode=lines[at].lower();at+=1
    raw=[[float(x) for x in line.split()[:3]] for line in lines[at:at+nat]]
    if mode.startswith('d'):
        pos=[[sum(v[k]*cell[k][j] for k in range(3)) for j in range(3)] for v in raw]
    elif mode.startswith(('c','k')):
        pos=[[x*scale for x in v] for v in raw]
    else:raise ValueError('Unsupported coordinates')
    return cell,species,counts,pos

def area(cell):
    a,b=cell[:2]
    cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    return math.sqrt(sum(x*x for x in cross))

base='raw'
rows=[];excluded=[];fingerprints={}
reference=read_poscar(os.path.join(base,'scf_eq','POSCAR'))
protocol=[digest(os.path.join(base,'scf_eq',f)) for f in ('INCAR','KPOINTS')]
expected_titles=None
for name in sorted(os.listdir(base)):
    folder=os.path.join(base,name)
    if not os.path.isdir(folder) or not name.startswith('scf_'):continue
    outpath=os.path.join(folder,'OUTCAR')
    if not os.path.isfile(outpath):
        excluded.append(dict(directory=name,reason='OUTCAR absent',energy_lines=0,ediff=0,normal_end=0))
        continue
    out=open(outpath).read()
    energies=re.findall(r'energy\s+without entropy=\s*([-\d.]+)\s+energy\(sigma->0\)\s*=\s*([-\d.]+)',out)
    ediff=out.count('aborting loop because EDIFF is reached')
    normal=out.count('General timing and accounting')
    if len(energies)!=1 or ediff!=1 or normal!=1:
        excluded.append(dict(directory=name,reason='Incomplete static SCF',energy_lines=len(energies),ediff=ediff,normal_end=normal))
        continue
    if re.search(r'VERY BAD NEWS|BRMIX:|Error EDD|ZHEGV failed',out,re.I):
        raise ValueError(name+': electronic solver error')
    current=read_poscar(os.path.join(folder,'POSCAR'))
    if current[:3]!=reference[:3]:raise ValueError(name+': cell/species/counts changed')
    if [digest(os.path.join(folder,f)) for f in ('INCAR','KPOINTS')]!=protocol:
        raise ValueError(name+': input protocol differs')
    titles=re.findall(r'TITEL\s*=\s*(.*)',out)
    if expected_titles is None:expected_titles=titles
    if titles!=expected_titles:raise ValueError(name+': output pseudopotentials differ')
    if float(re.findall(r'NELECT\s*=\s*([-\d.]+)',out)[-1])!=156.:
        raise ValueError(name+': unexpected electron count')
    shifts=[[v-w for v,w in zip(p,q)] for p,q in zip(current[3],reference[3])]
    d=0. if name=='scf_eq' else float(name.split('scf_d')[1])
    for index,vec in enumerate(shifts):
        expected=d if index in (10,11,17) else 0.
        if max(abs(vec[0]),abs(vec[1]),abs(vec[2]-expected))>1e-7:
            raise ValueError(name+': incorrect frozen-layer displacement')
    energy=float(energies[0][0]);sigma=float(energies[0][1])
    ez=[v[2] for v in current[3]]
    outer_gap=current[0][2][2]-(max(ez)-min(ez))
    fingerprints[name]={f:digest(os.path.join(folder,f)) for f in
                       ('INCAR','KPOINTS','POSCAR','OUTCAR','OSZICAR','script_std')
                       if os.path.isfile(os.path.join(folder,f))}
    rows.append(dict(directory=name,d_A=d,energy_without_entropy_eV=energy,
                     energy_sigma0_eV=sigma,outer_periodic_gap_A=outer_gap))
rows.sort(key=lambda row:row['d_A'])
if len(rows)!=20 or [row['d_A'] for row in rows]!=[0.]+list(map(float,range(2,21))):
    raise ValueError('Expected exactly the verified 20-point set')
area_A2=area(reference[0]);e0=rows[0]['energy_without_entropy_eV']
for row in rows:
    row['delta_E_meV']=1000*(row['energy_without_entropy_eV']-e0)
    row['W_meV_A2']=row['delta_E_meV']/area_A2
    row['W_J_m2']=row['W_meV_A2']*.01602176634
keys=['directory','d_A','energy_without_entropy_eV','energy_sigma0_eV','delta_E_meV','W_meV_A2','W_J_m2','outer_periodic_gap_A']
with open('exfoliation.csv','w') as f:
    w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
with open('excluded.csv','w') as f:
    w=csv.DictWriter(f,['directory','reason','energy_lines','ediff','normal_end'],lineterminator='\n')
    w.writeheader();w.writerows(excluded)
summary=dict(natoms=18,species=reference[1],counts=reference[2],area_A2=area_A2,
             c_A=reference[0][2][2],moved_atom_indices_1based=[11,12,18],
             accepted_points=len(rows),excluded_points=len(excluded),
             energy_reference_eV=e0,energy_definition='energy without entropy',
             geometry_scope='Frozen prototype-derived HfI2 structure; no accepted HfI2 relaxation in this dataset',
             final_point=rows[-1],tail_16_to_20_range_meV=max(r['delta_E_meV'] for r in rows[-5:])-min(r['delta_E_meV'] for r in rows[-5:]),
             output_potential_titles=expected_titles,sha256=fingerprints)
with open('summary.json','w') as f:json.dump(summary,f,indent=2,sort_keys=True)
print('accepted=%d excluded=%d atoms=18 moved=11,12,18'%(len(rows),len(excluded)))
print('area=%.12f A^2 c=%.12f A'%(area_A2,reference[0][2][2]))
for row in rows:
    print('d=%4.1f A E=%14.8f eV dE=%10.5f meV W=%10.6f meV/A^2 outer_gap=%9.5f A'%
          (row['d_A'],row['energy_without_entropy_eV'],row['delta_E_meV'],row['W_meV_A2'],row['outer_periodic_gap_A']))
print('16--20 A energy range=%.5f meV'%summary['tail_16_to_20_range_meV'])
for row in excluded:
    print('excluded %s: %s energy=%d EDIFF=%d end=%d'%(row['directory'],row['reason'],row['energy_lines'],row['ediff'],row['normal_end']))
```

</details>


完整源码如下，与上面的下载文件相同。保存为 `review_hfi2_exfoliation.py`，和 `exfoliation.csv`、`excluded.csv`、`POSCAR` 放在同一目录。

<details>
<summary>review_hfi2_exfoliation.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Validate HfI2 separation-energy bookkeeping and emit a focused review table."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

EV_A2_TO_J_M2 = 16.02176634
EXPECTED_AREA_A2 = 10.848221494425957
TAIL_DISTANCES = {16.0, 17.0, 18.0, 19.0, 20.0}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing CSV header")
        return reader.fieldnames, list(reader)


def poscar_area(path: Path) -> float:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 5:
        raise ValueError(f"{path}: incomplete POSCAR lattice")
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError(f"{path}: expected positive POSCAR scale factor")
    a = [float(value) * scale for value in lines[2].split()[:3]]
    b = [float(value) * scale for value in lines[3].split()[:3]]
    if len(a) != 3 or len(b) != 3:
        raise ValueError(f"{path}: malformed first two lattice vectors")
    cross = (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )
    area = math.sqrt(sum(value * value for value in cross))
    if not math.isfinite(area) or area <= 0:
        raise ValueError(f"{path}: non-positive/non-finite in-plane area")
    return area


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted", type=Path, default=Path("exfoliation.csv"))
    parser.add_argument("--excluded", type=Path, default=Path("excluded.csv"))
    parser.add_argument("--poscar", type=Path, default=Path("POSCAR"))
    parser.add_argument("--outdir", type=Path, default=Path("review"))
    args = parser.parse_args()

    accepted_header, accepted_rows = read_csv(args.accepted)
    excluded_header, excluded_rows = read_csv(args.excluded)
    area = poscar_area(args.poscar)
    if not math.isclose(area, EXPECTED_AREA_A2, rel_tol=0, abs_tol=2e-9):
        raise ValueError(
            f"{args.poscar}: area {area:.12f} A^2 differs from reviewed cell "
            f"{EXPECTED_AREA_A2:.12f} A^2"
        )
    required = {
        "directory", "d_A", "energy_without_entropy_eV", "energy_sigma0_eV",
        "delta_E_meV", "W_meV_A2", "W_J_m2", "outer_periodic_gap_A",
    }
    missing = required - set(accepted_header)
    if missing:
        raise ValueError(f"{args.accepted}: missing columns {sorted(missing)}")
    for required_name in ("directory", "reason", "energy_lines", "ediff", "normal_end"):
        if required_name not in excluded_header:
            raise ValueError(f"{args.excluded}: missing column {required_name}")

    by_distance: dict[float, dict[str, str]] = {}
    for row in accepted_rows:
        d = float(row["d_A"])
        if d in by_distance:
            raise ValueError(f"{args.accepted}: duplicate accepted d={d:g} A")
        for column in required - {"directory"}:
            value = float(row[column])
            if not math.isfinite(value):
                raise ValueError(f"{args.accepted}: non-finite {column} at d={d:g} A")
        by_distance[d] = row
    expected_distances = {0.0} | set(float(d) for d in range(2, 21))
    if set(by_distance) != expected_distances:
        missing_d = sorted(expected_distances - set(by_distance))
        unexpected_d = sorted(set(by_distance) - expected_distances)
        raise ValueError(
            f"accepted d set differs: missing={missing_d}, unexpected={unexpected_d}"
        )
    if by_distance[0.0]["directory"] != "scf_eq":
        raise ValueError("the sole d=0 reference must be scf_eq")

    e0 = float(by_distance[0.0]["energy_without_entropy_eV"])
    recalculated: dict[float, tuple[float, float, float]] = {}
    for d, row in by_distance.items():
        energy = float(row["energy_without_entropy_eV"])
        delta_e = energy - e0
        delta_mev = delta_e * 1000.0
        work_mev_a2 = delta_mev / area
        work_j_m2 = delta_e / area * EV_A2_TO_J_M2
        checks = (
            ("delta_E_meV", delta_mev, 2e-5),
            ("W_meV_A2", work_mev_a2, 2e-7),
            ("W_J_m2", work_j_m2, 2e-8),
        )
        for column, calculated, tolerance in checks:
            stored = float(row[column])
            if not math.isclose(calculated, stored, rel_tol=0, abs_tol=tolerance):
                raise ValueError(
                    f"d={d:g} A: recomputed {column}={calculated:.12g}, "
                    f"stored={stored:.12g}"
                )
        recalculated[d] = (delta_mev, work_mev_a2, work_j_m2)

    if len(accepted_rows) != 20 or len(excluded_rows) != 7:
        raise ValueError(
            f"reviewed dataset requires 20 accepted and 7 excluded; "
            f"found {len(accepted_rows)} and {len(excluded_rows)}"
        )
    excluded_by_name = {row["directory"]: row for row in excluded_rows}
    if len(excluded_by_name) != len(excluded_rows):
        raise ValueError(f"{args.excluded}: duplicate excluded directory")
    expected_d1 = {"scf_d1", "scf_d1.00"}
    if expected_d1 - set(excluded_by_name):
        raise ValueError(f"nominal d=1 A exclusions are missing: {sorted(expected_d1 - set(excluded_by_name))}")
    if excluded_by_name["scf_d1"]["reason"] != "OUTCAR absent":
        raise ValueError("scf_d1 exclusion reason no longer matches the reviewed record")
    if excluded_by_name["scf_d1.00"]["reason"] != "Incomplete static SCF":
        raise ValueError("scf_d1.00 exclusion reason no longer matches the reviewed record")

    selected = [0.0, 2.0, 16.0, 17.0, 18.0, 19.0, 20.0]
    selected_rows: list[dict[str, str]] = []
    for d in selected:
        row = by_distance[d]
        delta_mev, work_mev_a2, work_j_m2 = recalculated[d]
        selected_rows.append({
            "directory": row["directory"],
            "d_A": f"{d:.1f}",
            "energy_without_entropy_eV": row["energy_without_entropy_eV"],
            "delta_E_meV": f"{delta_mev:.8f}",
            "W_meV_A2": f"{work_mev_a2:.8f}",
            "W_J_m2": f"{work_j_m2:.10f}",
            "outer_periodic_gap_A": row["outer_periodic_gap_A"],
        })

    args.outdir.mkdir(parents=True, exist_ok=True)
    table_path = args.outdir / "hfi2-selected-separation-review.csv"
    exclusion_path = args.outdir / "hfi2-exclusion-review.csv"
    report_path = args.outdir / "hfi2-separation-review.md"
    write_csv(table_path, [
        "directory", "d_A", "energy_without_entropy_eV", "delta_E_meV",
        "W_meV_A2", "W_J_m2", "outer_periodic_gap_A",
    ], selected_rows)
    write_csv(exclusion_path, excluded_header, excluded_rows)

    tail_energies = [float(by_distance[d]["energy_without_entropy_eV"]) for d in sorted(TAIL_DISTANCES)]
    tail_spread_mev = (max(tail_energies) - min(tail_energies)) * 1000.0
    step_19_20_mev = (
        float(by_distance[20.0]["energy_without_entropy_eV"])
        - float(by_distance[19.0]["energy_without_entropy_eV"])
    ) * 1000.0
    w20 = recalculated[20.0][2]
    report_path.write_text(
        "# HfI2 frozen-slab separation review\n\n"
        f"- POSCAR area: {area:.12f} Å².\n"
        f"- Accepted scan points: {len(accepted_rows)}; excluded directories: {len(excluded_rows)}.\n"
        "- Accepted distances: d=0 and d=2…20 Å. The nominal d=1 Å attempts are not accepted: "
        "scf_d1 has no OUTCAR and scf_d1.00 is an incomplete static SCF.\n"
        "- Energy field used throughout: OUTCAR energy without entropy, eV/cell.\n"
        f"- At d=20 Å, ΔE={recalculated[20.0][0]:.8f} meV/cell and W={w20:.10f} J/m².\n"
        f"- The d=16…20 Å five-point energy spread is {tail_spread_mev:.5f} meV/cell; "
        f"the d=19→20 Å change is {step_19_20_mev:.5f} meV/cell.\n\n"
        "Interpretation: these values describe the frozen six-layer, prototype-derived slab under "
        "one specified layer-separation operation. The d=0 reference is itself a six-layer slab, "
        "not a bulk calculation. The finite-distance energy and non-monotone high-distance spread "
        "do not establish a bulk-referenced exfoliation energy or a converged asymptote.\n",
        encoding="utf-8",
    )
    print(f"accepted={len(accepted_rows)} excluded={len(excluded_rows)} area={area:.12f} A^2")
    print(f"d20: delta_E={recalculated[20.0][0]:.8f} meV/cell W={w20:.10f} J/m^2")
    print(f"d16-20 energy spread={tail_spread_mev:.5f} meV/cell; d19->20={step_19_20_mev:.5f} meV/cell")
    print(table_path)
    print(exclusion_path)
    print(report_path)


if __name__ == "__main__":
    main()
```

</details>

将上面的 CSV、POSCAR 与脚本放在同一目录，运行：

```bash
python3 review_hfi2_exfoliation.py --outdir review
```

从原始 OUTCAR 运行提取器，再运行复核脚本，终端输出为：

~~~text
accepted=20 excluded=7 atoms=18 moved=11,12,18
area=10.848221494426 A^2 c=82.187316728572 A
16--20 A energy range=0.77266 meV

accepted=20 excluded=7 area=10.848221494426 A^2
d20: delta_E=248.09474000 meV/cell W=0.3664117622 J/m^2
d16-20 energy spread=0.77266 meV/cell; d19->20=-0.42288 meV/cell
~~~

20 个接受点的归一化量与原表一致；末段起伏和 19→20 Å 的下降也在复算中保留。它们提示下一步要检查大距离结果与周期镜像的关系。

## 文献中的体相参照与层厚检查

以下两篇论文都把材料剥离能与明确的多层参考结构和分离距离联系起来。TbCl 研究的 **Fig. 3a** 使用五层 slab；正文报告单层剥离能 0.24 J/m²，并与 graphite（约 0.32 J/m²）和 H-MoS₂（约 0.29 J/m²）比较，随后把较低能量解释为从 bulk 更易剥离。见 “5d orbital induced room temperature quantum anomalous Hall effect in TbCl,” *npj Computational Materials* 11, 236 (2025), [DOI](https://doi.org/10.1038/s41524-025-01732-0)。

CaCl 研究的 **Fig. 5(a)** 比较 AB-stacking 与 P3m1 结构的距离曲线，图注明确说明 bulk 以 16 个原子层建模；正文报告 AB-stacking 的剥离能为 0.17 J/m²，并据此讨论其较易剥离。见 Ying Chen et al., “A van der Waals CaCl semiconducting electrene and ferromagnetic half-metallicity induced by superhalogen decoration,” *Materials Today Communications* 32 (2022), 104176, [DOI](https://doi.org/10.1016/j.mtcomm.2022.104176)。

参照是六层冻结 HfI₂ slab。d=16–20 Å 能量仍非单调，表中报告各实际距离的 ΔE/A；继续增加分离距离并检验平台后讨论大距离极限。与体相参照论文比较时，先统一参考厚度、堆垛与位移定义。

下一步：用[离子弛豫](/Atlas/m/relax/)处理参考几何；希望观察结合时电子密度的变化，可接[差分电荷](/Atlas/m/delta-charge/vasp/)。后者的 H₂ 教学例子演示的是处理方法，其数值不能移来解释本例 HfI₂。

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
