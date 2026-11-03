# JANUS TIME-SAT-004E12C4 — INTERNAL DEVELOPMENT ONLY

Linked design gate: [Issue #622](https://github.com/Hawkar-usls/Janus-Fundamentum/issues/622).
Parents: [E12C3 draft #621](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/621) and its exposed 8 original source SHAs.

## What this branch implements

* Deterministic **new** original-CNF generators with 2 source seeds per family per split, including full width5/6, negative width4, partial width6, planted 3SAT, near 60/67/69.9/70.1/75/80/90 percent clause-coverage boundaries and internal small UNSAT controls.
* Three source presentations (original, row/literal shuffle, bijective variable/polarity renaming). Same original SHA and family are the scientific independent unit; presentations/repetitions are NOT additional independent source samples.
* Exact full sign-mask certificate recheck before emitting XOR, no absorbed clause index duplication, and exact ordered residual CNF plus multiset conservation. Incomplete masks and repeated clauses are not discarded.
* Conservative selector using only source certificate features and **development** source-group full-cold paired receipts. At least two distinct matching development originals, both uncensored and independently verified, and observed group medians at least 1.5x RAW are required even for a research-only XOR decision. No model => unmodified RAW. This is a development heuristic, **not** a proven expected-profit bound.
* Internal exhaustive verification for small UNSAT sources (not an external custodian or general portable UNSAT proof); larger UNSAT claims remain unverified until a separately checked proof is supplied.
* UNKNOWN/timeout and unverified SAT/UNSAT are censored, not treated as negative or positive finite ratios.

## Explicit exclusions

**No E12C4 timed held-out experiment has been run and no executable preregistration has been accepted.** Held-out sources are internal and are not externally blind. The prototype currently has an **optional fitted model from all 16 publicly exposed E12C3 VM receipts**, and therefore chooses RAW by default. This is intentional to avoid pretending a predictive model exists.

A future *separate* frozen execution PR must lock code Git SHA, both source and model SHA manifests, the development receipts and fitted coefficients, exact metric/aggregation, original-family split, budget (CPU12s/wall18s/AS2GiB/max6–8 VMs), independent UNSAT proof verification path, and the source-level statistical acceptance rule **before** the first held-out solve. It must retain every held-out case including timeouts and failed expectations. Do not select held-out seeds by checking their solver speed first.

Gates remain distinct: SOUNDNESS, RESULT_VERIFICATION, NET_PROFIT. A CI success here is at most an *internal implementation check*, not a NET_PROFIT_PASS, not a champion and not AUTONOMY_FULL.

## Commands

```bash
python -m unittest discover -s tests -p 'test_time_sat_004e12c4_profit_aware_dev.py' -v
python experiments/direct/janus_time_sat_004e12c4_profit_aware_dev.py --write-cohort-lock evidence/e12c4-development/COHORT_LOCK.json
python experiments/direct/janus_time_sat_004e12c4_profit_aware_dev.py --write-development-fit evidence/e12c4-development/DEV_FIT.json
```

The generator does **not** invoke a SAT solver, upload any scientific benchmark results, access the user's PC/NAS, or spend Rowan credits. This branch does not change `main` or C023.
