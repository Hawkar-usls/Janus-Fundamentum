# C024 — One-Pass Temporal Separation

**Status:** proved implementation property / cumulative novelty charge open.

## Policy-0A local Resolution discipline

At each residual state, Policy-0A:

1. freezes the current propagated CNF `F`;
2. builds positive and negative pivot-parent lists from clauses of `F` only;
3. enumerates parent pairs in deterministic pivot/length/lexicographic order;
4. adds accepted resolvents to the output clause set;
5. never inserts a fresh resolvent into the parent lists of the same pass.

Therefore the pass is one inference layer, not saturation to a fixed point.

## Lemma — fresh resolvents cannot chain inside one state

Let `C` be newly emitted during the local Resolution pass of state `S`. Then `C`
cannot be a parent of any later Resolution event in the same state.

### Proof

All parent lists are constructed before the event loop begins. The loop mutates
the output clause set used for deduplication and final output, but it never
mutates the parent lists. Hence no newly emitted clause is visited as `left` or
`right` by the current pass.

## Corollary — two-step abstract counterexamples require a state transition

The minimal abstract failure of the directed cycle-or-rooted class uses:

```text
L = {0->1, 2->1}
R = {1->0, 2->1}
resolve on 0<->1
Q = {2->1}
```

If `R` itself is produced from a graph-tautology axiom and a transitivity clause,
Policy-0A cannot immediately resolve `L` with that fresh `R`. Before `R` can be a
parent, execution must:

1. complete the current local pass;
2. run post-unit propagation;
3. choose and apply at least one branch unless the state terminates;
4. simplify the clause into a descendant residual;
5. enter a later state's one-pass parent set.

Thus every multi-inference provenance chain is temporally separated by search
state transitions. Branch novelty and unit/component effects along those
transitions are available as explicit proof charges.

## Relation to graphic rank

One Resolution inference can reduce clause graphic rank relative to its
higher-rank parent by at most one. One branch transition cannot decrease
`novelty + graphic_rank`.

Temporal separation therefore suggests an amortized resource:

```text
novel branch gains between Resolution rank-loss events
versus
number of explicit rank-losing Resolution events.
```

The finite C024 dangerous-unit provenance paths exhibit exact balance: each
learned origin is narrowed only through novel branches before it becomes a unit.
A cumulative theorem for every possible provenance DAG remains open.

## Machine obligations

The accompanying attempted-pair audit reconstructs the frozen parent lists and
checks every pair actually reached before the attempt/addition budgets. It asks
whether the abstract unsafe forest can be produced directly from one state's
input parent set, independently of which resolvents are new or duplicates.

## Claim boundary

This file proves an implementation property of Policy-0A's local pass. It does
not by itself establish an exponential lower bound and does not resolve P versus
NP.
