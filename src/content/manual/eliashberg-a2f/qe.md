参考：

- QE PHonon 用户指南（lambda.x 章节）：<https://www.quantum-espresso.org/Doc/user_guide/>
- Giustino, *Electron-phonon interactions from first principles*, Rev. Mod. Phys. 89, 015003 (2017)

## λ(ω) 谱函数：lambda.x

lambda.x 是 EPC 链的收口程序：把逐 q 的电声矩阵元汇总成 Eliashberg 谱函数 α²F(ω)、总耦合强度 λ 与对数平均声子频率 ω_log。这一页把它的输入文件逐行讲透，再讲输出怎么读。

## 输入文件：lambdax.in 逐行讲

真实文件全文如下（数值均为实测体系 Sc2C/ZrCl2 链的原值）：

```text
10  0.12  1    ! emax (THz，取比最高声子模略高), lambda.x 自身展宽 degauss, 展宽类型
    10         ! 参与计算电声矩阵元的 q 点总数
    0.00000000  0.00000000  0.00000000   1.00  ! 第 1 个 q 点（Γ），qx qy qz + 权重
    0.00000000  0.14433757  0.00000000   6.00  ! q 点与其简并度权重
    0.00000000  0.28867514  0.00000000   6.00  !
    0.00000000  0.43301270  0.00000000   6.00  !
    0.00000000 -0.57735027  0.00000000   3.00  !
    0.12500000  0.21650635  0.00000000   6.00  !
    0.12500000  0.36084392  0.00000000  12.00  !
    0.12500000  0.50518149  0.00000000  12.00  !
    0.25000000  0.43301270  0.00000000   6.00  !
    0.25000000  0.57735027  0.00000000   6.00  ! 最后一个 q 点
elph_dir/elph.inp_lambda.1 ! 电声输出文件名，
elph_dir/elph.inp_lambda.2 ! 顺序与上面 q 点一一对应
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
elph_dir/elph.inp_lambda.9
elph_dir/elph.inp_lambda.10
0.1                      ! μ*，Allen–Dynes 公式中的库仑赝势
```

要点：

- **q 点与权重**：8×8×1 网格按对称性约化成 10 个点，权重是星形简并度（如 12 对应两条镜面等价方向）。q 坐标用晶体坐标。
- **文件对应关系**：`elph.inp_lambda.N` 的 N 与 ph.x 分批的 q 编号一致——phx(q=1) 出第 1 份，phx1(q=2–4) 出第 2–4 份，以此类推。
- **头行三个数**：emax 单位是 THz，取略高于最高声子模即可；中间的 0.12 是 lambda.x 积分 α²F 用的自身展宽（与 ph.x 的 el_ph_sigma 那套展宽是两回事，别混）；第三个数选展宽类型。
- **μ\***：经验库仑赝势，0.1 是惯例起点，敏感性要单独扫（见 Allen–Dynes 页）。

## 运行

```bash
[<user>@<cluster> ph64]$ lambda.x -i lambdax.in > lambdax.out
```

## 输出逐项读法

输出里每档展宽一行（degauss 列来自 ph.x 的 el_ph_sigma×el_ph_nsigma 序列，0.001→0.020 Ry 共 20 档）：

```text
lambda = 0.312769 ( 0.224612 ) = 259.219 K N(Ef)= 22.787828 at degauss= 0.002
```

- `lambda`：总电声耦合强度（括号内为分解部分）
- `= 259.219 K`：ω_log，对数平均声子频率（单位 K）
- `N(Ef)`：费米面态密度（states/spin/Ry/unit cell）

输出末尾给出 α²F 谱数据文件（`alpha2F.dat`）与 Tc 列表。α²F(ω) 的读法：看 λ 随频率的累积在哪里陡升——低频声学支主导还是高频光学模主导，直接决定"软化驱动 vs 高频模驱动"的结论。

## 展宽序列怎么读

ph.x 的 `el_ph_sigma=0.001, el_ph_nsigma=20` 生成了 20 档展宽，输出就扫出 20 行。读表策略：**从大展宽（收敛端）往小展宽读**，λ/ω_log 随展宽变小而漂移，开始明显偏离平台的位置就是不可信区。实测无应变体系在可信窗内：

```text
lambda = 0.31277  259.219  ... 0.32205  261.564  ... 0.28630  257.419
```

λ 稳定在 0.31–0.32，ω_log 稳定在 259–262 K。同体系拉伸 3% 时 λ 从 0.54 漂到 0.36，窗口窄得多——展宽敏感性随体系变差，判读窗口要逐算例重定。

逐模线宽也在输出里（Γ 点）：

```text
lambda( 4) = 1.1124 gamma = 1534.64 GHz
lambda( 7) = 3.5962 gamma = 9215.98 GHz
```

## 常见故障

若输出全为 NaN：几乎都是某个 `elph.inp_lambda.N` 里负 w² 被 sqrt 放大成 NaN（诊断与修复见虚频/软模判据页——备份 elph_dir、awk 置零、重跑即恢复）。

## 下一步

```text
lambda.x（本页）
    ↓ λ / ω_log / μ*
Allen–Dynes Tc（含双网格判据）
```
