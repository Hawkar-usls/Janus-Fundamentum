# JANUS · TIME-SAT-PARTIAL-002 — cheap admission of partial SAT probes

**Status 2026-11-01: correctness PASS; skip mechanism PASS; acceleration FAIL; production NOT READY.**
Protocol: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/574#issuecomment-6558660800

## Design

This is a source-only, classical preprocessor admission gate for CaDiCaL195 and Glucose4, NOT physical retrocausality, entropy reversal or P=NP. The previously established TIME-SAT-PARTIAL-001 slowdowns remain archived.

Before looking at this run's answers, the rule was frozen: admit a bounded failed-literal probe ONLY for n <= 32, encoded CNF with <= 512 clauses, no initial unit clauses, >= 1 complementary binary wedge (a OR b) AND (a OR NOT b), and binary-clause density >= 0.25. A wedge logically entails a; it is standard easy SAT structure, not a new computational principle.

Features are deterministic functions of the original CNF only: n, clauses, unit/binary/short counts, polarity imbalance, binary density, wedge targets. They never inspect SAT labels, baseline timing, original solver answers or previous probing outcomes. Feature computation is charged to total cost.

Four independently controlled arms:
- **raw**: original encoded formula directly into cold external CDCL.
- **feature_only**: compute features, ALWAYS skip the expensive probe and invoke same cold CDCL.
- **unconditional**: legacy TIME-SAT-001 bounded goal-ordered partial-state probe and the same CDCL.
- **adaptive**: compute features and run the legacy bounded probe only when admitted, otherwise same cold CDCL.

Any added unit must derive from an actual Boolean propagation contradiction and pass an independent original-CNF entailment check using CaDiCaL. Incomplete or interrupted speculative work is discarded, returning safely to original CDCL. An independent entailment failure is a test failure, never silently treated as harmless timeout. The actual end-to-end time includes feature scan, 5% cap of 140,000 clause visits on probing, all entailment checks, cold CDCL and original SAT model verification. Exact-One multiplicity and complementary literals are preserved by the existing classical encoding.

## Actual test results

**Corrected dual-host CI:** https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41312735704 ; source branch HEAD 349508e3e07514ac186280eda3eb6d1c0f7145f3. Both Ubuntu 22.04 and 24.04 succeeded: **7/7 new TIME-SAT-002 groups, 7/7 prior TIME-SAT-001 groups, standalone C023 independent verifier PASS**.

The initial run #41312674840 contained a mistaken negative fixture. The alleged wedge-free formula (1 OR 2),(1 OR 3),(NOT 1 OR 2) **does have** a wedge entailing 2. The test was corrected to genuinely wedge-free (1 OR 2),(1 OR 3),(2 OR 3), and CI rerun. Failed test evidence remains visible and is not reclassified as an algorithm failure.

The frozen public 60-case SAT/Exact-One sample, original suite SHA256 865af20c649740dc7847a7204d9cd0c36470ddb66777c4e92c26bde33c58c53b, and five older n18/n220/n240 cases were reused, plus three tiny constructed wedge mechanism controls. Small cases used three repetitions, large cases two. Two independent GitHub-hosted machines, actual pinned python-sat 1.9.dev17 CaDiCaL195 and Glucose4. **These are previously observed, unblinded cases**, not an external hidden holdout.

### Ratio of whole-pipeline median elapsed time to pure CDCL (60 public small cases)

| Runner | Solver | Unconditional | Adaptive |
| --- | --- | ---: | ---: |
| Ubuntu 22.04 | CaDiCaL195 | 2.78x slower | **1.20x slower** |
| Ubuntu 22.04 | Glucose4 | 3.19x slower | **1.30x slower** |
| Ubuntu 24.04 | CaDiCaL195 | 2.87x slower | **1.19x slower** |
| Ubuntu 24.04 | Glucose4 | 3.19x slower | **1.30x slower** |

Both runners: **22/60 admitted, 38/60 skipped, 13 admitted with derived sound units, 9 admitted with no units, 2 skipped despite counterfactual derived units**. These counts describe predicted usefulness in logic, **NOT speed-saving success**. Adaptive speedup over pure CDCL was NOT observed; the descriptive 95% paired-instance bootstrap intervals for the 60-case ratios were above 1 for both solvers/hosts. This does not establish out-of-sample confidence.

On MAJ3-K4 n18 and all four synthetic n220/n240 controls the adaptive filter **skipped** the ~7,001 old expensive clause visits. Yet gate overhead remained nonzero. The three specifically constructed small wedge controls were all slower than pure CDCL, even when the oracle produced valid units: standard CDCL already handles such structures efficiently.

## Evidence and limitations

- Source: experiments/direct/janus_time_sat_partial_002.py
- Tests: tests/test_time_sat_partial_002.py
- Benchmark with 2,000 paired instance bootstrap resamples: experiments/direct/janus_time_sat_partial_002_benchmark.py
- CI: .github/workflows/validate-time-sat-partial-002.yml
- Permanent verified summary: experiments/TIME_SAT_PARTIAL_002_CLOUD_EVIDENCE_20261101.json
- Full evidence Ubuntu 22.04: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41312735704/artifacts/13086356583
- Full evidence Ubuntu 24.04: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41312735704/artifacts/13086530704

**Still missing original protocol gates:** genuinely sealed external SAT data; a sufficient independent challenge; per-variant isolated native peak RSS (process-wide ru_maxrss is NOT per-arm RSS); newly produced independently replayable UNSAT proof; robust cross-machine confidence. No automatic Demiurge model training or deployment occurred. No C023 update, no main merge, no quantum/time-travel mechanism demonstrated.

**Research conclusion:** the ability to skip obviously uneconomical probes has now been measured, but even source-only gate scanning usually costs more than direct CDCL on this public corpus. Further research requires truly blinded challenging cases and a criterion that predicts **net saved wall time** rather than merely the existence of some implied literal. Keep PR #574 DRAFT, no production promotion.
