# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `1312a57404e4132ee69b96f0e6a887d711e3bd1a`
- **Source commit time:** `2026-09-27T22:42:30+03:00`
- **Indexed changed scientific artifacts:** `664`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `3091b7f0ef3b671ad56ea7bff718c8948be4b5e1`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `6`

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

- **Frontier:** `R5_E9_MATCHING_NORMALIZED_AFFINE_CYCLE_SYNDROME_COMPRESSION_GATE_V1`
- **Carrier:** NP-complete connected/linear cubic positive Exact-One; matching-normalized A=I+P+Q; affine parity intersect cycle-2factor independence
- Established: Exact linear cubic Positive 1-in-3 SAT is NP-complete via a constant-size linear cubic EQ3 regularization gadget.
- Established: For cubic Exact-One, Boolean SAT is exactly affine parity Ax=1 mod 2 at Hamming weight n/3.
- Established: Affine-coset global Hamming optimality is equivalent to absence of a negative binary-matroid circuit; greedy descent uses at most n improving circuits, but universal polynomial negative-circuit synthesis on the full NP-complete carrier is not an admitted free primitive.
- Established: Any cubic bipartite Levi graph admits polynomial matching normalization A=I+P+Q.
- Established: For a linear carrier, the unmatched-pair graph C_M with edges {p(i),q(i)} is a simple disjoint union of cycles.
- Established: Exact-One is exactly Ax=1 mod 2 together with supp(x) independent in C_M.
- Established: Boben adjacent/A reductions terminate structurally in a polynomial bounded-width terminal class, but exact semantic transport through arbitrary A-reduction sequences remains open.
- Established: Commuting P,Q is a closed polynomial terminal; high-nullity noncommuting families and separator-generated high-nullity families already exist, so neither commutativity nor raw nullity is universal.
- Established: Distance-regular/strongly-regular Delsarte classification results do not apply to arbitrary source conflict graphs and are forbidden as a universal spectral shortcut.

### Live split

```json
{
  "primary": {
    "goal": "Construct a deterministic polynomial exact solver for the affine-parity plus cycle-2factor-independence form, with polynomial syndrome/state compression and witness reconstruction.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Use Boben A-reduction semantic lift only if an exact polynomial-size signature algebra is proved; do not assume constant state from the one-step rank-3 relation.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Derive the exact transfer/trellis state required when eliminating each cycle component while preserving Ax=1 mod 2.
2. Prove a polynomial bound for a canonical compressed syndrome representation, or construct an explicit source-valid family falsifying that representation and abandon it.
3. If cycle-syndrome compression fails, return to A-reduction semantic transport with a polynomial-size representation target, not to a hidden SAT/negative-circuit oracle.
4. Promote E8_D1 only after one route closes SOUND, COMPLETE, TERMINATES, POLY and polynomial witness reconstruction for every instance in the NP-complete linear cubic carrier.

## Commits newer than semantic checkpoint — MUST INGEST

- `db1e5f64edd6` — 2026-09-27T21:08:57+03:00 — R5 E9: sync semantic checkpoint after cycle-2factor normalization
- `9d4047896b1d` — 2026-09-27T21:22:21+03:00 — R5 E9: freeze singular UNSAT rank-14 countercontrol
- `0211dfa54dae` — 2026-09-27T21:22:39+03:00 — R5 E9: add singular UNSAT exact regression
- `6ddc22ae29a9` — 2026-09-27T22:41:43+03:00 — R5 E9: prove EQ3 gauge-nullity UNSAT family
- `5a04104a2cb9` — 2026-09-27T22:42:17+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT regression
- `1312a57404e4` — 2026-09-27T22:42:30+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT CI

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `a5caaf99c780832a…`
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

- `1312a57404e4` — 2026-09-27T22:42:30+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT CI
- `5a04104a2cb9` — 2026-09-27T22:42:17+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT regression
- `6ddc22ae29a9` — 2026-09-27T22:41:43+03:00 — R5 E9: prove EQ3 gauge-nullity UNSAT family
- `0211dfa54dae` — 2026-09-27T21:22:39+03:00 — R5 E9: add singular UNSAT exact regression
- `9d4047896b1d` — 2026-09-27T21:22:21+03:00 — R5 E9: freeze singular UNSAT rank-14 countercontrol
- `db1e5f64edd6` — 2026-09-27T21:08:57+03:00 — R5 E9: sync semantic checkpoint after cycle-2factor normalization
- `3091b7f0ef3b` — 2026-09-27T21:07:40+03:00 — R5 E9: add cycle-2factor exact normal-form CI
- `b11a523e9d94` — 2026-09-27T20:57:58+03:00 — R5 E9: add exact cycle-2factor normal-form regression
- `590c9a6e8561` — 2026-09-27T20:57:37+03:00 — R5 E9: derive matching-normalized cycle-2factor Exact-One form
- `e27477ca9904` — 2026-09-27T19:07:29+03:00 — R5 E9: CI for linear cubic universality bridge
- `d389cb793186` — 2026-09-27T19:04:57+03:00 — R5 E9: add checker for linear cubic EQ3 regularizer
- `fd22b609cd3b` — 2026-09-27T19:04:38+03:00 — R5 E9: prove linear cubic EQ3 regularization universality bridge
- `6f1ef3b1dbd9` — 2026-09-27T17:51:17+03:00 — R5 E9: sync checkpoint after perfect-code and A-only terminal closure
- `de9c9fb16500` — 2026-09-27T17:50:25+03:00 — R5 E9: add CI for perfect-code and A-irreducible controls
- `60351fa4c091` — 2026-09-27T17:50:14+03:00 — R5 E9: add controls for A-irreducible terminal closure
- `cec70a4d9708` — 2026-09-27T17:49:43+03:00 — R5 E9: close Boben A-irreducible terminals by bounded width
- `ca73ad6b8e62` — 2026-09-27T17:48:40+03:00 — R5 E9: add checker for directed perfect-code normal form
- `245704dee837` — 2026-09-27T17:48:24+03:00 — R5 E9: add directed perfect-code normal form
- `c365d05768e6` — 2026-09-27T17:39:25+03:00 — R5 E9: compact and sync semantic checkpoint after Boben state barrier
- `12951a374240` — 2026-09-27T17:38:25+03:00 — R5 E9: add CI for Boben local state barrier
- `53906e11c112` — 2026-09-27T17:38:15+03:00 — R5 E9: add checker for Boben local bond-dimension barrier
- `ec00bb9c8181` — 2026-09-27T17:37:53+03:00 — R5 E9: prove local Boben semantic bond-dimension barrier
- `9f1e093b97d7` — 2026-09-27T17:35:07+03:00 — R5 E9: sync checkpoint after Boben semantic audit
- `43e3d0cd879d` — 2026-09-27T17:33:35+03:00 — R5 E9: add CI for Boben semantic audit
- `a3c10fffa342` — 2026-09-27T17:33:23+03:00 — R5 E9: add executable Boben semantic counterexamples

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
