参考：

- [MACE：预训练模型与分子动力学](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html)
- [ASE：分子动力学、日志与时间步长](https://docs.ase-lib.org/ase/md.html)
- [ASE：轨迹文件](https://docs.ase-lib.org/ase/io/trajectory.html)
- [MACE-MP-0 官方模型](https://github.com/ACEsuit/mace-foundations/releases/tag/mace_mp_0)

## 给 64 个 Si 原子加上温度，再检查能量能否守住

这一页接着[可变晶胞优化](/Atlas/m/vc-relax/mace/)的结果往下走。把已经检查过原子力和应力的 8 原子晶胞扩成 2×2×2 超胞，先与 300 K 热浴接触 1 ps，再关掉温控器，用 NVE 积分运行 0.5 ps。最后回到同一帧，把时间步长减半，再走相同的物理时间。

这样可以分别看三个变化：初始速度产生的温度、热浴交换能量时的波动，以及离开热浴之后的能量守恒。这里每一步的力来自固定的 MACE 模型，属于机器学习势分子动力学。运行过程没有调用 DFT 求解器，因此不能把这份轨迹标成 AIMD。

### 从结构文件接上动力学

目录沿用前两篇，模型位于 `../models/mace-mp-0-small.model`，结构位于 `../si-vc-relax/relaxed.extxyz`。模型 SHA256 为 `2ddb079cee0e131eaaf6912ba581b394551ead283e95c99cfe78c605d10b5736`，与官方发布文件逐字节一致。

`FixCom()` 固定整体质心运动，所以 64 原子系统这里有 3×64−3=189 个自由度。初始速度使用固定随机种子并调整到 300 K；这只定义起点的动能，不意味着势能和动能已经达到平衡。

输入保存在 `md.py`。`Bussi` 部分提供 300 K 热浴，耦合时间为 100 fs；`VelocityVerlet` 部分没有热浴。两段 NVE 都重新读 `equilibrated.traj`，从同一组位置、速度和晶胞出发，才可以比较步长的影响。

```python
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ cat md.py
from pathlib import Path
import csv
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
from ase import units
from ase.constraints import FixCom
from ase.io import read, write
from ase.md.bussi import Bussi
from ase.md.verlet import VelocityVerlet
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from mace.calculators import MACECalculator

torch.set_num_threads(2)
model = Path("../models/mace-mp-0-small.model")
print("MACE", metadata.version("mace-torch"), "ASE", metadata.version("ase"))
print("model_sha256", hashlib.sha256(model.read_bytes()).hexdigest())
calc = MACECalculator(model_paths=str(model), device="cpu", default_dtype="float64")

# Use the accepted variable-cell minimum and make a 64-atom supercell.
assert json.loads(Path("../si-vc-relax/result.json").read_text())["converged"]
atoms = read("../si-vc-relax/relaxed.extxyz").repeat((2, 2, 2))
atoms.set_constraint(FixCom())
atoms.calc = calc
MaxwellBoltzmannDistribution(atoms, temperature_K=300.0, force_temp=True,
                            rng=np.random.default_rng(20260922))
Stationary(atoms, preserve_temperature=True)
write("initial.traj", atoms)
print(f"INITIAL atoms={len(atoms)} DOF={atoms.get_number_of_degrees_of_freedom()} "
      f"temperature_K={atoms.get_temperature():.8f}")

# Bring kinetic and potential energy into contact with a 300 K bath.
warmup = Bussi(atoms, timestep=1.0 * units.fs, temperature_K=300.0,
               taut=100.0 * units.fs, rng=np.random.default_rng(923),
               trajectory="warmup.traj", logfile="warmup.log", loginterval=10)
t0 = time.perf_counter()
warmup.run(1000)
write("equilibrated.traj", atoms)
write("equilibrated.extxyz", atoms)
print(f"WARMUP_DONE steps={warmup.nsteps} time_ps=1.000 "
      f"temperature_K={atoms.get_temperature():.8f} wall_s={time.perf_counter()-t0:.3f}")

results = {}
for label, dt_fs, steps in [("nve-1fs", 1.0, 500), ("nve-0p5fs", 0.5, 1000)]:
    # Read exactly the same positions, velocities, cell and constraints twice.
    atoms = read("equilibrated.traj")
    atoms.calc = calc
    state_hash = hashlib.sha256(atoms.positions.tobytes() + atoms.get_momenta().tobytes()).hexdigest()
    dyn = VelocityVerlet(atoms, timestep=dt_fs * units.fs,
                         trajectory=label + ".traj", logfile=label + ".log",
                         loginterval=round(5.0 / dt_fs))
    series = []
    with open(label + ".csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_ps", "potential_eV_atom", "kinetic_eV_atom",
                         "total_eV_atom", "temperature_K"])
        def record():
            epot = atoms.get_potential_energy() / len(atoms)
            ekin = atoms.get_kinetic_energy() / len(atoms)
            row = [dyn.get_time() / (1000 * units.fs), epot, ekin,
                   epot + ekin, atoms.get_temperature()]
            series.append(row)
            writer.writerow([f"{value:.12f}" for value in row])
            handle.flush()
        dyn.attach(record, interval=round(5.0 / dt_fs))
        print(f"START {label} steps={steps} timestep_fs={dt_fs} initial_state_sha256={state_hash}")
        t0 = time.perf_counter()
        dyn.run(steps)
    data = np.asarray(series)
    delta = 1000 * (data[:, 3] - data[0, 3])
    fit = np.polyfit(data[:, 0], delta, 1)
    results[label] = dict(steps=dyn.nsteps, timestep_fs=dt_fs, duration_ps=float(data[-1, 0]),
                         initial_state_sha256=state_hash,
                         max_abs_delta_meV_atom=float(np.abs(delta).max()),
                         final_delta_meV_atom=float(delta[-1]),
                         linear_drift_meV_atom_ps=float(fit[0]),
                         mean_temperature_K=float(data[:, 4].mean()),
                         wall_seconds=time.perf_counter()-t0)
    write(label + "-final.extxyz", atoms)
    print(json.dumps(results[label], indent=2))

same_start = results["nve-1fs"]["initial_state_sha256"] == results["nve-0p5fs"]["initial_state_sha256"]
results["same_initial_state"] = same_start
Path("result.json").write_text(json.dumps(results, indent=2) + "\n")
assert same_start
assert results["nve-1fs"]["max_abs_delta_meV_atom"] < 0.1
assert results["nve-0p5fs"]["max_abs_delta_meV_atom"] < results["nve-1fs"]["max_abs_delta_meV_atom"]
print("MD_INTEGRATION_ACCEPTED")
```

脚本每 5 fs 保存一个 NVE 数据点和一个轨迹帧：1 fs 的计算每 5 步保存一次，0.5 fs 的计算每 10 步保存一次。这样两条曲线具有相同的时间节点，最后都到 0.5 ps。CSV 保留较多有效数字，是因为普通 MD 日志的能量显示精度不足以分析很小的积分误差。

### 计算进行时，先看时间有没有向前走

这次在 Talos 的 `atlas-mace` tmux 窗口使用 2 个 CPU 线程运行，MACE 0.3.16、ASE 3.29.0、float64，没有启用 GPU。

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ python -u md.py > md.out 2>&1; echo "exit=$?"
exit=0
```

较长的运行过程中，在另一个终端进入 `si-md`，用 `tail -n 20 md.out` 查看当前阶段；热化时读 `tail -n 5 warmup.log`，进入 NVE 后改读 `tail -n 5 nve-1fs.csv`。需要定时刷新时，实际用过 `watch -n 15 'tail -n 3 nve-0p5fs.csv'`；也可以用 `tail -f` 连续追加查看，退出查看用 Ctrl+C。

`md.out` 的前几行记录软件版本和模型哈希。加载模型时的环境提示仍保留在[完整输出](/Atlas/examples/mace-si/si-md/md.out.txt)；其中 `MaxwellBoltzmannDistribution` 的提示说明当前 ASE 建议以后改用 `thermalize_momenta`，本次实际运行使用的接口和版本没有被改写。真正进入动力学后的第一条信息为 `INITIAL atoms=64 DOF=189 temperature_K=300.00000000`。

然后看 `warmup.log` 的开头：

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ head -n 6 warmup.log
Time[ps]      Etot[eV]     Epot[eV]     Ekin[eV]    T[K]
0.0000        -341.2943    -343.7373       2.4430   300.0
0.0100        -341.3533    -343.1480       1.7947   220.4
0.0200        -341.2770    -342.1515       0.8745   107.4
0.0300        -340.9980    -342.0093       1.0113   124.2
0.0400        -340.9481    -342.4656       1.5175   186.3
```

`Etot`、`Epot`、`Ekin` 分别是整个超胞的总能、势能和动能，单位 eV；时间是 ps。第 0 步虽然设成 300 K，0.02 ps 时温度已经降到约 107 K：原子从优化后的静态结构开始运动，部分动能转成了势能，热浴也在交换能量。这不是要求重新把每一帧速度强行设成 300 K 的理由。

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ tail -n 5 warmup.log
0.9600        -338.6129    -341.5274       2.9145   357.9
0.9700        -338.1598    -340.9155       2.7557   338.4
0.9800        -338.0414    -340.6811       2.6398   324.2
0.9900        -338.2284    -341.0193       2.7909   342.7
1.0000        -338.3569    -341.4208       3.0639   376.2
```

NVT 允许瞬时温度和总能量波动。1 ps 的这段计算用于展示温控和后续积分的衔接；末帧温度为 376.2 K；仅凭这段短轨迹，不能断言已经充分平衡。`equilibrated.traj` 保存的就是这一段末帧，文件名也不能代替时间窗口和多种初速度的平衡检查。

### 关掉热浴后，换一种方式读输出

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ head -n 4 nve-1fs.csv
time_ps,potential_eV_atom,kinetic_eV_atom,total_eV_atom,temperature_K
0.000000000000,-5.334700231401,0.047873985718,-5.286826245683,376.248701548092
0.005000000000,-5.336124815382,0.049297758571,-5.286827056811,387.438342002394
0.010000000000,-5.335895786760,0.049066670310,-5.286829116450,385.622185339634
```

这里能量已经除以原子数，列名里的 `_eV_atom` 要和上面的总能单位区分开。NVE 段没有强迫温度保持某个值，动能和势能会继续互相交换；应该检查它们的和是否在允许范围内波动。

最后程序输出两套积分的实际摘要：

```text
INITIAL atoms=64 DOF=189 temperature_K=300.00000000
WARMUP_DONE steps=1000 time_ps=1.000 temperature_K=376.24870155 wall_s=324.613
START nve-1fs steps=500 timestep_fs=1.0 initial_state_sha256=aa5fa0d6ed2b008e2cede92f7a1c70d79bc1e7b2df2a991cf4e1b29809ca0a6d
{
  "steps": 500,
  "timestep_fs": 1.0,
  "duration_ps": 0.5,
  "initial_state_sha256": "aa5fa0d6ed2b008e2cede92f7a1c70d79bc1e7b2df2a991cf4e1b29809ca0a6d",
  "max_abs_delta_meV_atom": 0.014623237966304714,
  "final_delta_meV_atom": 0.001887423370483532,
  "linear_drift_meV_atom_ps": 0.0014274760219451569,
  "mean_temperature_K": 331.80169436485613,
  "wall_seconds": 161.21382180787623
}
START nve-0p5fs steps=1000 timestep_fs=0.5 initial_state_sha256=aa5fa0d6ed2b008e2cede92f7a1c70d79bc1e7b2df2a991cf4e1b29809ca0a6d
{
  "steps": 1000,
  "timestep_fs": 0.5,
  "duration_ps": 0.5,
  "initial_state_sha256": "aa5fa0d6ed2b008e2cede92f7a1c70d79bc1e7b2df2a991cf4e1b29809ca0a6d",
  "max_abs_delta_meV_atom": 0.0036474880289461,
  "final_delta_meV_atom": 0.00047103504829948406,
  "linear_drift_meV_atom_ps": 0.0003567237150614159,
  "mean_temperature_K": 331.8879410554873,
  "wall_seconds": 322.6769241001457
}
MD_INTEGRATION_ACCEPTED
```

两次 `initial_state_sha256` 完全相同，说明比较确实从相同的位置和速度开始。1 fs 的轨迹在保存的 101 个节点上，最大每原子总能变化为 **0.014623 meV/atom**；减到 0.5 fs 后为 **0.003647 meV/atom**，约缩小到原来的 0.249。这才是本次接受积分设置的主要证据。脚本设定的 0.1 meV/atom 是本算例的数值检查条件，需要随实际研究精度重新选择。

0.5 ps 内两条轨迹的平均瞬时温度分别为 331.80 K 与 331.89 K。它们接近但不要求每一时刻相等；减小时间步长后轨迹会逐渐偏离，这和是否出现系统性能量漂移是两件不同的检查。

进一步用 [check_trajectory.py](/Atlas/examples/mace-si/si-md/check_trajectory.py) 直接读取二进制轨迹，逐帧核对 CSV 中的能量、原子数、晶胞和初始速度：

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ python check_trajectory.py > trajectory-check.out
(venv) talos@talos-MS-7D54:<工作目录>/si-md$ cat trajectory-check.json
{
  "nve-1fs": {
    "frames": 101,
    "csv_rows": 101,
    "atoms_per_frame": 64,
    "all_frames_finite": true,
    "max_energy_csv_mismatch_eV_atom": 4.991562718714704e-13,
    "volume_range_A3": 0.0,
    "max_total_momentum_ase_units": 6.754135550515241e-15,
    "minimum_pair_distance_A": 2.094835590190839,
    "final_rms_displacement_A": 0.26843685625154534
  },
  "nve-0p5fs": {
    "frames": 101,
    "csv_rows": 101,
    "atoms_per_frame": 64,
    "all_frames_finite": true,
    "max_energy_csv_mismatch_eV_atom": 4.991562718714704e-13,
    "volume_range_A3": 0.0,
    "max_total_momentum_ase_units": 6.9125315400528245e-15,
    "minimum_pair_distance_A": 2.0949198169361503,
    "final_rms_displacement_A": 0.2684607696667986
  },
  "initial_positions_identical": true,
  "initial_momenta_identical": true
}
```

两条轨迹都包含 101 帧，64 个原子始终保留，晶胞体积保持不变，CSV 与轨迹中存储的能量差处于写入小数位造成的舍入范围内。初始位置和动量逐项一致。这里还列出了轨迹中最短原子间距和末帧均方根位移，便于发现明显结构异常；短轨迹没有出现这种异常，仍不能外推成长时间热稳定性或新的相变结论。

### 把温度和积分误差画在同一张图里

把 [warmup.log](/Atlas/examples/mace-si/si-md/warmup.log)、[nve-1fs.csv](/Atlas/examples/mace-si/si-md/nve-1fs.csv)、[nve-0p5fs.csv](/Atlas/examples/mace-si/si-md/nve-0p5fs.csv) 和 [plot.py](/Atlas/examples/mace-si/si-md/plot.py) 放在同一目录，运行 `python3 plot.py`。绘图只需要 NumPy 与 Matplotlib；不需要在本机再加载 MACE 模型。

```python
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warmup = np.loadtxt("warmup.log", skiprows=1)
one = np.genfromtxt("nve-1fs.csv", delimiter=",", names=True)
half = np.genfromtxt("nve-0p5fs.csv", delimiter=",", names=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(3, 1, figsize=(8, 9), layout="constrained")
axes[0].plot(warmup[:, 0], warmup[:, 4], color="#6D28D9")
axes[0].axhline(300, color="#666666", linestyle="--", linewidth=1)
axes[0].set(title="64-atom Si with MACE-MP-0 small", ylabel="Temperature (K)",
            xlabel="Bussi warmup time (ps)")
for data, label, color in [(one, "1.0 fs", "#176B87"), (half, "0.5 fs", "#B45309")]:
    delta = 1000 * (data["total_eV_atom"] - data["total_eV_atom"][0])
    axes[1].plot(data["time_ps"], delta, label=label, color=color)
    axes[2].plot(data["time_ps"], data["temperature_K"], label=label, color=color)
axes[1].set(ylabel="Energy change (meV/atom)", xlabel="NVE time (ps)")
axes[2].set(ylabel="Temperature (K)", xlabel="NVE time (ps)")
for ax in axes:
    ax.grid(alpha=0.18)
for ax in axes[1:]:
    ax.legend(frameon=False, title="Time step")
fig.savefig("md-check.svg")
fig.savefig("md-check.png", dpi=180)
print("md-check.svg", "md-check.png")
```

![64 原子 Si 的热化温度和两种步长的 NVE 能量检查](/Atlas/examples/mace-si/si-md/md-check.svg)

第一幅图看热浴交换能量时的温度起伏；第二幅图从两条轨迹各自的初始总能中减去同一个基准，放大每原子能量的微小变化；第三幅图保留真实温度波动。不能用一条平滑温度曲线代替能量守恒检验，也不能把 NVT 中的总能变化按 NVE 的标准判错。

本机已有 ASE 时，可以下载 [nve-1fs.traj](/Atlas/examples/mace-si/si-md/nve-1fs.traj)，用 `ase gui nve-1fs.traj` 打开并拖动帧滑块，观察原子运动。`.traj` 保留多个时刻以及计算属性；[末帧结构](/Atlas/examples/mace-si/si-md/nve-1fs-final.extxyz) 适合接着准备下一次计算，但只有一帧。

完整输入与结果：[md.py](/Atlas/examples/mace-si/si-md/md.py)、[运行输出](/Atlas/examples/mace-si/si-md/md.out.txt)、[0.5 fs 轨迹](/Atlas/examples/mace-si/si-md/nve-0p5fs.traj)、[数值摘要](/Atlas/examples/mace-si/si-md/result.json)。

下一步：若要报告温度相关物性，继续增加超胞、采样时间和独立初速度，并抽取实际轨迹构型做同一 DFT 设置的能量与力对照。需要回查输入结构时，返回[可变晶胞优化](/Atlas/m/vc-relax/mace/)；需要研究谐波动力学时，接着读[声子计算](/Atlas/m/phonon-dfpt/qe/)，重新建立对应 DFT 计算的结构与电子态前提。

```text
接受的势模型与结构 → 64 原子超胞 → 1 ps 温控预热
                                      ↓ 同一末帧
                         1 fs 的 NVE ↔ 0.5 fs 的 NVE
                                      ↓
                      原始轨迹核对 → 能量、温度与步长图
```
