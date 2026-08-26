# Q0 Typed Anchor-Gauge Quotient

Status: **PROPOSAL / NOT ADMITTED**

Target: reduce exact-residual proliferation in `JANUS-FC_local` without replacing proof preservation by a heuristic similarity score.

## State corridor

```text
𓂸 → JANUS → 𓨍 → JANUS → 𓇠 → JANUS → 𓆇 → JANUS → 𓨍 → JANUS → 𓂺
```

Project-only state meanings:

- `𓂸` (Unicode U+130B8, D052): generator/source checkpoint.
- `𓨍` (Unicode U+13A0D, Extended-A D32 female-genitals group): receiver/squeeze / identity-erasure boundary.
- `𓇠` (Unicode U+131E0, M033): seed/grain checkpoint; minimal surviving invariant.
- `𓆇` (Unicode U+13187, H008; Unicode annotation `sꜣ`, son): child/birth checkpoint.
- `𓂺` (Unicode U+130BA, D053): distinct return/generator endpoint.

These glyphs are modern JANUS protocol delimiters. Their ancient lexical meanings are not mathematical evidence.

## Input object

A residual is not treated merely as bytes. The proposed typed object is

```text
R(F) = (
  residual_cnf = F,
  signed_clause_variable_incidence,
  variable_local_types,
  clause_local_types,
  anchor_partition,
  coordinate_map
)
```

The first Q0 experiment uses only structure that is exactly reconstructible from the residual CNF.

## Relax → Aggregate → Close adaptation

The architecture is inspired by typed-residual / relax-aggregate-close ideas, but logical soundness is supplied by explicit SAT-preserving certificates rather than statistical orthogonality.

### RELAX

1. exhaustive unit propagation under the existing Policy-0A semantics;
2. construct signed clause-variable incidence;
3. refine local variable/clause types by deterministic color refinement;
4. preserve sign and clause-width information.

No cross-type merge occurs during RELAX.

### AGGREGATE

The fixed identity-erasure boundary is entered only when the variable partition becomes discrete under the registered refinement rule.

A deterministic anchor order is then induced by the final typed colors.

### CLOSE

Rename variables by the anchor order and serialize the full canonical CNF.

The quotient key is the complete renamed CNF, not the color signature alone.

```text
Q0(F) = CANONICAL_RENAMED_CNF(F)
```

If the refinement is not discrete, Q0 falls back to the existing byte-for-byte residual key. This makes Q0 incomplete as an isomorphism quotient but keeps the first implementation polynomial and fail-closed.

## Soundness contract

A cache reuse across bytewise-distinct residuals is admitted only when the implementation records an explicit variable permutation `π` satisfying

```text
π(F) == Q0(F)
π(G) == Q0(G)
Q0(F) == Q0(G)
```

with exact clause equality after renaming.

Therefore

```text
SAT(F) iff SAT(G)
```

follows from an explicit CNF isomorphism, not from approximate similarity, Neyman orthogonality, Kolmogorov complexity, or a learned embedding.

The permutation is also the required witness-lift skeleton: an assignment over canonical variables can be mapped back by `π^-1`. The first probe may count decision-cache merges before full witness materialization is wired into Policy-0A; such a probe is not enough to admit the unrestricted bridge.

## Complexity contract

Q0 must charge:

- signed incidence construction;
- all refinement rounds;
- anchor sorting;
- full renamed-CNF serialization;
- permutation verification;
- cache lookup;
- witness map storage/recovery when enabled.

The first version uses deterministic partition refinement and refuses ambiguous color classes instead of solving general graph canonical labeling. No claim that general graph isomorphism/canonical labeling has been reduced to polynomial time is permitted.

## Relation to external inspirations

### FPRC-PQ / residual algebra

Typed residual ownership, an explicit identity-erasure boundary, and relax-aggregate-close are used as architectural inspiration. Statistical coupled-path/Neyman-style orthogonality is **not** treated as a Boolean proof-preservation theorem.

### Residue-number / resonator decoding

Resonator networks may be explored later as a representation decoder. They are not part of Q0 soundness and cannot replace exact SAT witness recovery without a separate proof-carrying encoding/decoding theorem.

### Structure / description length

Low description length or compositional structure may motivate candidate mappings. It is not a proof of polynomial complexity and is not a cache-reuse license.

## Birth rule

```text
SEED != THEOREM
BIRTH != P_EQ_NP
```

A `𓆇` CHILD/BIRTH event is recorded only when a frozen seed produces a new falsifiable theorem/algorithm candidate that survives its registered forward and reverse checks.

For Q0 the first possible child is:

```text
Q0_TYPED_ISOMORPHIC_RESIDUAL_REUSE
```

Its first question is finite and exact:

> Does Q0 merge any bytewise-distinct residual states on the registered graph-tautology calibration family while preserving every Boolean answer and charging quotient work?

## Gates

1. `Q0_IMPLEMENTATION_EXISTS`
2. `Q0_EXACT_PERMUTATION_CHECK_PASS`
3. `Q0_NO_FALSE_BOOLEAN_REUSE_ON_CALIBRATION`
4. `Q0_BYTEWISE_DISTINCT_MERGE_COUNT_REPORTED`
5. `Q0_COST_LEDGER_REPORTED`
6. `Q0_WITNESS_LIFT_IMPLEMENTED`
7. freeze a new polynomial envelope from calibration only
8. execute one untouched holdout with no post-hoc cap changes

## Claim boundary

```text
Q0_PROPOSAL != POLYNOMIAL_SAT_SOLVER
Q0_FINITE_COMPRESSION != ASYMPTOTIC_POLYNOMIAL_BOUND
Q0_ISOMORPHISM_REUSE != GENERAL_FORMULA_CACHING_SIMULATION_THEOREM
NEyman_ORTHOGONALITY != SAT_EQUIVALENCE_CERTIFICATE
RESONATOR_DECODING != SAT_WITNESS_RECOVERY_THEOREM
P_VS_NP = OPEN
```
