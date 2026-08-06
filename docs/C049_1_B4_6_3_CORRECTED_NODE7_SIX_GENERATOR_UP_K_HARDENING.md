# C049.1 B4.6.3 — corrected Node-7 six-generator `up_k` repair

## Stack boundary

```text
BASE_PR = #112
BASE_EXACT_HEAD = 796ad144de65906c702e29928f683e6d53e3529c
REPAIR_TARGET = PR #113
GATE = C049.1_B4.6.3_CORRECTED_NODE7_SIX_GENERATOR_UP_K_HARDENING
```

Draft only. No merge and no automatic merge.

## Repair obligations

The first exact-head candidate was CI-green but not admitted. REPAIR-1 closes three proof-package defects.

### 1. True repeated `up_k`

The first application materializes the exact `7,776`-trajectory closure of the six corrected Node-7 zero envelopes. The second application accepts those `7,776` trajectories themselves as the new generator family.

```text
first up_k input generators  = 6
first up_k output entries    = 7,776
second up_k input generators = 7,776
second up_k relation checks  = 960,000
second up_k output entries   = 7,776
first stream bytes           = 2,286,145
second stream bytes          = 2,286,145
byte-identical               = TRUE
```

The second pass consumes neither original six generator identifiers nor a projection back to the original family.

### 2. Canonical GF(2) RREF

Every boundary subspace is normalized by full Gaussian elimination over GF(2), including elimination above and below each pivot. Rows are ordered by descending pivot, yielding one representation per subspace.

The proof package includes equivalent-basis controls for all five subspaces of `GF(2)^2`, including:

```text
span([2,1]) = span([3,1]) = span([3,2]) = [2,1]
```

### 3. Nonvacuous direct-witness control

The actual six-generator family has no removals. A separate three-generator fixture therefore exercises the deletion contract:

```text
CTRL-A = 0
CTRL-B = 01
CTRL-C = 1
```

`CTRL-B` and `CTRL-C` are removed only with explicit direct witnesses from retained `CTRL-A`. The digest-repaired tamper suite replaces the `CTRL-A -> CTRL-C` direct witness with the closure-only chain

```text
CTRL-A -> CTRL-B -> CTRL-C
```

and the independent verifier rejects it with:

```text
DIRECT_WITNESS_MISSING
```

## Candidate receipts

```text
input generators       = 6
ordered preorder pairs = 36
preorder relations     = 6 reflexive relations
retained generators    = 6
direct removals        = 0
first closure entries  = 7,776
second closure entries = 7,776
invariants             = 10/10
digest-repaired tampers = 10/10
```

```text
certificate bytes  = 10,137
certificate sha256 = 924e55a651518ce004964f5d7c5ea30e67424ca34507f18eb568341fc96528e0
semantic digest    = cfd99ea716076414847749fb98185cea63c2cf44e9ceaa659bf37eb9e8fc366a
closure digest     = 99a702ea7005e4a41d99fc4454040314ab106632672b267bffb5f59e29afa728
```

`ORIGINAL`, `REVERSED`, and `SEEDED_SHUFFLE` builds must remain byte-identical.

## Pending admission boundary

```text
PR112_CORRECTED_NODE7_FRONTIER_COMPRESSION = ADMITTED
PR113_REPAIR_1_IMPLEMENTED = TRUE
PR113_NODE7_SIX_GENERATOR_UP_K_ADMITTED = FALSE
CORRECTED_NODE7_PARENT_REFINEMENT_COMPLETE = TRUE
CORRECTED_NODE7_PARENT_UP_K_COMPLETE = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

Only exact-head CI plus a separate semantic admission review may promote the Node-7 `up_k` theorem.
