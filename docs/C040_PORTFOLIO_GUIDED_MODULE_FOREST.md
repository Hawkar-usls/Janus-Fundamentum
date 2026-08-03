# C040 — Portfolio-Guided Module-Forest Discovery

**Status:** `CONSTRUCTIVE_RESTRICTED_THEOREM / P_VS_NP=OPEN`

## Purpose

C039 gives a complete symbolic factor algebra for affine `GF(2)` regions. C039.1 gives a complete symbolic compiler for single-head Horn regions and proves that unrestricted boundary-only Horn CNF can blow up exponentially under projection.

C040 asks the next constructive question:

```text
Can the decomposition itself be discovered from raw tagged factors so that
native affine and single-head Horn engines are used automatically, while every
cross-language interface and every discovery step is charged?
```

The answer is positive for one explicit class: discovered acyclic module networks with logarithmic per-module interfaces.

C040 is not a universal vtree optimizer. It returns strict `OPEN` outside the admitted class.

## Raw input and native modules

The input is a set of factors tagged as either:

```text
AFFINE_GF2
SINGLE_HEAD_HORN
```

No module partition is supplied.

C040 constructs modules deterministically.

1. Build the affine factor-variable incidence subgraph and take its connected components.
2. Build the Horn factor-variable incidence subgraph and take its connected components.
3. Reject a Horn component with two positive rules headed by the same variable:

```text
OPEN_HEAD_CONFLICT
```

Thus every admitted Horn component is globally single-head, not merely clause-wise Horn.

The components are maximal under same-language variable connectivity. This makes the partition canonical under the fixed factor identifiers and avoids treating a favorable supplied partition as free.

## Module interaction forest

Two discovered modules are adjacent when they share at least one variable. The exact shared-variable set is the edge separator.

Admission requires:

```text
every shared variable belongs to at most two modules
the module interaction graph is a forest
for every module M: |B_M| <= floor(log2 L)
```

where `L` is the charged input encoding size and `B_M` is the union of all shared variables incident to `M`.

The algorithm returns:

```text
OPEN_INTERFACE_HYPEREDGE
OPEN_MODULE_CYCLE
OPEN_INTERFACE_WIDTH
```

when these conditions fail.

The condition is aligned with acyclic join trees and bounded-interface dynamic programming. It is not promoted as a new universal width parameter.

## Derived variable vtree

After the module forest is verified, C040 derives a deterministic binary variable tree.

- Every variable is owned by the smallest-id module containing it.
- Owned variables are balanced inside the module node.
- Child module subtrees are combined in sorted order.
- Forest roots are combined in sorted order.

The verifier checks that every input variable occurs exactly once as a leaf.

This tree is a verified decomposition witness. C040 does **not** claim that its standard TDD/SDD factor width is polynomial. The load-bearing proof object is the module-forest dynamic program described below.

## Exact bottom-up composition

Root every module-tree component at its smallest module identifier.

For a module `M`, let:

```text
B_M = all variables shared with neighboring modules
S_MP = variables shared with the parent P
```

C040 enumerates assignments only to `B_M`. For every such assignment:

1. solve the native module under the fixed boundary values;
2. check the already compiled child message on every child separator;
3. accept the assignment exactly when the native module and all child subtrees accept it.

The outgoing message to the parent is:

```text
M_M(S_MP) = exists (B_M \ S_MP) .
            native_M(B_M) AND AND_child M_child(S_Mchild)
```

It is stored as a complete table on the parent separator. Since the total incident boundary of each module is logarithmic, the enumeration is polynomial.

This is intentionally different from C039's pure affine symbolic RREF messages. Native regions remain symbolic; only the discovered cross-language interfaces are enumerated.

## Native proof objects

### Affine module

The native affine solver performs deterministic Gaussian elimination.

- SAT returns a complete module assignment respecting the fixed boundary.
- UNSAT returns provenance bitsets over original rows and fixed boundary equations whose XOR is exactly `0=1`.

### Single-head Horn module

The native Horn solver performs deterministic least-model closure.

- SAT returns the least model extending the fixed true boundary values.
- UNSAT returns a derivation trace ending in a negative clause or a head fixed false.

## SAT witness recovery

For every true parent-separator row, the message stores one deterministic accepted full boundary assignment.

Starting at each root:

1. choose the stored full boundary assignment;
2. recover the native module witness;
3. pass each child separator assignment to the child message;
4. combine module assignments, rejecting any inconsistency.

Because every shared variable is fixed by the same separator key, the recovered assignments agree. The final witness is checked against every original factor.

## UNSAT certificate

For every false message row, C040 records a blocker for every extension to the module's full incident boundary.

A blocker is either:

```text
NATIVE_UNSAT
CHILD_FALSE
```

`NATIVE_UNSAT` includes the affine provenance or Horn conflict trace. `CHILD_FALSE` points to an already compiled false child row.

An UNSAT root therefore supplies a finite recursive blocking proof for the empty separator assignment. Its volume is charged and bounded by the same logarithmic-interface tables.

## Constructive theorem

Let a raw tagged instance have encoding size `L`. Suppose deterministic discovery produces modules satisfying:

1. every module is pure affine or pure single-head Horn;
2. the module interaction graph is a forest;
3. each shared variable belongs to at most two modules;
4. every module has at most `floor(log2 L)` incident shared variables.

Then C040 constructs and verifies in

```text
sum_M 2^|B_M| poly(L_M)
```

time and certificate volume:

- the canonical native-module partition;
- the module interaction forest;
- a verified derived variable vtree;
- exact bottom-up separator messages;
- a complete SAT witness, or
- a recursively replayable UNSAT certificate.

Since `2^|B_M| <= L`, total construction and verification are polynomial.

No decomposition, module partition, SAT oracle, equivalence oracle, or external solver is supplied for free.

## What C040 genuinely adds

C034 proved polynomial heterogeneous composition when modules and a logarithmic shared boundary are already supplied.

C040 adds the missing restricted discovery layer:

```text
raw tagged factors
-> maximal native components
-> single-head admission
-> exact interaction graph
-> forest recognition
-> logarithmic interface check
-> derived variable vtree
-> proof-carrying dynamic program
```

This is the first active cycle in which the portfolio determines the decomposition directly from the input rather than merely scoring a supplied structure.

## Exact negative controls

### Multi-producer Horn

Two rules

```text
a -> q
b -> q
```

occur in one connected Horn component and violate single-head admission. C040 returns an explicit pair of conflicting factor identifiers:

```text
OPEN_HEAD_CONFLICT
```

This does not prove that richer Horn circuits or existential modules cannot represent the component. It proves only that the current C039.1 native language cannot admit it as a single-head module.

### Alternating module cycle

A four-module alternating affine/Horn ring is detected exactly and returns:

```text
OPEN_MODULE_CYCLE
```

A cycle is not promoted to intrinsic hardness. It is outside this acyclic theorem.

### Wide star

One affine center interacting with many disjoint Horn leaves has an acyclic module graph but a large center boundary. It returns:

```text
OPEN_INTERFACE_WIDTH
```

Thus acyclicity alone is insufficient.

## Frozen executable audit

```bash
python experiments/direct/janus_c040_portfolio_module_forest.py --self-test
```

The deterministic audit requires:

```text
350 random admitted module forests on at most 9 variables
exact SAT/UNSAT agreement with exhaustive bounded-domain validation
independent replay of every returned certificate
180-module alternating affine/Horn chain
64-variable affine core
64-variable single-head Horn core
64 duplicate-producer pairs -> OPEN_HEAD_CONFLICT
alternating four-module cycle -> OPEN_MODULE_CYCLE
24-leaf interface star -> OPEN_INTERFACE_WIDTH
explicit work exhaustion -> OPEN_WORK_BUDGET
unsupported beta-acyclic tag -> OPEN_LANGUAGE
corrupt message certificate -> REJECTED
```

Exhaustive enumeration is used only by the bounded audit validator. It is not called by module discovery, the native solvers, the dynamic program, witness recovery, or certificate replay.

## Relation to primary literature

The single-head Horn admission rule is inherited from the polynomial forgetting result of Liberatore.

The forest dynamic program is aligned with classical acyclic database/CSP join trees. C040 does not rename join-tree acyclicity.

Structural-CSP work also emphasizes that a useful decomposition and its representation must be charged. C040 constructs its restricted decomposition instead of assuming one.

Knowledge-compilation methodology requires charging both succinctness and supported operations. C040 explicitly charges discovery, native decision, interface enumeration, projection, witness recovery, UNSAT replay and certificate volume.

## Relation to the active route

### C039

Pure affine components are solved natively by Gaussian elimination. Their internal continuation assignments are never enumerated.

### C039.1

Pure globally single-head Horn components are solved natively. Duplicate positive heads are exposed before composition rather than hidden inside a false compactness claim.

### C034

C040's interface tables use the same bounded-interface principle, but C040 discovers the modules and acyclic composition structure from raw factors.

### C038

C040 emits a verified variable vtree candidate, but it does not claim a universal vtree-width theorem. The exact tractability proof is tied to the discovered module forest and logarithmic module boundaries.

## Surviving gate

The next exact target is:

```text
RICHER_MESSAGES_OR_POLYNOMIAL_DISCOVERY_BEYOND_ACYCLIC_LOG_INTERFACES
```

A genuine next advance must do at least one of:

1. construct richer Horn or mixed-language messages that absorb multi-producer components;
2. extend proof-carrying composition to a rigorously larger cyclic structural class;
3. discover decompositions with polynomially bounded non-enumerative interfaces;
4. prove a decisive obstruction for one explicit richer message/decomposition proposal.

A heuristic score improvement, a supplied partition, or a small final artifact without charged construction does not pass the gate.

## Claim boundary

C040 is a complete polynomial compiler only for the discovered acyclic portfolio class with logarithmic per-module interfaces. It does not prove that arbitrary CNF admits this decomposition, solve unrestricted Horn-affine mixtures, establish polynomial standard vtree factor width, or resolve P versus NP.

```text
P_VS_NP=OPEN
```
