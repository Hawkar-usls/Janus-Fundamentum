# JANUS TRUMP R47AF — Representation Authority Fiber Gate

Date: 2026-09-04

Status: **PREREGISTERED / EXECUTABLE FALSIFIER ADDED / UNIVERSAL COVERAGE OPEN**

## Core distinction

For a candidate representation `C`, representation equality, formula identity, and semantic identity are different relations:

`FORMULA_IDENTITY != REPRESENTATION_IDENTITY != SEMANTIC_IDENTITY`.

A small representation has no theorem authority merely because it is compact.

## Predicate-sufficiency theorem target

For target predicate `P=SAT`, semantic authority requires a universal proof of

`forall x,y: C(x)=C(y) => SAT(x)=SAT(y)`.

Equivalently, every fiber of `C` must be monochromatic with respect to SAT truth.

One exact counterexample

`exists x,y: C(x)=C(y) and SAT(x)!=SAT(y)`

is sufficient to refute predicate sufficiency for that representation and quarantine it from semantic decision authority.

Finite failure to find such a collision is calibration only. It is not a universal proof.

## Authority lattice

### Semantic authority

A representation receives `SEMANTIC_AUTHORITY_GRANTED` only when predicate sufficiency is theorem-backed or otherwise proof-carrying and independently replayable.

### Algorithmic authority

Semantic authority is necessary but not sufficient for algorithmic authority.

`ALGORITHMIC_AUTHORITY_GRANTED` additionally requires:

1. a polynomial-time encoder;
2. polynomial representation size;
3. a polynomial-time decider that operates on the representation and returns the target predicate.

A polynomial decoder that reconstructs the original instance is not enough. A polynomial witness verifier is also not enough. Either can leave the actual SAT decision problem untouched.

Therefore the corrected law is:

`POLYNOMIAL_SIZE + PREDICATE_SUFFICIENCY + POLYNOMIAL_REPRESENTATION_DECIDER => ALGORITHMIC_AUTHORITY`.

No weaker conjunction is silently promoted.

## Positive control

`EXACT_CANONICAL_CNF_IDENTITY` is an injective control. Equality of its representations implies equality of the canonical formulas by construction, so SAT truth cannot diverge inside a fiber.

This grants semantic authority to the identity control only. It does **not** grant algorithmic authority, because no polynomial SAT decider is supplied.

## Negative control — CLV

TRUMP uses CLV-style quantities as useful structural/resource measurements. R47AF explicitly prevents such measurements from being mistaken for semantic decision representations.

The executable gate searches for two formulas with equal

`CLV=(clause_count,literal_count,variable_count)`

but opposite SAT truth values.

An explicit witness is:

SAT:

`(x1) AND (x2) AND (x1 OR x2)`

UNSAT:

`(x1) AND (NOT x1) AND (x1 OR x2)`

Both have

`CLV=(3,4,2)`.

Thus CLV alone has a mixed SAT/UNSAT fiber and is insufficient as a semantic decision representation.

This does not weaken CLV's legitimate use as a resource profile or envelope coordinate. It only denies a stronger authority that was never proved.

## Relation to R47AC/R47AE

R47AC establishes a conditional polynomial composition theorem under universal polynomial persisted-envelope coverage. R47AE supplies a sealed finite witness where the root clause cap suffices. R47AF adds an orthogonal guard:

A state may fit a polynomial persisted-size envelope while a lossy semantic representation of that state still fails predicate sufficiency.

Therefore resource boundedness and semantic authority must remain separate proof obligations.

## Fiber gate for future candidates

Every proposed compression, quotient, signature, invariant, or canonical representation intended to carry a SAT decision must pass one of two lanes:

### Proof lane

Prove universal SAT-monochromaticity of every fiber and carry the proof/replay metadata.

### Counterexample lane

Search for an exact mixed fiber. One independently replayed SAT/UNSAT collision seals

`QUARANTINED_INSUFFICIENT_REPRESENTATION`.

## Firewalls

- `FINITE_NO_COLLISION != UNIVERSAL_SUFFICIENCY`.
- `POLYNOMIAL_SIZE != PREDICATE_SUFFICIENCY`.
- `POLYNOMIAL_DECODER != POLYNOMIAL_DECIDER`.
- `POLYNOMIAL_VERIFIER != POLYNOMIAL_DECIDER`.
- `RESOURCE_PROFILE != SEMANTIC_AUTHORITY`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
