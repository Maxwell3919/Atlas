在事先选定的自旋模型中，两份磁构型能量可以确定一个有效交换参数。这个参数是否能描述其他构型，需要另外检验。本页沿用两原子 bcc Fe 的 FM、AFM 结果，先枚举周期最近邻键，再用四原子超胞检查计数、能量归一化和最终磁矩。磁矩发生塌缩的构型不能直接套入固定自旋长度的映射。

[下载原始计算目录、周期键表与分析脚本](/Atlas/examples/interface-magnet-exchange-j/example-pack.tar.gz)。本页使用固定 a=2.8 Å、PBE、ENCUT=400 eV 的同一套输入协议。已有两原子计算的准备和结果见 [磁性候选态](/Atlas/m/magnetic-gs/vasp/)，SCF 文件读法见 [SCF](/Atlas/m/scf/vasp/)。

## 定义自旋模型并数清周期键

先写清本例采用的模型约定：

```text
E(N, C) = N * epsilon_ref - J * C
C = sum over unique periodic nearest-neighbor bonds (e_i dot e_j)
|e_i| = 1
```

每条周期键只数一次，共线方向用 +1 或 −1 表示。这里 e_i 是单位方向，不把 MAGMOM 初值 3 μB 直接当成自旋量子数，也不额外乘一个未定义的 S²。按这个符号约定，J>0 的最近邻项偏好平行排列。

所用两原子常规胞里的 Fe 分别在角点和体心。每个 Fe 有 8 个最近邻；为了确认周期边界没有漏算，脚本从 POSCAR 的分数坐标出发，遍历相邻平移单元，找出距离 √3 a/2 的原子对，并把 (i,j,R) 与反向的 (j,i,−R) 合并。

```text
[bcgong@localhost fe_exchange_j]$ python enumerate_bonds.py
fm2: N=2; neighbors/site=[8, 8]; unique bonds=8; correlation sum=+8
afm2: N=2; neighbors/site=[8, 8]; unique bonds=8; correlation sum=-8
fm4: N=4; neighbors/site=[8, 8, 8, 8]; unique bonds=16; correlation sum=+16
neel4: N=4; neighbors/site=[8, 8, 8, 8]; unique bonds=16; correlation sum=-16
stripe4: N=4; neighbors/site=[8, 8, 8, 8]; unique bonds=16; correlation sum=+0
nearest-neighbor distance = 2.4248711306 A
```

两原子常规胞共有 8 条独立最近邻键，FM 的 C=+8，AFM 的 C=−8。四原子超胞中有 16 条键，下面三个初始模式的 C 分别为 +16、−16、0。最后一个模式特意选为相关和为零，模型会对它给出一个独立的能量预测。

读两原子胞的实际键表：

```text
[bcgong@localhost fe_exchange_j]$ cat bonds-2fe.csv
atom_i,atom_j,shift_x,shift_y,shift_z,distance_A
1,2,-1,-1,-1,2.424871130596428
1,2,-1,-1,0,2.424871130596428
1,2,-1,0,-1,2.424871130596428
1,2,-1,0,0,2.424871130596428
1,2,0,-1,-1,2.424871130596428
1,2,0,-1,0,2.424871130596428
1,2,0,0,-1,2.424871130596428
1,2,0,0,0,2.424871130596428
```

这八行虽然都是原子 1 与原子 2，却对应不同的周期平移。只对文件里两个原子做一次最小镜像距离，会把它们合成一对，从而把交换参数的分母数错。每行距离均约 2.4248711306 Å，与 √3×2.8/2 一致。

两原子模型给出 E_FM = 2 ε_ref − 8J，E_AFM = 2 ε_ref + 8J，所以 J=(E_AFM−E_FM)/16。这里统一使用 OUTCAR 的 `energy(sigma->0)`：

```text
[bcgong@localhost fe_exchange_j]$ grep 'energy  without entropy' fm2/OUTCAR afm2/OUTCAR
fm2/OUTCAR:  energy  without entropy=      -16.47400754  energy(sigma->0) =      -16.47377314
afm2/OUTCAR:  energy  without entropy=      -15.60874618  energy(sigma->0) =      -15.60782301
```

两份 E0 分别为 −16.47377314 和 −15.60782301 eV/晶胞，差值为 0.86595013 eV。代入后 J_eff≈0.0541218831 eV/键，即 54.1218831 meV/键；参考能 ε_ref≈−8.0203990375 eV/原子。

这两个方程恰好决定 ε_ref 和 J 两个未知数，所以能把两份输入能量回代到零误差。独立磁构型则用来检验这个模型的预测。

## 在四原子超胞中检查磁态与归一化

将常规胞沿 x 加倍，准备 `fm4`、`neel4`、`stripe4` 三个目录。坐标对应先前同一 bcc 几何：

```text
[bcgong@localhost fm4]$ cat POSCAR
Fe bcc 2x1x1 conventional supercell
1.0
5.6 0.0 0.0
0.0 2.8 0.0
0.0 0.0 2.8
Fe
4
Direct
0.0 0.0 0.0
0.25 0.5 0.5
0.5 0.0 0.0
0.75 0.5 0.5
```

第一晶格长度加倍，原来的两原子结构平移一次，得到四个 Fe。编号依次为 x=0、1.4、2.8、4.2 Å 上的四个位置，y/z 交替为 0 或 1.4 Å。

空间长度加倍后，沿该方向将 k 网格减半，保持倒空间采样密度：

```text
[bcgong@localhost fm4]$ cat KPOINTS
Fe bcc 2x1x1, folded 12x12x12 grid
0
Gamma
6 12 12
0 0 0
```

原来的 12×12×12 Γ 网格变成 6×12×12，另外两方向不变。能量比较还要按原子数归一化，不能把四原子总能量直接减去两原子总能量当作磁性差值。

```text
[bcgong@localhost stripe4]$ cat INCAR
SYSTEM = Fe bcc stripe4
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
MAGMOM = 3 3 -3 -3
LORBIT = 11
LREAL = .FALSE.
LASPH = .TRUE.
NCORE = 2
NSW = 0
IBRION = -1
LWAVE = .FALSE.
LCHARG = .FALSE.
```

三个目录中只有 SYSTEM 和 MAGMOM 不同：FM 为 `3 3 3 3`，Néel 为 `3 -3 3 -3`，层状初态为 `3 3 -3 -3`。后者两个相邻位置朝上、接下来两个朝下，周期最近邻键中平行与反平行的数量相同。

`NSW = 0`、`IBRION = -1` 让三个目录保持同一原子几何，比较时不会混入各磁态分别弛豫的结构能。这里没有施加磁矩约束，MAGMOM 给出初始方向和幅值，并参与对称性判定；`LORBIT = 11` 负责输出 PAW 局域投影，不能把磁矩固定在输入值。因此结束后要读 OUTCAR，确认局域磁矩的幅值和逐原子符号仍对应所设模式。[MAGMOM](https://vasp.at/wiki/MAGMOM) · [LORBIT](https://vasp.at/wiki/LORBIT)

```text
[bcgong@localhost stripe4]$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-j-stripe4
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
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

三个任务均使用 8 个 MPI 进程，5 分钟限时，按 FM → Néel → 层状初态串行提交。脚本中的 CPU 编号只对这次已核验的节点分配成立；运行中实际亲和性为 16–23。

```text
[bcgong@localhost fm4]$ sbatch run.slurm
Submitted batch job 18195
[bcgong@localhost neel4]$ sbatch run.slurm
Submitted batch job 18196
[bcgong@localhost stripe4]$ sbatch run.slurm
Submitted batch job 18197
```

每个任务结束后才提交下一个。运行中使用 `squeue -j <作业号>` 与 `tail -f out` 查看队列和电子步；结束后核对正常计时及 EDIFF。

```text
[bcgong@localhost fe_exchange_j]$ grep -E 'aborting loop|Elapsed time' fm4/OUTCAR neel4/OUTCAR stripe4/OUTCAR
fm4/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
fm4/OUTCAR:                         Elapsed time (sec):       28.153
neel4/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
neel4/OUTCAR:                         Elapsed time (sec):       27.999
stripe4/OUTCAR:------------------------ aborting loop because EDIFF is reached ----------------------------------------
stripe4/OUTCAR:                         Elapsed time (sec):       77.122
```

三份输出都达到电子停止条件，耗时约 28.2、28.0、77.1 秒。前两个四原子结果保留了所设磁序：FM 的四个局域磁矩都约为 +2.098 μB，Néel 为交替的 ±1.317 μB。

第三份输出值得停下来细读：

```text
[bcgong@localhost stripe4]$ tail -6 OSZICAR
DAV:  47    -0.309815012114E+02   -0.44728E-05   -0.74169E-06 15788   0.346E-02    0.178E-02
DAV:  48    -0.309815019516E+02   -0.74024E-06   -0.10363E-06 14636   0.139E-02    0.208E-02
DAV:  49    -0.309815023000E+02   -0.34836E-06   -0.34283E-07 14588   0.765E-03    0.225E-02
DAV:  50    -0.309815021736E+02    0.12643E-06   -0.97524E-08 10060   0.420E-03    0.237E-02
DAV:  51    -0.309815021669E+02    0.66534E-08   -0.31759E-08  5596   0.226E-03
   1 F= -.30981502E+02 E0= -.30981573E+02  d E =0.212707E-03  mag=     0.0000
```

```text
[bcgong@localhost stripe4]$ grep -A 10 'magnetization (x)' OUTCAR | tail -11
 magnetization (x)
 
# of ion       s       p       d       tot
------------------------------------------
    1       -0.000   0.000  -0.007  -0.007
    2        0.000  -0.000   0.007   0.007
    3        0.000  -0.000   0.007   0.007
    4       -0.000   0.000  -0.007  -0.007
--------------------------------------------------
tot          0.000  -0.000  -0.000  -0.000
```

虽然电子循环结束，四个局域磁矩只剩约 −0.007、+0.007、+0.007、−0.007 μB，既远小于 FM/AFM 的磁矩，也没有保持所指定的逐原子初始符号。总磁矩为零不能说明目标反铁磁态保留了；这里的局域幅值已衰减到接近零。

磁矩检查脚本因此拒绝把这份输出当作固定单位向量的第三磁态：

```text
[bcgong@localhost fe_exchange_j]$ python fit_exchange.py
Traceback (most recent call last):
  File "fit_exchange.py", line 42, in <module>
    bonds=json.load(open('bonds-summary.json'));names=['fm2','afm2','fm4','neel4','stripe4'];rows=[read_case(n) for n in names]
  File "fit_exchange.py", line 38, in read_case
    if enforce_moment and min(abs(x) for x in moment)<.1:raise ValueError('Local moment collapsed; direction mapping invalid')
ValueError: Local moment collapsed; direction mapping invalid
```

脚本中的 0.1 μB 是用于拦截本例明显磁矩衰减的检查阈值，不是通用的磁性物理界限。实际读数约 0.007 μB，比两份参考磁态小两个数量级。继续把这个能量按初始 `++--` 模式算预测残差，会把未获得的磁态当成已获得。

接下来用原来的 FM2/AFM2 两态求 J，并用 FM4/Néel4 检查晶胞折叠。stripe4 已达到电子停止条件，但所需磁构型没有保持，因此只记录它的能量和局域磁矩，不给它分配初始模式的关联和或预测残差。若某个目录连 EDIFF 都未达到，读取函数会直接报错，它的末步能量也不能进入拟合：

```text
[bcgong@localhost fe_exchange_j]$ python fit_two_states.py
J_eff = 54.12188312 meV per unique NN bond; Eref = -8.0203990375 eV/atom
fm2   N=2 C= +8 E0=-16.47377314 predicted=-16.47377314 eV/cell residual=+0.000000 meV/atom; moments=[2.098, 2.098]
afm2  N=2 C= -8 E0=-15.60782301 predicted=-15.60782301 eV/cell residual=-0.000000 meV/atom; moments=[1.317, -1.317]
fm4   N=4 C=+16 E0=-32.94760653 predicted=-32.94754628 eV/cell residual=-0.015063 meV/atom; moments=[2.098, 2.098, 2.098, 2.098]
neel4 N=4 C=-16 E0=-31.21566841 predicted=-31.21564602 eV/cell residual=-0.005598 meV/atom; moments=[1.317, -1.317, 1.317, -1.317]
stripe4: EXCLUDED from fit/model residual; E0=-30.98157307 eV/cell; local moments=[-0.007, 0.007, 0.007, -0.007]
The intended third magnetic state was not obtained. The nearest-neighbor model has not passed independent validation.
```

FM4 和 Néel4 相对两原子拟合式的回代误差分别约 −0.0151、−0.0056 meV/原子。它们说明在这里的精度下，超胞计数、能量归一化和匹配 k 密度得到了较好的数值复现。这两个对照代表的仍是原来的两种磁序，不能代替独立第三磁序的检验。

因此 J_eff=54.1219 meV/键表示指定两态与最近邻键定义下的有效参数。FM 与 AFM 的 PAW 局域磁矩幅值分别约为 2.098 和 1.317 μB，已经发生明显变化。虽然上面的模型把方向归一化为单位向量，这个数学约定并没有使 DFT 中的磁矩长度固定。因此，两态能量差给出的 J_eff 还包含随磁构型发生的电子态响应；要把它用于其他磁序，需要更多实际保持的独立磁构型来检查，也需判断是否要加入更远邻等作用项。

若要继续建立可转用的自旋模型，需要获取更多实际保持的磁构型，或采用合适的约束/响应方法，再用足够独立的数据区分不同作用项。

## 状态与模型核对表

| 状态 | 用途 | 原子数 | 关联和 | E0（eV/胞） | 回代残差（meV/原子） | 局域磁矩（μB） |
| --- | --- | --- | --- | --- | --- | --- |
| fm2 | fit | 2 | 8 | -16.47377314 | 0.00000000 | 2.098;2.098 |
| afm2 | fit | 2 | -8 | -15.60782301 | -0.00000000 | 1.317;-1.317 |
| fm4 | folding check | 4 | 16 | -32.94760653 | -0.01506250 | 2.098;2.098;2.098;2.098 |
| neel4 | folding check | 4 | -16 | -31.21566841 | -0.00559750 | 1.317;-1.317;1.317;-1.317 |
| stripe4 | rejected target | 4 |  | -30.98157307 |  | -0.007;0.007;0.007;-0.007 |

J_eff=54.12188312 meV/唯一最近邻键，Eref=−8.0203990375 eV/原子；stripe4 的空白关联与残差表示它被排除，不能按初始模式计算预测残差。

## 对照文献中的分析方法

Rezaei 等，*Benchmarking first-principles approaches for extracting magnetic exchange interactions*，[DOI: 10.1038/s41524-026-02161-3](https://doi.org/10.1038/s41524-026-02161-3)，Fig. 3 比较交换参数随磁构型数变化的结果，并区分全部与展宽/熵筛选后的构型集合。正文讨论金属构型选择和配置数对能量映射的影响。本例的 FM4/Néel4 检查的是晶胞折叠，stripe4 磁矩塌缩后被排除；因此 J_eff 是指定两态和最近邻键定义下的有效参数。

```text
同协议的真实磁构型能量
  └─ 明确 H、单位方向和每条键的计数
       └─ 周期键枚举 → 两态反算 → 回代
             ├─ 匹配 k 密度的超胞对照
             └─ 独立第三磁态：先验收磁矩与模式，再谈模型预测
```

## 从原始文件重建结果

周期键表给出关联和，最终局域磁矩决定某份能量能否按指定模式进入映射。两态拟合和四原子折叠对照分别输出；塌缩的 stripe4 保留实际读数。可以把这些读取规则写成下面的请求：

```text
请编写 Python 3 独立后处理程序。先从真实 POSCAR 枚举周期唯一最近邻键并输出键表，注明单位向量模型 H=NEref-J*sum(e_i·e_j)。读取 fm2/afm2/fm4/neel4/stripe4 的 INCAR、POSCAR、KPOINTS、POTCAR.identity.txt 与 OUTCAR，检查输入协议、网格密度、电子收敛、计时和最终局域磁矩；两态拟合 J，四原子同序仅作折叠对照，塌缩的 stripe4 排除关联和残差。输出能量、原子数、键关联和、局域矩及残差 CSV，先写 bonds-summary.json，再写 exchange-summary.json，另用导出脚本生成两份 CSV。拟合态若缺少收敛/计时记录、局域磁矩绝对值低于本例检查阈值 0.1 μB、逐原子符号改变，或输入协议不匹配，就报错退出。stripe4 以关闭幅值检查的方式单独读取，作为已排除的诊断记录；不由单个 J 生成温度或 Tc 数据。
```

[fit_two_states.py 完整源码](/Atlas/examples/interface-magnet-exchange-j/fit_two_states.py) · [export_exchange_table.py 完整源码](/Atlas/examples/interface-magnet-exchange-j/export_exchange_table.py) · [enumerate_bonds.py 完整源码](/Atlas/examples/interface-magnet-exchange-j/enumerate_bonds.py) · [fit_exchange.py 完整源码](/Atlas/examples/interface-magnet-exchange-j/fit_exchange.py)

<details>
<summary>fit_two_states.py 的完整源码</summary>

```python
from __future__ import print_function
import json,math
from fit_exchange import read_case,file_sha,sampling_length

bonds=json.load(open('bonds-summary.json'))
names=['fm2','afm2','fm4','neel4'];rows=[read_case(n) for n in names]
if len(set(file_sha(n+'/POTCAR') for n in names))!=1:raise ValueError('Different PAW')
protocol=[dict((k,v) for k,v in r['active_incar'].items() if k not in ['SYSTEM','MAGMOM']) for r in rows]
if any(p!=protocol[0] for p in protocol):raise ValueError('Protocol mismatch')
for group in [['fm2','afm2'],['fm4','neel4']]:
 for file in ['POSCAR','KPOINTS']:
  if len(set(file_sha(n+'/'+file) for n in group))!=1:raise ValueError('Different '+file)
ks=sampling_length('fm2')
if any(max(abs(x-y) for x,y in zip(sampling_length(n),ks))>1e-9 for n in names):raise ValueError('Different reciprocal mesh density')
for r in rows:
 want=bonds['states'][r['state']]['spin_directions']
 if r['final_spin_signs']!=want and r['final_spin_signs']!=[-x for x in want]:raise ValueError('Final signs changed')
cf=bonds['states']['fm2']['correlation_sum'];ca=bonds['states']['afm2']['correlation_sum']
j=(rows[1]['E0_eV_cell']-rows[0]['E0_eV_cell'])/(cf-ca)
ere=(rows[0]['E0_eV_cell']+j*cf)/rows[0]['n_atoms']
for r in rows:
 corr=bonds['states'][r['state']]['correlation_sum'];pred=ere*r['n_atoms']-j*corr
 r['predicted_E0_eV_cell']=pred;r['correlation_sum']=corr;r['residual_meV_atom']=1000*(r['E0_eV_cell']-pred)/r['n_atoms']
# Read the rejected trial only for diagnosis; it is excluded from fitting and residual validation.
rejected=read_case('stripe4',enforce_moment=False)
rejected['requested_initial_signs']=bonds['states']['stripe4']['spin_directions']
rejected['accepted_as_target_state']=False
rejected['reason']='local moments fall to about 0.007 muB and requested site pattern is not retained'
report={'definition':bonds['definition'],'J_effective_meV_per_bond':j*1000,'Eref_eV_atom':ere,'fit_states':['fm2','afm2'],'folding_checks':['fm4','neel4'],'rows':rows,'rejected_trial':rejected,'independent_third_state_validation':'not passed; the intended third magnetic state was not obtained','scope':'two-state effective parameter; no unique material J or validated nearest-neighbor model claimed'}
json.dump(report,open('exchange-summary.json','w'),indent=2)
print('J_eff = %.8f meV per unique NN bond; Eref = %.10f eV/atom'%(j*1000,ere))
for r in rows:print('%-5s N=%d C=%+3d E0=% .8f predicted=% .8f eV/cell residual=%+.6f meV/atom; moments=%s'%(r['state'],r['n_atoms'],r['correlation_sum'],r['E0_eV_cell'],r['predicted_E0_eV_cell'],r['residual_meV_atom'],r['local_moment_muB']))
print('stripe4: EXCLUDED from fit/model residual; E0=%.8f eV/cell; local moments=%s'%(rejected['E0_eV_cell'],rejected['local_moment_muB']))
print('The intended third magnetic state was not obtained. The nearest-neighbor model has not passed independent validation.')
```

</details>

<details>
<summary>export_exchange_table.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Export model-fit states and the rejected stripe trial without implying Tc."""
import csv, json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / "exchange-summary.json").read_text(encoding="utf-8"))
roles = {"fm2": "fit", "afm2": "fit", "fm4": "folding check", "neel4": "folding check"}
rows = []
for row in summary["rows"]:
    rows.append({
        "state": row["state"], "role": roles[row["state"]], "atoms": row["n_atoms"],
        "correlation_sum": row["correlation_sum"], "E0_eV_cell": f'{row["E0_eV_cell"]:.8f}',
        "model_E0_eV_cell": f'{row["predicted_E0_eV_cell"]:.8f}',
        "residual_meV_atom": f'{row["residual_meV_atom"]:.8f}',
        "local_moments_muB": ";".join(f"{m:.3f}" for m in row["local_moment_muB"]),
        "interpretation": "two-state fit" if row["state"] in ("fm2", "afm2") else "supercell folding check",
    })
trial = summary["rejected_trial"]
rows.append({
    "state": trial["state"], "role": "rejected target",
    "atoms": trial["n_atoms"], "correlation_sum": "",
    "E0_eV_cell": f'{trial["E0_eV_cell"]:.8f}', "model_E0_eV_cell": "",
    "residual_meV_atom": "", "local_moments_muB": ";".join(f"{m:.3f}" for m in trial["local_moment_muB"]),
    "interpretation": "moment collapsed; not an independent validation state",
})
with (root / "exchange-state-model-checks.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["state", "role", "atoms", "correlation_sum", "E0_eV_cell", "model_E0_eV_cell", "residual_meV_atom", "local_moments_muB", "interpretation"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
with (root / "exchange-fit-summary.csv").open("w", newline="", encoding="utf-8") as handle:
    fields = ["J_eff_meV_per_unique_NN_bond", "Eref_eV_atom", "fit_states", "independent_third_state_validation", "scope"]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerow({
        "J_eff_meV_per_unique_NN_bond": f'{summary["J_effective_meV_per_bond"]:.8f}',
        "Eref_eV_atom": f'{summary["Eref_eV_atom"]:.10f}',
        "fit_states": ";".join(summary["fit_states"]),
        "independent_third_state_validation": summary["independent_third_state_validation"],
        "scope": summary["scope"],
    })
print("Wrote 5 model-state rows and one fit-summary row; no finite-temperature result is inferred")
```

</details>

<details>
<summary>enumerate_bonds.py 的完整源码</summary>

```python
from __future__ import print_function
import itertools,math,json,csv

def read_poscar(name):
    s=open(name).readlines();scale=float(s[1]);cell=[[float(v)*scale for v in l.split()[:3]] for l in s[2:5]]
    n=sum(map(int,s[6].split()))
    if not s[7].lower().startswith('d'):raise ValueError('Direct coordinates required')
    f=[list(map(float,l.split()[:3])) for l in s[8:8+n]]
    return cell,f

def enumerate_cell(name,label):
    cell,f=read_poscar(name);n=len(f);a=math.sqrt(sum(x*x for x in cell[1]));distance=math.sqrt(3)*a/2
    bonds=set();coordination=[0]*n
    for i,j in itertools.product(range(n),repeat=2):
        for t in itertools.product([-1,0,1],repeat=3):
            delta=[sum((f[j][k]+t[k]-f[i][k])*cell[k][d] for k in range(3)) for d in range(3)]
            r=math.sqrt(sum(v*v for v in delta))
            if abs(r-distance)<1e-9:
                coordination[i]+=1
                forward=(i,j)+t;reverse=(j,i)+tuple(-v for v in t)
                bonds.add(min(forward,reverse))
    if any(z!=8 for z in coordination):raise ValueError('bcc nearest-neighbor coordination is not eight')
    bonds=sorted(bonds)
    with open('bonds-'+label+'.csv','w') as out:
        w=csv.writer(out);w.writerow(['atom_i','atom_j','shift_x','shift_y','shift_z','distance_A'])
        for row in bonds:w.writerow([row[0]+1,row[1]+1]+list(row[2:])+[distance])
    return {'n_atoms':n,'neighbor_distance_A':distance,'coordination':coordination,'n_unique_bonds':len(bonds),'bonds':[list(t) for t in bonds]}

if __name__=='__main__':
    cells={'2fe':enumerate_cell('fm2/POSCAR','2fe'),'4fe':enumerate_cell('fm4/POSCAR','4fe')}
    states=[('fm2','2fe',[1,1]),('afm2','2fe',[1,-1]),('fm4','4fe',[1,1,1,1]),('neel4','4fe',[1,-1,1,-1]),('stripe4','4fe',[1,1,-1,-1])]
    report={'definition':'H = Eref - J * sum_unique_periodic_NN_bonds(e_i dot e_j); unit vectors; each bond counted once','cells':cells,'states':{}}
    for name,label,spin in states:
        corr=sum(spin[b[0]]*spin[b[1]] for b in cells[label]['bonds'])
        report['states'][name]={'cell':label,'spin_directions':spin,'correlation_sum':corr}
        print('%s: N=%d; neighbors/site=%s; unique bonds=%d; correlation sum=%+d'%(name,cells[label]['n_atoms'],cells[label]['coordination'],cells[label]['n_unique_bonds'],corr))
    json.dump(report,open('bonds-summary.json','w'),indent=2)
    print('nearest-neighbor distance = %.10f A'%cells['2fe']['neighbor_distance_A'])
```

</details>

<details>
<summary>fit_exchange.py 的完整源码</summary>

```python
from __future__ import print_function
import re,json,math,os,hashlib

def active(path):
    d={}
    for line in open(path):
        line=line.split('#')[0].split('!')[0]
        if '=' in line:
            k,v=line.split('=',1);d[k.strip()]=v.strip()
    return d

def file_sha(name):
    if os.path.basename(name)=='POTCAR' and not os.path.exists(name):
        values=re.findall(r'[0-9a-f]{64}',open(os.path.join(os.path.dirname(name),'POTCAR.identity.txt')).read())
        if len(values)!=1:raise ValueError('Expected one recorded PAW hash')
        return values[0]
    return hashlib.sha256(open(name,'rb').read()).hexdigest()

def sampling_length(name):
    pos=open(name+'/POSCAR').readlines();scale=float(pos[1])
    lengths=[math.sqrt(sum(float(x)**2 for x in l.split()[:3]))*scale for l in pos[2:5]]
    nk=list(map(int,open(name+'/KPOINTS').readlines()[3].split()))
    return [x*y for x,y in zip(lengths,nk)]

def read_case(name,enforce_moment=True):
    p=active(name+'/INCAR');out=open(name+'/OUTCAR').read()
    if 'aborting loop because EDIFF is reached' not in out or 'General timing and accounting' not in out:raise ValueError('Unfinished '+name)
    if p.get('ISPIN')!='2':raise ValueError('Expected collinear spin polarization')
    n=sum(map(int,open(name+'/POSCAR').readlines()[6].split()))
    block=out.split('magnetization (x)')[-1]
    moment=[]
    for line in block.splitlines():
        fields=line.split()
        if len(fields)==5 and fields[0].isdigit():moment.append(float(fields[-1]))
        if len(moment)==n:break
    if len(moment)!=n:raise ValueError('Missing local magnetic moments')
    signs=[1 if x>0 else -1 for x in moment]
    if enforce_moment and min(abs(x) for x in moment)<.1:raise ValueError('Local moment collapsed; direction mapping invalid')
    return {'state':name,'n_atoms':n,'E0_eV_cell':float(re.findall(r'energy\(sigma->0\)\s*=\s*([-+0-9.Ee]+)',out)[-1]),'F_eV_cell':float(re.findall(r'free\s+energy\s+TOTEN\s*=\s*([-+0-9.Ee]+)',out)[-1]),'local_moment_muB':moment,'final_spin_signs':signs,'elapsed_s':float(re.findall(r'Elapsed time \(sec\):\s*([0-9.]+)',out)[-1]),'active_incar':p,'OUTCAR_sha256':hashlib.sha256(open(name+'/OUTCAR','rb').read()).hexdigest()}

if __name__=='__main__':
    bonds=json.load(open('bonds-summary.json'));names=['fm2','afm2','fm4','neel4','stripe4'];rows=[read_case(n) for n in names]
    if len(set(file_sha(n+'/POTCAR') for n in names))!=1:raise ValueError('PAW identity differs')
    for family in [['fm2','afm2'],['fm4','neel4','stripe4']]:
        if len(set(file_sha(n+'/POSCAR') for n in family))!=1:raise ValueError('Structure differs within cell family')
        if len(set(file_sha(n+'/KPOINTS') for n in family))!=1:raise ValueError('KPOINTS differ within cell family')
    density=sampling_length('fm2')
    if any(max(abs(x-y) for x,y in zip(sampling_length(n),density))>1e-9 for n in names):raise ValueError('Reciprocal sampling density differs')
    reference=dict((k,v) for k,v in rows[0]['active_incar'].items() if k not in ['SYSTEM','MAGMOM'])
    for r in rows:
        if dict((k,v) for k,v in r['active_incar'].items() if k not in ['SYSTEM','MAGMOM'])!=reference:raise ValueError('Protocol mismatch: '+r['state'])
        want=bonds['states'][r['state']]['spin_directions']
        if r['final_spin_signs']!=want and r['final_spin_signs']!=[-v for v in want]:raise ValueError('Final magnetic pattern changed')
    fm,afm=rows[:2];n2=fm['n_atoms'];cf=bonds['states']['fm2']['correlation_sum'];ca=bonds['states']['afm2']['correlation_sum']
    j=(afm['E0_eV_cell']-fm['E0_eV_cell'])/(cf-ca)
    ref=(fm['E0_eV_cell']+j*cf)/n2
    for r in rows:
        corr=bonds['states'][r['state']]['correlation_sum'];pred=ref*r['n_atoms']-j*corr
        r['correlation_sum']=corr;r['predicted_E0_eV_cell']=pred;r['residual_meV_atom']=1000*(r['E0_eV_cell']-pred)/r['n_atoms']
    report={'definition':bonds['definition'],'J_effective_meV_per_bond':j*1000,'Eref_eV_atom':ref,'fit_states':['fm2','afm2'],'validation_states':['fm4','neel4','stripe4'],'rows':rows,'scope':'two-state effective nearest-neighbor parameter; third-state residual tests transferability; local moment magnitudes are not constrained equal'}
    json.dump(report,open('exchange-summary.json','w'),indent=2)
    print('J_eff = %.8f meV per unique NN bond; Eref = %.10f eV/atom'%(j*1000,ref))
    for r in rows:
        print('%-7s N=%d C=%+3d E0=% .8f predicted=% .8f eV/cell residual=%+.6f meV/atom; moments=%s'%(r['state'],r['n_atoms'],r['correlation_sum'],r['E0_eV_cell'],r['predicted_E0_eV_cell'],r['residual_meV_atom'],r['local_moment_muB']))
```

</details>

[输入、原始输出与完整后处理包](/Atlas/examples/interface-magnet-exchange-j/example-pack.tar.gz)解压后，在 `example-pack` 目录执行：

```bash
python3 enumerate_bonds.py
python3 fit_two_states.py
python3 export_exchange_table.py
```

实际读取结果见正文表及 [exchange-state-model-checks.csv](/Atlas/examples/interface-magnet-exchange-j/exchange-state-model-checks.csv) · [exchange-fit-summary.csv](/Atlas/examples/interface-magnet-exchange-j/exchange-fit-summary.csv) · [exchange-summary.json](/Atlas/examples/interface-magnet-exchange-j/exchange-summary.json)。

相关输入说明：[VASP：从磁构型能量映射 Heisenberg 模型](https://vasp.at/tutorials/latest/magnetism/part2/) · [MAGMOM](https://vasp.at/wiki/MAGMOM) · [LORBIT](https://vasp.at/wiki/LORBIT)

下一步接 [磁性候选态](/Atlas/m/magnetic-gs/vasp/)，扩大能够稳定保持的磁构型集合。若关心同一磁序相对晶体方向的能量差，则接 [磁各向异性能量](/Atlas/m/mae/vasp/)，采用一致的 SOC 与方向协议。
