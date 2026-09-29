# JANUS Context Cache — CURRENT

> Canonical externalized recovery surface generated from Git, with the P-vs-NP stream-resume cache embedded as the semantic checkpoint.

- **Repository:** `Hawkar-usls/Janus-Fundamentum`
- **PR:** `#510`
- **Branch:** `codex/r5-e8-direct-contract-20260921-82493a57`
- **Live source HEAD:** `480eed45722312b7b16e4a5d9f3d19149e125892`
- **Source commit time:** `2026-09-29T04:49:04+03:00`
- **Indexed changed scientific artifacts:** `940`

## Continuity status

- Semantic cache: `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json`
- Semantic source HEAD: `66e9e29aa352f9b2df8ea9b36ec1732066ad19b8`
- Relation: **`LIVE_DESCENDS_FROM_SEMANTIC_CACHE`**
- Commits after semantic checkpoint: `21`

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

- **Frontier:** `R5_E9_LINEAR_CUBIC_CROSSING_PENALTY_TRADE_GATE_V1`
- **Carrier:** connected square linear-cubic Positive-1-in-3 source after exact integer-lattice membership, in odd affine-coset form Ay=-1 with y odd; minimize ||y||_1 and solve the discrete crossing-penalty source-trade problem
- Established: Exact linear-cubic Positive 1-in-3 SAT is NP-complete via the frozen constant-size EQ3 regularizer with polynomial witness transfer.
- Established: Integer-lattice membership Ax=1 over Z is polynomial by Smith/Hermite methods and is a sound UNSAT terminal.
- Established: The change y=2z-1 is an exact bijection between integer Az=1 and odd integer Ay=-1; F(z)=sum_i|2z_i-1| equals ||y||_1.
- Established: Exact-One SAT iff the odd-coset L1 optimum is n; UNSAT has optimum at least n+2.
- Established: Every feasible odd point satisfies sum_i y_i=-n/3; every feasible move is y->y+2g with integer Ag=0, and cubic column sums force sum_i g_i=0.
- Established: Thresholding an integer lattice point yields a positive NAE coloring b. Writing z=b+p-q gives Ap-Aq=-1_T, |T|=3(||q||_1-||p||_1), and F-n=4||p||_1+2|T|/3.
- Established: The shortcut p=0 or z in {-1,0,1} at a global optimum is false on an exact connected rank-14 linear-cubic control; positive overshoot can be unavoidable.
- Established: The real L1 relaxation is universal and trivial: min{||y||_1:Ay=-1,y real}=n/3, attained at -1/3*1 for every square cubic source.
- Established: No odd feasible point can be a continuous L1 optimum; a strict real kernel descent direction always exists.
- Established: For integer source trade g, exact objective change is (||y+2g||_1-||y||_1)/2 = s^T g + P_y(g), where s=sign(y) and P_y(g)=sum_i max(0,-|y_i|-2 s_i g_i). The missing information is the discrete crossing penalty.
- Established: Known Graver augmentation gives polynomially many iterations conditional on a suitable improving/best Graver direction, but constructing that direction remains open on the unrestricted linear-cubic carrier.
- Established: Connected square linear-cubic nullity-one matrices can have primitive integer-kernel/Graver coefficient infinity norm 2^(n/7-1); therefore cubicity and linearity do not imply polynomially bounded primitive trade coefficients.
- Established: Large Graver coefficients have only polynomial bit length, so this is a coefficient-enumeration barrier, not a lower bound against symbolic augmentation.
- Established: The EQ3 NP-hard image has exponentially large subdeterminants and linear row/column deletion distance to TU, so bounded-determinant and O(1)-near-TU machinery is not universal.
- Established: Pair2 completeness and empty-triple completeness are false even on explicit connected square linear-cubic UNSAT controls; fixed local-projection arity escalation is frozen.
- Established: All finitary polymorphisms of raw EXACT_ONE_3 are coordinate projections; ordinary bounded-width local consistency is not a universal route.
- Established: Network/graphic/TU, balanced, separator, low-nullity, commuting, phase, series/projective and other certified islands remain polynomial terminals but do not cover the universal residual.
- Established: P_VS_NP remains OPEN and E8_D1 remains EMPTY.

### Live split

```json
{
  "primary": {
    "goal": "Construct a deterministic polynomial integer source-trade procedure that, for odd feasible y, finds g in ker_Z(A) with s^T g + P_y(g)<0 or certifies global odd-coset L1 optimality, with polynomial total bit complexity and witness reconstruction.",
    "status": "OPEN"
  },
  "secondary": {
    "goal": "Find a symbolic decomposition/augmentation calculus that tolerates exponentially large primitive trade coefficients and updates the exact NAE defect-flow state (T,p,q) without enumerating the Graver basis.",
    "status": "OPEN"
  },
  "reserve": {
    "goal": "Investigate set-cover integrality-gap / minimally-nonideal Lehman-core extraction as a possible blossom-like global decomposition, but do not assume an unproved complete classification of cubic Lehman matrices.",
    "status": "OPEN"
  }
}
```

### Next attack

1. Attack the zero-crossing region first: decide whether there exists integer g in ker(A) satisfying s_i g_i >= -d_i for every i and s^T g<0; identify an exact polynomial donor or a source-valid obstruction.
2. If zero-crossing descent fails, classify the minimum crossing set and derive a symbolic augmentation rule whose cost is the exact penalty P_y(g), not an LP surrogate.
3. Use the NAE defect-flow equations Ap-Aq=-1_T to search for a min-cost circulation/b-matching formulation that changes T,p,q jointly and survives the EQ3 determinant-packing barrier.
4. Search source literature on linear-cubic configuration trades, circuit/Graver augmentation, parity-constrained flows, and Lehman/minimally-nonideal cores for a polynomial symbolic donor; reject donors requiring bounded coefficients, bounded determinants, bounded treedepth, or O(1) near-TU distance.
5. Do not infer hardness from general hypergraph toric ideals unless the exact linear-cubic regular intersection is source-proved.
6. Promote E8_D1 only after SOUND+COMPLETE+TERMINATES+POLY+RECONSTRUCT hold for arbitrary 3CNF.

## Commits newer than semantic checkpoint — MUST INGEST

- `620f19b64a9c` — 2026-09-29T04:03:08+03:00 — R5 E9: eliminate EQ3 private L1 coordinates exactly
- `50c5c8500bf8` — 2026-09-29T04:03:23+03:00 — R5 E9: add exact EQ3 L1 private-elimination checker
- `78e0cbc8909c` — 2026-09-29T04:03:56+03:00 — R5 E9: sync semantic checkpoint to crossing-penalty trade frontier
- `a5b56657ee56` — 2026-09-29T04:08:55+03:00 — R5 E9: derive NAE transversal copy-flow normal form
- `d911d51d384b` — 2026-09-29T04:09:31+03:00 — R5 E9: add exact NAE copy-flow regression
- `9fce9bc8db9b` — 2026-09-29T04:09:38+03:00 — R5 E9: add CI for NAE transversal copy flow
- `cdd3b8c52dd4` — 2026-09-29T04:22:52+03:00 — R5 E9: reduce parity defects to source-signed linear even cover WGFP
- `e2e79fa1c36f` — 2026-09-29T04:23:47+03:00 — R5 E9: add source-signed even-cover WGFP regression
- `4d060d749e84` — 2026-09-29T04:23:56+03:00 — R5 E9: add CI for source-signed even-cover WGFP
- `d71a16a888c1` — 2026-09-29T04:34:04+03:00 — R5 E9: prove maximum linear even-cover saturation equivalence
- `00c94877999b` — 2026-09-29T04:34:20+03:00 — R5 E9: add maximum even-cover saturation regression
- `f675173f3ef1` — 2026-09-29T04:34:29+03:00 — R5 E9: add CI for maximum even-cover saturation
- `4f41dd32fa95` — 2026-09-29T04:40:28+03:00 — R5 E9: add independent-flat two-external augmentation router
- `c7575b64bb28` — 2026-09-29T04:40:47+03:00 — R5 E9: prove fixed-NAE sign equivalence and zero-crossing trap
- `9bb40a0690d2` — 2026-09-29T04:41:12+03:00 — R5 E9: add checker for zero-crossing trap
- `644609b4b4fd` — 2026-09-29T04:42:16+03:00 — R5 E9: prove prime unique-model linear-nullity two-edge tower
- `7e940a17c60b` — 2026-09-29T04:42:48+03:00 — R5 E9: freeze three-external hostile local-minimum countercontrol
- `534eae0ff8a7` — 2026-09-29T04:42:50+03:00 — R5 E9: add regression for prime unique-model nullity tower
- `7b6eafd3315e` — 2026-09-29T04:43:15+03:00 — R5 E9: add IF2E router and three-external hostile regression
- `44d31b0ab5ae` — 2026-09-29T04:48:43+03:00 — R5 E9: falsify circuit-only integer L1 augmentation
- `480eed457223` — 2026-09-29T04:49:04+03:00 — R5 E9: add exact circuit-augmentation barrier checker

## Transport / stale-bootstrap watch

- `.github/workflows/bootstrap-pa0029-nm0033.yml`: **PRESENT** — sha256 `1c797a7936a08cedd722eac59fadda976acd569b64b91f1bec93dcef9cafdc3b`
- `.github/workflows/bootstrap-pa0029-nm0033-arithmetic-repair.yml`: **PRESENT** — sha256 `d2b85f2b6022053a237bbd0d20fa9f6610dfe749b394b6d680696c9d84c22d02`
- `.janus_bootstrap_pa0029_nm0033_payload.txt`: **PRESENT** — sha256 `41d52c45bfa314f66a959159f80d5bfdcaa3d3f9c2141d624f8762899b5e9fe2`
- `.janus_bootstrap_pa0029_nm0033_arithmetic_repair_payload.txt`: **PRESENT** — sha256 `11e93256d6aa25386a9e974972925a635c1738f1c97a49869c8c9aefd8195d4e`

## Must-read authority/evidence artifacts

- **OK** `.janus/P_VS_NP_STREAM_CACHE_CURRENT.json` `d6fc5e9acbbfda5a…`
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
- `a2fa88d9656d` — 2026-09-29T03:58:45+03:00 — R5 E9: add CI for exponential Graver coefficient family

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
