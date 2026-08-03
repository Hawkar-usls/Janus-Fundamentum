# C049.1 Phase B2 — extension preorder, domination receipts, and `up_k`

Phase B2 implements the next closed layer of the Jeong–Kim–Oum full-set engine over `GF(2)`. It uses the corrected definitions in `arXiv:1507.02184v4`; it does not introduce a new trajectory relation.

## 1. Extension preorder

For compact `B`-trajectories `Gamma` and `Delta`, the producer decides

```text
Gamma preccurlyeq Delta
```

by the lattice-path characterization from Section 3.2. A valid path starts at `(0,0)`, ends at `(|Gamma|-1,|Delta|-1)`, uses only `(1,0)`, `(0,1)`, or `(1,1)` steps, and at every visited pair compares statistics with identical `(L,R)` and nondecreasing `lambda`.

The emitted witness contains the complete deterministic lattice path. For the focused positive fixture, the path must repeat a statistic and therefore proves the extension semantics rather than merely pointwise comparison at the original lengths.

## 2. Why a removed generator is safe

The implementation minimizes a finite generator family before constructing `up_k`. A generator `Delta` is deleted only with a direct retained witness

```text
Gamma preccurlyeq Delta.
```

For every candidate `Theta`, if the deleted generator could cover it, then

```text
Delta preccurlyeq Theta.
```

Transitivity of the published preorder gives

```text
Gamma preccurlyeq Theta.
```

Thus every state covered through `Delta` remains covered through the retained `Gamma`. The reverse inclusion is immediate because every retained generator came from the original family. Therefore

```text
up_k(original generators) = up_k(retained generators).
```

Equivalent generators are reduced to the lexicographically least canonical representative; strict predecessors are preferred to strictly larger generators. Every deletion has its own lattice-path receipt. No deletion is justified by a digest, heuristic score, supplied layout, or SAT result.

## 3. Complete finite `U_k(B)` closure

For an admitted boundary dimension `dim(B)` and width cap `k`, the producer:

1. enumerates every `GF(2)` subspace of `B` in canonical RREF form;
2. enumerates every compact `B`-trajectory up to the published length bound
   `(2 dim(B)+1)(2k+1)`;
3. tests every candidate against the minimized generators using the exact extension preorder;
4. emits every retained `up_k` entry with a source-generator index and lattice path.

The enumeration is a computable function of `dim(B)` and `k`; Phase B2 does not claim that these parameters are universally bounded. The later branch-decomposition integration must provide and charge that bound.

## 4. Accounting and refusal terminals

The ledger separately charges canonical row reduction, pivot tests, XORs, subspace inclusion reductions, trajectory prefixes, extension trials, universe entries, lattice cells, predecessor tests, path vertices, pairwise dominance tests, witnesses, and full-set entries. Boundary-coordinate changes are explicitly present with value zero in this phase and become active in expand/join/shrink.

The only capability refusals are:

```text
OPEN_DISCOVERY_BUDGET
OPEN_WORK_BUDGET
OPEN_CERTIFICATE_VOLUME
```

Every closed and refused case binds a fixed-point serialized certificate size and an integrity digest.

## 5. Independent audit

The verifier imports neither the B2 producer nor the B2 core. It independently reimplements `GF(2)` canonicalization, compactness, the lattice-path relation, all subspaces, all compact trajectories for the audit boundaries, generator minimization, closure equality, and semantic tamper rejection.

Frozen results:

```text
7 total cases
4 CLOSED_EXACT
1 OPEN_DISCOVERY_BUDGET
1 OPEN_WORK_BUDGET
1 OPEN_CERTIFICATE_VOLUME

dim(B)=1, k=1:
  complete compact universe = 552
  retained up_k entries     = 42
  input generators          = 3
  retained generators       = 2
  deleted generators        = 1

dim(B)=0, k=2:
  complete compact universe = 27
  retained up_k entries     = 27

semantic tamper controls:
  lattice path              rejected
  missing full-set entry    rejected
  deletion witness          rejected
```

Frozen artifact digest:

```text
4c62118a3d4cf7928c0cd99d016c8063e63c8932b7ee4c020a0be815d22375cd
```

## Strict boundary

Phase B2 does not implement partition-aware `expand`, `join`, or `shrink`; it does not run the branch-decomposition dynamic program or iterative compression; it cannot emit complete `NO_LAYOUT_AT_CAP`; and it does not yet compose a discovered layout through C047.

```text
NEXT_GATE = C049.1_PHASE_B3_PARTITION_AWARE_EXPAND_JOIN_SHRINK
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
