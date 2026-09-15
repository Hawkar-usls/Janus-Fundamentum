# TRUMP Bicameral Bucket Unique-Core Residual Single-Variable Separator — v1 Theorem Seal

## Scoped verdict

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1`

This seal is strictly scoped. It does **not** prove general SAT in P, P=NP, or general residual-separator tractability.

## Frozen lineage

- Parent state: `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.7.json`
- Frozen preregistration commit: `913cbe32145df5931f282fdd7403adc620f0e5d2`
- Frozen candidate commit: `86678c8d725d9355fe6638c8e02d88791a302baa`
- Independent checker commit: `deabafaf0861f796d19dc0ecf8a2ccaae42ddeb1`
- Frozen CI head: `11a3adaf62e365949302e2164327ce8285f6f168`
- Actions run/job: `34993184716 / 104462750297`

## Scoped theorem

Assume the v3.7 predecessor surface:

1. an exact unique common-core state has already been derived;
2. the target residual relation component is connected and contains at least three relations;
3. from raw residual scopes alone, a single Boolean residual variable `s` is deterministically discovered such that removing `s` disconnects the target residual relation-overlap graph;
4. no trusted separator hint is accepted;
5. exactly the two restrictions `s=0` and `s=1` are formed;
6. after exact restriction in each branch, the residual dependency graph is recomputed from the restricted raw factors;
7. every connected residual component in an admitted branch has size at most two, so only the already sealed v3.6 singleton and one-pair carriers are used.

Then the original scoped instance can be decided exactly without a three-or-more-factor join chain and without a global residual Cartesian product:

- if either exact branch admits and reconstructs an assignment that replays every original relation, the original instance is SAT;
- if both exact branches terminate in independently certified exact UNSAT, the original instance is UNSAT;
- otherwise the gate returns OPEN.

### Soundness

Every assignment of the original instance gives exactly one Boolean value to `s`, so it belongs to exactly one of the two restrictions. Conversely, a satisfying assignment reconstructed in either branch together with the frozen unique common-core state and `s=value` is replayed against all original relations before admission. Hence branch SAT implies original SAT, and original SAT must survive one branch. Exact UNSAT is promoted only when both exhaustive Boolean branches have exact UNSAT certificates.

### Resource discipline

The separator has domain size two, so the gate forms exactly two restrictions. Restriction scans explicit tuple rows. Branch componentization is polynomial in residual scope incidence size. Each admitted branch invokes only sealed size-1/size-2 residual carriers and the existing guarded exact handoff. No 3+ natural-join chain is materialized, no global residual Cartesian product is enumerated, no L² budget is raised, and no alternative separator/order search is used.

## Machine receipt

The frozen v3.7 forensic target is explained by separator variable `47`.

Positive control:
- separator: `47`
- branch statuses: `ADMIT_EXACT_SEPARATOR_BRANCH_SAT`, `ADMIT_EXACT_SEPARATOR_BRANCH_SAT`
- terminal: `ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD`
- original witness replay: PASS

One-branch UNSAT control:
- branch statuses: `EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION`, `ADMIT_EXACT_SEPARATOR_BRANCH_SAT`
- terminal: SAT admission

Both-branches UNSAT control:
- both branches: `EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION`
- terminal: `EXACT_UNSAT_BY_BOTH_SEPARATOR_BRANCHES`

Fail-closed controls:
- no admissible single-variable articulation: `OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR`
- branch still contains residual component >2: `OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR`
- injected hint: `REJECT_RAW_INPUT`
- tampered provenance: `REJECT_TAMPERED_PROVENANCE`

Independent checker uses BFS componentization and full original-relation witness replay; it does not use candidate separator helpers. All checks and regressions passed in Actions run `34993184716`.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_PARTIAL_OVERLAP_FACTORIZATION = NOT_PROVED`
- `GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
