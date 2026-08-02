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
| C037 | Explicit residual OBDD alignment | Exact minimization, pairwise distinguishing suffixes, SAT witnesses and UNSAT DAG certificates once the residual graph is explicit | Partition refinement alone avoids state explosion; an equivalence-query teacher is free | `POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION` |
| C038 | Structured vtree factor alignment | Exact vtree-cut continuation rows, replayable separators, witness/UNSAT tables and deterministic charged candidate construction | Recursive structure or a supplied vtree automatically removes exponential interfaces | `POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION` |
| C039 | Symbolic affine factor compiler | Exact bottom-up affine join/project/canonicalize on any charged vtree, at most `|B_u|` RREF rows per satisfiable message, replayed merge/separate, SAT recovery and XOR-provenance UNSAT | Exponential communication rows must be materialized; affine closure automatically extends to Horn/affine or arbitrary CNF | `CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN` |
| C031 | Proof-carrying SAT refuter | Formal lower-bound transfer interface | Uncertified circuit counterexamples and free direct-sum amplification | `NO_SHARING_REFUTER_AMPLIFICATION` |

## Constructive P=NP track

```text
tractable local languages
-> exact semantic cut signatures or certified symbolic elimination
-> proof-carrying cross-class interface compression
-> jointly selected decomposition, message language and proof rules
-> certified merge and separator extraction
-> certified cross-language fact exchange
-> polynomial reachable quotient construction
-> polynomial vtree discovery and symbolic factor construction
-> cross-language symbolic projection closed under join
-> SAT witness + UNSAT certificate
-> universal polynomial SAT algorithm
```

C036 supplies polynomial same-language separator extraction for Horn and affine
messages. C036.1 supplies a complete affine-to-Horn directed separator test and a
sound but incomplete proof-carrying unary negotiation protocol. Its equality/NEQ
control proves that `OPEN_FIXPOINT` is not compatibility.

C037 supplies the complete continuation quotient after an exact finite residual
graph has been generated and aligns fixed-order refinement with reduced OBDD.

C038 moves from one line to a recursive vtree. For each vtree cut it constructs
the exact Boolean communication rows and their continuation quotient, together
with replayable outside-assignment separators. This is aligned with structured
d-DNNF / SDD / TDD factor-width views; it is not a new width parameter.

The equality control shows both sides of C038:

```text
paired vtree: local equality interactions remain small
blocked vtree: one cut has exactly 2^n continuation rows
```

A deterministic co-occurrence heuristic rediscovers the paired structure on this
family, but no universal optimality or polynomial-width guarantee is claimed.

C039 closes symbolic factor construction for the affine branch. Each factor is
placed at the lowest vtree node containing its support. A region exports the
canonical affine relation on variables referenced by ancestor factors:

```text
M_u = canonical_RREF(project_{B_u}(M_left AND M_right AND F_u)).
```

Every satisfiable message contains at most `|B_u|` independent rows. Every row
carries original-equation XOR provenance. Equal canonical messages are merged;
distinct affine messages admit a polynomially extracted separator. A top-down
extension trace recovers SAT witnesses, and UNSAT is accepted only with a replayed
`0=1` provenance.

On blocked affine equality, C038 has `2^n` explicit continuation rows. C039 retains
the boundary variables and processes the crossing equations symbolically. The
audit reaches `n=64`, corresponding to `18446744073709551616` explicit rows,
without materializing them. This is not a contradiction: explicit factor width
and symbolic algebraic manipulation charge different objects.

The immediate target after C039 is:

```text
CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN
```

Construct a replayable message algebra that remains polynomial when Horn, affine,
beta-acyclic, PS-signature or compiled regions interact. Charge decomposition
discovery, factor placement, joins, projections, canonicalization, merge and
separator proofs, witness recovery, UNSAT discovery, and certificate volume.
Return `OPEN` whenever the admitted closure or any explicit polynomial budget
fails.

## Canonical cycle allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 Horn-affine negotiation extension of C036
C037   explicit residual OBDD alignment
C038   structured vtree factor alignment
C039   proof-carrying symbolic affine factor compilation
```

The C036.1 branch and several pre-admission paths retain their original `c037`
spelling as legacy aliases for replayability, but the route matrix and
machine-readable artifact assign the result only to `C036.1`. C037 uniquely
denotes OBDD alignment.

## Converged constructive bottleneck

The following names are linked views of one missing core:

```text
C025 certified residual quotient complexity
C032 symbolic PS-signature compression
C033 portfolio selection with symbolic messages
C034 proof-carrying cross-class interface compression
C035 joint decomposition/language/proof selection
C036 cross-language symbolic separator discovery
C036.1 reverse Horn-to-affine separation or stronger fact algebra
C037 order/decomposition and reachable quotient construction
C038 vtree discovery and symbolic factor construction
C039 cross-language symbolic projection closed under join
```

C039 removes the truth-table construction cost for pure affine subtrees on every
vtree. It does not remove the cross-language gate. No future cycle may claim
progress merely by renaming this object. Progress requires a new polynomial
construction theorem, a strictly stronger replayable message algebra, a complete
separator/projector for a larger join-closed language, or a decisive obstruction
to one explicit proposed algebra.

## Separation track

```text
proof-carrying circuit refuter
-> certificate-preserving SAT embedding
-> no-sharing amplification
-> SAT not in P/poly
-> P != NP
```

This track remains useful as an adversarial control even while the user-selected
primary objective is `P=NP`.

## Non-duplication rule

Before admitting a new hypothesis, compare it against:

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
GF(2) affine elimination
Schaefer fixed-language mixtures
communication/continuation equivalence across cuts
partition refinement and canonical residual automata
symbolic bisimulation and distinguishing-test bases
active automata learning and equivalence-query teachers
cooperating decision procedures and DPLL(T)/DPLL(XOR) propagation
existential quantification and forgetting closure of the proposed message language
factor placement and variable-retention cost at vtree joins
```

A renamed known parameter is registered as an alignment result, not promoted as
a new theorem.
