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
| C033 | Proof-carrying tractable portfolio | Exact Horn, dual-Horn and beta-acyclic solving with witness recovery and strict `OPEN` | Every tractable regime must first have small explicit PS tables | `PORTFOLIO_SELECTION_WITH_SYMBOLIC_MESSAGES` |
| C034 | Affine and cross-class composition | Replayable GF(2) certificates and exact `O(2^k poly(L))` heterogeneous composition | Named tractable modules imply unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Replayed residual messages give a sound merge congruence; absorbing proofs and affine RREF compress | Exponential diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Proof-carrying partition refinement | Complete polynomial separator extraction for Horn and affine residuals | Failure to find a separator permits merging | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C037A | Explicit residual OBDD alignment | Exact continuation quotient and certificates after explicit fixed-order state generation | Partition refinement alone avoids state explosion | `POLYNOMIAL_ORDER_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C037B | Certified Horn-affine ping-pong | Complete affine-to-Horn inclusion test and sound unary fact exchange with proof cache | A propagation fixpoint certifies compatibility | `REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA` |
| C038 | Recursive separator structured compiler | One assignment-independent vtree and exact `n^O(k)` proof-carrying compilation for fixed discoverable separator bound `k` | A supplied or branch-dependent vtree is free; small final circuit implies cheap construction | `SEMANTIC_VTREE_DISCOVERY_BEYOND_GRAPH_SEPARATORS` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact semantic cut signatures or certified symbolic elimination
-> proof-carrying cross-class interface compression
-> jointly selected decomposition, message language and proof rules
-> certified merge, separator extraction and fact exchange
-> polynomial structured reachable-message construction
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C037A identifies fixed-order quotient construction with reduced OBDDs.
C037B crosses the Horn-affine boundary in one complete direction and supplies a
sound but incomplete proof-carrying negotiation fixpoint.

C038 replaces one linear order by one verified recursive separator plan. For
every fixed separator bound `k`, the plan and structured deterministic
compilation are constructed and checked in `n^O(k)` total work. Every assignment
branch uses the same vtree.

The result is still restricted. A dense clique-primal dual-Horn formula returns
`OPEN` in C038 although C033 solves it. Hence graph separators cannot be the
universal selector.

The immediate target is C039:

```text
SEMANTIC VTREE DISCOVERY BEYOND GRAPH SEPARATORS
```

The next constructor must combine graph decomposition with Horn/dual-Horn
closure, affine row spaces, beta-acyclic elimination, PS signatures, C037B
cross-language facts and verified compiled messages. It must charge discovery,
intermediate object size, join/project work, merge/separator proofs, witness
recovery and UNSAT certificate discovery.

## Converged constructive bottleneck

The following are linked views of the same missing universal core:

```text
C025 certified residual quotient complexity
C032 symbolic PS-signature compression
C033 portfolio selection with symbolic messages
C034 proof-carrying cross-class interface compression
C035 joint decomposition/language/proof selection
C036 cross-language symbolic separator discovery
C037A ordered reachable quotient construction
C037B stronger cross-language fact algebra
C038 structured vtree and reachable-message construction
```

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a strictly stronger replayable
message algebra, a complete separator extractor for a larger closed language, or
a decisive obstruction to one explicit route.

## Separation track

```text
proof-carrying circuit refuter
-> certificate-preserving SAT embedding
-> no-sharing amplification
-> SAT not in P/poly
-> P != NP
```

This track remains an adversarial control while the selected primary objective
is a constructive proof of `P=NP`.

## Non-duplication rule

Before admitting a new hypothesis, compare it against:

```text
PS-width
MIM-width / incidence / primal treewidth
DNNF / d-DNNF / structured d-DNNF / OBDD / SDD
backdoor size
residual-state width
proof width and certificate discovery
beta-acyclic and Davis-Putnam elimination
Horn and dual-Horn closure
GF(2) affine elimination
Schaefer fixed-language mixtures
communication/continuation equivalence
partition refinement and canonical residual automata
active automata learning and equivalence-query teachers
DPLL(T) / DPLL(XOR) style fact exchange
bottom-up knowledge-compilation intermediate blow-up
```

A renamed known parameter is registered as an alignment result, not promoted as
a new theorem.
