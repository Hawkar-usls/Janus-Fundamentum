# C023 — JANUS Exact Formula-Caching Calculus

**Status:** exploratory / machine-checkable finite calculus / proof-system classification open.

## Exact machine under study

Policy-0A uses the following deterministic dispatcher and search core:

1. visible affine recognition at the root;
2. exhaustive unit propagation;
3. exact canonical residual lookup;
4. one polynomially budgeted local Resolution pass;
5. another unit-propagation fixpoint;
6. deterministic most-frequent-variable branching, false first;
7. insertion of the completed exact residual and its Boolean result into the cache.

A cached judgement has the form

```text
canonical residual F  =>  Boolean answer b
```

and can be reused only when the current residual is byte-for-byte equal to `F`
after exhaustive unit propagation and the referenced state completed earlier in
the depth-first run.

## JANUS-FC_local

We call the resulting certificate system `JANUS-FC_local`.

Its proof objects contain:

- one record for every recursive call;
- one record for every unique residual state;
- every unit-propagation event and reason;
- every attempted-budget parameter and accepted local resolvent;
- every deterministic branch and child restriction;
- every exact cache target;
- the DFS completion order needed to prevent forward cache references.

A cache hit is **not** treated as ordinary Resolution DAG sharing.  It reuses a
whole residual-unsatisfiability judgement reached under a potentially different
decision context.

## Relation to established Formula Caching

Beame, Impagliazzo, Pitassi and Segerlind distinguish several caching systems.
Their simplest Formula-Caching algorithm stores previously refuted residual
formulas and tests exact cache membership before branching.  They prove that the
basic Formula-Caching and contradiction-caching systems are polynomially
equivalent, and that the basic systems do not polynomially simulate regular
Resolution.  When the algorithm returns a **reason** for unsatisfiability and is
augmented with weakening, the resulting system becomes substantially stronger
and can simulate regular Resolution.

Policy-0A stores only the exact residual key and a Boolean answer.  It does not
return a context-independent reason clause.  Therefore its cache rule is closer
to basic Formula Caching than to reason-caching.  However, Policy-0A also performs
a bounded explicit local Resolution pass before branching, so identifying it
with a named historical system without a simulation proof would be unsound.
`JANUS-FC_local` is retained as its own exact calculus until that comparison is
proved.

Primary source:

- P. Beame, R. Impagliazzo, T. Pitassi, N. Segerlind, *Formula Caching in DPLL*,
  ACM Transactions on Computation Theory 1(3), 2010; ECCC TR06-140.

## Current executable evidence

### Random small CNFs

A deterministic search compared 1,200 non-affine UNSAT formulas on four and five
variables.  Production Policy-0A and the traced calculus agreed exactly, but no
formula produced a cache hit.  Exact residual convergence is therefore rare in
this random finite sample.

### Explicit cache diamonds

For every selector `x`, the diamond family contains a residual clause `C` and
both `(x OR C)` and `(not x OR C)`.  Either selector value yields the same
canonical child residual.

The no-cache policy expands an exponential binary prefix, while Policy-0A keeps
only linearly many distinct residual states.  The two paths reach the same cache
key with opposite decision boundaries, so one context-specific conflict clause
cannot represent the cache hit without additional reasoning.

This demonstrates genuine formula-level memoization power, but only through
syntactic repetition of an identical subproblem.  It is not a general SAT
speedup and is not a lower bound against Formula Caching.

### Structured MAJ3-lifted Tseitin

The next audit profiles exact hits on the MAJ3-lifted K4 contradiction.  The gate
is whether caching reduces the number of unique residuals below the explicit
quadratic envelope, not merely whether cache hits occur.

## Open classification gates

1. Prove a linear translation from every Policy-0A UNSAT execution to a
   `JANUS-FC_local` certificate.
2. Prove or refute a polynomial simulation of `JANUS-FC_local` by basic
   Formula Caching / contradiction caching.
3. Determine whether the bounded local Resolution pass implicitly supplies the
   equivalent of a returned reason.
4. Search for an infinite family with exponentially many pairwise distinct
   exact residuals despite caching.
5. Attempt a direct lifting theorem for `JANUS-FC_local` if simulation into a
   known proof system fails.
6. Charge certificate size, cache lookup, canonicalization, local proof work,
   branch edges, and witness recovery separately.

## Claim boundary

C023 does not show that Formula Caching is polynomial or exponential on general
SAT, does not transfer the C022 no-cache lower bound to Policy-0A, and does not
resolve P versus NP.  It replaces an informal Python memo dictionary by an
explicit proof-system interface that can be attacked mathematically.
