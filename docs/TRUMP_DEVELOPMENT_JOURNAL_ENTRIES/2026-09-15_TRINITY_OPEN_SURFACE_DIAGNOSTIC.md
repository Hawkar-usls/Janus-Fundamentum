# 2026-09-15 — APMA Trinity OPEN-surface diagnostic

Authority: `FINITE_DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION`

GitHub-only diagnostic run `34905726704` evaluated two frozen OPEN surfaces of the recovered APMA Trinity Sovereign selector.

## Cycle surface

Frozen incidence topology: `[(1,3,4),(1,2,5),(2,3)]`.
All 256 sign orientations were evaluated exactly by the current Trinity implementation.

Observed decisions:
- `COMMIT_SAT`: 128
- `OPEN_UNKNOWN_STATE_CLASS`: 128

Every OPEN orientation had the same structural diagnostic:
- typed-module route: `OPEN_MODULE_CYCLE`
- factor route: `OPEN_FACTOR_GRAPH_CYCLE`

This is finite diagnostic evidence only. It proves no asymptotic statement. It identifies an exact uncovered structural regime in the current selector.

## Width surface

Frozen wide-center-tree controls:
- k=2: COMMIT_SAT, boundary 2, budget 4
- k=3: COMMIT_SAT, boundary 3, budget 5
- k=4: COMMIT_SAT, boundary 4, budget 5
- k=6: COMMIT_SAT, boundary 6, budget 6
- k=8: OPEN_INTERFACE_WIDTH, budget 6
- k=12: OPEN_INTERFACE_WIDTH, budget 7
- k=16: OPEN_INTERFACE_WIDTH, budget 7
- k=24: OPEN_INTERFACE_WIDTH, budget 8

Again, no trend or asymptotic inference is authorized from these finite cases.

## Exact diagnosis

The current implementation is replayable after restoration of the historical compositional-synthesis predecessor. The remaining observed algorithmic gaps are not runtime failures:

1. `CYCLE_COMPOSITION_EXACT_TRANSFER_DOOR_MISSING`
2. `WIDER_INTERFACE_EXACT_POLYNOMIAL_REPRESENTATION_MISSING`

Recommended next formal target:
`CYCLE_COMPOSITION_EXACT_TRANSFER_PROOF_OR_FALSIFICATION`

Reason: the frozen triangle-cycle topology isolates a small pure cycle obstruction without conflating it with increasing interface width.

Scientific firewall remains unchanged:
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
- scientific promotion: `NONE`
