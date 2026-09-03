# JANUS TRUMP R44AG — global FPC affine expressiveness barrier

## Fixed global implicit model

R44AG tests `UNORDERED_FIXED_POINT_LOGIC_WITH_COUNTING_GLOBAL_DECISION`: fixed points and counting over an unordered relational encoding, without external order or rank operators.

## Published theorem

Albert Atserias, Andrei A. Bulatov, Anuj Dawar, *Affine systems of equations and counting infinitary logic*, Theoretical Computer Science 410(18):1666–1683, 2009, DOI `10.1016/j.tcs.2008.12.049`.

They prove that solvability of systems of equations over a fixed finite Abelian group is not definable in the relevant counting infinitary/fixed-point language. Yet this affine CSP is tractable; GF(2) is solved exactly in polynomial time by Gaussian elimination.

## Correct Legend classification

This is **not** a standalone failure of `L2_EXACT_SEMANTICS`.

A partial FPC mechanism may stay perfectly sound by returning no decision on instances it cannot express.

The theorem blocks:

`L1 UNIVERSAL EXIT` **while L2 exactness is preserved**.

So the correct seals are:

`L1_BARRIER_UNDER_L2 != L2_SOUNDNESS_FAILURE`.

`PARTIAL_SOUNDNESS != UNIVERSAL_TOTALITY`.

`INEXPRESSIBLE != FALSE`.

An FPC-only universal transition language cannot be both total and exact on the affine/GF(2) subclass already handled by TRUMP's algebraic route.

## Scope

The encoding is unordered. No transfer is made to ordered structures, algorithms exploiting concrete input order, rank-extended fixed-point logics, or arbitrary polynomial-time algorithms.

`UNORDERED_FPC_BARRIER != ORDERED_FIXED_POINT_OR_ARBITRARY_ALGORITHM_BARRIER`.

## Next mathematical question

A successor global implicit language must regain affine/rank power. It then receives either a direct exact polynomial totality theorem or a theorem-level barrier for that precisely stronger model.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
