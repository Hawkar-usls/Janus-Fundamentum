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
| C034 | Affine and cross-class composition | Replayable GF(2) certificates and exact bounded-interface heterogeneous composition | Named tractable modules imply an unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Replayed exact residual messages give a sound merge congruence; absorbing proofs and affine RREF compress | Exponential diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Proof-carrying partition refinement | Complete polynomial separator extraction for Horn and affine residuals | Failure to find a separator permits merging | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C036.1 | Horn-affine negotiation extension | Complete affine-to-Horn directed inclusion and replayable shared-literal conflict traces | A propagation fixpoint certifies compatibility | `REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA` |
| C036.2 | Proof-Carrying Open-Core Vault | Exact capability-scoped OPEN storage, logical STALE, immutable evaluations and fail-closed replay | Cached OPEN is intrinsic hardness; capability changes permit silent reuse | `CI_ADMISSION_AND_PROTOCOL_INTEGRATION` |
| C037 | Explicit residual OBDD alignment | Exact minimization and certificates after explicit fixed-order state generation | Partition refinement alone avoids state explosion | `POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact cut continuation rows and replayable factor separators for a verified vtree | Recursive structure or a supplied vtree automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039 | Symbolic factor construction contract | Proof-carrying `LEAF/JOIN/PROJECT/MERGE/SEPARATE` envelopes, payload-policy gate and capability-locked Vault protocol | Encoded truth tables are symbolic; unsupported languages may fall back to SAT; supplied vtree is discovered | `POLYNOMIAL_SYMBOLIC_JOIN_PROJECT_MERGE_AND_REPLAYABLE_FACTOR_EQUIVALENCE` |
| C039.2 | Low-affine-dimension Horn/affine composer | Exact Horn or dual-Horn plus affine composition in `O(2^d poly(L))` for projected affine dimension `d` under one fixed capability exponent | Raw shared-variable count is the only semantic interface measure; an input-dependent exponent is polynomial | `CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION` |
| C040 | Portfolio-guided semantic vtree discovery contract | Sound polynomial selection from a frozen polynomial candidate portfolio using one full bounded C039 probe per candidate and deterministic certified cost selection | A supplied, branch-dependent or adaptively generated vtree substitutes for polynomial discovery; sampled probes certify success | `POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> certified symbolic cut messages
-> proof-carrying JOIN and PROJECT
-> certified MERGE and SEPARATE
-> polynomial reachable quotient construction
-> charged portfolio-guided vtree discovery
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C038 verifies recursive vtree factors but does not provide a universal polynomial
vtree constructor. C039 receives a supplied, verified vtree and validates symbolic
factor operations. C039.2 extends the symbolic-composition side for low projected
affine dimension; it does not discover a vtree.

C040 owns the discovery boundary. Its phase order is frozen:

```text
canonical formula and capability
-> proof-carrying feature extraction
-> generate the complete candidate list
-> freeze and hash the candidate manifest
-> run exactly one bounded full C039 probe per candidate
-> select by deterministic certified cost tuple
```

Only a full C039 `CLOSED_POLY` certificate makes a candidate selectable. Among
successful candidates the selector minimizes:

```text
(max_node_representation,
 total_representation,
 total_work_units,
 vtree_digest)
```

If every frozen candidate returns `OPEN_*`, C040 returns only:

```text
OPEN_PORTFOLIO_EXHAUSTED
```

This terminal means that this exact portfolio failed under this exact capability
and budget. It is not hardness, incompatibility or evidence that another vtree
does not work.

C037-style equality forests, affine-support information, Horn head maps,
beta-elimination orders and exact capability-scoped OPEN traces may guide candidate
construction. They remain proof-carrying features, not decomposition proofs.

## C039 / C040 route separation

```text
C039:
  supplied verified vtree
  symbolic factor construction
  certified merge/separate

C039.2:
  low-affine-dimension Horn/affine composition
  no vtree discovery claim

C040:
  assignment-independent candidate generation
  manifest frozen before probes
  discovery and all failed probes charged
  no supplied-vtree substitution
```

The branch and validated file names of the low-affine composer may retain a legacy
`c040` spelling for pre-admission replay. Its canonical logical cycle is `C039.2`;
`C040` is reserved for semantic-vtree discovery.

## Canonical cycle allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 Horn-affine negotiation extension
C036.2 proof-carrying Open-Core Vault
C037   explicit residual OBDD alignment
C038   structured vtree factor alignment
C039   symbolic factor construction without truth-table enumeration
C039.2 low-affine-dimension Horn/affine composition
C040   portfolio-guided semantic vtree discovery
```

## Converged constructive bottleneck

```text
POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS
+
POLYNOMIAL_SYMBOLIC_FACTOR_CONSTRUCTION
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

C040 proves only the safe-selection meta-theorem: a fixed polynomial portfolio
with polynomially bounded C039 probes can be searched soundly in polynomial total
work. The missing theorem is that a polynomially generated candidate family always
contains a vtree with a polynomial complete compilation, or a stronger charged
assignment-independent discovery mechanism.

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

This remains an adversarial control. No empirical failure of the constructive
track is a separation proof.

## Non-duplication and honesty rules

Before admission, compare against:

```text
PS-width
MIM-width / incidence width
DNNF / d-DNNF / OBDD / SDD / TDD
factor width and vtree communication rows
backdoor size and backdoor depth
residual-state width
proof width and certificate discovery
beta-acyclic and Davis-Putnam elimination
Horn and dual-Horn closure
GF(2) affine elimination and projected affine dimension
Schaefer fixed-language mixtures
communication/continuation equivalence across cuts
partition refinement and canonical residual automata
active learning and equivalence-query teachers
cooperating decision procedures and DPLL(T)/DPLL(XOR)
knowledge-compilation intermediate blow-up
```

Never promote:

```text
a supplied decomposition as free discovery
an input-dependent exponent as polynomial
a branch-dependent vtree as one global decomposition
partial, sampled or estimated probes as CLOSED_POLY
finite fixtures as universal candidate completeness
OPEN as UNSAT or intrinsic hardness
similarity, reduction or shared features as OPEN transfer
one representation lower bound as P!=NP
```

A renamed known parameter is an alignment result, not a new theorem.
