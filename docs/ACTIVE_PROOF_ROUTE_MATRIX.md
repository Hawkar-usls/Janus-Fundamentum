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
| C039.0 | Symbolic-factor construction contract | Proof-carrying `LEAF/JOIN/PROJECT/MERGE/SEPARATE` envelopes, payload-policy gate and capability-locked Vault protocol | Encoded truth tables are symbolic; unsupported languages may fall back to SAT; supplied vtree is discovered | `POLYNOMIAL_SYMBOLIC_JOIN_PROJECT_MERGE_AND_REPLAYABLE_FACTOR_EQUIVALENCE` |
| C039.1 | Pure-affine symbolic vtree factors | Exact polynomial affine join/project/RREF messages on any charged vtree | Explicit continuation rows must always be materialized | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C039.2 | Single-head Horn symbolic projection | Exact restriction, guarded join, projection, merge/separate, decision and witness lifting without clause growth in the single-head subclass; unrestricted boundary-only Horn CNF can require `2^n` clauses | Tractable Horn SAT implies compact Horn projection messages | `RICHER_HORN_MESSAGE_LANGUAGE_OR_PORTFOLIO_GUIDED_HEAD_DISJOINT_ISOLATION` |
| C039.3 | Low-affine-dimension Horn/affine composer | Exact Horn or dual-Horn plus affine composition in `O(2^d poly(L))` for projected affine dimension `d` under one fixed capability exponent | Raw shared-variable count is the only semantic interface measure; an input-dependent exponent is polynomial | `CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION` |
| C040 | Portfolio-guided semantic vtree discovery contract | Sound polynomial selection from a frozen polynomial candidate portfolio using one full bounded C039 probe per candidate and deterministic certified cost selection | A supplied, branch-dependent or adaptively generated vtree substitutes for polynomial discovery; sampled probes certify success | `POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS` |
| C041 | Joint compiler/portfolio completeness | Reserved: evaluate candidate constructors only under a capability digest containing the admitted C039 implementations | `OPEN_PORTFOLIO_EXHAUSTED` can be attributed to discovery before compiler closure is exhausted | `UNIVERSAL_POLYNOMIAL_COMPILE_OR_EXACT_OPEN_FRONTIER` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> certified symbolic cut messages
-> proof-carrying JOIN and PROJECT
-> certified MERGE and SEPARATE
-> polynomial reachable quotient construction
-> affine, single-head Horn and low-dimensional mixed compiler capabilities
-> charged portfolio-guided vtree discovery
-> joint compiler/portfolio completeness
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C038 verifies recursive vtree factors but does not provide a universal polynomial
vtree constructor. C039.0 receives a supplied verified vtree and validates symbolic
factor operations. C039.1, C039.2 and C039.3 enlarge the set of supplied trees that
can produce a complete replayable `CLOSED_POLY` result.

C040 owns only the discovery boundary. Its phase order is frozen:

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

This terminal means that this exact portfolio failed under this exact compiler
capability and budget. Adding C039.2, C039.3 or another message implementation
changes the capability digest and makes the prior OPEN record stale.

C037-style equality forests, affine-support information, Horn head maps,
beta-elimination orders and exact capability-scoped OPEN traces may guide candidate
construction. They remain proof-carrying features, not decomposition proofs.

## C039 / C040 route separation

```text
C039.0:
  supplied verified vtree
  symbolic factor operation contract

C039.1:
  pure-affine symbolic factors

C039.2:
  single-head Horn symbolic projection

C039.3:
  low-affine-dimension Horn/affine composition

C040:
  assignment-independent candidate generation
  manifest frozen before probes
  one full bounded C039 probe per candidate
  discovery and every failed probe charged
```

The low-affine composer branch and validated filenames may retain a legacy `c040`
spelling for pre-admission replay. Its canonical logical cycle is `C039.3`.
`C040` is reserved for semantic-vtree discovery.

## Immediate priority

```text
1. Treat PR #55 / C039.2 as the current Horn symbolic implementation, not pending.
2. Treat PR #56 as C039.3 and integrate it into the C039 capability manifest.
3. Re-run the frozen C040 portfolio under a digest containing C039.1-C039.3.
4. Open C041 only on the resulting exact OPEN frontier.
```

Starting C041 before compiler integration would measure an artificially weak C039
probe rather than vtree-candidate completeness.

## Canonical cycle allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 Horn-affine negotiation extension
C036.2 proof-carrying Open-Core Vault
C037   explicit residual OBDD alignment
C038   structured vtree factor alignment
C039.0 symbolic-factor operation contract
C039.1 pure-affine symbolic vtree factors
C039.2 single-head Horn symbolic projection
C039.3 low-affine-dimension Horn/affine composition
C040   portfolio-guided semantic vtree discovery
C041   joint compiler/portfolio completeness
```

## Converged constructive bottleneck

```text
POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS
+
POLYNOMIAL_JOIN-CLOSED_SYMBOLIC_MESSAGE_ALGEBRA
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

C040 proves only the safe-selection meta-theorem. The missing theorem is that a
polynomially generated candidate family, together with the admitted compiler
capability, always contains a vtree with a polynomial complete compilation, or a
stronger charged assignment-independent discovery mechanism.

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a stronger replayable message
algebra, a complete separator extractor for a larger closed language, or a
decisive obstruction to one explicit route.

## Non-duplication and honesty rules

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
