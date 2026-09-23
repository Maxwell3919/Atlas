参考：

- [MACE：预训练模型与 ASE 接口](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html)
- [ASE：晶体结构的构造](https://docs.ase-lib.org/ase/build/build.html)
- [ASE：结构优化](https://docs.ase-lib.org/ase/optimize.html)
- [ASE：FrechetCellFilter 与晶胞自由度](https://docs.ase-lib.org/ase/filters.html)

## 让偏大的 Si 晶胞自己收缩

固定晶胞优化只能移动原子。这里把金刚石 Si 的立方胞边长设成 5.60 Å，同时给一个原子加上小位移，让原子坐标和六个晶胞应变自由度一起调整。问题变成了：能量降低之后，原子力和晶胞应力是否同时足够小？

模型准备沿用[固定晶胞优化](/Atlas/m/relax/mace/)中的 MACE-MP-0 small，SHA256 为 `2ddb079cee0e131eaaf6912ba581b394551ead283e95c99cfe78c605d10b5736`。这里只读同一份模型，重新建立一个明确的 8 原子 Si 输入。

### 把应力交给优化器

`FrechetCellFilter` 把晶胞变形与原子位移一起传给 BFGS。`scalar_pressure=0.0` 给出零外压条件；这里是三维体相，各晶胞方向都可以变化。二维薄层的真空方向需要另行约束，不能原封不动照搬这一行。

这份输入没有设置 `mask`，也没有打开 `hydrostatic_strain` 或 `constant_volume`，因此体积和剪切都参与优化。它要检验的是从偏大、略有扰动的晶胞能否走回零外压附近，因此末态三条边的长度与三个角都要从结果中读回。若只希望保持立方形状并改变边长，应另设均匀缩放约束；那将是另一组几何自由度，须重新检查末态应力。

```python
(venv) talos@talos-MS-7D54:<工作目录>$ vi si-vc-relax/vc-relax.py
(venv) talos@talos-MS-7D54:<工作目录>$ cd si-vc-relax
(venv) talos@talos-MS-7D54:<工作目录>/si-vc-relax$ cat vc-relax.py
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import time
import numpy as np
import torch
from ase import units
from ase.build import bulk
from ase.filters import FrechetCellFilter
from ase.io import write
from ase.optimize import BFGS
from mace.calculators import MACECalculator

torch.set_num_threads(2)
model = Path("../models/mace-mp-0-small.model")
print("MACE", metadata.version("mace-torch"), "ASE", metadata.version("ase"))
print("model_sha256", hashlib.sha256(model.read_bytes()).hexdigest())
calc = MACECalculator(model_paths=str(model), device="cpu", default_dtype="float64")

# Start diamond Si from a larger cubic cell and perturb one atom.
atoms = bulk("Si", "diamond", a=5.60, cubic=True)
atoms.positions[0] += [0.05, -0.03, 0.02]
write("initial.extxyz", atoms)
atoms.calc = calc
e0 = atoms.get_potential_energy()
v0 = atoms.get_volume()
print(f"INITIAL atoms={len(atoms)} energy_eV={e0:.10f} volume_A3={v0:.8f}")

start = time.perf_counter()
cell_filter = FrechetCellFilter(atoms, scalar_pressure=0.0)
opt = BFGS(cell_filter, trajectory="vc-relax.traj", logfile="vc-relax.log")
converged = opt.run(fmax=0.0005, steps=150)
energy = atoms.get_potential_energy()
forces = atoms.get_forces()
stress = atoms.get_stress()
fmax = float(np.linalg.norm(forces, axis=1).max())
smax = float(np.abs(stress).max())
write("relaxed.extxyz", atoms)
write("relaxed.cif", atoms)
result = dict(converged=bool(converged), steps=opt.nsteps,
              initial_energy_eV=float(e0), energy_eV=float(energy),
              initial_volume_A3=v0, volume_A3=atoms.get_volume(),
              cell_lengths_A=atoms.cell.lengths().tolist(),
              cell_angles_deg=atoms.cell.angles().tolist(),
              fmax_eV_A=fmax, stress_eV_A3=stress.tolist(),
              max_abs_stress_GPa=smax / units.GPa,
              wall_seconds=time.perf_counter()-start)
Path("result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert converged and fmax < 0.001 and smax < 0.0001
print("VC_RELAX_ACCEPTED")
```

`fmax=0.0005` 是优化器面对这个 filter 时的停止条件。晶胞自由度也参与了这个量，所以脚本收尾时另取真实原子力和六个应力分量核对：最大原子力要小于 0.001 eV/Å，各应力分量绝对值要小于 0.0001 eV/Å³。后一个阈值约等于 0.0160 GPa。

### 将日志里的变化对应到晶胞

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-vc-relax$ python -u vc-relax.py > vc-relax.out 2>&1; echo "exit=$?"
exit=0
```

较大结构运行期间，在第二个终端用 `tail -f vc-relax.log` 看优化器步数，用 `tail -n 20 vc-relax.out` 看是否出现异常。这个算例的优化本身约一秒，直接读完整日志更清楚：

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-vc-relax$ cat vc-relax.log
Step     Time          Energy          fmax
BFGS:    0 21:28:45      -42.766777        0.631790
BFGS:    1 21:28:45      -42.787008        0.602829
BFGS:    2 21:28:45      -42.932028        0.532014
BFGS:    3 21:28:45      -42.940549        0.448262
BFGS:    4 21:28:46      -42.965981        0.079182
BFGS:    5 21:28:46      -42.966354        0.069595
BFGS:    6 21:28:46      -42.966982        0.030133
BFGS:    7 21:28:46      -42.967115        0.014189
BFGS:    8 21:28:46      -42.967141        0.012601
BFGS:    9 21:28:46      -42.967147        0.010599
BFGS:   10 21:28:46      -42.967154        0.005556
BFGS:   11 21:28:46      -42.967158        0.004568
BFGS:   12 21:28:46      -42.967159        0.003521
BFGS:   13 21:28:46      -42.967160        0.003369
BFGS:   14 21:28:46      -42.967162        0.004335
BFGS:   15 21:28:46      -42.967163        0.003981
BFGS:   16 21:28:46      -42.967165        0.002002
BFGS:   17 21:28:46      -42.967165        0.000523
BFGS:   18 21:28:46      -42.967165        0.000419
```

初态总能为 −42.766777 eV，早期几步下降较快；到第 17 步，filter 的 `fmax` 仍为 0.000523，略高于 0.0005。第 18 步继续下降后才结束。看见程序退出还不够，再核对真实的力、应力和晶胞：

```text
(venv) talos@talos-MS-7D54:<工作目录>/si-vc-relax$ cat result.json
{
  "converged": true,
  "steps": 18,
  "initial_energy_eV": -42.76677684200746,
  "energy_eV": -42.967165172147226,
  "initial_volume_A3": 175.61599999999996,
  "volume_A3": 163.18884458209394,
  "cell_lengths_A": [
    5.464480703128529,
    5.464718899266747,
    5.464793393633502
  ],
  "cell_angles_deg": [
    89.99451924668405,
    90.00373954700109,
    89.99687367253333
  ],
  "fmax_eV_A": 0.0002580385197946813,
  "stress_eV_A3": [
    -7.795706733771092e-06,
    2.4939587082779995e-06,
    5.71265227698127e-06,
    1.5484093725681533e-05,
    -1.2207863628214975e-05,
    1.1799012875139589e-05
  ],
  "max_abs_stress_GPa": 0.002480825296156292,
  "wall_seconds": 1.0119415447115898
}
```

体积从 175.6160 Å³ 降到 163.1888 Å³。三条边长都约为 5.4647 Å，三个角接近 90°；没有强制保持立方对称，所以残留的微小差别也如实保留。最大原子力为 2.5804×10⁻⁴ eV/Å，最大应力分量为 0.00248 GPa，均低于脚本单独检查的阈值。

ASE 的应力数组按 `xx, yy, zz, yz, xz, xy` 排列，原始值单位是 eV/Å³。它描述当前结构对晶胞变形的响应，不能由总能量的最后几位代替。日志中的 0.000419 与这里的 0.000258 不同，正是因为前者来自包含晶胞自由度的 filter，后者只统计实际原子力。

本次得到的是 MACE-MP-0 small 预测的在零外压下优化后的结构。没有做 DFT 对照，也没有测定有限温度晶格常数；后续 MD 沿用这份模型和结构，结论需要保持相同范围。

### 画出体积收缩与力的收敛

[optimization.csv](/Atlas/examples/mace-si/si-vc-relax/optimization.csv) 是从 `vc-relax.traj` 逐帧提取的 8 原子超胞总能量、最大原子力和晶胞体积。将它与 [plot.py](/Atlas/examples/mace-si/si-vc-relax/plot.py) 放在同一个本地目录，运行 `python3 plot.py`：

绘图脚本使用同目录的 [atlas_plot_style.py](/Atlas/examples/mace-si/si-vc-relax/atlas_plot_style.py)；下载完整算例包时已包含这个文件。它同时保存网页预览与可编辑 PDF，具体版式见[重绘与导出](/Atlas/plotting/)。

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = np.genfromtxt("optimization.csv", delimiter=",", names=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(3, 1, figsize=(7, 8), sharex=True, layout="constrained")
axes[0].plot(data["step"], 1000 * (data["energy_eV"] - data["energy_eV"][0]) / 8, "o-", color="#0072b2")
axes[0].set_ylabel("Energy change (meV/atom)")
axes[0].set_title("Diamond Si: variable-cell MACE relaxation")
axes[1].plot(data["step"], data["volume_A3"], "o-", color="#cc79a7")
axes[1].set_ylabel("Cell volume (angstrom^3)")
axes[2].semilogy(data["step"], data["fmax_eV_A"], "o-", color="#B45309")
axes[2].axhline(0.001, color="#555555", linestyle="--", label="atomic-force threshold")
axes[2].set(ylabel="Largest force (eV/angstrom)", xlabel="BFGS step")
axes[2].legend(frameon=False)
for ax in axes:
    ax.grid(alpha=0.18)
fig.savefig("cell-relaxation.svg")
fig.savefig("cell-relaxation.png", dpi=180)
print("cell-relaxation.svg", "cell-relaxation.png")
```

![Si 可变晶胞优化的能量、体积与原子力](/Atlas/examples/mace-si/si-vc-relax/cell-relaxation.svg)

图中体积在前几步迅速接近末态，原子力还要继续优化才能降到阈值以下。保留完整轨迹，可以分清“晶胞基本不变了”和“所有接受条件都已满足”。

完整材料：[输入](/Atlas/examples/mace-si/si-vc-relax/vc-relax.py)、[原始输出](/Atlas/examples/mace-si/si-vc-relax/vc-relax.out.txt)、[轨迹](/Atlas/examples/mace-si/si-vc-relax/vc-relax.traj)、[末态结构](/Atlas/examples/mace-si/si-vc-relax/relaxed.extxyz)、[CIF](/Atlas/examples/mace-si/si-vc-relax/relaxed.cif)。

下一步：用这份末态扩成 64 原子超胞，进入[机器学习势分子动力学](/Atlas/m/mlip-md/mace/)，检查有限时间轨迹和积分步长。

```text
明确结构与模型 → 可变晶胞优化 → 原子力、应力、晶胞检查
                                              ↓
                                64 原子超胞 → 热化 → NVE 对照
```
