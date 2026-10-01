# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `837a387b3dae1f492af91ca73590a80adad4c3e3`
- **Source commit time:** `2026-10-01T06:58:51+03:00`
- **Indexed changed scientific artifacts:** `1045`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `480eed45722312b7b16e4a5d9f3d19149e125892`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `120`

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
- `3a60af0631c7` — 2026-09-30T05:32:40+03:00 — R5 E9: add exact AF3 APSQ EQ3 source-return regression
- `42d520841356` — 2026-09-30T05:32:47+03:00 — R5 E9: add CI for AF3 APSQ EQ3 local source return
- `1905caed5bb1` — 2026-09-30T05:35:37+03:00 — R5 E9: add AF3 residual normal-codimension DP router
- `698011e9cb79` — 2026-09-30T05:40:26+03:00 — R5 E9: prove Paley AF3 linear-excess barrier
- `1e2b2ab72842` — 2026-09-30T05:42:43+03:00 — R5 E9: add exact residual-normal codimension DP regression
- `1df439744bbb` — 2026-09-30T05:42:55+03:00 — R5 E9: add CI for AF3 residual-normal codimension DP router
- `a8b3b9a6389d` — 2026-09-30T05:56:34+03:00 — R5 E9: prove AF3 RNCDP inert source-return identity
- `888a360afec7` — 2026-09-30T05:57:25+03:00 — R5 E9: add exact AF3 RNCDP inert source-return regression
- `38c840ea467c` — 2026-09-30T05:57:34+03:00 — R5 E9: add CI for AF3 RNCDP inert source return
- `2342ff8e2d89` — 2026-09-30T05:59:02+03:00 — R5 E9: close projectively-distinct hyperplane-cover shortcut
- `6ec209236afe` — 2026-09-30T05:59:17+03:00 — R5 E9: add F3 four-hyperplane cover regression
- `11cf454019a4` — 2026-09-30T05:59:40+03:00 — R5 E9: add CI for F3 four-hyperplane cover barrier
- `98ef041af307` — 2026-09-30T06:02:02+03:00 — R5 E9: prove global AF3 APSQ factorization of EQ3 regularizer
- `260408147852` — 2026-09-30T06:02:43+03:00 — R5 E9: add exact global AF3 EQ3 APSQ factorization regression
- `b70f974bb002` — 2026-09-30T06:02:52+03:00 — R5 E9: add CI for global AF3 EQ3 APSQ factorization
- `601fa603eafa` — 2026-09-30T06:04:12+03:00 — R5 E9: reconcile AF3 with infinite linear-dimension UNSAT cover family
- `f9050ef24336` — 2026-09-30T06:08:19+03:00 — R5 E9: add locally-3K2 clique-operator Exact-One countercontrol
- `4cb1c946a86f` — 2026-09-30T06:08:34+03:00 — R5 E9: add exact clique-operator noninvariance regression
- `a058e8831115` — 2026-09-30T06:08:52+03:00 — R5 E9: add CI for clique-operator Exact-One noninvariance
- `634184a16b07` — 2026-09-30T06:12:13+03:00 — R5 E9: close essential AF3 cover-size shortcut
- `36a7a14f0ea2` — 2026-09-30T06:12:26+03:00 — R5 E9: add exact six-hyperplane essential-cover regression
- `6ccf5064e4cd` — 2026-09-30T06:19:07+03:00 — R5 E9: prove AF3 projective scaling invariance
- `ff316dda71a1` — 2026-09-30T06:26:31+03:00 — R5 E9: add AF3 projective scaling regression
- `bbf2369c5b5a` — 2026-09-30T06:26:56+03:00 — R5 E9: make AF3 projective regression kernel-dimensional
- `9addb3121770` — 2026-09-30T06:27:05+03:00 — R5 E9: add CI for AF3 projective invariance
- `4fbae71b9101` — 2026-09-30T06:31:31+03:00 — R5 E9: add AF3 normal-excess dual FPT router
- `bf08e87be017` — 2026-09-30T06:32:21+03:00 — R5 E9: add exact AF3 normal-excess router regression
- `c4ed01ca7ae8` — 2026-09-30T06:33:16+03:00 — R5 E9: add CI for AF3 normal-excess dual router
- `60877843fca4` — 2026-09-30T06:33:28+03:00 — R5 E9: prove exact one-zero minus-two augmentation criterion
- `88e671194b0c` — 2026-09-30T06:34:10+03:00 — R5 E9: add one-zero exact augmentation regression
- `65e7e4a33664` — 2026-09-30T06:34:19+03:00 — R5 E9: add CI for one-zero exact augmentation theorem
- `4d870d06310a` — 2026-09-30T06:37:09+03:00 — R5 E9: prove one-zero bipartite complement-graph polynomial terminal
- `0f0dd2919f0d` — 2026-09-30T06:42:10+03:00 — R5 E9: prove PG15 augmented ternary support-width barrier
- `f79856cc267f` — 2026-09-30T06:42:30+03:00 — R5 E9: add exact PG15 support-width checker
- `ae8a3aa4fbea` — 2026-09-30T06:42:40+03:00 — R5 E9: add CI for PG15 support-width barrier
- `e6410f147212` — 2026-09-30T06:45:20+03:00 — R5 E9: correct AF3 normal-excess projective invariance
- `936d74edb2d1` — 2026-09-30T06:46:57+03:00 — R5 E9: compress AF3 dual router to syndrome-image rank
- `0bbb0deabad3` — 2026-09-30T06:47:49+03:00 — R5 E9: regression-test syndrome-rank compressed AF3 router
- `11a14d62c08a` — 2026-09-30T06:49:43+03:00 — R5 E9: add affine F3 parallel-triple UNSAT terminal
- `7967fa6f7d24` — 2026-09-30T06:50:23+03:00 — R5 E9: add exact checker for F3 parallel-triple terminal
- `b2fe277a4e0a` — 2026-09-30T06:50:32+03:00 — R5 E9: add CI for F3 parallel-triple UNSAT terminal
- `aac63f73af05` — 2026-09-30T06:59:20+03:00 — R5 E9: add affine F3 rank-2 quotient cover UNSAT router
- `33007d906421` — 2026-09-30T07:00:16+03:00 — R5 E9: add exact checker for affine F3 rank-2 cover router
- `5638c04d0318` — 2026-09-30T07:00:28+03:00 — R5 E9: add CI for affine F3 rank-2 cover router
- `8a6e8c0dee0b` — 2026-09-30T07:12:44+03:00 — R5 E9: falsify rank-2 F3 cover completeness with Paley19
- `d5097828bfea` — 2026-09-30T07:13:35+03:00 — R5 E9: add exact Paley19 rank-2 cover falsifier checker
- `f7333dd9cf93` — 2026-09-30T07:13:44+03:00 — R5 E9: add CI for Paley19 rank-2 cover falsifier
- `bc0ffec278db` — 2026-09-30T07:47:51+03:00 — R5 E9: close AF3 model-count mod-3 shortcut
- `8c6b2ac8e247` — 2026-09-30T07:48:11+03:00 — R5 E9: add exact checker for mod-3 model-count barrier
- `edf2d8691d31` — 2026-09-30T07:48:19+03:00 — R5 E9: add CI for mod-3 model-count barrier
- `4b48016fc803` — 2026-09-30T08:00:51+03:00 — R5 E9: prove directed-triangle fourth-point completion barrier
- `7ac2a5ba39bc` — 2026-09-30T08:01:10+03:00 — R5 E9: add exact directed-triangle completion regression
- `27525c9144e2` — 2026-09-30T08:01:23+03:00 — R5 E9: add CI for directed-triangle completion barrier
- `23fcf5f92ee8` — 2026-09-30T08:02:24+03:00 — R5 E9: add affine F3 critical-exponent and rank-2 cover terminal
- `efd35e99d91c` — 2026-09-30T08:03:35+03:00 — R5 E9: add exact checker for F3 critical exponent rank-2 cover terminal
- `d2e147d6f925` — 2026-09-30T08:03:43+03:00 — R5 E9: add CI for F3 critical exponent rank-2 cover terminal
- `837a387b3dae` — 2026-10-01T06:58:51+03:00 — E9: prove exact Paley19 minimum AF3 cover rank six

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

- `837a387b3dae` — 2026-10-01T06:58:51+03:00 — E9: prove exact Paley19 minimum AF3 cover rank six
- `d2e147d6f925` — 2026-09-30T08:03:43+03:00 — R5 E9: add CI for F3 critical exponent rank-2 cover terminal
- `efd35e99d91c` — 2026-09-30T08:03:35+03:00 — R5 E9: add exact checker for F3 critical exponent rank-2 cover terminal
- `23fcf5f92ee8` — 2026-09-30T08:02:24+03:00 — R5 E9: add affine F3 critical-exponent and rank-2 cover terminal
- `27525c9144e2` — 2026-09-30T08:01:23+03:00 — R5 E9: add CI for directed-triangle completion barrier
- `7ac2a5ba39bc` — 2026-09-30T08:01:10+03:00 — R5 E9: add exact directed-triangle completion regression
- `4b48016fc803` — 2026-09-30T08:00:51+03:00 — R5 E9: prove directed-triangle fourth-point completion barrier
- `edf2d8691d31` — 2026-09-30T07:48:19+03:00 — R5 E9: add CI for mod-3 model-count barrier
- `8c6b2ac8e247` — 2026-09-30T07:48:11+03:00 — R5 E9: add exact checker for mod-3 model-count barrier
- `bc0ffec278db` — 2026-09-30T07:47:51+03:00 — R5 E9: close AF3 model-count mod-3 shortcut
- `f7333dd9cf93` — 2026-09-30T07:13:44+03:00 — R5 E9: add CI for Paley19 rank-2 cover falsifier
- `d5097828bfea` — 2026-09-30T07:13:35+03:00 — R5 E9: add exact Paley19 rank-2 cover falsifier checker
- `8a6e8c0dee0b` — 2026-09-30T07:12:44+03:00 — R5 E9: falsify rank-2 F3 cover completeness with Paley19
- `5638c04d0318` — 2026-09-30T07:00:28+03:00 — R5 E9: add CI for affine F3 rank-2 cover router
- `33007d906421` — 2026-09-30T07:00:16+03:00 — R5 E9: add exact checker for affine F3 rank-2 cover router
- `aac63f73af05` — 2026-09-30T06:59:20+03:00 — R5 E9: add affine F3 rank-2 quotient cover UNSAT router
- `b2fe277a4e0a` — 2026-09-30T06:50:32+03:00 — R5 E9: add CI for F3 parallel-triple UNSAT terminal
- `7967fa6f7d24` — 2026-09-30T06:50:23+03:00 — R5 E9: add exact checker for F3 parallel-triple terminal
- `11a14d62c08a` — 2026-09-30T06:49:43+03:00 — R5 E9: add affine F3 parallel-triple UNSAT terminal
- `0bbb0deabad3` — 2026-09-30T06:47:49+03:00 — R5 E9: regression-test syndrome-rank compressed AF3 router
- `936d74edb2d1` — 2026-09-30T06:46:57+03:00 — R5 E9: compress AF3 dual router to syndrome-image rank
- `e6410f147212` — 2026-09-30T06:45:20+03:00 — R5 E9: correct AF3 normal-excess projective invariance
- `ae8a3aa4fbea` — 2026-09-30T06:42:40+03:00 — R5 E9: add CI for PG15 support-width barrier
- `f79856cc267f` — 2026-09-30T06:42:30+03:00 — R5 E9: add exact PG15 support-width checker
- `0f0dd2919f0d` — 2026-09-30T06:42:10+03:00 — R5 E9: prove PG15 augmented ternary support-width barrier

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
