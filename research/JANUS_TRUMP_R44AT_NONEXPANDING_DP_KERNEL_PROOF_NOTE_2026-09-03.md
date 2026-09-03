# JANUS TRUMP R44AT — Nonexpanding Davis-Putnam polarity-product kernel

For a variable `v`, let `p` and `q` be its positive and negative occurrence counts. Exact Davis-Putnam elimination removes `p+q` pivot clauses and introduces at most `p*q` non-tautological resolvents.

Hence whenever

`p*q <= p+q`,

one exact elimination cannot increase the clause count. Repeating only such eliminations with a fixed deterministic tie-break gives a polynomial exact preprocessing phase: the number of clauses never exceeds the original `m`, the number of variables only decreases, and every clause contains at most the remaining `n` variables, so total literal storage is at most `O(mn)`.

This strictly extends the degree-at-most-3 rule. In particular `(p,q)=(2,2)` is safe because `4=4`, so balanced degree-4 variables can be eliminated without increasing the number of clauses.

The fixed-point condition is `p*q>p+q`, equivalently `(p-1)(q-1)>1`, for every remaining variable.

Darmann and Döcker (Discrete Applied Mathematics 292, 2021, DOI `10.1016/j.dam.2020.12.010`) prove NP-completeness of Monotone 3-Sat-(3,2). Every variable in that exact-3-literal class has `p=3,q=2`, hence `p*q=6>5=p+q`; therefore the R44AT reducer has no legal first move on the entire class.

This is a route barrier, not a proof that the class is outside P.

Seals:

- `NONEXPANDING_DP = EXACT_POLYNOMIAL_PROGRESS_WHEN_APPLICABLE`
- `BALANCED_DEGREE4 != HARD_STOP_FOR_THIS_STRONGER_RULE`
- `MINIMAL_POLARITY_PRODUCT_HARD_CORE = (3,2)/(2,3)`
- `POLARITY_PRODUCT_CORE != TERMINAL_STATUS`
- `NP_COMPLETE_FIXED_POINT_CLASS != P_NE_NP`

Scientific status: `TRUMP_finished=false`; `SAT_IN_P=NOT_PROVED`; `P_VS_NP=OPEN`.
