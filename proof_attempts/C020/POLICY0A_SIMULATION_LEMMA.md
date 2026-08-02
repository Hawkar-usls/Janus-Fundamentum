# C020 proof attempt — Policy-0A simulation lemma

## Status

`DRAFT / NOT PROVED / REQUIRED FOR ASYMPTOTIC LOWER BOUND`

## Target statement

Let `F` be an UNSAT CNF on `N` variables. Assume the Policy-0A root affine
shortcut returns `None`, and the policy terminates with total charged work `W`.
Then there exists a `Res(⊕)` refutation of `F` satisfying

```text
size  <= c1 W
depth <= c2 N + c3
```

for absolute constants `c1,c2,c3` determined by the proof encoding.

Because Policy-0A uses only ordinary clauses and Boolean variable branches after
the root shortcut, it is enough to build an ordinary resolution refutation;
ordinary resolution embeds into `Res(⊕)`.

## Execution objects

A residual node `u` stores:

```text
R_u       exact canonical residual CNF
P_u       clauses added by the one-pass resolution budget
x_u       branch variable, unless terminal
u_0,u_1   child residual nodes
```

A memo edge points to an already constructed node with exactly the same
canonical residual CNF.

Every added clause `C in P_u` must store:

```text
parent clause A
parent clause B
pivot variable p
C = resolve_p(A,B)
```

The current implementation computes these clauses but does not yet retain this
provenance.

## Inductive proof object

For every residual node `u`, construct a derivation of a clause `B_u` over the
variables fixed on the path to `u` such that

```text
F entails B_u
```

and the current path assignment falsifies `B_u`.

At the root, `B_root` must be the empty clause.

### Terminal conflict

If unit propagation or direct restriction produces an empty clause, trace the
conflict back through the unit chain. Resolve the conflicting input/learned
clause against the unit reasons in reverse order. This yields a clause containing
only negations of path decisions.

### Branch node

Suppose the false child derives

```text
B_0 OR x
```

and the true child derives

```text
B_1 OR NOT x.
```

After weakening both clauses to a common path clause `B`, resolve on `x` to
obtain `B` for the parent.

The precise treatment of weakening must match the selected resolution syntax.
Alternatively, child clauses can be maintained in one common canonical decision
clause format so that no semantic weakening is required.

### Memo node

If two execution paths reach the same exact residual CNF, reuse the same
subderivation DAG. The incoming decision clauses may differ, so the proof object
must distinguish:

1. the residual refutation core, reusable by hash;
2. the path-lifting wrapper, reconstructed for each incoming decision context.

This is the main place where naive `size=O(number of memo states)` can fail.
The wrapper cost must be charged explicitly.

## Candidate size recurrence

Let:

```text
r_u = number of resolvents added at u
q_u = number of unit-reason resolutions needed at u
i_u = number of incoming memo edges to u
```

A safe first recurrence is

```text
S(u) <= r_u + q_u + 1 + S(u_0) + S(u_1)
```

for a tree expansion. This can duplicate a shared memo core exponentially.

The desired DAG recurrence is instead

```text
S_total <= O(
  total generated resolvents
  + total unit reason edges
  + total branch edges
  + total memo wrapper edges
).
```

Therefore `W` must include every incoming memo wrapper, not only unique residual
states.

## Candidate depth recurrence

Along any execution path:

1. each branch fixes one previously unassigned variable;
2. every unit propagation fixes another previously unassigned variable;
3. hence branch plus unit events total at most `N`;
4. each residual resolution pass adds only one derivation layer, because newly
   generated resolvents are not re-indexed during that pass;
5. every recursive transition follows at least one fresh branch assignment, so
   there are at most `N` residual passes on a path;
6. every branch combination adds one layer.

This suggests

```text
D <= N unit layers + N local-resolution layers + N branch layers + O(1)
  <= 3N + O(1).
```

The unit term requires a reason graph: simplifying a clause under an assignment
is not itself a legal proof inference.

## Attacks against the lemma

### A1 — memo-context explosion

The same residual CNF may be reached under exponentially many decision contexts.
A reusable residual refutation might require a different lifted decision clause
for each context. Exact residual memoization alone does not prove proof-DAG
sharing of all wrappers.

Required response: charge incoming memo contexts in `W`, or prove one context-free
refutation core can be attached with constant overhead.

### A2 — hidden weakening

The branch combination may silently use semantic weakening. If the target system
permits only syntactic resolution, the weakening steps must be explicit and
charged.

### A3 — unit reason absence

Policy-0A currently performs destructive unit simplification without recording
which clause forced each unit. A conflict cannot be reconstructed without these
reasons.

### A4 — learned-clause restriction provenance

A learned resolvent may be simplified by later assignments. The verifier must
show that the simplified clause is the appropriate restriction of a previously
derived clause, or reconstruct a legal derivation in the restricted context.

### A5 — depth hidden inside provenance

Although one policy pass adds only one resolution layer syntactically, its parent
clauses may come from proofs of unequal depths. The verifier must compute

```text
depth(C) = 1 + max(depth(A), depth(B))
```

and establish the global path bound.

## Current assessment

The linear-depth claim remains plausible, but the `O(W)` size claim is not yet
safe because of memo-context wrappers. The next executable artifact must expose
exactly this resource instead of treating memo hits as free.

## Required implementation

Create a proof-emitting Policy-0A variant with:

```text
stable clause IDs
resolution parent IDs
unit reason IDs
restriction events
branch IDs
memo core IDs
incoming context wrappers
computed proof depth
```

An independent verifier must reject:

- invalid resolvents;
- missing unit reasons;
- inconsistent restrictions;
- illegal branch combinations;
- memo reuse under a non-equivalent residual;
- incorrect size or depth totals.

Only after that verifier passes on finite fixtures should the general recurrence
be promoted from a proof plan to a lemma.
