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
| C043 | Bounded live signed affine-intersection support | C042 basis inheritance, separate semantic verifier, exact signed recurrence, maximum live-support and coefficient-volume accounting | Compact final support excuses exponential intermediate closure; verifier may call producer | `POLYNOMIAL_LOCALIZATION_OF_SUPERPOLYNOMIAL_GLOBAL_INTERSECTION_SUPPORT` |
| C044 | Local signed-cover vtree composition | Deterministic coordinate-primal separator discovery, local signed-cover leaves, exact branch composition and independent terminal reconstruction in `L^O(k)` for fixed `k` | Global signed-support `OPEN` implies every localization is exponential; a supplied decomposition may be treated as free | `JOINT_AFFINE_BASIS_DECOMPOSITION_AND_MESSAGE_DISCOVERY` |
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
-> proof-carrying laminar affine arrangements
-> proof-carrying bounded live signed support
-> proof-carrying local signed-support vtree composition
-> joint affine-basis / decomposition / message discovery
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

## C042 proof-carrying laminar theorem

Given a CNF together with an affine system, C042 constructs `x=p+B lambda` by provenance-carrying Gaussian elimination. Falsifying one clause defines an affine subspace `U_C` of the coordinate space. C042 discovers whether every pair of nonempty `U_C` is disjoint or nested.

After duplicate and contained factors are removed, the maximal forbidden subspaces are pairwise disjoint. Their exact union cardinality is the sum of `2^dimension`. Equality with `2^d` gives an independently replayable UNSAT cover. Otherwise deterministic conditional counting produces a point outside the union and lifts it to a complete witness.

## C043 bounded-live-signed-support theorem

C043 inherits the complete C042 affine basis artifact. It no longer accepts a free coordinate table.

For deterministic forbidden-factor order, maintain

```text
1_(union_{i <= t} U_i) = sum_S c_t(S) 1_S
c_t = c_(t-1) + e_(U_t) - T_(U_t)c_(t-1)
T_U(S) = S intersect U.
```

The controlling parameter is

```text
K = max_t |supp(c_t)|.
```

Every transition records canonical intersections, signed deltas, coefficient merges, zero cancellation, outgoing terms, live support, temporary working support and coefficient bit volume. The separate verifier does not import or call the producer; it independently checks the C042 basis, clause translation, factor order, every transition, signed counts, SAT witness or UNSAT cover.

The implementation fixes polynomial support, work, coefficient and certificate envelopes. A 32-term intermediate family that later collapses to one final term is rejected immediately under a support cap of 8. C023/C041 controls at dimensions 18, 24 and 30 return `OPEN_INTERSECTION_CLOSURE`.

Current status:

```text
C043 = ARCHITECTURE_CONTRACT_ADMITTED
       / FULL_IMPLEMENTATION_CANDIDATE
```

Final admission requires exact-head CI and review of refusal-terminal capability replay. It is not automatic.

## C044 local signed-support theorem

C044 begins from a genuine C043 `OPEN_INTERSECTION_CLOSURE`.

For each coordinate region it first attempts a complete local signed-support compilation. If that overflows, C044 deterministically searches the coordinate primal graph for the first disconnected split or balanced separator of size at most the fixed capability `k`. The complete recursive plan is fixed before any separator values are chosen.

Accepted leaves store exact signed affine-subspace covers and charge both live and pre-cancellation working support. Separator nodes enumerate only `2^|S|` assignments, check separator-local forbidden factors, and combine independent child witnesses or child refutations.

For fixed `k`, bounded local support `K`, and balanced components:

```text
T(n) <= 2^k sum_i T(n_i) + poly(L,K,n^k)
max_i n_i <= 2n/3
```

so total discovery, solving, witness recovery, certificate construction and independent verification are `L^O(k)`.

Strict extension controls:

```text
40 independent units:
  global C043 -> OPEN_INTERSECTION_CLOSURE
  C044        -> SAT with separator size 0

40-variable path:
  global C043 -> OPEN_INTERSECTION_CLOSURE
  C044        -> SAT with separator size 1
```

The dense registered hard-image pressure family still returns:

```text
OPEN_LOCAL_SUPPORT
reason = NO_ADMITTED_SEPARATOR
```

This is a capability-scoped refusal, not a hardness theorem.

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
C040    portfolio-guided semantic-vtree discovery
C041    affine-coordinate 3-SAT identity obstruction
C042    proof-carrying laminar affine forbidden-subspace cover
C043    bounded live signed affine-intersection support
C044    local signed-support vtree composition
```

## Converged constructive bottleneck

```text
Construct, in polynomial total work, an affine basis, decomposition and join-closed proof-carrying message algebra whose semantic state volume is polynomial on every CNF, with SAT witness recovery and independently checkable UNSAT evidence.
```

C041 proves that affine coordinates alone cannot satisfy this obligation. C042 supplies a genuine laminar polynomial class. C043 extends it to globally bounded live signed support while charging intermediate closure. C044 proves that some superpolynomial global supports can be localized by a deterministically discovered fixed-separator decomposition. The surviving question is whether basis choice, semantic decomposition and message language can be discovered jointly in polynomial total work on every input.

## Non-duplication and honesty rules

Compare every candidate against C023 NAND3+NEQ, C034 unrestricted Horn-affine NP-hardness, CNF satisfiability in an affine subspace, finite-field intersection-poset methods, PS-width, OBDD/SDD/d-SDNNF/TDD, backdoors, treewidth, DPLL(T)/DPLL(XOR), existential forgetting, intermediate compilation size, certificate discovery and verifier work.

Never promote a supplied decomposition or affine basis as free discovery, an input-dependent exponent as polynomial, compact final output as proof of compact construction, finite tests as a theorem, `OPEN` as hardness, or semantic equivalence decided by a hidden SAT/coNP oracle.
