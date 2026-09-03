# JANUS TRUMP R47A3 — Post-subsumption descent correction

Status: **CORRECTION / STRONGER STRUCTURAL INVARIANT**

R47A2 intentionally searched for a dense bipolar witness with many unique non-tautological resolvents. Its frozen CI failed, but the failure was scientifically informative: the witness satisfied `unique_non_tautological_resolvents > p+n` for every variable, yet exact DP still produced strict CLV descent for every variable after canonicalization and subsumption.

This establishes that **raw resolvent multiplicity is not the right obstruction invariant**.

For variable `v`, let:

- `P_v` and `N_v` be the positive/negative parent-clause sets,
- `p_v=|P_v|`, `n_v=|N_v|`,
- `B_v` be the unaffected base clauses,
- `R_v` be the unique non-tautological exact-DP resolvents,
- `T_v = SUBSUMPTION_MINIMIZE(CANONICAL(B_v union R_v))`.

The exact post-DP clause count is therefore

`C'_v = |T_v|`.

The correct clause-descent test is simply

`C'_v < C`.

Equivalently define the certified post-subsumption gain

`g_v = C - |T_v|`.

Then

`g_v > 0  =>  exact DP on v is a strict clause-count descent`.

The quantity `g_v` is polynomially computable under the existing frozen R42/R45A implementation: there are at most `p_v n_v <= C^2/4` parent pairs; canonical deduplication is polynomial; the current subsumption pass uses at most quadratic pair checks in the pool size. No SAT oracle or truth label is needed.

## R47A2 forensic correction

The frozen R47A2 witness had input CLV `(13,39,5)` and for every variable showed raw unique-resolvent expansion, but after canonical subsumption its exact-DP outputs had clause counts `10,9,11,12,7`, respectively. Hence every variable had `g_v>0` despite raw expansion.

Therefore the implication

`|R_v| > p_v+n_v  =>  no direct DP descent`

is false.

The earlier sufficient lemma

`new_resolvents < p_v+n_v  =>  clause descent`

remains valid, but its converse must not be used.

## Algorithmic upgrade

The producer should rank/pre-filter pivots using the exact post-subsumption gain rather than raw resolvent count alone:

1. Cheap occurrence screen (`p_v,n_v`).
2. Generate unique non-tautological resolvents.
3. Canonical merge with unaffected base.
4. Subsumption minimize.
5. Compute `g_v = C-|T_v|`.
6. If `g_v>0`, emit immediate certified descent and stop under FIRST-CERTIFIED-DESCENT semantics.
7. Only if `g_v<=0` continue into bounded-ascent normalization/RUP/other macro layers.

This is an algorithmic improvement because many apparent raw-expansion pivots can be accepted before invoking heavier normalization.

## New obstruction class

A genuine direct-DP-resistant state must satisfy, for every bipolar variable `v`,

`|T_v| >= C`.

That is stronger than any condition based only on `p_v`, `n_v`, or raw resolvent multiplicity.

The next counterexample hunt must therefore target **post-subsumption non-descent for all variables**, not raw resolvent expansion.

## Firewalls

- `R47A_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
- `R47A2 = SCIENTIFICALLY_INFORMATIVE_FAILED_HYPOTHESIS`
- `RAW_RESOLVENT_EXPANSION != POST_SUBSUMPTION_NON_DESCENT`
