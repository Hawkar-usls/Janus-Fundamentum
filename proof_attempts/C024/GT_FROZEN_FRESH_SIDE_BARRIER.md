# C024 — GT Frozen Fresh-Side Barrier

## Status

```text
LEMMA = PROVED
SCOPE = ABSTRACT_FROZEN_ONE_PASS
GT_SPECIFIC_ASSUMPTION = SAME_CUT_ABSENCE_IN_ENTRY_KEY
ARBITRARY_N = YES
POST_UNIT_EXTINCTION = NOT_PROVED_HERE
BRANCH_HANDOFF_EXTINCTION = NOT_PROVED_HERE
P_VS_NP = OPEN
```

## Purpose

C024 mechanically falsified the overstrong statement

> a frozen local-Resolution pass never creates a raw same-cut double bridge.

Raw same-cut pairs do occur in the output of a pass.  The correct theorem is
temporal: a pair created during a frozen pass cannot be reused during that same
pass.

## Definitions

Fix one Policy-0A state.

```text
K = exact entry key after pre-unit closure
F = set of clauses freshly produced by the frozen local-Resolution pass
R = K union F
```

The frozen parent universe of the pass is exactly `K`.  Every Resolution event
in the pass chooses both parents from `K`; clauses in `F` are appended to the
output but are not inserted into the current parent universe.

Let

```text
SameCut(C,D,p)
```

mean that `C` and `D` are component-spanning clauses, contain complementary
orientations of pivot `p`, the pivot is a bridge in both quotient graphs, and
the two induced bridge cuts are equal.

The internal structure of `SameCut` is irrelevant to this lemma.  It is only a
binary relation on clauses and a pivot.

## Lemma

### Frozen Fresh-Side Barrier

Assume

```text
for all C,D in K and all p:
    not SameCut(C,D,p).
```

Then every same-cut pair in `R` contains a fresh side:

```text
for all C,D in R and all p:
    SameCut(C,D,p)
    implies C in F or D in F.
```

Consequently, no same-cut pair first appearing in `R` is co-eligible as a
parent pair during the frozen pass which created it.

## Proof

Take `C,D in R` with `SameCut(C,D,p)`.

Suppose for contradiction that neither clause is fresh:

```text
C not in F
D not in F.
```

Because `R = K union F`, this implies

```text
C in K
D in K.
```

But the hypothesis says that no two clauses of `K` form a same-cut pair.  This
contradicts `SameCut(C,D,p)`.

Therefore

```text
C in F or D in F.
```

The frozen parent universe is `K`, so any side in `F` is unavailable as a
parent until a later exact key is admitted.  Hence the pair cannot be selected
for Resolution during the pass which first creates it.  QED.

## Strength and limitations

This lemma is independent of:

```text
n;
GT clause syntax;
quotient-graph size;
which inference created the fresh clause;
whether one or both sides are fresh;
whether the raw pair is safe or unsafe if resolved later.
```

It closes C024 obligation `T1` for arbitrary `n`, conditional only on the
inductive entry-key hypothesis.

It does not prove that a raw same-cut pair disappears before the next exact key.
That is the remaining handoff problem:

```text
R -> P  post-unit extinction/noncreation
P -> K' branch and child-preunit extinction
```

The two finite witnesses show both possibilities:

```text
GT_5: fresh/fresh complementary units die before P;
GT_4: entry/fresh mixed pair survives to P but dies before K'.
```

## Implementation bridge

The accompanying checker verifies, through `GT_8`, that:

```text
every local Resolution event uses only entry-key parents;
no fresh output clause is reused in the same pass;
every raw same-cut pair has at least one fresh side;
no exact entry key has a same-cut pair.
```

The checker is not the proof of the abstract lemma.  It certifies that the exact
Policy-0A implementation satisfies the frozen-parent assumptions used by the
proof.

## Consequence for the C024 induction

The local induction is reduced from three open transitions to two:

```text
T0 root same-cut absence                         finite/proof support available
T1 frozen fresh-side barrier                     PROVED
T2a post-unit extinction/noncreation             OPEN for arbitrary n
T2b branch handoff extinction                    OPEN for arbitrary n
T3 induction from T0+T1+T2a+T2b                 PENDING
```

Even after local closure, the global Policy-0A cache-DAG lower bound remains a
separate open gate.  No claim about `P` versus `NP` follows from this lemma.
