# C025 — Akinator proof-carrying elimination selector

Canonical TOPA source:

`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_AKINATOR_PROOF_CARRYING_ELIMINATION_SELECTOR.md`

Status: **GLOBAL-PROGRESS SKELETON PROVED / UNIVERSAL CAP AVAILABILITY OPEN**  
Claim ceiling: **P_VS_NP = OPEN**

## Exact operation

For CNF `F` and current variable `x`, partition clauses into positive pivot clauses `P_x`, negative pivot clauses `N_x`, and retained clauses `R_x`. Add every distinct non-tautological Resolution resolvent between `P_x` and `N_x`, remove all pivot clauses, and keep `R_x`.

Call the result `ELIM_x(F)`.

Analytic theorem:

`ELIM_x(F)` is exactly the existential projection `exists x . F` on the remaining variables. Thus SAT is preserved with no semantic oracle.

A proof-carrying certificate lists the pivot partition and, for every `P_x x N_x` pair, either the exact resolvent or a tautology witness, plus canonical deduplication and the exact output fingerprint. Verification is polynomial in explicit pair/certificate bytes.

## True global progress

For pure elimination, `Phi(F)=#remaining variables`. Every accepted step removes one variable and introduces none, so `Phi` decreases exactly by one. There are at most the initial number of variables accepted steps.

## Hidden exponent

If `M_t` is current clause count, a crude complete-elimination recurrence permits

`M_{t+1} <= O(M_t^2)`.

Repeatedly treating each step as merely “polynomial in current state” can yield degree drift such as

`M_t <= N^(2^t)`

up to constants.

Therefore:

`POLY_IN_CURRENT_STATE_AT_EACH_STEP != UNIFORM_POLY_IN_ORIGINAL_INPUT`.

## ELIM-CAP_C

Freeze one universal constant `C` before seeing the input and cap every materialized state by `N^C`, where `N` is original encoded input length.

At every state scan pivot variables in canonical order, stream the exact elimination result, abort a candidate once the output would exceed the cap, and accept the first pivot whose complete exact output fits. Never backtrack.

Conditional theorem:

If for some universal fixed `C` every nonterminal state reached by this deterministic selector has at least one capped pivot, the selector decides CNF-SAT in deterministic polynomial time, implying `P=NP`.

This is conditional only.

`UNIVERSAL_ELIM_CAP_C_AVAILABILITY = OPEN`.

## Boundary-width sufficient condition

Let `B_t(x)` be all variables co-occurring with `x` or `NOT x` in pivot clauses, excluding `x`, and let `w=|B_t(x)|`.

Every distinct non-tautological resolvent lies over this boundary; there are at most `3^w` possible non-tautological clauses. Hence a universal `w=O(log N)` dynamic elimination-width bound is a sufficient polynomial regime.

High `w` does not imply all `3^w` clauses actually occur.

## Macro restore cap

When no pivot fits the fixed cap, a structural macro/rewrite must have a precise job: restore at least one capped elimination pivot while preserving SAT, staying under fixed polynomial state/extension budgets, and being deterministically discoverable from a polynomial candidate language with no oracle or backtracking.

For macro-assisted steps with extension budget `K_max(N)<=N^k`, use

`Phi_ext = r*(n+K_max+1) + v`

where `r` is remaining original-root count and `v` total live variables. Require each atomic macro-assisted step to eliminate at least one original root; then `Phi_ext` strictly decreases even if bounded extensions are introduced.

`MACRO_RESTORE_CAP_UNIVERSAL_AVAILABILITY = OPEN`  
`POLYNOMIAL_AKINATOR = OPEN`  
`P_VS_NP = OPEN`
