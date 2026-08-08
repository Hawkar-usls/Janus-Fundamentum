# C049.1 B4.6.3 — corrected Node-6 `up_k` hardening

```text
BASE_PR = #109
BASE_EXACT_HEAD = 243b841f1a3023f0acfb3d8b1e381798f369921b
P_VS_NP = OPEN
```

## Source boundary

PR #109 independently replayed the first internal join on the corrected ordinary H/V path domain and froze exactly:

```text
child pairs              = 1,296
ordinary H/V refinements = 38,240
successful refinements   = 2,684
failed refinements       = 35,556
unique generators        = 414
diagonal steps           = 0
```

The generic B2 engine stopped honestly at its semantic work capability. This layer consumes only that corrected transcript. It does not consume the historical Node-6 generator family, historical Node-6 closure, or any Node-7 through root full set.

## Corrected preorder partition

The 414 corrected generators form exactly two collapsed `(L,R)` skeleton signatures:

```text
bucket 0 = 207 generators
bucket 1 = 207 generators
```

Each bucket has one unique canonical zero envelope. The producer supplies a direct extension-preorder witness from that envelope to every other generator in the same bucket and proves that the reverse relation is absent.

```text
input generators    = 414
retained generators = 2
 direct removals     = 412
```

The two skeletons differ at their middle boundary state. An exhaustive ordered cross-bucket audit performs `85,698` relation tests and finds zero relations.

## Exact closure

For `dim(B)=2` and `k=1`, every skeleton run has exactly six compact binary typical patterns:

```text
0
01
010
1
10
101
```

Each corrected skeleton has three distinct runs. Therefore its complete reachable catalog has `6^3 = 216` trajectories, and both skeletons together have:

```text
complete corrected Node-6 up_k catalog = 432 entries
```

The 414 input generators are a strict subset of this closure. The hardening discovers 18 additional reachable entries, nine in each skeleton bucket.

```text
up_k(original 414) = up_k(retained 2) = 432 entries
```

This differs from the historical contaminated result `468 -> 3 -> 468` and does not reuse it.

## Independent replay

The verifier imports neither the producer nor B1/B2 theorem cores. It independently:

```text
replays every compressed generator chunk and record digest
reconstructs both skeleton buckets
replays all 412 direct deletion witnesses
recomputes all 85,698 ordered cross-bucket relation tests
exhaustively tests 65,534 binary scalar sequences
rebuilds all 432 reachable trajectories
replays every reachable-entry witness
checks the 18 new entries and their 9+9 partition
recomputes the complete work ledger
checks 14 invariants
rejects 12 digest-repaired semantic tamper attacks
```

## Strict boundary

```text
PR109_CORRECTED_FIRST_JOIN = ADMITTED
CORRECTED_NODE6_PARENT_REFINEMENT_COMPLETE = TRUE
CORRECTED_NODE6_PARENT_UP_K_COMPLETE = CI_PENDING
CORRECTED_NODE6_FULL_SET_ENTRY_COUNT = CI_PENDING
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
CORRECTED_NODE7_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_STRUCTURAL_COMPRESSION_ADMITTED = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
ROOT_EMPTY_PROVED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

Next gate after exact-head CI admission:

```text
C049.1_B4.6.3_CORRECTED_NODE6_INTEGRATION_AND_NODE7_PARENT_REFINEMENT
```
