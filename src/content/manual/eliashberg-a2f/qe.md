参考：

- [PHonon：电声系数与 lambda.x](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html)
- [PHonon 用户指南](https://www.quantum-espresso.org/Doc/ph_user_guide/)

## 先看 λ 随展宽怎样变化

下面两条曲线来自 Sc₂C/ZrCl₂ 主算例 `ph64`、`ph96` 留存的 `lambda.dat`，对应密电子 k 网格 64×64×1 和 96×96×1；两者声子 q 网格同为 8×8×1。数据于 2026-09-22 重新读取。

![两个密电子网格下的 lambda 和公式 Tc 随展宽变化](/Atlas/figures/epc-broadening.svg)

两条线在部分区间几乎重合，却都继续随展宽变化。网格之间接近与展宽方向形成平台，是两件不同的事。图中 Tc 是留存输出中的公式值，不能当作已经收敛的预测值。

## lambda.x 读取什么

本算例输入原文如下：

```text
[<user>@<cluster> ph64]$ cat lambdax.in
10  0.12  1    ! emax (something more than highest phonon mode in THz), degauss, smearing method
    10         ! Number of q-points for which EPC is calculated,
    0.00000000  0.00000000  0.00000000   1.00  ! the first q-point, use kpoints.x program to calculate
    0.00000000  0.14433757  0.00000000   6.00  ! q-points and their weight
    0.00000000  0.28867514  0.00000000   6.00  !
    0.00000000  0.43301270  0.00000000   6.00  ! 4th q-point, qx,qy,qz
    0.00000000 -0.57735027  0.00000000   3.00  !
    0.12500000  0.21650635  0.00000000   6.00  !
    0.12500000  0.36084392  0.00000000  12.00  !
    0.12500000  0.50518149  0.00000000  12.00  !
    0.25000000  0.43301270  0.00000000   6.00  !
    0.25000000  0.57735027  0.00000000   6.00  ! the last q-point
elph_dir/elph.inp_lambda.1 ! elph output file names,
elph_dir/elph.inp_lambda.2 ! in the same order as the q-points before
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
elph_dir/elph.inp_lambda.9
elph_dir/elph.inp_lambda.10
0.1                      ! \mu the Coloumb coefficient in the modified
                         ! Allen-Dynes formula for T_c (via \omega_log)
[<user>@<cluster> ph64]$
```

q 点、权重和文件顺序必须逐项对应上游清单；不能从这段数字外观就猜坐标约定。尤其要核对权重总和与完整网格的关系，再按运行版本读取 lambda.x 的说明。这里保留原始输入用于复核，不将其认定为已经通过输入审计的通用模板。

## 按表头读数

```text
[<user>@<cluster> ph64]$ head -n 4 lambda.dat; tail -n 3 lambda.dat
# degauss   lambda    int alpha2F  <log w>     N(Ef)
  0.001    2.940003    2.902508    97.625   32.317854
  0.002    2.062339    2.025444   100.907   29.723113
  0.003    1.837986    1.801992   101.797   29.244028
  0.018    0.840009    0.795808   118.455   24.677094
  0.019    0.817430    0.772534   119.438   24.729924
  0.020    0.796142    0.750607   120.400   24.781569
[<user>@<cluster> ph64]$
```

第二列是 λ，第三列的表头为 `int alpha2F`，第四列为 `<log w>`。不要把第三列随意叫作“分解部分”。同目录 `lambdax.out` 给第四列标注 K；展宽列标注 Ry。

在 0.001 Ry 与 0.020 Ry 两端，λ 从 2.940003 变到 0.796142。这个变化不能靠挑选较大的展宽或取区间平均消除。更正（2026-09-22）：旧文中 λ≈0.31、ω_log≈259 K 的片段不属于本次核对的这张主算例表，已从这条教案主线移出。

## 谱函数和累计耦合分开看

`alpha2F.dat` 记录随频率分布的谱函数；累计 λ(ω) 需要对 α²F(ω)/ω 积分，并核对频率单位与零频处理。谱峰高低与某频段对总 λ 的贡献并非同一个读数。先确认文件布局：本目录二十档展宽的数据存在换行，不能把每个物理频率误当作两条独立记录。

## 下一步

进入[Allen–Dynes 页](/Atlas/m/allen-dynes/qe/)，把 λ、ω_log 与选定的 μ* 一起对应到同一行，再检查公式估计对数值设置的敏感性。

```text
逐 q 电声数据 → lambda.x → lambda.dat / alpha2F.dat
                                  ↓
                 网格、权重、单位与展宽逐项核对
                                  ↓
                       同一行的 λ、ω_log → Tc
```
