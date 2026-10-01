## 用已有 SnSe₂/Sr₂N 密度，求均匀网格电子态

六原子 SnSe₂/Sr₂N 异质薄层先在均匀网格上做 SCF 并保存密度，再用 `ICHARG=11` 求固定密度的本征态与 DOS。问题是给定构型在这一模型下的态密度分布，取样与能量轴均从真实输出读取。

父子记录都使用 18×18×1 网格；本例展示固定密度文件接续，没有做加密网格实验。记录由 bcgong 上 VASP 5.4.4 于 2025 年 6 月 3 日执行，下面按存档文件读取结果。固定背景下仍需解本征值问题，见 [QE 方法论文附录 A.2 式 (A.8)](https://doi.org/10.1088/0953-8984/21/39/395502)；VASP 密度读取和 PAW 一中心信息规则见 [ICHARG](https://vasp.at/wiki/ICHARG)。

[下载父 SCF、固定密度分支与后处理](/Atlas/examples/vasp/snse2-sr2n-nscf-files.tar.gz)。解包得到 `snse2-sr2n-nscf`，含 `scf`、`dos` 和脚本。父 CHGCAR 只保存一份；POTCAR 正文未包含。OUTCAR 开头 PAW 细节回显已移除，计算参数与迭代、数值、结束段保留；运行运行脚本保留原记录中的环境与程序路径。

## 先读父结构与自洽输入

实际元素 Sn、Se、N、Sr，计数 1、2、1、2，组成 SnSe₂ 与 Sr₂N。原 `SYSTEM=SnS2` 是遗留标题，计算元素由 POSCAR 与 PAW 决定。本页保留原文件，不据标题误认材料。完整父 POSCAR：


```text
11                                      
   1.00000000000000     
     3.9501156207146009    0.0000000001522404   -0.0000000000000000
    -1.9750578097205296    3.4209004743098745    0.0000000000000000
    -0.0000000000000001    0.0000000000000002   39.4021877938467284
   Sn   Se   N    Sr
     1     2     1     2
Direct
  0.0000000000000000  0.0000000000000000  0.5940212009837095
  0.6666666670000012  0.3333333329999988  0.6325735570448590
  0.3333333329999988  0.6666666670000012  0.5481899174149424
  0.6666666670000012  0.3333333329999988  0.4539734079959168
  0.0000000000000000 -0.0000000000000000  0.4934254572360981
  0.3333333329999988  0.6666666670000012  0.4248064611244732
```

第三矢量 39.40218779 Å 包含薄层和真空，面内长度约 3.95012 Å。子 POSCAR 与父逐字节一致。

### 完整父 INCAR

保留全部注释。井号开头的 SOC、DFT+U、NELECT、NEDOS、NSW 等行没有生效；不能把它们当实际参数。`LREAL=A` 是自动实空间投影，原注释误写 reciprocal space，以标签值为准。


```text
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
   ENCUT = 520 eV
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
```

父 `ISTART=0`，没有生效的 ICHARG 行，实际默认 ICHARG=2，从原子密度开始自洽。`LCHARG=T` 保存父密度，`LWAVE=F` 不写波函数。实际 ISPIN=1、无 SOC、NELECT=51。PAW 元数据：


```json
{
  "ZVAL": [
    14.0,
    6.0,
    5.0,
    10.0
  ],
  "TITEL": [
    "PAW_PBE Sn_d 06Sep2000",
    "PAW_PBE Se 06Sep2000",
    "PAW_PBE N 08Apr2002",
    "PAW_PBE Sr_sv 07Sep2000"
  ]
}
```

14+2×6+5+2×10=51。父子 POTCAR 已在原主机逐字节比较一致；公开包仅记录 TITEL/ZVAL，复算从授权库准备相同数据。

完整父 KPOINTS：


```text
K-Spacing Value to Generate K-Mesh: 0.020
0
Gamma
  18  18   1
0.0  0.0  0.0
```

父运行脚本实际使用 32 个 MPI 进程，安装路径脱敏：


```bash
#!/bin/bash

#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

#unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 32  /data/software/vasp.5.4.4/bin/vasp_std > out
```

父 OUTCAR 有 EDIFF 达到与 timing 段，`out` 结束段如下：


```text
DAV:  19    -0.261383705181E+02    0.53513E-03   -0.21138E-03  2992   0.233E-01    0.138E-01
DAV:  20    -0.261382733019E+02    0.97216E-04   -0.97801E-04  3024   0.143E-01    0.874E-02
DAV:  21    -0.261383055850E+02   -0.32283E-04   -0.15680E-04  3632   0.561E-02    0.675E-02
DAV:  22    -0.261382429473E+02    0.62638E-04   -0.26199E-04  2928   0.577E-02    0.295E-02
DAV:  23    -0.261382457820E+02   -0.28347E-05   -0.37380E-05  3256   0.302E-02    0.211E-02
DAV:  24    -0.261382474571E+02   -0.16751E-05   -0.10138E-05  2944   0.185E-02    0.114E-02
DAV:  25    -0.261382458930E+02    0.15641E-05   -0.10307E-05  2944   0.131E-02    0.580E-03
DAV:  26    -0.261382462108E+02   -0.31776E-06   -0.17047E-06  2312   0.630E-03
   1 F= -.27075118E+02 E0= -.27073536E+02  d E =-.316316E-02
```

## 将密度带到独立分支

父密度须与结构、PAW、泛函、自旋模型对应。原位核验父子 CHGCAR 的 SHA256 都为：

```text
a5ce4be5ffd31a68f0b5a96ee3f9d9b330f171a9366bc9d5bf52694d93e4f9ec
```

需要复算时，另建目录保存新输入；包内 dos 保留原结果：

```bash
cd snse2-sr2n-nscf
mkdir dos-rerun
cp dos/{INCAR,POSCAR,KPOINTS,script_std} dos-rerun/
cp scf/CHGCAR dos-rerun/
cd dos-rerun
# 准备与父相同的 POTCAR，使用 vi 按本机安装位置编辑 script_std
```

实际子 INCAR 完整内容：


```text
SYSTEM = SnS2

########## about parallelation ###########
   LPLANE =.TRUE.
   NPAR = 4
   NSIM = 4
##########################################

############### about I/O ################
#  ISTART =      0    job   : 0-new  1-cont  2-samecut
   ICHARG =      11    charge: 1-file 2-atom 10+ const
##########################################

########### about switch control ##########
   LWAVE = F                 whether write WAVECAR
   LCHARG = F                whether write CHGCAR and CHG
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
   ENCUT = 520 eV
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
```

子分支设置 ICHARG=11、关闭 LCHARG；密度不更新，本征值求解仍需收敛。IBRION=-1、实际 NSW=0 固定几何。ENCUT、展宽、IVDW、LREAL、LMAXMIX 等保持一致。LMAXMIX=4 保留 d 通道的一中心密度信息，CHGCAR 存在不能替代兼容性核验。

子 KPOINTS 完整内容与父相同：


```text
K-Spacing Value to Generate K-Mesh: 0.020
0
Gamma
  18  18   1
0.0  0.0  0.0
```

原始子分支脚本实际使用 4 个 MPI 进程：


```bash
#!/bin/bash

#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

#unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 4  /data/software/vasp.5.4.4/bin/vasp_std > out
```

原 `out` 最后几轮：


```text
DAV:   4    -0.259318183595E+02   -0.33615E+01   -0.33382E+01  3160   0.262E+01
DAV:   5    -0.261345829638E+02   -0.20276E+00   -0.20258E+00  4376   0.522E+00
DAV:   6    -0.261380585204E+02   -0.34756E-02   -0.34751E-02  3544   0.708E-01
DAV:   7    -0.261382382185E+02   -0.17970E-03   -0.17969E-03  3904   0.122E-01
DAV:   8    -0.261382483521E+02   -0.10134E-04   -0.10133E-04  3256   0.271E-02
DAV:   9    -0.261382490733E+02   -0.72118E-06   -0.72085E-06  2520   0.705E-03
   1 F= -.27075121E+02 E0= -.27073546E+02  d E =-.314903E-02
```

最后 dE=−7.2118×10⁻⁷ eV、d eps=−7.2085×10⁻⁷ eV，满足 1e-6 eV；OUTCAR 确有 EDIFF 达到和 timing。只看到 DOS 文件不足以判定求解完成。

| 实际字段 | 父 SCF | 固定密度分支 |
| --- | --- | --- |
| ICHARG | 2 | 11 |
| 完整网格 | 18×18×1 | 18×18×1 |
| 不可约 NKPTS | 37 | 37 |
| NBANDS | 32 | 32 |
| NELECT | 51 | 51 |
| ISPIN | 1 | 1 |
| ENCUT / eV | 520 | 520 |
| ISMEAR、SIGMA / eV | 0、0.05 | 0、0.05 |
| 密度 | 自洽更新 | 固定父密度 |

## 从 DOSCAR 读取真实能量轴

[官方 DOSCAR 说明](https://vasp.at/wiki/DOSCAR)给出头部与 ISPIN=1 的总 DOS 三列：E、DOS、积分 DOS。这里单位为 states/eV/整个六原子晶胞，不能直接标成每原子。文件之后还有投影块，下面只提取首个总 DOS 块。

头部 NEDOS=301、EF=−1.49081474 eV，范围约 −38.37991605 至 4.59266727 eV。相对能量用本次 E−EF，不用其他分支的费米能。

从前面的复算准备目录返回下载包中的存档目录，再运行后处理：

```bash
cd ..
python3 analyze_nscf.py
```

若只读取存档，直接在解包后的 `snse2-sr2n-nscf` 目录运行。程序使用 Python 标准库，得到以下输出：


```text
ICHARG: parent=2 child=11; counts: NELECT=51 NKPTS=37 NBANDS=32
NEDOS=301; EF=-1.49081474 eV; mean_DOS_spacing=0.14324333 eV
nearest_EF_sample: E-EF=0.06781474 eV; DOS=2.5730 states/eV/cell
same_POSCAR=True same_KPOINTS=True parent_EDIFF=True child_EDIFF=True
```

平均能量间隔约 0.14324 eV。离 EF 最近一行在 E−EF=0.06781474 eV，DOS=2.5730 states/eV/cell；它不是 EF 处的精确插值。高斯展宽与有限能量/k 网格共同影响曲线，不能从单个零值或粗采样谷底提取精确带隙。表用于读取本次态分布，更精细的带边或定量 DOS 要用实际网格对照。

[总 DOS CSV](/Atlas/examples/vasp/snse2-sr2n-nscf/results/total-dos.csv)、[摘要](/Atlas/examples/vasp/snse2-sr2n-nscf/results/summary.json)、[DOSCAR](/Atlas/examples/vasp/snse2-sr2n-nscf/dos/DOSCAR)和 EIGENVAL 随包保留。沿高对称路径的能带需要另建 Line-Mode 分支；本页不可约点是均匀网格采样。

如果让 AI 帮忙整理这一步，可以把要读取的文件、提取规则和输出单位一起交代：

> 读取 scf 和 dos 两个目录的 OUTCAR、POSCAR、KPOINTS，以及父 CHGCAR 和子 DOSCAR、EIGENVAL。核对 ICHARG=2 与 11、有效参数、结构和电子/能带/k 点数量；计算父 CHGCAR 的 SHA-256。针对实际 ISPIN=1 的 DOSCAR，仅提取第一个总 DOS 块，保留 E、E−EF、states/eV/整胞的 DOS 和积分 DOS，输出 CSV 与 JSON。给出离 EF 最近一行的能量偏移，不能把它写成精确的 DOS(EF)。用 Python 标准库，检查块长度、列数与有限数值。

<details><summary>完整后处理源码 analyze_nscf.py</summary>


```python
"""Extract the existing uniform-grid, non-spin-polarized VASP DOS."""
from pathlib import Path
import csv, hashlib, json, math, re

def main():
    root = Path(__file__).resolve().parent
    parent = root / 'scf'
    child = root / 'dos'
    texts = [(p / 'OUTCAR').read_text() for p in (parent, child)]

    def number(t, key):
        return float(re.search('\\b' + key + '\\s*=\\s*([-+0-9.]+)', t).group(1))

    def digest(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()
    fields = ['ENCUT', 'ISPIN', 'ISMEAR', 'SIGMA', 'NELECT', 'NBANDS', 'NKPTS', 'LMAXMIX', 'IVDW']
    ps = {k: number(texts[0], k) for k in fields}
    cs = {k: number(texts[1], k) for k in fields}
    if ps != cs:
        raise ValueError('Parent/child effective parameters differ.')
    if (parent / 'POSCAR').read_bytes() != (child / 'POSCAR').read_bytes():
        raise ValueError('Parent and child structure differs.')
    if int(cs['ISPIN']) != 1:
        raise ValueError('This parser expects the actual ISPIN=1 case.')
    ls = (child / 'DOSCAR').read_text().splitlines()
    head = list(map(float, ls[5].split()))
    n = int(head[2])
    ef = head[3]
    rows = [list(map(float, s.split())) for s in ls[6:6 + n]]
    if len(rows) != n or any((len(x) != 3 or not all((math.isfinite(v) for v in x)) for x in rows)):
        raise ValueError('Unexpected total DOS block.')
    el = (child / 'EIGENVAL').read_text().splitlines()
    ne, nk, nb = map(int, el[5].split())
    if (ne, nk, nb) != (int(cs['NELECT']), int(cs['NKPTS']), int(cs['NBANDS'])):
        raise ValueError('EIGENVAL counts disagree.')
    out = root / 'results'
    out.mkdir(exist_ok=True)
    with (out / 'total-dos.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['energy_eV', 'energy_minus_EF_eV', 'DOS_states_per_eV_cell', 'integrated_states_per_cell'])
        for energy, dos, integ in rows:
            w.writerow([energy, energy - ef, dos, integ])
    idx = min(range(n), key=lambda i: abs(rows[i][0] - ef))
    summary = dict(version=texts[1].splitlines()[0].strip(), parent_parameters=ps, child_parameters=cs, parent_ICHARG=number(texts[0], 'ICHARG'), child_ICHARG=number(texts[1], 'ICHARG'), parent_EDIFF_reached='aborting loop because EDIFF is reached' in texts[0], child_EDIFF_reached='aborting loop because EDIFF is reached' in texts[1], parent_timing_footer='General timing and accounting' in texts[0], child_timing_footer='General timing and accounting' in texts[1], parent_CHGCAR_sha256=digest(parent / 'CHGCAR'), same_POSCAR=True, same_KPOINTS=(parent / 'KPOINTS').read_bytes() == (child / 'KPOINTS').read_bytes(), NEDOS=n, fermi_energy_eV=ef, energy_min_eV=head[1], energy_max_eV=head[0], mean_DOS_energy_spacing_eV=(rows[-1][0] - rows[0][0]) / (n - 1), nearest_EF_sample=dict(energy_eV=rows[idx][0], energy_minus_EF_eV=rows[idx][0] - ef, DOS_states_per_eV_cell=rows[idx][1], integrated_states_per_cell=rows[idx][2]), EIGENVAL_counts=dict(NELECT=ne, NKPTS=nk, NBANDS=nb))
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('ICHARG: parent={} child={}; counts: NELECT={} NKPTS={} NBANDS={}'.format(int(summary['parent_ICHARG']), int(summary['child_ICHARG']), ne, nk, nb))
    print('NEDOS={}; EF={:.8f} eV; mean_DOS_spacing={:.8f} eV'.format(n, ef, summary['mean_DOS_energy_spacing_eV']))
    print('nearest_EF_sample: E-EF={:.8f} eV; DOS={:.4f} states/eV/cell'.format(rows[idx][0] - ef, rows[idx][1]))
    print('same_POSCAR={} same_KPOINTS={} parent_EDIFF={} child_EDIFF={}'.format(summary['same_POSCAR'], summary['same_KPOINTS'], summary['parent_EDIFF_reached'], summary['child_EDIFF_reached']))
if __name__ == '__main__':
    main()
```

</details>
