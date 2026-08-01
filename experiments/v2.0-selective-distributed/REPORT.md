# JANUS P–N Junction v2.0 — Selective Distributed Field

**Status:** `PASS_DISTRIBUTED_LATENCY_GATE`  
**Holdout seed:** `440224`  
**Parameters:** frozen before holdout  
**SAT budget:** `28 × n` coordinator rounds  
**Test surface:** planted random 3-SAT near α≈4.26, planted 5-SAT near α≈6.1, guaranteed contradictory sign-core formulas

## What changed

v2.0 is a distributed controller rather than a replacement monolith:

- **GLADIUS_SELECTIVE** runs the new v0.4 field: weakened oscillation signal, persistent clause charge, and an avalanche accepted only when both depletion depth and measured packet utility agree.
- **LEGACY_V03** remains an untouched shadow/control lane. Holocron never injects memory into it.
- **ANCHOR** is activated selectively as the stable field only after measured stagnation.
- **SCOUT/CHAOS** exists as a bounded fallback but was not required in the holdout.
- **NO_RECOMBINATION** is split into:
  - `PROVEN_NO_RECOMBINATION` only when a sound complete sign-core witness is found;
  - `SEARCH_EXHAUSTED_NO_PROOF` otherwise.

The coordinator reports two separate costs:

1. **latency rounds** — when the first physical lane solves;
2. **total work** — all committed flips, memory reconstruction, and avalanche probes across every lane.

## Main holdout result

Across **64 new 3-SAT instances** from `n=32` through `n=240`:

| metric | v0.3 | v2.0 | change |
|---|---:|---:|---:|
| solved | 64/64 | 64/64 | no loss |
| median latency | 116.5 | **87.0** | **−25.3%** |
| mean latency | 155.97 | **137.38** | **−11.9%** |
| p90 latency | 334 | **316** | **−5.4%** |
| mean total work | 155.97 | 329.19 | **2.11× work** |

Paired instance comparison:

- v2.0 faster: **25**
- tied with preserved v0.3 lane: **39**
- slower: **0**

| n | v0.3 median | v2.0 median | change |
|---:|---:|---:|---:|
| 32 | 13.5 | 13.5 | +0.0% |
| 48 | 30.5 | 30.0 | +1.6% |
| 64 | 85.0 | 51.5 | +39.4% |
| 96 | 95.0 | 82.5 | +13.2% |
| 128 | 153.0 | 91.5 | +40.2% |
| 160 | 215.0 | 215.0 | +0.0% |
| 192 | 287.5 | 256.0 | +11.0% |
| 240 | 301.5 | 276.5 | +8.3% |

## Which lane solved first

- `LEGACY_V03`: **39**
- `GLADIUS_SELECTIVE`: **24**
- `ANCHOR`: **1**
- `SCOUT`: **0**

The new selective field therefore produced the first answer in **37.5%** of the 3-SAT holdout instances. Anchor activated in only **23.4%** of cases, and the CHAOS scout was never needed.

## 5-SAT

For the tested planted 5-SAT family, Holocron kept a single stable lane because the formulas were solved quickly. v2.0 preserved a 100% solve rate at `n=64, 96, 128` without paying the distributed portfolio cost.

## No-recombination stress

On **18 guaranteed UNSAT sign-core instances**:

- false SAT results: **0**
- `PROVEN_NO_RECOMBINATION`: **18/18**
- average proof-stage search latency: **0 rounds**, because the contradiction witness was detected before local search.

This proof detector is deliberately narrow. Failure to find this witness is not an UNSAT proof.

## Result boundary

This release demonstrates a distributed latency improvement on finite planted random SAT instances and a narrow sound UNSAT witness. It does **not** establish:

- P=NP;
- a polynomial worst-case bound;
- superiority over CDCL or state-of-the-art SAT solvers;
- reduced single-node work or energy.

The current Python simulation executes physical lanes sequentially, so its measured Python wall time is about **2.07×** v0.3. The expected benefit of deployment is lower elapsed latency from actual parallel ESP32 nodes, not free computation.

## Next physical gate

Map the release onto the prepared swarm:

- **Gladius:** `GLADIUS_SELECTIVE`
- **Anchor:** stable backup field
- **Holocron:** untouched v0.3 control lane, coordinator, display, result witness
- existing P/N Cortex: telemetry only
- new experimental packet: assignment/mode/depth exchange without changing existing mining packet ABI

Required measurements:

- elapsed wall time per node and at Holocron;
- energy per solved instance;
- ESP-NOW messages and packet loss;
- memory-injection reconstruction cost;
- agreement between simulator rounds and physical timing;
- standard DIMACS and crafted benchmark families.

**Canonical result:**  
> v2.0 reduced distributed solution latency without hiding the extra work; no instance regressed against its preserved v0.3 control lane.
