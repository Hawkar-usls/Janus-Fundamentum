# JANUS TRUMP R50G25K — outer coverage preregistration, no family expansion

## Parent

R50G25J sealed structural result:

- exact-DP pivot-free extension confluence established from implemented definitions;
- frozen target quotient `1212 -> 1188 -> 1074`;
- no claim of arbitrary-CNF scheduler termination;
- `SAT_IN_P = NOT_PROVED`, `P_VS_NP = OPEN`.

## Purpose

This gate performs **no family expansion** and no new target generation. It freezes the claim and falsifier for the next algorithmic attack before looking at its result.

## Preregistered next claim

For an admissible post-DP target `T`, define its BCE/BVE incidence requirements exactly as in R50G25A/B. A candidate polynomial cover finder `P(T)` must return a finite set of pivot-free binary clauses satisfying every currently exposed BCE/BVE incidence requirement, or return an explicit uncovered requirement witness.

The first candidate to test is deliberately non-minimal:

1. enumerate the polynomial-size binary clause universe over variables of `T`;
2. enumerate all current BCE/BVE incidence requirements;
3. for each still-uncovered requirement, choose the lexicographically first binary clause that hits it;
4. add that clause, mark every requirement it hits as covered, and continue;
5. never solve exact minimum set cover and never branch over subsets.

This is a deterministic support-cover construction, not a minimum cover.

## Polynomial accounting preregistration

Let `V` be the number of variables, `C` the number of clauses, and `L` the literal count of target `T`.

The candidate finder is allowed to enumerate at most `O(V^2)` binary clauses. BCE candidate discovery and BVE candidate discovery must use the already explicit finite scans; requirement-to-clause incidence may be checked by a direct nested scan. The implementation must emit a meter ledger sufficient to bound the finder by an explicit polynomial in `C,L,V`.

Exact truth-table enumeration and the old `exact_minimum_cover` are permitted only as **validation oracles** on the frozen <=6-variable domain. They are forbidden from the candidate algorithm core.

## Frozen-domain test preregistration

Without adding new skeletons, replay the candidate polynomial cover finder on all 1212 frozen target states from R50G25J.

For each target:

- build `P(T)` without calling `exact_minimum_cover`;
- require pivot-free output;
- require every current BCE/BVE incidence requirement to be covered, otherwise emit an explicit obstruction;
- apply the structural J lemma to obtain `Q_P(T)=NF(T union P(T))`;
- run the micro-RUP scheduler from R50G25G/H on `Q_P(T)`;
- verify terminal semantics and SAT reconstruction using the frozen exact oracle only as validation.

## Preregistered outcomes

Exactly one of the following must be emitted:

1. `POLYNOMIAL_SUPPORT_COVER_1212_TERMINAL` — all 1212 frozen targets receive a polynomially constructed cover and the downstream micro scheduler terminates correctly;
2. `POLYNOMIAL_SUPPORT_COVER_EXPLICIT_REQUIREMENT_OBSTRUCTION` — the finder encounters at least one requirement with no admissible binary support clause;
3. `POLYNOMIAL_SUPPORT_COVER_SCHEDULER_COUNTEREXAMPLE` — the finder covers all current requirements but at least one resulting normalized state does not reach a verified terminal under the frozen micro scheduler;
4. `POLYNOMIAL_ACCOUNTING_VIOLATION` — implementation exceeds or cannot certify the preregistered polynomial meter envelope;
5. `IMPLEMENTATION_OR_REPLAY_FAILURE` — fail closed on any provenance/replay/certificate drift.

No outcome may be promoted to arbitrary 3CNF coverage from this frozen test alone.

## Critical distinction

`A polynomial cover of currently exposed BCE/BVE incidence debt` is **not** the same as `a polynomial SAT algorithm`.

Even if the candidate succeeds on all 1212 frozen targets, outer coverage remains open until we prove that arbitrary admissible targets enter the same machine and that repeated debt replacement / scheduler behavior is globally controlled.

## Next gate

`R50G25L_POLYNOMIAL_SUPPORT_COVER_FINDER_OR_EXPLICIT_OBSTRUCTION`

## Firewall

- no new source skeletons in K;
- exact minimum cover is not part of the next algorithm core;
- truth enumeration is validation only;
- finite 1212 success is not universal coverage;
- `SAT_IN_P = NOT_PROVED`;
- `P_VS_NP = OPEN`;
- `TRUMP_finished = false`.
