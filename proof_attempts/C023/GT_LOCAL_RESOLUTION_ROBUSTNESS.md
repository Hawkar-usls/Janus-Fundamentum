# C023 — Graph-Tautology Lower Bound Under Policy-0A Local Resolution

**Status:** open proof attempt / no lower bound claimed.

## Target

Prove or refute the following exact statement.

> Let `GT_n` be the smart graph-tautology CNF.  Every execution of
> `JANUS-FC_local` using Policy-0A's deterministic branch rule, exact residual
> cache and registered one-pass local Resolution budgets requires
> superpolynomial charged work in the actual CNF encoding length.

The historical Formula-Caching theorem gives an exponential node lower bound for
basic caching with weakening and subsumption on `GT_n`.  It does **not** directly
cover Policy-0A, because Policy-0A derives and retains a polynomially bounded set
of local resolvents at every residual before branching.

## Why a polynomial local budget is not automatically harmless

It is invalid to argue:

```text
polynomially many resolutions per state
+ exponentially many basic-FC states
= exponential total work.
```

A single strategically chosen learned clause may eliminate exponentially many
future residual states.  Robustness must therefore be proved at the level of the
lower-bound invariant, not inferred from the local inference count.

## Exact local rule

At a residual `F` after exhaustive unit propagation, Policy-0A sets

```text
width_limit    = maximum_clause_width(F) + 1
attempt_budget = max(64, 4 * literal_occurrences(F))
addition_budget = max(8, clause_count(F) // 4)
```

It enumerates complementary parent pairs from the clauses present at the start
of the pass.  Accepted non-tautological resolvents within the width limit are
stored, but newly added clauses are not re-indexed recursively during the same
pass.  A second unit-propagation fixpoint follows.

Thus the extra rule is a deterministic, non-saturating, one-layer Resolution
closure with explicit polynomial cost.

## Candidate proof routes

### Route A — invariant robustness

Adapt the graph-tautology Formula-Caching lower-bound measure so that one local
resolution pass changes the measure by at most a polynomial factor.  Required
lemmas:

1. classify every possible accepted resolvent by its order-variable support;
2. bound how many lower-bound witness objects one resolvent can invalidate;
3. prove that the complete pass invalidates only a polynomial fraction;
4. show exact cache reuse does not identify states carrying distinct surviving
   witness objects.

No one of these lemmas is currently proved.

### Route B — compilation to FCWS

Translate each Policy-0A state and its local proof ledger to a polynomial number
of FCWS nodes while preserving cache legality.  This would allow the historical
`GT_n` lower bound to transfer.

The obstruction is that Resolution is not a native FCWS inference.  Simulating a
resolvent by branching on its pivot may duplicate the cached sub-DAG, and no
polynomial bound is presently known.

### Route C — direct decision-DAG lower bound

View each completed exact residual as a semantic node and each local resolution
pass as a bounded annotation.  Prove a communication, branching-program or
information lower bound directly for this annotated residual DAG.

This avoids translating local Resolution into FCWS but requires a new theorem.

### Route D — find a different hard family

Seek a family for which every clause derivable by the registered one-pass budget
is provably local or redundant, while exact residual caching still has an
exponential state lower bound.  MAJ3-lifted Tseitin remains a second candidate,
but no cached-calculus lifting theorem is known.

## Executable pressure

The accompanying clause-shape audit records, for finite `GT_n` fixtures:

- every accepted local resolvent;
- width and variable support;
- parent widths;
- whether the resolvent is new globally or repeated across states;
- whether it immediately creates a unit or contradiction after the second
  propagation phase;
- how much of total charged work is cache lookup versus local proof work.

Finite shape regularity is evidence for choosing an invariant only; it is not an
asymptotic proof.

## Claim boundary

This document does not transfer the historical Formula-Caching lower bound to
Policy-0A, does not lower-bound clause learning, pool resolution or regular
Resolution, and does not resolve P versus NP.
