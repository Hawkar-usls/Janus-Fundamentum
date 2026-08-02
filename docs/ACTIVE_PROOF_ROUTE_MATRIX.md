# JANUS Active Proof Route Matrix

**Purpose:** compare every new mechanism against the existing proof graph before creating another hypothesis.

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
| C036.1 | Explicit residual OBDD alignment | Exact minimization, distinguishing suffixes, SAT witnesses and UNSAT DAG certificates after explicit residual generation | Partition refinement alone avoids state explosion; an equivalence-query teacher is free | `POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C037 | Horn-affine negotiation | Complete affine-to-Horn directed inclusion/separator extraction plus replayable shared-literal conflict traces and SQLite proof caching | A propagation fixpoint certifies compatibility; constants-only exchange decides Horn-affine mixtures | `REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA` |
| C037.1 | Pairwise Horn parity aliases | Complete proof-carrying extraction of all shared Horn equalities, compressed to a spanning forest; Horn disequalities collapse to unary facts | Binary SCC extraction is complete for arbitrary Horn; pairwise aliases decide Horn-affine mixtures | `HIGHER_ARITY_HORN_TO_AFFINE_CONSEQUENCE_DISCOVERY_OR_DECISIVE_ARITY_OBSTRUCTION` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact semantic cut signatures or certified symbolic elimination
-> proof-carrying cross-class interface compression
-> jointly selected decomposition, message language and proof rules
-> certified merge and separator extraction
-> polynomial reachable quotient construction or certified cross-language exchange
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C036.1 aligns complete fixed-order continuation refinement with reduced OBDDs. C037 crosses the Horn-affine boundary in one complete direction and adds replayable unary negotiation.

C037.1 now closes the exact constants-only obstruction:

```text
Horn x=y
plus affine x XOR y = 1
-> certified affine conflict
```

For every shared pair, general Horn entailment checks both clauses defining equality. Accepted equalities are emitted only as a union-find spanning forest, giving at most `|S|-1` proof-carrying alias rows. A binary implication-graph SCC shortcut is explicitly rejected because ternary Horn rules may be load-bearing.

A second theorem narrows the pairwise language: for satisfiable Horn formulas, every entailed `x XOR y = 1` already fixes the pair to one opposite orientation and is therefore contained in unary propagation. The genuinely new pairwise facts are equalities.

The immediate negotiation target is:

```text
HIGHER_ARITY_HORN_TO_AFFINE_CONSEQUENCE_DISCOVERY_OR_DECISIVE_ARITY_OBSTRUCTION
```

C037.1 remains `OPEN` on NAND3+NEQ reduction images without unary or equality consequences. A missing alias never authorizes compatibility or merging.

The structured decomposition route remains:

```text
C038 PROOF-CARRYING STRUCTURED DECOMPOSITION SEARCH
```

## Canonical cycle allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 explicit residual / OBDD alignment
C037   Horn-affine negotiation
C037.1 pairwise parity-alias negotiation extension
C038   structured vtree decomposition
```

## Converged constructive bottleneck

```text
C025 certified residual quotient complexity
C032 symbolic PS-signature compression
C033 portfolio selection with symbolic messages
C034 proof-carrying cross-class interface compression
C035 joint decomposition/language/proof selection
C036 cross-language symbolic separator discovery
C036.1 order/decomposition and reachable quotient construction
C037 reverse Horn-to-affine separation or stronger fact algebra
C037.1 higher-arity consequence discovery or arity obstruction
```

No future cycle may claim progress merely by renaming this object. Progress requires a new polynomial construction theorem, a strictly stronger replayable message algebra, a complete separator extractor for a larger closed language, or a decisive obstruction to one explicit construction route.

## Separation track

```text
proof-carrying circuit refuter
-> certificate-preserving SAT embedding
-> no-sharing amplification
-> SAT not in P/poly
-> P != NP
```

## Non-duplication rule

Before admission compare against:

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
symbolic bisimulation and distinguishing-test bases
active automata learning and equivalence-query teachers
cooperating decision procedures and DPLL(T)/DPLL(XOR) propagation
Horn prime implicates and closure systems
```

A renamed known parameter is registered as an alignment result, not promoted as a new theorem.
