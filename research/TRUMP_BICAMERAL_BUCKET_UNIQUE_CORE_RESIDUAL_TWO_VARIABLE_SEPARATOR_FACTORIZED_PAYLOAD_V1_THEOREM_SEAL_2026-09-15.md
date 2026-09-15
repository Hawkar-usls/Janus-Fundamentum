# TRUMP Bicameral Bucket Unique-Core Residual Two-Variable Separator — v1 Theorem Seal

## Scoped verdict

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1`

This seal is strictly scoped. It does **not** prove general SAT in P, P=NP, general residual-separator tractability, or that arbitrary connected mixed cores are solved.

## Frozen lineage

- Parent continuity: `registry/TRUMP_CURRENT_STATE_2026-09-15_v3.9.json`
- Parent blob: `9d0c49695b2201d05ba00f13c65d55ac848ba3fc`
- Preregistration commit: `94ca81ba0e5da9c2f44097170b2d4d51c4e9200d`
- Preregistration blob: `08579c4bcfecce6d006c2a3b1d53cc78e333ce70`
- Candidate commit: `f849115af7602ba6f4d7c3b289a2daa75354f22d`
- Candidate blob: `0853ebb9a3e273fdaeca172dbe2502cc7214cf61`
- Independent checker commit: `af0909dcc1824ef40832958c35059a39f272bb7c`
- Independent checker blob: `991dee8ee14ba139095570bc2a2c827cdc7aae11`
- Frozen CI head: `d85e46beb564ca55f69af5ea0df3f8b0adf97746`
- Actions run/job: `34997650364 / 104477846188`

## Scoped theorem

Assume the frozen v3.9 unique-common-core residual surface, complete target coverage, and a residual relation component not admitted by the sealed single-variable separator gate. Enumerate unordered pairs of raw residual variables in deterministic lexicographic order. A pair `{a,b}` is structurally admissible only if each of the four exact Boolean restrictions `(a,b) in {00,01,10,11}` either:

1. is exact UNSAT because an explicit relation becomes empty, or
2. after restriction and recomputation, every residual relation-overlap component has size at most two and is therefore handled only by the already sealed v3.6 singleton/one-pair carriers and exact guarded handoff.

If the lexicographically first admissible pair exists, then exactly four branches are exhaustive. A branch may authorize SAT only after reconstruction and full replay against every original relation. The original instance is SAT iff at least one branch provides such an exact witness. The original instance is exact UNSAT only if all four branches independently terminate exact UNSAT. Otherwise the gate returns OPEN.

### Soundness

Every Boolean assignment to the original instance has exactly one value pair for `{a,b}`, hence belongs to exactly one of the four restrictions. Restriction is performed by explicit tuple filtering only. Therefore no satisfying assignment is lost except when it violates the selected pair assignment, and the union of four branches covers all assignments. Reconstructed SAT witnesses are checked against all original relations. UNSAT promotion requires all four exhaustive branches to be exact UNSAT.

### Resource discipline

Pair discovery scans all unordered raw residual variable pairs: `O(V^2)` structural candidates. Only the selected pair is branched, and exactly four Boolean assignments are materialized. No separator set of size three or larger is enumerated. Leaf reasoning uses only sealed residual component-size-`<=2` carriers. The frozen receipt reports zero three-plus join chains, zero global residual Cartesian products, no budget raise, and no alternative elimination-order search.

## Machine receipt

Positive v3.9 no-articulation triangle:
- selected pair: `[47,48]`
- four branch statuses: all `ADMIT_EXACT_PAIR_SEPARATOR_BRANCH_SAT`
- terminal: `ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD`
- full original witness replay: PASS

Leaf-extended frozen control:
- selected pair: `[47,48]`
- all four branches SAT and exactly replayed

One-surviving-assignment control:
- branch statuses: three `EXACT_UNSAT_BY_EMPTY_PAIR_RESTRICTION`, one `ADMIT_EXACT_PAIR_SEPARATOR_BRANCH_SAT`
- terminal: SAT admission

All-four-UNSAT control:
- all four branches: `EXACT_UNSAT_BY_EMPTY_PAIR_RESTRICTION`
- terminal: `EXACT_UNSAT_BY_ALL_PAIR_SEPARATOR_BRANCHES`

Fail-closed controls:
- K4 distinct-edge-variable residual: `OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR`
- independent checker agrees on K4 OPEN
- injected pair hint: `REJECT_RAW_INPUT`
- tampered pair/provenance: `REJECT_TAMPERED_PROVENANCE`

Independent checker uses a separate unordered-pair scan, BFS componentization, does not call candidate pair-discovery helpers, and verifies SAT by full original-relation replay.

## Regressions

The same frozen CI run preserved:
- v3.8 single-variable separator PASS
- v3.6 residual-component-`<=2` PASS
- v3.5 conditioned payload PASS
- guarded bounded-output elimination PASS
- Schaefer mixed-carrier barrier PASS

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY = NOT_PROVED`
- `GENERAL_PARTIAL_OVERLAP_FACTORIZATION = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE_PENDING_HQ_REVIEW`
