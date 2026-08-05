# C049.1 B4.6.3 — join-path domain correction

```text
BASE = admitted PR #105
BASE_EXACT_HEAD = 78c16ef6e43d477660aff85be3cd7cc0a1024791
P_VS_NP = OPEN
```

## Correction

The admitted root obstruction proves that two distinct path domains were conflated:

```text
extension preorder comparison -> (1,0), (0,1), (1,1)
trajectory join/interleaving  -> (1,0), (0,1)
```

This layer introduces a strict ordinary-join API. Every join step advances exactly one child order. The existing extension-preorder recurrence remains diagonal-inclusive.

## Bounded exhaustive audit

For every grid `1 <= m,n <= 6`:

```text
ordinary join paths       = C(m+n-2,m-1)
diagonal-inclusive paths  = Delannoy(m-1,n-1)
```

Aggregate counts:

```text
ordinary H/V interleavings =   923
diagonal-inclusive paths   = 4,494
removed diagonal paths     = 3,571
```

Every ordinary path is replayed through the strict validator.

## False zero witness

For the admitted two-state root witness, the legacy diagonal path

```text
(0,0) -> (1,1)
```

produces the false empty-boundary trajectory `0`.

The corrected join domain rejects that path. Its two legal interleavings both produce:

```text
010
```

Hence the false zero state is removed at the API boundary.

## Extension preorder preservation

The same two-state trajectory compared with itself still has the extension witness:

```text
(0,0) -> (1,1)
```

This is required and remains valid because extension comparison is not a linear interleaving.

## Downstream boundary

The correction does not rehabilitate historical B3/B4 artifacts. Child languages from Node-6 onward were generated under the contaminated join domain and must be replayed from the first internal join.

```text
B3_JOIN_PATH_DOMAIN_CORRECTED_API = TRUE
LEGACY_B3_JOIN_ARTIFACTS_PROMOTABLE = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
ROOT_STRUCTURAL_COMPRESSION_ADMITTED = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
P_VS_NP = OPEN
```

Next gate after exact-head admission:

```text
C049.1_B4.6.3_CORRECTED_REPLAY_FROM_FIRST_INTERNAL_JOIN
```
