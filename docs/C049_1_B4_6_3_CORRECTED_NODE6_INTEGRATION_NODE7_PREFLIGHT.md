# C049.1 B4.6.3 — Corrected Node-6 integration and Node-7 preflight

## Stack

```text
BASE_PR = #110
BASE_EXACT_HEAD = 9def1508cb434ff182a14e4efee423a4f64ea653
```

This layer consumes only the corrected H/V Node-6 transcript from PR #109 and the admitted corrected Node-6 `up_k` certificate from PR #110. Historical Node-6 through root full sets are forbidden as theorem inputs.

## Integration contract

The executor is rebound to the admitted path-domain split:

```text
ordinary join/interleaving = H/V only
extension preorder         = H/V/diagonal
```

The corrected Node-6 generator family is replayed from the PR #109 transcript. The PR #110 closure is then integrated exactly once:

```text
input generators   = 414
retained generators = 2
direct removals     = 412
full-set entries    = 432
```

The integrated closure is byte- and semantic-bound to:

```text
PR #110 exact head = 9def1508cb434ff182a14e4efee423a4f64ea653
certificate SHA256 = f2c6b63d1eb297a57d36cabbf917bbad766e97034ea4e2421db1985a02965f20
semantic digest    = a67f7e1b4d4b90460ea3b7f2f242de74c464ecfcdfe5378759eac6e9f3bea9b5
entries digest     = 245cf63c6483d34f351be0c67a604eec1c6dbf33d1b667c73347f0aa837b0601
```

## Corrected Node-7 workload

The exact child handoff is:

```text
left child  = corrected Node-6 full set = 432 entries
right child = rebuilt whole-factor leaf = 36 entries
child pairs = 432 × 36 = 15,552
```

Using only ordinary H/V interleavings,

```text
refinements = Σ C(m+n-2,m-1) = 1,531,584
```

This replaces the historical diagonal-inclusive preflight:

```text
legacy child pairs     = 16,848
legacy Delannoy paths  = 9,744,432
legacy counts          = NON-PROMOTABLE
```

The present layer sets a pair cap of `20,000`, which admits the complete corrected child product, and a refinement cap of `1,500,000`, which forces an honest stop before enumerating the `1,531,584` Node-7 refinements. No Node-7 refinement record is emitted in this preflight layer.

## Independent verification

The verifier independently checks:

- PR #110 artifact bytes, semantic digest, fixed-point certificate bytes and exact closure entries;
- every integrated transcript chunk, chain link, payload digest and record digest;
- all `1,296` Node-6 pairs and all `38,240` ordinary H/V refinements;
- zero diagonal join steps;
- the `2,684 / 35,556` success/failure partition;
- all `414` generator provenance records and `2,270` duplicate deletions;
- certified replacement `414 → 2 → 432`;
- independent Node-7 counts `15,552` pairs and `1,531,584` H/V refinements;
- no Node-7 records before the admitted enumeration gate;
- `14/14` invariant gates and `12/12` digest-repaired semantic tamper attacks.

The verifier imports neither the producer nor the B1/B2 theorem cores.

## Strict pending boundary

Until exact-head CI succeeds:

```text
PR110_CORRECTED_NODE6_UP_K = ADMITTED
CORRECTED_NODE6_INTEGRATION = CI_PENDING
CORRECTED_NODE7_PARENT_PREFLIGHT_COMPLETE = CI_PENDING
CORRECTED_NODE7_PARENT_REFINEMENT_COMPLETE = FALSE
CORRECTED_NODE7_PARENT_UP_K_COMPLETE = FALSE
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

The only permitted next gate after exact-head green CI is:

```text
C049.1_B4.6.3_CORRECTED_NODE7_PARENT_FRONTIER_COMPRESSION
```
