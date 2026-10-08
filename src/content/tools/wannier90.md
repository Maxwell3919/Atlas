# Wannier90：从 QE 接口文件检查电子模型

电子结构程序给出采样点上的 Bloch 态，Wannier90 用选定带与投影构造可插值的电子模型。先检查子空间与接口，再检查独立点误差；局域化结束不等于费米面、速度或耦合收敛。本站 [Si 实例](/Atlas/m/wannier90/qe/)是四条隔离价带，不能直接当作金属的近费米模型。

## 安装和版本先分开记录

[官方 3.1.0 安装说明](https://github.com/wannier-developers/wannier90/blob/v3.1.0/README.install)要求 Fortran、BLAS/LAPACK 与 GNU make，配置由 `make.inc` 指定，`make wannier` 构建 `wannier90.x`。在已下载 3.1.0 源码、核对编译器和库之后，可从 `config/make.inc.gfort` 等模板配置，并用 `make -j2 wannier`；这不是本页已完成的安装记录。本轮没有安装或运行 Wannier90。

公开 `k4/silicon.wout` 标明 Wannier90 3.1.0，`si.scf.out` 与接口输出来自 QE 7.5。记录两个版本，不能只记录一个“QE 版本”。复跑还需匹配的 NSCF save 和波函数，文本包不替代它们。

## 文件怎样连接

[3.1.0 文件说明](https://github.com/wannier-developers/wannier90/blob/v3.1.0/doc/user_guide/files.tex)和[预处理说明](https://github.com/wannier-developers/wannier90/blob/v3.1.0/doc/user_guide/wannier-pp.tex)把接口分成两步：`wannier90.x -pp silicon` 从 `silicon.win` 生成 `silicon.nnkp`；QE 的 `pw2wannier90.x` 读取自己的接口输入及 NSCF 父态，写 `silicon.amn/mmn/eig`；之后 `wannier90.x silicon` 才进行局域化及所请求的插值。这里 `silicon` 是同一 seed，不是任意目录名。

| 输入与输出 | 本例用途 | 出错时先核什么 |
|---|---|---|
| `silicon.win → silicon.nnkp` | 完整 k 点、近邻及投影 | seed、k 点顺序、预处理是否完成 |
| `si.nscf.in/out` 与 save → `silicon.amn/mmn/eig` | 同一组 Bloch 态的投影、重叠和能量 | prefix/outdir、带数、网格和父波函数 |
| 接口文件 → `silicon.wout`、`silicon_hr.dat`、`silicon_band.dat` | 局域化与电子插值 | 窗口、投影、维度和独立 DFT 对照 |

QE 7.5 [接口源码](https://github.com/QEF/q-e/blob/qe-7.5/PP/src/pw2wannier90.f90)提供实际读取与错误检查。遇到找不到文件或维度不一致，不要只改扩展名或拼另一套网格的矩阵；回到同一 seed、父态和完整 k 点列表。3.1.0 安装说明还提醒：缺少 `EXIT_FLAG` 时退出码未必能可靠表示错误，所以必须看 `wout` 内容。

## 不启动计算的小检查

下载 [Si 文本包](/Atlas/examples/si-wannier-lesson-files.tar.gz)，先查看成员，再解包到新目录，保持顶层 `si-wannier/`。在该目录运行以下 Python 标准库检查；它不读波函数、不生成新能带。本轮已在现有公开文件上执行同一检查。

```bash
python3 - <<'PY'
from pathlib import Path
for label, nk in [('k4', 64), ('k6', 216)]:
    rows = [line.split() for line in (Path(label)/'silicon.eig').read_text().splitlines() if line.strip()]
    assert len(rows) == 4*nk
    assert {(int(r[0]), int(r[1])) for r in rows} == {(b,k) for k in range(1,nk+1) for b in range(1,5)}
    assert 'Release: 3.1.0' in (Path(label)/'silicon.wout').read_text()
    print(label, len(rows), 'energy rows; four bands; Wannier90 3.1.0')
PY
```

实际检查为 `k4` 256 行、`k6` 864 行。这只确认保存的能量接口覆盖；误差与能量零点仍应读 [Si 完整教程](/Atlas/m/wannier90/qe/)。要把电子模型接到位移响应，继续看 [EPW 的额外输入](/Atlas/tools/epw/)。
