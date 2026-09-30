# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `b53c23ebf36c6b0d07fa037c4151d053d6cb12df`
- **Source commit time:** `2026-09-30T05:32:06+03:00`
- **Indexed changed scientific artifacts:** `992`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `480eed45722312b7b16e4a5d9f3d19149e125892`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `63`

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
- `7aae6e312146` — 2026-09-29T04:57:16+03:00 — R5 E9: add global Walsh moment kernel augmentation router
- `703cf69645d9` — 2026-09-29T04:57:58+03:00 — R5 E9: add Walsh moment augmentation regression
- `404c9f1bd197` — 2026-09-29T04:58:13+03:00 — R5 E9: add CI for Walsh moment global augmentation
- `c6a72f69d591` — 2026-09-29T05:09:46+03:00 — R5 E9: add exact MaxLin2-AA router for negative-mean Walsh gate
- `62ffcf76426f` — 2026-09-29T05:11:57+03:00 — R5 E9: add exact Walsh-to-MaxLin2 mapping regression
- `87efa2d7c38e` — 2026-09-29T05:12:07+03:00 — R5 E9: add CI for Walsh MaxLin2-AA router
- `da9a19e241f3` — 2026-09-29T13:07:14+03:00 — R5 E9: add Paley11 chain-switch post-RKPR linear-nullity family
- `64b373e90b66` — 2026-09-29T13:08:00+03:00 — R5 E9: add exact Paley11 chain-switch nullity checker
- `e3bb810fa89b` — 2026-09-29T13:08:12+03:00 — R5 E9: add CI for Paley11 chain-switch nullity family
- `fe80c58e3c6c` — 2026-09-29T13:18:00+03:00 — R5 E9: add Paley11 gradient-kernel post-RKPR UNSAT terminal
- `db8358972870` — 2026-09-29T13:19:15+03:00 — R5 E9: add exact Paley11 gradient-kernel checker
- `fc5ad37840c5` — 2026-09-29T13:19:24+03:00 — R5 E9: add Paley11 gradient-kernel CI
- `b8dd44bb17bb` — 2026-09-29T13:26:55+03:00 — R5 E9: prove infinite Paley-orbit post-RKPR gradient family
- `469349bd9b7b` — 2026-09-29T13:27:58+03:00 — R5 E9: add exact checker for infinite Paley-orbit family
- `8bc2dbd046e8` — 2026-09-29T13:28:07+03:00 — R5 E9: add CI for infinite Paley-orbit gradient family
- `b82a8ebc6e74` — 2026-09-29T14:58:57+03:00 — R5 E9: add exact TU row-space integer LP router
- `102b3b95b8d9` — 2026-09-29T15:03:54+03:00 — R5 E9: add exact TU row-space router regression
- `da74ed88e414` — 2026-09-29T15:04:02+03:00 — R5 E9: add CI for exact TU row-space router
- `c43992f8911e` — 2026-09-29T15:05:47+03:00 — R5 E9: bind PG15 non-TU residual control
- `d8a7a0846dcb` — 2026-09-29T15:06:47+03:00 — R5 E9: remove duplicate TU row-space theorem
- `2389d8fc71dd` — 2026-09-29T15:06:53+03:00 — R5 E9: remove duplicate TU row-space checker
- `7df75eb560c4` — 2026-09-29T15:07:00+03:00 — R5 E9: remove duplicate TU row-space CI
- `f0818bdb7d88` — 2026-09-30T03:06:14+03:00 — R5 E9: add Paley19 gradient-kernel post-RKPR control theorem
- `9efd37493952` — 2026-09-30T03:06:49+03:00 — R5 E9: add exact Paley19 gradient-kernel checker
- `29c3a79d7a05` — 2026-09-30T03:06:56+03:00 — R5 E9: add CI for Paley19 gradient-kernel control
- `a164045d23c0` — 2026-09-30T03:15:08+03:00 — R5 E9: prove infinite post-RKPR sqrt-nullity Paley barrier
- `5ffac5b1325b` — 2026-09-30T03:15:57+03:00 — R5 E9: add checker for infinite Paley post-RKPR barrier
- `cd01e32f09c2` — 2026-09-30T03:16:25+03:00 — R5 E9: keep infinite Paley checker exact with integer sqrt
- `4a73a4317e24` — 2026-09-30T03:16:34+03:00 — R5 E9: add CI for infinite Paley post-RKPR sqrt-nullity barrier
- `11011ae1b97c` — 2026-09-30T03:52:39+03:00 — R5 E9: add affine F3 nowhere-zero Exact-One normal form
- `059c0fcf5e36` — 2026-09-30T03:53:15+03:00 — R5 E9: add exact affine F3 nowhere-zero regression
- `4e7506885f09` — 2026-09-30T03:53:29+03:00 — R5 E9: add CI for affine F3 nowhere-zero normal form
- `432c9bd28356` — 2026-09-30T04:05:19+03:00 — R5 E9: add exact checker for affine F3 nowhere-zero normal form
- `e3cd39c9b20b` — 2026-09-30T04:05:53+03:00 — R5 E9: remove duplicate affine F3 checker
- `29664d5bb057` — 2026-09-30T04:15:43+03:00 — R5 E9: add augmented ternary branch-width full-support DP router
- `adfbd510e682` — 2026-09-30T04:16:26+03:00 — R5 E9: add exact branch-width full-support DP regression
- `f5b52bf95c06` — 2026-09-30T04:16:34+03:00 — R5 E9: add CI for augmented ternary branch-width DP
- `165af10bcaae` — 2026-09-30T04:24:54+03:00 — R5 E9: add affine F3 projective blocking line terminal
- `a6f4fd196780` — 2026-09-30T04:25:28+03:00 — R5 E9: add exact checker for projective blocking line terminal
- `cb4c72acf7fc` — 2026-09-30T04:25:38+03:00 — R5 E9: add CI for projective blocking line terminal
- `784cfa930a8a` — 2026-09-30T04:30:00+03:00 — R5 E9: add affine F3 parallel-class fixed-point quotient
- `3eae415d1dbe` — 2026-09-30T04:30:30+03:00 — R5 E9: add exact checker for affine F3 parallel-class quotient
- `85716a950963` — 2026-09-30T04:30:38+03:00 — R5 E9: add CI for affine F3 parallel-class quotient
- `7bc65a9348cc` — 2026-09-30T04:49:49+03:00 — R5 E9: add line-free proper blocking source countercontrol
- `b8a5ccfd7925` — 2026-09-30T04:50:33+03:00 — R5 E9: add exact line-free proper blocking countercontrol
- `dea704682975` — 2026-09-30T04:50:43+03:00 — R5 E9: add CI for line-free proper blocking countercontrol
- `d78c2eb3689b` — 2026-09-30T05:11:59+03:00 — R5 E9: prove infinite AF3 PCQ-fixed line-free UNSAT 2-lift family
- `327b42fb9e63` — 2026-09-30T05:13:13+03:00 — R5 E9: add exact checker for AF3 PCQ-fixed line-free 2-lift family
- `80107908fe4c` — 2026-09-30T05:13:22+03:00 — R5 E9: add CI for AF3 PCQ-fixed line-free 2-lift family
- `58da760a67ad` — 2026-09-30T05:14:44+03:00 — R5 E9: add affine F3 parallel-saturation quotient
- `fc02013a5738` — 2026-09-30T05:15:25+03:00 — R5 E9: add exact F3 parallel-saturation regression
- `50dba3f20081` — 2026-09-30T05:15:36+03:00 — R5 E9: add CI for affine F3 parallel saturation quotient
- `a578d7cc3da9` — 2026-09-30T05:18:40+03:00 — R5 E9: add two-edge-twist exact contraction recognition router
- `9a4cf5ff45e1` — 2026-09-30T05:20:55+03:00 — R5 E9: add regression for two-edge-twist contraction router
- `71c2206d34f5` — 2026-09-30T05:21:07+03:00 — R5 E9: add CI for two-edge-twist contraction router
- `14944ed2a576` — 2026-09-30T05:22:02+03:00 — R5 E9: prove F3 parallel collapse of unique-model tower
- `74d3bfff97a3` — 2026-09-30T05:22:33+03:00 — R5 E9: add exact regression for unique-model F3 collapse
- `6264dd021824` — 2026-09-30T05:22:41+03:00 — R5 E9: add CI for unique-model F3 parallel collapse
- `65530c97e691` — 2026-09-30T05:26:39+03:00 — R5 E9: prove persistent F3 UNSAT certificate for prime tower
- `e997cb31f383` — 2026-09-30T05:27:15+03:00 — R5 E9: add exact regression for persistent F3 UNSAT certificate
- `b694e147e696` — 2026-09-30T05:27:25+03:00 — R5 E9: add CI for persistent F3 UNSAT certificate
- `b53c23ebf36c` — 2026-09-30T05:32:06+03:00 — R5 E9: add AF3 APSQ EQ3 local source-return barrier

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

- `b53c23ebf36c` — 2026-09-30T05:32:06+03:00 — R5 E9: add AF3 APSQ EQ3 local source-return barrier
- `b694e147e696` — 2026-09-30T05:27:25+03:00 — R5 E9: add CI for persistent F3 UNSAT certificate
- `e997cb31f383` — 2026-09-30T05:27:15+03:00 — R5 E9: add exact regression for persistent F3 UNSAT certificate
- `65530c97e691` — 2026-09-30T05:26:39+03:00 — R5 E9: prove persistent F3 UNSAT certificate for prime tower
- `6264dd021824` — 2026-09-30T05:22:41+03:00 — R5 E9: add CI for unique-model F3 parallel collapse
- `74d3bfff97a3` — 2026-09-30T05:22:33+03:00 — R5 E9: add exact regression for unique-model F3 collapse
- `14944ed2a576` — 2026-09-30T05:22:02+03:00 — R5 E9: prove F3 parallel collapse of unique-model tower
- `71c2206d34f5` — 2026-09-30T05:21:07+03:00 — R5 E9: add CI for two-edge-twist contraction router
- `9a4cf5ff45e1` — 2026-09-30T05:20:55+03:00 — R5 E9: add regression for two-edge-twist contraction router
- `a578d7cc3da9` — 2026-09-30T05:18:40+03:00 — R5 E9: add two-edge-twist exact contraction recognition router
- `50dba3f20081` — 2026-09-30T05:15:36+03:00 — R5 E9: add CI for affine F3 parallel saturation quotient
- `fc02013a5738` — 2026-09-30T05:15:25+03:00 — R5 E9: add exact F3 parallel-saturation regression
- `58da760a67ad` — 2026-09-30T05:14:44+03:00 — R5 E9: add affine F3 parallel-saturation quotient
- `80107908fe4c` — 2026-09-30T05:13:22+03:00 — R5 E9: add CI for AF3 PCQ-fixed line-free 2-lift family
- `327b42fb9e63` — 2026-09-30T05:13:13+03:00 — R5 E9: add exact checker for AF3 PCQ-fixed line-free 2-lift family
- `d78c2eb3689b` — 2026-09-30T05:11:59+03:00 — R5 E9: prove infinite AF3 PCQ-fixed line-free UNSAT 2-lift family
- `dea704682975` — 2026-09-30T04:50:43+03:00 — R5 E9: add CI for line-free proper blocking countercontrol
- `b8a5ccfd7925` — 2026-09-30T04:50:33+03:00 — R5 E9: add exact line-free proper blocking countercontrol
- `7bc65a9348cc` — 2026-09-30T04:49:49+03:00 — R5 E9: add line-free proper blocking source countercontrol
- `85716a950963` — 2026-09-30T04:30:38+03:00 — R5 E9: add CI for affine F3 parallel-class quotient
- `3eae415d1dbe` — 2026-09-30T04:30:30+03:00 — R5 E9: add exact checker for affine F3 parallel-class quotient
- `784cfa930a8a` — 2026-09-30T04:30:00+03:00 — R5 E9: add affine F3 parallel-class fixed-point quotient
- `cb4c72acf7fc` — 2026-09-30T04:25:38+03:00 — R5 E9: add CI for projective blocking line terminal
- `a6f4fd196780` — 2026-09-30T04:25:28+03:00 — R5 E9: add exact checker for projective blocking line terminal
- `165af10bcaae` — 2026-09-30T04:24:54+03:00 — R5 E9: add affine F3 projective blocking line terminal

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
