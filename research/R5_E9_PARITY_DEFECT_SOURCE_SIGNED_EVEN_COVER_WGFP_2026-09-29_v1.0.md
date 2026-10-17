# R5 E9 — Parity-defect augmentation as source-signed linear even cover / WGFP

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_NEGATIVE_KERNEL_TO_SOURCE_SIGNED_03_02_WGFP__GENERAL_DICHOTOMY_HARD_SIDE__LINEAR_SOURCE_SUBCLASS_OPEN__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`
- `research/R5_E9_CUBIC_KERNEL_CIRCUIT_CONNECTED_CONTRACTION_2026-09-27_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_parity_defect_source_signed_even_cover_wgfp.py`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE THE MISSING POLYNOMIAL AUGMENTATION ORACLE.
IT GIVES AN EXACT REDUCTION OF THE NEGATIVE-BINARY-KERNEL QUERY TO A
HIGHLY STRUCTURED WEIGHTED GENERAL-FACTOR / LINEAR-EVEN-COVER INSTANCE.
THE GENERAL DEGREE-CONSTRAINT PAIR LIES ON THE NP-HARD SIDE OF THE 2026
SUBCUBIC WGFP DICHOTOMY, WHILE THE 4-CYCLE-FREE REGULAR EVEN-COVER
COMPLEXITY IS EXPLICITLY LEFT OPEN IN CURRENT LDPC LITERATURE.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Parity point and defect count

Let

\[
A\in\{0,1\}^{n\times n}
\]

be square, 3-uniform, 3-regular and linear, and let

\[
x\in\{0,1\}^n,\qquad Ax=\mathbf1\pmod 2.
\]

Every source row has odd Boolean weight, hence weight exactly 1 or 3.
Let

\[
t(x)=|\{r:(Ax)_r=3\text{ over }\mathbb Z\}|
\]

be the number of `111` rows.

Counting selected incidences in two ways gives

\[
3|x|=(n-t(x))+3t(x)=n+2t(x).
\]

Therefore

\[
\boxed{t(x)=\frac{3|x|-n}{2}.}
\]

In particular:

\[
\boxed{
Ax=\mathbf1\text{ over }\mathbb Z
\iff t(x)=0
\iff |x|=n/3.
}
\]

Thus affine-coset Hamming descent is exactly `111`-defect descent.

## 2. Binary kernel moves as a general factor on the Levi graph

Let `L(A)` be the cubic bipartite Levi graph with variable shore `V_X` and row shore `V_R`.
For a binary kernel vector

\[
0\ne z\in\ker_{\mathbb F_2}(A),
\]

select in `L(A)` every incidence edge adjacent to a selected variable `i` with `z_i=1`.

Then:

- a variable node has selected degree `0` or `3`;
- a row node has selected degree `0` or `2`, because `Az=0 mod 2` and source rows have degree 3.

Conversely any Levi subgraph satisfying

```text
variable nodes: degree in {0,3},
row nodes:      degree in {0,2}
```

selects either all or none of the three incidences of each variable and therefore reconstructs a unique binary kernel vector `z`.

### Theorem PDSW-1 — exact factor/kernel bijection

Binary kernel vectors are in one-to-one correspondence with general factors of the Levi graph under degree constraints

\[
\boxed{D_X=\{0,3\},\qquad D_R=\{0,2\}.}
\]

The zero kernel vector corresponds to the empty factor.

Because the source is linear, `L(A)` is 4-cycle-free, hence has girth at least six.

## 3. Source-induced edge weights collapse to one sign per variable

Put

\[
w_i=1-2x_i\in\{-1,+1\}.
\]

Assign every incidence edge `(r,i)` the half-weight

\[
\boxed{\omega_{ri}=\frac12 w_i.}
\]

All three incidence edges of the same variable therefore carry the same weight.
If factor `F_z` corresponds to kernel vector `z`, all three incidences of every selected variable are present, so

\[
\omega(F_z)
=\frac32\sum_{i:z_i=1}w_i.
\]

But

\[
\Delta_x(z)=|x\oplus z|-|x|
=\sum_{i:z_i=1}(1-2x_i)
=\sum_{i:z_i=1}w_i.
\]

Hence

\[
\boxed{\omega(F_z)=\frac32\Delta_x(z).}
\]

Multiplying all edge weights by two gives integral weights `w_i in {+1,-1}` on incidences and factor weight `3 Delta_x(z)`.

## 4. Exact defect interpretation

Both `x` and `x xor z` satisfy the same parity syndrome. Applying Section 1 to both gives

\[
3\big(|x\oplus z|-|x|\big)
=2\big(t(x\oplus z)-t(x)\big).
\]

Therefore

\[
\boxed{
t(x\oplus z)-t(x)
=\frac32\Delta_x(z)
=\omega(F_z).
}
\]

So the same factor weight simultaneously equals:

```text
change in number of 111 defects,
3/2 times Hamming augmentation charge.
```

Thus:

### Corollary PDSW-2

The following are equivalent:

1. there exists a negative binary-kernel augmentation;
2. there exists a nonempty `{0,3}/{0,2}` Levi factor of negative source weight;
3. there exists a nonempty even cover whose signed variable weight is negative;
4. the current parity point is not minimum Hamming weight in its affine coset.

By the parent circuit theorem, any such negative kernel contains a negative circuit component, and at most `n` successful augmentations suffice if the negative-factor oracle is polynomial.

## 5. Hypergraph even-cover contraction

Contract each all-or-none variable node into one 3-uniform hyperedge on its three incident row vertices.
Then a factor is exactly a set `Y` of source variables/hyperedges such that every row-vertex has even selected degree (`0` or `2`).

Thus the missing primitive is the source-signed optimization problem

\[
\boxed{
\min_{\emptyset\ne Y:\ A1_Y=0\ (\mathrm{mod}\ 2)}
\sum_{i\in Y}(1-2x_i).
}
\]

on a 3-uniform, 3-regular, **linear** hypergraph.

Call it

```text
SOURCE_SIGNED_LINEAR_EVEN_COVER_333.
```

A negative optimum is exactly an improving affine-coset step.

## 6. 2026 WGFP dichotomy boundary

Shao and Zivny, *Real-weighted general factors on subcubic graphs*, Mathematical Programming (published 14 September 2026), prove a complete dichotomy for real-weighted general factors on subcubic graphs.
Their Theorem 1.2 states that `WGFP(D)` is strongly polynomial if either

1. arity-3 `{0,3}` is absent, or
2. every arity-k degree constraint `D` satisfies `D subseteq {0,k}`;

otherwise the problem is NP-hard.
DOI: `10.1007/s10107-026-02416-3`.

Our constraint language contains

```text
{0,3} at degree-3 variable nodes,
{0,2} at degree-3 row nodes.
```

Therefore condition 1 fails and condition 2 fails (`{0,2}` is not a subset of `{0,3}` for an arity-3 row node). The **general** subcubic weighted problem containing this pair lies on the NP-hard side.

This is an anti-loop boundary, not a hardness proof for the exact JANUS subclass. The JANUS instance has additional simultaneous promises:

```text
cubic bipartite Levi graph,
4-cycle-free / hypergraph-linear,
all three incidence weights of one variable equal,
weights are only +/-1 after common scaling,
weight signs come from a syndrome-one parity point x.
```

No theorem in the cited dichotomy says that those promises preserve the NP-hardness reduction.

## 7. 2026 regular-LDPC boundary: linearity is an explicit open gap

Jia, Peng, Liu, Wang and Yan, *On the Intractability of the Minimum Distance Problem for Regular LDPC Codes*, arXiv:2606.23161v3 (2026), prove NP-completeness for minimum distance on `(3,3)`-regular Tanner graphs.

Crucially, their Discussion separately identifies the 4-cycle-free / linear-hypergraph restriction as open. They define

```text
MinLinearEvenCover_(J,K)
```

for J-uniform, K-regular, linear hypergraphs and state Conjecture 23 that it remains NP-complete and W[1]-complete for fixed `J,K >= 3`.

For `J=K=3`, our unsigned support family sits exactly inside that still-open linear-even-cover geometry, while our live query additionally has syndrome-induced +/- weights.

Therefore the current literature supports neither of the invalid shortcuts:

```text
regular sparse Tanner graph -> polynomial,
regular sparse Tanner graph -> hardness automatically survives linearity.
```

The source-specific linearity promise must be used or defeated explicitly.

## 8. Sharpened live gate

Freeze

```text
R5_E9_SOURCE_SIGNED_LINEAR_EVEN_COVER_333_GATE_V1
```

Input:

```text
A: square 3-uniform 3-regular linear incidence matrix,
x in {0,1}^n with Ax=1 mod 2,
w_i=1-2x_i.
```

Required deterministic polynomial output:

1. a nonzero `z in ker_F2(A)` with `sum_i w_i z_i < 0`, or
2. a polynomially checkable certificate that no such `z` exists.

Equivalent allowed representations:

```text
negative {0,3}/{0,2} factor on the cubic Levi graph,
negative signed even cover in the linear 3-uniform hypergraph,
negative connected contracted cubic circuit after support selection.
```

If the oracle returns a negative support, apply `x <- x xor z`; the Hamming potential decreases by at least one and at most `n` successful augmentations occur. If it certifies absence, the parent CAD theorem certifies global affine-coset minimum. Exact-One is SAT iff the resulting minimum has weight `n/3`.

Forbidden:
- invoke generic WGFP despite its hard-side classification;
- invoke generic LDPC decoding/minimum distance;
- assume Conjecture 23 as a theorem;
- enumerate the kernel/even covers;
- lose the linearity/girth-six promise;
- treat the support-dependent contracted cubic graph as fixed in advance.

## 9. Ceiling

```text
PARITY DEFECT IDENTITY
3|x| = n + 2t(x)
= PROVED

BINARY KERNEL
iff LEVI GENERAL FACTOR {0,3}/{0,2}
= PROVED

SOURCE EDGE WEIGHTS
= ONE +/- SIGN REPEATED ON ALL 3 INCIDENCES OF A VARIABLE

FACTOR WEIGHT
= DELTA t
= (3/2) DELTA Hamming
= PROVED

NEGATIVE KERNEL / NEGATIVE FACTOR / NEGATIVE SIGNED EVEN COVER
= EXACTLY EQUIVALENT

GENERAL SUBCUBIC {0,3}/{0,2} WGFP
= NP-HARD SIDE OF SHAO-ZIVNY 2026 DICHOTOMY

(3,3)-REGULAR MINIMUM DISTANCE WITHOUT LINEARITY
= NP-COMPLETE (JIA ET AL. 2026)

4-CYCLE-FREE / LINEAR REGULAR EVEN-COVER COMPLEXITY
= EXPLICITLY OPEN IN JIA ET AL. CONJECTURE 23

SOURCE-SIGNED LINEAR EVEN-COVER POLYNOMIAL ORACLE
= OPEN / CURRENT BOTTLENECK

UNIVERSAL POLYNOMIAL SAT DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
