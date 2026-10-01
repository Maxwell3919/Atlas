层间距会随热运动改变，界面也可能滑移或出现局部重构。研究这些过程时，AIMD 需要同时跟踪原子坐标、温度和电子能量；一条能量曲线有起伏，本身不能说明界面已经保持稳定，也不能说明结构发生了破坏。先确认力与积分能可靠推进轨迹，再读结构随时间的变化。

这里用实际运行的 8 原子周期 fcc Al 学习这一步。它来自 [Al 晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax) 的单原子原胞，沿三个原胞基矢各重复两次。使用 QE 7.5、LDA-PZ、`Al.pz-vbc.UPF`、40/160 Ry 截断和 4³ 超胞 k 网格，固定晶胞。已有 100 步 SVR 轨迹和两条相同初态、等时长的 NVE 轨迹；它们检验热浴响应与时间步长误差，时长分别约 97 和 48 fs。

[下载完整 Al 计算包](/Atlas/examples/al-lesson-files.tar.gz)，解压后进入 `al/aimd`。普通电子自洽和弛豫见 [SCF](/Atlas/m/scf/qe/) 与 [固定晶胞优化](/Atlas/m/relax/qe/)。研究 ZrCl₂/Sc₂C 或 SnSe₂/Sr₂N 时，初态应来自自身的已接受界面，并重新确定合适的超胞、电子采样、步长和采样窗口；本例的 Al 轨迹不能代表它们的热稳定性。

## 同一初态使步长比较有意义

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



## 原子运动后不再保持初始空间群

原输入未设置 `nosym`，原子按不同初速度移动后，第二个几何不满足起始空间群，输出出现：

```text
Error in routine checkallsym (1):
some of the original symmetry operations not satisfied
```

随后使用 `nosym=.true.` 的独立目录完成计算。这是运动几何与对称性设置不相容；根据此报错不能判断材料已经发生热破坏。均匀网格的不可约点数随对称性设置改变，电子计算耗时也会变化。数据包保存了初次失败目录与最终输入，重跑时使用下方列出的最终分支。

## 一次离子推进前，先读电子求解

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



## 先区分温控交换与积分误差

![恒温和NVE轨迹的瞬时温度](/Atlas/examples/al/figures/aimd-temperature.png)

SVR 的输入目标为 300 K，但这段不足 0.1 ps 的实际平均温度只有 196.418 K，瞬时范围为 90.061–348.887 K。它显然还不能作为充分平衡的 300 K 系综。初始位置接近零温极小值，最初输入的动能会转移为位移的势能；8 原子体系也会有很大的瞬时温度起伏。延长平衡与采样、增大体系，并检查统计量才可能回答热平衡性质。

NVE 没有温控，温度从初始 300 K 下降也不自动意味着程序丢失能量。下面右图把势能变化与动能变化一起画出，两个方向相反；是否守恒，应看左图里的总和。

![等时长NVE的能量变化与动势能交换](/Atlas/examples/al/figures/aimd-energy.png)

两条 NVE 具有相同初始位置、初速度、电子协议和固定晶胞。大步长设置为 `nstep=50, dt=20`，小步长设置为 `nstep=100, dt=10`；两者坐标都推进到 48.377687 fs。

| NVE 步长 | 步数 | 总能量峰峰变化 / meV·atom⁻¹ |
|---:|---:|---:|
| 0.967554 fs | 50 | 0.019405 |
| 0.483777 fs | 100 | 0.004269 |

表中峰峰值取各自完整的能量记录：大步长共 50 个能量时刻，范围为 0–47.410133 fs；小步长共 100 个，范围为 0–47.893910 fs。若只比较共同的 50 个能量时刻 0–47.410133 fs，小步长取 CSV 数据第 1、3、…、99 行，两条记录的峰峰值分别为 **0.019405 和 0.004218 meV/atom**。这一等时刻对照仍显示减半步长后短程能量波动减小。

坐标检查单独使用两条轨迹的完整末帧：它们都位于 48.377687 fs，原子位置 RMS 差为 2.27×10⁻⁵ Å。这个共同坐标终点与上面的能量采样终点不同。两项结果检验的是本例短时间内的积分步长误差；不能把短时波动外推成长期能量稳定，也不能拿 SVR 中随热浴交换而变化的总能量套用 NVE 的守恒要求。



[Bussi、Donadio 与 Parrinello，*Canonical sampling through velocity-rescaling*](https://arxiv.org/html/0803.4060)式 (7)给出 SVR 动能与目标分布交换的时间尺度；Fig. 1 区分热浴引起的能量变化与积分误差，Fig. 2 直接比较两种时间步长下的 NVE 总能量和 NVT 有效守恒量。本例采用相同初态的 NVE 步长对照，没有提取论文的 NVT 有效守恒量，故不能用 SVR 的 $E_{\mathrm{kin}}+E_{\mathrm{tot}}$ 波动作为对应的积分误差。

## 提取能量、温度与坐标

每个完成目录都有 `al.md.in/out/err`。脚本按 MD 步号拆开电子 SCF 与离子输出，读取能量、温度和坐标；保留两个时间字段。坐标属于 $n\Delta t$，此处 QE 7.5 的位置 Verlet 输出中能量与中心差分速度属于 $(n-1)\Delta t$。跨步长比较能量时对齐 `energy_sample_time_fs`，看坐标则使用 `position_time_fs`。

三条分支共 250 个 SCF 循环均达到了 `conv_thr=1e-10 Ry`，每步最后一次迭代没有遗留对角化警告。大步长 NVE 的一次中途警告在后续迭代消失；另一个早期 NVT 分支在第 44 步末次迭代仍有警告，保存在包内但没有进入上述结果。程序最后的 `JOB DONE.` 说明程序正常结束，逐步电子记录才说明这些力由达到当前电子条件的计算给出。

```text
编写 analyse_aimd.py，读取 nvt-dt20-cg、nve-dt20-nosym、nve-dt10-nosym 的最终
al.md.in/out/err；要求分别 100、50、100 个 MD 步、正常步数停止、JOB DONE 和空 stderr。
每步核对电子收敛，区分中途与末次迭代的对角化警告。dt 乘 0.04837768653 得到 fs，
分别保存能量时间 (n-1)*dt 和坐标时间 n*dt；Ry 转 eV，能量差除以 8 个原子。
保存 thermo.csv、连续坐标轨迹和 JSON 摘要；比较 NVE 的等时长能量变化与共同末帧。
保留原始文件，不从不足 0.1 ps 的位移拟合扩散系数或判断长期热稳定性。
```

[analyse_aimd.py 完整源码](/Atlas/examples/al/aimd/analyse_aimd.py)

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

提取程序使用 Python 3 与 NumPy；绘图另需 Matplotlib。保留数据包的目录层级，在 `al/aimd` 目录运行：

```bash
python3 analyse_aimd.py
```

实际输出为：

```text
case                steps  dt_fs    coord_end_fs  energy_range_meV_atom  mean_T_K
nvt-dt20-cg          100  0.967554  96.755373      51.897811       196.418
nve-dt20-nosym        50  0.967554  48.377687       0.019405       142.856
nve-dt10-nosym       100  0.483777  48.377687       0.004269       142.226
All 250 SCF cycles converged; no final-iteration diagonalization warning; 3 native JOB DONE endings.
```

NVT 的 51.897811 meV/atom 范围包含热浴交换，不能与 NVE 的守恒误差放在同一标准下排名。结果还保存在各分支的 `thermo.csv` 与 `summary.json`。坐标 XYZ 含初始帧及所有推进帧，三条分支分别有 101、51、101 帧；连续未回卷坐标被保留，避免周期边界跳转被当成突然运动。

| 分支 | 输入与脚本 | 完整 OUT | 数值与坐标 |
|---|---|---|---|
| nvt-dt20-cg | [输入](/Atlas/examples/al/aimd/nvt-dt20-cg/al.md.in) / [脚本](/Atlas/examples/al/aimd/nvt-dt20-cg/run.slurm) | [OUT](/Atlas/examples/al/aimd/nvt-dt20-cg/al.md.out) | [CSV](/Atlas/examples/al/aimd/nvt-dt20-cg/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nvt-dt20-cg/trajectory.xyz) |
| nve-dt20-nosym | [输入](/Atlas/examples/al/aimd/nve-dt20-nosym/al.md.in) / [脚本](/Atlas/examples/al/aimd/nve-dt20-nosym/run.slurm) | [OUT](/Atlas/examples/al/aimd/nve-dt20-nosym/al.md.out) | [CSV](/Atlas/examples/al/aimd/nve-dt20-nosym/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nve-dt20-nosym/trajectory.xyz) |
| nve-dt10-nosym | [输入](/Atlas/examples/al/aimd/nve-dt10-nosym/al.md.in) / [脚本](/Atlas/examples/al/aimd/nve-dt10-nosym/run.slurm) | [OUT](/Atlas/examples/al/aimd/nve-dt10-nosym/al.md.out) | [CSV](/Atlas/examples/al/aimd/nve-dt10-nosym/thermo.csv) / [XYZ](/Atlas/examples/al/aimd/nve-dt10-nosym/trajectory.xyz) |



完整 MPI 和环境设置见每条分支自己的 `run.slurm`。恒温分支原记录使用 16 个 MPI 进程、8 个 k 点池，两个 NVE 使用 8 个 MPI 进程；所有分支每进程一个 OpenMP 线程。重新计算前应修改实际程序与赝势路径。已有数据的提取和重画不需要提交这些作业。

## 用实际数据重画积分对照

温度图使用 CSV 的真实采样时间；NVE 总能量以各自第一行作差，再转成 meV/atom。势能和动能交换图也取同一基准。坐标的短时 RMS 位移可保留为轨迹核对，不能将其斜率直接换成扩散系数。

```text
从 Al 根目录读取三条 aimd/<case>/thermo.csv。温度用真实时间，NVE 能量按
energy_sample_time_fs 对齐并以首行作差；换算为 meV/atom，分开势能和动能交换。
坐标若需作图，从 trajectory.npz 的 positions_A 与 time_fs 读取并保留独立时间约定。
用现有 plot_aimd.py 和 atlas_plot_style.py 重建图，不平滑、插值或补出新的采样点。
```

[绘图源码](/Atlas/examples/al/plot_aimd.py) · [实际使用的绘图样式](/Atlas/examples/al/atlas_plot_style.py)

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

从 `al` 根目录运行 `python3 plot_aimd.py` 可重建原有 PNG/PDF。正文使用温度响应和能量交换图，因为它们直接解释上述两类结果；原位移图与生成代码保留在数据包中。`prepare_aimd.py` 记录最初的超胞和速度生成过程，可从 [原源码](/Atlas/examples/al/prepare_aimd.py) 查看；它生成的起始输入没有包含所有后续修复，重跑应采用表中最终输入。

## 怎样接到界面热运动

界面 AIMD 的判读需要回到构型：在同一共同晶胞下追踪层间距的分布、两层相对滑移、层内键长和配位变化，并对相邻时间段与末帧查看是否发生持续重构。若原子跨过周期边界，应先按层和键的连续性展开坐标，再求距离，不能把分数 z 的跳变直接解释成层脱离。

Bu 与 Sun 的 [WS₂/Sc₂C 研究](https://doi.org/10.1039/D5CP01402F)在 §2 为 AIMD 构造 4×4×1 超胞，§3.1 使用 300 K、1 fs 步长、6 ps 轨迹；Fig. 6(a–c)给出声子，Fig. 6(d–f)展示对应 AIMD 的能量时间序列。这里借鉴的是“先给出超胞、温度与窗口，再结合轨迹和振动结果读结构”的分析方法。其 6 ps 是该研究的设置，不能作为任意材料的充分采样标准；Al 例子更短，也没有界面层间距统计。

原文把该 AIMD 图描述为自由能涨落；本例 QE 数据明确是程序打印的电子能量、离子动能与温度，不把单条轨迹的能量序列重新命名为材料自由能。要讨论温度下的界面稳定性，需用该材料实际轨迹说明采样期间观察到的结构变化，并把未出现的事件限制在所用超胞、温度和观察窗口内。

零温附近的集体模式见 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 或 [有限位移声子](/Atlas/m/phonon-finite-disp/qe/)。它们与有限温度、有限时长的 AIMD 各自补充一部分结构证据。

[pw.x MD 与时间单位](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [QE 7.5 Verlet 实现](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/dynamics_module.f90)
