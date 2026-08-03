# C024 — Merged-tail extinction lemma

Status: **FORMALIZING**  
Scope: fresh local-Resolution non-tail bridge occurrences whose oriented tail Hasse component is non-singleton, before the historical `n-2` novelty frontier of deterministic Policy-0A on `GT_n`.

## 1. Why this lemma is needed

The canonical root shield applies when a bad literal

```text
l : a -> b
```

has singleton tail component `{a}` and non-singleton head component.  Raw local Resolution can nevertheless create non-tail bridge literals whose tail component is already merged.  Such a literal has no immediate untouched `N_a` shield.

The temporal lower-bound route therefore requires an extinction statement:

> A fresh merged-tail non-tail bridge must disappear, become safe, or terminate the recursive computation before its clause can enter a later parent-eligible exact residual key.

## 2. Stronger unit-conflict claim falsified

The initial conjecture

> every fresh merged-tail non-tail bridge is born in a post-local unit-conflict state

is false.  The exact finite split through `GT_8` is:

```text
fresh merged-tail occurrences              18
post-unit contradiction                    17
branch-UNSAT without post-units              1
```

The unique non-conflict case occurs at `GT_4`.  The state executes both recursive children; neither child produces a later exact key containing the same literal as a component-spanning non-tail bridge.

Thus the correct theorem is a **disjunction of extinction mechanisms**, not a universal unit-conflict theorem.

## 3. Exact finite state split through GT_8

```text
GT_4: 1 occurrence
      BRANCH_UNSAT
      2 executed child calls
      0 post-unit events
      0 bad child exact keys

GT_5: 8 occurrences, all post-unit contradiction
GT_6: 4 occurrences, all post-unit contradiction
GT_7: 2 occurrences, all post-unit contradiction
GT_8: 3 occurrences, all post-unit contradiction
```

For the 17 contradiction cases:

```text
EMPTY_ON_UNIT_ASSIGNMENT                   12
OPPOSITE_UNITS                              5
executed child calls                        0
```

For the single branch case:

```text
executed child calls                        2
child exact keys containing bad lineage     0
children terminal before exact key          2
```

## 4. Causal unit-reason provenance

The post-unit contradiction occurring in the same state is not merely correlated with the merged-tail resolvent.  An all-source backward reason-DAG audit reconstructs every possible unit source rather than choosing one arbitrary reason.

Among the 17 contradiction cases:

```text
merged-tail resolvent is a direct conflict source       4
merged-tail resolvent is an ancestor conflict source   13
merged-tail resolvent merely co-located                  0
```

Therefore every one of the 17 clauses is causally contained in the contradiction proof:

- four are clauses directly responsible for a final opposing unit or empty-on-assignment conflict;
- thirteen occur earlier in the backward unit-reason closure;
- none is an irrelevant clause that happened to be emitted in a contradictory state.

Each event resolvent occurs exactly once in the local output.

The observed all-source closure sizes range from 2 to 12 clauses, and the number of earlier unit events in the closure ranges from 0 to 5.  These are finite measurements, not assumed asymptotic constants.

## 5. Correct arbitrary-n statement

### Merged-Tail Extinction Disjunction

Let `R` be a fresh local resolvent containing a component-spanning non-tail bridge literal `l : a -> b` with

```text
|component(a)| > 1.
```

Before any restriction of `R` can appear in a later parent-eligible pre-frontier exact key as a component-spanning non-tail bridge, prove that at least one of the following occurs:

1. **Unit-conflict extinction.** Post-local unit propagation derives a contradiction whose all-source reason closure contains `R` or the relevant residual of `R`.
2. **Recursive extinction.** Every executed child is UNSAT or otherwise terminates before producing an exact key carrying the same bad lineage.
3. **Structural safety.** The lineage survives only after losing the merged-tail non-tail-bridge property—for example it is satisfied, deleted, becomes nonspanning, becomes a nonbridge, or becomes canonically root-shielded.

The finite executions through `GT_8` use mechanism 1 seventeen times and mechanism 2 once.  Mechanism 3 is included because an arbitrary-`n` proof must not silently assume that the finite dichotomy is exhaustive.

## 6. Candidate proof route for unit-conflict extinction

The finite reason closures suggest proving a local order-theoretic inconsistency:

1. A merged-tail bridge `l : a -> b` connects two already nontrivial quotient regions while being the unique edge of its resolvent across one cut.
2. The two parent clauses and their pivot encode alternate directed comparisons already forced inside those regions.
3. Removing the Resolution pivot collapses that alternate structure into units of opposite polarity or a unit whose assignment empties another residual clause.
4. Reverse unit-reason resolution derives the terminal conflict using the fresh resolvent as a direct or ancestral clause.

The executable provenance audit supplies the exact finite reason DAGs needed to identify a uniform symbolic template.  The next proof attack should classify the 17 closures by their root GT axiom ancestry and directed quotient pattern.

## 7. The GT4 branch base case

The unique `GT_4` exception is:

```text
endpoint shape: (2,1)
terminal state: BRANCH_UNSAT
post-unit events: 0
executed children: 2
later bad exact keys: 0
```

This may be isolated as a finite base case if the arbitrary-`n` conflict argument applies for `n >= 5`.  It must not be generalized away without proof: a larger instance could in principle realize recursive rather than unit-conflict extinction.

## 8. Consequence with the singleton-tail handoff lemma

Combining:

```text
merged-tail lineage
    -> extinction before parent eligibility

singleton-tail lineage
    -> lexicographic branch avoids tail
    -> head merged or already merged
    -> untouched N_a root shield
```

would establish the Temporal Root-Shield Lemma for every fresh local non-tail bridge.  Together with the different-cut and graphic-rank lemmas, this excludes unsafe acyclic low-rank resolvents from all parent-eligible pre-frontier keys.

A separate global historical-frontier/cache-DAG counting theorem would still be required to obtain the desired asymptotic Policy-0A lower bound.

## 9. Falsification conditions

The extinction lemma is rejected by any execution containing:

1. a fresh merged-tail bad lineage that reaches a later exact key unchanged;
2. a contradictory birth state whose all-source reason closure excludes the lineage and every relevant residual;
3. a recursive child carrying the same merged-tail non-tail bridge into a parent-eligible exact key;
4. a nonterminal transition not covered by a proved structural-safety case.

The finite certificate searches for conditions 1–3 through `GT_8`; condition 4 remains part of the arbitrary-`n` proof obligation.

## Claim boundary

The exact extinction disjunction and causal classification are exhaustively certified through `GT_8`: 17 causal post-unit contradictions and one `GT_4` branch extinction, with no surviving bad child exact key.  The arbitrary-`n` extinction theorem, the lexicographic singleton-tail handoff theorem, the global cache-frontier transfer, and `P` versus `NP` remain open.
