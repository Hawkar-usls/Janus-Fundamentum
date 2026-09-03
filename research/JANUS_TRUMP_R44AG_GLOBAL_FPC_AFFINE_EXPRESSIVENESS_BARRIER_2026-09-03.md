# JANUS TRUMP R44AG — global FPC affine expressiveness barrier

## Fixed global implicit model

R44AG tests a route that is genuinely global but implicit rather than explicitly materializing a large relaxation:

`UNORDERED_FIXED_POINT_LOGIC_WITH_COUNTING_GLOBAL_DECISION`.

The model allows fixed points and counting on an unordered relational encoding, but no externally supplied linear order and no rank/linear-algebra operator.

## Published theorem

Albert Atserias, Andrei A. Bulatov, Anuj Dawar, *Affine systems of equations and counting infinitary logic*, Theoretical Computer Science 410(18):1666–1683, 2009, DOI `10.1016/j.tcs.2008.12.049`.

They prove that solvability of systems of equations over a fixed finite Abelian group is not definable in infinitary finite-variable logic with counting, and hence is not definable in least fixed-point logic or fixed-point logic with counting on the unordered encodings considered.

This is deliberately striking because affine solvability is tractable. In particular, the GF(2) specialization is exactly solvable in polynomial time by Gaussian elimination.

## TRUMP consequence

`GLOBAL_FIXED_POINT_ACCESS != COMPLETE_ALGEBRAIC_ACCESS`.

An unordered FPC-only universal transition language would already lose an exact tractable subclass that TRUMP knows how to recognize through its CNF -> GF(2) route.

Therefore:

`TRACTABLE != FPC_DEFINABLE`.

and

`IMPLICIT_COMPRESSION != EXACTNESS_IF_THE_LANGUAGE_LOSES_AFFINE_SOLVABILITY`.

The barrier is about expressiveness, not runtime hardness. It blocks this fixed implicit semantic language from discharging L1/L2 universal exactness.

## Critical scope

The encoding is unordered. R44AG does **not** transfer this theorem to ordered structures, algorithms allowed to exploit an external order, fixed-point logics extended by rank operators, or arbitrary polynomial-time algorithms.

Seal:

`UNORDERED_FPC_BARRIER != ORDERED_FIXED_POINT_OR_ARBITRARY_ALGORITHM_BARRIER`.

## Next mathematical question

A successor implicit global language must at least regain the affine/rank power that FPC lacks. The next admissible object is therefore a precisely fixed rank/linear-algebra-extended global model, and it must receive either:

- a direct exact polynomial totality theorem for arbitrary 3CNF, or
- an expressiveness/complexity barrier for that stronger fixed model.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
