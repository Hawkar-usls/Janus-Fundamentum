# JANUS TRUMP R44BE — selector OR merge accumulates maximum-deficiency debt

Let `A` and `B` be CNF formulas. Rename their variables apart, obtaining `A#` and `B#`, and introduce a fresh selector `s`:

`M = {s ∨ C : C∈A#} ∪ {¬s ∨ D : D∈B#}`.

The construction is exact for SAT-OR:

`SAT(M) iff SAT(A) or SAT(B)`.

Write `a=delta*(A)>=1`, `b=delta*(B)>=1`.

For any nonempty sub-clause-set `Q⊆M`, let `A'` and `B'` denote the corresponding **unguarded** selected subsets from the two branches.

If `B'=empty`, the fresh selector occurs in every selected guarded A-clause, so

`delta(Q)=delta(A')-1 <= a-1`.

The symmetric bound is `b-1` when `A'=empty`.

If both parts are nonempty, the disjoint branch-variable copies plus the single selector give

`delta(Q)=|A'|+|B'|-|Var(A')|-|Var(B')|-1`

`=delta(A')+delta(B')-1`

`<=a+b-1`.

Because `a,b>=1`, maximum deficiency on each branch is attained by a nonempty sub-clause-set. Taking guarded copies of maximizers `A0,B0` yields deficiency exactly `a+b-1`. Hence

`boxed(delta*(M)=a+b-1)`.

For the R44BD target, if both children have rank exactly `k-1`, then

`delta*(M)=2k-3`.

For `k>=3`,

`2k-3 > k-1`,

so even the maxdef-friendliest disjoint-copy selector merge fails the required rank descent.

If the original branch formulas are not renamed apart, use the unguarded selected subsets `A'`,`B'`. The mixed-subset identity is then

`delta(Q)=delta(A')+delta(B')-1+|Var(A')∩Var(B')|`.

Thus semantic-variable overlap can only increase the mixed deficiency relative to the disjoint-copy baseline.

Important notation warning: if `QA,QB` denote the already-guarded subsets, their individual deficiencies already count selector `s`; the displayed `-1` identity must therefore be written in terms of the **unguarded** branch subsets as above.

This theorem does not block every possible OR merge. It blocks the selector-guarded class in the precise rank used by R44BD. The special layer `k=2`, where two rank-one children merge to rank one, is not refuted by this calculation.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
