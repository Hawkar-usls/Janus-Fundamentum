# R5 E8 — Dual-Blowup Survivor Source/History Synthesis

Date: 2026-09-22

Authority: `SOURCE_HISTORY_SYNTHESIS_ONLY__NO_SUCCESSOR_AUTHORIZATION__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authority:

- `research/R5_B1B1C5B2B2_E8_FROZEN_GREEDY_POSTMORTEM_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_FROZEN_GREEDY_COUNTERFAMILY_SECOND_PASS_AUDIT_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_D1_REFERENCE_ELIMINATION_ADMISSION_AUDIT_2026-09-21_v1.0.md`
- `docs/C020_NONLINEAR_AFFINE_MASKING.md`

## 1. Purpose

After falsifying the exact frozen structural-only greedy projector, ask only:

```text
Is there an already-known representation family
that survives BOTH concrete E8 representation controls:

A) parity / flat-CNF elimination blow-up

and

B) cyclic structural-AIG Shannon blow-up

without merely hiding the difficulty in
terminal SAT, forgetting, compilation size,
semantic equivalence, or extension discovery?
```

This artifact is source/history synthesis only.

It does not open a successor algorithm.

## 2. Source S1 — ECNF is a dual-blowup representation survivor

Primary source:

Frédéric Koriche, Jean-Marie Lagniez, Pierre Marquis, Samuel Thomas,
“Knowledge Compilation for Model Counting: Affine Decision Trees,” IJCAI 2013.

Source:
https://www.ijcai.org/Proceedings/13/Papers/145.pdf

The paper defines:

```text
ECNF
=
finite conjunctions of extended clauses

extended clause
=
finite disjunction of affine / XOR clauses.
```

It also states:

```text
CNF
is linearly translatable into
ECNF.
```

### E8 control A — parity

A parity condition is already an affine clause / affine system.

Therefore the E8 parity witness need not be materialized as an exponentially large flat CNF inside ECNF.

```text
PARITY_NATIVE_COMPACTNESS
=
PASS
```

### E8 control B — cyclic local projection

The frozen counterfamily block is

```text
(x OR A)
AND
(NOT x OR B)
```

and exact selector elimination gives

```text
A OR B.
```

For the cyclic family, `A` and `B` are ordinary two-literal clauses.

Every literal is a unary affine clause, hence `A OR B` is directly representable as one ECNF extended clause.

Therefore:

```text
CYCLIC_LOCAL_PROJECTION_COMPACTNESS
=
PASS
```

for this specific control.

### Terminal blocker

The same IJCAI paper states that UNSAT for ECNF has the same complexity as for CNF:

```text
UNSAT(ECNF)
=
coNP-complete.
```

Derived consequence:

```text
CONSISTENCY / SAT(ECNF)
=
NP-complete.
```

The hardness is immediate from the linear CNF embedding; membership is ordinary polynomial verification of an assignment.

Thus:

```text
CTRL-E8-S1
=
ECNF_DUAL_BLOWUP_SURVIVOR_NOT_TERMINAL

ARBITRARY_CNF_ENTRY
=
PASS_LINEAR

PARITY_COMPACTNESS
=
PASS

CYCLIC_LOCAL_PROJECTION_COMPACTNESS
=
PASS

EXACT_EXPRESSIVITY
=
PASS

POLY_TERMINAL_CONSISTENCY
=
FAIL_UNLESS_P_EQUALS_NP

RESULT
=
SURVIVING_BOTH_SPECIFIC_REPRESENTATION_BLOWUPS
DOES_NOT_SUPPLY_D1.
```

## 3. Source S2 — EADT moves the blocker to forgetting

Same IJCAI 2013 source introduces EADT, extended affine decision trees.

The language is complete and supports polynomial-time consistency / model-counting style queries once an EADT representation is already available.

The paper also gives a CNF-to-EADT compiler based on generalized affine Shannon branching.

However, its knowledge-compilation transformation table explicitly marks general forgetting:

```text
FO(EADT)
=
NOT POLYNOMIAL UNLESS P=NP.
```

Thus:

```text
CTRL-E8-S2
=
EADT_AFFINE_AWARE_TRACTABLE_TARGET_BUT_FORGETTING_BARRIER

AFFINE_DECISIONS
=
NATIVE

POLY_CONSISTENCY_ON_COMPILED_OBJECT
=
PASS

COMPLETE_LANGUAGE
=
PASS

GENERAL_FORGETTING
=
NOT_POLY_UNLESS_P_EQUALS_NP

UNIVERSAL_POLY_CNF_TO_SMALL_EADT
=
NOT ESTABLISHED

RESULT
=
MOVING_TO_A_TRACTABLE_AFFINE_DECISION_LANGUAGE
DOES_NOT_CLOSE_REPEATED_PROJECTION.
```

The existence of a compiler in the paper is not interpreted as a universal polynomial-size / polynomial-total-work compilation theorem.

## 4. Source S3 — existential/disjunctive closure tradeoff

Primary sources:

Pierre Marquis,
“Existential Closures for Knowledge Compilation,” IJCAI 2011.

Hélène Fargier and Pierre Marquis,
“Extending the Knowledge Compilation Map: Krom, Horn, Affine and Beyond,” AAAI 2008.

The existential-closure principle makes forgetting easy by allowing existential work to remain represented explicitly:

```text
for any base language L,

L[exists]
supports forgetting by construction.
```

This is exactly the independent literature analogue of the E8 hidden-existential firewall:

```text
SYNTACTICALLY REMEMBER
"exists x still applies"

!=

REMOVE SEMANTIC CHOICE
AND RETAIN POLY TERMINAL SOLVING.
```

### CNF[exists]

Entry from arbitrary CNF is trivial and forgetting is easy in the existential closure.

But consistency remains as hard as CNF-SAT: wrapping or retaining existential variables does not solve the existential search problem.

Therefore:

```text
EASY_ENTRY
+
EASY_FORGETTING
!=
TRACTABLE_TERMINAL_CONSISTENCY.
```

### AFF[OR]

The AAAI 2008 source defines:

```text
AFF[OR]
=
disjunctions of affine formulae.
```

It is a complete propositional language.

Its KC tables establish polynomial:

```text
CO
=
consistency

FO
=
forgetting

AND_BC
=
bounded conjunction
```

among its supported operations.

This makes `AFF[OR]` a strong positive target control.

However, the paper explicitly leaves design of compilation algorithms targeting `AFF[OR]` as further work; it does not provide a universal polynomial arbitrary-CNF-to-polysize-`AFF[OR]` compiler.

Moreover, independently of the source:

```text
IF

Compile_AFFOR(F)
runs in poly(|F|)
and outputs poly(|F|) size

FOR EVERY CNF F,

THEN

run polynomial CO on Compile_AFFOR(F)

=> SAT in P
=> P=NP.
```

Hence such a universal compiler is itself a P=NP-level missing theorem.

### Control summary

```text
CTRL-E8-S3
=
EXISTENTIAL_CLOSURE_AND_AFFINE_DISJUNCTION_TRADEOFF

CNF[exists]:
EASY ENTRY
EASY FORGETTING
HARD TERMINAL CONSISTENCY

AFF[OR]:
TRACTABLE CONSISTENCY
TRACTABLE FORGETTING
AFFINE-NATIVE
BUT UNIVERSAL POLY CNF COMPILATION
NOT ESTABLISHED

LESSON
=
ENTRY / FORGETTING / CONSISTENCY / COMPILATION
ARE DISTINCT OBLIGATIONS.
```

## 5. Neighboring modern controls

### Structured d-DNNF

Harry Vinall-Smeeth, IJCAI 2024,
“Structured d-DNNF Is Not Closed under Negation.”

The paper proves that structured d-DNNF does not support polynomial-time general existential quantification.

Therefore:

```text
STRUCTURED_dDNNF
=
NOT_A_REPEATED_PROJECTION_ESCAPE.
```

This is a neighboring representation barrier, not a lower bound for arbitrary DNNF/AIG/ECNF.

### Learned-clause factoring / Extended Resolution

SAT 2026, Pollitt et al.,
“Factoring Learned Clauses.”

The work factors XOR/ITE structure from learned clauses and explicitly states that effective use of Extended Resolution in SAT remains an open challenge.

Therefore:

```text
KNOWN_PRACTICAL_SEMANTIC_FACTORING
!=
UNIVERSAL_POLY_EXTENSION_DISCOVERY_THEOREM.
```

### BVA

SAT 2026,
“Automated Reencoding Meets Graph Theory.”

The paper proves structural limits of even idealized BVA; e.g. for at-most-one it cannot reach fewer than `3n-6` clauses, while product encodings use `2n+o(n)`.

Therefore:

```text
AUXILIARY_REENCODING_MECHANISM
!=
UNIVERSAL_ACCESS_TO_ALL_COMPACT_ENCODINGS.
```

These are controls only; none is used as a general impossibility theorem for E8.

## 6. Internal history binding

### C020 nonlinear affine masking

Path:

`docs/C020_NONLINEAR_AFFINE_MASKING.md`

Already established internally:

```text
VISIBLE_AFFINE_STRUCTURE
=
NOT_REPRESENTATION_INVARIANT.
```

A polynomial-size bijective nonlinear triangular mask turns an explicit affine contradiction into a non-affine-looking exact CNF while preserving satisfiability.

Thus a successor of the form

```text
if XOR visible:
    Gaussian
else:
    generic CNF machinery
```

is already historically insufficient.

The missing issue is discovery / invariant representation, not the existence of Gaussian elimination.

### Existing scoped internal routes

Do not rediscover:

- `TRUMP_BICAMERAL_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_*`
- `TRUMP_EXACT_INTERFACE_QUOTIENT_BASIS_*`
- `TRUMP_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO_THEOREM_*`
- guarded bounded-output elimination
- C023 / C023R exact residual and cache-DAG routes.

Those already cover scoped cases where:

```text
affine structure is exposed,
factorization is available,
projection output is polynomially bounded,
or exact residual sharing is sufficient.
```

Dedicated internal `EADT / ECNF / AFF[OR]` lineage was not located in the current repository tree audit.

This means only:

```text
DEDICATED_INTERNAL_EADT_ECNF_AFFOR_LINEAGE
=
NOT_LOCATED_IN_THIS_AUDIT
```

not:

```text
PROVED_ABSENT.
```

## 7. Source/history synthesis verdict

```text
R5_E8_DUAL_BLOWUP_SOURCE_HISTORY_SYNTHESIS_V1

P_VS_NP
=
OPEN

FROZEN_STRUCTURAL_GREEDY
=
FALSIFIED

FLAT_CNF_DP
=
FALSIFIED_AS_UNIVERSAL_POLY_REPRESENTATION_ROUTE

KNOWN_REPRESENTATION_SURVIVING
BOTH_SPECIFIC_SIZE_CONTROLS
=
YES

EXAMPLE
=
ECNF / mixed clause-of-affine form

BUT

POLY_TERMINAL_SAT
=
FAIL / NP-HARD
```

Conversely:

```text
KNOWN_TRACTABLE
PROJECTION_AWARE / AFFINE_AWARE TARGETS
=
EXIST

BUT

UNIFORM_POLY
ARBITRARY_CNF ENTRY
WITH POLY SIZE
=
NOT ESTABLISHED IN THE AUDITED SET

AND SOME TARGETS HAVE
SEPARATE TRANSFORMATION OR SIZE BARRIERS.
```

Therefore the postmortem question

```text
Is there an already-known invariant
that avoids both E8 blowups
without hiding complexity elsewhere?
```

receives, for the audited set:

```text
ANSWER
=
NONE FOUND.
```

This is a source-history exhaustion result for the audited set, not an impossibility theorem.

## 8. Mature successor question

No new syntax is authorized.

The only legitimate successor question is:

```text
DOES THERE EXIST
A POLY-RECOGNIZABLE,
COMPOSITIONALLY DISCOVERABLE
SUBCLASS T
OF AN ECNF-LIKE MIXED STATE LANGUAGE
SUCH THAT:

1. arbitrary CNF enters T
   by uniform poly construction;

2. affine/parity objects remain compact;

3. local exact resolvents/projections
   such as A OR B remain compact;

4. exact forgetting is polynomial;

5. consistency is polynomial;

6. the invariant defining T
   is preserved after every elimination step;

7. recognition / preservation
   uses no SAT or equivalence oracle;

8. total state/history/reconstruction
   stays polynomial in original input length.
```

Observe the pressure point:

If item 1 plus item 5 hold universally for arbitrary CNF with polynomial construction and size, SAT is already in P.

Therefore any claimed `T` is itself theorem-level territory, not an engineering representation choice.

## 9. Successor lock

```text
NEW_E8_SUCCESSOR_ALGORITHM
=
LOCKED

NEXT_AUTHORIZED_OBJECT
=
SOURCE_BOUND_TRACTABLE_INVARIANT_INVENTORY_ONLY

NO:
new selector
new compiler
synthetic extension hunt
D1 promotion
P=NP claim
```

The next source-only inventory, if opened, must search specifically for known subclasses/invariants inside mixed affine+clausal representations satisfying as many of items 1-8 as possible, and record the first obligation that fails.

## Claim ceiling

```text
DUAL_BLOWUP_SURVIVOR_EXISTS
=
YES
(ECNF as audited example)

DUAL_BLOWUP_SURVIVOR_IS_D1
=
NO

AUDITED_LANGUAGE_CLOSING_ALL_GATES
=
NONE_FOUND

SUCCESSOR
=
LOCKED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
