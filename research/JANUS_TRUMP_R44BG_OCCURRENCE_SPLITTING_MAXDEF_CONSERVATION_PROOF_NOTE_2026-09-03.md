# JANUS TRUMP R44BG — occurrence splitting preserves maximum deficiency

## Exact transform

For every literal occurrence `e` of an original variable `x`, create a fresh occurrence variable `y_e` and use the same polarity of `y_e` in the transformed main clause.

Add one polarity-aware link:

- positive occurrence `x`: `(¬y_e ∨ x)`;
- negative occurrence `¬x`: `(¬x ∨ y_e)`.

For a fixed assignment to original master variables, the occurrence variables admit an extension exactly when the original clauses are satisfied. Hence

`exists_y T_split(F)(x,y) iff F(x)`.

## Degree scope

This construction makes each private occurrence variable `y_e` have degree 2 and removes direct reuse of the same master variable inside the transformed main clauses.

It does **not** generally lower the standard maximum variable occurrence degree: if an original master variable `x` had total degree `d`, then `x` appears in exactly `d` link clauses. Thus its total degree remains `d`.

The theorem below is therefore about exact semantics and maximum deficiency, not about reducing the formula's usual maximum variable degree.

## Maximum-deficiency theorem

Take any selected subformula `Q` of `T_split(F)`.

Let:

- `A` be its selected transformed main clauses;
- `L` be its selected link clauses;
- `U` be the set of all occurrence indices belonging to clauses in `A`.

Selected occurrence variables are exactly `U union L`. Selected master variables are exactly `Var(L)`. Therefore

`delta(Q)=|A|+|L|-|U union L|-|Var(L)|`

`=|A|-|U minus L|-|Var(L)|`.

For each original variable appearing in `A`, either at least one selected-main occurrence has its link in `L`, in which case the original variable is counted in `Var(L)`, or no selected-main occurrence has its link in `L`, in which case at least one occurrence of that variable is counted in `U minus L`. Different original variables have different occurrence indices. Thus

`|Var(L)| + |U minus L| >= |Var(A)|`.

Consequently

`delta(Q) <= |A|-|Var(A)| <= delta*(F)`.

For equality, take an original sub-clause-set `A0` attaining `delta*(F)`. Select its transformed main clauses and all occurrence links belonging to them. Then `U subset L`, `Var(L)=Var(A0)`, and

`delta(Q)=|A0|-|Var(A0)|=delta*(F)`.

Hence

`boxed(delta*(T_split(F))=delta*(F))`.

## R44BD consequence

Occurrence splitting provides private degree-2 variables in main clauses, while the master variables move into implication links. Even with that structural separation it conserves maximum deficiency exactly. Thus it cannot repair the additive selector debt proved in R44BE.

This theorem is not a barrier for arbitrary shared/nonlocal gadgets.

`PRIVATE_OCCURRENCE_DEGREE_TWO != LOWER_STANDARD_MAX_VARIABLE_DEGREE`.

`OCCURRENCE_COPIES != FREE_MATCHING_CREDIT`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
