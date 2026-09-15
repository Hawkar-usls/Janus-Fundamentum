# 2026-09-15 — Wide / mixed interface continuity checkpoint

Authority: `CONTINUITY_CHECKPOINT__SCOPED_AUTHORITIES_ONLY__NO_GLOBAL_PROMOTION`

## Integration anchor

The previously diverged research lineage was integrated into `main` through PR #443 with merge commit:

`77cb1fb03c2b93540bc4e23b0dc98d2986870d1d`

Both parents were preserved:

- prior `main`: `af1798dc57d287485bb6739dde9ee4682dffbba4`
- scoped research lineage: `ab94a94010d686a175f1d064b109b235e9f085c7`

No historical scientific verdict was rewritten.

## Newly integrated scoped authorities

### Wide exact-interface quotient

Verdict: `PASS_U1_AND_P1_SCOPED_SEPARATION`.

- unrestricted downstream coordinate-observation contract can require all `2^|B|` exact classes;
- strict affine downstream contracts may factor exactly through a low-rank syndrome;
- representative control: `|B|=32`, rank `5`, raw `2^32` assignments -> `32` exact syndrome classes;
- no raw assignment enumeration in discovery;
- result lineage head: `3df50dcb6ba8a9279b419d00661e837f529033a3`;
- seal: `f6c8af94a7a609b45812aa572f20f50fe73991c8`.

### Factorized feedback-interface portfolio

Verdict: `PASS_SCOPED_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO`.

If the complete frozen downstream dependency hypergraph over a wide feedback interface decomposes exactly into disconnected components and every component has a separately sealed polynomial exact carrier, the global representation is the additive portfolio `[Q_1,...,Q_t]`; the Cartesian product is not materialized.

- result seal commit: `b4e26b71ad0f0d1aa69ee456efe0439cea48f28f`;
- Actions run: `34910238642`;
- exact cross-component transfer or reconstruction coupling forces component merge;
- unknown connected wide component fails closed.

### Connected mixed-carrier Schaefer barrier

Verdict: `PASS_SCHAEFER_MIXED_CARRIER_BARRIER`.

For the fixed language `Gamma={OR2, EVEN_XOR3}`:

- `OR2` is individually bijunctive/2CNF;
- `EVEN_XOR3` is individually affine;
- the combined language is neither 0-valid, 1-valid, Horn, dual-Horn, bijunctive, nor affine;
- by the source-bound Boolean Schaefer dichotomy, `SAT(Gamma)` is NP-complete.

Therefore a polynomial exact mechanism for **all** connected instances of this fixed mixed language would imply `P=NP`. This is a conditional classification barrier, not a proof that such a mechanism cannot exist.

- result seal commit: `ecd6b72ed74380d2a6c211df66c473a4d5f32dd0`;
- Actions run: `34910835360`.

### Logarithmic alien-constraint exact transfer

Verdict: `PASS_SCOPED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER`.

Two admitted orientations:

- OR2 base + EVEN_XOR3 aliens: enumerate exactly `4^k` alien tuple selections; admit only when `4^k <= L`;
- affine EVEN_XOR3 base + OR2 aliens: enumerate exactly `3^k` alien tuple selections; admit only when `3^k <= L`.

Each surviving tuple selection gives explicit pins into the native polynomial base solver. Overlap-inconsistent selections are rejected. SAT witnesses replay every original relation; UNSAT requires complete alien-branch accounting.

Hence the admitted lifecycle is `L * poly(L)` and does not enumerate the full variable cube.

- result seal commit: `39b7a0af2c0849dcac163aba62eccf9f18963800`;
- Actions run: `34911259582`;
- positive controls were connected and cyclic (cycle ranks `6` and `2` in the independent checker);
- over-budget cases return `OPEN_ALIEN_TUPLE_BUDGET` before enumeration.

## Current scoped open surface

`CONNECTED_MIXED_CARRIER_WITH_SUPERLOGARITHMIC_ALIEN_TUPLE_BUDGET_AND_NO_OTHER_SEALED_STRUCTURE`

The next positive mechanism must reduce the **effective alien-choice dimension** through an exact, preregistered structure such as factorization, quotient/rank, bounded alien interaction width, or another proved carrier. A generic unrestricted mixed-language glue is forbidden as a routine assumption by the Schaefer barrier.

## Global scientific state unchanged

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- historical v1.1 `FAIL_NO_TRANSFER_RULE` remains immutable historical authority
- v1.3 composite scoped PASS remains valid in its own scope
- `APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE` remains the global APMA frontier status recorded by its authority; the scoped interface results above have `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
