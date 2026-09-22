# R5 E8 6I — Instance-Specific Induced-Algebra Source Admission Audit

Date: 2026-09-22

Authority: `SOURCE_BOUND_STRUCTURAL_PRINCIPLE_ADMISSION_AUDIT__ONE_SCOPED_GATE_ONLY__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authority:

- `research/R5_B1B1C5B2B2_E8_6H_POST_INVENTORY_STRATEGIC_LOCK_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_SOURCE_BOUND_TRACTABLE_INVARIANT_INVENTORY_2026-09-22_v1.0.md`

## 0. Why this audit is allowed under 6H

6H permits strategic review only if a genuinely new **source-bound structural principle** appears after the mandatory anti-duplication comparison.

This audit does not claim a new result in the literature.

The question is only whether a known external principle is:

1. new to the current JANUS audited set;
2. structurally non-reducible to the seven mandatory predecessor mechanisms;
3. precise enough to define one exact theorem gate without introducing a heuristic solver.

## 1. Source-bound principle

### Primary source A — induced problem / algebra assignment on solutions

Rustem Takhanov,
*On the induced problem for fixed-template CSPs*,
arXiv:1708.08292v3, revised 2023.

Source:

https://arxiv.org/abs/1708.08292

The source fixes a finite family of algebras `B` on the value domain and asks whether one can assign an algebra `A_v in B` to each CSP variable such that every constraint relation is a subalgebra of the product of the algebras assigned to its scope.

Equivalently, for every basic operation symbol, each relation is preserved by the coordinate-wise tuple of the variable-specific operations.

The source proves that finding such an algebra assignment is itself a fixed-template CSP over an induced template `Gamma^B`.

It further introduces the CSP-with-input-prototype problem and proves that, when every algebra in `B` is tractable, the prototype-to-original-solution stage is tractable.

Thus the source separates exactly the resources relevant to 6H:

```text
PROTOTYPE / STRUCTURAL CERTIFICATE DISCOVERY
from
SOLUTION GIVEN A PROTOTYPE.
```

### Primary source B — multi-sorted algebraic CSP

Andrei A. Bulatov and Peter Jeavons,
*An Algebraic Approach to Multi-sorted Constraints*,
CP 2003, LNCS 2833, 183–198.

Source record:

https://ora.ox.ac.uk/objects/uuid%3A401ed69e-3437-4e1c-b9f1-f3d6e6a758c4

The source establishes that one-sorted simplification can hide tractable structure and develops multi-sorted polymorphisms whose interpretations may differ across domains/sorts while still acting as one compatible operation family on every relation.

This is the external structural precedent for variable/sort-specific algebraic behavior.

### Primary source C — discoverability is sometimes polynomial

Clément Carbonnel,
*The Dichotomy for Conservative Constraint Satisfaction is Polynomially Decidable*,
arXiv:1604.07063.

Source:

https://arxiv.org/abs/1604.07063

The source gives a polynomial-time recognition algorithm for conservative-CSP tractability and outputs the associated coloured graph.

This is a positive control only:

```text
ALGEBRAIC TRACTABILITY CERTIFICATES
CAN SOMETIMES BE POLYNOMIALLY DISCOVERABLE.
```

It does not imply polynomial discovery for arbitrary 3-SAT induced-algebra prototypes.

## 2. Candidate structural principle

Freeze:

```text
INSTANCE-SPECIFIC
INDUCED ALGEBRA CERTIFICATE

I_B(F)
=
(v -> A_v in B)
```

such that every local relation of `F` is a subalgebra of the product of the assigned algebras.

The crucial difference from the previous fixed-language inventory is:

```text
ONE GLOBAL POLYMORPHISM
is not required.

VARIABLE / SORT SPECIFIC
TRACTABLE ALGEBRA INTERPRETATIONS
may be coordinated by the same operation signature.
```

The induced template `Gamma^B` records exactly which algebra-label tuples are compatible with each original relation.

Therefore certificate discovery is not hidden:

```text
DISCOVER I_B(F)
=
solve the explicit induced CSP
over Gamma^B.
```

## 3. Mandatory predecessor comparison

### P1 — FACTORIZED_FEEDBACK

```text
REDUCIBLE
=
NO
```

Factorized feedback requires exact cross-component independence and disjoint dependency components.

The induced-algebra principle permits connected constraints and represents coupling by local subalgebra preservation conditions.

No component factorization is assumed.

### P2 — EXACT_INTERFACE_QUOTIENT

```text
REDUCIBLE
=
NO
```

The quotient theorem compresses raw interface assignments by downstream observational equivalence.

The induced-algebra principle does not quotient assignments.  It assigns local algebraic closure structure to variable sorts and constrains those labels relation-by-relation.

### P3 — LOG_ALIEN_TRANSFER

```text
REDUCIBLE
=
NO
```

The log-alien theorem is polynomial only under an explicit `q^k <= L` bounded-alien admission.

The induced-algebra source principle has no bounded alien-count premise.

### P4 — AFFINE_BOUNDARY

```text
REDUCIBLE
=
NO
```

The historical uniform affine-boundary route is all-affine and was already superseded by the raw/compositional basis layer.

The induced-algebra principle is expressly heterogeneous and may coordinate different algebra interpretations at different variables/sorts.

### P5 — GUARDED_OUTPUT_ELIMINATION

```text
REDUCIBLE
=
NO
```

Guarded elimination certifies a fixed elimination route when every bucket passes a polynomial pre-expansion row-product budget.

The induced-algebra principle contains no bucket-output guard and no elimination-order assumption.

### P6 — C023 / C023R

```text
REDUCIBLE
=
NO
```

C023/C023R are exact residual-cache / execution-DAG objects.

The induced-algebra certificate is a static algebraic closure assignment and does not rely on branch convergence, cache hits or residual equality.

### P7 — RAW_SCHAEFER_BASIS

```text
REDUCIBLE
=
NO,
BUT DIRECTLY ADJACENT.
```

The raw Schaefer basis theorem recognizes whether **one common** frozen Boolean basis preserves the complete language.

The induced-algebra principle strictly changes the object:

```text
one global operation
->
variable-specific operation interpretations
linked by relation-local product closure.
```

If `|B|=1`, the induced-algebra route collapses back toward the global-basis case.

For `|B|>1`, the algebra-label compatibility instance `Gamma^B` is an additional structural layer not present in the sealed raw-basis theorem.

The raw-basis theorem itself named
`RAW_STRUCTURE_TO_COMPOSITIONAL_BASIS_EXPLANATION`
as a later open surface.  The external induced-algebra framework is a source-bound realization of such a surface, not a relabeling of the fixed-six recognizer.

## 4. Admission verdict

```text
SOURCE_BOUND_STRUCTURAL_PRINCIPLE
=
FOUND

NEW_TO_LITERATURE
=
NO

NEW_TO_CURRENT_JANUS_AUDITED_SET
=
YES

MANDATORY_PREDECESSOR_COMPARISON
=
PASS_NOT_REDUCIBLE

6H_UNLOCK_SCOPE
=
ONE EXACT 6I ADMISSION GATE ONLY

SUCCESSOR_ALGORITHM
=
STILL LOCKED

D1
=
EMPTY

P_VS_NP
=
OPEN
```

This authorizes analysis of the induced-algebra bridge.

It does **not** authorize free-form algorithm design.

## 5. Two exact boundary controls already closed

### 5.1 Too rigid — standard Boolean B4

Freeze the common ternary signature library

```text
B4
=
{AND3, OR3, MAJ3, XOR3}.
```

Exact exhaustive checker:

`research/tools/r5_e8_6i_induced_algebra_b4_checker.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_BOOLEAN_B4_INDUCED_ALGEBRA_KILLER_TEST_2026-09-22_v1.0.json`

The satisfiable formula

```text
(x OR y OR z)
AND
(NOT x OR NOT y OR NOT z)
```

admits no common assignment of one B4 algebra label to each of `x,y,z` that preserves both clause relations.

Also:

```text
Gamma_3SAT -> Gamma_3SAT^B4
=
NO HOMOMORPHISM
```

under the frozen B4 induced template.

Therefore:

```text
B4 UNIVERSAL COVERAGE
=
FALSIFIED.
```

This is a fixed-library falsifier only.

### 5.2 Too expressive — constant value-coding algebras

Authority:

`research/R5_B1B1C5B2B2_E8_6I_CONSTANT_ALGEBRA_HIDDEN_CHOICE_CONTROL_2026-09-22_v1.0.md`

For

```text
B_const={A_0,A_1}
```

where the common unary operation of `A_b` constantly returns `b`, every induced relation is exactly the original Boolean relation after the renaming

```text
0 <-> A_0
1 <-> A_1.
```

Thus:

```text
Gamma^{B_const}
cong
Gamma.
```

Coverage is perfect, but prototype discovery is exactly the original CSP.

Therefore:

```text
VALUE-CODING COVERAGE
=
NO ALGORITHMIC PROGRESS.
```

## 6. Exact 6I theorem gate

The only authorized target is now:

```text
R5_E8_6I_INDUCED_ALGEBRA
COVERAGE_DISCOVERY_BRIDGE_GATE_V1
```

Fix the full signed 3-clause Boolean template `Gamma_3SAT`.

A candidate finite/poly-described tractable algebra family `B` is admitted only if all gates close.

### G1 — algebra tractability

Every algebra in `B` has an exact source-bound polynomial CSP/input-prototype algorithm.

### G2 — polynomial description/construction

`B`, its operation tables/circuits, and the induced local label relations are constructible in `poly(L)`.

For a fixed finite `B`, this is constant-template work; for an instance-generated family, its total description is charged.

### G3 — prototype discovery

```text
CSP(Gamma_3SAT^B)
=
POLYNOMIAL
```

by a proof/theorem, not by finite diagnostics.

No SAT oracle, equivalence oracle, witness guessing or semantic sweeping may be used to find the prototype.

### G4 — coverage / sound fail-closed reduction

There must be an exact source-bound proof that the prototype layer is sufficient for **every** 3-CNF instance.

A source-native sufficient form is:

```text
Gamma_3SAT
->
Gamma_3SAT^B
```

together with the induced-CSP / input-prototype reduction.

An alternative coverage theorem is allowed only if it proves the same complete SAT/UNSAT decision coverage without hidden exponential branching.

### G5 — prototype-to-original solve

Given a prototype homomorphism, solve/reconstruct the original Boolean CSP in polynomial time using only the proved tractability of `B` and source-bound input-prototype machinery.

### G6 — lifecycle

```text
T_construct
+
T_prototype_discovery
+
T_original_solve
+
T_reconstruct
+
T_verify
+
T_history

<=
poly(L).
```

### G7 — no semantic-choice encoding

Reject a family if its algebra labels merely encode arbitrary Boolean assignments or another object whose discovery is polynomially equivalent to the original SAT problem.

`B_const` is the frozen negative control.

## 7. Conditional consequence

If one `B` closes G1–G7 for the full signed 3-clause template, then the source-induced pipeline gives a uniform polynomial algorithm for 3-SAT.

At that point, and only after independent replay of all lifecycle claims:

```text
SAT in P
=>
P = NP.
```

No such `B` is established here.

## 8. Current next object

```text
CURRENT_THEOREM_TARGET
=
CLASSIFY THE INDUCED TEMPLATE
Gamma_3SAT^B
FOR NONTRIVIAL TRACTABLE
BOOLEAN / LIFTED ALGEBRA FAMILIES

FIRST CLOSED CONTROL
=
B4 FAILS COVERAGE

SECOND CLOSED CONTROL
=
B_const HIDES SAT CHOICE

NEXT SEARCH
=
SOURCE-BOUND ALGEBRA FAMILIES
BETWEEN THESE EXTREMES,
WITH PROVABLE POLY
PROTOTYPE DISCOVERY
```

No heuristic search is authorized as evidence.

Finite enumeration may be used only to falsify a fixed candidate or discover a symbolic theorem statement.

## Claim ceiling

```text
NEW GENERAL SAT ALGORITHM
=
NO

SUCCESSOR ALGORITHM
=
LOCKED

6I SOURCE-BOUND GATE
=
AUTHORIZED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
