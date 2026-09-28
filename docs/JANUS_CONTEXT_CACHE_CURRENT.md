# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `d5cd5db5a3816b91acf6788ae4bad03e940dbf06`
- **Source commit time:** `2026-09-29T02:30:33+03:00`
- **Indexed changed scientific artifacts:** `867`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `05563fb285a1b2a4ae62d2a6aab0143bdbe52899`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `94`

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

- `79e3015cd010` — 2026-09-28T20:45:03+03:00 — R5 E9: kill monotone Tukey tope descent on PG15 SAT
- `11793acebcaa` — 2026-09-28T20:45:36+03:00 — R5 E9: add PG15 monotone tope-descent countercontrol
- `bd6205f45e17` — 2026-09-28T20:45:45+03:00 — R5 E9: add CI for Tukey tope-descent barrier
- `f510fd4789aa` — 2026-09-28T20:49:25+03:00 — R5 E9: bound source-kernel augmenting paths by tope geodesics
- `ba8c9de2ad21` — 2026-09-28T20:49:58+03:00 — R5 E9: add source-kernel tope geodesic regression
- `c5178dad5b94` — 2026-09-28T20:52:14+03:00 — R5 E9: add CI for source-kernel tope geodesic bound
- `4d46fc88a5cb` — 2026-09-28T20:53:19+03:00 — R5 E9: prove PG15 kernel boundary is nonconvex and nongated
- `4de044cf8440` — 2026-09-28T20:53:54+03:00 — R5 E9: add PG15 boundary nonconvexity regression
- `a5030a34807a` — 2026-09-28T20:54:11+03:00 — R5 E9: add CI for kernel-boundary nonconvexity barrier
- `e7f9f0f7a0d0` — 2026-09-28T20:57:00+03:00 — R5 E9: isolate polynomial source-kernel navigation shell
- `f318557a9306` — 2026-09-28T20:57:31+03:00 — R5 E9: add navigation-shell finite binding
- `19f903e120d5` — 2026-09-28T20:57:39+03:00 — R5 E9: add CI for source-kernel navigation shell
- `5d7f1da66f7a` — 2026-09-28T20:58:18+03:00 — R5 E9: bind exact PG15 interval vector in nonconvex barrier
- `6989b0f9d519` — 2026-09-28T21:04:01+03:00 — R5 E9: add rational-kernel projective ratio pinning quotient
- `54774f50cd5a` — 2026-09-28T21:10:11+03:00 — R5 E9: freeze kernel-tope greedy local-minimum barrier
- `e1062ed9da53` — 2026-09-28T21:10:40+03:00 — R5 E9: add exact PG15 tope local-minimum checker
- `bec918c31cfa` — 2026-09-28T21:10:50+03:00 — R5 E9: add CI for kernel-tope greedy barrier
- `96c5cd2e81f3` — 2026-09-28T21:14:04+03:00 — R5 E9: repair tope adjacency for parallel kernel hyperplanes
- `aa237e2a4c76` — 2026-09-28T21:14:42+03:00 — R5 E9: verify projective hyperplane classes in greedy barrier
- `a78056a75165` — 2026-09-28T21:16:09+03:00 — R5 E9: certify exact boundary distances from PG15 trap
- `71be1c58613f` — 2026-09-28T21:23:44+03:00 — R5 E9: prove raw tope-radius 2-lift amplifier
- `5b802dab7ee7` — 2026-09-28T21:24:23+03:00 — R5 E9: add raw-radius 2-lift amplifier regression
- `29b9f62a0fb2` — 2026-09-28T21:24:31+03:00 — R5 E9: add CI for raw-radius 2-lift amplifier
- `d8e60cc564d2` — 2026-09-28T21:35:08+03:00 — R5 E9: add exact geometric tope-radius stress controls
- `c8f67b77b847` — 2026-09-28T21:36:22+03:00 — R5 E9: bind geometric augmentation meta-theorem and prime-tower stress
- `9390f66e6134` — 2026-09-28T21:36:29+03:00 — R5 E9: add CI for geometric tope-radius stress
- `8012c8d052b3` — 2026-09-28T21:43:35+03:00 — R5 E9: prove linear projective escape-radius prime tower
- `7aa19ec97edd` — 2026-09-28T21:44:26+03:00 — R5 E9: add exact recurrence replay through n120
- `f6a098bddb52` — 2026-09-28T21:44:33+03:00 — R5 E9: add CI for projective escape-radius recurrence
- `789c1400869c` — 2026-09-28T21:55:26+03:00 — R5 E9: reconcile RKPR with prime tower and EQ3 hardness image
- `46f9a6f0f774` — 2026-09-28T21:55:50+03:00 — R5 E9: add RKPR post-quotient reconciliation replay
- `97244b0e6985` — 2026-09-28T21:55:57+03:00 — R5 E9: add CI for RKPR post-quotient reconciliation
- `55490108beea` — 2026-09-28T22:45:25+03:00 — R5 E9: add rational-tope defect syndrome projective filter
- `52a7d50f280c` — 2026-09-28T22:46:14+03:00 — R5 E9: add exact projective parity filter checker
- `afe2e97cc3df` — 2026-09-28T22:46:23+03:00 — R5 E9: add CI for projective parity filter
- `c7fb34355b27` — 2026-09-28T22:52:50+03:00 — R5 E9: sharpen projective parity filter with Smith torsion identity
- `36577823df8b` — 2026-09-28T23:16:58+03:00 — R5 E9: prove two-edge SAT lift survives RKPR with linear nullity
- `75f7ac08250f` — 2026-09-28T23:17:59+03:00 — R5 E9: add exact RKPR-survival regression for two-edge SAT lifts
- `3d572a8026d1` — 2026-09-28T23:18:07+03:00 — R5 E9: add CI for two-edge SAT RKPR survival
- `beaf84b5ed06` — 2026-09-28T23:53:35+03:00 — R5 E9: prove primitive linear-nullity local-swap barrier
- `d9d54a1f2bd3` — 2026-09-28T23:54:05+03:00 — R5 E9: add exact primitive local-swap barrier checker
- `3d7a21320533` — 2026-09-28T23:54:11+03:00 — R5 E9: add CI for primitive local-swap barrier
- `e10bd1f522eb` — 2026-09-29T00:19:35+03:00 — R5 E9: prove connected commuting two-perm nullity collapse
- `a37dc3f4559f` — 2026-09-29T00:20:00+03:00 — R5 E9: add exact checker for commuting nullity collapse
- `3bf5f4708c72` — 2026-09-29T00:20:15+03:00 — R5 E9: add CI for commuting nullity collapse
- `6743f72cba8d` — 2026-09-29T00:23:19+03:00 — R5 E9: prove linear cubic trace rank nullity bound
- `9c9d5da7fde0` — 2026-09-29T00:23:48+03:00 — R5 E9: add exact checker for linear cubic trace rank bound
- `c749c8ac5e8f` — 2026-09-29T00:24:03+03:00 — R5 E9: add CI for linear cubic trace rank bound
- `35fd7f0afe3d` — 2026-09-29T00:32:53+03:00 — R5 E9: add Paley11 post-RKPR linear nullity-10 control
- `a479c74e7203` — 2026-09-29T00:33:20+03:00 — R5 E9: add exact Paley11 post-RKPR checker
- `462088b2b0e2` — 2026-09-29T00:33:27+03:00 — R5 E9: add CI for Paley11 post-RKPR control
- `198faf5d844c` — 2026-09-29T00:38:40+03:00 — R5 E9: prove infinite Paley post-RKPR sqrt-nullity family
- `f1558aad3c32` — 2026-09-29T00:39:30+03:00 — R5 E9: add exact regression for Paley sqrt-nullity family
- `bee44236bd7f` — 2026-09-29T00:39:42+03:00 — R5 E9: add CI for Paley sqrt-nullity family
- `9ebadc90e883` — 2026-09-29T00:42:29+03:00 — R5 E9: prove graphic-kernel Z3 phase solver island
- `09347d93a329` — 2026-09-29T00:42:59+03:00 — R5 E9: add checker for graphic-kernel Z3 solver island
- `260d77cc956a` — 2026-09-29T00:43:08+03:00 — R5 E9: add CI for graphic-kernel Z3 solver island
- `b605330bda4b` — 2026-09-29T00:46:12+03:00 — R5 E9: close exact graphic-kernel recognition via network matrices
- `9468c6a9137f` — 2026-09-29T00:46:56+03:00 — R5 E9: add checker for exact graphic-kernel network router
- `86a4a7879253` — 2026-09-29T00:47:39+03:00 — R5 E9: add CI for exact graphic-kernel network router
- `d7256243325a` — 2026-09-29T01:14:00+03:00 — R5 E9: add exact cycle-kernel flow solver router
- `7ecda3714cbc` — 2026-09-29T01:14:30+03:00 — R5 E9: add cycle-kernel flow router regression
- `669d849f579e` — 2026-09-29T01:14:37+03:00 — R5 E9: add CI for cycle-kernel flow router
- `3d3b68e7b930` — 2026-09-29T01:20:48+03:00 — R5 E9: add bidirected cycle-kernel binet router
- `0bf3e91ce41f` — 2026-09-29T01:22:24+03:00 — R5 E9: add bidirected binet router regression
- `bb16a1cb46e0` — 2026-09-29T01:22:32+03:00 — R5 E9: add CI for bidirected binet router
- `11d7cf104b90` — 2026-09-29T01:32:40+03:00 — R5 E9: add exact TU-rowspace Boolean LP router
- `01d26b711a0b` — 2026-09-29T01:33:21+03:00 — R5 E9: add TU-rowspace router regression
- `84429eb3a166` — 2026-09-29T01:33:29+03:00 — R5 E9: add CI for TU-rowspace Boolean LP router
- `42b88fff70e5` — 2026-09-29T01:39:56+03:00 — R5 E10A: seal deterministic optimal-face blossom parity DP
- `d512cd1a28dd` — 2026-09-29T01:40:48+03:00 — Remove duplicate optimal-face blossom parity theorem
- `d3d16c724f0d` — 2026-09-29T01:43:50+03:00 — R5 E10A: strict-max promise universal padding barrier
- `3526f6b46384` — 2026-09-29T01:47:00+03:00 — R5 E10A: add strict-max padding barrier exact checker
- `090e601e1fb2` — 2026-09-29T01:47:16+03:00 — R5 E10A: add strict-max padding barrier CI
- `b5accb7d274f` — 2026-09-29T01:48:10+03:00 — R5 E10A: enable push replay for strict-max padding barrier
- `5feabff534f6` — 2026-09-29T01:55:04+03:00 — Bootstrap PA-0029 NM-0033 arithmetic repair
- `ab9864e27230` — 2026-09-29T01:57:29+03:00 — Diagnose PA-0029 NM-0033 payload transport
- `48c38517c2a1` — 2026-09-29T02:29:26+03:00 — R5 E9: prove Paley voltage post-RKPR linear-nullity family
- `0e847f6d28ad` — 2026-09-29T02:30:20+03:00 — R5 E9: add exact checker for Paley voltage nullity family
- `d5cd5db5a381` — 2026-09-29T02:30:33+03:00 — R5 E9: CI for Paley voltage nullity family

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `d2b85f2b6022053a237bbd0d20fa9f6610dfe749b394b6d680696c9d84c22d02`
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

- `d5cd5db5a381` — 2026-09-29T02:30:33+03:00 — R5 E9: CI for Paley voltage nullity family
- `0e847f6d28ad` — 2026-09-29T02:30:20+03:00 — R5 E9: add exact checker for Paley voltage nullity family
- `48c38517c2a1` — 2026-09-29T02:29:26+03:00 — R5 E9: prove Paley voltage post-RKPR linear-nullity family
- `ab9864e27230` — 2026-09-29T01:57:29+03:00 — Diagnose PA-0029 NM-0033 payload transport
- `5feabff534f6` — 2026-09-29T01:55:04+03:00 — Bootstrap PA-0029 NM-0033 arithmetic repair
- `b5accb7d274f` — 2026-09-29T01:48:10+03:00 — R5 E10A: enable push replay for strict-max padding barrier
- `090e601e1fb2` — 2026-09-29T01:47:16+03:00 — R5 E10A: add strict-max padding barrier CI
- `3526f6b46384` — 2026-09-29T01:47:00+03:00 — R5 E10A: add strict-max padding barrier exact checker
- `d3d16c724f0d` — 2026-09-29T01:43:50+03:00 — R5 E10A: strict-max promise universal padding barrier
- `d512cd1a28dd` — 2026-09-29T01:40:48+03:00 — Remove duplicate optimal-face blossom parity theorem
- `42b88fff70e5` — 2026-09-29T01:39:56+03:00 — R5 E10A: seal deterministic optimal-face blossom parity DP
- `84429eb3a166` — 2026-09-29T01:33:29+03:00 — R5 E9: add CI for TU-rowspace Boolean LP router
- `01d26b711a0b` — 2026-09-29T01:33:21+03:00 — R5 E9: add TU-rowspace router regression
- `11d7cf104b90` — 2026-09-29T01:32:40+03:00 — R5 E9: add exact TU-rowspace Boolean LP router
- `bb16a1cb46e0` — 2026-09-29T01:22:32+03:00 — R5 E9: add CI for bidirected binet router
- `0bf3e91ce41f` — 2026-09-29T01:22:24+03:00 — R5 E9: add bidirected binet router regression
- `3d3b68e7b930` — 2026-09-29T01:20:48+03:00 — R5 E9: add bidirected cycle-kernel binet router
- `669d849f579e` — 2026-09-29T01:14:37+03:00 — R5 E9: add CI for cycle-kernel flow router
- `7ecda3714cbc` — 2026-09-29T01:14:30+03:00 — R5 E9: add cycle-kernel flow router regression
- `d7256243325a` — 2026-09-29T01:14:00+03:00 — R5 E9: add exact cycle-kernel flow solver router
- `86a4a7879253` — 2026-09-29T00:47:39+03:00 — R5 E9: add CI for exact graphic-kernel network router
- `9468c6a9137f` — 2026-09-29T00:46:56+03:00 — R5 E9: add checker for exact graphic-kernel network router
- `b605330bda4b` — 2026-09-29T00:46:12+03:00 — R5 E9: close exact graphic-kernel recognition via network matrices
- `260d77cc956a` — 2026-09-29T00:43:08+03:00 — R5 E9: add CI for graphic-kernel Z3 solver island
- `09347d93a329` — 2026-09-29T00:42:59+03:00 — R5 E9: add checker for graphic-kernel Z3 solver island

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
