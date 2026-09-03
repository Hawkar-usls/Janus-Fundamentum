# JANUS TRUMP R47A — Universal Coverage Theorem Frontier

Status: **OPEN — theorem attack in progress**

Parent charter: `JANUS_TRUMP_R47_UNIVERSAL_POLYNOMIAL_COVERAGE_CHARTER_2026-09-03.json`

## Exact theorem target

For every reachable nonterminal normalized TRUMP state `F`, prove that one of the following is polynomially discoverable and independently certifiable:

1. a terminal result; or
2. a macro transition `F -> F'` with `Phi(F') < Phi(F)`.

The current macro grammar makes the critical unresolved lemma concrete:

> **Universal Macro Lemma (UML).** For every reachable stack-lean, non-affine, RUP-stalled, BVE-stalled state `F`, there exists a variable `v` occurring in both polarities such that the frozen exact-DP -> R33 -> affine -> RUP normalization macro is accepted: it either reaches a verified terminal or returns a formula with strictly smaller frozen progress measure.

A proof of UML is necessary but not sufficient for `SAT in P`; R47A must additionally prove polynomial discovery, polynomial intermediate size, polynomial verifier cost, and polynomial global transition count.

## Why R46B matters but does not solve R47A

If transition admissibility is local, then global optimization is unnecessary:

`CERT(F -> F_v)=PASS AND [TERMINAL(F_v) OR Phi(F_v)<Phi(F)] => STOP SCANNING`.

This removes the need for a global argmin, but still leaves the universal existence question: **does such a `v` always exist?**

## Symbolic attack decomposition

R47A will attack UML by partitioning a normalized state using polynomially measurable quantities for each variable `v`:

- `p_v`: number of clauses containing `v`;
- `n_v`: number of clauses containing `-v`;
- `p_v*n_v`: exact raw resolution-pair upper count;
- number and total literal mass of non-tautological resolvents;
- subsumption gain after exact DP;
- variable elimination count;
- local overlap/duplicate-resolvent structure;
- post-DP R33 simplification gain;
- whether post-DP state becomes Horn, 2-SAT, affine, RUP-terminal, or strict-CLV descent.

The proof must show that every reachable nonterminal state enters at least one case whose transition is admissible. Any residual `OTHER` case keeps the theorem OPEN.

## Counterexample obligation

In parallel with symbolic proof, actively search for a reachable normalized state `F` satisfying all of:

- nonterminal after R33;
- not recognized affine;
- no RUP terminal;
- no accepted BVE successor;
- for every variable with both polarities, the frozen exact-DP macro is nonterminal and does not strictly decrease `Phi`.

Such an `F` is an explicit counterexample to the current Universal Macro Lemma and must be preserved rather than explained away.

## Complexity obligations that cannot be skipped

Even if UML is proved, R47A remains OPEN until these are explicit:

- discovery bound for finding an admissible `v`;
- polynomial bound on every DP/resolvent/intermediate representation;
- independent verification bound;
- polynomial bound on formula-size growth across the complete run;
- polynomial bound on number of accepted transitions;
- one composed polynomial `T(n)` in original input encoding length.

## Epistemic firewall

- `P_VS_NP = OPEN`
- `P_EQ_NP = NOT_PROVED`
- `SAT_IN_P = NOT_PROVED`
- finite audits are counterexample hunting/regression only;
- JANUS ranking is never proof authority;
- no theorem elevation until the FOR-ALL statement and the global polynomial bound are both proved.
