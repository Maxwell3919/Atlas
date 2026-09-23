参考：

- [MACE：预训练模型与 ASE 接口](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html)
- [ASE：晶体结构的构造](https://docs.ase-lib.org/ase/build/build.html)
- [ASE：结构优化](https://docs.ase-lib.org/ase/optimize.html)

## 把一个 Si 原子挪开，再看它如何回到平衡位置

这里从金刚石结构的 Si 出发：立方常规胞有 8 个原子，边长取 5.43 Å。先把第一个原子沿三个方向分别移动 0.10、−0.06、0.04 Å，再固定晶胞做 BFGS 优化。这样起点带着明确的原子力，可以同时看见能量下降、力收敛和晶胞保持不变。

结构由 ASE 的 `bulk("Si", "diamond", a=5.43, cubic=True)` 明确生成。5.43 Å 是这次教学输入，不是本次拟合出的平衡晶格常数。所用 MACE-MP-0 small 势来自[官方模型发布](https://github.com/ACEsuit/mace-foundations/releases/tag/mace_mp_0)，本机缓存与重新下载的官方文件逐字节一致。

### 先把模型和输入放在计算目录里

这次在 Talos 的 `atlas-mace` tmux 会话运行，CPU 上使用 2 个计算线程。进入已有 MACE 环境后，把模型复制到相邻的 `models` 目录；三个算例共用这一份模型，后面的脚本都显式读它。

```text
talos@talos-MS-7D54:<工作目录>$ source <MACE环境>/bin/activate
(venv) talos@talos-MS-7D54:<工作目录>$ export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
(venv) talos@talos-MS-7D54:<工作目录>$ mkdir -p models si-relax si-vc-relax si-md
(venv) talos@talos-MS-7D54:<工作目录>$ cp ~/.cache/mace/2023-12-10-mace-128-L0_energy_epoch-249.model models/mace-mp-0-small.model
(venv) talos@talos-MS-7D54:<工作目录>$ sha256sum models/mace-mp-0-small.model
2ddb079cee0e131eaaf6912ba581b394551ead283e95c99cfe78c605d10b5736  models/mace-mp-0-small.model
```

如果本机还没有这份缓存，可以从[官方模型文件](https://github.com/ACEsuit/mace-foundations/releases/download/mace_mp_0/2023-12-10-mace-128-L0_energy_epoch-249.model)下载，保存为 `models/mace-mp-0-small.model`，再用同一条 `sha256sum` 核对。

输入是 Python 文件：ASE 管原子坐标和优化步，MACE 返回每一步的能量与力。`float64` 指明计算精度；`fmax=0.001` 的单位是 eV/Å。100 是最多允许的 BFGS 步数，达到步数上限并不等于收敛。

这里把 `float64` 与较小的力阈值配在一起，便于读取优化末段的微小变化；提高浮点精度不会重新训练模型，也不会消除模型本身的力误差。若调小 `fmax`，需要继续比较末步原子力和结构变化，而不是只观察能量的小数位。`model_paths` 则直接决定采用哪一份势能面：更换模型后，即使沿用同样的优化参数，也应重新优化并核验结果。

实际用 `vi` 保存后，再用 `cat` 核对内容：

```python
(venv) talos@talos-MS-7D54:<工作目录>$ vi si-relax/relax.py
(venv) talos@talos-MS-7D54:<工作目录>$ cd si-relax
(venv) talos@talos-MS-7D54:<工作目录>/si-relax$ cat relax.py
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
from ase.build import bulk
from ase.io import write
from ase.optimize import BFGS
from mace.calculators import MACECalculator

torch.set_num_threads(2)
model = Path("../models/mace-mp-0-small.model")
print("MACE", metadata.version("mace-torch"), "ASE", metadata.version("ase"))
print("model_sha256", hashlib.sha256(model.read_bytes()).hexdigest())
calc = MACECalculator(model_paths=str(model), device="cpu", default_dtype="float64")

# Diamond Si, conventional cubic cell: 8 atoms, a = 5.43 angstrom.
# Move one atom to give the optimizer a finite restoring force.
atoms = bulk("Si", "diamond", a=5.43, cubic=True)
atoms.positions[0] += [0.10, -0.06, 0.04]
write("initial.extxyz", atoms)
cell_before = atoms.cell.array.copy()
atoms.calc = calc
e0 = atoms.get_potential_energy()
f0 = np.linalg.norm(atoms.get_forces(), axis=1).max()
print(f"INITIAL atoms={len(atoms)} energy_eV={e0:.10f} fmax_eV_A={f0:.8f}")

start = time.perf_counter()
opt = BFGS(atoms, trajectory="relax.traj", logfile="relax.log")
converged = opt.run(fmax=0.001, steps=100)
energy = atoms.get_potential_energy()
fmax = np.linalg.norm(atoms.get_forces(), axis=1).max()
unchanged = bool(np.array_equal(cell_before, atoms.cell.array))
write("relaxed.extxyz", atoms)
write("relaxed.cif", atoms)
result = dict(converged=bool(converged), steps=opt.nsteps,
              energy_eV=float(energy), initial_energy_eV=float(e0),
              fmax_eV_A=float(fmax), cell_unchanged=unchanged,
              volume_A3=atoms.get_volume(), wall_seconds=time.perf_counter()-start)
Path("result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert converged and fmax < 0.001 and unchanged
print("RELAX_ACCEPTED")
```

`initial.extxyz` 会在调用优化器前写出，留下扰动后的起点；`relax.traj` 保存优化各步；`relaxed.extxyz` 和 `relaxed.cif` 保存末步结构。脚本末尾再次读取最大原子力，还会逐项比较初末晶胞。最后的 `RELAX_ACCEPTED` 是这份脚本在这些检查通过后打印的标记。

### 先看程序有没有运行，再看优化走到了哪里

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-relax$ python -u relax.py > relax.out 2>&1; echo "exit=$?"
exit=0
```

这次 8 原子的优化阶段不到一秒，整条命令还包括导入软件与加载模型的时间。较大体系运行时，可以在另一个终端进入同一目录，用 `tail -f relax.log` 连续看步数，用 `tail -n 20 relax.out` 查程序消息；退出 `tail -f` 的 Ctrl+C 只结束查看，不会终止原终端的计算。

`relax.out` 的开头先给出 MACE 0.3.16、ASE 3.29.0 和模型 SHA256。原始输出还含有模型加载提示与 cuequivariance 加速未启用的提示；这次明确选择 CPU，随后确实进入了计算。正文第一条结构消息是：

```text
INITIAL atoms=8 energy_eV=-42.8918232886 fmax_eV_A=0.99965933
```

起始最大力接近 1 eV/Å，确实没有直接落在停止阈值之内。再读优化器逐步输出：

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-relax$ cat relax.log
Step     Time          Energy          fmax
BFGS:    0 21:28:05      -42.891823        0.999659
BFGS:    1 21:28:05      -42.910864        0.828194
BFGS:    2 21:28:05      -42.949597        0.104508
BFGS:    3 21:28:05      -42.950252        0.088540
BFGS:    4 21:28:05      -42.952003        0.077116
BFGS:    5 21:28:05      -42.952356        0.054305
BFGS:    6 21:28:05      -42.952629        0.042112
BFGS:    7 21:28:05      -42.952964        0.045880
BFGS:    8 21:28:05      -42.953423        0.045291
BFGS:    9 21:28:05      -42.953707        0.033300
BFGS:   10 21:28:05      -42.953808        0.023585
BFGS:   11 21:28:05      -42.953841        0.015487
BFGS:   12 21:28:05      -42.953861        0.006808
BFGS:   13 21:28:05      -42.953870        0.003906
BFGS:   14 21:28:05      -42.953872        0.001449
BFGS:   15 21:28:05      -42.953872        0.000627
```

`Energy` 是整个 8 原子晶胞的势能，`fmax` 是最大的原子力模长。第 6 到第 8 步的最大力有小幅回升，能量仍在下降；因此不能要求每个原子的力每步都严格递减。第 14 步的 0.001449 eV/Å 还高于阈值，第 15 步才降到 0.000627 eV/Å。

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-relax$ cat result.json
{
  "converged": true,
  "steps": 15,
  "energy_eV": -42.953871918991695,
  "initial_energy_eV": -42.89182328857759,
  "fmax_eV_A": 0.0006266642896855485,
  "cell_unchanged": true,
  "volume_A3": 160.10300699999996,
  "wall_seconds": 0.7575141163542867
}
```

这里三项相互对应：优化器返回 `converged: true`，重新计算的最大力为 6.2666×10⁻⁴ eV/Å，`cell_unchanged: true` 表明晶胞没有被改动。势能降低了约 0.06205 eV。这个结果说明这份势函数下的固定晶胞优化达到了设定阈值；它没有检验这份势对 Si 的 DFT 力误差，也没有证明结构的声子稳定性。

### 把优化过程画出来

从轨迹逐帧读取能量、力和体积，导出的[数据表](/Atlas/examples/mace-si/si-relax/optimization.csv) 第一列是优化步数。绘图取相对初态的每原子能量，力使用对数坐标，最后几步是否跨过阈值就能直接看清。导出脚本也保留在[这里](/Atlas/examples/mace-si/export_series.py)，它读取计算实际生成的 `.traj`，不从图片反推数值。

将 `optimization.csv` 和 [plot.py](/Atlas/examples/mace-si/si-relax/plot.py) 下载到同一个本地目录，运行 `python3 plot.py`。完整绘图代码如下：

绘图脚本使用同目录的 [atlas_plot_style.py](/Atlas/examples/mace-si/si-relax/atlas_plot_style.py)；下载完整算例包时已包含这个文件。它同时保存网页预览与可编辑 PDF，具体版式见[重绘与导出](/Atlas/plotting/)。

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = np.genfromtxt("optimization.csv", delimiter=",", names=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True, layout="constrained")
axes[0].plot(data["step"], 1000 * (data["energy_eV"] - data["energy_eV"][0]) / 8, "o-", color="#0072b2")
axes[0].set_ylabel("Energy change (meV/atom)")
axes[0].set_title("Diamond Si: fixed-cell MACE relaxation")
axes[1].semilogy(data["step"], data["fmax_eV_A"], "o-", color="#B45309")
axes[1].axhline(0.001, color="#555555", linestyle="--", label="force threshold")
axes[1].set(ylabel="Largest force (eV/angstrom)", xlabel="BFGS step")
axes[1].legend(frameon=False)
for ax in axes:
    ax.grid(alpha=0.18)
fig.savefig("relaxation.svg")
fig.savefig("relaxation.png", dpi=180)
print("relaxation.svg", "relaxation.png")
```

![固定晶胞 Si 的能量下降与最大原子力](/Atlas/examples/mace-si/si-relax/relaxation.svg)

能量曲线很早就趋于平缓，但最大力到第 15 步才越过虚线。这也是为什么不能只凭“最后几步能量没变多少”接受结构。

完整材料：[输入](/Atlas/examples/mace-si/si-relax/relax.py)、[原始输出](/Atlas/examples/mace-si/si-relax/relax.out.txt)、[优化轨迹](/Atlas/examples/mace-si/si-relax/relax.traj)、[末步 CIF](/Atlas/examples/mace-si/si-relax/relaxed.cif)。

下一步：想让晶格常数也由这份势决定，接着做[可变晶胞优化](/Atlas/m/vc-relax/mace/)；准备有限温度轨迹时，先使用那里已检查原子力与应力的结构，再进入[机器学习势分子动力学](/Atlas/m/mlip-md/mace/)。

```text
明确结构与模型 → 固定晶胞优化 → 检查力和晶胞
                                ↓
                         可变晶胞优化 → MD
```
