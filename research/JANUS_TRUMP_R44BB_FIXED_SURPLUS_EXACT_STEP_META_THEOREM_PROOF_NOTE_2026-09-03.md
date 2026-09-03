# JANUS TRUMP R44BB — fixed-surplus witness batch-elimination bound

Let `F` be a normalized Boolean CNF of maximum clause width at most 3 with

`σ(F)=s>=1`

for a fixed constant `s`.

The nontrivial statement proved here is **not** that a single exact polynomial Davis-Putnam step exists: one ordinary DP elimination is already polynomial for an arbitrary current CNF state. The actual content is a bound on the size of an entire minimum-surplus witness when no R44AT nonexpanding variable exists.

Assume

`p(v)q(v)>p(v)+q(v)`

for every variable `v`.

For total degree `d=p+q<=4`,

`pq<=floor(d^2/4)<=d`,

contradicting the strict inequality. Hence every variable has degree at least 5.

Compute a nonempty surplus witness `V` with

`|Γ(V)|-|V|=s`.

Every occurrence of a variable in `V` belongs to a clause in `Γ(V)`. Since each clause has width at most 3,

`sum_{v in V} d(v) <= 3|Γ(V)| = 3(|V|+s)`.

The degree lower bound gives

`5|V| <= 3(|V|+s)`,

hence

`|V| <= floor(3s/2)`.

Thus for fixed `s`, the entire witness contains only a constant number of variables. Eliminating all variables in `V` by exact Davis-Putnam in a fixed order therefore has polynomial charged work for that fixed `s`. With the crude recurrence

`M_{i+1}<=2M_i^2`,

after `k<=floor(3s/2)` eliminations,

`M_k<=2^(2^k-1)m^(2^k)`.

This is polynomial for fixed `s`, with an exponent depending on `s`.

## Correct claim ceiling

The theorem supplies a **structural fixed-surplus batch bound**. It does not identify unbounded surplus as the unique remaining frontier and it does not improve the generic fact that one current-state DP elimination is polynomial.

In particular:

`ONE_CURRENT_POLY_DP_STEP != POLYNOMIAL_TOTAL_TRAJECTORY`

`FIXED_s_BATCH_POLYNOMIAL != UNIFORM_P_FOR_UNBOUNDED_s`

`VARIABLE_COUNT_DESCENT != POLYNOMIAL_LIVE_STATE_OVER_THE_WHOLE_RUN`.

The live frontier therefore remains the later R44BC/R44BD maximum-deficiency branch-compression problem, not an `UNBOUNDED_SURPLUS` claim inferred from R44BB.

Scientific status:

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
