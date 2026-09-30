# C024 — Derived-Clause Novelty Potential

**Status:** universal all-clause potential falsified at `GT_8` / frontier-dangerous provenance potential finitely survives through `GT_8`.

## Motivation

C024 showed that every observed component-joining unit occurs only after the
historical target level `n-2` has already been reached. The remaining concern was
that a clause learned earlier by Policy-0A local Resolution might be inherited
and later collapse to a unit without paying the missing historical novel joins.

The exact provenance audit rejects that concern for every observed pre-unit
component merge through `GT_8`.

## Exact provenance result

There are twelve pre-unit component merges in the verified range. Direct
comparison with the original root axioms classifies all twelve as derived-only.
One parent generation backward:

```text
3 arise from a local binary resolvent in the immediate parent state;
9 arise from a binary clause inherited in the parent residual key.
```

Recursive replay of pre-units, branch simplification, post-units and local
Resolution reaches one unique first origin for every event:

```text
all 12 originate at an explicit local Resolution event;
none requires an unexplained parent-output clause;
none has a shorter root-axiom origin under the recorded execution;
maximum minimum ancestry length = 5 transitions.
```

## Novel-branch charge certificate

For every certified path, let:

- `r` be the novelty level of the call where the origin resolvent is created;
- `w` be the width of that origin clause;
- `t = n-2` be the historical target novelty;
- `k` be the number of later branch restrictions that narrow the clause before
  it becomes a component-joining unit.

The executable audit verifies simultaneously:

```text
k = w - 1
r + k = t
```

and, at every one of the `k` transitions:

1. the selected branch variable occurs in the active provenance clause;
2. the branch removes exactly one literal;
3. the branch joins two distinct Hasse components and is therefore novel;
4. no pre-unit or post-unit stage removes a provenance literal;
5. no nonnovel branch narrows the provenance clause.

Thus these derived clauses do not replace the historical joins. They store
conditional consequences whose conversion to units still consumes exactly the
missing novel branches.

## Finite data

```text
origin width      occurrences      required novel narrowing steps
2                      3                         1
3                      4                         2
4                      2                         3
5                      1                         4
6                      2                         5
```

For `GT_8`, both pre-unit merges originate at novelty level `1` from width-six
resolvents:

```text
(-2,-4,-5,-6,-7, 8)
(-1,-4,-5,-6,-7,-8)
```

Each clause is narrowed through five novel branches:

```text
width 6 -> 5 -> 4 -> 3 -> 2 -> 1
novelty 1 -> 2 -> 3 -> 4 -> 5 -> 6
```

## Potential on certified dangerous provenance

For an active provenance clause `C` under partial order `P`, define

```text
Phi(P,C) = novelty(P) + active_width(C under P) - 1.
```

Along all twelve certified paths:

```text
Phi(P,C) = n-2
```

at origin and after every narrowing step.

## Universal all-clause form — falsified

A global branch-shrink census examined every strict clause-width decrease before
the target frontier for `GT_4..GT_8`.

Aggregate result:

```text
all branch shrink events                     7,538
novel-branch shrink events                   6,926
nonnovel-branch shrink events                  612
immediate-local-resolvent nonnovel shrinks     269
```

The first failure occurs at `GT_8`. For example, at novelty level four the
nonnovel branch `-10` narrows the immediate local resolvent

```text
(-6,-9,10,24) -> (-6,-9,24)
```

without increasing novelty.

Therefore the statement

```text
every width decrease of every local resolvent is paid by novelty
```

is false.

## Narrow frontier-dangerous form — survived finite attack

The same census marks every branch transition belonging to a provenance path
that actually produces a component-joining unit. It finds:

```text
certified dangerous shrink events      31
dangerous novel shrinks                31
dangerous nonnovel shrinks              0
```

Thus the surviving conjecture must distinguish structurally dangerous clauses
from harmless learned clauses. A retrospective definition such as “eventually
becomes a component-unit” is insufficient for an asymptotic proof.

## Component-tree hypothesis

The certified data suggests an execution-independent structural predicate.
Whenever a dangerous clause is created:

```text
origin width = number of current Hasse components - 1.
```

Interpret each clause literal as an undirected edge between the current
components containing its two comparison vertices. The candidate structure is:

1. every literal joins two different current components;
2. the literal edges form a spanning tree over all current components;
3. falsifying a literal contracts its tree edge;
4. the residual clause remains a spanning tree on the contracted components;
5. after `w-1` contractions, the remaining unit is the final edge between two
   components.

If true, every narrowing branch is automatically novel and the equality

```text
novelty + width - 1 = n-2
```

is a consequence of tree contraction rather than a numerical coincidence.

## Refined conjecture

Let `C` be a local resolvent whose component-edge graph is a spanning tree at
creation. Suppose descendants preserve the corresponding residual clause rather
than satisfying or replacing it. Then any branch that strictly narrows this
residual must contract a tree edge, hence is novel; after contraction the
residual remains a component-spanning tree.

The missing proof obligations are:

- characterize which Policy-0A resolvents can become early component-joining
  units;
- prove such resolvents necessarily satisfy the component-tree predicate;
- prove units and subsequent local Resolution cannot create an uncharged
  shortcut between tree contractions;
- preserve the label through exact residual caching.

## Next falsification test

Construct the component graph of every certified dangerous origin and every
immediate local resolvent before the target. Verify:

```text
all dangerous origins are spanning trees;
all contractions on dangerous paths preserve the tree;
no spanning-tree clause is narrowed by a nonnovel branch.
```

Any failure kills the component-tree criterion. Survival produces a concrete
combinatorial lemma rather than an execution-relative label.

## Claim boundary

The universal all-clause potential is disproved. The narrower dangerous-path
potential is a machine-verified finite pattern and the component-tree statement
is a conjecture under attack. No asymptotic lower bound for `JANUS-FC_local` and
no solution of P versus NP is claimed.
