# Phonopy：从超胞力到力常数，再检查声子

有限位移路线用一个小位移引起的原子力构造力常数。Phonopy 组织超胞、位移、力与声子后处理；电子程序仍负责计算力。它与 QE 的 DFPT 路线可以检查同一材料的不同数值协议，但两条路线的文件不能仅凭分支编号混接，更不能用力常数代替电子–声子势响应。

## 版本与隔离安装

公开 Al `phonopy_params.yaml` 与 `summary.json` 记录 Phonopy **4.5.0**。本页依据 [4.5.0 安装说明](https://github.com/phonopy/phonopy/blob/v4.5.0/doc/install.md)、[QE 接口说明](https://github.com/phonopy/phonopy/blob/v4.5.0/doc/qe.md)和[同版本 load 源码](https://github.com/phonopy/phonopy/blob/v4.5.0/phonopy/cui/load.py)，不把持续更新的在线说明当作旧版本验收。

读者可在独立 conda 环境安装匹配版本，例如 `conda create -n phonopy-450 -c conda-forge phonopy=4.5.0`，激活后用 `python -c 'import phonopy; print(phonopy.__version__)'` 核身份。求解依赖和平台可用性须由实际安装验证；本轮没有安装或独立运行 Phonopy。下面的软件命令属于可复跑说明，保存结果只作为历史证据。

## 超胞、位移和力要保持一一对应

同版本 QE 接口读取显式晶格的 `ibrav=0` 结构。`phonopy-init --qe -d --dim="2 2 2" -c 单胞.in` 生成位移超胞与 `phonopy_disp.yaml`；位移结构的电子计算应是固定几何求力，不能把每个结构先 relax 再拿最终力拟合原位移。`phonopy-init -f 输出1 输出2` 用与位移顺序一致的 QE 输出生成 `FORCE_SETS`，后处理读取这些关系。

本站 [Al 已有有限位移数据](/Atlas/examples/al/finite-disp/n2-d0.01/phonopy_params.yaml)保存 2³ 原胞超胞、两份正负 0.01 Å 位移，以及力常数；配套 [位移表](/Atlas/examples/al/finite-disp/n2-d0.01/phonopy_disp.yaml)、[第一份求力输出](/Atlas/examples/al/finite-disp/n2-d0.01/disp-001/al.scf.out)、[第二份求力输出](/Atlas/examples/al/finite-disp/n2-d0.01/disp-002/al.scf.out)和[分析脚本](/Atlas/examples/al/finite-disp/analyse.py)保存真实父链。脚本使用 ASE 将 QE 输出的力读为 eV/Å；保存 YAML 的晶格为 Å、力常数为 eV/Å²。不要把未转换的 Ry/bohr 直接塞进这个接口。[4.5.0 原生 QE 解析器](https://github.com/phonopy/phonopy/blob/v4.5.0/phonopy/interface/qe.py)读出的力仍为 Ry/bohr，并减去各输出的平均力；若接入本例 Å/eV 的 API，需要一次明确单位转换。原生 `--qe` 的 Bohr 路线与此处 ASE/Å 路线应分别记录，不能一边换单位、一边再按另一套默认频率因子处理。

常见失败先检查：输出没有完整力块、原子数/顺序不同、输出与位移文件错配、晶格单位错误、刚体漂移和截断/超胞不足。原子质量进入动力学矩阵；临时改质量“消除虚频”改变了模型。力常数对称化也不能代替超胞、位移幅度和电子求力收敛。

## 从保存的力常数做最小重读

从上方链接下载 `phonopy_params.yaml` 到新目录，并在匹配环境运行：

```bash
python3 - <<'PY'
import phonopy
assert phonopy.__version__ == '4.5.0'
ph = phonopy.load('phonopy_params.yaml', produce_fc=False, symmetrize_fc=False, primitive_matrix='P')
ph.run_qpoints([[0,0,0], [.5,0,.5]], with_eigenvectors=True)
print(ph.qpoints.frequencies)  # THz，Γ 与 X，三条声学分支
PY
```

输入是已保存的力常数，不重新拟合或启动 QE；默认加载参数仍应同原生 YAML 和版本一起检查。[历史摘要](/Atlas/examples/al/finite-disp/n2-d0.01/summary.json)的对称化 X 点频率约为 6.356939、6.356939、9.842140 THz，Γ 仅有近零残差。本页未把这段重读标为本轮执行通过，也没有据此接受材料收敛。与 [DFPT 教程](/Atlas/m/phonon-dfpt/qe/)比较时，保留两条父链各自的网格、超胞和对称化约定。

查看运动方向可打开 [公开 Si Γ 模式互动](/Atlas/tools/si-modes/)。该互动读取另一份 QE 7.5 的原生模式和 AXSF，是跨材料的可视化教学，既不是本页 Al 的模式，也不是 Phonopy 重算结果。
