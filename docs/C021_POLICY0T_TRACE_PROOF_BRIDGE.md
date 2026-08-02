# C021 pre-admission — finite Policy-0T trace-to-proof bridge

## Status

`EXPLORATORY / FINITE BRIDGE VERIFIED / UNIFORM TRANSLATOR NOT PROVED`

## Result

C020 independently verified two objects for the same four-variable non-affine
UNSAT fixture:

1. a deterministic Policy-0T transition trace;
2. a fifteen-line root Resolution refutation.

C021 verifies that these are not merely unrelated certificates.

The trace branches at the root on

```text
x4
```

and both child executions return UNSAT. The proof derives the exact sibling
conflict clauses

```text
x4 = false  ->  (4)
x4 = true   ->  (-4)
```

Each clause restricts to the empty clause under the corresponding branch
assignment and is satisfied under the opposite branch. The final proof line
resolves `(4)` and `(-4)` on the exact trace branch variable and obtains the
empty clause.

## Reproduction

```bash
python experiments/direct/janus_tear_policy0t_trace_certificate.py
python experiments/direct/janus_tear_policy0t_root_resolution_certificate.py
```

Expected aligned result:

```text
trace nodes:                   3
root branch variable:          4
false-branch conflict:       (4)
true-branch conflict:       (-4)
used root axioms:              8
resolution lines:              7
proof lines:                  15
maximum width:                 3
proof depth:                   3
final clause:              EMPTY
```

## Why this matters

The finite H130 bridge now has the exact shape required by the standard
branch-combination idea:

```text
proof of conflict under x=0 -> clause (x)
proof of conflict under x=1 -> clause (-x)
resolve siblings on x       -> parent conflict
```

The earlier certificates established only that a trace and a root proof both
existed. C021 checks that the root proof's final conflict clauses correspond to
the actual deterministic branch made by Policy-0T.

## Remaining theorem

The general translator must recurse over an arbitrary Policy-0T tree. At every
node it must:

1. reconstruct terminal conflict clauses from unit reasons or a local
   Resolution contradiction;
2. lift restricted learned clauses to the current decision context;
3. derive sibling conflict clauses with opposite branch literals;
4. resolve them to the parent conflict;
5. charge every local derivation and branch wrapper;
6. prove

```text
proof size  O(total charged Policy-0T work)
proof depth O(number of variables).
```

The difficult point is no longer the final depth-one branch rule. It is a
uniform treatment of unit propagation and restricted learned clauses at every
recursive level without semantic weakening or hidden proof work.

## Claim boundary

This finite alignment is not the H130 simulation lemma and is not an asymptotic
lower bound. It does not prove `P != NP` or `P = NP`. It closes one exact finite
gate and identifies the recursive lifting of local reasons as the next gate.
