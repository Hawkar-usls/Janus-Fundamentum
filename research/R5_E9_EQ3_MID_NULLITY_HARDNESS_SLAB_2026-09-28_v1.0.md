# R5 E9 — EQ3 middle-nullity hardness slab

Date: 2026-09-28

Status:
`JANUS_DERIVED_EXACT_HARDNESS_SLAB_THEOREM__MIDDLE_NULLITY_IS_NP_COMPLETE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_eq3_mid_nullity_hardness_slab.py`

Scientific firewall:

```text
THIS THEOREM DOES NOT PROVE P=NP.
IT PROVES THAT THE CURRENT MIDDLE-NULLITY RESIDUAL ALREADY CONTAINS
AN NP-COMPLETE CONSTANT-RATIO SLAB UNDER THE EXISTING EXACT EQ3 REDUCTION.
THEREFORE A UNIVERSAL POLYNOMIAL QUOTIENT FOR THIS SLAB WOULD ITSELF
BE A P-VS-NP-SCALE RESULT.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source and existing exact reduction

Take a cubic positive 1-in-3 instance `Phi` with `m` variables and `m` clauses.
Let its square incidence matrix be

```text
M in {0,1}^{m x m}
```

with every row and column of weight three, and write

```text
kappa = nullity_Q(M).
```

The existing EQ3 regularization replaces each source variable by one 10-variable,
9-clause equality gadget and retains the `m` source clauses on occurrence
terminals.  The output is a linear, cubic, square positive 1-in-3 instance with

```text
N = 10m
```

variables and clauses, and is satisfiable iff `Phi` is satisfiable.

The only new question here is the exact rational rank/nullity of that output.

## 2. Local gadget rank

Let `G` be the `9 x 10` coefficient matrix of the frozen EQ3 gadget with clauses

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6).
```

Exact elimination gives

```text
rank_Q(G) = 8,
nullity_Q(G) = 2.
```

A homogeneous kernel parametrization may be chosen as

```text
terminal coordinates 0,1,2 and coordinate 9 = q,
coordinates 6,7,8 = r,
coordinates 3,4,5 = -q-r.
```

Thus each gadget contributes exactly two quotient coordinates `(q,r)` after its
nine local equations are imposed.

For `m` disjoint gadgets the local block has rank `8m` and quotient dimension
`2m`.

## 3. Exact rank increment of the retained source rows

Each retained source clause touches one terminal occurrence from each of three
source-variable gadgets.  On the local quotient every terminal occurrence of a
given gadget has value exactly `q`; the internal mode `r` is invisible to every
retained source row.

Therefore, after quotienting by the gadget rowspace, the `m` retained source
rows act on

```text
(q_1,...,q_m,r_1,...,r_m)
```

as

```text
[M  0].
```

Hence their rank increment modulo the local gadget rowspace is exactly

```text
rank_Q(M) = m-kappa.
```

Consequently the full output incidence matrix `A_R` has

```text
rank_Q(A_R)
= 8m + rank_Q(M)
= 8m + (m-kappa)
= 9m-kappa.
```

Since `N=10m`, its rational nullity is exactly

\[
\boxed{
K := \nu_{\mathbb Q}(A_R) = 10m-(9m-\kappa)=m+\kappa.
}
\]

This is an identity, not an asymptotic estimate.

## 4. The output always lies deep inside the middle band

For every square row/column-weight-three incidence matrix, the row-basis
coverage theorem gives

```text
0 <= kappa <= 2m/3.
```

Therefore

```text
m <= K <= 5m/3.
```

Using `N=10m`,

\[
\boxed{
N/10 \le K \le N/6.
}
\]

The overlap-excess parameter of the output is

```text
Delta = 2N-3K
      = 20m-3(m+kappa)
      = 17m-3kappa.
```

Hence

```text
15m <= Delta <= 17m,
```

or equivalently

\[
\boxed{
3N/2 \le \Delta \le 17N/10.
}
\]

Thus both exact FPT parameters are linear on every output of this reduction:

```text
K = Theta(N),
Delta = Theta(N).
```

The reduction never approaches either polynomial island `K=O(log N)` or
`Delta=O(log N)`.

## 5. Hardness-slab theorem

### Theorem MHS-1

Positive 1-in-3 SAT remains NP-complete when restricted simultaneously to

```text
linear,
cubic / 3-uniform / 3-regular,
square incidence,
N/10 <= nullity_Q(A) <= N/6.
```

Equivalently, the constant-ratio nullity slab

\[
\boxed{1/10 \le \nu_{\mathbb Q}(A)/N \le 1/6}
\]

already contains an exact Karp image of the NP-complete cubic positive 1-in-3
source class.

### Proof

The parent EQ3 construction is a deterministic polynomial Karp reduction into
the linear cubic square carrier and preserves satisfiability exactly.  Sections
2--4 prove that every output additionally lies in the displayed rational-nullity
slab.  Membership in NP is immediate.  QED.

## 6. Consequence for the current bottleneck

The residual condition

```text
K = omega(log N)
and
Delta = omega(log N)
```

is not merely a region in which the two current routers happen to be weak.
It contains an NP-complete subproblem with a fixed linear margin from both
boundaries.

Therefore none of the following can close the universal problem by itself:

```text
prove middle instances secretly have K=O(log N),
prove middle instances secretly have Delta=O(log N),
refine only the asymptotic constants in either exponential router.
```

The next successful route must exploit a new exact global semantic invariant on
this constant-ratio slab, or else give a representation change whose total
construction/solve/reconstruction/verification cost is polynomial there.

Freeze the sharper target as

```text
R5_E9_EQ3_MID_NULLITY_HARDNESS_SLAB_GLOBAL_QUOTIENT_GATE_V1
```

with mandatory scope

```text
linear cubic square Exact-One,
N/10 <= nu_Q(A) <= N/6.
```

A polynomial solver for this gate, combined with the existing exact reduction,
would decide an NP-complete problem in polynomial time and therefore imply
`P=NP`.  No such solver is supplied by this theorem.

## 7. Anti-loop value

This theorem closes the following dead-end hypotheses:

```text
MIDDLE BAND MAY BE AN ARTIFACT OF LOOSE PARAMETER BOUNDS
= FALSIFIED.

NP-HARDNESS MAY LIVE ONLY NEAR LOW-k OR NEAR MAXIMAL-k ENDS
= FALSIFIED BY THE EXISTING EQ3 IMAGE.

NEXT TARGET
= GLOBAL SEMANTIC QUOTIENT ON A FIXED CONSTANT-RATIO HARDNESS SLAB.
```

## 8. Ceiling

```text
EQ3 GADGET RANK
= 8
= EXACT

OUTPUT NULLITY
K = m + kappa
= PROVED

OUTPUT OVERLAP EXCESS
Delta = 17m - 3kappa
= PROVED

HARDNESS SLAB
N/10 <= K <= N/6
= PROVED

CORRESPONDING Delta SLAB
3N/2 <= Delta <= 17N/10
= PROVED

LINEAR CUBIC EXACT-ONE ON THIS SLAB
= NP-COMPLETE

UNIVERSAL POLYNOMIAL QUOTIENT
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```