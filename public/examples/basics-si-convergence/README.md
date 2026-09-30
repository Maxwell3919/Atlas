# Si QE 总能量扫描

原始 QE 7.5 计算输出位于 si-pbe/；三条轴分别扫描 ecutwfc、ecutrho、均匀 k 网格。体系为固定晶胞两原子金刚石 Si，PBE USPP、occupations=fixed、零网格偏移。

在包根目录运行：

```bash
python3 analyze_si_convergence.py si-pbe --outdir reproduced
```

Python 3 标准库即可。SHA256SUMS.raw 保存原始小文件的相对路径和哈希；results/ 是附带的实际提取结果，run.log 保存命令输出。原始输出的时间、程序版本与计算资源记录在 OUT 中。

重新计算时，从 QE 官方库准备 Si.pbe-n-rrkjus_psl.1.0.0.UPF，放在 si-pbe/pseudo/，并把各 run.sh 中的 <qe_bin> 改为实际程序位置。原始输入的相对路径按各计算子目录解释。保存目录由重新计算生成。

赝势：https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF
