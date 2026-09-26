# R5 E9 — Local Permutation-Swap High-Nullity Phase-Fail Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__RANK_ONE_PERTURBATION_SOURCE_BOUND__JANUS_FAMILY_COUPLING_SCOPED`

Immediate predecessor:
`NM-0030-POLYSIZE-2GROUP-FIXED-GIRTH-COVER`

## G0 — exact changed object

NM-0030 closes the polynomial-size 2-group high-girth cover obligation provided
one already has a base family with

```
nullity = omega(log n),
PQ != QP,
Z3 phase = FAIL.
```

The repository already contains a connected noncommuting phase-PASS family on

```
Omega_m=Z_3 x Z_m
```

with

```
dim_Q ker(I+P+Q)=m+1=n/3+1.
```

The changed question is whether a bounded-rank local modification of one
permutation can destroy the phase certificate while preserving linear nullity,
the cubic source contract, connectedness and an exact witness.

## G1 — internal anti-duplication

Repository-first search covered:

- R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND and its large-nullity phase-PASS family;
- R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM;
- PA-0025/NM-0029 filtered-cover/nullity work;
- all current phase and cover artifacts.

No artifact was found giving a family-wide phase-FAIL construction by swapping
two images of Q while preserving linear rational nullity.

## G2 — source-bound linear algebra

Low-rank perturbation bounds are standard matrix theory.

For matrices A and E,

```
rank(A+E) <= rank(A)+rank(E),
```

so

```
nullity(A+E) >= nullity(A)-rank(E).
```

Rank-one perturbation theory is classical and extensively studied.

The proposed Q-image transposition changes only two rows of the permutation
matrix, with opposite row differences, so the perturbation has rank one.  That
factorization is elementary and need not be presented as external novelty.

Classification:

```
LOW-RANK / RANK-ONE PERTURBATION INEQUALITY
=
SOURCE-BOUND / STANDARD.

EXACT JANUS PERMUTATION-SWAP COUPLING
=
SCOPED THEOREM TARGET.
```

## G3 — exact family to test

Use the existing E9 family

```
P(r,a)=(r+1,a)

Q(0,a)=(2,a+1)
Q(1,a)=(0,a)
Q(2,a)=(1,a)
```

on Z_3 x Z_m.

For m>=3 set

```
u=(0,0),
v=(2,2),
```

and define Q' by swapping the two images

```
Q(u)=(2,1),
Q(v)=(1,2).
```

Thus

```
Q'(u)=(1,2),
Q'(v)=(2,1),
```

and Q'=Q elsewhere.

The authorized theorem must verify uniformly, not only computationally:

1. Q' remains a permutation and every row {i,P(i),Q'(i)} has three distinct
   coordinates;
2. the source stays connected;
3. P,Q' remain noncommuting;
4. the Z3 phase equations are inconsistent;
5. Q'-Q has rank one, hence nullity remains at least m;
6. an explicit Boolean Exact-One witness exists.

## G4 — source search result

Targeted searches located general rank-one perturbation literature but no
source stating this exact permutation/cocycle/nullity construction.

This is a scoped source audit, not a legal novelty certification.

## Audit decision

```
PA-0028
LOCAL PERMUTATION-SWAP HIGH-NULLITY PHASE-FAIL AUDIT
=
PASS_SCOPED_GAP_CONFIRMED

RANK-ONE PERTURBATION
=
SOURCE-BOUND

OLD PHASE-PASS LARGE-NULLITY FAMILY
=
INTERNAL REUSE

SWAPPED PHASE-FAIL LINEAR-NULLITY FAMILY
=
NO SOURCE CLOSURE LOCATED

NEW MATH AUTHORIZED
=
R5_E9_LOCAL_SWAP_PHASEFAIL_BASE_FAMILY_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
