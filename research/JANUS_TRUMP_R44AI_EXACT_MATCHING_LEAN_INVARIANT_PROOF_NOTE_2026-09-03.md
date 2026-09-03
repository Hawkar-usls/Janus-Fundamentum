# JANUS TRUMP R44AI — Exact matching-lean invariant and universal-progress obstruction

## Candidate

Let `I_ML(F)` be the matching-lean kernel obtained by matching-autarky reduction. Autarky removal preserves satisfiability, and the matching-lean kernel is a canonical polynomial-time computable normal form in the matching-autarky system.

Thus `I_ML` is a legitimate exact polynomial preprocessing invariant.

## SAT obstruction family

Let

`G(x,y) = {(x OR y), (NOT x OR y), (x OR NOT y)}`.

It is satisfiable, e.g. by `x=y=true`. It has deficiency `delta(G)=3-2=1`. Every two-clause proper subset has the same two variables and deficiency `0`; every one-clause subset has deficiency `-1`; the empty subset has deficiency `0`. Hence every proper sub-clause-set has smaller deficiency. By the standard characterization of matching-lean clause-sets, `G` is matching-lean.

Let `S_k` be the disjoint union of `k` variable-disjoint copies of `G`. Then `delta(S_k)=k`. Any proper sub-clause-set contains at most `k-1` complete gadgets; each incomplete gadget contributes deficiency at most zero. Hence every proper sub-clause-set has deficiency at most `k-1`, so `S_k` is matching-lean. It is satisfiable componentwise.

Therefore `I_ML(S_k)=S_k` for arbitrarily large satisfiable formulas.

## UNSAT obstruction family

For `n>=1`, let

`U_n = {x1, (NOT x1 OR x2), ..., (NOT x_{n-1} OR xn), NOT xn}`.

The first unit forces `x1=true`, the implication chain forces every `xi=true`, and the final unit forces `xn=false`, so `U_n` is unsatisfiable.

It is minimally unsatisfiable: deleting either endpoint unit allows the obvious all-false/all-true completion; deleting implication `i` allows `x1,...,xi=true` and `x_{i+1},...,xn=false`. Thus every proper clause deletion restores satisfiability.

Every minimally unsatisfiable clause-set is lean and hence matching-lean. Therefore `I_ML(U_n)=U_n` for arbitrarily large unsatisfiable formulas.

## Conclusion

`I_ML` satisfies exactness and polynomial computability but fails universal strict progress on both SAT and UNSAT inputs.

Seals:

- `EXACT_REDUCTION != UNIVERSAL_PROGRESS`
- `POLYTIME_CANONICAL_KERNEL != POLYTIME_DECISION`
- `IRREDUCIBLE_UNDER_I != TERMINAL_SAT_OR_UNSAT`
- `NO_MATCHING_AUTARKY != SAT`
- `NO_MATCHING_AUTARKY != UNSAT`

Scientific status: `P_VS_NP=OPEN`.
