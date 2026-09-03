# JANUS TRUMP R44BK — exclusive shared OR proxies can increase maximum deficiency

Fix `r>=2` distinct input literals on variables `x1,...,xr`. Assume these variables occur only in one repeated block of clauses

`(l1 ∨ ... ∨ lr ∨ R_i)`.

Replace the repeated common disjunction by a fresh proxy `y`, producing

`(y ∨ R_i)`,

and add an exact CNF definition for

`y <-> (l1 ∨ ... ∨ lr)`.

This is a standard exact shared functional compression.

Let `A` be a maximum-deficiency sub-clause-set of the original formula that contains at least one block clause.

Because the input variables are exclusive to the compressed block, all `r` input variables occur in `A`, and after transformation they occur in none of the transformed copies of A's original clauses. One fresh variable `y` replaces them.

Therefore the transformed copy `A'` has:

- the same number of clauses as `A`;
- exactly `r-1` fewer variables.

Hence

`delta(A') = delta(A)+(r-1)`.

Crucially, `A'` alone is already a valid sub-clause-set of the full Tseitin extension. No definition clause is needed to witness this lower bound. Thus

`delta*(T(F)) >= delta*(F)+(r-1)`.

For `r=2`, a shared proxy for an exclusive repeated pair `a∨b` therefore creates at least one unit of extra maximum-deficiency debt on any maximum-deficiency witness touching the compressed block.

The point is specific: ordinary syntactic/common-subexpression compression is not automatically compression in the R44BD rank. Replacing multiple variable-side incidence resources by one proxy can reduce matching capacity.

This theorem does not cover mixed cases where the gate inputs also occur elsewhere in the formula, where a maximum-deficiency witness avoids the compressed block, or where later semantic simplification deletes additional clauses.

`BYTE_COMPRESSION != MAXDEF_COMPRESSION`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
