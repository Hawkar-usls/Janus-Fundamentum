# C039.1 — Single-Head Horn Symbolic Compiler

```text
C039.1 = IMPLEMENTATION / DRAFT
P_VS_NP = OPEN
```

## Purpose

C039.1 is the first executable language profile admitted under the C039
proof-carrying symbolic-factor contract. It implements only:

```text
SINGLE_HEAD_HORN_V1
LEAF
JOIN
PROJECT
evaluate_supplied_vtree
```

It does not implement general Horn compilation, Horn `MERGE`, Horn `SEPARATE`,
vtree discovery, a SAT fallback, or cross-language composition.

## Profile

Rules are normalized as

```text
body -> head
body -> bottom
```

where `body` is a canonical set of atoms. Every atom may occur as the head of at
most one non-tautological rule. Constraints with head `bottom` do not consume an
atomic head slot.

The unique-head invariant is replayed after every `LEAF`, `JOIN`, and `PROJECT`.
A conflicting second definition of an atomic head returns

```text
OPEN_LANGUAGE
reason_code = SINGLE_HEAD_CLOSURE_LOST
```

There is no silent promotion to general Horn.

## Exact projection

For an eliminated variable `x`, let its optional unique producer be

```text
B -> x
```

and let every rule containing `x` in its body be

```text
x & C_i -> h_i
```

C039.1 removes all rules containing `x`. If the producer exists, it emits the
canonical resolvents

```text
B & C_i -> h_i
```

If no producer exists, the negative occurrences are dropped: existentially,
`x=false` satisfies them. Tautologies and duplicate rules are removed.

This is deterministic Davis–Putnam-style forgetting specialized to a unique
positive occurrence. For each eliminated variable, one producer and `k`
consumers are replaced by at most `k` resolvents. Therefore the rule count does
not increase. The implementation still charges literal volume and work because
rule bodies may grow.

## Correction to the proposed blow-up fixture

A fixture asserting exponentially many projected rules for a strict single-head
input would contradict the chosen profile. Polynomial-size forgetting is the
reason for selecting single-head Horn in the first place.

The first implementation therefore freezes a different control:

```text
n boundary atoms -> x
x -> h_1
...
x -> h_n
```

After eliminating `x`, the result has exactly `n` rules and `n(n+1)` literals.
The audit checks `n=4` and `n=8`. A deliberately small literal budget forces an
incremental, fail-closed stop:

```text
OPEN_REPRESENTATION_GROWTH
reason_code = PROJECTION_VOLUME
output_message_digest = null
partial_factor = null
```

The compiler stops on the first canonical rule that crosses the bound. It does
not construct a larger result and then inspect its size.

## Operation certificates

Every operation certificate binds:

```text
schema
canonical_id
operator
terminal
reason_code
capability_digest
language_profile
input_message_digests
output_message_digest
work_units
budget_digest
proof_payload
operation_digest
```

Semantic digests use canonical JSON and domain-separated SHA-256. Floats,
assignment rows, communication rows, truth tables, evaluation vectors, bitmaps,
lookup tables, and model enumerations are rejected.

## Capability boundary

The executable capability manifest is frozen as:

```text
HORN_LEAF_IMPLEMENTED=true
HORN_JOIN_IMPLEMENTED=true
HORN_PROJECT_IMPLEMENTED=true
HORN_MERGE_IMPLEMENTED=false
HORN_SEPARATE_IMPLEMENTED=false
GENERAL_HORN_IMPLEMENTED=false
VTREE_DISCOVERY_IMPLEMENTED=false
```

## Supplied-vtree evaluation

`evaluate_supplied_vtree` validates a full binary vtree, exact variable coverage,
unique node identifiers, disjoint child scopes, boundary containment, and exact
single ownership of all formula rules. It then executes `LEAF`, `JOIN`, and
`PROJECT` bottom-up.

The evaluation certificate records:

```text
formula_digest
vtree_digest
capability_digest
language_profile_digest
budget_digest
max_message_size
total_representation_size
leaf_work
join_work
projection_work
proof_bytes
closed_nodes
open_nodes
first_open_node_digest
first_open_terminal
first_open_reason_code
root_message_digest
evaluation_certificate_digest
```

`root_message_digest` is present only after a complete `FACTOR_BUILT`. Every
`OPEN_*` or invalid vtree returns it as `null`.

```text
evaluate_supplied_vtree != discover_vtree
```

Candidate generation and selection remain reserved for C040.

## Frozen audit

```bash
python experiments/direct/janus_c039_1_single_head_horn_symbolic_compiler.py --self-test
```

The deterministic checks cover:

1. exact capability boundaries;
2. message digest determinism;
3. replayable `LEAF`;
4. `JOIN` scope validation;
5. duplicate-head `OPEN_LANGUAGE`;
6. exact producer substitution;
7. exact elimination without a producer;
8. polynomial `n=4,8` projection volume;
9. fail-closed incremental volume exhaustion;
10. deterministic supplied-vtree evaluation;
11. no root digest on `OPEN`;
12. invalid-vtree rejection;
13. encoded truth-table rejection.

Finite tests validate this implementation only.

## Claim boundary

C039.1 proves no universal statement about arbitrary Horn CNF, arbitrary vtrees,
or arbitrary CNF. It does not implement a universal polynomial SAT algorithm and
does not resolve P versus NP.
