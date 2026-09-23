# Al 两条致密电子网格的实际结果

k32 来自已完成的 32³ 致密电子网格分支；k48 来自随后独立运行的 48³ 分支。
两者响应电子网格均为 16³，DFPT q 网格均为 4³，使用同一结构、PZ 赝势、40/160 Ry、nbnd=6、SCF degauss=0.02 Ry、conv_thr=1e-12、tr2_ph=1e-14、10 个电子展宽和 μ*=0.10。
目录名 k32/k48 是公开包映射；实际终端教案使用 epc-q4/epc-q4-k48。

目录包含真实输入、原生输出、8 个不可约 q 动力学矩阵、电声文件、q 权重、lambda.x 谱和 Tc 表。波函数及软件二进制不随包提供。数值保持原样；公开编辑只有路径文字替换。source-public-hashes.json 同时保留每个原件与公开副本的 SHA256，路径编辑后的文件不应与原件哈希混用。

pseudo_dir 在公开输入和 XML 中统一为 ../pseudo。公开 Slurm 脚本将原始 QE bin 路径写为 ${QE_BIN}/；自行重跑前需要在 shell 中设置并导出 QE_BIN，指向自己的 QE 7.5 bin。oneAPI 的 source 路径是本次真实运行环境，按所在机器实际配置。所有重跑应使用另建计算目录，避免覆盖本包原生输出。

k32/history 保留第一次批任务：dense SCF 本身完成，随后的旧 run.slurm 第 16 行 cp al.a2Fsave al.a2Fsave.k32 把 a2Fsave 当成当前目录文件，原错误为：cp: 对 'al.a2Fsave' 调用 stat 失败: 没有那个文件或目录。正确文件位于 tmp。第 14 行 set -e 使首批任务在此退出。之后真实 continue.slurm 从 tmp 保存 dense 文件并完成响应、ph.x、q2r.x 与 matdyn.x。本包保留该历史脚本与错误输出，不把 k32/run.slurm 或 history 内的历史脚本当作完整成功链重跑入口。重建 k32 时先在新目录运行 al.dense.in 并检查收敛，随后才运行 continue.slurm；lambda.x 需要另从该目录读取 lambda.in 执行。k48/run.slurm 是本次已经执行的完整串行脚本，保存 tmp/al.a2Fsave 后再进行响应 SCF，并在 ph.x 前 cmp 比对。

在解包根目录执行：

```bash
python3 rebuild_tc.py k32 k48 --outdir comparison-k32-k48
python3 compare_tc.py --a k32 --b k48 --out comparison-k32-k48
python3 plot_tc_crossings.py --data comparison-k32-k48 --out figures --prefix al-k32-k48
```

前两条仅用标准库，从原生逐 q elph 输入重建 lambda.x 运算，复现输出的打印精度，再逐点配对并查找全部折线交点。绘图使用 NumPy、Matplotlib。32³/48³ 在 0.005–0.050 Ry 的共同采样范围内没有交点；最小差为 0.009221798 K，出现在 0.050 Ry，不能将最近点称为交点。

`comparison-k32-k48/` 同时保留原生三位小数 Tc、由打印频率矩复算的 Tc 和从原始电声输入重建的 Tc。`compare_dense_grids.py` 是对原生打印表的辅助比较，主文使用上面的 `compare_tc.py`，以减少最终打印格式对求交的影响。重建不恢复电声文件中未打印的精度。

需要 NumPy 2.x 的逐 q 与谱积分核对：
python3 verify_tc_chain.py --source k32 --output checks/k32
python3 verify_tc_chain.py --source k48 --output checks/k48

同一 q 网格、响应网格下两条曲线的交点只是一项采样比较，不是材料 Tc 的收敛判据。该 q4 教学例仍需独立检查更密响应 k/q 网格、截断能、展宽区间和模型条件。两套原生矩阵均保留真实 Γ 正频残差及程序的低频 λ 处理。不要改负谱或低频原值来制造通过结果。
