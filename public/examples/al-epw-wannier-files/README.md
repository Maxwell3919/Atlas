# Al: QE → Wannier → EPW 教学计算文件

程序版本：QE 7.5、EPW 6.0。物理模型：非相对论 NC LDA-PZ；一原子 fcc Al；40/160 Ry；父声子 q4³。最终电子粗网格12³，细积分24³/12³。数值收敛和材料预测均未被接受。

## 包中内容

- `inputs/`：完整输入；`inputs/parent/`保留产生父链所需的 dense SCF、响应 SCF、ph 和 q2r 输入。
- `runs/`：各次执行的纯文本输入、stdout、stderr及必要数值输出，包含失败/停止尝试。
- `derived/`：逐点能带误差、原生谱CSV、实空间衰减及声学阈值核对。
- `analyse_bands.py`、`analyse_final.py`：从包内纯文本证据重新提取CSV，不运行DFT。
- `tools/`：重跑准备脚本。脚本拒绝覆盖已有阶段目录。
- `PUBLIC-FILES.json`：公开副本与原始私有文件的内容哈希。路径/用户名/邮箱可脱敏，科学数值不改写。

## 从头重跑

先配置已有QE/EPW可执行文件和MPI；只在获分配或已授权的空闲资源上执行。下面命令会实际启动计算，不会自动提交调度任务。

```bash
python3 tools/download_pseudo.py
export QE_BIN=/path/to/qe/bin
export NPROC=8
bash tools/run_stage.sh parent
bash tools/run_stage.sh nscf
bash tools/run_stage.sh wannier
bash tools/run_stage.sh coarse
bash tools/run_stage.sh fine
bash tools/run_stage.sh bandcheck
bash tools/run_stage.sh phononcheck
```

父链带有ph.x双网格EPC参数，所以脚本先写32³的`tmp/al.a2Fsave`，再运行16³响应SCF并确认该文件未变，随后计算q4³声子。这张ph.x谱不进入后续EPW谱积分。若已有完整同协议父链，可将它放入`00-phonon`，运行`tools/collect_phonons.py 00-phonon phonon-save`后从nscf阶段继续。

Wannier阶段用1进程；粗EPC阶段复制同一Wannier运行的`al.ukk`、`al.bvec`、`al.mmn`、`al.win`并用NPROC进程执行。此拆分绕过本机已安装MPI版Wannier库与EPW单主进程库调用的冲突；不是每种编译都存在同一问题。后续细网格从同一批`*.fmt`和`al.epmatwp`继续，不混用另一轮文件。

完整重跑脚本经过语法和路径检查；科学程序的现场执行证据在`runs/`，重跑时仍需检查每一步原生输出。公开包不含赝势正文、波函数或响应势，下载赝势后核对SHA-256，其余重型文件由前序计算生成。

## 结果解释

`derived/epw-a2f-k12-q4-fine24-q12.csv`三列是频率meV、alpha2F、原生累计lambda。g直接求和lambda=.3507955；谱累计lambda=.3508982；两种离散汇总分别保留。旧4³电子粗网格的谱和未收敛1K能隙只作诊断，不是最终材料结论。48³/24³积分被停止，没有形成可比较的完成结果。最终ASR、低频阈值和全q网格频率由phonon-threshold-audit记录。
