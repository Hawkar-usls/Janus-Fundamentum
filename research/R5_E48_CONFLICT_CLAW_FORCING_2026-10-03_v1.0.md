# R5 E48 — Conflict-Claw Forcing Terminal

Date: 2026-10-03

Status:
`EXACT_CONFLICT_CLAW_NECESSITY__NONCLAW_VERTICES_FORCED_SELECTED__POLYNOMIAL_UNSAT_AND_FULL_WITNESS_TERMINAL`

Scientific ceiling:

```text
THIS NOTE APPLIES TO THE FROZEN ALL-POSITIVE SQUARE+CUBIC+LINEAR E12 CARRIER.

FOR EVERY EXACT-ONE WITNESS S, EVERY UNSELECTED CONFLICT-GRAPH VERTEX IS THE
CENTER OF AN INDUCED CLAW K_{1,3} WHOSE THREE LEAVES LIE IN S.

THEREFORE EVERY VERTEX THAT IS NOT A CLAW CENTER IS FORCED SELECTED IN EVERY
WITNESS.

THIS YIELDS POLYNOMIAL FORCING/UNSAT RULES BUT DOES NOT SOLVE THE FULL E12 CORE.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be square+cubic+linear:

```text
every row has weight 3,
every column has weight 3,
any two distinct rows overlap in at most one column.
```

Let `G_A` be the conflict graph on variable-columns: two variables are adjacent iff
they occur together in some source row.

R5 E45 proves

```text
A is Exact-One SAT
iff
G_A has an independent set S of size n/3.
```

The statement below uses the stronger row-by-row Exact-One structure plus linearity.

## 2. Every unselected vertex produces three selected neighbors

Assume `S` is an Exact-One witness and take

```text
v notin S.
```

Because every variable occurs in exactly three source rows, let those rows be

```text
R_1,R_2,R_3.
```

Since `v` is unselected and every source row contains exactly one selected variable,
for each `i` there is a selected variable

```text
s_i in R_i - {v}.
```

Thus each `s_i` is adjacent to `v` in `G_A`.

## 3. The three selected neighbors are distinct

Suppose

```text
s_i=s_j=s
```

for two different rows `R_i,R_j`.

Then those two distinct source rows share both variables

```text
v and s,
```

so their overlap has size at least two, contradicting linearity.

Therefore

```text
s_1,s_2,s_3
```

are pairwise distinct.

## 4. The three selected neighbors are pairwise nonadjacent

All three `s_i` belong to the Exact-One witness `S`.

By R5 E45, `S` is an independent set of `G_A`. Hence

```text
s_1,s_2,s_3
```

are pairwise nonadjacent.

Therefore the induced subgraph on

```text
{v,s_1,s_2,s_3}
```

is exactly a claw `K_{1,3}` centered at `v`.

So we have proved:

### Theorem CLAW-NECESSITY

```text
boxed:
If S is an Exact-One witness, every v notin S is the center of an induced claw
whose three leaves belong to S.
```

Equivalently:

```text
boxed:
Every vertex that is not a claw center is selected in every Exact-One witness.
```

## 5. Forced set

Define

```text
F = {v in V(G_A) : v is not the center of any induced K_{1,3}}.
```

Then every Exact-One witness `S` satisfies

```text
boxed:
F subseteq S.
```

This gives immediate exact consequences.

### Rule C1 — cardinality UNSAT

Every witness has size exactly `n/3`. Therefore

```text
|F| > n/3
```

implies

```text
UNSAT.
```

Equivalently, a necessary SAT condition is that at least `2n/3` vertices are claw
centers.

### Rule C2 — conflict UNSAT

Because every witness is independent, if `F` contains an edge of `G_A`, then two
forced-selected variables conflict.

Hence

```text
F not independent
```

implies

```text
UNSAT.
```

### Rule C3 — complete witness terminal

If

```text
|F|=n/3,
```

then any witness must equal `F`.

Therefore simply check whether every source row contains exactly one member of `F`.
If yes, `F` is a complete Exact-One witness and the instance is SAT. If not, the
instance is UNSAT.

## 6. Polynomial recognition

A conflict vertex has degree six in the linear cubic carrier: its three source rows
contribute two distinct neighbors each.

To test whether `v` is a claw center, inspect all

```text
C(6,3)=20
```

triples of neighbors and ask whether some triple is pairwise nonadjacent.

Thus all claw centers and the forced set `F` are computable in linear time up to a
constant factor once `G_A` is built.

The resulting gate is deterministic polynomial time.

## 7. Why this is stronger than merely testing claw-free graphs

A claw-free conflict graph has

```text
F=V(G_A).
```

For every nonempty carrier,

```text
|F|=n>n/3,
```

so E48 immediately returns UNSAT.

Thus:

```text
boxed:
No nonempty all-positive square+cubic+linear Exact-One SAT carrier has a claw-free
conflict graph.
```

This strictly generalizes the special claw-free observation: E48 also forces every
individual non-claw-center even when many other vertices do contain claws.

## 8. Relation to R5 E47

R5 E47 proves that chordal 6-regular conflict components collapse to `K_7` and are
UNSAT.

Every vertex of `K_7` is a non-claw-center, so E48 also rejects such a component by
its forced-set cardinality rule.

The mechanisms are different:

```text
E47: chordal + regular rigidity -> K7;
E48: witness geometry -> every unselected vertex must expose an induced claw.
```

E48 therefore subsumes the final UNSAT conclusion of E47 on chordal instances while
remaining applicable far outside chordal graphs.

## 9. Scope caveat

This theorem is intentionally stated for the frozen **all-positive** E12 carrier.

After arbitrary literal negations in a signed 1-in-3 representation, selected
Boolean variables need not form an independent set of the unsigned co-occurrence
conflict graph. Therefore the claw theorem must not be silently transferred to a
general signed 1-in-3 instance.

The E12 route is enough for universality: R5 E12 already proves that this all-positive
square+cubic+linear subclass is NP-complete.

## 10. Router update

Add before expensive graph-language branches:

```text
CLAW0  build G_A;
CLAW1  compute all claw centers;
CLAW2  F = non-claw-centers;
CLAW3  |F|>n/3 -> UNSAT;
CLAW4  F not independent -> UNSAT;
CLAW5  |F|=n/3 -> verify F directly and terminate;
CLAW6  otherwise force F selected and N(F) unselected, then propagate Exact-One.
```

The final propagation step may trigger existing low-degree/projective/decomposition
rules.

## 11. Frontier

E48 does not close the irreducible cubic core. A survivor may have every unselected
vertex claw-capable and may have `F` small or empty, as in the toroidal SAT control.

But any future universal algorithm may now assume after exact propagation that the
remaining all-positive E12 core has sufficiently many claw centers and no forced
non-claw conflict.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e48_conflict_claw_forcing.py
```
