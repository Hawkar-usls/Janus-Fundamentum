# C021 proof attempt — Policy-0T decision-clause invariant

## Status

`FORMALIZING / FINITE RECURSIVE TRANSLATOR VERIFIED / UNIVERSAL INDUCTION OPEN`

## Corrected scope

The invariant applies only to the **non-affine Policy-0T search core** after the
root dispatcher has returned:

```text
affine_answer = None
```

It cannot prove an ordinary-Resolution simulation for the full dispatcher. H130
is destroyed separately because visible affine/Gaussian reasoning decides
Resolution-hard expander-Tseitin formulas in polynomial work.

The repaired target is H132.

## Target

For every UNSAT node `u` in a provenance-complete no-cache Policy-0T execution,
let

```text
Delta_u
```

be all assignments inherited at entry to `u`. Define

```text
B(Delta_u) = OR of the literals falsified by Delta_u.
```

Examples:

```text
x=0 contributes  x
x=1 contributes -x
```

The candidate invariant is:

> From root axioms and provenance-certified local Resolution lines, derive a
> clause `C_u` such that `C_u` is a subclause of `B(Delta_u)`.

At the root `B` is empty, so the returned clause must be the empty clause.

## Why a subclause invariant matters

Lifting every residual proof to the full clause `B(Delta_u)` would silently use
weakening. The subclause invariant avoids it.

Suppose `u` branches on `x`.

The false child returns

```text
C_0 subseteq B(Delta_u) union {x}.
```

The true child returns

```text
C_1 subseteq B(Delta_u) union {-x}.
```

Three legal cases remain:

1. if `x in C_0` and `-x in C_1`, resolve on `x`;
2. if `x` is absent from `C_0`, return `C_0` directly;
3. if `-x` is absent from `C_1`, return `C_1` directly.

Every result is a derived subclause of the parent decision boundary, with no
semantic weakening.

## Residual lifting lemma — finite implementation

A residual clause is not treated as a proof line. The translator retains a
root-derived clause `D` and only uses its restriction `D|Delta` for execution.

For every recorded local Resolution event it verifies:

```text
resolve(D_left, D_right, pivot) | Delta
  = recorded residual resolvent.
```

Thus deleted assignment-falsified literals remain present in the actual proof
clause and no reverse restriction rule is invented.

## Unit-reason lemma — finite implementation

When unit propagation assigns literal `l`, the translator stores the root-level
proof line whose current restriction is `(l)`.

If a terminal conflict clause contains `-l`, it resolves the conflict backwards
with the reason clause on `var(l)`. Unit assignments are eliminated in reverse
order. After all local reasons are processed, the returned clause is checked to
be a subclause of the node-entry decision boundary.

## Executable recursive translator

```bash
python experiments/direct/janus_tear_policy0t_recursive_trace_translator.py
```

The translator consumes the independently replayed C020 trace. It does not read
the separate hardwired fifteen-line proof.

Verified output:

```text
trace nodes:                 3
axiom lines:                10
Resolution lines:           13
proof lines:                23
reverse unit resolutions:    2
branch resolutions:          1
maximum width:               3
proof depth:                 3
final clause:            EMPTY
```

Every proof line is replayed independently from its parents.

## What is now closed finitely

On the first non-affine branching fixture, one mechanism now closes the entire
chain:

```text
verified execution trace
-> root provenance retained under restriction
-> local residual resolutions lifted
-> terminal implied literals removed through reasons
-> sibling conflicts combined
-> root empty clause independently verified
```

## Universal obligations still open

The finite fixture does not cover every trace shape. H134 and H132 still require:

1. direct child conflicts caused immediately by a branch restriction;
2. opposite unit clauses before either assignment is applied;
3. multiple unit-propagation batches;
4. post-resolution unit conflicts at arbitrary depth;
5. duplicate residuals with alternative provenance lines;
6. deeper branch trees;
7. a proof that every charged event adds constant proof size;
8. a proof that maximum proof depth is `O(N)`.

## Candidate size accounting

Let `W` charge:

```text
recursive occurrences
+ local Resolution events
+ unit-reason edges
+ branch edges
+ emitted proof lines.
```

With no memoization, each execution occurrence has one tree position. If every
case of the universal induction emits constant overhead, then:

```text
proof size = O(W).
```

## Candidate depth accounting

Along a root-to-leaf path, every branch or propagated unit fixes a fresh
variable. Branch combination adds at most one layer, and reverse unit reasoning
adds at most one layer per propagated assignment. The intended recurrence is:

```text
D(u) <= max(D(child_0), D(child_1))
        + O(number of local assignments + 1),
```

which would telescope to `O(N)`.

This recurrence is not yet a theorem for all traces.

## Falsification attacks

The invariant is destroyed if any provenance-complete non-affine trace exhibits:

- a terminal conflict whose implied literals cannot be removed by reasons;
- a local residual resolvent that cannot be lifted from root-derived parents;
- a branch pair requiring weakening;
- superconstant proof overhead for one charged event;
- proof depth growing superlinearly in fresh assignments along a path.

## Claim boundary

The recursive translator is a finite verified witness, not a proof of the
universal H134 induction or H132 asymptotic simulation. It does not establish the
MAJ3 lower bound, `P != NP`, or `P = NP`.
