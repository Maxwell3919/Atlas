参考：

- QE 官方文档 INPUT_MATDYN：<https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html>
- PHonon 用户指南：<https://www.quantum-espresso.org/Doc/user_guide/>

## 本页目标

声子谱跑完不等于结束：要逐支逐 q 检查有没有负频率，并判断负频是数值残差还是真实的结构失稳；另外在 λ/Tc 链上还有一个由负 w² 引发的 NaN 陷阱。读完本页你能：用一行命令扫负频、按证据判断虚频性质、把 λ.x 的 NaN 修好重跑。

## 前置

DFPT 声子链完成（见 DFPT 声子页），`zrclscc.freq` 与 `zrclscc.freq.gp` 已生成；Γ 点动力学矩阵 `scc.dyn1` 可读。

## 扫负频（一行命令，无需 python）

```bash
awk '{for(i=2;i<=NF;i++) if($i+0<-1.0){print FILENAME, NR, $0; next}}' scc.freq scc.freq.gp
```

把 `scc.freq` 换成你自己的频率文件即可；阈值 −1.0 cm⁻¹ 用来过滤接近零的数值噪声。真实命中示例（Γ 点附近）：

```text
scc.freq.gp 457 0.023094 -1.5221 11.1103 ...
chk_imag: ./scc.dyn1 | q = (0 0 0) | ω=-20.939 cm-1
```

## 判读：−20.939 cm⁻¹ 是不是失稳？

四层证据逐层看，不要只看一个数：

1. **量级**：只有 −20 cm⁻¹ 量级，且其余负值都在 −1～−2 cm⁻¹ 的噪声带内；真正的软模通常在 −100 cm⁻¹ 量级且随 q 连续下探。
2. **位置**：只出现在 Γ（q=0）。声学求和规则（ASR）的数值残差正是 Γ 点声学支不为零，插值程序还会再放大几 cm⁻¹。
3. **q 方向行为**：沿 M、K 方向没有伴随的连续软化谷——CDW 型失稳会沿特定波矢形成谷。
4. **对照**：同一结构更大网格的母体计算（如 96×96×1）在 Γ 干净无负 w²，说明负值来自插值/ASR，而非势能面本身。

四条都指向同一结论：这是 ASR 残差 + 插值假象，不是结构失稳；相应的 q2r/matdyn 已用 `zasr`/`asr='crystal'` 处理。反之，若量级大、沿特定 q 连续软化、母体也有，才进入「虚频驱动的不稳定性」讨论。

## 陷阱：负 w² 把 λ.x 打成 NaN

Γ 点的负频率在 EPC 输出里以 **w² 为负** 的形式出现：`elph_dir/elph.inp_lambda.1` 第 2/3 行记录了 `w² = -0.364091E-07` 这样的值。λ.x 对 w² 开方就得到 NaN，并污染整条链：

```text
alpha2F.dat 全为 NaN → lambda = NaN → omega_log = NaN → T_c = NaN
```

### 定位与修复

```bash
grep -n "w2" elph_dir/elph.inp_lambda.1 | head
```

修复：先备份，再把第 2、3 行的负 w² 置零，重跑 λ.x：

```bash
cp -a elph_dir elph_dir.bak_w2
awk 'NR==2||NR==3{for(i=1;i<=NF;i++) if($i+0<0) $i=0} {print}' elph_dir/elph.inp_lambda.1 > elph_dir/elph.inp_lambda.1.fixed
mv elph_dir/elph.inp_lambda.1.fixed elph_dir/elph.inp_lambda.1
```

重跑后输出恢复正常（真实记录：`lambda = 1.06825  327.576 ...`，NaN 消失）。注意：置零只对 ASR 残差量级的小负 w² 合理——它本应≈0；若负值大，说明结构本身有问题，应回到虚频判读去。

## 逐模读数

λ.x 输出还给出 Γ 点逐模式贡献，可直接定位强散射的声子支：

```text
lambda( 4) = 1.1124 gamma = 1534.64 GHz
lambda( 7) = 3.5962 gamma = 9215.98 GHz
```

`gamma` 是模式线宽（GHz），与逐模 λ 一起构成声子线宽分析的入口。

## 思考

- ASR 残差为什么总是落在 Γ 点？`asr='crystal'` 在 q2r/matdyn 两步各做了什么？
- 负 w² 置零在什么前提下才合理？如果 −w² 达到 −10²cm⁻¹ 量级还能这样处理吗？
- 插值程序为什么会在 Γ 附近放大几 cm⁻¹ 的假负频？
