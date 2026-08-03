# C044 Canonical Acceptance and the C045 Gate

```text
P_VS_NP=OPEN
```

## Governance status

C044 is the canonical local signed-support composition cycle. Its implementation
remains a draft and is not automatically merged or promoted beyond its exact
capability.

```text
C043 = ARCHITECTURE_CONTRACT_ADMITTED
       / FULL_IMPLEMENTATION_CANDIDATE
       / FULL_CI_GREEN
       / FINAL_ADMISSION_REVIEW_PENDING

C044 = CANONICAL
       / IMPLEMENTED
       / FULL_CI_GREEN
       / DRAFT
       / REVIEW_PENDING

C045 = RESERVED
       / JOINT_AFFINE_BASIS_DECOMPOSITION_AND_MESSAGE_DISCOVERY
       / SPECIFICATION_PENDING
```

The C043 line is deliberately not labelled `FULLY_ADMITTED` until its final
refusal-replay review is closed.

## What C044 establishes

C044 turns local signed affine-subspace support into a proof-carrying symbolic
message language on a deterministically discovered recursive decomposition.

The implementation constructs the affine basis, translates clauses, discovers
one assignment-independent coordinate-primal decomposition, compiles exact local
signed messages, composes separator branches, recovers SAT witnesses and emits
complete UNSAT blockers. The decomposition plan is fixed before separator values
are inspected.

Two strict-extension controls separate global and local support behavior:

```text
40 independent unit factors:
  C043 global -> OPEN_INTERSECTION_CLOSURE
  C044 local  -> SAT
  maximum separator size = 0

40-variable path:
  C043 global -> OPEN_INTERSECTION_CLOSURE
  C044 local  -> SAT
  maximum separator size = 1
```

Therefore, for the exact recorded capabilities:

```text
global signed-support overflow
  does not imply
local signed-support overflow.
```

This is a strict constructive separation between the global C043 representation
and the local C044 representation. It is not a universal statement that every
global overflow admits a compact local decomposition.

## Proof-carrying composition

Every accepted local leaf records the signed transition algebra, including:

- affine intersections in canonical RREF form;
- signed deltas and coefficient merges;
- zero cancellation;
- live support;
- pre-cancellation working support;
- exact conditional-count traces.

At a separator, every assignment receives either a compatible child composition
or a replayable blocker. Root SAT lifts one complete witness through the recursive
plan. Root UNSAT contains blockers covering every separator branch.

The independent verifier does not call the producer. It reconstructs the affine
basis, clause translation, decomposition plan, local signed transitions,
separator composition and final terminal.

Frozen controls record:

```text
300 random CNF + affine instances
300 exact terminals
0 SAT/UNSAT mismatches
0 false witnesses
0 independent-verifier failures

tampered witness       -> REJECTED
tampered plan          -> REJECTED
tampered OPEN evidence -> REJECTED
```

## Exact boundary

The registered NAND3+NEQ pressure image returns:

```text
OPEN_LOCAL_SUPPORT
reason = NO_ADMITTED_SEPARATOR
```

The meaning is capability-scoped:

```text
under the canonical affine basis,
coordinate-primal separator language,
local signed-support bounds,
and fixed separator cap,
no admitted decomposition was found.
```

It is not a hardness theorem, an incompatibility theorem, or evidence that every
basis and every symbolic language must fail.

## C045 — Joint Affine Basis, Decomposition and Message Discovery

C044 fixes the canonical Gaussian parameterization

```text
x = p + B lambda.
```

C045 is reserved for proof-carrying joint discovery over the representation
itself. A valid C045 portfolio must generate candidate coordinate systems before
any candidate evaluation, freeze and hash the full manifest, and charge every
candidate transform, decomposition attempt and symbolic compilation.

The target cycle is:

```text
raw CNF + affine equations
-> proof-carrying candidate basis transforms
-> frozen basis manifest
-> candidate-specific clause translation
-> candidate-specific C044 decomposition and message probe
-> deterministic certified selection
-> CLOSED_POLY or exact capability-scoped OPEN
```

Candidate generation may include only explicitly registered, polynomially
generated invertible affine-coordinate transformations. No SAT branch, witness,
UNSAT blocker, failed local assignment or post-probe repair may influence the
candidate set.

The first C045 specification must define at least:

```text
basis_transform_digest
basis_generation_proof_digest
frozen_basis_manifest_digest
candidate_capability_digest
translation_cost
separator_discovery_cost
local_message_cost
full_probe_certificate_digest
selection_receipt
```

A selected basis means only the best successful candidate in the frozen finite
portfolio under the exact budgets. Portfolio exhaustion remains `OPEN`; it is
never promoted to hardness.

## Surviving gate

```text
JOINT_AFFINE_BASIS_DECOMPOSITION_AND_MESSAGE_DISCOVERY
```

No C045 implementation or universal candidate-basis completeness theorem is
claimed by this document.
