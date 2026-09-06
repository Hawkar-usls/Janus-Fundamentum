# R50G25AA diagnostic: one-cycle scalar repayment is falsified by sealed Z traces

Source artifact: R50G25Z run `34045971286`, artifact `9993361591`, SHA256 `b0f035f994a0b739f1c6942aaf2160e921782bb1afc1f4df183c1bc4f1e6de78`.

This diagnostic is derived from the sealed Z `fallback_trace` records only; it does not alter AA's preregistered domain, policy, or verdict criteria.

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

Observed scalar DP delta over those 222 inter-residual cycles:

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

## Consequence

The candidate local invariant

`every residual -> DP -> W-restart cycle strictly decreases S=C+L`

is falsified on the already sealed Z domain: 168/222 observed inter-residual cycles increase `S`.

Therefore a future universal proof cannot rely on immediate one-cycle repayment of exact-DP fill-in. A viable invariant must be genuinely amortized across multiple variable-elimination cycles, or use a different structural potential than raw `C+L`.

A trivial termination potential conditional on the frozen scalar budget exists because every fallback eliminates at least one variable and `S<=B` is enforced, but that does not prove the missing statement that an admissible within-budget exact-DP door always exists.

## Firewall

- this is a finite trace diagnostic, not a universal lower or upper bound;
- `CLV growth != scalar C+L growth` in general, even though all 222 observed inter-residual DP steps here had positive scalar delta;
- `P_VS_NP = OPEN`;
- `SAT_IN_P = NOT_PROVED`;
- `TRUMP_finished = false`.
