应变下的声子负频先要从结构、电子采样和二维长波处理诊断；确认它反映真实势能面之后，才有理由研究热涨落或量子涨落是否改变软模。[Ba₂N 原文](https://doi.org/10.1103/PhysRevB.105.165101) Fig. 8 展示 +5% 下 K 点虚频，这是简谐稳定性约束；该文没有用有限温度重整化来消除它。

本文保留一个 MACE–Si 方法存档：从 64 原子轨迹的位移 u 和力 F 拟合 F≈−Φu，再由 phonopy 求同一路径的频率。它回答二阶模型能否描述这批热运动样本。数据来自 MACE-MP-0 small，计算使用 MACE、symfc 和 phonopy；没有 ZrCl₂/Sc₂C 的 DFT 力校准、温度采样或 EPC。

[Hellman 等 TDEP 原文](https://arxiv.org/html/1303.1145) Sec. II 的式 (3)–(4) 将 MD 位移—力关系写成最小二乘问题，Sec. III 的 Fig. 1 比较对称性约束下的采样收敛。本文借鉴的是力拟合和样本敏感性检查，没有运行 TDEP 软件或计算其自由能。SSCHA 则优化变分自由能；它的辅助谐频率、自由能 Hessian 频率和动力学谱峰各有定义，不能由本例的 Φ 一次代替。后面的 40/60 帧频率差会具体说明为何力拟合误差较平稳仍不足以接受温度重整化声子。

## 把参考结构写清楚，再取位移

沿用前两页的相邻目录，模型仍为 MACE-MP-0 small。`prepare.py` 从 `../si-vc-relax/relaxed.extxyz` 取晶胞，从 `../si-md/nve-1fs.traj` 取旧轨迹。复算核验还会读取旧的 `../si-md/initial.traj`。模型文件位于 `../models/mace-mp-0-small.model`，SHA256 为 `2ddb079cee0e131eaaf6912ba581b394551ead283e95c99cfe78c605d10b5736`；来源与下载方法见[前面的 MACE 模型准备](/Atlas/m/relax/mace/)。

旧 vc-relax 晶胞的三个角与 90° 有约 0.005° 的微小差别。如果一边保留这个剪切，一边直接给晶胞施加理想立方对称，后面的力常数对称化就没有统一参考。这里明确采用另一个参考：取旧晶胞体积的立方根作晶格常数，重新生成理想金刚石 Si 常规胞，然后只允许均匀体积变化，用同一 MACE 模型检查原子力和应力。旧结构与旧轨迹都保留原文件。

下面的 `<MACE环境>` 表示运行本次计算的 Python 环境路径。实际环境是 MACE 0.3.16、ASE 3.29.0、phonopy 4.4.0、symfc 1.7.3；ASE 和 SciPy 来自当前账户的用户包目录，phonopy 和 symfc 来自虚拟环境。这一点记录在[环境文件](/Atlas/examples/mace-si/si-effective-fc/environment.public.json)中，复算时需要核对真正加载的包，而不只看激活了哪个环境。

```console
[talos@talos-MS-7D54 mace]$ mkdir si-effective-fc
[talos@talos-MS-7D54 mace]$ cd si-effective-fc
[talos@talos-MS-7D54 si-effective-fc]$ vi prepare.py
[talos@talos-MS-7D54 si-effective-fc]$ cat prepare.py
```

[完整的 prepare.py](/Atlas/examples/mace-si/si-effective-fc/prepare.py)是本次实际运行的输入。它依次建立参考结构、计算两种小位移幅度、重新计算映射构型的力，再运行独立初速度轨迹。建立参考的部分是：

<details>
<summary>prepare.py 的完整源码</summary>

```python
from pathlib import Path
import csv
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
import ase, scipy, phonopy, symfc
from ase import units
from ase.build import bulk
from ase.calculators.singlepoint import SinglePointCalculator
from ase.constraints import FixCom
from ase.filters import FrechetCellFilter
from ase.io import read, write
from ase.md.bussi import Bussi
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from ase.md.verlet import VelocityVerlet
from ase.optimize import BFGS
from mace.calculators import MACECalculator
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
from scipy.optimize import linear_sum_assignment

torch.set_num_threads(2)
start = time.perf_counter()
model = Path('../models/mace-mp-0-small.model')
versions = {name: metadata.version(name) for name in ['mace-torch','ase','phonopy','symfc','spglib','scipy','numpy','torch']}
paths = {mod.__name__: mod.__file__ for mod in [ase, scipy, phonopy, symfc]}
provenance = dict(versions=versions, module_paths=paths,
                  model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                  cpu_threads=2, source_trajectory_sha256=hashlib.sha256(Path('../si-md/nve-1fs.traj').read_bytes()).hexdigest())
print('ENVIRONMENT', json.dumps(provenance, indent=2), flush=True)
Path('environment.json').write_text(json.dumps(provenance, indent=2)+'\n')
calc = MACECalculator(model_paths=str(model), device='cpu', default_dtype='float64')

# Define the cubic reference explicitly. No old trajectory file is modified.
old_uc = read('../si-vc-relax/relaxed.extxyz')
old_ref = old_uc.repeat((2,2,2))
a0 = old_uc.get_volume()**(1/3)
uc = bulk('Si','diamond',a=a0,cubic=True)
uc.calc = calc
opt = BFGS(FrechetCellFilter(uc, hydrostatic_strain=True), logfile='reference-relax.log', trajectory='reference-relax.traj')
accepted = opt.run(fmax=1e-5, steps=100)
assert accepted
assert np.ptp(uc.cell.lengths()) < 1e-10
assert np.max(np.abs(uc.cell.angles()-90)) < 1e-10
write('reference-unitcell.extxyz', uc)
ase_ref = uc.repeat((2,2,2))
write('reference-supercell.extxyz', ase_ref)
ref_info = dict(a_initial_A=a0, a_final_A=float(uc.cell.lengths()[0]), steps=opt.nsteps,
                volume_A3=uc.get_volume(), fmax_eV_A=float(np.linalg.norm(uc.get_forces(),axis=1).max()),
                stress_eV_A3=uc.get_stress().tolist())
print('CUBIC_REFERENCE',json.dumps(ref_info),flush=True)
Path('reference.json').write_text(json.dumps(ref_info,indent=2)+'\n')

def new_phonon():
    cell=PhonopyAtoms(symbols=uc.get_chemical_symbols(), cell=uc.cell.array, scaled_positions=uc.get_scaled_positions())
    return Phonopy(cell, supercell_matrix=[2,2,2], primitive_matrix='F', symprec=1e-5)

ph = new_phonon()
ph_ref = ph.supercell
# Explicit atom-order mapping: phonopy's supercell order differs from ASE.repeat.
frac = ph_ref.scaled_positions[:,None,:]-ase_ref.get_scaled_positions()[None,:,:]
frac -= np.rint(frac)
cost = np.linalg.norm(frac@ase_ref.cell.array,axis=2)
rows, order = linear_sum_assignment(cost)
assert np.array_equal(rows,np.arange(64))
assert cost[rows,order].max()<1e-8
np.save('phonopy-to-ase-order.npy',order)
ph.save('reference-phonopy.yaml')
print('ATOM_ORDER max_mapping_error_A',cost[rows,order].max(),'primitive_atoms',len(ph.primitive),flush=True)

baseline={}
for amplitude in [0.01,0.005]:
    label=f'harmonic-{amplitude:g}'
    ph=new_phonon()
    ph.generate_displacements(distance=amplitude,is_plusminus=True)
    forces=[]
    displaced=[]
    for index, sc in enumerate(ph.supercells_with_displacements):
        from ase import Atoms
        atoms=Atoms(symbols=sc.symbols,cell=sc.cell,scaled_positions=sc.scaled_positions,pbc=True)
        atoms.calc=calc
        force=atoms.get_forces()
        forces.append(force)
        displaced.append(atoms.copy())
        displaced[-1].calc=SinglePointCalculator(displaced[-1],energy=atoms.get_potential_energy(),forces=force)
        print('FINITE_DISPLACEMENT',label,index+1,'fmax',float(np.linalg.norm(force,axis=1).max()),flush=True)
    ph.forces=np.array(forces)
    ph.produce_force_constants(fc_calculator='traditional')
    raw_drift=float(np.abs(ph.force_constants.sum(axis=1)).max())
    ph.symmetrize_force_constants()
    np.save(label+'-fc.npy',ph.force_constants)
    ph.save(label+'.yaml',settings={'force_constants':True})
    write(label+'-forces.traj',displaced)
    baseline[label]=dict(amplitude_A=amplitude, force_evaluations=len(forces),raw_fc_translational_drift_eV_A2=raw_drift,
                         corrected_fc_translational_drift_eV_A2=float(np.abs(ph.force_constants.sum(axis=1)).max()))
print('HARMONIC_BASELINES',json.dumps(baseline),flush=True)
Path('baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')

# Transfer only displacements from the old cell. Every mapped configuration gets new forces.
source=read('../si-md/nve-1fs.traj',':')
us=[]; fs=[]; mapped=[]; temperatures=[]
for i,frame in enumerate(source):
    delta=frame.get_scaled_positions(wrap=False)-old_ref.get_scaled_positions(wrap=False)
    delta-=np.rint(delta)
    u=delta@ase_ref.cell.array
    u-=u.mean(axis=0)
    atoms=ase_ref.copy()
    atoms.positions+=u
    atoms.calc=calc
    force=atoms.get_forces()
    us.append(u[order]); fs.append(force[order]); temperatures.append(frame.get_temperature())
    copy=atoms.copy()
    copy.calc=SinglePointCalculator(copy,energy=atoms.get_potential_energy(),forces=force)
    mapped.append(copy)
    if i%20==0: print('MAPPED_FORCE',i,'of',len(source),'max_u_A',float(np.linalg.norm(u,axis=1).max()),flush=True)
np.savez_compressed('mapped-dataset.npz',displacements=np.array(us),forces=np.array(fs),source_temperature_K=temperatures,
                    source_time_ps=np.arange(len(source))*0.005,order=order)
write('mapped-configurations.traj',mapped)
print('MAPPING_DONE snapshots',len(source),'all_forces_recomputed',True,flush=True)

# An independent velocity seed probes transfer beyond the original short trajectory.
atoms=ase_ref.copy(); atoms.set_constraint(FixCom()); atoms.calc=calc
MaxwellBoltzmannDistribution(atoms,temperature_K=300,force_temp=True,rng=np.random.default_rng(2026092202))
Stationary(atoms,preserve_temperature=True)
seed_hash=hashlib.sha256(atoms.get_momenta().tobytes()).hexdigest()
write('independent-initial.traj',atoms)
print('INDEPENDENT_START seed=2026092202 momentum_sha256',seed_hash,flush=True)
warm=Bussi(atoms,1*units.fs,temperature_K=300,taut=100*units.fs,rng=np.random.default_rng(924),
           trajectory='independent-warmup.traj',logfile='independent-warmup.log',loginterval=10)
t0=time.perf_counter(); warm.run(1000)
print('INDEPENDENT_WARMUP_DONE steps',warm.nsteps,'temperature_K',atoms.get_temperature(),'wall_s',time.perf_counter()-t0,flush=True)
write('independent-after-warmup.traj',atoms)
dyn=VelocityVerlet(atoms,1*units.fs,trajectory='independent-nve.traj',logfile='independent-nve.log',loginterval=10)
rows=[]
with open('independent-nve.csv','w',newline='') as h:
    writer=csv.writer(h); writer.writerow(['time_ps','temperature_K','potential_eV_atom','total_eV_atom'])
    def record():
        ep=atoms.get_potential_energy()/64
        row=[dyn.get_time()/(1000*units.fs),atoms.get_temperature(),ep,ep+atoms.get_kinetic_energy()/64]
        writer.writerow(row);h.flush();rows.append(row)
    dyn.attach(record,interval=10)
    t0=time.perf_counter();dyn.run(500)
series=np.array(rows)
info=dict(warmup_steps=1000,production_steps=500,timestep_fs=1,snapshots=len(rows),
          velocity_seed=2026092202,momentum_sha256=seed_hash,mean_temperature_K=float(series[:,1].mean()),
          temperature_std_K=float(series[:,1].std()),
          max_abs_delta_total_meV_atom=float(np.max(np.abs(series[:,3]-series[0,3]))*1000),
          production_wall_s=time.perf_counter()-t0,total_prepare_wall_s=time.perf_counter()-start)
Path('independent.json').write_text(json.dumps(info,indent=2)+'\n')
print('INDEPENDENT_MD_DONE',json.dumps(info,indent=2),flush=True)
print('DATA_PREPARATION_FINISHED',flush=True)
```

</details>

```python
old_uc = read('../si-vc-relax/relaxed.extxyz')
old_ref = old_uc.repeat((2,2,2))
a0 = old_uc.get_volume()**(1/3)
uc = bulk('Si','diamond',a=a0,cubic=True)
uc.calc = calc
opt = BFGS(FrechetCellFilter(uc, hydrostatic_strain=True),
           logfile='reference-relax.log', trajectory='reference-relax.traj')
accepted = opt.run(fmax=1e-5, steps=100)
```

`hydrostatic_strain=True` 把晶胞变化限制为均匀缩放，理想金刚石结构保持立方。随后 8 原子常规胞扩为 2×2×2 的 64 原子超胞。phonopy 中明确使用 F 型原胞；原胞有 2 个 Si，因此后面每个 q 点应有 6 个频率。

```console
[talos@talos-MS-7D54 si-effective-fc]$ export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
[talos@talos-MS-7D54 si-effective-fc]$ /usr/bin/time -v <MACE环境>/bin/python -u prepare.py > prepare.out 2> prepare.time; echo prepare_exit=$?
prepare_exit=0
```

本次整个准备程序的墙钟时间为 9 分 11.78 秒，峰值常驻内存约 1.14 GiB。`prepare.out` 保存程序记录，`prepare.time` 保存诊断信息及资源统计，轨迹随计算逐步写入。运行时在另一个 tmux 窗口查看文件即可。完整的[准备输出](/Atlas/examples/mace-si/si-effective-fc/prepare.out.txt)和[拟合输出](/Atlas/examples/mace-si/si-effective-fc/fit.out.txt)也可以直接下载。

```console
[talos@talos-MS-7D54 si-effective-fc]$ head -n 12 prepare.out
cuequivariance or cuequivariance_torch is not available. Cuequivariance acceleration will be disabled.
ENVIRONMENT {
  "versions": {
    "mace-torch": "0.3.16",
    "ase": "3.29.0",
    "phonopy": "4.4.0",
    "symfc": "1.7.3",
    "spglib": "2.7.0",
    "scipy": "1.18.0",
    "numpy": "2.4.6",
    "torch": "2.12.0"
  },
[talos@talos-MS-7D54 si-effective-fc]$ cat reference.json
{
  "a_initial_A": 5.464664315456402,
  "a_final_A": 5.464664315456402,
  "steps": 0,
  "volume_A3": 163.1888445820938,
  "fmax_eV_A": 5.823070155755285e-15,
  "stress_eV_A3": [
    1.3476746059391367e-07,
    1.3476746062774258e-07,
    1.347674606181336e-07,
    -3.30674418285811e-17,
    -1.0755458939616247e-17,
    -4.190839656418783e-17
  ]
}
```

日志首行说明没有启用可选的 cuequivariance 加速，本次计算明确使用 CPU；继续往下读，版本和模型校验信息仍然正常写出。参考晶格常数为 **5.464664315456402 Å**。`steps: 0` 表示初始参考已经满足所设优化阈值，优化器没有再移动原子或晶胞，并不表示遗漏了结构检查。原子最大力约 `5.8e-15 eV/Å`，三个正应力约 `1.35e-7 eV/Å³`。

## 同时保留小位移基线和热运动构型

小位移基线描述这个参考结构附近的势能曲率。脚本分别生成正负 0.01 Å、正负 0.005 Å 位移，用 MACE 计算每个构型的力，然后由 phonopy 重建二阶力常数。这个高对称 Si 超胞每个幅度只有 2 个对称不等价的位移构型；换成低对称结构后，位移数量会变化。

位移幅度决定在平衡位置附近多远处测量恢复力。幅度太大时，高阶项会混入二阶近似；幅度很小时，力的数值噪声相对于位移会被放大。因此这里保留一大一小两种幅度，并在后文直接比较频率，而不把较小幅度自动当成较准确的答案。正负位移同时计算，也有助于分开对位移方向呈奇、偶变化的力贡献。

```python
ph.generate_displacements(distance=amplitude, is_plusminus=True)
# 对 ph.supercells_with_displacements 中的每个超胞计算 MACE 原子力。
ph.forces = np.array(forces)
ph.produce_force_constants(fc_calculator='traditional')
raw_drift = float(np.abs(ph.force_constants.sum(axis=1)).max())
ph.symmetrize_force_constants()
```

这几行摘自输入，逐个构型的 `Atoms` 转换和计算器设置保留在完整文件中。`raw_drift` 先记录平移求和残差，再施加力常数对称化；这里不会把原始残差藏在后处理后面。两种幅度的原始残差分别约 `6.2e-14` 和 `1.2e-13 eV/Å²`，都已经很小。实际位移构型和力分别写在 `harmonic-0.01-forces.traj`、`harmonic-0.005-forces.traj`，力常数同时保存为 NumPy 数组和 phonopy YAML。

旧 MD 使用的晶胞与新参考略有不同，所以不能把旧位置改一下后直接沿用旧力。脚本先计算每个原子相对旧参考的分数坐标位移，按周期边界取回最近的对应位置，再把这个位移放到新立方参考中：

```python
delta = frame.get_scaled_positions(wrap=False) - old_ref.get_scaled_positions(wrap=False)
delta -= np.rint(delta)
u = delta @ ase_ref.cell.array
u -= u.mean(axis=0)
atoms = ase_ref.copy()
atoms.positions += u
atoms.calc = calc
force = atoms.get_forces()
```

最后一行重新调用 MACE 求力。101 帧全部执行了这一步。去掉 `u` 的平均值用于移除整体平移；这不改变原子间相对位移。脚本另外检查 ASE 与 phonopy 的原子排序，用明确的置换把位移和力一起重排；两者不能只重排其中一个。本次排序匹配的最大位置差为 0，映射保存在 `phonopy-to-ase-order.npy`。

映射后的构型、力保存在 `mapped-configurations.traj` 与 `mapped-dataset.npz`。NPZ 中 `displacements` 和 `forces` 都是 `(101, 64, 3)` 数组，单位分别为 Å 和 eV/Å；`source_time_ps` 和 `source_temperature_K` 描述原始轨迹。映射后的构型集合不能自动视作新晶胞中充分平衡的正则系综，原轨迹温度也只是它们的来源信息。

## 用另一组初速度检查能否预测新轨迹

独立验证重新从理想立方参考开始，使用速度种子 `2026092202`。先与 300 K 的 Bussi 热浴接触 1 ps，再关闭温控器，采用 1 fs 时间步长运行 0.5 ps NVE，每 10 fs 保存一帧，共 51 帧。它没有从旧轨迹末帧接着运行。

```console
[talos@talos-MS-7D54 si-effective-fc]$ watch -n 5 'tail -n 4 independent-warmup.log'
```

窗口会持续显示已经写入的 MD 日志，按 `Ctrl+C` 返回命令行。预热结束后继续看 `independent-nve.log`；其中一行对应一个输出时刻，依次是时间、总能量、势能、动能和瞬时温度。这里的能量是 64 原子超胞总量。

```console
[talos@talos-MS-7D54 si-effective-fc]$ head -n 6 independent-nve.log
Time[ps]      Etot[eV]     Epot[eV]     Ekin[eV]    T[K]
0.0000        -338.5123    -341.8403       3.3280   408.7
0.0100        -338.5125    -341.8148       3.3023   405.5
0.0200        -338.5119    -340.9806       2.4686   303.1
0.0300        -338.5114    -340.1817       1.6703   205.1
0.0400        -338.5116    -340.2321       1.7206   211.3
[talos@talos-MS-7D54 si-effective-fc]$ tail -n 4 independent-nve.log
0.4700        -338.5118    -340.7058       2.1940   269.4
0.4800        -338.5121    -341.1789       2.6667   327.5
0.4900        -338.5122    -341.4887       2.9765   365.5
0.5000        -338.5121    -341.4939       2.9818   366.2
```

势能和动能随原子振动相互转换，温度也会明显起伏。总能量在同一小范围内变化；程序按每原子能量进一步核对，记录点中的最大漂移为 **0.0148847 meV/atom**。这验证的是这段短 NVE 的积分表现。

```console
[talos@talos-MS-7D54 si-effective-fc]$ tail -n 17 prepare.out
MAPPING_DONE snapshots 101 all_forces_recomputed True
INDEPENDENT_START seed=2026092202 momentum_sha256 8d77daace18335b69edb8611fa3dd19da02c7ad3003307cfede492a46ac91c14
INDEPENDENT_WARMUP_DONE steps 1000 temperature_K 408.67462446295895 wall_s 341.06818941328675
INDEPENDENT_MD_DONE {
  "warmup_steps": 1000,
  "production_steps": 500,
  "timestep_fs": 1,
  "snapshots": 51,
  "velocity_seed": 2026092202,
  "momentum_sha256": "8d77daace18335b69edb8611fa3dd19da02c7ad3003307cfede492a46ac91c14",
  "mean_temperature_K": 322.4618765415747,
  "temperature_std_K": 42.461517079713495,
  "max_abs_delta_total_meV_atom": 0.01488466970211988,
  "production_wall_s": 169.9470366705209,
  "total_prepare_wall_s": 547.166096650064
}
DATA_PREPARATION_FINISHED
```

`INDEPENDENT_WARMUP_DONE` 后的 408.675 K 是预热末帧温度；生产段平均值是 **322.462 K**，标准差约 **42.462 K**。300 K 是热浴设定值，不能把这一短轨迹的所有帧都标成 300 K 平衡样本。程序末尾同时给出步数、帧数、速度种子和动量校验值，核验脚本还会直接比较新旧初始速度，确认这次验证有独立起点。

## 拟合时给后来的一段轨迹留位置

[fit.py](/Atlas/examples/mace-si/si-effective-fc/fit.py)读取已经得到的力，不再运行 MACE。源轨迹共有 101 帧，间隔 5 fs。三次拟合分别使用编号 1–20、1–40、1–60 的连续帧，对应 0.005–0.100、0.005–0.200、0.005–0.300 ps。编号 80–100 的 21 帧，即 0.400–0.500 ps，始终留作同轨迹的后段验证。

这里保留了训练段与后段之间的时间间隔，但没有测定自相关时间，不能把相邻帧当成完全独立样本。前面的 51 帧新种子轨迹另外作为独立起点的验证集，也不参与拟合。60 帧训练段的原轨迹平均温度为 **333.039 K**，后段为 **329.561 K**；新种子验证段为 **322.462 K**。这些数据实际覆盖的时间与温度都写在 `fit-summary.json` 中。

```python
ph.dataset = {
    'displacements': np.array(u[train], order='C'),
    'forces': np.array(f[train], order='C'),
}
ph.produce_force_constants(
    fc_calculator='symfc', calculate_full_force_constants=True,
    fc_calculator_log_level=1,
)
fc = ph.force_constants
prediction = -np.einsum('ijab,sjb->sia', fc, positions, optimize=True)
```

symfc 使用参考晶体的对称性与力常数约束来拟合 `Φ`。最后一行把所得力常数乘回验证位移，得到预测力。报告中的 RMSE 是所有帧、所有原子和三个笛卡尔力分量的均方根误差；这使训练、后段验证和独立验证可以用相同定义比较。

`calculate_full_force_constants=True` 选择完整原子对矩阵的存储布局，不是把拟合阶数提高了。当前模型仍只包含对位移线性的恢复力；将训练帧数从 20 增至 60，改变的是这些系数的拟合数据。即使增加数据，二阶表达式本身仍可能不能准确描述热运动中较大的位移，所以后面必须同时读取验证力误差与频率变化。


拟合需要成对的位移与力、统一参考结构以及未参加拟合的验证数据。下面列出数据准备和结果检查的具体要求。

```text
编写 fit.py，用 reference-unitcell.extxyz、reference-supercell.extxyz、phonopy-to-ase-order.npy、mapped-dataset.npz 及 independent-nve.traj 建立有限温度有效二阶力常数。位移为 Å、力为 eV/Å，预测力为 -Φu；按周期最小像处理位移并减去整体平移，再按保存映射排序。原数据 101×64×3，独立轨迹 51×64×3；训练索引依次 1–20、1–40、1–60，后段 80–100 与独立轨迹始终不拟合。用 symfc 拟合完整 (64,64,3,3) 力常数，与两种简谐位移基线比较。保存 NPY/YAML、Γ—X—W—K—Γ—L 色散 CSV（THz）、学习曲线、三组力预测误差及真实平均温度到 fit-summary.json。保留负频，比较 40/60 帧色散差；这段程序不执行 SSCHA 自由能变分。
```

下面是算例实际使用的完整源码。

<details>
<summary>fit.py 完整源码</summary>

```python
from pathlib import Path
import csv
import hashlib
import json
import time
import numpy as np
from ase.io import read
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms

start=time.perf_counter()
uc=read('reference-unitcell.extxyz')
ref=read('reference-supercell.extxyz')
order=np.load('phonopy-to-ase-order.npy')
data=np.load('mapped-dataset.npz')
u=data['displacements']; f=data['forces']
assert u.shape==f.shape==(101,64,3)
assert np.isfinite(u).all() and np.isfinite(f).all()
assert np.max(np.abs(u.mean(axis=1)))<1e-12
assert Path('independent.json').exists(), 'Wait for independent MD to finish.'
frames=read('independent-nve.traj',':')
ui=[];fi=[];temps=[]
for frame in frames:
    d=frame.get_scaled_positions(wrap=False)-ref.get_scaled_positions(wrap=False)
    d-=np.rint(d)
    cart=d@ref.cell.array
    cart-=cart.mean(axis=0)
    ui.append(cart[order]);fi.append(frame.calc.results['forces'][order]);temps.append(frame.get_temperature())
ui=np.array(ui);fi=np.array(fi)
assert ui.shape==fi.shape==(51,64,3)
assert np.isfinite(ui).all() and np.isfinite(fi).all()
np.savez_compressed('independent-dataset.npz',displacements=ui,forces=fi,temperature_K=temps,time_ps=np.arange(len(frames))*.01)

vertices=np.array([[0,0,0],[.5,0,.5],[.5,.25,.75],[.375,.375,.75],[0,0,0],[.5,.5,.5]])
labels=['Gamma','X','W','K','Gamma','L']
paths=[np.linspace(a,b,51) for a,b in zip(vertices[:-1],vertices[1:])]

def new_phonon():
    cell=PhonopyAtoms(symbols=uc.get_chemical_symbols(),cell=uc.cell.array,scaled_positions=uc.get_scaled_positions())
    return Phonopy(cell,supercell_matrix=[2,2,2],primitive_matrix='F',symprec=1e-5)

def dispersion(ph,label):
    ph.run_band_structure(paths)
    bs=ph.band_structure
    with open(label+'-bands.csv','w',newline='') as h:
        w=csv.writer(h);w.writerow(['segment','distance_inv_A','q1','q2','q3']+[f'frequency_{i+1}_THz' for i in range(6)])
        for seg,(q,d,freq) in enumerate(zip(bs.qpoints,bs.distances,bs.frequencies)):
            for qi,di,fi in zip(q,d,freq):w.writerow([seg,di,*qi,*fi])
    ph.run_qpoints([[0,0,0]])
    gamma=ph.qpoints.frequencies[0].tolist()
    allfreq=np.concatenate(bs.frequencies)
    assert np.isfinite(allfreq).all()
    return dict(min_path_THz=float(allfreq.min()),max_path_THz=float(allfreq.max()),gamma_THz=gamma,
                boundaries_inv_A=[float(bs.distances[0][0])]+[float(d[-1]) for d in bs.distances]),allfreq

def errors(fc,positions,forces):
    prediction=-np.einsum('ijab,sjb->sia',fc,positions,optimize=True)
    residual=prediction-forces
    rmse=float(np.sqrt(np.mean(residual**2)))
    force_rms=float(np.sqrt(np.mean(forces**2)))
    return dict(snapshots=len(positions),rmse_meV_A=1000*rmse,force_rms_meV_A=1000*force_rms,
                relative_rmse=rmse/force_rms,max_abs_error_meV_A=1000*float(np.abs(residual).max()),
                r2=1-float(np.sum(residual**2)/np.sum((forces-forces.mean())**2))),prediction

baseline={}; allfreq={}
for label in ['harmonic-0.01','harmonic-0.005']:
    ph=new_phonon();ph.force_constants=np.load(label+'-fc.npy')
    stats,freq=dispersion(ph,label);allfreq[label]=freq
    ev,_=errors(ph.force_constants,ui,fi)
    stats['independent_force_error']=ev
    baseline[label]=stats
    print('BASELINE',label,json.dumps(stats),flush=True)
baseline_difference=float(np.max(np.abs(allfreq['harmonic-0.01']-allfreq['harmonic-0.005'])))
print('AMPLITUDE_COMPARISON max_abs_frequency_difference_THz',baseline_difference,flush=True)

results=[]
for ntrain in [20,40,60]:
    train=np.arange(1,ntrain+1)
    held=np.arange(80,101)
    ph=new_phonon()
    ph.dataset={'displacements':np.array(u[train],order='C'),'forces':np.array(f[train],order='C')}
    print('FIT_START ntrain',ntrain,'training_time_ps',[float(data['source_time_ps'][train[0]]),float(data['source_time_ps'][train[-1]])],flush=True)
    t0=time.perf_counter()
    ph.produce_force_constants(fc_calculator='symfc',calculate_full_force_constants=True,fc_calculator_log_level=1)
    fc=ph.force_constants
    assert fc.shape==(64,64,3,3) and np.isfinite(fc).all()
    label=f'effective-{ntrain}'
    np.save(label+'-fc.npy',fc)
    ph.save(label+'.yaml',settings={'force_constants':True})
    fit_seconds=time.perf_counter()-t0
    train_error,_=errors(fc,u[train],f[train])
    block_error,_=errors(fc,u[held],f[held])
    independent_error,pred=errors(fc,ui,fi)
    bands,freq=dispersion(ph,label)
    out=dict(training_snapshots=ntrain,training_source_indices=train.tolist(),heldout_source_indices=held.tolist(),
             source_training_temperature_K=float(data['source_temperature_K'][train].mean()),
             source_heldout_temperature_K=float(data['source_temperature_K'][held].mean()),
             independent_temperature_K=float(np.mean(temps)),fit_wall_s=fit_seconds,
             train=train_error,heldout_block=block_error,independent=independent_error,bands=bands,
             translational_drift_eV_A2=float(np.abs(fc.sum(axis=1)).max()),
             permutation_difference_eV_A2=float(np.max(np.abs(fc-fc.transpose(1,0,3,2)))))
    results.append(out);allfreq[label]=freq
    np.save(label+'-independent-prediction.npy',pred)
    print('FIT_RESULT',json.dumps(out,indent=2),flush=True)

summary=dict(reference=json.loads(Path('reference.json').read_text()),
             baseline=baseline,baseline_amplitude_max_frequency_difference_THz=baseline_difference,
             fits=results,band_labels=labels,band_vertices_fractional=vertices.tolist(),
             independent=json.loads(Path('independent.json').read_text()),
             effective_40_vs_60_max_path_difference_THz=float(np.max(np.abs(allfreq['effective-40']-allfreq['effective-60']))),
             total_fit_script_wall_s=time.perf_counter()-start,
             interpretation='Finite-temperature effective second-order force-constant fitting demonstration; not a temperature-converged phonon renormalization or SSCHA calculation.')
Path('fit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with open('learning-curve.csv','w',newline='') as h:
    w=csv.writer(h);w.writerow(['training_snapshots','train_RMSE_meV_A','heldout_block_RMSE_meV_A','independent_RMSE_meV_A'])
    for r in results:w.writerow([r['training_snapshots'],r['train']['rmse_meV_A'],r['heldout_block']['rmse_meV_A'],r['independent']['rmse_meV_A']])
print('EFFECTIVE_40_VS_60_MAX_PATH_DIFFERENCE_THz',summary['effective_40_vs_60_max_path_difference_THz'],flush=True)
print('FIT_PIPELINE_FINISHED wall_s',time.perf_counter()-start,flush=True)
```

</details>

```console
[talos@talos-MS-7D54 si-effective-fc]$ vi fit.py
[talos@talos-MS-7D54 si-effective-fc]$ head -25 fit.py
[talos@talos-MS-7D54 si-effective-fc]$ /usr/bin/time -v <MACE环境>/bin/python -u fit.py > fit.out 2> fit.time; echo fit_exit=$?
fit_exit=0
[talos@talos-MS-7D54 si-effective-fc]$ grep -A 6 'FIT_START ntrain 20' fit.out
FIT_START ntrain 20 training_time_ps [0.005, 0.1]
-------------------------------- Symfc start -------------------------------
Symfc version 1.7.3 (https://github.com/symfc/symfc)
Citation: A. Seko and A. Togo, Phys. Rev. B, 110, 214302 (2024)
Computing [2] order force constants.
Increase log-level to watch detailed symfc log.
--------------------------------- Symfc end --------------------------------
[talos@talos-MS-7D54 si-effective-fc]$ cat learning-curve.csv
training_snapshots,train_RMSE_meV_A,heldout_block_RMSE_meV_A,independent_RMSE_meV_A
20,92.72588650442586,86.62868149875958,77.09242204712771
40,87.96706190084986,86.10940691973528,77.19010954980308
60,83.98692651911895,85.97194072830276,76.89831035078684
```

`Computing [2] order force constants` 表示这里只拟合二阶力常数；日志没有在计算三阶散射、寿命或自由能 Hessian。三次拟合与后续色散导出合计用时约 1.45 秒。训练误差从 92.73 降至 83.99 meV/Å，同轨迹后段从 86.63 降至 85.97 meV/Å。独立轨迹误差在 77 meV/Å 左右，20→40 帧时还略有上升，增加样本没有产生单调改善。

60 帧模型的独立误差为 **76.90 meV/Å**，相对于这段验证力分量的 RMS 为 **16.13%**，最大单分量误差约 **0.781 eV/Å**。0.005 Å 小位移基线在同一独立数据上的 RMSE 为 **82.32 meV/Å**。这说明有限温度拟合在这份验证数据上的整体误差有所减小，但最大误差仍值得保留查看。这里比较的是二阶模型对 MACE 原子力的近似程度，尚未做 MACE 与 DFT 的力对照。

## 看色散，也看换一批样本时色散怎样变化

同一组二阶力常数写入 phonopy 后，沿 `Γ—X—W—K—Γ—L` 路径求频率。路径分数坐标相对于 F 型原胞倒格矢，在 `fit-summary.json` 中完整保存。每段含 51 个 q 点、每点 6 支频率，CSV 一共有 255 行数值。

```console
[talos@talos-MS-7D54 si-effective-fc]$ head -n 4 effective-60-bands.csv
segment,distance_inv_A,q1,q2,q3,frequency_1_THz,frequency_2_THz,frequency_3_THz,frequency_4_THz,frequency_5_THz,frequency_6_THz
0,0.0,0.0,0.0,0.0,-1.6573891556325794e-07,9.430686606104846e-08,1.5821163659874482e-07,11.910694433538477,11.910694433538481,11.910694433538483
0,0.003659877138918024,0.01,0.0,0.01,0.13274382119700026,0.1327438211970908,0.22197645411589487,11.910060451541211,11.91025748264103,11.91025748264103
0,0.007319754277836048,0.02,0.0,0.02,0.26536556630029917,0.2653655663004601,0.44386590230708867,11.9081556303742,11.908943845952427,11.908943845952429
```

`segment` 记录路径段，`distance_inv_A` 是沿路径累计的倒空间距离，随后三个数是原胞倒空间分数坐标，最后六列是 THz 单位的频率。相邻路径段的端点各保存一次；绘图脚本按 `segment` 画线，避免把不同段错误连接。

Γ 点的三支声学频率在约 `±2e-7 THz` 的数值范围内，另外三支为约 `11.9107 THz`。这里保留输出中的微小负号，没有为了让图好看而把负数取绝对值。结合接近机器精度的平移求和残差，这三支对应应当为零的平移模；这项判断不适用于任意幅度的负频率。

[plot.py](/Atlas/examples/mace-si/si-effective-fc/plot.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/mace-si/si-effective-fc/atlas_plot_style.py)）只依赖 NumPy 与 Matplotlib，读取本目录的 CSV、JSON、NPZ 和预测力数组。把[数据包](/Atlas/examples/mace-si/si-effective-fc/public-bundle.tar.gz)中、[清单](/Atlas/examples/mace-si/si-effective-fc/public-files.json)列出的文件放在同一目录后，可在本机执行：

色散来自 `harmonic-0.005-bands.csv`、`harmonic-0.01-bands.csv`、`effective-40-bands.csv` 和 `effective-60-bands.csv`。曲线本身使用 THz，差值图把两组对应频率相减后乘 1000，才变成 GHz；这一步不会重新拟合力常数。`fit-summary.json` 提供高对称点的位置，不能用等间隔刻度代替真实路径长度。


绘图时把不同样本数的结果放在同一路径上比较，保留负频率和各分支的拟合设置。

```text
编写 plot.py，从本目录 CSV、fit-summary.json、independent-dataset.npz 和预测力 NPY 出图。用 summary 中的路径边界，频率保持 THz，叠画简谐与有效二阶色散；并列比较训练、后段与独立轨迹的力 RMSE，画预测力对照和 40/60 帧色散变化。只读取已保存数据，使用 NumPy、Matplotlib 与 atlas_plot_style.py，不加载 MACE。保留所有负频和真实采样温度。
```

下面是算例实际使用的完整源码。

<details>
<summary>plot.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

# Run beside the CSV/JSON/NPZ outputs. No MACE, ASE or phonopy import is needed.
root=Path(__file__).resolve().parent
summary=json.loads((root/'fit-summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'svg.fonttype':'none','savefig.dpi':200})
colors={'harmonic':'#5d626a','effective':'#0072b2','small':'#e69f00','validation':'#009e73'}
def bands(name): return np.genfromtxt(root/(name+'-bands.csv'),delimiter=',',skip_header=1)
def decorate(ax):
    ticks=summary['fits'][-1]['bands']['boundaries_inv_A']
    for x in ticks:ax.axvline(x,color='#dddddd',lw=.6,zorder=0)
    ax.axhline(0,color='#bbbbbb',lw=.7,zorder=0)
    ax.set_xticks(ticks,['Γ','X','W','K','Γ','L'])
    ax.set_xlim(ticks[0],ticks[-1])
    ax.set_xlabel('Wave-vector path')
base=bands('harmonic-0.005'); other=bands('harmonic-0.01'); fit=bands('effective-60')
fig,axes=plt.subplots(1,2,figsize=(10.4,4),layout='constrained')
for seg in range(5):
    rows=base[:,0]==seg
    for branch in range(5,11):
        axes[0].plot(base[rows,1],1000*(other[rows,branch]-base[rows,branch]),color=colors['harmonic'],lw=1)
        axes[1].plot(base[rows,1],base[rows,branch],color=colors['harmonic'],lw=1.1,ls='--')
        axes[1].plot(fit[rows,1],fit[rows,branch],color=colors['effective'],lw=1.15)
for ax in axes:decorate(ax)
axes[0].set_title('Small-displacement amplitude check')
axes[0].set_ylabel('Frequency difference (GHz)')
axes[1].set_title('One finite-temperature fitting demonstration')
axes[1].set_ylabel('Frequency [THz]')
axes[1].plot([],[],color=colors['harmonic'],ls='--',label='Small displacement: 0.005 Å')
axes[1].plot([],[],color=colors['effective'],label='Effective FCs: 60 training frames')
axes[1].legend(frameon=False,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.18))
fig.savefig(root/'effective-phonons.svg');fig.savefig(root/'effective-phonons.png');plt.close(fig)

fig,axes=plt.subplots(2,2,figsize=(10.4,7.2),layout='constrained')
learning=np.genfromtxt(root/'learning-curve.csv',delimiter=',',names=True)
for field,label,color in [('train_RMSE_meV_A','Training block',colors['harmonic']),
                         ('heldout_block_RMSE_meV_A','Held-out later block',colors['small']),
                         ('independent_RMSE_meV_A','Independent velocity seed',colors['validation'])]:
    axes[0,0].plot(learning['training_snapshots'],learning[field],'-o',label=label,color=color,ms=4)
axes[0,0].set(xlabel='Training snapshots',ylabel='Force RMSE [meV/Å]',title='Sample-count comparison')
axes[0,0].set_xticks([20,40,60]);axes[0,0].legend(frameon=False,fontsize=8)
ind=np.load(root/'independent-dataset.npz')
pred=np.load(root/'effective-60-independent-prediction.npy')
true=ind['forces'].reshape(-1);estimate=pred.reshape(-1)
lo=min(true.min(),estimate.min());hi=max(true.max(),estimate.max())
axes[0,1].scatter(true,estimate,s=3,alpha=.22,color=colors['effective'],rasterized=True)
axes[0,1].plot([lo,hi],[lo,hi],color='#333333',lw=.8)
axes[0,1].set(xlabel='MACE force component [eV/Å]',ylabel='Effective-model force [eV/Å]',title='Independent trajectory, 60-frame fit')
axes[0,1].text(.04,.94,f"RMSE = {summary['fits'][-1]['independent']['rmse_meV_A']:.2f} meV/Å",transform=axes[0,1].transAxes,va='top')
source=np.load(root/'mapped-dataset.npz')
axes[1,0].plot(source['source_time_ps'],source['source_temperature_K'],color=colors['harmonic'],lw=1,label='Source trajectory')
axes[1,0].plot(ind['time_ps'],ind['temperature_K'],color=colors['validation'],lw=1,label='Independent trajectory')
axes[1,0].axvspan(.005,.300,color=colors['effective'],alpha=.09,label='60-frame training interval')
axes[1,0].axvspan(.400,.500,color=colors['small'],alpha=.12,label='Held-out source interval')
axes[1,0].set(xlabel='Production time [ps]',ylabel='Instantaneous temperature [K]',title='Actual short-trajectory temperatures')
axes[1,0].legend(frameon=False,fontsize=7,loc='best')
short=bands('effective-40')
for seg in range(5):
    rows=fit[:,0]==seg
    for branch in range(5,11):axes[1,1].plot(fit[rows,1],1000*(fit[rows,branch]-short[rows,branch]),color=colors['effective'],lw=1)
decorate(axes[1,1]);axes[1,1].set_title('Sensitivity to 40 versus 60 training frames')
axes[1,1].set_ylabel('Frequency(60) − frequency(40) [GHz]')
fig.savefig(root/'fit-validation.svg');fig.savefig(root/'fit-validation.png');plt.close(fig)
print('Created effective-phonons.svg/png and fit-validation.svg/png')
```

</details>

```bash
python3 plot.py
```

该命令生成两组 SVG 与 PNG。第一组将两个小位移幅度的频率差单独画出，再比较小位移基线与 60 帧有效力常数的色散。

![小位移幅度检查与有限温度有效二阶力常数色散](/Atlas/examples/mace-si/si-effective-fc/effective-phonons.svg)

0.01 Å 与 0.005 Å 两个基线沿路径的最大频率差为 **0.001122 THz**，约 1.122 GHz。这是小位移幅度的一项检查，超胞尺寸和模型误差仍需另外处理。Γ 点光学频率从小位移基线的约 11.4631 THz 变为这次有效模型的约 11.9107 THz；两条曲线的差别属于本次参考与采样协议下的拟合结果，不能直接作为收敛的热致频移引用。

![样本数量、独立预测力、实际轨迹温度与色散敏感性](/Atlas/examples/mace-si/si-effective-fc/fit-validation.svg)

第二组把误差曲线、独立轨迹的预测力、两段轨迹实际温度和 40→60 帧的色散变化放在一起。虽然独立力 RMSE 的变化已经很小，40 帧与 60 帧模型沿路径的最大频率差仍有 **0.214015 THz**。因此“力误差曲线看起来平了”不足以说明声子已经不再依赖样本。

误差随样本数的曲线直接读取 `learning-curve.csv`，三列分别对应训练段、同轨迹后段与独立速度种子，不能合并成一条“测试误差”。力散点使用 `independent-dataset.npz` 中的 MACE 力，以及 `effective-60-independent-prediction.npy` 中二阶模型的预测力；两者按同一帧、原子和分量排列。它比较的是二阶模型与 MACE，图轴不能改写成 DFT 力。

## 把导出的文件重新读回来

[verify.py](/Atlas/examples/mace-si/si-effective-fc/verify.py)单独读取轨迹、位移—力数组和保存的力常数，用普通矩阵乘法重新计算独立误差，再从 YAML 重建 phonopy 对象。读取时明确指定 `is_compact_fc=False`，获得完整的 `(64, 64, 3, 3)` 力常数；默认压缩布局只保留原胞代表原子的行，形状会是 `(2, 64, 3, 3)`，两种布局不能直接按相同数组比较。


回读文件的检查可按下面的说明实现：

```text
编写 verify.py，回读 fit-summary.json、environment.json、映射、NPZ、轨迹和 YAML。核对源轨迹与模型哈希、原子映射为 0–63 的排列、保存力与轨迹一致以及独立轨迹初速度不同。用普通矩阵乘法 -Φu 重算独立力误差；读取 YAML 指定 is_compact_fc=False，比较完整 (64,64,3,3) 数组，重新计算 Γ 点频率。将差异与已有摘要对照，写 verification.json 并打印实际检查结果，不运行新的力计算。
```

下面是算例实际使用的完整源码。

<details>
<summary>verify.py 完整源码</summary>

```python
from pathlib import Path
import ast
import hashlib
import json
import numpy as np
from ase.io import read
import phonopy

summary=json.loads(Path('fit-summary.json').read_text())
environment=json.loads(Path('environment.json').read_text())
source_hash=hashlib.sha256(Path('../si-md/nve-1fs.traj').read_bytes()).hexdigest()
assert source_hash==environment['source_trajectory_sha256']
assert hashlib.sha256(Path('../models/mace-mp-0-small.model').read_bytes()).hexdigest()==environment['model_sha256']
order=np.load('phonopy-to-ase-order.npy')
assert sorted(order.tolist())==list(range(64))
mapped=np.load('mapped-dataset.npz')
frames=read('mapped-configurations.traj',':')
assert len(frames)==101
saved_forces=np.array([a.calc.results['forces'][order] for a in frames])
force_difference=float(np.max(np.abs(saved_forces-mapped['forces'])))
assert force_difference<1e-12

new=read('independent-initial.traj');old=read('../si-md/initial.traj')
assert not np.array_equal(new.get_momenta(),old.get_momenta())
ind=np.load('independent-dataset.npz')
assert len(read('independent-nve.traj',':'))==51
fc=np.load('effective-60-fc.npy')
matrix=fc.transpose(0,2,1,3).reshape(192,192)
prediction=-(ind['displacements'].reshape(-1,192)@matrix.T).reshape(-1,64,3)
saved=np.load('effective-60-independent-prediction.npy')
prediction_difference=float(np.max(np.abs(prediction-saved)))
assert prediction_difference<1e-12
rmse=float(np.sqrt(np.mean((prediction-ind['forces'])**2))*1000)
assert abs(rmse-summary['fits'][-1]['independent']['rmse_meV_A'])<1e-10
for fit in summary['fits']:
    assert set(fit['training_source_indices']).isdisjoint(fit['heldout_source_indices'])
for name in ['harmonic-0.01','harmonic-0.005','effective-20','effective-40','effective-60']:
    table=np.genfromtxt(name+'-bands.csv',delimiter=',',skip_header=1)
    assert table.shape==(255,11) and np.isfinite(table).all()
ph=phonopy.load('effective-60.yaml', is_compact_fc=False, symmetrize_fc=False)
yaml_fc_difference=float(np.max(np.abs(ph.force_constants-fc)))
assert yaml_fc_difference<1e-10
ph.run_qpoints([[0,0,0]])
gamma_difference=float(np.max(np.abs(ph.qpoints.frequencies[0]-np.array(summary['fits'][-1]['bands']['gamma_THz']))))
assert gamma_difference<1e-5
for name in ['prepare.py','fit.py','plot.py','verify.py']:
    ast.parse(Path(name).read_text())
result=dict(source_trajectory_unchanged=True,independent_initial_velocities=True,mapped_frames=101,independent_frames=51,
            saved_force_max_difference_eV_A=force_difference,independent_prediction_max_difference_eV_A=prediction_difference,
            independently_recomputed_RMSE_meV_A=rmse,yaml_force_constant_max_difference_eV_A2=yaml_fc_difference,
            gamma_reload_max_difference_THz=gamma_difference,all_dispersion_rows_finite=True)
Path('verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
print('DATA_AND_EXPORT_CHECKS_FINISHED')
```

</details>

```console
[talos@talos-MS-7D54 si-effective-fc]$ <MACE环境>/bin/python verify.py > verification.out 2>&1; echo verification_exit=$?
verification_exit=0
[talos@talos-MS-7D54 si-effective-fc]$ cat verification.out
{
  "source_trajectory_unchanged": true,
  "independent_initial_velocities": true,
  "mapped_frames": 101,
  "independent_frames": 51,
  "saved_force_max_difference_eV_A": 0.0,
  "independent_prediction_max_difference_eV_A": 0.0,
  "independently_recomputed_RMSE_meV_A": 76.89831035078684,
  "yaml_force_constant_max_difference_eV_A2": 4.679416576447437e-16,
  "gamma_reload_max_difference_THz": 3.754156711138878e-07,
  "all_dispersion_rows_finite": true
}
DATA_AND_EXPORT_CHECKS_FINISHED
```

原轨迹的 SHA256 未变；保存的构型原子力与拟合数据完全相同；从力常数独立重算得到同一个 RMSE；YAML 读回的力常数与原数组最大差约 `4.7e-16 eV/Å²`。Γ 点重算差约 `3.8e-7 THz`，出现在接近零的声学模数值范围内。这些检查证明文件链条能够回读，不能替代采样长度、超胞和温度的收敛检查。

接下来若继续研究温度效应，应在同一明确晶胞协议下延长平衡与生产段、增加独立种子，检查分块误差和频率是否随数据量稳定，再比较多个温度。固定这一个体积的计算没有包含热膨胀；经典 MD 也没有包含核量子统计。本次 0.5 ps 轨迹和 64 原子超胞尚不足以完成这些检查。

## 温度稳定化需要什么材料证据

[Chen、Zhang 与 Zheng 的 CoTe₂ 原文](https://doi.org/10.1103/l89c-t2s4) Fig. 1(d) 先展示沿不稳定本征位移的势能面，Fig. 1(e) 再比较简谐与 100、200、300 K 的 SSCHA 自由能 Hessian 频率。原文 Computational details 使用为该材料构型训练并核对 DFT 能量、力和压力的深度势，辅助 SSCHA 采样与自由能优化。这个例子说明“有一个势模型”和“温度下接受了稳定性结论”之间需要实际的材料数据。

本例 Si 的 60 帧二阶模型在独立轨迹上的力 RMSE 约为 76.90 meV/Å，40→60 帧仍有 0.214015 THz 的最大频率变化。它适合练习位移—力数组、参考结构映射、独立轨迹与色散敏感性，尚不能确定温度稳定化。更不能将它用作异质结 K 点软模的修正，或将拟合频率直接与旧 EPC 矩阵元拼接计算 Tc。

对研究体系，首先沿[虚频诊断](/Atlas/m/imaginary-phonon/qe/)核查稳定性，保留相同结构、完整动力学矩阵与本征位移。需要有限温度路线时，再决定采用经典热采样的有效力常数，还是包含核量子统计的 SSCHA；对应的力模型必须覆盖本体系和所研究应变、温度附近的构型，并以 DFT 力和目标软模核对。固定体积计算不含热膨胀，经典 MD 不含核量子统计，结论应依其实际采样和频率定义表述。

## 参考资料

参考：

- [MACE：ASE calculator](https://mace-docs.readthedocs.io/en/latest/guide/ase.html)
- [Phonopy：Python API、力常数与色散](https://phonopy.github.io/phonopy/phonopy-module.html)
- [symfc：位移—力数据与对称化力常数](https://symfc.github.io/symfc/)
- [hiPhive：从 MD 轨迹建立有效谐模型](https://hiphive.materialsmodeling.org/advanced_topics/effective_harmonic_models.html)
