# C023 — Graph-Tautology Lower Bound Under Policy-0A Local Resolution

**Status:** open proof attempt / no lower bound claimed.

## Target

Prove or refute the following exact statement.

> Let `GT_n` be the smart graph-tautology CNF. Every execution of
> `JANUS-FC_local` using Policy-0A's deterministic branch rule, exact residual
> cache and registered one-pass local Resolution budgets requires
> superpolynomial charged work in the actual CNF encoding length.

The historical Formula-Caching theorem gives an exponential node lower bound for
basic caching with weakening and subsumption on `GT_n`. It does **not** directly
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
future residual states. Robustness must therefore be proved at the level of the
lower-bound invariant, not inferred from the local inference count.

## Exact local rule

At a residual `F` after exhaustive unit propagation, Policy-0A sets

```text
width_limit     = maximum_clause_width(F) + 1
attempt_budget  = max(64, 4 * literal_occurrences(F))
addition_budget = max(8, clause_count(F) // 4)
```

It enumerates complementary parent pairs from the clauses present at the start
of the pass. Accepted non-tautological resolvents within the width limit are
stored, but newly added clauses are not re-indexed recursively during the same
pass. A second unit-propagation fixpoint follows.

Thus the extra rule is a deterministic, non-saturating, one-layer Resolution
closure with explicit polynomial cost.

## Finite pressure obtained in C023

### State ablation

For order size `n=9`:

```text
cache only:                       6,230 unique states
cache + registered local pass:    4,001 unique states
state reduction:                  2,229
local complementary-pair tries:   1,034,744
accepted local resolvents:          140,097
```

The local pass materially helps, but on this fixture it changes the state count
by a factor of about `1.56`, not by orders of magnitude. This is evidence only;
it does not imply an asymptotic bound.

### Weakening/subsumption lookup

On `GT_8`, adding exact FCWS-style weakening/subsumption lookup changes

```text
738 states -> 737 states
```

through one successful generalized hit, while charging

```text
265,191 cached-formula comparisons
26,159,347 clause-pair checks.
```

Thus naive generalized lookup is not a free strengthening and does not explain
the finite growth collapse.

### Clause-shape census

On `GT_8`, the registered local pass emits:

```text
18,014 total resolvent occurrences
 6,117 distinct resolvent clauses
11,897 repeated occurrences
```

Widths three and four account for `14,579` events. Vertex supports four and five
account for `12,282` events. Only `48` emitted resolvents are units, and the
second propagation phase records `182` unit events across `45` states. No empty
resolvent is produced directly by the pass in the audited range.

This suggests that the pass is dominated by repeatedly rediscovered low-width,
small-support clauses, but a proof must show that such clauses cannot destroy the
historical lower-bound witness structure too quickly.

## Candidate proof routes

### Route A — invariant robustness

Adapt the graph-tautology Formula-Caching lower-bound measure so that one local
resolution pass changes the measure by at most a polynomial factor. Required
lemmas:

1. classify every accepted resolvent by its order-variable support;
2. bound how many lower-bound witness objects one resolvent can invalidate;
3. prove that the complete pass invalidates only a polynomial fraction;
4. show exact cache reuse does not identify states carrying distinct surviving
   witness objects;
5. charge repeated rediscovery rather than counting a repeated clause as fresh
   proof information.

No one of these lemmas is currently proved.

### Immediate next lemma — bounded witness destruction

Let `W(F)` denote the witness family used in the selected proof of the historical
`GT_n` Formula-Caching lower bound. For every Policy-0A state `F` and every
accepted one-step resolvent `C` with vertex support `s`, seek an explicit bound

```text
|W(F) \ W(F and C)| <= poly(n, s) * local_mass(F)
```

where `local_mass(F)` is the unit of progress used in that lower-bound proof.
The statement must then be summed over the exact addition budget without hiding
a factor exponential in `s`; audited supports grow up to `n`, even though most
finite events have smaller support.

This formulation is intentionally provisional until the historical witness
objects and node measure are reconstructed line by line from the primary proof.

### Route B — compilation to FCWS

Translate each Policy-0A state and its local proof ledger to a polynomial number
of FCWS nodes while preserving cache legality. This would allow the historical
`GT_n` lower bound to transfer.

The obstruction is that Resolution is not a native FCWS inference. Simulating a
resolvent by branching on its pivot may duplicate the cached sub-DAG, and no
polynomial bound is presently known.

### Route C — direct decision-DAG lower bound

View each completed exact residual as a semantic node and each local resolution
pass as a bounded annotation. Prove a communication, branching-program or
information lower bound directly for this annotated residual DAG.

This avoids translating local Resolution into FCWS but requires a new theorem.

### Route D — find a different hard family

Seek a family for which every clause derivable by the registered one-pass budget
is provably local or redundant, while exact residual caching still has an
exponential state lower bound. MAJ3-lifted Tseitin remains a second candidate,
but no cached-calculus lifting theorem is known.

## Executable artifacts

```text
janus_tear_policy0a_graph_tautology_probe.py
janus_tear_policy0aws_graph_tautology_probe.py
janus_tear_policy0a_gt_local_resolution_shapes.py
janus_tear_policy0a_gt_resolution_ablation.py
validate-c023-gt-robustness.yml
```

Finite shape regularity and state growth guide the choice of invariant only; they
are not an asymptotic proof.

## Claim boundary

This document does not transfer the historical Formula-Caching lower bound to
Policy-0A, does not lower-bound clause learning, pool resolution or regular
Resolution, and does not resolve P versus NP.
