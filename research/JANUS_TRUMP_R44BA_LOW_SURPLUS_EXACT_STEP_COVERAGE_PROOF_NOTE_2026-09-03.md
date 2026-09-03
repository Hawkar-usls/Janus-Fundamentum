# JANUS TRUMP R44BA — low-surplus exact one-step coverage

Let `F` be a nonempty Boolean CNF of maximum clause width at most 3. Write `sigma(F)` for surplus, `mu_vd(F)` for minimum variable degree, and `nM(k)` for the non-Mersenne sequence. We prove:

> If `sigma(F) <= 2`, then one deterministic polynomial-time satisfiability-preserving transition exists that strictly decreases `n(F)+c(F)`.

This is deliberately a **one-step** theorem. Exact Davis-Putnam elimination of a width-3 formula may create width-4 clauses, so no invariant-closed iteration theorem is inferred.

## Case sigma <= 0

A nonempty clause-set is matching-lean iff its surplus is at least 1. Hence `sigma(F)<=0` yields a nontrivial matching autarky. Matching-autarky reduction is polynomial-time computable. Applying a nontrivial autarky deletes at least one touched-and-satisfied clause and does not add variables or clauses, so `n+c` strictly decreases.

## Case sigma in {1,2}: surplus/min-degree violation

Assume

`mu_vd(F) > nM(sigma(F))`.

R44AO proves constructively for Boolean width<=3 clause-sets that the Kullmann-Zhao critical set can be found and its MLCR satisfying assignment can be constructed in polynomial time, yielding a nontrivial autarky of `F`. Again at least one clause is deleted, so `n+c` strictly decreases.

## Case sigma=1 and no violation

Now `mu_vd(F) <= nM(1)`. Since `nM` enumerates positive non-Mersenne integers, its initial values are `2,4,5,...`, hence `nM(1)=2`.

Choose a minimum-degree variable `v`; let `p` and `q` be its positive and negative occurrence counts. Then `p+q<=2`, so `p*q<=p+q`. Exact Davis-Putnam elimination removes `p+q` pivot clauses and creates at most `p*q` non-tautological resolvents. Thus clause count does not increase while `v` is removed. Therefore `n+c` decreases by at least one.

## Case sigma=2 and no violation

Here `mu_vd(F) <= nM(2)=4`. Choose a minimum-degree variable `v` with `p+q<=4`. For fixed sum at most four the maximum product is attained at `(2,2)`, giving `p*q<=4`; direct inspection for sums below four gives `p*q<=p+q`. Hence R44AT's nonexpanding exact DP rule applies, again decreasing `n+c`.

## Consequence

No nonempty width<=3 state with `sigma<=2` can be a fixed point of the union of:

1. polynomial matching-autarky reduction,
2. the constructive width-3 critical-autarky transition from R44AO,
3. nonexpanding exact DP elimination from R44AT.

Thus any width<=3 state irreducible under all three rules must satisfy

`boxed(sigma(F) >= 3)`.

At `sigma=3`, `nM(3)=5`; the first degree-five polarity profiles not covered by `p*q<=p+q` are `(3,2)` and `(2,3)`, exactly matching the regular hard frontier isolated in R44AT/R44AU.

## Scope firewall

The theorem does **not** say that every formula initially satisfying `sigma<=2` is polynomial-time decidable by iterating this rule. A DP successor may leave maximum width three. Therefore:

`LOW_SURPLUS_ONE_STEP_COVERAGE != LOW_SURPLUS_POLYNOMIAL_DECIDER`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
