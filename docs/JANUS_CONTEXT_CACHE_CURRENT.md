# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `3a592d68aa6422576da9bef08309f0e7a97d0c12`
- **Source commit time:** `2026-09-29T03:33:08+03:00`
- **Indexed changed scientific artifacts:** `903`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `05563fb285a1b2a4ae62d2a6aab0143bdbe52899`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `128`

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
- `cca768e15373` — 2026-09-29T02:38:09+03:00 — R5 E9: add integer-lattice Smith terminal
- `b0091f3de589` — 2026-09-29T02:42:33+03:00 — R5 E9: add exact Smith lattice terminal checker
- `e7364206c1f5` — 2026-09-29T02:44:13+03:00 — R5 E9: CI for integer-lattice Smith terminal
- `04d50eae81c8` — 2026-09-29T02:58:16+03:00 — R5 E9: add integer-lattice pair-projection 2-SAT terminal
- `393e7dcd1813` — 2026-09-29T02:58:54+03:00 — R5 E9: add exact pair-projection 2-SAT checker
- `3d7563c94007` — 2026-09-29T02:59:09+03:00 — R5 E9: CI for lattice pair-projection 2-SAT terminal
- `5531ffc733f4` — 2026-09-29T02:59:30+03:00 — R5 E9: reconcile Paley voltage family with SNF terminal
- `0fc2deb10cfc` — 2026-09-29T03:04:06+03:00 — R5 E9: linearize post-SNF RKPR falsifier via EQ3
- `cd36a8f5ca59` — 2026-09-29T03:06:05+03:00 — R5 E9: prove Paley free-orbit post-RKPR linear nullity barrier
- `e49052311fb1` — 2026-09-29T03:06:50+03:00 — R5 E9: add exact Paley free-orbit structural checker
- `d31bf97c214d` — 2026-09-29T03:07:01+03:00 — R5 E9: add Paley free-orbit barrier CI
- `55ca05acf362` — 2026-09-29T03:07:15+03:00 — R5 E9: record Paley free-orbit barrier receipt
- `760c65707859` — 2026-09-29T03:07:32+03:00 — R5 E9: open gradient quotient next gate
- `e5f4f950e9d0` — 2026-09-29T03:07:43+03:00 — R5 E9: add Paley gradient quotient control
- `4fdea0fb9a4a` — 2026-09-29T03:08:41+03:00 — R5 E9: prove gradient-exact kernel Z3 phase polynomial island
- `9ad821f7385e` — 2026-09-29T03:08:59+03:00 — R5 E9: add gradient-exact Z3 phase checker
- `8d3c7a3d1ebb` — 2026-09-29T03:09:09+03:00 — R5 E9: add gradient-exact Z3 phase island CI
- `759d63bde7e3` — 2026-09-29T03:09:48+03:00 — temporary marker
- `df0b241799d3` — 2026-09-29T03:10:29+03:00 — R5 E9: fix integer-potential step in gradient-phase proof
- `f6e5699f8395` — 2026-09-29T03:10:36+03:00 — remove temporary gradient-phase marker
- `f60dd06b98a6` — 2026-09-29T03:11:34+03:00 — R5 E9: add exact checker for EQ3-linearized pair2 strict control
- `00bcfd88b855` — 2026-09-29T03:11:51+03:00 — R5 E9: CI for EQ3-linearized post-SNF/RKPR pair2 control
- `ecdd65478a60` — 2026-09-29T03:14:23+03:00 — R5 E9: prove Paley full-orbit post-RKPR sqrt-nullity barrier
- `35f03d9aa7d3` — 2026-09-29T03:15:26+03:00 — R5 E9: add exact Paley full-orbit barrier checker
- `18f292477e89` — 2026-09-29T03:15:39+03:00 — R5 E9: add Paley full-orbit sqrt-nullity CI
- `5cc78daf06c5` — 2026-09-29T03:18:14+03:00 — R5 E9: falsify pair2 completeness and add triple mod7 terminal
- `4be8ce563307` — 2026-09-29T03:21:52+03:00 — R5 E9: falsify pair-projection completeness on linear-cubic carrier
- `0eed3744c479` — 2026-09-29T03:22:59+03:00 — R5 E9: add exact pair2 completeness falsifier checker
- `17b25b7a9d80` — 2026-09-29T03:23:56+03:00 — R5 E9: add CI for pair2 completeness falsifier
- `5983c4a70e70` — 2026-09-29T03:25:30+03:00 — R5 E9: add integer-lattice L1 Graver augmentation gate
- `13432a47778c` — 2026-09-29T03:25:45+03:00 — R5 E9: falsify pair2 completeness on linear cubic carrier
- `904a8ba22cfe` — 2026-09-29T03:26:06+03:00 — R5 E9: add exact L1 Graver gate checker
- `71334111ff4b` — 2026-09-29T03:26:20+03:00 — R5 E9: add CI for integer-lattice L1 Graver gate
- `2adcc87e4cdb` — 2026-09-29T03:26:50+03:00 — R5 E9: add exact pair2 completeness falsifier checker
- `466b73317f94` — 2026-09-29T03:27:00+03:00 — R5 E9: add pair2 completeness falsifier CI
- `49d3347b88b0` — 2026-09-29T03:28:57+03:00 — R5 E9: prove Exact-One3 projection-polymorphism bounded-width barrier
- `78b289dd6f0f` — 2026-09-29T03:29:15+03:00 — R5 E9: add exact finite polymorphism regression
- `bdef754555b4` — 2026-09-29T03:29:29+03:00 — R5 E9: add CI for projection-polymorphism barrier
- `3a592d68aa64` — 2026-09-29T03:33:08+03:00 — R5 E9: prove F2^4 five-line spread UNSAT terminal

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
- `0eed3744c479` — 2026-09-29T03:22:59+03:00 — R5 E9: add exact pair2 completeness falsifier checker
- `4be8ce563307` — 2026-09-29T03:21:52+03:00 — R5 E9: falsify pair-projection completeness on linear-cubic carrier
- `5cc78daf06c5` — 2026-09-29T03:18:14+03:00 — R5 E9: falsify pair2 completeness and add triple mod7 terminal
- `18f292477e89` — 2026-09-29T03:15:39+03:00 — R5 E9: add Paley full-orbit sqrt-nullity CI
- `35f03d9aa7d3` — 2026-09-29T03:15:26+03:00 — R5 E9: add exact Paley full-orbit barrier checker
- `ecdd65478a60` — 2026-09-29T03:14:23+03:00 — R5 E9: prove Paley full-orbit post-RKPR sqrt-nullity barrier
- `00bcfd88b855` — 2026-09-29T03:11:51+03:00 — R5 E9: CI for EQ3-linearized post-SNF/RKPR pair2 control
- `f60dd06b98a6` — 2026-09-29T03:11:34+03:00 — R5 E9: add exact checker for EQ3-linearized pair2 strict control
- `f6e5699f8395` — 2026-09-29T03:10:36+03:00 — remove temporary gradient-phase marker
- `df0b241799d3` — 2026-09-29T03:10:29+03:00 — R5 E9: fix integer-potential step in gradient-phase proof
- `759d63bde7e3` — 2026-09-29T03:09:48+03:00 — temporary marker
- `8d3c7a3d1ebb` — 2026-09-29T03:09:09+03:00 — R5 E9: add gradient-exact Z3 phase island CI
- `9ad821f7385e` — 2026-09-29T03:08:59+03:00 — R5 E9: add gradient-exact Z3 phase checker
- `4fdea0fb9a4a` — 2026-09-29T03:08:41+03:00 — R5 E9: prove gradient-exact kernel Z3 phase polynomial island

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
