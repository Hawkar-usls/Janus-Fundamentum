# R5 E8 6I — Frozen Three-Sheet 1-Independence Barrier

Date: 2026-09-22

Authority: `PROVED_SOURCE_BOUND_DISJUNCTIVE_BARRIER__NO_D1_PROMOTION`

Parent gate:

`research/R5_B1B1C5B2B2_E8_6I_DISJUNCTIVE_INDEPENDENCE_REFINEMENT_SHEET_ABSORPTION_GATE_2026-09-22_v1.0.md`

Checker:

`research/tools/r5_e8_6i_three_sheet_1_independence_barrier_checker.py`

## 1. Source definition recovered

For constraint languages `Gamma` and `Delta`, write
`CSP_{Delta<=k}(Gamma union Delta)` for instances containing at most
`k` constraints from `Delta`.

The source notion is:

```text
Delta is k-independent with respect to Gamma
iff

every instance I of CSP(Gamma union Delta)
is satisfiable whenever every subinstance of I
containing at most k Delta-constraints is satisfiable.
```

For `k=1`, Cohen et al.'s disjunctive theorem, as restated by
Jonsson--Lööw, gives a tractable Horn-like disjunctive class when:

```text
CSP_{Delta<=1}(Gamma union Delta)
=
globally tractable

and

Delta
=
1-independent with respect to Gamma.
```

The Horn-like relation shape is:

```text
c
OR
d_1
OR ...
OR
d_n

c in Gamma
d_i in Delta.
```

Thus at most one disjunct is supplied by `Gamma); all remaining disjuncts
must lie in `Delta`.

Sources:

- Broxvall--Jonsson--Renz, *Disjunctions, independence, refinements*,
  Artificial Intelligence 140 (2002), 153--173.
- Jonsson--Lööw, *Computational Complexity of Linear Constraints over the Integers*,
  Definition 13 and Theorem 14.

## 2. Frozen three-sheet source binding

The already-proved source-model binding uses the eight ternary Boolean
threshold-two relations:

```text
M_tau(x,y,z)
=
AT_LEAST_2(sign-adjusted x,y,z)

tau in {+,-}^3.
```

For every sign vector `tau`, the frozen OR3 cover is:

```text
M_tau
OR
M_{flip_2(tau)}
OR
M_{flip_3(tau)}.
```

There are eight such covers.

Fixing the first sign partitions the eight base relations into two
four-element blocks:

```text
B_+
=
{M_{+bc}: b,c in {+,-}}

B_-
=
{M_{-bc}: b,c in {+,-}}.
```

Inside each block, the eight frozen covers realize all four 3-subsets.

## 3. Necessary Delta coverage for the Horn-like source family

Any exact use of the source family

```text
Gamma OR Delta*
```

on the frozen 3-sheet representation permits at most one Gamma-disjunct
per clause relation.

Therefore every frozen 3-sheet cover must contain at least two relations
belonging to `Delta`.

Because every 3-subset of `B_+` occurs as a cover:

```text
|Delta intersect B_+|
>=
3.
```

Likewise:

```text
|Delta intersect B_-|
>=
3.
```

This argument does not require `Gamma` and `Delta` to be disjoint.

## 4. Complementary-pair lemma

Pair every threshold-two relation with the relation obtained by flipping
all three signs:

```text
M_tau
<-->
M_not_tau.
```

These four pairs form a perfect matching between `B_+` and `B_-`.

Since `Delta` omits at most one relation from `B_+` and at most one
from `B_-`, at most two of the four complementary pairs can be broken.

Therefore at least two complete complementary pairs lie entirely in
`Delta`.

In particular, some:

```text
M_tau,
M_not_tau
in Delta.
```

## 5. Exact 1-independence falsifier

Use the same three CSP variables `x,y,z`.

The single constraint:

```text
M_tau(x,y,z)
```

is satisfiable.

The single constraint:

```text
M_not_tau(x,y,z)
```

is satisfiable.

But their conjunction is impossible:

```text
M_tau
requires at least two sign-adjusted literals true.

M_not_tau
requires at least two complementary literals true,

equivalently at most one of the original sign-adjusted literals true.
```

Hence:

```text
M_tau(x,y,z)
AND
M_not_tau(x,y,z)

=
UNSAT.
```

Take an instance `I` consisting only of these two `Delta)-constraints
and no `Gamma)-constraints.

Every subinstance of `I` with at most one `Delta)-constraint is
satisfiable.

The full instance is not satisfiable.

Therefore, by the source definition:

```text
Delta
IS NOT
1-INDEPENDENT
WITH RESPECT TO Gamma.
```

This holds for **every** `Gamma/Delta` assignment capable of representing
all frozen three-sheet clauses inside the Horn-like source family.

## 6. One-alien tractability is not the blocker

Every relation in `Gamma union Delta` is one of the eight threshold-two
relations and therefore has a 2-CNF definition.

Consequently:

```text
CSP_{Delta<=1}(Gamma union Delta)
=
POLYNOMIAL
```

for every such split.

The exact blocker is therefore:

```text
1-INDEPENDENCE
=
FAIL
```

not the one-alien solver.

## 7. Theorem

```text
R5_E8_6I_FROZEN_THREE_SHEET_1_INDEPENDENCE_BARRIER_V1

For the exact frozen three-sheet OR3 binding,
no source-compatible Gamma/Delta split can satisfy
the Broxvall/Cohen 1-independence tractability condition.

DIRECT HORN-LIKE
DISJUNCTIVE-COMPOSITION ROUTE
=
BLOCKED.
```

The checker independently enumerates every admissible `Delta` subset and
verifies the complementary-pair falsifier.

## 8. Scope firewall

This theorem does **not** block:

- a nontrivial polynomial refinement that changes the base relations;
- a different exact three-sheet/cover representation;
- a different disjunctive source theorem family after exact model binding;
- a non-Boolean or multi-sorted global refinement certificate;
- an interaction certificate that is not equivalent to a fixed Gamma/Delta split.

It blocks only the **direct frozen three-sheet** use of the source
`1-independence` theorem.

## 9. Frontier after the barrier

Already closed:

```text
DIRECT Delta_sheet* + GS
=
FALSIFIED

DIRECT EXPLICIT SELECTOR
=
NP-COMPLETE REPACKAGING

DIRECT SELECTOR PSEUDOPARTITION
=
BLOCKED

DIRECT FROZEN Gamma OR Delta*
VIA 1-INDEPENDENCE
=
BLOCKED
```

Therefore the disjunctive donor can only help through a genuine
**refinement** that changes the interaction representation before the
source theorem is applied.

Next target:

```text
R5_E8_6I_NONTRIVIAL_REFINEMENT_ESCAPE_GATE_V1
```

Required:

```text
REFINE(F)
=
poly size/time

SAT preserved exactly

refined base constraints
fit a precisely cited tractable
disjunctive theorem family

global variable/decoder coherence preserved

refinement discovery is not original SAT

total lifecycle
=
poly(original L).
```

## Claim ceiling

```text
SOURCE_EXACT_1_INDEPENDENCE_DEFINITION
=
RECOVERED

DIRECT_FROZEN_1_INDEPENDENCE
=
FALSIFIED

NONTRIVIAL_REFINEMENT_ESCAPE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
