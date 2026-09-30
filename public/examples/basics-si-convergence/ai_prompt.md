# Si 总能量扫描的 Python 编程需求

读取随包提供的 si-pbe/*/scf.in、scf.out、scf.err 和 SHA256SUMS.raw，使用 Python 3 标准库生成数值表。

1. 校验原始文件的 SHA-256；读出 QE 版本、原子数、输入截断和网格，核对 OUT 截断回显。
2. 完整样本同时具有唯一最终 ! total energy、SCF convergence has been achieved 和 JOB DONE；不完整目录保留在运行清单。
3. 分别处理 cutoff40…cutoff80、rho320/rho480/scf、k4…k14 三条轴。核对结构、赝势、占据、电子阈值及其他固定参数相同。scf/cutoff60/k8 是等效基准副本，在同组中只计一次。
4. 每组最高采样点为参照。两个原子/原胞，1 Ry=13.6056931229905 eV；参照差与相邻差都转为 meV/atom。以1 meV/atom选择参照差及后续相邻差均满足的最低设置。
5. 输出 convergence.csv、run-inventory.csv、scf-history.csv、summary.json、source-files.json 和 energy-report.md。输入文件保持原样，输出目录由 --outdir 指定。
6. 报告三个独立扫描的固定条件和实际选点。最高点作为有限参照；独立最低设置尚未组合运行。力、应力或其他目标量由相应数据另行比较。

脚本只提取已有结果，不调用 QE。源码应完整可读，可使用同包的 analyze_si_convergence.py 对照。
