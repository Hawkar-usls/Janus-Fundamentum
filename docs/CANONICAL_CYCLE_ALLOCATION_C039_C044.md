# Canonical Cycle Allocation: C039–C044

```text
P_VS_NP=OPEN
```

This document is the governance allocation for the active symbolic-factor,
semantic-vtree and affine-coordinate routes. It does not merge or admit any
implementation by itself.

## Canonical allocation

| Cycle | Canonical responsibility | Canonical PR / status |
|---|---|---|
| C039.0 | Proof-carrying symbolic-factor operation contract | PR #54, specification admitted, draft |
| C039.1 | Pure-affine symbolic vtree evaluator | PR #52, draft |
| C039.2 | Single-head Horn projection, theorem, implementation and supplied-vtree evaluation | PR #55, migration target; PR #62 is migration source only |
| C039.3 | Low-affine-dimension Horn/dual-Horn plus affine composition | PR #56, draft |
| C040 | Portfolio-guided semantic-vtree discovery contract | PR #58, specification admitted, draft |
| C040.1 | Producer-lane affine/Horn module-forest restricted theorem | PR #60, full CI green, contract adapter missing |
| C040.2 | Reserved for frozen-manifest producer-lane constructor adapter with full C039 probes | implementation pending |
| C041 | Affine-coordinate 3-SAT identity obstruction | canonical predecessor of C042 |
| C042 | Proof-carrying laminar affine forbidden-subspace cover | PR #59, canonical and reopened |
| C043 | Bounded maximum-live signed affine-intersection support | PR #63, architecture strengthened, full admission pending |
| C044 | Local signed-support vtree composition or strict OPEN | reserved |

## Duplicate and migration rules

### PR #62 to PR #55

PR #62 does not own a cycle number. It is a replayable migration source for
canonical C039.2 PR #55.

The following material must migrate:

```text
evaluate_supplied_vtree
full binary-vtree validation
evaluation_certificate_digest
capability digest and capability flags
exact rule ownership per vtree node
root_message_digest = null on every OPEN
encoded truth-table rejection
13 deterministic acceptance checks
```

PR #62 remains open until the migration commit exists on PR #55 and the exact
head passes both specialized CI and the JANUS registry. Only then may PR #62 be
closed as:

```text
SUPERSEDED_BY_PR_55 / HISTORY_PRESERVED
```

### PR #60 and C040 contract

PR #60 proves a valid restricted module-forest theorem. Its direct dynamic
program enumerates complete incident-boundary assignments only under an explicit
logarithmic interface bound and charges that work. It is not automatically a
C040 `VTREE_SELECTED_CERTIFIED` result.

Full C040 conformance additionally requires:

```text
register PRODUCER_LANE_MODULE_FOREST_V1 as a candidate constructor
emit feature and generation proof digests
charge candidate generation separately
freeze and hash the complete candidate manifest before probes
run exactly one full bounded C039 probe per frozen candidate
select only a replayable CLOSED_POLY candidate
use deterministic certified tie-breaking
```

The existing direct module-forest dynamic program remains an independent
restricted theorem and validation oracle.

## C042–C044 metadata resolution

```text
PR #59 = canonical C042 and must remain open during review
PR #61 = superseded laminar prototype; closed without merge
PR #63 = canonical C043; draft and full-admission pending
PR #64 = superseded C043 duplicate; closed without merge
C044    = reserved; no implementation claim
```

C043 writes are held until this allocation is landed and its base is confirmed
against canonical C042.

## Admission discipline

Green CI is necessary but not sufficient for production readiness.

```text
implemented + specialized CI green + registry green
    -> implementation admitted for its exact declared profile

draft review + approved canonical lineage + merge
    -> production-ready repository state
```

No `OPEN` terminal is a hardness theorem. Capability changes invalidate prior
portfolio-scoped OPEN records until exact replay under the new capability digest.

## Frozen prohibitions

```text
NO_AUTOMATIC_MERGE
NO_DUPLICATE_CYCLE_OWNERSHIP
NO_SUPPLIED_VTREE_PROMOTED_TO_DISCOVERY
NO_ASSIGNMENT_TABLE_PROMOTED_TO_SYMBOLIC_FACTOR
NO_PARTIAL_PROBE_PROMOTED_TO_SUCCESS
NO_OPEN_PROMOTED_TO_HARDNESS
NO_GENERAL_SAT_FALLBACK
```
