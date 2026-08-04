# C049.1 Phase B4.6.3 — negative root engine replay

## Target

Exercise the B4.5 full-set engine on a genuine width-`1` negative instance
without allowing an incomplete execution to collapse to `NO_LAYOUT_AT_CAP`.

## Fixture

The whole-factor arrangement consists of six one-dimensional subspaces of
`GF(2)^3` in the order

```text
[2], [4], [6], [3], [5], [1]
```

with `k=1`. The first five factors in the displayed order have exact width
vector

```text
[1,1,1,1]
```

so the iterative-compression precondition is satisfied. After adding the sixth
factor, all `720` whole-factor permutations are replayed independently:

```text
minimum width = 2
accepting width-1 layouts = 0
```

The canonical B4.2 scaffold has width vector

```text
[1,2,2,2,1]
```

and therefore forces the engine through its first boundary-coordinate
dimension-two `up_k` computation.

## Result contract

The producer runs the existing B4.5 node kernel with an explicit B2 capability
of `2,000,000`. Capability exhaustion is intercepted at the node boundary,
converted into an honest proof-carrying OPEN terminal, and the already emitted
pair/refinement/generator/duplicate transcript is flushed and retained.

The independent verifier checks:

```text
all 720 permutations and the previous width-1 order
exact scaffold width profile
complete pair inventory before B2
sum of pair Delannoy counts = refinement records
refinements = successful + failed
successful attempts = disjoint generator provenance partition
all duplicate deletions
attempted B2 counter = cap + 1
no root receipt exists
NO_LAYOUT_AT_CAP remains disabled
```

## Expected interpretation

A capability stop is not a negative root. It establishes only that no
trajectory was lost in the completely processed prefix before the semantic
`up_k` boundary. It does not justify a claim about missing root entries.

```text
NO_TRAJECTORY_LOSS_BEFORE_B2 = CHECKED
NO_UNSOUND_DOMINANCE_CLAIM = CHECKED
NO_MISSING_ROOT_ENTRIES = NOT_REACHED
NEGATIVE_ROOT_REACHED = FALSE
```

If the bounded run stops at dimension-two `up_k`, the next gate is

```text
C049.1_B4.6.3_DIMENSION_TWO_UP_K_CAPABILITY_HARDENING
```

## Strict boundary

```text
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

H002 and SIM-3 remain untouched.
