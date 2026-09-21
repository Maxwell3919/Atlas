## 需要 / 产出

前置：DFPT 声子与插值已完成，手头有 `scc.dyn*`（ph.x 原始 q 点动力学矩阵）、`scc.fc`、`scc.freq`、`scc.freq.gp`（matdyn 插值色散）。本步只做读数诊断：定位虚频、判断是 ASR 残余还是结构软模，并处理下游 `lambda.x` 的 NaN 故障链。

## 本步与相邻步骤不同之处

DFPT 声子一章管"怎么算出 dyn/freq"；本章管"负值出现后怎么办"。电声 α²F 一章管 λ/Tc 读数；本章管"λ 有数但 ω_log、Tc 全 NaN"的故障链——根因排查、备份置零、重跑验收都在这里。

## 参数（只列本步）

无新计算参数。判读阈值：|ω|>1 cm⁻¹ 以下当数值噪声。ASR 相关开关在 q2r/matdyn：`zasr='crystal'`、`asr='crystal'`。

## 命令与输出

无 python3 环境下的逐行负频检查（awk 一行）：

```bash
awk '{for(i=2;i<=NF;i++) if($i+0<-1.0){print FILENAME, NR, $0; next}}' scc.freq scc.freq.gp
```

ASR 设置确认：

```bash
grep -nEi 'asr|zasr' q2rx.in matdynxline.in lambdax.in
q2rx.in:2:zasr='crystal'
matdynxline.in:2: asr='crystal'
```

Γ 点残余实锤（dyn 原始 q 点）：

```
./scc.dyn1 | q = ( 0.000000000 0.000000000 0.000000000 ) | ω=-20.939 cm-1
```

## 后处理

本例四层证据的判读：

| 文件 | 结果 | 含义 |
| --- | --- | --- |
| scc.dyn1 | −20.9 cm⁻¹ ×2 支 | Γ 声学支 ASR 残余 |
| scc.dyn2–10 | 无 |ω|>1 负频 | q 网格无真软模 |
| scc.freq（已 asr） | 无 |ω|>1 负频 | ASR 已压掉 |
| scc.freq.gp | 5 点 −1.1～−1.8，都在 Γ 附近 | 插值/声学支数值噪声 |

结论路径：只有 Γ 一对虚频、其余 q 干净、加 asr 后插值端只剩约 −2 cm⁻¹ → ASR 残余，不是结构失稳。−21 cm⁻¹ 略偏大（理想常 <10 cm⁻¹），但力常数整体可用；只有虚频连成段（整条支深于几十 cm⁻¹）才是真软模，那要回头查结构弛豫与 k 收敛。

下游逐模读数（λ.x 输出，按模编号）：

```
lambda( 4)= 0.1611 gamma= 165.60 GHz
lambda( 5)= 0.1364 gamma= 140.28 GHz
lambda( 7)= 0.5848 gamma= 1116.94 GHz
```

声学支 λ≈0 属正常；贡献集中在少数几支。

## 失败与假阳性

- NaN 故障链：Γ 负频 → `elph_dir/elph.inp_lambda.1` 第 2/3 行 w²=−0.364091E−07 → λ.x `sqrt(w²)` 得 NaN → α²F 全 NaN → ω_log、Tc 全 NaN；λ 列照常打印（`lambda = 1.068245 ( NaN ) = NaN K`），极具迷惑性。
- 只看 `scc.freq` 得出"无虚频"是假阳性：它已过 asr，必须回 dyn 原始值复核。
- 别因 −2 cm⁻¹ 量级噪声重跑整套 ph.x；收益小，且 ASR 已能压住。
- 修复记录：`cp -a elph_dir elph_dir.bak_w2` 备份 → awk 置零 NR==2||NR==3 的负 w²（声学支 λ 本来≈0，几乎不动 λ，只救 ω_log）→ 重跑后 λ=1.06825、ω_log=327.576 K 全部恢复有限值。

## 可选脚本 + 检查清单

```bash
# 分层扫描：dyn 原始 q 点 + 插值色散
chk_imag() {
  d="${1:-.}"
  awk '/^[[:space:]]*q =/ { q=$0; f=FILENAME }
       /freq (|omega(/ { cm=$8+0
         if (cm < -1.0) printf " %s | %s | ω=%.3f cm-1\n", f, q, cm }
       END { if(!n) print " no imag in dyn (|ω|>1 cm-1)" }' "$d"/scc.dyn*
  for f in "$d"/scc.freq "$d"/scc.freq.gp; do
    [ -f "$f" ] || continue
    awk '{ for(i=2;i<=NF;i++) if($i+0<-1.0) { c++; if(c<=20) print " ", $0 }
    } END { if(!c) print " no imag"; else print " imag lines:", c+0 }' "$f"
  done
}
```

清单：

- [ ] dyn 原始值与插值色散两层都查过
- [ ] 虚频只在 Γ 一对 → 判 ASR 残余；连成段 → 判结构软模并回头查弛豫
- [ ] `elph.inp_lambda.*` 负 w² 只在 Γ（第 2/3 行）
- [ ] 置零前已备份 `elph_dir.bak_w2`，置零后 awk 复读确认
- [ ] 重跑 λ.x 后 α²F 无 NaN、ω_log 有限
