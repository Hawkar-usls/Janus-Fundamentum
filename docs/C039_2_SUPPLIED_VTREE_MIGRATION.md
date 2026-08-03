# C039.2 Supplied-Vtree Evaluator Migration

```text
P_VS_NP=OPEN
```

This package migrates the useful, fully green evaluator and capability-boundary
audit from PR #62 into canonical C039.2 PR #55.

## Governance

```text
source: PR #62 / d302e0bf6d6c2c8f9bf25c098b9f8b500eb83c13
target: PR #55 / C039.2
```

PR #62 does not retain a cycle identifier. It stays open until the migration
head passes both specialized CI and the JANUS registry. After the target commit
SHA is recorded in PR #62, the source may be closed as:

```text
SUPERSEDED_BY_PR_55 / HISTORY_PRESERVED
```

## Migrated interface

`evaluate_supplied_vtree` receives:

```text
single-head Horn formula
supplied full binary vtree
exact rule-owner map
fixed capability and budget
```

It verifies:

- unique node identifiers;
- exact leaf-variable coverage;
- disjoint child scopes;
- boundary containment;
- exact ownership of every normalized rule;
- rule support containment at the claimed owner;
- the `SINGLE_HEAD_HORN_V1` invariant.

It then evaluates bottom-up with proof-carrying `LEAF`, `JOIN`, and `PROJECT`
operations. It does not discover or repair a vtree.

```text
evaluate_supplied_vtree != discover_vtree
```

## Canonical terminals

Legacy strings from the pre-admission Horn projector are normalized at the
C039.2 envelope:

```text
projection volume
  -> OPEN_REPRESENTATION_GROWTH
     reason_code = PROJECTION_VOLUME

lost unique-head closure
  -> OPEN_LANGUAGE
     reason_code = SINGLE_HEAD_CLOSURE_LOST
```

Every `OPEN` or invalid evaluation has:

```text
root_message_digest = null
```

No partial factor is returned after a budget crossing.

## Capability boundary

```text
LEAF=true
JOIN=true
PROJECT=true
MERGE=true
SEPARATE=true
GENERAL_HORN_POLY_PROJECTION=false
VTREE_DISCOVERY=false
```

The `MERGE` and `SEPARATE` flags reflect the existing canonical C039.2 Horn
entailment/countermodel implementation in PR #55. This migration does not claim a
polynomial compact projection for unrestricted Horn CNF.

## Incremental projection budget

Single-head projection generates at most one resolvent per consumer because an
eliminated variable has at most one producer. Candidate resolvents are processed
in deterministic order and charged before admission into the output message.

The first crossing returns:

```text
OPEN_REPRESENTATION_GROWTH
reason_code = PROJECTION_VOLUME
output_message_digest = null
partial_factor = null
```

## Acceptance gate

```bash
python experiments/direct/janus_c039_2_supplied_vtree_evaluator.py --self-test
```

The 13 deterministic checks cover:

1. frozen capability boundaries;
2. message-digest determinism;
3. native LEAF replay;
4. JOIN scope rejection;
5. unique-head loss at JOIN;
6. exact producer substitution;
7. consumer removal without a producer;
8. polynomial single-head fan-out controls at `n=4,8`;
9. incremental fail-closed projection growth;
10. deterministic supplied-vtree evaluation;
11. absent root message on OPEN;
12. invalid-vtree fail-closed behavior;
13. encoded truth-table rejection.

## Claim boundary

This migration supplies a real deterministic evaluator for a provided verified
vtree in the declared single-head Horn language. It does not implement vtree
discovery, unrestricted Horn projection, arbitrary CNF solving, or a universal
polynomial SAT algorithm.
