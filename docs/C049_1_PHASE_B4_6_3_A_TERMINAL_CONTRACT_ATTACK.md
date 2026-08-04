# C049.1 Phase B4.6.3-A — Terminal Contract Attack Gate

## Position

B4.6.2 proves that one frozen grouped GF(2) arrangement can complete every iterative-compression round, compute every selected root full set, reconstruct one accepting ancestry chain, and retain all failed refinements and cumulative work.

B4.6.3 must prove a stronger statement:

```text
accepting root entry exists
iff
there exists a whole-factor layout of width at most k
```

Only that biconditional can authorize both production terminals:

```text
FOUND_LAYOUT
NO_LAYOUT_AT_CAP
```

This A-gate does **not** claim the biconditional. It hardens the terminal contract before the induction proof is attempted.

## Executable attack ledger

The producer and independent verifier exercise four fixtures.

### Positive B4.6.2 cycle

The frozen B4.6.2 manifest digest is bound exactly. Its reconstructed order `[0,1,2]` is independently checked against every cut of the original grouped arrangement. The bounded fixture therefore has a valid `FOUND_LAYOUT` witness.

This is a fixture-level positive terminal only. It is not a general terminal-completeness theorem.

### Known no-layout fixture

```text
d = 2
k = 1
V0 = V1 = GF(2)^2
```

Both permutations have maximum cut width `2`; the exhaustive bounded oracle finds zero width-1 layouts. Nevertheless the trajectory engine has not supplied a complete negative root transcript for this fixture. The only admissible engine terminal is therefore:

```text
OPEN_TERMINAL_COMPLETENESS_PENDING
```

The fixture oracle is deliberately forbidden from being relabelled as a root-full-set `NO_LAYOUT_AT_CAP` certificate.

### Insertion-only obstruction

For the six-factor B4.1 obstruction, all six insertions of the final factor fail at `k=1`, while the complete bounded oracle finds exactly `72` valid layouts. A selected exact layout witness is emitted.

Thus:

```text
insertion failure != NO_LAYOUT_AT_CAP
```

### Budget cutoff

A deterministic two-permutation prefix is retained with every exact cut. Because the search is incomplete, the terminal remains:

```text
OPEN_WORK_BUDGET
```

A budget stop cannot be repaired into `NO_LAYOUT_AT_CAP` by changing outer digests.

## Independent replay

The verifier does not import the producer. It independently implements:

```text
GF(2) RREF
span membership
subspace intersection
exact cut transcripts
complete permutation enumeration
insertion candidate enumeration
budget-prefix replay
fixed-point certificate accounting
```

Five digest-repaired tamper controls are rejected:

```text
fake negative terminal
removed positive oracle witness
insertion-only false negative
budget-cut false negative
altered FOUND_LAYOUT order
```

## Frozen audit

```text
cases                              4
positive fixture layouts           6
known no-layout fixture layouts    0
insertion-obstruction layouts     72
successful insertion candidates    0
oracle cut recomputations        5120
fixed-point certificate bytes   13939
tamper controls rejected            5
artifact digest 5984b617e58c07eebf6c4a1eae2a8a1d058c3e43186564c407841cf88e75989a
file SHA-256    98e15569c0d09934f7997f0369754dc0aa29bde983dd1d905bb124c845b74087
```

## Remaining induction obligations

The following are still open:

```text
leaf full-set completeness as a general language statement
internal-node full-set biconditional
composition of B2 up_k preservation through every B3 node
root acceptance biconditional
complete negative root certificate
```

The next gate is therefore:

```text
C049.1_B4.6.3_B_ROOT_FULL_SET_BICONDITIONAL
```

That gate must identify the semantic language represented by each node full set, prove the leaf base case, prove preservation and reflection through every child-pair/lattice-path/refinement/up_k step, and only then promote an empty accepting root to `NO_LAYOUT_AT_CAP`.

## Strict boundary

```text
FOUND_LAYOUT fixture witnesses = ENABLED
NO_LAYOUT_AT_CAP production     = DISABLED
TERMINAL_COMPLETENESS           = NOT_PROVED
CURRENT_GLOBAL_TERMINAL         = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                         = OPEN
```
