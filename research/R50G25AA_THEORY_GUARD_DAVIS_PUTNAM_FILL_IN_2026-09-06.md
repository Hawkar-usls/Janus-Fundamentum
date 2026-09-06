# R50G25AA theory guard: Davis–Putnam fill-in is a real universal obstruction

## Why this note exists

R50G25Z showed a finite but strong result: every preregistered residual in its 16-case domain terminated inside the frozen polynomial state budget after controlled exact-DP fallback. That finite success must not be promoted by the argument “exact DP always removes one variable, therefore repeated exact DP is polynomial.”

## Classical obstruction

Zvi Galil, **“On the Complexity of Regular Resolution and the Davis-Putnam Procedure,”** *Theoretical Computer Science* 4(1), 23–46 (1977), DOI `10.1016/0304-3975(77)90054-8`, constructs infinitely many contradictory CNF formulas for which every regular proof tree requires exponentially many distinct clauses. The paper states the corresponding consequence for Davis–Putnam: for this family the procedure generates `2^(c n)` distinct clauses for some constant `c>0` **for any variable-elimination order**.

Independent structural literature on bucket / directional elimination likewise treats induced width as the parameter controlling variable-elimination complexity; exact elimination is generally exponential in induced width. This is background context, not a TRUMP theorem.

## Exact implication for TRUMP

The classical result blocks only the following invalid promotion:

`VARIABLE_COUNT_DESCENDS + EXACT_DP_IS_SEMANTICALLY_VALID => UNIVERSAL_POLYNOMIAL_SAT_SOLVER`.

That implication is false.

It does **not** by itself refute the current hybrid scheduler because TRUMP does not run pure Davis–Putnam: before each controlled-DP fallback it runs the frozen R33 / affine / RUP / SA-BVE policy, and restarts that stack after fallback.

Therefore the live universal obligation becomes sharper:

> Prove that the hybrid stack always opens a certified door before Galil-style elimination fill-in can force the representation beyond a polynomial root budget, or exhibit a reachable hybrid residual where every exact-DP fallback exceeds that budget.

## AA analytic certificate

For a residual CNF `F` and pivot `x`, let:

- `C,L,V` be current clause/literal/variable counts;
- `p,q` be the numbers of positive and negative parent clauses of `x`;
- `SP,SN` be total literal counts in those positive and negative parent sets.

Before materializing any resolvents, AA uses

`UB_C = C - p - q + p*q`

`UB_L = L - SP - SN + q*(SP-p) + p*(SN-q)`

`UB_S = UB_C + UB_L`.

Every raw parent pair is pessimistically counted as a distinct non-tautological resolvent of maximum pair length. Tautology deletion, literal/clause deduplication, and strict-subsumption normalization can only reduce the exact canonical result, so `UB_S <= B` is a sufficient certificate that the exact DP state fits the frozen root budget `B`.

AA independently checks the soundness relation `exact_size <= UB_S` on every materialized pivot it audits.

## Firewall

- `P_VS_NP = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `TRUMP_finished = false`
- finite AA success cannot override the classical pure-DP lower bound
- the Galil lower bound is external theory context; it is not evidence that the present hybrid already encounters the hard family
- conversely, finite hybrid success is not evidence that the hybrid universally excludes that family or its analogues
