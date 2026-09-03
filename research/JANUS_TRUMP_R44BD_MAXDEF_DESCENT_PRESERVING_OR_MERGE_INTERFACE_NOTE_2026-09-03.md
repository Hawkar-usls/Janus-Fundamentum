# JANUS TRUMP R44BD — corrected maxdef descent-preserving OR-merge interface

R44BD freezes a theorem target; it does not claim that the merge exists.

Let a fixed polynomial criticalization produce a nonterminal `delta*`-critical CNF `G` with

`k = delta*(G) > 0`.

For a deterministic remaining variable `x`, form the two simplified cofactors `G0` and `G1`.

The branchwise statement must include a terminal exception:

- a child may close immediately as SAT or UNSAT and then need not have rank `<=k-1`;
- every **nonterminal** child is required by the inherited critical structure to satisfy `delta*<=k-1`.

This matters already for the rank-one contradiction `{(x),(not x)}`: either assignment creates an empty clause, so the children are terminal UNSAT rather than rank-zero nonterminal formulas.

## Terminal dispatch before merge

Before invoking any OR-merge:

1. If either child is terminal SAT, the parent is SAT; lift that branch witness with the chosen value of `x`.
2. If one child is terminal UNSAT and the other is nonterminal, continue with the single nonterminal child. Its SAT status equals the parent's and no OR debt remains.
3. If both children are terminal UNSAT, the parent is terminal UNSAT after replayable composition of the two branch certificates.
4. Invoke the missing merge operator `M(G0,G1)` only when **both** children are nonterminal.

Thus the actual merge precondition is

`delta*(G0), delta*(G1) <= k-1`

with both children nonterminal CNFs.

## Corrected merge obligations

For fixed original input size `N`, there must be fixed constants `a,b`, independent of `k` and of the input instance, such that:

1. `SAT(M) iff SAT(G0) or SAT(G1)`.
2. `M` returns a CNF `Q` with `delta*(Q)<=k-1`, or an exact terminal.
3. Merge construction and proof metadata cost at most `N^b`.
4. `Q` and all live replay/merge metadata fit within `N^a` encoded size.
5. Downstream SAT/UNSAT evidence lifts through the merge and the parent branch split in polynomial charged work.
6. A fixed exact normalization `Norm(Q)` returns either a terminal or the next critical CNF `G'` with

   `delta*(G') <= delta*(Q) <= k-1`,

   while preserving the same polynomial state/work envelopes.

The explicit rank-nonincreasing condition on normalization is essential; normalization cannot be allowed to restore the debt just discharged by the merge.

## Correct polynomial termination argument

The initial critical state is itself within the `N^a` state envelope, hence

`k0 = delta*(G0_initial) <= number_of_clauses <= N^a`.

Every nonterminal macrostep—single surviving child or two-child merge followed by `Norm`—reduces the nonnegative integer rank by at least one. Therefore the run has at most

`N^a`

nonterminal macrosteps, not necessarily at most `N`.

With at most `N^b` charged work per step and polynomial replay, total work remains polynomial in the original input size.

Consequently, a universal fixed `M` and `Norm` satisfying these corrected obligations would yield a deterministic polynomial SAT decider and therefore `P=NP`.

## Already-failed natural merges

- selector merge: exact OR, but the choice is reified rather than discharged;
- ordinary CNF Davis-Putnam merge: exact but can rebound `delta*` (R44AS-RANK);
- auxiliary-free CNF projection: parity gives exponential CNF size;
- quantifier-prefix hiding: small syntax but SAT remains in the terminal evaluator.

Status:

`TARGET_FROZEN_V2__NOT_PROVED`

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
