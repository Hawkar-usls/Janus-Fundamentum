# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `d9807a85a3f276fee614093af042ec54cc97d269`
- **Source commit time:** `2026-09-29T04:50:46+03:00`
- **Indexed changed scientific artifacts:** `940`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `480eed45722312b7b16e4a5d9f3d19149e125892`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `1`

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

- **Frontier:** `R5_E9_GLOBAL_SIGN_CROSSING_SOURCE_TRADE_GATE_V2`
- **Carrier:** connected square linear-cubic Positive-1-in-3 source after polynomial integer-lattice membership; odd affine-coset Ay=-1 with y odd; SAT iff min ||y||_1=n; threshold form is NAE transversal plus nonnegative copy-flow
- Established: Exact linear-cubic Positive 1-in-3 SAT is NP-complete via the frozen EQ3 regularizer with polynomial witness transfer.
- Established: Integer-lattice membership Az=1 over Z is polynomial; y=2z-1 converts it exactly to odd Ay=-1 and SAT iff the odd-coset L1 optimum is n.
- Established: For a feasible odd point, an integer source trade is y->y+2g with g in ker_Z(A); exact half-objective change is s^T g + P_y(g), with P_y the sign-crossing penalty.
- Established: Thresholding an integer feasible point gives a NAE transversal B. Exact identities: |T|=3|B|-n and F=n/3+2|B|+4||p||_1. Exact-One SAT iff the transversal number is n/3.
- Established: For fixed NAE threshold b, copy magnitudes obey r_minority-r_majority1-r_majority2=tau. The copy matrix is exactly M_b=R_b A S_b, so row/column signing preserves the source determinant/kernel obstruction.
- Established: Zero-crossing augmentation is exactly augmentation inside one fixed NAE orthant. It is not complete: for every Exact-One witness x, zc=1-2x is integer feasible, is a fixed-orthant optimum with F=5n/3, while x has F=n; the direct improving trade crosses every coordinate.
- Established: The frozen unique-model 18_3 source is a stronger finite hostile control: from its complement point, every support-minimal rational kernel circuit is integer-line-search nonimproving although the unique Boolean witness has lower objective.
- Established: Support-minimal oriented-matroid circuits therefore cannot replace genuinely global/Graver augmentation.
- Established: A recursive two-edge frustration-2 lift from the frozen unique-model 18_3 seed yields an infinite connected square linear-cubic SAT family that is unique-model, signed-trade-free, unbalanced, 3-cut-prime, and has rational nullity at least n/18+1.
- Established: Thus large nullity, model multiplicity, small signed trades, and <=3-edge decompositions cannot justify the missing sign-crossing move.
- Established: Primitive integer-kernel/Graver coefficients can be exponentially large even for connected square linear-cubic nullity-one matrices; a valid algorithm must handle binary-encoded large coefficients symbolically.
- Established: Private EQ3 integer coordinates eliminate exactly to a separable convex source penalty phi(q), returning the NP-complete source core rather than a network/TU problem.
- Established: Direct matching/matchgate/delta-matroid, fixed-modulus counting, PolaritySAT-2026, small-boundary summaries, low-nullity, near-TU, and bounded-width/local-consistency shortcuts are frozen negative controls.
- Established: P_VS_NP remains OPEN and E8_D1 remains EMPTY.

### Live split

```json
{
  "primary": {
    "goal": "Construct a deterministic polynomial source-trade procedure that can cross NAE orthants: from a polynomially constructed integer feasible point, find a globally improving g in ker_Z(A) under the exact crossing penalty or certify global odd-coset L1 optimality, with polynomial bit complexity and witness reconstruction.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Exploit the exact NAE transversal/copy-flow representation to build a blossom/Lehman-like global augmentation or decomposition that keeps the three-way copy constraint exact and does not enumerate Graver elements, thresholds, or crossing sets.",
    "status": "OPEN"
  },
  "reserve": {
    "goal": "Investigate minimally-nonideal/Lehman cores only as a source of recognizable global inequalities or contractions; do not assume a complete classification or polynomial idealness recognizer.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Search for a polynomially constructible non-circuit global augmentation certificate for separable-convex lattice optimization on A=I+P+Q / linear-cubic source matrices.
2. Use the exact copy-flow identity M_b=R_b A S_b to derive a threshold-changing move calculus; zero-crossing-only is forbidden.
3. Test every proposed global move on the unique-model prime linear-nullity SAT tower and on the existing prime linear-nullity UNSAT tower.
4. Investigate Lehman/minimally-nonideal rank inequalities as blossom-like donors, but require polynomial discovery/separation and exact witness reconstruction; idealness recognition itself is not a free oracle.
5. Do not replace Graver augmentation by rational circuits: the frozen 18_3 complement state is circuit-local but not globally optimal.
6. Promote E8_D1 only after SOUND+COMPLETE+TERMINATES+POLY+RECONSTRUCT hold for arbitrary 3CNF.

## Commits newer than semantic checkpoint — MUST INGEST

- `d9807a85a3f2` — 2026-09-29T04:50:46+03:00 — R5 E9: synchronize semantic checkpoint to global sign-crossing trade gate

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `d2b85f2b6022053a237bbd0d20fa9f6610dfe749b394b6d680696c9d84c22d02`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `e86f968896d3aa7a…`
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

- `d9807a85a3f2` — 2026-09-29T04:50:46+03:00 — R5 E9: synchronize semantic checkpoint to global sign-crossing trade gate
- `480eed457223` — 2026-09-29T04:49:04+03:00 — R5 E9: add exact circuit-augmentation barrier checker
- `44d31b0ab5ae` — 2026-09-29T04:48:43+03:00 — R5 E9: falsify circuit-only integer L1 augmentation
- `7b6eafd3315e` — 2026-09-29T04:43:15+03:00 — R5 E9: add IF2E router and three-external hostile regression
- `534eae0ff8a7` — 2026-09-29T04:42:50+03:00 — R5 E9: add regression for prime unique-model nullity tower
- `7e940a17c60b` — 2026-09-29T04:42:48+03:00 — R5 E9: freeze three-external hostile local-minimum countercontrol
- `644609b4b4fd` — 2026-09-29T04:42:16+03:00 — R5 E9: prove prime unique-model linear-nullity two-edge tower
- `9bb40a0690d2` — 2026-09-29T04:41:12+03:00 — R5 E9: add checker for zero-crossing trap
- `c7575b64bb28` — 2026-09-29T04:40:47+03:00 — R5 E9: prove fixed-NAE sign equivalence and zero-crossing trap
- `4f41dd32fa95` — 2026-09-29T04:40:28+03:00 — R5 E9: add independent-flat two-external augmentation router
- `f675173f3ef1` — 2026-09-29T04:34:29+03:00 — R5 E9: add CI for maximum even-cover saturation
- `00c94877999b` — 2026-09-29T04:34:20+03:00 — R5 E9: add maximum even-cover saturation regression
- `d71a16a888c1` — 2026-09-29T04:34:04+03:00 — R5 E9: prove maximum linear even-cover saturation equivalence
- `4d060d749e84` — 2026-09-29T04:23:56+03:00 — R5 E9: add CI for source-signed even-cover WGFP
- `e2e79fa1c36f` — 2026-09-29T04:23:47+03:00 — R5 E9: add source-signed even-cover WGFP regression
- `cdd3b8c52dd4` — 2026-09-29T04:22:52+03:00 — R5 E9: reduce parity defects to source-signed linear even cover WGFP
- `9fce9bc8db9b` — 2026-09-29T04:09:38+03:00 — R5 E9: add CI for NAE transversal copy flow
- `d911d51d384b` — 2026-09-29T04:09:31+03:00 — R5 E9: add exact NAE copy-flow regression
- `a5b56657ee56` — 2026-09-29T04:08:55+03:00 — R5 E9: derive NAE transversal copy-flow normal form
- `78e0cbc8909c` — 2026-09-29T04:03:56+03:00 — R5 E9: sync semantic checkpoint to crossing-penalty trade frontier
- `50c5c8500bf8` — 2026-09-29T04:03:23+03:00 — R5 E9: add exact EQ3 L1 private-elimination checker
- `620f19b64a9c` — 2026-09-29T04:03:08+03:00 — R5 E9: eliminate EQ3 private L1 coordinates exactly
- `66e9e29aa352` — 2026-09-29T04:01:39+03:00 — R5 E9: add CI for continuous L1 crossing barrier
- `d972c0cd518d` — 2026-09-29T04:01:29+03:00 — R5 E9: add exact checker for continuous L1 crossing barrier
- `4c0189564bef` — 2026-09-29T04:00:49+03:00 — R5 E9: isolate continuous L1 barycenter and crossing penalty

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
