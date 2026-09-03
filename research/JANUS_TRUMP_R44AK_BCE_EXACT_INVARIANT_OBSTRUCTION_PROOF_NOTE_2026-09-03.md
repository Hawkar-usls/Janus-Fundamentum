# JANUS TRUMP R44AK — BCE exact-invariant obstruction

## Candidate

Let `I_BCE(F)` be the unique fixed point obtained by repeatedly deleting blocked clauses. Standard BCE results give satisfiability preservation and confluence, hence a canonical polynomial-time exact preprocessing map.

## Infinite SAT fixed points

For `n>=3`, let

`E_n = AND_i [(¬x_i ∨ x_{i+1}) ∧ (x_i ∨ ¬x_{i+1})]`

with indices modulo `n`. This is satisfiable (all variables equal).

For `A_i=(¬x_i ∨ x_{i+1})`, literal `¬x_i` has the predecessor clause `A_{i-1}` as an opposing clause, and the resolvent is `(¬x_{i-1} ∨ x_{i+1})`, not a tautology. Literal `x_{i+1}` has successor `A_{i+1}` as an opposing clause, giving `(¬x_i ∨ x_{i+2})`, also not a tautology. The symmetric argument holds for `B_i=(x_i ∨ ¬x_{i+1})`. Therefore no clause is blocked and `I_BCE(E_n)=E_n`.

## Infinite UNSAT fixed points

For `n>=2`, let

`U_n={x_1,(¬x_1∨x_2),...,(¬x_{n-1}∨x_n),¬x_n}`.

This is UNSAT by forward implication. The endpoint units have non-tautological resolvents with the adjacent implication clauses. Every internal implication clause has a non-tautological resolvent with its predecessor and successor on its two literals. Hence no clause is blocked and `I_BCE(U_n)=U_n`.

## Composition with the R44AI matching-lean invariant

`U_n` is minimally unsatisfiable and therefore lean, hence matching-lean.

For `E_n`, the full formula has `2n` clauses and `n` variables, so deficiency `n`. Any proper subformula using all `n` variables has deficiency at most `n-1`. If a proper subformula uses only `v<n` variables, those variables induce at most `v-1` edges of the cycle, and each edge contributes at most two clauses. Thus it has at most `2(v-1)` clauses and deficiency at most `v-2<n`. Hence `E_n` is matching-lean.

Therefore both infinite families are fixed points of the composition `I_BCE o I_ML`.

## Verdict

`EXACT + POLYTIME + CANONICAL + COMPOSED` still does not imply universal strict descent.

Scientific boundary: `TRUMP_finished=false`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
