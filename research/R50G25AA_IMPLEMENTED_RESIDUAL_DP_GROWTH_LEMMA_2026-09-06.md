# R50G25AA implemented residual exact-DP growth lemma

## Statement

For every formula `F` returned as `RESIDUAL` by the frozen W/Y policy implementation, and for every variable `x` remaining in `F`:

1. `x` occurs in both polarities in `F`, hence `exact_dp_record(F,x)` exists;
2. exact DP removes `x`, so the post-DP variable count is strictly smaller;
3. no exact-DP pivot has lexicographically strict CLV descent under `(C,L,V)`;
4. therefore every exact-DP pivot on a W residual is classified `GROWTH` by the implemented Y relation.

This is a statement about the current implemented definitions, not a theorem about arbitrary SAT preprocessors or all possible TRUMP successors.

## Derivation from code

### A. R33 stall excludes pure variables

`r33.simplify` checks, in order, tautology deletion, unit propagation, `pure_literals`, subsumption, blocked-clause elimination, and bounded variable elimination before it may return `STALLED_STACK_LEAN_CORE`.

If any remaining variable occurred in only one polarity, `pure_literals(active)` would be nonempty and `PURE_LITERAL_AUTARKY` would fire instead of stalling. Therefore every variable in an R33 stalled core occurs positively and negatively.

### B. W residual excludes every strict-descent SA-BVE pivot

After R33 stalls and affine recognition and first certified RUP strengthening both fail, W calls `best_sa_bve_candidate(after_r33)`. The SA-BVE candidate constructor is exact DP followed by strict-subsumption normalization and returns a candidate precisely when the transformed CLV is lexicographically smaller than the current CLV.

W returns `RESIDUAL / NO_RUP_NO_SA_BVE` only when this candidate is `None`. Therefore no remaining variable has an exact-DP+NF transform with strict CLV descent.

### C. Equality is impossible for exact DP

For every remaining variable `x`, both polarities exist, so exact DP is defined. Independent replay requires `x` to be absent from the transformed state. Thus `V_after < V_before`.

If `(C_after,L_after)=(C_before,L_before)`, then the full CLV tuple would already be lexicographically smaller because `V_after<V_before`. Therefore `EQUAL_MEASURE` cannot occur on a valid exact-DP pivot here.

Combined with B, every exact-DP pivot must satisfy `CLV_after > CLV_before` lexicographically, i.e. Y labels it `GROWTH`.

## Consequence

The controlled-DP fallback is not merely occasionally allowed to grow. **Growth is structurally mandatory at every W residual under the current policy.** The live completeness/complexity obligation is therefore not to find a descending exact-DP pivot; none exists by construction. It is to prove that after a bounded amount of mandatory fill-in, the restarted hybrid stack opens a reducing/terminal door before the inherited polynomial root budget is exhausted.

This sharpens the next universal target to an amortized/hybrid escape invariant, for example a potential of the form

`Phi = remaining_variables + certified_fill_in_debt + hybrid_escape_credit`

or an equivalent structural bound linking residual parent incidence (`p*q`, `SP`, `SN`) to guaranteed subsequent R33/RUP/SA-BVE/affine progress.

## Firewall

- `P_VS_NP = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `TRUMP_finished = false`
- implemented-definition lemma != universal polynomial SAT theorem
- mandatory local DP growth makes the Galil-style fill-in guard more, not less, relevant
