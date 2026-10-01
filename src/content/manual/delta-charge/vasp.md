两个 H 原子在固定距离上组成 H₂ 后，电子是向键中间聚集，还是主要留在原子附近？本页在同一晶胞中计算固定键长的分子 AB，以及冻结在分子原位置的单个 H 原子 A、B，再求 Δn=nAB−nA−nB。正负区域和各自的积分回答相对于这组原子参考，电子在哪里积累、在哪里耗尽；两颗 H 等价，这里关注成键重排的空间分布。

这种相减首先要说明参考态。[Shang 等的 Si–N 功能化 h-BN 研究](https://doi.org/10.1103/jmys-zkgs)在 Sec. III、Fig. 1(d) 附近明确写出完整体系减 h-BN、N、Si 的密度定义。本例采用分子减两个原位自旋极化 H 原子的定义；参考片段、几何和自旋由本页输入确定，文献中的 Si–B 成键结论不移到 H₂。

[VASP：CHGCAR 文件结构](https://vasp.at/wiki/CHGCAR) · [VASP：细 FFT 网格 NGXF](https://vasp.at/wiki/NGXF) · [VASP：初始磁矩 MAGMOM](https://vasp.at/wiki/MAGMOM)

```text
Δn(r) = n_AB(r) − n_A(r) − n_B(r)
```

这里的 n 是电子数密度，正值表示相对于冻结原子参考的电子积累，负值表示电子耗尽。它不是带负号的电荷密度 −en；也不能把正值区域的积分直接当成从一个 H 转移给另一个 H 的电子数。

[下载输入、小体积原始输出、分析与绘图脚本](/Atlas/examples/h2-delta-charge-files.tar.gz)，解压为 `h2-delta-charge`。三份密度单独提供：[AB/CHGCAR.gz](/Atlas/examples/h2-delta-charge/AB/CHGCAR.gz)、[A/CHGCAR.gz](/Atlas/examples/h2-delta-charge/A/CHGCAR.gz)、[B/CHGCAR.gz](/Atlas/examples/h2-delta-charge/B/CHGCAR.gz)。分别放回解压目录的 AB、A、B 子目录，保留文件名 `CHGCAR.gz`，解析程序可以直接读取，不必先解压。VESTA 等值面需要完整三维网格，下载方式见后面的转换步骤。POTCAR 正文不随包分发；重新运行 VASP 需要自行准备有使用权限的同一份 H 赝势，并核对包内指纹。

## 三份结构，保留同一个坐标系

本例人为构造一个边长 10 Å 的立方晶胞，两个 H 在 (5,5,4.63) 和 (5,5,5.37) Å，键长固定为 0.74 Å，用来观察指定几何下的成键电子密度。对照原子保持在分子里的位置，删去另一个原子后没有移到原点，也没有单独弛豫。

三个 POSCAR 保留同一个晶胞和坐标系：

```console
[bcgong@localhost grid144]$ cat AB/POSCAR A/POSCAR B/POSCAR
H2 charge difference AB
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
2
Cartesian
5.000000 5.000000 4.630000
5.000000 5.000000 5.370000

H2 charge difference A
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
1
Cartesian
5.000000 5.000000 4.630000

H2 charge difference B
1.0
10.0 0.0 0.0
0.0 10.0 0.0
0.0 0.0 10.0
H
1
Cartesian
5.000000 5.000000 5.370000
[bcgong@localhost grid144]$
```

三份晶胞矩阵完全相同；AB 有两个原子，A 和 B 各一个。不同原子数会让 CHGCAR 的结构头长度不同，所以不能按同一个固定行号跳过表头，然后直接相减整个文本。

## 先让电子协议和 FFT 网格一致

三项计算放在 `grid144` 的 AB、A、B 目录。完整分子的输入为：

```console
[bcgong@localhost grid144]$ cat AB/INCAR
SYSTEM = H2 fixed geometry charge difference
ISTART = 0
ICHARG = 2
ENCUT = 400
PREC = Accurate
EDIFF = 1E-8
NELM = 100
ALGO = Normal
ISMEAR = 0
SIGMA = 0.02
ISPIN = 2
MAGMOM = 1 -1
ISYM = 0
NBANDS = 8
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
LMAXMIX = 2
NCORE = 1
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .TRUE.
NGX = 72
NGY = 72
NGZ = 72
NGXF = 144
NGYF = 144
NGZF = 144
[bcgong@localhost grid144]$
```

`ISTART=0`、`ICHARG=2` 让三项各自从原子叠加电荷开始做自洽。这里需要的是三个独立自洽结果，不能把 AB 的密度直接复制成 A、B 的最终密度。`IBRION=-1`、`NSW=0` 保持结构不动。

三项统一使用 400 eV 截断、`PREC=Accurate`、Gaussian 展宽 `SIGMA=0.02 eV` 和 `EDIFF=1E-8 eV`。相同设置是逐点相减的前提。应用到其他分子时，需分别检查截断、盒长与展宽对目标密度的影响。

`ISPIN=2` 让单个 H 可以得到一个未配对电子。A 的初始 `MAGMOM=1`，B 为 `−1`，分子为 `1 -1`；除了 `SYSTEM` 和 `MAGMOM`，三份 INCAR 的电子参数逐项一致。MAGMOM 是初始条件，最终磁矩还要从输出和密度积分验证，不能只按输入预期填写。

`LCHARG=.TRUE.` 写出后面要相减的 CHGCAR。`LWAVE=.FALSE.` 关闭波函数写出，目录内的 WAVECAR 为零字节。`LREAL=.FALSE.` 在倒空间处理投影，`LASPH=.TRUE.` 保留 PAW 球内非球形贡献；这些选择在三份输入中保持一致。

密度使用 144×144×144 的细网格，粗网格为 72×72×72。这两套网格各有用途，不能只保证最终 CHGCAR 的行数一致，却忽略电子计算本身的网格警告。

本例前一次 48³/96³ 尝试虽然结束并写出了密度，OUTCAR 仍明确提醒：

```console
[bcgong@localhost grid144]$ grep -A 8 -B 2 "Your FFT grids" ../AB/OUTCAR
|           W    W  A    A  R    R  N    N  II  N    N   GGGG   !!!           |
|                                                                             |
|      Your FFT grids (NGX,NGY,NGZ) are not sufficient for an accurate        |
|      calculation.                                                           |
|      The results might be wrong                                             |
|      good settings for NGX NGY and  NGZ are                                 |
|                        70  70  and  70                                      |
|     Mind: This setting results in a small but reasonable wrap around error  |
|     It is also necessary to adjust these  values to the FFT routines you use|
|                                                                             |
 -----------------------------------------------------------------------------
[bcgong@localhost grid144]$
```

三项改为 72³/144³ 后，网格不足警告消失。下面使用的是这组三份密度；若要确定所需数值精度，还应继续检查网格加密后的变化。

孤立分子用大盒子与 Γ 点作周期近似，实际 KPOINTS 为：

```console
[bcgong@localhost grid144]$ cat AB/KPOINTS
Gamma for an isolated molecule in a periodic box
0
Gamma
1 1 1
0 0 0
[bcgong@localhost grid144]$
```

盒长仍需按研究问题检查。仅仅用了 Γ 点和 10 Å 晶胞，并不自动证明周期镜像效应可以忽略。

## 三份 SCF 串行完成，再读输出

AB 的真实提交脚本如下。此现场用 4 个 MPI 进程；A、B 脚本对应各自目录，电子参数不变。

```console
[bcgong@localhost grid144]$ cat AB/run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-h2g144-AB
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
unset SLURM_CPUS_PER_TASK
export I_MPI_PIN_PROCESSOR_LIST=16,17,18,19
cd "$SLURM_SUBMIT_DIR"
mpirun -np 4 <vasp_bin>/vasp_std > out
[bcgong@localhost grid144]$
```

`OMP_NUM_THREADS=1` 避免每个 MPI 进程再启动额外线程。`I_MPI_PIN_PROCESSOR_LIST` 是这个节点现场使用的核绑定，换机器应遵循其调度配置。这里按 AB、A、B 的次序串行提交，每项结束并核对之后才继续下一项。

```console
[bcgong@localhost AB]$ sbatch run.slurm
Submitted batch job 18203
[bcgong@localhost AB]$ tail -4 out
DAV:  26    -0.675757525392E+01   -0.96419E-07   -0.89909E-10    32   0.964E-05    0.141E-05
DAV:  27    -0.675757527955E+01   -0.25634E-07   -0.32106E-10    32   0.582E-05    0.892E-06
DAV:  28    -0.675757528376E+01   -0.42084E-08   -0.20943E-11    32   0.152E-05
   1 F= -.67575753E+01 E0= -.67575753E+01  d E =-.395750E-14  mag=    -0.0000
[bcgong@localhost AB]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       37.584
[bcgong@localhost AB]$ cd ../A
[bcgong@localhost A]$ sbatch run.slurm
Submitted batch job 18204
[bcgong@localhost A]$ tail -3 out
DAV:  31    -0.111553427162E+01   -0.37212E-07    0.11147E-11    40   0.712E-07    0.109E-07
DAV:  32    -0.111553427860E+01   -0.69796E-08    0.21005E-11    32   0.517E-07
   1 F= -.11155343E+01 E0= -.11155343E+01  d E =-.379612E-12  mag=     1.0000
[bcgong@localhost A]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       43.484
[bcgong@localhost A]$ cd ../B
[bcgong@localhost B]$ sbatch run.slurm
Submitted batch job 18205
[bcgong@localhost B]$ grep -E "Your FFT grids|aborting loop|Elapsed time" OUTCAR
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       42.155
[bcgong@localhost B]$ cd ..
```

`aborting loop because EDIFF is reached` 在这里表示电子循环达到所设精度后退出，不是程序异常。三项分别耗时 37.584、43.484、42.155 秒，末尾都有完整运行统计，也不再出现 FFT 网格不足提示。

等待时可在对应目录运行 `tail -f out` 或 `watch -n 2 "tail -n 8 out"`；Ctrl-C 退出的是监视。看到文件不再增长以后，仍要读收敛与正常结束段，不能只看任务已离开队列。

## OUT 的头部、电子迭代与末尾分别告诉我们什么

先看 AB 的标准输出开头：

```console
[bcgong@localhost grid144]$ head -n 24 AB/out
 running on    4 total cores
 distrk:  each k-point on    4 cores,    1 groups
 distr:  one band on    1 cores,    4 groups
 using from now: INCAR     
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Feb 26 2024 21:30:50) complex          
  
 POSCAR found type information on POSCAR  H 
 POSCAR found :  1 types and       2 ions
 scaLAPACK will be used
 LDA part: xc-table for Pade appr. of Perdew
 POSCAR, INCAR and KPOINTS ok, starting setup
 FFT: planning ...
 WAVECAR not read
 entering main loop
       N       E                     dE             d eps       ncg     rms          rms(c)
DAV:   1     0.330307833686E+01    0.33031E+01   -0.36026E+02    32   0.737E+01
DAV:   2    -0.473855047208E+01   -0.80416E+01   -0.80416E+01    32   0.253E+01
DAV:   3    -0.523992505854E+01   -0.50137E+00   -0.50137E+00    40   0.977E+00
DAV:   4    -0.524239736218E+01   -0.24723E-02   -0.24723E-02    32   0.677E-01
DAV:   5    -0.524242226125E+01   -0.24899E-04   -0.24899E-04    32   0.648E-02    0.455E+00
DAV:   6    -0.656955046096E+01   -0.13271E+01   -0.55591E+00    32   0.924E+00    0.337E+00
DAV:   7    -0.655514804124E+01    0.14402E-01   -0.10946E+00    32   0.371E+00    0.163E+00
DAV:   8    -0.660675599031E+01   -0.51608E-01   -0.24393E-01    32   0.135E+00    0.950E-01
DAV:   9    -0.674177913766E+01   -0.13502E+00   -0.19305E-01    32   0.123E+00    0.399E-01
[bcgong@localhost grid144]$
```

这里确认了 VASP 版本、实际 4 个进程、1 种元素和 2 个原子。`WAVECAR not read` 与本次从头计算的输入一致。`DAV` 行是电子迭代，列中有当前能量、能量变化 dE、本征值求解变化 d eps 与残差；它们属于迭代过程，前几步的能量不能用作最终结果。

再读 OUTCAR 中与这次密度对应的实际参数：

```console
[bcgong@localhost grid144]$ grep -E "NELECT|dimension x,y,z|aborting loop|Elapsed time" AB/OUTCAR
   dimension x,y,z NGX =    72 NGY =   72 NGZ =   72
   dimension x,y,z NGXF=   144 NGYF=  144 NGZF=  144
   dimension x,y,z NGX =    70 NGY =   70 NGZ =   70
   NELECT =       2.0000    total number of electrons
------------------------ aborting loop because EDIFF is reached ----------------------------------------
                         Elapsed time (sec):       37.584
[bcgong@localhost grid144]$
```

输出中的实际粗、细网格为 72³ 和 144³。另一个 70³ 行是程序给出的网格尺度信息，不应覆盖已经明确写出的实际设置；最终还要从 CHGCAR 表头核对密度数组的真实尺寸。电子数 `NELECT=2` 是完整 H₂ 的价电子数，A、B 各为 1。

目录中的文件有不同分工：`out` 和 `OSZICAR` 便于看电子步，`OUTCAR` 保留实际参数、能量、磁矩、力与结束统计；`CHGCAR` 提供总密度和磁化密度网格；`vasprun.xml` 是结构化输出；`CONTCAR` 保存最终结构。这个固定构型例子中没有新的离子移动。

## 读 CHGCAR 时，把总密度与磁化密度分开

先看 AB/CHGCAR 的头部：

```console
[bcgong@localhost grid144]$ head -n 15 AB/CHGCAR
H2 fixed geometry charge difference     
   1.00000000000000     
    10.000000    0.000000    0.000000
     0.000000   10.000000    0.000000
     0.000000    0.000000   10.000000
   H 
     2
Direct
  0.500000  0.500000  0.463000
  0.500000  0.500000  0.537000
 
  144  144  144
 -.14180101703E-06 0.15839254613E-05 0.82756458881E-05 0.18919626660E-04 0.24598790238E-04
 0.17342576419E-04 0.32962757902E-05 -.14502942528E-05 0.91047738927E-05 0.21835186348E-04
 0.20713305658E-04 0.74212176581E-05 -.14663704630E-05 0.36751736964E-05 0.14473913947E-04
[bcgong@localhost grid144]$
```

结构头后面的 `144 144 144` 才是第一份体数据的网格尺寸，共 2,985,984 个值。数值按 x 最快、再 y、再 z 的顺序存放。第一块是 `n↑+n↓`，后面还包括 PAW 单中心信息和第二块 `n↑−n↓`；不能把后续所有数字都当成同一份总密度接在一起。

在这份文件的写出约定下，设第一块原始值为 Dᵢ，晶胞体积 V=1000 Å³：

```text
n_i = D_i / V                         单位：e/Å³
NELECT = Σ_i D_i / Ngrid
Δn_i = (D_AB,i − D_A,i − D_B,i) / V
∫ Δn(r) dr ≈ Σ_i (D_AB,i − D_A,i − D_B,i) / Ngrid
```

这里的网格体积元是 V/Ngrid。保留原始数组再按实际体积换算，可以同时检查单位和电子数；不需要用未知比例把积分强行调整成期望值。

先核对三份密度确实可逐点相减，再计算电子数与差分积分。检查程序需要分别读取总密度和磁化密度，以便将积分与 NELECT、最终磁矩对应起来。可把下面的需求交给 AI 编程助手：

```text
编写 Python 3 的 analyze_charge.py，读取 AB、A、B 目录的 CHGCAR 或 CHGCAR.gz 及对应 OUTCAR、OSZICAR、KPOINTS 与赝势指纹。核对电子收敛、正常退出、相同晶胞和网格、相同 k 点及赝势，并确认 A/B 原子保持 AB 中原位。分别读取第一块总密度与第二块磁化密度，各取 nx*ny*nz 个值；按 ΣD/N 积分，检查总数与 NELECT、磁化积分与最终磁矩。用第一块计算 AB−A−B，输出全胞、正值、负值积分及 e/Å³ 极值，保存 CHGDIFF.vasp、delta-charge.cube、delta-planar.csv、delta-y5.csv、charge-difference-summary.json。保持源文件只读，按原始数据计算，不归一化到期望值。
```

[完整源码：analyze_charge.py](/Atlas/examples/h2-delta-charge/analyze_charge.py)。在解包后的 `h2-delta-charge` 目录运行；脚本读取页首下载的三份 `CHGCAR.gz`。原始执行记录如下：

<details>
<summary>analyze_charge.py 的完整源码</summary>

```python
from __future__ import print_function
import os, re, math, json, hashlib, csv, gzip, io
BOHR = 0.529177210903

def det(cell):
    a,b,c=cell
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def finite(values):
    return all(not (math.isnan(x) or math.isinf(x)) for x in values)

def open_text(filename):
    if os.path.isfile(filename):
        return io.open(filename, 'r', encoding='ascii')
    if os.path.isfile(filename+'.gz'):
        return io.TextIOWrapper(gzip.open(filename+'.gz', 'rb'), encoding='ascii')
    raise IOError('Missing '+filename+' or '+filename+'.gz')

def digest(filename):
    if os.path.isfile(filename):
        handle=open(filename,'rb')
    elif os.path.isfile(filename+'.gz'):
        handle=gzip.open(filename+'.gz','rb')
    elif filename.endswith('/POTCAR') and os.path.isfile(filename+'.sha256'):
        value=open(filename+'.sha256').read().split()[0]
        if not re.match(r'^[0-9a-f]{64}$',value):
            raise ValueError('Invalid pseudopotential fingerprint')
        return value
    else:
        raise IOError('Missing source '+filename)
    sha=hashlib.sha256()
    while True:
        chunk=handle.read(1024*1024)
        if not chunk:break
        sha.update(chunk)
    handle.close()
    return sha.hexdigest()

def read_charge(filename):
    f=open_text(filename)
    head=[f.readline(),f.readline()]
    scale=float(head[1].split()[0])
    if scale<=0:raise ValueError('This example requires a positive scalar scale')
    lines=[f.readline() for _ in range(3)];head+=lines
    cell=[[float(x)*scale for x in line.split()[:3]] for line in lines]
    species=f.readline();counts_line=f.readline();head += [species,counts_line]
    counts=list(map(int,counts_line.split()));nat=sum(counts)
    mode=f.readline();head.append(mode)
    if mode.lower().startswith('s'):mode=f.readline();head.append(mode)
    coords_lines=[f.readline() for _ in range(nat)];head+=coords_lines
    coords=[[float(x) for x in line.split()[:3]] for line in coords_lines]
    if mode.lower().startswith('d'):
        positions=[[sum(v[k]*cell[k][a] for k in range(3)) for a in range(3)] for v in coords]
    elif mode.lower().startswith(('c','k')):
        positions=[[x*scale for x in v] for v in coords]
    else:raise ValueError('Unknown coordinate mode')
    line=f.readline()
    while line and not line.strip():line=f.readline()
    grid=list(map(int,line.split()))
    if len(grid)!=3 or min(grid)<=0:raise ValueError('Invalid charge grid')
    n=grid[0]*grid[1]*grid[2]
    def block():
        values=[]
        while len(values)<n:
            line=f.readline()
            if not line:raise ValueError('Truncated scalar block')
            values.extend(float(x.replace('D','E')) for x in line.split())
        if len(values)!=n or not finite(values):raise ValueError('Invalid scalar block length/values')
        return values
    total=block()
    magnetic=None
    while True:
        line=f.readline()
        if not line:break
        words=line.split()
        if len(words)==3 and all(re.match(r'^\d+$',x) for x in words):
            candidate=list(map(int,words))
            if candidate==grid:
                magnetic=block();break
    f.close()
    if magnetic is None:raise ValueError('Expected second spin-density block')
    return dict(header=head,cell=cell,species=species.split(),counts=counts,
                positions=positions,grid=grid,total=total,magnetic=magnetic)

def incar(path):
    result={}
    for line in open(path):
        line=line.split('#',1)[0].split('!',1)[0]
        if '=' in line:
            key,value=line.split('=',1)
            if key.strip().upper() not in ('SYSTEM','MAGMOM'):
                result[key.strip().upper()]=value.strip()
    return result

cases={}
protocol=None
for name,expected_nelect,expected_mag in [('AB',2.,0.),('A',1.,1.),('B',1.,-1.)]:
    out=open(name+'/OUTCAR').read()
    if out.count('aborting loop because EDIFF is reached')!=1 or out.count('General timing and accounting')!=1:
        raise ValueError(name+': missing converged SCF / normal end')
    if re.search(r'VERY BAD NEWS|BRMIX:|Error EDD|ZHEGV failed',out,re.I):
        raise ValueError(name+': solver error')
    if 'Your FFT grids' in out:
        raise ValueError(name+': VASP reports an insufficient FFT grid')
    nelect=float(re.findall(r'NELECT\s*=\s*([-\d.]+)',out)[-1])
    mag=float(re.findall(r'mag=\s*([-\d.Ee+]+)',open(name+'/OSZICAR').read())[-1])
    data=read_charge(name+'/CHGCAR');n=len(data['total'])
    total=math.fsum(data['total'])/n
    spin=math.fsum(data['magnetic'])/n
    if abs(total-nelect)>1e-5 or abs(nelect-expected_nelect)>1e-8:
        raise ValueError(name+': electron count mismatch')
    if abs(mag-expected_mag)>2e-4 or abs(spin-mag)>2e-4:
        raise ValueError(name+': unexpected spin state')
    tags=incar(name+'/INCAR')
    if protocol is None:protocol=tags
    elif tags!=protocol:raise ValueError('Different electronic protocols')
    data.update(nelect=nelect,integral_e=total,mag_OSZICAR_muB=mag,mag_grid_muB=spin)
    cases[name]=data

ab,a,b=[cases[name] for name in ('AB','A','B')]
if not (ab['grid']==a['grid']==b['grid']):raise ValueError('FFT grids differ')
if not (ab['cell']==a['cell']==b['cell']):raise ValueError('Cells differ')
if not (ab['species']==a['species']==b['species']==['H']):raise ValueError('Expected the H model')
if ab['counts']!=[2] or a['counts']!=[1] or b['counts']!=[1]:raise ValueError('Wrong atom counts')
for point,target in [(a['positions'][0],ab['positions'][0]),(b['positions'][0],ab['positions'][1])]:
    if max(abs(x-y) for x,y in zip(point,target))>1e-6:raise ValueError('A fragment moved')
hashes={}
pot_hash=[]
for name in ('AB','A','B'):
    for filename in ('POSCAR','INCAR','KPOINTS','OUTCAR','OSZICAR','CHGCAR','POTCAR'):
        value=digest(name+'/'+filename)
        if filename=='POTCAR':pot_hash.append(value)
        else:hashes[name+'/'+filename]=value
if len(set(pot_hash))!=1:raise ValueError('Different pseudopotentials')
if len(set(open(name+'/KPOINTS').read() for name in ('AB','A','B')))!=1:
    raise ValueError('Different k sampling')
vol=abs(det(ab['cell']));nx,ny,nz=ab['grid'];n=nx*ny*nz
if max(abs(ab['cell'][i][j]-(10. if i==j else 0.)) for i in range(3) for j in range(3))>1e-8:
    raise ValueError('Plot extraction is specific to the 10 Angstrom cubic cell')
delta=[x-y-z for x,y,z in zip(ab['total'],a['total'],b['total'])]
integral=math.fsum(delta)/n
if abs(integral)>1e-5:raise ValueError('Charge difference does not integrate to zero')
positive=math.fsum(x for x in delta if x>0)/n
negative=math.fsum(x for x in delta if x<0)/n
nxy=nx*ny
plane=[math.fsum(delta[k*nxy:(k+1)*nxy])/nxy/vol for k in range(nz)]
linear=[100.*x for x in plane]
dz=10./nz
cumulative=[0.]
for k in range(1,nz+1):
    cumulative.append(cumulative[-1]+.5*(linear[k-1]+linear[k%nz])*dz)
with open('delta-planar.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['z_A','delta_n_e_A3','delta_N_e_A','cumulative_e'])
    for k in range(nz+1):
        writer.writerow(['%.10f'%(k*dz),'%.12e'%plane[k%nz],
                         '%.12e'%linear[k%nz],'%.12e'%cumulative[k]])
j=ny//2
with open('delta-y5.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['x_A','z_A','delta_n_e_A3'])
    for k in range(nz):
        for i in range(nx):
            writer.writerow(['%.10f'%(10.*i/nx),'%.10f'%(10.*k/nz),
                             '%.12e'%(delta[(k*ny+j)*nx+i]/vol)])
with open('CHGDIFF.vasp','w') as handle:
    handle.writelines(ab['header']);handle.write('\n%d %d %d\n'%(nx,ny,nz))
    for k in range(0,n,5):handle.write(' '.join('%.11E'%x for x in delta[k:k+5])+'\n')
# A Gaussian cube uses bohr and electrons/bohr^3; its z index runs fastest.
with open('delta-charge.cube','w') as handle:
    handle.write('H2 minus frozen spin-polarized H fragments\n')
    handle.write('Signed electron-number density in electrons/bohr^3\n')
    handle.write('%5d %13.8f %13.8f %13.8f\n'%(2,0.,0.,0.))
    for count,vector in zip((nx,ny,nz),ab['cell']):
        handle.write('%5d %13.8f %13.8f %13.8f\n'%tuple([count]+[v/count/BOHR for v in vector]))
    for position in ab['positions']:
        handle.write('%5d %13.8f %13.8f %13.8f %13.8f\n'%tuple([1,1.]+[v/BOHR for v in position]))
    line=[]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                line.append('%.10E'%(delta[(k*ny+j)*nx+i]/vol*BOHR**3))
                if len(line)==6:handle.write(' '.join(line)+'\n');line=[]
    if line:handle.write(' '.join(line)+'\n')
summary={'grid':ab['grid'],'volume_A3':vol,'positions_A':ab['positions'],
         'delta_integral_e':integral,'positive_integral_e':positive,'negative_integral_e':negative,
         'minimum_delta_n_e_A3':min(delta)/vol,'maximum_delta_n_e_A3':max(delta)/vol,
         'cumulative_endpoint_e':cumulative[-1],'potcar_sha256':pot_hash[0],
         'definition':'total-charge first block: AB - A - B; density = stored_value / cell_volume',
         'sha256':hashes,'cases':{}}
for name in ('AB','A','B'):
    summary['cases'][name]={key:cases[name][key] for key in
        ('nelect','integral_e','mag_OSZICAR_muB','mag_grid_muB')}
with open('charge-difference-summary.json','w') as handle:json.dump(summary,handle,indent=2,sort_keys=True)
for name in ('AB','A','B'):
    row=summary['cases'][name]
    print('%s NELECT=%.1f integral=%.10f e mag(OSZICAR)=%.4f mag(grid)=%.10f'%
          (name,row['nelect'],row['integral_e'],row['mag_OSZICAR_muB'],row['mag_grid_muB']))
print('grid = %d %d %d; points = %d; volume = %.6f A^3'%(nx,ny,nz,n,vol))
print('integral_delta = %.12e e; accumulated = %.10f e; depleted = %.10f e'%(integral,positive,negative))
print('delta_n range = %.10f to %.10f e/A^3'%(min(delta)/vol,max(delta)/vol))
print('cumulative endpoint = %.12e e'%cumulative[-1])
print('Wrote CHGDIFF.vasp, delta-charge.cube, delta-planar.csv, delta-y5.csv, charge-difference-summary.json')
```

</details>

```console
[bcgong@localhost grid144]$ python -B analyze_charge.py | tee analysis.out
AB NELECT=2.0 integral=2.0000000029 e mag(OSZICAR)=-0.0000 mag(grid)=-0.0000000000
A NELECT=1.0 integral=1.0000000012 e mag(OSZICAR)=1.0000 mag(grid)=1.0000000012
B NELECT=1.0 integral=1.0000000012 e mag(OSZICAR)=-1.0000 mag(grid)=-1.0000000012
grid = 144 144 144; points = 2985984; volume = 1000.000000 A^3
integral_delta = 4.362638146422e-10 e; accumulated = 0.2578313944 e; depleted = -0.2578313940 e
delta_n range = -0.0555594237 to 0.8029641058 e/A^3
cumulative endpoint = 4.362638192728e-10 e
Wrote CHGDIFF.vasp, delta-charge.cube, delta-planar.csv, delta-y5.csv, charge-difference-summary.json
[bcgong@localhost grid144]$
```

AB 的总密度积分为 2.0000000029 e，A、B 各为 1.0000000012 e。第二块积分与 OSZICAR 的最终磁矩相符：分子约为 0，两个冻结原子分别约为 +1、−1 μB。后面的差分使用三份文件的第一块，并没有把磁化密度当成总电子数密度。

差分的全胞积分为 4.36×10⁻¹⁰ e，与零相符；正值区域积累 0.2578313944 e，负值区域耗尽 0.2578313940 e，二者相抵。这个数是相对于指定冻结参考的空间重排量。H₂ 两个相同原子具有对称性，它不能被解读为“0.258 e 从 A 转移到了 B”。

## 从密度数组到 VESTA：先转换，再设等值面

前面的 `analyze_charge.py` 已核对自洽结果、电子数与自旋参考态。下面的 `build_delta_chgcar.py` 用同一组三份密度重新生成只有一个标量块的 `CHGCAR_DELTA`，沿用 AB 的结构头和 VASP 存储约定，供配套 VESTA 场景读取。若直接查看下载包中的网格与场景，可从下一小节打开文件。下载[本次完整 VESTA 文件、场景与脚本](/Atlas/examples/charge-vesta-files.tar.gz)，解包进入 `charge-vesta`；原始三份 `CHGCAR.gz` 沿用页首链接。

下面是可交给 AI 编程助手的完整需求说明。它根据本例已经完成的转换整理，便于复现同一种处理：

```text
编写 Python 3 命令行程序 build_delta_chgcar.py，依赖 NumPy。输入 --ab、--a、--b 是 VASP CHGCAR 或 gzip 压缩 CHGCAR.gz；解析 POSCAR 风格结构头，支持元素/原子数、Direct/Cartesian 坐标以及可选 Selective dynamics。读取结构后的第一块 nx ny nz 总电子密度，恰好 N=nx*ny*nz 个有限值，x 最快；不混入 augmentation 或第二块磁化密度。检查三项晶胞矩阵相同、网格相同、AB 原子数等于 A+B，A/B 元素与坐标保持 AB 中原位。D 是体积缩放的 VASP 存储值，n=D/V，单位 e/Å³；逐点计算 D_AB-D_A-D_B，输出仅用于 VESTA 的单块 CHGCAR_DELTA，保留 AB 结构头。分别计算各输入 ΣD/N、差分全胞/正值/负值积分、极值及源文件 SHA256，写 JSON。若本例差分全胞残差大于 1e-6 e 则报错；打印科学计数法残差，不能把舍入成零称作精确证明。所有目标文件写入前检查存在性，拒绝覆盖。命令参数为 --output 与 --summary。不得归一化到期望电子数或画替代图。GUI 使用 VESTA 打开输出并核对单位：±0.03 e/Å³ 等于 ±30 的原始存储值；本次 VESTA 场景将其转换为 ±0.00444555 e/bohr³。保存场景，导出实际等值面 PNG；记录配色、阈值与显示范围。
```

[完整源码：build_delta_chgcar.py](/Atlas/examples/charge-vesta/scripts/build_delta_chgcar.py)。环境为 Python 3、NumPy；安装依赖后在新输出目录执行：

<details>
<summary>build_delta_chgcar.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Build a VESTA-readable VASP volumetric file for Δρ = ρ(AB) − ρ(A) − ρ(B).

Inputs are CHGCAR files (plain text or gzip-compressed).  The script reads only
VASP's first total-charge grid block; magnetization and PAW augmentation blocks
are not part of the plotted scalar field.  The output keeps VASP's stored
volume-scaled values, so divide a grid value by cell volume (Å³) to get e/Å³.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import Iterable, TextIO

import numpy as np

_INTEGER = re.compile(r"^[+-]?\d+$")


def _open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="ascii", errors="strict")
    return path.open("rt", encoding="ascii", errors="strict")


def _line(stream: TextIO, label: str) -> str:
    value = stream.readline()
    if not value:
        raise ValueError(f"Unexpected end of file while reading {label}")
    return value


def _ints(tokens: list[str]) -> bool:
    return bool(tokens) and all(_INTEGER.fullmatch(token) for token in tokens)


def _float(token: str) -> float:
    return float(token.replace("D", "E").replace("d", "e"))


def _float_values(stream: TextIO) -> Iterable[float]:
    for line in stream:
        for token in line.split():
            yield _float(token)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_uncompressed(path: Path) -> str:
    opener = gzip.open if path.suffix.lower() == ".gz" else open
    digest = hashlib.sha256()
    with opener(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_chgcar(path: Path) -> dict:
    """Parse cell/atoms, one 3-D total-charge block, and its exact VASP header."""
    header: list[str] = []
    with _open_text(path) as stream:
        title = _line(stream, "title")
        header.append(title)
        scale_tokens = _line(stream, "scale factor").split()
        header.append(" ".join(scale_tokens) + "\n")
        if not scale_tokens:
            raise ValueError(f"{path}: missing scale factor")
        scale = _float(scale_tokens[0])

        raw_cell = []
        for axis in "abc":
            row = _line(stream, f"lattice vector {axis}")
            header.append(row)
            values = [_float(token) for token in row.split()[:3]]
            if len(values) != 3:
                raise ValueError(f"{path}: invalid lattice vector {axis}")
            raw_cell.append(values)
        raw_cell = np.asarray(raw_cell, dtype=np.float64)
        raw_volume = abs(float(np.linalg.det(raw_cell)))
        if raw_volume <= 0 or scale == 0:
            raise ValueError(f"{path}: invalid cell volume or scale factor")
        factor = scale if scale > 0 else (abs(scale) / raw_volume) ** (1.0 / 3.0)
        cell = raw_cell * factor

        species_or_counts = _line(stream, "species/count line")
        header.append(species_or_counts)
        fields = species_or_counts.split()
        if _ints(fields):
            counts = [int(token) for token in fields]
            species = [f"X{i + 1}" for i in range(len(counts))]
        else:
            species = fields
            count_line = _line(stream, "atom counts")
            header.append(count_line)
            count_fields = count_line.split()
            if not _ints(count_fields):
                raise ValueError(f"{path}: atom-count line is not integer-valued")
            counts = [int(token) for token in count_fields]
        if len(species) != len(counts) or any(count <= 0 for count in counts):
            raise ValueError(f"{path}: invalid species/count list")
        atom_species = [symbol for symbol, count in zip(species, counts) for _ in range(count)]

        coordinate_line = _line(stream, "coordinate mode or selective-dynamics line")
        header.append(coordinate_line)
        if coordinate_line.strip().lower().startswith("s"):
            coordinate_line = _line(stream, "coordinate mode")
            header.append(coordinate_line)
        mode = coordinate_line.strip().lower()
        if not mode or mode[0] not in {"d", "c", "k"}:
            raise ValueError(f"{path}: unknown coordinate mode {coordinate_line!r}")

        fractional_or_cartesian = []
        for atom_index in range(len(atom_species)):
            atom_line = _line(stream, f"atom coordinate {atom_index + 1}")
            header.append(atom_line)
            xyz = [_float(token) for token in atom_line.split()[:3]]
            if len(xyz) != 3:
                raise ValueError(f"{path}: invalid coordinate for atom {atom_index + 1}")
            fractional_or_cartesian.append(xyz)
        coordinates = np.asarray(fractional_or_cartesian, dtype=np.float64)
        cartesian = coordinates @ cell if mode[0] == "d" else coordinates * factor

        dimensions = None
        for _ in range(40):
            candidate = _line(stream, "grid dimensions")
            header.append(candidate)
            fields = candidate.split()
            if _ints(fields) and len(fields) == 3 and all(int(value) > 0 for value in fields):
                dimensions = tuple(int(value) for value in fields)
                break
        if dimensions is None:
            raise ValueError(f"{path}: no 3-D grid dimensions after the structure header")

        npoints = math.prod(dimensions)
        values = np.fromiter(itertools.islice(_float_values(stream), npoints),
                             dtype=np.float64, count=npoints)
        if values.size != npoints:
            raise ValueError(f"{path}: expected {npoints} charge values, read {values.size}")

    return {
        "path": path,
        "header": header,
        "cell": cell,
        "volume_A3": abs(float(np.linalg.det(cell))),
        "species": atom_species,
        "cartesian_A": cartesian,
        "dimensions": dimensions,
        "values": values,
        "sha256_gz_or_file": _sha256_file(path),
        "sha256_uncompressed": _sha256_uncompressed(path),
    }


def check_same_cell_and_grid(data: dict[str, dict]) -> None:
    reference = data["AB"]
    for label in ("A", "B"):
        item = data[label]
        if item["dimensions"] != reference["dimensions"]:
            raise ValueError(f"{label} grid {item['dimensions']} != AB grid {reference['dimensions']}")
        if not np.allclose(item["cell"], reference["cell"], rtol=0.0, atol=1e-8):
            raise ValueError(f"{label} cell vectors differ from AB")
    if len(reference["species"]) != len(data["A"]["species"]) + len(data["B"]["species"]):
        raise ValueError("AB atom count must equal A plus B")

    # Verify that A and B retain the corresponding AB atomic coordinates.
    remaining = list(range(len(reference["species"])))
    for label in ("A", "B"):
        item = data[label]
        for symbol, xyz in zip(item["species"], item["cartesian_A"]):
            matches = [i for i in remaining
                       if reference["species"][i] == symbol
                       and np.allclose(reference["cartesian_A"][i], xyz, rtol=0.0, atol=1e-6)]
            if not matches:
                raise ValueError(f"{label} atom {symbol} at {xyz} Å is not an AB atom at that position")
            remaining.remove(matches[0])
    if remaining:
        raise ValueError(f"A/B references did not account for AB atom indices {remaining}")


def write_grid(path: Path, header: list[str], values: np.ndarray) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}; choose another output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    out_header = list(header)
    out_header[0] = "H2 delta density rho_AB-rho_A-rho_B; VASP volume-scaled grid values\n"
    with path.open("wt", encoding="ascii", newline="\n") as stream:
        stream.writelines(out_header)
        for start in range(0, values.size, 5):
            chunk = values[start:start + 5]
            stream.write(" ".join(f"{value: .11E}" for value in chunk) + "\n")


def build(ab: Path, a: Path, b: Path, output: Path, summary: Path) -> dict:
    for path in (output, summary):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}; choose a new output path")
    if output.resolve() == summary.resolve():
        raise ValueError("Output and summary must have different paths")
    data = {"AB": read_chgcar(ab), "A": read_chgcar(a), "B": read_chgcar(b)}
    check_same_cell_and_grid(data)
    npoints = math.prod(data["AB"]["dimensions"])
    volume = data["AB"]["volume_A3"]
    delta_stored = data["AB"]["values"] - data["A"]["values"] - data["B"]["values"]
    delta_rho = delta_stored / volume

    total_e = float(np.sum(delta_stored, dtype=np.float64) / npoints)
    positive_e = float(np.sum(np.maximum(delta_stored, 0.0), dtype=np.float64) / npoints)
    negative_e = float(np.sum(np.minimum(delta_stored, 0.0), dtype=np.float64) / npoints)
    if abs(total_e) > 1e-6:
        raise ValueError(f"Difference density does not conserve charge: integral={total_e:.9g} e")

    if not all(np.isfinite(item["values"]).all() for item in data.values()):
        raise ValueError("Input grid contains non-finite values")
    write_grid(output, data["AB"]["header"], delta_stored)
    record = {
        "source": {label: {"path": str(item["path"]),
                           "sha256_file": item["sha256_gz_or_file"],
                           "sha256_uncompressed": item["sha256_uncompressed"]}
                   for label, item in data.items()},
        "output": str(output),
        "formula": "rho_AB(r) - rho_A(r) - rho_B(r)",
        "grid": list(data["AB"]["dimensions"]),
        "volume_A3": volume,
        "points": npoints,
        "grid_value_convention": "VASP CHGCAR values are rho(r) * cell_volume; divide this output's grid values by volume_A3 to obtain e/Angstrom^3.",
        "minimum_delta_rho_e_A3": float(np.min(delta_rho)),
        "maximum_delta_rho_e_A3": float(np.max(delta_rho)),
        "delta_integral_e": total_e,
        "negative_integral_e": negative_e,
        "positive_integral_e": positive_e,
        "vesta_symmetric_threshold_grid_value": 30.0,
        "equivalent_threshold_e_A3": 30.0 / volume,
        "input_grid_integrals_e": {
            label: float(np.sum(item["values"], dtype=np.float64) / npoints)
            for label, item in data.items()
        },
        "output_sha256": _sha256_file(output),
    }
    summary.parent.mkdir(parents=True, exist_ok=True)
    if summary.exists():
        raise FileExistsError(f"Refusing to overwrite {summary}; choose another summary path")
    summary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ab", type=Path, required=True, help="AB CHGCAR or CHGCAR.gz")
    parser.add_argument("--a", type=Path, required=True, help="A CHGCAR or CHGCAR.gz")
    parser.add_argument("--b", type=Path, required=True, help="B CHGCAR or CHGCAR.gz")
    parser.add_argument("--output", type=Path, required=True, help="New VESTA-readable VASP volumetric file")
    parser.add_argument("--summary", type=Path, required=True, help="New JSON validation summary")
    args = parser.parse_args()
    result = build(args.ab, args.a, args.b, args.output, args.summary)
    print(f"grid: {result['grid'][0]} {result['grid'][1]} {result['grid'][2]}")
    print(f"volume: {result['volume_A3']:.6f} Å^3")
    print(f"integrals A/B/AB: {result['input_grid_integrals_e']['A']:.9f} / "
          f"{result['input_grid_integrals_e']['B']:.9f} / {result['input_grid_integrals_e']['AB']:.9f} e")
    print(f"delta integral: {result['delta_integral_e']:.3e} e")
    print(f"delta rho min/max: {result['minimum_delta_rho_e_A3']:.6f} / "
          f"{result['maximum_delta_rho_e_A3']:.6f} e/Å^3")
    print(f"±{result['equivalent_threshold_e_A3']:.3f} e/Å^3 maps to ±{result['vesta_symmetric_threshold_grid_value']:.1f} stored VASP grid values (VESTA display units must be checked)")
    print(f"wrote: {result['output']}")
    print(f"summary: {args.summary}")


if __name__ == "__main__":
    main()
```

</details>

```bash
python3 -m pip install numpy
python3 -B scripts/build_delta_chgcar.py --ab ../h2-delta-charge/AB/CHGCAR.gz --a ../h2-delta-charge/A/CHGCAR.gz --b ../h2-delta-charge/B/CHGCAR.gz --output new-h2/CHGCAR_DELTA --summary new-h2/summary.json
```

本次对真实密度执行同一转换得到的关键输出为：

```text
grid: 144 144 144
volume: 1000.000000 Å^3
integrals A/B/AB: 1.000000001 / 1.000000001 / 2.000000003 e
delta integral: 4.363e-10 e
delta rho min/max: -0.055559 / 0.802964 e/Å^3
```

完整未舍入统计在[summary.json](/Atlas/examples/charge-vesta/h2/summary.json)。差分积分残差为 4.3626382×10⁻¹⁰ e，正负积分分别为 +0.2578313944388549 和 −0.2578313940025911 e。它们在当前文件精度下相抵；显示成 `0.0000` 只是打印舍入。

### 打开网格，设置正负两套等值面

用 VESTA 的 **File → Open** 打开刚生成的 `new-h2/CHGCAR_DELTA`；若使用下载包中的结果，则打开 `h2/CHGCAR_DELTA`。先确认两颗 H 的位置与 10 Å 晶胞。打开 **Properties → Isosurfaces**，添加正、负密度两项，分别用金黄与蓝色。物理阈值为 ±0.03 e/Å³；本次界面转换后保存的数值是 ±0.00444555 e/bohr³（1 bohr=0.529177210903 Å），不能把 30 当成这个界面的密度阈值。下载的 `h2/h2-isosurfaces.vesta` 已记录阈值与颜色；打开后仍应核对导入文件。

把显示范围收至分数坐标 0.3–0.7，沿 a 方向观察，c 轴竖直、b 轴水平；通过 **File → Export Raster Image** 导出 PNG。下图为 VESTA 导出的等值面。

<figure><img src="/Atlas/examples/delta-charge/h2_delta_3d_zoom.png" alt="H2 差分电子密度的真实 VESTA 正负等值面，金黄为积累，蓝色为耗尽" loading="lazy"/><figcaption>固定 H–H=0.74 Å 的 H₂：金黄为 Δn=+0.03 e/Å³，蓝色为 Δn=−0.03 e/Å³，浅色球为 H。金黄区域连接两原子，蓝色区域分布在分子轴两端。阈值下的空间形貌表示相对于冻结原子参考的密度重排。</figcaption></figure>

## 平面显示的范围：核对正负区域轮廓

随后切换到红蓝平面显示并再次导出。配套 `h2/h2-planar-view.vesta` 保存了当时的显示设置；此场景没有记录可复核的切面坐标，所以这张图用来辅助辨认轮廓，不用它读取某一位置的连续密度值。

<figure><img src="/Atlas/examples/delta-charge/h2_delta_slice.png" alt="同一 H2 数据在 VESTA 中导出的红蓝平面显示，红色为积累区域，蓝色为耗尽区域" loading="lazy"/><figcaption>同一密度数据的平面显示：红色对应积累，蓝色对应耗尽。图中未附连续色标与切面坐标，判读限于正负区域的轮廓；定量检查使用前面的完整网格积分。</figcaption></figure>

两幅图都显示键区积累与分子轴两端耗尽；由于两颗 H 相同且冻结参考对称，全胞差分近零不能推出 A→B 的定向转移。对于异质结构，仍需保留片段的原位置、电荷与自旋参考态。

## 参照文献，确定图要回答的问题

Shang 等在 Si–N 功能化 h-BN 的 Fig. 1(d,e) 中并列展示差分密度与 ELF，分别读密度增减和局域化空间分布。[Phys. Rev. B 113, 094504 (2026)](https://doi.org/10.1103/jmys-zkgs)。该图的差分密度阈值与单位未在图注给出；本例阈值由自己的密度数据选择。文献里的材料结论不用于解释这里的 H₂。

下一步：若要给空间区域分配净电子数，可接 [Bader 分析](/Atlas/m/bader/vasp/)；若要看电子局域特征，可接 [ELF](/Atlas/m/elf/vasp/)。这两种量与 Δn 的定义不同，需要各自读取对应的输出。

```text
固定 AB 几何 → 原位保留 A、B → 匹配参数的三份 SCF
                                  ↓
                        CHGCAR 结构、网格、电子数
                                  ↓
                       第一密度块 AB − A − B
                                  ↓
                    VESTA 正负等值面 + 完整网格积分
```
