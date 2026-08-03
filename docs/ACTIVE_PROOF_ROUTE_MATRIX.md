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
| C032 | PS-width alignment | JANUS cut signatures are PS-width signatures; high treewidth may have PS-width 2 | Inventing a renamed enumerative cut parameter | `POLYNOMIAL_PS_DECOMPOSITION_OR_SYMBOLIC_SIGNATURE_COMPRESSION` |
| C033 | Tractable portfolio | Exact Horn, dual-Horn and beta-acyclic solving with witnesses and strict `OPEN` | Every tractable regime needs small explicit PS tables | `PORTFOLIO_SELECTION_WITH_SYMBOLIC_MESSAGES` |
| C034 | Affine and bounded heterogeneous composition | Replayable GF(2) certificates and exact bounded-interface composition | Tractable modules imply unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Equal replayed messages give sound merges; affine RREF and absorbing proofs compress states | Diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Same-language partition refinement | Complete polynomial Horn and affine separator extraction | Missing separator permits merging | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C037 | Explicit residual OBDD alignment | Exact continuation quotient after explicit state generation | Refinement alone avoids state explosion | `POLYNOMIAL_ORDER_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact cut communication rows and replayable separators on a verified vtree | Recursive structure automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039.0 | Symbolic-factor operation contract | Proof-carrying `LEAF/JOIN/PROJECT/MERGE/SEPARATE` envelopes on a supplied verified vtree | Hidden tables are symbolic; supplied vtree counts as discovery | `POLYNOMIAL_SYMBOLIC_JOIN_PROJECT_MERGE` |
| C039.1 | Pure-affine symbolic vtree factors | Polynomial affine join/project/RREF messages on any charged vtree | Explicit continuation rows are unavoidable for affine cuts | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C039.2 | Single-head Horn projection | Polynomial proof-carrying restriction, guarded join, projection, merge/separate and witness lifting; exact `2^n` obstruction for unrestricted boundary-only Horn CNF | Horn satisfiability or Horn expressibility implies compact projection | `RICHER_HORN_MESSAGE_LANGUAGE_OR_PORTFOLIO_GUIDED_HEAD_DISJOINT_ISOLATION` |
| C039.3 | Low-affine-dimension Horn/affine composer | Exact Horn or dual-Horn plus affine composition in `O(2^d poly(L))` under one fixed capability exponent | Input-dependent exponent is polynomial; raw boundary size is the only interface measure | `CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION` |
| C040 | Portfolio-guided semantic-vtree discovery | Frozen assignment-independent candidate manifest and one full bounded C039 probe per candidate | Adaptive repair or a supplied good vtree is free discovery | `POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS` |
| C041 | Joint compiler/portfolio completeness | Reserved: evaluate candidate constructors under the full fixed C039 capability digest | Portfolio failure can be blamed on discovery before compiler closure is exhausted | `UNIVERSAL_POLYNOMIAL_COMPILE_OR_EXACT_OPEN_FRONTIER` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## C039 compiler ladder

```text
C039.0  supplied-vtree operation contract
C039.1  pure-affine symbolic factors
C039.2  single-head Horn symbolic projection
C039.3  low-affine-dimension Horn/dual-Horn plus affine composition
```

C039.2 is the canonical identity of this branch. Existing `c039_1` branch,
filename, executable and wire-schema spellings are deterministic replay aliases.

## C039.2 theorem and obstruction

For single-head Horn, each eliminated variable has at most one producer. Exact
Horn resolution therefore generates at most one replacement per consumer, clause
count does not increase, the single-head invariant is preserved, and witnesses
lift in reverse elimination order.

For unrestricted boundary-only Horn CNF, the linear family

```text
a_i -> q_i
b_i -> q_i
(q_1 AND ... AND q_n) -> z
```

requires exactly `2^n` Horn clauses after forgetting all `q_i`. This blocks plain
boundary Horn CNF as a universal symbolic language, not richer Horn circuits,
existential modules, other decompositions, or all SAT algorithms.

## Immediate priority

```text
1. Integrate C039.2 into the C039 operation envelope.
2. Integrate sibling PR #56 as C039.3 mixed-language capability.
3. Re-run C040 frozen portfolios under the enlarged capability digest.
4. Open C041 only on the resulting exact OPEN frontier.
```

A C040 `OPEN_PORTFOLIO_EXHAUSTED` result obtained before C039.2/C039.3 integration
is stale evidence about an earlier compiler, not evidence against the vtree
portfolio.

## Canonical cycle allocation

```text
C039.0 symbolic-factor operation contract
C039.1 pure-affine symbolic vtree factors
C039.2 single-head Horn symbolic projection
C039.3 low-affine-dimension Horn/affine composition
C040   portfolio-guided semantic-vtree discovery
C041   joint compiler/portfolio completeness
```

## Converged bottleneck

```text
POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS
+
POLYNOMIAL_JOIN-CLOSED_SYMBOLIC_MESSAGE_ALGEBRA
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

No representation-specific blow-up, finite audit, or `OPEN_*` terminal is promoted
to a general hardness or P versus NP conclusion.
