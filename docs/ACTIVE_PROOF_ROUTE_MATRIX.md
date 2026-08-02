# JANUS Active Proof Route Matrix

**Purpose:** compare every new mechanism against the existing proof graph before
creating another hypothesis.

```text
P_VS_NP=OPEN
```

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C023 | Boolean polymorphism admission | Exact Schaefer dispatch and fixed `{NAND3,NEQ}` obstruction | Separate tractable languages imply tractable mixture | Instance-specific decomposition with charged interfaces |
| C024 | Fracture channel core | Coarse region graph can be a star while exact elimination recovers arbitrary 3-CNF | Low coarse fracture treewidth captures hardness | `NONLINEAR_QUOTIENT_CORE` |
| C025 | Certified residual quotient | Separates residual-state volume from semantic merge-proof volume | Free semantic equality merging | `CERTIFIED_RESIDUAL_QUOTIENT_COMPLEXITY` |
| C027 | Context projection discovery | OR and XOR cones have exact but representation-sensitive projections | Compact circuit implies tractable projection | `TRACTABLE_PROJECTION_DISCOVERY` |
| C028 | Mixed-cone invariants | Decomposable NNF is tractable; overlap variables form a backdoor | Determinism, gate-tree topology and constant alternation imply tractability | `SEMANTIC_SUPPORT_OVERLAP` |
| C029 | Occurrence-splitting minor | Connected equality splitting preserves the source incidence graph as a minor | Variable copying plus equalities lowers incidence width | `NON_MINOR_PRESERVING_SEMANTIC_COMPRESSION` |
| C032 | PS-width alignment | JANUS cut signatures are exactly PS-width signatures; high treewidth can have PS-width 2 | Inventing a new enumerative cut parameter | `POLYNOMIAL_PS_DECOMPOSITION_OR_SYMBOLIC_SIGNATURE_COMPRESSION` |
| C033 | Proof-carrying tractable portfolio | Normalization plus exact Horn, dual-Horn and beta-acyclic solving with witness recovery and strict `OPEN` | Every tractable regime must first have small explicit PS tables | `PORTFOLIO_SELECTION_WITH_SYMBOLIC_MESSAGES` |
| C034 | Affine and cross-class composition | Replayable GF(2) certificates and exact `O(2^k poly(L))` heterogeneous composition for shared boundary `k` | Named tractable modules imply an unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Replayed exact residual messages give a sound merge congruence; absorbing proofs and affine RREF produce real compression | Exponential diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact semantic cut signatures or certified symbolic elimination
-> proof-carrying cross-class interface compression
-> jointly selected decomposition, message language and proof rules
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C034 completed the first four-engine restricted portfolio and proved exact
composition for logarithmic shared boundaries. C035 now supplies the first
sound proof-carrying state merge rule and shows why a fixed tuple of exact local
messages is not enough: it may under-merge exponentially even on an easy Horn
family unless cross-module certificates and decomposition selection are charged.

The immediate target is C036:

```text
PROOF-CARRYING PARTITION REFINEMENT
```

Start from coarse verified terminal classes, refine only when an explicit
continuation separates two states, attach a replayable separating witness or
proof, and return `OPEN` when separator discovery, quotient size or certificate
volume exceeds a polynomial budget.

## Converged constructive bottleneck

The following names are now linked views of one missing core:

```text
C025 certified residual quotient complexity
C032 symbolic PS-signature compression
C033 portfolio selection with symbolic messages
C034 proof-carrying cross-class interface compression
C035 joint decomposition/language/proof selection
```

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a strictly stronger replayable
message algebra, or a decisive obstruction to one explicit construction route.

## Separation track

```text
proof-carrying circuit refuter
-> certificate-preserving SAT embedding
-> no-sharing amplification
-> SAT not in P/poly
-> P != NP
```

This track remains useful as an adversarial control even while the user-selected
primary objective is `P=NP`.

## Non-duplication rule

Before admitting a new hypothesis, compare it against:

```text
PS-width
MIM-width / incidence width
DNNF / d-DNNF / OBDD / SDD
backdoor size
residual-state width
proof width and certificate discovery
beta-acyclic elimination
Davis-Putnam variable elimination
Horn and dual-Horn closure
GF(2) affine elimination
Schaefer fixed-language mixtures
communication/continuation equivalence across cuts
partition refinement and canonical residual automata
```

A renamed known parameter is registered as an alignment result, not promoted as
a new theorem.
