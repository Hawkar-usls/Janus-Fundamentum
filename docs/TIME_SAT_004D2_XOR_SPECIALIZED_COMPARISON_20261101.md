# JANUS TIME-SAT-004D2 · GF(2) versus specialized XOR solver

Research date: 2026-11-01. Scientific status: sound limited same-source performance result; NOT a hidden independent exam or production gate.

## Experiment
Five pre-frozen arms operate on the SAME exact original public SATComp2026 Lights-out CNF, 625 variables / 9216 clauses / decoded original SHA256 6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361. Each arm reads SHA-verified original source, runs in a fresh one-thread Python child with 2GiB virtual memory, 8 seconds soft CPU, 11 seconds parent wall cap. Three seeded-order repeats each on GitHub Ubuntu22 and Ubuntu24.

Arms: JANUS original-CNF exact XOR group recognition + Python GF(2); CryptoMiniSat 5.15.0 using exactly the extracted XOR equations with recognition cost charged; CryptoMiniSat 5.15.0 given original unmodified CNF to process on its own; cold CaDiCaL195 on original CNF; cold Glucose4 on original CNF. The parent times the complete child, including Python process startup, imports, source read and SHA, structural extraction when used, solver input initialization, solve and independent SAT model checking against ALL original clauses.

## Verified run
[Full original dual-host CI #41330327931](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41330327931), exact tested HEAD 3f9c415f3579aa34510dd124364d4d9084894eb1: both jobs PASS; 6/6 new adversarial offline tests per machine and C023 independent serialized certificate verifier PASS.

Median seconds of full process, 3 repetitions per host:

| Algorithm | Ubuntu 22.04 | Ubuntu 24.04 |
|---|---:|---:|
| JANUS GF(2) exact full XOR recognition | 0.113395 | 0.102057 |
| CryptoMiniSat native XOR after source recognition | 0.159949 | 0.132340 |
| CryptoMiniSat on original CNF | 5.869163 | 4.634381 |
| CaDiCaL195 on original CNF | CPU LIMIT (3/3) | CPU LIMIT (3/3) |
| Glucose4 on original CNF | CPU LIMIT (3/3) | CPU LIMIT (3/3) |

All 18 specialized-arm SAT solutions independently satisfy the original 9216 CNF clauses. The other 12 raw CDCL runs are UNKNOWN_CPU_LIMIT_SIGXCPU and must NOT be converted into finite solver speedup ratios or UNSAT results.

The descriptive ratio of median native-XOR CryptoMiniSat to median JANUS was 1.41055x Ubuntu22 and 1.29673x Ubuntu24, corresponding to a narrower ~29% / ~23% less JANUS full-process wall time. These ratios are observation-specific and NOT a claim of statistical, general algorithmic, or asymptotic superiority; 3 repetitions per worker on one public previously seen family with different Python/C++ implementation stacks do NOT justify a meaningful 95% population uncertainty interval. CryptoMiniSat itself achieves an efficient answer using native XOR and even solves the source CNF without external extraction.

**First CI FAIL retained**: initial offline randomized generator sometimes put different parity equations on identical variable supports and incorrectly expected exact full-XOR recognition. Corrected ONLY the synthetic test to use distinct supports, leaving production, benchmark source and algorithm untouched. Only the later successful run is performance evidence.

## Durable exact evidence
[Archival CI #41330600482](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41330600482) SUCCESS: saved both exact original GitHub Action artifact ZIP bytes and both original complete benchmark JSON files, checking SHA-256 before deriving any summary.

[Permanent two-worker evidence](../experiments/time_sat_004_external/time_sat_004d2_evidence/summary.json) includes original GitHub artifact IDs, source run/head, original ZIP+inner JSON SHA256, complete raw per-arm timing receipts, successful RSS readings, and honest CPU-censoring. The original ZIPs and original per-run JSONs remain unchanged. Process RSS from CPU-killed children is not available; do not claim a proven memory advantage.

## Scientific boundaries
This is standard classical XOR structure and GF(2) elimination, not P=NP, a physical reverse-time effect or a universal JANUS solver. The comparison passes an engineering correctness/feasibility gate on ONE prior-known public problem only. An externally hidden multi-family held-out challenge, externally administered independent proof witness, honest per-family paired confidence intervals, and system-level failure/abstention behaviour on mixed CNF are still OPEN. The existing Green–Tao source is a useful negative control for which full-XOR specialization abstains.

TIME-SAT-004D and 004F remain OPEN/NOT READY; C023/main unchanged. PR #582 and its descendant research PRs remain DRAFT. Next scientific experiment needs frozen multiple fresh XOR-heavy and mixed-XOR CNF families, independently checked original models, a strong native-XOR baseline, actual full costs, and strict hold-out separation.
