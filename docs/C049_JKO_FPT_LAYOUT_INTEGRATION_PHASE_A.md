# C049.1 — proof-carrying Jeong–Kim–Oum layout integration, Phase A

## Status

```text
PHASE_A = IMPLEMENTED / SELF_TEST_GREEN
FULL_FPT_CONSTRUCTOR = PENDING
P_VS_NP = OPEN
```

C048.1 identifies the C047 cut width

\[
\max_t \dim\bigl(P_t\cap S_t\bigr)
\]

with the linear-layout width of a finite-field subspace arrangement. Jeong, Kim and Oum proved a constructive fixed-parameter algorithm for finding a width-at-most-`k` layout when one exists over a fixed finite field.

C049.1 follows the C049 grouped-subspace partition obstruction and must integrate that constructor without treating its internal dynamic program or a supplied layout as free. Phase A implements the sound preprocessing and transcript boundary needed before the full B-trajectory/full-set engine is ported.

## Implemented in Phase A

### 1. Provenance-preserving normalization

Every forbidden affine factor remains represented by its exact equation list. Layout construction uses only its normal space; the C047 trellis retains all affine right-hand sides as the distinguished offset functional.

### 2. JKO column-reduction skeleton

For each factor normal space `V_i`, Phase A constructs

\[
V_i' = V_i \cap \operatorname{span}\{V_j:j\ne i\}.
\]

The package records RREF bases for `V_i`, the span of all other spaces, and `V_i'`. The audit checks exhaustively on small arrangements that every permutation has exactly the same cut-width vector before and after this reduction.

This is the GF(2) specialization of the column-reduction step in Jeong–Kim–Oum, Lemma 5.2.

### 3. Sound local `NO_LAYOUT_AT_CAP`

Jeong–Kim–Oum Proposition 2.2 implies that if a layout has width at most `k`, then

\[
\dim\left(V_i\cap\operatorname{span}(\mathcal V\setminus\{V_i\})\right)\le 2k
\]

for every factor. Therefore a reduced dimension greater than `2k` is a replayable certificate that no linear layout of width at most `k` exists.

Phase A emits `NO_LAYOUT_AT_CAP` only for this internally reconstructed obstruction. A bare external no-layout transcript is rejected as

```text
OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT
```

because the complete full-set rejection proof is not yet implemented.

### 4. Verified `FOUND_LAYOUT` to C047 composition

A `FOUND_LAYOUT` transcript contains:

- the complete factor permutation;
- the exact cut-width vector;
- an RREF basis of every cut space;
- constructor identity and trace;
- a transcript digest.

The verifier recomputes every cut from the original and reduced spaces. Only an exact width-at-most-`k` layout is passed to an independently replayed C047 offset-aware functional trellis.

External layouts are accepted only as `REPLAY_ONLY` evidence:

```text
discovery_claim = false
```

They are never counted as an implementation of the published constructor.

### 5. Complete capability accounting

Phase A charges:

- all other-space spans and factor intersections;
- baseline or transcript-validation discovery;
- both original and reduced cut computations;
- the nested C047 work ledger;
- outer certificate bytes to a fixed point;
- independent verifier reconstruction.

Exact refusal terminals include:

```text
OPEN_FPT_ENGINE_PENDING
OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT
OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT
OPEN_DISCOVERY_BUDGET
OPEN_WORK_BUDGET
OPEN_CERTIFICATE_VOLUME
```

All refusal evidence is independently replayed.

## Frozen audit

```text
90 random column-reduction fixtures
13,595 complete permutation checks
0 cut-width preservation failures
0 unsound local obstructions

local dim(V_i ∩ span others) > 2k -> NO_LAYOUT_AT_CAP
duplicate-offset C046 family      -> SAT
complementary-offset C046 family  -> UNSAT
verified hidden-order transcript  -> SAT / width 2 / replay-only
bare NO_LAYOUT transcript         -> rejected
modified layout transcript        -> rejected
missing full-set engine           -> OPEN_FPT_ENGINE_PENDING
work/certificate refusal evidence -> independently replayed
corrupt SAT and OPEN evidence      -> rejected
```

Frozen integrity:

```text
b38c982c7657f5f5e20a704ad46c65ab54c7b31a6104f4b8cb744f9aeff09ae3
```

## Remaining C049.1 obligation

Phase A does **not** implement the FPT constructor itself. The remaining engine must faithfully port and charge:

1. compact `B`-trajectories and typical-sequence compression;
2. the `up_k` full-set closure;
3. `expand`, `join`, and `shrink` over a bounded-width branch decomposition;
4. iterative compression from `n-1` to `n` subspaces;
5. deterministic reconstruction of `FOUND_LAYOUT`;
6. complete replayable `NO_LAYOUT_AT_CAP` when the full set contains no width-`k` trajectory;
7. all intermediate states, lattice paths, failed refinements, coefficient volume, and certificate bytes.

The published theorem closes existence for fixed `k`; C049.1 still owes the proof-carrying implementation.

## Claim boundary

C049.1 Phase A does not claim a complete reimplementation of Jeong–Kim–Oum, does not claim a polynomial algorithm for unbounded `k`, does not solve the NAND3+NEQ hard image, and does not resolve P versus NP.
