# R5 E8 6I — Boolean multi-sorted Fano blocker

Date: 2026-09-22

Authority: `EXACT_FIXED_GADGET_BLOCKER__NO_LIFTED_DOMAIN_CLAIM__NO_D1_PROMOTION`

## 1. Source-bound mechanism under test

The relevant classical mechanism is the multi-sorted algebraic CSP framework of:

Andrei A. Bulatov and Peter Jeavons,
*An Algebraic Approach to Multi-sorted Constraints*,
CP 2003.

Source record:

https://ora.ox.ac.uk/objects/uuid%3A401ed69e-3437-4e1c-b9f1-f3d6e6a758c4

Their framework permits different sorts to have different interpretations of the same multi-sorted operation.

In particular, tractability can be obtained by combining constant, semilattice, near-unanimity and affine behaviour across sorts, provided the corresponding multi-sorted operations preserve all relations.

This is strictly richer than requiring one global Boolean polymorphism.

The 6I question is therefore:

> Does arbitrary 3-CNF become universally tractable if each Boolean variable is treated as its own sort and each sort may obtain its own global mixed-operation certificate?

## 2. Why the previous single-operation blocker is not enough

The already sealed full Boolean single-ternary catalogue blocker says:

```text
ALL SINGLE BASIC TERNARY
BOOLEAN TRACTABLE ALGEBRAS
=
INSUFFICIENT.
```

However, the multi-sorted theorem allows a stronger certificate.

For a target sort `v`, one may use a global multi-sorted operation

```text
t^v=(t_w^v)_w
```

whose interpretation at `v` is tractable while its interpretations on other sorts may be arbitrary Boolean operations.

Different target sorts may use different global operations.

Thus a separate exact blocker is required.

## 3. Frozen paired-clause relation

For every hyperedge `{x,y,z}`, impose both:

```text
R+ = (x OR y OR z)

R- = (NOT x OR NOT y OR NOT z).
```

Their common Boolean solutions are exactly NAE assignments on the edge.

For a mixed ternary operation triple

```text
(f,g,h)
```

the checker tests literal preservation of both `R+` and `R-`.

Domain:

```text
f,g,h
in
ALL 256 Boolean ternary operations.
```

Exact survivor count:

```text
1533.
```

The full survivor relation has an exact six-category quotient.

A preserving triple is present iff:

```text
CASE A:
the triple contains both CONST_0 and CONST_1

OR

CASE B:
all three operations are the same positive projection P_i.
```

No other triple survives.

Therefore all 256 operation tables collapse exactly, for this paired relation, to:

```text
C0
C1
P0
P1
P2
OTHER
```

where `OTHER` covers every operation that can occur only in CASE A.

For local tractability at a target Boolean sort, the useful categories are:

```text
C0
C1
OTHER
```

because `OTHER` has non-essentially-unary tractable representatives, while the positive projections are the projection-only hard/no-structure regime.

## 4. Frozen Fano instance

Use the seven vertices:

```text
0,1,2,3,4,5,6
```

and Fano-plane triples:

```text
012
034
056
135
146
236
245.
```

On every triple impose both paired clauses `R+` and `R-`.

The Boolean NAE instance has:

```text
0
```

two-colourings.

This is checked directly over all `2^7` assignments.

## 5. Exact multi-sorted certificate enumeration

Now enumerate the exact six-category operation labels on the seven sorts.

Search space:

```text
6^7
=
279936.
```

Require every Fano hyperedge to obey the exact paired-preservation quotient.

Result:

```text
GLOBAL PRESERVING ASSIGNMENTS
=
3
```

and they are exactly:

```text
(P0,P0,P0,P0,P0,P0,P0)

(P1,P1,P1,P1,P1,P1,P1)

(P2,P2,P2,P2,P2,P2,P2).
```

Thus:

```text
for every vertex v,

number of global preserving
mixed ternary polymorphisms
whose local interpretation at v
is constant or non-essentially-unary
=
0.
```

## 6. Theorem meaning

The Fano paired language therefore has only the three uniform projection certificates at the Boolean ternary level.

Consequently the Bulatov–Jeavons style multi-sorted tractability certificate cannot be made universal for arbitrary 3-CNF merely by:

- treating each Boolean variable as a separate sort;
- allowing variable-dependent interpretations;
- allowing a different global mixed ternary operation for each target sort;
- allowing arbitrary Boolean ternary operations away from the target.

The obstruction is exact and local to the fixed seven-variable Fano gadget.

## 7. Relation to multi-operation algebras

For Boolean CSP, Schaefer/Post classification implies that a tractable Boolean algebra must generate a non-essentially-unary / constant tractability operation rather than remain in the projection-only regime.

If a multi-operation multi-sorted algebraic certificate produced such a tractable Boolean term on a target sort, term composition would yield a global ternary multi-sorted polymorphism of the kind ruled out above.

Therefore this gadget blocks the **Boolean-domain** multi-operation escape represented by the classical multi-sorted tractability mechanism.

This does not block larger domains.

## 8. Consequence for 6I

The legitimate remaining direction is now narrower:

```text
BOOLEAN SINGLE-OPERATION
=
BLOCKED

BOOLEAN MULTI-SORTED /
MULTI-OPERATION CERTIFICATE
=
BLOCKED BY FANO CONTROL

NEXT
=
NON-BOOLEAN / LIFTED DOMAIN
WITH TRUE INTERNAL BLOCK STRUCTURE
```

The most relevant old mechanism donors are therefore:

1. lifted languages / input prototypes;
2. semilattice-block Mal'tsev hybrid algorithms;
3. few-subpowers / compact generating representations;
4. conservative / coloured-graph tractability recognition;
5. multi-sorted coordination on genuinely different/larger domains.

## 9. Next theorem shape

A future candidate must construct, in polynomial time, a lifted instance

```text
Lift(F)
```

over domains larger than the literal Boolean sort such that:

```text
SAT(F)
iff
SAT(Lift(F)),
```

and the lifted relations admit a source-bound tractable structure such as:

```text
COARSE QUOTIENT
=
SEMILATTICE / FINITE-WIDTH PROPAGATION

FINE BLOCKS
=
MAL'TSEV / AFFINE / FEW-SUBPOWERS

GLOBAL STATE
=
POLYNOMIAL COMPACT GENERATING REPRESENTATION.
```

Construction, recognition, interaction certificates, solve, reconstruction and complete history must all be polynomial in the original input length.

Without that lift theorem there is no successor.

## 10. Claim ceiling

```text
P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED

BOOLEAN_MULTISORTED_6I
=
BLOCKED

LIFTED_DOMAIN_6I
=
OPEN SOURCE-BOUND FRONTIER
```

Checker:

`research/tools/r5_e8_6i_boolean_multisorted_fano_checker.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_BOOLEAN_MULTISORTED_FANO_BLOCKER_2026-09-22_v1.0.json`
