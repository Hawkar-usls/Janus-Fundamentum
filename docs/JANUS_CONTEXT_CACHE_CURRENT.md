# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `e2cc859a97f7a576f6bcb09b80e67effe42cc90e`
- **Source commit time:** `2026-09-28T02:52:06+03:00`
- **Indexed changed scientific artifacts:** `683`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `f1e556b93e6e85eec5846faffb6fc3e79992a30e`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `5`

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

- **Frontier:** `R5_E9_THREE_CUT_IRREDUCIBLE_GLOBAL_CONTRACTION_GATE_V1`
- **Carrier:** NP-complete connected/linear cubic positive Exact-One; exact forms include A=I+P+Q, affine parity plus cycle-2factor independence, dual rank-3 perfect hypermatching, and grouped Levi interfaces
- Established: Exact linear cubic Positive 1-in-3 SAT is NP-complete via the constant-size linear cubic EQ3 regularization gadget.
- Established: Cubic Exact-One is exactly affine parity Ax=1 mod 2 at Hamming weight n/3; negative-kernel descent is exact but polynomial synthesis on the full carrier is not admitted.
- Established: Matching normalization A=I+P+Q gives Exact-One = affine parity intersect independence in a simple cycle 2-factor.
- Established: Raw rational/F2 nullity, singularity, commutativity, primitivity, local EQ3 gauge quotient, common matchgate basis, local matching gadgets, and one-toggle additive Exact-Matching counters are all closed as universal shortcuts.
- Established: Boben A-reductions terminate structurally in bounded-width terminals, but exact semantic transport remains open; one A-step needs at least 3 states and an explicit two-step region needs at least 4.
- Established: For every exact 3-edge interface, if r boundary edges meet internal variable/EQ vertices, q is the number of internal clause/EXACT1 vertices, and y is extendable, then |y_V|-|y_C| == -q mod 3.
- Established: The complete 3-edge boundary algebra is constant: every nonempty projected relation is either an even delta-matroid with at most three tuples or a complementary two-state relation, i.e. twisted EQ3.
- Established: Therefore genuine <=3-edge separator composition itself cannot cause exponential semantic state growth; complementary 3-cut states carry only one Boolean all-or-none choice.
- Established: Trivial vertex-isolating 3-cuts are not progress when contraction merely recreates the same local EQ3/EXACT1 atom.

### Live split

```json
{
  "primary": {
    "goal": "Recursively exploit genuine nontrivial <=3-edge separations using the exact constant boundary algebra, then construct a polynomial contraction or exact terminal for the residual 3-cut-irreducible rank-3 core.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "On the residual core, construct source-specific polynomial syndrome compression for affine parity plus cycle-2factor independence; generic high-width affine/Krom shortcuts are forbidden.",
    "status": "OPEN"
  },
  "reserve": {
    "goal": "Use Boben A-reduction only if arbitrary sequences admit an exact polynomial-size correlation algebra and polynomial witness reconstruction.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Formalize a polynomial decomposition that contracts every genuine nontrivial <=3-edge separation and prove total signature/witness-reconstruction cost polynomial; do not count trivial atom cuts.
2. Characterize the residual cubic-linear core after exhaustive nontrivial 3-cut composition and test whether Boben A-reduction necessarily creates a contractible 3-cut or a bounded-width terminal.
3. In parallel, derive a canonical source-specific syndrome representation for the residual A=I+P+Q cycle-2factor form and prove polynomial closure or construct an explicit falsifier.
4. Do not reopen local matching gadgets, additive Exact-Matching counters, local gauge quotient, raw-nullity, singularity, commutativity-only, primitive/imprimitive, or constant three-state Boben lifts.
5. Promote E8_D1 only after SOUND, COMPLETE, TERMINATES, POLY and polynomial witness reconstruction hold for every instance in the NP-complete carrier.

## Commits newer than semantic checkpoint — MUST INGEST

- `f5db73a4cc3a` — 2026-09-28T02:41:26+03:00 — R5 E9: sync semantic checkpoint after exact 3-cut algebra
- `55718cb83fec` — 2026-09-28T02:50:27+03:00 — R5 E9: add balanced set-partitioning Exact-One terminal
- `28e0649970fc` — 2026-09-28T02:51:50+03:00 — R5 E10: rule out edge-wise matchgate gauges for EQ3/Exact1
- `29617c02149e` — 2026-09-28T02:52:02+03:00 — R5 E9: add checker for balanced Exact-One terminal
- `e2cc859a97f7` — 2026-09-28T02:52:06+03:00 — R5 E10: add exact checker for edge-wise matchgate gauge barrier

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `95ac116808646abf…`
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

- `e2cc859a97f7` — 2026-09-28T02:52:06+03:00 — R5 E10: add exact checker for edge-wise matchgate gauge barrier
- `29617c02149e` — 2026-09-28T02:52:02+03:00 — R5 E9: add checker for balanced Exact-One terminal
- `28e0649970fc` — 2026-09-28T02:51:50+03:00 — R5 E10: rule out edge-wise matchgate gauges for EQ3/Exact1
- `55718cb83fec` — 2026-09-28T02:50:27+03:00 — R5 E9: add balanced set-partitioning Exact-One terminal
- `f5db73a4cc3a` — 2026-09-28T02:41:26+03:00 — R5 E9: sync semantic checkpoint after exact 3-cut algebra
- `f1e556b93e6e` — 2026-09-28T02:40:10+03:00 — R5 E9: add CI for exact three-edge-cut algebra
- `f1e6f9fb1d36` — 2026-09-28T02:39:58+03:00 — R5 E9: add checker for exact three-edge-cut algebra
- `acdd0edb4dd3` — 2026-09-28T02:39:27+03:00 — R5 E9: prove exact three-edge-cut boundary algebra
- `0192c134abab` — 2026-09-28T02:28:10+03:00 — R5 E9: sync semantic checkpoint after exact-matching exchange barrier
- `b47e6a2cfceb` — 2026-09-28T02:24:07+03:00 — R5 E9: add CI for exact-matching toggle exchange
- `6a88b0fa7c5e` — 2026-09-28T02:23:57+03:00 — R5 E9: add exact toggle pair-exchange replay
- `365808a740a5` — 2026-09-28T02:23:27+03:00 — R5 E9: prove exact-matching toggle pair-exchange barrier
- `2711d52b3e08` — 2026-09-28T02:15:27+03:00 — R5 E9: add exact checker for EQ3 local gauge quotient
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
