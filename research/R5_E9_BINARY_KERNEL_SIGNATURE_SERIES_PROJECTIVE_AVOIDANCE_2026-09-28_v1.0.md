# R5 E9 — Binary-Kernel Signatures, Exact Series Classes, and Projective-Line Avoidance

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_SERIES_SIGNATURE_NORMAL_FORM__PROJECTIVE_LINE_AVOIDANCE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_ROOTED_SERIES_PAIR_SYNDROME_CONTRACTION_2026-09-28_v1.0.md`
- `research/R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `research/R5_E9_SINGLE_ODD_ROOTED_DUAL_FANO_POLY_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_binary_kernel_signature_series_projective_avoidance.py`

Scientific ceiling:

```text
THIS NOTE IS AN EXACT REPRESENTATION/CONTRACTION THEOREM.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
GENERIC 2-SUB-SAT / UNION-OF-SUBSPACE AVOIDANCE IS NP-HARD.
THE ONLY LIVE OPPORTUNITY AFTER THIS NOTE IS SOURCE-SPECIFIC GEOMETRY OF THE
3-REGULAR LINE ARRANGEMENT, OR A STRICTLY STRONGER GLOBAL CONTRACTION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source setup

Let

```text
A in {0,1}^{n x n}
```

be the incidence matrix of a cubic square Exact-One source: every row and every
column has weight three. Work over `F2` and write

```text
b = 1_n.
```

Because every row has odd weight,

```text
A 1 = b  over F2.
```

Let

```text
K = ker_F2(A),
k = dim_F2(K).
```

Choose a basis `z^(1),...,z^(k)` of `K`. For each original column coordinate
`j`, define its **kernel signature**

\[
\sigma_j=(z^{(1)}_j,\ldots,z^{(k)}_j)\in\mathbb F_2^k.
\]

The definition depends on the chosen basis only up to an invertible linear
change of coordinates in `F2^k`; equality, zero/nonzero status, and projective
incidence are basis-independent.

## 2. Exact dual representation of the augmented syndrome matroid

Form the augmented binary matrix

```text
A_plus = [A | b]
```

with distinguished root `e_b` for the last column.

A vector `(x,t) in F2^(n+1)` is a dependency of `A_plus` iff

```text
A x + t b = 0.
```

Since `b=A1`, this is equivalent to

```text
A(x+t1)=0.
```

Hence

\[
\ker(A_+) = \{(z+t\mathbf1,t):z\in K,\ t\in\mathbb F_2\}.
\]

Choose the dependency-space basis

```text
(z^(1),0),...,(z^(k),0),(1,1).
```

The transpose of this basis is a binary representation of the dual matroid
`M(A_plus)^*`. Its columns are therefore

\[
\boxed{h_j=(\sigma_j,1)\quad(j<n),\qquad h_{e_b}=(0,1).}
\]

All these dual columns are nonzero.

## 3. Series classes are exactly signature classes

In a binary matroid, a two-element cocircuit of the primal is a two-element
circuit of the dual. Over `F2`, two nonzero dual columns are parallel iff they
are equal.

Therefore:

### Theorem BKS-1

For distinct original elements `i,j`,

\[
\boxed{\{i,j\}\text{ is a 2-cocircuit of }M(A_+)\iff \sigma_i=\sigma_j.}
\]

For an original element `j`,

\[
\boxed{\{j,e_b\}\text{ is a 2-cocircuit}\iff \sigma_j=0.}
\]

Consequences:

1. the rooted series-pair preprocessor has a canonical coding interpretation;
2. nonroot series contraction aggregates all coordinates having the same
   nonzero kernel signature;
3. root-series contraction aggregates every zero-signature coordinate into a
   forced cost offset;
4. after exhaustive series contraction, every surviving original coordinate
   has a **distinct nonzero** signature.

Thus a series-irreducible source with `m` surviving original coordinates obeys

\[
\boxed{m\le 2^k-1},
\]

and in particular

\[
\boxed{k\ge \lceil\log_2(m+1)\rceil}.
\]

This is a structural lower bound on binary nullity for a series-irreducible
residual; it is not a tractability theorem.

## 4. Parity solutions are evaluations of the signature set

Every parity solution of

```text
A x = b
```

has the form

\[
x=\mathbf1+z,\qquad z\in K.
\]

Write a kernel vector using coefficient vector `t in F2^k`:

\[
z_j=\sigma_j\cdot t.
\]

Hence

\[
\boxed{x_j=1+\sigma_j\cdot t.}
\]

This is an exact parameterization of every parity solution, not a relaxation.

For unit original weights,

\[
\mu(A)=\min_{Ax=b}|x|
      = n-\max_{t\in\mathbb F_2^k}\big|\{j:\sigma_j\cdot t=1\}\big|.
\]

After series aggregation the same identity holds with the multiplicity of each
signature used as its weight and the zero-signature class used as the fixed
forced offset.

## 5. Every source row becomes a projective line

Take a source row with support `{a,b,c}`. Every `z in K` obeys

```text
z_a + z_b + z_c = 0.
```

Because this is true for every basis vector of `K`,

\[
\boxed{\sigma_a+\sigma_b+\sigma_c=0.}
\]

After exhaustive series contraction the three signatures are distinct and
nonzero, so

\[
\{\sigma_a,\sigma_b,\sigma_c\}
=\{u,v,u+v\}
\]

is a projective line of `PG(k-1,2)`.

The source linearity promise means two source rows share at most one surviving
point; the cubic promise means each surviving point appears with the aggregated
source multiplicity inherited from the contraction. Before aggregation every
source point occurs in exactly three source rows.

## 6. Exact-One becomes hyperplane avoidance

On one source row, the parity bits

```text
(z_a,z_b,z_c)
```

have even parity. Therefore they are either

```text
000
```

or a permutation of

```text
011.
```

Since `x=1+z`, the row has exactly one selected `x` iff the `z`-pattern is not
`000`.

Choose any two line generators, say `u=sigma_a`, `v=sigma_b`. Then

\[
\boxed{
\text{row is Exact-One}
\iff
(u\cdot t)\lor(v\cdot t)=1.
}
\]

Equivalently, the row fails exactly when

\[
t\in\operatorname{span}(u,v)^\perp,
\]

a codimension-two subspace of `F2^k`.

Thus, on the series-irreducible source:

### Theorem BKS-2

\[
\boxed{
A\text{ is Exact-One SAT}
\iff
\exists t\in\mathbb F_2^k
\text{ such that no source projective line is contained in }H_t,
}
\]

where

\[
H_t=\{u\in\mathbb F_2^k:u\cdot t=0\}.
\]

Equivalently,

\[
\boxed{
\exists t\notin\bigcup_{R}\operatorname{span}(R)^\perp.
}
\]

UNSAT means that the orthogonal codimension-two subspaces of the source lines
cover all of `F2^k`.

This gives a canonical source-generated **Union-of-Subspace Avoidance** form.

## 7. Prior-art boundary: generic avoidance is already hard

Arvind and Guruswami, *CNF Satisfiability in a Subspace and Related Problems*,
IPEC 2021, LIPIcs 214:5, DOI `10.4230/LIPIcs.IPEC.2021.5`, define the equivalent
Union-of-Subspace Avoidance problem and prove NP-hardness already for 2-SUB-SAT.

Therefore the representation

```text
AND_i( linear_form_i(t) OR linear_form'_i(t) )
```

is not a generic polynomial terminal.

A future PASS must exploit structure absent from arbitrary 2-SUB-SAT, namely the
source-generated line arrangement / cubic-incidence provenance, or introduce a
strictly stronger global representation-changing contraction.

## 8. Frozen `PG(3,2)` controls

Use all fifteen nonzero vectors of `F2^4` as potential kernel signatures and
select fifteen projective lines so every point occurs in exactly three selected
lines. This automatically gives a linear cubic `15_3` incidence source whose
signature set is series-irreducible.

The companion checker freezes two exact controls.

### PG15_UNSAT_R13

Selected projective lines:

```text
(1,10,11) (1,12,13) (1,14,15)
(2,4,6)   (2,5,7)    (2,12,14)
(3,4,7)   (3,8,11)   (3,9,10)
(4,11,15) (5,8,13)   (5,9,12)
(6,8,14)  (6,9,15)   (7,10,13)
```

Exact finite facts:

```text
rank_Q(A)  = 13
rank_F2(A) = 11
2-cocircuit series pairs in M([A|1]) = 0
Exact-One witnesses = 0
```

### PG15_SAT_R11

Selected projective lines:

```text
(1,2,3)   (1,10,11) (1,12,13)
(2,9,11)  (2,12,14) (3,4,7)
(3,5,6)   (4,9,13)  (4,10,14)
(5,8,13)  (5,10,15) (6,8,14)
(6,9,15)  (7,8,15)  (7,11,12)
```

Exact finite facts:

```text
rank_Q(A)  = 11
rank_F2(A) = 10
2-cocircuit series pairs in M([A|1]) = 0
Exact-One witness = {1,5,7,9,14} in 1-based point labels
```

These controls prove only that series-irreducibility is compatible with both
SAT and UNSAT and with rational singularity. They remain finite and do not by
themselves escape the existing low-rational-nullity router.

## 9. Sharpened live gate

Freeze

```text
R5_E9_PROJECTIVE_LINE_AVOIDANCE_GLOBAL_CONTRACTION_GATE_V1
```

for the post-series source residual.

A PASS must provide one of:

1. a deterministic polynomial algorithm deciding whether the source-generated
   3-regular projective-line family admits a hyperplane containing no source
   line, with witness reconstruction;
2. an exact polynomial contraction of the projective arrangement with a strict
   global potential and polynomial lift;
3. a theorem forcing every superlog-rational-nullity source into one of the
   already admitted matroid/graph/balanced/separator terminals; or
4. the end-to-end universal SAT solver contract.

Forbidden pseudo-progress:

- applying generic 2-SUB-SAT/USA as if it were polynomial;
- enumerating all `2^k` coefficient vectors `t` when `k` is superlogarithmic;
- treating distinct signatures or projective-line incidence as SAT/UNSAT by
  itself;
- reintroducing identical signatures under a new variable name;
- using a finite `PG(3,2)` census as an asymptotic theorem.

## 10. Ceiling

```text
SERIES CLASS = EQUAL BINARY-KERNEL SIGNATURE
= PROVED

ROOT SERIES = ZERO BINARY-KERNEL SIGNATURE
= PROVED

POST-SERIES SIGNATURES
= DISTINCT NONZERO PROJECTIVE POINTS
= PROVED

SOURCE ROW
= PROJECTIVE LINE {u,v,u+v}
= PROVED

EXACT-ONE
= HYPERPLANE AVOIDING EVERY SOURCE LINE
= PROVED

GENERIC 2-SUB-SAT / SUBSPACE AVOIDANCE
= NP-HARD (SOURCE-BOUND PRIOR ART)

PG(3,2) SERIES-IRREDUCIBLE SAT + UNSAT CONTROLS
= EXACT FINITE REGRESSION

SOURCE-SPECIFIC PROJECTIVE-LINE GLOBAL CONTRACTION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
