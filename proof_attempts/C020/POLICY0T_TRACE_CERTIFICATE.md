# C020 proof attempt — Policy-0T trace and finite root certificate

## Status

`FINITE VERIFIED TRACE + FINITE VERIFIED ROOT RESOLUTION PROOF / GENERAL TRANSLATION OPEN`

## Purpose

H130 needs a certified bridge from one concrete no-cache SAT policy to a proof
system. The first layer proves that the recorded execution is not an informal
solver log: every local inference and recursive transition is replayable
independently. The second layer verifies an ordinary Resolution refutation of
the same root formula.

Executable artifacts:

```bash
python experiments/direct/janus_tear_policy0t_trace_certificate.py
python experiments/direct/janus_tear_policy0t_root_resolution_certificate.py
```

## Fixture

Both certificates use the four-variable ten-clause UNSAT formula from the C020
unit-propagation collision. It has:

```text
unit clauses at the root:       0
visible affine root decision:   none
SAT witnesses:                  0
```

Thus the policy cannot terminate through the affine shortcut or initial unit
propagation.

## Certified transition fields

For every search node the trace emitter records:

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

## Exact transition result

```text
root affine shortcut:   none
trace nodes:             3
resolution events:      8
unit events:             4
maximum branch depth:    1
root answer:             UNSAT
```

Every recorded resolvent is checked as the exact legal resolvent of two clauses
indexed at the start of the corresponding Policy-0T local pass.

## Exact root Resolution result

A separate certificate derives the empty clause directly from eight of the ten
root axioms:

```text
used axiom lines:        8
resolution lines:        7
total proof lines:      15
maximum width:           3
proof depth:             3
final clause:        EMPTY
```

Its independent verifier checks every axiom membership, parent index, pivot,
resolvent, line depth, final empty clause, maximum width and proof depth.

The proof has the following compact structure:

```text
(-1,-3,-4) and (-1,3,-4) -> (-1,-4)
( 1,-2,-4) and ( 1,2,-4) -> ( 1,-4)
(-1,-4)   and ( 1,-4)    -> (-4)

(-1,-2,4) and ( 1,-2,4)  -> (-2,4)
( 2,-3,4) and ( 2,3,4)   -> ( 2,4)
(-2,4)    and ( 2,4)     -> (4)

(-4) and (4) -> EMPTY
```

## What this closes

The two artifacts establish a finite end-to-end positive control:

```text
recorded Policy-0T execution
-> independently replayed transitions

same root CNF
-> independently verified Resolution refutation
-> empty clause
```

This prevents hidden changes to clauses, uncharged branch choices, fabricated
unit reasons, invalid local resolvents, or an invalid final root proof in the
fixture.

## What remains open

The root proof was found and verified separately. The laboratory has **not yet
proved that the emitted transition trace itself transforms mechanically into
that proof**, or that the same construction works for every Policy-0T run.

The missing general layer must:

1. derive one conflict clause from every terminal restricted execution;
2. reverse-resolve every unit reason;
3. lift restricted learned clauses into the parent context;
4. combine sibling conflicts on the queried variable;
5. preserve DAG/tree accounting without hidden weakening;
6. prove for every run that

```text
proof size  O(W)
proof depth O(N).
```

Only this uniform translation permits the MAJ3 lifting theorem to yield the H130
asymptotic Policy-0T lower bound.

## Claim boundary

The finite trace and finite root proof do not prove the H130 simulation lemma,
the MAJ3 asymptotic lower bound, `P != NP`, or `P = NP`. They show that both
ends of the proposed bridge are independently valid on the first non-affine
branching fixture; the uniform bridge between them remains the theorem under
attack.
