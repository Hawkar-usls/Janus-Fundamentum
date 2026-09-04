# JANUS TRUMP R50G5 — Immediate-BVE exact-descent algebraic reduction

## Scope

This note uses only the frozen source definitions already present in R33, R45A, R47J, R50A and R50G4. No learned selector, score, random choice, empirical frequency or post-hoc rule is proof authority.

Let `F` be a canonical CNF with `W(F) <= 4`. Assume the first frozen R33 micro-proposal at `F` is BVE on pivot `x`, and its proposed successor leaves W4. This is `IMMEDIATE_BVE_W4_ESCAPE` in R50G4.

Write:

- `P_x = {C in F : x in C}`,
- `N_x = {C in F : -x in C}`,
- `R_x` for the distinct non-tautological DP resolvents of `P_x x N_x`,
- `B = F \ (P_x union N_x)`.

The R33 BVE proposal is the canonical formula

`G = canon(B union R_x)`

and R33 admits this BVE candidate only when

`|R_x| <= |P_x| + |N_x|`

and

`measure_R33(G) < measure_R33(F)`.

The escape condition says only `W(G) > 4`; it does not negate exactness or descent.

## Theorem 1 — the immediate-BVE pivot is bipolar

R33 calls `bve_candidate` only when both positive and negative parent sets are nonempty. Therefore

`P_x != empty` and `N_x != empty`.

Hence `x` is bipolar and exact DP on `x` is defined.

## Theorem 2 — R45A exact DP is the same DP pool followed by certified subsumption minimisation

`r45a.exact_dp_record(F,x)` computes the same full set of non-tautological cross-polarity resolvents, forms

`Pool = canon(B union R_x) = G`,

then applies `subsumption_minimize` to obtain `H`.

Thus `H` contains no clause not already in `G`; clauses omitted from `G` are certified subsumed by retained clauses. Consequently

`SAT(F) iff SAT(H)`

under exact variable elimination plus satisfiability-preserving subsumption deletion.

Moreover

`C(H) <= C(G)`,

and if clause count is equal then the retained literal total cannot exceed that of `G`. Therefore, in R47J's `(C,L,V)` measure,

`clv(H) <=lex clv(G)`.

Since R33 admitted the BVE only when `measure(G) < measure(F)`, and both measures are `(C,L,V)`, we obtain

`clv(H) < clv(F)`.

This is a strict descent before any R47J normalisation begins.

## Theorem 3 — no fresh variables and strict variable descent

Exact DP removes every parent containing `x` or `-x` and every resolvent omits `x`. It introduces no fresh variable. Hence

`Vars(H) subseteq Vars(F) \ {x}`,

so

`|Vars(H)| <= |Vars(F)| - 1`.

R47J normalisation uses existing R33 rules, affine recognition/terminal solving, and RUP literal strengthening/deletion. None introduces a fresh variable. Therefore for every nonterminal final formula `J` returned by the same-pivot R47J macro,

`Vars(J) subseteq Vars(H) subseteq Vars(F) \ {x}`.

Thus the machine-safe predicates `no_fresh_variables` and `strict_variable_descent` are automatically true for this same pivot.

## Theorem 4 — R47J normalisation preserves the already-achieved strict CLV descent

R47J starts from `H`. On each changing R33 pass it requires strict CLV descent. On each changing RUP pass it requires strict CLV descent and restarts. If neither changes, it stops at the current state. Affine/Horn/2SAT/RUP-UNSAT outcomes are certified terminals.

Therefore, for a nonterminal final formula `J`,

`clv(J) <=lex clv(H) < clv(F)`.

So the same-pivot R47J macro is always legacy-accepted:

`terminal(J) OR clv(J) < clv(F)`.

No empirical assumption is used.

## Theorem 5 — per-transition resource and replay authority

R45A's exact DP record checks all positive-negative parent pairs. With `C=C(F)`, the number of pair checks is bounded by `C^2/4 + 1`; its peak explicit clause/literal ledger is polynomial in the explicit input state. R47J supplies a finite restart-height bound and independent replay of the exact macro. Therefore this same-pivot macro is an exact, independently replayable, polynomial-per-transition producer.

This theorem is per transition. It is not an end-to-end polynomiality theorem by itself.

## Corollary — exact characterization of the only same-pivot failure

R50A machine-safe R47J acceptance is

`terminal OR (no_fresh AND strict_variable_descent AND final_max_width <= 4)`.

For an immediate-BVE pivot `x`, Theorems 3 and 4 make the first two nonterminal predicates automatic. Hence

`R47J_SAFE(F,x)`

**iff**

`R47J_terminal(F,x) OR W(J_x) <= 4`.

Therefore an immediate BVE escape is not a failure of exactness, descent, reconstruction, or per-transition polynomiality. The only same-pivot obstruction left by the frozen W4 machine is failure of the normalised exact-DP image to re-enter W4.

## Reduced universal obligation

The original desired implication

`IMMEDIATE_BVE_ESCAPE(F) => exists v [R49H(F,v) OR R47J_SAFE(F,v)]`

is therefore reduced to the following precise statement:

For every reachable immediate-BVE state `F`, if `x` is its deterministic immediate-BVE pivot, then either

1. the exact same-pivot R47J normalisation is terminal or returns to W4, or
2. some other pivot is already R49H-authorised or R47J-safe.

Equivalently, a counterexample must satisfy all of:

- immediate BVE on `x`,
- same-pivot exact R47J macro exists and strictly descends CLV,
- same-pivot final state is nonterminal and still has width > 4,
- no R49H pivot exists,
- no other R47J-safe pivot exists.

That object is now the exact algebraic target. No broader search predicate is authoritative.

## Status boundary

Closed here from frozen source definitions:

- immediate BVE implies a bipolar exact-DP pivot;
- same-pivot exact DP exists;
- exactness/replay/per-transition polynomial envelope hold;
- no fresh variables;
- strict variable descent;
- strict CLV descent;
- legacy R47J acceptance;
- machine-safe failure can only be nonterminal width > 4 after normalisation.

Not closed here:

- universal W4 re-entry;
- existence of an alternate certified door in every remaining case;
- universal `U_mu` progress;
- `3SAT in P`;
- `P=NP`.

The next theorem target is therefore no longer generic BVE escape. It is the much narrower **wide-survivor impossibility or alternate-door theorem** for the normalised exact-DP image of the deterministic immediate-BVE pivot.
