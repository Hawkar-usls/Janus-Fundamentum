# C049.1 Phase B4.6.2 — full iterative-compression cycle

## Scope

B4.6.2 executes every iterative-compression round of one frozen grouped
`GF(2)` arrangement. It starts from the canonical one-factor layout and, for
each new whole-factor block:

1. constructs the B4.2 charged width-at-most-`3k` scaffold internally;
2. computes every node full set through B3 expand/join/shrink and B2 `up_k`;
3. retains every child pair, Delannoy path, failed refinement, raw precompact
   join, dominance deletion and cumulative-work event;
4. selects an accepting root entry deterministically;
5. follows the complete B4.6.1 ancestry chain to the leaves; and
6. independently recomputes the exact cut-width transcript of the resulting
   factor order before passing it to the next round.

The frozen cycle uses

```text
ambient dimension = 2
k = 1
whole factor blocks = [[1], [2], [1]]
affine offsets = [0, 1, 1]
initial order = [0]
rounds = 2, 3
```

The repeated normal-space block with a distinct affine offset forces a
nonzero-boundary transport in the second round. Factor identity and offsets are
never merged.

## Proof-carrying contract

Each round emits a complete chunked scaffold transcript and a separate
reconstruction receipt. The outer artifact binds all round transcript roots,
previous and reconstructed orders, exact maximum widths and one cumulative
ledger that never resets between rounds. The fixed-point serialized byte count
is charged into the final work total.

The independent verifier does not import the B4.6.2 producer. It replays the
scaffold geometry, leaf full sets, all B3 refinements, B2 closure semantics,
node handoffs, reconstruction ancestry, round transitions and final layout. CI
also regenerates the complete package twice and compares every manifest and
reconstruction artifact.

Before the cycle runs, CI independently replays the frozen B1, B2, B3 and B4.1
certificates. Four digest-repaired controls alter the final order, a round
cumulative counter, an affine offset and the forbidden `FOUND_LAYOUT` flag.

## Strict boundary

B4.6.2 proves only that the implemented positive reconstruction mechanism can
be composed across all rounds of the frozen instance. It does not yet prove the
published terminal-completeness invariant for every width-`k` layout and does
not enable an empty-root negative conclusion.

```text
LOCAL_RESULT = FULL_ITERATIVE_COMPRESSION_CYCLE_REPLAYED
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
NEXT_GATE = C049.1_B4.6.3_TERMINAL_COMPLETENESS
P_VS_NP = OPEN
```

Draft only. No automatic merge.
