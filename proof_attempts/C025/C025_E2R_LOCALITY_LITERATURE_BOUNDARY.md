# C025-E2R-L1 — Literature transfer boundary

The following external results are relevant **templates**, not transferred theorems for B2/ER3:

1. Dmitry Sokolov, *Pseudorandom Generators, Resolution and Heavy Width* (CCC 2022): exponential Resolution lower bounds for functional Nisan-Wigderson encodings that include local extension variables; the heavy-width measure is designed to survive these local auxiliaries.
2. Impagliazzo, Mouli, Pitassi, *Lower Bounds for Polynomial Calculus with Extension Variables over Finite Fields* (CCC 2023), plus later follow-up work: lower bounds with bounded-locality / bounded-arity extension variables in algebraic proof systems.
3. Guarded-extension-variable separations concern weaker systems without unrestricted fresh variables and therefore must not be promoted to a full ER lower bound.

## Required transfer audit

Before any literature result is used against `ER3[kappa-local]`, establish all of:

```text
SOURCE_FORMULA_OBJECT_IDENTITY_OR_EXPLICIT_REDUCTION
SOURCE_EXTENSION_SEMANTICS_MATCH_OR_SIMULATION
SOURCE_PROOF_RULE_SIMULATION
SOURCE_LOCALITY_PARAMETER_MAP
SOURCE_SIZE_PARAMETER_MAP
RESTRICTION_STABILITY
```

Absent these, status remains `INSPIRATION_ONLY`.

## Current decision

The immediate attack is not to cite a lower bound as if it applied. It is to test whether the **heavy-width style invariant itself** can be redefined for the frozen transitive-support-local B2 grammar and remain stable under Resolution plus partial assignments.
