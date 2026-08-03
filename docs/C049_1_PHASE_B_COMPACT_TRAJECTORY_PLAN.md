# C049.1 Phase B — compact B-trajectories and full-set constructor

```text
STATUS = ACTIVE
PHASE_A = IMPLEMENTED / FULL_CI_GREEN
PHASE_B = B1_COMPACT_TRAJECTORY_NORMAL_FORM_PENDING
FULL_FPT_CONSTRUCTOR = NOT_YET_COMPLETE
P_VS_NP = OPEN
```

## Purpose

C048.1 identifies the C047 cut width with the finite-field subspace-arrangement linear-layout width studied by Jeong, Kim and Oum. C049 proves that whole input subspaces must remain grouped leaves. C049.1 Phase A implements provenance-preserving normalization, the JKO column-reduction preprocessing, one sound local `NO_LAYOUT_AT_CAP` obstruction, strict transcript validation, and exact composition of verified layouts with the C047 offset-aware affine-functional trellis.

Phase B must implement the remaining partition-aware FPT discovery engine. It is bound to the corrected extended source:

```text
Jeong–Kim–Oum, arXiv:1507.02184v4
```

Earlier definitions and the proof of Lemma 3.24 were revised; the port must follow v4 rather than silently reconstructing the shorter conference version.

## B1 — canonical compact B-trajectories

The first independently admissible layer implements:

```text
B-statistic validation
trajectory validation
extension relation
canonical compactification
typical-sequence compression
replay trace for every deletion/compression
```

Required invariants:

```text
compact(compact(Gamma)) = compact(Gamma)
canonical output is deterministic
width never increases under compactification
endpoints and boundary subspaces are preserved
invalid or noncanonical transcripts are rejected
```

The independent verifier must reconstruct the normal form without importing the producer.

## B2 — dominance and up_k

After B1, implement the corrected dominance relation and the bounded closure:

```text
Gamma_1 <= Gamma_2
up_k(FullSet)
canonical deduplication
provenance DAG for retained states
domination witness for discarded states
```

Soundness alone is insufficient. The full set must satisfy both obligations:

```text
every retained trajectory is realizable
and
every width-at-most-k layout is represented by a retained trajectory
```

Only the second obligation permits a complete `NO_LAYOUT_AT_CAP` certificate.

## B3 — expand, join and shrink

Operations must preserve the grouped-factor discipline from C049:

```text
one factor normal space = one indivisible leaf
```

Every join charges:

- all input trajectory pairs;
- all lattice paths;
- boundary-coordinate transports;
- intermediate uncompressed trajectories;
- compactification and dominance tests;
- retained and discarded candidates;
- fixed-point certificate bytes.

A small final full set does not excuse an exponential intermediate join.

## B4 — iterative compression

For each newly inserted whole factor:

```text
full set for factors 1..i-1
+ grouped factor V_i
-> partition-aware refinement
-> new full set
-> FOUND_LAYOUT or complete NO_LAYOUT_AT_CAP
```

All failed refinements and all intermediate states are part of the work ledger. The constructor may not record only the successful path.

## B5 — terminal integration with C047

A discovered layout must contain:

```text
complete factor permutation
exact cut-width vector
RREF basis for every cut space
trajectory ancestry
iterative-compression transcript
constructor and capability digests
```

`FOUND_LAYOUT` is then compiled by C047 with every distinguished affine offset functional `beta_i` preserved.

A complete negative terminal is allowed only when the replayed root full set contains no accepting width-`k` trajectory:

```text
NO_LAYOUT_AT_CAP
```

Until B1–B4 and the completeness proof are implemented, the only honest engine terminal is:

```text
OPEN_TRAJECTORY_ENGINE_INCOMPLETE
```

It must never be converted into `NO_LAYOUT_AT_CAP`.

## Capability terminals

```text
OPEN_DISCOVERY_BUDGET
OPEN_WORK_BUDGET
OPEN_CERTIFICATE_VOLUME
OPEN_TRAJECTORY_ENGINE_INCOMPLETE
```

Every refusal is bound to an explicit fixed capability and independently replayed.

## Forbidden shortcuts

```text
NO_UNPARTITIONED_BASIS_EXPANSION
NO_SUPPLIED_LAYOUT_PROMOTED_TO_DISCOVERY
NO_BARE_NO_LAYOUT_TRANSCRIPT
NO_BRANCH_VALUE_DEPENDENT_DISCOVERY
NO_HIDDEN_SAT_OR_EQUIVALENCE_ORACLE
NO_FIXED_K_FPT_PROMOTED_TO_UNIVERSAL_POLYNOMIAL
NO_OPEN_PROMOTED_TO_HARDNESS
```

## Completion criterion

C049.1 is complete only when the repository contains an executable producer and independent verifier for B1–B5, a frozen audit, full work and certificate accounting, replayable `FOUND_LAYOUT` and `NO_LAYOUT_AT_CAP`, and exact C047 SAT/UNSAT composition.

```text
P_VS_NP=OPEN
```
