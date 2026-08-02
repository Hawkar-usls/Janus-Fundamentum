# C021 lemma — direct branch conflicts are unreachable in Policy-0T

## Statement

At every actual Policy-0T branch point, assigning the selected branch variable
cannot make `simplify_one` return an immediate empty-clause conflict.

## Proof

Immediately before branching, Policy-0T has completed exhaustive unit
propagation on the current residual CNF and has not reported a contradiction or
an empty satisfied formula.

Therefore the residual CNF contains no unit clause. Every remaining clause has
width at least two.

A branch assignment fixes one variable. For any clause:

- if the assigned literal satisfies the clause, the clause is removed;
- if the opposite literal occurs, exactly that one literal is deleted;
- otherwise the clause is unchanged.

Deleting at most one literal from a clause of width at least two leaves width at
least one. Hence no clause becomes empty during the immediate child restriction.

Thus:

```text
unit propagation exhausted
+ no contradiction
+ nonempty CNF
=> direct_conflict child record is unreachable.
```

## Consequence for H134

The universal branch induction needs only two recursively translated children.
It does not require a separate direct-child-conflict proof rule for the current
Policy-0T implementation.

The trace format may retain `direct_conflict` defensively, but every valid trace
must record it as false at a genuine branch point.

## Claim boundary

This lemma uses exhaustive unit propagation before every branch. It does not
apply unchanged to policies that branch while unit clauses remain or that assign
multiple variables in one branch transition.
