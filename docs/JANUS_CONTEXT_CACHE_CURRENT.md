# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `b73cdfbc97b0781826b0fbe92bebcc5e00c7fac5`
- **Source commit time:** `2026-09-28T02:15:12+03:00`
- **Indexed changed scientific artifacts:** `672`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `efed2c7e3fcd9ab03407b02fe9ba6b01362e1719`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `14`

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

- **Frontier:** `R5_E9_UNIVERSAL_SEMANTIC_COMPRESSION_DUAL_ROUTE_V1`
- **Carrier:** NP-complete connected/linear cubic positive Exact-One; exact forms include A=I+P+Q, affine parity intersect cycle-2factor independence, and Boben-reducible v3 Levi structure
- Established: Exact linear cubic Positive 1-in-3 SAT is NP-complete via a constant-size linear cubic EQ3 regularization gadget.
- Established: For cubic Exact-One, Boolean SAT is exactly affine parity Ax=1 mod 2 at Hamming weight n/3.
- Established: Affine-coset global Hamming optimality is equivalent to absence of a negative binary-matroid circuit; greedy descent uses at most n improving circuits, but universal polynomial negative-circuit synthesis on the full NP-complete carrier is not an admitted free primitive.
- Established: Any cubic bipartite Levi graph admits polynomial matching normalization A=I+P+Q.
- Established: For a linear carrier, the unmatched-pair graph C_M with edges {p(i),q(i)} is a simple disjoint union of cycles.
- Established: Exact-One is exactly Ax=1 mod 2 together with supp(x) independent in C_M.
- Established: A connected linear cubic rank-14 n=15 carrier is singular over Q but Exact-One UNSAT; singularity or lambda_min=-3 is not sufficient for SAT.
- Established: The EQ3 regularizer has a terminal-zero local F2 kernel mode; recursively regularizing the connected linear-cubic UNSAT n=15 seed gives n_t=15*10^t and nullity_F2>=n_t/10 while preserving UNSAT. Raw F2 nullity is not a SAT/progress measure.
- Established: The local-swap family is SAT, connected, linear cubic, primitive for every m>=3, and has nullity_Q>=n/3. Primitive group action does not imply O(log n) rational nullity, so the primitive/imprimitive nullity router is closed as stated.
- Established: The older Harries n_t=35*2^t high-nullity family is automatically Exact-One UNSAT because 3 does not divide n_t; retain it only as a structural stress family, not a SAT-side obstruction.
- Established: Boben adjacent/A reductions terminate structurally in a polynomial bounded-width terminal class, but exact semantic transport through arbitrary A-reduction sequences remains open.
- Established: One adjacent Boben semantic contraction has minimum hidden bond dimension 3; a 2-state wire lift is impossible. The local relation is a three-entry partial permutation, but global closure under repeated A-steps is unproved.
- Established: Krom plus genuinely high-width affine boundary is already universal in the existing APAC sharpness theorem; the affine-cycle residual must not be relabeled as ordinary 2-SAT.
- Established: Commuting P,Q is a closed polynomial terminal; noncommuting high-nullity primitive SAT families exist, so commutativity, primitivity and raw nullity are not universal currencies.

### Live split

```json
{
  "primary": {
    "goal": "Construct a deterministic polynomial exact solver for affine parity plus cycle-2factor independence, using a provably polynomial semantic/syndrome representation rather than raw syndrome enumeration or a negative-circuit oracle.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Exploit universal Boben A-reducibility only if exact semantic information can be carried through arbitrary adjacent reductions with polynomial total state and polynomial witness reconstruction.",
    "status": "OPEN"
  }
}
```

### Next attack

1. For the affine-cycle form, derive a canonical representation of the Krom-over-affine boundary that uses the source relations b_i+b_p(i)+b_q(i)=0; test and prove polynomial closure, not generic high-width Krom assumptions.
2. For Boben A-reduction, exploit the exact three-state partial-permutation structure of one adjacent contraction and determine whether repeated reductions close under a polynomial signature algebra; abandon any representation on an explicit growing family if it does not.
3. Use exact-matching / graph-lift machinery only when the number of group/syndrome constraints is proved bounded or when the external deterministic Bipartite Exact Matching claim is independently validated; do not import it as an oracle.
4. Do not reopen raw-nullity, singularity, commutativity-only, or primitive/imprimitive routers.
5. Promote E8_D1 only after one route closes SOUND, COMPLETE, TERMINATES, POLY and polynomial witness reconstruction for every instance in the NP-complete linear cubic carrier.

## Commits newer than semantic checkpoint — MUST INGEST

- `774aef861935` — 2026-09-27T22:57:11+03:00 — R5 E9: sync semantic checkpoint after nullity route closures
- `9b45c55ee542` — 2026-09-27T23:12:34+03:00 — R5 E9: freeze EQ3 gauge-nullity UNSAT counterfamily
- `adbeee3ced22` — 2026-09-27T23:12:55+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT regression
- `a8f333bf61ec` — 2026-09-27T23:13:03+03:00 — R5 E9: add CI for EQ3 gauge-nullity UNSAT family
- `b6192d85e5b5` — 2026-09-27T23:13:39+03:00 — R5 E9: remove duplicate gauge-nullity theorem
- `e71898a2e208` — 2026-09-27T23:13:44+03:00 — R5 E9: remove duplicate gauge-nullity checker
- `591e8e81e20e` — 2026-09-27T23:13:51+03:00 — R5 E9: remove duplicate gauge-nullity workflow
- `c09c01be5e90` — 2026-09-27T23:24:12+03:00 — R5 E9: freeze two-step Boben state-4 barrier
- `44547a4ce762` — 2026-09-27T23:24:38+03:00 — R5 E9: add two-step Boben state-4 replay
- `ac934d02ef73` — 2026-09-27T23:24:52+03:00 — R5 E9: add CI for two-step Boben state-4 barrier
- `a5e7fcf80d9f` — 2026-09-27T23:35:05+03:00 — R5 E9: repair legal Boben two-step replay
- `64f0d8af5ab7` — 2026-09-27T23:35:29+03:00 — R5 E9: correct legal Boben two-step certificate
- `820e1045b841` — 2026-09-27T23:46:39+03:00 — R5 E9: rule out common EQ3/Exact1 matchgate basis
- `b73cdfbc97b0` — 2026-09-28T02:15:12+03:00 — R5 E9: prove EQ3 local gauge quotient returns source hardness

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `56f439ebb7566bbb…`
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

- `b73cdfbc97b0` — 2026-09-28T02:15:12+03:00 — R5 E9: prove EQ3 local gauge quotient returns source hardness
- `820e1045b841` — 2026-09-27T23:46:39+03:00 — R5 E9: rule out common EQ3/Exact1 matchgate basis
- `64f0d8af5ab7` — 2026-09-27T23:35:29+03:00 — R5 E9: correct legal Boben two-step certificate
- `a5e7fcf80d9f` — 2026-09-27T23:35:05+03:00 — R5 E9: repair legal Boben two-step replay
- `ac934d02ef73` — 2026-09-27T23:24:52+03:00 — R5 E9: add CI for two-step Boben state-4 barrier
- `44547a4ce762` — 2026-09-27T23:24:38+03:00 — R5 E9: add two-step Boben state-4 replay
- `c09c01be5e90` — 2026-09-27T23:24:12+03:00 — R5 E9: freeze two-step Boben state-4 barrier
- `591e8e81e20e` — 2026-09-27T23:13:51+03:00 — R5 E9: remove duplicate gauge-nullity workflow
- `e71898a2e208` — 2026-09-27T23:13:44+03:00 — R5 E9: remove duplicate gauge-nullity checker
- `b6192d85e5b5` — 2026-09-27T23:13:39+03:00 — R5 E9: remove duplicate gauge-nullity theorem
- `a8f333bf61ec` — 2026-09-27T23:13:03+03:00 — R5 E9: add CI for EQ3 gauge-nullity UNSAT family
- `adbeee3ced22` — 2026-09-27T23:12:55+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT regression
- `9b45c55ee542` — 2026-09-27T23:12:34+03:00 — R5 E9: freeze EQ3 gauge-nullity UNSAT counterfamily
- `774aef861935` — 2026-09-27T22:57:11+03:00 — R5 E9: sync semantic checkpoint after nullity route closures
- `efed2c7e3fcd` — 2026-09-27T22:55:37+03:00 — R5 E9: add primitive local-swap family CI
- `94b1075a4d29` — 2026-09-27T22:55:29+03:00 — R5 E9: add primitive local-swap family regression
- `afc1ed0fe575` — 2026-09-27T22:55:00+03:00 — R5 E9: prove primitive linear-nullity local-swap family
- `1312a57404e4` — 2026-09-27T22:42:30+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT CI
- `5a04104a2cb9` — 2026-09-27T22:42:17+03:00 — R5 E9: add EQ3 gauge-nullity UNSAT regression
- `6ddc22ae29a9` — 2026-09-27T22:41:43+03:00 — R5 E9: prove EQ3 gauge-nullity UNSAT family
- `0211dfa54dae` — 2026-09-27T21:22:39+03:00 — R5 E9: add singular UNSAT exact regression
- `9d4047896b1d` — 2026-09-27T21:22:21+03:00 — R5 E9: freeze singular UNSAT rank-14 countercontrol
- `db1e5f64edd6` — 2026-09-27T21:08:57+03:00 — R5 E9: sync semantic checkpoint after cycle-2factor normalization
- `3091b7f0ef3b` — 2026-09-27T21:07:40+03:00 — R5 E9: add cycle-2factor exact normal-form CI
- `b11a523e9d94` — 2026-09-27T20:57:58+03:00 — R5 E9: add exact cycle-2factor normal-form regression

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
