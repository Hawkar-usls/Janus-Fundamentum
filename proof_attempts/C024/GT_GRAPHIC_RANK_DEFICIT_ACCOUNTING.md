# C024 — Graphic-Rank Deficit Accounting

**Status:** local accounting lemmas proved / frontier-capacity theorem open.

## Deficit

Fix a partial order `P` with `m(P)` Hasse components. For a clause `C`, let
`rho_P(C)` be the graphic rank of its external-literal graph. Define

```text
d_P(C) = m(P) - 1 - rho_P(C).
```

Interpretation:

- `d=0`: the clause externally connects all current components;
- `d>0`: its external graph is missing `d` independent component connections;
- internal literals and cycle redundancy do not reduce `d` because they carry no
  independent graphic rank.

Directed-cycle clauses require a separate consistency label, but the rank
accounting below remains valid for their underlying external graph.

## Lemma 1 — branch deficit is nonincreasing

Let `P -> P'` be a branch and let `C'` be an unsatisfied residual of `C`.

### Nonnovel branch

The number of Hasse components is unchanged. The branch can delete only a loop
from the clause component graph, so graphic rank is unchanged. Therefore

```text
d_P'(C') = d_P(C).
```

### Novel branch

The branch joins two Hasse components, so

```text
m(P') = m(P)-1.
```

The graphic-rank branch lemma gives

```text
rho_P'(C') >= rho_P(C)-1.
```

Hence

```text
d_P'(C')
  = m(P')-1-rho_P'(C')
 <= m(P)-2-(rho_P(C)-1)
  = d_P(C).
```

Thus branch restriction never increases rank deficit.

## Lemma 2 — one Resolution inference increases deficit by at most one

At a fixed state, the Hasse partition is fixed. For

```text
L, R |- Q
```

the graphic-rank Resolution lemma gives

```text
rho_P(Q) >= max(rho_P(L),rho_P(R))-1.
```

Therefore

```text
d_P(Q)
 <= min(d_P(L),d_P(R))+1.
```

Relative to the lower-deficit parent, one inference introduces at most one new
missing independent component connection.

## Provenance corollary

Consider a clause-provenance path beginning at a clause of deficit zero and
ending at deficit `d`. Branch steps cannot increase deficit, and each Resolution
step increases it by at most one. Therefore the path contains at least `d`
rank-losing Resolution inferences.

More generally, if the initial deficit is `d_0`, reaching deficit `d` requires
at least `d-d_0` positive deficit increments.

## Shortcut interpretation

An acyclic low-rank external clause of deficit `d` may omit `d` independent
connections among the current Hasse components. If it eventually becomes an
external unit, it can apparently avoid up to `d` of the component joins that a
component-spanning clause would need.

The accounting lemmas show that these missing joins are not free at the clause
level: every unit of shortcut deficit must be created by an explicit Resolution
inference somewhere in its ancestry.

## One-pass temporal separation

Policy-0A freezes its parent lists. A newly created clause cannot participate in
another Resolution inference in the same state. Consequently successive deficit
increments on one provenance lineage are separated by state transitions.

A state transition is caused by a branch unless the current state terminates.
Thus a deficit-`d` lineage cannot be manufactured by a depth-`d` Resolution chain
inside one local pass.

## What remains unproved

Local deficit accounting does not itself imply an exponential global lower
bound. A rank-losing clause created at one state may be inherited by many
descendants, and a single event may influence a whole subtree.

The missing **frontier-capacity theorem** must bound how much historical frontier
mass one deficit lineage can eliminate or identify. Candidate forms include:

```text
capacity(lineage of deficit d) <= 2^d
```

or an equivalent Kraft-style charge in which:

- novel binary branches split frontier mass;
- rank-loss events consume explicit proof budget;
- exact cache reuse may identify only equal residual obligations;
- one-pass temporal separation prevents uncharged inference chaining.

No such global capacity inequality is claimed here.

## Falsification conditions

The accounting framework fails if any of the following is found:

1. a branch transition increases `d`;
2. one Resolution event increases `d` by more than one relative to both parents;
3. a unit or simplification stage creates an uncharged positive deficit jump;
4. an exact cache edge reuses a low-deficit proof for a higher-deficit obligation
   without preserving the relevant label;
5. a polynomial number of rank-loss events covers the full exponential frontier
   in a way incompatible with any capacity charge.

The first two conditions are ruled out by proved combinatorial lemmas. The
remaining three are active C024 targets.

## Claim boundary

This file proves only local rank-deficit accounting. It does not establish the
frontier-capacity theorem, an asymptotic lower bound for `JANUS-FC_local`, or a
solution to P versus NP.
