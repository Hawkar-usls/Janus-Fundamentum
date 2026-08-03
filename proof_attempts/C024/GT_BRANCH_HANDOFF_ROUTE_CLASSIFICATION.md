# C024 — GT Branch-Handoff Same-Cut Route Classification

## Status

```text
THEOREM = PROVED
SCOPE = ONE_CONSISTENT_BRANCH_RESTRICTION_ON_ARBITRARY_QUOTIENT
EXISTING_PAIR_CROSS_CUT_EXTINCTION = PROVED
SPANNING_SPANNING_BRANCH_BIRTH = IMPOSSIBLE
BRANCH_SAFE_BIRTH_REQUIRES_CYCLE_SHIELD_COLLAPSE = PROVED
FINITE_RAW_BRANCH_SAME_CUT = ABSENT_THROUGH_GT_8
SELECTED_BRANCH_CUT_OR_SHIELD_DICHOTOMY = OPEN
T2B_BRANCH_HANDOFF = OPEN
P_VS_NP = OPEN
```

## Purpose

After T1 and T2a, the only local C024 gate is the branch handoff

```text
P --selected branch literal--> B --child pre-units--> K'.
```

Unlike post-unit closure, a branch assignment may merge relation components
while more than two remain.  Abstract cycle-shield-collapse births are therefore
possible.  The correct arbitrary-quotient theorem is a route classification,
not universal branch safety.

There are exactly two ways for a same-cut pair to threaten the next exact key:

```text
A. an existing same-cut pair in P survives the branch restriction;
B. the branch restriction creates a new same-cut pair in B.
```

This note proves the pure graph conditions for both routes and isolates the
remaining GT-specific selector theorem.

## Model

Fix the quotient relation components immediately before the selected branch.
Let

```text
q : V -> V/{x=y}
```

be the identification induced by assigning a comparison whose endpoints lie in
distinct current components `x,y`.  An internal branch assignment is the
identity on quotient vertices.

For every surviving clause, the post-branch external graph is the image under
`q` of its source external graph, with loops omitted.  A satisfied source clause
is removed and cannot participate in `B`.

## Route A — inherited same-cut pair

Let clauses `C,D` contain complementary pivot literals and suppose those pivot
edges are bridges inducing the same source cut

```text
S | T.
```

### Lemma A1 — crossing the common cut destroys both pivot bridges

Assume the branch identifies

```text
x in S,
y in T.
```

Delete the pivot edge from either source graph.  Before contraction its two
bridge sides are disconnected.  After identifying `x` and `y`, the images of
those sides share the vertex `q(x)=q(y)`.  Hence the graph with the pivot removed
is connected across the former cut.

The pivot is therefore not a bridge in the residual clause.  This applies to
both parents because their bridge cuts are equal.

Consequently an inherited same-cut pair cannot survive a branch which crosses
its common cut.

### Lemma A2 — assigning the pivot itself destroys the pair

If the selected branch variable is the complementary pivot, one polarity
satisfies one parent and the other polarity satisfies the other parent; the
opposite parent loses its pivot literal.  In either child the complementary
pivot pair is absent.

### Necessary condition for inherited survival

If both clauses survive and their same-cut pivot bridges remain after a branch
which is not the pivot itself, then the branch endpoints must lie on the same
side of the common cut.

Thus Route A is reduced to a selector obligation:

> the deterministic Policy-0A branch must cross every reachable raw same-cut
> transient cut, assign its pivot, or otherwise remove/protect one side before
> exact-key admission.

## Route B — newly born pair

Assume no source same-cut pair exists in `P`, but two residual clauses in `B`
form one.

The post-unit cycle-shield route theorem applies to any consistent comparison
restriction, including a branch restriction.

### Lemma B1 — internal-only sources cannot participate

Further component identification cannot turn an internal source literal into an
external edge.  Hence an `INTERNAL_ONLY` source cannot yield a
component-spanning residual parent.

### Lemma B2 — spanning/spanning pairs are reflected, not born

For a component-spanning source graph:

```text
connectedness survives contraction;
a residual bridge was already a source bridge;
the contracted endpoints lie on one side of every surviving bridge cut;
equal residual cuts lift uniquely to equal source cuts.
```

Therefore two component-spanning sources which form a same-cut pair after the
branch already formed a same-cut pair before it.  They cannot create Route B.

### Theorem B3 — branch-safe birth requires cycle-shield collapse

If both source clauses are branch-safe and a new same-cut pair appears in `B`,
at least one source must be `DIRECTED_CYCLE`, and its last protecting external
directed cycle must fail to survive the branch restriction.

Thus Route B has the unique branch-safe form

```text
DIRECTED_CYCLE source
+ selected branch contraction
+ cycle-shield collapse
+ exposed bridge
+ complementary exposed bridge with the same cut.
```

One exposed bridge is insufficient.  A same-cut birth requires a complementary
bridge partner inducing the identical cut.

## Combined branch-handoff classification

Under the exact-key local invariant, every same-cut threat in raw child input
`B` belongs to exactly one of:

```text
ROUTE_A_INHERITED:
  an existing P pair whose common cut was not crossed;

ROUTE_B_CYCLE_COLLAPSE:
  at least one cycle-protected source loses its final shield and two
  complementary same-cut bridges are exposed.
```

There is no third branch-safe route.

## Exact finite branch census through GT_8

Across all parent states at novelty at most `n-2`:

```text
branch child records                    1,208
executed children                       1,208
acyclic branch assignments              1,208
cyclic branch assignments                   0
component-joining branch states           436
internal branch states                     168

same-cut pairs in P                         1
same-cut pairs in raw B                     0
same-cut pairs in exact K'                  0
raw transmitted same-cut pairs              0
raw branch same-cut births                  0
```

The unique Route A candidate is the GT_4 mixed entry/fresh transient.  In both
branch polarities the left pivot ceases to be a bridge already in raw `B`; the
right residual is directed-cycle protected.  Child pre-units are not needed to
establish raw same-cut absence.

## Exact Route B exposure profile

The finite branch contractions collapse

```text
42,966
```

directed-cycle shields.  Only two collapsed residuals expose any bridge.  They
are the two polarities of one GT_8 source lineage:

```text
source       = (-9,11,-14,-16,-17,-18,-23)
source class = DIRECTED_CYCLE
residual     = (-9,11,-14,-17,-18,-23)  or
               (-9,11,-14,-16,-17,-18)
exposed edge = -17
role         = TAIL_SINGLETON
```

The source is a fresh local resolvent with root ancestry

```text
N_6 + four transitivity axioms.
```

For the complementary literal `+17`, the two children contain 44 candidate
occurrences in total:

```text
DIRECTED_CYCLE         42
COMPONENT_SPANNING      2
SPANNING_NONBRIDGE      2
SAME_CUT_BRIDGE         0
```

The sole acyclic spanning candidate in each child is the canonical root clause

```text
N_6 = (6,12,17,21,24,26,-28),
```

whose parallel edges from the merged head component keep `+17` non-bridge.
Every other complementary candidate remains directed-cycle protected.

Therefore the two bridge exposures are isolated and Route B is absent in the
finite frontier.

## Remaining arbitrary-n theorem

The complete T2b obligation is now equivalent to the following GT-specific
statement.

### Selected-Branch Cut-or-Shield Dichotomy

For every reachable pre-frontier branch state:

1. every inherited raw same-cut pair is crossed by the selected branch, has its
   pivot assigned, or loses a parent before exact-key admission; and
2. every cycle-shield collapse exposing a bridge has no complementary exposed
   bridge with the same cut.  Every complementary occurrence is instead
   cycle-protected, internal, unsafe-and-terminal, or carries a pivot-avoiding
   alternate path.

The existing frequency and singleton-tail certificates support the expected
mechanism:

```text
branch touches the isolated tail -> inherited bridge cut is destroyed;
branch avoids the tail and merges the head -> canonical N_tail shield gains
                                             parallel entry edges;
disjoint branch -> the previous shield is preserved.
```

The finite bridge-shield witness supplies explicit pivot-avoiding paths for all
119 component-spanning complementary occurrences of 62 non-tail exact-key
bridges.  Converting those paths and the branch-frequency rule into an
arbitrary-`n` induction remains the open part.

## Consequence

A proof of Selected-Branch Cut-or-Shield Dichotomy closes

```text
T2B_BRANCH_HANDOFF
```

and, with T0, proved T1, and proved T2a, closes the temporal exact-key induction.
That would eliminate the local Resolution obstruction for exact Policy-0A on
graph tautologies.

The global cache-frontier lower bound would remain a separate gate.

## Mechanical artifacts

```text
experiments/direct/janus_tear_gt_branch_handoff_stage_census.py
experiments/direct/janus_tear_gt_branch_bridge_exposure_profile.py
experiments/direct/janus_tear_gt_bridge_shield_path_witness.py
experiments/direct/janus_tear_gt_surviving_branch_frequency_certificate.py
proof_attempts/C024/GT_SINGLETON_TAIL_BRANCH_HANDOFF_LEMMA.md
```

## Claim boundary

The route classification and cut-crossing extinction lemmas are proved for one
consistent restriction on an arbitrary quotient.  The Selected-Branch
Cut-or-Shield Dichotomy, completed T2b induction, global cache lower bound, and
`P` versus `NP` remain open.
