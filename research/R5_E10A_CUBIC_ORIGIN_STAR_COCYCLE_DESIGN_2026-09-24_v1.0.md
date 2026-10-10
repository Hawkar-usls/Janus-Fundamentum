# R5 E10A — Cubic-Origin Star-Cocycle Design Characterization

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_PARENT_IMAGE_CHARACTERIZATION_AFTER_PA0006__NO_MINOR_IMAGE_CLOSURE_YET`

Authorizing audit:
`PA-0006-CUBIC-ORIGIN-TORSO-IMAGE`

Parent scope:
`R5_E10A_CUBIC_ORIGIN_TORSO_IMAGE_GATE_V1`

Checker:
`experiments/r5_e10a_cubic_origin_star_cocycle_design.py`

## 1. Purpose

PA-0006 re-bound the widened PA-0005 two-row class to the actual cubic origin

```
M([H|f]),
H=I+P+Q,
f=1,
```

without illegally imposing local cubic degree on a decomposition torso.

This note gives an intrinsic binary-matroid characterization of the **parent**
cubic origin itself.  It converts "row/column weight three" into a statement
about the cocycle space and the distinguished element.

It does not yet characterize arbitrary minors / torsos of that parent.

## 2. Star-cocycle design

Let M be a binary matroid on

```
E = U union {f},
|U|=n,
```

with distinguished element f.

A **cubic star-cocycle design through f** is a multiset

```
D_1,...,D_n
```

of cocycles of M such that:

1. every D_i contains f;
2. `|D_i-{f}|=3`;
3. every element `e in U` belongs to exactly three of the sets
   `D_i-{f}`, counted with multiplicity;
4. the incidence vectors `chi(D_i)` span the full cocycle space
   `C^*(M)`.

Repeated cocycles are allowed.  This matches repeated parity-check rows, which
are not forbidden by the cubic-origin representation.

## 3. Exact characterization theorem

### Theorem COCYCLE-DESIGN-1

For a binary matroid M with distinguished f and `|E-f|=n`, the following are
equivalent.

**(A)** M has a representation

```
[H | 1],
```

where H is an `n x n` binary matrix with every row and every column of
Hamming weight exactly three.

**(B)** `(M,f)` admits a cubic star-cocycle design.

#### (A) => (B)

Take the n rows of `[H|1]`.

The support of row i is

```
D_i = {f} union T_i,
|T_i|=3,
```

because row i of H has weight three.

Every non-f column of H has weight three, so every `e in U` lies in exactly
three T_i.

For a represented binary matroid, the row space is exactly its cocycle space.
Therefore the n rows span `C^*(M)).

Hence they form a cubic star-cocycle design.

#### (B) => (A)

Form an `n x n` binary matrix H whose i-th row is the incidence vector of

```
T_i = D_i-{f}.
```

Condition 2 gives row weight three.
Condition 3 gives column weight three.

Append an all-ones column indexed by f.  The row space of

```
[H|1]
```

is exactly the span of the `chi(D_i)`, which by condition 4 is
`C^*(M)`.

Two binary matrices represent the same binary matroid exactly when their row
spaces are the same cocycle space.  Thus `[H|1]` represents M.

QED.

## 4. Recovery of I+P+Q

The bipartite incidence graph of any square binary H with row/column weight
three is 3-regular.

By the standard 1-factorization / König edge-colouring theorem for regular
bipartite graphs, its edges split into three perfect matchings.

Relabel rows against one matching.  Their three incidence matrices are then

```
I, P, Q,
```

for permutation matrices P,Q with disjoint supports.

Therefore COCYCLE-DESIGN-1 is equivalently a characterization of the exact
`I+P+Q` parent representation; no extra local torso assumption was inserted.

## 5. Immediate source-derived identities

Since every non-f element is covered three times,

```
H 1 = 1.
```

Thus in `[H|1]` the sum of all columns is zero.  The full ground set is a
binary cycle; this is the already source-audited Eulerian parent property.

Summing all star cocycles gives the additional cocycle

```
U                    if n is even,
U union {f}           if n is odd.
```

These identities are controls only.  Eulerianity alone was already ruled out
as a tractability mechanism in the E10 source audit.

## 6. Why this is a lineage rebind and not local cubicity

The theorem is stated on the **full cubic parent**.

After deletion/contraction or 1/2/3-sum decomposition, an individual torso need
not itself possess such a design.  Therefore the old firewall remains:

```
DO NOT infer
local row/column degree three,
local I+P+Q,
or local n/3
for a torso.
```

The correct minor-image question becomes:

> Does the candidate torso admit an extension by deleted/contracted/interface
> elements to some binary parent carrying a cubic star-cocycle design through
> the distinguished f?

This is a liftability problem in cocycle space.

## 7. First finite controls

The checker verifies:

1. explicit square (3,3)-regular matrices generated from three disjoint perfect
   matchings satisfy the star-design conditions;
2. reconstruction from the star rows returns row/column weight exactly three;
3. a rank-4 seven-element deletion of a cubic parent admits the expected
   weight-three cocycle cover;
4. the standard S8 representation itself fails the *direct* square-cubic
   parity-check test: its cocycle space has only three weight-three cocycles
   and one coordinate is missed by all of them.

Control 4 is not promoted as a new S8 barrier: S8 may occur as a proper minor
of a larger cubic parent, and the E10 audit already records that the parent
Eulerian property is not minor-hereditary.

## 8. New exact subgate

Freeze:

```
R5_E10A_CUBIC_ORIGIN
STAR_COCYCLE_MINOR_LIFT_GATE_V1
```

Input:
a 3-connected S8-containing two-row torso/interface.

Question:
does there exist a polynomial-size extension by deleted / contracted /
separator elements and a distinguished-f star-cocycle design whose resulting
binary parent has this torso as the required minor?

Allowed exits:

A. universal polynomial construction for the PA-0005 complete-labelled
   scaffold (or another sufficient universal two-row carrier);

B. an exact obstruction to such a star-cocycle lift, yielding a genuine
   cubic-origin minor-image invariant.

Forbidden:

- treating direct star-design failure of the torso as minor-image failure;
- imposing local cubicity on the torso;
- returning to scalar separator weights;
- replacing a matroid minor proof by an equisatisfiable factor-graph
  realization;
- reopening generic PA-0005 PIT before the liftability test.

## 9. Ceiling

```
FULL CUBIC PARENT
<=> SPANNING 3-REGULAR STAR OF 4-COCYCLES THROUGH f
=
PROVED

I+P+Q RECOVERY
=
SOURCE-BOUND BIPARTITE 1-FACTORIZATION

DIRECT S8 CUBIC-PARENT REALIZATION
=
NEGATIVE CONTROL ONLY

STAR-COCYCLE MINOR LIFTABILITY
=
OPEN <<< NEXT

CUBIC-ORIGIN TORSO IMAGE
=
OPEN

DETERMINISTIC GF(2)^2 PRESCRIBED SHORTEST PATH
=
OPEN
```
