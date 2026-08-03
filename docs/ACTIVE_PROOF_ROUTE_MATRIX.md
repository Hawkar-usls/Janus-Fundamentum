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
| C039.1 | Symbolic affine factor compiler | Polynomial affine join/project/RREF messages on any charged vtree | Explicit continuation rows are unavoidable for affine cuts | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C040 | Low-affine-dimension Horn composer | Exact Horn/dual-Horn plus affine composition in `O(2^d poly(L))`, where `d` is projected affine interface dimension | Raw shared-variable count is the only safe composition parameter; unary/pairwise facts are complete | `CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact symbolic module messages
-> proof-carrying merge and separator extraction
-> safe cross-language facts
-> explicit OBDD / exact vtree factor alignment
-> fixed-k structured compilation
-> pure-affine symbolic factor compilation
-> semantic-dimension cross-language composition
-> broader join-closed symbolic projection
-> SAT witness + independently checkable UNSAT evidence
-> universal polynomial SAT algorithm
```

## C040 bridge

For a Horn or dual-Horn module `H` and affine module `A`, let:

```text
S = Vars(H) intersect Vars(A)
R = project_S(Models(A))
d = dimension(R).
```

C040 computes `R` by provenance-carrying Gaussian elimination and enumerates its `2^d` basis states. Each state is checked by native Horn closure and affine extension. For a fixed capability exponent `q`, the branch closes only when:

```text
2^d <= L^q.
```

This strictly improves C034 on large raw interfaces with low affine dimension. An 80-variable dense dual-Horn clique-primal instance joined to one equality class has `d=1` and is solved with at most two semantic states.

The C023 `{NAND3,NEQ}` image has projected affine dimension equal to the number of source variables and returns `OPEN_DIMENSION_BUDGET`.

A separate Horn/affine obstruction has no unary or pairwise Horn restrictions but is UNSAT over a one-dimensional affine line. Therefore C036.1/C036.3 fact exchange is useful but not complete; complete semantic states can be stronger than bounded-arity facts.

## Canonical cycle allocation

```text
C036    same-language refinement
C036.1  Horn-affine unary negotiation
C036.2  exact OPEN vault
C036.3  Horn parity/equality aliases
C037    explicit residual OBDD alignment
C038    exact structured-vtree factor alignment
C039    fixed-k recursive separator compiler
C039.1  pure-affine symbolic vtree factor compiler
C040    low-affine-dimension Horn/dual-Horn composer
```

Legacy branch and file paths may retain older identifiers solely for pre-admission replayability. PR titles, this route matrix, and new machine-readable artifacts define the canonical allocation.

## Converged constructive bottleneck

The surviving universal obligation is:

```text
construct, in polynomial total work, a decomposition and a join-closed proof-carrying message algebra whose semantic state volume is polynomial on every CNF, with SAT witness recovery and independently checkable UNSAT evidence.
```

C040 closes one real cross-language region, but only when the affine interface has polynomially enumerable dimension under one fixed capability. The next advance must cover high-dimensional interfaces without hiding exhaustive search, or prove a stronger symbolic projection theorem for a larger language.

## Non-duplication and honesty rules

Before admitting a new hypothesis compare against:

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
