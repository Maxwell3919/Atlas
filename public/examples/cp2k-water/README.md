# CP2K 周期水的能量与力

CP2K 2026.2，PBE/GPW，8 Å 周期立方胞中的一个固定水分子，O/H 使用 DZVP-MOLOPT-SR-GTH-q6/q1 与 GTH-PBE-q6/q1。模型从官方 H2O-fixed 的相对坐标派生；原例采用不同晶胞、泛函和优化流程，保存在 official_example/，本例不对照原回归能量。

cases/ 含 baseline（600/60 Ry）、grid_control（800/80 Ry）、H1_y_plus/minus（600/60 Ry、第二个原子 y ±0.005 Å）。四份 cp2k.out/cp2k.err 是实际运行输出，保留科学记录、警告和计时，主机身份与路径已简写。input.inp 只将实际数据文件路径派生为 ../../data/，没有再次提交运行。

在本目录复用已有输出：

```bash
python3 source/postprocess.py case cases/baseline
python3 source/postprocess.py case cases/grid_control
python3 source/postprocess.py case cases/H1_y_plus
python3 source/postprocess.py case cases/H1_y_minus
python3 source/postprocess.py compare cases
python3 source/export_csv.py .
```

脚本只用 Python 3 标准库。case 提取最后一次 ENERGY| 和 FORCES| 的 O/H/H 三行，compare 做中心有限差分与网格差，export_csv 将物理数值写为 native_energy_forces.csv。脚本产生的 JSON 是程序之间的数值中间文件，读者直接核对原 OUT 与 CSV 即可。CSV 每行一个原子，energy_Ha 是整胞总能（同一算例三行重复），力保留 Ha/Bohr，并另列 eV/Å。

未来运行便携输入时，从相应 cases 子目录启动 CP2K，确保 ../../data/ 正确解析；按可用计算资源选匹配 launcher 与 MPI/OMP 设置。已有输出来自32 MPI ranks×OMP1，每份都保留非平方MPI进程数的性能警告。version_observation/另存一次 --version 打印版本后退出2的错误，它与四份正常 ENERGY_FORCE 输出分开。

此包只检查固定模型中的能量/力提取、两套网格差和一个位移步长的导数。EPS_SCF=1e-10 是实际电子停止设置，不能充当力误差界；基组、胞大小与位移极限尚未通过这组数据收敛。
