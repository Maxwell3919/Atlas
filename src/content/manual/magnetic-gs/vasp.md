[VASP：MAGMOM](https://vasp.at/wiki/MAGMOM) · [ISPIN](https://vasp.at/wiki/ISPIN) · [磁构型能量比较教程](https://vasp.at/tutorials/latest/magnetism/part2/) · [OUTCAR](https://vasp.at/wiki/OUTCAR)

总磁矩为零，可以是两个局域磁矩相互抵消，也可以是每个原子都没有自旋极化。用 bcc Fe 的两个原子比较一次，就能在 OUTCAR 里看到这两种情况的区别。

采用 MAGMOM 官方示例中的两原子 bcc 常规胞，元素选 Fe，固定晶格常数 2.8 Å。分别从平行、反平行和非自旋极化三个初始条件计算；三份结构、POTCAR、截断能、k 网格和展宽保持相同。这里只比较这个固定晶胞内的三个候选态。

进入新建的 `fe_bcc/fm` 目录，用 `vi` 编辑输入，保存后逐项读取。

```text
[bcgong@localhost fm]$ cat POSCAR
Fe bcc conventional cell, a=2.8 A
1.0
2.8 0.0 0.0
0.0 2.8 0.0
0.0 0.0 2.8
Fe
2
Direct
0.0 0.0 0.0
0.5 0.5 0.5
```
原点和体心各有一个 Fe，正好可以给两个位置相反的磁矩。若使用只有一个 Fe 的原胞，这种两亚晶格反平行构型就放不进去。

```text
[bcgong@localhost fm]$ cat INCAR
SYSTEM = Fe bcc FM
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
NCORE = 2
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .FALSE.
```
`ISPIN = 2` 开启共线自旋极化，`MAGMOM = 3 3` 给两个 Fe 相同的初始方向。`ISTART = 0`、`ICHARG = 2` 让这条路线从原子电荷开始，避免无意间继承另一种磁态的 WAVECAR 或 CHGCAR。磁矩在迭代中可以改变；3 μB 只是初值。

```text
[bcgong@localhost fm]$ cat KPOINTS
Fe bcc 12x12x12
0
Gamma
12 12 12
0 0 0
```
```text
[bcgong@localhost fm]$ grep -E 'TITEL|ZVAL' POTCAR
   TITEL  = PAW_PBE Fe 06Sep2000
   POMASS =   55.847; ZVAL   =    8.000    mass and valenz
```
每个 Fe 的价电子数为 8。这个数用于后面的电子数与电荷分析；它不是最终局域磁矩。POTCAR 的数据内容不放入网页，需要使用自己有权访问的同一套赝势。

```text
[bcgong@localhost fm]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-fe-fm
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
这份脚本实际使用 8 个 MPI 进程。所在节点的调度器有 64 个核，提交时原有声子任务使用 16 个核，新任务使总申请达到 24 个核，保留了 40 个核。运行中也检查了其他用户进程与实际亲和性。

脚本里的 16–23 是这次现场核验的空闲核编号。它解决的是本机 Intel MPI 从 `SLURM_CPUS_PER_TASK` 隐式推导 pin domain、导致默认绑核与现有任务重叠的问题；换节点时需重新核验分配与实际绑核，不能把这组编号作为通用参数。两次发生重叠的教学试跑已停止并保留旧目录，下面使用修正后结束的结果。

```text
[bcgong@localhost fm]$ sbatch run.slurm
Submitted batch job 18184
```
提交后可以用 `squeue -j 18184` 看队列，用 `tail -f out` 连续查看 DAV 行。离开 tail 的 Ctrl-C 只退出查看；不等于取消调度器中的作业。下面读取这次实际结束后的末尾。

```text
[bcgong@localhost fm]$ tail -6 OSZICAR
DAV:  14    -0.164736558456E+02    0.17455E-05   -0.64595E-07  7024   0.113E-02    0.231E-03
DAV:  15    -0.164736559442E+02   -0.98581E-07   -0.19652E-08  5632   0.162E-03    0.504E-04
DAV:  16    -0.164736559240E+02    0.20253E-07   -0.26883E-09  3104   0.664E-04    0.225E-04
DAV:  17    -0.164736559385E+02   -0.14517E-07   -0.28991E-10  2984   0.189E-04    0.542E-05
DAV:  18    -0.164736559415E+02   -0.30582E-08   -0.59411E-11  3008   0.941E-05
   1 F= -.16473656E+02 E0= -.16473773E+02  d E =0.351602E-03  mag=     4.2127
```
```text
[bcgong@localhost fm]$ grep 'aborting loop because EDIFF is reached' OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
```
第 18 个电子步达到 `EDIFF = 1E-8 eV`；最终总磁矩为 4.2127 μB/胞。接着读取各原子的局域投影。

```text
[bcgong@localhost fm]$ grep -A8 'magnetization (x)' OUTCAR | tail -9
 magnetization (x)
 
# of ion       s       p       d       tot
------------------------------------------
    1       -0.013  -0.058   2.170   2.098
    2       -0.013  -0.058   2.170   2.098
--------------------------------------------------
tot         -0.027  -0.116   4.339   4.196
```
两个 Fe 的局域投影磁矩同为 2.098 μB，方向相同。表中的投影和是 4.196 μB，与整个晶胞积分得到的 4.2127 μB 略有差别；原子投影区之外还有贡献，所以不要强迫这两种定义逐位相等。

另开 `afm` 目录，使用 `cp fm/POSCAR fm/INCAR fm/KPOINTS fm/POTCAR fm/run.slurm afm/` 复制输入。进入 `afm` 后用 `vi INCAR` 将 MAGMOM 改为 `3 -3`，其余物理参数保持一致。脚本仅改任务名。本次提交返回 18185，运行 13 秒结束。

```text
[bcgong@localhost afm]$ cat INCAR
SYSTEM = Fe bcc AFM
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
MAGMOM = 3 -3
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
NCORE = 2
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .FALSE.
```
```text
[bcgong@localhost afm]$ tail -3 OSZICAR
DAV:  17    -0.156073614162E+02    0.35728E-07   -0.10112E-08  2040   0.357E-03    0.789E-04
DAV:  18    -0.156073614215E+02   -0.53635E-08   -0.14757E-08  2520   0.323E-03
   1 F= -.15607361E+02 E0= -.15607823E+02  d E =0.138476E-02  mag=    -0.0000
```
摘要中的总磁矩接近零。先别把这一行读成“非磁”，继续读每个原子的投影表。

```text
[bcgong@localhost afm]$ grep -A8 'magnetization (x)' OUTCAR | tail -9
 magnetization (x)
 
# of ion       s       p       d       tot
------------------------------------------
    1        0.015   0.023   1.279   1.317
    2       -0.015  -0.023  -1.279  -1.317
--------------------------------------------------
tot         -0.000   0.000  -0.000   0.000
```
两个位置分别为 +1.317 和 −1.317 μB，这是一份反平行的自洽解。它与下面不允许自旋极化的计算不是同一状态。

再复制一份输入到 `nm`，用 `vi INCAR` 将 ISPIN 改为 1，删除 MAGMOM 行。其余结构、赝势和网格仍与 FM 相同；这次任务 18186 运行 6 秒结束。

```text
[bcgong@localhost nm]$ tail -4 OSZICAR
DAV:  13    -0.154907076144E+02   -0.23614E-06   -0.27636E-08  1740   0.307E-03    0.193E-04
DAV:  14    -0.154907076366E+02   -0.22224E-07   -0.10682E-09  1012   0.391E-04    0.721E-05
DAV:  15    -0.154907076292E+02    0.74524E-08   -0.14799E-10  1008   0.160E-04
   1 F= -.15490708E+02 E0= -.15490741E+02  d E =0.101602E-03
```
非自旋极化计算不会在这里给出 mag 摘要。三份都要有电子收敛行与 OUTCAR 统计尾段，才能把能量排在同一张表里。

```text
[bcgong@localhost fe_bcc]$ python magnetic_energies.py
fm  F=-16.47365594 eV  E0=-16.47377314 eV  dE0=   0.0000 meV/atom  M= 4.2127 muB/cell
afm F=-15.60736142 eV  E0=-15.60782301 eV  dE0= 432.9751 meV/atom  M=-0.0000 muB/cell
nm  F=-15.49070763 eV  E0=-15.49074150 eV  dE0= 491.5158 meV/atom  M= 0.0000 muB/cell
```
脚本先用 SHA-256 核对三份 POSCAR、KPOINTS、POTCAR 完全一致，再检查电子收敛与程序统计段。表格同时保留有限展宽自由能 F 和 `energy(sigma->0)`；最后一列能量差统一选零展宽外推量，并除以每胞两个 Fe，换算成 meV/atom。

在这组固定设置下，FM 比所算 AFM 低约 432.98 meV/atom，比非自旋极化解低约 491.52 meV/atom。这个排序回答的是三份候选解之间的比较。要形成材料磁基态结论，还需检查更多可能的磁超胞、各磁态的几何优化、k 网格及展宽对相对能量的影响。

将 `magnetic-energies.json` 与 `plot_magnetic.py` 放到本机同一目录，执行 `python3 plot_magnetic.py`，即可生成能量差柱图和 PDF。图标题保留固定晶格常数，纵轴保留每原子单位，避免把每胞能量差误读成每原子值。

下一步接 [磁各向异性能](/Atlas/m/mae/vasp/)，在需要比较的磁态上引入 SOC 并旋转磁化方向；或者接 [交换参数](/Atlas/m/exchange-j/vasp/)，为选定自旋模型准备足够多的磁构型能量。

![固定晶格常数下 Fe 的三个磁构型能量](/Atlas/examples/vasp/fe-bcc/magnetic-energies.png)

```text
同一固定晶胞与同一组数值参数
  ├─ ISPIN=2，MAGMOM 平行 → FM 自洽解
  ├─ ISPIN=2，MAGMOM 反平行 → AFM 自洽解
  └─ ISPIN=1 → 非自旋极化解
             └─ 核对最终局域磁矩与收敛 → 统一能量定义比较
```
