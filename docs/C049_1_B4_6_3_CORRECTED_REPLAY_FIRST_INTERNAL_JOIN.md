# C049.1 B4.6.3 — corrected replay from the first internal join

```text
BASE_PR = #108
BASE_EXACT_HEAD = ddd18da87fd6c2721deb6b729acdea0af7cf5b6e
P_VS_NP = OPEN
```

PR #108 separated the path domains:

```text
extension preorder comparison -> H / V / diagonal
trajectory join/interleaving  -> H / V only
```

This layer is the first downstream replay on the corrected algebra. It rebuilds every leaf full set from the six-factor negative fixture and executes Node-6 from its two child families. No historical Node-6, Node-7, Node-8, Node-9 or root full set is accepted as an input.

## Exact replay contract

For each of the `36 × 36 = 1,296` Node-6 child pairs:

1. expand both child trajectories into the common boundary;
2. enumerate exactly `C(m+n-2,m-1)` ordinary H/V interleavings;
3. reject every diagonal or non-interleaving path;
4. execute join and genuine shrink;
5. retain every successful and failed refinement in the chunked transcript;
6. preserve successful provenance and duplicate-deletion conservation;
7. attempt the ordinary B2 `up_k` closure under the frozen semantic cap.

The theorem intentionally permits two honest outcomes:

```text
CORRECTED_NODE6_FULL_SET_COMPUTED
```

or

```text
HONEST_OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY
```

The certificate chooses the next gate from the replayed result. It may not invent `FOUND_LAYOUT` or `NO_LAYOUT_AT_CAP`.

## Independent verifier

The verifier imports neither the producer nor the corrected join module. It independently:

- reconstructs the 720-order grouped-layout oracle;
- verifies every deterministic chunk and record digest;
- checks global record-id continuity;
- recomputes every pair's binomial H/V path count;
- checks every path endpoint and every H/V step;
- verifies the full success/failure partition;
- verifies successful-provenance and duplicate-deletion conservation;
- reconstructs the certificate byte-for-byte;
- rejects ten semantic attacks after all certificate digests and byte counts are repaired;
- statically rejects imports of historical downstream full-set theorem modules.

## Strict boundary

```text
PR108_JOIN_PATH_DOMAIN_CORRECTION = ADMITTED
CORRECTED_FIRST_INTERNAL_JOIN_REPLAYED = CI_PENDING
CORRECTED_NODE6_PARENT_REFINEMENT_COMPLETE = CI_PENDING
CORRECTED_NODE6_PARENT_UP_K_COMPLETE = RESULT_DEPENDENT
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
ROOT_STRUCTURAL_COMPRESSION_ADMITTED = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
ROOT_EMPTY_PROVED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

Draft only. No merge and no automatic merge.
