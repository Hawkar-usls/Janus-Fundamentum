# JANUS · TIME-SAT-004D0 — real large-CNF adapter smoke, NEGATIVE scientific finding

**Date:** 2026-11-01. **Status:** adapter correctness PASS on tested cases; empirical SAT acceleration **NOT DEMONSTRATED**; full 004D gate OPEN. Production C023/main unchanged.

## Scope and source provenance

TIME-SAT-004B established 12 public external-origin SAT Competition 2026 original CNFs and raw/decoded SHA-256, from two original acquisition runs, original preregistration draft PR #577. The 004D0 experimental branch inherits the SIGXCPU classification repair from draft PR #579.

The current JANUS 003 direct binary-resolution filter derives a forced unit from the source pattern `(a OR b) AND (a OR -b)`. Legacy JANUS-003 preprocessing and TIME-SAT-002 assumptions are **not** safely applicable to arbitrarily large input CNFs; this is a separate opt-in, resource-bounded adapter. **It does not run the original JANUS UFR solver at large scale, does not implement a universal P=NP solver and is not evidence of time travel.**

Two real CNFs were frozen for this **public developmental smoke**: first previously 004B CPU-limited label-SAT `lights-out` (625 variables, 9,216 clauses, source decoded SHA256 `6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361`), first previously CPU-limited label-UNSAT `greentao` (527 variables, 12,692 clauses, decoded SHA256 `622732d1d213e930a7711270aefa079c9329cb9a446b4f24d848fea2cab6b5a7`). Selection was informed by prior known baseline timeouts. **Not hidden or held out**; not a preregistered independent competition.

## Four-arm classical comparison, same original CNF

- `raw`: cold original CDCL only.
- `feature_only`: collect bounded binary-pair index/features but never add units.
- `janus_direct`: independently replay original-index two-parent binary resolution witness and pass derived redundant units to the same solver only when sound.
- `janus_frozen_forecast`: frozen uncalibrated 003B abstract cost estimate; run the same optional insertion only when its estimated benefit exceeds inspection/audit costs.

All arms use identical immutable original CNF, same pinned PySAT version CaDiCaL195 / Glucose4, original DIMACS source verification, same process limits: 2 GiB virtual address space, six seconds CPU and nine seconds wall. Each arm runs in a fresh isolated child; full child wall includes Python startup, source parsing, feature scan, original CDCL and SAT model checking if a model exists. Source output distinguishes CPU signal, wall deadline and other signal. **Only one randomized-order repetition** on each of two GitHub-hosted Ubuntu machines: descriptive engineering smoke, NOT adequate paired statistical evidence. Built-in simplification arm beyond the default solver settings not implemented. UNSAT independent portable proof not generated.

### Experiment results

[CI #41326432087](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41326432087), exact research HEAD `1c07c58ca513180453c28a87f6f520c6e790b129`:
- Ubuntu 22.04 **7/7 new tests PASS**, **6/6 earlier 004B tests PASS**.
- Ubuntu 24.04 **7/7 new tests PASS**, **6/6 earlier 004B tests PASS**.
- **32/32 process-isolated cases ended `UNKNOWN_CPU_LIMIT_SIGXCPU`**, meaning neither CaDiCaL195 nor Glucose4, with or without the optional JANUS component, returned SAT or UNSAT inside the six-second budget.
- No sound solver-level speed ratio can be inferred from timeout-censored wall time. In particular **we cannot claim that JANUS solved anything faster.**

The first workflow attempt [#41326394780](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41326394780) failed because its YAML referenced a nonexistent old test filename; this was fixed to `test_time_sat_004b.py` before successful run. The failed CI is not reclassified as PASS.

The exact two successful original Actions ZIP artifacts and their full JSON output were permanently retained with SHA-256 in **[archival CI #41326950377](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41326950377)**. [Original two-host summary](../experiments/time_sat_004_external/time_sat_004d0_evidence/summary.json) pins source run, commit, original ZIP hashes, each original job time and every UNKNOWN outcome.

### Independent cheap-stage diagnostic: 0 useful wedges on both real CNFs

A second **source-only diagnostic with no SAT calls** downloaded and rechecked the same two pinned original sources. It safely inspected the entire encoded clause corpus under source memory limits:
- **Lights-out**: 45,312 literal occurrences scanned; **0 resolution wedges**; frozen cost filter `admit=false` / abstract net -90,624 units. Proof-only scan ~4 ms.
- **Green–Tao**: 38,748 literal occurrences scanned; **0 resolution wedges**; `admit=false` / abstract net -77,496 units. Proof-only scan ~3.7 ms.

The two diagnostic timings are **NOT comparable to the child solver's timed-out wall timings**; they exclude solver and process startup. The structural finding is decisive for this particular frozen 003A/003B mechanism: there are **no applicable binary-source pair resolvents** for it on either input. The current forecast safely declines optional work; the feature scan is an extra cost. No new SAT-solving mechanism is exercised.

[Complete proof-only diagnostics](../evidence/time_sat_004d0_diagnostics/diagnostics.json) and original two-host frozen result JSON are durable Git files.

## Scientifically valid decision and next stage

**PASS:** bounded >240-variable source adapter works with frozen upstream SHA, correct source pair witness tests, no unsupported SAT claims, correctly classified 32 CPU limits. **NEGATIVE:** 0 usable 003A structural deductions on the two real benchmark instances and no SAT/UNSAT result from any of 32 bounded trials. **NOT ESTABLISHED:** advantage over raw CaDiCaL195/Glucose4; even an observational speedup ratio is not computable with all results censored.

004D **remains OPEN**. To challenge stronger CDCL fairly, the next candidate must either invent/identify a more useful *sound and cheaply justified* original-CNF inference on these hard external-origin families, or explicitly decline to run. Freeze that method and parameters on training data, test different families and a sealed independent held-out set with paired repeated runs, native simplification controls, portable UNSAT proofs, per-process peak RSS, and an independently administered outside-GitHub Witness. Do NOT spend extra workers/repetitions testing unchanged binary wedges on these two sources; they provably supply no units. Preserve negative results in Meta Registry. C023/main remain unchanged.
