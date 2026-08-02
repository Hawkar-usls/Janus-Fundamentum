# C020 proof attempt — Policy-0T transition trace certificate

## Status

`FINITE VERIFIED TRACE / GLOBAL RESOLUTION CERTIFICATE NOT YET EMITTED`

## Purpose

H130 needs a certified bridge from one concrete no-cache SAT policy to a proof
system. The first layer is to prove that the recorded execution is not an
informal solver log: every local inference and recursive transition must be
replayable independently.

The executable artifact is:

```bash
python experiments/direct/janus_tear_policy0t_trace_certificate.py
```

## Fixture

The trace uses the four-variable ten-clause UNSAT formula from the C020
unit-propagation collision. It has:

```text
unit clauses at the root:       0
visible affine root decision:   none
SAT witnesses:                  0
```

Thus the trace cannot terminate through the affine shortcut or initial unit
propagation.

## Certified transition fields

For every search node the emitter records:

- the exact canonical input CNF;
- the pre-resolution unit batches and their unit-clause reasons;
- every locally added resolvent with both parents, pivot, and attempt index;
- the exact post-resolution CNF;
- the post-resolution unit batches;
- the deterministic most-frequent branch variable;
- both restricted child formulas or a direct empty-clause conflict;
- terminal status and returned Boolean result;
- recursion depth.

The replay verifier independently recomputes each field from the parent CNF and
rejects any mismatch.

## Exact finite result

```text
root affine shortcut:   none
trace nodes:             3
resolution events:      8
unit events:             4
maximum branch depth:    1
root answer:             UNSAT
```

The self-test also checks that every recorded resolvent is the exact legal
resolvent of two clauses indexed at the start of the corresponding Policy-0T
local pass.

## What this closes

The artifact closes the finite execution-integrity layer:

```text
recorded Policy-0T trace
-> independently replayed local inferences and branches
-> same UNSAT result
```

It prevents hidden changes to clauses, uncharged branch choices, fabricated
unit reasons, or invalid local resolvents in the tested fixture.

## What remains open

The trace is **not** yet an ordinary Resolution refutation of the root formula.
The missing layer must transform terminal restricted conflicts back into clauses
over parent decisions and combine sibling branches by legal Resolution steps.

Required next objects:

1. one conflict clause for every terminal node;
2. reverse resolution through each recorded unit reason;
3. explicit lifting of restricted learned clauses to the parent context;
4. branch combination on the queried variable;
5. one root empty clause;
6. independently verified proof size and depth.

Only after this layer is implemented can the laboratory test the general H130
claims

```text
proof size  O(W)
proof depth O(N).
```

## Claim boundary

This finite trace does not prove the H130 simulation lemma, the MAJ3 asymptotic
lower bound, `P != NP`, or `P = NP`. It supplies the first machine-checkable
execution substrate on which those claims can be attacked.
