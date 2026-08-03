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
| C034 | Affine and bounded heterogeneous composition | Replayable GF(2) certificates and exact `O(2^k poly(L))` composition | Tractable modules imply unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Equal replayed messages give sound merges | Diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Same-language partition refinement | Complete polynomial Horn and affine separator extraction | Missing separator permits merging | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C036.1 | Horn-affine unary negotiation | Complete affine-to-Horn directed inclusion plus replayable literal exchange | Propagation fixpoint certifies compatibility | `STRONGER_CROSS_LANGUAGE_FACT_ALGEBRA` |
| C036.2 | Proof-carrying OPEN vault | Exact capability-scoped reuse of replayed refusal traces | Similarity or reduction transfers `OPEN` | `SAFE_REUSE_ONLY` |
| C036.3 | Horn equality aliases | Complete pairwise Horn equality extraction compressed to a proof forest | Pairwise facts decide unrestricted Horn-affine mixtures | `HIGHER_ARITY_OR_NONENUMERATIVE_COMPOSITION` |
| C037 | Explicit residual OBDD alignment | Exact continuation quotient after graph generation | Refinement alone avoids state explosion | `POLYNOMIAL_ORDER_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact cut communication rows and replayable separators | Recursive structure automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039 | Fixed-k recursive separator compiler | One assignment-independent vtree and proof-carrying DAG in `n^O(k)` | Graph separators characterize all tractable instances | `PORTFOLIO_GUIDED_SEMANTIC_VTREE_DISCOVERY` |
| C039.1 | Symbolic affine factor compiler | Polynomial affine join/project/RREF messages | Explicit continuation rows are unavoidable for affine cuts | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C039.2 | Low-affine-dimension Horn composer | Exact Horn/dual-Horn plus affine composition in `O(2^d poly(L))` | Raw shared-variable count is the only safe parameter | `CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION` |
| C041 | Affine-coordinate 3-SAT identity | C023 followed by canonical affine coordinates reproduces the source 3-CNF syntactically and preserves supports | Coordinate substitution alone simplifies the hard image | `POLYNOMIAL_DISCOVERY_OF_TRACTABLE_COORDINATE_FACTOR_STRUCTURE_OR_STRICT_OPEN` |
| C042 | Laminar affine forbidden-subspace cover | Polynomial recognition, exact union counting, SAT witness recovery and UNSAT disjoint-cover certificates for laminar clause-falsifying affine subspaces | High affine dimension alone forces enumeration; coordinate factors cannot be solved without extra structure | `POLYNOMIAL_DECOMPOSITION_OF_CROSSING_AFFINE_FORBIDDEN_SUBSPACES` |
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
-> affine-coordinate clause predicates
-> certified tractable affine-subspace arrangement structure
-> broader join-closed symbolic projection
-> SAT witness + independently checkable UNSAT evidence
-> universal polynomial SAT algorithm
```

## C041 coordinate identity obstruction

Under the C023 `{NAND3,NEQ}` embedding, use the canonical affine coordinates

```text
x_i = lambda_i
c_i = 1 XOR lambda_i.
```

Every negative Horn literal over a falsity indicator translates back to the original source literal. Hence each Horn NAND3 clause becomes exactly its source 3-CNF clause, preserving polarity, support, primal adjacency and satisfiability. Affine-coordinate substitution is therefore only a change of notation on the hard image.

A valid coordinate selector must additionally discover a replayable tractable property of the coordinate factors or return `OPEN` within a fixed polynomial budget.

## C042 laminar arrangement theorem

For `x = p + B lambda`, falsifying one CNF clause imposes an affine system on `lambda`; denote its solution set by `U_C`. C042 recognizes the condition that every two nonempty `U_C` are disjoint or nested.

After removing duplicates and contained factors, the maximal forbidden subspaces are pairwise disjoint. Their exact union cardinality is therefore the sum of `2^dimension`. Equality with `2^d` gives an independently replayable UNSAT cover. Otherwise deterministic conditional counting fixes one coordinate at a time and produces a point outside the union, hence a SAT witness, without enumerating `2^d` assignments.

The C023 hard image contains crossing forbidden subspaces and returns `OPEN_NON_LAMINAR`. The next route must decompose or symbolically cover crossing arrangements with polynomial discovery and proof volume.

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
C039.2  low-affine-dimension Horn/dual-Horn composer
C040    portfolio-guided semantic-vtree discovery (reserved)
C041    affine-coordinate 3-SAT identity obstruction
C042    laminar affine forbidden-subspace cover
```

## Converged constructive bottleneck

```text
Construct, in polynomial total work, a decomposition and join-closed proof-carrying message algebra whose semantic state volume is polynomial on every CNF, with SAT witness recovery and independently checkable UNSAT evidence.
```

C041 proves that affine coordinates alone cannot satisfy this obligation. C042 supplies a real polynomial coordinate class, but rejects crossing subspace arrangements, including the deterministic hard-image pressure fixture.

## Non-duplication and honesty rules

Compare every candidate against PS-width, OBDD/SDD/d-SDNNF/TDD, backdoors, treewidth, Horn/dual-Horn closure, GF(2) elimination, beta-acyclic elimination, DPLL(T)/DPLL(XOR), existential forgetting, finite-field subspace arrangements, intermediate compilation size, and certificate discovery.

Never promote a supplied decomposition as free discovery, an input-dependent exponent as polynomial, finite tests as a theorem, `OPEN` as hardness, one representation lower bound as `P!=NP`, or semantic equivalence decided by a hidden SAT/coNP oracle.
