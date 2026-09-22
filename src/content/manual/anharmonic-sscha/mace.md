参考：

- [MACE：ASE calculator](https://mace-docs.readthedocs.io/en/latest/guide/ase.html)
- [Phonopy：Python API、力常数与色散](https://phonopy.github.io/phonopy/phonopy-module.html)
- [symfc：位移—力数据与对称化力常数](https://symfc.github.io/symfc/)
- [hiPhive：从 MD 轨迹建立有效谐模型](https://hiphive.materialsmodeling.org/advanced_topics/effective_harmonic_models.html)

## 从 Si 热运动轨迹拟合有限温度有效二阶力常数

[64 个 Si 原子的 MACE 分子动力学](/Atlas/m/mlip-md/mace/)已经留下每一帧的结构、原子力和温度。这里接着取出位移 `u` 和力 `F`，用一个二阶模型近似这段热运动中的力：`F ≈ −Φu`。得到 `Φ` 后，再交给 phonopy 构造动力学矩阵，沿同一条倒空间路径输出频率。

这条路线叫有限温度有效二阶力常数拟合。这里实际运行的是 MACE、symfc 和 phonopy，没有执行 SSCHA 的变分自由能最小化。算例的作用是把数据准备、拟合、独立验证和声子图接通；后面会看到，样本数由 40 增至 60 时，色散仍有可见变化，因此这份结果还不能称为已经收敛的温度重整化声子。

### 把参考结构写清楚，再取位移

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

### 同时保留小位移基线和热运动构型

小位移基线描述这个参考结构附近的势能曲率。脚本分别生成正负 0.01 Å、正负 0.005 Å 位移，用 MACE 计算每个构型的力，然后由 phonopy 重建二阶力常数。这个高对称 Si 超胞每个幅度只有 2 个对称不等价的位移构型；换成低对称结构后，位移数量会变化。

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

### 用另一组初速度检查能否预测新轨迹

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

### 拟合时给后来的一段轨迹留位置

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

### 看色散，也看换一批样本时色散怎样变化

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

[plot.py](/Atlas/examples/mace-si/si-effective-fc/plot.py)只依赖 NumPy 与 Matplotlib，读取本目录的 CSV、JSON、NPZ 和预测力数组。把[数据包](/Atlas/examples/mace-si/si-effective-fc/public-bundle.tar.gz)中、[清单](/Atlas/examples/mace-si/si-effective-fc/public-files.json)列出的文件放在同一目录后，可在本机执行：

```bash
python3 plot.py
```

该命令生成两组 SVG 与 PNG。第一组将两个小位移幅度的频率差单独画出，再比较小位移基线与 60 帧有效力常数的色散。

![小位移幅度检查与有限温度有效二阶力常数色散](/Atlas/examples/mace-si/si-effective-fc/effective-phonons.svg)

0.01 Å 与 0.005 Å 两个基线沿路径的最大频率差为 **0.001122 THz**，约 1.122 GHz。这是小位移幅度的一项检查，超胞尺寸和模型误差仍需另外处理。Γ 点光学频率从小位移基线的约 11.4631 THz 变为这次有效模型的约 11.9107 THz；两条曲线的差别属于本次参考与采样协议下的拟合结果，不能直接作为收敛的热致频移引用。

![样本数量、独立预测力、实际轨迹温度与色散敏感性](/Atlas/examples/mace-si/si-effective-fc/fit-validation.svg)

第二组把误差曲线、独立轨迹的预测力、两段轨迹实际温度和 40→60 帧的色散变化放在一起。虽然独立力 RMSE 的变化已经很小，40 帧与 60 帧模型沿路径的最大频率差仍有 **0.214015 THz**。因此“力误差曲线看起来平了”不足以说明声子已经不再依赖样本。

### 把导出的文件重新读回来

[verify.py](/Atlas/examples/mace-si/si-effective-fc/verify.py)单独读取轨迹、位移—力数组和保存的力常数，用普通矩阵乘法重新计算独立误差，再从 YAML 重建 phonopy 对象。读取时明确指定 `is_compact_fc=False`，获得完整的 `(64, 64, 3, 3)` 力常数；默认压缩布局只保留原胞代表原子的行，形状会是 `(2, 64, 3, 3)`，两种布局不能直接按相同数组比较。

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

下一步可以回到[机器学习势 MD](/Atlas/m/mlip-md/mace/)延长采样，或沿[有限位移声子](/Atlas/m/phonon-finite-disp/qe/)另做势模型与 DFT 的力和谐性频率对照。若要计算 SSCHA 自由能及其 Hessian，需要另接[SSCHA 官方流程](https://sscha.eu/Tutorials/tutorial_06_the_SSCHA_with_MLP/)，这里的二阶拟合结果不能直接代替那一步。

```text
已核验模型与结构
    ↓
明确立方参考 ─→ ±0.01 / ±0.005 Å 小位移谐性基线
    ↓
旧轨迹位移映射 → 在新构型上重算 MACE 力
    ↓
20 / 40 / 60 帧有效二阶力常数
    ├→ 同轨迹后段验证
    ├→ 独立速度种子轨迹验证
    └→ phonopy 色散 → 样本数与频率变化检查
```
