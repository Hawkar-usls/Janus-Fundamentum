# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `7aea8f113b66d02330dc1c792c2978462cca1472`
- **Source commit time:** `2026-09-28T03:16:40+03:00`
- **Indexed changed scientific artifacts:** `693`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `3e6118229890f31800268fc683de8062736aa558`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `3`

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

- **Frontier:** `R5_E9_THREE_CUT_IRREDUCIBLE_UNBALANCED_STRONG_ODD_CYCLE_GATE_V1`
- **Carrier:** NP-complete connected/linear cubic positive Exact-One; exact forms include A=I+P+Q, affine parity plus cycle-2factor independence, dual rank-3 perfect hypermatching, grouped Levi interfaces, and set-partitioning polytope P(A)
- Established: Exact linear cubic Positive 1-in-3 SAT is NP-complete via the constant-size linear cubic EQ3 regularization gadget.
- Established: Cubic Exact-One is exactly affine parity Ax=1 mod 2 at Hamming weight n/3; negative-kernel descent is exact but polynomial synthesis on the full carrier is not admitted.
- Established: Matching normalization A=I+P+Q gives Exact-One = affine parity intersect independence in a simple cycle 2-factor.
- Established: For every exact 3-edge interface the boundary algebra is constant: every nonempty projected relation is either an even delta-matroid with at most three tuples or a complementary twisted-EQ3 pair.
- Established: Therefore genuine <=3-edge interfaces do not create semantic state explosion; trivial vertex-isolating 3-cuts are not counted as progress.
- Established: If the source incidence matrix A is balanced, P(A)={x>=0:Ax=1} is integral and a Boolean Exact-One witness is deterministically constructible in polynomial time.
- Established: If A is unbalanced, polynomial balancedness recognition supplies a strong odd-cycle / chordless 4k+2 Levi-cycle certificate.
- Established: The frozen connected linear-cubic 15_3 rank-14 UNSAT control has no nontrivial edge cut of size <=3: its 30 three-edge cuts are exactly the 30 vertex stars. It is unbalanced via rows {0,12,13} and columns {0,8,12}, which form the forbidden odd 3x3 cycle submatrix.
- Established: That 15_3 object is a hostile control for separator+balanced+singularity shortcuts, not an ultimate hard core: its rational nullity is only 1 and the existing low-nullity router can solve it.
- Established: A common EQ3/EXACT1 matchgate basis and the stronger edge-wise matchgate-gauge route are closed as universal Pfaffian shortcuts.
- Established: Three-port local matching gadgets and one-toggle additive Exact-Matching counters are closed; ordinary matching escape must be genuinely nonlocal.
- Established: Every connected acyclic grouped EQ3/EXACT1 region containing an EQ3 node has a boundary relation that is not a delta-matroid, hence is not ordinary matching-realizable, for arbitrary region size.
- Established: Boben A-reductions terminate structurally in bounded-width terminals, but exact semantic transport remains open; one A-step needs at least 3 states and an explicit legal two-step region needs at least 4.
- Established: Raw rational/F2 nullity, singularity, commutativity, primitivity, local EQ3 gauge quotient and Harries/OET amplifier statistics are not universal complexity currencies.

### Live split

```json
{
  "primary": {
    "goal": "Compose all genuine nontrivial <=3-edge separations with polynomial total signature/reconstruction cost, route balanced pieces to the LP-integral terminal, and solve or contract the remaining 3-cut-irreducible unbalanced core carrying an explicit strong odd cycle.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "On the residual core, prove or falsify a low-rational-nullity bound after exhaustive genuine <=3-cut decomposition; the rank-14 n=15 control is not a falsifier because its nullity is 1. If the bound fails, freeze an explicit high-nullity 3-cut-irreducible counterfamily and abandon this currency.",
    "status": "OPEN"
  },
  "reserve": {
    "goal": "Derive source-specific polynomial syndrome compression for affine parity plus cycle-2factor independence or a polynomial Boben correlation algebra; generic high-width affine/Krom and constant-state shortcuts remain forbidden.",
    "status": "OPEN"
  }
}
```

### Next attack

1. On a residual strong odd cycle, derive an exact dimension-dropping contraction including all third-incidence boundary semantics; belt-only projection or ordinary matching realization is insufficient.
2. Exploit det(C_odd)=2 only if the resulting single Z2 torsion channel plus Boolean range constraints can be represented and updated in polynomial total size; abandon it on an explicit source-valid growth family.
3. Search for a high-rational-nullity 3-cut-irreducible unbalanced family before promoting any low-nullity residual theorem.
4. Do not reopen tree-shaped grouped matching gadgets, local/additive Exact-Matching gadgets, common or edge-wise matchgate gauges, local EQ3 gauge quotient, singularity-only, or constant three-state Boben lifts.
5. Promote E8_D1 only after SOUND, COMPLETE, TERMINATES, POLY and polynomial witness reconstruction hold for every instance in the NP-complete carrier.

## Commits newer than semantic checkpoint — MUST INGEST

- `5dc336418238` — 2026-09-28T03:07:27+03:00 — R5 E9: sync semantic checkpoint after acyclic matching barrier
- `b76675b6429c` — 2026-09-28T03:15:51+03:00 — R5 E9: sync semantic checkpoint after irreducible UNSAT hostile control
- `7aea8f113b66` — 2026-09-28T03:16:40+03:00 — R5 E9: falsify low-nullity prime-core hypothesis by two-edge lifts

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `807e95ebab2f9f2fe8699e17e4242584a295aec41bf9658d6517e7c67c5721f2`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `3837482dab238d43…`
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

- `7aea8f113b66` — 2026-09-28T03:16:40+03:00 — R5 E9: falsify low-nullity prime-core hypothesis by two-edge lifts
- `b76675b6429c` — 2026-09-28T03:15:51+03:00 — R5 E9: sync semantic checkpoint after irreducible UNSAT hostile control
- `5dc336418238` — 2026-09-28T03:07:27+03:00 — R5 E9: sync semantic checkpoint after acyclic matching barrier
- `3e6118229890` — 2026-09-28T03:06:41+03:00 — R5 E9: add CI for 3-cut-irreducible singular UNSAT control
- `5d7718002c8d` — 2026-09-28T03:06:33+03:00 — R5 E9: add checker for 3-cut-irreducible singular UNSAT control
- `b96a0b96a54c` — 2026-09-28T03:05:27+03:00 — R5 E9: add CI for singular UNSAT 3-cut hostile core
- `b01463284dd2` — 2026-09-28T03:05:18+03:00 — R5 E9: add exact 3-cut census for singular UNSAT core
- `694bad41c55e` — 2026-09-28T03:05:04+03:00 — R5 E9: freeze singular UNSAT 3-cut-irreducible hostile core
- `17d7e41c474a` — 2026-09-28T03:04:38+03:00 — R5 E9: freeze 3-cut-irreducible singular UNSAT hostile control
- `53fb72e1a43c` — 2026-09-28T03:03:24+03:00 — R5 E9: add CI for acyclic grouped matching barrier
- `7138befb3d1b` — 2026-09-28T03:03:11+03:00 — R5 E9: add checker for acyclic grouped matching barrier
- `fd154fbc2e79` — 2026-09-28T03:02:34+03:00 — R5 E9: prove acyclic grouped matching delta-matroid barrier
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
