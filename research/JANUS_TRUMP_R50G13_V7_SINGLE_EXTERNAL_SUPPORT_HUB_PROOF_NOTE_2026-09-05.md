# JANUS TRUMP R50G13 — V7 single external support hub

## Frozen target

Assume a canonical persisted source `F` with `W(F)<=4`, `|Vars(F)|=7`, and the first frozen R33 microstep is an immediate BVE W4 escape on `x`. Assume further that same-pivot R47J on `x` is nonterminal and wide, and that every alternate `y!=x` has neither an R49H door nor an R47J_SAFE door.

R50G13 does **not** assume this object exists. It derives the exact certificate it would have to carry.

## Lemma H1 — V7 unsafe R47J has exact V6/W5 form

For any bipolar pivot `y`, frozen R47J removes `y` and introduces no fresh variables. Hence from seven source variables its final formula has at most six variables. If the final state is nonterminal and wide, R50G12 gives `V_final >= W_final + 1`. Therefore

`V_final = 6` and `W_final = 5`.

For every widest width-5 clause `C` there is exactly one final variable `z` outside `Vars(C)`, and every nonblocking support of every literal of `C` uses `z`.

## Lemma H2 — support polarity coherence

Fix a widest clause `C`, a literal `l in C`, and its unique external hub variable `z`. Suppose two nonblocking supports existed, one containing `z` and one containing `-z`.

Apply the assumptions `neg(C\\{l})`. Clause `C` becomes unit `l`. Because each support is nontautological against `C` on `l`, all its other C-literals are falsified by those assumptions. After `l` is forced, the two supports become unit `z` and unit `-z`, yielding a UP conflict.

Therefore `C\\{l}` would be a frozen single-literal RUP strengthening, contradicting RUP fixpoint. Thus all nonblocking supports for a fixed `l` use one common hub polarity `sigma(l)`.

## Lemma H3 — opposite-hub guard obligation

Fix `l` and `sigma(l)`. Under the same assumptions `neg(C\\{l})`, a nonblocking support forces `sigma(l) z`.

Let `E` be any clause containing `-sigma(l) z`. Since the final variable set is exactly `Vars(C) union {z}`, to avoid a UP conflict `E` must already be satisfied after the assumptions and forced literals. Equivalently, `E` must contain at least one literal from

`{ l } union { -k : k in C, k != l }`,

where `k` denotes the signed literal occurring in `C`.

If not, all non-hub literals of `E` are false and the forced hub value falsifies its hub literal, producing a conflict and again making `C\\{l}` RUP-redundant.

This is an exact guard condition, not a heuristic.

## Lemma H4 — all seven pivots carry chi debt

For every alternate `y!=x`, absence of R49H gives `chi_star(F,y)>=5`; W4 gives `chi_star(F,y)<=6`. Hence `chi_star(F,y) in {5,6}`.

For distinguished `x`, immediate BVE W4 escape itself contains a non-tautological resolvent wider than four, so `chi_star(F,x)>=5`; again W4 gives `<=6`.

Therefore an all-doors-closed V7 obstruction satisfies

`forall y in Vars(F): chi_star(F,y) in {5,6}`.

## Lemma H5 — sevenfold hub debt

Same-pivot `x` is assumed nonterminal-wide. Every alternate `y!=x` has its R47J_SAFE door closed, so each alternate R47J final is also nonterminal-wide.

By H1, **all seven pivots** therefore produce exact independently replayable final states with:

- exactly six variables,
- max width exactly five,
- R33/RUP normalization fixpoint,
- a single external hub for every widest clause,
- H2 polarity coherence,
- H3 opposite-hub guard obligations.

Thus a genuine V7 obstruction is not one single-hub core. It is a **sevenfold hub-debt object**, plus chi debt `{5,6}` on every source pivot.

## What this closes and what it does not

R50G13 closes the symbolic normal form above. It does not yet prove that sevenfold hub debt is impossible and therefore does not yet eliminate V7.

The next exact obligation is:

`SEVENFOLD_HUB_DEBT_INCIDENCE_IMPOSSIBILITY_OR_EXPLICIT_V7_ALL_DOORS_CLOSED_WITNESS`.

Firewalls remain: `V6 eliminated`, `V7 OPEN`, `full immediate-BVE OPEN`, `U_mu OPEN`, `SAT_IN_P NOT_PROVED`, `P_VS_NP OPEN`.
