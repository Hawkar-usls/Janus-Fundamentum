# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `ef6ee2aa6bf3054b600aefa8fb2eaaea73a7e457`
- **Source commit time:** `2026-09-29T03:57:02+03:00`
- **Indexed changed scientific artifacts:** `916`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `c9873372bcc260aa17f299188b55f528c9b2a0a1`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `8`

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

- **Frontier:** `R5_E9_LINEAR_CUBIC_SOURCE_TRADE_AUGMENTATION_GATE_V1`
- **Carrier:** connected square linear-cubic Positive-1-in-3 source after exact integer-lattice membership; solve the global L1/odd-parity affine-lattice optimization rather than any fixed local projection hierarchy
- Established: Exact linear-cubic Positive 1-in-3 SAT is NP-complete via the frozen constant-size EQ3 regularizer with polynomial witness transfer.
- Established: Integer-lattice membership Ax=1 over Z is polynomial by Smith/Hermite methods and is a sound UNSAT terminal.
- Established: For L_A={z in Z^n:Az=1}, F(z)=sum_i |2z_i-1| has F(z)>=n with equality exactly on Boolean z; therefore Exact-One SAT iff min_{L_A} F=n, and UNSAT has exact gap at least 2.
- Established: Any initial integer lattice witness yields a polynomial-bit finite box containing an F-minimizer.
- Established: Known Graver augmentation gives a polynomial number of iterations conditional on access to a suitable improving/best Graver direction; constructing such a direction for the unrestricted linear-cubic carrier remains open.
- Established: Full unary/pair integer-lattice projection consistency is not complete on the exact connected square linear-cubic carrier.
- Established: Empty Boolean triple projection is a sound polynomial terminal but is not complete: an explicit 480-variable connected square linear-cubic UNSAT source passes SNF, RKPR, full pair2, and all empty-triple tests.
- Established: All finitary polymorphisms of the raw Boolean EXACT_ONE_3 relation are coordinate projections; ordinary bounded-width/fixed-local-consistency CSP methods therefore cannot decide the full carrier.
- Established: Network/graphic/binet/TU-rowspace, balanced, separator, low-nullity, commuting, phase and other certified islands remain polynomial terminals but do not cover the universal residual.
- Established: The EQ3 NP-hard image contains m pairwise row/column-disjoint determinant-2 internal minors on N=10m variables; hence it has a subdeterminant of magnitude 2^m=2^(N/10) and needs at least m=N/10 row/column deletions to become TU.
- Established: Therefore bounded-subdeterminant and O(1)-deletion-to-TU/network/cographic structure are not automatic consequences of cubic-linearity on the hard image.
- Established: Polynomial-dimensional bilinear annihilation summaries, direct projected-delta-matroid endpoint encodings, fixed-modulus counting, local bond-dimension summaries, raw nullity/singularity, and local EQ3 gauge quotients are frozen anti-loop routes.
- Established: P_VS_NP remains OPEN and E8_D1 remains EMPTY.

### Live split

```json
{
  "primary": {
    "goal": "Construct a deterministic polynomial SOURCE_TRADE_AUGMENT(A,z,l,u) that either finds a feasible integer kernel trade strictly decreasing F(z)=sum_i|2z_i-1| or certifies global F-optimality, without enumerating an exponential Graver basis.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Exploit the equivalent odd-parity coset form Ay=-1, y in (2Z+1)^n, minimize ||y||_1; isolate a source-specific balanced signed-trade or parity-flow structure that survives the EQ3 determinant packing barrier.",
    "status": "OPEN"
  },
  "reserve": {
    "goal": "Use representation-changing root-aware/projective/matroid decomposition only if it gives a polynomially discoverable contraction with exact witness lifting and does not merely repackage the original NP-hard carrier.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Materialize and prove the exact odd-L1 parity-coset normal form y=2z-1: Ay=-1, y odd, F(z)=||y||_1; derive that every integer kernel trade has zero coordinate sum in the cubic carrier.
2. Recast an improving Graver step as a balanced sign-compatible source trade and separate the already-polynomial network/TU/graphic subcase from the true non-network residual.
3. Use the PG15 UNSAT optimum-17 control to falsify naive rational-direction scaling/rounding: a continuous improving direction toward 1/3 can overshoot after integer scaling.
4. Search current literature and the repo for a polynomial source-specific circuit/trade oracle that tolerates unbounded determinants; reject any result whose tractability depends on bounded Graver norm, bounded treedepth, bounded subdeterminants, or O(1) near-TU distance.
5. If SOURCE_TRADE_AUGMENT collapses to a known NP-hard primitive with no extra source structure, freeze it explicitly and seek a genuinely different global representation.
6. Promote E8_D1 only after SOUND+COMPLETE+TERMINATES+POLY+RECONSTRUCT hold for arbitrary 3CNF.

## Commits newer than semantic checkpoint — MUST INGEST

- `5b9b1fd3c146` — 2026-09-29T03:37:56+03:00 — R5 E9: add exact triple-empty lift falsifier checker
- `5f3f94c9ae38` — 2026-09-29T03:39:18+03:00 — R5 E9: synchronize semantic checkpoint to source-trade augmentation frontier
- `4f462a685ab4` — 2026-09-29T03:41:16+03:00 — R5 E9: derive odd-L1 parity-coset source-trade normal form
- `d40ad5b159f0` — 2026-09-29T03:41:37+03:00 — R5 E9: add exact odd-L1 source-trade regression
- `dfa150d17ee4` — 2026-09-29T03:51:47+03:00 — R5 E9: derive NAE defect-flow decomposition and positive-layer barrier
- `c86fb2ba353b` — 2026-09-29T03:52:20+03:00 — R5 E9: add exact NAE defect-flow positive-layer regression
- `ffe65f3a8ed0` — 2026-09-29T03:56:30+03:00 — R5 E9: prove exponential Graver coefficients in linear-cubic nullity-one family
- `ef6ee2aa6bf3` — 2026-09-29T03:57:02+03:00 — R5 E9: add exact exponential Graver family regression

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `d2b85f2b6022053a237bbd0d20fa9f6610dfe749b394b6d680696c9d84c22d02`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `651019114327efbf…`
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

- `ef6ee2aa6bf3` — 2026-09-29T03:57:02+03:00 — R5 E9: add exact exponential Graver family regression
- `ffe65f3a8ed0` — 2026-09-29T03:56:30+03:00 — R5 E9: prove exponential Graver coefficients in linear-cubic nullity-one family
- `c86fb2ba353b` — 2026-09-29T03:52:20+03:00 — R5 E9: add exact NAE defect-flow positive-layer regression
- `dfa150d17ee4` — 2026-09-29T03:51:47+03:00 — R5 E9: derive NAE defect-flow decomposition and positive-layer barrier
- `d40ad5b159f0` — 2026-09-29T03:41:37+03:00 — R5 E9: add exact odd-L1 source-trade regression
- `4f462a685ab4` — 2026-09-29T03:41:16+03:00 — R5 E9: derive odd-L1 parity-coset source-trade normal form
- `5f3f94c9ae38` — 2026-09-29T03:39:18+03:00 — R5 E9: synchronize semantic checkpoint to source-trade augmentation frontier
- `5b9b1fd3c146` — 2026-09-29T03:37:56+03:00 — R5 E9: add exact triple-empty lift falsifier checker
- `c9873372bcc2` — 2026-09-29T03:36:53+03:00 — R5 E9: falsify triple-empty completeness via exact two-edge lift
- `9f37d12b95b4` — 2026-09-29T03:34:48+03:00 — R5 E9: add CI for EQ3 determinant packing barrier
- `5d904345553f` — 2026-09-29T03:34:32+03:00 — R5 E9: add exact EQ3 determinant packing checker
- `f3edd34ceb0a` — 2026-09-29T03:34:16+03:00 — R5 E9: prove exponential subdeterminant and linear TU-deletion barrier
- `ef4c165d03cf` — 2026-09-29T03:34:03+03:00 — R5 E9: add CI for five-line spread UNSAT terminal
- `fb0f43233656` — 2026-09-29T03:33:43+03:00 — R5 E9: add exact five-line spread UNSAT regression
- `3a592d68aa64` — 2026-09-29T03:33:08+03:00 — R5 E9: prove F2^4 five-line spread UNSAT terminal
- `bdef754555b4` — 2026-09-29T03:29:29+03:00 — R5 E9: add CI for projection-polymorphism barrier
- `78b289dd6f0f` — 2026-09-29T03:29:15+03:00 — R5 E9: add exact finite polymorphism regression
- `49d3347b88b0` — 2026-09-29T03:28:57+03:00 — R5 E9: prove Exact-One3 projection-polymorphism bounded-width barrier
- `466b73317f94` — 2026-09-29T03:27:00+03:00 — R5 E9: add pair2 completeness falsifier CI
- `2adcc87e4cdb` — 2026-09-29T03:26:50+03:00 — R5 E9: add exact pair2 completeness falsifier checker
- `71334111ff4b` — 2026-09-29T03:26:20+03:00 — R5 E9: add CI for integer-lattice L1 Graver gate
- `904a8ba22cfe` — 2026-09-29T03:26:06+03:00 — R5 E9: add exact L1 Graver gate checker
- `13432a47778c` — 2026-09-29T03:25:45+03:00 — R5 E9: falsify pair2 completeness on linear cubic carrier
- `5983c4a70e70` — 2026-09-29T03:25:30+03:00 — R5 E9: add integer-lattice L1 Graver augmentation gate
- `17b25b7a9d80` — 2026-09-29T03:23:56+03:00 — R5 E9: add CI for pair2 completeness falsifier

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
