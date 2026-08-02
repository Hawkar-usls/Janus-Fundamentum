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
| C036 | Proof-carrying partition refinement | Complete polynomial separator extraction for Horn and affine residuals; every accepted split carries a replayable continuation | Failure to find a separator permits merging; explicit refinement automatically has polynomial state generation | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C037 | Explicit residual OBDD alignment | Exact minimization, pairwise distinguishing suffixes, SAT witnesses and UNSAT DAG certificates once the residual graph is explicit | Partition refinement alone avoids state explosion; an equivalence-query teacher is free | `POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact vtree-cut continuation rows, replayable separators, witness/UNSAT tables and deterministic charged candidate construction | Recursive structure or a supplied vtree automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact semantic cut signatures or certified symbolic elimination
-> proof-carrying cross-class interface compression
-> jointly selected decomposition, message language and proof rules
-> certified merge and separator extraction
-> polynomial reachable quotient construction
-> polynomial vtree discovery and symbolic factor construction
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C036 supplies polynomial same-language separator extraction for Horn and affine
messages. C037 supplies the complete continuation quotient after an exact finite
residual graph has been generated and aligns fixed-order refinement with reduced
OBDD.

C038 moves from one line to a recursive vtree. For each vtree cut it constructs
the exact Boolean communication rows and their continuation quotient, together
with replayable outside-assignment separators. This is aligned with structured
d-DNNF / SDD / TDD factor-width views; it is not a new width parameter.

The equality control shows both sides of the result:

```text
paired vtree: local equality interactions remain small
blocked vtree: one cut has exactly 2^n continuation rows
```

A deterministic co-occurrence heuristic rediscovers the paired structure on this
family, but no universal optimality or polynomial-width guarantee is claimed.

The immediate target is C039:

```text
SYMBOLIC_FACTOR_CONSTRUCTION_WITHOUT_TRUTH_TABLE_ENUMERATION
```

Construct the same cut quotient and proof objects using Horn, affine,
beta-acyclic, PS-signature or compiled symbolic messages, while charging vtree
discovery, joins, projections, merges, separators, SAT witness recovery and UNSAT
certificate discovery. Return `OPEN` when any volume exceeds an explicit
polynomial budget.

## Lineage warning

Two sibling draft PRs currently use the label `C037`: the explicit OBDD alignment
and the Horn-affine negotiation bridge. C038 is stacked on the OBDD branch because
it generalizes its decomposition axis. Canonical admission must reconcile the
numbering and preserve both results without silently overwriting either route.

## Converged constructive bottleneck

The following names are linked views of one missing core:

```text
C025 certified residual quotient complexity
C032 symbolic PS-signature compression
C033 portfolio selection with symbolic messages
C034 proof-carrying cross-class interface compression
C035 joint decomposition/language/proof selection
C036 cross-language symbolic separator discovery
C037 order/decomposition and reachable quotient construction
C038 vtree discovery and symbolic factor construction
```

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a strictly stronger replayable
message algebra, a complete separator extractor for a larger closed language, or
a decisive obstruction to one explicit construction route.

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
DNNF / d-DNNF / OBDD / SDD / TDD
factor width and vtree communication rows
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
symbolic bisimulation and distinguishing-test bases
active automata learning and equivalence-query teachers
```

A renamed known parameter is registered as an alignment result, not promoted as
a new theorem.
