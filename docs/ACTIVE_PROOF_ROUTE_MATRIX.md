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
| C034 | Affine and cross-class composition | Replayable GF(2) certificates and exact `O(2^k poly(L))` heterogeneous composition for shared boundary `k` | Named tractable modules imply an unrestricted tractable mixture | `PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION` |
| C035 | Certified interface congruence | Replayed exact residual messages give a sound merge congruence; absorbing proofs and affine RREF produce real compression | Exponential diversity in one product language is intrinsic hardness | `JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION` |
| C036 | Proof-carrying partition refinement | Complete polynomial separator extraction for Horn and affine residuals; every accepted split carries a replayable continuation | Failure to find a separator permits merging; explicit refinement automatically has polynomial state generation | `CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY` |
| C036.1 | Horn-affine negotiation extension | Complete affine-to-Horn directed inclusion/separator extraction plus replayable shared-literal conflict traces and SQLite proof caching | A propagation fixpoint certifies compatibility; constants-only exchange decides Horn-affine mixtures | `REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA` |
| C036.2 | Proof-Carrying Open-Core Vault | Exact capability-scoped OPEN storage, logical STALE, immutable evaluations and fail-closed replay | Cached OPEN is intrinsic hardness; capability changes permit silent reuse | `CI_ADMISSION_AND_PROTOCOL_INTEGRATION` |
| C037 | Explicit residual OBDD alignment | Exact minimization, pairwise distinguishing suffixes, SAT witnesses and UNSAT DAG certificates once the residual graph is explicit | Partition refinement alone avoids state explosion; an equivalence-query teacher is free | `POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact vtree-cut continuation rows, replayable separators, witness/UNSAT tables and deterministic charged candidate construction | Recursive structure or a supplied vtree automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039 | Symbolic factor construction contract | Proof-carrying LEAF/JOIN/PROJECT/MERGE/SEPARATE envelopes, payload-policy gate and capability-locked Vault protocol | Encoded truth tables are symbolic; unsupported languages may fall back to SAT; supplied vtree is discovered | `POLYNOMIAL_SYMBOLIC_JOIN_PROJECT_MERGE_AND_REPLAYABLE_FACTOR_EQUIVALENCE` |
| C039.1 | Single-head Horn symbolic compiler | Exact replayable LEAF/JOIN/PROJECT and deterministic supplied-vtree cost certificates; strict single-head forgetting keeps rule count nonincreasing while charging literal volume | A general-Horn exponential projection fixture applies unchanged to strict single-head Horn; supplied-vtree evaluation is discovery | `GENERAL_HORN_OR_CROSS_LANGUAGE_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C040 | Portfolio-guided semantic vtree discovery | Reserved: discovery cost must be charged and candidate quality must be replayable | A supplied good vtree substitutes for polynomial discovery | `POLYNOMIAL_VTREE_DISCOVERY` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> certified symbolic cut messages
-> proof-carrying JOIN and PROJECT
-> certified MERGE and SEPARATE
-> polynomial reachable quotient construction
-> portfolio-guided polynomial vtree discovery
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C038 receives or heuristically constructs a vtree and explicitly enumerates the
cut communication rows. Its equality control demonstrates both a small paired
vtree and an exponential blocked cut, but does not prove universal discovery.

C039 receives a supplied, verified vtree and specifies symbolic factor
construction. The first C039 commit validates operation envelopes, registered
symbolic payloads, proof-reference closure, budget terminals and the external
`OpenCoreVaultSink` protocol.

C039.1 supplies the first executable profile: `SINGLE_HEAD_HORN_V1`. It performs
exact LEAF/JOIN/PROJECT and emits replayable supplied-vtree cost certificates.
The profile allows at most one defining rule per atomic head. Under its exact
Davis–Putnam-style projection, the rule count does not increase; literal volume
and work are still charged and may return fail-closed `OPEN` under a chosen
budget. This result does not extend to arbitrary Horn CNF.

```text
C039:
  supplied verified vtree
  symbolic factor construction
  certified merge/separate contract

C039.1:
  supplied verified vtree
  executable single-head Horn LEAF/JOIN/PROJECT
  no Horn MERGE/SEPARATE
  no general Horn

C040:
  portfolio-guided semantic vtree discovery
  discovery cost charged
  no supplied-vtree substitution
```

## Canonical cycle allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 Horn-affine negotiation extension
C036.2 proof-carrying Open-Core Vault
C037   explicit residual OBDD alignment
C038   structured vtree factor alignment
C039   symbolic factor construction without truth-table enumeration
C039.1 single-head Horn symbolic compiler
C040   portfolio-guided semantic vtree discovery
```

## Converged constructive bottleneck

```text
POLYNOMIAL_VTREE_DISCOVERY
+
POLYNOMIAL_SYMBOLIC_FACTOR_CONSTRUCTION
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

No future cycle may claim progress merely by renaming this object. Progress
requires a new polynomial construction theorem, a strictly stronger replayable
message algebra, a complete separator extractor for a larger closed language,
or a decisive obstruction to one explicit route.

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

## Non-duplication rule

Before admission, compare against:

```text
PS-width
MIM-width / incidence width
DNNF / d-DNNF / OBDD / SDD / TDD
factor width and vtree communication rows
backdoor size
residual-state width
proof width and certificate discovery
beta-acyclic elimination
Davis-Putnam variable elimination
Horn and dual-Horn closure
single-head Horn forgetting and single-head equivalence
GF(2) affine elimination
Schaefer fixed-language mixtures
communication/continuation equivalence across cuts
partition refinement and canonical residual automata
symbolic bisimulation and distinguishing-test bases
active automata learning and equivalence-query teachers
cooperating decision procedures and DPLL(T)/DPLL(XOR) propagation
```

A renamed known parameter is an alignment result, not a new theorem.
