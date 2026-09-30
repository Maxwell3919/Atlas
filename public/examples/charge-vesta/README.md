# 电荷与 ELF 后处理及 VESTA 场景

H₂差分密度为固定10 Å立方胞、H–H=0.74 Å下三份144³网格的 rho_AB−rho_A−rho_B。原始CHGCAR下载位于 /Atlas/examples/h2-delta-charge/{A,B,AB}/CHGCAR.gz。差分积分为4.3626382×10⁻¹⁰ e，与原始数据打印精度一致。

H₂等值面的物理阈值为±0.03 e/Å³，VESTA场景对应±0.00444555 e/bohr³，VASP原始存储数组对应±30。h2_delta_slice.png为红蓝平面辅助显示，未保留切面坐标，不作定量截面。Fe ELF两块分别为上、下自旋的无量纲36³网格，仅分块，不求和。两幅ELF图采用0.10等值面，视向不同，应按晶轴比较。

包内提供差分网格、两自旋ELF网格、相对路径VESTA场景、转换与提取源码、Bader表和布居数据。转换环境为Python3.12.3；H₂脚本需要NumPy，其他提取脚本仅需标准库。完整命令、输入文件和图注见对应教程：差分电荷、ELF、Bader、COHP和布居分析。
