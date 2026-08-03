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
| C042 | Proof-carrying laminar affine cover | Charged basis discovery, semantic certificate replay, exact union counting and witness/certificate recovery under `64(L+1)^6` | A supplied basis, digest-only verification, or small final output makes construction free | `POLYNOMIAL_DECOMPOSITION_OF_CROSSING_AFFINE_FORBIDDEN_SUBSPACES` |
| C043 | Global bounded live signed support | Signed recurrence prototype solves genuine crossings when `K=max_t|supp(c_t)|` stays polynomial | Number of crossing pairs, final support only, codimension, or producer replay alone certifies tractability | `COMPLETE_PROOF_CARRYING_GLOBAL_SIGNED_SUPPORT_COMPILER` |
| C044 | Local signed-support vtree composition (reserved) | No admitted theorem yet | A globally large support is harmless merely because local pieces look small | `LOCAL_SIGNED_SUPPORT_VTREE_COMPOSITION_OR_STRICT_OPEN` |
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
-> proof-carrying laminar affine covers
-> global bounded live signed support
-> local signed-support vtree composition
-> broader decomposed symbolic projection
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

## C042 proof-carrying laminar theorem

Given a CNF together with an affine system, C042 constructs `x=p+B lambda` by provenance-carrying Gaussian elimination. Falsifying one clause defines an affine subspace `U_C` of the coordinate space. C042 discovers whether every pair of nonempty `U_C` is disjoint or nested.

After duplicate and contained factors are removed, the maximal forbidden subspaces are pairwise disjoint. Their exact union cardinality is the sum of `2^dimension`. Equality with `2^d` gives an independently replayable UNSAT cover. Otherwise deterministic conditional counting fixes one coordinate at a time and produces a point outside the union, then lifts it to a complete witness.

The v2 proof package closes the C042 obligations for independent semantic replay, paid basis construction, one fixed polynomial budget, SUB-SAT literature alignment and high-dimensional pressure controls.

## C043 global signed-support contract

Process the forbidden subspaces in a deterministic order and maintain

```text
1_(union_{i <= t} U_i) = sum_S c_t(S) 1_S.
```

The primary parameter is

```text
K = max_t |supp(c_t)|,
```

where only canonical intersections with nonzero coefficients remain. It is not the number of crossing pairs and not merely the final support size.

Adding `U_t` must replay

```text
c_t = c_(t-1) + e_(U_t) - T_(U_t)c_(t-1),
T_U(S) = S intersect U.
```

Canonical RREF merges equal intersections and zero coefficients cancel. Algebraic induction over these transitions proves the union-indicator identity on every coordinate assignment without enumerating `2^d` points.

For one fixed exponent `q`, the support capability is

```text
K <= min(absolute_support_cap, L^q).
```

Construction, coefficient-bit arithmetic, exact counting, witness recovery, proof volume and independent verification must fit `O(m K poly(d,L))` and their fixed polynomial ledgers. Exceeding live support returns `OPEN_INTERSECTION_CLOSURE`; work or proof-volume overflow returns its own exact OPEN terminal.

The existing prototype establishes the signed recurrence and genuine crossing controls, but full C043 admission still requires:

```text
C042 basis integration instead of a free coordinate map
separate janus_c043_crossing_verifier.py
independent transition/coefficient/count replay instead of calling the producer
fixed producer and verifier capability manifests
```

## C044 reserved local decomposition route

C043 is deliberately global. It does not absorb local vtree decomposition into the same theorem.

C044 may discover a vtree or factor decomposition whose local signed supports and separator messages remain polynomial even when the global C043 support is large. It must charge:

```text
vtree discovery
factor placement
maximum local live support
separator representation
join and projection
canonicalization
intermediate products
SAT witness lifting
UNSAT proof volume
verifier work
```

Any oversized local factor, separator message or join returns

```text
OPEN_LOCAL_SUPPORT.
```

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
C042    proof-carrying laminar affine forbidden-subspace cover
C043    global bounded-live-signed-support compiler
C044    local signed-support vtree composition (reserved)
```

## Converged constructive bottleneck

```text
Construct, in polynomial total work, a decomposition and join-closed proof-carrying message algebra whose semantic state volume is polynomial on every CNF, with SAT witness recovery and independently checkable UNSAT evidence.
```

C041 proves that coordinates alone do not compress. C042 closes a laminar class. C043 targets globally bounded live signed support. C044 is reserved for discovering and composing polynomial local supports when global support is too large.

## Non-duplication and honesty rules

Compare every candidate against C023 NAND3+NEQ, C034 unrestricted Horn-affine NP-hardness, CNF satisfiability in an affine subspace, polynomial systems over `GF(2)`, PS-width, OBDD/SDD/d-SDNNF/TDD, backdoors, treewidth, Horn/dual-Horn closure, beta-acyclic elimination, DPLL(T)/DPLL(XOR), existential forgetting, finite-field subspace arrangements, characteristic-polynomial/intersection-poset methods, intermediate compilation size, certificate discovery and verifier work.

Never promote a supplied decomposition or affine basis as free discovery, an input-dependent exponent as polynomial, finite tests as a theorem, `OPEN` as hardness, final compactness as proof of cheap intermediate construction, or semantic equivalence decided by a hidden SAT/coNP oracle.
