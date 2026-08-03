# C040.2 Producer-Lane C039 Adapter

```text
P_VS_NP=OPEN
```

C040.2 closes the orchestration gap identified in C040.1 PR #60 without
reclassifying the direct module-forest dynamic program as a C040 symbolic probe.

## Constructor

The registered assignment-independent constructor is:

```text
PRODUCER_LANE_MODULE_FOREST_V1
```

It receives raw tagged factors and performs only candidate generation:

```text
parse raw factors
-> deterministic producer lanes by head and producer rank
-> same-lane connectivity
-> module interaction forest
-> derived binary variable vtree
-> generation proof and charged work
```

It does not call the direct boundary-table dynamic program during candidate
selection.

## Frozen phase discipline

```text
canonical raw factors and capability
-> extract proof-carrying producer-lane feature
-> generate candidate vtree
-> freeze and hash candidate manifest
-> invoke exactly one full C039 probe for the candidate
-> accept only replayable CLOSED_POLY
-> deterministic certified selection or exact OPEN
```

Candidate generation is complete before any probe result is observed. The
constructor declares:

```text
depends_on_assignment_values = false
generated_before_probe = true
```

## Work accounting

The certificate separates:

```text
candidate_generation_work_units
probe_work_units
total_work_units
```

and enforces:

```text
total_work_units = candidate_generation_work_units + probe_work_units
```

A generation or probe budget crossing returns `OPEN_DISCOVERY_BUDGET` and no
selected vtree.

## Direct C040.1 theorem remains independent

PR #60's module-forest dynamic program remains a valid restricted theorem and a
validation oracle. It may enumerate complete incident-boundary assignments only
under its explicit logarithmic interface condition and charged table budget.

C040.2 records:

```text
direct_module_forest_dp_promoted_to_selection = false
```

A SAT result from the direct DP is not automatically a
`VTREE_SELECTED_CERTIFIED` result.

## Probe binding boundary

The adapter validates a generic full C039 probe receipt containing:

```text
formula_digest
capability_digest
vtree_digest
full_compile = true
terminal
c039_certificate_digest
max_node_representation
total_representation
total_work_units
```

The exact admitted C039.2 Horn evaluator binding is pending migration PR #66.
A complete mixed affine/Horn binding remains pending a canonical combined C039
probe. Until those bindings land, C040.2 is an implemented orchestration adapter,
not a universal discovery theorem.

## Acceptance gate

```bash
python experiments/direct/janus_c040_2_producer_lane_c039_adapter.py --self-test
```

The 12 deterministic checks cover digest determinism, one probe per frozen
candidate, pre-probe manifest freezing, assignment independence, generation-proof
replay, certified selection, all-OPEN discipline, separated work ledgers,
non-promotion of the direct DP, capability locking, hidden-table rejection and
budget failure.

## Claim boundary

C040.2 proves correct orchestration for the registered producer-lane constructor
and a supplied full C039 probe callback. It does not prove that this one candidate
is good for every formula, that the candidate portfolio is complete, or that
arbitrary CNF is polynomial-time decidable.
