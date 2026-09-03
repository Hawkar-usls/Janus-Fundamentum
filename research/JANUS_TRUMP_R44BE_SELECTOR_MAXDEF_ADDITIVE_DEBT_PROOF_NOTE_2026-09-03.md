# JANUS TRUMP R44BE — selector OR merge accumulates maximum-deficiency debt

Let `A` and `B` be CNF formulas. Rename their variables apart, obtaining `A#` and `B#`, and introduce a fresh selector `s`:

`M = {s ∨ C : C∈A#} ∪ {¬s ∨ D : D∈B#}`.

The construction is exact for SAT-OR:

`SAT(M) iff SAT(A) or SAT(B)`.

Write `a=delta*(A)>=1`, `b=delta*(B)>=1`.

For any nonempty sub-clause-set `Q⊆M`, split it as `Q=QA∪QB`.

If `QB=empty`, the selector occurs in every clause of `QA`, so

`delta(Q)=delta(QA_un_guarded)-1 <= a-1`.

The symmetric bound is `b-1` when `QA=empty`.

If both parts are nonempty, the branch-variable copies are disjoint and the selector is their only common variable. Therefore

`delta(Q)=|QA|+|QB|-|Var(QA_un_guarded)|-|Var(QB_un_guarded)|-1`

`=delta(QA_un_guarded)+delta(QB_un_guarded)-1`

`<=a+b-1`.

Because `a,b>=1`, maximum deficiency on each branch is attained by a nonempty sub-clause-set. Taking guarded copies of maximizers `A0,B0` yields a mixed subset of deficiency exactly `a+b-1`. Hence

`boxed(delta*(M)=a+b-1)`.

For the R44BD target, if both children have rank exactly `k-1`, then

`delta*(M)=2k-3`.

For `k>=3`,

`2k-3 > k-1`,

so even the maxdef-friendliest disjoint-copy selector merge fails the required rank descent.

If the children share their original semantic variables instead, a mixed subset has the more general identity

`delta(Q)=delta(QA)+delta(QB)-1+|Var(QA) intersect Var(QB)|`,

so overlap can only make the maximum-deficiency problem worse.

This theorem does not block every possible OR merge. It blocks the entire selector-guarded family in the precise rank used by R44BD. The special layer `k=2`, where two rank-one children merge to rank one, is not refuted by this calculation.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
