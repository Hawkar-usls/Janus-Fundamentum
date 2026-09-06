# R50G25AC — Local min-UB safe-envelope lemma

## Status

Paper proof from the implemented AB upper-bound definitions, plus an executable audit against the sealed AB artifact. This is **not proof-assistant formalized** and is **not a universal SAT-in-P theorem**.

## Definitions

For a canonical W-policy residual formula `F`, write:

- `C` = clause count,
- `L` = literal count,
- `V` = remaining variable count,
- `S = C + L`.

For a remaining variable `x`, let:

- `p = p_x` = number of clauses containing `+x`,
- `q = q_x` = number of clauses containing `-x`,
- `SP = SP_x` = sum of clause lengths over `+x` parents,
- `SN = SN_x` = sum of clause lengths over `-x` parents,
- `d = p + q`.

The frozen AB analytic formulas are

`UB_C = C - p - q + p*q`

and

`UB_L = L - SP - SN + q*(SP-p) + p*(SN-q)`.

Therefore, by direct algebra,

`UB_S = UB_C + UB_L`

`= S - d - (SP+SN) + q*SP + p*SN - p*q`.

## Lemma

For every canonical W-policy residual with `V >= 1`, there exists a remaining variable `x` such that

`UB_S(x) <= G(S,V)`

where

`G(S,V) = S + (2V-1) * S^2 / (4V^2)`.

### Proof

Choose a remaining variable `x` of minimum occurrence degree `d_x`. Since each literal occurrence belongs to exactly one remaining variable,

`sum_x d_x = L`,

so

`d_x <= L/V <= S/V`.

A W residual has no live PURE door, hence each remaining variable occurs in both polarities and exact DP on `x` is defined.

Every canonical clause over the `V` remaining variables has width at most `V`. Hence

`SP <= pV` and `SN <= qV`.

Starting with the exact AB identity,

`UB_S = S - d - (SP+SN) + q*SP + p*SN - p*q`

and discarding the non-positive terms `-d-(SP+SN)` gives

`UB_S <= S + q*SP + p*SN - p*q`.

Using `SP <= pV` and `SN <= qV`,

`UB_S <= S + (2V-1)pq`.

By AM-GM,

`pq <= (p+q)^2/4 = d^2/4`.

Therefore

`UB_S <= S + (2V-1)d^2/4`

`<= S + (2V-1)S^2/(4V^2)`.

This proves the claim.

## Safe-envelope corollary

Let the inherited controlled-growth root budget be

`B = (C0+L0)(V0+1)^2`.

If at a W residual

`G(S,V) <= B`,

then at least one remaining variable has analytic `UB_S <= B`. Since the exact canonical DP result is no larger than its sound analytic upper bound, at least one within-budget exact-DP fallback exists.

Equivalently, the sufficient scalar envelope is

`S <= 2V^2/(2V-1) * (sqrt(1 + (2V-1)B/V^2) - 1)`.

## What this closes

It removes the need to *assume* a good pivot exists whenever the residual lies inside the stronger safe envelope. Existence follows from averaging and the implemented analytic bound.

## What remains open

The inherited invariant `S <= B` alone is weaker than `G(S,V) <= B`. AC therefore does **not** prove that every root-reachable residual stays in the safe envelope. That is the next global reachability obligation.

Nor does AC prove polynomial runtime by itself. The global scheduler must additionally keep all root-reachable residuals inside the envelope and retain polynomial accounting for W-policy replay, one exact-DP materialization, certificate replay, and reconstruction.

## Theory guard

Classical Davis–Putnam variable elimination has exponential lower-bound families for every elimination order (Z. Galil, *Theoretical Computer Science* 4(1), 1977, DOI: 10.1016/0304-3975(77)90054-8). Therefore variable-count descent alone cannot justify polynomiality. The only admissible route here is to prove additional hybrid-scheduler structure that prevents such fill-in on the reachable domain.

## Firewall

- `P_VS_NP = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `TRUMP_finished = false`
- local safe-envelope lemma != global completeness
- finite AB artifact audit != universal coverage
