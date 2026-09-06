# R50G25AA diagnostic: amortized potentials on sealed Z traces

Source artifact: R50G25Z run `34045971286`, artifact `9993361591`, SHA256 `b0f035f994a0b739f1c6942aaf2160e921782bb1afc1f4df183c1bc4f1e6de78`.

This diagnostic is derived from the sealed Z `fallback_trace` records only; it does not alter AA's preregistered domain, policy, or verdict criteria. Arithmetic for the potential checks was recomputed with unbounded Python integers.

## Definitions

For consecutive fallback records inside one Z case:

- `S_res = C_res + L_res` at a W residual before controlled DP;
- `S_dp = C_dp + L_dp` immediately after the chosen exact-DP fallback;
- `S_next = C_next + L_next` at the next W residual after the restart stack;
- `DP_scalar_delta = S_dp - S_res`;
- `W_recovery = S_dp - S_next`;
- `net_cycle_delta = S_next - S_res`.

The final fallback of a case has no next residual if W terminates, so it is excluded from the inter-residual net-cycle count.

## Exact Z trace counts

- controlled-DP fallback steps in all 16 Z cases: `238`
- fallback steps with a following residual: `222`
- `net_cycle_delta > 0`: `168`
- `net_cycle_delta = 0`: `1`
- `net_cycle_delta < 0`: `53`

Observed scalar DP delta over the 222 inter-residual cycles:

- minimum: `+2`
- maximum: `+93`
- mean: `+33.61711711711712`

Observed W-restart scalar recovery:

- minimum: `0`
- maximum: `258`

Observed full-cycle net scalar delta:

- minimum: `-232`
- maximum: `+77`
- mean: `+12.563063063063064`

## Candidate 0: raw scalar repayment is falsified

The local invariant

`every residual -> DP -> W-restart cycle strictly decreases S=C+L`

is falsified on the sealed Z domain: 168/222 observed inter-residual cycles increase `S`.

Therefore a future universal proof cannot rely on immediate one-cycle repayment of exact-DP fill-in.

## Candidate 1: full-cycle cubic horizon potential survives Z

For every one of the 222 inter-residual transitions, the finite trace satisfies strict descent of

`Phi3(F) = (C(F)+L(F)) * (V(F)+1)^3`.

Exact finite count:

- strict descents: `222/222`
- non-descents: `0/222`.

This is a candidate invariant only. Z does not prove it for arbitrary residuals or future domains.

## Candidate 2: immediate-DP quartic horizon potential survives all Z fallbacks

For all 238 controlled-DP fallback steps, even before W-restart reductions are credited, the finite trace satisfies strict descent of

`Phi4(F) = (C(F)+L(F)) * (V(F)+1)^4`.

Exact finite count:

- strict descents: `238/238`
- non-descents: `0/238`.

The weaker immediate-DP cubic candidate is already falsified: 18/238 fallback steps are non-descending under `Phi3`. Thus the observed exponent-4 immediate potential is not being reported merely because every positive exponent works.

## Interpretation

The surviving finite potentials give concrete AB proof/falsification targets:

1. Try to derive a hybrid full-cycle inequality strong enough to imply `Phi3_next < Phi3_residual` from residual incidence (`p,q,SP,SN`) plus the certified W-restart rules.
2. Independently try to derive or falsify `Phi4_after_DP < Phi4_before_DP` for the deterministic minimum `(C_after,L_after,var)` controlled pivot.
3. Do not silently replace the frozen Z/AA budget `B=(C0+L0)(V0+1)^2` by a cubic or quartic budget. Even a universal `Phi3/Phi4` theorem would establish a different polynomial envelope and would require a separately preregistered successor gate.

A trivial termination potential conditional on the frozen scalar budget exists because every fallback eliminates at least one variable and `S<=B` is enforced, but that does not prove the missing statement that an admissible within-budget exact-DP door always exists.

## Firewall

- these are finite trace diagnostics, not universal lower or upper bounds;
- `CLV growth != scalar C+L growth` in general;
- `Phi3` and `Phi4` surviving Z do not prove the current quadratic root budget;
- `P_VS_NP = OPEN`;
- `SAT_IN_P = NOT_PROVED`;
- `TRUMP_finished = false`.
