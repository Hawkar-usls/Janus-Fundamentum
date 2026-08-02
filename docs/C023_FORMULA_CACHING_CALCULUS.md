# C023 — JANUS Exact Formula-Caching Calculus

**Status:** machine-checkable finite calculus / reason interface under attack /
asymptotic lower bound open.

## Exact machine under study

Policy-0A uses the following deterministic dispatcher and search core:

1. visible affine recognition at the root;
2. exhaustive unit propagation;
3. exact canonical residual lookup;
4. one polynomially budgeted local Resolution pass;
5. another unit-propagation fixpoint;
6. deterministic most-frequent-variable branching, false first;
7. insertion of the completed exact residual and Boolean result into the cache.

A cached judgement has the form

```text
canonical residual F  =>  Boolean answer b
```

and can be reused only when the current residual is byte-for-byte equal to `F`
after exhaustive unit propagation and the referenced state completed earlier in
the depth-first run.

## JANUS-FC_local

The resulting certificate system is called `JANUS-FC_local`.

Its proof objects contain:

- one record for every recursive call;
- one record for every unique residual state;
- every unit-propagation event and reason;
- every local Resolution budget and accepted resolvent;
- every deterministic branch and child restriction;
- every exact cache target;
- the completion order needed to forbid forward cache references.

A separately implemented serialized verifier receives only primitive call and
state records. It accepts valid certificates and rejects corrupt cache targets,
Boolean results, residual keys and contexts.

A cache hit is **not** treated as ordinary Resolution DAG sharing. It reuses a
whole residual-unsatisfiability judgement reached under a potentially different
decision and inherited-unit context.

## Relation to established proof systems

The Formula-Caching literature separates at least three resources:

```text
exact residual + Boolean answer
reason returned for the residual
clause learning / pool resolution / WRTI-WRTL / restarts
```

Policy-0A has only the first resource. It does not return a context-independent
reason clause. Its cache rule is therefore closest to basic Formula Caching, but
its bounded explicit local Resolution pass prevents an unproved identification
with a named historical system.

Reason plus weakening is a materially stronger system and can simulate regular
Resolution. Pool resolution and several clause-learning systems have polynomial
proofs of graph-tautology families that are exponentially hard for basic Formula
Caching. Consequently, adding “a reason” must specify and charge its exact rule,
including weakening, input lemmas, arbitrary lemmas, restarts and extensions.

`JANUS-FC_local` remains its own exact calculus until a simulation theorem is
proved.

## Finite evidence

### Random small CNFs

A deterministic audit compared 1,200 non-affine UNSAT formulas on four and five
variables. Production Policy-0A and the traced calculus agreed exactly, but no
formula produced a cache hit. Exact residual convergence is rare in this random
finite sample.

### Explicit cache diamonds

The cache-diamond family creates two selector branches with one identical child
residual. Exact caching compresses the repeated binary prefix to linearly many
states and reaches one residual under opposite decision contexts.

However, the same family has a fixed 31-line ordinary Resolution refutation that
ignores every selector and private clause. It therefore separates the cached and
no-cache **executions**, not Formula Caching and Resolution.

### MAJ3-lifted K4

```text
recursive calls:                 4,117
unique exact residual states:    2,427
cache hits:                        888
local Resolution events:        37,432
charged certificate records:    50,796
fully unfolded call occurrences:15,671
```

The unique-state count remains above the explicit quadratic envelope `1,296`.

Unfolding the cache DAG and applying the C022 translator produces a 149,030-line
ordinary Resolution proof. Global sound clause deduplication reduces it to
93,394 lines, still larger than the 50,796-record FC certificate on this finite
fixture. This is an upper-bound comparison only, not an asymptotic separation.

### Reason reuse on MAJ3-K4

There are 438 directly reused residual states and 1,326 direct contexts. In the
fixed language of clauses emitted by the fully unfolded C022 translator:

```text
one reusable reason sufficient:                  5 states
multiple reasons required:                     433 states
one distinct reason per direct context:         422 states
minimum reasons summed over all states:       1,287
maximum minimum reason cover for one state:      27
```

Unfolding direct cache targets repeats 1,963 states across 11,156 repeated-state
occurrences. Only 79 repeated states receive one identical reusable emitted
reason; 1,082 occurrences depend on inherited unit literals, and one state has
128 distinct emitted reasons.

These are exact finite set-cover facts in one clause language. They do not rule
out a stronger polynomial reason language or extraction algorithm.

### Graph tautologies

For order sizes `3..9`, Policy-0A uses

```text
1, 3, 12, 40, 140, 738, 4,001
```

unique states. At `n=9`, the encoding-unit count is `789`, with `1,034,744`
local pair attempts and `140,097` accepted local resolvents.

Removing local Resolution increases the `n=9` state count to `6,230`; the pass
helps by a finite factor rather than collapsing the search by orders of
magnitude.

Adding exact Weakening/Subsumption cache lookup changes `GT_8` from 738 to 737
states through one generalized hit, while charging 265,191 cached-formula
comparisons and 26,159,347 clause-pair checks.

On `GT_8`, the local pass emits 18,014 resolvent occurrences but only 6,117
distinct clauses. Widths three and four account for 14,579 events; 11,897
resolvent occurrences are duplicates across states. Only 48 emitted clauses are
units and the second propagation phase records 182 unit events.

These results make graph tautologies a concrete candidate against the exact
Boolean-cache calculus, but the historical lower bound still must be proved
robust under Policy-0A's extra local Resolution rule.

## Open classification gates

1. Prove a universal execution-to-`JANUS-FC_local` certificate induction and
   polynomial replay cost.
2. Determine whether the local Resolution pass can be simulated by basic
   Formula Caching with polynomial overhead.
3. Specify the weakest reusable reason language and prove polynomial extraction,
   not merely post-hoc existence after full unfolding.
4. Prove robustness of the graph-tautology Formula-Caching lower bound under the
   registered local pass.
5. Alternatively, prove a direct residual-DAG or lifting lower bound on
   MAJ3-lifted Tseitin formulas.
6. Charge certificate size, cache lookup, canonicalization, local proof work,
   branch edges, reason extraction, verification and witness recovery.

## Primary resources

- `janus_tear_policy0a_fc_trace.py`
- `janus_tear_policy0a_fc_serialized_verifier.py`
- `janus_tear_policy0a_fc_proof_system.py`
- `janus_tear_policy0a_direct_reason_cover.py`
- `janus_tear_policy0a_resolution_dag_dedup.py`
- `janus_tear_policy0a_graph_tautology_probe.py`
- `janus_tear_policy0aws_graph_tautology_probe.py`
- `janus_tear_policy0a_gt_local_resolution_shapes.py`
- `janus_tear_policy0a_gt_resolution_ablation.py`
- `proof_attempts/C023/GT_LOCAL_RESOLUTION_ROBUSTNESS.md`

## Claim boundary

C023 does not prove that Formula Caching is polynomial or exponential on general
SAT, does not transfer the C022 no-cache lower bound to Policy-0A, and does not
resolve P versus NP. It replaces an informal memo dictionary by an explicit
proof-system interface and identifies the missing reason/lower-bound theorems.
