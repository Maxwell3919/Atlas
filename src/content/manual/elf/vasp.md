[VASP：LELF](https://vasp.at/wiki/LELF) · [ELFCAR](https://vasp.at/wiki/ELFCAR) · [NPAR](https://vasp.at/wiki/NPAR)

ELF 文件中的数是电子局域化函数，不能按 CHGCAR 的电子密度单位去读。这里接着 [bcc Fe 磁构型比较](/Atlas/m/magnetic-gs/vasp/) 的铁磁小体系，读取实际生成的两个自旋通道，并在 VESTA 中查看同一阈值下的三维等值面。

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

`NPAR = 1` 指带并行分组数，不表示只使用一个 CPU；下面仍由 8 个 MPI 进程运行。`NGX/NGY/NGZ` 在这里显式控制 ELF 的采样密度，`NGXF/NGYF/NGZF` 控制另一套细网格，二者虽然同属一次计算，改动的输出分辨率不同。若只把绘图插值调得更平滑，文件中的 36³ 个原始采样值并不会增加；需要更细的空间检查时，应重新计算网格并读回 ELFCAR。

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
任务 18188 用 8 个 MPI 进程运行，实际耗时约 102 秒。

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

与密度文件相比，ELFCAR 的外壳很相似，数据的含义却不同：ELF 已经是无量纲函数，既不除以体积，也不再除以网格点数或本次最大值。后一种做法会把 0.13 人为画成 1，失去与原文件的对应。

对于这份 `ISPIN = 2` 输出，第一个块是 ELF↑，后面接 ELF↓。两个通道都应读取；只拿第一块画图，不能称为一份包含两个自旋通道的完整检查。

## 分离两个标量块，再交给 VESTA

下载[完整原始 ELFCAR、分离数据、场景与脚本](/Atlas/examples/charge-vesta-files.tar.gz)，解包进入 `charge-vesta`。本次转换不合并自旋通道：两个输出都保留相同结构，各写一块无量纲标量网格。

下面的需求说明根据本例实际转换整理，可复制给 AI 编程助手：

```text
编写 Python 3 标准库命令行程序 split_elf_spin_channels.py。输入 --input 为本例 ISPIN=2、共线自旋 VASP ELFCAR；--output-dir 为新目标目录。保留 POSCAR 风格结构头，识别两次三整数网格尺寸，第一块为 ELF_up、第二块为 ELF_down；检查尺寸相同，逐块恰好 nx*ny*nz 个有限数值，范围0–1。x索引最快。不能把原子坐标误认为网格头，不能合并、平均、除体积或除最大值。检查两块之间及末尾无额外未解析内容，遇到本例以外的布局清楚报错。分别写 ELFCAR_up.vasp、ELFCAR_down.vasp，只含结构与一块网格；JSON记录输入SHA256、网格、通道顺序、每通道min/max/mean。所有目标文件应在写入前检查，已有文件则拒绝覆盖。终端打印验证摘要。GUI操作使用VESTA逐一打开两文件，Properties → Isosurfaces设同一无量纲阈值0.10，保存各场景并File → Export Raster Image导出PNG。保持网格与阈值不变；图注标通道、阈值、36³采样，区分原始网格与显示插值。
```

[完整源码：split_elf_spin_channels.py](/Atlas/examples/charge-vesta/scripts/split_elf_spin_channels.py)。只需 Python 3 标准库，不依赖 NumPy 或绘图库。

```bash
python3 -B scripts/split_elf_spin_channels.py --input elf/ELFCAR --output-dir new-elf
```

本次读取真实 ELFCAR 的输出：

```text
grid: 36 36 36 (46656 points per spin channel)
ELF_up: min=0.00007131 max=0.13286000 mean=0.09257966
ELF_down: min=0.00011024 max=0.33390000 mean=0.15832494
wrote: ELFCAR_up.vasp
wrote: ELFCAR_down.vasp
```

两个通道各有 46,656 个有限值，[验证摘要](/Atlas/examples/charge-vesta/elf/elf-spin-channels.summary.json)保留完整范围和输入哈希。ELF 为无量纲函数，上面的均值不是盆地电子数。

### 先看上自旋，再用相同阈值打开下自旋

通过 **File → Open** 打开 `elf/ELFCAR_up.vasp`；在 **Properties → Isosurfaces** 设置 `ELF=0.10`，使用蓝色半透明表面，保留金色 Fe 球。通过 **File → Export Raster Image** 导出 PNG，并用 **File → Save As** 保存场景。

<figure><img src="/Atlas/examples/elf/elf_up_isosurface.png" alt="真实 VESTA 导出的 bcc Fe 上自旋 ELF=0.10 等值面" loading="lazy"/><figcaption>上自旋 ELF↑=0.10，36³ 原始网格。蓝色为等值面，金色球为 Fe，周期单元边界截断部分表面；图中表面的封闭或连接形状只对应这一阈值。</figcaption></figure>

再打开 `elf/ELFCAR_down.vasp`，同样设置 `ELF=0.10` 后导出。可直接下载场景 [elf-up.vesta](/Atlas/examples/charge-vesta/elf/elf-up.vesta)、[elf-down.vesta](/Atlas/examples/charge-vesta/elf/elf-down.vesta)，它们用相对路径导入各自的单块网格。

<figure><img src="/Atlas/examples/elf/elf_down_isosurface.png" alt="真实 VESTA 导出的 bcc Fe 下自旋 ELF=0.10 等值面" loading="lazy"/><figcaption>下自旋 ELF↓=0.10，使用同一36³网格和阈值。两幅截图视向不同，比较时先按左下角晶轴对应方向；不要用投影面积估算两个通道的体积或电子数。</figcaption></figure>

同一阈值下两通道的形貌不同，与数值范围差异相呼应。单凭 ELF 不能把这一区别归属到具体 d 轨道或某个转移电子数；轨道组成要结合投影分析，实空间电荷分区接 [Bader](/Atlas/m/bader/vasp/)。

## 参照文献中的阈值与截面表达

Shi 等研究二维 LaH₂ 时，在 Fig. 1(c–f) 配合 ELF=0.75 三维等值面与0–1色标的二维截面。[J. Phys.: Condens. Matter 34, 475303 (2022)](https://doi.org/10.1088/1361-648X/ac96bb)。这说明等值面阈值和截面色标应分别标注；0.75 不适用于本例 Fe 的数值范围，也不能用增大显示插值代替更细原始网格。

```text
共线自旋 SCF + LELF + NPAR=1 → ELFCAR 两块验证
  → 分别保存单块 ELF↑/ELF↓ → VESTA 同阈值等值面 → 导出与场景保存
```
