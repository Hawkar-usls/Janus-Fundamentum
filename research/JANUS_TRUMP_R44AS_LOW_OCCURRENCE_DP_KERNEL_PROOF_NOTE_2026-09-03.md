# JANUS TRUMP R44AS — Low-occurrence Davis-Putnam kernel

For a variable `v` occurring `p` times positively and `q` times negatively, Davis-Putnam elimination removes all `p+q` pivot clauses and adds at most `p*q` non-tautological resolvents.

If `d=p+q<=3`, then

`p*q <= floor(d^2/4) <= 2 < d` for every nonzero `d<=3` except the trivial one-polarity cases where the bound is even smaller.

Therefore eliminating a degree-at-most-3 variable strictly reduces the number of variables and does not increase the number of clauses; in fact the clause count drops by at least one before optional tautology/subsumption cleanup.

A deterministic procedure that repeatedly eliminates the first degree-at-most-3 variable is therefore an exact polynomial-time preprocessing phase with polynomial live state.

It is not universal. Published bounded-occurrence hardness results place the next frontier exactly at four occurrences: 3-SAT remains NP-complete on classes where every variable occurs exactly four times; Darmann-Döcker 2021 establish even strong exact-3-literal monotone four-occurrence restrictions.

Hence arbitrarily large nonterminal degree-4 cores exist on which the reduction has no first move.

Seals:

- `DEGREE_LE_3_DP = EXACT_POLYNOMIAL_PROGRESS_WHEN_APPLICABLE`
- `DEGREE4_CORE != TERMINAL_STATUS`
- `LOW_DEGREE_PROGRESS != UNIVERSAL_DESCENT`
- `NP_HARD_FIXED_POINT_CLASS != P_NE_NP`

Scientific status: `TRUMP_finished=false`; `SAT_IN_P=NOT_PROVED`; `P_VS_NP=OPEN`.
