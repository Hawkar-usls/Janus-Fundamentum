# R47A Lemma 1 — Single-side occurrence forces exact-DP clause descent

Status: **SYMBOLIC SUFFICIENT CASE PROVED** (not universal coverage)

Let `F` be a canonical CNF with `C` clauses and let variable `v` occur in `p>=1` positive clauses and `n>=1` negative clauses. The frozen exact-DP macro removes all `p+n` clauses containing `v` or `-v`, keeps the remaining `C-p-n` base clauses, and generates at most one non-tautological resolvent for each positive/negative parent pair. Therefore the number `R` of generated non-tautological resolvents satisfies

`R <= p*n`.

Before subsumption/canonical duplicate removal, the DP pool therefore satisfies

`C_pool <= C - p - n + p*n`.

If `min(p,n)=1`, assume without loss of generality `p=1`. Then

`C_pool <= C - 1 - n + n = C - 1 < C`.

Canonicalization and subsumption can only remove clauses, so the transformed exact-DP formula also has strictly fewer clauses than `F`. Since the frozen TRUMP progress tuple compares clause count first, this is already a strict progress step before any downstream R33/affine/RUP normalization can be needed to establish descent.

Hence:

> For every canonical nonterminal formula `F`, if there exists a variable `v` occurring in both polarities with `min(p_v,n_v)=1`, exact DP on `v` is polynomially discoverable and yields strict clause-count descent.

## Discovery cost

Occurrence counts for all variables are obtainable by one pass over the literal encoding, i.e. `O(L)` in the current formula literal count. Choosing the first variable satisfying `p_v>0`, `n_v>0`, and `min(p_v,n_v)=1` therefore does not require a global macro scan.

## Representation bound for this case

For the selected variable, `p*n = max(p,n) <= C`. Thus the raw number of generated parent pairs and possible resolvents is at most linear in the current clause count. Each resolvent has length at most the sum of its two parent lengths minus two, so total generated literal mass is polynomial in the current encoding length.

## Consequence for R47A

The unresolved universal core can be narrowed to normalized states in which every variable appearing in both polarities satisfies

`p_v >= 2 AND n_v >= 2`.

This is only a sufficient structural case. It does **not** establish that every reachable nonterminal TRUMP state has such a variable, nor that all residual states have an accepted macro.

## Firewall

- `R47A_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
