## 需要 / 产出

结构目录完成 `rx`（vc-relax）与 `pwx`（SCF）后，在电声目录（如 `ph64/`）内按序产出：

- `pwx.out`（给 ph.x 准备 outdir 的 SCF）与 `pwxall.out`（密 k + `la2F=.true.`，必须在 ph.x 之前）
- `phx.out`（q=1）→ `phx1.out`（q=2–4）→ `phx2.out`（q=5–7）→ `phx3.out`（q=8–10）
- `q2rx.out` → `scc.fc`、`dyna2F`；`matdynxline.out`（线模色散）→ `scc.freq`、`scc.freq.gp`、`matdyn.modes`
- 电声副产物：`elph_dir/elph.inp_lambda.1–10`、`elph.gamma.1–10`

## 本步与相邻步骤不同之处

本步是 DFPT 声子本身（ph.x → q2r → matdyn）；λ/Tc 读数与 NaN 诊断是它的下游（分别见电声与虚频两章）。`ph64` 与 `ph96` 的区别只在 pwxall 的 k 网格（64 64 1 vs 96 96 1），q 网格都是 8 8 1。

## 参数（只列本步）

- q 网格 8 8 1，不可约 q 共 10 个（对应 elph 文件 .1–.10）。
- ph.x 分四段提交：q=1、q=2–4、q=5–7、q=8–10，四段共用同一 outdir 与 `scc.dyn*`。
- q2r 用 `zasr='crystal'`；matdyn 线模版用 `asr='crystal'`。
- 完整 &PHONON/&ELECTRONS 输入模板：待填充。

## 命令与输出

六段作业验收（脚本见文末）：

```
==== <电声目录>/ph64 ====
[DONE] pwxall.out
[DONE] pwx.out
[DONE] phx.out
[DONE] phx1.out
[DONE] phx2.out
[DONE] phx3.out
```

单文件验收看尾部标志：

```
=------------------------------------------------------------------------------=
JOB DONE.
=------------------------------------------------------------------------------=
```

ASR 相关行 grep 实录：

```
q2rx.in:2:zasr='crystal'
matdynxline.in:2: asr='crystal'
```

## 后处理

六个 out 全 DONE 后，在同一目录串行提交 `q2rx.slurm → matdynxline.slurm → lambdax.slurm`。产物对号：`scc.dyn0`–`scc.dyn10`（原始 q 点）、`scc.fc`（q2r 力常数）、`scc.freq`/`scc.freq.gp`（插值色散）、`matdyn.modes`（含本征矢）。画谱用线模输出；查虚频回 dyn 原始值（见虚频一章）。

## 失败与假阳性

- 四段 ph.x 理论上可并行（前段结束即交后段），但共用同一 outdir 与 `scc.dyn*`；I/O 不稳时跑完一段再交下一段。
- 某个 out 没有 JOB DONE 也没有 Error，多半是没跑完，别急着交 q2r。
- q2r 没做时 matdyn 读不到 `scc.fc`，会给出错误谱而不报错——交 matdyn 前先确认 `scc.fc` 存在。

## 可选脚本 + 检查清单

```bash
# pwxall 到 phx3 六段验收
chk_epc() {
  d="$1"
  echo "==== $d ===="
  for f in pwxall.out pwx.out phx.out phx1.out phx2.out phx3.out; do
    p="$d/$f"
    if [ ! -f "$p" ]; then echo "[NO OUT] $f"; continue; fi
    if grep -q "JOB DONE" "$p"; then st=DONE
    elif grep -qiE "Error|CRASH|stopped" "$p"; then st=ERROR
    else st=RUN/INCOMPLETE; fi
    echo "[$st] $f"
  done
}

# 全树盘点：哪些 out 有/没有 JOB DONE
find . -name '*.out' | while read -r f; do
  grep -q "JOB DONE" "$f" || echo "$f"
done
```

清单：

- [ ] pwxall、pwx、phx、phx1/2/3 六个 out 全部 JOB DONE
- [ ] `elph_dir/elph.inp_lambda.1–10` 与 `elph.gamma.1–10` 齐全
- [ ] q2r 产出 `scc.fc`，matdyn 产出 `scc.freq`/`scc.freq.gp`
- [ ] zasr/asr='crystal' 已在 q2r、matdyn 输入中确认
- [ ] 全部 DONE 后才提交 q2r → matdyn → lambdax
