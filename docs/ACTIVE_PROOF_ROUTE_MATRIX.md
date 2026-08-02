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
| C036.1 | Horn-affine negotiation extension | Complete affine-to-Horn directed inclusion and replayable shared-literal conflict traces | A propagation fixpoint certifies compatibility | `REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA` |
| C037 | Explicit residual OBDD alignment | Exact minimization and certificates after explicit fixed-order state generation | Partition refinement alone avoids state explosion | `POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact cut continuation rows and replayable factor separators for a verified vtree | Recursive structure or a supplied vtree automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C038.0 | Exact OPEN core vault | Capability-scoped replayable reuse of exact portfolio refusal records | Similarity or reduction to an OPEN core proves OPEN | `NO_STRUCTURAL_OPEN_PROPAGATION` |
| C039 | Fixed-k recursive separator compiler | One assignment-independent vtree and exact `n^O(k)` symbolic structured compilation for fixed discoverable separator bound `k` | Full cut-table enumeration is required; branch-dependent vtrees are harmless | `SEMANTIC_VTREE_DISCOVERY_BEYOND_GRAPH_SEPARATORS` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact semantic cut signatures or certified symbolic elimination
-> proof-carrying cross-class interface compression
-> jointly selected decomposition, message language and proof rules
-> certified merge, separator extraction and cross-language fact exchange
-> polynomial reachable quotient construction
-> exact structured vtree factorization
-> symbolic factor construction without full truth-table enumeration
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C037 identifies fixed-order continuation quotients with reduced OBDDs. C038
moves to recursive vtrees but constructs exact cut factors by explicit row
enumeration.

C039 supplies the first restricted symbolic construction through this gate. For
fixed separator bound `k`, it discovers one recursive balanced-separator plan
before value branching and compiles along one verified vtree in `n^O(k)` total
work. Separator assignments are deterministic OR branches and predetermined
components are decomposable AND children.

The equality family separates C039 from a blocked OBDD order:

```text
EQ_12 blocked OBDD width  4096
C039 structured nodes        13
```

The limitation is equally important. A dense clique-primal dual-Horn formula is
solved by C033 but returns `OPEN` in C039. Thus graph separators alone are not the
universal semantic-vtree selector.

The immediate target is C040:

```text
PORTFOLIO_GUIDED_SEMANTIC_VTREE_DISCOVERY
```

Construct decomposition decisions from proof-carrying Horn/dual-Horn closure,
affine row spaces, beta-acyclic elimination, PS signatures, C036.1 facts and
compiled messages. Charge discovery, intermediate size, joins, projections,
merge/separator proofs, SAT witness recovery and UNSAT certificate discovery.

## Canonical cycle allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 Horn-affine negotiation extension
C037   explicit residual OBDD alignment
C038   exact structured-vtree factor alignment
C038.0 exact OPEN cache side branch
C039   fixed-k symbolic recursive separator compiler
C040   portfolio-guided semantic-vtree discovery
```

Some pre-admission branches and implementation files retain legacy cycle
spellings for exact replay. Canonical docs, entrypoints, machine-readable
proposals and this matrix control the logical numbering.

## Converged constructive bottleneck

```text
C025 certified residual quotient complexity
C032 symbolic PS-signature compression
C033 portfolio selection with symbolic messages
C034 proof-carrying cross-class interface compression
C035 joint decomposition/language/proof selection
C036 cross-language symbolic separator discovery
C036.1 stronger cross-language fact algebra
C037 ordered reachable quotient construction
C038 exact vtree-factor construction
C039 restricted symbolic factor construction
```

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a stronger replayable message
algebra, a complete separator extractor for a larger closed language, or a
decisive obstruction to one explicit route.

## Separation track

```text
proof-carrying circuit refuter
-> certificate-preserving SAT embedding
-> no-sharing amplification
-> SAT not in P/poly
-> P != NP
```

This remains an adversarial control while the selected primary objective is a
constructive proof of `P=NP`.

## Non-duplication rule

Before admitting a new hypothesis, compare it against:

```text
PS-width
MIM-width / incidence / primal treewidth
DNNF / d-DNNF / structured d-DNNF / OBDD / SDD / TDD
factor width and vtree communication rows
backdoors and residual-state width
proof width and certificate discovery
beta-acyclic and Davis-Putnam elimination
Horn / dual-Horn closure
GF(2) affine elimination
Schaefer fixed-language mixtures
communication/continuation equivalence
partition refinement and canonical residual automata
active learning and equivalence-query teachers
DPLL(T) / DPLL(XOR) fact exchange
bottom-up knowledge-compilation intermediate blow-up
```

A renamed known parameter is registered as an alignment result, not promoted as
a new theorem.
