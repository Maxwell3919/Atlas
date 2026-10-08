# ABINIT：从固定 H₂ 输入读出原生 SCF

[延伸案例：收紧 SCF 后的 10 / 20 Ha 两点敏感性](/Atlas/cases/abinit-h2-sensitivity/)——读取完整输入、能量与力差、原图和相邻 CSV；两点不等于基组收敛。

ABINIT 是独立电子结构主引擎。本页以一个真实保存的 NC-LDA H₂ 固定几何 SCF 说明输入、原生输出与停止条件；[案例与完整数值表](/Atlas/cases/abinit-h2/)保留告警和精度边界。它没有做结构优化、基组或盒长收敛，也不把另一引擎的 PBE 能量当作答案。

## 实际版本与安装范围

保存结果来自 Ubuntu 24.04 amd64 的 `abinit 9.10.4-2ubuntu3`，原生程序报告 `9.10.4`。这是 MPI 链接的 Ubuntu 构建，实际测试为直接启动一个进程，没有 `mpirun`；不是自行编译的串行版本。原生日志明确提示该旧版本已不受支持。以下固定版本路线用于复现已有记录，不是最新生产版本推荐；官网[安装入口](https://docs.abinit.org/installation/)与[Ubuntu Noble 包及依赖](https://packages.ubuntu.com/noble/abinit)用于核对适用系统。

执行环境曾用 `dpkg-deb --extract` 将官方包展开到任务目录，并补齐本地 netCDF-Fortran 与 libxc。下列命令为读者重建同一布局：不运行包维护脚本，不修改系统，不包含本站二进制分发。网站作者本轮没有安装或运行 ABINIT。实际安装身份核验、一次原生 SCF、保存结果独立验收是三个不同环节。完整执行下面的命令块；`set -eu` 只作用于子 shell，任一步失败立即结束该块。不要把子 shell 放入 `if`、`&&` 或 `||` 条件中运行，以免改变 `set -e` 行为。`ABINIT_ROOT` 在调用 shell 中导出为绝对路径，两个块在同一 shell 续用；换终端时须重新导出实际已核目录，不能依赖子 shell 内变量传播。

```sh
# Export in the calling shell: the subshell below cannot propagate variables back.
export ABINIT_ROOT="$PWD/abinit-9.10.4-local"
(
set -eu
case "$ABINIT_ROOT" in /*) ;; *) exit 1 ;; esac
mkdir "$ABINIT_ROOT"
cd "$ABINIT_ROOT"
mkdir packages program deps
curl -fL 'https://archive.ubuntu.com/ubuntu/pool/universe/a/abinit/abinit_9.10.4-2ubuntu3_amd64.deb' -o packages/abinit.deb
curl -fL 'https://archive.ubuntu.com/ubuntu/pool/universe/n/netcdf-fortran/libnetcdff7_4.6.0+really4.5.4+ds-3build2_amd64.deb' -o packages/netcdff.deb
curl -fL 'https://archive.ubuntu.com/ubuntu/pool/universe/libx/libxc/libxc9_5.2.3-1ubuntu1_amd64.deb' -o packages/libxc.deb
sha256sum -c <<'HASHES'
52d625d930f02589afc6d8230145d2d93e217e3aebee87ca934ddd87f39ad17a  packages/abinit.deb
dd3bebd8093b9110077467e7c37430253a61fc0f82347bdc5dd967bf77c9068b  packages/netcdff.deb
a0da6ac5ddcce78130b622f514ce9731d10d575d661404a119682939ffef8af6  packages/libxc.deb
HASHES
dpkg-deb --extract packages/abinit.deb program
dpkg-deb --extract packages/netcdff.deb deps
dpkg-deb --extract packages/libxc.deb deps
sha256sum -c <<'ELF'
4e83f055fdc2796b1fe1be75a8894aec5ffa2921fb14179ce3f8c914c1ee25d2  program/usr/bin/abinit
9e8fe96709d71af61b88ad88caff7db8899369162b96aee66ecd6a553a5370f9  deps/usr/lib/x86_64-linux-gnu/libnetcdff.so.7.1.0
34ddf244137e183cb6484fd6ae0571b284cdcd121b94f8303f995c3402600f43  deps/usr/lib/x86_64-linux-gnu/libxc.so.9.2.3
ELF
readelf -h -l -d program/usr/bin/abinit
LD_LIBRARY_PATH="$ABINIT_ROOT/deps/usr/lib/x86_64-linux-gnu" ldd "$ABINIT_ROOT/program/usr/bin/abinit" > ldd.stdout 2> ldd.stderr
# ldd can return zero even when a shared library is missing.
if grep -F 'not found' ldd.stdout; then
  printf '%s\n' 'Missing library: stop.' >&2
  exit 1
else
  test "$?" -eq 1  # grep error (exit 2) also stops the subshell.
fi
env -i HOME="$HOME" PATH=/usr/bin:/bin LC_ALL=C \
 LD_LIBRARY_PATH="$ABINIT_ROOT/deps/usr/lib/x86_64-linux-gnu" \
 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
 timeout --kill-after=5s 30s "$ABINIT_ROOT/program/usr/bin/abinit" --version \
 > version.stdout 2> version.stderr
printf '9.10.4\n' > expected-version.stdout
cmp -s expected-version.stdout version.stdout
printf '%s\n' 'Native identity and library gates passed; SCF not yet run.'
)
```

先确认 `/etc/os-release` 为 Ubuntu 24.04，`dpkg --print-architecture` 为 amd64。包依赖还包括宿主 BLAS/LAPACK、libc6、libgcc、libgfortran5、OpenMPI 和 mpi-default-bin；netCDF-Fortran 依赖 netCDF-C（libnetcdf19），其宿主解析链还含 HDF5 等库。本地展开这三个包并不会安装这些宿主依赖。`ldd` 任何 `not found`、加载器/ABI 错误或版本不符都应停止，不能称安装成功。已有环境上 `--version` 成功只验证原生身份和加载，不验证 SCF 或物理准确性。

## 输入、接口与一次小复现

[完整 h2.abi](/Atlas/examples/abinit-h2/inputs/h2.abi)源于[9.10.4 官方教程输入](https://github.com/abinit/abinit/blob/9.10.4/tests/tutorial/Input/tbase1_1.abi#L8-L44)，仅改变赝势目录和文件名定位。将 `inputs/` 与 `data/` 放在同一根目录；`pp_dirpath "../data"` 相对运行 cwd `inputs/`，对应精确 [H.psp8](/Atlas/examples/abinit-h2/data/H.psp8)。NC、标量相对论、LDA Perdew–Wang 赝势的默认 XC 为 `ixc=-1012`。`acell 10 10 10` 与 `xcart ±0.7` 用 Bohr；`ecut 10` 与 `toldfe 1d-6` 用 Ha；一个默认 Γ 点，`nstep 10` 是最多步数，`diemac 2` 是混合预条件设置。

只需要读记录时，直接打开[原生 stdout](/Atlas/examples/abinit-h2/outputs/h2.stdout)、[stderr](/Atlas/examples/abinit-h2/outputs/h2.stderr)和[完整 h2.abo](/Atlas/examples/abinit-h2/inputs/h2.abo)。若自行重跑，只在安装块成功后继续，另建空目录，勿覆盖这些保存结果。在调用 shell 中先导出实际预览或已发布站点的载荷根 URL，例如 `export ABINIT_PAYLOAD_URL='http://127.0.0.1:8765/Atlas/examples/abinit-h2'`（自己的 loopback 预览服务；本候选未发布）。命令块会下载两个原件并检查哈希；不要跳过校验。此块再次核 ELF、动态库和精确版本；下载/目录/输入哈希或原生进程（含 timeout）失败即结束，不进入后续解析，也不沿用旧输出作新成功证据：

```sh
(
set -eu
: "${ABINIT_ROOT:?Export the absolute verified extraction directory before this block.}"
: "${ABINIT_PAYLOAD_URL:?Export the actual preview/published payload root URL before this block.}"
case "$ABINIT_ROOT" in /*) ;; *) exit 1 ;; esac
mkdir rerun-h2
cd rerun-h2
mkdir inputs data outputs
sha256sum -c <<ELF
4e83f055fdc2796b1fe1be75a8894aec5ffa2921fb14179ce3f8c914c1ee25d2  ${ABINIT_ROOT}/program/usr/bin/abinit
9e8fe96709d71af61b88ad88caff7db8899369162b96aee66ecd6a553a5370f9  ${ABINIT_ROOT}/deps/usr/lib/x86_64-linux-gnu/libnetcdff.so.7.1.0
34ddf244137e183cb6484fd6ae0571b284cdcd121b94f8303f995c3402600f43  ${ABINIT_ROOT}/deps/usr/lib/x86_64-linux-gnu/libxc.so.9.2.3
ELF
readelf -h -l -d "$ABINIT_ROOT/program/usr/bin/abinit"
LD_LIBRARY_PATH="$ABINIT_ROOT/deps/usr/lib/x86_64-linux-gnu" ldd "$ABINIT_ROOT/program/usr/bin/abinit" > ldd.stdout 2> ldd.stderr
# ldd can return zero even when a shared library is missing.
if grep -F 'not found' ldd.stdout; then
  printf '%s\n' 'Missing library: stop.' >&2
  exit 1
else
  test "$?" -eq 1  # grep error (exit 2) also stops the subshell.
fi
env -i HOME="$HOME" PATH=/usr/bin:/bin LC_ALL=C \
 LD_LIBRARY_PATH="$ABINIT_ROOT/deps/usr/lib/x86_64-linux-gnu" \
 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
 timeout --kill-after=5s 30s "$ABINIT_ROOT/program/usr/bin/abinit" --version \
 > version.stdout 2> version.stderr
printf '9.10.4\n' > expected-version.stdout
cmp -s expected-version.stdout version.stdout
curl -fL "${ABINIT_PAYLOAD_URL%/}/inputs/h2.abi" -o inputs/h2.abi
curl -fL "${ABINIT_PAYLOAD_URL%/}/data/H.psp8" -o data/H.psp8
sha256sum -c <<'INPUTS'
7a5a8f556bd91817f239b0b9c11a5f307874f97d2ca708044ce4b75403dc1ded  inputs/h2.abi
af415463efe6cbd281cad1b3fda928016408ec401b0f2c671275fa8f19594983  data/H.psp8
INPUTS
cd inputs
env -i HOME="$HOME" PATH=/usr/bin:/bin LC_ALL=C  LD_LIBRARY_PATH="$ABINIT_ROOT/deps/usr/lib/x86_64-linux-gnu"  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1  timeout --kill-after=5s 120s "$ABINIT_ROOT/program/usr/bin/abinit" h2.abi  > ../outputs/h2.stdout 2> ../outputs/h2.stderr
printf '%s\n' 'Native process exited successfully; inspect logs and SCF criteria separately.'
)
```

输入为 `.abi` 与 PSP8；输出为 `.abo`、stdout/stderr 和原生派生文件。上面给出的是实际单进程调用形式，不保证新机器逐字相同结果，也不是本站已执行的新计算。不要把保存的 `run-metadata.json` 冒充新运行的元数据。

## 只处理保存结果与错误定位

[22 项公开文件索引](/Atlas/cases/abinit-h2/#h-公开文件与许可)提供可读原件而非压缩包替代。保持完整相对目录，先复制到新后处理目录，再执行标准库解析器；它不导入或运行 ABINIT：

```sh
# saved-abinit-h2 contains all 22 downloaded members in their listed layout.
cp -R saved-abinit-h2 postprocess-abinit-h2
cd postprocess-abinit-h2
python3 parse-native.py
# Inspect parser-state.json: failure must be null; process exit alone is insufficient.
# Optional, only with an already available matplotlib environment:
python3 plot-native.py
```

IN 是 `run-metadata.json`、两份日志与 `inputs/h2.abo`；OUT 是当前副本内的 `scf-ledger.csv`、`forces.csv`、`warnings.json`、`echoed-native-settings.json`、`native-criterion-checks.json` 和 `parser-state.json`。绘图另写 `figures/` CSV/PNG/SVG。这些操作覆盖副本中的派生文件，保留下载原件；网站集成没有运行它们。解析器核对 stdout/abo ETOT、连续迭代号、原生收敛标记、有限数、两次能差和完整力向量；未知标题、缺标记、非有限值或不一致会写失败状态，不能只看 Python exit code。找不到 PSP 首先核 cwd 与 `../data`；动态库缺失属于环境失败；达到 `nstep` 不等于达到 `toldfe`；告警单列阅读，不能删掉再判断成功。

## 密度警告和物理用途

初始密度在首次 ITER 之前的告警包含 1275 个严重负值点，正下限 `xc_denpos=1e-14`，最低为 `−3.4e-5 el/Bohr³`；这不是可直接忽略的舍入误差。[mkdenpos 非自旋分支](https://github.com/abinit/abinit/blob/9.10.4/shared/common/src/33_xc_lowlevel/m_drivexc.F90#L703-L717)把 `rho < +xc_denpos` 的值设为正下限，但 `numneg` 和最低值 `worst` 只统计 `rho < -xc_denpos`；[告警分支](https://github.com/abinit/abinit/blob/9.10.4/shared/common/src/33_xc_lowlevel/m_drivexc.F90#L773-L786)要求 `numneg>0` 且 `iwarn=0`。因此 1275 是严重负值告警计数，不是全部下限修改点数；`[-xc_denpos, +xc_denpos)` 中的值也可能被设为下限，却不触发这项告警。零可见告警不能证明没有这种下限修改。

按官方 9.10.4 标签源码，[rhotoxc 每次调用先置 iwarn=0](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L415-L425)；`iwarn` 只可能抑制[同一次调用的 ishift 循环](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L619-L630)内另一轮平移网格的严重负值告警。本例 `intxc=0`，只有[intxc=0 的单次网格遍历](https://github.com/abinit/abinit/blob/9.10.4/src/56_xc/m_rhotoxc.F90#L619-L620)，不会因此静默后续 SCF 的新调用。此处解释的是该标签源码；尚未证明它与实际 Ubuntu 9.10.4-2ubuntu3 构建所用源码逐字等价。

后续及最终 XC 裁剪前密度仍为 **UNKNOWN**：保存记录没有该时刻的 XC 工作缓冲区，下限附近的修改也不全由告警报告。不能从告警数或返回的密度文件倒推出完整修改次数、裁剪前最低值或最终未裁剪；UNKNOWN 不应归因于贯穿整个 SCF 的永久告警锁存。原始版本不受支持的 notice 也保留。

本例用于学习固定模型中 SCF 停止、文件和单位。已保存六步及原生 `toldfe` 标记，但 10 Ha/10 Bohr 并未完成基组或盒长准确性检验；净力抵消也不证明每个原子力准确，更不是材料或实验结论。[同版本教程](https://github.com/abinit/abinit/blob/9.10.4/doc/tutorial/base1.md)可查进一步参数含义，不能借用其中其他几何或原子化能替代本次结果。

## 许可与来源

ABINIT 使用 GPL-3.0-or-later；少量代码的其他许可须依[同版本 COPYING](https://github.com/abinit/abinit/blob/9.10.4/COPYING)及[Ubuntu copyright](/Atlas/examples/abinit-h2/licenses/ABINIT-Ubuntu-copyright)分别核对。H 赝势由 PseudoDojo 的[固定公开源码](https://github.com/abinit/pseudo_dojo/tree/4048962957711c04281ffe6c2bd2c96f0f7110aa)取得，CC BY 4.0，含[归属说明](/Atlas/examples/abinit-h2/licenses/H-NOTICE.txt)，不把 ABINIT GPL 自动套到数据上。本站仅提供已核公开输入、保存结果和后处理源，不分发 `.deb` 或可执行二进制。
