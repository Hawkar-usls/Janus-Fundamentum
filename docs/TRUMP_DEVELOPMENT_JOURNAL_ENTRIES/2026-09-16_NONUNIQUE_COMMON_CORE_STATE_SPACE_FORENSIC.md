# 2026-09-16 — Nonunique common-core state-space forensic

Authority: `DIAGNOSTIC_ONLY__NO_NEW_MULTI_STATE_CARRIER_AUTHORITY`

## Question

After the v3.19 raw-GT2 census found no remaining unadmitted frozen raw GT2 obstruction, the next scoped question was whether `OPEN_NONUNIQUE_COMMON_CORE_SUPPORT` is actually reached by any existing source-authorized raw predecessor fixture, and whether a large common-core width itself creates an exponential state-space obligation.

The gate was frozen as:

`TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC`

No new multi-state solver, separator, recursion rule, join chain, global Cartesian product, or budget raise was licensed.

## Frozen-before-implementation observation

For explicit relation tables, the actual common-core support is

`S = intersection_i pi_C(F_i)`.

Because every projected state comes from an explicitly stored row,

`|S| <= min_i |pi_C(F_i)| <= min_i |F_i| <= L_explicit_rows`.

Thus enumerating all `2^|C|` Boolean assignments is not required merely to recover the *actual explicit support*. This is a representation-level bound only; it is not a general multi-state solving theorem.

## Raw reachability census

The candidate and independent checker reconstructed and SHA-deduplicated the frozen/reproducibly generated predecessor fixtures from v3.4 through v3.16.

Machine receipt:

- unique authoritative raw fixtures: `8`
- authoritative raw fixtures with exact common-core support size `>1`: `0`
- first real nonunique fixture: `null`
- every READY authoritative fixture had exact common-core support size `1`
- support-bound lemma verified independently on every READY authoritative fixture
- synthetic v3.5 multiple-core control has exact support size `2`, but is explicitly calibration-only and excluded from raw reachability authority
- Phase B per-state replay was therefore not activated on an authoritative real nonunique fixture

Verdict:

`PASS_DIAGNOSTIC_NO_AUTHORITATIVE_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FOUND`

## Immutable first implementation failure

The first workflow run is preserved:

- Actions run: `35042004343`
- job: `104623675436`
- head: `c4d5bda574ce9ee8163aac45ea77269de3a9b26a`

The candidate completed successfully and the independent calculation agreed with the candidate, but the prereg assertion step failed because the v1 independent checker stored the correct factual field

`candidate_helpers_imported = false`

inside a dictionary later passed to `all(checks.values())`. The correct `false` fact therefore self-failed the checker verdict.

This was an implementation Boolean-polarity error, not a scientific discrepancy. The v1 checker remains byte-frozen at blob:

`79c51eaa784b538a3184cdbe1c2bc4c72a5823f8`.

## Successor checker repair

A v1.1 wrapper changed only the polarity of that governance assertion to the positive invariant `candidate_helpers_not_imported = true`, bound itself to the frozen v1 blob, and recorded the immutable failed run/job. Candidate code, preregistration, fixture census, and scientific outcome were unchanged.

Repair commit / scientific head before result writeback:

`c34752b2e01f612c341e95b0711363fb386545cb`

Repaired Actions:

- run: `35042487552`
- job: `104625131347`
- conclusion: `SUCCESS`

All substantive stages passed:

- candidate forensic
- independent checker v1.1
- preregistered invariants
- v3.19 raw GT2 census regression
- v3.18 exact two-factor carrier regression
- v3.5 unique-core predecessor regression
- authority firewall notice

## Interpretation

This diagnostic closes two narrower questions only:

1. Within the current frozen/reproducibly generated predecessor evidence set, there is no authoritative raw instance demonstrating `|S|>1` at this gate.
2. In explicit-table semantics, the cardinality of the actual common-core support is bounded by explicit input rows; raw core width alone does not license a `2^|C|` state-space claim.

It does **not** close `NONUNIQUE_COMMON_CORE_SUPPORT` in general, because there is no authoritative real nonunique predecessor fixture on which to demonstrate exact multi-state routing/reconstruction and total replay cost. The synthetic v3.5 control must not be promoted into raw-reachability evidence.

Captain rule: do not invent the next blocker from synthetic controls. Either acquire a source-authorized raw predecessor with exact support size greater than one, or move the scoped frontier to the next genuinely evidenced open predecessor surface under a separate preregistration.

Global firewalls remain unchanged: `P_VS_NP = OPEN`, `GENERAL_SAT_IN_P = NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED = NO`, and the global APMA frontier is not advanced by this diagnostic.
