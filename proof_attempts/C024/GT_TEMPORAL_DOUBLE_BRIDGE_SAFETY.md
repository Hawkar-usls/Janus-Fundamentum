# C024 — GT Temporal Double-Bridge Safety

## Status

```text
RAW_SAME_CUT_NONCREATION = FALSIFIED
FINITE_RAW_SAME_CUT_TRANSIENTS = TWO_CLASSIFIED
FINITE_EXACT_KEY_SAME_CUT = ABSENT_THROUGH_GT_8
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
T2B_BRANCH_ROUTE_CLASSIFICATION = PROVED
T2B_ROOT_BRANCH_HANDOFF = PROVED_ARBITRARY_N
T2B_TWO_NODE_TAIL_WING_HANDOFF = PROVED
T2B_NONROOT_WING_REACHABILITY = OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION = PENDING_NONROOT_ONLY
GLOBAL_CACHE_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

## Operational stages

```text
K  exact entry key after pre-unit closure
R  frozen one-pass Resolution output
P  post-unit residual
B  raw child after the selected branch
K' reached child exact key after child pre-units
```

Fresh clauses in `R` are not parents in the frozen pass which created them. The explicit `B` stage separates branch contraction from child pre-unit consequences.

## Exact finite stage map through GT_8

```text
K:   611 double-bridge pairs / 0 same-cut
R:  1391 double-bridge pairs / 2 same-cut transients
P:  1390 double-bridge pairs / 1 same-cut survivor
B:  1208 executed children     / 0 same-cut pairs
K':                              0 same-cut eligible pairs
```

The two raw same-cut transients are completely classified:

1. `GT_4`, pivot `5`, pair `(5,6)` / `(-2,-5)`: the pair survives to `P`, but under both selected branch polarities pivot `5` becomes non-bridge in the left residual and the right residual is `DIRECTED_CYCLE`; the pair is absent already in `B`.
2. `GT_5`, pair `(10)` / `(-10)`: both sides are fresh local resolvents and close as `POST_UNIT_CONTRADICTION` before `P`.

## T1 — Frozen Fresh-Side Barrier

If

```text
R = K union F
```

and `K` contains no same-cut pair, every same-cut pair first appearing in `R` contains at least one fresh side. The frozen parent universe remains `K`, so the pair cannot be co-eligible during its birth pass.

```text
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
```

Implementation conformance:

```text
states                         615
frozen Resolution events   14,509
fresh parent reuse              0
raw same-cut pairs              2
fresh sides             one:1 / two:1
```

## T2a — Post-Unit Total-Component Collapse

Pure contraction can create same-cut pairs in abstract quotient graphs. The exact route classification nevertheless proves:

```text
spanning + spanning birth = impossible;
internal-only source birth = impossible;
branch-safe birth requires DIRECTED_CYCLE shield collapse.
```

Under the exact-key induction hypothesis, every clause in `R` is branch-safe. Before the first component-merging post-unit, earlier units are internal and preserve surviving external graphs. The first external unit therefore has a one-edge spanning graph already in `R`, which is possible only with exactly two relation components. It collapses the last two components to one, leaving no external bridge or cut.

```text
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
```

Finite support:

```text
post-unit events                            33
component-merging events                    10
all component merges                     2 -> 1
cycle-shield collapses                     385
collapsed residuals with bridge              0
new same-cut births                           0
```

## T2b — Pure branch route classification

Every branch threat belongs to one of two routes.

### Route A — inherited pair

An inherited same-cut pair can survive only if both clauses survive, the selected branch does not assign the pivot, and the selected contraction remains on one side of the common bridge cut. A cut-crossing contraction destroys bridgehood.

### Route B — newly born pair

A new same-cut pair from branch-safe sources requires directed-cycle shield collapse and simultaneous exposure of two complementary bridges with the identical cut. Two spanning sources can transmit a pair but cannot create one; bridge reflection would lift a child pair to its source.

```text
T2B_BRANCH_ROUTE_CLASSIFICATION = PROVED
```

Finite branch census:

```text
executed children                         1,208
acyclic branch assignments                1,208
same-cut pairs in P                           1
same-cut pairs in B                           0
new branch births                             0
branch cycle-shield collapses             42,966
bridge-bearing collapses                       2
same-cut complementary bridge partners         0
```

## Complete finite unshielded fate partition

Every immediate-local unshielded non-tail bridge occurrence in `P` was replayed through every executed child:

```text
unshielded P-occurrences                  19
root                                      16
non-root                                   3
branch-polarity transitions               38

CANONICALLY_SHIELDED                      12
CLAUSE_EXTINCT                            20
SPANNING_NONBRIDGE                         2
TAIL_SINGLETON_SAFE                        4
UNSAFE_UNSHIELDED                          0
```

Every canonical shield is proof-carrying: the exact residual of the original non-minimality clause `N_a` is reconstructed, membership in `K'` is checked, the complementary literal is verified non-bridge, and an explicit parallel quotient edge is emitted.

## Root branch handoff — arbitrary n

All selected root occurrences instantiate one of four graph implications:

```text
PIVOT:
    tracked literal assigned -> lineage extinct;

CROSS_CUT:
    contraction crosses the bridge cut -> pivot non-bridge;

INTERNAL_HEAD:
    selected clause literal merges the singleton head -> extinction or canonical N_a shield;

INTERNAL_TAIL:
    selected clause literal is the unique internal edge of a two-node tail wing -> extinction or tail-singleton safety.
```

The implications are proved under their explicit graph/CNF hypotheses. The finite template cover through `GT_12` has no fifth route:

```text
CROSS_CUT       13
INTERNAL_HEAD   40
INTERNAL_TAIL    3
PIVOT            6
unclassified     0
unsafe selected  0
```

Selector independence is false: among `6,960` hypothetical all-variable polarity trials through `GT_12`, `3,404` are unsafe, all on nonselected variables.

The exact unsafe set is the geometric class

```text
clause-absent
and INTERNAL_HEAD
and disjoint from the distinguished bad head endpoint.
```

Semantic equality with the child-replayed unsafe set holds on all 62 certified root occurrences.

Every root comparison variable has the same original frequency

```text
2(n-1),
```

so selected-versus-unsafe frequency differences equal fresh frozen-resolvent surplus differences.

### Complete root pivot blocks

A complete root pivot block accepts

```text
M(n) = (n-1)(n-2)
```

fresh clauses. Every nonpivot comparison edge incident to a pivot endpoint receives exact surplus

```text
S(n) = 3n-7,
```

while every edge disjoint from both endpoints receives zero. The addition budget fully processes exactly

```text
q = floor(n/12)
```

initial star pivots `(0,1),...,(0,q)` before entering one partial block.

For `n>=48`, `q>=4`. A safe star edge gains at least `qS`, while every unsafe edge gains at most `2S` from complete blocks and at most `S` from the partial block. Therefore

```text
fresh_surplus(selected) > fresh_surplus(unsafe)
```

for every unsafe alternative.

The remaining finite base `GT_4,...,GT_47` is independently replayed:

```text
root unshielded occurrences                       625
nonvacuous occurrences                            621
minimum strict selected-minus-unsafe gap            6
violations                                           0
```

Thus:

```text
FROZEN_UNSAFE_SURPLUS_SEPARATION = PROVED_ARBITRARY_N
ROOT_BRANCH_HANDOFF = PROVED_ARBITRARY_N
```

The root half of T2b is closed.

## Non-root route and proved tail-wing implication

Exactly three non-root unshielded P-occurrences occur through `GT_8`, all in one depth-two `GT_8` state:

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13)
```

For each bad pivot:

```text
bridge tail side                  two quotient nodes
selected literal                  -8
selected edge                     unique internal tail-wing edge
satisfying polarity               CLAUSE_EXTINCT
falsifying polarity               wing contraction -> TAIL_SINGLETON_SAFE
```

### Two-Node Tail-Wing Handoff

If a bad bridge separates a two-node tail wing and the selected clause literal is its unique internal edge, one polarity satisfies and removes the clause; the other removes the selected literal, contracts the complete wing to one quotient node, and makes the bad pivot tail-singleton safe.

```text
T2B_TWO_NODE_TAIL_WING_HANDOFF = PROVED
```

The only remaining local reachability theorem is:

### Non-Root Wing Reachability

Prove that every arbitrary-`n` reachable non-root unshielded P-occurrence is already handled by another safe route or satisfies the proved two-node tail-wing hypotheses.

## Remaining induction

```text
T0 root same-cut absence                   available
T1 frozen fresh-side barrier               PROVED
T2a post-unit total collapse               PROVED
T2b pure branch routes                     PROVED
T2b root branch handoff                    PROVED_ARBITRARY_N
T2b two-node tail-wing implication         PROVED
T2b non-root wing reachability             OPEN
T3 exact-key temporal induction            pending non-root only
```

Once Non-Root Wing Reachability is proved, T2b closes completely and T3 preserves same-cut absence through every

```text
K -> R -> P -> B -> K'
```

transition. This closes the local Resolution obstruction for exact Policy-0A on graph tautologies.

The global cache lower bound remains separate: the historical `2^(n-2)` novelty frontier must still be transferred to the exact cache DAG while charging local proof work, terminal events, and cache reuse.

## Principal artifacts

```text
proof_attempts/C024/GT_FROZEN_FRESH_SIDE_BARRIER.md
proof_attempts/C024/GT_POST_UNIT_TOTAL_COMPONENT_COLLAPSE_BARRIER.md
proof_attempts/C024/GT_BRANCH_HANDOFF_ROUTE_CLASSIFICATION.md
proof_attempts/C024/GT_ROOT_HANDOFF_GRAPH_LEMMAS.md
proof_attempts/C024/GT_ROOT_UNSAFE_SET_CHARACTERIZATION.md
proof_attempts/C024/GT_ROOT_UNIFORM_FREQUENCY_BASELINE.md
proof_attempts/C024/GT_ROOT_FROZEN_BLOCK_DOMINATION.md
proof_attempts/C024/GT_NONROOT_TWO_NODE_TAIL_WING_LEMMA.md
experiments/direct/janus_tear_gt_root_surplus_gap_finite_base.py
experiments/direct/janus_tear_gt_nonroot_unshielded_wing_profile.py
```

## Claim boundary

T1, T2a, the pure branch-route classification, arbitrary-`n` root branch handoff, and the two-node tail-wing implication are proved under their explicit hypotheses. Complete recursive handoff is finite-certified through `GT_8`, and the exact root theorem is proved for every `n` by the independently admitted finite base plus asymptotic block domination. Non-Root Wing Reachability, T3, the global cache-DAG lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
