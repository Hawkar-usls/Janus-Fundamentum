# C025 — Akinator RSPC semantic-survival search barrier

Provider mirror of the canonical TOPA note:

`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_AKINATOR_RSPC_SEMANTIC_SURVIVAL_SEARCH_BARRIER.md`

Status: **PROVED_IN_GENERAL_CIRCUIT_SCOPE / RESTRICTED_SELECTOR_FRONTIER_OPEN**  
Claim ceiling: **P_VS_NP = OPEN**

## Core theorem

For a Boolean circuit/B2 DAG `C` and partial root assignment `rho`, define `SURVIVE(C,rho)` iff `C|rho` is nonconstant.

`SURVIVE` is NP-complete in the general circuit representation.

Membership: a certificate is two completions `alpha,beta` extending `rho` with `C(alpha) != C(beta)`; verification is polynomial.

Hardness: map a CNF `F(x)` to `C_F(z,x) := z AND F(x)` with empty `rho`. Then `F` is satisfiable iff `C_F` is nonconstant.

Therefore:

- `GENERAL_RESIDUAL_NONCONSTANCY = NP_COMPLETE`
- `GENERAL_RESIDUAL_CONSTANCY = coNP_COMPLETE`
- `CHEAP_SURVIVAL_WITNESS_VERIFICATION != CHEAP_SURVIVAL_WITNESS_DISCOVERY`

This does not prove hardness for the exact Sokolov source-matched restriction relation.

## Constructive escape language

Carry explicit `W0(g), W1(g)` witnesses with every represented function.

- root literal: trivial witnesses;
- NOT: swap witnesses;
- AND `e=a AND b`: accept without semantic search when retained `W1(a),W1(b)` agree on overlap; construct `W1(e)` by union.

All operand pairs in an explicit state of `V` literals/macros are enumerable in `O(V^2)`, so this accepted-step language is polynomial in the explicit state size.

## One-witness incompleteness

Let

`a(x,y)=x OR y`

`b(x,y)=x OR NOT y`.

Retained positive witnesses `(0,1)` for `a` and `(0,0)` for `b` conflict, yet `a AND b` is nonconstant because `x=1` satisfies both.

Thus:

`ONE_WITNESS_PER_VALUE != COMPLETE_COMPOSITIONAL_SURVIVAL`.

## New resource

Let `omega(g)` be the number of retained constructive positive witnesses for `g`, and `Omega(S)=max_g omega(g)` over the selector state.

Naive AND compatibility joins cost `O(omega(a) * omega(b) * support_check_cost)`.

No superpolynomial lower bound on `Omega` is claimed.

## Next gate

Prove or refute a source-matched selector language with:

1. polynomially enumerable candidate macros;
2. polynomially retained witness frontier in original input length `N`;
3. deterministic no-backtracking discovery;
4. universal local availability on target states;
5. exact source-restriction survival;
6. globally sound polynomially bounded progress potential.

If all six hold universally, the resulting deterministic polynomial selector decides SAT in polynomial time; that is a conditional bridge to `P=NP`, not a proof that the selector exists.

`PROOF_CARRYING_STRUCTURAL_SELECTOR = OPEN`  
`POLYNOMIAL_AKINATOR = OPEN`  
`P_VS_NP = OPEN`
