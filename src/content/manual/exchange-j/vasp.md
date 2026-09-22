[VASP：从磁构型能量映射 Heisenberg 模型](https://vasp.at/tutorials/latest/magnetism/part2/) · [MAGMOM](https://vasp.at/wiki/MAGMOM) · [LORBIT](https://vasp.at/wiki/LORBIT)

两份磁构型能量可以解出一个有效交换参数，但是否能预测第三个磁构型，还需要实际检查。这里接着两原子 bcc Fe 的 FM、AFM 结果，先逐条枚举周期最近邻键，再用一个四原子超胞检验计数、能量归一化和磁态是否保留。

[下载原始计算目录、周期键表与分析脚本](/Atlas/examples/vasp/fe-exchange-j-files.tar.gz)。本页使用固定 a=2.8 Å、PBE、ENCUT=400 eV 的同一套输入协议。已有两原子计算的准备和结果见 [磁性候选态](/Atlas/m/magnetic-gs/vasp/)，SCF 文件读法见 [SCF](/Atlas/m/scf/vasp/)。

先写清本页采用的模型约定：

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

这两个方程恰好决定 ε_ref 和 J 两个未知数，所以能把两份输入能量回代到零误差。这一步只证明代数闭合，还不能证明最近邻模型适合 Fe。

为了增加一次实际检查，将常规胞沿 x 加倍，准备 `fm4`、`neel4`、`stripe4` 三个目录。坐标对应先前同一 bcc 几何：

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

三个任务均使用 8 个 MPI 进程，5 分钟限时，按 FM → Néel → 层状初态串行提交。脚本中的 CPU 编号只对这次已核验的节点分配成立；运行中实际亲和性为 16–23。原有声子任务占用另 16 核，总申请保持 24/64 核。

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

完整验收脚本因此拒绝把这份输出当作固定单位向量的第三磁态：

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

因此下面只拟合原来的两份磁态，并用 FM4/Néel4 检查晶胞折叠；第三份输出仅保留为诊断记录，明确排除在拟合和第三态残差验证之外：

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

第三个初态未通过磁态保持检查，所以这个最近邻模型尚未完成独立验证。J_eff=54.1219 meV/键只能作为本页明确定义的两态有效参数，不能称为唯一材料交换常数。FM 与 AFM 的 PAW 局域磁矩幅值本就从约 2.098 变为 1.317 μB，刚性局域磁矩假设已经需要审查；若存在更远邻、非 Heisenberg 项或其他电子重排，它们也会混入这两个总能量的差值。

若要继续建立可转用的自旋模型，需要获取更多实际保持的磁构型，或采用合适的约束/响应方法，再用足够独立的数据区分不同作用项。仅扩大线性方程求解器的输出小数位，不能补上这些信息。

在本机使用下载包中的真实数据重新生成表和图：

```bash
python3 enumerate_bonds.py
python3 fit_two_states.py
python3 plot_exchange.py
```

前两条命令只用 Python 标准库，绘图需要 NumPy 和 Matplotlib。`plot_exchange.py` 输出 `exchange-model-check.png` 与 PDF：左侧对比两个超胞对照的 DFT 与模型能量，并标出很小的折叠误差；右侧并列画出 FM、AFM 与第三初态收敛后的局域磁矩幅值。第三初态在图中明确标为未纳入模型验证。

![超胞回代对照与第三初态的局域磁矩变化](/Atlas/examples/vasp/fe-exchange-j/exchange-model-check.png)

下一步接 [磁性候选态](/Atlas/m/magnetic-gs/vasp/)，扩大能够稳定保持的磁构型集合。若关心同一磁序相对晶体方向的能量差，则接 [磁各向异性能量](/Atlas/m/mae/vasp/)，采用一致的 SOC 与方向协议。

```text
同协议的真实磁构型能量
  └─ 明确 H、单位方向和每条键的计数
       └─ 周期键枚举 → 两态反算 → 回代
             ├─ 匹配 k 密度的超胞对照
             └─ 独立第三磁态：先验收磁矩与模式，再谈模型预测
```
