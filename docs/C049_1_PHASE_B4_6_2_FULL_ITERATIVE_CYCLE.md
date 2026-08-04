# C049.1 Phase B4.6.2 — full iterative-compression cycle

## Result

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

## Frozen audit

```text
rounds                                  2
scaffolds constructed                   2
root full sets computed                 2
layouts reconstructed                   2
child pairs processed               1,548
lattice paths processed           166,516
failed refinements                163,051
successful refinements              3,465
raw precompact join statistics   1,312,448
round transcript chunks                 60
uncompressed chunk bytes        961,660,314
compressed chunk bytes           21,599,494
fixed-point outer bytes                8,623
cumulative work                  5,413,165
final factor order                 [0,1,2]
final exact maximum width                 1
failures                                  0
```

Frozen outer manifest digest:

```text
5e7df2407456fe41a5dadda4f8855df5f7ab2ae96dfac637d8857c2c4c0c44e6
```

Round 2 reconstructs `[0,1]` with exact width `0`. Round 3 consumes that
reconstructed order, internally appends factor `2`, executes the complete
scaffold and reconstructs `[0,1,2]` with exact width `1`.

## Proof-carrying contract

Each round emits a complete chunked scaffold transcript and a separate
reconstruction receipt. The outer artifact binds all round transcript roots,
previous and reconstructed orders, exact maximum widths and one cumulative
ledger that never resets between rounds. The fixed-point serialized byte count
is charged into the final work total.

The independent verifier imports neither the B4.6.2 producer nor a supplied
layout. It replays scaffold geometry, leaf full sets, all B3 refinements, B2
closure semantics, node handoffs, reconstruction ancestry, round transitions
and final layout. CI regenerates the complete package twice and compares every
outer artifact, round manifest and reconstruction receipt.

Before the cycle runs, CI independently replays the frozen B1, B2, B3 and B4.1
certificates. Four digest-repaired controls alter the final order, a round
cumulative counter, an affine offset and the forbidden `FOUND_LAYOUT` flag.

The first independent-verifier candidate omitted the producer's charged
`ROOT_ACCEPTANCE_TESTS` event from reconstruction replay. It correctly rejected
the transcript but for a verifier-accounting mismatch. The hardened verifier
adds that missing replay event; the producer and frozen result did not change.

## Files

```text
experiments/direct/janus_c049_1_b4_6_2_full_iterative_cycle.py
experiments/direct/janus_c049_1_b4_6_2_full_iterative_cycle_verifier.py
experiments/direct/janus_c049_1_b4_6_2_full_iterative_cycle_verifier_hardened.py
experiments/direct/C049.1-JANUS-PHASE-B4.6.2-FULL-ITERATIVE-COMPRESSION-CYCLE.frozen.json
registry/c049.1-phase-b4.6.2-status.json
.github/workflows/validate-c049-1-phase-b4-6-2-full-iterative-cycle.yml
```

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
