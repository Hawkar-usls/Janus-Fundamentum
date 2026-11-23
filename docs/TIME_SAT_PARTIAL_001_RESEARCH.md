# JANUS · TIME-SAT-PARTIAL-001: strong CDCL falsification of bidirectional partial consistency

**Date:** 2026-11-01. **Status:** bounded semantic correctness PASS; **performance NEGATIVE** on the frozen public suite; external hidden test, per-instance peak RSS and independent portable UNSAT certificates **NOT DONE**. **PR #574 stays DRAFT; C023/main is not changed.**

## Direct source contract

The original experiment was registered in the merged [Meta Registry scientific synthesis](https://github.com/Hawkar-usls/janus-meta-registry/blob/main/data/JANUS-ENTROPY-TIME-CAUSALITY-REGISTRY-SYNTHESIS-2026-11-01-v1.0.json), under `experimental_program[TIME-SAT-PARTIAL-001]` in [PR #433](https://github.com/Hawkar-usls/janus-meta-registry/pull/433).

That source requires **fixed original and externally hidden instances, an actual strong CDCL baseline, measurable time/propagations/memory/solved cases/incorrect pruning and validated UNSAT proof**, and a stop rule on no improvement. This first experiment implements **fixed public tests and actual strong CDCL**; it does *not* satisfy external-blind challenge, independently replayed UNSAT proof for every new instance, or per-variant peak RSS. Therefore the full scientific gate is still **NOT READY**, despite correct software tests.

This is entirely *classical* forward-time SAT inference. "Backward" refers to ordering probes by constrained output/goal clauses and evaluating what input choices they admit. It is NOT physical retrocausality, a tachyon, closed timelike curve, an entropy violation or an oracle with information from the future.

## Three fair arms

All three are given the **same original CNF**, native Exact-One constraints encoded as at-least-one and pairwise at-most-one clauses preserving duplicate/negated literal multiplicity. Each cold-starts the **same** strong third-party CDCL solver (CaDiCaL195 or Glucose4, pinned PySAT 1.9.dev17).

1. **raw:** CDCL on unchanged encoded CNF.
2. **forward:** ordinary sound SAT unit propagation, append only independently proven implied unit clauses, then the same CDCL.
3. **bidirectional:** identical forward pass; identify high-pressure clause goals from the source formula alone and tentatively propagate both Boolean values of up to eight relevant unset variables. A unit may be added only when its opposite value has **actually produced a constraint conflict**. All speculative work is bounded to 5% of a 140,000 clause-visit budget, plus at most one crossing visit; a truncated probe never implies UNSAT. Every added unit is separately challenged using **CaDiCaL on the unchanged original formula under its opposite assumption**, and the complete cost of these checks is charged to the augmented pipeline. Cold-start external solver then searches the same source CNF plus verified redundant unit clauses.

**Unsound branch elimination fails CI.** Models are independently checked under the original SAT/Exact-One semantics. A "partial state consistent with current local clauses" does not prove the full formula SAT. No preprocessor **ever** establishes UNSAT on its own; only the external complete solver's answer is used, and this benchmark does **not** generate portable UNSAT proof artifacts.

## Reproducible verification

CI: [independent GitHub Actions #41310145885](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41310145885); source SHA `f48ad8d6690aaf2c6f24550287364ece769c35a0`.

Two separate GitHub-hosted runners **Ubuntu 22.04 and Ubuntu 24.04** independently installed `python-sat==1.9.dev17`; each ran seven new hostile test groups, eight NOVIKOV-002 groups and independent legacy serialized C023 verifier — **all PASS**.

Test corpus: 60 original frozen SAT/Exact-One cases, SHA256 `865af20c649740dc7847a7204d9cd0c36470ddb66777c4e92c26bde33c58c53b`, exhaustive independent UFR Boolean reference; five additional deterministic controls: real MAJ3-K4 n18/1024 clauses, planted SAT n220 and n240, and embedded 4-bit UNSAT cores n220/n240. The generated large examples are NOT the historical Janus 220–240-variable CNFs nor external blindly hidden instances. Three repetitions per small case and two per large case, stage order rotated to reduce warmup bias (not to prove statistical confidence).

## Measured results: decisive negative speed data

Median per-case **whole-pipeline runtime ratio** relative to identical cold-start raw CDCL; ratios above 1 mean slower.

| Runner | Solver | Forward / raw | Forward+goal-consistency / raw | Goal filter slower cases |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 22.04 | CaDiCaL195 | 1.214x | **2.964x** | 57/60 |
| Ubuntu 22.04 | Glucose4 | 1.261x | **3.290x** | 60/60 |
| Ubuntu 24.04 | CaDiCaL195 | 1.217x | **2.631x** | 57/60 |
| Ubuntu 24.04 | Glucose4 | 1.307x | **3.291x** | 60/60 |

Example large-instance **raw CDCL** and augmented result (Ubuntu 24.04; all answers agree between both engines):

| Formula | Raw CaDiCaL / full bidirectional | Raw Glucose4 / full bidirectional | Answer |
| --- | ---: | ---: | --- |
| MAJ3-K4 n18 | 27.82 / 43.04 ms | 32.87 / 49.03 ms | UNSAT |
| planted SAT n220 | 3.59 / 12.73 ms | 3.25 / 12.75 ms | SAT verified |
| planted SAT n240 | 3.89 / 13.22 ms | 3.59 / 13.22 ms | SAT verified |
| embedded 4-bit UNSAT n220 | 2.05 / 11.32 ms | 1.92 / 11.27 ms | UNSAT (no portable proof) |
| embedded 4-bit UNSAT n240 | 2.27 / 11.78 ms | 2.02 / 11.59 ms | UNSAT (no portable proof) |

On **all five large cases**, the goal-first partial stage spent about 7,001 charged clause visits in probing but produced **zero derived units**. It wasted work without helping strong CDCL. This is a negative result; do not interpret local consistency as a source of new information. Some tiny benchmarks produced redundant sound units, but the cost outweighed any gain.

MAJ3-K4 UNSAT **also** has an earlier independently replayed C023/UFR certificate in PENROSE-003. This benchmark merely compares CaDiCaL and Glucose4 verdicts; agreement is not a portable UNSAT proof. The user-facing claims about MAJ3-K4 must not falsely attribute the proof to this new experiment.

## Evidence and source files

- Core: `experiments/direct/janus_time_sat_partial_001.py`
- Test: `tests/test_time_sat_partial_001.py`
- Benchmark: `experiments/direct/janus_time_sat_partial_001_benchmark.py`
- CI: `.github/workflows/validate-time-sat-partial-001.yml`
- Permanent summary, two runner reports: `experiments/TIME_SAT_PARTIAL_001_CDCL_EVIDENCE_20261101.json`.
- [Ubuntu 22.04 full per-case artifact](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41310145885/artifacts/13084158937) and [Ubuntu 24.04 full per-case artifact](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41310145885/artifacts/13084148956) (30-day retention).

## Implications for the Next Scientific Gate

Original registration says **no improvement means keep the heuristic disabled**. The correct decision is **STOP on general acceleration; retain as experimental optional integrity check only**. No automatic merge into C023.

Research on partial consistency remains valid only if the next protocol freezes an **externally hidden** benchmark source, compares with strong CDCL under equal hardware/time/RSS/proof budgets and specifies in advance *exactly when* a probe can be expected to pay for itself. Test confidence intervals across at least two independent workers and preserve all negative runs. Do not invent entropy rates or statistical success probabilities: the Meta Registry prohibits using thermodynamic concepts as guarantees of SAT speedup.
