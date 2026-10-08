# GPAW：从 Python 输入到 PAW 能量与力

GPAW 是独立的密度泛函计算引擎，ASE 负责结构、优化器和文件接口。本页使用 **GPAW 26.7.0 / ASE 3.29.0** 的原生平面波 H₂ 小例，连接安装、可执行输入、完整输出与[能量—力核验案例](/Atlas/cases/gpaw-h2/)。它并非把已有程序的后处理重新命名为引擎。

## 先区分 Python 包与原生扩展

26.7.0 的[发行元数据](https://gitlab.com/gpaw/gpaw/-/blob/26.7.0/pyproject.toml#L22)要求 Python ≥3.10、ASE ≥3.29.0；本例实际为 Python 3.12.3、ASE 3.29.0、NumPy 2.2.6、SciPy 1.15.3、LibXC 5.2.3，串行、无 MPI/OpenMP。在线[安装指南](https://gpaw.readthedocs.io/install.html)会更新，版本要求以 26.7.0 源包为准。

GPAW 的 Python 层需要可加载的 `_gpaw` 编译扩展，以及相容的 LibXC 和 BLAS。仅 `import gpaw`、pip 元数据或纯 Python wheel 成功都不证明这个条件；缺 `xc.h`、`-lxc` 或运行时共享库时，应先解决原生前提。这里没有提供可跨机器直接使用的二进制 wheel。

以下为读者在自己的 Linux 隔离环境中重建的步骤，未在本网页编辑任务中执行。先备好 Python 开发头文件、C/C++ 编译器、BLAS 与 LibXC 5.2.3 的开发头文件及共享库；路径与 ABI 必须属于本机。发行包来自[官方 26.7.0 源包](https://pypi.org/project/gpaw/26.7.0/#files)，SHA-256 为 `1509af00cfcd032bbbce197a5b3e37edb82bf458db5e200f6a105ec74efbca15`，下载后先核对，确认顶层为 `gpaw-26.7.0/` 再解包。

```bash
python3.12 -m venv gpaw-env
. gpaw-env/bin/activate
python -m pip install 'numpy==2.2.6' 'scipy==1.15.3' 'ase==3.29.0' \
  'setuptools==80.9.0' 'wheel==0.45.1' 'pybind11==2.13.6'
# 当前目录已有核对过的 gpaw-26.7.0.tar.gz；解包到新目录。
tar -xf gpaw-26.7.0.tar.gz
```

将下面的 `siteconfig.py` 放在工作目录。将 `libxc_prefix` 改成本机已验证的 LibXC 安装前缀；如发行版库布局为 `lib64` 或多架构目录，也要对应修改。BLAS 必须能被本机链接器找到。

```python
libxc_prefix = '/your/local/libxc-5.2.3'
compiler = 'g++'
mpi = False
scalapack = False
fftw = False
libraries = ['xc', 'blas']
include_dirs = [libxc_prefix + '/include']
library_dirs = [libxc_prefix + '/lib']
runtime_library_dirs = [libxc_prefix + '/lib']
```

本例曾遇到构建产物不能提供可用原生扩展的问题；实际修复采用标准串行 setuptools wheel 流程，而非把前提失败算成安装通过。下面对应已执行的构建顺序，路径换为读者本地工作目录。

```bash
export GPAW_CONFIG="$PWD/siteconfig.py" GPAW_BUILD_JOBS=1
mkdir built-wheels
cd gpaw-26.7.0
python -m pip wheel --no-index --no-build-isolation --no-deps \
  --wheel-dir ../built-wheels . -v
cd ..
python -m pip install --no-index --no-deps built-wheels/gpaw-26.7.0-*.whl
python -c "import gpaw, ase, _gpaw; print(gpaw.__version__, ase.__version__, _gpaw.__file__)"
gpaw info
```

检查 wheel 确有 `_gpaw*.so`、加载路径属于该环境、动态链接器没有 `not found`，并核 `gpaw info` 的 LibXC/并行设置。原环境这几项已实际通过，且后续 H₂ 原生求解成功；它不证明另一台机器已安装成功。MPI 和通用主机服务未验证。相同输入的 Preston 固定设置验证已独立接受，见[案例中的跨主机观察与资源边界](/Atlas/cases/gpaw-h2/#h-preston-同输入验证与跨主机观察)；它不等于其他机器或材料精度认证。

## 可执行接口与物理选择

[完整输入 h2.py](/Atlas/examples/gpaw-h2/inputs/h2.py)有三个参数：`--stage smoke|relax|forcecheck`、`--setup-dir` 和 `--out`。它锁定 GPAW/ASE 版本，替换数据搜索路径，只接受一个 H.PBE 或 H.PBE.gz；输出目录已经存在会拒绝覆盖。精确输入哈希为 `bbcf810022eea28f1102eba9a8a3cc2c85723d260fcc4404731023a232e657e1`。文件头的历史 proposal 状态保留以维持字节，实际执行结果见案例的完整输出。

本例选择 PBE、PAW、PW(340 eV)、6 Å 立方周期盒、Γ 唯一 k 点、2 bands、零电荷、非自旋极化和零宽度占据。PW 需要周期边界；盒中 H₂ 是有限周期模型，未验证镜像误差。电子 SCF 的 `maxiter=60` 是停止上限，不是收敛证据。

[26.7.0 的 Energy/Density/Eigenstates 实现](https://gitlab.com/gpaw/gpaw/-/blob/26.7.0/gpaw/convergence_criteria.py#L122)分别检查：最近三次外推总能量按价电子数归一化后的峰—峰差 <10⁻⁶ eV/价电子；密度变化绝对值积分按价电子数归一化 <10⁻⁶ electrons/价电子；Kohn–Sham 残差平方积分按价电子数归一化 <10⁻⁸ eV²/价电子。第三项不是本征值相邻步差。读取原生 SCF 表的收敛标记与 `Converged`，不要用脚本退出码代替。

## 移动原子时的对称性错误

以初始结构建立点群后，优化或单原子位移可能破坏原点群；`Broken symmetry!` 一类检查失败要保留失败结果。此例被接受的完整纠正输入已明确使用：

```python
symmetry='off'
```

该选项关闭点群及利用时间反演的 k 点约化，见[同版本参数处理](https://gitlab.com/gpaw/gpaw/-/blob/26.7.0/gpaw/old/calculator.py#L1177)与[Symmetry 实现](https://gitlab.com/gpaw/gpaw/-/blob/26.7.0/gpaw/symmetry.py)。这不是物理时间反演破缺；这里仍为 Γ 单点、权重 1。不要把其他模型的修复或未运行建议当作本例实际结果。

## 数据与许可证

[H.PBE.gz](/Atlas/examples/gpaw-h2/data/H.PBE.gz)来自 [gpaw-data 1.2.1](https://pypi.org/project/gpaw-data/1.2.1/)，哈希 `e16130c5eb16325a4404f46be86182a4b0f468038ae5c8ab9ffc777a2993fd1d`。本页随例保留 [GPAW notice](/Atlas/examples/gpaw-h2/licenses/GPAW-LICENSE)、[数据 notice](/Atlas/examples/gpaw-h2/licenses/gpaw-data-LICENSE)、[GPL-3.0 全文](/Atlas/examples/gpaw-h2/licenses/GPL-3.0)及 [ASE notice](/Atlas/examples/gpaw-h2/licenses/ASE-LICENSE)。GPAW、改编输入及 PAW 数据为 GPL-3.0-or-later；ASE 为 LGPL-2.1-or-later。许可证范围不等于计算结论的准确性保证。继续阅读[完整复现与结果检查](/Atlas/cases/gpaw-h2/)。
