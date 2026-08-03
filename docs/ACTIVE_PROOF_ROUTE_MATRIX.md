# JANUS Active Proof Route Matrix

**Purpose:** compare every new mechanism against the existing proof graph before
creating another hypothesis.

```text
P_VS_NP=OPEN
```

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C023 | Boolean polymorphism admission | Exact Schaefer dispatch and fixed `{NAND3,NEQ}` obstruction | Separate tractable languages imply tractable mixture | Instance-specific decomposition with charged interfaces |
| C024 | Fracture channel core | Coarse region graph may be a star while exact elimination recovers arbitrary 3-CNF | Low coarse fracture treewidth captures hardness | `NONLINEAR_QUOTIENT_CORE` |
| C025 | Certified residual quotient | Separates state volume from merge-proof volume | Free semantic equality merging | `CERTIFIED_RESIDUAL_QUOTIENT_COMPLEXITY` |
| C027 | Context projection discovery | OR/XOR projections are exact but representation-sensitive | Compact circuit implies tractable projection | `TRACTABLE_PROJECTION_DISCOVERY` |
| C028 | Mixed-cone invariants | Decomposable NNF is tractable; overlap variables form a backdoor | Determinism or gate-tree topology implies tractability | `SEMANTIC_SUPPORT_OVERLAP` |
| C029 | Occurrence-splitting minor | Connected equality splitting preserves source incidence graph as a minor | Variable copying plus equality lowers incidence width | `NON_MINOR_PRESERVING_SEMANTIC_COMPRESSION` |
| C032 | PS-width alignment | JANUS cut signatures are PS-width signatures | Renamed enumerative cut parameter | `POLYNOMIAL_PS_DECOMPOSITION_OR_SYMBOLIC_SIGNATURE_COMPRESSION` |
| C033 | Tractable portfolio | Exact Horn, dual-Horn and beta-acyclic solving with witnesses and strict `OPEN` | Every tractable regime needs small explicit PS tables | `PORTFOLIO_SELECTION_WITH_SYMBOLIC_MESSAGES` |
| C034 | Affine and bounded heterogeneous composition | Replayable GF(2) certificates and `O(2^k poly(L))` composition for raw boundary `k` | Tractable modules imply unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Equal replayed messages give sound merges; RREF and absorbing proofs compress states | Diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Same-language partition refinement | Complete polynomial Horn and affine separator extraction | Missing separator permits merging | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C036.1 | Horn-affine unary negotiation | Complete affine-to-Horn inclusion and replayable literal exchange | Propagation fixpoint certifies compatibility | `STRONGER_CROSS_LANGUAGE_FACT_ALGEBRA` |
| C036.2 | Proof-carrying OPEN vault | Exact capability-scoped reuse of replayed refusal traces | Similarity or reduction transfers `OPEN` | `SAFE_REUSE_ONLY` |
| C036.3 | Horn equality aliases | Complete pairwise Horn equality extraction compressed to a proof forest | Pairwise facts decide unrestricted mixtures | `COMPLETE_HORN_AFFINE_HULL` |
| C036.4 | Complete Horn affine hull | All unconditional Horn affine consequences are unary facts and equalities; reverse directed inclusion is complete | Another XOR arity exposes the remaining NAND3+NEQ conflict | `CONDITIONAL_MULTIROW_INTERACTION` |
| C037 | Explicit residual OBDD alignment | Exact continuation quotient and proof objects after explicit residual generation | Refinement alone avoids state explosion | `POLYNOMIAL_ORDER_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact cut communication rows and replayable separators | Recursive structure automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039 | Fixed-k recursive separator compiler | One assignment-independent vtree and structured proof DAG in `n^O(k)` for fixed `k` | Graph separators characterize all tractable instances | `PORTFOLIO_GUIDED_SEMANTIC_VTREE_DISCOVERY` |
| C039.0 | Symbolic-factor contract | Digest-bound `LEAF/JOIN/PROJECT/MERGE/SEPARATE`, budgets and strict `OPEN` terminals | Enumerative payloads may masquerade as symbolic factors | Implement closed message languages |
| C039.1 | Pure-affine symbolic factors | Polynomial affine join/project/RREF messages on a charged vtree | Explicit continuation rows are unavoidable for affine cuts | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C039.2 | Single-head Horn projection | Polynomial proof-carrying projection for single-head Horn; exact exponential boundary-CNF obstruction for general Horn | Horn SAT implies compact Horn boundary messages | `RICHER_HORN_MESSAGES_OR_HEAD_DISJOINT_ISOLATION` |
| C040 | Low-affine-dimension composer | Horn/dual-Horn plus affine in `O(2^d poly(L))`, where `d` is projected affine dimension | Raw shared-variable count is the only semantic composition parameter | `AFFINE_COORDINATE_CLAUSE_FACTORING_BEYOND_STATE_ENUMERATION` |
| C041 | Laminar affine-subspace avoidance | Polynomial exact SUB-SAT for laminar clause-falsifying affine subspaces, with SAT witness and UNSAT cover certificate | High affine dimension always forces state enumeration | `NON_LAMINAR_AFFINE_SUBSPACE_UNION_COMPRESSION` |
| C042 | Bounded signed-intersection support | Exact signed inclusion-exclusion over canonical affine intersections with fixed-polynomial support, budget-bound replay, SAT witness and UNSAT cover | Non-laminar crossings necessarily require point enumeration or the full powerset of factors | `POLYNOMIAL_DECOMPOSITION_BEYOND_BOUNDED_SIGNED_INTERSECTION_SUPPORT` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact symbolic module messages
-> proof-carrying merge and separator extraction
-> safe cross-language facts
-> explicit OBDD / exact vtree factor alignment
-> fixed-k structured compilation
-> pure-affine and guarded Horn projection
-> semantic-dimension cross-language composition
-> affine-coordinate union-of-subspaces compression
-> bounded signed-intersection cover compression
-> broader join-closed symbolic cover language
-> SAT witness + independently checkable UNSAT evidence
-> universal polynomial SAT algorithm
```

## C040 bridge

For a Horn or dual-Horn module `H` and affine module `A`:

```text
S = Vars(H) intersect Vars(A)
R = project_S(Models(A))
d = dimension(R).
```

C040 enumerates the `2^d` true affine interface states, not all `2^|S|`
assignments. This solves large raw interfaces of low affine dimension but
returns `OPEN_DIMENSION_BUDGET` on the general `{NAND3,NEQ}` image.

## C041 bridge

Parameterize all affine solutions as:

```text
x = p + B lambda.
```

For each CNF clause `C`, define the affine subspace:

```text
U_C = {lambda : C is false}.
```

Then:

```text
F AND A is SAT iff lambda lies outside UNION_C U_C.
```

C041 closes this problem when the nonempty `U_C` form a laminar family:
each pair is disjoint or one contains the other. Removing contained spaces
leaves pairwise-disjoint maxima, so exact cover volume is the sum of their
powers-of-two cardinalities. SAT witnesses are recovered by greedy coordinate
fixing with exact intersection counts.

The `{NAND3,NEQ}` control contains overlapping incomparable forbidden
subspaces and returns `OPEN_NON_LAMINAR`.

## C042 bridge

C042 processes the forbidden affine subspaces in deterministic clause order and
maintains the exact indicator identity:

```text
1_(UNION processed U) = SUM_S c_S 1_S.
```

A new factor is incorporated by affine intersection and coefficient
cancellation. Equal intersections merge by canonical RREF. Let `K` be the
maximum number of nonzero signed terms at any stage. Under one fixed capability
with `K <= L^q`, fixed polynomial work and certificate budgets, the complete
construction, exact counting, SAT witness recovery and UNSAT cover verification
run in `O(m K poly(d,L))`.

This strictly extends C041: crossing hyperplanes in dimension 64 require only
three signed terms. The NAND3+NEQ pressure family exceeds the support budget and
returns `OPEN_INTERSECTION_CLOSURE`; this is a representation refusal, not a
hardness result.

## Canonical cycle allocation

```text
C036    same-language refinement
C036.1  Horn-affine unary negotiation
C036.2  exact OPEN vault
C036.3  Horn equality aliases
C036.4  complete Horn affine hull
C037    explicit residual OBDD alignment
C038    exact structured-vtree factor alignment
C039    fixed-k recursive separator compiler
C039.0  symbolic-factor contract
C039.1  pure-affine symbolic vtree factors
C039.2  single-head Horn projection
C040    low-affine-dimension Horn/dual-Horn composer
C041    laminar affine-subspace avoidance
C042    bounded signed-intersection support
```

Legacy branch and file paths may retain older identifiers solely for
pre-admission replayability. PR titles, this route matrix and new
machine-readable artifacts define the canonical allocation.

## Converged constructive bottleneck

The surviving universal obligation is:

```text
construct, in polynomial total work, a decomposition and join-closed
proof-carrying message algebra whose semantic state or cover volume is
polynomial on every CNF, with SAT witness recovery and independently
checkable UNSAT evidence.
```

C041 removes `2^d` enumeration for laminar subspace arrangements. C042
extends exact counting to crossing arrangements whose deterministically
constructed nonzero signed-intersection support remains within one fixed
polynomial capability. The next advance must decompose or symbolically compress
instances where this global support is superpolynomial, without hiding a SAT
oracle or exponential intermediate objects.

## Non-duplication and honesty rules

Before admitting a candidate compare against:

```text
PS-width and communication rows
OBDD / SDD / d-SDNNF / TDD
treewidth / branch decompositions
Horn and dual-Horn closure
GF(2) elimination and affine dimension
SUB-SAT / union-of-subspace avoidance
subspace-arrangement intersection posets and Möbius support
beta-acyclic elimination
DPLL(T) / DPLL(XOR)
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
non-laminarity as a hardness proof
signed-support explosion as a lower bound against all algorithms
```
