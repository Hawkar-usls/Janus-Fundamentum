# JANUS TRUMP R44BG — occurrence splitting preserves maximum deficiency

## Exact transform

For every literal occurrence `e` of an original variable `x`, create a fresh occurrence variable `y_e` and use the same polarity of `y_e` in the transformed main clause.

Add one polarity-aware link:

- positive occurrence `x`: `(¬y_e ∨ x)`;
- negative occurrence `¬x`: `(¬x ∨ y_e)`.

The first says `y_e -> x`; the second says `x -> y_e`.

For a fixed assignment to original master variables, a transformed positive literal can be true exactly when the original positive literal is true, and a transformed negative literal can be true exactly when the original negative literal is true. Because occurrence variables are private to literal occurrences, extensions can be selected independently across occurrences. Hence

`exists_y T_split(F)(x,y) iff F(x)`.

## Maximum-deficiency theorem

Take any selected subformula `Q` of `T_split(F)`.

Let:

- `A` be its selected transformed main clauses;
- `L` be its selected link clauses;
- `U` be the set of all occurrence indices belonging to clauses in `A`.

Selected occurrence variables are exactly `U union L`. Selected master variables are exactly `Var(L)`, i.e. original variables having at least one selected link. Therefore

`delta(Q)`
`= |A|+|L|-|U union L|-|Var(L)|`
`= |A|-|U minus L|-|Var(L)|`.

For each original variable appearing in `A`, either at least one selected-main occurrence has its link in `L`, in which case the original variable is counted in `Var(L)`, or no selected-main occurrence has its link in `L`, in which case at least one occurrence of that variable is counted in `U minus L`. Different original variables have different occurrence indices. Thus

`|Var(L)| + |U minus L| >= |Var(A)|`.

Consequently

`delta(Q) <= |A|-|Var(A)| <= delta*(F)`.

So `delta*(T_split(F))<=delta*(F)`.

For equality, take an original sub-clause-set `A0` attaining `delta*(F)`. Select the transformed main clause for each clause of `A0`, and select every link belonging to every occurrence in `A0`. Then `U subset L`, `Var(L)=Var(A0)`, and

`delta(Q)=|A0|-|Var(A0)|=delta*(F)`.

Hence

`boxed(delta*(T_split(F))=delta*(F))`.

## R44BD consequence

Occurrence splitting is a natural shared-master auxiliary construction: it can make every transformed main-clause literal use a private low-occurrence variable while the master variables appear only in implication links. Nevertheless it conserves maximum deficiency exactly. Thus it cannot repair the additive selector debt proved in R44BE.

This theorem is not a barrier for arbitrary shared/nonlocal gadgets.

`LOWER_OCCURRENCE_DEGREE != LOWER_MAXIMUM_DEFICIENCY`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
