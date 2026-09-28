# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `c5178dad5b94c78ecbe10be5c572f331e552a46c`
- **Source commit time:** `2026-09-28T20:52:14+03:00`
- **Indexed changed scientific artifacts:** `802`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `05563fb285a1b2a4ae62d2a6aab0143bdbe52899`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `20`

## Scientific firewall

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

## Semantic live frontier

- **Frontier:** `R5_E9_PROJECTIVE_LINE_AVOIDANCE_GLOBAL_CONTRACTION_GATE_V1`
- **Carrier:** post-series connected linear-cubic Exact-One source represented by distinct nonzero binary-kernel signatures; every source row is a projective line {u,v,u+v} and SAT is existence of a hyperplane containing no source line
- Established: Exact-One SAT iff mu(A)=n/3, equivalently the rooted minimum-circuit threshold in M_F2([A|1]).
- Established: All previously certified polynomial terminals remain active: full rational rank/low rational nullity, balanced, commuting/abelian, phase-pass, perfect-conflict, genuine small separators, single-odd rooted matroid terminals, and other frozen E9/E10 terminals.
- Established: Polynomial-dimensional bilinear annihilation summaries are impossible in the scoped witness-selection model: m independent polarity channels have connection rank 2^m.
- Established: Direct endpoint projected-delta-matroid encodings fail on all 42 perfect-matching normalizations of AFFINE_3X3.
- Established: Rooted and nonroot 2-cocircuit series pairs admit exact polynomial weighted contraction with witness lifting; SAT_12_3 collapses to a constant AG(3,2) core.
- Established: For K=ker_F2(A), equal kernel signatures are exactly nonroot series classes and zero signatures are exactly root-series classes.
- Established: After exhaustive series contraction all surviving signatures are distinct and nonzero; a surviving row has signatures {u,v,u+v}, a projective line in PG(k-1,2).
- Established: Every parity solution is x_j=1+sigma_j dot t. Exact-One holds iff no source projective line is contained in H_t={u:u dot t=0}.
- Established: Equivalently SAT asks for t outside the union of codimension-two orthogonal subspaces of the source lines.
- Established: Generic 2-SUB-SAT / union-of-subspace avoidance is NP-hard; only source-specific 3-regular linear projective-line geometry or a stronger global contraction remains admissible.
- Established: Series-irreducible PG(3,2) controls include both SAT and UNSAT instances; series-irreducibility alone is not a decision certificate.
- Established: No unconditional deterministic polynomial SAT decider has been established.

### Live split

```json
{
  "primary": {
    "goal": "Construct a deterministic polynomial global contraction or zero-test for the 3-regular projective-line hyperplane-avoidance residual, with exact witness lifting and a strict polynomial progress measure.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Exploit the exact Walsh/incidence form of the bad-line count without enumerating 2^k characters; reject any method that is only generic sparse-Fourier minimization or nearest-codeword in disguise.",
    "status": "OPEN"
  },
  "reserve": {
    "goal": "Import an external polynomial donor only after exact source audit and hostile-control validation.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Derive the exact bad-line counting identity for a character t using 3-regular projective-line incidence and test whether equality q(t)=0 has a source-specific polynomial certificate.
2. Search current literature for algorithms or hardness specific to 3-regular projective-line / partial-Steiner parallel-class objects; do not import degree-at-most-3 hardness as exact degree-3 without proof.
3. Test any Fourier/spectral or projective contraction first on the frozen series-irreducible PG15 SAT and UNSAT controls and on high-girth/high-nullity source families.
4. If the Walsh zero-test is only generic codeword optimization, freeze that route and move to a genuinely representation-changing contraction on the projective arrangement.
5. Promote E8_D1 only after SOUND+COMPLETE+TERMINATES+POLY+RECONSTRUCT hold for arbitrary 3CNF.

## Commits newer than semantic checkpoint — MUST INGEST

- `c7ddc902348f` — 2026-09-28T18:12:02+03:00 — R5 E9: synchronize semantic checkpoint to projective-line avoidance gate
- `16d7a4284629` — 2026-09-28T18:31:05+03:00 — R5 E9: prove projective signature Walsh arrangement quotient
- `177cd4b176ea` — 2026-09-28T19:10:50+03:00 — R5 E9: prove projective line-trade gauge and mod-3 Walsh gap
- `4d6ec5eea8fd` — 2026-09-28T19:11:23+03:00 — R5 E9: add projective line-trade gauge regression
- `ae7034a92cd7` — 2026-09-28T19:13:47+03:00 — R5 E9: strengthen line-trade gauge with terminal-exposing switch
- `7c7daf5cc4dc` — 2026-09-28T19:14:23+03:00 — R5 E9: strengthen line-trade regression with full-rank terminal census
- `237aa3e648b2` — 2026-09-28T19:17:36+03:00 — R5 E9: prove fixed-r projective trade rank-ascent router
- `a980d85e89da` — 2026-09-28T19:18:05+03:00 — R5 E9: add fixed-r trade rank-ascent regression
- `2a28c8b43829` — 2026-09-28T20:14:14+03:00 — R5 E9: prove projective fractional-support exact closure
- `dfd4ba288014` — 2026-09-28T20:15:09+03:00 — R5 E9: add projective fractional-support closure regression
- `5419bb7585f0` — 2026-09-28T20:15:20+03:00 — R5 E9: add CI for projective fractional-support closure
- `40d673255f47` — 2026-09-28T20:34:53+03:00 — R5 E9: prove rational-kernel Tukey-depth boundary quotient
- `3e4c7d688740` — 2026-09-28T20:35:26+03:00 — R5 E9: add kernel Tukey-depth boundary regression
- `bba8036e144c` — 2026-09-28T20:35:38+03:00 — R5 E9: add CI for kernel Tukey-depth boundary
- `79e3015cd010` — 2026-09-28T20:45:03+03:00 — R5 E9: kill monotone Tukey tope descent on PG15 SAT
- `11793acebcaa` — 2026-09-28T20:45:36+03:00 — R5 E9: add PG15 monotone tope-descent countercontrol
- `bd6205f45e17` — 2026-09-28T20:45:45+03:00 — R5 E9: add CI for Tukey tope-descent barrier
- `f510fd4789aa` — 2026-09-28T20:49:25+03:00 — R5 E9: bound source-kernel augmenting paths by tope geodesics
- `ba8c9de2ad21` — 2026-09-28T20:49:58+03:00 — R5 E9: add source-kernel tope geodesic regression
- `c5178dad5b94` — 2026-09-28T20:52:14+03:00 — R5 E9: add CI for source-kernel tope geodesic bound

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `b32b1ddf5e8d9247…`
- **OK** `tools/janus_stream_resume_cache.py` `adc6ab7f260d2384…`
- **OK** `research/R5_E9_UNIVERSAL_SELECTOR_EQUIVALENCE_BARRIER_2026-09-27_v1.0.md` `a426b38d6d17eea3…`
- **OK** `research/R5_E9_UNIVERSAL_SELECTOR_INTERNAL_ANTI_LOOP_BINDING_2026-09-27_v1.0.md` `e3ce2b82dd656b71…`
- **OK** `research/R5_E9_WDR_LEAN_NORMAL_FORM_SCHEDULER_CONTRACT_2026-09-23_v1.0.md` `ee4078d86270efbe…`
- **OK** `research/R5_E9_LINEAR_EXACT_ONE_PARTIAL_WDR_CLOSURE_2026-09-27_v1.0.md` `11044f9cebcd08fc…`
- **OK** `research/R5_E9_CUBIC_LINEAR_EXACT_ONE_MATCHING_LEAN_THEOREM_2026-09-27_v1.0.md` `bf126a9bd69803ac…`
- **OK** `research/R5_E9_EXACT_ONE_LINEAR_AUTARKY_LEAN_THEOREM_2026-09-27_v1.0.md` `ff3d6aaa77edf4ad…`
- **OK** `research/R5_E9_EXACT_ONE_BIG_ELS_LEAN_THEOREM_2026-09-27_v1.0.md` `cf51fa1c6f1e120f…`
- **OK** `research/R5_E9_PRESCRIBED_C10_FREIHEITSSATZ_STRENGTHENING_2026-09-27_v1.0.md` `cccefbc833dd56e2…`
- **OK** `research/R5_E9_PRESCRIBED_C10_POLYSIZE_2GROUP_COVER_THEOREM_2026-09-27_v1.0.md` `c4938cf21866168d…`
- **OK** `research/R5_E9_TRADE_FREE_UNIQUE_MODEL_DISSOCIATED_NULLITY_GATE_2026-09-27_v1.0.md` `0fefd86cb9a972d0…`
- **OK** `experiments/r5_e9_universal_selector_frontier.py` `0e84ba31b55aa1d2…`
- **OK** `experiments/r5_e9_trade_free_unique_model_control.py` `d8d97584a6a624cf…`
- **OK** `registry/JANUS_P_VS_NP_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0.json` `df511048a4205b0c…`
- **OK** `registry/JANUS_P_VS_NP_PREMATH_AUDIT_LEDGER_2026-09-24_v1.0.json` `18e5ae1343bbcabb…`
- **OK** `governance/JANUS_P_VS_NP_PREMATH_SUPPLEMENT_2026-09-27_v1.5.json` `56bb7ae58b780d98…`

## Recent non-cache commits

- `c5178dad5b94` — 2026-09-28T20:52:14+03:00 — R5 E9: add CI for source-kernel tope geodesic bound
- `ba8c9de2ad21` — 2026-09-28T20:49:58+03:00 — R5 E9: add source-kernel tope geodesic regression
- `f510fd4789aa` — 2026-09-28T20:49:25+03:00 — R5 E9: bound source-kernel augmenting paths by tope geodesics
- `bd6205f45e17` — 2026-09-28T20:45:45+03:00 — R5 E9: add CI for Tukey tope-descent barrier
- `11793acebcaa` — 2026-09-28T20:45:36+03:00 — R5 E9: add PG15 monotone tope-descent countercontrol
- `79e3015cd010` — 2026-09-28T20:45:03+03:00 — R5 E9: kill monotone Tukey tope descent on PG15 SAT
- `bba8036e144c` — 2026-09-28T20:35:38+03:00 — R5 E9: add CI for kernel Tukey-depth boundary
- `3e4c7d688740` — 2026-09-28T20:35:26+03:00 — R5 E9: add kernel Tukey-depth boundary regression
- `40d673255f47` — 2026-09-28T20:34:53+03:00 — R5 E9: prove rational-kernel Tukey-depth boundary quotient
- `5419bb7585f0` — 2026-09-28T20:15:20+03:00 — R5 E9: add CI for projective fractional-support closure
- `dfd4ba288014` — 2026-09-28T20:15:09+03:00 — R5 E9: add projective fractional-support closure regression
- `2a28c8b43829` — 2026-09-28T20:14:14+03:00 — R5 E9: prove projective fractional-support exact closure
- `a980d85e89da` — 2026-09-28T19:18:05+03:00 — R5 E9: add fixed-r trade rank-ascent regression
- `237aa3e648b2` — 2026-09-28T19:17:36+03:00 — R5 E9: prove fixed-r projective trade rank-ascent router
- `7c7daf5cc4dc` — 2026-09-28T19:14:23+03:00 — R5 E9: strengthen line-trade regression with full-rank terminal census
- `ae7034a92cd7` — 2026-09-28T19:13:47+03:00 — R5 E9: strengthen line-trade gauge with terminal-exposing switch
- `4d6ec5eea8fd` — 2026-09-28T19:11:23+03:00 — R5 E9: add projective line-trade gauge regression
- `177cd4b176ea` — 2026-09-28T19:10:50+03:00 — R5 E9: prove projective line-trade gauge and mod-3 Walsh gap
- `16d7a4284629` — 2026-09-28T18:31:05+03:00 — R5 E9: prove projective signature Walsh arrangement quotient
- `c7ddc902348f` — 2026-09-28T18:12:02+03:00 — R5 E9: synchronize semantic checkpoint to projective-line avoidance gate
- `05563fb285a1` — 2026-09-28T17:45:38+03:00 — R5 E9: add CI for kernel-signature projective avoidance
- `85a14827a61f` — 2026-09-28T17:43:33+03:00 — R5 E9: add kernel-signature projective avoidance regression
- `c92fa9cc9cc3` — 2026-09-28T17:41:59+03:00 — R5 E9: derive kernel-signature series and projective avoidance normal form
- `d917a16093c4` — 2026-09-28T17:13:43+03:00 — R5 E9: extend series contraction regression to singular 15_3
- `36a8ea82be59` — 2026-09-28T17:10:56+03:00 — R5 E9: add CI for rooted series-pair syndrome contraction

## Resume protocol

1. Read JANUS_CONTEXT_CACHE_START_HERE.md.
2. Read docs/JANUS_CONTEXT_CACHE_CURRENT.md.
3. Treat .janus/P_VS_NP_STREAM_CACHE_CURRENT.json as the semantic frontier/next-action checkpoint and registry/JANUS_CONTEXT_CACHE_CURRENT.json as the automatic live Git continuity/index layer.
4. If relation_to_live_source_head is LIVE_DESCENDS_FROM_SEMANTIC_CACHE, ingest every listed newer non-cache commit before continuing mathematics.
5. If the relation is DIVERGED_OR_SOURCE_MISSING or SEMANTIC_CACHE_AHEAD_OF_LIVE, stop writes and reconcile Git history.
6. Fetch must-read/critical artifacts and run anti-duplication/source checks before a new theorem or experiment.
7. Never promote P_VS_NP, E8_D1, or a PA/NM identifier from cache text alone; promotion requires governance/checker/CI.

## Scope boundary

This repository cache stores explicit scientific/project context only. It deliberately excludes private model chain-of-thought, hidden runtime cache, credentials, and secrets.

## Machine-readable companion

`registry/JANUS_CONTEXT_CACHE_CURRENT.json` contains the complete live index and the embedded semantic checkpoint. History is append-only under `registry/context_cache/history/<source-head>.json`.
