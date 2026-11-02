# JANUS TIME-SAT-004E2 · conservative auto-select XOR experiment

**Scope:** research-only, frozen before measured 004E2 CI. [Parent 004E1 draft #598](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/598) completed a known public Binary-tree-parity source within 30 CPU seconds using exact structural source XOR + CryptoMiniSat; the 3 raw engines were CPU-censored. Thus **no numeric finite speedup** can be inferred for any censored comparison.

## Plain explanation

JANUS is trying a small optional selector, not yet a trained generalized predictive model:

- Verify the exact original CNF SHA-256 and DIMACS size.
- Run the existing `extract_mixed_xor` complete source clause block scanner. It checks that each converted XOR representation is logically equivalent to exactly accounted original clauses, and it preserves every remaining original clause.
- **Only if at least 80%** of the original source clauses belong to complete XOR blocks **and at least one XOR equation is present**, run native-XOR CryptoMiniSat.
- Otherwise, or if the scanner reports a resource abstention, use raw CryptoMiniSat with *all* original clauses.
- Every SAT result, whichever solver produced it, must satisfy **every clause in the original SHA-pinned CNF**. Solver-only UNSAT without portable proof is explicitly not certified UNSAT. CPU timeouts mean UNKNOWN, not UNSAT.

The threshold was calibrated from the *previously observed* 004D4B/004E1 public development source structures. Therefore an apparent correct choice on these four **ALREADY KNOWN** sources is **training resubstitution** — do not call it cross-family generalization or a blinded success.

## Four frozen known original public source families

1. Linear-equations — n1200/m21040, previous source group cap abstention; expects safe raw fallback.
2. XOR-shifting — n2273/m8366, previously 77.4% converted; threshold skips.
3. Minimum-disagreement-parity — n1250/m7190, previously 68.9% converted; threshold skips.
4. Binary-tree-parity — n1023/m4088, previously 83.9% converted; threshold chooses native XOR; this is the previous **training-positive**, not a new test case.

All four SHA-256 values and original candidate ordering come from the previously archived official SAT Competition 2026 source CNFs, not recomputed from newly selected examples. Fixed policy: [precommit JSON](../experiments/time_sat_004_external/PREREGISTERED_004E2_PRESEEN_MULTIFAMILY_ADAPTIVE_20261102.json), immutable blob `09563db338939cb19b0bb6aab7ce56dce3eda5f2`.

## Five equal-budget, cold-process arms

- `adaptive_cms`: pay for exact original source scan, pick XOR-native or raw CMS by fixed 80% gate.
- `noop_scan_cms`: pay for **the same scan**, throw away the result, always run original raw CMS. This measures the cost of simply observing features.
- `cms_original`: no scan, original raw CryptoMiniSat.
- `cadical195_original`: no scan, original raw CaDiCaL195.
- `glucose4_original`: no scan, original raw Glucose4.

Each arm receives a new child process: Python imports, SHA source verification, strict original DIMACS shape and CNF parse, optional complete XOR scan, native solver startup, solve, and **SAT model validation against original** are all included. Two shuffled repeats per arm per family per Ubuntu 22.04/24.04 hosted runner = **80 fixed trials**. Limits: 6 seconds CPU, 10 seconds wall, 2 GiB virtual address space per child; no Rowan spending, no user NAS/PC load.

## Scientific success / failure conditions

**Engineering PASS** means only that all fixed 80 trials were executed, source models verified if SAT, negative controls counted, all unknown/timeouts recorded, and earlier source model / C023 verifier tests remain sound.

**Research benefit** cannot be declared if the gate merely selects the already known positive binary-tree family. A positive native-XOR completion compared to raw timeouts on that single previously seen source reinforces its local calibration only. Finite speed ratios are **not defined** when controls hit CPU limits. On other preseen families, strict skip-all raw and scan+raw no-op controls reveal an additional observation-cost penalty; this can make the gate *worse*, not better.

**Generalization is STILL OPEN:** an independent party must provide novel SHA-committed original sources and full independently checked SAT assignments, preferably at least three distinct previously unseen families and a statistically adequate pre-registered number of paired runs. The selection policy and threshold must be frozen BEFORE those data are revealed; do not tune on held-out results.

**Production C023 is never modified.** TIME-SAT-004C independent external proof witness remains OPEN, 004D PARTIAL, 004E experimental, 004F NOT READY. No P=NP claim.

## Reproduction

The fixed two-runner 004E2 GitHub Actions workflow runs the new test file, original 004E1 and 004D4 regressions, C023 serialized checker and 40 trials per runner. Complete original artifacts are retained by a separate SHA-verified archive mechanism in the research branch and, after confirmation, registered append-only in Meta Registry. Do not interpret the checksum archive as independent administration.
