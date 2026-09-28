# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `24ea91f06754ff206dd13782db1b3a64931111ef`
- **Source commit time:** `2026-09-28T16:55:21+03:00`
- **Indexed changed scientific artifacts:** `777`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `8e940bc0e949dabf589a033479f7afce93e1ef22`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `11`

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

- **Frontier:** `R5_E9_ROOTED_SYNDROME_F7STAR_GLOBAL_CONTRACTION_GATE_V1`
- **Carrier:** cubic square Exact-One = minimum-weight circuit through distinguished syndrome element e_b in M_F2([A|1]); arbitrary signed 3CNF remains universal parent
- Established: Exact-One SAT iff mu(A)=n/3, where mu(A)=min{|x|:Ax=1 over F2}.
- Established: mu(A) equals minimum weight of a circuit through e_b in M_F2([A|1]).
- Established: Augmented regular matroid implies deterministic polynomial decision+witness reconstruction.
- Established: The entire prior two-edge UNSAT prime tower has augmented regular matroids and is polynomially decided; it is no longer a hostile residual here.
- Established: Rooted MFMC strictly extends regularity: if e_b is in no F7* minor of its connected component, minimum circuit through e_b is polynomially computable.
- Established: Therefore the live matroid obstruction is source-generated rooted F7* containing e_b, not generic nonregularity or unrooted F7/F7*.
- Established: KS-derived 2334_3 Exact-One UNSAT has theta(G)=n/3 but alpha(G)<n/3, so theta/Hoffman equality is not a SAT certificate.
- Established: No unconditional deterministic polynomial SAT decider has been established.

### Live split

```json
{
  "primary": {
    "goal": "Exact polynomial contraction/decomposition for source-generated rooted F7* containing e_b preserving minimum circuit-through-e_b and witness lift with strict polynomial global decrease.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Build the smallest source-valid rooted-F7* hostile control, starting from FANO_7/AFFINE_3X3.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Check open literature and repo for rooted-F7* shortest-route decompositions beyond MFMC.
2. Test FANO_7 and AFFINE_3X3 for rooted F7* through e_b.
3. Classify rooted F7* interface costs under binary 1/2/3-sums and prove polynomial total-state composition or falsify it.
4. Exploit source provenance A*1=1 plus cubic/linear incidence, not a generic shortest-circuit oracle.
5. Promote E8_D1 only after SOUND+COMPLETE+TERMINATES+POLY+RECONSTRUCT for arbitrary 3CNF.

## Commits newer than semantic checkpoint — MUST INGEST

- `b0db547849a7` — 2026-09-28T15:25:40+03:00 — R5 E9: add CI for KS theta-equality countercarrier
- `c5a42f73d972` — 2026-09-28T15:34:05+03:00 — R5 E9: sync semantic checkpoint to rooted F7* syndrome gate
- `2f01102867a2` — 2026-09-28T15:42:04+03:00 — R5 E9: freeze rooted F7* source controls
- `9d73742c3b32` — 2026-09-28T15:42:43+03:00 — R5 E9: add exact rooted F7* source-control census
- `a0dd1e8d1135` — 2026-09-28T15:42:56+03:00 — R5 E9: add CI for rooted F7* source controls
- `cd4ee9ab1d43` — 2026-09-28T16:11:50+03:00 — R5 E9: extend syndrome terminal to single-odd dual-Fano criterion
- `89f5f64e60da` — 2026-09-28T16:13:36+03:00 — R5 E9: add exact rooted dual-Fano source census
- `eee109833b13` — 2026-09-28T16:14:02+03:00 — R5 E9: add CI for rooted dual-Fano source controls
- `436015067066` — 2026-09-28T16:54:21+03:00 — R5 E9: reconcile rooted dual-Fano with E10 and semantic terminals
- `84b2c77be435` — 2026-09-28T16:55:01+03:00 — R5 E9: add exact cross-route rooted dual-Fano regression
- `24ea91f06754` — 2026-09-28T16:55:21+03:00 — R5 E9: add CI for rooted dual-Fano E10 reconciliation

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `810575d026d236f8…`
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

- `24ea91f06754` — 2026-09-28T16:55:21+03:00 — R5 E9: add CI for rooted dual-Fano E10 reconciliation
- `84b2c77be435` — 2026-09-28T16:55:01+03:00 — R5 E9: add exact cross-route rooted dual-Fano regression
- `436015067066` — 2026-09-28T16:54:21+03:00 — R5 E9: reconcile rooted dual-Fano with E10 and semantic terminals
- `eee109833b13` — 2026-09-28T16:14:02+03:00 — R5 E9: add CI for rooted dual-Fano source controls
- `89f5f64e60da` — 2026-09-28T16:13:36+03:00 — R5 E9: add exact rooted dual-Fano source census
- `cd4ee9ab1d43` — 2026-09-28T16:11:50+03:00 — R5 E9: extend syndrome terminal to single-odd dual-Fano criterion
- `a0dd1e8d1135` — 2026-09-28T15:42:56+03:00 — R5 E9: add CI for rooted F7* source controls
- `9d73742c3b32` — 2026-09-28T15:42:43+03:00 — R5 E9: add exact rooted F7* source-control census
- `2f01102867a2` — 2026-09-28T15:42:04+03:00 — R5 E9: freeze rooted F7* source controls
- `c5a42f73d972` — 2026-09-28T15:34:05+03:00 — R5 E9: sync semantic checkpoint to rooted F7* syndrome gate
- `b0db547849a7` — 2026-09-28T15:25:40+03:00 — R5 E9: add CI for KS theta-equality countercarrier
- `8e940bc0e949` — 2026-09-28T15:25:19+03:00 — R5 E9: add checker for KS theta-equality countercarrier
- `721f3b8056f8` — 2026-09-28T15:24:59+03:00 — R5 E9: add CI for rooted MFMC syndrome terminal
- `c817538fbd83` — 2026-09-28T15:24:29+03:00 — R5 E9: build linear-cubic KS theta-equality countercarrier
- `efa672ef4efa` — 2026-09-28T15:24:26+03:00 — R5 E9: add rooted MFMC syndrome regression checker
- `de90927bb8a0` — 2026-09-28T15:23:35+03:00 — R5 E9: extend syndrome terminal to rooted MFMC matroids
- `b9b36579fd77` — 2026-09-28T15:21:42+03:00 — R5 E9: add CI for prime-tower augmented regularity
- `5235e35582af` — 2026-09-28T15:21:31+03:00 — R5 E9: add regression for prime-tower augmented regularity
- `4d8153140aed` — 2026-09-28T15:20:35+03:00 — R5 E9: prove augmented regularity of the UNSAT prime tower
- `02aa589f4dba` — 2026-09-28T15:10:55+03:00 — R5 E9: add CI for augmented regular-matroid syndrome terminal
- `8cdb09dbf7cf` — 2026-09-28T15:10:42+03:00 — R5 E9: add exact regression for augmented regular-matroid terminal
- `b9e7fd4f58ab` — 2026-09-28T15:10:02+03:00 — R5 E9: prove augmented-regular-matroid polynomial syndrome terminal
- `f1bdc0616e38` — 2026-09-28T14:57:52+03:00 — R5 E9: synchronize semantic checkpoint after global representation barriers
- `ad3ccb96cbd4` — 2026-09-28T14:54:59+03:00 — R5 E9: add CI for PolaritySAT hostile donor falsifier
- `ba193be31c95` — 2026-09-28T14:54:20+03:00 — R5 E9: add CI for singular prime h-perfect relaxation gap

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
