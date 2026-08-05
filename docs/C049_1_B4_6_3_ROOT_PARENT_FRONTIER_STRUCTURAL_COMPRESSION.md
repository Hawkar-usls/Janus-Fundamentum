# C049.1 B4.6.3 — root parent-frontier structural compression

```text
BASE = admitted PR #104
BASE_EXACT_HEAD = babdf21ba20c1d24ed97fff4bb14121d0dfc1287
ROOT_NODE = 10
P_VS_NP = OPEN
```

## Purpose

PR #104 reaches root node 10 on the hardened ancestry and freezes the exact preflight:

```text
left Node-9 entries   = 252
right leaf-5 entries  = 36
child pairs           = 9,072
fine refinements      = 4,954,128
common boundary       = [1]
parent boundary       = []
shrink                = non-identity
```

The previous executor stopped honestly at its `2,000,000` refinement cap. This layer does not merely raise that cap. It replaces fine-path traversal with an exact multiplicity-preserving dynamic program over root scalar cell matrices.

## Structural dynamic program

For each of the `9,072` certified child pairs, every lattice cell receives the exact B3 join correction followed by the genuine shrink correction `[1] -> []`. Because the parent boundary is empty, each projected statistic is a scalar lambda value.

The producer then computes, at every lattice cell, a map

```text
raw scalar prefix stream -> exact path multiplicity
```

from the three Delannoy predecessors. It never materializes an individual fine-refinement record and never enumerates a fine lattice path. Pairwise multiplicities are checked against the exact Delannoy number before aggregation.

```text
child Cartesian pair records materialized = 0
fine lattice paths enumerated             = 0
fine refinement records materialized      = 0
```

The complete multiplicity ledger is:

```text
fine refinement multiplicity        = 4,954,128
distinct raw scalar streams          =   194,247
compact scalar classes               =        77
successful refinements               =     7,825
failed refinements                   = 4,946,303
successful compact generators        =         6
failed compact classes               =        71
```

Width multiplicities:

```text
width 0 =         1
width 1 =     7,824
width 2 = 1,440,803
width 3 = 3,505,500
```

The six successful empty-boundary generators and their refinement multiplicities are:

```text
0    ->     1
01   -> 1,898
010  -> 1,351
1    ->   221
10   -> 1,898
101  -> 2,456
```

Every one of the other 71 compact classes stores a first scalar value greater than `k=1`; its complete multiplicity is therefore a universal failed-refinement block. Successful and failed multiplicities sum exactly to `4,954,128`.

## Decisive root-reflection correction

A direct reuse of the Node-9 lower-envelope shortcut is unsound at the root.

The two retained Node-9 zero envelopes joined with the leaf-5 zero envelope have only eight quotient paths:

```text
7 paths -> 010
1 path  -> 0
```

All eight lower-envelope paths have width at most one. Nevertheless, the complete child languages contain `4,946,303` failed refinements and four successful compact sequences absent from the lower-envelope outputs:

```text
01, 1, 10, 101
```

Therefore:

```text
LOWER_ENVELOPE_SUCCESS
DOES NOT REFLECT
UNIVERSAL_SUCCESS_OF_A_ROOT_QUOTIENT_PATH
```

The admitted contract must retain the complete typical-pattern child languages and exact path multiplicities. The producer records this counterexample as part of the theorem artifact; a verifier must reject any repaired-digest attempt to set reflection to true.

## Independent verification

The independent verifier imports neither the producer nor its functions. It uses a reverse-priority compactifier and a backward memoized suffix recurrence rather than the producer's forward prefix recurrence. It independently reconstructs:

```text
source byte and semantic bindings
root geometry and non-identity shrink
all 9,072 pair matrices
all pairwise Delannoy multiplicities
194,247 distinct raw streams
77 compact scalar classes
7,825 / 4,946,303 success-failure partition
six successful generators
71 universal failure classes
lower-envelope reflection obstruction
fixed-point certificate bytes
```

Twelve invariants and ten digest-repaired tamper controls are required.

## Strict boundary

This theorem closes the root generator frontier before B2 `up_k`. It does not yet install the root full set into the executor or reconstruct a whole-factor layout.

```text
ROOT_PARENT_GENERATOR_FRONTIER_COMPLETE = TRUE
ROOT_PARENT_REFINEMENT_COMPLETE         = TRUE
ROOT_PARENT_UP_K_COMPLETE               = FALSE
ROOT_FULL_SET_COMPUTED                  = FALSE
ROOT_EMPTY_PROVED                       = FALSE
TERMINAL_COMPLETENESS_PROVED            = FALSE
FOUND_LAYOUT                            = FORBIDDEN
NO_LAYOUT_AT_CAP                        = FORBIDDEN
CURRENT_GLOBAL_TERMINAL                 = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                                 = OPEN
```

Next gate after exact-head admission:

```text
C049.1_B4.6.3_ROOT_SIX_GENERATOR_UP_K_CLOSURE
```
