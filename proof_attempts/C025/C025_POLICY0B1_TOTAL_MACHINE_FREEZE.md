# C025 — Policy-0B.1 Total Deterministic Machine Freeze

**Status:** `FROZEN_BASELINE__TOTAL_CORRECT__EXPONENTIAL_BRANCH_BOUND_EXPLICIT`.

Policy-0B.1 is the heuristic-free control machine used to isolate the remaining C2 search exponent.

Frozen transitions:

```text
canonicalize + exact subsumption
-> restrict by current root context
-> smallest-unit exact UP
-> complete fair frozen Resolution layer
-> retain only empty/unit or one canonical strict-subsuming strengthening per frozen clause
-> repeat to fixpoint
-> branch on minimum unassigned root id, false first
```

Disabled in this baseline:

```text
AUTOMATIC_EXTENSION_PROPOSAL = NONE
GLOBAL_REASON_CACHE          = NONE
EXACT_RESIDUAL_MEMOIZATION   = NONE
HEURISTIC_BRANCH_SCORE       = NONE
RANDOM_TIE_BREAK             = NONE
```

The C025-B/B2 reason languages remain independently proved library components; they are not silently invoked without a C2 discovery rule.

## Retention potential

For a frozen clause `D`, among all non-unit resolvents `C` with `C proper_subset D`, retain exactly

```text
min_C (|C|, canonical C).
```

Replace `D` by that clause.  No other non-unit candidate is retained.

Therefore active clause count cannot increase, and every nontrivial non-unit strengthening strictly reduces total active literal volume.

Derived units are propagated immediately rather than added to a permanent clause database.

## Correctness / termination

All transformations are exact under the current node context. Branching on one unassigned root variable partitions the remaining assignments into exhaustive `0/1` cases. Root-branch depth is at most `n`.

Thus the machine is a deterministic complete SAT decision procedure.

## Resource ceiling

Per-node preprocessing is polynomial in original input size because active clause count/literal volume never exceed the root bounds and every fair layer has at most `L^2/4` parent-pair attempts.

But:

```text
recursive_nodes <= 2^(n+1)-1 <= 2^(N+1)-1.
```

Hence only

```text
TOTAL_WORK <= 2^N * N^O(1)
```

is currently established.

This freezes the hidden exponential into the branch frontier rather than hiding it in heuristics.

## C2 handoff

A future discovery module must be deterministic, checkable, representation-bounded and must include a **global** progress/amortization theorem. Polynomial work per state is not enough.

```text
POLY_WORK_PER_STATE != POLY_NUMBER_OF_STATES
POLICY0B1_FROZEN != C2_SOLVED
P_VS_NP = OPEN
```

Arbiter specification: `Hawkar-usls/Demi_Head/docs/TOPA_POLICY0B1_TOTAL_MACHINE_FREEZE.md`.
