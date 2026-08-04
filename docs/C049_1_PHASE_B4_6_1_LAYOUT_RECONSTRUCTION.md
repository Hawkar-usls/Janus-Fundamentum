# C049.1 Phase B4.6.1 — root-trajectory layout reconstruction

## Purpose

B4.5 computes a nonempty root full set for one complete charged B4.2 scaffold, but it deliberately stops before reconstructing a concrete linear layout. B4.6.1 adds the first backward witness pass.

The producer does not accept a supplied scaffold, full-set table, transcript, or layout as discovery. It regenerates the frozen B4.5 transcript internally, selects one accepting empty-boundary root entry by a deterministic digest rule, and follows only producer-issued ancestry links.

## Reconstruction chain

For every selected internal full-set entry, the receipt binds:

```text
up_k entry
-> retained source generator
-> generator provenance id
-> canonical successful refinement
-> child pair
-> left and right child entry indices
-> recursively reconstructed child receipts
```

The B2 extension witness between the retained generator and the selected `up_k` entry is replayed at every node. The successful B3 refinement must have output width at most `k`, and its output trajectory must equal the retained generator used by the selected entry.

At a whole-factor leaf, the receipt terminates with the original factor identifier, its complete normal-space block, and its affine offset. Internal receipts concatenate the reconstructed child orders according to the certified scaffold orientation.

## Exact soundness check

After reconstructing the complete factor order, the producer recomputes every prefix/suffix cut directly over the original whole normal-space blocks. The artifact records the exact RREF boundary and width at every cut, including the two zero-width endpoint cuts.

For the frozen B4.5 fixture, a successful B4.6.1 run must therefore establish only the local statement:

```text
one accepting root entry
has one replayable whole-factor ancestry
whose reconstructed order has exact width at most k
```

This is not yet the full iterative-compression theorem.

## Accounting

The B4.6.1 ledger begins at the final B4.5 cumulative work and charges:

- root acceptance tests;
- every selected entry lookup;
- every B2 extension-path vertex;
- generator, refinement, and child-pair provenance lookup;
- every recursive branch combination; and
- every exact layout-cut recomputation.

The final artifact includes a fixed-point serialized certificate byte count and binds the complete B4.5 manifest and transcript-root digests.

## Independent verification

The verifier imports neither the B4.6.1 producer nor its reconstruction functions. It first independently replays the complete B4.5 transcript, including all 164,072 refinements, then reconstructs the root ancestry again from the chunked records and recomputes the exact layout width.

Digest-repaired controls alter:

- deterministic root-entry selection;
- an internal parent pointer;
- one affine offset; and
- the reconstructed order.

All must be rejected after nested receipt digests, the outer manifest digest, and the fixed-point byte count are repaired.

## Strict boundary

B4.6.1 does **not** yet execute iterative compression over every prefix round and does not prove terminal completeness. Therefore the local result is named:

```text
LAYOUT_WITNESS_RECONSTRUCTED
```

It is intentionally not promoted to the global constructor terminal `FOUND_LAYOUT`.

```text
B4.6.1_ROOT_ANCESTRY_REPLAY = IMPLEMENTED_CANDIDATE
B4.6.2_FULL_ITERATIVE_COMPRESSION_CYCLE = OPEN
TERMINAL_COMPLETENESS = OPEN
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

Draft only. No automatic merge.
