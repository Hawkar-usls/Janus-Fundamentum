# R5 E9 — Integer-lattice NAE defect-flow decomposition and positive-layer barrier

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_NAE_DEFECT_FLOW__P_ZERO_UNIVERSAL_SHORTCUT_FALSIFIED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_INTEGER_LATTICE_L1_GRAVER_AUGMENTATION_GATE_2026-09-29_v1.0.md`
- `research/R5_E9_ODD_L1_PARITY_COSET_SOURCE_TRADE_NORMAL_FORM_2026-09-29_v1.0.md`

Checker:
- `experiments/r5_e9_integer_lattice_nae_defect_flow_positive_layer_barrier.py`

Scientific ceiling:

```text
THIS NOTE SHARPENS THE SOURCE-TRADE FRONTIER.
IT DOES NOT PROVIDE THE MISSING POLYNOMIAL SOURCE-TRADE ORACLE.
IT PROVES AN EXACT NAE-DEFECT DECOMPOSITION AND FALSIFIES THE SHORTCUT
THAT A GLOBAL L1 OPTIMUM CAN ALWAYS BE CHOSEN WITH NO POSITIVE OVERSHOOT.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A` be a square cubic 0/1 matrix: every row and every column has exactly
three ones. Let

\[
z\in\mathbb Z^n,\qquad Az=\mathbf 1.
\]

Define the nearest Boolean sign pattern

\[
b_i:=\mathbf 1[z_i\ge 1]
\]

and the correction

\[
g:=z-b.
\]

Then

```text
b_i=1 => g_i>=0,
b_i=0 => g_i<=0.
```

Write the disjoint nonnegative parts

\[
p_i:=\begin{cases}g_i,&b_i=1\\0,&b_i=0\end{cases},
\qquad
q_i:=\begin{cases}0,&b_i=1\\-g_i,&b_i=0.\end{cases}
\]

Thus

\[
g=p-q,
\qquad p,q\in\mathbb Z_{\ge0}^n,
\qquad \operatorname{supp}(p)\cap\operatorname{supp}(q)=\varnothing.
\]

## 2. Every integer lattice point induces a positive NAE coloring

Fix one source row with variables `i,j,k`. Since

\[
z_i+z_j+z_k=1,
\]

it is impossible that all three `b` values are zero: then all three `z` values
are at most zero and the row sum is at most zero.

It is also impossible that all three `b` values are one: then all three `z`
values are at least one and the row sum is at least three.

Therefore every row has Boolean weight exactly one or two.

### Theorem NDF-1

For every integer lattice point `z` with `Az=1`, the threshold vector `b` is a
positive NAE witness:

\[
\boxed{(Ab)_r\in\{1,2\}\text{ for every row }r.}
\]

Let

\[
T:=\{r:(Ab)_r=2\}
\]

be the set of two-one defect rows.

## 3. Exact defect-flow equation

Because `z=b+p-q` and `Az=1`,

\[
A(p-q)=\mathbf1-Ab.
\]

The right-hand side is zero on weight-one rows and `-1` on `T`. Hence

\[
\boxed{Ap-Aq=-\mathbf1_T.}
\]

Summing all rows and using column cubicity,

\[
3\|p\|_1-3\|q\|_1=-|T|,
\]

so

\[
\boxed{|T|=3(\|q\|_1-\|p\|_1).}
\]

In particular

\[
\boxed{3\mid |T|.}
\]

This divisibility is not an empirical property: it is forced by the exact
integer lattice equations.

## 4. Exact objective decomposition

If `b_i=1`, then `z_i=1+p_i` and

\[
|2z_i-1|=1+2p_i.
\]

If `b_i=0`, then `z_i=-q_i` and

\[
|2z_i-1|=1+2q_i.
\]

Therefore

\[
F(z)=n+2(\|p\|_1+\|q\|_1).
\]

Eliminating `||q||_1` with the defect identity gives

\[
\boxed{
F(z)-n
=4\|p\|_1+\frac{2}{3}|T|.
}
\]

### Corollary NDF-2

The global source-trade objective has two independent exact costs:

1. `2|T|/3` for NAE rows with two selected variables;
2. `4||p||_1` for positive integer overshoot beyond Boolean value one.

Thus minimizing only the NAE defect count is not, by itself, the original L1
problem.

## 5. The tempting p=0 shortcut

A natural hope is:

```text
Every lattice-feasible source has an L1-optimal point with p=0,
that is, no coordinate z_i exceeds 1.
```

If true, the objective would collapse to `n+2|T|/3` and every optimum would live
in `{-1,0,1}^n`.

The next control falsifies this exactly.

## 6. Frozen connected linear-cubic countercontrol

Use the 15 source rows below, in 1-based indexing:

```text
(1,15,12)
(2,14,4)
(3,2,8)
(4,3,9)
(5,4,6)
(6,12,10)
(7,1,3)
(8,9,15)
(9,7,5)
(10,8,7)
(11,5,2)
(12,13,14)
(13,11,1)
(14,6,11)
(15,10,13)
```

The checker proves exactly that the incidence matrix is connected, square,
linear, row-cubic and column-cubic, and has rational rank 14.

Define

\[
z_0=(-1,1,0,1,-1,1,2,0,0,-1,1,1,1,-1,1)^T
\]

and

\[
v=(-4,2,-1,2,-4,2,5,-1,-1,-4,2,2,2,-4,2)^T.
\]

Direct multiplication gives

\[
Az_0=\mathbf1,
\qquad
Av=0.
\]

Since `rank_Q(A)=14`, the rational solution set of `Az=1` is the affine line

\[
z=z_0+\lambda v.
\]

Coordinate 3 is `-lambda`. Hence every integer solution has
`lambda=k in Z`. Conversely every integer `k` gives an integer solution. Thus
**all** integer solutions are exactly

\[
\boxed{
z(k)=z_0+k v,
\qquad k\in\mathbb Z.
}
\]

Equivalently,

\[
z(k)=(-4k-1,\ 2k+1,\ -k,\ 2k+1,\ -4k-1,\ 2k+1,\ 5k+2,
-k,-k,-4k-1,2k+1,2k+1,2k+1,-4k-1,2k+1).
\]

## 7. Exact global L1 optimum

Grouping equal affine coordinate forms yields

\[
F(k)
=4|-8k-3|
+7|4k+1|
+3|-2k-1|
+|10k+3|.
\]

For `k>=0`, all signs are fixed and

\[
\boxed{F(k)=76k+25.}
\]

For `k<=-1`, all signs reverse in the required groups and

\[
\boxed{F(k)=-76k-25.}
\]

Therefore

\[
\boxed{\min_{k\in\mathbb Z}F(k)=25}
\]

uniquely at `k=0`.

Since `n=15`, this source is Exact-One UNSAT and has exact defect mass

\[
D=(25-15)/2=5.
\]

At the unique optimum `k=0`, the threshold decomposition has

```text
||p||_1 = 1,
||q||_1 = 4,
|T|     = 9,
```

and indeed

\[
25-15=4\cdot1+\frac23\cdot9=10.
\]

## 8. Positive overshoot is unavoidable

For every feasible integer point:

- if `k>=0`, coordinate 7 is `5k+2>=2`;
- if `k<=-1`, coordinates of form `-4k-1` are at least 3.

Hence

\[
\boxed{
\text{every integer solution has some coordinate }z_i\ge2.
}
\]

Equivalently,

\[
\boxed{
\|p\|_1>0\text{ for every feasible integer point.}
}
\]

So the universal shortcut

```text
GLOBAL L1 OPTIMUM CAN ALWAYS BE CHOSEN WITH p=0
```

is false even on a connected rank-14 linear-cubic 15-source.

## 9. Consequence for SOURCE_TRADE_AUGMENT

The positive-circulation layer is not removable by a generic clipping theorem.
A correct universal augmentation mechanism must handle genuine mass on both
sides:

\[
Ap-Aq=-\mathbf1_T,
\qquad p,q\ge0,
\]

and must be able to change both the NAE defect set `T` and the positive-overshoot
mass `p`.

This rules out replacing the global L1 gate by the finite-domain problem
`z in {-1,0,1}^n`.

The live gate remains

```text
R5_E9_LINEAR_CUBIC_SOURCE_TRADE_AUGMENTATION_GATE_V1
```

but now with the exact source-specific currency

```text
(NAE two-one defect set T, positive overshoot p, negative overshoot q).
```

## 10. Ceiling

```text
INTEGER LATTICE POINT -> POSITIVE NAE COLORING
= PROVED

Ap-Aq = -1_T
= PROVED

|T| = 3(||q||_1-||p||_1)
= PROVED

F-n = 4||p||_1 + 2|T|/3
= PROVED

3 DIVIDES |T|
= PROVED

UNIVERSAL p=0 OPTIMUM SHORTCUT
= FALSIFIED EXACTLY

FROZEN 15-SOURCE GLOBAL OPTIMUM
= 25

POSITIVE OVERSHOOT AT EVERY FEASIBLE POINT
= PROVED

SOURCE_TRADE_AUGMENT
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
