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
| C032 | PS-width alignment | JANUS cut signatures are PS-width signatures; high treewidth may have PS-width 2 | Inventing a renamed enumerative cut parameter | `POLYNOMIAL_PS_DECOMPOSITION_OR_SYMBOLIC_SIGNATURE_COMPRESSION` |
| C033 | Tractable portfolio | Exact Horn, dual-Horn and beta-acyclic solving with witnesses and strict `OPEN` | Every tractable regime needs small explicit PS tables | `PORTFOLIO_SELECTION_WITH_SYMBOLIC_MESSAGES` |
| C034 | Affine and bounded heterogeneous composition | Replayable GF(2) certificates and exact `O(2^k poly(L))` composition for raw shared boundary `k` | Tractable modules imply unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Equal replayed messages give sound merges; affine RREF and absorbing proofs compress states | Diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Same-language partition refinement | Complete polynomial Horn and affine separator extraction | Missing separator permits merging | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C036.1 | Horn-affine unary negotiation | Complete affine-to-Horn directed inclusion plus replayable literal exchange | Propagation fixpoint certifies compatibility | `STRONGER_CROSS_LANGUAGE_FACT_ALGEBRA` |
| C036.2 | Proof-carrying OPEN vault | Exact capability-scoped reuse of replayed refusal traces | Similarity or reduction transfers `OPEN` | `SAFE_REUSE_ONLY` |
| C036.3 | Horn equality aliases | Complete pairwise Horn equality extraction compressed to a proof forest | Pairwise facts decide unrestricted Horn-affine mixtures | `HIGHER_ARITY_OR_NONENUMERATIVE_COMPOSITION` |
| C037 | Explicit residual OBDD alignment | Exact continuation quotient, distinguishing suffixes, SAT witness and UNSAT DAG after graph generation | Refinement alone avoids state explosion | `POLYNOMIAL_ORDER_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact cut communication rows and replayable separators on a supplied/discovered candidate vtree | Recursive structure automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039 | Fixed-k recursive separator compiler | One assignment-independent vtree and proof-carrying structured DAG in `n^O(k)` for fixed `k` | Graph separators characterize all tractable instances | `PORTFOLIO_GUIDED_SEMANTIC_VTREE_DISCOVERY` |
| C039.0 | Symbolic-factor operation contract | Proof-carrying `LEAF/JOIN/PROJECT/MERGE/SEPARATE` envelopes and strict `OPEN` terminals on a supplied verified vtree | A supplied vtree counts as discovery; hidden tables count as symbolic messages | `POLYNOMIAL_SYMBOLIC_JOIN_PROJECT_MERGE` |
| C039.1 | Symbolic affine factor compiler | Polynomial affine join/project/RREF messages on any charged vtree | Explicit continuation rows are unavoidable for affine cuts | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C039.2 | Single-head Horn projection | Exact proof-carrying projection without clause growth for single-head Horn; unrestricted boundary-only Horn CNF can require `2^n` clauses | Tractable Horn SAT implies compact Horn projection messages | `RICHER_HORN_MESSAGE_LANGUAGE_OR_PORTFOLIO_GUIDED_HEAD_DISJOINT_ISOLATION` |
| C039.3 | Low-affine-dimension Horn/affine composer | Exact Horn or dual-Horn plus affine composition in `O(2^d poly(L))` for projected affine dimension `d` under one fixed capability exponent | Raw shared-variable count is the only semantic interface measure; an input-dependent exponent is polynomial | `CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION` |
| C040 | Portfolio-guided semantic-vtree discovery | Frozen assignment-independent candidate manifest and one full bounded C039 probe per candidate | Adaptive post-probe vtree repair or a supplied good tree is free discovery | `POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS` |
| C041 | Joint compiler/portfolio completeness | Reserved: compiler capabilities and candidate constructors must be evaluated together under one fixed capability digest | Portfolio failure can be blamed on discovery without checking message-language closure | `UNIVERSAL_POLYNOMIAL_COMPILE_OR_EXACT_OPEN_FRONTIER` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact symbolic module messages
-> proof-carrying merge and separator extraction
-> safe cross-language facts
-> explicit OBDD / exact vtree factor alignment
-> fixed-k structured compilation
-> affine + single-head Horn + low-dimensional mixed capabilities
-> charged portfolio-guided vtree discovery
-> joint compiler/portfolio completeness
-> SAT witness + independently checkable UNSAT evidence
-> universal polynomial SAT algorithm
```

## C039 compiler ladder

```text
C039.0 supplied-vtree operation contract
C039.1 pure-affine symbolic factors
C039.2 single-head Horn symbolic projection
C039.3 low-affine-dimension Horn/dual-Horn plus affine composition
```

The compiler ladder and discovery must be assessed together. Adding a language
implementation can make a previously failing vtree compile; adding a constructor
can expose a region already supported by the current message algebra. Therefore a
C040 `OPEN_PORTFOLIO_EXHAUSTED` record is capability-scoped and becomes stale when
C039.2, C039.3 or any later compiler capability is added.

## C039.3 bridge

For a Horn or dual-Horn module `H` and affine module `A`, let:

```text
S = Vars(H) intersect Vars(A)
R = project_S(Models(A))
d = dimension(R).
```

C039.3 computes `R` by provenance-carrying Gaussian elimination and enumerates its
`2^d` basis states. Each state is checked by native Horn closure and affine
extension. For one fixed capability exponent `q`, the branch closes only when:

```text
2^d <= L^q.
```

This improves raw-boundary enumeration on large interfaces of low affine
dimension. The C023 `{NAND3,NEQ}` image keeps high projected dimension and returns
`OPEN_DIMENSION_BUDGET`.

## C040 route separation

```text
C039.x:
  symbolic factor and composition capabilities
  supplied verified vtree
  no universal discovery claim

C040:
  assignment-independent candidate generation
  complete manifest frozen before probes
  one full bounded C039 probe per candidate
  every failed probe and certificate byte charged
```

Branch, executable and wire-schema names containing `c040` in the low-affine
composer are replay aliases only. The canonical cycle of that theorem is C039.3.
C040 is reserved for semantic-vtree discovery.

## Immediate priority

```text
1. Admit and integrate C039.2 single-head Horn into the C039 operation envelope.
2. Integrate C039.3 as a certified mixed-language probe capability.
3. Re-run C040 portfolios under the enlarged capability digest.
4. Open C041 only on the resulting exact OPEN frontier.
```

Starting C041 before steps 1-3 would conflate weak compilation with weak vtree
discovery.

## Converged constructive bottleneck

```text
POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS
+
POLYNOMIAL_JOIN-CLOSED_SYMBOLIC_MESSAGE_ALGEBRA
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a stronger replayable message
algebra, a complete separator/projector for a larger closed language, or a
decisive obstruction to one explicit route.

## Non-duplication and honesty rules

Before admission compare against:

```text
PS-width and communication rows
OBDD / SDD / d-SDNNF / TDD
backdoor size and backdoor depth
treewidth / branch decompositions
Horn and dual-Horn closure
GF(2) elimination and affine subspace dimension
beta-acyclic elimination
DPLL(T) / DPLL(XOR) cooperation
existential forgetting and projection closure
intermediate knowledge-compilation size
certificate discovery, not only verification
```

Never promote:

```text
a supplied decomposition as free discovery
an input-dependent exponent as polynomial
finite tests as a universal theorem
OPEN as UNSAT or intrinsic hardness
one representation lower bound as P!=NP
semantic equivalence decided by a hidden SAT/coNP oracle
```
