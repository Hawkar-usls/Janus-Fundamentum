# JANUS TRUMP R47K — RUP Strengthening Repayment Lower-Bound Theorem

Date: 2026-09-03

Status: **SYMBOLIC SUFFICIENT-CONDITION THEOREM; O4 REMAINS OPEN**

## Scope

Let `F` be a genuine reachable residual fixpoint under the frozen pre-macro stack. For a bipolar pivot `v`, let:

- `D_v` be frozen exact DP + canonicalization + subsumption minimization;
- `P_v` be the canonical formula after the frozen R33 normalization of `D_v`, assuming R33 does not semantically terminate;
- `G_v` be the canonical formula after frozen R35B RUP, assuming affine recognition and RUP do not semantically terminate;
- `k_v` be the number of successful R35B single-literal RUP strengthenings from `P_v` to `G_v`.

Write `CLV(X)=(C(X),L(X),V(X))` lexicographically.

## Lemma 1 — each successful frozen RUP strengthening repays at least one literal

R35B chooses a source clause `C`, removes exactly one literal `l`, and replaces `C` by the strict subclause `C\{l}`. The replacement is then canonicalized with the rest of the formula.

One successful strengthening therefore cannot add a clause, literal, or variable. Before any extra duplicate collapse caused by canonicalization, it removes exactly one literal occurrence. Duplicate collapse can only remove more material.

Hence after `k_v` successful strengthenings:

`C(G_v) <= C(P_v)`

`L(G_v) <= L(P_v) - k_v`

`V(G_v) <= V(P_v)`.

This bound is independent of the detailed UP trace. The UP trace and independent residual-formula checker remain proof authority for whether each strengthening is semantically valid.

## Lemma 2 — clause-tie repayment sufficient condition

Assume

`C(P_v)=C(F)`.

Define the literal debt remaining after R33:

`delta_v = L(P_v)-L(F)`.

If `delta_v <= 0`, then `P_v` is already at or below the original clause/literal coordinates. Because exact DP removed pivot `v` and the frozen normalizers introduce no fresh variable, the nonterminal macro is already a strict CLV descent whenever the first two coordinates tie exactly.

If `delta_v > 0` and

`k_v >= delta_v`,

then by Lemma 1:

`L(G_v) <= L(P_v)-k_v <= L(F)`.

Therefore either:

1. `C(G_v)<C(F)`, giving immediate clause descent; or
2. `C(G_v)=C(F)` and `L(G_v)<L(F)`, giving literal descent; or
3. `C(G_v)=C(F)` and `L(G_v)=L(F)`, in which case the eliminated pivot remains absent and `V(G_v)<V(F)`, giving variable-coordinate descent.

Thus:

`C(P_v)=C(F) AND k_v >= max(0,L(P_v)-L(F))`

is a sufficient condition for a nonterminal frozen R45A macro to be accepted.

## Corollary — necessary form of a rejected clause-tie pivot

For a nonterminal rejected pivot with

`C(P_v)=C(F)`, necessarily:

`L(P_v)>L(F)`

and

`k_v < L(P_v)-L(F)`.

Otherwise Lemma 2 would force acceptance.

So an O4 counterexample cannot merely have positive DP debt. Every clause-tie pivot must additionally preserve a strictly positive **post-R33 literal deficit** that exceeds the total number of successful certified RUP strengthenings.

## Clause-debt boundary

If

`C(P_v)>C(F)`,

`k_v` alone does not lower-bound clause-count repayment: a single-literal strengthening normally preserves clause count, although canonical duplicate collapse may reduce it. Therefore no universal clause-debt repayment theorem is claimed here.

For this lane the remaining exact accounting variables are:

`q_v = C(P_v)-C(G_v)`

and, on clause repayment tie,

`lambda_v = L(P_v)-L(G_v)`.

A rejected nonterminal clause-debt pivot must fail the lexicographic repayment threshold relative to `F`.

## Updated O4 adversary shape

A genuine reachable macro-dead residual must have, for every bipolar pivot `v`:

1. no certified terminal escape;
2. no post-R33 direct CLV descent;
3. if `C(P_v)=C(F)`, a positive literal deficit `delta_v>0` with `k_v<delta_v`;
4. if `C(P_v)>C(F)`, insufficient clause collapse and subsequent literal/variable repayment to cross below `F`.

This is strictly narrower than the R47H debt partition.

## Algorithmic consequence

For a candidate pivot, the deterministic producer may maintain the observable quantity

`literal_deficit_after_R33 = max(0,L(P_v)-L(F))`.

During RUP, once the count of independently certified successful strengthenings reaches that deficit while the clause coordinate is tied to `F`, acceptance is already guaranteed by the theorem. Continuing RUP is unnecessary for the purpose of proving existence of a descending successor, though a production early-stop implementation requires its own replay/regression gate.

This is a proof-derived early-accept opportunity, not learned guidance.

## Epistemic firewall

- R47K proves a sufficient condition, not that some pivot always satisfies it.
- The clause-debt lane remains open.
- Universal existence of terminal escape or sufficient repayment remains `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
