参考：

- QE 官方文档 INPUT_PW（calculation='nscf'）：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>
- FermiSurfer 项目主页：<https://github.com/FermiSurfer/FermiSurfer>

## 本页目标

在收敛自洽的基础上用密 k 网格做一次非自洽计算，得到费米面上的电子态密度与费米面文件，供 FermiSurfer 等 3D 费米面工具出图。读完本页你能：写 nscf 输入、跑 fs.x、核对 bxsf 产物。

## 前置

scf 已收敛（普通 32×32×1 网格即可）；`outdir/prefix` 与 scf 保持一致——nscf 直接读 scf 落盘的电荷密度，不再自洽迭代，所以很快（分钟级到小时级）。

## nscf 输入：相对 scf 只有四处增量

真实费米面链的 nscf 输入全文（`…/FS/nscf.in`）：

```fortran
&CONTROL
  calculation = 'nscf'         ! ① 非自洽：读 scf 电荷，只解 Kohn–Sham 方程
  outdir = './out/'
  prefix = '<prefix>'
  pseudo_dir = '<赝势库路径>'
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0, nat = 6, ntyp = 4,
  ecutwfc = 100, ecutrho = 800,
  input_dft = 'vdw-DF3-opt1'
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 2.0d-3             ! ② 展宽比 scf 的 3.7d-3 更细
/
&ELECTRONS
  conv_thr = 1.0000000000d-12  ! ③（nscf 无自洽循环，此键实际不参与迭代）
  mixing_beta = 4.0000000000d-01
/
ATOMIC_SPECIES
（与 scf 相同，略）
（替换为你的结构块：CELL_PARAMETERS / ATOMIC_POSITIONS）
K_POINTS automatic
  64 64 1 0 0 0                ! ④ 密网格：费米面分辨率由它决定
```

与 scf 的差异就四处：`calculation='nscf'`、k 网格 32³→64³、degauss 收细、以及**不再需要** `&ions/&cell` 空壳（离子不动了）。若做 DOS 需要严格全 BZ 采样，常再补 `nosym = .true.`——本例真实文件未加（对称约化在该用途下可接受），是否需要按后续画图工具的要求定。

## 费米面：fs.x

```fortran
&fermi
    outdir = './out/'
    prefix = '<prefix>'
/
```

```bash
fs.x -i fs.in > fs.out
```

fs.x 读取 nscf 落盘的本征值，输出 Xcrysden 格式的费米面文件：

```text
zrclscc_fs.bxsf
```

## 验收与出图

- nscf 输出末尾同样应有 `JOB DONE`；费米能级取输出里的 `the Fermi energy is` 行。
- `ls -lh` 确认 `.bxsf` 生成（几十 MB 量级，随网格变密增大）。
- bxsf 交给 FermiSurfer / XCrySDen 打开即可看 3D 费米面；先在 FermiSurfer 里把等能面值设为费米能级。

## 链路小结

```text
scf (32×32×1) → nscf (64×64×1) → fs.x → .bxsf → FermiSurfer
```

能带、DOS、费米面三者共用同一次 scf；nscf 之后的所有电子结构产品（bands.x、projwfc.x、fs.x）都只是换一种方式消费它的本征值。

## 思考

- 为什么费米面要用比 scf 更密的 k 网格？分辨率瓶颈在 nscf 还是在 scf？
- `nosym` 加与不加，对 DOS 积分和费米面文件各有什么影响？
- 若费米面穿过多条能带，bxsf 里如何区分它们？
