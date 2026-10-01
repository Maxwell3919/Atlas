给平衡态 Al 原子初速度后，势能与动能会随运动相互转换。这里先读热浴如何改变温度，再从同一初态比较两种步长的 NVE 轨迹，检查积分误差。每个离子步都重新求电子基态并计算原子力，因此输出要按“离子步里包含电子自洽”的层次读取。

这里用实际运行的 8 原子周期 fcc Al 演示。它由 [晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax) 中的单原子原胞沿三个原胞基矢各重复两次得到，原始立方晶格常数为 3.95606780081 Å。保持晶胞不变，使用 QE 7.5、LDA-PZ、`Al.pz-vbc.UPF`、40/160 Ry 截断能和 4³ 超胞 k 网格。后者是本例的短轨迹设置，尚未证明力和统计量对电子采样收敛。

本次有三个完成的分支：100 步 SVR 恒温轨迹，以及两种步长覆盖相同时间的 NVE 轨迹。从这些输出提取逐步温度、总能量与坐标，比较同一初态下的时间步长误差；这段采样未覆盖长期热稳定、熔点或扩散过程。

完整输入、输出、逐步数据和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。在解包后的 `al` 目录运行文末的作图命令；重新进行 MD 时，按实际位置填写赝势库与 QE 可执行文件路径。

本例 SVR 热浴的依据是 [Bussi、Donadio 与 Parrinello 的随机速度缩放方法式 (7)](https://arxiv.org/html/0803.4060)，其中热浴时间尺度控制动能向目标分布的调整。该文第 II.3 节及 Fig. 1 区分热浴交换的能量和积分误差；下面用关闭温控器的 NVE 分支比较步长，对应其中的 Hamiltonian 运动部分。

## 先准备同一份位置和初速度

8 个原子的初速度来自固定种子 20260922 的正态分布，先减去质心速度，再按 21 个自由度归一化到 300 K。初速度和坐标都写进输入，因此两条 NVE 可以从同一个初态比较步长。最初的输入准备过程保存在 `prepare_aimd.py`，具体初速度记录在 `initial-velocities.json`。

下面是最终用于恒温轨迹的完整输入。`ATOMIC_POSITIONS crystal` 是超胞的分数坐标，`ATOMIC_VELOCITIES` 使用 QE 的原子单位，不是 Å/fs。

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ cat al.md.in
&CONTROL
 calculation = 'md'
 nstep = 100
 dt = 20
 iprint = 1
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'low'
/
&SYSTEM
 ibrav = 0
 nosym = .true.
 nat = 8
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 18
/
&ELECTRONS
 diagonalization = 'cg'
 diago_thr_init = 1.0d-9
 diago_full_acc = .true.
 diago_cg_maxiter = 200
 conv_thr = 1.0d-10
/
&IONS
 ion_dynamics = 'verlet'
 ion_velocities = 'from_input'
 ion_temperature = 'svr'
 tempw = 300
 nraise = 20
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
Al 0.50000000000000 0.00000000000000 0.00000000000000
Al 0.00000000000000 0.50000000000000 0.00000000000000
Al 0.50000000000000 0.50000000000000 0.00000000000000
Al 0.00000000000000 0.00000000000000 0.50000000000000
Al 0.50000000000000 0.00000000000000 0.50000000000000
Al 0.00000000000000 0.50000000000000 0.50000000000000
Al 0.50000000000000 0.50000000000000 0.50000000000000
CELL_PARAMETERS angstrom
-3.95606780081072 0.00000000000000 3.95606780081072
0.00000000000000 3.95606780081072 3.95606780081072
-3.95606780081072 3.95606780081072 0.00000000000000
K_POINTS automatic
4 4 4 0 0 0
ATOMIC_VELOCITIES
Al -2.96685438852231e-04 5.46443872130152e-04 3.52588534897630e-04
Al 1.83169591108944e-04 -2.23845342698565e-05 3.04783826563648e-04
Al -3.62394243793356e-04 -5.62805162705629e-04 -3.77915518336268e-04
Al 5.62907234083758e-05 9.24073788215892e-05 -1.03170084336693e-04
Al 3.21602394621728e-04 1.76949229988034e-04 3.06925804418459e-05
Al 2.89759188061222e-04 3.51480144555030e-05 -1.67953236314361e-04
Al -1.50927363418241e-04 -2.43518115575532e-04 1.17081675570922e-04
Al -4.08148511364416e-05 -2.22406828442608e-05 -1.56107778486724e-04
```

`calculation='md'` 表示晶胞固定的分子动力学。`dt=20` 使用 pw.x 的 Rydberg 原子时间单位，换算为 0.9675537306 fs；100 步推进的坐标时间为 96.75537306 fs。不能把 20 当成 20 fs，也不能直接套用 cp.x 的 Hartree 原子时间单位。

`ion_temperature='svr'` 是随机速度缩放温控，`tempw=300` 设置目标温度，`nraise=20` 对应约 19.35 fs 的温控特征时间。它不意味着每一步都等于 300 K。这里固定了初速度，没有固定 QE 内部温控的随机数；重新运行这条 SVR 轨迹，逐点温度不会与下面完全重合。

## 热运动为什么会触发对称性错误

第一次输入没有 `nosym`。完美初始晶体具有很多对称操作，原子按不同初速度移动后却不再满足它们，因此第一次离子移动之后程序停止：

```console
maxwell@maxwell:~/al/aimd$ tail -10 nve-dt20/al.md.out


     Linear momentum :   -0.0000000000    0.0000000000   -0.0000000000

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     Error in routine checkallsym (1):
     some of the original symmetry operations not satisfied
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

     stopping ...
```

这是输入设置与运动后的结构不相容，不是“材料在第一步就不稳定”。原目录保留，另建目录复制并用 `vi` 加入 `nosym=.true.`：

```console
maxwell@maxwell:~/al/aimd$ mkdir nve-dt20-nosym
maxwell@maxwell:~/al/aimd$ cp nve-dt20/al.md.in nve-dt20-nosym/al.md.in
maxwell@maxwell:~/al/aimd$ cp nve-dt20/run.slurm nve-dt20-nosym/run.slurm
maxwell@maxwell:~/al/aimd$ cd nve-dt20-nosym
maxwell@maxwell:~/al/aimd/nve-dt20-nosym$ mkdir tmp
maxwell@maxwell:~/al/aimd/nve-dt20-nosym$ vi al.md.in

```

这次保留时间反演配对，但不再要求运动中的晶体保持初始空间群。均匀 k 网格覆盖范围会相应变化，因此后面的计算比完美晶体的初始 SCF 更费时。

## 提交脚本与正在运行时的读法

恒温分支最终使用 16 个 MPI 进程、8 个 k 点池，每个进程一个 OpenMP 线程。下面是实际提交的完整脚本。两个 NVE 分支各使用 8 个 MPI 进程，自己的脚本随数据一起保存。

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-nvt-cg
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
mpirun -np 16 <qe_bin>/pw.x -nk 8 -in al.md.in > al.md.out 2> al.md.err
```

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ sbatch run.slurm
Submitted batch job 1977
```

运行中可以在同一个目录查看队列，再持续看 OUT 文件末尾：

```bash
squeue -j 1977
tail -f al.md.out
```

`tail -f` 中按 Ctrl+C 只结束查看，不会停止 Slurm 作业。看见新的 `Entering Dynamics` 行，说明程序又推进了一个离子步；它前面的一段 `iteration #` 则是该几何下的电子 SCF 迭代。两种 iteration 不要混在一起。

## OUT 中的一步包含哪些内容

先取 NVE 大步长分支的第一个离子步。最初的 SCF 已经收敛，紧接着打印能量分解、力与应力。以下是连续输出节选：

```text
!    total energy              =     -33.52087979 Ry
     estimated scf accuracy    <          2.3E-11 Ry
     smearing contrib. (-TS)   =       0.00028280 Ry
     internal energy E=F+TS    =     -33.52116259 Ry

     convergence has been achieved in   8 iterations

     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000001    0.00000040   -0.00000005
     atom    2 type  1   force =    -0.00000007    0.00000003   -0.00000003
     atom    3 type  1   force =     0.00000000    0.00000004   -0.00000039
     atom    4 type  1   force =    -0.00000038   -0.00000001    0.00000001
     atom    5 type  1   force =     0.00000035   -0.00000005    0.00000002
     atom    6 type  1   force =     0.00000001   -0.00000010    0.00000035
     atom    7 type  1   force =     0.00000006    0.00000003    0.00000001
     atom    8 type  1   force =     0.00000003   -0.00000034    0.00000008

     Total force =     0.000001     Total SCF correction =     0.000004
     SCF correction compared to forces is large: reduce conv_thr to get better values


     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=        2.98
   0.00002024   0.00000000   0.00000000            2.98        0.00        0.00
   0.00000000   0.00002024  -0.00000000            0.00        2.98       -0.00
   0.00000000  -0.00000000   0.00002024            0.00       -0.00        2.98


     Molecular Dynamics Calculation
     mass Al               =    26.98
     Time step             =    20.00 a.u.,  0.9676 femto-seconds
```

`estimated scf accuracy` 对应电子自洽的残差估计；本例每步要求小于 10⁻¹⁰ Ry。力是接下来推进原子位置所用的量。应力和 `P` 也会随运动变化，这里固定的是晶胞，不是把压力锁定为零。

这一段还保留了力的警告：初始结构的 `Total force` 只有约 10⁻⁶ Ry/bohr，而 `Total SCF correction` 为约 4×10⁻⁶ Ry/bohr，修正相对原力较大。电子残差达到输入阈值，并不能让这条提示自动失效。对本例接近对称极小值的初态，绝对数值很小，但仍不能宣称力已对 `conv_thr` 收敛；若要研究更精细的动力学量，需要另做更紧电子阈值的力与轨迹对照。后面的减半时间步只检查当前电子设置下的积分误差。

随后出现新的坐标与动能、温度：

```text
Entering Dynamics:    iteration =     1
                           time      =   0.0010 pico-seconds


ATOMIC_POSITIONS (crystal)
Al               0.0001375488        0.0008057202        0.0006561644
Al               0.5001926177        0.0006227609       -0.0006826455
Al               0.0007320655        0.4982569085        0.0002374365
Al               0.4996630927        0.5000608996        0.0001863149
Al              -0.0006258245        0.0007079354        0.4997654513
Al               0.4993407332        0.0002099472        0.4998840831
Al               0.0006842362        0.4996289887        0.4997195349
Al               0.4998755303        0.4997068395        0.5002336603


     kinetic energy (Ekin) =           0.01995091 Ry
     temperature           =         299.99999998 K 
     Ekin + Etot (const)   =         -33.50092887 Ry
     Ions kinetic stress =            2.34 (kbar)
                                      2.03           0.64           0.14
                                      0.64           3.10           1.57
                                      0.14           1.57           1.90



     Linear momentum :   -0.0000000000    0.0000000000   -0.0000000000
```

这里 `kinetic energy` 是离子动能；电子 SCF 给出的 `Etot` 与它相加，才是本次 NVE 检查的能量总和。金属展宽仍是电子计算中的数值设置，不应把 `degauss` 换算成离子温度写在这张图上。

前面的 OUT 同时打印了 `total energy` 与 `internal energy E=F+TS`。这条有限电子展宽的轨迹使用程序推进离子时对应的 `Etot` 加离子动能，不把其中一部分时刻换成另一列内部能。此处的 NVE 是固定晶胞、没有离子热浴的积分分支；电子展宽参数仍固定保留，不能进一步称为已经验证的真实有限电子温度系综。

QE 7.5 这段位置 Verlet 输出有一个细节：打印出的新坐标已前进到 n·dt，但同一块里的 Etot 和中心差分速度属于前一个坐标时刻 (n−1)·dt。提取脚本因此分别保存 `position_time_fs` 与 `energy_sample_time_fs`；画能量曲线使用后者，导出的坐标轨迹使用前者。这样才能把不同步长的同一物理时刻对齐。

## 结束后，逐步核对电子部分

```console
maxwell@maxwell:~/al/aimd/nvt-dt20-cg$ tail -12 al.md.out
     fftw         :    306.57s CPU    311.40s WALL (  645522 calls)
 
     Parallel routines
 
     PWSCF        :  10m 1.45s CPU  10m14.91s WALL

 
   This run was terminated on:  22:48:37  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

对于指定步数的 MD，输出 `The maximum number of steps has been reached.` 是走完所设步数的正常停止条件。仍需核对实际步数、每步 SCF 是否收敛，以及每步最后一次对角化是否有未解决的警告。

这个例子的第一个 `nvt-dt20-nosym` 分支虽打印了 `JOB DONE.`，第 44 步最后一次 Davidson 对角化却留下 `1 eigenvalues not converged`，因此没有用于本页主图。它保留在原目录，另建 `nvt-dt20-cg`，用 `cp`、`vi` 改为 CG 并收紧本征态精度设置后重新运行。两条 NVT 的随机热浴不同，不能把它们逐点相减当作算法误差。

NVE 大步长分支也有一次对角化警告，但发生在最后一个离子步的中间 SCF 迭代，随后的最终迭代已经消失。提取脚本区分中途警告与最终未解决的警告，不用简单的关键字计数代替这项检查。


提取轨迹时，应让能量、温度、坐标与同一个 MD 步号对应。下面的程序需求也保留电子求解和时间步长的检查。

```text
编写 analyse_aimd.py，读取 nvt-dt20-cg、nve-dt20-nosym、nve-dt10-nosym 的最终 al.md.in/out/err。分别要求 100、50、100 个离子步、正常步数停止和 JOB DONE、空 stderr、每段电子收敛；区分中间 SCF 对角化警告与每步末次迭代仍存在的警告。Ry 转 eV，dt 的时间单位乘 0.04837768653 转 fs；记录 QE Verlet 坐标时间 n*dt 与能量采样时间 (n-1)*dt 两列。总能量取程序 Etot 加离子动能，再除以 8 个原子。保留晶胞与连续坐标以计算短时 RMS 位移；写 thermo.csv、轨迹与 JSON 摘要，报告 NVE 总能量峰峰变化和共同末时刻位置差。不由短时位移拟合扩散系数。
```

下面是算例实际使用的完整源码。

<details>
<summary>analyse_aimd.py 完整源码</summary>

```python
from pathlib import Path
import re,csv,json,sys
import numpy as np
r=Path(__file__).resolve().parent
BOHR=0.529177210903;RYEV=13.605693122994;RYTIME_FS=0.04837768653
scenarios=[('nvt-dt20-cg',20.,100),('nve-dt20-nosym',20.,50),('nve-dt10-nosym',10.,100)]
if '--nve-only' in sys.argv: scenarios=scenarios[1:]
all_summary={};all_rows={};all_xyz={}
for name,dt,nstep in scenarios:
    d=r/name;txt=(d/'al.md.out').read_text();inp=(d/'al.md.in').read_text()
    assert 'JOB DONE.' in txt and 'The maximum number of steps has been reached.' in txt
    assert (d/'al.md.err').stat().st_size==0
    assert not re.search(r'convergence NOT achieved|Error in routine',txt)
    starts=list(re.finditer(r'Entering Dynamics:\s+iteration\s*=\s*(\d+)',txt));assert len(starts)==nstep
    cellblock=inp.split('CELL_PARAMETERS angstrom')[1].split('K_POINTS')[0]
    cell=np.array([list(map(float,l.split())) for l in cellblock.strip().splitlines()])
    init=np.array([list(map(float,l.split()[1:4])) for l in inp.split('ATOMIC_POSITIONS crystal')[1].split('CELL_PARAMETERS')[0].strip().splitlines()])
    assert init.shape==(8,3) and cell.shape==(3,3)
    nconv=len(re.findall(r'convergence has been achieved in\s+(\d+) iterations',txt));assert nconv==nstep
    rows=[];positions=[init@cell]
    for i,m in enumerate(starts):
        step=int(m.group(1));assert step==i+1
        pre=txt[(starts[i-1].end() if i else 0):m.start()]
        end=starts[i+1].start() if i+1<len(starts) else len(txt)
        b=txt[m.start():end]
        potential=float(re.findall(r'!\s+total energy\s*=\s*([-\d.]+)\s+Ry',pre)[-1])
        kinetic=float(re.search(r'kinetic energy \(Ekin\)\s*=\s*([-\d.]+)',b).group(1))
        total=float(re.search(r'Ekin \+ Etot \(const\)\s*=\s*([-\d.]+)',b).group(1))
        temperature=float(re.search(r'temperature\s*=\s*([-\d.]+)\s*K',b).group(1))
        assert abs(total-(potential+kinetic))<2e-8
        assert 'eigenvalues not converged' not in re.split(r'iteration\s+#\s*\d+',pre)[-1]
        early_warnings=pre.count('eigenvalues not converged')
        conv=int(re.findall(r'convergence has been achieved in\s+(\d+) iterations',pre)[-1])
        residual=float(re.findall(r'estimated scf accuracy\s*<\s*([.\dEe+\-]+)\s*Ry',pre)[-1])
        assert residual<=1.0e-10
        posblock=b.split('ATOMIC_POSITIONS (crystal)')[1].strip().splitlines()[:8]
        frac=np.array([list(map(float,l.split()[1:4])) for l in posblock]);assert frac.shape==(8,3)
        positions.append(frac@cell)
        # Position-Verlet in QE 7.5 advances coordinates before output_tau.
        # Etot and the centred finite-difference velocity belong to the preceding position.
        rows.append(dict(step=step,energy_sample_time_fs=(step-1)*dt*RYTIME_FS,position_time_fs=step*dt*RYTIME_FS,temperature_K=temperature,potential_Ry=potential,kinetic_Ry=kinetic,total_Ry=total,scf_iterations=conv,early_diagonalization_warning_count=early_warnings,scf_estimated_accuracy_Ry=residual))
    t=np.array([v['energy_sample_time_fs'] for v in rows]);en=np.array([v['total_Ry'] for v in rows]);temps=np.array([v['temperature_K'] for v in rows]);de=(en-en[0])*RYEV*1000/8
    for v,x in zip(rows,de):v['total_change_meV_atom']=float(x)
    with (d/'thermo.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    xyz=np.array(positions);np.savez_compressed(d/'trajectory.npz',positions_A=xyz,cell_A=cell,time_fs=np.arange(nstep+1)*dt*RYTIME_FS)
    lattice=' '.join(f'{v:.12f}' for v in cell.ravel())
    with (d/'trajectory.xyz').open('w') as f:
        for j,pos in enumerate(xyz):
            f.write('8\nLattice="'+lattice+'" Properties=species:S:1:pos:R:3 pbc="T T T" time_fs='+str(j*dt*RYTIME_FS)+'\n')
            f.writelines('Al '+' '.join(f'{x:.10f}' for x in p)+'\n' for p in pos)
    wall=re.findall(r'PWSCF\s*:\s*(.*?)\s+CPU\s+(.*?)\s+WALL',txt)[-1][1]
    summary=dict(nsteps=nstep,natoms=8,dt_Ry_au=dt,dt_fs=dt*RYTIME_FS,coordinate_end_time_fs=nstep*dt*RYTIME_FS,energy_end_time_fs=float(t[-1]),all_scf_converged=True,final_scf_iteration_diagonalization_warnings=0,early_scf_diagonalization_warnings=sum(v['early_diagonalization_warning_count'] for v in rows),scf_cycles=nconv,scf_iterations_min=min(x['scf_iterations'] for x in rows),scf_iterations_max=max(x['scf_iterations'] for x in rows),temperature_first_K=float(temps[0]),temperature_mean_K=float(np.mean(temps)),temperature_min_K=float(np.min(temps)),temperature_max_K=float(np.max(temps)),temperature_last_K=float(temps[-1]),energy_change_final_meV_atom=float(de[-1]),energy_peak_to_peak_meV_atom=float(np.ptp(de)),energy_linear_slope_meV_atom_ps=float(np.polyfit(t,de,1)[0]*1000),rms_displacement_final_A=float(np.sqrt(np.mean(np.sum((xyz[-1]-xyz[0])**2,axis=1)))),max_atom_displacement_A=float(np.max(np.linalg.norm(xyz[-1]-xyz[0],axis=1))),wall_time=wall,interpretation='short fixed-volume small-cell trajectory; not thermal-stability or equilibrium-property evidence')
    (d/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');all_summary[name]=summary;all_rows[name]=rows;all_xyz[name]=xyz
coarse=np.array([v['total_change_meV_atom'] for v in all_rows['nve-dt20-nosym']]);fine=np.array([v['total_change_meV_atom'] for v in all_rows['nve-dt10-nosym'][::2]])
assert coarse.shape==fine.shape
matched=dict(matched_energy_times=50,energy_time_end_fs=all_rows['nve-dt20-nosym'][-1]['energy_sample_time_fs'],max_energy_change_difference_meV_atom=float(np.max(np.abs(coarse-fine))),final_position_same_time_fs=all_summary['nve-dt20-nosym']['coordinate_end_time_fs'],rms_position_difference_at_same_end_A=float(np.sqrt(np.mean(np.sum((all_xyz['nve-dt20-nosym'][-1]-all_xyz['nve-dt10-nosym'][-1])**2,axis=1)))))
all_summary['nve_matched_time_comparison']=matched
all_summary['time_axis_note']='QE7.5 position Verlet prints advanced coordinates at n*dt; Etot and centred velocity in that block refer to preceding geometry at (n-1)*dt. CSV keeps both clocks.'
(r/'summary.json').write_text(json.dumps(all_summary,indent=2)+'\n')
print('case                steps  dt_fs    coord_end_fs  energy_range_meV_atom  mean_T_K')
for name,s in all_summary.items():
    if not isinstance(s,dict) or 'nsteps' not in s:continue
    print(f"{name:20s} {s['nsteps']:3d}  {s['dt_fs']:.6f}  {s['coordinate_end_time_fs']:9.6f}  {s['energy_peak_to_peak_meV_atom']:13.6f}       {s['temperature_mean_K']:.3f}")
print(f"All {sum(n for _,_,n in scenarios)} SCF cycles converged; no final-iteration diagonalization warning; {len(scenarios)} native JOB DONE endings.")
print('Early SCF diagonalization warnings:', {n: all_summary[n]['early_scf_diagonalization_warnings'] for n,_,_ in scenarios})
print('NVE position difference at the common final time:',matched['rms_position_difference_at_same_end_A'],'angstrom RMS')
print('NVE total-energy conservation tested only over ~48 fs; no thermodynamic convergence claim.')
```

</details>

```console
maxwell@maxwell:~/al/aimd$ ../.venv/bin/python analyse_aimd.py > analysis.out
maxwell@maxwell:~/al/aimd$ cat analysis.out
case                steps  dt_fs    coord_end_fs  energy_range_meV_atom  mean_T_K
nvt-dt20-cg          100  0.967554  96.755373      51.897811       196.418
nve-dt20-nosym        50  0.967554  48.377687       0.019405       142.856
nve-dt10-nosym       100  0.483777  48.377687       0.004269       142.226
All 250 SCF cycles converged; no final-iteration diagonalization warning; 3 native JOB DONE endings.
Early SCF diagonalization warnings: {'nvt-dt20-cg': 0, 'nve-dt20-nosym': 1, 'nve-dt10-nosym': 0}
NVE position difference at the common final time: 2.272203084249565e-05 angstrom RMS
NVE total-energy conservation tested only over ~48 fs; no thermodynamic convergence claim.
```

最终使用的三条轨迹共有 250 段电子 SCF，均达到设置的残差要求，最终对角化无未解决的警告。这证明它们完成了本例规定的数值流程，还没有证明电子网格、超胞尺寸和轨迹长度对物性收敛。

## 温度下降是否说明轨迹坏了

![恒温和NVE轨迹的瞬时温度](/Atlas/examples/al/figures/aimd-temperature.png)

SVR 的输入目标为 300 K，但这段不足 0.1 ps 的实际平均温度只有 196.418 K，瞬时范围为 90.061–348.887 K。它显然还不能作为充分平衡的 300 K 系综。初始位置接近零温极小值，最初输入的动能会转移为位移的势能；8 原子体系也会有很大的瞬时温度起伏。延长平衡与采样、增大体系，并检查统计量才可能回答热平衡性质。

NVE 没有温控，温度从初始 300 K 下降也不自动意味着程序丢失能量。下面右图把势能变化与动能变化一起画出，两个方向相反；是否守恒，应看左图里的总和。

![等时长NVE的能量变化与动势能交换](/Atlas/examples/al/figures/aimd-energy.png)

两条 NVE 具有相同初始位置、初速度、电子协议和固定晶胞。大步长设置为 `nstep=50, dt=20`，小步长设置为 `nstep=100, dt=10`；两者坐标都推进到 48.377687 fs。

| NVE 步长 | 步数 | 总能量峰峰变化 / meV·atom⁻¹ |
|---:|---:|---:|
| 0.967554 fs | 50 | 0.019405 |
| 0.483777 fs | 100 | 0.004269 |

步长减半后，本段轨迹的能量波动明显减小。两条轨迹在共同终点的原子位置 RMS 差为 2.27×10⁻⁵ Å。这是本例短时间内的积分步长检查；不能把一个小的短时波动范围外推成长期能量稳定，也不能拿 SVR 中随热浴交换而变化的总能量套用 NVE 的守恒要求。

## 提取坐标并重新画图

每个完成目录下的 `thermo.csv` 按离子步保存能量、温度、SCF 迭代数和残差；`trajectory.xyz` 含初始帧及全部推进后的帧，写有晶格与周期边界，长度分别为 101、51、101 帧。原始未回卷坐标被保留，没有用绝对值或人工平滑修饰运动。

```console
maxwell@maxwell:~/al/aimd$ head -4 nve-dt20-nosym/thermo.csv
step,energy_sample_time_fs,position_time_fs,temperature_K,potential_Ry,kinetic_Ry,total_Ry,scf_iterations,early_diagonalization_warning_count,scf_estimated_accuracy_Ry,total_change_meV_atom
1,0.0,0.9675537305999999,299.99999998,-33.52087979,0.01995091,-33.50092887,8,0,2.3e-11,0.0
2,0.9675537305999999,1.9351074611999999,299.25269602,-33.52083006,0.01990121,-33.50092885,7,0,3.4e-11,3.401423562183524e-05
3,1.9351074611999999,2.9026611918,297.01880642,-33.52068143,0.01975265,-33.50092877,7,0,5.3e-11,0.0001700711660248932
```

![短时间原子位移](/Atlas/examples/al/figures/aimd-displacement.png)

图中 RMS 位移是相对初始原子位置的短时变化，没有据此拟合扩散系数。要重新出图，把 `aimd` 子目录和 [plot_aimd.py](/Atlas/examples/al/plot_aimd.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 放在同一 Al 数据目录，运行：


图中分别保留恒温与 NVE 时段，以及两种时间步长的实际采样点；下面列出出图时使用的数据列。

```text
编写 plot_aimd.py，从 Al 根目录读取三条轨迹各自的 aimd/<case>/thermo.csv。温度按真实时间绘制；NVE 总能量用 energy_sample_time_fs 对齐，以各自第一行作能量变化基准，换成 meV/atom；同时画势能与动能交换。位移从各目录 trajectory.npz 的 positions_A 计算相对初帧的 RMS，横轴使用其中 time_fs，保留坐标与能量两套时间约定。输出现有温度、能量和位移三组 PNG/PDF，复用 atlas_plot_style.py。
```

下面是算例实际使用的完整源码。

<details>
<summary>plot_aimd.py 完整源码</summary>

```python
"""Plot the verified QE Al AIMD records from the Al bundle root."""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=r/'aimd';out=r/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
colors=['#009e73','#d55e00','#cc79a7']
def data(name):return np.genfromtxt(d/name/'thermo.csv',delimiter=',',names=True)
def save(fig,name):
    fig.tight_layout();fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
nvt=data('nvt-dt20-cg');nve20=data('nve-dt20-nosym');nve10=data('nve-dt10-nosym')
fig,ax=plt.subplots(2,1,figsize=(7.4,6),sharex=True)
ax[0].plot(nvt['energy_sample_time_fs'],nvt['temperature_K'],color=colors[0],label='SVR target 300 K; dt = 0.968 fs')
ax[0].axhline(300,color='#777',ls='--',lw=1,label='Target')
ax[0].set(ylabel='Instantaneous temperature (K)');ax[0].legend(frameon=False,fontsize=9)
for arr,c,label in [(nve20,colors[1],'NVE dt = 0.968 fs'),(nve10,colors[2],'NVE dt = 0.484 fs')]:
    ax[1].plot(arr['energy_sample_time_fs'],arr['temperature_K'],color=c,label=label)
ax[1].set(xlabel='Time of the sampled energy/velocity (fs)',ylabel='Instantaneous temperature (K)');ax[1].legend(frameon=False,fontsize=9)
fig.suptitle('8-atom periodic Al | short trajectories, not a thermal-stability test',fontsize=11);save(fig,'aimd-temperature')
fig,ax=plt.subplots(1,2,figsize=(10,4))
for arr,c,label in [(nve20,colors[1],'dt = 0.968 fs'),(nve10,colors[2],'dt = 0.484 fs')]:
    ax[0].plot(arr['energy_sample_time_fs'],arr['total_change_meV_atom'],color=c,label=label)
ax[0].set(xlabel='Time (fs)',ylabel='Change of total energy (meV/atom)');ax[0].legend(frameon=False)
conv=13.605693122994*1000/8
for field,c,label in [('kinetic_Ry',colors[1],'Kinetic'),('potential_Ry',colors[0],'Potential')]:
    ax[1].plot(nve10['energy_sample_time_fs'],(nve10[field]-nve10[field][0])*conv,color=c,label=label)
ax[1].set(xlabel='Time (fs)',ylabel='Energy change (meV/atom)');ax[1].legend(frameon=False)
fig.suptitle('NVE step-size check over ~48 fs | identical initial positions and velocities',fontsize=11);save(fig,'aimd-energy')
fig,ax=plt.subplots(figsize=(7.2,3.7))
for name,c,label in [('nvt-dt20-cg',colors[0],'SVR'),('nve-dt20-nosym',colors[1],'NVE dt = 0.968 fs'),('nve-dt10-nosym',colors[2],'NVE dt = 0.484 fs')]:
    a=np.load(d/name/'trajectory.npz');p=a['positions_A'];rms=np.sqrt(np.mean(np.sum((p-p[0])**2,axis=2),axis=1))
    ax.plot(a['time_fs'],rms,color=c,label=label)
ax.set(xlabel='Coordinate time (fs)',ylabel='RMS displacement from initial positions (Å)',title='Short-time displacement; no diffusion or long-term stability inference')
ax.legend(frameon=False);save(fig,'aimd-displacement')
print('Wrote aimd-temperature, aimd-energy, aimd-displacement as PNG and PDF')
```

</details>

```bash
python plot_aimd.py
```

这会生成温度、能量与位移三组 PNG/PDF。原始提取代码为 [analyse_aimd.py](/Atlas/examples/al/aimd/analyse_aimd.py)，初态记录为 [initial-velocities.json](/Atlas/examples/al/aimd/initial-velocities.json)；最初的输入准备记录为 [prepare_aimd.py](/Atlas/examples/al/prepare_aimd.py)。它保留初态的生成过程；本页实际完成的三条路线使用后续调整过的 `nosym` 与 CG 设置，重跑时应使用上表各目录中的最终输入和 `run.slurm`，不能把最初的生成脚本当成最终三条路线的一键入口。

<details>
<summary>prepare_aimd.py 的完整源码</summary>

```python
from pathlib import Path
import numpy as np,json
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
r=Path(__file__).resolve().parent;d=r/'aimd';d.mkdir()
cell=np.array(json.loads((r/'structure.json').read_text())['cell_angstrom'])
p=Phonopy(PhonopyAtoms(symbols=['Al'],cell=cell,scaled_positions=[[0,0,0]],masses=[26.9815385]),np.eye(3,dtype=int)*2,primitive_matrix='P')
sc=p.supercell;N=len(sc);rng=np.random.default_rng(20260922)
v=rng.normal(size=(N,3));v-=v.mean(axis=0)
kb=1.380649e-23;mass=26.9815385*1.66053906660e-27;dof=3*N-3
v*=np.sqrt(dof*kb*300/(mass*np.sum(v*v)))
va=v/(0.529177210903e-10/4.837768653e-17)
base=(r/'finite-disp/n2-d0.01/disp-001/al.scf.in').read_text()
base=base[:base.index('ATOMIC_POSITIONS crystal')]+'ATOMIC_POSITIONS crystal\n'+''.join('Al '+' '.join(f'{x:.14f}' for x in row)+'\n' for row in sc.scaled_positions)+'CELL_PARAMETERS angstrom\n'+''.join(' '.join(f'{x:.14f}' for x in row)+'\n' for row in sc.cell)+'K_POINTS automatic\n4 4 4 0 0 0\nATOMIC_VELOCITIES\n'+''.join('Al '+' '.join(f'{x:.14e}' for x in row)+'\n' for row in va)
for name,dt,nstep,thermostat in [('nvt-dt20',20,100,'svr'),('nve-dt20',20,50,'not_controlled'),('nve-dt10',10,100,'not_controlled')]:
 sub=d/name;sub.mkdir();(sub/'tmp').mkdir()
 inp=base.replace(" calculation = 'scf'",f" calculation = 'md'\n nstep = {nstep}\n dt = {dt}\n iprint = 1").replace(" verbosity = 'high'"," verbosity = 'low'").replace(' conv_thr = 1.0d-12',' conv_thr = 1.0d-10')
 ions=f"&IONS\n ion_dynamics = 'verlet'\n ion_velocities = 'from_input'\n ion_temperature = '{thermostat}'\n tempw = 300\n nraise = 20\n/\n"
 inp=inp.replace('ATOMIC_SPECIES',ions+'ATOMIC_SPECIES');(sub/'al.md.in').write_text(inp)
 head=(r/'dfpt/run.slurm').read_text().split('set -e\n')[0].replace('atlas-al-ph4',f'atlas-al-{name}')
 (sub/'run.slurm').write_text(head+'set -e\nmpirun -np 8 <qe_bin>/pw.x -in al.md.in > al.md.out 2> al.md.err\n')
(d/'initial-velocities.json').write_text(json.dumps({'seed':20260922,'temperature_K_from_21_dof':mass*np.sum(v*v)/(dof*kb),'center_of_mass_velocity_m_s':v.mean(axis=0).tolist(),'velocity_unit':'bohr/Rydberg atomic time','velocities':va.tolist(),'physical_time_fs':{'nvt-dt20':96.75537306,'nve-dt20':48.37768653,'nve-dt10':48.37768653},'scope':'short integration and thermostat demonstration; 8-atom box and 4^3 mesh are not a production thermal-stability protocol'},indent=2))
print('Prepared 8-atom Al: SVR 100xdt20, matched-duration NVE 50xdt20 and 100xdt10; explicit identical initial velocities, 300K/21 DOF.')
```

</details>

| 分支 | 输入与脚本 | 完整 OUT | 数值与坐标 |
|---|---|---|---|
| nvt-dt20-cg | [输入](/Atlas/examples/al/aimd/nvt-dt20-cg/al.md.in) / [脚本](/Atlas/examples/al/aimd/nvt-dt20-cg/run.slurm) | [OUT](/Atlas/examples/al/aimd/nvt-dt20-cg/al.md.out) | [CSV](/Atlas/examples/al/aimd/nvt-dt20-cg/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nvt-dt20-cg/trajectory.xyz) |
| nve-dt20-nosym | [输入](/Atlas/examples/al/aimd/nve-dt20-nosym/al.md.in) / [脚本](/Atlas/examples/al/aimd/nve-dt20-nosym/run.slurm) | [OUT](/Atlas/examples/al/aimd/nve-dt20-nosym/al.md.out) | [CSV](/Atlas/examples/al/aimd/nve-dt20-nosym/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nve-dt20-nosym/trajectory.xyz) |
| nve-dt10-nosym | [输入](/Atlas/examples/al/aimd/nve-dt10-nosym/al.md.in) / [脚本](/Atlas/examples/al/aimd/nve-dt10-nosym/run.slurm) | [OUT](/Atlas/examples/al/aimd/nve-dt10-nosym/al.md.out) | [CSV](/Atlas/examples/al/aimd/nve-dt10-nosym/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nve-dt10-nosym/trajectory.xyz) |

## 文献中的 AIMD 热稳定性图件表达

恒温 AIMD 可同时展示温度、能量和结构在采样窗口内的变化。轨迹长度应由所研究的过程、相关时间与统计误差决定；结构快照用于检查键长、配位和界面变化。能量守恒则用独立 NVE 对照检验，恒温轨迹中的能量涨落还受到温控器影响。下图文献采用 300 K、10 ps 的轨迹，这是该研究的实际设置。

<figure class="research-figure"><img src="/Atlas/figures/literature/M8_AIMD_ThermalStability_ZrI2_Fig2.jpg" alt="六种 ZrI2 基异质结在 300 K 下运行 10 ps 的 AIMD 温度与总能量演化及结构快照" loading="lazy"/><figcaption>六种 ZrI<sub>2</sub> 基异质结在 300 K、10 ps 恒温 AIMD 模拟中的温度 <em>T</em>(<em>t</em>) 与总能量 <em>E</em>(<em>t</em>) 双轴时间序列（a–f），同时给出初始构型与 10 ps 末帧的结构快照以检验热稳定性。引自 Zhang 等人，<em>Phys. Chem. Chem. Phys.</em> <strong>27</strong>, 19410 (2025)，Fig. 2a–f，<a href="https://doi.org/10.1039/D5CP02349A" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D5CP02349A</a>。</figcaption></figure>

下一步：若要看零温附近的振动模式，转到 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 或 [有限位移声子](/Atlas/m/phonon-finite-disp/qe/)。短 AIMD 与这些计算回答的时间尺度和近似不同，应分别检查后再合起来讨论。

```text
明确结构 + 初速度 → 每步电子 SCF → 力 → Verlet 移动 → 温度 / 能量 / 坐标
                                    ├─ NVE：相同步长时间对照与能量守恒
                                    └─ SVR：温控响应与平衡、采样长度检查
```

## 参考资料

[pw.x 的 MD、时间步与温控输入](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [QE 7.5 的 Verlet 实现](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/dynamics_module.f90)
