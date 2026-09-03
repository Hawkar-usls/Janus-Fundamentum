# JANUS TRUMP R44BL — mixed-input shared OR proxies do not lower maximum deficiency

Let

`L = l1 ∨ ... ∨ lr`, `r>=2`,

be a repeated common disjunction inside a nonempty block of clauses

`(L ∨ R_i)`.

The input variables may also occur elsewhere in the formula.

Replace `L` in the chosen block by a fresh shared proxy `y`, and add the standard exact CNF definition

`(¬l_i ∨ y)` for every `i=1,...,r`,

plus

`(l1 ∨ ... ∨ lr ∨ ¬y)`.

These `r+1` clauses enforce exactly `y <-> L`.

Let `A` be a sub-clause-set attaining `delta*(F)`.

If `A` avoids the compressed block, its clauses are unchanged, so they already show

`delta*(T_OR(F)) >= delta*(F)`.

Now suppose `A` contains at least one compressed block clause. Then all `r` input variables occur in `A`.

Let `A'` be the transformed copies of A's original clauses. Let `q` be the number of the `r` input variables that still occur in `A'` through other, uncompressed occurrences.

The transformation removes the common block occurrences of all r inputs, retains q inputs elsewhere, and introduces y. Therefore

`|Var(A')| = |Var(A)| - r + q + 1`,

and

`delta(A') = delta(A) + r - q - 1`.

Now include all `r+1` definition clauses. The proxy y is already present. Exactly `r-q` missing input variables are newly introduced by the definition, so the definition clauses increase deficiency by

`(r+1) - (r-q) = q+1`.

Hence

`delta(A' union D)`
`= delta(A)+r-q-1+q+1`
`= delta(A)+r`
`= delta*(F)+r`.

Therefore

`delta*(T_OR(F)) >= delta*(F)`

for every F, and if some maximum-deficiency witness touches the compressed block,

`delta*(T_OR(F)) >= delta*(F)+r`.

This removes the exclusivity assumption from R44BK for the standard OR-Tseitin encoding. In fact, once the exact definition clauses are charged, mixed reuse of the gate inputs elsewhere does not rescue maximum-deficiency descent.

The theorem does not cover arbitrary Boolean functions, nonstandard encodings with semantic clause deletion, multi-output circuits, or non-CNF merge states.

`DEFINITION_CLAUSE_DEBT_MUST_BE_CHARGED`.

`COMMON_SUBEXPRESSION_COMPRESSION != R44BD_RANK_DESCENT`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
