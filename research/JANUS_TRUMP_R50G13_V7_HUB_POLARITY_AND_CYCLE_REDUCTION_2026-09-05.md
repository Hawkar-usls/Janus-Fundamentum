# JANUS TRUMP R50G13 — V7 single external support hub: polarity and cycle reduction

## Frozen target

Assume a persisted source formula `F` has exactly seven variables, width at most four, is pre-BVE clean, and its first frozen R33 microproposal is an immediate BVE width-4 escape on pivot `x`. Assume the same-pivot R47J result is nonterminal and has width greater than four. To refute the alternate-door theorem at this state, every `y != x` must also have both R49H and R47J_SAFE closed.

R50G12 already proves that any R47J final formula on at most six variables which is nonterminal and wide must have exactly six variables, maximum width exactly five, and every chosen width-5 clause has exactly one variable outside it. That outside variable is the clause's **single external support hub**.

## Lemma 1 — exact support shape in the V6/W5 hub normal form

Let `H` be tautology-free, R33/BCE-fixed and RUP-fixed with exactly six variables. Let `C` be a surviving width-5 clause and let `z` be the unique variable outside `Vars(C)`.

For `l in C`, a nonblocking support clause `D` contains `-l` and has a non-tautological resolvent with `C` on `l`. R50G12 implies `D` contains the external variable `z`. Tautology-freedom means it contains exactly one of `z,-z`. Non-tautological resolution with `C` forbids the complement of any other literal of `C`. Hence every support has the shape

`{-l, sigma*z} union A`,

where `A` is a subset of the other literals of `C` with the same polarity as in `C`, and `sigma` is `+1` or `-1`.

## Lemma 2 — unique hub polarity per wide-clause literal

Fix `l in C`. Suppose two nonblocking supports use opposite hub polarities:

`D+ = {-l, +z} union A+`,

`D- = {-l, -z} union A-`.

Consider the frozen single-literal RUP strengthening `C -> C\{l}`. Under assumptions negating every literal of `C\{l}`, clause `C` becomes unit `l`. Every literal of `A+` and `A-` is false. Therefore `D+` becomes unit `+z` and `D-` becomes unit `-z`, producing a UP conflict. Thus `C\{l}` would be an admissible single-literal RUP strengthening, contradicting RUP-fixedness.

Therefore all nonblocking supports of one `l` use one common hub polarity `sigma(l)`.

## Lemma 3 — opposite-hub shielding

Let `E` contain `-l` and the opposite hub polarity `-sigma(l) z`. If resolving `E` with `C` on `l` were non-tautological, then `E` would itself be a nonblocking support of `l` with the forbidden opposite hub polarity. Hence that resolvent must be tautological.

Because `E` already contains `-l`, tautology can only be supplied by the complement of another literal `m in C\{l}`. Thus every such opposite-hub clause is **shielded** by at least one other complement from `C`.

This is a source-level structural obligation, not a heuristic pattern.

## Lemma 4 — all doors closed at V7 forces exact V6/W5 after every pivot

The same-pivot `x` is wide by assumption. For every alternate `y != x`, closing R47J_SAFE means its R47J final result is nonterminal and width greater than four. Exact DP removes `y` and introduces no fresh variables, so the final formula has at most six variables. R50G12's external-support theorem forces at least six variables for a surviving width-5 clause. Therefore every pivot `v` in the seven-variable source satisfies, under the all-doors-closed obstruction:

`Vars(J_v(F)) = Vars(F)\{v}` and `W(J_v(F)) = 5`.

No R47J normalization lane may eliminate an additional variable in such an obstruction.

## Lemma 5 — the V7 obstruction carries a hub map and a directed cycle

For each pivot `v`, choose the canonical lexicographically first width-5 clause in the independently replayed final `J_v(F)`. Since exactly six variables remain and the chosen clause uses five, exactly one remaining variable is outside it. Define this unique variable as `h(v)`.

Thus

`h : Vars(F) -> Vars(F)` with `h(v) != v`.

Every finite functional digraph has a directed cycle. Since self-loops are impossible, the cycle length is at least two.

Therefore any seven-variable all-doors-closed immediate-BVE counterexample must carry an explicit, independently replayable **HUB-CYCLE certificate** in addition to the R50G11 double-debt certificate.

## What this does not prove

The existence of the required hub cycle is a necessary condition, not yet a contradiction. R50G13 does **not** promote `V7_IMMEDIATE_BVE_CASE_ELIMINATED`, `IMMEDIATE_BVE_CASE_ELIMINATED`, `U_MU`, `SAT_IN_P`, or `P=NP`.

The next exact target after this reduction is:

`V7_HUB_CYCLE_IMPOSSIBILITY_UNDER_PRE_BVE_ANCESTRY_OR_EXPLICIT_REALIZING_SOURCE`.

A local or finite no-find result has no universal authority.
