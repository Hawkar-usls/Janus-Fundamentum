# JANUS TRUMP R50G24 — pairwise counterpolarity closure replay

## Why this gate exists

R50G23 isolated the exact collapse history of the 30 frozen R50G22 clean skeletons under same-pivot R47J (pivot 1). A first bounded R50G24 probe, executed by the GitHub-native JANUS habitat lane, then tested 2,154 single-clause counterpolarity mutations. Some mutations changed the first collapse transition, but none produced a strong nonempty bipolar stalled residual core.

The next minimum controlled debt was therefore not a third arbitrary complexity source. It was a **coordinated pair**: clause 1 must invalidate the original first local transition, and clause 2 must be derived from the direct-additive debt of the replacement transition exposed by clause 1.

This R50G24 gate independently replays that pairwise experiment inside `Janus-Fundamentum`. The JANUS habitat result is treated only as a sealed expected transcript. If this implementation does not reproduce it exactly, the gate fails.

## Frozen mutation grammar

For each of the exact same 30 R50G22/R50G23 skeletons:

1. Keep R47J pivot fixed at `1`.
2. Add no new variables.
3. Generate a binary clause `C1` from the R50G23 direct-additive debt of the original first R33 transition.
4. Require `C1` to actually change that first transition.
5. Inspect the new first transition after `C1` and derive its own direct-additive debt.
6. Generate a second binary clause `C2` from that replacement debt.
7. Replay the two-clause source through the same R47J candidate and independent macro replay.
8. Inspect the first R33 pass after DP.

A strong candidate requires all of the following simultaneously:

- the same-pivot R47J candidate still exists;
- independent R47J replay passes;
- R33 stops at `STALLED_STACK_LEAN_CORE`;
- the residual CNF is nonempty;
- every residual variable still occurs in both polarities.

Changing the first rule is **not** success by itself.

## Sealed pairwise result to replay

The GitHub-native JANUS lane reported:

- frozen skeletons: `30`;
- candidate first clauses: `360`;
- first-transition breaks: `122`;
- replacement states with direct additive debt: `122`;
- coordinated binary+binary pair trials: `1774`;
- R47J replay failures: `0`;
- strong nonempty bipolar residuals: `0`.

After clause 1, the replacement first transition partition was:

- `BLOCKED_CLAUSE_ELIMINATION`: `88`;
- `BOUNDED_VARIABLE_ELIMINATION`: `34`.

Across all 1,774 complete pairs, the first rule of the final R33 cascade was:

- `BLOCKED_CLAUSE_ELIMINATION`: `887`;
- `BOUNDED_VARIABLE_ELIMINATION`: `786`;
- `PURE_LITERAL_AUTARKY`: `94`;
- `UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE`: `7`.

Thus BCE or BVE is first in `1673 / 1774` pair outcomes, over 94% of this exact bounded replay space.

## Interpretation

The important result is not merely another finite negative. It exposes a **replacement cycle**.

A counterpolarity clause can invalidate a BCE transition only to reveal BVE. A pivot-touching second clause can then invalidate or move that BVE, but the resulting state frequently re-opens BCE. In the complementary direction, an intervention against BVE often leaves or restores a blocked-clause door. The near misses therefore behave less like isolated simplification rules and more like a coupled local escape network:

`BCE <-> BVE -> {SUBSUMPTION, PURE, EMPTY}`

This is still an empirical structural description of the frozen bounded replay. It is not a theorem that all DIRECT5 states possess such a cycle.

## Next debt-front

If and only if the independent replay reproduces the sealed transcript exactly, the next gate is:

`R50G25_BCE_BVE_REPLACEMENT_CYCLE_STRUCTURAL_DEBT`

R50G25 must **not** expand the source family and must **not** simply permit a third arbitrary clause. It should first characterize the minimum joint condition under which both doors are simultaneously closed at the same post-DP state:

- no blocked clause remains available to R33;
- no accepted bounded-variable-elimination step remains available to R33;
- the state remains nonempty and bipolar;
- no unit/tautology/subsumption/pure-literal transition has merely become the new immediate escape.

Only after this joint structural debt is characterized should a construction search be allowed.

## Epistemic firewall

This gate may establish an exact finite replay and a local next debt-front. It may not conclude that every pairwise mutation fails, that all DIRECT5 instances collapse, that `U_mu` is closed, that SAT is in P, or that P=NP.
