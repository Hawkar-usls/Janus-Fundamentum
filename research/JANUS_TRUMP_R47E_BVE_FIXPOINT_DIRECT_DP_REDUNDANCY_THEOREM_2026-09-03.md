# JANUS TRUMP R47E — BVE fixpoint implies direct-DP redundancy

Status: **symbolic theorem about the frozen implementation**. Universal macro coverage remains OPEN.

## Statement

Let `F` be a canonical residual state for which the frozen R42 subsumption-aware BVE scan returns no candidate:

`best_sa_bve_candidate(F).candidate = None`.

Then for every bipolar variable `v` in `F`, the frozen exact-DP transformation used by R45A before normalization does **not** have strict CLV descent:

`CLV(DP_subsumed(F,v)) >=_lex CLV(F)`.

Equivalently, a direct-DP early producer whose only acceptance rule is immediate terminal/strict-CLV descent cannot select any pivot at a genuine R42 BVE fixpoint.

## Proof from frozen code identity

R42 defines `sa_bve_candidate_for_var(F,v)` by:

1. `all_dp_resolvents(F,v)`;
2. remove every parent clause containing `v` or `-v` to form the unaffected base;
3. canonicalize `base + all non-tautological resolvents`;
4. call `subsumption_minimize`;
5. compute frozen `CLV` before and after;
6. return a candidate **iff** `CLV(after) < CLV(before)`.

R45A `exact_dp_record(F,v)` uses the same R42 `all_dp_resolvents`, the same unaffected base construction, and the same R42 `subsumption_minimize` to obtain its forced post-DP formula before R33 normalization.

Therefore the direct post-DP formula tested by R45A is exactly the formula whose strict CLV descent would cause R42 `sa_bve_candidate_for_var` to exist.

R42 `best_sa_bve_candidate(F)` scans every current variable. If it returns `None`, no bipolar pivot passed that strict-descending direct-DP test. Hence every bipolar pivot has non-descending immediate post-DP CLV.

QED.

## Algorithmic consequence

At a residual state already certified as an R42 BVE fixpoint, the following stage is redundant:

`FIRST_DIRECT_DP_DESCENT`

because it is guaranteed to return no selection.

The minimal genuinely new residual mechanism begins only after allowing a bounded non-descending DP transformation and applying downstream normalization:

`BVE_FIXPOINT -> exact DP (temporary ascent/non-descent allowed) -> R33 -> affine/RUP -> terminal or strict final CLV descent`.

Thus the theorem-critical residual question is not

`does some pivot have direct DP descent?`

but

`does some pivot have certified descent after the frozen normalization of its bounded DP ascent?`

This is precisely the Universal Macro Lemma frontier.

## Production grammar cleanup

For true residual fixpoints, prefer:

`R33 -> affine -> RUP -> SA-BVE -> [if fixpoint] FIRST NORMALIZED DP MACRO -> fallback/OPEN`

and do not spend a second scan rediscovering direct-DP descent immediately after SA-BVE has proved none exists.

## Firewalls

- `DIRECT_DP_DESCENT_AT_BVE_FIXPOINT = IMPOSSIBLE_BY_FROZEN_DEFINITION`
- `NORMALIZED_DP_MACRO_UNIVERSAL_COVERAGE = NOT_PROVED`
- `R47A_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_EQ_NP = NOT_PROVED`
- `P_NE_NP = NOT_PROVED`
- `P_VS_NP = OPEN`
- `TRUMP_finished = false`
