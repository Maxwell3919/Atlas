# Si Γ 点虚频与 ASR 对照

原始记录来自 QE 7.5 金刚石 Si 固定晶胞算例：两原子，PBE，60/640 Ry，8×8×8 电子网格。目录保留 ph.x 与两次 dynmat.x 的输入、完整输出、标准错误、同一动力学矩阵和位移文件。

## 重新生成诊断与频率图

需要 Python、NumPy、Matplotlib。在本目录运行：

    python3 analyse_modes.py > analysis.out
    python3 plot_asr.py

脚本读取已有结果，不执行 QE。analyse_modes.py 输出诊断 CSV、向量 CSV 和检查 JSON；plot_asr.py 输出频率 CSV 及 SVG/PNG/PDF。当前验证环境：Python 3.12.3、NumPy 2.4.6、Matplotlib 3.11.1。

si.dynG 中 alat=10.2 Bohr；tau 是以 alat 为单位的笛卡尔坐标，r=tau*alat，不是原胞分数坐标。filout 位移是动力学矩阵本征矢除以质量平方根后归一化的分量，不是 Å 位移。脚本针对这两个等质量 Si 的 Γ 点模式检查平移成分与简并子空间。

两份 Molden 文件保留原样；其中 si-no.mold 把负频率写成零，频率符号应以 .modes/ph.out.txt 为准。历史 dynmat.axsf 来自后运行的 crystal 分支。

重跑上游 ph.x 需要匹配的 Si SCF 保存目录和 QE；本包不含波函数或 SCF save。run.sh 中的程序路径和 Slurm/MPI 设置须按运行环境配置。父 SCF 输入、输出另见网站 Si 教学包。
