[Henkelman 组：Bader 程序](https://www.henkelmanlab.org/code/bader/) · [VASP：LAECHG](https://vasp.at/wiki/LAECHG) · [CHGCAR](https://vasp.at/wiki/CHGCAR)

Bader 分析把实空间分成一个个原子盆地，再积分盆地内的电子数。先用两个完全等价的 Fe 原子跑通一次：它们的分区电子数应当相同，整胞总数也应与 VASP 的价电子数一致。这个小体系很容易看清输入、三维网格、参考密度与 ACF.dat 之间的关系。

结构和磁态来自 [bcc Fe 磁构型比较](/Atlas/m/magnetic-gs/vasp/) 的 FM 解。下载 [真实输入、OUTCAR、96³ 电荷网格及后处理脚本](/Atlas/examples/vasp/fe-bcc-lesson-files.tar.gz) 后，解包进入 `fe-bcc/charge_elf`。包中保留两套网格的输出与检查结果，POTCAR 仅提供 TITEL、ZVAL 和哈希标识。

这次在新的 `charge_elf` 目录中复制 POSCAR、KPOINTS、POTCAR 和提交脚本，用 `vi INCAR` 打开全电子密度输出。保存后读取实际输入。

```text
[bcgong@localhost charge_elf]$ cat INCAR
SYSTEM = Fe bcc FM charge and ELF
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 100
ALGO = Normal
ISMEAR = 1
SIGMA = 0.1
ISPIN = 2
MAGMOM = 3 3
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
NPAR = 1
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .TRUE.

LAECHG = .TRUE.
LELF = .TRUE.
NGXF = 96
NGYF = 96
NGZF = 96
```
`LAECHG` 写出 AECCAR0、AECCAR1、AECCAR2：分别对应芯电子、原子叠加的价电子密度和最终自洽价电子密度。用来找分区边界的参考是 AECCAR0 + AECCAR2；实际积分的目标仍是 CHGCAR 中的总价电子密度。AECCAR1 不代替已经收敛的 AECCAR2。

本次同时写了 ELFCAR，供 [ELF](/Atlas/m/elf/vasp/) 使用，因此显式设了 `NPAR = 1`。96³ 是 AECCAR 与 CHGCAR 的细网格；ELFCAR 的采样网格要另外从它自己的文件头读取。

`NGXF/NGYF/NGZF` 决定沿三条晶格矢量保存多少个细网格点。它们加密的是密度的空间表示，ENCUT 控制的则是波函数平面波基组，两者不能互相替代。这里 Fe 的核区密度变化很快，先用 96³、再用 192³，是为了直接观察参考密度积分与盆地电荷对网格的敏感性；每个方向翻倍会使三维点数增加到八倍，也相应增加文件和后处理开销。

```text
[bcgong@localhost charge_elf]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-fe-charge
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
unset SLURM_CPUS_PER_TASK
export I_MPI_PIN_PROCESSOR_LIST=16,17,18,19,20,21,22,23
cd $SLURM_SUBMIT_DIR
mpirun -np 8 /data/software/vasp.5.4.4/bin/vasp_std > out
```
这个教学任务使用现场核验过的 8 个空闲核并行运行，与其他教学任务按次序提交；任务 18187 用时 26 秒。命令 `tail -f out` 可在运行时查看电子步；结束后仍需读停止行与统计尾段。

```text
[bcgong@localhost charge_elf]$ tail -4 OSZICAR
DAV:  16    -0.164736467596E+02    0.20496E-07   -0.31079E-09  2807   0.760E-04    0.228E-04
DAV:  17    -0.164736467728E+02   -0.13183E-07   -0.30314E-10  2702   0.201E-04    0.489E-05
DAV:  18    -0.164736467769E+02   -0.41130E-08   -0.60443E-11  2639   0.102E-04
   1 F= -.16473647E+02 E0= -.16473764E+02  d E =0.351572E-03  mag=     4.2127
```
```text
[bcgong@localhost charge_elf]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
```text
[bcgong@localhost charge_elf]$ ls -lh AECCAR0 AECCAR2 CHGCAR ELFCAR
-rw-rw-r-- 1 bcgong bcgong  16M Sep 22 21:42 AECCAR0
-rw-rw-r-- 1 bcgong bcgong  16M Sep 22 21:42 AECCAR2
-rw-rw-r-- 1 bcgong bcgong  31M Sep 22 21:42 CHGCAR
-rw-rw-r-- 1 bcgong bcgong 139K Sep 22 21:42 ELFCAR
```
文件出现只是开始。AECCAR0 很早就会写出，AECCAR2 才对应自洽完成后的密度；要先确认 SCF 完整结束，再进行相加。

```text
[bcgong@localhost charge_elf]$ head -14 AECCAR0
Fe bcc FM charge and ELF                
   1.00000000000000     
     2.800000    0.000000    0.000000
     0.000000    2.800000    0.000000
     0.000000    0.000000    2.800000
   Fe
     2
Direct
  0.000000  0.000000  0.000000
  0.500000  0.500000  0.500000
 
   96   96   96
 0.22196122414E+07 0.11375194526E+06 0.25172471731E+05 0.14564894925E+05 0.78478711560E+04
 0.37607831076E+04 0.17456520963E+04 0.88918058069E+03 0.56326744509E+03 0.44347649245E+03
```
结构块之后的 `96 96 96` 表示 884,736 个点。相加时，两份文件的晶胞、元素顺序、坐标和网格都必须一致；只按行号相加，或者对不同长度的数据直接 zip，会把错误静默带入参考密度。

随例子提供的 `sum_charge.py` 检查这四项，并且要求标量块长度恰好等于三维网格乘积。脚本只取第一块总电荷密度，写成 CHGCAR_sum 后重新读回，既不混入磁化密度块，也不把 augmentation occupancies 当作网格值相加。

```text
[bcgong@localhost charge_elf]$ python sum_charge.py
AECCAR0_integral = 39.5201008301
AECCAR2_integral = 16.0011953963
CHGCAR_integral = 16.0000000133
grid = [96, 96, 96]
points = 884736
reference_integral = 55.5212962264
scope = first total-charge block only; no spin-density or augmentation blocks copied
```
CHGCAR 的积分是 16.0000000133，与两个 Fe 各 8 个价电子相符。芯电子密度很尖锐，96³ 对其积分仍不够好：AECCAR0 的积分为 39.5201，而这套 Fe 赝势每胞的芯电子数应为 2 × (26 − 8) = 36。先保留这个差异，后面加密网格检查，不用一个“总电子数对上了”掩盖参考密度的数值问题。

运行 Bader 时，把 CHGCAR 作为积分目标，把刚得到的 CHGCAR_sum 作为找边界的参考：

```text
[bcgong@localhost charge_elf]$ <bader_bin>/bader CHGCAR -ref CHGCAR_sum
```

本例执行的是服务器上 Bader 1.05 的可执行文件。输出依次读取目标与参考网格、寻找盆地、细化边界，最后写出 ACF.dat；已有记录显示两个 Bader maxima，真空电荷为 0，总价电子数为 16。继续看每个原子分到了多少电子。

```text
[bcgong@localhost charge_elf]$ cat ACF.dat
    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL
 --------------------------------------------------------------------------------
    1    0.000000    0.000000    0.000000    8.000303     1.161917    10.977166
    2    1.400000    1.400000    1.400000    7.999697     1.161917    10.974834
 --------------------------------------------------------------------------------
    VACUUM CHARGE:               0.0000
    VACUUM VOLUME:               0.0000
    NUMBER OF ELECTRONS:        16.0000
```
`CHARGE` 是盆地内积分得到的价电子数。若把净电荷定义为 Q = ZVAL − N_Bader，那么这里两个 Fe 的 Q 约为 −0.000303 与 +0.000303 e。等价原子出现的这点差异首先反映离散网格和边界划分误差，不能解释成 Fe 原子之间发生了有方向的电荷转移。

`MIN DIST` 是原子到盆地边界的最短距离，并不是最近邻键长。这里 MIN DIST 为 1.161917 Å，而 bcc Fe 的最近邻距离约为 2.424871 Å；前者小于后者是几何上很自然的结果，不能作为分区失败的依据。

再在新目录 `charge_elf_192` 中把 NGXF、NGYF、NGZF 改为 192，保持结构、赝势、k 网格和电子参数一致。本次同时将 ELF 使用的粗网格从 18³ 改为 36³，VASP 任务 18188 用时 102 秒结束。后处理仍执行同一个相加脚本和 Bader 命令。

```text
[bcgong@localhost charge_elf_192]$ cat ACF.dat
    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL
 --------------------------------------------------------------------------------
    1    0.000000    0.000000    0.000000    7.999923     1.187177    10.975705
    2    1.400000    1.400000    1.400000    8.000077     1.187177    10.976295
 --------------------------------------------------------------------------------
    VACUUM CHARGE:               0.0000
    VACUUM VOLUME:               0.0000
    NUMBER OF ELECTRONS:        16.0000
```
两原子现在分别得到 7.999923 和 8.000077 个价电子，仍精确汇总为显示精度内的 16。96³ 到 192³，每个原子的变化约为 0.000380 e，等价原子之间的不对称减小了。与此同时，AECCAR0 积分从 39.5201 靠近到 36.2910：参考密度核区的积分还没有完全闭合，不能把它与价电子盆地积分的稳定程度混为一个指标。

这份小例子可以核对文件、网格、守恒和等价原子。真正比较异质结构的电荷转移时，应逐步加密网格，观察关心的原子或层电荷是否达到所需精度，并在所有对照计算中使用相同分区定义。

下一步接 [差分电荷密度](/Atlas/m/delta-charge/vasp/)，查看电子在空间中的增减位置；或接 [ELF](/Atlas/m/elf/vasp/)，读取这次同一计算写出的局域化函数。盆地电荷与空间分布回答的问题不同，应保留各自的定义。

```text
收敛的固定几何 SCF
  ├─ CHGCAR：积分价电子
  └─ AECCAR0 + AECCAR2：找分区边界的参考
                 └─ 相同结构与完整网格检查 → Bader → ACF.dat
                                                   └─ 总数、等价性与网格加密检查
```
