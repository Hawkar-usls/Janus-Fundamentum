# JANUS TRUMP R44BB — fixed-surplus exact one-step theorem

Let `F` be a normalized Boolean CNF of maximum clause width at most 3, and let

`σ(F)=s>=1`

for a fixed constant `s`.

We prove that `F` always admits one deterministic polynomial-time satisfiability-preserving transition that removes at least one variable.

## Case A — a nonexpanding DP variable exists

For a variable `v`, let `p(v)` and `q(v)` be its positive and negative occurrence counts.

If

`p(v) q(v) <= p(v)+q(v)`,

ordinary Davis-Putnam elimination deletes the `p+q` pivot clauses and adds at most `pq` non-tautological resolvents. Hence the clause count does not increase and one variable disappears. This is the R44AT transition.

## Case B — no nonexpanding DP variable exists

Assume instead

`p(v) q(v) > p(v)+q(v)`

for every variable `v`.

For total degree `d=p+q<=4`,

`pq <= floor(d^2/4) <= d`,

contradicting the strict inequality. Therefore every variable has degree at least 5.

Compute a nonempty surplus witness `V` with

`|Γ(V)|-|V|=s`.

The inherited surplus machinery used earlier in the R44AN/R44AO line computes `σ(F)` and such a witnessing variable set in polynomial time.

Every occurrence of a variable in `V` belongs to a clause in `Γ(V)`. Since every clause has width at most 3,

`sum_{v in V} d(v) <= 3|Γ(V)| = 3(|V|+s)`.

But every variable has degree at least 5, so

`5|V| <= 3(|V|+s)`.

Thus

`2|V| <= 3s`

and therefore

`|V| <= floor(3s/2)`.

Because `s` is fixed, the witness contains only a constant number of variables.

Now eliminate every variable of `V` by exact Davis-Putnam elimination in a fixed order. If `M_i` is the clause count before the `(i+1)`-st elimination, a crude universal bound is

`M_{i+1} <= M_i + M_i^2 <= 2 M_i^2`.

After `k=|V|<=floor(3s/2)` steps,

`M_k <= 2^(2^k-1) m^(2^k)`.

For fixed `s`, `k` and `2^k` are constants. Hence total live state and charged work are polynomial in the original input size.

Each Davis-Putnam step is exact existential projection, so satisfiability is preserved throughout, and at least one variable is removed.

## Consequence

For every fixed constant `s>=1`, no nonempty width-3 CNF with `σ(F)=s` is a fixed point against exact polynomial one-step progress.

In particular, for `s=3`, if no R44AT variable exists then a surplus witness has at most

`floor(9/2)=4`

variables and can be eliminated with fixed polynomial overhead.

## Boundary

This theorem is deliberately not promoted to a complete SAT algorithm.

1. The polynomial exponent depends on `s`.
2. If `s` grows with the input, the bound is not a uniform polynomial bound.
3. Davis-Putnam elimination can create clauses wider than 3, so the theorem is not automatically closed under iteration.

Therefore:

`FIXED_SURPLUS_POLYNOMIAL != UNIFORM_POLYNOMIAL_IN_UNBOUNDED_SURPLUS`

and

`ONE_STEP_EXACT_PROGRESS != CLOSED_POLYNOMIAL_TRAJECTORY`.

Scientific status remains:

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
