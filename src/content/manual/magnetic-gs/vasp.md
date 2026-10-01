界面或载流子变化会不会使原来采用的非自旋极化参考失效？如果能带出现自旋分裂，或同协议自旋极化计算形成稳定磁矩，就需要比较候选磁态的能量和最终磁化密度。[He 等关于空穴掺杂 H‑ZrCl₂ 的原文](https://doi.org/10.1039/D2TC00564F) Fig. 3 把总磁矩与自旋极化能并列，Fig. 4(a–c) 再用自旋分辨 PDOS 和自旋密度识别磁矩来源。这是判断载流子诱导磁性的一条材料证据链。

文献研究的是空穴掺杂单层。它不能证明电子供给型 ZrCl₂/Sc₂C 界面有同样的磁态，也不能把空穴浓度阈值移作界面 Bader 电荷的阈值。当前存档只有下面的 bcc Fe 操作样本，没有主体系同协议磁构型比较。Fe 用来说明 MAGMOM 初值、局域矩与统一能量定义之间的关系；它不提供异质结磁基态结果。

同一结构在不同初始磁排列下可能收敛到不同电子态。本例在固定 a=2.8 Å 的两原子 bcc Fe 晶胞中比较 FM、AFM 和非自旋极化候选，先从 OUTCAR 核对最终局域磁矩，再按统一 E0 排序。总磁矩为零既可能是局域矩抵消，也可能是无自旋极化的解，需要逐原子检查。

采用 MAGMOM 官方示例中的两原子 bcc 常规胞，元素选 Fe，固定晶格常数 2.8 Å。分别从平行、反平行和非自旋极化三个初始条件计算；三份结构、POTCAR、截断能、k 网格和展宽保持相同。这里只比较这个固定晶胞内的三个候选态。

普通输入与提交操作见 [VASP SCF](/Atlas/m/scf/vasp/)。

## 在同一晶胞中准备三种初态

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

`NSW = 0`、`IBRION = -1` 固定了原子位置，使这组三态比较都发生在 a=2.8 Å 的同一几何上。金属 Fe 使用 `ISMEAR = 1` 的 Methfessel–Paxton 展宽，`SIGMA = 0.1` 的单位是 eV。展宽帮助费米能附近的部分占据稳定迭代，也会影响三态能量差；后续检查网格与 SIGMA 时，要让三个目录一起采用新的设置，再比较相对能量是否稳定。[展宽与 k 点的关系](https://vasp.at/wiki/Smearing_technique)

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
这份脚本使用 8 个 MPI 进程。

脚本里的 16–23 是这次现场核验的空闲核编号。它解决的是本机 Intel MPI 从 `SLURM_CPUS_PER_TASK` 隐式推导 pin domain、导致默认绑核与现有任务重叠的问题；换节点时需重新核验分配与实际绑核，不能把这组编号作为通用参数。

```text
[bcgong@localhost fm]$ sbatch run.slurm
Submitted batch job 18184
```
## 读取最终磁矩，确认初态收敛成了什么

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
两个 Fe 的局域投影磁矩同为 2.098 μB，符号相同。这里没有开启 SOC，正负号表示共线自旋轴上的相对取向；表题中的 `(x)` 不表示已经确定了磁化沿晶体 x 方向。表中的投影和是 4.196 μB，与整个晶胞积分得到的 4.2127 μB 略有差别；原子投影区之外还有贡献，所以不要强迫这两种定义逐位相等。

另开 `afm` 目录，使用 `cp fm/POSCAR fm/INCAR fm/KPOINTS fm/POTCAR fm/run.slurm afm/` 复制输入。进入 `afm` 后用 `vi INCAR` 将 MAGMOM 改为 `3 -3`，其余物理参数保持一致。脚本仅改任务名。本次提交返回 18185，运行 13 秒结束。

MAGMOM 还参与对称性判定，所以 AFM 输入中的正负号也决定了哪些对称操作可以保留。以后从磁性 CHGCAR 或 WAVECAR 续算时，这一行仍用于确定对称性，不能因为已有磁化密度就随手删去。[MAGMOM 的续算说明](https://vasp.at/wiki/MAGMOM)

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
原始运行使用相同的 PAW 数据；公开包不含 POTCAR，脚本核对记录哈希与各 OUTCAR 的 TITEL，不能据此重新验证三份 POTCAR 的字节。POSCAR、KPOINTS 则逐文件比较 SHA-256；随后检查电子收敛、程序统计段和实际 ISPIN。表格同时保留有限展宽自由能 F 和 `energy(sigma->0)`；最后一列能量差统一选零展宽外推量，并除以每胞两个 Fe，换算成 meV/atom。

在这组固定设置下，FM 比所算 AFM 低约 432.98 meV/atom，比非自旋极化解低约 491.52 meV/atom。这个排序回答的是三份候选解之间的比较。要形成材料磁基态结论，还需检查更多可能的磁超胞、各磁态的几何优化、k 网格及展宽对相对能量的影响。

## 三候选态结果表

| state | E0_eV_cell | F_eV_cell | delta_E0_meV_atom_from_FM | cell_moment_muB |
| --- | --- | --- | --- | --- |
| fm | -16.47377314 | -16.47365594 | 0.000000 | 4.212700 |
| afm | -15.60782301 | -15.60736142 | 432.975065 | -0.000000 |
| nm | -15.49074150 | -15.49070763 | 491.515820 | 0.000000 |

## 比较的能量怎样回答磁性问题

He 等，*Formation of magnetic anionic electrons by hole doping*，[DOI: 10.1039/D2TC00564F](https://doi.org/10.1039/D2TC00564F)，Fig. 3（期刊第 7676 页）把 E_NM−E_FM 与总磁矩放在同一空穴浓度轴上；正的极化能表示所比 FM 解比非磁解低。Fig. 4（第 7677 页）用自旋分辨 PDOS 和空间自旋密度核对磁矩来源。本文的 Fe 能量差则定义为 (E_state−E_FM)/2，两种参考方向要读清。

如果需要检查界面磁性，应同时核对总磁矩、原子投影之外的磁化贡献以及自旋密度。在间隙态参与的材料里，原子局域投影不能覆盖全部磁矩。Fe 的 MAGMOM 初值只设置原子初始矩；它没有构造或验收间隙中心的磁化初态。随后仍要检验相关候选态是否在同一几何与协议下稳定存在。

## 从原始文件重建结果

前面的 OUTCAR 投影表用来辨认最终磁态；下面的脚本汇总 F、E0 和 OSZICAR 总磁矩，不提取局域投影。它核对结构、网格和 PAW 记录，以 FM 为参考计算能量差，每胞两个 Fe，除以 2 后换算为 meV/atom。脚本核对三态输入与实际输出的 ISPIN，并要求 FM/AFM 的最后摘要含有限磁矩；其他物理参数仍需按前面展示的输入逐项比较。对应的编程请求是：

```text
请编写 Python 3 后处理程序，在含 fm、afm、nm 的 example-pack 目录中运行。用 SHA256 比较三份 POSCAR、KPOINTS；公开包不含 POTCAR，用包根目录 POTCAR.identity.txt 的原始哈希及各 OUTCAR 的 TITEL 记录核对 PAW。要求 OUTCAR 有 EDIFF 收敛标记和最终计时段，读取最后的 F 和 energy(sigma->0)，核对各 INCAR 与 OUTCAR 的 ISPIN：fm/afm 必须为 2，nm 必须为 1。从 OSZICAR 最后一条 F 摘要取总磁矩；fm/afm 缺少 mag、字段无效或非有限值时必须失败，不能回退到早先摘要或零。只有 nm 已确认 ISPIN=1 时，才允许缺少 mag 并按零记录。以 fm 的 E0 为参考，差值除以两个 Fe，再乘 1000，输出 magnetic-energies.json；另写脚本导出三态 CSV。局域磁矩由正文中的 OUTCAR 投影表检查，不在这个汇总脚本中提取。
```

[magnetic_energies.py 完整源码](/Atlas/examples/interface-magnet-magnetic-gs/magnetic_energies.py) · [export_magnetic_table.py 完整源码](/Atlas/examples/interface-magnet-magnetic-gs/export_magnetic_table.py)

<details>
<summary>magnetic_energies.py 的完整源码</summary>

```python
from __future__ import print_function
import re,json,hashlib,os,math

def sha(p):
    if os.path.basename(p)=='POTCAR' and not os.path.exists(p):
        record=open('POTCAR.identity.txt').read()
        hashes=re.findall(r'[0-9a-f]{64}',record)
        if len(hashes)!=1:raise ValueError('Expected one recorded PAW hash')
        return hashes[0]
    return hashlib.sha256(open(p,'rb').read()).hexdigest()
rows=[]
for state in ['fm','afm','nm']:
    for name in ['POSCAR','KPOINTS','POTCAR']:
        if sha(state+'/'+name)!=sha('fm/'+name): raise ValueError('Different '+name)
    text=open(state+'/OUTCAR').read()
    reference=open('fm/OUTCAR').read()
    titles=re.findall(r'TITEL\s*=([^\n]+)',text)
    if titles!=re.findall(r'TITEL\s*=([^\n]+)',reference):raise ValueError('OUTCAR PAW identity differs')
    if 'aborting loop because EDIFF is reached' not in text or 'General timing and accounting' not in text: raise ValueError('Incomplete '+state)
    f=float(re.findall(r'free  energy\s+TOTEN\s*=\s*([-0-9.]+)',text)[-1])
    e0=float(re.findall(r'energy\(sigma->0\)\s*=\s*([-0-9.]+)',text)[-1])
    expected_spin=1 if state=='nm' else 2
    incar='\n'.join(re.split(r'[!#]',line,1)[0] for line in open(state+'/INCAR'))
    input_spin=re.findall(r'\bISPIN\s*=\s*(\d+)\b',incar,re.I)
    output_spin=re.findall(r'\bISPIN\s*=\s*(\d+)\b',text)
    if not input_spin or int(input_spin[-1])!=expected_spin or not output_spin or int(output_spin[-1])!=expected_spin:
        raise ValueError('Expected ISPIN='+str(expected_spin)+' in INCAR and OUTCAR for '+state)
    summaries=[line for line in open(state+'/OSZICAR') if re.search(r'\bF\s*=',line)]
    if not summaries:raise ValueError('Missing final OSZICAR summary for '+state)
    mag=re.search(r'\bmag\s*=\s*(\S+)',summaries[-1])
    if mag is None:
        if state!='nm':raise ValueError('Missing final mag for '+state)
        moment=0.0
    else:
        moment=float(mag[1])
        if not math.isfinite(moment):raise ValueError('Non-finite final mag for '+state)
    rows.append({'state':state,'F_eV_cell':f,'E0_eV_cell':e0,'mag_cell_muB':moment})
for row in rows:
    row['dE0_meV_atom']=(row['E0_eV_cell']-rows[0]['E0_eV_cell'])*1000/2
    print('%-3s F=% .8f eV  E0=% .8f eV  dE0=%9.4f meV/atom  M=%7.4f muB/cell'%(row['state'],row['F_eV_cell'],row['E0_eV_cell'],row['dE0_meV_atom'],row['mag_cell_muB']))
json.dump(rows,open('magnetic-energies.json','w'),indent=2)
```

</details>

<details>
<summary>export_magnetic_table.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Export the three-state Fe comparison as a compact CSV table."""
import csv, json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = json.loads((root / "magnetic-energies.json").read_text(encoding="utf-8"))
with (root / "magnetic-state-energy-table.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["state", "E0_eV_cell", "F_eV_cell", "delta_E0_meV_atom_from_FM", "cell_moment_muB"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "state": row["state"],
            "E0_eV_cell": f'{row["E0_eV_cell"]:.8f}',
            "F_eV_cell": f'{row["F_eV_cell"]:.8f}',
            "delta_E0_meV_atom_from_FM": f'{row["dE0_meV_atom"]:.6f}',
            "cell_moment_muB": f'{row["mag_cell_muB"]:.6f}',
        })
print(f"Wrote {len(rows)} rows to magnetic-state-energy-table.csv")
```

</details>

[输入、原始输出与完整后处理包](/Atlas/examples/interface-magnet-magnetic-gs/example-pack.tar.gz)解压后，在 `example-pack` 目录执行：

```bash
python3 magnetic_energies.py
python3 export_magnetic_table.py
```

实际读取结果见正文表及 [magnetic-state-energy-table.csv](/Atlas/examples/interface-magnet-magnetic-gs/magnetic-state-energy-table.csv) · [magnetic-energies.json](/Atlas/examples/interface-magnet-magnetic-gs/magnetic-energies.json)。

相关输入说明：[VASP：MAGMOM](https://vasp.at/wiki/MAGMOM) · [ISPIN](https://vasp.at/wiki/ISPIN) · [磁构型能量比较教程](https://vasp.at/tutorials/latest/magnetism/part2/) · [OUTCAR](https://vasp.at/wiki/OUTCAR)

若主体系出现需要解释的磁性证据，先结合[自旋分辨电子态](/Atlas/m/fatband/qe/)组织具体的磁化密度和候选态比较。是否进一步建立交换模型或比较磁化方向，由实际磁态和研究问题决定。
