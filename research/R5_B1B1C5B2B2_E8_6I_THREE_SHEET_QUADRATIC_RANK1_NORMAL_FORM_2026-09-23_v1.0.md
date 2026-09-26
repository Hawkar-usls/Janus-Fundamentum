# R5 E8 6I — Three-Sheet Quadratic / Rank-One Normal Form

Date: 2026-09-23

Authority: `PROVED_EXACT_NORMAL_FORM__NOT_A_SOLVER__NO_D1_PROMOTION`

Checker:

`research/tools/r5_e8_6i_three_sheet_quadratic_rank1_normal_form_checker.py`

Parent:

`R5_E8_6I_REPRESENTATION_CHANGE_BEFORE_RELAXATION_GATE_V1`

## 1. Variable coherence is already cheaply compressible

Let one Boolean SAT variable have occurrence copies

```text
x_1,...,x_d.
```

Exact one-value coherence is

```text
EQ_d = {0^d,1^d}.
```

Over F2 this has a linear-size repetition-code description:

```text
x_1 + x_2 = 0
x_2 + x_3 = 0
...
x_{d-1} + x_d = 0.
```

Therefore:

```text
VARIABLE COPY COHERENCE
=
EXACT AFFINE CODE
OF SIZE O(d).
```

This is a positive control.

The delta-matroid obstruction is specific to that edge-CSP representation; it does not
mean equality itself lacks a compact polynomial representation.

## 2. Exact local sheet encoding

Encode the three frozen sheets by two local Boolean flip bits

```text
(u,v) in {(0,0),(1,0),(0,1)}.
```

Over F2 this is exactly:

```text
u v = 0.
```

The selected threshold-two sheet accepts iff

```text
Maj(a,b+u,c+v)=1.
```

For Boolean values,

```text
Maj(x,y,z)
=
xy + xz + yz
over F2.
```

Expanding gives

```text
ab + au + ac + av
+ bc + bv + cu + uv
=
1.
```

Together with

```text
uv=0,
```

this is an exact quadratic encoding of one three-sheet clause.

The checker verifies all eight truth rows and obtains exactly:

```text
000 -> {}
001 -> {(1,0)}
010 -> {(0,1)}
011 -> {(0,0)}
100 -> {(1,0),(0,1)}
101 -> {(0,0),(1,0)}
110 -> {(0,0),(0,1)}
111 -> {(0,0),(1,0),(0,1)}.
```

Hence:

```text
exists u,v
[
 uv=0
 and
 Maj(a,b+u,c+v)=1
]

iff

a OR b OR c.
```

No approximation is used.

## 3. Global quadratic normal form

For every original clause introduce only its two local flip variables.

Add:

- the two quadratic equations above for every clause;
- the affine repetition-code equations for occurrence coherence.

The resulting system has linear many variables/equations and degree at most two.

Thus:

```text
F is satisfiable

iff

Q(F) over F2
has a solution,
```

where `Q(F)` is constructed in polynomial, in fact linear-output, time up to ordinary
bookkeeping.

This is an exact representation theorem, not a complexity improvement.

## 4. One global rank-one moment lift

Let

```text
w=(1,z_1,...,z_N)
```

contain all Boolean prototype/occurrence and local flip variables.

Define

```text
Z = w w^T
over F2.
```

Then

```text
Z_00 = 1,
Z_0i = z_i,
Z_ij = z_i z_j.
```

Every quadratic equation of `Q(F)` becomes a linear equation in entries of `Z`.

Conversely, any symmetric rank-one `Z` over F2 with `Z_00=1` has the form

```text
Z = w w^T
```

for the uniquely recovered Boolean vector

```text
w_i=Z_0i.
```

Therefore SAT is reduced exactly to

```text
find Z such that

A_F(vec Z)=b_F
Z symmetric
Z_00=1
rank_F2(Z)=1.
```

Equivalently:

```text
AFFINE SUBSPACE
INTERSECT
BOOLEAN RANK-ONE VARIETY.
```

Materializing the full moment matrix costs O(N^2), still polynomial.

## 5. What this isolates

All equality/coherence constraints are linear.

All clause semantics become linear after the moment lift.

The remaining nonlinear object is only:

```text
MULTIPLICATIVE CONSISTENCY

Z_ij
=
Z_0i Z_0j

for all relevant products,
```

or globally:

```text
rank(Z)=1.
```

Thus the old phrase

```text
GLOBAL SHEET COHERENCE
```

can be sharpened for this representation to

```text
EXACT BOOLEAN RANK-ONE COMPLETION
OF A SPARSE AFFINE MOMENT SYSTEM.
```

## 6. Source context

General bilinear systems can be reformulated as finding rank-one solutions to linear
matrix constraints; this connection is standard in bilinear-system / MinRank literature.

General finite-field MinRank / multivariate-quadratic solving is not a free polynomial
step. Therefore the rank-one lift is not promoted as a solver.

The value of the normal form is that it exposes exactly which extra structural theorem
would be required.

## 7. New exact gate

Freeze:

```text
R5_E8_6I
SPARSE_BOOLEAN_RANK1_COMPLETION_GATE_V1
```

Input:

the affine matrix subspace `L_F={Z:A_F(vec Z)=b_F, Z=Z^T, Z_00=1}`
constructed from the frozen three-sheet quadratic normal form.

Question:

Can one decide and construct in deterministic polynomial time whether

```text
L_F
contains a rank-one matrix
```

using a structural property specific to this JANUS-generated family that is stronger than
general MinRank/MQ?

A valid PASS must prove:

1. a property satisfied by every `L_F`;
2. a source-proved or newly proved polynomial rank-one completion algorithm for exactly
   that property;
3. polynomial witness reconstruction;
4. no relaxation gap and no hidden enumeration;
5. total lifecycle polynomial in the original 3CNF length.

## 8. Anti-loop

Reject:

- simply dropping the rank-one condition;
- replacing it by a fixed-level LP/SDP/AIP moment relaxation already covered by the
  projection-minion barriers;
- generic MinRank/MQ algorithms with exponential worst-case complexity;
- calling the polynomial-size quadratic encoding itself a compression result.

## 9. Ceiling

```text
VARIABLE_COHERENCE_AFFINE_CODE
=
PASS

THREE_SHEET_TO_QUADRATIC_F2
=
PASS EXACT NORMAL FORM

QUADRATIC_TO_LINEAR_MOMENT_LIFT
=
PASS EXACT WITH RANK-ONE CONDITION

SPARSE BOOLEAN RANK-ONE COMPLETION
=
OPEN <<< NEW MICRO-GAP

D1
=
EMPTY

P_VS_NP
=
OPEN
```
