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
| C040.1 | Producer-lane affine/Horn module-forest implementation | Deterministically isolates duplicate Horn producers into single-head lanes, discovers acyclic native module forests, and compiles exact SAT/UNSAT messages when complete module boundaries are logarithmic | Duplicate heads must be rejected before decomposition; producer isolation automatically yields small interfaces; a derived vtree has low standard factor width | `RICHER_MESSAGES_OR_DISCOVERY_BEYOND_FOREST_LOG_BOUNDARIES` |
| C041 | Joint compiler/portfolio completeness | Reserved in the C040 contract line for evaluation under the integrated C039 capability digest | `OPEN_PORTFOLIO_EXHAUSTED` can be attributed to discovery before compiler closure is exhausted | `UNIVERSAL_POLYNOMIAL_COMPILE_OR_EXACT_OPEN_FRONTIER` |
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
-> producer-lane module-forest implementation
-> joint compiler/portfolio completeness
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C038 verifies recursive vtree factors but does not provide a universal polynomial
vtree constructor. C039.0 receives a supplied verified vtree and validates symbolic
factor operations. C039.1, C039.2 and C039.3 enlarge the set of supplied trees that
can produce a complete replayable `CLOSED_POLY` result.

C040 owns the frozen semantic-vtree discovery contract:

```text
canonical formula and capability
-> proof-carrying feature extraction
-> generate the complete candidate list
-> freeze and hash the candidate manifest
-> run exactly one bounded full C039 probe per candidate
-> select by deterministic certified cost tuple
```

Only a full C039 `CLOSED_POLY` certificate makes a candidate selectable. A failed
portfolio returns only capability-scoped `OPEN_PORTFOLIO_EXHAUSTED`.

C040.1 is an implementation candidate under that discovery direction, not a
replacement contract. It receives raw tagged affine and Horn factors and assigns
Horn producers to deterministic lanes:

```text
for each head h:
  sort producers by factor id
  producer rank k -> lane k
```

Connected components inside one lane are single-head by construction. Affine
factors remain in native affine connected components. Shared variables induce a
module interaction graph.

C040.1 closes exactly when:

```text
module graph is a forest
every shared variable occurs in at most two modules
for every module M: |B_M| <= floor(log2 L)
```

The exact proof-carrying dynamic program costs

```text
sum_M 2^|B_M| poly(L_M).
```

Native affine regions use Gaussian elimination and native Horn regions use
least-model reasoning. Only cross-module interfaces are enumerated. A derived
binary variable vtree is validated as an embedding witness, but the load-bearing
proof object is the module-forest dynamic program, not a standard factor-width
claim.

Producer lanes strictly improve the baseline refusal. Sixty-four independent
pairs

```text
a_i -> q_i
b_i -> q_i
```

are accepted after lane isolation with maximum module boundary one.

For the C039.2 projection-obstruction family

```text
a_i -> q_i
b_i -> q_i
(q_1 AND ... AND q_n) -> z,
```

discovery constructs a star: the lane-zero rules form one central module and the
lane-one producers form leaves. The central boundary is

```text
{q_1,...,q_n}.
```

At `n=64`, C040.1 returns `OPEN_INTERFACE_WIDTH` before materializing `2^64`
interface rows. Thus duplicate-head collision is removed, but the exact wide
interface remains visible and charged.

Three producers of one head create one shared variable in three lane modules and
return `OPEN_INTERFACE_HYPEREDGE`. Cyclic module graphs return
`OPEN_MODULE_CYCLE`. Neither terminal is promoted to intrinsic hardness.

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
  frozen assignment-independent candidate portfolio
  one full bounded C039 probe per candidate
  certified deterministic selection

C040.1:
  deterministic producer-lane module construction
  exact forest/log-boundary admission
  proof-carrying native-module dynamic program
```

The C040.1 branch, executable, proposal and wire-schema paths retain the legacy
`c040` spelling because the package was assembled before the canonical C040
contract allocation was reconciled. The logical cycle is uniquely `C040.1`.

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
C040   portfolio-guided semantic vtree discovery contract
C040.1 producer-lane module-forest implementation
C041   joint compiler/portfolio completeness
```

## Converged constructive bottleneck

```text
POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS
+
POLYNOMIAL_JOIN-CLOSED_SYMBOLIC_MESSAGE_ALGEBRA
+
RICHER_MESSAGES_OR_DISCOVERY_BEYOND_FOREST_LOG_BOUNDARIES
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

C040 proves safe selection for a frozen polynomial candidate portfolio. C040.1
supplies one genuinely discovered mixed-language class, but its explicit interface
algebra remains limited to forests with logarithmic complete module boundaries.
The missing theorem is either a richer proof-carrying message algebra or a
strictly stronger charged decomposition theorem.

## Non-duplication and honesty rules

Never promote:

```text
a supplied decomposition as free discovery
an input-dependent exponent as polynomial
a branch-dependent vtree as one global decomposition
partial, sampled or estimated probes as CLOSED_POLY
finite fixtures as universal candidate completeness
producer isolation as automatic interface compression
OPEN as UNSAT or intrinsic hardness
similarity, reduction or shared features as OPEN transfer
one representation lower bound as P!=NP
```
