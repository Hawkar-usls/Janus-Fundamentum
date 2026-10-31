# R5 E8 6I — Rank-One Affine-Cut Hull Barrier

Date: 2026-09-23

Authority:

`PROVED_SCOPED_BARRIER__SAME_MOMENT_SPACE_AFFINE_CUTS_ONLY__NO_D1_PROMOTION`

Checker:

`research/tools/r5_e8_6i_rank1_affine_cut_hull_barrier.py`

Parent:

`R5_E8_6I_SPARSE_BOOLEAN_RANK1_COMPLETION_GATE_V1`

## 1. Scope

This result concerns the most direct RAIL instantiation after the exact moment lift:

```text
AFFINE MOMENT ABSTRACTION L_F
+
LEARN ONLY NEW AFFINE F2 EQUATIONS
IN THE SAME MOMENT COORDINATES
```

A learned cut is therefore an equation

```text
<lambda,Z> = beta  over F2
```

that is valid for every genuine rank-one lift.

The theorem below proves that such cuts are not separation-complete even for
one frozen three-sheet clause.

It does **not** block:

- nonlinear cuts;
- a new representation before refinement;
- recursively tractable cut languages richer than affine equations;
- higher-dimensional certificates whose solver remains independently polynomial.

## 2. One-clause concrete set

Use variables

```text
(a,b,c,u,v) in F2^5
```

with frozen local equations

```text
uv = 0

ab + au + ac + av + bc + bv + cu + uv = 1.
```

The exact satisfying local assignments are the 12 tuples

```text
00110
01001
01100
10001
10010
10100
10110
11000
11001
11100
11101
11110
```

in `(a,b,c,u,v)` order.

For each tuple define the symmetric moment matrix

```text
M(w)=w w^T,
w=(1,a,b,c,u,v).
```

Let `S` be these 12 genuine rank-one moment points.

## 3. Affine hull computation

The checker performs exact Gaussian elimination over F2 on the 21 independent
upper-triangular moment coordinates.

Result:

```text
|S| = 12

affine_dimension(aff(S))
=
11

|aff(S)|
=
2^11
=
2048.
```

The 12 genuine moment points are affinely independent.

The checker then exhaustively enumerates all 2048 points in `aff(S)` and
tests the exact moment identity

```text
Z_ij = Z_0i Z_0j.
```

Exactly 12 points are rank-one moments.

Therefore:

```text
SPURIOUS POINTS
IN COMPLETE AFFINE HULL
=
2048 - 12
=
2036.
```

So even the **complete affine closure of all genuine local solutions** is far
from exact.

## 4. Explicit inseparable spurious witness

Take three genuine local assignments

```text
s1 = 00110
s2 = 01001
s3 = 01100.
```

Over F2, an affine combination of an odd number of points is their XOR.
Set

```text
q
=
M(s1) + M(s2) + M(s3).
```

Then

```text
q in aff(S).
```

Its first row is

```text
(1,0,0,0,1,1),
```

so naive decoding gives

```text
a=b=c=0,
u=v=1.
```

This cannot be a genuine local lift.

Indeed the rank-one identity fails, for example

```text
q_uv = 0
but
q_0u q_0v = 1.
```

Nevertheless q satisfies the linearized local constraints, including

```text
Z_uv = 0
```

and the expanded linear moment equation.

## 5. No affine separator theorem

### Theorem

There is no affine F2 equation in the current moment coordinates that

1. is satisfied by every point of `S`, and
2. rejects `q`.

### Proof

Every affine equation valid on `S` is valid on `aff(S)` by definition of
affine hull.

Since

```text
q in aff(S),
```

q satisfies every such equation.

QED.

The checker independently verifies this by computing the 10-dimensional
annihilator of the 11-dimensional difference space and enumerating all

```text
2^10 = 1024
```

affine equations valid on `S`.

The explicit q satisfies all 1024.

## 6. RAIL consequence

The RAIL meta-theorem requires every non-liftable abstract witness to admit a
fresh sound cut from a polynomial obstruction basis.

For the attempted instantiation

```text
ABSTRACT STATE
=
current F2 moment vector

CUT LANGUAGE
=
affine equations over those same coordinates,
```

the explicit q is non-liftable but has **no sound affine separating cut at all**.

Therefore R5 fails independently of basis cardinality.

Hence:

```text
SAME-MOMENT-SPACE
AFFINE-CUT RAIL
=
BLOCKED.
```

This is stronger than saying that some chosen affine basis was incomplete:
even the full family of affine equations valid on the genuine local set cannot
separate q.

## 7. Important firewall: polynomial number of nonlinear defects is not enough

Rank-one consistency itself has a polynomial family of pairwise identities

```text
Z_ij = Z_0i Z_0j.
```

For the explicit q, `Z_uv = Z_0u Z_0v` already detects failure.

But treating these identities as refinement cuts does not by itself instantiate
RAIL, because the refined abstraction must remain exactly polynomially solvable
at the next recursive level.

Adding all multiplicative identities simply reconstructs the original quadratic
rank-one feasibility problem.

Thus:

```text
POLYNOMIALLY MANY
OBSTRUCTION PREDICATES

!=

POLYNOMIAL RAIL
OBSTRUCTION CURRENCY.
```

The missing object must combine:

```text
SEPARATION COMPLETENESS
+
TRACTABLE CUT LANGUAGE / RECURSION
+
POLYNOMIAL TOTAL STATE.
```

## 8. Source context

General MQ over GF(2) is NP-complete / NP-hard in the literature; the JANUS
normal form is an exact reduction from signed 3SAT to a sparse quadratic system,
so generic MQ or generic MinRank machinery does not provide a free polynomial
solver.

This barrier itself does not rely on a complexity assumption: it is a direct
finite affine-hull argument.

## 9. Next exact gate

Freeze:

```text
R5_E8_6I
RANK1_NONAFFINE_TRACTABLE_CUT_CURRENCY_GATE_V1
```

Question:

Can the JANUS sparse-F2 rank-one family admit a cut/certificate language that is

```text
1. sound for every genuine rank-one lift,
2. separation-complete for every spurious affine witness,
3. polynomially discoverable,
4. polynomially representable in total,
5. exactly solvable after refinement,
6. reconstructive,
7. not equivalent to re-imposing the full quadratic SAT/MQ system?
```

Priority source families:

- bounded-structure bilinear / MinRank algorithms;
- graph/matroid cycle-space certificates;
- tractable delta-matroid / matching-style nonlinear constraints;
- recursive affine-interface systems with source-proved polynomial separation;
- special sparse quadratic systems with width/rank/acyclicity guarantees.

## 10. Ceiling

```text
THREE_SHEET
-> SPARSE_F2_RANK1
=
PASS EXACT NORMAL FORM

SAME-MOMENT AFFINE CUT BASIS
=
FALSIFIED THEOREM-LEVEL

NONLINEAR TRACTABLE CUT CURRENCY
=
OPEN <<< ACTIVE MICRO-GAP

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT_PROVED
```
