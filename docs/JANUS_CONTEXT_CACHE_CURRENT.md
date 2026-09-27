# JANUS Context Cache — CURRENT

> Canonical externalized working checkpoint. Generated from repository state; not from chat memory.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Source HEAD:** `e3fb10d7f525b7c90c45c67b3f8877ddd5d7c2c5`
- **Source commit time:** `2026-09-27T15:07:17+03:00`
- **Base ref:** `origin/main`
- **Indexed changed scientific artifacts:** `612`

## Scope

Externalize explicit scientific/project state so a new session can resume after UI or stream-cache loss without reconstructing the branch from chat history.

This cache deliberately excludes private model chain-of-thought, hidden runtime cache, and secrets. It stores the explicit project/scientific state needed for deterministic resumption.

## Immutable scientific firewall

```text
P_VS_NP = OPEN
E8_D1 = EMPTY
UNIVERSAL_SELECTOR = OPEN
TOTAL_PATH = T_construct + T_solve + T_reconstruct + T_verify <= poly(|F|)
FINITE_TESTS != UNIVERSAL_PROOF
EXISTENCE != POLYNOMIAL_CONSTRUCTION
```

## Active goal

**UNIVERSAL_DETERMINISTIC_POLYNOMIAL_3SAT_SOLVER**

Construct and prove a deterministic polynomial-time algorithm for arbitrary 3-CNF/SAT, with exact SAT equivalence and polynomial construction, solve, reconstruction, and verification costs.

## Live frontier seed

- `R0` — CLOSED on initial cubic-linear Exact-One survivor
- `R1_BIG_SCC_ELS` — CLOSED on untouched standard Exact-One; broader certified equivalence OPEN
- `R2_MATCHING_AUTARKY` — CLOSED on cubic-linear Exact-One
- `R2_SIMPLE_LINEAR_AUTARKY` — CLOSED on standard Exact-One carrier; general autarky not closed
- `R3_BCE` — CLOSED on initial linear Exact-One with minimum degree >= 2
- `R4_NO_GROWTH_DP` — CLOSED on initial cubic-linear Exact-One
- `R5_STRUCTURAL_DOMINANCE` — OPEN
- `R6_RANKED_SR_MACRO` — OPEN
- `R7_DIRECT_HORN_DUALHORN_KROM` — CLOSED as direct terminal tests on nonempty cubic-linear Exact-One
- `REPRESENTATION_CHANGE` — OPEN; current live direction includes affine-coset plus exact-weight formulation

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `research/R5_E9_UNIVERSAL_SELECTOR_EQUIVALENCE_BARRIER_2026-09-27_v1.0.md` `a426b38d6d17eea3…`
- **OK** `research/R5_E9_UNIVERSAL_SELECTOR_INTERNAL_ANTI_LOOP_BINDING_2026-09-27_v1.0.md` `e3ce2b82dd656b71…`
- **OK** `research/R5_E9_WDR_LEAN_NORMAL_FORM_SCHEDULER_CONTRACT_2026-09-23_v1.0.md` `ee4078d86270efbe…`
- **OK** `research/R5_E9_LINEAR_EXACT_ONE_PARTIAL_WDR_CLOSURE_2026-09-27_v1.0.md` `11044f9cebcd08fc…`
- **OK** `research/R5_E9_CUBIC_LINEAR_EXACT_ONE_MATCHING_LEAN_THEOREM_2026-09-27_v1.0.md` `bf126a9bd69803ac…`
- **OK** `research/R5_E9_EXACT_ONE_LINEAR_AUTARKY_LEAN_THEOREM_2026-09-27_v1.0.md` `ff3d6aaa77edf4ad…`
- **OK** `research/R5_E9_EXACT_ONE_BIG_ELS_LEAN_THEOREM_2026-09-27_v1.0.md` `cf51fa1c6f1e120f…`
- **OK** `research/R5_E9_PRESCRIBED_C10_FREIHEITSSATZ_STRENGTHENING_2026-09-27_v1.0.md` `cccefbc833dd56e2…`
- **OK** `research/R5_E9_PRESCRIBED_C10_POLYSIZE_2GROUP_COVER_THEOREM_2026-09-27_v1.0.md` `c4938cf21866168d…`
- **OK** `experiments/r5_e9_universal_selector_frontier.py` `0e84ba31b55aa1d2…`
- **MISSING** `experiments/r5_e9_cubic_linear_exact_one_affine_weight_checker.py`
- **OK** `registry/JANUS_P_VS_NP_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0.json` `df511048a4205b0c…`
- **OK** `registry/JANUS_P_VS_NP_PREMATH_AUDIT_LEDGER_2026-09-24_v1.0.json` `18e5ae1343bbcabb…`
- **OK** `governance/JANUS_P_VS_NP_PREMATH_SUPPLEMENT_2026-09-27_v1.1.json` `a1920c31b0563815…`

## Recent non-cache commits

- `e3fb10d7f525` — 2026-09-27T15:07:17+03:00 — Automate JANUS persistent context cache refresh
- `260f1b5857e6` — 2026-09-27T15:06:52+03:00 — Add JANUS context cache resume entrypoint
- `d93b0b9ff7dd` — 2026-09-27T15:06:30+03:00 — Add deterministic JANUS context cache generator
- `c86148ee608d` — 2026-09-27T15:05:19+03:00 — Add JANUS persistent context cache configuration
- `480e4ee82b54` — 2026-09-27T14:57:47+03:00 — Repair spectral replay governance validator drift
- `d34504c67227` — 2026-09-27T14:57:34+03:00 — Repair trade-free replay governance validator drift
- `1d5883e4edeb` — 2026-09-27T14:53:47+03:00 — Add CI validation for P-vs-NP stream resume cache
- `450804ab69d6` — 2026-09-27T14:53:32+03:00 — Document P-vs-NP stream resume recovery protocol
- `d405b1df3d0a` — 2026-09-27T14:53:09+03:00 — Add current P-vs-NP stream resume checkpoint
- `553e94296531` — 2026-09-27T14:52:33+03:00 — Add durable P-vs-NP stream resume cache tool
- `65870a285b36` — 2026-09-27T14:22:46+03:00 — R5 E9 add trade-free unique-model replay workflow
- `5ec6132ad00e` — 2026-09-27T14:22:33+03:00 — R5 E9 authorize trade-free dissociated-nullity gate
- `4793d50f760c` — 2026-09-27T14:22:05+03:00 — R5 E9 audit trade-free dissociated-nullity gate
- `1cba0c83ea54` — 2026-09-27T14:21:44+03:00 — R5 E9 add trade-free unique-model regression
- `7287535b0745` — 2026-09-27T14:21:23+03:00 — R5 E9 add trade-free unique-model countercontrol theorem
- `8e4828f8db06` — 2026-09-27T13:52:13+03:00 — Reconcile affine kernel trade pre-math coverage
- `96a0ab19dd5b` — 2026-09-27T13:46:17+03:00 — R5 E9 derive cubic girth10 spectral nullity bound
- `21d1f9d41d94` — 2026-09-27T13:46:02+03:00 — Remove accidental transport-only dummy file
- `7e73123e8475` — 2026-09-27T13:45:34+03:00 — dummy
- `d4476576ce48` — 2026-09-27T13:32:31+03:00 — Add signed-trade boundary projection regression

## Resume protocol

1. Read JANUS_CONTEXT_CACHE_START_HERE.md.
2. Read docs/JANUS_CONTEXT_CACHE_CURRENT.md for the human checkpoint.
3. Use registry/JANUS_CONTEXT_CACHE_CURRENT.json as the machine-readable authority for source HEAD, file hashes, transport state, and evidence pointers.
4. Fetch the listed must-read artifacts before changing scientific status.
5. Run anti-duplication/source checks before creating a new theorem or experiment.
6. Never promote P_VS_NP, E8_D1, or a PA/NM identifier from cache text alone; promotion still requires the repository governance/checker path.

## Machine-readable companion

`registry/JANUS_CONTEXT_CACHE_CURRENT.json` contains the complete indexed snapshot, evidence excerpts, hashes, and recent commit list.

Historical snapshots are append-only under `registry/context_cache/history/<source-head>.json`.
