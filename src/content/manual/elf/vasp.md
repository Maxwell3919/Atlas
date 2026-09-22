[VASP：LELF](https://vasp.at/wiki/LELF) · [ELFCAR](https://vasp.at/wiki/ELFCAR) · [NPAR](https://vasp.at/wiki/NPAR)

ELF 文件中的数是电子局域化函数，不能按 CHGCAR 的电子密度单位去读。这里接着 [bcc Fe 磁构型比较](/Atlas/m/magnetic-gs/vasp/) 的铁磁小体系，读取实际生成的两个自旋通道，并画出经过 z = 0 的截面。

下载 [输入、完整 OUTCAR、ELFCAR 与绘图脚本](/Atlas/examples/vasp/fe-bcc-lesson-files.tar.gz)。其中 `charge_elf` 和 `charge_elf_192` 分别保留较粗、较细的实空间采样，后者用于下面的截图数据。它们都是共线自旋计算；这条 ELF 路线不接非共线 SOC 输出。

在新目录中用 `cp` 复制 FM 的结构、KPOINTS 和 POTCAR，进入目录后用 `vi INCAR` 打开 LELF。保存后读回的输入如下。

```text
[bcgong@localhost charge_elf_192]$ cat INCAR
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
NGXF = 192
NGYF = 192
NGZF = 192

NGX = 36
NGY = 36
NGZ = 36
```
这份 VASP 5.4.4 计算显式设置了 `NPAR = 1`，与 LELF 文档的要求一致。不要保留另一份输入的 NPAR=4，然后只把 LELF 打开。`LAECHG` 与细网格用于同次计算的 [Bader 分析](/Atlas/m/bader/vasp/)，ELFCAR 自己的采样来自 NGX、NGY、NGZ：本例是 36 × 36 × 36。

结构固定，`ISPIN = 2`，两个 Fe 的初始磁矩平行。程序最终收敛到的总磁矩约为 4.2127 μB/胞；这里没有用初始 MAGMOM 数值代替结果。

```text
[bcgong@localhost charge_elf_192]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-fe-grid192
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
任务 18188 用 8 个 MPI 进程运行，实际耗时约 102 秒；每次只运行一个教学任务，并在原有研究任务之外保留至少半台机器的空闲算力。

```text
[bcgong@localhost charge_elf_192]$ tail -4 OSZICAR
DAV:  16    -0.164736471272E+02    0.20405E-07   -0.31078E-09  2807   0.760E-04    0.228E-04
DAV:  17    -0.164736471409E+02   -0.13691E-07   -0.30315E-10  2702   0.201E-04    0.489E-05
DAV:  18    -0.164736471451E+02   -0.41252E-08   -0.60352E-11  2639   0.102E-04
   1 F= -.16473647E+02 E0= -.16473764E+02  d E =0.351572E-03  mag=     4.2127
```
```text
[bcgong@localhost charge_elf_192]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
```text
[bcgong@localhost charge_elf_192]$ grep -E 'dimension x,y,z|LELF' OUTCAR
   dimension x,y,z NGX =    36 NGY =   36 NGZ =   36
   dimension x,y,z NGXF=   192 NGYF=  192 NGZF=  192
   dimension x,y,z NGX =    18 NGY =   18 NGZ =   18
   LELF         =      T    write electronic localiz. function (ELF)
```
这几行分别确认电子迭代结束、LELF 确实启用，以及粗网格 36³ 与细网格 192³。两套网格服务于不同输出，不能看到 AECCAR 使用 192³ 就假定 ELFCAR 也有同样的点数。

```text
[bcgong@localhost charge_elf_192]$ head -15 ELFCAR
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
 
   36   36   36
 0.18012E-01 0.31080E-03 0.73938E-04 0.16325E-03 0.73557E-03 0.30330E-02 0.95991E-02 0.23283E-01 0.44567E-01 0.69501E-01
 0.90951E-01 0.10258     0.10283     0.96336E-01 0.90702E-01 0.91312E-01 0.98696E-01 0.10827     0.11271     0.10827    
 0.98696E-01 0.91312E-01 0.90702E-01 0.96336E-01 0.10283     0.10258     0.90951E-01 0.69501E-01 0.44567E-01 0.23283E-01
```
文件头仍是晶胞、元素、原子数与 Direct 坐标；空行后的 `36 36 36` 才是第一个 ELF 数据块的形状。x 索引最快、z 最慢，因此一张固定 z 截面恰好由连续的 36 × 36 个数构成。

对于这份 `ISPIN = 2` 输出，第一个块是 ELF↑，后面接 ELF↓。两个通道都应读取；只拿第一块画图，不能称为一份包含两个自旋通道的完整检查。

```text
[bcgong@localhost charge_elf_192]$ python read_elf.py
up grid=[36, 36, 36] values=46656 min=7.1308e-05 max=0.13286
down grid=[36, 36, 36] values=46656 min=0.00011024 max=0.3339
Wrote elf-up-z0.dat and elf-down-z0.dat; z=0 slice
```
脚本检查了两个块各自都有 46,656 个有限数值，形状一致，范围在 0–1 之内。本例上自旋的最大值约 0.13286，下自旋约 0.33390。验收不止是 `ls` 看文件存在：还包括完整网格、两个通道、数值范围和来源 SCF 的收敛。

脚本把 z = 0 的截面分别写入 `elf-up-z0.dat` 与 `elf-down-z0.dat`，每份有 36 行、每行 36 个数。它们是无量纲的 ELF 值，不需要乘电子电荷或除以晶胞体积。

```text
[bcgong@localhost charge_elf_192]$ head -2 elf-up-z0.dat
0.01801200 0.00031080 0.00007394 0.00016325 0.00073557 0.00303300 0.00959910 0.02328300 0.04456700 0.06950100 0.09095100 0.10258000 0.10283000 0.09633600 0.09070200 0.09131200 0.09869600 0.10827000 0.11271000 0.10827000 0.09869600 0.09131200 0.09070200 0.09633600 0.10283000 0.10258000 0.09095100 0.06950100 0.04456700 0.02328300 0.00959910 0.00303300 0.00073557 0.00016325 0.00007394 0.00031080
0.00031080 0.00011587 0.00007131 0.00018791 0.00082675 0.00327530 0.01007200 0.02396500 0.04528300 0.06999900 0.09104900 0.10228000 0.10234000 0.09594000 0.09060100 0.09151900 0.09909300 0.10870000 0.11313000 0.10870000 0.09909300 0.09151900 0.09060100 0.09594000 0.10234000 0.10228000 0.09104900 0.06999900 0.04528300 0.02396500 0.01007200 0.00327530 0.00082675 0.00018791 0.00007131 0.00011587
```
切片上的每一行对应一个 y，列对应 x。这里晶格边长 2.8 Å，因此两个相邻采样点相隔约 0.07778 Å。

```text
[bcgong@localhost charge_elf]$ python read_elf.py
up grid=[18, 18, 18] values=5832 min=7.3938e-05 max=0.13202
down grid=[18, 18, 18] values=5832 min=0.00015527 max=0.33107
Wrote elf-up-z0.dat and elf-down-z0.dat; z=0 slice
```
较粗的文件是每个通道 18³ 个点。加密后，两通道最大值分别从 0.13202、0.33107 变为 0.13286、0.33390；主要数值范围相近，但粗网格无法显示细网格才采到的位置。比较两张图时应保持同一截面、同一颜色范围，不靠改变色标来制造差异。

在本机进入解包后的 `fe-bcc/charge_elf_192`，执行：

```bash
python3 plot_elf.py
```

脚本读取两份截面表，并排画出上、下自旋通道；横纵轴为 Å，色标统一为 0–1，输出 `elf-z0.png` 和 `elf-z0.pdf`。在 VESTA 中也可打开 ELFCAR 查看三维等值面；截图时应写明所选自旋数据块与等值面数值。

这张截面反映的是所算共线磁态中的局域化函数。不能把某个颜色直接换算为转移了多少个电子；要讨论转移电子数，接 [Bader](/Atlas/m/bader/vasp/)。要看成键前后的密度增减位置，接 [差分电荷密度](/Atlas/m/delta-charge/vasp/)。

![Fe 上、下自旋的 ELF 截面](/Atlas/examples/vasp/fe-bcc/charge_elf_192/elf-z0.png)

```text
收敛的共线自旋 SCF + LELF + NPAR=1
  └─ ELFCAR → 结构头与两套自旋网格检查
                   └─ 固定 z 的两个截面 → 同一色标可视化
```
